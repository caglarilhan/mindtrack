import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class SentimentAnalyzer:
    """
    Gelişmiş sentiment analizi
    Haber, sosyal medya ve makro veri entegrasyonu
    """
    
    def __init__(self, news_api_key: str = None):
        self.news_api_key = news_api_key
        self.sentiment_cache = {}
        self.sentiment_history = []
        
    def get_news_sentiment(self, query: str, days: int = 7) -> Dict:
        """
        NewsAPI ile haber sentiment analizi
        """
        try:
            if not self.news_api_key:
                return {"error": "NewsAPI key gerekli"}
            
            # Tarih aralığı
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # NewsAPI çağrısı
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'language': 'tr,en',
                'sortBy': 'relevancy',
                'apiKey': self.news_api_key,
                'pageSize': 100
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                news_data = response.json()
                articles = news_data.get('articles', [])
                
                if articles:
                    # Sentiment analizi
                    sentiment_scores = self._analyze_news_sentiment(articles)
                    
                    return {
                        "total_articles": len(articles),
                        "sentiment_scores": sentiment_scores,
                        "overall_sentiment": self._calculate_overall_sentiment(sentiment_scores),
                        "sentiment_trend": self._calculate_sentiment_trend(articles),
                        "key_topics": self._extract_key_topics(articles),
                        "analysis_date": datetime.now().isoformat()
                    }
                else:
                    return {"error": "Haber bulunamadı"}
            else:
                return {"error": f"API hatası: {response.status_code}"}
                
        except Exception as e:
            print(f"Haber sentiment hatası: {e}")
            return {"error": str(e)}
    
    def _analyze_news_sentiment(self, articles: list) -> Dict:
        """
        Haber sentiment skorlarını hesaplar
        """
        try:
            sentiment_scores = {
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'scores': []
            }
            
            # Sentiment keywords
            positive_words = [
                'yükseldi', 'arttı', 'büyüdü', 'güçlendi', 'iyileşti', 'kazandı',
                'başarılı', 'olumlu', 'güven', 'optimist', 'büyüme', 'kâr',
                'yükseliş', 'güçlenme', 'iyileşme', 'başarı', 'olumlu', 'güven'
            ]
            
            negative_words = [
                'düştü', 'azaldı', 'küçüldü', 'zayıfladı', 'kötüleşti', 'kaybetti',
                'başarısız', 'olumsuz', 'güvensizlik', 'pesimist', 'küçülme', 'zarar',
                'düşüş', 'zayıflama', 'kötüleşme', 'başarısızlık', 'olumsuz', 'güvensizlik'
            ]
            
            for article in articles:
                title = article.get('title', '').lower()
                description = article.get('description', '').lower()
                content = title + ' ' + description
                
                # Sentiment skoru hesapla
                positive_count = sum(1 for word in positive_words if word in content)
                negative_count = sum(1 for word in word in negative_words if word in content)
                
                if positive_count > negative_count:
                    sentiment = 'positive'
                    score = positive_count / (positive_count + negative_count + 1)
                elif negative_count > positive_count:
                    sentiment = 'negative'
                    score = negative_count / (positive_count + negative_count + 1)
                else:
                    sentiment = 'neutral'
                    score = 0.5
                
                sentiment_scores[sentiment] += 1
                sentiment_scores['scores'].append({
                    'title': article.get('title', ''),
                    'sentiment': sentiment,
                    'score': score,
                    'published_at': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', '')
                })
            
            return sentiment_scores
            
        except Exception as e:
            print(f"Sentiment analiz hatası: {e}")
            return {"positive": 0, "negative": 0, "neutral": 0, "scores": []}
    
    def _calculate_overall_sentiment(self, sentiment_scores: Dict) -> str:
        """
        Genel sentiment'i hesaplar
        """
        try:
            total = sentiment_scores['positive'] + sentiment_scores['negative'] + sentiment_scores['neutral']
            
            if total == 0:
                return 'neutral'
            
            positive_ratio = sentiment_scores['positive'] / total
            negative_ratio = sentiment_scores['negative'] / total
            
            if positive_ratio > 0.6:
                return 'very_positive'
            elif positive_ratio > 0.4:
                return 'positive'
            elif negative_ratio > 0.6:
                return 'very_negative'
            elif negative_ratio > 0.4:
                return 'negative'
            else:
                return 'neutral'
                
        except Exception as e:
            return 'neutral'
    
    def _calculate_sentiment_trend(self, articles: list) -> Dict:
        """
        Sentiment trend'ini hesaplar
        """
        try:
            # Tarihe göre grupla
            daily_sentiment = {}
            
            for article in articles:
                try:
                    date = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')).date()
                    sentiment = self._get_article_sentiment(article)
                    
                    if date not in daily_sentiment:
                        daily_sentiment[date] = {'positive': 0, 'negative': 0, 'neutral': 0}
                    
                    daily_sentiment[date][sentiment] += 1
                except:
                    continue
            
            # Trend hesapla
            if len(daily_sentiment) > 1:
                dates = sorted(daily_sentiment.keys())
                positive_trend = []
                negative_trend = []
                
                for date in dates:
                    daily = daily_sentiment[date]
                    total = daily['positive'] + daily['negative'] + daily['neutral']
                    
                    if total > 0:
                        positive_trend.append(daily['positive'] / total)
                        negative_trend.append(daily['negative'] / total)
                
                if len(positive_trend) > 1:
                    positive_slope = np.polyfit(range(len(positive_trend)), positive_trend, 1)[0]
                    negative_slope = np.polyfit(range(len(negative_trend)), negative_trend, 1)[0]
                    
                    return {
                        "positive_trend": float(positive_slope),
                        "negative_trend": float(negative_slope),
                        "trend_direction": "improving" if positive_slope > 0 else "worsening",
                        "trend_strength": abs(positive_slope) + abs(negative_slope)
                    }
            
            return {"trend_direction": "stable", "trend_strength": 0}
            
        except Exception as e:
            return {"trend_direction": "stable", "trend_strength": 0}
    
    def _get_article_sentiment(self, article: dict) -> str:
        """
        Tek haber sentiment'ini belirler
        """
        try:
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            content = title + ' ' + description
            
            positive_words = ['yükseldi', 'arttı', 'büyüdü', 'güçlendi', 'iyileşti', 'kazandı']
            negative_words = ['düştü', 'azaldı', 'küçüldü', 'zayıfladı', 'kötüleşti', 'kaybetti']
            
            positive_count = sum(1 for word in positive_words if word in content)
            negative_count = sum(1 for word in negative_words if word in content)
            
            if positive_count > negative_count:
                return 'positive'
            elif negative_count > positive_count:
                return 'negative'
            else:
                return 'neutral'
                
        except:
            return 'neutral'
    
    def _extract_key_topics(self, articles: list) -> list:
        """
        Ana konuları çıkarır
        """
        try:
            # Basit keyword extraction
            all_text = ' '.join([
                article.get('title', '') + ' ' + article.get('description', '')
                for article in articles
            ]).lower()
            
            # Türkçe finansal keywords
            keywords = [
                'faiz', 'enflasyon', 'döviz', 'borsa', 'hisse', 'kâr', 'zarar',
                'büyüme', 'ekonomi', 'merkez bankası', 'tcmb', 'bütçe', 'vergi',
                'ihracat', 'ithalat', 'cari açık', 'işsizlik', 'gsmh', 'gayri safi'
            ]
            
            key_topics = []
            for keyword in keywords:
                if keyword in all_text:
                    count = all_text.count(keyword)
                    key_topics.append({
                        'topic': keyword,
                        'frequency': count,
                        'importance': count / len(articles)
                    })
            
            # Önem sırasına göre sırala
            key_topics.sort(key=lambda x: x['importance'], reverse=True)
            
            return key_topics[:10]  # Top 10
            
        except Exception as e:
            return []
    
    def get_social_sentiment(self, symbol: str) -> Dict:
        """
        Sosyal medya sentiment analizi (simüle)
        """
        try:
            # Gerçek sosyal medya API'si yerine simüle edilmiş veri
            # Twitter, Reddit, StockTwits entegrasyonu eklenebilir
            
            # Simüle edilmiş sentiment verisi
            sentiment_data = {
                'twitter': {
                    'mentions': np.random.randint(100, 1000),
                    'positive_ratio': np.random.uniform(0.3, 0.7),
                    'negative_ratio': np.random.uniform(0.2, 0.5),
                    'neutral_ratio': np.random.uniform(0.1, 0.3)
                },
                'reddit': {
                    'mentions': np.random.randint(50, 500),
                    'positive_ratio': np.random.uniform(0.4, 0.8),
                    'negative_ratio': np.random.uniform(0.1, 0.4),
                    'neutral_ratio': np.random.uniform(0.1, 0.3)
                },
                'stocktwits': {
                    'mentions': np.random.randint(200, 800),
                    'positive_ratio': np.random.uniform(0.3, 0.7),
                    'negative_ratio': np.random.uniform(0.2, 0.6),
                    'neutral_ratio': np.random.uniform(0.1, 0.3)
                }
            }
            
            # Genel sentiment skoru
            total_positive = sum(data['positive_ratio'] * data['mentions'] for data in sentiment_data.values())
            total_negative = sum(data['negative_ratio'] * data['mentions'] for data in sentiment_data.values())
            total_mentions = sum(data['mentions'] for data in sentiment_data.values())
            
            if total_mentions > 0:
                overall_sentiment = (total_positive - total_negative) / total_mentions
            else:
                overall_sentiment = 0
            
            return {
                "platform_sentiment": sentiment_data,
                "overall_sentiment": float(overall_sentiment),
                "total_mentions": total_mentions,
                "sentiment_label": self._get_sentiment_label(overall_sentiment),
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Sosyal sentiment hatası: {e}")
            return {"error": str(e)}
    
    def _get_sentiment_label(self, score: float) -> str:
        """
        Sentiment skoruna göre etiket verir
        """
        if score > 0.3:
            return "Very Positive"
        elif score > 0.1:
            return "Positive"
        elif score > -0.1:
            return "Neutral"
        elif score > -0.3:
            return "Negative"
        else:
            return "Very Negative"
    
    def get_macro_sentiment(self) -> Dict:
        """
        Makro ekonomik sentiment analizi
        """
        try:
            # TCMB, TÜİK, uluslararası kuruluş verileri
            # Simüle edilmiş makro sentiment
            
            macro_indicators = {
                'inflation': {
                    'value': 65.0,
                    'trend': 'decreasing',
                    'sentiment': 'positive',
                    'weight': 0.3
                },
                'interest_rate': {
                    'value': 50.0,
                    'trend': 'stable',
                    'sentiment': 'neutral',
                    'weight': 0.25
                },
                'exchange_rate': {
                    'value': 32.5,
                    'trend': 'stable',
                    'sentiment': 'neutral',
                    'weight': 0.2
                },
                'gdp_growth': {
                    'value': 4.2,
                    'trend': 'increasing',
                    'sentiment': 'positive',
                    'weight': 0.15
                },
                'unemployment': {
                    'value': 9.8,
                    'trend': 'decreasing',
                    'sentiment': 'positive',
                    'weight': 0.1
                }
            }
            
            # Ağırlıklı sentiment skoru
            total_score = 0
            total_weight = 0
            
            for indicator, data in macro_indicators.items():
                weight = data['weight']
                sentiment_score = self._sentiment_to_score(data['sentiment'])
                
                total_score += sentiment_score * weight
                total_weight += weight
            
            if total_weight > 0:
                macro_sentiment = total_score / total_weight
            else:
                macro_sentiment = 0
            
            return {
                "indicators": macro_indicators,
                "overall_sentiment": float(macro_sentiment),
                "sentiment_label": self._get_sentiment_label(macro_sentiment),
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Makro sentiment hatası: {e}")
            return {"error": str(e)}
    
    def _sentiment_to_score(self, sentiment: str) -> float:
        """
        Sentiment string'ini skora çevirir
        """
        sentiment_map = {
            'very_positive': 0.8,
            'positive': 0.4,
            'neutral': 0.0,
            'negative': -0.4,
            'very_negative': -0.8
        }
        return sentiment_map.get(sentiment, 0.0)
    
    def get_comprehensive_sentiment(self, symbol: str, query: str = None) -> Dict:
        """
        Kapsamlı sentiment analizi
        """
        try:
            if not query:
                query = symbol
            
            # Tüm sentiment verilerini topla
            news_sentiment = self.get_news_sentiment(query)
            social_sentiment = self.get_social_sentiment(symbol)
            macro_sentiment = self.get_macro_sentiment()
            
            # Ağırlıklı ortalama
            sentiment_scores = []
            weights = []
            
            if "error" not in news_sentiment:
                sentiment_scores.append(news_sentiment.get('overall_sentiment', 0))
                weights.append(0.4)  # Haber %40
            
            if "error" not in social_sentiment:
                sentiment_scores.append(social_sentiment.get('overall_sentiment', 0))
                weights.append(0.3)  # Sosyal medya %30
            
            if "error" not in macro_sentiment:
                sentiment_scores.append(macro_sentiment.get('overall_sentiment', 0))
                weights.append(0.3)  # Makro %30
            
            # Genel sentiment skoru
            if sentiment_scores and weights:
                overall_sentiment = np.average(sentiment_scores, weights=weights)
            else:
                overall_sentiment = 0
            
            return {
                "symbol": symbol,
                "overall_sentiment": float(overall_sentiment),
                "sentiment_label": self._get_sentiment_label(overall_sentiment),
                "news_sentiment": news_sentiment,
                "social_sentiment": social_sentiment,
                "macro_sentiment": macro_sentiment,
                "confidence": self._calculate_sentiment_confidence(
                    news_sentiment, social_sentiment, macro_sentiment
                ),
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Kapsamlı sentiment hatası: {e}")
            return {"error": str(e)}
    
    def _calculate_sentiment_confidence(self, news: Dict, social: Dict, macro: Dict) -> str:
        """
        Sentiment güven seviyesini hesaplar
        """
        try:
            valid_sources = 0
            total_sources = 3
            
            if "error" not in news:
                valid_sources += 1
            if "error" not in social:
                valid_sources += 1
            if "error" not in macro:
                valid_sources += 1
            
            confidence_ratio = valid_sources / total_sources
            
            if confidence_ratio >= 0.8:
                return "VERY HIGH"
            elif confidence_ratio >= 0.6:
                return "HIGH"
            elif confidence_ratio >= 0.4:
                return "MEDIUM"
            else:
                return "LOW"
                
        except:
            return "MEDIUM"

# Test fonksiyonu
if __name__ == "__main__":
    # Sentiment analyzer'ı başlat
    analyzer = SentimentAnalyzer()
    
    print("🔍 Sentiment Analizi Testi:")
    print("=" * 50)
    
    # Test hissesi
    symbol = "SISE.IS"
    
    # Kapsamlı sentiment analizi
    print(f"📊 {symbol} için sentiment analizi...")
    sentiment_result = analyzer.get_comprehensive_sentiment(symbol)
    
    if "error" not in sentiment_result:
        print("✅ Sentiment analizi tamamlandı!")
        print(f"🎯 Genel Sentiment: {sentiment_result['sentiment_label']}")
        print(f"📊 Sentiment Skoru: {sentiment_result['overall_sentiment']:.3f}")
        print(f"🎯 Güven Seviyesi: {sentiment_result['confidence']}")
        
        # Haber sentiment
        if "error" not in sentiment_result['news_sentiment']:
            news = sentiment_result['news_sentiment']
            print(f"\n📰 Haber Sentiment:")
            print(f"   Toplam Haber: {news.get('total_articles', 0)}")
            print(f"   Genel Sentiment: {news.get('overall_sentiment', 'N/A')}")
        
        # Sosyal medya sentiment
        if "error" not in sentiment_result['social_sentiment']:
            social = sentiment_result['social_sentiment']
            print(f"\n📱 Sosyal Medya Sentiment:")
            print(f"   Toplam Mention: {social.get('total_mentions', 0)}")
            print(f"   Sentiment: {social.get('sentiment_label', 'N/A')}")
        
        # Makro sentiment
        if "error" not in sentiment_result['macro_sentiment']:
            macro = sentiment_result['macro_sentiment']
            print(f"\n🏛️ Makro Sentiment:")
            print(f"   Sentiment: {macro.get('sentiment_label', 'N/A')}")
            print(f"   Skor: {macro.get('overall_sentiment', 0):.3f}")
    else:
        print(f"❌ Sentiment analizi hatası: {sentiment_result['error']}")
