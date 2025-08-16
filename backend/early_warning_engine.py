import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict

from indicators import (
    detect_rsi_bullish_divergence,
    detect_macd_bullish_momentum,
    detect_obv_increase,
    detect_vwap_breakout,
    detect_bullish_engulfing,
    detect_morning_star,
    detect_three_white_soldiers,
    detect_volume_spike,
    detect_bearish_engulfing,
    detect_evening_star,
    detect_three_black_crows,
    detect_volume_drop,
    detect_rsi_bearish,
    detect_macd_bearish
)
from social_sentiment_service import SocialSentimentService
from google_trends_service import GoogleTrendsService
from news_sentiment_service import NewsSentimentService
import investpy
import pandas as pd
from datetime import datetime

cred = credentials.Certificate("/Users/caglarilhan/borsailhanos/backend/bist-backend-key.json")
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)

db = firestore.client()

class EarlyWarningEngine:
    """
    Erken Uyarı Motoru - Teknik, sosyal medya ve haber sinyalleri
    """
    
    def __init__(self, twitter_keys=None, reddit_keys=None, newsapi_key=None):
        self.twitter_keys = twitter_keys
        self.reddit_keys = reddit_keys
        self.newsapi_key = newsapi_key
    
    def analyze_stock(self, symbol: str) -> Dict:
        """
        Hisse için erken uyarı analizi
        """
        try:
            ticker = symbol.replace(".IS", "")
            df = investpy.get_stock_recent_data(stock=ticker, country="turkey")
            
            if df.empty or len(df) < 50:
                return {"symbol": symbol, "error": "Yeterli veri yok"}
            
            df = df.rename(columns={
                'Close': 'close', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Volume': 'volume'
            })
            
            # Bullish skor
            bullish_signals = [
                detect_rsi_bullish_divergence(df),
                detect_macd_bullish_momentum(df),
                detect_obv_increase(df),
                detect_vwap_breakout(df),
                detect_bullish_engulfing(df),
                detect_morning_star(df),
                detect_three_white_soldiers(df),
                detect_volume_spike(df)
            ]
            bullish_score = sum(bullish_signals) / len(bullish_signals)
            
            # Bearish skor
            bearish_signals = [
                detect_bearish_engulfing(df),
                detect_evening_star(df),
                detect_three_black_crows(df),
                detect_volume_drop(df),
                detect_rsi_bearish(df),
                detect_macd_bearish(df)
            ]
            bearish_score = sum(bearish_signals) / len(bearish_signals)
            
            # Sosyal medya sentiment
            social = SocialSentimentService(self.twitter_keys, self.reddit_keys)
            social_summary = social.get_social_sentiment_summary(symbol, twitter_count=10, reddit_limit=10, lang="tr")
            social_score = (social_summary["avg_sentiment"] + 1) / 2
            
            # Google Trends
            trends = GoogleTrendsService()
            trend_score_data = trends.get_trend_score(symbol, timeframe="now 7-d", geo="TR")
            trend_score = trend_score_data.get("change", 0)
            trend_score = max(min(trend_score, 1), -1)
            trend_score = (trend_score + 1) / 2
            
            # Haber sentiment
            news = NewsSentimentService(self.newsapi_key)
            news_summary = news.get_news_sentiment_summary(symbol, lang="tr", max_results=10)
            news_score = (news_summary["avg_sentiment_score"] + 1) / 2
            
            # Kombine skorlar
            bullish_ews = 0.5 * bullish_score + 0.2 * social_score + 0.15 * trend_score + 0.15 * news_score
            bearish_ews = 0.5 * bearish_score + 0.2 * (1-social_score) + 0.15 * (1-trend_score) + 0.15 * (1-news_score)
            
            # Yorum
            if bullish_ews > 0.7 and bullish_ews > bearish_ews:
                signal = "YÜKSELİŞ ERKEN UYARI"
                confidence = bullish_ews
            elif bearish_ews > 0.7 and bearish_ews > bullish_ews:
                signal = "DÜŞÜŞ ERKEN UYARI"
                confidence = bearish_ews
            else:
                signal = "NÖTR"
                confidence = max(bullish_ews, bearish_ews)
            
            return {
                "symbol": symbol,
                "signal": signal,
                "confidence": confidence,
                "bullish_score": bullish_score,
                "bearish_score": bearish_score,
                "social_score": social_score,
                "trend_score": trend_score,
                "news_score": news_score,
                "risk_signals": [],
                "opportunity_signals": []
            }
            
        except Exception as e:
            return {"symbol": symbol, "error": str(e)}

# --- Eski fonksiyon (geriye uyumluluk için) ---
def early_warning_for_symbol(symbol, twitter_keys=None, reddit_keys=None, newsapi_key=None):
    ticker = symbol.replace(".IS", "")
    try:
        df = investpy.get_stock_recent_data(stock=ticker, country="turkey")
        if df.empty or len(df) < 50:
            return {"symbol": symbol, "error": "Yeterli veri yok"}
        df = df.rename(columns={
            'Close': 'close', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Volume': 'volume'
        })
        # Bullish skor
        bullish_signals = [
            detect_rsi_bullish_divergence(df),
            detect_macd_bullish_momentum(df),
            detect_obv_increase(df),
            detect_vwap_breakout(df),
            detect_bullish_engulfing(df),
            detect_morning_star(df),
            detect_three_white_soldiers(df),
            detect_volume_spike(df)
        ]
        bullish_score = sum(bullish_signals) / len(bullish_signals)
        # Bearish skor
        bearish_signals = [
            detect_bearish_engulfing(df),
            detect_evening_star(df),
            detect_three_black_crows(df),
            detect_volume_drop(df),
            detect_rsi_bearish(df),
            detect_macd_bearish(df)
        ]
        bearish_score = sum(bearish_signals) / len(bearish_signals)
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}

    # Sosyal medya sentiment
    social = SocialSentimentService(twitter_keys, reddit_keys)
    social_summary = social.get_social_sentiment_summary(symbol, twitter_count=10, reddit_limit=10, lang="tr")
    social_score = (social_summary["avg_sentiment"] + 1) / 2

    # Google Trends
    trends = GoogleTrendsService()
    trend_score_data = trends.get_trend_score(symbol, timeframe="now 7-d", geo="TR")
    trend_score = trend_score_data.get("change", 0)
    trend_score = max(min(trend_score, 1), -1)
    trend_score = (trend_score + 1) / 2

    # Haber sentiment
    news = NewsSentimentService(newsapi_key)
    news_summary = news.get_news_sentiment_summary(symbol, lang="tr", max_results=10)
    news_score = (news_summary["avg_sentiment_score"] + 1) / 2

    # Kombine skorlar
    bullish_ews = 0.5 * bullish_score + 0.2 * social_score + 0.15 * trend_score + 0.15 * news_score
    bearish_ews = 0.5 * bearish_score + 0.2 * (1-social_score) + 0.15 * (1-trend_score) + 0.15 * (1-news_score)

    # Yorum
    if bullish_ews > 0.7 and bullish_ews > bearish_ews:
        signal = "YÜKSELİŞ ERKEN UYARI"
        confidence = bullish_ews
    elif bearish_ews > 0.7 and bearish_ews > bullish_ews:
        signal = "DÜŞÜŞ ERKEN UYARI"
        confidence = bearish_ews
    else:
        signal = "NÖTR"
        confidence = max(bullish_ews, bearish_ews)
    return {
        "symbol": symbol,
        "signal": signal,
        "confidence": confidence,
        "bullish_score": bullish_score,
        "bearish_score": bearish_score,
        "bullish_ews": bullish_ews,
        "bearish_ews": bearish_ews,
        "social_score": social_score,
        "trend_score": trend_score,
        "news_score": news_score,
        "details": {
            "social": social_summary,
            "trend": trend_score_data,
            "news": news_summary
        }
    }

def scan_and_write_early_warnings(symbols, twitter_keys=None, reddit_keys=None, newsapi_key=None):
    results = []
    for sym in symbols:
        result = early_warning_for_symbol(sym, twitter_keys, reddit_keys, newsapi_key)
        result['timestamp'] = datetime.now()
        results.append(result)
        # Firestore'a yaz
        db.collection('early_warnings').document(sym).set(result)
    return results

# Test fonksiyonu: BIST30 taraması
if __name__ == "__main__":
    twitter_keys = None
    reddit_keys = None
    newsapi_key = None
    symbols = [
        "THYAO.IS", "ASELS.IS", "KRDMD.IS", "TUPRS.IS", "EKGYO.IS",
        "SAHOL.IS", "VAKBN.IS", "BIMAS.IS", "EREGL.IS", "TKFEN.IS",
        "PGSUS.IS", "SISE.IS", "AKBNK.IS", "GARAN.IS", "HALKB.IS",
        "ISCTR.IS", "TCELL.IS", "ENKAI.IS", "KOZAL.IS", "FROTO.IS",
        "TAVHL.IS", "SOKM.IS", "TOASO.IS", "GUBRF.IS", "OYAKC.IS",
        "MGROS.IS", "ULKER.IS", "ARCLK.IS", "KOZAA.IS", "VESTL.IS"
    ]
    results = scan_and_write_early_warnings(symbols, twitter_keys, reddit_keys, newsapi_key) 