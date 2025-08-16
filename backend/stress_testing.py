"""
PRD v2.0 - BIST AI Smart Trader
Stress Testing Module

Portföy stres testi modülü:
- Scenario-based testing
- Historical stress tests
- Monte Carlo stress tests
- Regime change detection
- Recovery analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from scipy import stats
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

@dataclass
class StressTestResult:
    """Stres testi sonucu"""
    scenario_name: str
    portfolio_return: float
    portfolio_volatility: float
    var_95: float
    var_99: float
    max_drawdown: float
    recovery_time: Optional[int] = None
    additional_metrics: Dict = None

@dataclass
class RegimeChange:
    """Rejim değişimi tespiti"""
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    regime_type: str
    severity: float
    description: str

class StressTesting:
    """
    Portföy Stres Testi Motoru
    
    PRD v2.0 gereksinimleri:
    - Senaryo tabanlı stres testleri
    - Tarihsel stres testleri
    - Monte Carlo stres testleri
    - Rejim değişimi tespiti
    - Toparlanma analizi
    """
    
    def __init__(self, confidence_level: float = 0.95, 
                 recovery_threshold: float = 0.05):
        """
        Stress Testing başlatıcı
        
        Args:
            confidence_level: Güven seviyesi
            recovery_threshold: Toparlanma eşiği
        """
        self.confidence_level = confidence_level
        self.recovery_threshold = recovery_threshold
        self.alpha = 1 - confidence_level
        
        # Stres testi sabitleri
        self.SCENARIO_TYPES = ["market_crash", "interest_rate", "sector_crisis", 
                               "volatility_spike", "correlation_breakdown"]
        self.HISTORICAL_CRISES = ["2008_financial", "2020_covid", "2022_inflation"]
        
    def run_scenario_stress_test(self, portfolio_weights: Dict[str, float],
                                asset_returns: pd.DataFrame,
                                scenarios: Optional[Dict[str, Dict]] = None) -> Dict[str, StressTestResult]:
        """
        Senaryo tabanlı stres testi
        
        Args:
            portfolio_weights: Portföy ağırlıkları
            asset_returns: Varlık getiri matrisi
            scenarios: Stres senaryoları
            
        Returns:
            Dict: Stres testi sonuçları
        """
        if scenarios is None:
            # Varsayılan stres senaryoları
            scenarios = {
                "market_crash": {
                    "description": "Piyasa çöküşü",
                    "shock_multiplier": -0.25,
                    "volatility_multiplier": 2.0
                },
                "interest_rate_shock": {
                    "description": "Faiz oranı şoku",
                    "bond_shock": -0.15,
                    "equity_shock": 0.08,
                    "commodity_shock": -0.05
                },
                "sector_crisis": {
                    "description": "Sektör krizi",
                    "finance_shock": -0.35,
                    "tech_shock": -0.20,
                    "energy_shock": -0.15,
                    "other_shock": -0.10
                },
                "volatility_spike": {
                    "description": "Volatilite artışı",
                    "volatility_multiplier": 3.0,
                    "correlation_increase": 0.3
                },
                "correlation_breakdown": {
                    "description": "Korelasyon bozulması",
                    "correlation_shock": -0.4,
                    "volatility_increase": 1.5
                }
            }
        
        results = {}
        
        for scenario_name, scenario in scenarios.items():
            print(f"   🔥 {scenario_name} senaryosu test ediliyor...")
            
            # Senaryo uygula
            shocked_returns = self._apply_scenario_shock(asset_returns, scenario)
            
            # Stres altında portföy getirisi
            portfolio_return_series = self._calculate_portfolio_returns(
                portfolio_weights, shocked_returns
            )
            
            # Risk metrikleri hesapla
            risk_metrics = self._calculate_stress_risk_metrics(portfolio_return_series)
            
            # Toparlanma analizi
            recovery_time = self._calculate_recovery_time(portfolio_return_series)
            
            # Sonuç oluştur
            results[scenario_name] = StressTestResult(
                scenario_name=scenario_name,
                portfolio_return=risk_metrics["annual_return"],
                portfolio_volatility=risk_metrics["volatility"],
                var_95=risk_metrics["var_95"],
                var_99=risk_metrics["var_99"],
                max_drawdown=risk_metrics["max_drawdown"],
                recovery_time=recovery_time,
                additional_metrics={
                    "scenario_description": scenario["description"],
                    "shock_parameters": scenario,
                    "cumulative_return": (1 + portfolio_return_series).prod() - 1
                }
            )
        
        return results
    
    def run_historical_stress_test(self, portfolio_weights: Dict[str, float],
                                  asset_returns: pd.DataFrame,
                                  crisis_periods: Optional[Dict[str, Dict]] = None) -> Dict[str, StressTestResult]:
        """
        Tarihsel stres testi
        
        Args:
            portfolio_weights: Portföy ağırlıkları
            asset_returns: Varlık getiri matrisi
            crisis_periods: Kriz dönemleri
            
        Returns:
            Dict: Tarihsel stres testi sonuçları
        """
        if crisis_periods is None:
            # Varsayılan kriz dönemleri (basit yaklaşım)
            crisis_periods = {
                "2008_financial": {
                    "description": "2008 Finansal Kriz",
                    "start_date": "2008-09-01",
                    "end_date": "2009-03-01",
                    "shock_multiplier": -0.30
                },
                "2020_covid": {
                    "description": "2020 COVID-19 Kriz",
                    "start_date": "2020-02-01",
                    "end_date": "2020-04-01",
                    "shock_multiplier": -0.25
                },
                "2022_inflation": {
                    "description": "2022 Enflasyon Kriz",
                    "start_date": "2022-01-01",
                    "end_date": "2022-06-01",
                    "shock_multiplier": -0.20
                }
            }
        
        results = {}
        
        for crisis_name, crisis in crisis_periods.items():
            print(f"   📅 {crisis_name} krizi test ediliyor...")
            
            # Kriz dönemi simülasyonu
            crisis_returns = self._simulate_crisis_period(asset_returns, crisis)
            
            # Kriz altında portföy getirisi
            portfolio_return_series = self._calculate_portfolio_returns(
                portfolio_weights, crisis_returns
            )
            
            # Risk metrikleri hesapla
            risk_metrics = self._calculate_stress_risk_metrics(portfolio_return_series)
            
            # Toparlanma analizi
            recovery_time = self._calculate_recovery_time(portfolio_return_series)
            
            # Sonuç oluştur
            results[crisis_name] = StressTestResult(
                scenario_name=crisis_name,
                portfolio_return=risk_metrics["annual_return"],
                portfolio_volatility=risk_metrics["volatility"],
                var_95=risk_metrics["var_95"],
                var_99=risk_metrics["var_99"],
                max_drawdown=risk_metrics["max_drawdown"],
                recovery_time=recovery_time,
                additional_metrics={
                    "crisis_description": crisis["description"],
                    "crisis_period": f"{crisis['start_date']} - {crisis['end_date']}",
                    "cumulative_return": (1 + portfolio_return_series).prod() - 1
                }
            )
        
        return results
    
    def run_monte_carlo_stress_test(self, portfolio_weights: Dict[str, float],
                                   asset_returns: pd.DataFrame,
                                   n_simulations: int = 10000,
                                   stress_intensity: float = 2.0) -> Dict[str, float]:
        """
        Monte Carlo stres testi
        
        Args:
            portfolio_weights: Portföy ağırlıkları
            asset_returns: Varlık getiri matrisi
            n_simulations: Simülasyon sayısı
            stress_intensity: Stres yoğunluğu
            
        Returns:
            Dict: Monte Carlo stres testi sonuçları
        """
        print(f"   🎲 Monte Carlo stres testi ({n_simulations} simülasyon)...")
        
        # Varlık getiri parametreleri
        mean_returns = asset_returns.mean()
        std_returns = asset_returns.std()
        corr_matrix = asset_returns.corr()
        
        # Monte Carlo simülasyonu
        stress_results = []
        
        for sim in range(n_simulations):
            # Stres altında getiri simülasyonu
            stressed_returns = self._simulate_stressed_returns(
                mean_returns, std_returns, corr_matrix, stress_intensity
            )
            
            # Portföy getirisi hesapla
            portfolio_return = sum(
                weight * stressed_returns[asset] 
                for asset, weight in portfolio_weights.items()
            )
            
            stress_results.append(portfolio_return)
        
        # Sonuçları analiz et
        stress_results = np.array(stress_results)
        
        return {
            "mean_return": stress_results.mean(),
            "std_return": stress_results.std(),
            "var_95": np.percentile(stress_results, 5),
            "var_99": np.percentile(stress_results, 1),
            "cvar_95": stress_results[stress_results <= np.percentile(stress_results, 5)].mean(),
            "max_loss": stress_results.min(),
            "stress_intensity": stress_intensity,
            "n_simulations": n_simulations
        }
    
    def detect_regime_changes(self, portfolio_returns: pd.Series,
                             window_size: int = 63,
                             volatility_threshold: float = 2.0,
                             correlation_threshold: float = 0.1) -> List[RegimeChange]:
        """
        Rejim değişimi tespiti
        
        Args:
            portfolio_returns: Portföy getiri serisi
            window_size: Rolling window boyutu
            volatility_threshold: Volatilite eşiği
            correlation_threshold: Korelasyon eşiği
            
        Returns:
            List[RegimeChange]: Tespit edilen rejim değişimleri
        """
        print("   🔍 Rejim değişimi tespit ediliyor...")
        
        regime_changes = []
        
        # Rolling volatilite hesapla
        rolling_vol = portfolio_returns.rolling(window=window_size).std()
        
        # Volatilite değişimi tespit et
        vol_change = rolling_vol.pct_change()
        high_vol_periods = vol_change > volatility_threshold
        
        # Rejim değişimi noktalarını bul
        regime_start = None
        current_regime = "normal"
        
        for date, is_high_vol in high_vol_periods.items():
            if pd.isna(is_high_vol):
                continue
                
            if is_high_vol and current_regime == "normal":
                # Yüksek volatilite rejimi başladı
                regime_start = date
                current_regime = "high_volatility"
                
            elif not is_high_vol and current_regime == "high_volatility":
                # Yüksek volatilite rejimi bitti
                if regime_start is not None:
                    regime_changes.append(RegimeChange(
                        start_date=regime_start,
                        end_date=date,
                        regime_type="high_volatility",
                        severity=rolling_vol.loc[regime_start:date].max(),
                        description=f"Yüksek volatilite dönemi: {regime_start.date()} - {date.date()}"
                    ))
                current_regime = "normal"
                regime_start = None
        
        # Açık rejim varsa kapat
        if current_regime == "high_volatility" and regime_start is not None:
            regime_changes.append(RegimeChange(
                start_date=regime_start,
                end_date=portfolio_returns.index[-1],
                regime_type="high_volatility",
                severity=rolling_vol.loc[regime_start:].max(),
                description=f"Açık yüksek volatilite dönemi: {regime_start.date()}"
            ))
        
        return regime_changes
    
    def calculate_recovery_metrics(self, portfolio_returns: pd.Series,
                                  stress_periods: List[RegimeChange]) -> Dict[str, Dict]:
        """
        Toparlanma metrikleri hesaplama
        
        Args:
            portfolio_returns: Portföy getiri serisi
            stress_periods: Stres dönemleri
            
        Returns:
            Dict: Toparlanma metrikleri
        """
        print("   📈 Toparlanma metrikleri hesaplanıyor...")
        
        recovery_metrics = {}
        
        for period in stress_periods:
            # Stres dönemi öncesi portföy değeri
            pre_stress_date = period.start_date - pd.Timedelta(days=1)
            if pre_stress_date in portfolio_returns.index:
                pre_stress_value = (1 + portfolio_returns.loc[:pre_stress_date]).prod()
            else:
                pre_stress_value = 1.0
            
            # Stres dönemi sonunda portföy değeri
            stress_end_value = (1 + portfolio_returns.loc[:period.end_date]).prod()
            
            # Toparlanma dönemi analizi
            recovery_period = portfolio_returns.loc[period.end_date:]
            recovery_metrics[period.regime_type] = {
                "stress_period": f"{period.start_date.date()} - {period.end_date.date()}",
                "pre_stress_value": pre_stress_value,
                "stress_end_value": stress_end_value,
                "total_loss": pre_stress_value - stress_end_value,
                "loss_percentage": (pre_stress_value - stress_end_value) / pre_stress_value * 100,
                "recovery_time_days": self._calculate_recovery_time(recovery_period),
                "severity": period.severity,
                "description": period.description
            }
        
        return recovery_metrics
    
    def generate_stress_test_report(self, portfolio_weights: Dict[str, float],
                                  asset_returns: pd.DataFrame,
                                  portfolio_returns: pd.Series) -> Dict:
        """
        Kapsamlı stres testi raporu
        
        Args:
            portfolio_weights: Portföy ağırlıkları
            asset_returns: Varlık getiri matrisi
            portfolio_returns: Portföy getiri serisi
            
        Returns:
            Dict: Stres testi raporu
        """
        print("📊 Stres Testi Raporu Oluşturuluyor...")
        
        # Senaryo tabanlı stres testi
        scenario_results = self.run_scenario_stress_test(portfolio_weights, asset_returns)
        
        # Tarihsel stres testi
        historical_results = self.run_historical_stress_test(portfolio_weights, asset_returns)
        
        # Monte Carlo stres testi
        monte_carlo_results = self.run_monte_carlo_stress_test(portfolio_weights, asset_returns)
        
        # Rejim değişimi tespiti
        regime_changes = self.detect_regime_changes(portfolio_returns)
        
        # Toparlanma metrikleri
        recovery_metrics = self.calculate_recovery_metrics(portfolio_returns, regime_changes)
        
        # Rapor oluştur
        report = {
            "scenario_stress_tests": {
                name: {
                    "portfolio_return": result.portfolio_return,
                    "portfolio_volatility": result.portfolio_volatility,
                    "var_95": result.var_95,
                    "var_99": result.var_99,
                    "max_drawdown": result.max_drawdown,
                    "recovery_time": result.recovery_time,
                    "additional_metrics": result.additional_metrics
                }
                for name, result in scenario_results.items()
            },
            "historical_stress_tests": {
                name: {
                    "portfolio_return": result.portfolio_return,
                    "portfolio_volatility": result.portfolio_volatility,
                    "var_95": result.var_95,
                    "var_99": result.var_99,
                    "max_drawdown": result.max_drawdown,
                    "recovery_time": result.recovery_time,
                    "additional_metrics": result.additional_metrics
                }
                for name, result in historical_results.items()
            },
            "monte_carlo_stress_test": monte_carlo_results,
            "regime_changes": [
                {
                    "start_date": change.start_date.isoformat(),
                    "end_date": change.end_date.isoformat(),
                    "regime_type": change.regime_type,
                    "severity": change.severity,
                    "description": change.description
                }
                for change in regime_changes
            ],
            "recovery_metrics": recovery_metrics,
            "summary": {
                "total_scenarios": len(scenario_results),
                "total_historical_crises": len(historical_results),
                "regime_changes_detected": len(regime_changes),
                "worst_case_scenario": min(scenario_results.keys(), 
                                         key=lambda x: scenario_results[x].portfolio_return),
                "most_severe_regime": max(regime_changes, key=lambda x: x.severity).regime_type if regime_changes else "none"
            }
        }
        
        print("✅ Stres Testi Raporu Tamamlandı!")
        return report
    
    def _apply_scenario_shock(self, asset_returns: pd.DataFrame, scenario: Dict) -> pd.DataFrame:
        """Senaryo şokunu uygula"""
        shocked_returns = asset_returns.copy()
        
        if "shock_multiplier" in scenario:
            # Genel şok
            shocked_returns = shocked_returns * (1 + scenario["shock_multiplier"])
            
        if "volatility_multiplier" in scenario:
            # Volatilite artışı
            shocked_returns = shocked_returns * scenario["volatility_multiplier"]
            
        if "bond_shock" in scenario:
            # Tahvil şoku (ilk 3 varlık)
            for i, asset in enumerate(asset_returns.columns):
                if i < 3:
                    shocked_returns[asset] = asset_returns[asset] * (1 + scenario["bond_shock"])
                    
        if "equity_shock" in scenario:
            # Hisse şoku (4-6. varlıklar)
            for i, asset in enumerate(asset_returns.columns):
                if 3 <= i < 6:
                    shocked_returns[asset] = asset_returns[asset] * (1 + scenario["equity_shock"])
        
        return shocked_returns
    
    def _simulate_crisis_period(self, asset_returns: pd.DataFrame, crisis: Dict) -> pd.DataFrame:
        """Kriz dönemi simülasyonu"""
        # Basit yaklaşım: tüm varlıklara şok uygula
        crisis_returns = asset_returns * (1 + crisis["shock_multiplier"])
        return crisis_returns
    
    def _simulate_stressed_returns(self, mean_returns: pd.Series, std_returns: pd.Series,
                                  corr_matrix: pd.DataFrame, stress_intensity: float) -> pd.Series:
        """Stres altında getiri simülasyonu"""
        # Multivariate normal dağılım ile simülasyon
        stressed_returns = {}
        
        for asset in mean_returns.index:
            # Stres altında parametreler
            stressed_mean = mean_returns[asset] * (1 - stress_intensity * 0.1)
            stressed_std = std_returns[asset] * (1 + stress_intensity * 0.2)
            
            # Getiri simülasyonu
            stressed_returns[asset] = np.random.normal(stressed_mean, stressed_std)
        
        return pd.Series(stressed_returns)
    
    def _calculate_portfolio_returns(self, portfolio_weights: Dict[str, float],
                                   asset_returns: pd.DataFrame) -> pd.Series:
        """Portföy getirisi hesapla"""
        portfolio_returns = pd.Series(0.0, index=asset_returns.index)
        
        for asset, weight in portfolio_weights.items():
            if asset in asset_returns.columns:
                portfolio_returns += weight * asset_returns[asset]
        
        return portfolio_returns
    
    def _calculate_stress_risk_metrics(self, portfolio_returns: pd.Series) -> Dict:
        """Stres altında risk metrikleri"""
        return {
            "annual_return": portfolio_returns.mean() * 252,
            "volatility": portfolio_returns.std() * np.sqrt(252),
            "var_95": abs(np.percentile(portfolio_returns, 5)),
            "var_99": abs(np.percentile(portfolio_returns, 1)),
            "max_drawdown": self._calculate_max_drawdown(portfolio_returns)
        }
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Maksimum drawdown hesapla"""
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        return abs(drawdown.min())
    
    def _calculate_recovery_time(self, returns: pd.Series) -> Optional[int]:
        """Toparlanma süresi hesapla"""
        if len(returns) < 10:
            return None
            
        # Basit yaklaşım: pozitif getiri sayısı
        positive_returns = (returns > 0).sum()
        total_returns = len(returns)
        
        if positive_returns / total_returns > 0.6:
            return positive_returns
        else:
            return None

# Test fonksiyonu
def test_stress_testing():
    """Stress Testing test fonksiyonu"""
    print("🧪 Stress Testing Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    n_days = 252  # 1 yıl
    n_assets = 6
    
    # Farklı varlık türleri için getiri verisi
    returns_data = {}
    asset_names = []
    
    for i in range(n_assets):
        if i < 2:  # Tahvil
            asset_name = f'Bond_{i+1}'
            returns_data[asset_name] = np.random.normal(0.0003, 0.003, n_days)
        elif i < 4:  # Hisse
            asset_name = f'Stock_{i+1}'
            returns_data[asset_name] = np.random.normal(0.0008, 0.015, n_days)
        else:  # Emtia
            asset_name = f'Commodity_{i+1}'
            returns_data[asset_name] = np.random.normal(0.0005, 0.025, n_days)
        
        asset_names.append(asset_name)
    
    asset_returns = pd.DataFrame(returns_data, 
                                index=pd.date_range('2023-01-01', periods=n_days, freq='D'))
    
    # Test portföy ağırlıkları (gerçek varlık isimleriyle)
    portfolio_weights = {}
    for i, asset_name in enumerate(asset_names):
        if i < 2:  # Tahvil
            portfolio_weights[asset_name] = 0.20
        elif i < 4:  # Hisse
            portfolio_weights[asset_name] = 0.25 if i == 2 else 0.20
        else:  # Emtia
            portfolio_weights[asset_name] = 0.10 if i == 4 else 0.05
    
    # Portföy getirisi hesapla
    portfolio_returns = pd.Series(0.0, index=asset_returns.index)
    for asset, weight in portfolio_weights.items():
        portfolio_returns += weight * asset_returns[asset]
    
    # Stress Testing başlat
    stress_tester = StressTesting(confidence_level=0.95, recovery_threshold=0.05)
    
    # Senaryo stres testi
    print("\n🔥 Senaryo Stres Testi:")
    scenario_results = stress_tester.run_scenario_stress_test(portfolio_weights, asset_returns)
    for scenario, result in scenario_results.items():
        print(f"   {scenario}: VaR %95 = {result.var_95:.4f}, "
              f"Getiri = {result.portfolio_return:.4f}")
    
    # Tarihsel stres testi
    print("\n📅 Tarihsel Stres Testi:")
    historical_results = stress_tester.run_historical_stress_test(portfolio_weights, asset_returns)
    for crisis, result in historical_results.items():
        print(f"   {crisis}: VaR %95 = {result.var_95:.4f}, "
              f"Getiri = {result.portfolio_return:.4f}")
    
    # Monte Carlo stres testi
    print("\n🎲 Monte Carlo Stres Testi:")
    mc_results = stress_tester.run_monte_carlo_stress_test(portfolio_weights, asset_returns)
    print(f"   VaR %95: {mc_results['var_95']:.4f}")
    print(f"   VaR %99: {mc_results['var_99']:.4f}")
    print(f"   Maksimum kayıp: {mc_results['max_loss']:.4f}")
    
    # Rejim değişimi tespiti
    print("\n🔍 Rejim Değişimi Tespiti:")
    regime_changes = stress_tester.detect_regime_changes(portfolio_returns)
    print(f"   Tespit edilen rejim değişimi: {len(regime_changes)}")
    
    # Toparlanma metrikleri
    print("\n📈 Toparlanma Metrikleri:")
    recovery_metrics = stress_tester.calculate_recovery_metrics(portfolio_returns, regime_changes)
    for regime, metrics in recovery_metrics.items():
        print(f"   {regime}: Kayıp %{metrics['loss_percentage']:.2f}, "
              f"Toparlanma süresi: {metrics['recovery_time_days']} gün")
    
    # Kapsamlı rapor
    print("\n📋 Kapsamlı Stres Testi Raporu:")
    stress_report = stress_tester.generate_stress_test_report(portfolio_weights, asset_returns, portfolio_returns)
    print(f"   Toplam senaryo: {stress_report['summary']['total_scenarios']}")
    print(f"   Tarihsel kriz: {stress_report['summary']['total_historical_crises']}")
    print(f"   Rejim değişimi: {stress_report['summary']['regime_changes_detected']}")
    print(f"   En kötü senaryo: {stress_report['summary']['worst_case_scenario']}")
    
    print("\n✅ Stress Testing Test Tamamlandı!")
    return stress_tester

if __name__ == "__main__":
    test_stress_testing()
