"""
PRD v2.0 - BIST AI Smart Trader
VaR Calculator Module

Value at Risk (VaR) hesaplama modülü:
- Historical VaR
- Parametric VaR  
- Monte Carlo VaR
- Portfolio VaR
- Confidence level desteği
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

@dataclass
class VaRResult:
    """VaR hesaplama sonucu"""
    var_value: float
    confidence_level: float
    time_horizon: int
    method: str
    additional_info: Dict = None

class VaRCalculator:
    """
    Value at Risk (VaR) Hesaplayıcı
    
    PRD v2.0 gereksinimleri:
    - Çoklu VaR metodu (Historical, Parametric, Monte Carlo)
    - Portföy seviyesinde hesaplama
    - Farklı confidence level'lar
    - Risk metrikleri (VaR, CVaR, Expected Shortfall)
    """
    
    def __init__(self, confidence_level: float = 0.95, time_horizon: int = 1):
        """
        VaR Calculator başlatıcı
        
        Args:
            confidence_level: Güven seviyesi (0.95 = %95)
            time_horizon: Zaman ufku (gün)
        """
        self.confidence_level = confidence_level
        self.time_horizon = time_horizon
        self.alpha = 1 - confidence_level
        
        # Risk metrikleri için sabitler
        self.CONFIDENCE_LEVELS = [0.90, 0.95, 0.99, 0.999]
        self.TIME_HORIZONS = [1, 5, 10, 21]  # 1g, 1h, 2h, 1ay
        
    def calculate_historical_var(self, returns: pd.Series, 
                                confidence_level: Optional[float] = None) -> VaRResult:
        """
        Historical VaR hesaplama
        
        Args:
            returns: Getiri serisi
            confidence_level: Güven seviyesi
            
        Returns:
            VaRResult: VaR hesaplama sonucu
        """
        if confidence_level is None:
            confidence_level = self.confidence_level
            
        alpha = 1 - confidence_level
        var_value = np.percentile(returns, alpha * 100)
        
        return VaRResult(
            var_value=abs(var_value),
            confidence_level=confidence_level,
            time_horizon=self.time_horizon,
            method="Historical VaR",
            additional_info={
                "returns_mean": returns.mean(),
                "returns_std": returns.std(),
                "returns_skew": returns.skew(),
                "returns_kurtosis": returns.kurtosis(),
                "min_return": returns.min(),
                "max_return": returns.max(),
                "data_points": len(returns)
            }
        )
    
    def calculate_parametric_var(self, returns: pd.Series,
                                confidence_level: Optional[float] = None,
                                distribution: str = "normal") -> VaRResult:
        """
        Parametric VaR hesaplama
        
        Args:
            returns: Getiri serisi
            confidence_level: Güven seviyesi
            distribution: Dağılım tipi (normal, t, skew-t)
            
        Returns:
            VaRResult: VaR hesaplama sonucu
        """
        if confidence_level is None:
            confidence_level = self.confidence_level
            
        alpha = 1 - confidence_level
        mean_return = returns.mean()
        std_return = returns.std()
        
        if distribution == "normal":
            # Normal dağılım varsayımı
            z_score = stats.norm.ppf(alpha)
            var_value = mean_return + z_score * std_return
            
        elif distribution == "t":
            # Student's t dağılımı
            df = len(returns) - 1  # Degrees of freedom
            t_score = stats.t.ppf(alpha, df)
            var_value = mean_return + t_score * std_return
            
        elif distribution == "skew-t":
            # Skewed t dağılımı (daha gerçekçi)
            # Basit yaklaşım: skewness adjustment
            skewness = returns.skew()
            z_score = stats.norm.ppf(alpha)
            skew_adjustment = skewness * (z_score**2 - 1) / 6
            var_value = mean_return + (z_score + skew_adjustment) * std_return
            
        else:
            raise ValueError(f"Desteklenmeyen dağılım: {distribution}")
        
        return VaRResult(
            var_value=abs(var_value),
            confidence_level=confidence_level,
            time_horizon=self.time_horizon,
            method=f"Parametric VaR ({distribution})",
            additional_info={
                "returns_mean": mean_return,
                "returns_std": std_return,
                "distribution": distribution,
                "z_score": z_score if distribution == "normal" else None,
                "skewness": returns.skew(),
                "kurtosis": returns.kurtosis()
            }
        )
    
    def calculate_monte_carlo_var(self, returns: pd.Series,
                                 confidence_level: Optional[float] = None,
                                 n_simulations: int = 10000,
                                 seed: Optional[int] = None) -> VaRResult:
        """
        Monte Carlo VaR hesaplama
        
        Args:
            returns: Getiri serisi
            confidence_level: Güven seviyesi
            n_simulations: Simülasyon sayısı
            seed: Random seed
            
        Returns:
            VaRResult: VaR hesaplama sonucu
        """
        if confidence_level is None:
            confidence_level = self.confidence_level
            
        if seed is not None:
            np.random.seed(seed)
            
        alpha = 1 - confidence_level
        
        # Parametreleri hesapla
        mean_return = returns.mean()
        std_return = returns.std()
        
        # Monte Carlo simülasyonu
        simulated_returns = np.random.normal(
            loc=mean_return,
            scale=std_return,
            size=n_simulations
        )
        
        # VaR hesapla
        var_value = np.percentile(simulated_returns, alpha * 100)
        
        # CVaR (Expected Shortfall) hesapla
        cvar_value = simulated_returns[simulated_returns <= var_value].mean()
        
        return VaRResult(
            var_value=abs(var_value),
            confidence_level=confidence_level,
            time_horizon=self.time_horizon,
            method="Monte Carlo VaR",
            additional_info={
                "returns_mean": mean_return,
                "returns_std": std_return,
                "n_simulations": n_simulations,
                "cvar_value": abs(cvar_value),
                "simulation_std": simulated_returns.std(),
                "seed": seed
            }
        )
    
    def calculate_portfolio_var(self, portfolio_returns: pd.DataFrame,
                              weights: Optional[List[float]] = None,
                              confidence_level: Optional[float] = None,
                              method: str = "parametric") -> VaRResult:
        """
        Portföy VaR hesaplama
        
        Args:
            portfolio_returns: Portföy getiri matrisi (her sütun bir varlık)
            weights: Varlık ağırlıkları (None ise eşit ağırlık)
            confidence_level: Güven seviyesi
            method: VaR metodu (parametric, historical, monte_carlo)
            
        Returns:
            VaRResult: Portföy VaR sonucu
        """
        if confidence_level is None:
            confidence_level = self.confidence_level
            
        if weights is None:
            # Eşit ağırlık
            weights = [1.0 / len(portfolio_returns.columns)] * len(portfolio_returns.columns)
        
        weights = np.array(weights)
        
        # Portföy getirisi hesapla
        portfolio_return_series = (portfolio_returns * weights).sum(axis=1)
        
        # Seçilen metoda göre VaR hesapla
        if method == "parametric":
            return self.calculate_parametric_var(portfolio_return_series, confidence_level)
        elif method == "historical":
            return self.calculate_historical_var(portfolio_return_series, confidence_level)
        elif method == "monte_carlo":
            return self.calculate_monte_carlo_var(portfolio_return_series, confidence_level)
        else:
            raise ValueError(f"Desteklenmeyen metod: {method}")
    
    def calculate_correlation_matrix(self, returns: pd.DataFrame) -> pd.DataFrame:
        """
        Varlık korelasyon matrisi hesaplama
        
        Args:
            returns: Getiri matrisi (her sütun bir varlık)
            
        Returns:
            pd.DataFrame: Korelasyon matrisi
        """
        return returns.corr()
    
    def calculate_diversification_benefit(self, individual_vars: List[float],
                                       portfolio_var: float) -> Dict[str, float]:
        """
        Portföy çeşitlendirme faydası hesaplama
        
        Args:
            individual_vars: Bireysel varlık VaR'ları
            portfolio_var: Portföy VaR'ı
            
        Returns:
            Dict: Çeşitlendirme metrikleri
        """
        undiversified_var = sum(individual_vars)
        diversification_benefit = undiversified_var - portfolio_var
        diversification_ratio = portfolio_var / undiversified_var if undiversified_var > 0 else 1.0
        
        return {
            "undiversified_var": undiversified_var,
            "diversified_var": portfolio_var,
            "diversification_benefit": diversification_benefit,
            "diversification_ratio": diversification_ratio,
            "benefit_percentage": (diversification_benefit / undiversified_var * 100) if undiversified_var > 0 else 0
        }
    
    def calculate_conditional_var(self, returns: pd.Series,
                                confidence_level: Optional[float] = None) -> float:
        """
        Conditional Value at Risk (CVaR) / Expected Shortfall hesaplama
        
        Args:
            returns: Getiri serisi
            confidence_level: Güven seviyesi
            
        Returns:
            float: CVaR değeri
        """
        if confidence_level is None:
            confidence_level = self.confidence_level
            
        alpha = 1 - confidence_level
        var_value = self.calculate_historical_var(returns, confidence_level).var_value
        
        # CVaR: VaR'ın altındaki getirilerin ortalaması
        tail_returns = returns[returns <= -var_value]
        cvar_value = tail_returns.mean() if len(tail_returns) > 0 else -var_value
        
        return abs(cvar_value)
    
    def calculate_var_decomposition(self, portfolio_returns: pd.DataFrame,
                                  weights: List[float],
                                  confidence_level: Optional[float] = None) -> Dict[str, float]:
        """
        Portföy VaR bileşen analizi (Component VaR)
        
        Args:
            portfolio_returns: Portföy getiri matrisi
            weights: Varlık ağırlıkları
            confidence_level: Güven seviyesi
            
        Returns:
            Dict: Her varlığın VaR katkısı
        """
        if confidence_level is None:
            confidence_level = self.confidence_level
            
        weights = np.array(weights)
        alpha = 1 - confidence_level
        
        # Kovaryans matrisi
        cov_matrix = portfolio_returns.cov()
        
        # Portföy standart sapması
        portfolio_std = np.sqrt(weights.T @ cov_matrix @ weights)
        
        # Portföy VaR
        portfolio_var = portfolio_std * stats.norm.ppf(alpha)
        
        # Component VaR hesapla
        component_vars = {}
        for i, asset in enumerate(portfolio_returns.columns):
            # Her varlığın marjinal VaR katkısı
            marginal_var = (cov_matrix.iloc[i, :] @ weights) / portfolio_std * stats.norm.ppf(alpha)
            component_var = weights[i] * marginal_var
            component_vars[asset] = abs(component_var)
        
        return component_vars
    
    def generate_var_report(self, returns: pd.Series,
                           confidence_levels: Optional[List[float]] = None,
                           methods: Optional[List[str]] = None) -> Dict:
        """
        Kapsamlı VaR raporu oluşturma
        
        Args:
            returns: Getiri serisi
            confidence_levels: Güven seviyeleri listesi
            methods: VaR metodları listesi
            
        Returns:
            Dict: Kapsamlı VaR raporu
        """
        if confidence_levels is None:
            confidence_levels = self.CONFIDENCE_LEVELS
            
        if methods is None:
            methods = ["historical", "parametric", "monte_carlo"]
        
        report = {
            "asset_info": {
                "data_points": len(returns),
                "mean_return": returns.mean(),
                "std_return": returns.std(),
                "skewness": returns.skew(),
                "kurtosis": returns.kurtosis(),
                "min_return": returns.min(),
                "max_return": returns.max()
            },
            "var_results": {},
            "cvar_results": {},
            "summary": {}
        }
        
        # Her güven seviyesi için VaR hesapla
        for conf_level in confidence_levels:
            report["var_results"][f"{conf_level:.1%}"] = {}
            report["cvar_results"][f"{conf_level:.1%}"] = {}
            
            for method in methods:
                try:
                    if method == "historical":
                        var_result = self.calculate_historical_var(returns, conf_level)
                    elif method == "parametric":
                        var_result = self.calculate_parametric_var(returns, conf_level)
                    elif method == "monte_carlo":
                        var_result = self.calculate_monte_carlo_var(returns, conf_level)
                    
                    report["var_results"][f"{conf_level:.1%}"][method] = var_result.var_value
                    
                    # CVaR hesapla
                    cvar_value = self.calculate_conditional_var(returns, conf_level)
                    report["cvar_results"][f"{conf_level:.1%}"][method] = cvar_value
                    
                except Exception as e:
                    report["var_results"][f"{conf_level:.1%}"][method] = f"Error: {str(e)}"
                    report["cvar_results"][f"{conf_level:.1%}"][method] = f"Error: {str(e)}"
        
        # Özet istatistikler
        report["summary"] = {
            "recommended_method": "parametric",  # Varsayılan öneri
            "risk_level": "medium",  # Basit risk seviyesi
            "data_quality": "good" if len(returns) > 252 else "limited"
        }
        
        return report

# Test fonksiyonu
def test_var_calculator():
    """VaR Calculator test fonksiyonu"""
    print("🧪 VaR Calculator Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    n_days = 252  # 1 yıl
    returns = pd.Series(np.random.normal(0.001, 0.02, n_days), 
                       index=pd.date_range('2023-01-01', periods=n_days, freq='D'))
    
    # VaR Calculator başlat
    var_calc = VaRCalculator(confidence_level=0.95, time_horizon=1)
    
    # Historical VaR test
    print("\n📊 Historical VaR Test:")
    hist_var = var_calc.calculate_historical_var(returns)
    print(f"   VaR (%95): {hist_var.var_value:.4f}")
    print(f"   Metod: {hist_var.method}")
    
    # Parametric VaR test
    print("\n📈 Parametric VaR Test:")
    param_var = var_calc.calculate_parametric_var(returns)
    print(f"   VaR (%95): {param_var.var_value:.4f}")
    print(f"   Metod: {param_var.method}")
    
    # Monte Carlo VaR test
    print("\n🎲 Monte Carlo VaR Test:")
    mc_var = var_calc.calculate_monte_carlo_var(returns, n_simulations=5000)
    print(f"   VaR (%95): {mc_var.var_value:.4f}")
    print(f"   Metod: {mc_var.method}")
    
    # CVaR test
    print("\n⚠️ CVaR Test:")
    cvar = var_calc.calculate_conditional_var(returns)
    print(f"   CVaR (%95): {cvar:.4f}")
    
    # Kapsamlı rapor test
    print("\n📋 Kapsamlı VaR Raporu:")
    report = var_calc.generate_var_report(returns)
    print(f"   Veri noktası: {report['asset_info']['data_points']}")
    print(f"   Ortalama getiri: {report['asset_info']['mean_return']:.6f}")
    print(f"   Standart sapma: {report['asset_info']['std_return']:.6f}")
    
    print("\n✅ VaR Calculator Test Tamamlandı!")
    return var_calc

if __name__ == "__main__":
    test_var_calculator()
