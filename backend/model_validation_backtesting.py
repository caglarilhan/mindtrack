"""
Model Validation & Backtesting - Sprint 15: Advanced Integration & API Gateway

Bu modül, cross-validation, walk-forward analizi ve backtesting stratejileri
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
from sklearn.model_selection import TimeSeriesSplit, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.metrics import confusion_matrix, classification_report

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Validasyon sonucu"""
    validation_id: str
    model_name: str
    validation_method: str
    cv_scores: List[float]
    mean_score: float
    std_score: float
    best_score: float
    worst_score: float
    created_at: datetime

@dataclass
class BacktestResult:
    """Backtest sonucu"""
    backtest_id: str
    model_name: str
    start_date: datetime
    end_date: datetime
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    created_at: datetime

@dataclass
class WalkForwardResult:
    """Walk-forward analiz sonucu"""
    walkforward_id: str
    model_name: str
    n_splits: int
    train_sizes: List[int]
    test_sizes: List[int]
    fold_scores: List[float]
    mean_score: float
    std_score: float
    score_trend: List[float]
    created_at: datetime

class ModelValidationBacktesting:
    """Model Validation & Backtesting ana sınıfı"""
    
    def __init__(self):
        self.validation_results = {}
        self.backtest_results = {}
        self.walkforward_results = {}
        self.validation_configs = {}
        
        # Varsayılan validasyon konfigürasyonları
        self._add_default_validation_configs()
    
    def _add_default_validation_configs(self):
        """Varsayılan validasyon konfigürasyonları ekle"""
        default_configs = [
            {
                "config_id": "TIMESERIES_CV",
                "name": "Time Series Cross Validation",
                "description": "Zaman serisi verisi için cross validation",
                "method": "timeseries",
                "n_splits": 5,
                "test_size": 0.2
            },
            {
                "config_id": "STRATIFIED_CV",
                "name": "Stratified Cross Validation",
                "description": "Sınıf dengesi korunarak cross validation",
                "method": "stratified",
                "n_splits": 5,
                "shuffle": True
            },
            {
                "config_id": "WALKFORWARD_ANALYSIS",
                "name": "Walk Forward Analysis",
                "description": "Zaman serisi için walk-forward analizi",
                "method": "walkforward",
                "n_splits": 10,
                "test_size": 0.1
            }
        ]
        
        for config_data in default_configs:
            self.validation_configs[config_data["config_id"]] = config_data
    
    def cross_validate_model(self, model, X: pd.DataFrame, y: pd.Series, 
                           method: str = "timeseries", **kwargs) -> ValidationResult:
        """Model cross-validation uygula"""
        try:
            if method == "timeseries":
                cv = TimeSeriesSplit(n_splits=kwargs.get('n_splits', 5))
            elif method == "stratified":
                cv = StratifiedKFold(n_splits=kwargs.get('n_splits', 5), shuffle=kwargs.get('shuffle', True))
            else:
                cv = TimeSeriesSplit(n_splits=5)
            
            # Cross-validation skorları
            cv_scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
            
            # Sonuçları oluştur
            validation_result = ValidationResult(
                validation_id=f"VALIDATION_{method}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                model_name=model.__class__.__name__,
                validation_method=method,
                cv_scores=cv_scores.tolist(),
                mean_score=float(cv_scores.mean()),
                std_score=float(cv_scores.std()),
                best_score=float(cv_scores.max()),
                worst_score=float(cv_scores.min()),
                created_at=datetime.now()
            )
            
            self.validation_results[validation_result.validation_id] = validation_result
            logger.info(f"Cross-validation completed: {method}, mean score: {validation_result.mean_score:.3f}")
            
            return validation_result
        
        except Exception as e:
            logger.error(f"Error in cross-validation: {e}")
            return None
    
    def walk_forward_analysis(self, model, X: pd.DataFrame, y: pd.Series, 
                            n_splits: int = 10, test_size: float = 0.1) -> WalkForwardResult:
        """Walk-forward analizi uygula"""
        try:
            cv = TimeSeriesSplit(n_splits=n_splits, test_size=int(len(X) * test_size))
            
            fold_scores = []
            train_sizes = []
            test_sizes = []
            score_trend = []
            
            for fold, (train_idx, test_idx) in enumerate(cv.split(X)):
                X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                
                # Model eğitimi
                model.fit(X_train, y_train)
                
                # Tahmin ve skor
                y_pred = model.predict(X_test)
                score = accuracy_score(y_test, y_pred)
                
                fold_scores.append(score)
                train_sizes.append(len(X_train))
                test_sizes.append(len(X_test))
                score_trend.append(score)
                
                logger.info(f"Fold {fold + 1}: Train size={len(X_train)}, Test size={len(X_test)}, Score={score:.3f}")
            
            # Sonuçları oluştur
            walkforward_result = WalkForwardResult(
                walkforward_id=f"WALKFORWARD_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                model_name=model.__class__.__name__,
                n_splits=n_splits,
                train_sizes=train_sizes,
                test_sizes=test_sizes,
                fold_scores=fold_scores,
                mean_score=float(np.mean(fold_scores)),
                std_score=float(np.std(fold_scores)),
                score_trend=score_trend,
                created_at=datetime.now()
            )
            
            self.walkforward_results[walkforward_result.walkforward_id] = walkforward_result
            logger.info(f"Walk-forward analysis completed: mean score: {walkforward_result.mean_score:.3f}")
            
            return walkforward_result
        
        except Exception as e:
            logger.error(f"Error in walk-forward analysis: {e}")
            return None
    
    def backtest_strategy(self, model, X: pd.DataFrame, y: pd.Series, 
                         initial_capital: float = 10000, 
                         position_size: float = 0.1) -> BacktestResult:
        """Strateji backtesting uygula"""
        try:
            # Model eğitimi
            model.fit(X, y)
            
            # Tahminler
            y_pred = model.predict(X)
            y_pred_proba = getattr(model, 'predict_proba', lambda x: np.zeros((len(x), 2)))(X)
            
            # Trading sinyalleri (olasılık > 0.5 ise al)
            if y_pred_proba.shape[1] > 1:
                buy_signals = y_pred_proba[:, 1] > 0.5
            else:
                buy_signals = y_pred > 0.5
            
            # Portfolio simülasyonu
            portfolio_value = initial_capital
            portfolio_values = [initial_capital]
            trades = []
            
            for i in range(1, len(X)):
                if buy_signals[i] and not buy_signals[i-1]:  # Buy signal
                    trade_amount = portfolio_value * position_size
                    portfolio_value += trade_amount * (y[i] - 1)  # Basit P&L
                    trades.append({
                        'type': 'buy',
                        'index': i,
                        'amount': trade_amount,
                        'return': y[i] - 1
                    })
                elif not buy_signals[i] and buy_signals[i-1]:  # Sell signal
                    trade_amount = portfolio_value * position_size
                    portfolio_value += trade_amount * (1 - y[i-1])  # Basit P&L
                    trades.append({
                        'type': 'sell',
                        'index': i,
                        'amount': trade_amount,
                        'return': 1 - y[i-1]
                    })
                
                portfolio_values.append(portfolio_value)
            
            # Performans metrikleri
            total_return = (portfolio_value - initial_capital) / initial_capital
            winning_trades = sum(1 for trade in trades if trade['return'] > 0)
            losing_trades = len(trades) - winning_trades
            win_rate = winning_trades / len(trades) if trades else 0
            
            # Sharpe ratio (basit hesaplama)
            returns = np.diff(portfolio_values) / portfolio_values[:-1]
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            
            # Maximum drawdown
            peak = portfolio_values[0]
            max_drawdown = 0
            for value in portfolio_values:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)
            
            # Sonuçları oluştur
            backtest_result = BacktestResult(
                backtest_id=f"BACKTEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                model_name=model.__class__.__name__,
                start_date=datetime.now(),
                end_date=datetime.now(),
                total_trades=len(trades),
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                total_return=total_return,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                created_at=datetime.now()
            )
            
            self.backtest_results[backtest_result.backtest_id] = backtest_result
            logger.info(f"Backtesting completed: total return: {total_return:.2%}, win rate: {win_rate:.2%}")
            
            return backtest_result
        
        except Exception as e:
            logger.error(f"Error in backtesting: {e}")
            return None
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Validasyon özeti getir"""
        try:
            summary = {
                "total_validations": len(self.validation_results),
                "total_backtests": len(self.backtest_results),
                "total_walkforwards": len(self.walkforward_results),
                "validation_methods": {},
                "model_performance": {},
                "backtest_performance": {}
            }
            
            # Validasyon yöntemleri
            for validation in self.validation_results.values():
                method = validation.validation_method
                summary["validation_methods"][method] = summary["validation_methods"].get(method, 0) + 1
            
            # Model performansı
            for validation in self.validation_results.values():
                model_name = validation.model_name
                if model_name not in summary["model_performance"]:
                    summary["model_performance"][model_name] = []
                summary["model_performance"][model_name].append(validation.mean_score)
            
            # Backtest performansı
            if self.backtest_results:
                returns = [bt.total_return for bt in self.backtest_results.values()]
                win_rates = [bt.win_rate for bt in self.backtest_results.values()]
                
                summary["backtest_performance"] = {
                    "average_return": np.mean(returns),
                    "average_win_rate": np.mean(win_rates),
                    "best_return": max(returns),
                    "worst_return": min(returns)
                }
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting validation summary: {e}")
            return {}


def test_model_validation_backtesting():
    """Model Validation & Backtesting test fonksiyonu"""
    print("\n🧪 Model Validation & Backtesting Test Başlıyor...")
    
    # Model Validation & Backtesting oluştur
    validator = ModelValidationBacktesting()
    
    print("✅ Model Validation & Backtesting oluşturuldu")
    print(f"📊 Toplam validasyon konfigürasyonu: {len(validator.validation_configs)}")
    
    # Test verisi oluştur
    print("\n📊 Test Verisi Oluşturma:")
    np.random.seed(42)
    n_samples = 200
    
    # Simüle edilmiş fiyat verisi
    dates = pd.date_range(start='2023-01-01', periods=n_samples, freq='D')
    prices = 100 + np.cumsum(np.random.randn(n_samples) * 0.02)
    returns = np.diff(prices) / prices[:-1]
    
    # Binary target (yukarı/aşağı hareket)
    target = (returns > 0).astype(int)
    
    # Feature matrix - tam uzunluk eşleştirme
    feature_length = len(returns) - 1
    
    features = pd.DataFrame({
        'price': prices[1:feature_length+1],
        'return_lag1': np.roll(returns, 1)[1:feature_length+1],
        'return_lag2': np.roll(returns, 2)[1:feature_length+1],
        'volatility': np.random.rand(feature_length) * 0.1,
        'momentum': np.random.rand(feature_length) * 0.05
    }, index=dates[1:feature_length+1])
    
    # Target'ı features ile aynı boyuta getir
    target = target[:feature_length]
    
    print(f"   ✅ Test verisi oluşturuldu: {len(features)} örnek, {len(features.columns)} özellik")
    
    # Basit model oluştur (Random Forest benzeri)
    class SimpleModel:
        def __init__(self):
            self.is_fitted = False
            self.feature_importance = None
        
        def fit(self, X, y):
            self.is_fitted = True
            self.feature_importance = np.random.rand(len(X.columns))
            return self
        
        def predict(self, X):
            if not self.is_fitted:
                raise ValueError("Model not fitted")
            return np.random.choice([0, 1], size=len(X))
        
        def predict_proba(self, X):
            if not self.is_fitted:
                raise ValueError("Model not fitted")
            proba = np.random.rand(len(X), 2)
            proba = proba / proba.sum(axis=1, keepdims=True)
            return proba
    
    model = SimpleModel()
    print("   ✅ Test modeli oluşturuldu")
    
    # Cross-validation testi
    print("\n📊 Cross-Validation Testi:")
    
    # Time Series CV
    validation_ts = validator.cross_validate_model(model, features, target, "timeseries", n_splits=5)
    if validation_ts:
        print(f"   ✅ Time Series CV tamamlandı")
        print(f"      📊 Ortalama skor: {validation_ts.mean_score:.3f}")
        print(f"      📊 En iyi skor: {validation_ts.best_score:.3f}")
        print(f"      📊 En kötü skor: {validation_ts.worst_score:.3f}")
    
    # Stratified CV
    validation_strat = validator.cross_validate_model(model, features, target, "stratified", n_splits=5)
    if validation_strat:
        print(f"   ✅ Stratified CV tamamlandı")
        print(f"      📊 Ortalama skor: {validation_strat.mean_score:.3f}")
        print(f"      📊 Standart sapma: {validation_strat.std_score:.3f}")
    
    # Walk-forward analizi testi
    print("\n📊 Walk-Forward Analizi Testi:")
    
    walkforward = validator.walk_forward_analysis(model, features, target, n_splits=5, test_size=0.2)
    if walkforward:
        print(f"   ✅ Walk-forward analizi tamamlandı")
        print(f"      📊 Toplam fold: {walkforward.n_splits}")
        print(f"      📊 Ortalama skor: {walkforward.mean_score:.3f}")
        print(f"      📊 Skor trendi: {walkforward.score_trend}")
    
    # Backtesting testi
    print("\n📊 Backtesting Testi:")
    
    backtest = validator.backtest_strategy(model, features, target, initial_capital=10000, position_size=0.1)
    if backtest:
        print(f"   ✅ Backtesting tamamlandı")
        print(f"      📊 Toplam işlem: {backtest.total_trades}")
        print(f"      📊 Kazanan işlem: {backtest.winning_trades}")
        print(f"      📊 Kaybeden işlem: {backtest.losing_trades}")
        print(f"      📊 Kazanma oranı: {backtest.win_rate:.2%}")
        print(f"      📊 Toplam getiri: {backtest.total_return:.2%}")
        print(f"      📊 Sharpe oranı: {backtest.sharpe_ratio:.3f}")
        print(f"      📊 Maksimum drawdown: {backtest.max_drawdown:.2%}")
    
    # Validasyon özeti
    print("\n📊 Validasyon Özeti:")
    summary = validator.get_validation_summary()
    
    if summary:
        print(f"   ✅ Validasyon özeti alındı")
        print(f"   📊 Toplam validasyon: {summary['total_validations']}")
        print(f"   📊 Toplam backtest: {summary['total_backtests']}")
        print(f"   📊 Toplam walk-forward: {summary['total_walkforwards']}")
        print(f"   📊 Validasyon yöntemleri: {summary['validation_methods']}")
        
        if summary['backtest_performance']:
            perf = summary['backtest_performance']
            print(f"   📊 Ortalama getiri: {perf['average_return']:.2%}")
            print(f"   📊 Ortalama kazanma oranı: {perf['average_win_rate']:.2%}")
            print(f"   📊 En iyi getiri: {perf['best_return']:.2%}")
            print(f"   📊 En kötü getiri: {perf['worst_return']:.2%}")
    
    print("\n✅ Model Validation & Backtesting Test Tamamlandı!")


if __name__ == "__main__":
    test_model_validation_backtesting()
