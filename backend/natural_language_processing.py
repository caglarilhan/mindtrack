"""
Natural Language Processing - Sprint 14: Advanced Machine Learning & AI Engine

Bu modül, FinBERT-TR, sentiment analysis ve text processing kullanarak
finansal haber, sosyal medya ve KAP ODA verilerini analiz eder.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
import json
import logging
import re
from collections import Counter
import hashlib

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TextDocument:
    """Metin dokümanı"""
    doc_id: str
    source: str  # news, social_media, kap_oda, twitter, etc.
    content: str
    title: Optional[str] = None
    author: Optional[str] = None
    timestamp: Optional[datetime] = None
    language: str = "tr"
    metadata: Dict[str, Any] = None
    processed: bool = False

@dataclass
class SentimentResult:
    """Sentiment analiz sonucu"""
    doc_id: str
    timestamp: datetime
    positive_score: float  # 0-1 arası pozitif skor
    negative_score: float  # 0-1 arası negatif skor
    neutral_score: float  # 0-1 arası nötr skor
    compound_score: float  # -1 ile +1 arası bileşik skor
    sentiment_label: str  # positive, negative, neutral
    confidence: float  # 0-1 arası güven skoru
    key_phrases: List[str] = None  # Anahtar ifadeler
    entities: List[str] = None  # Varlık isimleri
    topics: List[str] = None  # Konular

@dataclass
class FinancialEntity:
    """Finansal varlık"""
    entity_id: str
    name: str
    type: str  # company, index, currency, commodity, etc.
    symbol: Optional[str] = None
    sector: Optional[str] = None
    market_cap: Optional[float] = None
    country: str = "TR"
    aliases: List[str] = None  # Alternatif isimler
    created_at: datetime = None

@dataclass
class NewsEvent:
    """Haber olayı"""
    event_id: str
    title: str
    summary: str
    content: str
    source: str
    timestamp: datetime
    sentiment_score: float
    impact_score: float  # 0-10 arası etki skoru
    affected_entities: List[str] = None
    event_type: str = "general"  # earnings, merger, regulation, etc.
    market_reaction: Optional[str] = None

class NaturalLanguageProcessing:
    """Natural Language Processing ana sınıfı"""
    
    def __init__(self):
        self.text_documents = {}
        self.sentiment_results = {}
        self.financial_entities = {}
        self.news_events = {}
        self.text_processors = {}
        self.sentiment_models = {}
        self.entity_extractors = {}
        self.topic_models = {}
        
        # Varsayılan finansal varlıkları ekle
        self._add_default_financial_entities()
        
        # Text processor'ları tanımla
        self._define_text_processors()
        
        # Sentiment model'lerini tanımla
        self._define_sentiment_models()
        
        # Entity extractor'ları tanımla
        self._define_entity_extractors()
        
        # Topic model'lerini tanımla
        self._define_topic_models()
    
    def _add_default_financial_entities(self):
        """Varsayılan finansal varlıkları ekle"""
        default_entities = [
            {
                "entity_id": "SISE",
                "name": "Sisecam",
                "type": "company",
                "symbol": "SISE.IS",
                "sector": "materials",
                "market_cap": 15000000000,
                "aliases": ["Şişe Cam", "Sisecam", "SISE"]
            },
            {
                "entity_id": "EREGL",
                "name": "Ereğli Demir ve Çelik",
                "type": "company",
                "symbol": "EREGL.IS",
                "sector": "materials",
                "market_cap": 25000000000,
                "aliases": ["Ereğli", "Erdemir", "EREGL"]
            },
            {
                "entity_id": "TUPRS",
                "name": "Tüpraş",
                "type": "company",
                "symbol": "TUPRS.IS",
                "sector": "energy",
                "market_cap": 80000000000,
                "aliases": ["Tüpraş", "TUPRS", "Tupras"]
            },
            {
                "entity_id": "GARAN",
                "name": "Garanti Bankası",
                "type": "company",
                "symbol": "GARAN.IS",
                "sector": "financials",
                "market_cap": 120000000000,
                "aliases": ["Garanti", "GARAN", "Garanti Bank"]
            },
            {
                "entity_id": "AKBNK",
                "name": "Akbank",
                "type": "company",
                "symbol": "AKBNK.IS",
                "sector": "financials",
                "market_cap": 100000000000,
                "aliases": ["Akbank", "AKBNK", "Ak Bank"]
            },
            {
                "entity_id": "XU030",
                "name": "BIST 30",
                "type": "index",
                "symbol": "XU030.IS",
                "sector": "index",
                "aliases": ["BIST30", "BIST 30", "XU030"]
            },
            {
                "entity_id": "USDTRY",
                "name": "US Dollar / Turkish Lira",
                "type": "currency",
                "symbol": "USDTRY",
                "sector": "forex",
                "aliases": ["USD/TRY", "Dolar", "Dollar"]
            },
            {
                "entity_id": "XAUUSD",
                "name": "Gold / US Dollar",
                "type": "commodity",
                "symbol": "XAUUSD",
                "sector": "commodities",
                "aliases": ["Altın", "Gold", "XAU/USD"]
            }
        ]
        
        for entity_data in default_entities:
            entity = FinancialEntity(
                entity_id=entity_data["entity_id"],
                name=entity_data["name"],
                type=entity_data["type"],
                symbol=entity_data.get("symbol"),
                sector=entity_data.get("sector"),
                market_cap=entity_data.get("market_cap"),
                aliases=entity_data.get("aliases", []),
                created_at=datetime.now()
            )
            self.financial_entities[entity.entity_id] = entity
    
    def _define_text_processors(self):
        """Text processor'ları tanımla"""
        # Türkçe text preprocessing
        def turkish_text_processor(text: str) -> str:
            """Türkçe metin ön işleme"""
            try:
                # Küçük harfe çevir
                text = text.lower()
                
                # Türkçe karakterleri normalize et
                text = text.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
                
                # Sayıları kaldır
                text = re.sub(r'\d+', '', text)
                
                # Özel karakterleri kaldır
                text = re.sub(r'[^\w\s]', ' ', text)
                
                # Fazla boşlukları temizle
                text = re.sub(r'\s+', ' ', text).strip()
                
                return text
            
            except Exception as e:
                logger.error(f"Error in Turkish text processing: {e}")
                return text
        
        # İngilizce text preprocessing
        def english_text_processor(text: str) -> str:
            """İngilizce metin ön işleme"""
            try:
                # Küçük harfe çevir
                text = text.lower()
                
                # Sayıları kaldır
                text = re.sub(r'\d+', '', text)
                
                # Özel karakterleri kaldır
                text = re.sub(r'[^\w\s]', '', text)
                
                # Fazla boşlukları temizle
                text = re.sub(r'\s+', ' ', text).strip()
                
                return text
            
            except Exception as e:
                logger.error(f"Error in English text processing: {e}")
                return text
        
        self.text_processors = {
            "tr": turkish_text_processor,
            "en": english_text_processor
        }
    
    def _define_sentiment_models(self):
        """Sentiment model'lerini tanımla"""
        # Basit rule-based sentiment analyzer (FinBERT simülasyonu)
        def rule_based_sentiment_analyzer(text: str, language: str = "tr") -> Dict[str, float]:
            """Rule-based sentiment analyzer"""
            try:
                # Türkçe pozitif kelimeler
                turkish_positive = [
                    "artış", "yükseliş", "büyüme", "kâr", "kazanç", "olumlu", "iyi", "güçlü",
                    "başarılı", "yüksek", "iyileşme", "gelişme", "büyüme", "artış", "yükseliş"
                ]
                
                # Türkçe negatif kelimeler
                turkish_negative = [
                    "düşüş", "azalış", "kayıp", "zarar", "olumsuz", "kötü", "zayıf",
                    "başarısız", "düşük", "kötüleşme", "gerileme", "küçülme", "düşüş", "azalış"
                ]
                
                # İngilizce pozitif kelimeler
                english_positive = [
                    "increase", "rise", "growth", "profit", "gain", "positive", "good", "strong",
                    "successful", "high", "improvement", "development", "growth", "increase", "rise"
                ]
                
                # İngilizce negatif kelimeler
                english_negative = [
                    "decrease", "fall", "loss", "negative", "bad", "weak", "unsuccessful",
                    "low", "deterioration", "decline", "shrink", "decrease", "fall"
                ]
                
                # Finansal pozitif terimler
                financial_positive = [
                    "bullish", "rally", "surge", "jump", "climb", "soar", "leap", "boost",
                    "bullish", "rally", "surge", "jump", "climb", "soar", "leap", "boost"
                ]
                
                # Finansal negatif terimler
                financial_negative = [
                    "bearish", "crash", "plunge", "drop", "fall", "decline", "slump", "crash",
                    "bearish", "crash", "plunge", "drop", "fall", "decline", "slump", "crash"
                ]
                
                # Dil seçimi
                if language == "tr":
                    positive_words = turkish_positive
                    negative_words = turkish_negative
                else:
                    positive_words = english_positive
                    negative_words = english_negative
                
                # Finansal terimleri ekle
                positive_words.extend(financial_positive)
                negative_words.extend(financial_negative)
                
                # Kelime sayılarını hesapla
                words = text.lower().split()
                positive_count = sum(1 for word in words if word in positive_words)
                negative_count = sum(1 for word in words if word in negative_words)
                total_words = len(words)
                
                if total_words == 0:
                    return {
                        "positive_score": 0.33,
                        "negative_score": 0.33,
                        "neutral_score": 0.34,
                        "compound_score": 0.0
                    }
                
                # Skorları hesapla
                positive_score = positive_count / total_words
                negative_score = negative_count / total_words
                neutral_score = 1 - positive_score - negative_score
                
                # Compound score (-1 ile +1 arası)
                compound_score = positive_score - negative_score
                compound_score = max(-1.0, min(1.0, compound_score))
                
                return {
                    "positive_score": positive_score,
                    "negative_score": negative_score,
                    "neutral_score": neutral_score,
                    "compound_score": compound_score
                }
            
            except Exception as e:
                logger.error(f"Error in rule-based sentiment analysis: {e}")
                return {
                    "positive_score": 0.33,
                    "negative_score": 0.33,
                    "neutral_score": 0.34,
                    "compound_score": 0.0
                }
        
        self.sentiment_models = {
            "rule_based": rule_based_sentiment_analyzer
        }
    
    def _define_entity_extractors(self):
        """Entity extractor'ları tanımla"""
        def financial_entity_extractor(text: str) -> List[str]:
            """Finansal varlık çıkarıcı"""
            try:
                extracted_entities = []
                
                # Tüm finansal varlıkları kontrol et
                for entity_id, entity in self.financial_entities.items():
                    # Ana ismi kontrol et
                    if entity.name.lower() in text.lower():
                        extracted_entities.append(entity_id)
                        continue
                    
                    # Sembolü kontrol et
                    if entity.symbol and entity.symbol.lower() in text.lower():
                        extracted_entities.append(entity_id)
                        continue
                    
                    # Alternatif isimleri kontrol et
                    for alias in entity.aliases:
                        if alias.lower() in text.lower():
                            extracted_entities.append(entity_id)
                            break
                
                return list(set(extracted_entities))  # Duplicate'ları kaldır
            
            except Exception as e:
                logger.error(f"Error in financial entity extraction: {e}")
                return []
        
        self.entity_extractors = {
            "financial": financial_entity_extractor
        }
    
    def _define_topic_models(self):
        """Topic model'lerini tanımla"""
        def simple_topic_extractor(text: str) -> List[str]:
            """Basit topic extractor"""
            try:
                topics = []
                
                # Finansal topic anahtar kelimeleri
                topic_keywords = {
                    "earnings": ["kâr", "gelir", "ciro", "profit", "revenue", "earnings"],
                    "dividend": ["temettü", "dividend", "pay", "payment"],
                    "merger": ["birleşme", "devralma", "merger", "acquisition", "takeover"],
                    "regulation": ["düzenleme", "regülasyon", "regulation", "law", "rule"],
                    "market": ["piyasa", "borsa", "market", "trading", "exchange"],
                    "economy": ["ekonomi", "economy", "gdp", "inflation", "interest"],
                    "technology": ["teknoloji", "technology", "digital", "software", "ai"],
                    "energy": ["enerji", "energy", "oil", "gas", "renewable"],
                    "healthcare": ["sağlık", "healthcare", "medical", "pharma", "biotech"],
                    "finance": ["finans", "finance", "banking", "insurance", "credit"]
                }
                
                text_lower = text.lower()
                
                for topic, keywords in topic_keywords.items():
                    if any(keyword in text_lower for keyword in keywords):
                        topics.append(topic)
                
                return topics
            
            except Exception as e:
                logger.error(f"Error in topic extraction: {e}")
                return []
        
        self.topic_models = {
            "simple": simple_topic_extractor
        }
    
    def add_text_document(self, source: str, content: str, title: Optional[str] = None,
                         author: Optional[str] = None, timestamp: Optional[datetime] = None,
                         language: str = "tr", metadata: Optional[Dict[str, Any]] = None) -> str:
        """Metin dokümanı ekle"""
        try:
            doc_id = f"DOC_{source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
            
            document = TextDocument(
                doc_id=doc_id,
                source=source,
                content=content,
                title=title,
                author=author,
                timestamp=timestamp or datetime.now(),
                language=language,
                metadata=metadata or {}
            )
            
            self.text_documents[doc_id] = document
            logger.info(f"Text document added: {doc_id}")
            
            return doc_id
        
        except Exception as e:
            logger.error(f"Error adding text document: {e}")
            return None
    
    def preprocess_text(self, text: str, language: str = "tr") -> str:
        """Metni ön işle"""
        try:
            processor = self.text_processors.get(language)
            if processor:
                return processor(text)
            else:
                logger.warning(f"No text processor found for language: {language}")
                return text
        
        except Exception as e:
            logger.error(f"Error preprocessing text: {e}")
            return text
    
    def analyze_sentiment(self, doc_id: str, model_name: str = "rule_based") -> Optional[SentimentResult]:
        """Sentiment analizi yap"""
        try:
            if doc_id not in self.text_documents:
                logger.error(f"Document {doc_id} not found")
                return None
            
            document = self.text_documents[doc_id]
            sentiment_model = self.sentiment_models.get(model_name)
            
            if not sentiment_model:
                logger.error(f"Sentiment model {model_name} not found")
                return None
            
            # Metni ön işle
            processed_text = self.preprocess_text(document.content, document.language)
            
            # Sentiment analizi yap
            sentiment_scores = sentiment_model(processed_text, document.language)
            
            # Sentiment label belirle
            compound_score = sentiment_scores["compound_score"]
            if compound_score > 0.1:
                sentiment_label = "positive"
            elif compound_score < -0.1:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
            
            # Güven skoru hesapla (basit)
            confidence = abs(compound_score)
            
            # Anahtar ifadeler çıkar
            key_phrases = self._extract_key_phrases(processed_text)
            
            # Varlıkları çıkar
            entities = self._extract_entities(processed_text)
            
            # Konuları çıkar
            topics = self._extract_topics(processed_text)
            
            # Sentiment sonucu oluştur
            sentiment_result = SentimentResult(
                doc_id=doc_id,
                timestamp=datetime.now(),
                positive_score=sentiment_scores["positive_score"],
                negative_score=sentiment_scores["negative_score"],
                neutral_score=sentiment_scores["neutral_score"],
                compound_score=compound_score,
                sentiment_label=sentiment_label,
                confidence=confidence,
                key_phrases=key_phrases,
                entities=entities,
                topics=topics
            )
            
            self.sentiment_results[doc_id] = sentiment_result
            
            # Dokümanı işlenmiş olarak işaretle
            document.processed = True
            
            logger.info(f"Sentiment analysis completed: {doc_id} - {sentiment_label}")
            return sentiment_result
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return None
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Anahtar ifadeleri çıkar"""
        try:
            # Basit anahtar ifade çıkarımı
            words = text.split()
            if len(words) < 3:
                return []
            
            # En sık geçen 2-3 kelimelik kombinasyonları bul
            phrases = []
            for i in range(len(words) - 1):
                phrase = " ".join(words[i:i+2])
                if len(phrase) > 5:  # Minimum uzunluk
                    phrases.append(phrase)
            
            # En sık geçenleri seç
            phrase_counts = Counter(phrases)
            top_phrases = [phrase for phrase, count in phrase_counts.most_common(5)]
            
            return top_phrases
        
        except Exception as e:
            logger.error(f"Error extracting key phrases: {e}")
            return []
    
    def _extract_entities(self, text: str) -> List[str]:
        """Varlıkları çıkar"""
        try:
            entity_extractor = self.entity_extractors.get("financial")
            if entity_extractor:
                return entity_extractor(text)
            return []
        
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    def _extract_topics(self, text: str) -> List[str]:
        """Konuları çıkar"""
        try:
            topic_extractor = self.topic_models.get("simple")
            if topic_extractor:
                return topic_extractor(text)
            return []
        
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return []
    
    def create_news_event(self, title: str, content: str, source: str, 
                         sentiment_score: float, impact_score: float = 5.0) -> str:
        """Haber olayı oluştur"""
        try:
            event_id = f"EVENT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(title.encode()).hexdigest()[:8]}"
            
            # Özet oluştur (basit)
            summary = content[:200] + "..." if len(content) > 200 else content
            
            # Etkilenen varlıkları çıkar
            affected_entities = self._extract_entities(content)
            
            # Olay tipini belirle
            event_type = self._classify_event_type(title, content)
            
            # Market reaction tahmini
            market_reaction = self._predict_market_reaction(sentiment_score, impact_score)
            
            news_event = NewsEvent(
                event_id=event_id,
                title=title,
                summary=summary,
                content=content,
                source=source,
                timestamp=datetime.now(),
                sentiment_score=sentiment_score,
                impact_score=impact_score,
                affected_entities=affected_entities,
                event_type=event_type,
                market_reaction=market_reaction
            )
            
            self.news_events[event_id] = news_event
            logger.info(f"News event created: {event_id}")
            
            return event_id
        
        except Exception as e:
            logger.error(f"Error creating news event: {e}")
            return None
    
    def _classify_event_type(self, title: str, content: str) -> str:
        """Olay tipini sınıflandır"""
        try:
            text = (title + " " + content).lower()
            
            if any(word in text for word in ["kâr", "gelir", "profit", "earnings", "revenue"]):
                return "earnings"
            elif any(word in text for word in ["birleşme", "devralma", "merger", "acquisition"]):
                return "merger"
            elif any(word in text for word in ["düzenleme", "regülasyon", "regulation", "law"]):
                return "regulation"
            elif any(word in text for word in ["yeni ürün", "product", "launch", "innovation"]):
                return "product_launch"
            elif any(word in text for word in ["CEO", "yönetim", "management", "leadership"]):
                return "management_change"
            else:
                return "general"
        
        except Exception as e:
            logger.error(f"Error classifying event type: {e}")
            return "general"
    
    def _predict_market_reaction(self, sentiment_score: float, impact_score: float) -> str:
        """Market reaction tahmini"""
        try:
            # Sentiment ve impact skorlarına göre market reaction tahmini
            if sentiment_score > 0.3 and impact_score > 7:
                return "strong_positive"
            elif sentiment_score > 0.1 and impact_score > 5:
                return "positive"
            elif sentiment_score < -0.3 and impact_score > 7:
                return "strong_negative"
            elif sentiment_score < -0.1 and impact_score > 5:
                return "negative"
            else:
                return "neutral"
        
        except Exception as e:
            logger.error(f"Error predicting market reaction: {e}")
            return "neutral"
    
    def get_sentiment_summary(self, time_period: str = "1d") -> Dict[str, Any]:
        """Sentiment özeti getir"""
        try:
            # Zaman aralığını hesapla
            end_time = datetime.now()
            if time_period == "1d":
                start_time = end_time - timedelta(days=1)
            elif time_period == "1w":
                start_time = end_time - timedelta(weeks=1)
            elif time_period == "1m":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(days=1)
            
            # Zaman aralığındaki sentiment sonuçlarını filtrele
            period_results = [
                result for result in self.sentiment_results.values()
                if start_time <= result.timestamp <= end_time
            ]
            
            if not period_results:
                return {
                    "period": time_period,
                    "total_documents": 0,
                    "sentiment_distribution": {},
                    "average_scores": {},
                    "top_entities": [],
                    "top_topics": []
                }
            
            # Sentiment dağılımı
            sentiment_counts = Counter([result.sentiment_label for result in period_results])
            
            # Ortalama skorlar
            avg_positive = np.mean([result.positive_score for result in period_results])
            avg_negative = np.mean([result.negative_score for result in period_results])
            avg_neutral = np.mean([result.neutral_score for result in period_results])
            avg_compound = np.mean([result.compound_score for result in period_results])
            
            # En çok geçen varlıklar
            all_entities = []
            for result in period_results:
                if result.entities:
                    all_entities.extend(result.entities)
            entity_counts = Counter(all_entities)
            top_entities = [entity for entity, count in entity_counts.most_common(5)]
            
            # En çok geçen konular
            all_topics = []
            for result in period_results:
                if result.topics:
                    all_topics.extend(result.topics)
            topic_counts = Counter(all_topics)
            top_topics = [topic for topic, count in topic_counts.most_common(5)]
            
            return {
                "period": time_period,
                "total_documents": len(period_results),
                "sentiment_distribution": dict(sentiment_counts),
                "average_scores": {
                    "positive": avg_positive,
                    "negative": avg_negative,
                    "neutral": avg_neutral,
                    "compound": avg_compound
                },
                "top_entities": top_entities,
                "top_topics": top_topics
            }
        
        except Exception as e:
            logger.error(f"Error getting sentiment summary: {e}")
            return {}
    
    def get_nlp_summary(self) -> Dict[str, Any]:
        """NLP özeti getir"""
        try:
            summary = {
                "total_documents": len(self.text_documents),
                "total_sentiment_results": len(self.sentiment_results),
                "total_news_events": len(self.news_events),
                "total_financial_entities": len(self.financial_entities),
                "document_sources": {},
                "sentiment_distribution": {},
                "event_types": {},
                "entity_types": {}
            }
            
            # Doküman kaynakları
            source_counts = Counter([doc.source for doc in self.text_documents.values()])
            summary["document_sources"] = dict(source_counts)
            
            # Sentiment dağılımı
            if self.sentiment_results:
                sentiment_counts = Counter([result.sentiment_label for result in self.sentiment_results.values()])
                summary["sentiment_distribution"] = dict(sentiment_counts)
            
            # Olay tipleri
            if self.news_events:
                event_type_counts = Counter([event.event_type for event in self.news_events.values()])
                summary["event_types"] = dict(event_type_counts)
            
            # Varlık tipleri
            entity_type_counts = Counter([entity.type for entity in self.financial_entities.values()])
            summary["entity_types"] = dict(entity_type_counts)
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting NLP summary: {e}")
            return {}


def test_natural_language_processing():
    """Natural Language Processing test fonksiyonu"""
    print("\n🧪 Natural Language Processing Test Başlıyor...")
    
    # NLP modülü oluştur
    nlp = NaturalLanguageProcessing()
    
    print("✅ NLP modülü oluşturuldu")
    print(f"📊 Toplam finansal varlık: {len(nlp.financial_entities)}")
    
    # Test dokümanları ekle
    print("\n📊 Test Dokümanları Ekleme:")
    
    # Türkçe haber
    turkish_news = """
    Sisecam'da güçlü kâr artışı! Şirket, 2024 yılının ilk çeyreğinde 
    %25 oranında gelir artışı kaydetti. Bu gelişme, piyasada olumlu 
    karşılandı ve hisse senedi %8 yükseldi. Analistler, şirketin 
    güçlü performansını sürdüreceğini öngörüyor.
    """
    
    doc1_id = nlp.add_text_document(
        source="hurriyet",
        content=turkish_news,
        title="Sisecam'da Güçlü Kâr Artışı",
        language="tr"
    )
    
    if doc1_id:
        print(f"   ✅ Türkçe haber eklendi: {doc1_id}")
    
    # İngilizce haber
    english_news = """
    Eregli Steel reports strong earnings growth in Q1 2024. The company 
    achieved 20% revenue increase and positive market reaction. 
    Analysts expect continued strong performance from the steel sector.
    """
    
    doc2_id = nlp.add_text_document(
        source="bloomberg",
        content=english_news,
        title="Eregli Steel Strong Earnings",
        language="en"
    )
    
    if doc2_id:
        print(f"   ✅ İngilizce haber eklendi: {doc2_id}")
    
    # Negatif haber
    negative_news = """
    Tüpraş'ta beklenmeyen zarar! Şirket, operasyonel sorunlar nedeniyle 
    %15 oranında gelir kaybı yaşadı. Bu gelişme piyasada olumsuz 
    karşılandı ve hisse senedi %12 düştü.
    """
    
    doc3_id = nlp.add_text_document(
        source="milliyet",
        content=negative_news,
        title="Tüpraş'ta Beklenmeyen Zarar",
        language="tr"
    )
    
    if doc3_id:
        print(f"   ✅ Negatif haber eklendi: {doc3_id}")
    
    # Sentiment analizi
    print("\n📊 Sentiment Analizi Testi:")
    
    for doc_id in [doc1_id, doc2_id, doc3_id]:
        if doc_id:
            sentiment_result = nlp.analyze_sentiment(doc_id)
            if sentiment_result:
                print(f"   📊 {doc_id}: {sentiment_result.sentiment_label} (confidence: {sentiment_result.confidence:.3f})")
                print(f"      📊 Compound Score: {sentiment_result.compound_score:.3f}")
                print(f"      📊 Entities: {sentiment_result.entities}")
                print(f"      📊 Topics: {sentiment_result.topics}")
    
    # Haber olayları oluştur
    print("\n📊 Haber Olayları Testi:")
    
    event1_id = nlp.create_news_event(
        title="Sisecam Güçlü Kâr Açıkladı",
        content=turkish_news,
        source="hurriyet",
        sentiment_score=0.7,
        impact_score=8.0
    )
    
    if event1_id:
        print(f"   ✅ Haber olayı oluşturuldu: {event1_id}")
    
    # Sentiment özeti
    print("\n📊 Sentiment Özeti Testi:")
    sentiment_summary = nlp.get_sentiment_summary("1d")
    
    if sentiment_summary:
        print(f"   ✅ Sentiment özeti alındı")
        print(f"   📊 Toplam doküman: {sentiment_summary['total_documents']}")
        print(f"   📊 Sentiment dağılımı: {sentiment_summary['sentiment_distribution']}")
        print(f"   📊 Ortalama compound score: {sentiment_summary['average_scores']['compound']:.3f}")
        print(f"   📊 En çok geçen varlıklar: {sentiment_summary['top_entities']}")
        print(f"   📊 En çok geçen konular: {sentiment_summary['top_topics']}")
    
    # NLP özeti
    print("\n📊 NLP Özeti Testi:")
    nlp_summary = nlp.get_nlp_summary()
    
    if nlp_summary:
        print(f"   ✅ NLP özeti alındı")
        print(f"   📊 Toplam doküman: {nlp_summary['total_documents']}")
        print(f"   📊 Toplam sentiment sonucu: {nlp_summary['total_sentiment_results']}")
        print(f"   📊 Toplam haber olayı: {nlp_summary['total_news_events']}")
        print(f"   📊 Doküman kaynakları: {nlp_summary['document_sources']}")
        print(f"   📊 Sentiment dağılımı: {nlp_summary['sentiment_distribution']}")
    
    print("\n✅ Natural Language Processing Test Tamamlandı!")


if __name__ == "__main__":
    test_natural_language_processing()
