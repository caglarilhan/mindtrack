"""
Stress Testing Engine - Sprint 13: Advanced Risk Management & Compliance Engine

Bu modül, çeşitli stres testi senaryolarını yönetir, portföy stres testi yapar
ve aşırı piyasa koşulları altında risk analizi gerçekleştirir.
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

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StressScenario:
    """Stres testi senaryosu"""
    scenario_id: str
    name: str
    description: str
    category: str  # market, credit, liquidity, operational
    severity: str  # low, medium, high, extreme
    probability: float  # Senaryo olasılığı (0-1)
    time_horizon: int  # Gün cinsinden zaman ufku
    market_shocks: Dict[str, float]  # Piyasa şokları
    correlation_breaks: List[str]  # Korelasyon kırılımları
    volatility_multiplier: float  # Volatilite çarpanı
    created_at: datetime = None

@dataclass
class StressTestResult:
    """Stres testi sonucu"""
    test_id: str
    scenario_id: str
    portfolio_id: str
    test_date: datetime
    initial_value: float
    stressed_value: float
    value_change: float
    value_change_pct: float
    risk_metrics: Dict[str, float]
    stress_impact: Dict[str, float]
    worst_case_loss: float
    recovery_time_days: Optional[int] = None
    confidence_level: float = 0.95

@dataclass
class MarketShock:
    """Piyasa şoku"""
    shock_id: str
    asset_class: str
    shock_type: str  # price, volatility, correlation, liquidity
    magnitude: float  # Şok büyüklüğü
    direction: str  # positive, negative
    duration_days: int  # Şok süresi
    recovery_pattern: str  # immediate, gradual, permanent

@dataclass
class PortfolioStressData:
    """Portföy stres test verisi"""
    portfolio_id: str
    timestamp: datetime
    asset_allocations: Dict[str, float]
    risk_metrics: Dict[str, float]
    market_data: Dict[str, Any]
    stress_factors: Dict[str, float]

class StressTestingEngine:
    """Stress Testing Engine ana sınıfı"""
    
    def __init__(self):
        self.stress_scenarios = {}
        self.stress_test_results = {}
        self.market_shocks = {}
        self.portfolio_stress_data = {}
        self.scenario_templates = {}
        self.stress_models = {}
        
        # Varsayılan stres testi senaryoları
        self._add_default_scenarios()
        
        # Varsayılan piyasa şokları
        self._add_default_market_shocks()
        
        # Varsayılan stres testi modelleri
        self._add_default_stress_models()
    
    def _add_default_scenarios(self):
        """Varsayılan stres testi senaryoları ekle"""
        default_scenarios = [
            {
                "scenario_id": "MARKET_CRASH_2008",
                "name": "2008 Piyasa Çöküşü",
                "description": "2008 finansal krizi benzeri piyasa çöküşü",
                "category": "market",
                "severity": "extreme",
                "probability": 0.01,
                "time_horizon": 30,
                "market_shocks": {
                    "equity": -0.40,
                    "bonds": -0.15,
                    "commodities": -0.30,
                    "currencies": -0.20,
                    "real_estate": -0.35
                },
                "correlation_breaks": ["equity-bonds", "equity-commodities"],
                "volatility_multiplier": 3.0
            },
            {
                "scenario_id": "INTEREST_RATE_SPIKE",
                "name": "Faiz Oranı Artışı",
                "description": "Ani ve büyük faiz oranı artışı",
                "category": "credit",
                "severity": "high",
                "probability": 0.05,
                "time_horizon": 14,
                "market_shocks": {
                    "bonds": -0.25,
                    "equity": -0.20,
                    "real_estate": -0.15,
                    "currencies": -0.10
                },
                "correlation_breaks": ["bonds-equity"],
                "volatility_multiplier": 2.5
            },
            {
                "scenario_id": "LIQUIDITY_CRISIS",
                "name": "Likidite Krizi",
                "description": "Piyasa likiditesinin kuruması",
                "category": "liquidity",
                "severity": "high",
                "probability": 0.03,
                "time_horizon": 21,
                "market_shocks": {
                    "equity": -0.25,
                    "bonds": -0.20,
                    "commodities": -0.30,
                    "currencies": -0.15
                },
                "correlation_breaks": ["equity-bonds", "equity-commodities"],
                "volatility_multiplier": 2.0
            },
            {
                "scenario_id": "CURRENCY_CRISIS",
                "name": "Döviz Krizleri",
                "description": "Büyük döviz kuru hareketleri",
                "category": "market",
                "severity": "medium",
                "probability": 0.08,
                "time_horizon": 7,
                "market_shocks": {
                    "currencies": -0.35,
                    "equity": -0.15,
                    "bonds": -0.10,
                    "commodities": -0.20
                },
                "correlation_breaks": ["currencies-equity"],
                "volatility_multiplier": 2.5
            },
            {
                "scenario_id": "COMMODITY_SHOCK",
                "name": "Emtia Şoku",
                "description": "Petrol ve emtia fiyat şokları",
                "category": "market",
                "severity": "medium",
                "probability": 0.10,
                "time_horizon": 14,
                "market_shocks": {
                    "commodities": -0.40,
                    "equity": -0.10,
                    "bonds": -0.05,
                    "currencies": -0.08
                },
                "correlation_breaks": ["commodities-equity"],
                "volatility_multiplier": 2.0
            }
        ]
        
        for scenario_data in default_scenarios:
            scenario = StressScenario(
                scenario_id=scenario_data["scenario_id"],
                name=scenario_data["name"],
                description=scenario_data["description"],
                category=scenario_data["category"],
                severity=scenario_data["severity"],
                probability=scenario_data["probability"],
                time_horizon=scenario_data["time_horizon"],
                market_shocks=scenario_data["market_shocks"],
                correlation_breaks=scenario_data["correlation_breaks"],
                volatility_multiplier=scenario_data["volatility_multiplier"],
                created_at=datetime.now()
            )
            self.stress_scenarios[scenario.scenario_id] = scenario
    
    def _add_default_market_shocks(self):
        """Varsayılan piyasa şokları ekle"""
        default_shocks = [
            {
                "shock_id": "EQUITY_CRASH",
                "asset_class": "equity",
                "shock_type": "price",
                "magnitude": 0.30,
                "direction": "negative",
                "duration_days": 5,
                "recovery_pattern": "gradual"
            },
            {
                "shock_id": "BOND_SELLOFF",
                "asset_class": "bonds",
                "shock_type": "price",
                "magnitude": 0.15,
                "direction": "negative",
                "duration_days": 10,
                "recovery_pattern": "gradual"
            },
            {
                "shock_id": "VOLATILITY_SPIKE",
                "asset_class": "all",
                "shock_type": "volatility",
                "magnitude": 2.5,
                "direction": "positive",
                "duration_days": 7,
                "recovery_pattern": "immediate"
            },
            {
                "shock_id": "LIQUIDITY_DRAIN",
                "asset_class": "all",
                "shock_type": "liquidity",
                "magnitude": 0.50,
                "direction": "negative",
                "duration_days": 14,
                "recovery_pattern": "gradual"
            }
        ]
        
        for shock_data in default_shocks:
            shock = MarketShock(
                shock_id=shock_data["shock_id"],
                asset_class=shock_data["asset_class"],
                shock_type=shock_data["shock_type"],
                magnitude=shock_data["magnitude"],
                direction=shock_data["direction"],
                duration_days=shock_data["duration_days"],
                recovery_pattern=shock_data["recovery_pattern"]
            )
            self.market_shocks[shock.shock_id] = shock
    
    def _add_default_stress_models(self):
        """Varsayılan stres testi modelleri ekle"""
        self.stress_models = {
            "historical_simulation": {
                "description": "Tarihsel simülasyon tabanlı stres testi",
                "parameters": {
                    "lookback_period": 252,  # 1 yıl
                    "confidence_level": 0.95,
                    "monte_carlo_sims": 10000
                }
            },
            "monte_carlo": {
                "description": "Monte Carlo simülasyonu",
                "parameters": {
                    "simulations": 10000,
                    "time_steps": 30,
                    "confidence_level": 0.95
                }
            },
            "scenario_analysis": {
                "description": "Senaryo analizi",
                "parameters": {
                    "scenario_count": 1000,
                    "correlation_breaks": True,
                    "volatility_adjustment": True
                }
            },
            "extreme_value_theory": {
                "description": "Aşırı değer teorisi",
                "parameters": {
                    "threshold_percentile": 0.95,
                    "tail_estimation": "gpd",
                    "confidence_level": 0.90
                }
            }
        }
    
    def add_stress_scenario(self, scenario: StressScenario) -> bool:
        """Yeni stres testi senaryosu ekle"""
        try:
            self.stress_scenarios[scenario.scenario_id] = scenario
            logger.info(f"Stress scenario added: {scenario.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding stress scenario: {e}")
            return False
    
    def run_stress_test(self, portfolio_data: PortfolioStressData, scenario_id: str) -> StressTestResult:
        """Stres testi çalıştır"""
        try:
            if scenario_id not in self.stress_scenarios:
                logger.error(f"Scenario {scenario_id} not found")
                return None
            
            scenario = self.stress_scenarios[scenario_id]
            
            # Test ID oluştur
            test_id = f"STRESS_{scenario_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Başlangıç portföy değeri
            initial_value = self._calculate_portfolio_value(portfolio_data)
            
            # Stres testi uygula
            stressed_data = self._apply_stress_scenario(portfolio_data, scenario)
            
            # Stres altında portföy değeri
            stressed_value = self._calculate_portfolio_value(stressed_data)
            
            # Değer değişimi
            value_change = stressed_value - initial_value
            value_change_pct = (value_change / initial_value) * 100 if initial_value > 0 else 0
            
            # Risk metrikleri hesapla
            risk_metrics = self._calculate_stress_risk_metrics(stressed_data, scenario)
            
            # Stres etkisi analizi
            stress_impact = self._analyze_stress_impact(portfolio_data, stressed_data, scenario)
            
            # En kötü durum kaybı
            worst_case_loss = self._calculate_worst_case_loss(portfolio_data, scenario)
            
            # Toparlanma süresi tahmini
            recovery_time = self._estimate_recovery_time(value_change_pct, scenario)
            
            result = StressTestResult(
                test_id=test_id,
                scenario_id=scenario_id,
                portfolio_id=portfolio_data.portfolio_id,
                test_date=datetime.now(),
                initial_value=initial_value,
                stressed_value=stressed_value,
                value_change=value_change,
                value_change_pct=value_change_pct,
                risk_metrics=risk_metrics,
                stress_impact=stress_impact,
                worst_case_loss=worst_case_loss,
                recovery_time_days=recovery_time,
                confidence_level=0.95
            )
            
            self.stress_test_results[test_id] = result
            logger.info(f"Stress test completed: {test_id}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error running stress test: {e}")
            return None
    
    def _calculate_portfolio_value(self, portfolio_data: PortfolioStressData) -> float:
        """Portföy değeri hesapla"""
        try:
            total_value = 0.0
            
            # Asset allocation'lardan portföy değeri hesapla
            for asset_class, allocation in portfolio_data.asset_allocations.items():
                if asset_class in portfolio_data.market_data:
                    market_value = portfolio_data.market_data[asset_class].get("value", 0)
                    total_value += market_value * allocation
            
            return total_value
        
        except Exception as e:
            logger.error(f"Error calculating portfolio value: {e}")
            return 0.0
    
    def _apply_stress_scenario(self, portfolio_data: PortfolioStressData, scenario: StressScenario) -> PortfolioStressData:
        """Stres senaryosunu portföye uygula"""
        try:
            # Portföy verisini kopyala
            stressed_data = PortfolioStressData(
                portfolio_id=portfolio_data.portfolio_id,
                timestamp=portfolio_data.timestamp,
                asset_allocations=portfolio_data.asset_allocations.copy(),
                risk_metrics=portfolio_data.risk_metrics.copy(),
                market_data=portfolio_data.market_data.copy(),
                stress_factors=portfolio_data.stress_factors.copy()
            )
            
            # Market şoklarını uygula
            for asset_class, shock_magnitude in scenario.market_shocks.items():
                if asset_class in stressed_data.market_data:
                    current_value = stressed_data.market_data[asset_class].get("value", 0)
                    stressed_value = current_value * (1 + shock_magnitude)
                    stressed_data.market_data[asset_class]["value"] = stressed_value
                    
                    # Volatilite çarpanını uygula
                    if "volatility" in stressed_data.market_data[asset_class]:
                        current_vol = stressed_data.market_data[asset_class]["volatility"]
                        stressed_vol = current_vol * scenario.volatility_multiplier
                        stressed_data.market_data[asset_class]["volatility"] = stressed_vol
            
            # Korelasyon kırılımlarını uygula
            for correlation_break in scenario.correlation_breaks:
                if "-" in correlation_break:
                    asset1, asset2 = correlation_break.split("-")
                    if asset1 in stressed_data.stress_factors and asset2 in stressed_data.stress_factors:
                        # Korelasyonu sıfırla veya tersine çevir
                        stressed_data.stress_factors[f"{asset1}_{asset2}_correlation"] = 0.0
            
            return stressed_data
        
        except Exception as e:
            logger.error(f"Error applying stress scenario: {e}")
            return portfolio_data
    
    def _calculate_stress_risk_metrics(self, stressed_data: PortfolioStressData, scenario: StressScenario) -> Dict[str, float]:
        """Stres altında risk metrikleri hesapla"""
        try:
            risk_metrics = {}
            
            # Volatilite hesapla
            total_volatility = 0.0
            for asset_class, allocation in stressed_data.asset_allocations.items():
                if asset_class in stressed_data.market_data:
                    vol = stressed_data.market_data[asset_class].get("volatility", 0)
                    total_volatility += (vol * allocation) ** 2
            
            risk_metrics["stressed_volatility"] = np.sqrt(total_volatility)
            
            # VaR hesapla (basit yaklaşım)
            portfolio_value = self._calculate_portfolio_value(stressed_data)
            var_95 = portfolio_value * risk_metrics["stressed_volatility"] * 1.645
            var_99 = portfolio_value * risk_metrics["stressed_volatility"] * 2.326
            
            risk_metrics["var_95"] = abs(var_95)
            risk_metrics["var_99"] = abs(var_99)
            
            # Beta hesapla
            if "market_return" in stressed_data.market_data:
                market_return = stressed_data.market_data["market_return"]
                portfolio_return = stressed_data.market_data.get("portfolio_return", 0)
                risk_metrics["stressed_beta"] = portfolio_return / market_return if market_return != 0 else 1.0
            
            # Sharpe ratio hesapla
            risk_free_rate = 0.15  # %15
            expected_return = stressed_data.market_data.get("expected_return", 0)
            risk_metrics["stressed_sharpe"] = (expected_return - risk_free_rate) / risk_metrics["stressed_volatility"] if risk_metrics["stressed_volatility"] > 0 else 0
            
            return risk_metrics
        
        except Exception as e:
            logger.error(f"Error calculating stress risk metrics: {e}")
            return {}
    
    def _analyze_stress_impact(self, original_data: PortfolioStressData, stressed_data: PortfolioStressData, scenario: StressScenario) -> Dict[str, float]:
        """Stres etkisini analiz et"""
        try:
            impact_analysis = {}
            
            # Portföy değeri etkisi
            original_value = self._calculate_portfolio_value(original_data)
            stressed_value = self._calculate_portfolio_value(stressed_data)
            impact_analysis["portfolio_value_impact"] = (stressed_value - original_value) / original_value * 100
            
            # Asset class bazında etki
            for asset_class in original_data.asset_allocations:
                if asset_class in original_data.market_data and asset_class in stressed_data.market_data:
                    original_asset_value = original_data.market_data[asset_class].get("value", 0)
                    stressed_asset_value = stressed_data.market_data[asset_class].get("value", 0)
                    
                    if original_asset_value > 0:
                        asset_impact = (stressed_asset_value - original_asset_value) / original_asset_value * 100
                        impact_analysis[f"{asset_class}_impact"] = asset_impact
            
            # Risk metrikleri etkisi
            for metric in original_data.risk_metrics:
                if metric in stressed_data.risk_metrics:
                    original_value = original_data.risk_metrics[metric]
                    stressed_value = stressed_data.risk_metrics[metric]
                    
                    if original_value != 0:
                        metric_impact = (stressed_value - original_value) / abs(original_value) * 100
                        impact_analysis[f"{metric}_impact"] = metric_impact
            
            return impact_analysis
        
        except Exception as e:
            logger.error(f"Error analyzing stress impact: {e}")
            return {}
    
    def _calculate_worst_case_loss(self, portfolio_data: PortfolioStressData, scenario: StressScenario) -> float:
        """En kötü durum kaybını hesapla"""
        try:
            portfolio_value = self._calculate_portfolio_value(portfolio_data)
            
            # Senaryo olasılığına göre ağırlıklı kayıp
            worst_case_loss = 0.0
            
            for asset_class, shock_magnitude in scenario.market_shocks.items():
                if asset_class in portfolio_data.asset_allocations:
                    allocation = portfolio_data.asset_allocations[asset_class]
                    asset_loss = portfolio_value * allocation * abs(shock_magnitude)
                    worst_case_loss += asset_loss
            
            # Volatilite etkisi
            volatility_impact = portfolio_value * 0.1 * scenario.volatility_multiplier
            worst_case_loss += volatility_impact
            
            return worst_case_loss
        
        except Exception as e:
            logger.error(f"Error calculating worst case loss: {e}")
            return 0.0
    
    def _estimate_recovery_time(self, value_change_pct: float, scenario: StressScenario) -> Optional[int]:
        """Toparlanma süresini tahmin et"""
        try:
            if value_change_pct >= 0:
                return 0  # Kayıp yok
            
            # Basit toparlanma süresi tahmini
            severity_multiplier = {
                "low": 1,
                "medium": 2,
                "high": 3,
                "extreme": 5
            }
            
            base_recovery_time = abs(value_change_pct) / 10  # %10 günlük toparlanma
            severity_factor = severity_multiplier.get(scenario.severity, 2)
            
            recovery_time = int(base_recovery_time * severity_factor)
            
            return max(1, min(recovery_time, 365))  # 1-365 gün arası
        
        except Exception as e:
            logger.error(f"Error estimating recovery time: {e}")
            return None
    
    def run_monte_carlo_stress_test(self, portfolio_data: PortfolioStressData, scenario_id: str, num_simulations: int = 1000) -> List[StressTestResult]:
        """Monte Carlo stres testi çalıştır"""
        try:
            if scenario_id not in self.stress_scenarios:
                logger.error(f"Scenario {scenario_id} not found")
                return []
            
            scenario = self.stress_scenarios[scenario_id]
            results = []
            
            for i in range(num_simulations):
                # Rastgele şok varyasyonları oluştur
                modified_scenario = self._create_random_scenario_variation(scenario)
                
                # Stres testi çalıştır
                result = self.run_stress_test(portfolio_data, modified_scenario.scenario_id)
                if result:
                    results.append(result)
            
            logger.info(f"Monte Carlo stress test completed: {len(results)} simulations")
            return results
        
        except Exception as e:
            logger.error(f"Error running Monte Carlo stress test: {e}")
            return []
    
    def _create_random_scenario_variation(self, base_scenario: StressScenario) -> StressScenario:
        """Rastgele senaryo varyasyonu oluştur"""
        try:
            # Market şoklarına rastgele varyasyon ekle
            modified_shocks = {}
            for asset_class, base_shock in base_scenario.market_shocks.items():
                # ±20% rastgele varyasyon
                variation = random.uniform(-0.2, 0.2)
                modified_shock = base_shock * (1 + variation)
                modified_shocks[asset_class] = modified_shock
            
            # Volatilite çarpanına rastgele varyasyon ekle
            vol_variation = random.uniform(-0.3, 0.3)
            modified_vol_multiplier = base_scenario.volatility_multiplier * (1 + vol_variation)
            
            variation_id = f"{base_scenario.scenario_id}_VAR_{random.randint(1000, 9999)}"
            
            modified_scenario = StressScenario(
                scenario_id=variation_id,
                name=f"{base_scenario.name} (Variation)",
                description=f"Random variation of {base_scenario.name}",
                category=base_scenario.category,
                severity=base_scenario.severity,
                probability=base_scenario.probability,
                time_horizon=base_scenario.time_horizon,
                market_shocks=modified_shocks,
                correlation_breaks=base_scenario.correlation_breaks,
                volatility_multiplier=modified_vol_multiplier,
                created_at=datetime.now()
            )
            
            return modified_scenario
        
        except Exception as e:
            logger.error(f"Error creating random scenario variation: {e}")
            return base_scenario
    
    def get_stress_test_summary(self) -> Dict[str, Any]:
        """Stres testi özeti getir"""
        try:
            total_tests = len(self.stress_test_results)
            total_scenarios = len(self.stress_scenarios)
            
            # Senaryo kategorilerine göre dağılım
            category_counts = {}
            severity_counts = {}
            
            for scenario in self.stress_scenarios.values():
                category = scenario.category
                severity = scenario.severity
                
                category_counts[category] = category_counts.get(category, 0) + 1
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Test sonuçları analizi
            if self.stress_test_results:
                avg_value_change = np.mean([r.value_change_pct for r in self.stress_test_results.values()])
                max_loss = min([r.value_change_pct for r in self.stress_test_results.values()])
                avg_recovery_time = np.mean([r.recovery_time_days for r in self.stress_test_results.values() if r.recovery_time_days])
            else:
                avg_value_change = 0
                max_loss = 0
                avg_recovery_time = 0
            
            summary = {
                "total_scenarios": total_scenarios,
                "total_tests": total_tests,
                "category_distribution": category_counts,
                "severity_distribution": severity_counts,
                "test_results_summary": {
                    "average_value_change_pct": avg_value_change,
                    "maximum_loss_pct": max_loss,
                    "average_recovery_time_days": avg_recovery_time
                },
                "last_test_date": None,
                "most_severe_scenario": None
            }
            
            if self.stress_test_results:
                summary["last_test_date"] = max(r.test_date for r in self.stress_test_results.values()).isoformat()
            
            if self.stress_scenarios:
                most_severe = max(self.stress_scenarios.values(), key=lambda x: x.probability)
                summary["most_severe_scenario"] = most_severe.name
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting stress test summary: {e}")
            return {}


def test_stress_testing_engine():
    """Stress Testing Engine test fonksiyonu"""
    print("\n🧪 Stress Testing Engine Test Başlıyor...")
    
    # Stress Testing Engine oluştur
    engine = StressTestingEngine()
    
    print("✅ Varsayılan stres testi senaryoları eklendi")
    print(f"📊 Toplam senaryo sayısı: {len(engine.stress_scenarios)}")
    
    # Test portföy verisi oluştur
    print("\n📊 Test Portföy Verisi Oluşturma:")
    test_portfolio = PortfolioStressData(
        portfolio_id="TEST_PORTFOLIO_001",
        timestamp=datetime.now(),
        asset_allocations={
            "equity": 0.60,
            "bonds": 0.25,
            "commodities": 0.10,
            "currencies": 0.05
        },
        risk_metrics={
            "volatility": 0.15,
            "var_95": 0.025,
            "beta": 0.8,
            "sharpe_ratio": 1.2
        },
        market_data={
            "equity": {"value": 60000, "volatility": 0.20},
            "bonds": {"value": 25000, "volatility": 0.08},
            "commodities": {"value": 10000, "volatility": 0.25},
            "currencies": {"value": 5000, "volatility": 0.12},
            "market_return": 0.10,
            "portfolio_return": 0.08,
            "expected_return": 0.12
        },
        stress_factors={
            "equity_bonds_correlation": 0.3,
            "equity_commodities_correlation": 0.2
        }
    )
    
    print(f"   ✅ Test portföyü oluşturuldu: {test_portfolio.portfolio_id}")
    print(f"   📊 Toplam varlık: 4 sınıf")
    print(f"   📊 Başlangıç volatilite: {test_portfolio.risk_metrics['volatility']:.2%}")
    
    # Stres testi çalıştır
    print("\n📊 Stres Testi Çalıştırma:")
    scenario_id = "MARKET_CRASH_2008"
    result = engine.run_stress_test(test_portfolio, scenario_id)
    
    if result:
        print(f"   ✅ Stres testi tamamlandı: {result.test_id}")
        print(f"   📊 Başlangıç değer: {result.initial_value:,.0f} TL")
        print(f"   📊 Stres altında değer: {result.stressed_value:,.0f} TL")
        print(f"   📊 Değer değişimi: {result.value_change:,.0f} TL ({result.value_change_pct:.2f}%)")
        print(f"   📊 En kötü durum kaybı: {result.worst_case_loss:,.0f} TL")
        print(f"   📊 Tahmini toparlanma: {result.recovery_time_days} gün")
        
        # Risk metrikleri
        print(f"   📊 Stres altında VaR 95%: {result.risk_metrics.get('var_95', 0):,.0f} TL")
        print(f"   📊 Stres altında volatilite: {result.risk_metrics.get('stressed_volatility', 0):.2%}")
    
    # Monte Carlo stres testi
    print("\n📊 Monte Carlo Stres Testi:")
    mc_results = engine.run_monte_carlo_stress_test(test_portfolio, scenario_id, num_simulations=100)
    
    if mc_results:
        print(f"   ✅ Monte Carlo testi tamamlandı: {len(mc_results)} simülasyon")
        
        # Sonuç analizi
        value_changes = [r.value_change_pct for r in mc_results]
        avg_change = np.mean(value_changes)
        min_change = min(value_changes)
        max_change = max(value_changes)
        
        print(f"   📊 Ortalama değer değişimi: {avg_change:.2f}%")
        print(f"   📊 Minimum değer değişimi: {min_change:.2f}%")
        print(f"   📊 Maksimum değer değişimi: {max_change:.2f}%")
    
    # Stres testi özeti
    print("\n📊 Stres Testi Özeti:")
    summary = engine.get_stress_test_summary()
    print(f"   ✅ Stres testi özeti alındı")
    print(f"   📊 Toplam senaryo: {summary['total_scenarios']}")
    print(f"   📊 Toplam test: {summary['total_tests']}")
    print(f"   📊 Kategori dağılımı: {summary['category_distribution']}")
    print(f"   📊 Şiddet dağılımı: {summary['severity_distribution']}")
    
    if summary['test_results_summary']:
        print(f"   📊 Ortalama değer değişimi: {summary['test_results_summary']['average_value_change_pct']:.2f}%")
        print(f"   📊 Maksimum kayıp: {summary['test_results_summary']['maximum_loss_pct']:.2f}%")
        print(f"   📊 Ortalama toparlanma süresi: {summary['test_results_summary']['average_recovery_time_days']:.1f} gün")
    
    print("\n✅ Stress Testing Engine Test Tamamlandı!")


if __name__ == "__main__":
    test_stress_testing_engine()
