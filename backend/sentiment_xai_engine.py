"""
PRD v2.0 - Sentiment XAI Engine
FinBERT-TR + Twitter & KAP ODA duygu skoru
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class SentimentXAIEngine:
    """Sentiment analizi ve XAI motoru"""
    
    def __init__(self):
        self.sentiment_cache = {}
        self.xai_cache = {}
        self.news_cache = {}
        self.sentiment_model = None
        
    def analyze_text_sentiment(self, text: str, language: str = 'tr') -> Dict[str, Any]:
        """Metin sentiment analizi"""
        try:
            if not text or len(text.strip()) < 10:
                return {
                    'sentiment_score': 0.5,
                    'sentiment_label': 'NEUTRAL',
                    'confidence': 0.5,
                    'language': language,
                    'error': 'Text too short'
                }
            
            # Basit rule-based sentiment (gerçek FinBERT-TR yerine)
            sentiment_score = self._calculate_rule_based_sentiment(text, language)
            
            # Sentiment label belirle
            if sentiment_score >= 0.7:
                sentiment_label = 'POSITIVE'
            elif sentiment_score <= 0.3:
                sentiment_label = 'NEGATIVE'
            else:
                sentiment_label = 'NEUTRAL'
            
            # Güven skoru
            confidence = abs(sentiment_score - 0.5) * 2  # 0-1 arası
            
            result = {
                'sentiment_score': round(sentiment_score, 3),
                'sentiment_label': sentiment_label,
                'confidence': round(confidence, 3),
                'language': language,
                'text_length': len(text),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Sentiment analizi tamamlandı: {sentiment_label} ({sentiment_score:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Sentiment analizi hatası: {e}")
            return {
                'sentiment_score': 0.5,
                'sentiment_label': 'NEUTRAL',
                'confidence': 0.0,
                'language': language,
                'error': str(e)
            }
    
    def _calculate_rule_based_sentiment(self, text: str, language: str) -> float:
        """Rule-based sentiment skoru hesapla"""
        try:
            text_lower = text.lower()
            
            # Türkçe pozitif kelimeler
            positive_words_tr = {
                'artış', 'yükseliş', 'büyüme', 'kâr', 'kazanç', 'olumlu', 'güçlü',
                'başarılı', 'iyi', 'mükemmel', 'harika', 'süper', 'güzel', 'hoş',
                'faydalı', 'avantajlı', 'karlı', 'verimli', 'etkili', 'başarı'
            }
            
            # Türkçe negatif kelimeler
            negative_words_tr = {
                'düşüş', 'azalış', 'kayıp', 'zarar', 'olumsuz', 'zayıf', 'başarısız',
                'kötü', 'berbat', 'korkunç', 'korkutucu', 'tehlikeli', 'riskli',
                'zararlı', 'dezavantajlı', 'kayıplı', 'verimsiz', 'etkisiz', 'başarısız'
            }
            
            # İngilizce pozitif kelimeler
            positive_words_en = {
                'increase', 'growth', 'profit', 'gain', 'positive', 'strong',
                'successful', 'good', 'excellent', 'great', 'amazing', 'wonderful',
                'beneficial', 'advantageous', 'profitable', 'efficient', 'effective'
            }
            
            # İngilizce negatif kelimeler
            negative_words_en = {
                'decrease', 'decline', 'loss', 'negative', 'weak', 'unsuccessful',
                'bad', 'terrible', 'horrible', 'dangerous', 'risky', 'harmful',
                'disadvantageous', 'unprofitable', 'inefficient', 'ineffective'
            }
            
            # Finansal pozitif kelimeler
            financial_positive = {
                'revenue', 'earnings', 'dividend', 'expansion', 'acquisition',
                'partnership', 'innovation', 'technology', 'digital', 'online',
                'gelir', 'kazanç', 'temettü', 'genişleme', 'satın alma',
                'ortaklık', 'yenilik', 'teknoloji', 'dijital', 'çevrimiçi'
            }
            
            # Finansal negatif kelimeler
            financial_negative = {
                'debt', 'loss', 'bankruptcy', 'crisis', 'recession', 'downturn',
                'borç', 'kayıp', 'iflas', 'kriz', 'durgunluk', 'düşüş'
            }
            
            # Kelime sayılarını hesapla
            positive_count = 0
            negative_count = 0
            
            # Türkçe kelimeler
            if language == 'tr':
                for word in positive_words_tr:
                    if word in text_lower:
                        positive_count += 1
                
                for word in negative_words_tr:
                    if word in text_lower:
                        negative_count += 1
            
            # İngilizce kelimeler
            for word in positive_words_en:
                if word in text_lower:
                    positive_count += 1
            
            for word in negative_words_en:
                if word in text_lower:
                    negative_count += 1
            
            # Finansal kelimeler
            for word in financial_positive:
                if word in text_lower:
                    positive_count += 0.5  # Daha az ağırlık
            
            for word in financial_negative:
                if word in text_lower:
                    negative_count += 0.5  # Daha az ağırlık
            
            # Sentiment skoru hesapla
            total_words = positive_count + negative_count
            
            if total_words == 0:
                return 0.5  # Nötr
            
            # Pozitif oran
            positive_ratio = positive_count / total_words
            
            # Sentiment skoru (0-1 arası)
            sentiment_score = positive_ratio
            
            # Ek faktörler
            # Ünlem işareti sayısı
            exclamation_count = text.count('!')
            if exclamation_count > 0:
                if positive_count > negative_count:
                    sentiment_score += min(0.1, exclamation_count * 0.02)
                else:
                    sentiment_score -= min(0.1, exclamation_count * 0.02)
            
            # Büyük harf kullanımı
            upper_case_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if upper_case_ratio > 0.3:  # %30'dan fazla büyük harf
                if positive_count > negative_count:
                    sentiment_score += 0.05
                else:
                    sentiment_score -= 0.05
            
            # Skoru 0-1 arasında sınırla
            sentiment_score = max(0, min(1, sentiment_score))
            
            return sentiment_score
            
        except Exception as e:
            logger.error(f"Rule-based sentiment hesaplama hatası: {e}")
            return 0.5
    
    def analyze_news_sentiment(self, news_data: List[Dict]) -> Dict[str, Any]:
        """Haber sentiment analizi"""
        try:
            if not news_data:
                return {
                    'overall_sentiment': 0.5,
                    'sentiment_distribution': {},
                    'total_news': 0,
                    'error': 'No news data'
                }
            
            sentiment_scores = []
            sentiment_labels = []
            
            for news in news_data:
                title = news.get('title', '')
                content = news.get('content', '')
                language = news.get('language', 'tr')
                
                # Başlık ve içerik birleştir
                full_text = f"{title} {content}".strip()
                
                # Sentiment analizi
                sentiment_result = self.analyze_text_sentiment(full_text, language)
                
                if 'error' not in sentiment_result:
                    sentiment_scores.append(sentiment_result['sentiment_score'])
                    sentiment_labels.append(sentiment_result['sentiment_label'])
                    
                    # Cache'e kaydet
                    news_id = news.get('id', f"news_{len(sentiment_scores)}")
                    self.news_cache[news_id] = sentiment_result
            
            if not sentiment_scores:
                return {
                    'overall_sentiment': 0.5,
                    'sentiment_distribution': {},
                    'total_news': 0,
                    'error': 'No valid sentiment scores'
                }
            
            # Genel sentiment skoru
            overall_sentiment = np.mean(sentiment_scores)
            
            # Sentiment dağılımı
            sentiment_distribution = {
                'positive': sentiment_labels.count('POSITIVE'),
                'neutral': sentiment_labels.count('NEUTRAL'),
                'negative': sentiment_labels.count('NEGATIVE')
            }
            
            result = {
                'overall_sentiment': round(overall_sentiment, 3),
                'sentiment_distribution': sentiment_distribution,
                'total_news': len(news_data),
                'analyzed_news': len(sentiment_scores),
                'sentiment_scores': sentiment_scores,
                'sentiment_labels': sentiment_labels,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ {len(news_data)} haber analiz edildi, genel sentiment: {overall_sentiment:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Haber sentiment analizi hatası: {e}")
            return {
                'overall_sentiment': 0.5,
                'sentiment_distribution': {},
                'total_news': 0,
                'error': str(e)
            }
    
    def analyze_social_media_sentiment(self, social_data: List[Dict]) -> Dict[str, Any]:
        """Sosyal medya sentiment analizi"""
        try:
            if not social_data:
                return {
                    'overall_sentiment': 0.5,
                    'platform_sentiment': {},
                    'total_posts': 0,
                    'error': 'No social media data'
                }
            
            platform_sentiment = {}
            all_sentiment_scores = []
            
            for post in social_data:
                platform = post.get('platform', 'unknown')
                text = post.get('text', '')
                language = post.get('language', 'tr')
                
                if not text:
                    continue
                
                # Sentiment analizi
                sentiment_result = self.analyze_text_sentiment(text, language)
                
                if 'error' not in sentiment_result:
                    sentiment_score = sentiment_result['sentiment_score']
                    all_sentiment_scores.append(sentiment_score)
                    
                    # Platform bazlı sentiment
                    if platform not in platform_sentiment:
                        platform_sentiment[platform] = []
                    platform_sentiment[platform].append(sentiment_score)
            
            if not all_sentiment_scores:
                return {
                    'overall_sentiment': 0.5,
                    'platform_sentiment': {},
                    'total_posts': 0,
                    'error': 'No valid sentiment scores'
                }
            
            # Genel sentiment
            overall_sentiment = np.mean(all_sentiment_scores)
            
            # Platform bazlı ortalama sentiment
            platform_averages = {}
            for platform, scores in platform_sentiment.items():
                platform_averages[platform] = round(np.mean(scores), 3)
            
            result = {
                'overall_sentiment': round(overall_sentiment, 3),
                'platform_sentiment': platform_averages,
                'total_posts': len(social_data),
                'analyzed_posts': len(all_sentiment_scores),
                'platform_breakdown': platform_sentiment,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ {len(social_data)} sosyal medya postu analiz edildi")
            return result
            
        except Exception as e:
            logger.error(f"❌ Sosyal medya sentiment analizi hatası: {e}")
            return {
                'overall_sentiment': 0.5,
                'platform_sentiment': {},
                'total_posts': 0,
                'error': str(e)
            }
    
    def generate_sentiment_signals(self, symbol: str, 
                                 news_sentiment: Dict = None,
                                 social_sentiment: Dict = None) -> Dict[str, Any]:
        """Sentiment tabanlı sinyaller üret"""
        try:
            signals = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'overall_sentiment_score': 0.5,
                'sentiment_signal': 'NEUTRAL',
                'confidence': 0.5,
                'factors': {},
                'recommendation': 'HOLD'
            }
            
            # Sentiment skorlarını birleştir
            sentiment_scores = []
            weights = []
            
            if news_sentiment and 'overall_sentiment' in news_sentiment:
                news_score = news_sentiment['overall_sentiment']
                sentiment_scores.append(news_score)
                weights.append(0.6)  # Haberler daha ağırlıklı
            
            if social_sentiment and 'overall_sentiment' in social_sentiment:
                social_score = social_sentiment['overall_sentiment']
                sentiment_scores.append(social_score)
                weights.append(0.4)  # Sosyal medya daha az ağırlıklı
            
            if not sentiment_scores:
                return signals
            
            # Ağırlıklı ortalama sentiment
            if len(weights) == len(sentiment_scores):
                overall_score = np.average(sentiment_scores, weights=weights)
            else:
                overall_score = np.mean(sentiment_scores)
            
            signals['overall_sentiment_score'] = round(overall_score, 3)
            
            # Sentiment sinyali
            if overall_score >= 0.7:
                signals['sentiment_signal'] = 'BULLISH'
                signals['recommendation'] = 'BUY'
            elif overall_score <= 0.3:
                signals['sentiment_signal'] = 'BEARISH'
                signals['recommendation'] = 'SELL'
            else:
                signals['sentiment_signal'] = 'NEUTRAL'
                signals['recommendation'] = 'HOLD'
            
            # Güven skoru
            confidence = abs(overall_score - 0.5) * 2  # 0-1 arası
            signals['confidence'] = round(confidence, 3)
            
            # Faktörler
            signals['factors'] = {
                'news_sentiment': news_sentiment.get('overall_sentiment', 0.5) if news_sentiment else 0.5,
                'social_sentiment': social_sentiment.get('overall_sentiment', 0.5) if social_sentiment else 0.5,
                'news_count': news_sentiment.get('total_news', 0) if news_sentiment else 0,
                'social_count': social_sentiment.get('total_posts', 0) if social_sentiment else 0
            }
            
            logger.info(f"✅ {symbol} için sentiment sinyali üretildi: {signals['sentiment_signal']}")
            return signals
            
        except Exception as e:
            logger.error(f"❌ Sentiment sinyal üretme hatası: {e}")
            return {
                'symbol': symbol,
                'sentiment_signal': 'NEUTRAL',
                'error': str(e)
            }
    
    def explain_sentiment_decision(self, sentiment_result: Dict, 
                                 original_text: str = "") -> Dict[str, Any]:
        """Sentiment kararını açıkla (XAI)"""
        try:
            explanation = {
                'sentiment_score': sentiment_result.get('sentiment_score', 0.5),
                'sentiment_label': sentiment_result.get('sentiment_label', 'NEUTRAL'),
                'confidence': sentiment_result.get('confidence', 0.5),
                'explanation': {},
                'key_factors': [],
                'text_analysis': {}
            }
            
            # Sentiment skoruna göre açıklama
            score = sentiment_result.get('sentiment_score', 0.5)
            
            if score >= 0.7:
                explanation['explanation']['overall'] = 'Metin genel olarak olumlu duygular içeriyor'
                explanation['explanation']['reason'] = 'Pozitif kelimeler ve ifadeler baskın'
                explanation['key_factors'].append('Yüksek pozitif kelime oranı')
                explanation['key_factors'].append('Olumlu finansal terimler')
                
            elif score <= 0.3:
                explanation['explanation']['overall'] = 'Metin genel olarak olumsuz duygular içeriyor'
                explanation['explanation']['reason'] = 'Negatif kelimeler ve ifadeler baskın'
                explanation['key_factors'].append('Yüksek negatif kelime oranı')
                explanation['key_factors'].append('Olumsuz finansal terimler')
                
            else:
                explanation['explanation']['overall'] = 'Metin nötr duygular içeriyor'
                explanation['explanation']['reason'] = 'Pozitif ve negatif kelimeler dengeli'
                explanation['key_factors'].append('Dengeli kelime dağılımı')
                explanation['key_factors'].append('Kararsız duygu ifadeleri')
            
            # Güven skoru açıklaması
            confidence = sentiment_result.get('confidence', 0.5)
            if confidence >= 0.8:
                explanation['explanation']['confidence'] = 'Yüksek güven - net duygu ifadeleri'
            elif confidence >= 0.6:
                explanation['explanation']['confidence'] = 'Orta güven - belirgin duygu ifadeleri'
            else:
                explanation['explanation']['confidence'] = 'Düşük güven - belirsiz duygu ifadeleri'
            
            # Metin analizi
            if original_text:
                explanation['text_analysis'] = {
                    'length': len(original_text),
                    'word_count': len(original_text.split()),
                    'has_exclamation': '!' in original_text,
                    'has_question': '?' in original_text,
                    'upper_case_ratio': sum(1 for c in original_text if c.isupper()) / len(original_text)
                }
            
            # Öneriler
            if score >= 0.7:
                explanation['recommendation'] = 'Pozitif sentiment - alım fırsatı olabilir'
            elif score <= 0.3:
                explanation['recommendation'] = 'Negatif sentiment - satım fırsatı olabilir'
            else:
                explanation['recommendation'] = 'Nötr sentiment - mevcut pozisyonu koru'
            
            logger.info(f"✅ Sentiment kararı açıklandı: {explanation['sentiment_label']}")
            return explanation
            
        except Exception as e:
            logger.error(f"❌ Sentiment açıklama hatası: {e}")
            return {
                'sentiment_score': 0.5,
                'sentiment_label': 'NEUTRAL',
                'error': str(e)
            }
    
    def get_sentiment_summary(self, symbol: str) -> Dict[str, Any]:
        """Sentiment özeti"""
        try:
            # Cache'den veri topla
            news_sentiments = [v for v in self.news_cache.values() if 'error' not in v]
            
            if not news_sentiments:
                return {
                    'symbol': symbol,
                    'status': 'No sentiment data available',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Sentiment istatistikleri
            sentiment_scores = [s['sentiment_score'] for s in news_sentiments]
            sentiment_labels = [s['sentiment_label'] for s in news_sentiments]
            
            summary = {
                'symbol': symbol,
                'total_analyses': len(news_sentiments),
                'average_sentiment': round(np.mean(sentiment_scores), 3),
                'sentiment_volatility': round(np.std(sentiment_scores), 3),
                'sentiment_distribution': {
                    'positive': sentiment_labels.count('POSITIVE'),
                    'neutral': sentiment_labels.count('NEUTRAL'),
                    'negative': sentiment_labels.count('NEGATIVE')
                },
                'recent_sentiment': sentiment_scores[-5:] if len(sentiment_scores) >= 5 else sentiment_scores,
                'sentiment_trend': self._calculate_sentiment_trend(sentiment_scores),
                'timestamp': datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Sentiment özet hatası: {e}")
            return {
                'symbol': symbol,
                'error': str(e)
            }
    
    def _calculate_sentiment_trend(self, sentiment_scores: List[float]) -> str:
        """Sentiment trend hesapla"""
        try:
            if len(sentiment_scores) < 3:
                return 'INSUFFICIENT_DATA'
            
            # Son 3 skorun trendi
            recent_scores = sentiment_scores[-3:]
            
            if recent_scores[2] > recent_scores[1] > recent_scores[0]:
                return 'IMPROVING'
            elif recent_scores[2] < recent_scores[1] < recent_scores[0]:
                return 'DETERIORATING'
            else:
                return 'STABLE'
                
        except Exception as e:
            logger.error(f"Trend hesaplama hatası: {e}")
            return 'UNKNOWN'

# Test fonksiyonu
if __name__ == "__main__":
    print("🧪 Sentiment XAI Engine Test Ediliyor...")
    
    engine = SentimentXAIEngine()
    
    # Test metinleri
    test_texts = [
        "Şirket kârlarında artış yaşanıyor ve büyüme devam ediyor!",
        "Finansal kriz ve ekonomik durgunluk endişeleri artıyor.",
        "Piyasa dengeli seyrediyor, önemli bir değişiklik yok.",
        "Yeni teknoloji yatırımları ile dijital dönüşüm hızlanıyor!",
        "Borç oranları yükseliyor ve risk faktörleri artıyor."
    ]
    
    print("\n📝 Metin Sentiment Analizi:")
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Metin: {text}")
        sentiment = engine.analyze_text_sentiment(text, 'tr')
        print(f"   Sentiment: {sentiment['sentiment_label']} ({sentiment['sentiment_score']:.3f})")
        print(f"   Güven: {sentiment['confidence']:.3f}")
        
        # XAI açıklama
        explanation = engine.explain_sentiment_decision(sentiment, text)
        print(f"   Açıklama: {explanation['explanation']['overall']}")
        print(f"   Öneri: {explanation['recommendation']}")
    
    # Mock haber verisi
    print("\n📰 Haber Sentiment Analizi:")
    mock_news = [
        {'id': '1', 'title': 'Şirket kârları artıyor', 'content': 'Güçlü büyüme devam ediyor', 'language': 'tr'},
        {'id': '2', 'title': 'Ekonomik riskler artıyor', 'content': 'Durgunluk endişeleri', 'language': 'tr'},
        {'id': '3', 'title': 'Piyasa dengeli', 'content': 'Önemli değişiklik yok', 'language': 'tr'}
    ]
    
    news_sentiment = engine.analyze_news_sentiment(mock_news)
    print(f"   Genel Haber Sentiment: {news_sentiment['overall_sentiment']:.3f}")
    print(f"   Dağılım: {news_sentiment['sentiment_distribution']}")
    
    # Mock sosyal medya verisi
    print("\n📱 Sosyal Medya Sentiment Analizi:")
    mock_social = [
        {'platform': 'twitter', 'text': 'Harika bir yatırım fırsatı!', 'language': 'tr'},
        {'platform': 'twitter', 'text': 'Piyasa çok riskli', 'language': 'tr'},
        {'platform': 'instagram', 'text': 'Finansal başarı hikayesi', 'language': 'tr'}
    ]
    
    social_sentiment = engine.analyze_social_media_sentiment(mock_social)
    print(f"   Genel Sosyal Medya Sentiment: {social_sentiment['overall_sentiment']:.3f}")
    print(f"   Platform Sentiment: {social_sentiment['platform_sentiment']}")
    
    # Sentiment sinyali üret
    print("\n🎯 Sentiment Sinyali:")
    signal = engine.generate_sentiment_signals('SISE.IS', news_sentiment, social_sentiment)
    print(f"   Sinyal: {signal['sentiment_signal']}")
    print(f"   Öneri: {signal['recommendation']}")
    print(f"   Güven: {signal['confidence']:.3f}")
    
    # Sentiment özeti
    print("\n📊 Sentiment Özeti:")
    summary = engine.get_sentiment_summary('SISE.IS')
    print(f"   Toplam Analiz: {summary['total_analyses']}")
    print(f"   Ortalama Sentiment: {summary['average_sentiment']:.3f}")
    print(f"   Trend: {summary['sentiment_trend']}")
    
    print("\n✅ Test tamamlandı!")
