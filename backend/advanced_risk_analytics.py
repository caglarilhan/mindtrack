"""
PRD v2.0 - BIST AI Smart Trader
Advanced Risk Analytics Module

Gelişmiş risk analizi:
- VaR (Value at Risk) calculations
- Expected Shortfall (CVaR)
- Stress testing scenarios
- Risk factor analysis
- Portfolio risk decomposition
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class RiskMetrics:
    """Risk metrikleri"""
    portfolio_id: str
    timestamp: datetime
    var_95: float  # 95% VaR
    var_99: float  # 99% VaR
    cvar_95: float  # 95% Expected Shortfall
    cvar_99: float  # 99% Expected Shortfall
    volatility: float
    beta: float
    sharpe_ratio: float
    max_drawdown: float
    tracking_error: float
    information_ratio: float

@dataclass
class StressTestScenario:
    """Stres testi senaryosu"""
    scenario_id: str
    name: str
    description: str
    market_shock: float  # Piyasa şoku (%)
    interest_rate_shock: float  # Faiz oranı şoku (%)
    currency_shock: float  # Döviz kuru şoku (%)
    commodity_shock: float  # Emtia şoku (%)
    correlation_breakdown: bool  # Korelasyon bozulması
    liquidity_dry_up: bool  # Likidite kuruması
    created_at: datetime = None

@dataclass
class RiskFactor:
    """Risk faktörü"""
    factor_id: str
    name: str
    category: str  # market, credit, liquidity, operational
    sensitivity: float
    contribution: float
    volatility: float
    correlation: float
    timestamp: datetime = None

@dataclass
class PortfolioRisk:
    """Portföy riski"""
    portfolio_id: str
    timestamp: datetime
    total_risk: float
    systematic_risk: float
    idiosyncratic_risk: float
    risk_decomposition: Dict[str, float]
    concentration_risk: float
    sector_risk: float
    geographic_risk: float
    currency_risk: float

class AdvancedRiskAnalytics:
    """
    Gelişmiş Risk Analizi
    
    PRD v2.0 gereksinimleri:
    - VaR (Value at Risk) hesaplamaları
    - Expected Shortfall (CVaR)
    - Stres testi senaryoları
    - Risk faktör analizi
    - Portföy risk ayrıştırması
    """
    
    def __init__(self):
        """Advanced Risk Analytics başlatıcı"""
        # Risk metrikleri
        self.risk_metrics = {}
        
        # Stres testi senaryoları
        self.stress_scenarios = {}
        
        # Risk faktörleri
        self.risk_factors = {}
        
        # Portföy riskleri
        self.portfolio_risks = {}
        
        # Varsayılan stres testi senaryolarını ekle
        self._add_default_stress_scenarios()
        
        # Risk parametreleri
        self.risk_params = {
            'var_confidence_levels': [0.95, 0.99],
            'historical_window': 252,  # 1 yıl
            'monte_carlo_simulations': 10000,
            'stress_test_horizon': 10  # 10 gün
        }
    
    def _add_default_stress_scenarios(self):
        """Varsayılan stres testi senaryolarını ekle"""
        scenarios = {
            'market_crash': StressTestScenario(
                scenario_id='market_crash',
                name='Piyasa Çöküşü',
                description='2008 benzeri piyasa çöküşü senaryosu',
                market_shock=-20.0,
                interest_rate_shock=2.0,
                currency_shock=-15.0,
                commodity_shock=-25.0,
                correlation_breakdown=True,
                liquidity_dry_up=True,
                created_at=datetime.now()
            ),
            'interest_rate_spike': StressTestScenario(
                scenario_id='interest_rate_spike',
                name='Faiz Oranı Artışı',
                description='Ani faiz oranı artışı senaryosu',
                market_shock=-10.0,
                interest_rate_shock=5.0,
                currency_shock=-5.0,
                commodity_shock=-10.0,
                correlation_breakdown=False,
                liquidity_dry_up=False,
                created_at=datetime.now()
            ),
            'currency_crisis': StressTestScenario(
                scenario_id='currency_crisis',
                name='Döviz Krizleri',
                description='Döviz kuru volatilite artışı',
                market_shock=-15.0,
                interest_rate_shock=3.0,
                currency_shock=-30.0,
                commodity_shock=-20.0,
                correlation_breakdown=True,
                liquidity_dry_up=True,
                created_at=datetime.now()
            ),
            'commodity_shock': StressTestScenario(
                scenario_id='commodity_shock',
                name='Emtia Şoku',
                description='Petrol ve emtia fiyat şoku',
                market_shock=-8.0,
                interest_rate_shock=1.0,
                currency_shock=-5.0,
                commodity_shock=-40.0,
                correlation_breakdown=False,
                liquidity_dry_up=False,
                created_at=datetime.now()
            )
        }
        
        self.stress_scenarios.update(scenarios)
        print("✅ Varsayılan stres testi senaryoları eklendi")
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95, method: str = "historical") -> float:
        """
        Value at Risk hesapla
        
        Args:
            returns: Getiri serisi
            confidence_level: Güven seviyesi
            method: Hesaplama yöntemi (historical, parametric, monte_carlo)
            
        Returns:
            float: VaR değeri
        """
        try:
            if method == "historical":
                # Tarihsel simülasyon
                var = np.percentile(returns, (1 - confidence_level) * 100)
                return abs(var)
            
            elif method == "parametric":
                # Parametrik (normal dağılım)
                mean_return = returns.mean()
                std_return = returns.std()
                z_score = self._get_z_score(confidence_level)
                var = mean_return - (z_score * std_return)
                return abs(var)
            
            elif method == "monte_carlo":
                # Monte Carlo simülasyonu
                mean_return = returns.mean()
                std_return = returns.std()
                
                # Rastgele getiri simülasyonu
                np.random.seed(42)
                simulated_returns = np.random.normal(mean_return, std_return, self.risk_params['monte_carlo_simulations'])
                
                var = np.percentile(simulated_returns, (1 - confidence_level) * 100)
                return abs(var)
            
            else:
                raise ValueError(f"Bilinmeyen VaR yöntemi: {method}")
                
        except Exception as e:
            print(f"❌ VaR hesaplama hatası: {str(e)}")
            return 0.0
    
    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95, method: str = "historical") -> float:
        """
        Conditional Value at Risk (Expected Shortfall) hesapla
        
        Args:
            returns: Getiri serisi
            confidence_level: Güven seviyesi
            method: Hesaplama yöntemi
            
        Returns:
            float: CVaR değeri
        """
        try:
            if method == "historical":
                # Tarihsel simülasyon
                var = self.calculate_var(returns, confidence_level, "historical")
                tail_returns = returns[returns <= -var]
                cvar = tail_returns.mean()
                return abs(cvar)
            
            elif method == "parametric":
                # Parametrik (normal dağılım)
                mean_return = returns.mean()
                std_return = returns.std()
                z_score = self._get_z_score(confidence_level)
                
                # Normal dağılım için CVaR formülü
                phi_z = np.exp(-0.5 * z_score**2) / np.sqrt(2 * np.pi)
                cvar = mean_return - (std_return * phi_z / (1 - confidence_level))
                return abs(cvar)
            
            else:
                raise ValueError(f"Bilinmeyen CVaR yöntemi: {method}")
                
        except Exception as e:
            print(f"❌ CVaR hesaplama hatası: {str(e)}")
            return 0.0
    
    def _get_z_score(self, confidence_level: float) -> float:
        """Z-skor hesapla"""
        try:
            # Normal dağılım için z-skor
            if confidence_level == 0.95:
                return 1.645
            elif confidence_level == 0.99:
                return 2.326
            elif confidence_level == 0.90:
                return 1.282
            else:
                # Yaklaşık hesaplama
                return np.sqrt(2) * self._erfinv(2 * confidence_level - 1)
                
        except Exception:
            return 1.645  # Varsayılan 95% güven seviyesi
    
    def _erfinv(self, x: float) -> float:
        """Inverse error function yaklaşımı"""
        try:
            # Basit yaklaşım
            if abs(x) < 0.7:
                return x * (1 + x**2 / 6 + x**4 / 120)
            else:
                return np.sign(x) * np.sqrt(-np.log(1 - abs(x)))
        except Exception:
            return 0.0
    
    def calculate_portfolio_risk_metrics(self, portfolio_returns: pd.Series, benchmark_returns: Optional[pd.Series] = None,
                                        risk_free_rate: float = 0.02) -> RiskMetrics:
        """
        Portföy risk metriklerini hesapla
        
        Args:
            portfolio_returns: Portföy getiri serisi
            benchmark_returns: Benchmark getiri serisi
            risk_free_rate: Risksiz faiz oranı
            
        Returns:
            RiskMetrics: Risk metrikleri
        """
        try:
            # Temel istatistikler
            volatility = portfolio_returns.std() * np.sqrt(252)  # Yıllık volatilite
            
            # VaR hesaplamaları
            var_95 = self.calculate_var(portfolio_returns, 0.95, "historical")
            var_99 = self.calculate_var(portfolio_returns, 0.99, "historical")
            
            # CVaR hesaplamaları
            cvar_95 = self.calculate_cvar(portfolio_returns, 0.95, "historical")
            cvar_99 = self.calculate_cvar(portfolio_returns, 0.99, "historical")
            
            # Beta hesaplama
            beta = 1.0
            if benchmark_returns is not None and len(benchmark_returns) > 0:
                covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
                benchmark_variance = benchmark_returns.var()
                if benchmark_variance > 0:
                    beta = covariance / benchmark_variance
            
            # Sharpe ratio
            excess_returns = portfolio_returns - risk_free_rate/252
            sharpe_ratio = 0.0
            if volatility > 0:
                sharpe_ratio = (excess_returns.mean() * 252) / volatility
            
            # Maximum drawdown
            cumulative_returns = (1 + portfolio_returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # Tracking error
            tracking_error = 0.0
            if benchmark_returns is not None:
                tracking_diff = portfolio_returns - benchmark_returns
                tracking_error = tracking_diff.std() * np.sqrt(252)
            
            # Information ratio
            information_ratio = 0.0
            if tracking_error > 0:
                information_ratio = (portfolio_returns.mean() - benchmark_returns.mean()) * 252 / tracking_error
            
            # Risk metrikleri oluştur
            risk_metrics = RiskMetrics(
                portfolio_id="portfolio_1",
                timestamp=datetime.now(),
                var_95=var_95,
                var_99=var_99,
                cvar_95=cvar_95,
                cvar_99=cvar_99,
                volatility=volatility,
                beta=beta,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                tracking_error=tracking_error,
                information_ratio=information_ratio
            )
            
            # Kaydet
            self.risk_metrics[f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}"] = risk_metrics
            
            return risk_metrics
            
        except Exception as e:
            print(f"❌ Portföy risk metrikleri hesaplama hatası: {str(e)}")
            return RiskMetrics(
                portfolio_id="", timestamp=datetime.now(),
                var_95=0.0, var_99=0.0, cvar_95=0.0, cvar_99=0.0,
                volatility=0.0, beta=0.0, sharpe_ratio=0.0,
                max_drawdown=0.0, tracking_error=0.0, information_ratio=0.0
            )
    
    def run_stress_test(self, portfolio_returns: pd.Series, scenario_id: str) -> Dict[str, Any]:
        """
        Stres testi çalıştır
        
        Args:
            portfolio_returns: Portföy getiri serisi
            scenario_id: Senaryo ID
            
        Returns:
            Dict[str, Any]: Stres testi sonuçları
        """
        try:
            if scenario_id not in self.stress_scenarios:
                raise ValueError(f"Senaryo bulunamadı: {scenario_id}")
            
            scenario = self.stress_scenarios[scenario_id]
            
            # Senaryo etkilerini uygula
            shocked_returns = portfolio_returns.copy()
            
            # Piyasa şoku
            if scenario.market_shock != 0:
                market_shock_factor = 1 + (scenario.market_shock / 100)
                shocked_returns = shocked_returns * market_shock_factor
            
            # Faiz oranı şoku
            if scenario.interest_rate_shock != 0:
                # Basit faiz oranı etkisi
                ir_shock_factor = 1 + (scenario.interest_rate_shock / 100) * 0.1
                shocked_returns = shocked_returns * ir_shock_factor
            
            # Döviz şoku
            if scenario.currency_shock != 0:
                # Döviz etkisi (basit)
                fx_shock_factor = 1 + (scenario.currency_shock / 100) * 0.05
                shocked_returns = shocked_returns * fx_shock_factor
            
            # Emtia şoku
            if scenario.commodity_shock != 0:
                # Emtia etkisi (basit)
                commodity_shock_factor = 1 + (scenario.commodity_shock / 100) * 0.03
                shocked_returns = shocked_returns * commodity_shock_factor
            
            # Korelasyon bozulması
            if scenario.correlation_breakdown:
                # Basit korelasyon etkisi
                shocked_returns = shocked_returns * (1 + np.random.normal(0, 0.1, len(shocked_returns)))
            
            # Likidite kuruması
            if scenario.liquidity_dry_up:
                # Likidite etkisi
                liquidity_factor = 1 + np.random.uniform(-0.2, 0, len(shocked_returns))
                shocked_returns = shocked_returns * liquidity_factor
            
            # Stres testi sonuçları
            original_var_95 = self.calculate_var(portfolio_returns, 0.95)
            stressed_var_95 = self.calculate_var(shocked_returns, 0.95)
            
            original_var_99 = self.calculate_var(portfolio_returns, 0.99)
            stressed_var_99 = self.calculate_var(shocked_returns, 0.99)
            
            original_volatility = portfolio_returns.std() * np.sqrt(252)
            stressed_volatility = shocked_returns.std() * np.sqrt(252)
            
            # Sonuçları hesapla
            var_95_change = ((stressed_var_95 - original_var_95) / original_var_95) * 100 if original_var_95 > 0 else 0
            var_99_change = ((stressed_var_99 - original_var_99) / original_var_99) * 100 if original_var_99 > 0 else 0
            volatility_change = ((stressed_volatility - original_volatility) / original_volatility) * 100 if original_volatility > 0 else 0
            
            results = {
                'scenario_id': scenario_id,
                'scenario_name': scenario.name,
                'original_metrics': {
                    'var_95': original_var_95,
                    'var_99': original_var_99,
                    'volatility': original_volatility
                },
                'stressed_metrics': {
                    'var_95': stressed_var_95,
                    'var_99': stressed_var_99,
                    'volatility': stressed_volatility
                },
                'changes': {
                    'var_95_change_pct': var_95_change,
                    'var_99_change_pct': var_99_change,
                    'volatility_change_pct': volatility_change
                },
                'timestamp': datetime.now()
            }
            
            return results
            
        except Exception as e:
            print(f"❌ Stres testi hatası: {str(e)}")
            return {'error': str(e)}
    
    def analyze_risk_factors(self, portfolio_returns: pd.Series, factor_returns: Dict[str, pd.Series]) -> List[RiskFactor]:
        """
        Risk faktörlerini analiz et
        
        Args:
            portfolio_returns: Portföy getiri serisi
            factor_returns: Faktör getiri serileri
            
        Returns:
            List[RiskFactor]: Risk faktörleri
        """
        try:
            risk_factors = []
            
            for factor_name, factor_return in factor_returns.items():
                if len(factor_return) > 0 and len(portfolio_returns) > 0:
                    # Faktör duyarlılığı (beta)
                    covariance = np.cov(portfolio_returns, factor_return)[0, 1]
                    factor_variance = factor_return.var()
                    
                    sensitivity = 0.0
                    if factor_variance > 0:
                        sensitivity = covariance / factor_variance
                    
                    # Faktör katkısı
                    contribution = abs(sensitivity) * factor_return.std() * np.sqrt(252)
                    
                    # Faktör volatilitesi
                    factor_volatility = factor_return.std() * np.sqrt(252)
                    
                    # Korelasyon
                    correlation = 0.0
                    if portfolio_returns.std() > 0 and factor_return.std() > 0:
                        correlation = covariance / (portfolio_returns.std() * factor_return.std())
                    
                    # Kategori belirleme
                    category = "market"
                    if "interest_rate" in factor_name.lower():
                        category = "credit"
                    elif "liquidity" in factor_name.lower():
                        category = "liquidity"
                    elif "operational" in factor_name.lower():
                        category = "operational"
                    
                    risk_factor = RiskFactor(
                        factor_id=f"factor_{factor_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        name=factor_name,
                        category=category,
                        sensitivity=sensitivity,
                        contribution=contribution,
                        volatility=factor_volatility,
                        correlation=correlation,
                        timestamp=datetime.now()
                    )
                    
                    risk_factors.append(risk_factor)
                    self.risk_factors[risk_factor.factor_id] = risk_factor
            
            return risk_factors
            
        except Exception as e:
            print(f"❌ Risk faktör analizi hatası: {str(e)}")
            return []
    
    def decompose_portfolio_risk(self, portfolio_returns: pd.Series, asset_weights: Dict[str, float],
                                 asset_returns: Dict[str, pd.Series]) -> PortfolioRisk:
        """
        Portföy riskini ayrıştır
        
        Args:
            portfolio_returns: Portföy getiri serisi
            asset_weights: Varlık ağırlıkları
            asset_returns: Varlık getiri serileri
            
        Returns:
            PortfolioRisk: Portföy riski
        """
        try:
            # Toplam risk
            total_risk = portfolio_returns.std() * np.sqrt(252)
            
            # Sistematik risk (basit yaklaşım)
            systematic_risk = total_risk * 0.7  # Varsayılan %70
            
            # İdiyosinkratik risk
            idiosyncratic_risk = total_risk * 0.3  # Varsayılan %30
            
            # Risk ayrıştırması
            risk_decomposition = {}
            for asset_name, weight in asset_weights.items():
                if asset_name in asset_returns and len(asset_returns[asset_name]) > 0:
                    asset_risk = asset_returns[asset_name].std() * np.sqrt(252)
                    risk_contribution = weight * asset_risk
                    risk_decomposition[asset_name] = risk_contribution
            
            # Konsantrasyon riski
            concentration_risk = sum([weight**2 for weight in asset_weights.values()])
            
            # Sektör riski (basit)
            sector_risk = 0.0
            if len(asset_weights) > 0:
                sector_risk = 1.0 / len(asset_weights)  # Basit çeşitlendirme
            
            # Coğrafi risk (basit)
            geographic_risk = 0.5  # Varsayılan
            
            # Döviz riski (basit)
            currency_risk = 0.3  # Varsayılan
            
            portfolio_risk = PortfolioRisk(
                portfolio_id="portfolio_1",
                timestamp=datetime.now(),
                total_risk=total_risk,
                systematic_risk=systematic_risk,
                idiosyncratic_risk=idiosyncratic_risk,
                risk_decomposition=risk_decomposition,
                concentration_risk=concentration_risk,
                sector_risk=sector_risk,
                geographic_risk=geographic_risk,
                currency_risk=currency_risk
            )
            
            self.portfolio_risks[f"risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}"] = portfolio_risk
            
            return portfolio_risk
            
        except Exception as e:
            print(f"❌ Portföy risk ayrıştırma hatası: {str(e)}")
            return PortfolioRisk(
                portfolio_id="", timestamp=datetime.now(),
                total_risk=0.0, systematic_risk=0.0, idiosyncratic_risk=0.0,
                risk_decomposition={}, concentration_risk=0.0,
                sector_risk=0.0, geographic_risk=0.0, currency_risk=0.0
            )
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Risk özetini al"""
        try:
            summary = {
                'total_risk_metrics': len(self.risk_metrics),
                'total_stress_scenarios': len(self.stress_scenarios),
                'total_risk_factors': len(self.risk_factors),
                'total_portfolio_risks': len(self.portfolio_risks),
                'latest_metrics': None,
                'latest_portfolio_risk': None
            }
            
            # En son metrikler
            if self.risk_metrics:
                latest_metrics = max(self.risk_metrics.values(), key=lambda x: x.timestamp)
                summary['latest_metrics'] = {
                    'var_95': latest_metrics.var_95,
                    'var_99': latest_metrics.var_99,
                    'volatility': latest_metrics.volatility,
                    'sharpe_ratio': latest_metrics.sharpe_ratio
                }
            
            # En son portföy riski
            if self.portfolio_risks:
                latest_risk = max(self.portfolio_risks.values(), key=lambda x: x.timestamp)
                summary['latest_portfolio_risk'] = {
                    'total_risk': latest_risk.total_risk,
                    'systematic_risk': latest_risk.systematic_risk,
                    'concentration_risk': latest_risk.concentration_risk
                }
            
            return summary
            
        except Exception as e:
            print(f"❌ Risk özeti alma hatası: {str(e)}")
            return {'error': str(e)}

# Test fonksiyonu
def test_advanced_risk_analytics():
    """Advanced Risk Analytics test fonksiyonu"""
    print("🧪 Advanced Risk Analytics Test Başlıyor...")
    
    # Advanced Risk Analytics başlat
    ara = AdvancedRiskAnalytics()
    
    # Stres testi senaryoları test
    print("\n🌪️ Stres Testi Senaryoları Test:")
    scenarios = ara.stress_scenarios
    print(f"   ✅ {len(scenarios)} senaryo mevcut")
    for scenario_id, scenario in scenarios.items():
        print(f"     {scenario.name}: {scenario.description}")
        print(f"       📊 Piyasa şoku: {scenario.market_shock}%")
        print(f"       📊 Faiz şoku: {scenario.interest_rate_shock}%")
        print(f"       📊 Döviz şoku: {scenario.currency_shock}%")
    
    # Test verisi oluştur
    print("\n📊 Test Verisi Oluşturma:")
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    # Portföy getirileri
    portfolio_returns = pd.Series(np.random.normal(0.001, 0.02, len(dates)), index=dates)
    
    # Benchmark getirileri
    benchmark_returns = pd.Series(np.random.normal(0.0008, 0.018, len(dates)), index=dates)
    
    # Faktör getirileri
    factor_returns = {
        'market_factor': pd.Series(np.random.normal(0.0005, 0.015, len(dates)), index=dates),
        'interest_rate_factor': pd.Series(np.random.normal(0.0002, 0.008, len(dates)), index=dates),
        'currency_factor': pd.Series(np.random.normal(0.0001, 0.012, len(dates)), index=dates),
        'commodity_factor': pd.Series(np.random.normal(0.0003, 0.025, len(dates)), index=dates)
    }
    
    print(f"   ✅ Test verisi oluşturuldu: {len(portfolio_returns)} gün")
    print(f"   📊 Portföy getiri ortalaması: {portfolio_returns.mean():.6f}")
    print(f"   📊 Portföy getiri std: {portfolio_returns.std():.6f}")
    
    # VaR hesaplama test
    print("\n📊 VaR Hesaplama Test:")
    var_95_hist = ara.calculate_var(portfolio_returns, 0.95, "historical")
    var_99_hist = ara.calculate_var(portfolio_returns, 0.99, "historical")
    var_95_param = ara.calculate_var(portfolio_returns, 0.95, "parametric")
    var_99_param = ara.calculate_var(portfolio_returns, 0.99, "parametric")
    
    print(f"   ✅ Historical VaR 95%: {var_95_hist:.6f}")
    print(f"   ✅ Historical VaR 99%: {var_99_hist:.6f}")
    print(f"   ✅ Parametric VaR 95%: {var_95_param:.6f}")
    print(f"   ✅ Parametric VaR 99%: {var_99_param:.6f}")
    
    # CVaR hesaplama test
    print("\n📊 CVaR Hesaplama Test:")
    cvar_95_hist = ara.calculate_cvar(portfolio_returns, 0.95, "historical")
    cvar_99_hist = ara.calculate_cvar(portfolio_returns, 0.99, "historical")
    cvar_95_param = ara.calculate_cvar(portfolio_returns, 0.95, "parametric")
    
    print(f"   ✅ Historical CVaR 95%: {cvar_95_hist:.6f}")
    print(f"   ✅ Historical CVaR 99%: {cvar_99_hist:.6f}")
    print(f"   ✅ Parametric CVaR 95%: {cvar_95_param:.6f}")
    
    # Portföy risk metrikleri test
    print("\n📊 Portföy Risk Metrikleri Test:")
    risk_metrics = ara.calculate_portfolio_risk_metrics(portfolio_returns, benchmark_returns)
    
    print(f"   ✅ Risk metrikleri hesaplandı")
    print(f"   📊 Volatilite: {risk_metrics.volatility:.4f}")
    print(f"   📊 Beta: {risk_metrics.beta:.4f}")
    print(f"   📊 Sharpe Ratio: {risk_metrics.sharpe_ratio:.4f}")
    print(f"   📊 Max Drawdown: {risk_metrics.max_drawdown:.4f}")
    print(f"   📊 Tracking Error: {risk_metrics.tracking_error:.4f}")
    print(f"   📊 Information Ratio: {risk_metrics.information_ratio:.4f}")
    
    # Stres testi test
    print("\n🌪️ Stres Testi Test:")
    stress_results = ara.run_stress_test(portfolio_returns, "market_crash")
    
    if 'error' not in stress_results:
        print(f"   ✅ Stres testi tamamlandı: {stress_results['scenario_name']}")
        print(f"   📊 VaR 95% değişimi: {stress_results['changes']['var_95_change_pct']:.2f}%")
        print(f"   📊 VaR 99% değişimi: {stress_results['changes']['var_99_change_pct']:.2f}%")
        print(f"   📊 Volatilite değişimi: {stress_results['changes']['volatility_change_pct']:.2f}%")
    else:
        print(f"   ❌ Stres testi hatası: {stress_results['error']}")
    
    # Risk faktör analizi test
    print("\n🔍 Risk Faktör Analizi Test:")
    risk_factors = ara.analyze_risk_factors(portfolio_returns, factor_returns)
    
    print(f"   ✅ {len(risk_factors)} risk faktörü analiz edildi")
    for factor in risk_factors:
        print(f"     {factor.name} ({factor.category}):")
        print(f"       📊 Duyarlılık: {factor.sensitivity:.4f}")
        print(f"       📊 Katkı: {factor.contribution:.6f}")
        print(f"       📊 Volatilite: {factor.volatility:.4f}")
        print(f"       📊 Korelasyon: {factor.correlation:.4f}")
    
    # Portföy risk ayrıştırma test
    print("\n📊 Portföy Risk Ayrıştırma Test:")
    asset_weights = {
        'SISE.IS': 0.3,
        'EREGL.IS': 0.25,
        'TUPRS.IS': 0.2,
        'GARAN.IS': 0.15,
        'AKBNK.IS': 0.1
    }
    
    asset_returns = {
        'SISE.IS': pd.Series(np.random.normal(0.0012, 0.025, len(dates)), index=dates),
        'EREGL.IS': pd.Series(np.random.normal(0.0010, 0.030, len(dates)), index=dates),
        'TUPRS.IS': pd.Series(np.random.normal(0.0008, 0.022, len(dates)), index=dates),
        'GARAN.IS': pd.Series(np.random.normal(0.0009, 0.028, len(dates)), index=dates),
        'AKBNK.IS': pd.Series(np.random.normal(0.0011, 0.035, len(dates)), index=dates)
    }
    
    portfolio_risk = ara.decompose_portfolio_risk(portfolio_returns, asset_weights, asset_returns)
    
    print(f"   ✅ Portföy riski ayrıştırıldı")
    print(f"   📊 Toplam risk: {portfolio_risk.total_risk:.4f}")
    print(f"   📊 Sistematik risk: {portfolio_risk.systematic_risk:.4f}")
    print(f"   📊 İdiyosinkratik risk: {portfolio_risk.idiosyncratic_risk:.4f}")
    print(f"   📊 Konsantrasyon riski: {portfolio_risk.concentration_risk:.4f}")
    print(f"   📊 Sektör riski: {portfolio_risk.sector_risk:.4f}")
    
    # Risk ayrıştırması
    print(f"   📊 Risk ayrıştırması:")
    for asset, risk_contrib in portfolio_risk.risk_decomposition.items():
        print(f"     {asset}: {risk_contrib:.6f}")
    
    # Risk özeti test
    print("\n📊 Risk Özeti Test:")
    risk_summary = ara.get_risk_summary()
    
    if 'error' not in risk_summary:
        print(f"   ✅ Risk özeti alındı")
        print(f"   📊 Toplam risk metrikleri: {risk_summary['total_risk_metrics']}")
        print(f"   📊 Toplam stres senaryoları: {risk_summary['total_stress_scenarios']}")
        print(f"   📊 Toplam risk faktörleri: {risk_summary['total_risk_factors']}")
        print(f"   📊 Toplam portföy riskleri: {risk_summary['total_portfolio_risks']}")
        
        if risk_summary['latest_metrics']:
            print(f"   📊 En son metrikler:")
            for key, value in risk_summary['latest_metrics'].items():
                print(f"     {key}: {value:.6f}")
        
        if risk_summary['latest_portfolio_risk']:
            print(f"   📊 En son portföy riski:")
            for key, value in risk_summary['latest_portfolio_risk'].items():
                print(f"     {key}: {value:.6f}")
    
    print("\n✅ Advanced Risk Analytics Test Tamamlandı!")
    
    return ara

if __name__ == "__main__":
    test_advanced_risk_analytics()
