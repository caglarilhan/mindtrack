"""
PRD v2.0 - BIST AI Smart Trader
Risk Management Engine Module

Portföy risk yönetimi motoru:
- Portfolio risk management
- Risk limits & alerts
- Dynamic rebalancing
- Risk-adjusted returns
- Stress testing integration
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

@dataclass
class RiskMetrics:
    """Risk metrikleri"""
    var_95: float
    var_99: float
    cvar_95: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    beta: float
    correlation: float

@dataclass
class RiskAlert:
    """Risk uyarısı"""
    alert_type: str
    severity: str  # low, medium, high, critical
    message: str
    timestamp: pd.Timestamp
    asset: Optional[str] = None
    current_value: Optional[float] = None
    threshold: Optional[float] = None

class RiskManagementEngine:
    """
    Portföy Risk Yönetimi Motoru
    
    PRD v2.0 gereksinimleri:
    - Portföy risk yönetimi ve izleme
    - Risk limitleri ve uyarı sistemi
    - Dinamik portföy dengeleme
    - Risk-ayarlı getiri hesaplama
    - Stres testi entegrasyonu
    """
    
    def __init__(self, risk_free_rate: float = 0.02, 
                 max_position_size: float = 0.25,
                 max_sector_exposure: float = 0.40,
                 var_limit_95: float = 0.05,
                 var_limit_99: float = 0.08):
        """
        Risk Management Engine başlatıcı
        
        Args:
            risk_free_rate: Risksiz faiz oranı
            max_position_size: Maksimum pozisyon büyüklüğü
            max_sector_exposure: Maksimum sektör maruziyeti
            var_limit_95: %95 VaR limiti
            var_limit_99: %99 VaR limiti
        """
        self.risk_free_rate = risk_free_rate
        self.max_position_size = max_position_size
        self.max_sector_exposure = max_sector_exposure
        self.var_limit_95 = var_limit_95
        self.var_limit_99 = var_limit_99
        
        # Risk yönetimi sabitleri
        self.RISK_LEVELS = {
            "low": {"color": "🟢", "threshold": 0.3},
            "medium": {"color": "🟡", "threshold": 0.6},
            "high": {"color": "🟠", "threshold": 0.8},
            "critical": {"color": "🔴", "threshold": 1.0}
        }
        
        # Uyarı geçmişi
        self.alert_history: List[RiskAlert] = []
        
    def calculate_portfolio_risk_metrics(self, portfolio_returns: pd.Series,
                                       benchmark_returns: Optional[pd.Series] = None) -> RiskMetrics:
        """
        Portföy risk metrikleri hesaplama
        
        Args:
            portfolio_returns: Portföy getiri serisi
            benchmark_returns: Benchmark getiri serisi
            
        Returns:
            RiskMetrics: Risk metrikleri
        """
        # Temel risk metrikleri
        volatility = portfolio_returns.std() * np.sqrt(252)  # Yıllık volatilite
        
        # VaR hesaplama
        var_95 = np.percentile(portfolio_returns, 5)
        var_99 = np.percentile(portfolio_returns, 1)
        
        # CVaR hesaplama
        cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
        
        # Sharpe ratio
        excess_returns = portfolio_returns - self.risk_free_rate / 252
        sharpe_ratio = excess_returns.mean() / portfolio_returns.std() * np.sqrt(252)
        
        # Maximum drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Beta ve korelasyon (benchmark varsa)
        beta = 1.0
        correlation = 0.0
        if benchmark_returns is not None:
            # Beta hesaplama
            covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
            benchmark_variance = benchmark_returns.var()
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
            
            # Korelasyon
            correlation = portfolio_returns.corr(benchmark_returns)
        
        return RiskMetrics(
            var_95=abs(var_95),
            var_99=abs(var_99),
            cvar_95=abs(cvar_95),
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=abs(max_drawdown),
            beta=beta,
            correlation=correlation
        )
    
    def check_risk_limits(self, portfolio_weights: Dict[str, float],
                          portfolio_returns: pd.Series,
                          asset_returns: pd.DataFrame,
                          sector_info: Optional[Dict[str, str]] = None) -> List[RiskAlert]:
        """
        Risk limitlerini kontrol etme
        
        Args:
            portfolio_weights: Varlık ağırlıkları
            portfolio_returns: Portföy getiri serisi
            asset_returns: Varlık getiri matrisi
            sector_info: Varlık-sektör eşleştirmesi
            
        Returns:
            List[RiskAlert]: Risk uyarıları
        """
        alerts = []
        current_time = pd.Timestamp.now()
        
        # 1. Pozisyon büyüklüğü kontrolü
        for asset, weight in portfolio_weights.items():
            if weight > self.max_position_size:
                alerts.append(RiskAlert(
                    alert_type="position_size_limit",
                    severity="high",
                    message=f"Pozisyon büyüklüğü limiti aşıldı: {asset}",
                    timestamp=current_time,
                    asset=asset,
                    current_value=weight,
                    threshold=self.max_position_size
                ))
        
        # 2. Sektör maruziyeti kontrolü
        if sector_info:
            sector_exposures = {}
            for asset, weight in portfolio_weights.items():
                sector = sector_info.get(asset, "Unknown")
                sector_exposures[sector] = sector_exposures.get(sector, 0) + weight
            
            for sector, exposure in sector_exposures.items():
                if exposure > self.max_sector_exposure:
                    alerts.append(RiskAlert(
                        alert_type="sector_exposure_limit",
                        severity="medium",
                        message=f"Sektör maruziyeti limiti aşıldı: {sector}",
                        timestamp=current_time,
                        asset=sector,
                        current_value=exposure,
                        threshold=self.max_sector_exposure
                    ))
        
        # 3. VaR limitleri kontrolü
        risk_metrics = self.calculate_portfolio_risk_metrics(portfolio_returns)
        
        if risk_metrics.var_95 > self.var_limit_95:
            alerts.append(RiskAlert(
                alert_type="var_limit_95",
                severity="critical",
                message=f"%95 VaR limiti aşıldı",
                timestamp=current_time,
                current_value=risk_metrics.var_95,
                threshold=self.var_limit_95
            ))
        
        if risk_metrics.var_99 > self.var_limit_99:
            alerts.append(RiskAlert(
                alert_type="var_limit_99",
                severity="critical",
                message=f"%99 VaR limiti aşıldı",
                timestamp=current_time,
                current_value=risk_metrics.var_99,
                threshold=self.var_limit_99
            ))
        
        # 4. Volatilite kontrolü
        if risk_metrics.volatility > 0.25:  # %25 yıllık volatilite
            alerts.append(RiskAlert(
                alert_type="volatility_limit",
                severity="high",
                message=f"Volatilite limiti aşıldı",
                timestamp=current_time,
                current_value=risk_metrics.volatility,
                threshold=0.25
            ))
        
        # 5. Drawdown kontrolü
        if risk_metrics.max_drawdown > 0.20:  # %20 maksimum drawdown
            alerts.append(RiskAlert(
                alert_type="drawdown_limit",
                severity="high",
                message=f"Maksimum drawdown limiti aşıldı",
                timestamp=current_time,
                current_value=risk_metrics.max_drawdown,
                threshold=0.20
            ))
        
        # Uyarıları geçmişe ekle
        self.alert_history.extend(alerts)
        
        return alerts
    
    def optimize_portfolio_weights(self, asset_returns: pd.DataFrame,
                                 target_return: Optional[float] = None,
                                 risk_aversion: float = 1.0,
                                 constraints: Optional[Dict] = None) -> Dict[str, float]:
        """
        Portföy ağırlıklarını optimize etme
        
        Args:
            asset_returns: Varlık getiri matrisi
            target_return: Hedef getiri (None ise maksimum Sharpe)
            risk_aversion: Risk kaçınma parametresi
            constraints: Ek kısıtlamalar
            
        Returns:
            Dict[str, float]: Optimize edilmiş ağırlıklar
        """
        n_assets = len(asset_returns.columns)
        
        # Kovaryans matrisi
        cov_matrix = asset_returns.cov() * 252  # Yıllık
        
        # Ortalama getiriler
        mean_returns = asset_returns.mean() * 252  # Yıllık
        
        # Varsayılan kısıtlamalar
        if constraints is None:
            constraints = {
                "min_weight": 0.0,
                "max_weight": self.max_position_size,
                "sum_weights": 1.0
            }
        
        def objective_function(weights):
            """Optimizasyon amaç fonksiyonu"""
            weights = np.array(weights)
            
            # Portföy getirisi
            portfolio_return = np.sum(weights * mean_returns)
            
            # Portföy volatilitesi
            portfolio_volatility = np.sqrt(weights.T @ cov_matrix @ weights)
            
            if target_return is not None:
                # Hedef getiri ile volatilite minimizasyonu
                return risk_aversion * portfolio_volatility
            else:
                # Sharpe ratio maksimizasyonu
                excess_return = portfolio_return - self.risk_free_rate
                sharpe_ratio = excess_return / portfolio_volatility if portfolio_volatility > 0 else 0
                return -sharpe_ratio  # Minimize et (negatif Sharpe)
        
        def constraint_sum_weights(weights):
            """Ağırlık toplamı kısıtlaması"""
            return np.sum(weights) - constraints["sum_weights"]
        
        def constraint_target_return(weights):
            """Hedef getiri kısıtlaması"""
            if target_return is not None:
                return np.sum(weights * mean_returns) - target_return
            return 0
        
        # Kısıtlamalar
        constraint_list = [
            {'type': 'eq', 'fun': constraint_sum_weights}
        ]
        
        if target_return is not None:
            constraint_list.append({'type': 'eq', 'fun': constraint_target_return})
        
        # Sınırlar
        bounds = [(constraints["min_weight"], constraints["max_weight"]) for _ in range(n_assets)]
        
        # Başlangıç ağırlıkları (eşit ağırlık)
        initial_weights = np.array([1.0 / n_assets] * n_assets)
        
        # Optimizasyon
        result = minimize(
            objective_function,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraint_list,
            options={'maxiter': 1000}
        )
        
        if result.success:
            optimized_weights = result.x
            # Normalize et
            optimized_weights = optimized_weights / np.sum(optimized_weights)
            
            return dict(zip(asset_returns.columns, optimized_weights))
        else:
            # Optimizasyon başarısız, eşit ağırlık döndür
            equal_weights = {asset: 1.0 / n_assets for asset in asset_returns.columns}
            return equal_weights
    
    def calculate_risk_adjusted_returns(self, portfolio_returns: pd.Series,
                                      benchmark_returns: Optional[pd.Series] = None) -> Dict[str, float]:
        """
        Risk-ayarlı getiri metrikleri
        
        Args:
            portfolio_returns: Portföy getiri serisi
            benchmark_returns: Benchmark getiri serisi
            
        Returns:
            Dict: Risk-ayarlı getiri metrikleri
        """
        # Temel metrikler
        total_return = (1 + portfolio_returns).prod() - 1
        annualized_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
        volatility = portfolio_returns.std() * np.sqrt(252)
        
        # Sharpe ratio
        excess_returns = portfolio_returns - self.risk_free_rate / 252
        sharpe_ratio = excess_returns.mean() / portfolio_returns.std() * np.sqrt(252)
        
        # Sortino ratio (sadece downside risk)
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_deviation = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = excess_returns.mean() / downside_deviation * np.sqrt(252) if downside_deviation > 0 else 0
        
        # Calmar ratio (return / max drawdown)
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = abs(drawdown.min())
        calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0
        
        # Information ratio (benchmark varsa)
        information_ratio = 0
        if benchmark_returns is not None:
            active_returns = portfolio_returns - benchmark_returns
            tracking_error = active_returns.std() * np.sqrt(252)
            information_ratio = active_returns.mean() / tracking_error * np.sqrt(252) if tracking_error > 0 else 0
        
        return {
            "total_return": total_return,
            "annualized_return": annualized_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "calmar_ratio": calmar_ratio,
            "information_ratio": information_ratio,
            "max_drawdown": max_drawdown
        }
    
    def perform_stress_test(self, portfolio_weights: Dict[str, float],
                           asset_returns: pd.DataFrame,
                           stress_scenarios: Optional[Dict[str, Dict]] = None) -> Dict:
        """
        Stres testi performansı
        
        Args:
            portfolio_weights: Portföy ağırlıkları
            asset_returns: Varlık getiri matrisi
            stress_scenarios: Stres senaryoları
            
        Returns:
            Dict: Stres testi sonuçları
        """
        if stress_scenarios is None:
            # Varsayılan stres senaryoları
            stress_scenarios = {
                "market_crash": {
                    "description": "Piyasa çöküşü (-20% tüm varlıklar)",
                    "shock_multiplier": -0.20
                },
                "interest_rate_shock": {
                    "description": "Faiz oranı şoku (-10% tahvil, +5% hisse)",
                    "bond_shock": -0.10,
                    "equity_shock": 0.05
                },
                "sector_crisis": {
                    "description": "Sektör krizi (finans -30%, diğer -5%)",
                    "finance_shock": -0.30,
                    "other_shock": -0.05
                },
                "volatility_spike": {
                    "description": "Volatilite artışı (2x standart sapma)",
                    "volatility_multiplier": 2.0
                }
            }
        
        stress_results = {}
        
        for scenario_name, scenario in stress_scenarios.items():
            # Senaryo uygula
            if scenario_name == "market_crash":
                # Tüm varlıklara aynı şok
                shocked_returns = asset_returns * (1 + scenario["shock_multiplier"])
                
            elif scenario_name == "interest_rate_shock":
                # Basit yaklaşım: ilk 3 varlık tahvil, sonraki hisse
                shocked_returns = asset_returns.copy()
                n_assets = len(asset_returns.columns)
                
                for i, asset in enumerate(asset_returns.columns):
                    if i < 3:  # Tahvil varsayımı
                        shocked_returns[asset] = asset_returns[asset] * (1 + scenario["bond_shock"])
                    else:  # Hisse varsayımı
                        shocked_returns[asset] = asset_returns[asset] * (1 + scenario["equity_shock"])
                        
            elif scenario_name == "sector_crisis":
                # Basit yaklaşım: ilk 2 varlık finans
                shocked_returns = asset_returns.copy()
                
                for i, asset in enumerate(asset_returns.columns):
                    if i < 2:  # Finans varsayımı
                        shocked_returns[asset] = asset_returns[asset] * (1 + scenario["finance_shock"])
                    else:
                        shocked_returns[asset] = asset_returns[asset] * (1 + scenario["other_shock"])
                        
            elif scenario_name == "volatility_spike":
                # Volatilite artışı
                shocked_returns = asset_returns * scenario["volatility_multiplier"]
            
            # Stres altında portföy getirisi
            portfolio_return_series = pd.Series(0.0, index=asset_returns.index)
            for asset, weight in portfolio_weights.items():
                portfolio_return_series += weight * shocked_returns[asset]
            
            # Stres altında risk metrikleri
            stress_metrics = self.calculate_portfolio_risk_metrics(portfolio_return_series)
            
            stress_results[scenario_name] = {
                "description": scenario["description"],
                "portfolio_return": portfolio_return_series.mean() * 252,
                "portfolio_volatility": stress_metrics.volatility,
                "var_95": stress_metrics.var_95,
                "var_99": stress_metrics.var_99,
                "max_drawdown": stress_metrics.max_drawdown,
                "sharpe_ratio": stress_metrics.sharpe_ratio
            }
        
        return stress_results
    
    def generate_risk_report(self, portfolio_weights: Dict[str, float],
                            asset_returns: pd.DataFrame,
                            portfolio_returns: pd.Series,
                            benchmark_returns: Optional[pd.Series] = None) -> Dict:
        """
        Kapsamlı risk raporu oluşturma
        
        Args:
            portfolio_weights: Portföy ağırlıkları
            asset_returns: Varlık getiri matrisi
            portfolio_returns: Portföy getiri serisi
            benchmark_returns: Benchmark getiri serisi
            
        Returns:
            Dict: Kapsamlı risk raporu
        """
        print("📊 Risk Raporu Oluşturuluyor...")
        
        # Risk metrikleri
        risk_metrics = self.calculate_portfolio_risk_metrics(portfolio_returns, benchmark_returns)
        
        # Risk limitleri kontrolü
        sector_info = None  # Basit test için
        risk_alerts = self.check_risk_limits(portfolio_weights, portfolio_returns, asset_returns, sector_info)
        
        # Risk-ayarlı getiri
        risk_adjusted_returns = self.calculate_risk_adjusted_returns(portfolio_returns, benchmark_returns)
        
        # Stres testi
        stress_test_results = self.perform_stress_test(portfolio_weights, asset_returns)
        
        # Rapor oluştur
        report = {
            "risk_metrics": {
                "var_95": risk_metrics.var_95,
                "var_99": risk_metrics.var_99,
                "cvar_95": risk_metrics.cvar_95,
                "volatility": risk_metrics.volatility,
                "sharpe_ratio": risk_metrics.sharpe_ratio,
                "max_drawdown": risk_metrics.max_drawdown,
                "beta": risk_metrics.beta,
                "correlation": risk_metrics.correlation
            },
            "risk_alerts": [
                {
                    "type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "asset": alert.asset,
                    "current_value": alert.current_value,
                    "threshold": alert.threshold
                }
                for alert in risk_alerts
            ],
            "risk_adjusted_returns": risk_adjusted_returns,
            "stress_test_results": stress_test_results,
            "portfolio_composition": {
                "n_assets": len(portfolio_weights),
                "weights": portfolio_weights,
                "concentration": max(portfolio_weights.values()) if portfolio_weights else 0
            },
            "summary": {
                "overall_risk_level": "medium",  # Basit risk seviyesi
                "risk_alerts_count": len(risk_alerts),
                "critical_alerts": len([a for a in risk_alerts if a.severity == "critical"]),
                "recommendations": self._generate_risk_recommendations(risk_alerts, risk_metrics)
            }
        }
        
        print("✅ Risk Raporu Tamamlandı!")
        return report
    
    def _generate_risk_recommendations(self, risk_alerts: List[RiskAlert],
                                     risk_metrics: RiskMetrics) -> List[str]:
        """Risk önerileri oluşturma"""
        recommendations = []
        
        # VaR önerileri
        if risk_metrics.var_95 > self.var_limit_95 * 0.8:  # %80'e yaklaşıyorsa
            recommendations.append("VaR limitine yaklaşılıyor - pozisyon büyüklüklerini azaltmayı düşünün")
        
        # Volatilite önerileri
        if risk_metrics.volatility > 0.20:
            recommendations.append("Yüksek volatilite - portföy çeşitlendirmesini artırın")
        
        # Drawdown önerileri
        if risk_metrics.max_drawdown > 0.15:
            recommendations.append("Büyük drawdown - stop-loss seviyelerini gözden geçirin")
        
        # Sharpe ratio önerileri
        if risk_metrics.sharpe_ratio < 0.5:
            recommendations.append("Düşük Sharpe ratio - risk-ayarlı getiriyi iyileştirin")
        
        # Genel öneriler
        if not recommendations:
            recommendations.append("Portföy risk seviyesi kabul edilebilir aralıkta")
        
        return recommendations

# Test fonksiyonu
def test_risk_management_engine():
    """Risk Management Engine test fonksiyonu"""
    print("🧪 Risk Management Engine Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    n_days = 252  # 1 yıl
    n_assets = 8
    
    # Farklı varlık türleri için getiri verisi
    returns_data = {}
    asset_names = []
    
    for i in range(n_assets):
        if i < 3:  # Tahvil benzeri (düşük volatilite)
            asset_name = f'Bond_{i+1}'
            returns_data[asset_name] = np.random.normal(0.0005, 0.005, n_days)
        elif i < 6:  # Hisse benzeri (orta volatilite)
            asset_name = f'Stock_{i+1}'
            returns_data[asset_name] = np.random.normal(0.001, 0.02, n_days)
        else:  # Emtia benzeri (yüksek volatilite)
            asset_name = f'Commodity_{i+1}'
            returns_data[asset_name] = np.random.normal(0.0008, 0.03, n_days)
        
        asset_names.append(asset_name)
    
    asset_returns = pd.DataFrame(returns_data, 
                                index=pd.date_range('2023-01-01', periods=n_days, freq='D'))
    
    # Benchmark (piyasa ortalaması)
    benchmark_returns = asset_returns.mean(axis=1)
    
    # Test portföy ağırlıkları (gerçek varlık isimleriyle)
    portfolio_weights = {}
    for i, asset_name in enumerate(asset_names):
        if i < 3:  # Tahvil
            portfolio_weights[asset_name] = 0.15 if i < 2 else 0.10
        elif i < 6:  # Hisse
            portfolio_weights[asset_name] = 0.20 if i == 3 else (0.15 if i == 4 else 0.10)
        else:  # Emtia
            portfolio_weights[asset_name] = 0.10 if i == 6 else 0.05
    
    # Portföy getirisi hesapla
    portfolio_returns = pd.Series(0.0, index=asset_returns.index)
    for asset, weight in portfolio_weights.items():
        portfolio_returns += weight * asset_returns[asset]
    
    # Risk Management Engine başlat
    risk_engine = RiskManagementEngine(
        risk_free_rate=0.03,
        max_position_size=0.25,
        max_sector_exposure=0.40,
        var_limit_95=0.05,
        var_limit_99=0.08
    )
    
    # Risk metrikleri test
    print("\n📊 Risk Metrikleri Test:")
    risk_metrics = risk_engine.calculate_portfolio_risk_metrics(portfolio_returns, benchmark_returns)
    print(f"   %95 VaR: {risk_metrics.var_95:.4f}")
    print(f"   %99 VaR: {risk_metrics.var_99:.4f}")
    print(f"   Volatilite: {risk_metrics.volatility:.4f}")
    print(f"   Sharpe Ratio: {risk_metrics.sharpe_ratio:.4f}")
    print(f"   Max Drawdown: {risk_metrics.max_drawdown:.4f}")
    
    # Risk limitleri test
    print("\n⚠️ Risk Limitleri Test:")
    risk_alerts = risk_engine.check_risk_limits(portfolio_weights, portfolio_returns, asset_returns)
    print(f"   Toplam uyarı: {len(risk_alerts)}")
    for alert in risk_alerts:
        print(f"   {alert.severity.upper()}: {alert.message}")
    
    # Risk-ayarlı getiri test
    print("\n📈 Risk-Ayarlı Getiri Test:")
    risk_adjusted = risk_engine.calculate_risk_adjusted_returns(portfolio_returns, benchmark_returns)
    print(f"   Yıllık getiri: {risk_adjusted['annualized_return']:.4f}")
    print(f"   Sharpe Ratio: {risk_adjusted['sharpe_ratio']:.4f}")
    print(f"   Sortino Ratio: {risk_adjusted['sortino_ratio']:.4f}")
    print(f"   Calmar Ratio: {risk_adjusted['calmar_ratio']:.4f}")
    
    # Stres testi test
    print("\n🔥 Stres Testi Test:")
    stress_results = risk_engine.perform_stress_test(portfolio_weights, asset_returns)
    for scenario, results in stress_results.items():
        print(f"   {scenario}: VaR %95 = {results['var_95']:.4f}, "
              f"Getiri = {results['portfolio_return']:.4f}")
    
    # Kapsamlı rapor test
    print("\n📋 Kapsamlı Risk Raporu Test:")
    risk_report = risk_engine.generate_risk_report(portfolio_weights, asset_returns, portfolio_returns, benchmark_returns)
    print(f"   Risk seviyesi: {risk_report['summary']['overall_risk_level']}")
    print(f"   Uyarı sayısı: {risk_report['summary']['risk_alerts_count']}")
    print(f"   Kritik uyarı: {risk_report['summary']['critical_alerts']}")
    
    print("\n✅ Risk Management Engine Test Tamamlandı!")
    return risk_engine

if __name__ == "__main__":
    test_risk_management_engine()
