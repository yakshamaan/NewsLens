from app import db
from datetime import datetime

class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    source = db.Column(db.String(100))
    url = db.Column(db.String(1000), unique=True)
    published_at = db.Column(db.DateTime)
    category = db.Column(db.String(50))

    # Sentiment
    sentiment = db.Column(db.String(20))
    sentiment_score = db.Column(db.Float)

    # Emotions
    emotion = db.Column(db.String(20))
    emotion_score = db.Column(db.Float)
    emotion_scores_json = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'url': self.url,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'category': self.category,
            'sentiment': self.sentiment,
            'sentiment_score': self.sentiment_score,
            'emotion': self.emotion,
            'emotion_score': self.emotion_score,
            'emotion_scores': json.loads(self.emotion_scores_json) if self.emotion_scores_json else {},
        }