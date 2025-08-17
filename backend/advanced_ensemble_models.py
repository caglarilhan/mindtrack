"""
Advanced Ensemble Models - Sprint 15: Advanced Integration & API Gateway

Bu modül, stacking, blending, voting ve diğer gelişmiş ensemble tekniklerini
kullanarak tahmin doğruluğunu artırır.
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
from sklearn.model_selection import cross_val_score, StratifiedKFold, TimeSeriesSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnsembleModel:
    """Ensemble model"""
    model_id: str
    name: str
    ensemble_type: str  # stacking, blending, voting, bagging, boosting
    base_models: List[str]
    meta_model: Optional[str] = None
    weights: Optional[Dict[str, float]] = None
    parameters: Dict[str, Any] = None
    performance_metrics: Dict[str, float] = None
    created_at: datetime = None
    last_updated: datetime = None

@dataclass
class EnsemblePrediction:
    """Ensemble tahmin sonucu"""
    prediction_id: str
    ensemble_id: str
    timestamp: datetime
    final_prediction: float
    final_confidence: float
    base_predictions: Dict[str, float]
    prediction_weights: Dict[str, float]
    ensemble_variance: float
    prediction_quality: float
    meta_prediction: Optional[float] = None

@dataclass
class FeatureImportance:
    """Özellik önem bilgisi"""
    feature_name: str
    importance_score: float
    rank: int
    category: str  # technical, fundamental, market, sentiment
    description: str
    stability_score: float  # 0-1 arası kararlılık skoru

@dataclass
class ModelPerformance:
    """Model performans bilgisi"""
    model_id: str
    timestamp: datetime
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    cross_val_score: float
    prediction_latency: float  # ms cinsinden
    model_size: float  # MB cinsinden
    last_training_time: float  # saniye cinsinden

class AdvancedEnsembleModels:
    """Advanced Ensemble Models ana sınıfı"""
    
    def __init__(self):
        self.ensemble_models = {}
        self.base_models = {}
        self.meta_models = {}
        self.ensemble_predictions = {}
        self.feature_importances = {}
        self.model_performances = {}
        self.ensemble_configs = {}
        
        # Varsayılan ensemble konfigürasyonları
        self._add_default_ensemble_configs()
        
        # Ensemble stratejilerini tanımla
        self._define_ensemble_strategies()
    
    def _add_default_ensemble_configs(self):
        """Varsayılan ensemble konfigürasyonları ekle"""
        default_configs = [
            {
                "config_id": "STACKING_3LAYER",
                "name": "3 Katmanlı Stacking Ensemble",
                "description": "LightGBM + LSTM + TimeGPT -> Meta-Learner",
                "ensemble_type": "stacking",
                "base_models": ["lightgbm", "lstm", "timegpt"],
                "meta_model": "logistic_regression",
                "cv_folds": 5,
                "use_proba": True
            },
            {
                "config_id": "BLENDING_WEIGHTED",
                "name": "Ağırlıklı Blending Ensemble",
                "description": "Ağırlıklı ortalama ile model birleştirme",
                "ensemble_type": "blending",
                "base_models": ["lightgbm", "lstm", "timegpt", "random_forest"],
                "weights": {"lightgbm": 0.4, "lstm": 0.3, "timegpt": 0.2, "random_forest": 0.1},
                "cv_folds": 3
            },
            {
                "config_id": "VOTING_SOFT",
                "name": "Soft Voting Ensemble",
                "description": "Olasılık bazlı soft voting",
                "ensemble_type": "voting",
                "base_models": ["lightgbm", "lstm", "timegpt"],
                "voting_method": "soft",
                "weights": None
            },
            {
                "config_id": "BAGGING_BOOTSTRAP",
                "name": "Bootstrap Aggregating",
                "description": "Bootstrap sampling ile model çeşitliliği",
                "ensemble_type": "bagging",
                "base_models": ["decision_tree", "random_forest", "extra_trees"],
                "n_estimators": 10,
                "bootstrap": True
            },
            {
                "config_id": "BOOSTING_ADAPTIVE",
                "name": "Adaptive Boosting",
                "description": "Hata bazlı adaptif boosting",
                "ensemble_type": "boosting",
                "base_models": ["lightgbm", "xgboost", "catboost"],
                "learning_rate": 0.1,
                "n_estimators": 100
            }
        ]
        
        for config_data in default_configs:
            self.ensemble_configs[config_data["config_id"]] = config_data
    
    def _define_ensemble_strategies(self):
        """Ensemble stratejilerini tanımla"""
        # Stacking stratejisi
        def stacking_strategy(base_predictions: Dict[str, np.ndarray], 
                           meta_features: np.ndarray, 
                           meta_model: str = "logistic_regression") -> np.ndarray:
            """Stacking ensemble stratejisi"""
            try:
                # Base model tahminlerini birleştir
                stacked_features = np.column_stack(list(base_predictions.values()))
                
                # Meta-features ile birleştir
                if meta_features is not None:
                    stacked_features = np.column_stack([stacked_features, meta_features])
                
                # Meta-model tahmini (basit heuristik)
                if meta_model == "logistic_regression":
                    # Basit weighted average
                    weights = np.random.dirichlet(np.ones(len(base_predictions)))
                    final_prediction = np.average(stacked_features, weights=weights, axis=1)
                else:
                    # Diğer meta-modeller için
                    final_prediction = np.mean(stacked_features, axis=1)
                
                return final_prediction
            
            except Exception as e:
                logger.error(f"Error in stacking strategy: {e}")
                return np.mean(list(base_predictions.values()), axis=0)
        
        # Blending stratejisi
        def blending_strategy(base_predictions: Dict[str, np.ndarray], 
                           weights: Dict[str, float]) -> np.ndarray:
            """Blending ensemble stratejisi"""
            try:
                # Ağırlıklı ortalama
                weighted_predictions = []
                for model_name, predictions in base_predictions.items():
                    weight = weights.get(model_name, 1.0)
                    weighted_predictions.append(predictions * weight)
                
                final_prediction = np.sum(weighted_predictions, axis=0)
                return final_prediction
            
            except Exception as e:
                logger.error(f"Error in blending strategy: {e}")
                return np.mean(list(base_predictions.values()), axis=0)
        
        # Voting stratejisi
        def voting_strategy(base_predictions: Dict[str, np.ndarray], 
                          voting_method: str = "soft") -> np.ndarray:
            """Voting ensemble stratejisi"""
            try:
                if voting_method == "soft":
                    # Soft voting - olasılık ortalaması
                    final_prediction = np.mean(list(base_predictions.values()), axis=0)
                else:
                    # Hard voting - çoğunluk oyu
                    predictions_array = np.array(list(base_predictions.values()))
                    final_prediction = np.mean(predictions_array > 0.5, axis=0)
                
                return final_prediction
            
            except Exception as e:
                logger.error(f"Error in voting strategy: {e}")
                return np.mean(list(base_predictions.values()), axis=0)
        
        # Bagging stratejisi
        def bagging_strategy(base_predictions: Dict[str, np.ndarray], 
                           n_estimators: int = 10) -> np.ndarray:
            """Bagging ensemble stratejisi"""
            try:
                # Bootstrap sampling ile tahminler
                all_predictions = list(base_predictions.values())
                
                # Rastgele bootstrap sample'lar
                bootstrap_predictions = []
                for _ in range(n_estimators):
                    sample_indices = np.random.choice(len(all_predictions), size=len(all_predictions), replace=True)
                    sample_predictions = [all_predictions[i] for i in sample_indices]
                    bootstrap_predictions.append(np.mean(sample_predictions, axis=0))
                
                final_prediction = np.mean(bootstrap_predictions, axis=0)
                return final_prediction
            
            except Exception as e:
                logger.error(f"Error in bagging strategy: {e}")
                return np.mean(list(base_predictions.values()), axis=0)
        
        # Boosting stratejisi
        def boosting_strategy(base_predictions: Dict[str, np.ndarray], 
                            learning_rate: float = 0.1) -> np.ndarray:
            """Boosting ensemble stratejisi"""
            try:
                # Sequential boosting
                predictions_array = np.array(list(base_predictions.values()))
                
                # Ağırlıkları hesapla (hata bazlı)
                weights = np.ones(len(base_predictions))
                for i in range(1, len(base_predictions)):
                    # Önceki modelin hatasına göre ağırlık
                    error = np.mean(np.abs(predictions_array[i-1] - predictions_array[i]))
                    weights[i] = learning_rate * (1 - error)
                
                # Normalize et
                weights = weights / np.sum(weights)
                
                # Ağırlıklı tahmin
                final_prediction = np.average(predictions_array, weights=weights, axis=0)
                return final_prediction
            
            except Exception as e:
                logger.error(f"Error in boosting strategy: {e}")
                return np.mean(list(base_predictions.values()), axis=0)
        
        self.ensemble_strategies = {
            "stacking": stacking_strategy,
            "blending": blending_strategy,
            "voting": voting_strategy,
            "bagging": bagging_strategy,
            "boosting": boosting_strategy
        }
    
    def create_ensemble_model(self, config_id: str, base_models: Dict[str, Any]) -> str:
        """Ensemble model oluştur"""
        try:
            if config_id not in self.ensemble_configs:
                logger.error(f"Ensemble config {config_id} not found")
                return None
            
            config = self.ensemble_configs[config_id]
            
            # Base modelleri kaydet
            for model_name, model_obj in base_models.items():
                if model_name in config["base_models"]:
                    self.base_models[model_name] = model_obj
            
            # Ensemble model oluştur
            ensemble_model = EnsembleModel(
                model_id=f"ENSEMBLE_{config_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                name=config["name"],
                ensemble_type=config["ensemble_type"],
                base_models=config["base_models"],
                meta_model=config.get("meta_model"),
                weights=config.get("weights"),
                parameters=config,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            self.ensemble_models[ensemble_model.model_id] = ensemble_model
            logger.info(f"Ensemble model created: {ensemble_model.model_id}")
            
            return ensemble_model.model_id
        
        except Exception as e:
            logger.error(f"Error creating ensemble model: {e}")
            return None
    
    def generate_ensemble_prediction(self, ensemble_id: str, features: Dict[str, float], 
                                   meta_features: Optional[Dict[str, float]] = None) -> Optional[EnsemblePrediction]:
        """Ensemble tahmin üret"""
        try:
            if ensemble_id not in self.ensemble_models:
                logger.error(f"Ensemble model {ensemble_id} not found")
                return None
            
            ensemble = self.ensemble_models[ensemble_id]
            config = ensemble.parameters
            
            # Base model tahminlerini al
            base_predictions = {}
            for model_name in ensemble.base_models:
                if model_name in self.base_models:
                    # Simüle edilmiş tahmin (gerçek implementasyonda model.predict() kullanılır)
                    prediction = self._simulate_model_prediction(model_name, features)
                    base_predictions[model_name] = prediction
            
            if not base_predictions:
                logger.error("No base model predictions available")
                return None
            
            # Ensemble stratejisini uygula
            strategy = self.ensemble_strategies.get(config["ensemble_type"])
            if not strategy:
                logger.error(f"Strategy not found for {config['ensemble_type']}")
                return None
            
            # Meta-features'ları hazırla
            meta_features_array = None
            if meta_features and config.get("use_proba"):
                meta_features_array = np.array(list(meta_features.values()))
            
            # Final tahmin
            if config["ensemble_type"] == "stacking":
                final_prediction = strategy(base_predictions, meta_features_array, config.get("meta_model"))
            elif config["ensemble_type"] == "blending":
                final_prediction = strategy(base_predictions, config.get("weights", {}))
            elif config["ensemble_type"] == "voting":
                final_prediction = strategy(base_predictions, config.get("voting_method", "soft"))
            elif config["ensemble_type"] == "bagging":
                final_prediction = strategy(base_predictions, config.get("n_estimators", 10))
            elif config["ensemble_type"] == "boosting":
                final_prediction = strategy(base_predictions, config.get("learning_rate", 0.1))
            else:
                final_prediction = np.mean(list(base_predictions.values()), axis=0)
            
            # Tahmin kalitesi hesapla
            prediction_quality = self._calculate_prediction_quality(base_predictions, final_prediction)
            
            # Ensemble variance hesapla
            ensemble_variance = np.var(list(base_predictions.values()), axis=0).mean()
            
            # Güven skoru hesapla
            final_confidence = self._calculate_confidence_score(base_predictions, final_prediction)
            
            # Ensemble tahmin sonucu oluştur
            ensemble_prediction = EnsemblePrediction(
                prediction_id=f"PRED_{ensemble_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                ensemble_id=ensemble_id,
                timestamp=datetime.now(),
                final_prediction=float(final_prediction.mean()),
                final_confidence=final_confidence,
                base_predictions={k: float(v.mean()) for k, v in base_predictions.items()},
                meta_prediction=float(meta_features_array.mean()) if meta_features_array is not None else None,
                prediction_weights=config.get("weights", {}),
                ensemble_variance=float(ensemble_variance),
                prediction_quality=prediction_quality
            )
            
            self.ensemble_predictions[ensemble_prediction.prediction_id] = ensemble_prediction
            logger.info(f"Ensemble prediction generated: {ensemble_prediction.prediction_id}")
            
            return ensemble_prediction
        
        except Exception as e:
            logger.error(f"Error generating ensemble prediction: {e}")
            return None
    
    def _simulate_model_prediction(self, model_name: str, features: Dict[str, float]) -> np.ndarray:
        """Model tahminini simüle et"""
        try:
            # Gerçek implementasyonda bu kısım model.predict() ile değiştirilecek
            np.random.seed(hash(str(features)) % 2**32)
            
            if model_name == "lightgbm":
                # LightGBM benzeri tahmin
                base_score = 0.5
                feature_contribution = sum(features.values()) / len(features) * 0.1
                noise = np.random.normal(0, 0.05, 100)
                predictions = base_score + feature_contribution + noise
            
            elif model_name == "lstm":
                # LSTM benzeri tahmin
                base_score = 0.6
                feature_contribution = sum(features.values()) / len(features) * 0.15
                noise = np.random.normal(0, 0.03, 100)
                predictions = base_score + feature_contribution + noise
            
            elif model_name == "timegpt":
                # TimeGPT benzeri tahmin
                base_score = 0.55
                feature_contribution = sum(features.values()) / len(features) * 0.12
                noise = np.random.normal(0, 0.04, 100)
                predictions = base_score + feature_contribution + noise
            
            elif model_name == "random_forest":
                # Random Forest benzeri tahmin
                base_score = 0.52
                feature_contribution = sum(features.values()) / len(features) * 0.08
                noise = np.random.normal(0, 0.06, 100)
                predictions = base_score + feature_contribution + noise
            
            else:
                # Varsayılan tahmin
                base_score = 0.5
                feature_contribution = sum(features.values()) / len(features) * 0.1
                noise = np.random.normal(0, 0.05, 100)
                predictions = base_score + feature_contribution + noise
            
            # 0-1 arasında sınırla
            predictions = np.clip(predictions, 0, 1)
            
            return predictions
        
        except Exception as e:
            logger.error(f"Error simulating model prediction: {e}")
            return np.random.uniform(0.4, 0.6, 100)
    
    def _calculate_prediction_quality(self, base_predictions: Dict[str, np.ndarray], 
                                    final_prediction: np.ndarray) -> float:
        """Tahmin kalitesini hesapla"""
        try:
            # Base model tahminleri arasındaki tutarlılık
            predictions_array = np.array(list(base_predictions.values()))
            
            # Standart sapma (düşük = yüksek kalite)
            std_predictions = np.std(predictions_array, axis=0)
            consistency_score = 1 / (1 + std_predictions.mean())
            
            # Final tahminin kararlılığı
            stability_score = 1 / (1 + np.std(final_prediction))
            
            # Genel kalite skoru
            quality_score = (consistency_score + stability_score) / 2
            return float(quality_score)
        
        except Exception as e:
            logger.error(f"Error calculating prediction quality: {e}")
            return 0.5
    
    def _calculate_confidence_score(self, base_predictions: Dict[str, np.ndarray], 
                                  final_prediction: np.ndarray) -> float:
        """Güven skorunu hesapla"""
        try:
            # Base model tahminlerinin final tahmine yakınlığı
            predictions_array = np.array(list(base_predictions.values()))
            
            # Her base model tahmininin final tahmine olan uzaklığı
            distances = []
            for pred in predictions_array:
                distance = np.mean(np.abs(pred - final_prediction))
                distances.append(distance)
            
            # Ortalama uzaklık (düşük = yüksek güven)
            avg_distance = np.mean(distances)
            confidence_score = 1 / (1 + avg_distance)
            
            return float(confidence_score)
        
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.5
    
    def optimize_ensemble_weights(self, ensemble_id: str, validation_data: pd.DataFrame, 
                                target_column: str) -> Dict[str, float]:
        """Ensemble ağırlıklarını optimize et"""
        try:
            if ensemble_id not in self.ensemble_models:
                logger.error(f"Ensemble model {ensemble_id} not found")
                return {}
            
            ensemble = self.ensemble_models[ensemble_id]
            
            # Cross-validation ile ağırlık optimizasyonu
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            
            best_weights = None
            best_score = 0.0
            
            # Grid search benzeri ağırlık arama
            weight_combinations = [
                {"lightgbm": 0.4, "lstm": 0.3, "timegpt": 0.3},
                {"lightgbm": 0.5, "lstm": 0.3, "timegpt": 0.2},
                {"lightgbm": 0.6, "lstm": 0.25, "timegpt": 0.15},
                {"lightgbm": 0.3, "lstm": 0.4, "timegpt": 0.3},
                {"lightgbm": 0.35, "lstm": 0.35, "timegpt": 0.3}
            ]
            
            for weights in weight_combinations:
                cv_scores = []
                
                for train_idx, val_idx in cv.split(validation_data, validation_data[target_column]):
                    # Train/validation split
                    train_data = validation_data.iloc[train_idx]
                    val_data = validation_data.iloc[val_idx]
                    
                    # Base model tahminlerini al (simüle edilmiş)
                    base_predictions = {}
                    for model_name in ensemble.base_models:
                        if model_name in weights:
                            # Simüle edilmiş tahmin
                            features = val_data.drop(columns=[target_column]).iloc[0].to_dict()
                            prediction = self._simulate_model_prediction(model_name, features)
                            base_predictions[model_name] = prediction
                    
                    # Ağırlıklı ensemble tahmin
                    weighted_prediction = 0.0
                    for model_name, pred in base_predictions.items():
                        weight = weights.get(model_name, 0.0)
                        weighted_prediction += weight * pred.mean()
                    
                    # Binary tahmin
                    binary_prediction = (weighted_prediction > 0.5).astype(int)
                    
                    # Accuracy hesapla
                    accuracy = accuracy_score(val_data[target_column], binary_prediction)
                    cv_scores.append(accuracy)
                
                # Ortalama CV skoru
                avg_cv_score = np.mean(cv_scores)
                
                if avg_cv_score > best_score:
                    best_score = avg_cv_score
                    best_weights = weights
            
            # En iyi ağırlıkları güncelle
            if best_weights:
                ensemble.weights = best_weights
                ensemble.last_updated = datetime.now()
                logger.info(f"Ensemble weights optimized: {best_weights}")
            
            return best_weights or {}
        
        except Exception as e:
            logger.error(f"Error optimizing ensemble weights: {e}")
            return {}
    
    def calculate_feature_importance(self, ensemble_id: str, features: Dict[str, float]) -> List[FeatureImportance]:
        """Özellik önem skorlarını hesapla"""
        try:
            if ensemble_id not in self.ensemble_models:
                logger.error(f"Ensemble model {ensemble_id} not found")
                return []
            
            ensemble = self.ensemble_models[ensemble_id]
            
            # Her base model için özellik önem skorları
            feature_importances = defaultdict(list)
            
            for model_name in ensemble.base_models:
                # Simüle edilmiş özellik önem skorları
                model_importances = self._simulate_feature_importance(model_name, features)
                
                for feature_name, importance in model_importances.items():
                    feature_importances[feature_name].append(importance)
            
            # Ensemble özellik önem skorları
            ensemble_feature_importances = []
            
            for feature_name, importances in feature_importances.items():
                # Ağırlıklı ortalama
                if ensemble.weights:
                    weighted_importance = 0.0
                    total_weight = 0.0
                    
                    for i, model_name in enumerate(ensemble.base_models):
                        if i < len(importances):
                            weight = ensemble.weights.get(model_name, 1.0)
                            weighted_importance += weight * importances[i]
                            total_weight += weight
                    
                    if total_weight > 0:
                        final_importance = weighted_importance / total_weight
                    else:
                        final_importance = np.mean(importances)
                else:
                    final_importance = np.mean(importances)
                
                # Özellik kategorisini belirle
                category = self._determine_feature_category(feature_name)
                
                # Açıklama oluştur
                description = self._generate_feature_description(feature_name, category)
                
                # Kararlılık skoru hesapla
                stability_score = 1 / (1 + np.std(importances))
                
                feature_importance = FeatureImportance(
                    feature_name=feature_name,
                    importance_score=float(final_importance),
                    rank=0,  # Sıralama daha sonra yapılacak
                    category=category,
                    description=description,
                    stability_score=float(stability_score)
                )
                
                ensemble_feature_importances.append(feature_importance)
            
            # Önem skoruna göre sırala
            ensemble_feature_importances.sort(key=lambda x: x.importance_score, reverse=True)
            
            # Rank'ları güncelle
            for i, feature in enumerate(ensemble_feature_importances):
                feature.rank = i + 1
            
            # Sonuçları kaydet
            for feature in ensemble_feature_importances:
                self.feature_importances[f"{ensemble_id}_{feature.feature_name}"] = feature
            
            logger.info(f"Feature importance calculated for {ensemble_id}: {len(ensemble_feature_importances)} features")
            return ensemble_feature_importances
        
        except Exception as e:
            logger.error(f"Error calculating feature importance: {e}")
            return []
    
    def _simulate_feature_importance(self, model_name: str, features: Dict[str, float]) -> Dict[str, float]:
        """Model bazlı özellik önem skorlarını simüle et"""
        try:
            importances = {}
            
            # Model tipine göre farklı özellik önem skorları
            if model_name == "lightgbm":
                # LightGBM genellikle teknik indikatörlere önem verir
                for feature_name, feature_value in features.items():
                    if "rsi" in feature_name.lower():
                        importances[feature_name] = 0.9
                    elif "macd" in feature_name.lower():
                        importances[feature_name] = 0.8
                    elif "ema" in feature_name.lower():
                        importances[feature_name] = 0.7
                    else:
                        importances[feature_name] = random.uniform(0.3, 0.6)
            
            elif model_name == "lstm":
                # LSTM genellikle fiyat ve hacim verilerine önem verir
                for feature_name, feature_value in features.items():
                    if "price" in feature_name.lower():
                        importances[feature_name] = 0.9
                    elif "volume" in feature_name.lower():
                        importances[feature_name] = 0.8
                    elif "rsi" in feature_name.lower():
                        importances[feature_name] = 0.7
                    else:
                        importances[feature_name] = random.uniform(0.4, 0.6)
            
            elif model_name == "timegpt":
                # TimeGPT genellikle temel faktörlere önem verir
                for feature_name, feature_value in features.items():
                    if "pe_ratio" in feature_name.lower():
                        importances[feature_name] = 0.9
                    elif "roe" in feature_name.lower():
                        importances[feature_name] = 0.8
                    elif "debt" in feature_name.lower():
                        importances[feature_name] = 0.7
                    else:
                        importances[feature_name] = random.uniform(0.3, 0.6)
            
            else:
                # Varsayılan özellik önem skorları
                for feature_name, feature_value in features.items():
                    importances[feature_name] = random.uniform(0.4, 0.8)
            
            return importances
        
        except Exception as e:
            logger.error(f"Error simulating feature importance: {e}")
            return {name: random.uniform(0.3, 0.7) for name in features.keys()}
    
    def _determine_feature_category(self, feature_name: str) -> str:
        """Özellik kategorisini belirle"""
        try:
            feature_lower = feature_name.lower()
            
            if any(word in feature_lower for word in ["rsi", "macd", "ema", "bollinger", "volume", "price"]):
                return "technical"
            elif any(word in feature_lower for word in ["pe_ratio", "pb_ratio", "roe", "roa", "debt"]):
                return "fundamental"
            elif any(word in feature_lower for word in ["market_cap", "sector", "country"]):
                return "market"
            elif any(word in feature_lower for word in ["sentiment", "news", "social"]):
                return "sentiment"
            else:
                return "other"
        
        except Exception as e:
            logger.error(f"Error determining feature category: {e}")
            return "other"
    
    def _generate_feature_description(self, feature_name: str, category: str) -> str:
        """Özellik açıklaması oluştur"""
        try:
            descriptions = {
                "rsi": "Relative Strength Index - Aşırı alım/satım seviyeleri",
                "macd": "Moving Average Convergence Divergence - Trend değişim sinyali",
                "ema_20": "20 günlük Exponential Moving Average - Kısa vadeli trend",
                "ema_50": "50 günlük Exponential Moving Average - Orta vadeli trend",
                "pe_ratio": "Price-to-Earnings Ratio - Fiyat/Kazanç oranı",
                "roe": "Return on Equity - Özsermaye karlılığı",
                "volume": "İşlem hacmi - Likidite göstergesi",
                "price": "Hisse fiyatı - Anlık değer"
            }
            
            return descriptions.get(feature_name, f"{feature_name} - {category} kategorisinde özellik")
        
        except Exception as e:
            logger.error(f"Error generating feature description: {e}")
            return f"{feature_name} - Özellik açıklaması"
    
    def get_ensemble_summary(self) -> Dict[str, Any]:
        """Ensemble özeti getir"""
        try:
            summary = {
                "total_ensembles": len(self.ensemble_models),
                "total_base_models": len(self.base_models),
                "total_predictions": len(self.ensemble_predictions),
                "total_features": len(self.feature_importances),
                "ensemble_types": {},
                "performance_summary": {},
                "feature_importance_summary": {}
            }
            
            # Ensemble tipleri
            for ensemble in self.ensemble_models.values():
                ensemble_type = ensemble.ensemble_type
                summary["ensemble_types"][ensemble_type] = summary["ensemble_types"].get(ensemble_type, 0) + 1
            
            # Performans özeti
            if self.ensemble_predictions:
                qualities = [pred.prediction_quality for pred in self.ensemble_predictions.values()]
                confidences = [pred.final_confidence for pred in self.ensemble_predictions.values()]
                
                summary["performance_summary"] = {
                    "average_quality": np.mean(qualities),
                    "average_confidence": np.mean(confidences),
                    "total_predictions": len(self.ensemble_predictions)
                }
            
            # Özellik önem özeti
            if self.feature_importances:
                importance_scores = [feature.importance_score for feature in self.feature_importances.values()]
                stability_scores = [feature.stability_score for feature in self.feature_importances.values()]
                
                summary["feature_importance_summary"] = {
                    "average_importance": np.mean(importance_scores),
                    "average_stability": np.mean(stability_scores),
                    "total_features": len(self.feature_importances)
                }
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting ensemble summary: {e}")
            return {}


def test_advanced_ensemble_models():
    """Advanced Ensemble Models test fonksiyonu"""
    print("\n🧪 Advanced Ensemble Models Test Başlıyor...")
    
    # Advanced Ensemble Models oluştur
    ensemble_models = AdvancedEnsembleModels()
    
    print("✅ Advanced Ensemble Models oluşturuldu")
    print(f"📊 Toplam ensemble konfigürasyonu: {len(ensemble_models.ensemble_configs)}")
    print(f"📊 Kullanılabilir stratejiler: {list(ensemble_models.ensemble_strategies.keys())}")
    
    # Test base modelleri oluştur
    print("\n📊 Test Base Modelleri Oluşturma:")
    test_base_models = {
        "lightgbm": "LightGBM Model Object",
        "lstm": "LSTM Model Object",
        "timegpt": "TimeGPT Model Object",
        "random_forest": "Random Forest Model Object"
    }
    
    print(f"   ✅ {len(test_base_models)} test base model oluşturuldu")
    
    # Test özellikleri
    test_features = {
        "rsi": 35.5,
        "macd": 0.8,
        "ema_20": 88.0,
        "ema_50": 90.0,
        "volume": 2500,
        "pe_ratio": 12.5,
        "roe": 0.15
    }
    
    print(f"   📊 Test özellikleri: {len(test_features)} özellik")
    
    # Farklı ensemble tiplerini test et
    print("\n📊 Ensemble Model Testleri:")
    
    for config_id in ["STACKING_3LAYER", "BLENDING_WEIGHTED", "VOTING_SOFT"]:
        print(f"\n📊 {config_id} Testi:")
        
        # Ensemble model oluştur
        ensemble_id = ensemble_models.create_ensemble_model(config_id, test_base_models)
        
        if ensemble_id:
            print(f"   ✅ Ensemble model oluşturuldu: {ensemble_id}")
            
            # Ensemble tahmin üret
            prediction = ensemble_models.generate_ensemble_prediction(ensemble_id, test_features)
            
            if prediction:
                print(f"   ✅ Ensemble tahmin üretildi")
                print(f"      📊 Final tahmin: {prediction.final_prediction:.3f}")
                print(f"      📊 Güven skoru: {prediction.final_confidence:.3f}")
                print(f"      📊 Tahmin kalitesi: {prediction.prediction_quality:.3f}")
                print(f"      📊 Ensemble variance: {prediction.ensemble_variance:.3f}")
                print(f"      📊 Base tahminler: {len(prediction.base_predictions)}")
            
            # Özellik önem skorları hesapla
            feature_importances = ensemble_models.calculate_feature_importance(ensemble_id, test_features)
            
            if feature_importances:
                print(f"   ✅ Özellik önem skorları hesaplandı")
                print(f"      📊 Toplam özellik: {len(feature_importances)}")
                print(f"      📊 En önemli özellik: {feature_importances[0].feature_name} (skor: {feature_importances[0].importance_score:.3f})")
    
    # Ağırlık optimizasyonu testi
    print("\n📊 Ağırlık Optimizasyonu Testi:")
    
    # Test validation data oluştur
    np.random.seed(42)
    n_samples = 100
    test_data = pd.DataFrame({
        'rsi': np.random.uniform(20, 80, n_samples),
        'macd': np.random.uniform(-2, 2, n_samples),
        'ema_20': np.random.uniform(85, 95, n_samples),
        'target': np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
    })
    
    print(f"   ✅ Test validation data oluşturuldu: {n_samples} örnek")
    
    # Ağırlık optimizasyonu
    if "BLENDING_WEIGHTED" in ensemble_models.ensemble_models:
        ensemble_id = list(ensemble_models.ensemble_models.keys())[0]
        optimized_weights = ensemble_models.optimize_ensemble_weights(ensemble_id, test_data, 'target')
        
        if optimized_weights:
            print(f"   ✅ Ağırlık optimizasyonu tamamlandı")
            print(f"      📊 Optimize edilmiş ağırlıklar: {optimized_weights}")
    
    # Ensemble özeti
    print("\n📊 Ensemble Özeti:")
    summary = ensemble_models.get_ensemble_summary()
    
    if summary:
        print(f"   ✅ Ensemble özeti alındı")
        print(f"   📊 Toplam ensemble: {summary['total_ensembles']}")
        print(f"   📊 Toplam base model: {summary['total_base_models']}")
        print(f"   📊 Toplam tahmin: {summary['total_predictions']}")
        print(f"   📊 Toplam özellik: {summary['total_features']}")
        print(f"   📊 Ensemble tipleri: {summary['ensemble_types']}")
        
        if summary['performance_summary']:
            perf = summary['performance_summary']
            print(f"   📊 Ortalama kalite: {perf['average_quality']:.3f}")
            print(f"   📊 Ortalama güven: {perf['average_confidence']:.3f}")
        
        if summary['feature_importance_summary']:
            feat = summary['feature_importance_summary']
            print(f"   📊 Ortalama önem: {feat['average_importance']:.3f}")
            print(f"   📊 Ortalama kararlılık: {feat['average_stability']:.3f}")
    
    print("\n✅ Advanced Ensemble Models Test Tamamlandı!")


if __name__ == "__main__":
    test_advanced_ensemble_models()
