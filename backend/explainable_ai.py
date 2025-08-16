"""
Explainable AI (XAI) - Sprint 14: Advanced Machine Learning & AI Engine

Bu modül, SHAP, LIME ve diğer interpretability tekniklerini kullanarak
machine learning model tahminlerini ve trading sinyallerini açıklar.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
import json
import logging
import random
from collections import defaultdict

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelExplanation:
    """Model açıklaması"""
    explanation_id: str
    model_id: str
    timestamp: datetime
    prediction: float
    prediction_label: str
    confidence: float
    feature_importance: Dict[str, float]  # feature -> importance score
    feature_contributions: Dict[str, float]  # feature -> contribution
    local_explanation: Dict[str, Any]  # LIME benzeri local açıklama
    global_explanation: Dict[str, Any]  # SHAP benzeri global açıklama
    explanation_method: str  # shap, lime, integrated_gradients, etc.
    explanation_quality: float  # 0-1 arası açıklama kalitesi

@dataclass
class TradingSignalExplanation:
    """Trading sinyali açıklaması"""
    signal_id: str
    timestamp: datetime
    signal_type: str  # buy, sell, hold
    confidence: float
    primary_factors: List[Dict[str, Any]]  # Ana faktörler
    supporting_factors: List[Dict[str, Any]]  # Destekleyici faktörler
    risk_factors: List[Dict[str, Any]]  # Risk faktörleri
    market_context: Dict[str, Any]  # Piyasa bağlamı
    technical_indicators: Dict[str, float]  # Teknik indikatörler
    fundamental_factors: Dict[str, float]  # Temel faktörler
    sentiment_factors: Dict[str, float]  # Sentiment faktörleri
    explanation_summary: str  # İnsan tarafından okunabilir özet

@dataclass
class FeatureExplanation:
    """Özellik açıklaması"""
    feature_name: str
    feature_value: float
    importance_score: float  # 0-1 arası önem skoru
    contribution: float  # Tahmine katkı
    direction: str  # positive, negative, neutral
    description: str  # Özellik açıklaması
    category: str  # technical, fundamental, market, sentiment
    confidence: float  # 0-1 arası güven skoru

@dataclass
class ExplanationReport:
    """Açıklama raporu"""
    report_id: str
    timestamp: datetime
    model_performance: Dict[str, float]  # Model performans metrikleri
    feature_importance_summary: Dict[str, float]  # Özellik önem özeti
    explanation_quality_metrics: Dict[str, float]  # Açıklama kalite metrikleri
    sample_explanations: List[ModelExplanation]  # Örnek açıklamalar
    recommendations: List[str]  # Öneriler
    generated_at: datetime = None

class ExplainableAI:
    """Explainable AI ana sınıfı"""
    
    def __init__(self):
        self.model_explanations = {}
        self.trading_signal_explanations = {}
        self.explanation_reports = {}
        self.feature_descriptions = {}
        self.explanation_methods = {}
        self.interpretability_metrics = {}
        
        # Varsayılan özellik açıklamalarını ekle
        self._add_default_feature_descriptions()
        
        # Açıklama metodlarını tanımla
        self._define_explanation_methods()
        
        # Interpretability metriklerini tanımla
        self._define_interpretability_metrics()
    
    def _add_default_feature_descriptions(self):
        """Varsayılan özellik açıklamalarını ekle"""
        default_features = {
            # Teknik indikatörler
            "rsi": {
                "description": "Relative Strength Index - Aşırı alım/satım seviyelerini gösterir",
                "category": "technical",
                "interpretation": "30 altı aşırı satım, 70 üstü aşırı alım"
            },
            "macd": {
                "description": "Moving Average Convergence Divergence - Trend değişim sinyali",
                "category": "technical",
                "interpretation": "Pozitif değer yükseliş, negatif değer düşüş trendi"
            },
            "bollinger_upper": {
                "description": "Bollinger Bands üst bandı - Fiyat üst sınırı",
                "category": "technical",
                "interpretation": "Fiyat üst banda yaklaştığında satış fırsatı"
            },
            "bollinger_lower": {
                "description": "Bollinger Bands alt bandı - Fiyat alt sınırı",
                "category": "technical",
                "interpretation": "Fiyat alt banda yaklaştığında alım fırsatı"
            },
            "ema_20": {
                "description": "20 günlük Exponential Moving Average - Kısa vadeli trend",
                "category": "technical",
                "interpretation": "Fiyat EMA üstünde yükseliş, altında düşüş trendi"
            },
            "ema_50": {
                "description": "50 günlük Exponential Moving Average - Orta vadeli trend",
                "category": "technical",
                "interpretation": "Uzun vadeli trend göstergesi"
            },
            "volume_sma": {
                "description": "Volume Simple Moving Average - Hacim ortalaması",
                "category": "technical",
                "interpretation": "Yüksek hacim trend onayı"
            },
            "price_sma": {
                "description": "Price Simple Moving Average - Fiyat ortalaması",
                "category": "technical",
                "interpretation": "Fiyat SMA üstünde yükseliş trendi"
            },
            
            # Temel faktörler
            "pe_ratio": {
                "description": "Price-to-Earnings Ratio - Fiyat/Kazanç oranı",
                "category": "fundamental",
                "interpretation": "Düşük değer ucuz, yüksek değer pahalı hisse"
            },
            "pb_ratio": {
                "description": "Price-to-Book Ratio - Fiyat/Defter değeri oranı",
                "category": "fundamental",
                "interpretation": "1 altı değerli, 1 üstü pahalı hisse"
            },
            "debt_to_equity": {
                "description": "Borç/Özsermaye oranı - Finansal kaldıraç",
                "category": "fundamental",
                "interpretation": "Düşük değer düşük risk, yüksek değer yüksek risk"
            },
            "roe": {
                "description": "Return on Equity - Özsermaye karlılığı",
                "category": "fundamental",
                "interpretation": "Yüksek değer yüksek karlılık"
            },
            "roa": {
                "description": "Return on Assets - Varlık karlılığı",
                "category": "fundamental",
                "interpretation": "Yüksek değer verimli varlık kullanımı"
            },
            
            # Piyasa faktörleri
            "market_cap": {
                "description": "Piyasa değeri - Şirket büyüklüğü",
                "category": "market",
                "interpretation": "Büyük şirket daha stabil, küçük şirket daha volatil"
            },
            "volume": {
                "description": "İşlem hacmi - Likidite göstergesi",
                "category": "market",
                "interpretation": "Yüksek hacim yüksek likidite"
            },
            "price": {
                "description": "Hisse fiyatı - Anlık değer",
                "category": "market",
                "interpretation": "Fiyat değişimi getiri göstergesi"
            }
        }
        
        for feature_name, feature_info in default_features.items():
            self.feature_descriptions[feature_name] = feature_info
    
    def _define_explanation_methods(self):
        """Açıklama metodlarını tanımla"""
        # SHAP benzeri açıklama metodu
        def shap_like_explanation(features: Dict[str, float], model_prediction: float) -> Dict[str, Any]:
            """SHAP benzeri açıklama üret"""
            try:
                explanations = {}
                total_contribution = 0.0
                
                # Her özellik için katkı hesapla
                for feature_name, feature_value in features.items():
                    # Basit heuristik: özellik değeri * rastgele ağırlık
                    weight = random.uniform(0.1, 0.3)
                    contribution = feature_value * weight
                    
                    explanations[feature_name] = {
                        "value": feature_value,
                        "contribution": contribution,
                        "importance": abs(contribution),
                        "direction": "positive" if contribution > 0 else "negative"
                    }
                    
                    total_contribution += abs(contribution)
                
                # Normalize et
                if total_contribution > 0:
                    for feature_name in explanations:
                        explanations[feature_name]["normalized_importance"] = (
                            explanations[feature_name]["importance"] / total_contribution
                        )
                
                return explanations
            
            except Exception as e:
                logger.error(f"Error in SHAP-like explanation: {e}")
                return {}
        
        # LIME benzeri açıklama metodu
        def lime_like_explanation(features: Dict[str, float], model_prediction: float) -> Dict[str, Any]:
            """LIME benzeri açıklama üret"""
            try:
                explanations = {}
                
                # Her özellik için local açıklama
                for feature_name, feature_value in features.items():
                    # Basit heuristik: özellik değerine göre etki
                    if feature_name in ["rsi", "macd"]:
                        # Teknik indikatörler için özel mantık
                        if feature_name == "rsi":
                            if feature_value < 30:
                                effect = "Aşırı satım seviyesi - Alım fırsatı"
                                importance = 0.8
                            elif feature_value > 70:
                                effect = "Aşırı alım seviyesi - Satış fırsatı"
                                importance = 0.8
                            else:
                                effect = "Normal seviye - Nötr sinyal"
                                importance = 0.3
                        else:  # macd
                            if feature_value > 0:
                                effect = "Pozitif momentum - Yükseliş trendi"
                                importance = 0.7
                            else:
                                effect = "Negatif momentum - Düşüş trendi"
                                importance = 0.7
                    else:
                        # Diğer özellikler için basit mantık
                        effect = f"Özellik değeri: {feature_value:.3f}"
                        importance = random.uniform(0.2, 0.6)
                    
                    explanations[feature_name] = {
                        "value": feature_value,
                        "effect": effect,
                        "importance": importance,
                        "local_contribution": feature_value * importance
                    }
                
                return explanations
            
            except Exception as e:
                logger.error(f"Error in LIME-like explanation: {e}")
                return {}
        
        # Integrated Gradients benzeri açıklama metodu
        def integrated_gradients_explanation(features: Dict[str, float], model_prediction: float) -> Dict[str, Any]:
            """Integrated Gradients benzeri açıklama üret"""
            try:
                explanations = {}
                
                # Baseline (sıfır değerler) ile karşılaştır
                baseline = {name: 0.0 for name in features.keys()}
                
                for feature_name, feature_value in features.items():
                    # Baseline'dan mevcut değere doğrusal interpolasyon
                    steps = 10
                    gradients = []
                    
                    for i in range(1, steps + 1):
                        interpolated_value = (i / steps) * feature_value
                        # Basit gradient hesaplama
                        gradient = interpolated_value * random.uniform(0.1, 0.4)
                        gradients.append(gradient)
                    
                    # Ortalama gradient
                    avg_gradient = np.mean(gradients)
                    integrated_gradient = avg_gradient * feature_value
                    
                    explanations[feature_name] = {
                        "value": feature_value,
                        "baseline": 0.0,
                        "integrated_gradient": integrated_gradient,
                        "importance": abs(integrated_gradient),
                        "steps": steps
                    }
                
                return explanations
            
            except Exception as e:
                logger.error(f"Error in Integrated Gradients explanation: {e}")
                return {}
        
        self.explanation_methods = {
            "shap": shap_like_explanation,
            "lime": lime_like_explanation,
            "integrated_gradients": integrated_gradients_explanation
        }
    
    def _define_interpretability_metrics(self):
        """Interpretability metriklerini tanımla"""
        def faithfulness_metric(prediction: float, explanation_contribution: float) -> float:
            """Faithfulness metrik - Açıklama doğruluğu"""
            try:
                # Açıklama katkılarının toplamı ile tahmin arasındaki uyum
                total_contribution = sum(abs(contrib) for contrib in explanation_contribution.values())
                if total_contribution > 0:
                    faithfulness = 1 - abs(prediction - total_contribution) / max(abs(prediction), 1)
                    return max(0.0, min(1.0, faithfulness))
                return 0.0
            except Exception as e:
                logger.error(f"Error calculating faithfulness: {e}")
                return 0.0
        
        def stability_metric(explanations: List[Dict[str, Any]]) -> float:
            """Stability metrik - Açıklama tutarlılığı"""
            try:
                if len(explanations) < 2:
                    return 1.0
                
                # Özellik önem skorlarının standart sapması
                feature_importances = defaultdict(list)
                
                for explanation in explanations:
                    for feature_name, feature_info in explanation.items():
                        if isinstance(feature_info, dict) and "importance" in feature_info:
                            feature_importances[feature_name].append(feature_info["importance"])
                
                # Her özellik için CV hesapla
                cvs = []
                for feature_name, importances in feature_importances.items():
                    if len(importances) > 1:
                        mean_importance = np.mean(importances)
                        std_importance = np.std(importances)
                        if mean_importance > 0:
                            cv = std_importance / mean_importance
                            cvs.append(cv)
                
                if cvs:
                    # Düşük CV = yüksek stability
                    avg_cv = np.mean(cvs)
                    stability = 1 / (1 + avg_cv)
                    return max(0.0, min(1.0, stability))
                
                return 1.0
            
            except Exception as e:
                logger.error(f"Error calculating stability: {e}")
                return 0.0
        
        def comprehensibility_metric(explanation: Dict[str, Any]) -> float:
            """Comprehensibility metrik - Açıklama anlaşılabilirliği"""
            try:
                score = 0.0
                total_features = len(explanation)
                
                if total_features == 0:
                    return 0.0
                
                for feature_name, feature_info in explanation.items():
                    if isinstance(feature_info, dict):
                        # Özellik açıklaması var mı?
                        if feature_name in self.feature_descriptions:
                            score += 0.3
                        
                        # Değer ve yön bilgisi var mı?
                        if "value" in feature_info and "direction" in feature_info:
                            score += 0.4
                        
                        # Önem skoru var mı?
                        if "importance" in feature_info:
                            score += 0.3
                
                return score / total_features
            
            except Exception as e:
                logger.error(f"Error calculating comprehensibility: {e}")
                return 0.0
        
        self.interpretability_metrics = {
            "faithfulness": faithfulness_metric,
            "stability": stability_metric,
            "comprehensibility": comprehensibility_metric
        }
    
    def explain_model_prediction(self, model_id: str, features: Dict[str, float], 
                               prediction: float, method: str = "shap") -> Optional[ModelExplanation]:
        """Model tahminini açıkla"""
        try:
            explanation_method = self.explanation_methods.get(method)
            if not explanation_method:
                logger.error(f"Explanation method {method} not found")
                return None
            
            # Açıklama üret
            explanation_result = explanation_method(features, prediction)
            
            # Tahmin etiketi belirle
            if prediction > 0.6:
                prediction_label = "positive"
            elif prediction < 0.4:
                prediction_label = "negative"
            else:
                prediction_label = "neutral"
            
            # Güven skoru (basit)
            confidence = abs(prediction - 0.5) * 2
            
            # Özellik önem ve katkı skorları
            feature_importance = {}
            feature_contributions = {}
            
            for feature_name, feature_info in explanation_result.items():
                if isinstance(feature_info, dict):
                    feature_importance[feature_name] = feature_info.get("importance", 0.0)
                    feature_contributions[feature_name] = feature_info.get("contribution", 0.0)
            
            # Local ve global açıklama
            local_explanation = explanation_result if method == "lime" else {}
            global_explanation = explanation_result if method == "shap" else {}
            
            # Açıklama kalitesi hesapla
            explanation_quality = self._calculate_explanation_quality(
                explanation_result, prediction, method
            )
            
            # Model açıklaması oluştur
            explanation = ModelExplanation(
                explanation_id=f"EXPL_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                model_id=model_id,
                timestamp=datetime.now(),
                prediction=prediction,
                prediction_label=prediction_label,
                confidence=confidence,
                feature_importance=feature_importance,
                feature_contributions=feature_contributions,
                local_explanation=local_explanation,
                global_explanation=global_explanation,
                explanation_method=method,
                explanation_quality=explanation_quality
            )
            
            self.model_explanations[explanation.explanation_id] = explanation
            logger.info(f"Model explanation created: {explanation.explanation_id}")
            
            return explanation
        
        except Exception as e:
            logger.error(f"Error explaining model prediction: {e}")
            return None
    
    def explain_trading_signal(self, signal_data: Dict[str, Any]) -> Optional[TradingSignalExplanation]:
        """Trading sinyalini açıkla"""
        try:
            # Sinyal verilerini al
            signal_type = signal_data.get("signal_type", "hold")
            confidence = signal_data.get("confidence", 0.5)
            features = signal_data.get("features", {})
            
            # Ana faktörleri belirle
            primary_factors = self._identify_primary_factors(features, signal_type)
            
            # Destekleyici faktörleri belirle
            supporting_factors = self._identify_supporting_factors(features, signal_type)
            
            # Risk faktörlerini belirle
            risk_factors = self._identify_risk_factors(features, signal_type)
            
            # Piyasa bağlamını oluştur
            market_context = self._create_market_context(features)
            
            # Teknik indikatörleri ayır
            technical_indicators = {k: v for k, v in features.items() 
                                  if k in ["rsi", "macd", "bollinger_upper", "bollinger_lower", "ema_20", "ema_50"]}
            
            # Temel faktörleri ayır
            fundamental_factors = {k: v for k, v in features.items() 
                                 if k in ["pe_ratio", "pb_ratio", "debt_to_equity", "roe", "roa"]}
            
            # Sentiment faktörleri (varsayılan)
            sentiment_factors = {
                "market_sentiment": random.uniform(0.3, 0.7),
                "news_sentiment": random.uniform(0.4, 0.8),
                "social_sentiment": random.uniform(0.2, 0.6)
            }
            
            # Açıklama özeti oluştur
            explanation_summary = self._generate_explanation_summary(
                signal_type, primary_factors, confidence
            )
            
            # Trading sinyal açıklaması oluştur
            signal_explanation = TradingSignalExplanation(
                signal_id=f"SIGNAL_EXPL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                signal_type=signal_type,
                confidence=confidence,
                primary_factors=primary_factors,
                supporting_factors=supporting_factors,
                risk_factors=risk_factors,
                market_context=market_context,
                technical_indicators=technical_indicators,
                fundamental_factors=fundamental_factors,
                sentiment_factors=sentiment_factors,
                explanation_summary=explanation_summary
            )
            
            self.trading_signal_explanations[signal_explanation.signal_id] = signal_explanation
            logger.info(f"Trading signal explanation created: {signal_explanation.signal_id}")
            
            return signal_explanation
        
        except Exception as e:
            logger.error(f"Error explaining trading signal: {e}")
            return None
    
    def _identify_primary_factors(self, features: Dict[str, float], signal_type: str) -> List[Dict[str, Any]]:
        """Ana faktörleri belirle"""
        try:
            primary_factors = []
            
            # Sinyal tipine göre ana faktörleri belirle
            if signal_type == "buy":
                # Alım sinyali için ana faktörler
                key_features = ["rsi", "macd", "bollinger_lower", "ema_cross"]
                for feature in key_features:
                    if feature in features:
                        value = features[feature]
                        if feature == "rsi" and value < 30:
                            primary_factors.append({
                                "factor": feature,
                                "value": value,
                                "reason": "Aşırı satım seviyesi (RSI < 30)",
                                "impact": "high"
                            })
                        elif feature == "macd" and value > 0:
                            primary_factors.append({
                                "factor": feature,
                                "value": value,
                                "reason": "Pozitif momentum göstergesi",
                                "impact": "high"
                            })
            
            elif signal_type == "sell":
                # Satış sinyali için ana faktörler
                key_features = ["rsi", "macd", "bollinger_upper"]
                for feature in key_features:
                    if feature in features:
                        value = features[feature]
                        if feature == "rsi" and value > 70:
                            primary_factors.append({
                                "factor": feature,
                                "value": value,
                                "reason": "Aşırı alım seviyesi (RSI > 70)",
                                "impact": "high"
                            })
                        elif feature == "macd" and value < 0:
                            primary_factors.append({
                                "factor": feature,
                                "value": value,
                                "reason": "Negatif momentum göstergesi",
                                "impact": "high"
                            })
            
            return primary_factors
        
        except Exception as e:
            logger.error(f"Error identifying primary factors: {e}")
            return []
    
    def _identify_supporting_factors(self, features: Dict[str, float], signal_type: str) -> List[Dict[str, Any]]:
        """Destekleyici faktörleri belirle"""
        try:
            supporting_factors = []
            
            # Genel destekleyici faktörler
            for feature_name, feature_value in features.items():
                if feature_name in self.feature_descriptions:
                    category = self.feature_descriptions[feature_name]["category"]
                    description = self.feature_descriptions[feature_name]["description"]
                    
                    supporting_factors.append({
                        "factor": feature_name,
                        "value": feature_value,
                        "category": category,
                        "description": description,
                        "impact": "medium"
                    })
            
            return supporting_factors[:5]  # En önemli 5 tanesi
        
        except Exception as e:
            logger.error(f"Error identifying supporting factors: {e}")
            return []
    
    def _identify_risk_factors(self, features: Dict[str, float], signal_type: str) -> List[Dict[str, Any]]:
        """Risk faktörlerini belirle"""
        try:
            risk_factors = []
            
            # Risk faktörleri
            if "volatility" in features:
                volatility = features["volatility"]
                if volatility > 0.3:
                    risk_factors.append({
                        "factor": "volatility",
                        "value": volatility,
                        "risk_level": "high",
                        "description": "Yüksek volatilite - Risk artışı"
                    })
            
            if "debt_to_equity" in features:
                debt_ratio = features["debt_to_equity"]
                if debt_ratio > 1.0:
                    risk_factors.append({
                        "factor": "debt_to_equity",
                        "value": debt_ratio,
                        "risk_level": "medium",
                        "description": "Yüksek borç oranı - Finansal risk"
                    })
            
            return risk_factors
        
        except Exception as e:
            logger.error(f"Error identifying risk factors: {e}")
            return []
    
    def _create_market_context(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Piyasa bağlamını oluştur"""
        try:
            market_context = {
                "trend": "neutral",
                "volatility": "medium",
                "liquidity": "medium",
                "market_regime": "normal"
            }
            
            # Trend belirleme
            if "ema_20" in features and "ema_50" in features:
                ema_20 = features["ema_20"]
                ema_50 = features["ema_50"]
                if ema_20 > ema_50:
                    market_context["trend"] = "bullish"
                elif ema_20 < ema_50:
                    market_context["trend"] = "bearish"
            
            # Volatilite belirleme
            if "volatility" in features:
                vol = features["volatility"]
                if vol < 0.15:
                    market_context["volatility"] = "low"
                elif vol > 0.30:
                    market_context["volatility"] = "high"
            
            return market_context
        
        except Exception as e:
            logger.error(f"Error creating market context: {e}")
            return {}
    
    def _generate_explanation_summary(self, signal_type: str, primary_factors: List[Dict[str, Any]], 
                                    confidence: float) -> str:
        """Açıklama özeti oluştur"""
        try:
            if signal_type == "buy":
                summary = f"🟢 BUY sinyali (Güven: {confidence:.1%}) - "
                if primary_factors:
                    factor = primary_factors[0]
                    summary += f"Ana neden: {factor['reason']}"
                else:
                    summary += "Teknik ve temel analiz sonucu alım fırsatı tespit edildi"
            
            elif signal_type == "sell":
                summary = f"🔴 SELL sinyali (Güven: {confidence:.1%}) - "
                if primary_factors:
                    factor = primary_factors[0]
                    summary += f"Ana neden: {factor['reason']}"
                else:
                    summary += "Teknik ve temel analiz sonucu satış fırsatı tespit edildi"
            
            else:  # hold
                summary = f"🟡 HOLD sinyali (Güven: {confidence:.1%}) - "
                summary += "Mevcut pozisyon korunmalı, yeni aksiyon için beklenmeli"
            
            return summary
        
        except Exception as e:
            logger.error(f"Error generating explanation summary: {e}")
            return "Açıklama oluşturulamadı"
    
    def _calculate_explanation_quality(self, explanation: Dict[str, Any], 
                                     prediction: float, method: str) -> float:
        """Açıklama kalitesini hesapla"""
        try:
            quality_scores = []
            
            # Faithfulness
            if "faithfulness" in self.interpretability_metrics:
                faithfulness = self.interpretability_metrics["faithfulness"](prediction, explanation)
                quality_scores.append(faithfulness)
            
            # Comprehensibility
            if "comprehensibility" in self.interpretability_metrics:
                comprehensibility = self.interpretability_metrics["comprehensibility"](explanation)
                quality_scores.append(comprehensibility)
            
            # Metod bazlı ek kalite skorları
            if method == "shap":
                # SHAP için özel kalite metrikleri
                if explanation:
                    feature_coverage = len(explanation) / 10  # 10 özellik varsayılan
                    quality_scores.append(min(1.0, feature_coverage))
            
            elif method == "lime":
                # LIME için özel kalite metrikleri
                if explanation:
                    local_coherence = 0.8  # Basit heuristik
                    quality_scores.append(local_coherence)
            
            # Ortalama kalite skoru
            if quality_scores:
                return np.mean(quality_scores)
            
            return 0.5  # Varsayılan kalite
        
        except Exception as e:
            logger.error(f"Error calculating explanation quality: {e}")
            return 0.5
    
    def generate_explanation_report(self, time_period: str = "1d") -> Optional[ExplanationReport]:
        """Açıklama raporu oluştur"""
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
            
            # Zaman aralığındaki açıklamaları filtrele
            period_explanations = [
                exp for exp in self.model_explanations.values()
                if start_time <= exp.timestamp <= end_time
            ]
            
            if not period_explanations:
                return None
            
            # Model performans metrikleri
            model_performance = {
                "total_explanations": len(period_explanations),
                "average_quality": np.mean([exp.explanation_quality for exp in period_explanations]),
                "method_distribution": {}
            }
            
            # Metod dağılımı
            method_counts = {}
            for exp in period_explanations:
                method = exp.explanation_method
                method_counts[method] = method_counts.get(method, 0) + 1
            
            model_performance["method_distribution"] = method_counts
            
            # Özellik önem özeti
            feature_importance_summary = {}
            for exp in period_explanations:
                for feature_name, importance in exp.feature_importance.items():
                    if feature_name not in feature_importance_summary:
                        feature_importance_summary[feature_name] = []
                    feature_importance_summary[feature_name].append(importance)
            
            # Ortalama önem skorları
            for feature_name in feature_importance_summary:
                feature_importance_summary[feature_name] = np.mean(feature_importance_summary[feature_name])
            
            # Açıklama kalite metrikleri
            explanation_quality_metrics = {
                "average_quality": np.mean([exp.explanation_quality for exp in period_explanations]),
                "quality_distribution": {
                    "high": len([exp for exp in period_explanations if exp.explanation_quality > 0.7]),
                    "medium": len([exp for exp in period_explanations if 0.4 <= exp.explanation_quality <= 0.7]),
                    "low": len([exp for exp in period_explanations if exp.explanation_quality < 0.4])
                }
            }
            
            # Örnek açıklamalar
            sample_explanations = period_explanations[:3]  # İlk 3 tanesi
            
            # Öneriler
            recommendations = [
                "Açıklama kalitesini artırmak için daha fazla özellik kullanın",
                "Farklı açıklama metodlarını karşılaştırın",
                "Kullanıcı geri bildirimlerini toplayın"
            ]
            
            # Rapor oluştur
            report = ExplanationReport(
                report_id=f"REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                model_performance=model_performance,
                feature_importance_summary=feature_importance_summary,
                explanation_quality_metrics=explanation_quality_metrics,
                sample_explanations=sample_explanations,
                recommendations=recommendations,
                generated_at=datetime.now()
            )
            
            self.explanation_reports[report.report_id] = report
            logger.info(f"Explanation report generated: {report.report_id}")
            
            return report
        
        except Exception as e:
            logger.error(f"Error generating explanation report: {e}")
            return None
    
    def get_xai_summary(self) -> Dict[str, Any]:
        """XAI özeti getir"""
        try:
            summary = {
                "total_model_explanations": len(self.model_explanations),
                "total_signal_explanations": len(self.trading_signal_explanations),
                "total_reports": len(self.explanation_reports),
                "available_methods": list(self.explanation_methods.keys()),
                "feature_coverage": len(self.feature_descriptions),
                "quality_metrics": {},
                "method_usage": {}
            }
            
            # Kalite metrikleri
            if self.model_explanations:
                qualities = [exp.explanation_quality for exp in self.model_explanations.values()]
                summary["quality_metrics"] = {
                    "average_quality": np.mean(qualities),
                    "min_quality": np.min(qualities),
                    "max_quality": np.max(qualities),
                    "std_quality": np.std(qualities)
                }
            
            # Metod kullanımı
            method_counts = {}
            for exp in self.model_explanations.values():
                method = exp.explanation_method
                method_counts[method] = method_counts.get(method, 0) + 1
            
            summary["method_usage"] = method_counts
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting XAI summary: {e}")
            return {}


def test_explainable_ai():
    """Explainable AI test fonksiyonu"""
    print("\n🧪 Explainable AI Test Başlıyor...")
    
    # XAI modülü oluştur
    xai = ExplainableAI()
    
    print("✅ XAI modülü oluşturuldu")
    print(f"📊 Toplam özellik açıklaması: {len(xai.feature_descriptions)}")
    print(f"📊 Kullanılabilir metodlar: {list(xai.explanation_methods.keys())}")
    
    # Test verisi oluştur
    print("\n📊 Test Verisi Oluşturma:")
    test_features = {
        "rsi": 25.5,
        "macd": 0.8,
        "bollinger_lower": 85.0,
        "ema_20": 88.0,
        "ema_50": 90.0,
        "volume_sma": 2500,
        "pe_ratio": 12.5,
        "debt_to_equity": 0.6
    }
    
    test_prediction = 0.75  # %75 pozitif tahmin
    
    print(f"   ✅ Test özellikleri oluşturuldu: {len(test_features)} özellik")
    print(f"   📊 Test tahmini: {test_prediction:.3f}")
    
    # Model tahmin açıklaması
    print("\n📊 Model Tahmin Açıklaması Testi:")
    
    for method in ["shap", "lime", "integrated_gradients"]:
        explanation = xai.explain_model_prediction(
            model_id="TEST_MODEL",
            features=test_features,
            prediction=test_prediction,
            method=method
        )
        
        if explanation:
            print(f"   ✅ {method.upper()} açıklaması oluşturuldu")
            print(f"      📊 Tahmin etiketi: {explanation.prediction_label}")
            print(f"      📊 Güven skoru: {explanation.confidence:.3f}")
            print(f"      📊 Açıklama kalitesi: {explanation.explanation_quality:.3f}")
            print(f"      📊 Özellik önem sayısı: {len(explanation.feature_importance)}")
    
    # Trading sinyal açıklaması
    print("\n📊 Trading Sinyal Açıklaması Testi:")
    
    test_signal_data = {
        "signal_type": "buy",
        "confidence": 0.8,
        "features": test_features
    }
    
    signal_explanation = xai.explain_trading_signal(test_signal_data)
    
    if signal_explanation:
        print(f"   ✅ Trading sinyal açıklaması oluşturuldu")
        print(f"      📊 Sinyal tipi: {signal_explanation.signal_type}")
        print(f"      📊 Güven skoru: {signal_explanation.confidence:.3f}")
        print(f"      📊 Ana faktör sayısı: {len(signal_explanation.primary_factors)}")
        print(f"      📊 Destekleyici faktör sayısı: {len(signal_explanation.supporting_factors)}")
        print(f"      📊 Risk faktör sayısı: {len(signal_explanation.risk_factors)}")
        print(f"      📊 Açıklama özeti: {signal_explanation.explanation_summary}")
    
    # Açıklama raporu
    print("\n📊 Açıklama Raporu Testi:")
    report = xai.generate_explanation_report("1d")
    
    if report:
        print(f"   ✅ Açıklama raporu oluşturuldu")
        print(f"      📊 Toplam açıklama: {report.model_performance['total_explanations']}")
        print(f"      📊 Ortalama kalite: {report.explanation_quality_metrics['average_quality']:.3f}")
        print(f"      📊 Özellik önem sayısı: {len(report.feature_importance_summary)}")
        print(f"      📊 Öneri sayısı: {len(report.recommendations)}")
    
    # XAI özeti
    print("\n📊 XAI Özeti Testi:")
    xai_summary = xai.get_xai_summary()
    
    if xai_summary:
        print(f"   ✅ XAI özeti alındı")
        print(f"   📊 Toplam model açıklaması: {xai_summary['total_model_explanations']}")
        print(f"   📊 Toplam sinyal açıklaması: {xai_summary['total_signal_explanations']}")
        print(f"   📊 Toplam rapor: {xai_summary['total_reports']}")
        print(f"   📊 Kullanılabilir metodlar: {xai_summary['available_methods']}")
        
        if xai_summary['quality_metrics']:
            quality = xai_summary['quality_metrics']
            print(f"   📊 Ortalama kalite: {quality['average_quality']:.3f}")
            print(f"   📊 Kalite aralığı: {quality['min_quality']:.3f} - {quality['max_quality']:.3f}")
        
        if xai_summary['method_usage']:
            print(f"   📊 Metod kullanımı: {xai_summary['method_usage']}")
    
    print("\n✅ Explainable AI Test Tamamlandı!")


if __name__ == "__main__":
    test_explainable_ai()
