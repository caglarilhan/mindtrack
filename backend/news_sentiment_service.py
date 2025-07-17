import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

class NewsSentimentService:
    def __init__(self, newsapi_key=None):
        self.newsapi_key = newsapi_key
        self.english_sentiment = pipeline("sentiment-analysis")
        self.vader = SentimentIntensityAnalyzer()

    def fetch_newsapi_headlines(self, query, lang="tr", max_results=10):
        if not self.newsapi_key:
            return []
        url = f"https://newsapi.org/v2/everything?q={query}&language={lang}&apiKey={self.newsapi_key}"
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            return [a['title'] for a in data.get('articles', [])[:max_results]]
        return []

    def fetch_rss_headlines(self, query, lang="tr", max_results=10):
        url = f"https://news.google.com/rss/search?q={query}&hl={lang}"
        resp = requests.get(url)
        soup = BeautifulSoup(resp.content, features="xml")
        items = soup.findAll('item')
        news_list = [item.title.text for item in items[:max_results]]
        return news_list

    def analyze_sentiment(self, text, lang="tr"):
        if lang == "en":
            result = self.english_sentiment(text)
            return result[0]['label'], float(result[0]['score'])
        else:
            vader_score = self.vader.polarity_scores(text)
            return self._vader_to_label(vader_score['compound']), vader_score['compound']

    def _vader_to_label(self, score):
        if score >= 0.05:
            return "POSITIVE"
        elif score <= -0.05:
            return "NEGATIVE"
        else:
            return "NEUTRAL"

    def get_news_sentiment_summary(self, query, lang="tr", max_results=10):
        headlines = self.fetch_newsapi_headlines(query, lang, max_results)
        if not headlines:
            headlines = self.fetch_rss_headlines(query, lang, max_results)
        sentiments = [self.analyze_sentiment(h, lang=lang) for h in headlines]
        if sentiments:
            avg_score = sum([s[1] for s in sentiments]) / len(sentiments)
            pos_count = sum([1 for s in sentiments if s[0] == "POSITIVE"])
            neg_count = sum([1 for s in sentiments if s[0] == "NEGATIVE"])
            neu_count = sum([1 for s in sentiments if s[0] == "NEUTRAL"])
        else:
            avg_score = 0.0
            pos_count = neg_count = neu_count = 0
        return {
            "query": query,
            "news_count": len(headlines),
            "avg_sentiment_score": avg_score,
            "positive": pos_count,
            "negative": neg_count,
            "neutral": neu_count,
            "news_samples": headlines[:3]
        }

# Test fonksiyonu
if __name__ == "__main__":
    service = NewsSentimentService(newsapi_key="YOUR_NEWSAPI_KEY")
    result = service.get_news_sentiment_summary("THYAO", lang="tr", max_results=5)
    print(result) 