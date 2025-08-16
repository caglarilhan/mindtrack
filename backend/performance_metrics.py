"""
PRD v2.0 - BIST AI Smart Trader
Performance Metrics Module

Performans metrikleri modülü:
- Return metrics
- Risk metrics
- Risk-adjusted returns
- Drawdown analysis
- Performance attribution
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
class ReturnMetrics:
    """Getiri metrikleri"""
    total_return: float
    annualized_return: float
    daily_return: float
    monthly_return: float
    quarterly_return: float
    yearly_return: float

@dataclass
class RiskMetrics:
    """Risk metrikleri"""
    volatility: float
    var_95: float
    cvar_95: float
    max_drawdown: float
    downside_deviation: float
    semi_deviation: float

@dataclass
class RiskAdjustedReturns:
    """Risk-ayarlı getiriler"""
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    information_ratio: float
    treynor_ratio: float
    jensen_alpha: float

@dataclass
class DrawdownInfo:
    """Drawdown bilgisi"""
    start_date: datetime
    end_date: datetime
    peak_value: float
    trough_value: float
    drawdown_pct: float
    duration: int
    recovery_date: Optional[datetime] = None

@dataclass
class PerformanceAttribution:
    """Performans atıflandırması"""
    asset_allocation: float
    stock_selection: float
    interaction: float
    total_excess_return: float

class PerformanceMetrics:
    """
    Performans Metrikleri Motoru
    
    PRD v2.0 gereksinimleri:
    - Getiri metrikleri hesaplama
    - Risk metrikleri analizi
    - Risk-ayarlı getiri oranları
    - Drawdown analizi
    - Performans atıflandırması
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Performance Metrics başlatıcı
        
        Args:
            risk_free_rate: Risksiz faiz oranı
        """
        self.risk_free_rate = risk_free_rate
        
        # Risk-ayarlı getiri oranları
        self.RISK_ADJUSTED_RATIOS = {
            "SHARPE": "Sharpe Ratio",
            "SORTINO": "Sortino Ratio",
            "CALMAR": "Calmar Ratio",
            "INFORMATION": "Information Ratio",
            "TREYNOR": "Treynor Ratio"
        }
        
        # Drawdown analizi parametreleri
        self.DRAWDOWN_THRESHOLD = 0.05  # %5 eşik
        self.MIN_DRAWDOWN_DURATION = 5   # Minimum 5 gün
        
        # Performans atıflandırma
        self.ATTRIBUTION_METHODS = ["BRINSON", "FACTOR", "HOLDINGS_BASED"]
    
    def calculate_return_metrics(self, prices: pd.Series,
                                benchmark_prices: Optional[pd.Series] = None) -> ReturnMetrics:
        """
        Getiri metrikleri hesaplama
        
        Args:
            prices: Fiyat serisi
            benchmark_prices: Benchmark fiyat serisi
            
        Returns:
            ReturnMetrics: Getiri metrikleri
        """
        if len(prices) < 2:
            return None
        
        # Getiri serisi
        returns = prices.pct_change().dropna()
        
        # Toplam getiri
        total_return = (prices.iloc[-1] / prices.iloc[0]) - 1
        
        # Yıllıklandırılmış getiri
        n_years = len(prices) / 252
        annualized_return = (1 + total_return) ** (1 / n_years) - 1
        
        # Günlük getiri
        daily_return = returns.mean()
        
        # Aylık getiri (21 günlük)
        monthly_returns = returns.rolling(window=21).apply(lambda x: (1 + x).prod() - 1)
        monthly_return = monthly_returns.mean()
        
        # Üç aylık getiri (63 günlük)
        quarterly_returns = returns.rolling(window=63).apply(lambda x: (1 + x).prod() - 1)
        quarterly_return = quarterly_returns.mean()
        
        # Yıllık getiri (252 günlük)
        yearly_returns = returns.rolling(window=252).apply(lambda x: (1 + x).prod() - 1)
        yearly_return = yearly_returns.mean()
        
        return ReturnMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            daily_return=daily_return,
            monthly_return=monthly_return,
            quarterly_return=quarterly_return,
            yearly_return=yearly_return
        )
    
    def calculate_risk_metrics(self, returns: pd.Series,
                              confidence_level: float = 0.95) -> RiskMetrics:
        """
        Risk metrikleri hesaplama
        
        Args:
            returns: Getiri serisi
            confidence_level: Güven seviyesi
            
        Returns:
            RiskMetrics: Risk metrikleri
        """
        if len(returns) < 30:
            return None
        
        # Volatilite
        volatility = returns.std() * np.sqrt(252)
        
        # Value at Risk
        var_95 = np.percentile(returns, (1 - confidence_level) * 100)
        
        # Conditional Value at Risk
        cvar_95 = returns[returns <= var_95].mean()
        
        # Maximum drawdown
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = abs(drawdown.min())
        
        # Downside deviation (sadece negatif getiriler)
        negative_returns = returns[returns < 0]
        downside_deviation = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else 0
        
        # Semi-deviation (ortalamanın altındaki getiriler)
        mean_return = returns.mean()
        below_mean_returns = returns[returns < mean_return]
        semi_deviation = below_mean_returns.std() * np.sqrt(252) if len(below_mean_returns) > 0 else 0
        
        return RiskMetrics(
            volatility=volatility,
            var_95=abs(var_95),
            cvar_95=abs(cvar_95),
            max_drawdown=max_drawdown,
            downside_deviation=downside_deviation,
            semi_deviation=semi_deviation
        )
    
    def calculate_risk_adjusted_returns(self, returns: pd.Series,
                                      benchmark_returns: Optional[pd.Series] = None,
                                      risk_free_rate: Optional[float] = None) -> RiskAdjustedReturns:
        """
        Risk-ayarlı getiri oranları hesaplama
        
        Args:
            returns: Getiri serisi
            benchmark_returns: Benchmark getiri serisi
            risk_free_rate: Risksiz faiz oranı
            
        Returns:
            RiskAdjustedReturns: Risk-ayarlı getiri oranları
        """
        if len(returns) < 30:
            return None
        
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        # Günlük risksiz faiz oranı
        daily_rf = (1 + risk_free_rate) ** (1 / 252) - 1
        
        # Excess returns
        excess_returns = returns - daily_rf
        
        # Sharpe Ratio
        sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        # Sortino Ratio (downside deviation kullanarak)
        negative_returns = returns[returns < 0]
        downside_deviation = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else returns.std() * np.sqrt(252)
        sortino_ratio = excess_returns.mean() / downside_deviation * np.sqrt(252) if downside_deviation > 0 else 0
        
        # Calmar Ratio (maximum drawdown kullanarak)
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = abs(drawdown.min())
        
        annualized_return = (1 + returns).prod() ** (252 / len(returns)) - 1
        calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0
        
        # Information Ratio (benchmark varsa)
        information_ratio = 0
        if benchmark_returns is not None and len(benchmark_returns) > 0:
            # Ortak tarih aralığını bul
            common_dates = returns.index.intersection(benchmark_returns.index)
            if len(common_dates) > 10:
                returns_common = returns.loc[common_dates]
                benchmark_common = benchmark_returns.loc[common_dates]
                
                active_returns = returns_common - benchmark_common
                tracking_error = active_returns.std() * np.sqrt(252)
                information_ratio = active_returns.mean() / tracking_error * np.sqrt(252) if tracking_error > 0 else 0
        
        # Treynor Ratio (beta kullanarak)
        treynor_ratio = 0
        if benchmark_returns is not None and len(benchmark_returns) > 0:
            common_dates = returns.index.intersection(benchmark_returns.index)
            if len(common_dates) > 10:
                returns_common = returns.loc[common_dates]
                benchmark_common = benchmark_returns.loc[common_dates]
                
                # Beta hesaplama
                covariance = np.cov(returns_common, benchmark_common)[0, 1]
                benchmark_variance = benchmark_common.var()
                beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
                
                treynor_ratio = excess_returns.mean() / beta * np.sqrt(252) if beta != 0 else 0
        
        # Jensen's Alpha
        jensen_alpha = 0
        if benchmark_returns is not None and len(benchmark_returns) > 0:
            common_dates = returns.index.intersection(benchmark_returns.index)
            if len(common_dates) > 10:
                returns_common = returns.loc[common_dates]
                benchmark_common = benchmark_returns.loc[common_dates]
                
                # Beta hesaplama
                covariance = np.cov(returns_common, benchmark_common)[0, 1]
                benchmark_variance = benchmark_common.var()
                beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
                
                # Alpha hesaplama
                jensen_alpha = returns_common.mean() - (daily_rf + beta * (benchmark_common.mean() - daily_rf))
                jensen_alpha = jensen_alpha * 252  # Yıllıklandırma
        
        return RiskAdjustedReturns(
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            information_ratio=information_ratio,
            treynor_ratio=treynor_ratio,
            jensen_alpha=jensen_alpha
        )
    
    def analyze_drawdowns(self, prices: pd.Series,
                          threshold: Optional[float] = None) -> List[DrawdownInfo]:
        """
        Drawdown analizi
        
        Args:
            prices: Fiyat serisi
            threshold: Drawdown eşiği
            
        Returns:
            List: Drawdown bilgileri
        """
        if threshold is None:
            threshold = self.DRAWDOWN_THRESHOLD
        
        if len(prices) < 10:
            return []
        
        # Kümülatif getiri
        cumulative_returns = (1 + prices.pct_change().dropna()).cumprod()
        
        # Running maximum
        running_max = cumulative_returns.expanding().max()
        
        # Drawdown hesaplama
        drawdown = (cumulative_returns - running_max) / running_max
        
        # Drawdown noktalarını bul
        drawdowns = []
        in_drawdown = False
        drawdown_start = None
        peak_value = None
        
        for i, (date, dd_value) in enumerate(drawdown.items()):
            if pd.isna(dd_value):
                continue
            
            # Drawdown başlangıcı
            if dd_value <= -threshold and not in_drawdown:
                in_drawdown = True
                drawdown_start = date
                peak_value = running_max.iloc[i]
            
            # Drawdown sonu
            elif dd_value > -threshold and in_drawdown:
                in_drawdown = False
                
                # Drawdown bilgisi
                trough_value = cumulative_returns.loc[drawdown_start:date].min()
                drawdown_pct = (trough_value - peak_value) / peak_value
                duration = len(cumulative_returns.loc[drawdown_start:date])
                
                if duration >= self.MIN_DRAWDOWN_DURATION:
                    drawdowns.append(DrawdownInfo(
                        start_date=drawdown_start,
                        end_date=date,
                        peak_value=peak_value,
                        trough_value=trough_value,
                        drawdown_pct=abs(drawdown_pct),
                        duration=duration
                    ))
        
        # Hala devam eden drawdown
        if in_drawdown:
            trough_value = cumulative_returns.loc[drawdown_start:].min()
            drawdown_pct = (trough_value - peak_value) / peak_value
            duration = len(cumulative_returns.loc[drawdown_start:])
            
            if duration >= self.MIN_DRAWDOWN_DURATION:
                drawdowns.append(DrawdownInfo(
                    start_date=drawdown_start,
                    end_date=prices.index[-1],
                    peak_value=peak_value,
                    trough_value=trough_value,
                    drawdown_pct=abs(drawdown_pct),
                    duration=duration
                ))
        
        # Drawdown'ları büyüklüğe göre sırala
        drawdowns.sort(key=lambda x: x.drawdown_pct, reverse=True)
        
        return drawdowns
    
    def calculate_performance_attribution(self, portfolio_returns: pd.Series,
                                        benchmark_returns: pd.Series,
                                        asset_weights: Dict[str, float],
                                        asset_returns: Dict[str, pd.Series],
                                        method: str = "BRINSON") -> PerformanceAttribution:
        """
        Performans atıflandırması
        
        Args:
            portfolio_returns: Portföy getiri serisi
            benchmark_returns: Benchmark getiri serisi
            asset_weights: Varlık ağırlıkları
            asset_returns: Varlık getiri serileri
            method: Atıflandırma metodu
            
        Returns:
            PerformanceAttribution: Performans atıflandırması
        """
        if method == "BRINSON":
            # Brinson-Fachler atıflandırması (basit versiyon)
            
            # Benchmark ağırlıkları (eşit ağırlık varsayımı)
            benchmark_weights = {asset: 1.0 / len(asset_weights) for asset in asset_weights.keys()}
            
            # Portföy ve benchmark getirileri
            portfolio_return = portfolio_returns.mean() * 252
            benchmark_return = benchmark_returns.mean() * 252
            
            # Asset allocation effect
            asset_allocation = 0
            for asset in asset_weights.keys():
                if asset in asset_returns and asset in benchmark_weights:
                    asset_return = asset_returns[asset].mean() * 252
                    weight_diff = asset_weights[asset] - benchmark_weights[asset]
                    asset_allocation += weight_diff * asset_return
            
            # Stock selection effect
            stock_selection = 0
            for asset in asset_weights.keys():
                if asset in asset_returns and asset in benchmark_weights:
                    asset_return = asset_returns[asset].mean() * 252
                    benchmark_asset_return = benchmark_return  # Basit varsayım
                    weight = benchmark_weights[asset]
                    stock_selection += weight * (asset_return - benchmark_asset_return)
            
            # Interaction effect
            interaction = portfolio_return - benchmark_return - asset_allocation - stock_selection
            
            # Total excess return
            total_excess_return = portfolio_return - benchmark_return
            
        else:
            # Basit atıflandırma
            asset_allocation = 0
            stock_selection = 0
            interaction = 0
            total_excess_return = 0
        
        return PerformanceAttribution(
            asset_allocation=asset_allocation,
            stock_selection=stock_selection,
            interaction=interaction,
            total_excess_return=total_excess_return
        )
    
    def generate_performance_report(self, prices: pd.Series,
                                  benchmark_prices: Optional[pd.Series] = None,
                                  asset_weights: Optional[Dict[str, float]] = None,
                                  asset_returns: Optional[Dict[str, pd.Series]] = None) -> Dict:
        """
        Kapsamlı performans raporu oluşturma
        
        Args:
            prices: Fiyat serisi
            benchmark_prices: Benchmark fiyat serisi
            asset_weights: Varlık ağırlıkları
            asset_returns: Varlık getiri serileri
            
        Returns:
            Dict: Kapsamlı performans raporu
        """
        print("📊 Performans Raporu Oluşturuluyor...")
        
        # Getiri metrikleri
        return_metrics = self.calculate_return_metrics(prices, benchmark_prices)
        
        # Risk metrikleri
        returns = prices.pct_change().dropna()
        risk_metrics = self.calculate_risk_metrics(returns)
        
        # Risk-ayarlı getiriler
        benchmark_returns = None
        if benchmark_prices is not None:
            benchmark_returns = benchmark_prices.pct_change().dropna()
        
        risk_adjusted_returns = self.calculate_risk_adjusted_returns(returns, benchmark_returns)
        
        # Drawdown analizi
        drawdowns = self.analyze_drawdowns(prices)
        
        # Performans atıflandırması
        performance_attribution = None
        if asset_weights is not None and asset_returns is not None and benchmark_returns is not None:
            performance_attribution = self.calculate_performance_attribution(
                returns, benchmark_returns, asset_weights, asset_returns
            )
        
        # Rapor oluştur
        report = {
            "return_metrics": {
                "total_return": return_metrics.total_return if return_metrics else 0,
                "annualized_return": return_metrics.annualized_return if return_metrics else 0,
                "daily_return": return_metrics.daily_return if return_metrics else 0,
                "monthly_return": return_metrics.monthly_return if return_metrics else 0,
                "quarterly_return": return_metrics.quarterly_return if return_metrics else 0,
                "yearly_return": return_metrics.yearly_return if return_metrics else 0
            },
            "risk_metrics": {
                "volatility": risk_metrics.volatility if risk_metrics else 0,
                "var_95": risk_metrics.var_95 if risk_metrics else 0,
                "cvar_95": risk_metrics.cvar_95 if risk_metrics else 0,
                "max_drawdown": risk_metrics.max_drawdown if risk_metrics else 0,
                "downside_deviation": risk_metrics.downside_deviation if risk_metrics else 0,
                "semi_deviation": risk_metrics.semi_deviation if risk_metrics else 0
            },
            "risk_adjusted_returns": {
                "sharpe_ratio": risk_adjusted_returns.sharpe_ratio if risk_adjusted_returns else 0,
                "sortino_ratio": risk_adjusted_returns.sortino_ratio if risk_adjusted_returns else 0,
                "calmar_ratio": risk_adjusted_returns.calmar_ratio if risk_adjusted_returns else 0,
                "information_ratio": risk_adjusted_returns.information_ratio if risk_adjusted_returns else 0,
                "treynor_ratio": risk_adjusted_returns.treynor_ratio if risk_adjusted_returns else 0,
                "jensen_alpha": risk_adjusted_returns.jensen_alpha if risk_adjusted_returns else 0
            },
            "drawdown_analysis": {
                "total_drawdowns": len(drawdowns),
                "max_drawdown": max([d.drawdown_pct for d in drawdowns]) if drawdowns else 0,
                "avg_drawdown_duration": np.mean([d.duration for d in drawdowns]) if drawdowns else 0,
                "drawdown_details": [
                    {
                        "start_date": d.start_date,
                        "end_date": d.end_date,
                        "drawdown_pct": d.drawdown_pct,
                        "duration": d.duration
                    }
                    for d in drawdowns[:5]  # İlk 5 drawdown
                ]
            },
            "performance_attribution": {
                "asset_allocation": performance_attribution.asset_allocation if performance_attribution else 0,
                "stock_selection": performance_attribution.stock_selection if performance_attribution else 0,
                "interaction": performance_attribution.interaction if performance_attribution else 0,
                "total_excess_return": performance_attribution.total_excess_return if performance_attribution else 0
            },
            "summary": {
                "total_return": return_metrics.total_return if return_metrics else 0,
                "annualized_return": return_metrics.annualized_return if return_metrics else 0,
                "volatility": risk_metrics.volatility if risk_metrics else 0,
                "sharpe_ratio": risk_adjusted_returns.sharpe_ratio if risk_adjusted_returns else 0,
                "max_drawdown": risk_metrics.max_drawdown if risk_metrics else 0,
                "risk_adjusted_performance": "GOOD" if (risk_adjusted_returns.sharpe_ratio > 1.0 if risk_adjusted_returns else False) else "POOR"
            }
        }
        
        print("✅ Performans Raporu Tamamlandı!")
        return report

# Test fonksiyonu
def test_performance_metrics():
    """Performance Metrics test fonksiyonu"""
    print("🧪 Performance Metrics Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    n_days = 252  # 1 yıl
    
    # Tarih aralığı
    dates = pd.date_range('2023-01-01', periods=n_days, freq='D')
    
    # Portföy fiyat verisi
    base_price = 100.0
    trend = 0.0008  # Günlük trend
    volatility = 0.025  # Günlük volatilite
    
    prices = []
    for i in range(n_days):
        # Trend + noise
        price = base_price * (1 + trend * i + np.random.normal(0, volatility))
        prices.append(price)
        base_price = price
    
    price_series = pd.Series(prices, index=dates)
    
    # Benchmark fiyat verisi
    benchmark_base = 100.0
    benchmark_trend = 0.0006
    benchmark_vol = 0.020
    
    benchmark_prices = []
    for i in range(n_days):
        price = benchmark_base * (1 + benchmark_trend * i + np.random.normal(0, benchmark_vol))
        benchmark_prices.append(price)
        benchmark_base = price
    
    benchmark_price_series = pd.Series(benchmark_prices, index=dates)
    
    # Varlık getiri verileri (basit)
    asset_returns = {
        "Asset_1": pd.Series(np.random.normal(0.001, 0.03, n_days), index=dates),
        "Asset_2": pd.Series(np.random.normal(0.0008, 0.025, n_days), index=dates),
        "Asset_3": pd.Series(np.random.normal(0.0012, 0.035, n_days), index=dates)
    }
    
    asset_weights = {"Asset_1": 0.4, "Asset_2": 0.35, "Asset_3": 0.25}
    
    # Performance Metrics başlat
    perf_analyzer = PerformanceMetrics(risk_free_rate=0.03)
    
    # Getiri metrikleri test
    print("\n📈 Getiri Metrikleri Test:")
    return_metrics = perf_analyzer.calculate_return_metrics(price_series, benchmark_price_series)
    if return_metrics:
        print(f"   Toplam getiri: {return_metrics.total_return:.4f}")
        print(f"   Yıllıklandırılmış getiri: {return_metrics.annualized_return:.4f}")
        print(f"   Günlük getiri: {return_metrics.daily_return:.6f}")
        print(f"   Aylık getiri: {return_metrics.monthly_return:.4f}")
    
    # Risk metrikleri test
    print("\n⚠️ Risk Metrikleri Test:")
    returns = price_series.pct_change().dropna()
    risk_metrics = perf_analyzer.calculate_risk_metrics(returns)
    if risk_metrics:
        print(f"   Volatilite: {risk_metrics.volatility:.4f}")
        print(f"   VaR %95: {risk_metrics.var_95:.4f}")
        print(f"   CVaR %95: {risk_metrics.cvar_95:.4f}")
        print(f"   Maximum drawdown: {risk_metrics.max_drawdown:.4f}")
    
    # Risk-ayarlı getiriler test
    print("\n💪 Risk-Ayarlı Getiriler Test:")
    benchmark_returns = benchmark_price_series.pct_change().dropna()
    risk_adjusted_returns = perf_analyzer.calculate_risk_adjusted_returns(returns, benchmark_returns)
    if risk_adjusted_returns:
        print(f"   Sharpe Ratio: {risk_adjusted_returns.sharpe_ratio:.4f}")
        print(f"   Sortino Ratio: {risk_adjusted_returns.sortino_ratio:.4f}")
        print(f"   Calmar Ratio: {risk_adjusted_returns.calmar_ratio:.4f}")
        print(f"   Information Ratio: {risk_adjusted_returns.information_ratio:.4f}")
        print(f"   Jensen's Alpha: {risk_adjusted_returns.jensen_alpha:.6f}")
    
    # Drawdown analizi test
    print("\n📉 Drawdown Analizi Test:")
    drawdowns = perf_analyzer.analyze_drawdowns(price_series)
    print(f"   Toplam drawdown: {len(drawdowns)}")
    
    if drawdowns:
        max_dd = max([d.drawdown_pct for d in drawdowns])
        avg_duration = np.mean([d.duration for d in drawdowns])
        print(f"   Maximum drawdown: {max_dd:.4f}")
        print(f"   Ortalama drawdown süresi: {avg_duration:.1f} gün")
    
    # Performans atıflandırması test
    print("\n🔍 Performans Atıflandırması Test:")
    performance_attribution = perf_analyzer.calculate_performance_attribution(
        returns, benchmark_returns, asset_weights, asset_returns
    )
    if performance_attribution:
        print(f"   Varlık tahsisi: {performance_attribution.asset_allocation:.6f}")
        print(f"   Hisse seçimi: {performance_attribution.stock_selection:.6f}")
        print(f"   Etkileşim: {performance_attribution.interaction:.6f}")
        print(f"   Toplam fazla getiri: {performance_attribution.total_excess_return:.6f}")
    
    # Kapsamlı rapor test
    print("\n📋 Kapsamlı Performans Raporu Test:")
    performance_report = perf_analyzer.generate_performance_report(
        price_series, benchmark_price_series, asset_weights, asset_returns
    )
    print(f"   Toplam getiri: {performance_report['summary']['total_return']:.4f}")
    print(f"   Yıllık getiri: {performance_report['summary']['annualized_return']:.4f}")
    print(f"   Volatilite: {performance_report['summary']['volatility']:.4f}")
    print(f"   Sharpe Ratio: {performance_report['summary']['sharpe_ratio']:.4f}")
    print(f"   Risk-ayarlı performans: {performance_report['summary']['risk_adjusted_performance']}")
    
    print("\n✅ Performance Metrics Test Tamamlandı!")
    return perf_analyzer

if __name__ == "__main__":
    test_performance_metrics()

