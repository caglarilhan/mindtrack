"""
PRD v2.0 - BIST AI Smart Trader
Volatility Analysis Module

Volatilite analizi modülü:
- Historical volatility
- Implied volatility
- Volatility regimes
- Volatility forecasting
- Volatility clustering
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from scipy import stats
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class VolatilityMetrics:
    """Volatilite metrikleri"""
    historical_vol: float
    rolling_vol: pd.Series
    implied_vol: Optional[float] = None
    volatility_of_vol: float = 0.0
    skewness: float = 0.0
    kurtosis: float = 0.0

@dataclass
class VolatilityRegime:
    """Volatilite rejimi"""
    regime_type: str  # "LOW", "MEDIUM", "HIGH", "EXTREME"
    start_date: datetime
    end_date: datetime
    avg_volatility: float
    duration: int
    characteristics: Dict

@dataclass
class VolatilityForecast:
    """Volatilite tahmini"""
    forecast_date: datetime
    forecast_value: float
    confidence_interval: Tuple[float, float]
    model_type: str
    accuracy_score: float

class VolatilityAnalysis:
    """
    Volatilite Analiz Motoru
    
    PRD v2.0 gereksinimleri:
    - Tarihsel volatilite hesaplama
    - Beklenen volatilite analizi
    - Volatilite rejimi tespiti
    - Volatilite tahmini
    - Volatilite kümelenmesi analizi
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Volatility Analysis başlatıcı
        
        Args:
            risk_free_rate: Risksiz faiz oranı
        """
        self.risk_free_rate = risk_free_rate
        
        # Volatilite rejimleri
        self.VOLATILITY_REGIMES = {
            "LOW": {"name": "Düşük Volatilite", "threshold": 0.15},
            "MEDIUM": {"name": "Orta Volatilite", "threshold": 0.25},
            "HIGH": {"name": "Yüksek Volatilite", "threshold": 0.40},
            "EXTREME": {"name": "Aşırı Volatilite", "threshold": float('inf')}
        }
        
        # Volatilite hesaplama periyotları
        self.VOL_PERIODS = [5, 10, 21, 63, 126, 252]
        
        # Volatilite tahmin modelleri
        self.FORECAST_MODELS = ["GARCH", "EWMA", "HISTORICAL", "REGRESSION"]
    
    def calculate_historical_volatility(self, returns: pd.Series,
                                      window: int = 21,
                                      annualize: bool = True) -> VolatilityMetrics:
        """
        Tarihsel volatilite hesaplama
        
        Args:
            returns: Getiri serisi
            window: Rolling window boyutu
            annualize: Yıllıklandırma
            
        Returns:
            VolatilityMetrics: Volatilite metrikleri
        """
        if len(returns) < window:
            return None
        
        # Rolling volatilite
        rolling_vol = returns.rolling(window=window).std()
        
        # Yıllıklandırma
        if annualize:
            rolling_vol = rolling_vol * np.sqrt(252)
        
        # Güncel volatilite
        current_vol = rolling_vol.iloc[-1]
        
        # Volatilite istatistikleri
        vol_skewness = rolling_vol.skew()
        vol_kurtosis = rolling_vol.kurtosis()
        vol_of_vol = rolling_vol.std()
        
        return VolatilityMetrics(
            historical_vol=current_vol,
            rolling_vol=rolling_vol,
            volatility_of_vol=vol_of_vol,
            skewness=vol_skewness,
            kurtosis=vol_kurtosis
        )
    
    def calculate_implied_volatility(self, option_data: pd.DataFrame,
                                   method: str = "black_scholes") -> float:
        """
        Beklenen volatilite hesaplama (basit yaklaşım)
        
        Args:
            option_data: Opsiyon verisi
            method: Hesaplama metodu
            
        Returns:
            float: Beklenen volatilite
        """
        if method == "black_scholes":
            # Basit Black-Scholes yaklaşımı
            # Gerçek uygulamada daha karmaşık hesaplama gerekir
            
            # Opsiyon fiyatından volatilite çıkarma (Newton-Raphson)
            # Bu basit bir örnek
            implied_vol = 0.25  # Varsayılan değer
            
            return implied_vol
        
        elif method == "historical_implied":
            # Tarihsel opsiyon verilerinden
            if 'implied_vol' in option_data.columns:
                return option_data['implied_vol'].mean()
            else:
                return 0.25
        
        else:
            raise ValueError(f"Desteklenmeyen metod: {method}")
    
    def detect_volatility_regimes(self, returns: pd.Series,
                                 window: int = 21,
                                 regime_threshold: float = 0.02) -> List[VolatilityRegime]:
        """
        Volatilite rejimi tespiti
        
        Args:
            returns: Getiri serisi
            window: Volatilite hesaplama penceresi
            regime_threshold: Rejim değişim eşiği
            
        Returns:
            List: Volatilite rejimleri
        """
        # Rolling volatilite hesapla
        rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)
        
        # Rejim değişim noktalarını bul
        regime_changes = []
        current_regime = "MEDIUM"
        regime_start = rolling_vol.index[0]
        
        for i, (date, vol) in enumerate(rolling_vol.items()):
            if pd.isna(vol):
                continue
            
            # Rejim tipini belirle
            if vol < self.VOLATILITY_REGIMES["LOW"]["threshold"]:
                new_regime = "LOW"
            elif vol < self.VOLATILITY_REGIMES["MEDIUM"]["threshold"]:
                new_regime = "MEDIUM"
            elif vol < self.VOLATILITY_REGIMES["HIGH"]["threshold"]:
                new_regime = "HIGH"
            else:
                new_regime = "EXTREME"
            
            # Rejim değişimi
            if new_regime != current_regime:
                # Önceki rejimi kaydet
                regime_end = rolling_vol.index[i-1] if i > 0 else rolling_vol.index[0]
                regime_vol = rolling_vol.loc[regime_start:regime_end].mean()
                regime_duration = len(rolling_vol.loc[regime_start:regime_end])
                
                regime_changes.append(VolatilityRegime(
                    regime_type=current_regime,
                    start_date=regime_start,
                    end_date=regime_end,
                    avg_volatility=regime_vol,
                    duration=regime_duration,
                    characteristics={
                        "min_vol": rolling_vol.loc[regime_start:regime_end].min(),
                        "max_vol": rolling_vol.loc[regime_start:regime_end].max(),
                        "vol_std": rolling_vol.loc[regime_start:regime_end].std()
                    }
                ))
                
                # Yeni rejim başlat
                current_regime = new_regime
                regime_start = date
        
        # Son rejimi ekle
        if len(regime_changes) > 0:
            last_regime_start = regime_changes[-1].end_date
        else:
            last_regime_start = regime_start
        
        regime_vol = rolling_vol.loc[last_regime_start:].mean()
        regime_duration = len(rolling_vol.loc[last_regime_start:])
        
        regime_changes.append(VolatilityRegime(
            regime_type=current_regime,
            start_date=last_regime_start,
            end_date=rolling_vol.index[-1],
            avg_volatility=regime_vol,
            duration=regime_duration,
            characteristics={
                "min_vol": rolling_vol.loc[last_regime_start:].min(),
                "max_vol": rolling_vol.loc[last_regime_start:].max(),
                "vol_std": rolling_vol.loc[last_regime_start:].std()
            }
        ))
        
        return regime_changes
    
    def forecast_volatility(self, returns: pd.Series,
                           forecast_days: int = 5,
                           model: str = "EWMA") -> VolatilityForecast:
        """
        Volatilite tahmini
        
        Args:
            returns: Getiri serisi
            forecast_days: Tahmin günü
            model: Tahmin modeli
            
        Returns:
            VolatilityForecast: Volatilite tahmini
        """
        if len(returns) < 50:
            return None
        
        if model == "EWMA":
            # Exponential Weighted Moving Average
            lambda_param = 0.94  # RiskMetrics standardı
            
            # EWMA volatilite
            ewma_vol = returns.ewm(alpha=1-lambda_param).std().iloc[-1]
            
            # Tahmin
            forecast_value = ewma_vol * np.sqrt(252)
            
            # Güven aralığı (basit)
            confidence_lower = forecast_value * 0.8
            confidence_upper = forecast_value * 1.2
            
        elif model == "HISTORICAL":
            # Basit tarihsel ortalama
            historical_vol = returns.std() * np.sqrt(252)
            forecast_value = historical_vol
            
            # Güven aralığı
            confidence_lower = historical_vol * 0.7
            confidence_upper = historical_vol * 1.3
            
        elif model == "REGRESSION":
            # Linear regression ile trend
            x = np.arange(len(returns))
            y = returns.values
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Trend bazlı tahmin
            forecast_value = returns.std() * np.sqrt(252) * (1 + slope * forecast_days)
            
            # Güven aralığı
            confidence_lower = forecast_value * 0.8
            confidence_upper = forecast_value * 1.2
            
        else:
            raise ValueError(f"Desteklenmeyen model: {model}")
        
        # Tahmin tarihi
        forecast_date = returns.index[-1] + timedelta(days=forecast_days)
        
        # Basit doğruluk skoru
        accuracy_score = 0.7  # Varsayılan
        
        return VolatilityForecast(
            forecast_date=forecast_date,
            forecast_value=forecast_value,
            confidence_interval=(confidence_lower, confidence_upper),
            model_type=model,
            accuracy_score=accuracy_score
        )
    
    def analyze_volatility_clustering(self, returns: pd.Series,
                                    window: int = 21) -> Dict:
        """
        Volatilite kümelenmesi analizi
        
        Args:
            returns: Getiri serisi
            window: Analiz penceresi
            
        Returns:
            Dict: Volatilite kümelenme analizi
        """
        # Rolling volatilite
        rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)
        
        # Volatilite kümelenmesi testi (Ljung-Box)
        vol_series = rolling_vol.dropna()
        
        if len(vol_series) < 20:
            return {"error": "Yeterli veri yok"}
        
        # Autocorrelation
        autocorr = []
        max_lag = min(20, len(vol_series) // 4)
        
        for lag in range(1, max_lag + 1):
            if lag < len(vol_series):
                corr = vol_series.autocorr(lag=lag)
                autocorr.append(corr)
        
        # Ljung-Box testi (basit versiyon)
        q_stat = len(vol_series) * (len(vol_series) + 2) * sum([r**2 / (len(vol_series) - i - 1) 
                                                                for i, r in enumerate(autocorr)])
        
        # Volatilite persistence
        vol_persistence = vol_series.autocorr(lag=1) if len(vol_series) > 1 else 0
        
        # Volatilite mean reversion
        vol_mean_reversion = -vol_series.autocorr(lag=1) if len(vol_series) > 1 else 0
        
        return {
            "autocorrelation": autocorr,
            "ljung_box_statistic": q_stat,
            "volatility_persistence": vol_persistence,
            "volatility_mean_reversion": vol_mean_reversion,
            "clustering_strength": abs(vol_persistence),
            "mean_reversion_strength": abs(vol_mean_reversion)
        }
    
    def calculate_volatility_ratios(self, returns: pd.Series,
                                   benchmark_returns: Optional[pd.Series] = None) -> Dict:
        """
        Volatilite oranları hesaplama
        
        Args:
            returns: Getiri serisi
            benchmark_returns: Benchmark getiri serisi
            
        Returns:
            Dict: Volatilite oranları
        """
        # Temel volatilite metrikleri
        current_vol = returns.std() * np.sqrt(252)
        avg_vol = returns.rolling(window=21).std().mean() * np.sqrt(252)
        
        # Volatilite oranları
        vol_ratios = {
            "current_volatility": current_vol,
            "average_volatility": avg_vol,
            "volatility_ratio": current_vol / avg_vol if avg_vol > 0 else 1.0,
            "volatility_percentile": 0.0
        }
        
        # Volatilite yüzdelik dilimi
        rolling_vols = returns.rolling(window=21).std() * np.sqrt(252)
        if len(rolling_vols.dropna()) > 0:
            vol_ratios["volatility_percentile"] = stats.percentileofscore(
                rolling_vols.dropna(), current_vol
            ) / 100
        
        # Benchmark karşılaştırması
        if benchmark_returns is not None:
            benchmark_vol = benchmark_returns.std() * np.sqrt(252)
            vol_ratios.update({
                "benchmark_volatility": benchmark_vol,
                "relative_volatility": current_vol / benchmark_vol if benchmark_vol > 0 else 1.0,
                "volatility_spread": current_vol - benchmark_vol
            })
        
        return vol_ratios
    
    def generate_volatility_report(self, returns: pd.Series,
                                  benchmark_returns: Optional[pd.Series] = None) -> Dict:
        """
        Kapsamlı volatilite raporu oluşturma
        
        Args:
            returns: Getiri serisi
            benchmark_returns: Benchmark getiri serisi
            
        Returns:
            Dict: Kapsamlı volatilite raporu
        """
        print("📊 Volatilite Raporu Oluşturuluyor...")
        
        # Tarihsel volatilite
        vol_metrics = self.calculate_historical_volatility(returns, window=21)
        
        # Volatilite rejimleri
        volatility_regimes = self.detect_volatility_regimes(returns)
        
        # Volatilite tahmini
        volatility_forecast = self.forecast_volatility(returns, model="EWMA")
        
        # Volatilite kümelenmesi
        clustering_analysis = self.analyze_volatility_clustering(returns)
        
        # Volatilite oranları
        volatility_ratios = self.calculate_volatility_ratios(returns, benchmark_returns)
        
        # Rapor oluştur
        report = {
            "volatility_metrics": {
                "current_volatility": vol_metrics.historical_vol,
                "rolling_volatility": vol_metrics.rolling_vol.to_dict(),
                "volatility_of_volatility": vol_metrics.volatility_of_vol,
                "volatility_skewness": vol_metrics.skewness,
                "volatility_kurtosis": vol_metrics.kurtosis
            },
            "volatility_regimes": {
                "total_regimes": len(volatility_regimes),
                "current_regime": volatility_regimes[-1].regime_type if volatility_regimes else "UNKNOWN",
                "regime_details": [
                    {
                        "type": regime.regime_type,
                        "start_date": regime.start_date,
                        "end_date": regime.end_date,
                        "avg_volatility": regime.avg_volatility,
                        "duration": regime.duration
                    }
                    for regime in volatility_regimes
                ]
            },
            "volatility_forecast": {
                "forecast_date": volatility_forecast.forecast_date if volatility_forecast else None,
                "forecast_value": volatility_forecast.forecast_value if volatility_forecast else None,
                "confidence_interval": volatility_forecast.confidence_interval if volatility_forecast else None,
                "model_type": volatility_forecast.model_type if volatility_forecast else None
            },
            "clustering_analysis": clustering_analysis,
            "volatility_ratios": volatility_ratios,
            "summary": {
                "current_volatility_level": volatility_ratios["volatility_ratio"],
                "volatility_percentile": volatility_ratios["volatility_percentile"],
                "regime_stability": len(volatility_regimes),
                "clustering_present": clustering_analysis.get("clustering_strength", 0) > 0.1
            }
        }
        
        print("✅ Volatilite Raporu Tamamlandı!")
        return report

# Test fonksiyonu
def test_volatility_analysis():
    """Volatility Analysis test fonksiyonu"""
    print("🧪 Volatility Analysis Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    n_days = 252  # 1 yıl
    
    # Tarih aralığı
    dates = pd.date_range('2023-01-01', periods=n_days, freq='D')
    
    # Volatilite kümelenmesi olan getiri verisi
    returns_data = []
    volatility_regime = 0.02  # Başlangıç volatilitesi
    
    for i in range(n_days):
        # Volatilite rejimi değişimi
        if i % 63 == 0:  # Her 3 ayda bir
            volatility_regime = np.random.choice([0.015, 0.025, 0.035, 0.045])
        
        # Volatilite kümelenmesi
        volatility_regime = volatility_regime * 0.99 + np.random.normal(0, 0.001)
        volatility_regime = max(0.01, volatility_regime)  # Minimum volatilite
        
        # Getiri üret
        return_value = np.random.normal(0.001, volatility_regime)
        returns_data.append(return_value)
    
    returns_series = pd.Series(returns_data, index=dates)
    
    # Benchmark (piyasa ortalaması)
    benchmark_returns = pd.Series(
        np.random.normal(0.0008, 0.018, n_days),
        index=dates
    )
    
    # Volatility Analysis başlat
    vol_analyzer = VolatilityAnalysis(risk_free_rate=0.03)
    
    # Tarihsel volatilite test
    print("\n📊 Tarihsel Volatilite Test:")
    vol_metrics = vol_analyzer.calculate_historical_volatility(returns_series, window=21)
    if vol_metrics:
        print(f"   Güncel volatilite: {vol_metrics.historical_vol:.4f}")
        print(f"   Volatilite volatilitesi: {vol_metrics.volatility_of_vol:.4f}")
        print(f"   Volatilite skewness: {vol_metrics.skewness:.4f}")
        print(f"   Volatilite kurtosis: {vol_metrics.kurtosis:.4f}")
    
    # Volatilite rejimleri test
    print("\n🔄 Volatilite Rejimleri Test:")
    volatility_regimes = vol_analyzer.detect_volatility_regimes(returns_series)
    print(f"   Toplam rejim: {len(volatility_regimes)}")
    
    if volatility_regimes:
        current_regime = volatility_regimes[-1]
        print(f"   Mevcut rejim: {current_regime.regime_type}")
        print(f"   Rejim volatilitesi: {current_regime.avg_volatility:.4f}")
        print(f"   Rejim süresi: {current_regime.duration} gün")
    
    # Volatilite tahmini test
    print("\n🔮 Volatilite Tahmini Test:")
    volatility_forecast = vol_analyzer.forecast_volatility(returns_series, model="EWMA")
    if volatility_forecast:
        print(f"   Tahmin modeli: {volatility_forecast.model_type}")
        print(f"   Tahmin değeri: {volatility_forecast.forecast_value:.4f}")
        print(f"   Güven aralığı: [{volatility_forecast.confidence_interval[0]:.4f}, {volatility_forecast.confidence_interval[1]:.4f}]")
    
    # Volatilite kümelenmesi test
    print("\n📈 Volatilite Kümelenmesi Test:")
    clustering_analysis = vol_analyzer.analyze_volatility_clustering(returns_series)
    if "error" not in clustering_analysis:
        print(f"   Kümelenme gücü: {clustering_analysis['clustering_strength']:.4f}")
        print(f"   Mean reversion gücü: {clustering_analysis['mean_reversion_strength']:.4f}")
        print(f"   Ljung-Box istatistiği: {clustering_analysis['ljung_box_statistic']:.2f}")
    
    # Volatilite oranları test
    print("\n📊 Volatilite Oranları Test:")
    volatility_ratios = vol_analyzer.calculate_volatility_ratios(returns_series, benchmark_returns)
    print(f"   Güncel volatilite: {volatility_ratios['current_volatility']:.4f}")
    print(f"   Ortalama volatilite: {volatility_ratios['average_volatility']:.4f}")
    print(f"   Volatilite oranı: {volatility_ratios['volatility_ratio']:.4f}")
    print(f"   Volatilite yüzdelik: {volatility_ratios['volatility_percentile']:.2f}")
    
    if 'benchmark_volatility' in volatility_ratios:
        print(f"   Benchmark volatilitesi: {volatility_ratios['benchmark_volatility']:.4f}")
        print(f"   Göreceli volatilite: {volatility_ratios['relative_volatility']:.4f}")
    
    # Kapsamlı rapor test
    print("\n📋 Kapsamlı Volatilite Raporu Test:")
    volatility_report = vol_analyzer.generate_volatility_report(returns_series, benchmark_returns)
    print(f"   Mevcut volatilite seviyesi: {volatility_report['summary']['current_volatility_level']:.4f}")
    print(f"   Volatilite yüzdelik: {volatility_report['summary']['volatility_percentile']:.2f}")
    print(f"   Rejim kararlılığı: {volatility_report['summary']['regime_stability']}")
    print(f"   Kümelenme mevcut: {volatility_report['summary']['clustering_present']}")
    
    print("\n✅ Volatility Analysis Test Tamamlandı!")
    return vol_analyzer

if __name__ == "__main__":
    test_volatility_analysis()

