import tweepy
import praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

class SocialSentimentService:
    def __init__(self, twitter_keys=None, reddit_keys=None):
        # Twitter API
        if twitter_keys:
            auth = tweepy.OAuth1UserHandler(
                twitter_keys['api_key'],
                twitter_keys['api_secret'],
                twitter_keys['access_token'],
                twitter_keys['access_token_secret']
            )
            self.twitter_api = tweepy.API(auth)
        else:
            self.twitter_api = None
        # Reddit API
        if reddit_keys:
            self.reddit_api = praw.Reddit(
                client_id=reddit_keys['client_id'],
                client_secret=reddit_keys['client_secret'],
                user_agent=reddit_keys['user_agent']
            )
        else:
            self.reddit_api = None
        # Sentiment
        self.vader = SentimentIntensityAnalyzer()
        self.english_sentiment = pipeline("sentiment-analysis")

    def fetch_twitter_mentions(self, query, count=20):
        if not self.twitter_api:
            return []
        tweets = tweepy.Cursor(self.twitter_api.search_tweets, q=query, lang="en", tweet_mode='extended').items(count)
        return [tweet.full_text for tweet in tweets]

    def fetch_reddit_mentions(self, query, subreddit="stocks", limit=20):
        if not self.reddit_api:
            return []
        posts = self.reddit_api.subreddit(subreddit).search(query, limit=limit)
        return [post.title + " " + post.selftext for post in posts]

    def analyze_sentiment(self, texts, lang="en"):
        results = []
        for text in texts:
            if lang == "en":
                vader_score = self.vader.polarity_scores(text)
                transformer = self.english_sentiment(text[:512])
                results.append({
                    "text": text,
                    "vader": vader_score['compound'],
                    "transformer_label": transformer[0]['label'],
                    "transformer_score": transformer[0]['score']
                })
            else:
                vader_score = self.vader.polarity_scores(text)
                results.append({
                    "text": text,
                    "vader": vader_score['compound']
                })
        return results

    def get_social_sentiment_summary(self, query, twitter_count=20, reddit_limit=20, lang="en"):
        twitter_texts = self.fetch_twitter_mentions(query, count=twitter_count)
        reddit_texts = self.fetch_reddit_mentions(query, limit=reddit_limit)
        all_texts = twitter_texts + reddit_texts
        sentiments = self.analyze_sentiment(all_texts, lang=lang)
        if sentiments:
            avg_vader = sum([s['vader'] for s in sentiments]) / len(sentiments)
            pos_count = sum([1 for s in sentiments if s.get('transformer_label', '') == 'POSITIVE'])
            neg_count = sum([1 for s in sentiments if s.get('transformer_label', '') == 'NEGATIVE'])
        else:
            avg_vader = 0.0
            pos_count = neg_count = 0
        return {
            "query": query,
            "mention_count": len(all_texts),
            "avg_sentiment": avg_vader,
            "positive": pos_count,
            "negative": neg_count,
            "samples": all_texts[:3]
        } 