from flask import Blueprint, jsonify, render_template
from app.models import Article
from app.collector import fetch_articles
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/fetch')
def fetch():
    from app.collector import fetch_articles, should_fetch

    if not should_fetch():
        from app.models import Article
        count = Article.query.count()
        return jsonify({
            'message': f'Articles are fresh, skipping fetch. {count} articles in DB.'
        })

    count = fetch_articles()
    return jsonify({'message': f'Fetched {count} new articles'})

@main.route('/articles')
def get_articles():
    articles = Article.query.order_by(Article.published_at.desc()).limit(50).all()
    return jsonify([a.to_dict() for a in articles])

@main.route('/articles/<source>')
def get_by_source(source):
    articles = Article.query.filter_by(source=source)\
               .order_by(Article.published_at.desc()).limit(20).all()
    return jsonify([a.to_dict() for a in articles])

from app.nlp import analyze_article
from app import db

@main.route('/analyze')
def analyze():
    from app.models import Article
    from app.nlp import analyze_articles_batch

    articles = Article.query.filter_by(sentiment=None).all()

    if not articles:
        return jsonify({'message': 'All articles already analyzed'})

    batch_size = 16
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]
        analyze_articles_batch(batch)
        db.session.commit()
        print(f"Analyzed {min(i + batch_size, len(articles))}/{len(articles)}")

    return jsonify({'message': f'Analyzed {len(articles)} articles'})

@main.route('/stats')
def stats():
    from app.models import Article
    from sqlalchemy import func

    total = Article.query.count()
    positive = Article.query.filter_by(sentiment='positive').count()
    negative = Article.query.filter_by(sentiment='negative').count()
    neutral = Article.query.filter_by(sentiment='neutral').count()

    by_source = db.session.query(
        Article.source, func.count(Article.id)
    ).group_by(Article.source).all()

    return jsonify({
        'total_articles': total,
        'sentiment': {
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
        },
        'by_source': {source: count for source, count in by_source}
    })
@main.route('/reset')
def reset():
    from app.models import Article
    Article.query.delete()
    db.session.commit()
    return jsonify({'message': 'Database cleared'})