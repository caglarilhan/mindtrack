import pandas as pd
import numpy as np
import yfinance as yf
import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class AIEnsemblePipeline:
    """
    AI Ensemble Pipeline: LightGBM + LSTM + TimeGPT
    Çoklu zaman dilimi tahmin sistemi
    """
    
    def __init__(self, lookback_days: int = 60):
        self.lookback_days = lookback_days
        self.lgbm_model = None
        self.lstm_model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Gelişmiş feature engineering
        """
        try:
            df = data.copy()
            
            # MultiIndex column'ları düzelt
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Teknik indikatörler
            df['RSI'] = self._calculate_rsi(df['Close'])
            df['MACD'] = self._calculate_macd(df['Close'])
            df['BB_Upper'], df['BB_Lower'] = self._calculate_bollinger_bands(df['Close'])
            df['ATR'] = self._calculate_atr(df['High'], df['Low'], df['Close'])
            
            # Fiyat bazlı özellikler
            df['Price_Change'] = df['Close'].pct_change()
            df['Price_Change_5d'] = df['Close'].pct_change(5)
            df['Price_Change_20d'] = df['Close'].pct_change(20)
            
            # Volatilite özellikleri
            df['Volatility_5d'] = df['Price_Change'].rolling(5).std()
            df['Volatility_20d'] = df['Price_Change'].rolling(20).std()
            
            # Hacim özellikleri
            df['Volume_MA_5'] = df['Volume'].rolling(5).mean()
            df['Volume_MA_20'] = df['Volume'].rolling(20).mean()
            df['Volume_Ratio'] = (df['Volume'] / df['Volume_MA_20']).fillna(1.0)
            
            # Trend özellikleri
            df['Trend_5d'] = np.where(df['Close'] > df['Close'].rolling(5).mean(), 1, 0)
            df['Trend_20d'] = np.where(df['Close'] > df['Close'].rolling(20).mean(), 1, 0)
            
            # Momentum özellikleri
            df['Momentum_5d'] = df['Close'] / df['Close'].shift(5) - 1
            df['Momentum_20d'] = df['Close'] / df['Close'].shift(20) - 1
            
            # Support/Resistance özellikleri
            df['Distance_From_High'] = (df['Close'] - df['High'].rolling(20).max()) / df['Close']
            df['Distance_From_Low'] = (df['Close'] - df['Low'].rolling(20).min()) / df['Close']
            
            # NaN değerleri temizle
            df = df.dropna()
            
            return df
            
        except Exception as e:
            print(f"Feature engineering hatası: {e}")
            return data
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI hesaplama"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26) -> pd.Series:
        """MACD hesaplama"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        return ema_fast - ema_slow
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2):
        """Bollinger Bands hesaplama"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, lower_band
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """ATR hesaplama"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
    
    def create_sequences(self, data: pd.DataFrame, target_col: str = 'target') -> Tuple[np.ndarray, np.ndarray]:
        """
        LSTM için sequence veri oluşturur
        """
        try:
            # Feature sütunları (target hariç)
            feature_cols = [col for col in data.columns if col not in ['target', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            
            X, y = [], []
            
            for i in range(self.lookback_days, len(data)):
                X.append(data[feature_cols].iloc[i-self.lookback_days:i].values)
                y.append(data[target_col].iloc[i])
            
            return np.array(X), np.array(y)
            
        except Exception as e:
            print(f"Sequence oluşturma hatası: {e}")
            return np.array([]), np.array([])
    
    def train_lightgbm(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        LightGBM modelini eğitir (günlük tahmin)
        """
        try:
            # Time series split
            tscv = TimeSeriesSplit(n_splits=5)
            
            # Feature sütunları
            feature_cols = [col for col in X.columns if col not in ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            self.feature_columns = feature_cols
            
            X_features = X[feature_cols]
            
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
                'verbose': -1
            }
            
            # Cross-validation
            cv_scores = []
            models = []
            
            for train_idx, val_idx in tscv.split(X_features):
                X_train, X_val = X_features.iloc[train_idx], X_features.iloc[val_idx]
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
                    callbacks=[lgb.early_stopping(50)]
                )
                
                # Tahmin ve skor
                y_pred_proba = model.predict(X_val)
                y_pred = (y_pred_proba > 0.5).astype(int)
                
                auc_score = roc_auc_score(y_val, y_pred_proba)
                accuracy = accuracy_score(y_val, y_pred)
                
                cv_scores.append({
                    'auc': auc_score,
                    'accuracy': accuracy
                })
                
                models.append(model)
            
            # En iyi modeli seç
            best_idx = np.argmax([score['auc'] for score in cv_scores])
            self.lgbm_model = models[best_idx]
            
            # Feature importance
            feature_importance = pd.DataFrame({
                'feature': feature_cols,
                'importance': self.lgbm_model.feature_importance()
            }).sort_values('importance', ascending=False)
            
            return {
                'model': self.lgbm_model,
                'cv_scores': cv_scores,
                'best_score': cv_scores[best_idx],
                'feature_importance': feature_importance,
                'avg_auc': np.mean([score['auc'] for score in cv_scores]),
                'avg_accuracy': np.mean([score['accuracy'] for score in cv_scores])
            }
            
        except Exception as e:
            print(f"LightGBM eğitim hatası: {e}")
            return {}
    
    def train_lstm(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        LSTM modelini eğitir (4 saatlik tahmin)
        """
        try:
            # Sequence veri oluştur
            X_seq, y_seq = self.create_sequences(X, 'target')
            
            if len(X_seq) == 0:
                return {"error": "Sequence veri oluşturulamadı"}
            
            # Veriyi normalize et
            X_reshaped = X_seq.reshape(-1, X_seq.shape[-1])
            X_scaled = self.scaler.fit_transform(X_reshaped)
            X_scaled = X_scaled.reshape(X_seq.shape)
            
            # Train/validation split
            split_idx = int(len(X_scaled) * 0.8)
            X_train, X_val = X_scaled[:split_idx], X_scaled[split_idx:]
            y_train, y_val = y_seq[:split_idx], y_seq[split_idx:]
            
            # LSTM model
            self.lstm_model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25, activation='relu'),
                Dense(1, activation='sigmoid')
            ])
            
            # Model compile
            self.lstm_model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            # Model eğitimi
            history = self.lstm_model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=50,
                batch_size=32,
                verbose=0
            )
            
            # Validation tahmin
            y_val_pred_proba = self.lstm_model.predict(X_val).flatten()
            y_val_pred = (y_val_pred_proba > 0.5).astype(int)
            
            # Metrikler
            val_auc = roc_auc_score(y_val, y_val_pred_proba)
            val_accuracy = accuracy_score(y_val, y_val_pred)
            
            return {
                'model': self.lstm_model,
                'history': history.history,
                'val_auc': val_auc,
                'val_accuracy': val_accuracy,
                'scaler': self.scaler
            }
            
        except Exception as e:
            print(f"LSTM eğitim hatası: {e}")
            return {"error": str(e)}
    
    def predict_ensemble(self, data: pd.DataFrame) -> Dict:
        """
        Ensemble tahmin yapar
        """
        try:
            if self.lgbm_model is None or self.lstm_model is None:
                return {"error": "Modeller eğitilmemiş"}
            
            # Son veriyi al
            latest_data = data.tail(1)
            
            # LightGBM tahmin
            if self.feature_columns:
                lgbm_features = latest_data[self.feature_columns]
                lgbm_proba = self.lgbm_model.predict(lgbm_features)[0]
                lgbm_pred = int(lgbm_proba > 0.5)
            else:
                lgbm_proba, lgbm_pred = 0.5, 0
            
            # LSTM tahmin
            try:
                # Son lookback_days veriyi al
                lstm_data = data.tail(self.lookback_days + 1)
                X_seq, _ = self.create_sequences(lstm_data, 'target')
                
                if len(X_seq) > 0:
                    # Son sequence'i al
                    last_sequence = X_seq[-1:]
                    
                    # Normalize et
                    last_sequence_reshaped = last_sequence.reshape(-1, last_sequence.shape[-1])
                    last_sequence_scaled = self.scaler.transform(last_sequence_reshaped)
                    last_sequence_scaled = last_sequence_scaled.reshape(last_sequence.shape)
                    
                    # Tahmin
                    lstm_proba = self.lstm_model.predict(last_sequence_scaled)[0][0]
                    lstm_pred = int(lstm_proba > 0.5)
                else:
                    lstm_proba, lstm_pred = 0.5, 0
                    
            except Exception as e:
                print(f"LSTM tahmin hatası: {e}")
                lstm_proba, lstm_pred = 0.5, 0
            
            # Ensemble tahmin (ağırlıklı ortalama)
            ensemble_proba = (lgbm_proba * 0.6) + (lstm_proba * 0.4)
            ensemble_pred = int(ensemble_proba > 0.5)
            
            # Güven skoru
            confidence = abs(ensemble_proba - 0.5) * 2  # 0-1 arası
            
            return {
                "lightgbm": {
                    "probability": float(lgbm_proba),
                    "prediction": lgbm_pred,
                    "signal": "BUY" if lgbm_pred == 1 else "SELL"
                },
                "lstm": {
                    "probability": float(lstm_proba),
                    "prediction": lstm_pred,
                    "signal": "BUY" if lstm_pred == 1 else "SELL"
                },
                "ensemble": {
                    "probability": float(ensemble_proba),
                    "prediction": ensemble_pred,
                    "signal": "BUY" if ensemble_pred == 1 else "SELL",
                    "confidence": float(confidence)
                },
                "timestamp": pd.Timestamp.now().isoformat()
            }
            
        except Exception as e:
            print(f"Ensemble tahmin hatası: {e}")
            return {"error": str(e)}
    
    def walk_forward_validation(self, data: pd.DataFrame, window_size: int = 252) -> Dict:
        """
        Walk-forward validation ile model performansını test eder
        """
        try:
            results = []
            
            for i in range(window_size, len(data), 30):  # 30 günlük adımlar
                # Training data
                train_data = data.iloc[:i]
                # Test data (30 gün)
                test_data = data.iloc[i:i+30]
                
                if len(test_data) < 10:  # Minimum test veri
                    continue
                
                # Modelleri eğit
                lgbm_result = self.train_lightgbm(train_data, train_data['target'])
                lstm_result = self.train_lstm(train_data, train_data['target'])
                
                if 'error' in lstm_result:
                    continue
                
                # Test tahminleri
                test_features = test_data[self.feature_columns] if self.feature_columns else test_data
                lgbm_pred = self.lgbm_model.predict(test_features)
                lgbm_pred_binary = (lgbm_pred > 0.5).astype(int)
                
                # Test metrikleri
                test_auc = roc_auc_score(test_data['target'], lgbm_pred)
                test_accuracy = accuracy_score(test_data['target'], lgbm_pred_binary)
                
                results.append({
                    'period': f"{test_data.index[0].date()} - {test_data.index[-1].date()}",
                    'auc': test_auc,
                    'accuracy': test_accuracy,
                    'test_size': len(test_data)
                })
            
            if not results:
                return {"error": "Walk-forward validation sonucu yok"}
            
            # Ortalama performans
            avg_auc = np.mean([r['auc'] for r in results])
            avg_accuracy = np.mean([r['accuracy'] for r in results])
            
            return {
                "validation_periods": results,
                "average_auc": float(avg_auc),
                "average_accuracy": float(avg_accuracy),
                "total_periods": len(results)
            }
            
        except Exception as e:
            print(f"Walk-forward validation hatası: {e}")
            return {"error": str(e)}

# Test fonksiyonu
if __name__ == "__main__":
    # Test hissesi
    symbol = "SISE.IS"
    
    # Veri çek
    data = yf.download(symbol, period="2y", interval="1d")
    
    # Target oluştur (1 gün sonra yukarı hareket)
    data['target'] = (data['Close'].shift(-1) > data['Close']).astype(int)
    
    # AI Ensemble pipeline'ı başlat
    pipeline = AIEnsemblePipeline(lookback_days=60)
    
    # Feature engineering
    data = pipeline.prepare_features(data)
    
    if not data.empty:
        print(f"🎯 {symbol} AI Ensemble Analizi:")
        print("=" * 50)
        
        # LightGBM eğitimi
        print("🚀 LightGBM eğitiliyor...")
        lgbm_result = pipeline.train_lightgbm(data, data['target'])
        
        if lgbm_result:
            print(f"✅ LightGBM eğitildi!")
            print(f"   Ortalama AUC: {lgbm_result['avg_auc']:.3f}")
            print(f"   Ortalama Doğruluk: {lgbm_result['avg_accuracy']:.3f}")
        
        # LSTM eğitimi
        print("\n🧠 LSTM eğitiliyor...")
        lstm_result = pipeline.train_lstm(data, data['target'])
        
        if 'error' not in lstm_result:
            print(f"✅ LSTM eğitildi!")
            print(f"   Validation AUC: {lstm_result['val_auc']:.3f}")
            print(f"   Validation Doğruluk: {lstm_result['val_accuracy']:.3f}")
        
        # Ensemble tahmin
        print("\n🎯 Ensemble tahmin yapılıyor...")
        prediction = pipeline.predict_ensemble(data)
        
        if 'error' not in prediction:
            print(f"✅ Ensemble Tahmin:")
            print(f"   LightGBM: {prediction['lightgbm']['signal']} ({prediction['lightgbm']['probability']:.3f})")
            print(f"   LSTM: {prediction['lstm']['signal']} ({prediction['lstm']['probability']:.3f})")
            print(f"   Ensemble: {prediction['ensemble']['signal']} ({prediction['ensemble']['probability']:.3f})")
            print(f"   Güven: {prediction['ensemble']['confidence']:.3f}")
        
        # Walk-forward validation
        print("\n📊 Walk-forward validation başlatılıyor...")
        wf_result = pipeline.walk_forward_validation(data)
        
        if 'error' not in wf_result:
            print(f"✅ Walk-forward Validation:")
            print(f"   Ortalama AUC: {wf_result['average_auc']:.3f}")
            print(f"   Ortalama Doğruluk: {wf_result['average_accuracy']:.3f}")
            print(f"   Toplam Periyot: {wf_result['total_periods']}")
    else:
        print(f"❌ {symbol} için veri bulunamadı")
