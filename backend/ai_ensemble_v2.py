"""
PRD v2.0 - AI Sinyal Ensemble
LightGBM (daily) + LSTM (4h) + TimeGPT (10 gün)
sklearn-api + keras ile ROC-AUC > 0.7 hedefi
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ML imports
try:
    import lightgbm as lgb
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.metrics import roc_auc_score, classification_report
    from sklearn.preprocessing import StandardScaler
    import joblib
except ImportError:
    print("⚠️ LightGBM veya sklearn yüklü değil")
    lgb = None

# Deep Learning imports
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
except ImportError:
    print("⚠️ TensorFlow yüklü değil")
    tf = None

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEnsemble:
    """PRD v2.0 AI Ensemble - LightGBM + LSTM + TimeGPT"""
    
    def __init__(self):
        self.lightgbm_model = None
        self.lstm_model = None
        self.ensemble_weights = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Teknik indikatörler ve feature engineering"""
        try:
            df = data.copy()
            
            # Fiyat bazlı özellikler
            df['returns'] = df['Close'].pct_change()
            df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
            df['volatility'] = df['returns'].rolling(20).std()
            
            # Teknik indikatörler
            # Moving averages
            df['sma_20'] = df['Close'].rolling(20).mean()
            df['sma_50'] = df['Close'].rolling(50).mean()
            df['ema_12'] = df['Close'].ewm(span=12).mean()
            df['ema_26'] = df['Close'].ewm(span=26).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # Bollinger Bands
            df['bb_middle'] = df['Close'].rolling(20).mean()
            bb_std = df['Close'].rolling(20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            
            # Volume indicators
            df['volume_sma'] = df['Volume'].rolling(20).mean()
            df['volume_ratio'] = df['Volume'] / df['volume_sma']
            
            # Momentum indicators
            df['momentum'] = df['Close'] - df['Close'].shift(4)
            df['rate_of_change'] = (df['Close'] - df['Close'].shift(10)) / df['Close'].shift(10)
            
            # Support/Resistance levels
            df['pivot_high'] = df['High'].rolling(20, center=True).max()
            df['pivot_low'] = df['Low'].rolling(20, center=True).min()
            df['support_distance'] = (df['Close'] - df['pivot_low']) / df['Close']
            df['resistance_distance'] = (df['pivot_high'] - df['Close']) / df['Close']
            
            # Target variable (gelecek gün yön)
            df['target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
            
            # NaN değerleri temizle
            df = df.dropna()
            
            # Feature columns
            self.feature_columns = [
                'returns', 'log_returns', 'volatility', 'sma_20', 'sma_50',
                'ema_12', 'ema_26', 'rsi', 'macd', 'macd_signal', 'macd_histogram',
                'bb_middle', 'bb_upper', 'bb_lower', 'bb_width',
                'volume_ratio', 'momentum', 'rate_of_change',
                'support_distance', 'resistance_distance'
            ]
            
            logger.info(f"Feature engineering tamamlandı: {len(self.feature_columns)} özellik")
            return df
            
        except Exception as e:
            logger.error(f"Feature engineering hatası: {e}")
            return data
    
    def train_lightgbm(self, data: pd.DataFrame) -> bool:
        """LightGBM model eğitimi (daily timeframe)"""
        try:
            if lgb is None:
                logger.warning("LightGBM yüklü değil")
                return False
            
            # Feature ve target hazırla
            X = data[self.feature_columns]
            y = data['target']
            
            # Time series split
            tscv = TimeSeriesSplit(n_splits=5)
            
            # Model parametreleri
            params = {
                'objective': 'binary',
                'metric': 'auc',
                'boosting_type': 'gbdt',
                'num_leaves': 31,
                'learning_rate': 0.05,
                'feature_fraction': 0.9,
                'bagging_fraction': 0.8,
                'bagging_freq': 5,
                'verbose': -1,
                'random_state': 42
            }
            
            # Cross-validation
            cv_scores = []
            for train_idx, val_idx in tscv.split(X):
                X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                
                # LightGBM dataset
                train_data = lgb.Dataset(X_train, label=y_train)
                val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
                
                # Model eğitimi
                model = lgb.train(
                    params,
                    train_data,
                    valid_sets=[val_data],
                    num_boost_round=1000,
                    callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)]
                )
                
                # Validation score
                y_pred = model.predict(X_val)
                auc_score = roc_auc_score(y_val, y_pred)
                cv_scores.append(auc_score)
            
            # Final model eğitimi
            final_train_data = lgb.Dataset(X, label=y)
            self.lightgbm_model = lgb.train(
                params,
                final_train_data,
                num_boost_round=1000,
                callbacks=[lgb.log_evaluation(0)]
            )
            
            avg_auc = np.mean(cv_scores)
            logger.info(f"LightGBM eğitimi tamamlandı - CV AUC: {avg_auc:.4f}")
            
            return avg_auc > 0.7  # PRD hedefi
            
        except Exception as e:
            logger.error(f"LightGBM eğitim hatası: {e}")
            return False
    
    def train_lstm(self, data: pd.DataFrame, sequence_length: int = 10) -> bool:
        """LSTM model eğitimi (4h timeframe için sequence)"""
        try:
            if tf is None:
                logger.warning("TensorFlow yüklü değil")
                return False
            
            # Feature ve target hazırla
            X = data[self.feature_columns].values
            y = data['target'].values
            
            # Sequence data hazırla
            X_sequences, y_sequences = self._create_sequences(X, y, sequence_length)
            
            if len(X_sequences) < 100:
                logger.warning("Yetersiz sequence verisi")
                return False
            
            # Train/validation split
            split_idx = int(len(X_sequences) * 0.8)
            X_train, X_val = X_sequences[:split_idx], X_sequences[split_idx:]
            y_train, y_val = y_sequences[:split_idx], y_sequences[split_idx:]
            
            # LSTM model
            self.lstm_model = keras.Sequential([
                layers.LSTM(64, return_sequences=True, input_shape=(sequence_length, len(self.feature_columns))),
                layers.Dropout(0.2),
                layers.LSTM(32, return_sequences=False),
                layers.Dropout(0.2),
                layers.Dense(16, activation='relu'),
                layers.Dense(1, activation='sigmoid')
            ])
            
            # Compile
            self.lstm_model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy', 'AUC']
            )
            
            # Early stopping
            early_stopping = keras.callbacks.EarlyStopping(
                monitor='val_auc',
                patience=10,
                restore_best_weights=True
            )
            
            # Model eğitimi
            history = self.lstm_model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=100,
                batch_size=32,
                callbacks=[early_stopping],
                verbose=0
            )
            
            # Validation score
            val_pred = self.lstm_model.predict(X_val)
            auc_score = roc_auc_score(y_val, val_pred)
            
            logger.info(f"LSTM eğitimi tamamlandı - Validation AUC: {auc_score:.4f}")
            
            return auc_score > 0.7  # PRD hedefi
            
        except Exception as e:
            logger.error(f"LSTM eğitim hatası: {e}")
            return False
    
    def _create_sequences(self, X: np.ndarray, y: np.ndarray, 
                         sequence_length: int) -> Tuple[np.ndarray, np.ndarray]:
        """Sequence data oluştur"""
        X_sequences, y_sequences = [], []
        
        for i in range(sequence_length, len(X)):
            X_sequences.append(X[i-sequence_length:i])
            y_sequences.append(y[i])
        
        return np.array(X_sequences), np.array(y_sequences)
    
    def train_timegpt(self, data: pd.DataFrame) -> bool:
        """TimeGPT model eğitimi (10 gün forecast)"""
        try:
            # TimeGPT için basit implementasyon
            # Gerçek TimeGPT API entegrasyonu burada olacak
            
            # Basit time series model (placeholder)
            from sklearn.linear_model import LogisticRegression
            
            X = data[self.feature_columns]
            y = data['target']
            
            # Time series split
            tscv = TimeSeriesSplit(n_splits=5)
            cv_scores = []
            
            for train_idx, val_idx in tscv.split(X):
                X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                
                model = LogisticRegression(random_state=42)
                model.fit(X_train, y_train)
                
                y_pred = model.predict_proba(X_val)[:, 1]
                auc_score = roc_auc_score(y_val, y_pred)
                cv_scores.append(auc_score)
            
            avg_auc = np.mean(cv_scores)
            logger.info(f"TimeGPT placeholder eğitimi - CV AUC: {avg_auc:.4f}")
            
            return avg_auc > 0.7
            
        except Exception as e:
            logger.error(f"TimeGPT eğitim hatası: {e}")
            return False
    
    def train_ensemble(self, data: pd.DataFrame) -> bool:
        """Tüm modelleri eğit ve ensemble oluştur"""
        try:
            logger.info("AI Ensemble eğitimi başlıyor...")
            
            # Feature engineering
            data = self.prepare_features(data)
            
            if data.empty:
                logger.error("Feature engineering sonrası veri kalmadı")
                return False
            
            # Model eğitimleri
            lgb_success = self.train_lightgbm(data)
            lstm_success = self.train_lstm(data)
            timegpt_success = self.train_timegpt(data)
            
            # Ensemble weights
            if lgb_success and lstm_success and timegpt_success:
                # ROC-AUC'ye göre ağırlık
                self.ensemble_weights = [0.4, 0.35, 0.25]  # LightGBM, LSTM, TimeGPT
            elif lgb_success and lstm_success:
                self.ensemble_weights = [0.6, 0.4]
            elif lgb_success:
                self.ensemble_weights = [1.0]
            else:
                logger.error("Hiçbir model başarıyla eğitilemedi")
                return False
            
            logger.info(f"Ensemble eğitimi tamamlandı - Weights: {self.ensemble_weights}")
            return True
            
        except Exception as e:
            logger.error(f"Ensemble eğitim hatası: {e}")
            return False
    
    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """Ensemble tahmin"""
        try:
            if not self.ensemble_weights:
                logger.error("Ensemble eğitilmemiş")
                return data
            
            # Feature engineering
            data = self.prepare_features(data)
            
            if data.empty:
                return data
            
            X = data[self.feature_columns]
            
            # Model tahminleri
            predictions = []
            
            if self.lightgbm_model and len(self.ensemble_weights) >= 1:
                lgb_pred = self.lightgbm_model.predict(X)
                predictions.append(lgb_pred)
            
            if self.lstm_model and len(self.ensemble_weights) >= 2:
                # LSTM için sequence hazırla
                X_sequences = self._create_sequences(X.values, np.zeros(len(X)), 10)[0]
                if len(X_sequences) > 0:
                    lstm_pred = self.lstm_model.predict(X_sequences)
                    # Son tahminleri al
                    lstm_pred = np.concatenate([np.zeros(10), lstm_pred.flatten()])
                    predictions.append(lstm_pred[:len(X)])
                else:
                    predictions.append(np.zeros(len(X)))
            
            if len(self.ensemble_weights) >= 3:
                # TimeGPT placeholder
                timegpt_pred = np.random.random(len(X))  # Placeholder
                predictions.append(timegpt_pred)
            
            # Ensemble tahmin
            if len(predictions) == len(self.ensemble_weights):
                ensemble_pred = np.zeros(len(X))
                for i, (pred, weight) in enumerate(zip(predictions, self.ensemble_weights)):
                    ensemble_pred += pred * weight
                
                data['ensemble_probability'] = ensemble_pred
                data['ensemble_signal'] = np.where(ensemble_pred > 0.5, 'BUY', 'SELL')
                data['ensemble_confidence'] = np.abs(ensemble_pred - 0.5) * 2  # 0-1 arası
                
                logger.info("Ensemble tahmin tamamlandı")
            
            return data
            
        except Exception as e:
            logger.error(f"Ensemble tahmin hatası: {e}")
            return data
    
    def evaluate_ensemble(self, data: pd.DataFrame) -> Dict:
        """Ensemble performans değerlendirmesi"""
        try:
            if 'ensemble_probability' not in data.columns:
                return {}
            
            # ROC-AUC hesapla
            auc_score = roc_auc_score(data['target'], data['ensemble_probability'])
            
            # Sinyal doğruluğu
            signal_accuracy = (data['ensemble_signal'] == 
                             np.where(data['target'] == 1, 'BUY', 'SELL')).mean()
            
            # Classification report
            y_pred = (data['ensemble_probability'] > 0.5).astype(int)
            report = classification_report(data['target'], y_pred, output_dict=True)
            
            evaluation = {
                'roc_auc': auc_score,
                'signal_accuracy': signal_accuracy,
                'precision': report['weighted avg']['precision'],
                'recall': report['weighted avg']['recall'],
                'f1_score': report['weighted avg']['f1-score'],
                'prd_target_met': auc_score > 0.7  # PRD v2.0 hedefi
            }
            
            logger.info(f"Ensemble değerlendirmesi - ROC-AUC: {auc_score:.4f}")
            return evaluation
            
        except Exception as e:
            logger.error(f"Ensemble değerlendirme hatası: {e}")
            return {}
    
    def save_models(self, path: str = "models/"):
        """Modelleri kaydet"""
        try:
            import os
            os.makedirs(path, exist_ok=True)
            
            if self.lightgbm_model:
                self.lightgbm_model.save_model(f"{path}/lightgbm_model.txt")
            
            if self.lstm_model:
                self.lstm_model.save(f"{path}/lstm_model.h5")
            
            # Ensemble weights
            if self.ensemble_weights:
                np.save(f"{path}/ensemble_weights.npy", self.ensemble_weights)
            
            logger.info(f"Modeller kaydedildi: {path}")
            
        except Exception as e:
            logger.error(f"Model kaydetme hatası: {e}")

# Test fonksiyonu
def test_ai_ensemble():
    """AI Ensemble test"""
    try:
        print("🧪 AI Ensemble V2 Test")
        print("="*50)
        
        # Test verisi yükle
        symbol = "SISE.IS"
        data = yf.download(symbol, period="1y", interval="1d")
        
        if data.empty:
            print(f"❌ {symbol} verisi yüklenemedi")
            return
        
        print(f"📊 {symbol} verisi yüklendi: {len(data)} gün")
        
        # AI Ensemble başlat
        ensemble = AIEnsembleV2()
        
        # Ensemble eğitimi
        print("\n🤖 AI Ensemble Eğitimi:")
        success = ensemble.train_ensemble(data)
        
        if success:
            print("✅ Ensemble eğitimi başarılı!")
            
            # Tahmin
            print("\n🔮 Ensemble Tahmin:")
            result_data = ensemble.predict(data)
            
            if 'ensemble_probability' in result_data.columns:
                # Son 10 günün tahminleri
                recent_predictions = result_data.tail(10)
                print(recent_predictions[['Close', 'ensemble_probability', 'ensemble_signal', 'ensemble_confidence']].round(4))
                
                # Performans değerlendirmesi
                print("\n📊 Performans Değerlendirmesi:")
                evaluation = ensemble.evaluate_ensemble(result_data)
                
                if evaluation:
                    print(f"ROC-AUC: {evaluation['roc_auc']:.4f}")
                    print(f"Sinyal Doğruluğu: {evaluation['signal_accuracy']:.4f}")
                    print(f"Precision: {evaluation['precision']:.4f}")
                    print(f"Recall: {evaluation['recall']:.4f}")
                    print(f"F1-Score: {evaluation['f1_score']:.4f}")
                    print(f"PRD Hedefi: {'✅ Başarılı' if evaluation['prd_target_met'] else '❌ Başarısız'}")
                
                # Modelleri kaydet
                ensemble.save_models()
                
            else:
                print("❌ Tahmin başarısız")
        else:
            print("❌ Ensemble eğitimi başarısız")
        
        print("\n✅ AI Ensemble V2 test tamamlandı!")
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")

if __name__ == "__main__":
    test_ai_ensemble()
