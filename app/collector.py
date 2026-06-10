import requests
from datetime import datetime
from app import db
from app.models import Article
import os
import time

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
NEWS_API_URL = 'https://newsapi.org/v2/everything'

INDIA_QUERIES = [
    # India
    'India politics', 'India economy', 'India technology', 'India health',
    'India science', 'India military', 'India foreign policy', 'India elections',
    'Modi government', 'Indian parliament', 'India China border',
    'India Pakistan', 'India US relations', 'Indian startup',
    'NDTV', 'Times of India', 'The Hindu', 'India Today',

    # USA
    'US politics', 'US economy', 'White House', 'US Congress',
    'Donald Trump', 'US military', 'Federal Reserve', 'US elections',
    'Silicon Valley', 'Wall Street', 'US foreign policy', 'Pentagon',

    # UK
    'UK politics', 'UK economy', 'British parliament', 'Keir Starmer',
    'Bank of England', 'Brexit aftermath', 'UK military',

    # Europe
    'European Union', 'EU economy', 'NATO', 'Emmanuel Macron',
    'Germany politics', 'France elections', 'EU energy crisis',
    'ECB interest rates', 'European parliament',

    # Russia & Ukraine
    'Russia Ukraine war', 'Russia sanctions', 'Putin', 'Zelensky',
    'Ukraine military', 'Russia economy', 'Russia NATO',

    # China
    'China economy', 'China military', 'Xi Jinping', 'China Taiwan',
    'China US trade', 'China technology', 'Belt and Road',
    'China South China Sea',

    # Middle East
    'Israel Gaza', 'Iran nuclear', 'Saudi Arabia oil', 'Middle East conflict',
    'Iran US tensions', 'Turkey politics', 'OPEC oil prices',

    # Asia Pacific
    'North Korea missile', 'South Korea politics', 'Japan economy',
    'Kim Jong Un', 'Japan military', 'ASEAN summit',
    'Taiwan strait', 'Australia politics', 'Pakistan economy',

    # Africa & Latin America
    'Africa conflict', 'South Africa economy', 'Brazil politics',
    'Nigeria elections', 'Mexico drug cartel', 'Venezuela crisis',

    # Global topics
    'climate change', 'global inflation', 'world economy recession',
    'artificial intelligence regulation', 'crypto bitcoin',
    'global health WHO', 'United Nations', 'IMF World Bank',
    'cybersecurity attack', 'space exploration NASA',
    'nuclear weapons', 'global food crisis', 'refugee crisis',

    # Technology
    'AI artificial intelligence', 'OpenAI', 'Google technology',
    'Meta Facebook', 'Tesla Elon Musk', 'semiconductor chip shortage',
    'social media regulation', 'big tech antitrust',

    # Business & Markets
    'stock market crash', 'oil prices OPEC', 'interest rates inflation',
    'global supply chain', 'electric vehicles', 'renewable energy',
]

def should_fetch():
    from app.models import Article
    from datetime import datetime, timedelta

    latest = Article.query.order_by(Article.created_at.desc()).first()

    if not latest:
        return True  # DB is empty, always fetch

    age = datetime.utcnow() - latest.created_at
    return age > timedelta(hours=12)  # only fetch if data is older than 12 hours

def fetch_articles():
    articles_saved = 0

    for query in INDIA_QUERIES:
        try:
            response = requests.get(NEWS_API_URL, params={
                'q': query,
                'language': 'en',
                'pageSize': 10,
                'sortBy': 'publishedAt',
                'apiKey': NEWS_API_KEY,
            })

            data = response.json()

            if data.get('status') != 'ok':
                print(f"Error for '{query}': {data.get('message')}")
                continue

            for item in data.get('articles', []):
                existing = Article.query.filter_by(url=item.get('url')).first()
                if existing:
                    continue

                published = None
                if item.get('publishedAt'):
                    try:
                        published = datetime.strptime(
                            item['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'
                        )
                    except ValueError:
                        pass

                article = Article(
                    title=item.get('title', ''),
                    description=item.get('description', ''),
                    content=item.get('content', ''),
                    source=item.get('source', {}).get('name', ''),
                    url=item.get('url', ''),
                    published_at=published,
                    category=query.split()[-1].lower(),
                )

                db.session.add(article)
                articles_saved += 1

            db.session.commit()
            print(f"Fetched query: {query}")

            time.sleep(0.5)

        except Exception as e:
            print(f"Failed to fetch '{query}': {e}")
            db.session.rollback()

    print(f"Total new articles saved: {articles_saved}")
    return articles_saved