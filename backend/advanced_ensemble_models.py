"""
PRD v2.0 - Advanced Ensemble Models
Gelişmiş AI ensemble: XGBoost, CatBoost, Neural Networks, Transformer Models
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple, Any
import joblib
import json
import warnings
warnings.filterwarnings('ignore')

# Machine Learning
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.pipeline import Pipeline

# Advanced ML
import xgboost as xgb
import lightgbm as lgb
import catboost as cb

# Deep Learning
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, optimizers, callbacks
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠️ TensorFlow bulunamadı, deep learning devre dışı")

# Time Series
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("⚠️ StatsModels bulunamadı, ARIMA devre dışı")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedEnsembleModels:
    """Gelişmiş AI ensemble modelleri"""
    
    def __init__(self):
        self.models = {}
        self.ensemble = None
        self.scaler = RobustScaler()
        self.feature_importance = {}
        self.performance_history = []
        
        # Model türleri
        self.model_types = {
            "tree_based": ["RandomForest", "XGBoost", "LightGBM", "CatBoost", "GradientBoosting"],
            "neural_networks": ["MLP", "DeepNN", "LSTM", "Transformer"],
            "statistical": ["LogisticRegression", "SVM", "ARIMA", "SARIMAX"],
            "ensemble": ["Voting", "Stacking", "Blending"]
        }
        
        # Hyperparameter grids
        self.param_grids = self._get_param_grids()
        
    def _get_param_grids(self) -> Dict:
        """Hyperparameter grid'leri"""
        return {
            "RandomForest": {
                "n_estimators": [100, 200, 300],
                "max_depth": [10, 15, 20],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4]
            },
            "XGBoost": {
                "n_estimators": [100, 200, 300],
                "max_depth": [6, 8, 10],
                "learning_rate": [0.01, 0.05, 0.1],
                "subsample": [0.8, 0.9, 1.0],
                "colsample_bytree": [0.8, 0.9, 1.0]
            },
            "LightGBM": {
                "n_estimators": [100, 200, 300],
                "max_depth": [6, 8, 10],
                "learning_rate": [0.01, 0.05, 0.1],
                "num_leaves": [31, 63, 127],
                "subsample": [0.8, 0.9, 1.0]
            },
            "CatBoost": {
                "iterations": [100, 200, 300],
                "depth": [6, 8, 10],
                "learning_rate": [0.01, 0.05, 0.1],
                "l2_leaf_reg": [1, 3, 5, 7]
            }
        }
    
    def create_advanced_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Gelişmiş özellikler oluştur"""
        try:
            df = data.copy()
            
            # 1. Technical Indicators (mevcut)
            # ... (mevcut teknik indikatörler)
            
            # 2. Advanced Statistical Features
            # Rolling statistics
            for window in [5, 10, 20, 50]:
                df[f'RETURN_{window}D'] = df['Close'].pct_change(window)
                df[f'VOLATILITY_{window}D'] = df['Close'].pct_change().rolling(window).std()
                df[f'SHARPE_{window}D'] = df[f'RETURN_{window}D'] / df[f'VOLATILITY_{window}D']
                df[f'MAX_DRAWDOWN_{window}D'] = self._calculate_max_drawdown(df['Close'], window)
                df[f'CALMAR_{window}D'] = df[f'RETURN_{window}D'] / df[f'MAX_DRAWDOWN_{window}D']
            
            # 3. Price Action Features
            df['PRICE_RANGE'] = (df['High'] - df['Low']) / df['Close']
            df['BODY_SIZE'] = abs(df['Close'] - df['Open']) / df['Close']
            df['UPPER_SHADOW'] = (df['High'] - np.maximum(df['Open'], df['Close'])) / df['Close']
            df['LOWER_SHADOW'] = (np.minimum(df['Open'], df['Close']) - df['Low']) / df['Close']
            
            # 4. Volume Features
            df['VOLUME_PRICE_TREND'] = df['Volume'] * df['Close'].pct_change()
            df['VOLUME_MA_RATIO'] = df['Volume'] / df['Volume'].rolling(20).mean()
            df['VOLUME_WEIGHTED_AVG'] = (df['Volume'] * df['Close']).rolling(20).sum() / df['Volume'].rolling(20).sum()
            
            # 5. Momentum Features
            df['ROC_5'] = df['Close'].pct_change(5)
            df['ROC_10'] = df['Close'].pct_change(10)
            df['ROC_20'] = df['Close'].pct_change(20)
            df['MOMENTUM_ACCELERATION'] = df['ROC_5'] - df['ROC_20']
            
            # 6. Volatility Features
            df['ATR_RATIO'] = df['ATR'] / df['Close']
            df['BB_POSITION'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
            df['BB_SQUEEZE'] = df['BB_Width'] < df['BB_Width'].rolling(20).quantile(0.2)
            
            # 7. Trend Features
            df['TREND_STRENGTH'] = abs(df['SMA_20'] - df['SMA_50']) / df['SMA_50']
            df['TREND_ACCELERATION'] = df['TREND_STRENGTH'].diff()
            df['TREND_REVERSAL'] = ((df['SMA_20'] > df['SMA_50']) & (df['SMA_20'].shift(1) <= df['SMA_50'].shift(1))).astype(int)
            
            # 8. Cross-Asset Features (placeholder)
            df['USDTRY_CORRELATION'] = 0.0
            df['GOLD_CORRELATION'] = 0.0
            df['OIL_CORRELATION'] = 0.0
            
            # 9. Market Regime Features
            df['MARKET_REGIME'] = self._detect_market_regime(df)
            df['VOLATILITY_REGIME'] = self._detect_volatility_regime(df)
            
            # 10. Sentiment Features (placeholder)
            df['NEWS_SENTIMENT'] = 0.0
            df['SOCIAL_SENTIMENT'] = 0.0
            df['ANALYST_RATING'] = 0.0
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Gelişmiş özellik hatası: {e}")
            return data
    
    def _calculate_max_drawdown(self, prices: pd.Series, window: int) -> pd.Series:
        """Maksimum drawdown hesapla"""
        try:
            rolling_max = prices.rolling(window).max()
            drawdown = (prices - rolling_max) / rolling_max
            return drawdown.abs()
        except:
            return pd.Series(0, index=prices.index)
    
    def _detect_market_regime(self, df: pd.DataFrame) -> pd.Series:
        """Market rejimi tespit et"""
        try:
            # Basit market regime detection
            regime = pd.Series(0, index=df.index)
            
            # Bull market: SMA20 > SMA50 and positive momentum
            bull_condition = (df['SMA_20'] > df['SMA_50']) & (df['ROC_20'] > 0)
            regime[bull_condition] = 1
            
            # Bear market: SMA20 < SMA50 and negative momentum
            bear_condition = (df['SMA_20'] < df['SMA_50']) & (df['ROC_20'] < 0)
            regime[bear_condition] = -1
            
            # Sideways: neither bull nor bear
            regime[~bull_condition & ~bear_condition] = 0
            
            return regime
        except:
            return pd.Series(0, index=df.index)
    
    def _detect_volatility_regime(self, df: pd.DataFrame) -> pd.Series:
        """Volatilite rejimi tespit et"""
        try:
            volatility = df['Close'].pct_change().rolling(20).std()
            vol_quantile = volatility.rolling(50).quantile(0.8)
            
            regime = pd.Series(0, index=df.index)
            regime[volatility > vol_quantile] = 1  # High volatility
            regime[volatility < volatility.rolling(50).quantile(0.2)] = -1  # Low volatility
            
            return regime
        except:
            return pd.Series(0, index=df.index)
    
    def train_xgboost_model(self, X: pd.DataFrame, y: pd.Series, symbol: str) -> Dict:
        """XGBoost model eğit"""
        try:
            logger.info(f"🚀 {symbol} için XGBoost model eğitiliyor...")
            
            # Time series split
            tscv = TimeSeriesSplit(n_splits=5)
            
            # Grid search
            xgb_model = xgb.XGBClassifier(
                objective='binary:logistic',
                eval_metric='logloss',
                random_state=42,
                n_jobs=-1
            )
            
            grid_search = GridSearchCV(
                xgb_model,
                self.param_grids["XGBoost"],
                cv=tscv,
                scoring='f1',
                n_jobs=-1,
                verbose=0
            )
            
            grid_search.fit(X, y)
            
            # Best model
            best_model = grid_search.best_estimator_
            best_params = grid_search.best_params_
            
            # Cross-validation scores
            cv_scores = []
            for train_idx, val_idx in tscv.split(X):
                X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                
                best_model.fit(X_train, y_train)
                y_pred = best_model.predict(X_val)
                y_pred_proba = best_model.predict_proba(X_val)[:, 1]
                
                cv_scores.append({
                    'accuracy': accuracy_score(y_val, y_pred),
                    'precision': precision_score(y_val, y_pred, zero_division=0),
                    'recall': recall_score(y_val, y_pred, zero_division=0),
                    'f1': f1_score(y_val, y_pred, zero_division=0),
                    'roc_auc': roc_auc_score(y_val, y_pred_proba)
                })
            
            # Feature importance
            feature_importance = dict(zip(X.columns, best_model.feature_importances_))
            
            # Model kaydet
            self.models[f"{symbol}_XGBoost"] = best_model
            self.feature_importance[f"{symbol}_XGBoost"] = feature_importance
            
            logger.info(f"✅ XGBoost model eğitimi tamamlandı")
            logger.info(f"📊 En iyi parametreler: {best_params}")
            
            return {
                "symbol": symbol,
                "model_type": "XGBoost",
                "best_params": best_params,
                "cv_scores": cv_scores,
                "avg_scores": {
                    'accuracy': np.mean([s['accuracy'] for s in cv_scores]),
                    'precision': np.mean([s['precision'] for s in cv_scores]),
                    'recall': np.mean([s['recall'] for s in cv_scores]),
                    'f1': np.mean([s['f1'] for s in cv_scores]),
                    'roc_auc': np.mean([s['roc_auc'] for s in cv_scores])
                },
                "feature_importance": feature_importance,
                "training_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ XGBoost eğitimi hatası: {e}")
            return {"error": str(e)}
    
    def train_lightgbm_model(self, X: pd.DataFrame, y: pd.Series, symbol: str) -> Dict:
        """LightGBM model eğit"""
        try:
            logger.info(f"🚀 {symbol} için LightGBM model eğitiliyor...")
            
            # Time series split
            tscv = TimeSeriesSplit(n_splits=5)
            
            # Grid search
            lgb_model = lgb.LGBMClassifier(
                objective='binary',
                metric='binary_logloss',
                random_state=42,
                n_jobs=-1,
                verbose=-1
            )
            
            grid_search = GridSearchCV(
                lgb_model,
                self.param_grids["LightGBM"],
                cv=tscv,
                scoring='f1',
                n_jobs=-1,
                verbose=0
            )
            
            grid_search.fit(X, y)
            
            # Best model
            best_model = grid_search.best_estimator_
            best_params = grid_search.best_params_
            
            # Cross-validation scores
            cv_scores = []
            for train_idx, val_idx in tscv.split(X):
                X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                
                best_model.fit(X_train, y_train)
                y_pred = best_model.predict(X_val)
                y_pred_proba = best_model.predict_proba(X_val)[:, 1]
                
                cv_scores.append({
                    'accuracy': accuracy_score(y_val, y_pred),
                    'precision': precision_score(y_val, y_pred, zero_division=0),
                    'recall': recall_score(y_val, y_pred, zero_division=0),
                    'f1': f1_score(y_val, y_pred, zero_division=0),
                    'roc_auc': roc_auc_score(y_val, y_pred_proba)
                })
            
            # Feature importance
            feature_importance = dict(zip(X.columns, best_model.feature_importances_))
            
            # Model kaydet
            self.models[f"{symbol}_LightGBM"] = best_model
            self.feature_importance[f"{symbol}_LightGBM"] = feature_importance
            
            logger.info(f"✅ LightGBM model eğitimi tamamlandı")
            logger.info(f"📊 En iyi parametreler: {best_params}")
            
            return {
                "symbol": symbol,
                "model_type": "LightGBM",
                "best_params": best_params,
                "cv_scores": cv_scores,
                "avg_scores": {
                    'accuracy': np.mean([s['accuracy'] for s in cv_scores]),
                    'precision': np.mean([s['precision'] for s in cv_scores]),
                    'recall': np.mean([s['recall'] for s in cv_scores]),
                    'f1': np.mean([s['f1'] for s in cv_scores]),
                    'roc_auc': np.mean([s['roc_auc'] for s in cv_scores])
                },
                "feature_importance": feature_importance,
                "training_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ LightGBM eğitimi hatası: {e}")
            return {"error": str(e)}
    
    def train_catboost_model(self, X: pd.DataFrame, y: pd.Series, symbol: str) -> Dict:
        """CatBoost model eğit"""
        try:
            logger.info(f"🚀 {symbol} için CatBoost model eğitiliyor...")
            
            # Time series split
            tscv = TimeSeriesSplit(n_splits=5)
            
            # Grid search
            cb_model = cb.CatBoostClassifier(
                loss_function='Logloss',
                eval_metric='AUC',
                random_state=42,
                verbose=False
            )
            
            grid_search = GridSearchCV(
                cb_model,
                self.param_grids["CatBoost"],
                cv=tscv,
                scoring='f1',
                n_jobs=-1,
                verbose=0
            )
            
            grid_search.fit(X, y)
            
            # Best model
            best_model = grid_search.best_estimator_
            best_params = grid_search.best_params_
            
            # Cross-validation scores
            cv_scores = []
            for train_idx, val_idx in tscv.split(X):
                X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                
                best_model.fit(X_train, y_train)
                y_pred = best_model.predict(X_val)
                y_pred_proba = best_model.predict_proba(X_val)[:, 1]
                
                cv_scores.append({
                    'accuracy': accuracy_score(y_val, y_pred),
                    'precision': precision_score(y_val, y_pred, zero_division=0),
                    'recall': recall_score(y_val, y_pred, zero_division=0),
                    'f1': f1_score(y_val, y_pred, zero_division=0),
                    'roc_auc': roc_auc_score(y_val, y_pred_proba)
                })
            
            # Feature importance
            feature_importance = dict(zip(X.columns, best_model.feature_importances_))
            
            # Model kaydet
            self.models[f"{symbol}_CatBoost"] = best_model
            self.feature_importance[f"{symbol}_CatBoost"] = feature_importance
            
            logger.info(f"✅ CatBoost model eğitimi tamamlandı")
            logger.info(f"📊 En iyi parametreler: {best_params}")
            
            return {
                "symbol": symbol,
                "model_type": "CatBoost",
                "best_params": best_params,
                "cv_scores": cv_scores,
                "avg_scores": {
                    'accuracy': np.mean([s['accuracy'] for s in cv_scores]),
                    'precision': np.mean([s['precision'] for s in cv_scores]),
                    'recall': np.mean([s['recall'] for s in cv_scores]),
                    'f1': np.mean([s['f1'] for s in cv_scores]),
                    'roc_auc': np.mean([s['roc_auc'] for s in cv_scores])
                },
                "feature_importance": feature_importance,
                "training_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ CatBoost eğitimi hatası: {e}")
            return {"error": str(e)}
    
    def create_voting_ensemble(self, symbol: str) -> Dict:
        """Voting ensemble oluştur"""
        try:
            logger.info(f"🚀 {symbol} için voting ensemble oluşturuluyor...")
            
            # Mevcut modelleri kontrol et
            required_models = [f"{symbol}_XGBoost", f"{symbol}_LightGBM", f"{symbol}_CatBoost"]
            available_models = []
            
            for model_name in required_models:
                if model_name in self.models:
                    available_models.append((model_name, self.models[model_name]))
            
            if len(available_models) < 2:
                return {"error": "En az 2 model gerekli"}
            
            # Voting classifier
            estimators = [(name, model) for name, model in available_models]
            voting_clf = VotingClassifier(
                estimators=estimators,
                voting='soft'  # Probability-based voting
            )
            
            # Ensemble kaydet
            self.ensemble = voting_clf
            self.models[f"{symbol}_Ensemble"] = voting_clf
            
            logger.info(f"✅ Voting ensemble oluşturuldu: {len(available_models)} model")
            
            return {
                "symbol": symbol,
                "ensemble_type": "Voting",
                "models": [name for name, _ in available_models],
                "voting_method": "soft",
                "creation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ensemble oluşturma hatası: {e}")
            return {"error": str(e)}
    
    def predict_ensemble(self, X: pd.DataFrame, symbol: str) -> Dict:
        """Ensemble ile tahmin"""
        try:
            if self.ensemble is None:
                return {"error": "Ensemble henüz oluşturulmadı"}
            
            # Tahmin
            prediction = self.ensemble.predict(X)[0]
            probability = self.ensemble.predict_proba(X)[0]
            
            # Model bazında tahminler
            individual_predictions = {}
            for model_name, model in self.models.items():
                if symbol in model_name and "Ensemble" not in model_name:
                    try:
                        pred = model.predict(X)[0]
                        prob = model.predict_proba(X)[0]
                        individual_predictions[model_name] = {
                            "prediction": pred,
                            "probability": prob[1] if pred == 1 else prob[0]
                        }
                    except:
                        continue
            
            return {
                "symbol": symbol,
                "ensemble_prediction": prediction,
                "ensemble_probability": probability[1] if prediction == 1 else probability[0],
                "individual_predictions": individual_predictions,
                "prediction_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Ensemble tahmin hatası: {e}")
            return {"error": str(e)}
    
    def get_model_performance(self, symbol: str) -> Dict:
        """Model performans raporu"""
        try:
            performance_report = {
                "symbol": symbol,
                "models": {},
                "ensemble": None,
                "overall_performance": {}
            }
            
            # Bireysel model performansları
            for model_name, model in self.models.items():
                if symbol in model_name:
                    if "Ensemble" in model_name:
                        performance_report["ensemble"] = {
                            "model_name": model_name,
                            "model_type": "Voting Ensemble"
                        }
                    else:
                        # Model performans metrikleri burada hesaplanacak
                        performance_report["models"][model_name] = {
                            "model_type": model_name.split("_")[-1],
                            "feature_count": len(self.feature_importance.get(model_name, {}))
                        }
            
            # Genel performans
            if performance_report["models"]:
                performance_report["overall_performance"] = {
                    "total_models": len(performance_report["models"]),
                    "has_ensemble": performance_report["ensemble"] is not None,
                    "report_date": datetime.now().isoformat()
                }
            
            return performance_report
            
        except Exception as e:
            logger.error(f"❌ Performans raporu hatası: {e}")
            return {"error": str(e)}

# Test fonksiyonu
if __name__ == "__main__":
    ensemble = AdvancedEnsembleModels()
    
    # Test hissesi
    symbol = "GARAN.IS"
    logger.info(f"🧪 {symbol} için gelişmiş ensemble test ediliyor...")
    
    # Örnek veri oluştur (gerçek uygulamada accuracy_optimizer'dan gelecek)
    # Bu test için basit veri
    logger.info("✅ Advanced Ensemble Models modülü hazır!")
    logger.info(f"📊 Desteklenen model türleri: {list(ensemble.model_types.keys())}")
    logger.info(f"🔧 Hyperparameter grid'ler: {list(ensemble.param_grids.keys())}")
