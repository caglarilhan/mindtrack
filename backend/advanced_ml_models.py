"""
Advanced ML Models - Sprint 14: Advanced Machine Learning & AI Engine

Bu modül, LightGBM, LSTM ve TimeGPT ensemble modellerini kullanarak
finansal tahmin ve trading sinyalleri üretir.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
import json
import logging
import pickle
from pathlib import Path

# ML Libraries
try:
    import lightgbm as lgb
    from sklearn.model_selection import TimeSeriesSplit, cross_val_score
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.ensemble import VotingClassifier
    import joblib
except ImportError:
    print("Warning: Some ML libraries not available. Install with: pip install lightgbm scikit-learn joblib")
    lgb = None
    TimeSeriesSplit = None
    cross_val_score = None
    accuracy_score = None
    precision_score = None
    recall_score = None
    f1_score = None
    roc_auc_score = None
    StandardScaler = None
    MinMaxScaler = None
    VotingClassifier = None
    joblib = None

# Deep Learning Libraries
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
except ImportError:
    print("Warning: TensorFlow not available. Install with: pip install tensorflow")
    tf = None
    Sequential = None
    load_model = None
    LSTM = None
    Dense = None
    Dropout = None
    BatchNormalization = None
    Adam = None
    EarlyStopping = None
    ReduceLROnPlateau = None

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MLModelConfig:
    """ML model konfigürasyonu"""
    model_id: str
    model_type: str  # lightgbm, lstm, timegpt, ensemble
    parameters: Dict[str, Any]
    feature_columns: List[str]
    target_column: str
    prediction_horizon: int  # Gün cinsinden tahmin ufku
    retrain_frequency: int  # Gün cinsinden yeniden eğitim sıklığı
    created_at: datetime = None

@dataclass
class ModelPerformance:
    """Model performans metrikleri"""
    model_id: str
    timestamp: datetime
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    mse: float
    mae: float
    sharpe_ratio: float
    max_drawdown: float
    total_return: float

@dataclass
class TradingSignal:
    """Trading sinyali"""
    signal_id: str
    symbol: str
    timestamp: datetime
    signal_type: str  # buy, sell, hold
    confidence: float  # 0-1 arası güven skoru
    model_predictions: Dict[str, float]  # Her modelin tahmini
    ensemble_prediction: float  # Ensemble tahmin
    features: Dict[str, float]  # Kullanılan özellikler
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

@dataclass
class FeatureData:
    """Özellik verisi"""
    symbol: str
    timestamp: datetime
    technical_features: Dict[str, float]  # Teknik indikatörler
    fundamental_features: Dict[str, float]  # Temel veriler
    market_features: Dict[str, float]  # Piyasa verileri
    sentiment_features: Dict[str, float]  # Sentiment verileri
    target_value: Optional[float] = None

class AdvancedMLModels:
    """Advanced ML Models ana sınıfı"""
    
    def __init__(self):
        self.models = {}
        self.model_configs = {}
        self.model_performances = {}
        self.trading_signals = []
        self.feature_data = {}
        self.scalers = {}
        self.ensemble_weights = {}
        
        # Varsayılan model konfigürasyonları
        self._add_default_configs()
        
        # Ensemble ağırlıkları
        self._set_default_ensemble_weights()
    
    def _add_default_configs(self):
        """Varsayılan model konfigürasyonları ekle"""
        default_configs = [
            {
                "model_id": "LIGHTGBM_DAILY",
                "model_type": "lightgbm",
                "parameters": {
                    "objective": "binary",
                    "metric": "binary_logloss",
                    "boosting_type": "gbdt",
                    "num_leaves": 31,
                    "learning_rate": 0.05,
                    "feature_fraction": 0.9,
                    "bagging_fraction": 0.8,
                    "bagging_freq": 5,
                    "verbose": 0
                },
                "feature_columns": [
                    "rsi", "macd", "bollinger_upper", "bollinger_lower",
                    "ema_20", "ema_50", "volume_sma", "price_sma"
                ],
                "target_column": "target",
                "prediction_horizon": 1,
                "retrain_frequency": 30
            },
            {
                "model_id": "LSTM_4H",
                "model_type": "lstm",
                "parameters": {
                    "units": 50,
                    "dropout": 0.2,
                    "recurrent_dropout": 0.2,
                    "learning_rate": 0.001,
                    "batch_size": 32,
                    "epochs": 100,
                    "sequence_length": 20
                },
                "feature_columns": [
                    "price", "volume", "rsi", "macd", "bollinger_upper",
                    "bollinger_lower", "ema_20", "ema_50"
                ],
                "target_column": "target",
                "prediction_horizon": 4,
                "retrain_frequency": 7
            },
            {
                "model_id": "TIMEGPT_10D",
                "model_type": "timegpt",
                "parameters": {
                    "freq": "D",
                    "prediction_length": 10,
                    "context_length": 30,
                    "max_epochs": 10,
                    "learning_rate": 0.001
                },
                "feature_columns": [
                    "price", "volume", "market_cap", "pe_ratio",
                    "pb_ratio", "debt_to_equity", "roe", "roa"
                ],
                "target_column": "price",
                "prediction_horizon": 10,
                "retrain_frequency": 14
            }
        ]
        
        for config_data in default_configs:
            config = MLModelConfig(
                model_id=config_data["model_id"],
                model_type=config_data["model_type"],
                parameters=config_data["parameters"],
                feature_columns=config_data["feature_columns"],
                target_column=config_data["target_column"],
                prediction_horizon=config_data["prediction_horizon"],
                retrain_frequency=config_data["retrain_frequency"],
                created_at=datetime.now()
            )
            self.model_configs[config.model_id] = config
    
    def _set_default_ensemble_weights(self):
        """Varsayılan ensemble ağırlıkları ayarla"""
        self.ensemble_weights = {
            "LIGHTGBM_DAILY": 0.4,
            "LSTM_4H": 0.35,
            "TIMEGPT_10D": 0.25
        }
    
    def create_lightgbm_model(self, config: MLModelConfig) -> bool:
        """LightGBM modeli oluştur"""
        try:
            if not lgb:
                logger.error("LightGBM not available")
                return False
            
            # Model parametrelerini ayarla
            params = config.parameters.copy()
            params.update({
                "objective": "binary",
                "metric": "binary_logloss",
                "verbose": -1
            })
            
            # Model oluştur
            model = lgb.LGBMClassifier(**params)
            
            # Modeli kaydet
            self.models[config.model_id] = {
                "model": model,
                "config": config,
                "created_at": datetime.now(),
                "last_trained": None,
                "performance_history": []
            }
            
            logger.info(f"LightGBM model created: {config.model_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating LightGBM model: {e}")
            return False
    
    def create_lstm_model(self, config: MLModelConfig) -> bool:
        """LSTM modeli oluştur"""
        try:
            if not tf:
                logger.error("TensorFlow not available")
                return False
            
            # Model parametrelerini al
            units = config.parameters.get("units", 50)
            dropout = config.parameters.get("dropout", 0.2)
            recurrent_dropout = config.parameters.get("recurrent_dropout", 0.2)
            learning_rate = config.parameters.get("learning_rate", 0.001)
            sequence_length = config.parameters.get("sequence_length", 20)
            feature_count = len(config.feature_columns)
            
            # LSTM modeli oluştur
            model = Sequential([
                LSTM(units, return_sequences=True, input_shape=(sequence_length, feature_count)),
                Dropout(dropout),
                LSTM(units // 2, return_sequences=False),
                Dropout(dropout),
                Dense(units // 4, activation='relu'),
                Dropout(dropout),
                Dense(1, activation='sigmoid')
            ])
            
            # Modeli derle
            model.compile(
                optimizer=Adam(learning_rate=learning_rate),
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            # Modeli kaydet
            self.models[config.model_id] = {
                "model": model,
                "config": config,
                "created_at": datetime.now(),
                "last_trained": None,
                "performance_history": [],
                "sequence_length": sequence_length
            }
            
            logger.info(f"LSTM model created: {config.model_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating LSTM model: {e}")
            return False
    
    def create_timegpt_model(self, config: MLModelConfig) -> bool:
        """TimeGPT modeli oluştur (simülasyon)"""
        try:
            # TimeGPT için basit bir simülasyon modeli oluştur
            # Gerçek TimeGPT entegrasyonu için ayrı bir implementasyon gerekli
            
            class SimulatedTimeGPT:
                def __init__(self, config):
                    self.config = config
                    self.is_trained = False
                
                def fit(self, X, y):
                    self.is_trained = True
                    return self
                
                def predict(self, X):
                    # Basit trend tahmini
                    if self.is_trained:
                        return np.random.normal(0.001, 0.02, len(X))
                    return np.zeros(len(X))
            
            model = SimulatedTimeGPT(config)
            
            # Modeli kaydet
            self.models[config.model_id] = {
                "model": model,
                "config": config,
                "created_at": datetime.now(),
                "last_trained": None,
                "performance_history": []
            }
            
            logger.info(f"TimeGPT model created: {config.model_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating TimeGPT model: {e}")
            return False
    
    def prepare_features(self, data: pd.DataFrame, config: MLModelConfig) -> Tuple[np.ndarray, np.ndarray]:
        """Özellikleri hazırla"""
        try:
            # Özellik sütunlarını seç
            feature_cols = [col for col in config.feature_columns if col in data.columns]
            if not feature_cols:
                logger.error(f"No feature columns found in data for {config.model_id}")
                return None, None
            
            # Özellik verilerini al
            X = data[feature_cols].values
            
            # Target verisini al
            if config.target_column in data.columns:
                y = data[config.target_column].values
            else:
                logger.warning(f"Target column {config.target_column} not found")
                y = None
            
            # NaN değerleri temizle
            if np.isnan(X).any():
                X = np.nan_to_num(X, nan=0.0)
            
            if y is not None and np.isnan(y).any():
                y = np.nan_to_num(y, nan=0.0)
            
            return X, y
        
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None, None
    
    def prepare_lstm_features(self, data: pd.DataFrame, config: MLModelConfig) -> Tuple[np.ndarray, np.ndarray]:
        """LSTM için özellikleri hazırla (sequence format)"""
        try:
            sequence_length = config.parameters.get("sequence_length", 20)
            
            # Özellik verilerini al
            X, y = self.prepare_features(data, config)
            if X is None:
                return None, None
            
            # Sequence formatına çevir
            X_sequences = []
            y_sequences = []
            
            for i in range(sequence_length, len(X)):
                X_sequences.append(X[i-sequence_length:i])
                if y is not None:
                    y_sequences.append(y[i])
            
            if not X_sequences:
                logger.error("Not enough data for sequence creation")
                return None, None
            
            X_sequences = np.array(X_sequences)
            y_sequences = np.array(y_sequences) if y_sequences else None
            
            return X_sequences, y_sequences
        
        except Exception as e:
            logger.error(f"Error preparing LSTM features: {e}")
            return None, None
    
    def train_lightgbm_model(self, model_id: str, training_data: pd.DataFrame) -> bool:
        """LightGBM modelini eğit"""
        try:
            if model_id not in self.models:
                logger.error(f"Model {model_id} not found")
                return False
            
            model_info = self.models[model_id]
            config = model_info["config"]
            
            # Özellikleri hazırla
            X, y = self.prepare_features(training_data, config)
            if X is None or y is None:
                return False
            
            # Modeli eğit
            model_info["model"].fit(X, y)
            
            # Eğitim tarihini güncelle
            model_info["last_trained"] = datetime.now()
            
            logger.info(f"LightGBM model trained: {model_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error training LightGBM model: {e}")
            return False
    
    def train_lstm_model(self, model_id: str, training_data: pd.DataFrame) -> bool:
        """LSTM modelini eğit"""
        try:
            if model_id not in self.models:
                logger.error(f"Model {model_id} not found")
                return False
            
            model_info = self.models[model_id]
            config = model_info["config"]
            
            # LSTM özelliklerini hazırla
            X, y = self.prepare_lstm_features(training_data, config)
            if X is None or y is None:
                return False
            
            # Callbacks
            callbacks = [
                EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
                ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-7)
            ]
            
            # Modeli eğit
            history = model_info["model"].fit(
                X, y,
                validation_split=0.2,
                epochs=config.parameters.get("epochs", 100),
                batch_size=config.parameters.get("batch_size", 32),
                callbacks=callbacks,
                verbose=0
            )
            
            # Eğitim tarihini güncelle
            model_info["last_trained"] = datetime.now()
            
            logger.info(f"LSTM model trained: {model_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error training LSTM model: {e}")
            return False
    
    def train_timegpt_model(self, model_id: str, training_data: pd.DataFrame) -> bool:
        """TimeGPT modelini eğit (simülasyon)"""
        try:
            if model_id not in self.models:
                logger.error(f"Model {model_id} not found")
                return False
            
            model_info = self.models[model_id]
            config = model_info["config"]
            
            # Özellikleri hazırla
            X, y = self.prepare_features(training_data, config)
            if X is None or y is None:
                return False
            
            # Simülasyon modelini eğit
            model_info["model"].fit(X, y)
            
            # Eğitim tarihini güncelle
            model_info["last_trained"] = datetime.now()
            
            logger.info(f"TimeGPT model trained: {model_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error training TimeGPT model: {e}")
            return False
    
    def predict_with_model(self, model_id: str, data: pd.DataFrame) -> Optional[np.ndarray]:
        """Model ile tahmin yap"""
        try:
            if model_id not in self.models:
                logger.error(f"Model {model_id} not found")
                return None
            
            model_info = self.models[model_id]
            config = model_info["config"]
            model = model_info["model"]
            
            # Model tipine göre tahmin yap
            if config.model_type == "lightgbm":
                X, _ = self.prepare_features(data, config)
                if X is not None:
                    return model.predict_proba(X)[:, 1]  # Positive class probability
            
            elif config.model_type == "lstm":
                X, _ = self.prepare_lstm_features(data, config)
                if X is not None:
                    predictions = model.predict(X)
                    return predictions.flatten()
            
            elif config.model_type == "timegpt":
                X, _ = self.prepare_features(data, config)
                if X is not None:
                    return model.predict(X)
            
            return None
        
        except Exception as e:
            logger.error(f"Error predicting with model {model_id}: {e}")
            return None
    
    def generate_ensemble_prediction(self, data: pd.DataFrame) -> Dict[str, float]:
        """Ensemble tahmin üret"""
        try:
            ensemble_predictions = {}
            individual_predictions = {}
            
            # Her modelden tahmin al
            for model_id in self.models:
                prediction = self.predict_with_model(model_id, data)
                if prediction is not None:
                    individual_predictions[model_id] = prediction
                    
                    # Ağırlıklı tahmin
                    weight = self.ensemble_weights.get(model_id, 1.0)
                    ensemble_predictions[model_id] = prediction * weight
            
            # Ensemble tahmin hesapla
            if ensemble_predictions:
                # Ağırlıklı ortalama
                total_weight = sum(self.ensemble_weights.values())
                ensemble_result = sum(ensemble_predictions.values()) / total_weight
                
                return {
                    "ensemble_prediction": ensemble_result,
                    "individual_predictions": individual_predictions,
                    "weights": self.ensemble_weights
                }
            
            return {}
        
        except Exception as e:
            logger.error(f"Error generating ensemble prediction: {e}")
            return {}
    
    def generate_trading_signal(self, symbol: str, data: pd.DataFrame, 
                               current_price: float) -> Optional[TradingSignal]:
        """Trading sinyali üret"""
        try:
            # Ensemble tahmin al
            ensemble_result = self.generate_ensemble_prediction(data)
            if not ensemble_result:
                return None
            
            ensemble_prediction = ensemble_result["ensemble_prediction"]
            individual_predictions = ensemble_result["individual_predictions"]
            
            # Sinyal tipini belirle
            if ensemble_prediction > 0.6:
                signal_type = "buy"
                confidence = ensemble_prediction
            elif ensemble_prediction < 0.4:
                signal_type = "sell"
                confidence = 1 - ensemble_prediction
            else:
                signal_type = "hold"
                confidence = 0.5
            
            # Özellik değerlerini al
            features = {}
            if not data.empty and len(data.columns) > 0:
                latest_data = data.iloc[-1]
                for col in data.columns:
                    if col in latest_data:
                        features[col] = float(latest_data[col])
            
            # Trading sinyali oluştur
            signal = TradingSignal(
                signal_id=f"SIGNAL_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                symbol=symbol,
                timestamp=datetime.now(),
                signal_type=signal_type,
                confidence=confidence,
                model_predictions=individual_predictions,
                ensemble_prediction=ensemble_prediction,
                features=features,
                target_price=current_price * (1 + ensemble_prediction * 0.1) if signal_type == "buy" else None,
                stop_loss=current_price * 0.95 if signal_type == "buy" else None,
                take_profit=current_price * 1.15 if signal_type == "buy" else None
            )
            
            self.trading_signals.append(signal)
            logger.info(f"Trading signal generated: {signal.signal_id} - {signal.signal_type}")
            
            return signal
        
        except Exception as e:
            logger.error(f"Error generating trading signal: {e}")
            return None
    
    def evaluate_model_performance(self, model_id: str, test_data: pd.DataFrame) -> Optional[ModelPerformance]:
        """Model performansını değerlendir"""
        try:
            if model_id not in self.models:
                logger.error(f"Model {model_id} not found")
                return None
            
            model_info = self.models[model_id]
            config = model_info["config"]
            
            # Tahmin yap
            predictions = self.predict_with_model(model_id, test_data)
            if predictions is None:
                return None
            
            # Target verisini al
            X, y_true = self.prepare_features(test_data, config)
            if y_true is None:
                return None
            
            # Binary tahminlere çevir
            if config.model_type == "lightgbm":
                y_pred = (predictions > 0.5).astype(int)
            else:
                y_pred = (predictions > 0.5).astype(int)
            
            # Performans metrikleri hesapla
            accuracy = accuracy_score(y_true, y_pred) if len(y_true) > 0 else 0
            precision = precision_score(y_true, y_pred, zero_division=0) if len(y_true) > 0 else 0
            recall = recall_score(y_true, y_pred, zero_division=0) if len(y_true) > 0 else 0
            f1 = f1_score(y_true, y_pred, zero_division=0) if len(y_true) > 0 else 0
            roc_auc = roc_auc_score(y_true, predictions) if len(y_true) > 0 else 0
            
            # MSE ve MAE
            mse = np.mean((y_true - predictions) ** 2) if len(y_true) > 0 else 0
            mae = np.mean(np.abs(y_true - predictions)) if len(y_true) > 0 else 0
            
            # Trading performans metrikleri (basit)
            returns = np.diff(y_true) * y_pred[:-1]
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            cumulative_returns = np.cumsum(returns)
            max_drawdown = np.min(cumulative_returns) if len(cumulative_returns) > 0 else 0
            total_return = cumulative_returns[-1] if len(cumulative_returns) > 0 else 0
            
            # Performans kaydı oluştur
            performance = ModelPerformance(
                model_id=model_id,
                timestamp=datetime.now(),
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                roc_auc=roc_auc,
                mse=mse,
                mae=mae,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                total_return=total_return
            )
            
            # Performans geçmişine ekle
            model_info["performance_history"].append(performance)
            self.model_performances[f"{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"] = performance
            
            logger.info(f"Model performance evaluated: {model_id}")
            return performance
        
        except Exception as e:
            logger.error(f"Error evaluating model performance: {e}")
            return None
    
    def save_model(self, model_id: str, filepath: str) -> bool:
        """Modeli kaydet"""
        try:
            if model_id not in self.models:
                logger.error(f"Model {model_id} not found")
                return False
            
            model_info = self.models[model_id]
            model = model_info["model"]
            config = model_info["config"]
            
            # Model tipine göre kaydet
            if config.model_type == "lightgbm":
                model.save_model(filepath)
            elif config.model_type == "lstm":
                model.save(filepath)
            elif config.model_type == "timegpt":
                # Simülasyon modeli için pickle kullan
                with open(filepath, 'wb') as f:
                    pickle.dump(model, f)
            
            logger.info(f"Model saved: {model_id} to {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving model {model_id}: {e}")
            return False
    
    def load_model(self, model_id: str, filepath: str) -> bool:
        """Modeli yükle"""
        try:
            if model_id not in self.model_configs:
                logger.error(f"Model config {model_id} not found")
                return False
            
            config = self.model_configs[model_id]
            
            # Model tipine göre yükle
            if config.model_type == "lightgbm":
                model = lgb.Booster(model_file=filepath)
            elif config.model_type == "lstm":
                model = load_model(filepath)
            elif config.model_type == "timegpt":
                # Simülasyon modeli için pickle kullan
                with open(filepath, 'rb') as f:
                    model = pickle.load(f)
            
            # Modeli kaydet
            self.models[model_id] = {
                "model": model,
                "config": config,
                "created_at": datetime.now(),
                "last_trained": None,
                "performance_history": []
            }
            
            logger.info(f"Model loaded: {model_id} from {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading model {model_id}: {e}")
            return False
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Model özeti getir"""
        try:
            summary = {
                "total_models": len(self.models),
                "model_types": {},
                "trained_models": 0,
                "total_signals": len(self.trading_signals),
                "performance_summary": {}
            }
            
            # Model tiplerine göre sayım
            for model_id, model_info in self.models.items():
                model_type = model_info["config"].model_type
                summary["model_types"][model_type] = summary["model_types"].get(model_type, 0) + 1
                
                if model_info["last_trained"]:
                    summary["trained_models"] += 1
            
            # Performans özeti
            if self.model_performances:
                latest_performances = {}
                for model_id in self.models:
                    model_perfs = [p for p in self.model_performances.values() if p.model_id == model_id]
                    if model_perfs:
                        latest = max(model_perfs, key=lambda x: x.timestamp)
                        latest_performances[model_id] = {
                            "accuracy": latest.accuracy,
                            "f1_score": latest.f1_score,
                            "sharpe_ratio": latest.sharpe_ratio,
                            "last_evaluated": latest.timestamp.isoformat()
                        }
                
                summary["performance_summary"] = latest_performances
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting model summary: {e}")
            return {}


def test_advanced_ml_models():
    """Advanced ML Models test fonksiyonu"""
    print("\n🧪 Advanced ML Models Test Başlıyor...")
    
    # Advanced ML Models oluştur
    ml_models = AdvancedMLModels()
    
    print("✅ Varsayılan model konfigürasyonları eklendi")
    print(f"📊 Toplam konfigürasyon sayısı: {len(ml_models.model_configs)}")
    
    # Test verisi oluştur
    print("\n📊 Test Verisi Oluşturma:")
    np.random.seed(42)
    n_samples = 1000
    
    test_data = pd.DataFrame({
        'rsi': np.random.uniform(20, 80, n_samples),
        'macd': np.random.uniform(-2, 2, n_samples),
        'bollinger_upper': np.random.uniform(90, 110, n_samples),
        'bollinger_lower': np.random.uniform(90, 110, n_samples),
        'ema_20': np.random.uniform(95, 105, n_samples),
        'ema_50': np.random.uniform(95, 105, n_samples),
        'volume_sma': np.random.uniform(1000, 5000, n_samples),
        'price_sma': np.random.uniform(95, 105, n_samples),
        'price': np.random.uniform(90, 110, n_samples),
        'volume': np.random.uniform(500, 3000, n_samples),
        'market_cap': np.random.uniform(1e9, 1e10, n_samples),
        'pe_ratio': np.random.uniform(5, 25, n_samples),
        'pb_ratio': np.random.uniform(0.5, 3, n_samples),
        'debt_to_equity': np.random.uniform(0.1, 1.5, n_samples),
        'roe': np.random.uniform(0.05, 0.25, n_samples),
        'roa': np.random.uniform(0.02, 0.15, n_samples),
        'target': np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
    })
    
    print(f"   ✅ Test verisi oluşturuldu: {n_samples} örnek")
    print(f"   📊 Özellik sayısı: {len(test_data.columns) - 1}")
    
    # LightGBM modeli oluştur ve eğit
    print("\n📊 LightGBM Model Testi:")
    lightgbm_config = ml_models.model_configs["LIGHTGBM_DAILY"]
    success = ml_models.create_lightgbm_model(lightgbm_config)
    
    if success:
        print("   ✅ LightGBM modeli oluşturuldu")
        
        # Modeli eğit
        train_success = ml_models.train_lightgbm_model("LIGHTGBM_DAILY", test_data)
        if train_success:
            print("   ✅ LightGBM modeli eğitildi")
            
            # Performans değerlendir
            performance = ml_models.evaluate_model_performance("LIGHTGBM_DAILY", test_data)
            if performance:
                print(f"   📊 Model performansı:")
                print(f"      📊 Accuracy: {performance.accuracy:.3f}")
                print(f"      📊 F1 Score: {performance.f1_score:.3f}")
                print(f"      📊 ROC AUC: {performance.roc_auc:.3f}")
    
    # LSTM modeli oluştur ve eğit
    print("\n📊 LSTM Model Testi:")
    lstm_config = ml_models.model_configs["LSTM_4H"]
    success = ml_models.create_lstm_model(lstm_config)
    
    if success:
        print("   ✅ LSTM modeli oluşturuldu")
        
        # Modeli eğit
        train_success = ml_models.train_lstm_model("LSTM_4H", test_data)
        if train_success:
            print("   ✅ LSTM modeli eğitildi")
    
    # TimeGPT modeli oluştur ve eğit
    print("\n📊 TimeGPT Model Testi:")
    timegpt_config = ml_models.model_configs["TIMEGPT_10D"]
    success = ml_models.create_timegpt_model(timegpt_config)
    
    if success:
        print("   ✅ TimeGPT modeli oluşturuldu")
        
        # Modeli eğit
        train_success = ml_models.train_timegpt_model("TIMEGPT_10D", test_data)
        if train_success:
            print("   ✅ TimeGPT modeli eğitildi")
    
    # Ensemble tahmin testi
    print("\n📊 Ensemble Tahmin Testi:")
    ensemble_result = ml_models.generate_ensemble_prediction(test_data.tail(10))
    
    if ensemble_result:
        print("   ✅ Ensemble tahmin üretildi")
        ensemble_pred = ensemble_result['ensemble_prediction']
        if isinstance(ensemble_pred, np.ndarray):
            print(f"   📊 Ensemble tahmin: {np.mean(ensemble_pred):.3f}")
        else:
            print(f"   📊 Ensemble tahmin: {ensemble_pred:.3f}")
        print(f"   📊 Kullanılan ağırlıklar: {ensemble_result['weights']}")
    
    # Trading sinyali üretimi
    print("\n📊 Trading Sinyali Üretimi:")
    signal = ml_models.generate_trading_signal("SISE.IS", test_data.tail(20), 100.0)
    
    if signal:
        print("   ✅ Trading sinyali üretildi")
        print(f"   📊 Sinyal tipi: {signal.signal_type}")
        print(f"   📊 Güven skoru: {signal.confidence:.3f}")
        print(f"   📊 Ensemble tahmin: {signal.ensemble_prediction:.3f}")
    
    # Model özeti
    print("\n📊 Model Özeti:")
    summary = ml_models.get_model_summary()
    print(f"   ✅ Model özeti alındı")
    print(f"   📊 Toplam model: {summary['total_models']}")
    print(f"   📊 Eğitilmiş model: {summary['trained_models']}")
    print(f"   📊 Toplam sinyal: {summary['total_signals']}")
    print(f"   📊 Model tipleri: {summary['model_types']}")
    
    print("\n✅ Advanced ML Models Test Tamamlandı!")


if __name__ == "__main__":
    test_advanced_ml_models()
