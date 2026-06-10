from transformers import pipeline

print("Loading sentiment model...")
sentiment_pipeline = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    truncation=True,
    max_length=512,
    batch_size=16,
)
print("Sentiment model loaded.")

print("Loading emotion model...")
emotion_pipeline = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    truncation=True,
    max_length=512,
    top_k=None,
)
print("Emotion model loaded.")

def get_text(article):
    text = article.title or ''
    if article.description:
        text += ' ' + article.description
    return text[:512]

def analyze_articles_batch(articles):
    import json
    texts = [get_text(a) for a in articles]

    # Sentiment
    try:
        sentiment_results = sentiment_pipeline(texts)
        for article, result in zip(articles, sentiment_results):
            article.sentiment = result['label'].lower()
            article.sentiment_score = round(result['score'], 4)
    except Exception as e:
        print(f"Sentiment batch error: {e}")
        for article in articles:
            article.sentiment = 'neutral'
            article.sentiment_score = 0.0

    # Emotion
    try:
        emotion_results = emotion_pipeline(texts)
        for article, scores in zip(articles, emotion_results):
            sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
            top = sorted_scores[0]
            article.emotion = top['label'].lower()
            article.emotion_score = round(top['score'], 4)
            article.emotion_scores_json = json.dumps({
                s['label'].lower(): round(s['score'], 4)
                for s in sorted_scores
            })
    except Exception as e:
        print(f"Emotion batch error: {e}")
        for article in articles:
            article.emotion = 'neutral'
            article.emotion_score = 0.0
            article.emotion_scores_json = '{}'

    return articles

def analyze_article(article):
    import json
    text = get_text(article)

    try:
        result = sentiment_pipeline(text)[0]
        article.sentiment = result['label'].lower()
        article.sentiment_score = round(result['score'], 4)
    except Exception as e:
        print(f"Sentiment error: {e}")
        article.sentiment = 'neutral'
        article.sentiment_score = 0.0

    try:
        scores = emotion_pipeline(text)[0]
        sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
        top = sorted_scores[0]
        article.emotion = top['label'].lower()
        article.emotion_score = round(top['score'], 4)
        article.emotion_scores_json = json.dumps({
            s['label'].lower(): round(s['score'], 4)
            for s in sorted_scores
        })
    except Exception as e:
        print(f"Emotion error: {e}")
        article.emotion = 'neutral'
        article.emotion_score = 0.0
        article.emotion_scores_json = '{}'

    return article