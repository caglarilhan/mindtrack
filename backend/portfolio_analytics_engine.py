"""
PRD v2.0 - BIST AI Smart Trader
Portfolio Analytics Engine Module

Portföy analiz motoru:
- Portfolio analysis
- Risk metrics
- Performance tracking
- Asset allocation
- Rebalancing strategies
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class PortfolioAsset:
    """Portföy varlığı"""
    symbol: str
    quantity: float
    current_price: float
    purchase_price: float
    purchase_date: datetime
    sector: str = ""
    market_cap: float = 0.0
    weight: float = 0.0

@dataclass
class PortfolioMetrics:
    """Portföy metrikleri"""
    total_value: float
    total_cost: float
    total_return: float
    total_return_pct: float
    daily_return: float
    daily_return_pct: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    beta: float
    alpha: float
    tracking_error: float
    information_ratio: float
    calmar_ratio: float
    sortino_ratio: float
    treynor_ratio: float
    jensen_alpha: float
    timestamp: datetime = None

@dataclass
class RiskMetrics:
    """Risk metrikleri"""
    var_95: float  # Value at Risk 95%
    var_99: float  # Value at Risk 99%
    cvar_95: float  # Conditional VaR 95%
    cvar_99: float  # Conditional VaR 99%
    downside_deviation: float
    semi_variance: float
    skewness: float
    kurtosis: float
    correlation_matrix: pd.DataFrame = None
    covariance_matrix: pd.DataFrame = None
    timestamp: datetime = None

@dataclass
class AssetAllocation:
    """Varlık dağılımı"""
    asset_class: str
    current_weight: float
    target_weight: float
    deviation: float
    rebalance_needed: bool
    suggested_action: str
    risk_score: float
    expected_return: float

class PortfolioAnalyticsEngine:
    """
    Portföy Analiz Motoru
    
    PRD v2.0 gereksinimleri:
    - Portföy analizi
    - Risk metrikleri
    - Performans takibi
    - Varlık dağılımı
    - Yeniden dengeleme stratejileri
    """
    
    def __init__(self):
        """Portfolio Analytics Engine başlatıcı"""
        # Risk-free rate (Türkiye için)
        self.risk_free_rate = 0.15  # %15 yıllık
        
        # Benchmark (BIST100)
        self.benchmark_symbol = "XU100.IS"
        
        # Portföy geçmişi
        self.portfolio_history = []
        
        # Risk hedefleri
        self.risk_targets = {
            'max_volatility': 0.25,  # %25
            'max_drawdown': 0.15,    # %15
            'min_sharpe': 0.8,       # 0.8
            'max_var_95': 0.05       # %5
        }
        
        # Varlık sınıfları
        self.asset_classes = {
            'equity': 'Hisse Senedi',
            'bond': 'Tahvil',
            'commodity': 'Emtia',
            'real_estate': 'Gayrimenkul',
            'cash': 'Nakit',
            'crypto': 'Kripto Para',
            'forex': 'Döviz'
        }
    
    def create_portfolio(self, assets: List[PortfolioAsset]) -> Dict[str, Any]:
        """
        Portföy oluştur
        
        Args:
            assets: Varlık listesi
            
        Returns:
            Dict[str, Any]: Portföy bilgileri
        """
        try:
            if not assets:
                return {'error': 'Varlık listesi boş olamaz'}
            
            # Toplam değer hesapla
            total_value = sum(asset.quantity * asset.current_price for asset in assets)
            
            # Ağırlıkları hesapla
            for asset in assets:
                asset.weight = (asset.quantity * asset.current_price) / total_value
            
            # Portföy metrikleri hesapla
            portfolio_metrics = self._calculate_portfolio_metrics(assets)
            
            # Risk metrikleri hesapla
            risk_metrics = self._calculate_risk_metrics(assets)
            
            # Varlık dağılımı analizi
            asset_allocation = self._analyze_asset_allocation(assets)
            
            portfolio_data = {
                'assets': assets,
                'total_value': total_value,
                'total_assets': len(assets),
                'metrics': portfolio_metrics,
                'risk_metrics': risk_metrics,
                'asset_allocation': asset_allocation,
                'created_at': datetime.now(),
                'last_updated': datetime.now()
            }
            
            # Portföy geçmişine ekle
            self.portfolio_history.append(portfolio_data)
            
            print(f"✅ Portföy oluşturuldu: {len(assets)} varlık, {total_value:,.2f} TL")
            return portfolio_data
            
        except Exception as e:
            print(f"❌ Portföy oluşturma hatası: {str(e)}")
            return {'error': str(e)}
    
    def update_portfolio(self, portfolio_id: int, new_prices: Dict[str, float]) -> Dict[str, Any]:
        """
        Portföy güncelle
        
        Args:
            portfolio_id: Portföy ID
            new_prices: Yeni fiyatlar
            
        Returns:
            Dict[str, Any]: Güncellenmiş portföy
        """
        try:
            if portfolio_id >= len(self.portfolio_history):
                return {'error': 'Geçersiz portföy ID'}
            
            portfolio = self.portfolio_history[portfolio_id].copy()
            assets = portfolio['assets']
            
            # Fiyatları güncelle
            for asset in assets:
                if asset.symbol in new_prices:
                    asset.current_price = new_prices[asset.symbol]
            
            # Metrikleri yeniden hesapla
            portfolio['metrics'] = self._calculate_portfolio_metrics(assets)
            portfolio['risk_metrics'] = self._calculate_risk_metrics(assets)
            portfolio['asset_allocation'] = self._analyze_asset_allocation(assets)
            portfolio['last_updated'] = datetime.now()
            
            # Geçmişi güncelle
            self.portfolio_history[portfolio_id] = portfolio
            
            print(f"✅ Portföy güncellendi: {portfolio_id}")
            return portfolio
            
        except Exception as e:
            print(f"❌ Portföy güncelleme hatası: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_portfolio_metrics(self, assets: List[PortfolioAsset]) -> PortfolioMetrics:
        """Portföy metriklerini hesapla"""
        try:
            # Temel hesaplamalar
            total_value = sum(asset.quantity * asset.current_price for asset in assets)
            total_cost = sum(asset.quantity * asset.purchase_price for asset in assets)
            total_return = total_value - total_cost
            total_return_pct = (total_return / total_cost) * 100 if total_cost > 0 else 0
            
            # Günlük getiri (basit hesaplama)
            daily_return = total_return / 252  # Yıllık iş günü
            daily_return_pct = (daily_return / total_cost) * 100 if total_cost > 0 else 0
            
            # Volatilite (basit hesaplama)
            returns = [asset.weight * ((asset.current_price - asset.purchase_price) / asset.purchase_price) 
                      for asset in assets if asset.purchase_price > 0]
            volatility = np.std(returns) * np.sqrt(252) if returns else 0
            
            # Sharpe Ratio
            excess_return = total_return_pct - (self.risk_free_rate * 100)
            sharpe_ratio = excess_return / volatility if volatility > 0 else 0
            
            # Beta (basit hesaplama)
            beta = 1.0  # Varsayılan değer
            
            # Alpha
            alpha = excess_return - (beta * excess_return)
            
            # Diğer metrikler
            max_drawdown = self._calculate_max_drawdown(assets)
            tracking_error = volatility * 0.1  # Basit hesaplama
            information_ratio = alpha / tracking_error if tracking_error > 0 else 0
            
            # Calmar Ratio
            calmar_ratio = total_return_pct / abs(max_drawdown) if max_drawdown != 0 else 0
            
            # Sortino Ratio
            downside_returns = [r for r in returns if r < 0]
            downside_deviation = np.std(downside_returns) * np.sqrt(252) if downside_returns else 0
            sortino_ratio = excess_return / downside_deviation if downside_deviation > 0 else 0
            
            # Treynor Ratio
            treynor_ratio = excess_return / beta if beta > 0 else 0
            
            # Jensen Alpha
            jensen_alpha = alpha
            
            return PortfolioMetrics(
                total_value=total_value,
                total_cost=total_cost,
                total_return=total_return,
                total_return_pct=total_return_pct,
                daily_return=daily_return,
                daily_return_pct=daily_return_pct,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                beta=beta,
                alpha=alpha,
                tracking_error=tracking_error,
                information_ratio=information_ratio,
                calmar_ratio=calmar_ratio,
                sortino_ratio=sortino_ratio,
                treynor_ratio=treynor_ratio,
                jensen_alpha=jensen_alpha,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"❌ Portföy metrikleri hesaplama hatası: {str(e)}")
            return PortfolioMetrics(
                total_value=0, total_cost=0, total_return=0, total_return_pct=0,
                daily_return=0, daily_return_pct=0, volatility=0, sharpe_ratio=0,
                max_drawdown=0, beta=0, alpha=0, tracking_error=0, information_ratio=0,
                calmar_ratio=0, sortino_ratio=0, treynor_ratio=0, jensen_alpha=0
            )
    
    def _calculate_risk_metrics(self, assets: List[PortfolioAsset]) -> RiskMetrics:
        """Risk metriklerini hesapla"""
        try:
            # Getiri hesaplamaları
            returns = []
            for asset in assets:
                if asset.purchase_price > 0:
                    asset_return = (asset.current_price - asset.purchase_price) / asset.purchase_price
                    # Ağırlıklı getiri
                    weighted_return = asset_return * asset.weight
                    returns.extend([weighted_return] * int(asset.weight * 100))  # Basit simülasyon
            
            if not returns:
                return RiskMetrics(
                    var_95=0, var_99=0, cvar_95=0, cvar_99=0,
                    downside_deviation=0, semi_variance=0, skewness=0, kurtosis=0
                )
            
            returns = np.array(returns)
            
            # VaR hesaplamaları
            var_95 = np.percentile(returns, 5)
            var_99 = np.percentile(returns, 1)
            
            # CVaR hesaplamaları
            cvar_95 = np.mean(returns[returns <= var_95])
            cvar_99 = np.mean(returns[returns <= var_99])
            
            # Downside deviation
            downside_returns = returns[returns < 0]
            downside_deviation = np.std(downside_returns) if len(downside_returns) > 0 else 0
            
            # Semi-variance
            semi_variance = np.var(returns[returns < 0]) if len(returns[returns < 0]) > 0 else 0
            
            # Skewness ve Kurtosis
            skewness = float(pd.Series(returns).skew())
            kurtosis = float(pd.Series(returns).kurtosis())
            
            # Korelasyon matrisi (basit)
            correlation_matrix = pd.DataFrame({'Returns': returns}).corr()
            
            # Kovaryans matrisi (basit)
            covariance_matrix = pd.DataFrame({'Returns': returns}).cov()
            
            return RiskMetrics(
                var_95=var_95,
                var_99=var_99,
                cvar_95=cvar_95,
                cvar_99=cvar_99,
                downside_deviation=downside_deviation,
                semi_variance=semi_variance,
                skewness=skewness,
                kurtosis=kurtosis,
                correlation_matrix=correlation_matrix,
                covariance_matrix=covariance_matrix,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"❌ Risk metrikleri hesaplama hatası: {str(e)}")
            return RiskMetrics(
                var_95=0, var_99=0, cvar_95=0, cvar_99=0,
                downside_deviation=0, semi_variance=0, skewness=0, kurtosis=0
            )
    
    def _analyze_asset_allocation(self, assets: List[PortfolioAsset]) -> List[AssetAllocation]:
        """Varlık dağılımını analiz et"""
        try:
            allocation = []
            
            # Sektör bazında grupla
            sector_groups = {}
            for asset in assets:
                sector = asset.sector if asset.sector else 'Unknown'
                if sector not in sector_groups:
                    sector_groups[sector] = []
                sector_groups[sector].append(asset)
            
            # Her sektör için analiz
            for sector, sector_assets in sector_groups.items():
                current_weight = sum(asset.weight for asset in sector_assets)
                
                # Hedef ağırlık (basit: eşit dağılım)
                target_weight = 1.0 / len(sector_groups)
                
                # Sapma
                deviation = current_weight - target_weight
                
                # Yeniden dengeleme gerekli mi?
                rebalance_needed = abs(deviation) > 0.05  # %5 tolerans
                
                # Önerilen aksiyon
                if deviation > 0.05:
                    suggested_action = "Sat"
                elif deviation < -0.05:
                    suggested_action = "Al"
                else:
                    suggested_action = "Tut"
                
                # Risk skoru (basit hesaplama)
                risk_score = np.mean([asset.weight * 0.5 for asset in sector_assets])
                
                # Beklenen getiri (basit hesaplama)
                expected_return = np.mean([asset.weight * 0.1 for asset in sector_assets])
                
                allocation.append(AssetAllocation(
                    asset_class=sector,
                    current_weight=current_weight,
                    target_weight=target_weight,
                    deviation=deviation,
                    rebalance_needed=rebalance_needed,
                    suggested_action=suggested_action,
                    risk_score=risk_score,
                    expected_return=expected_return
                ))
            
            return allocation
            
        except Exception as e:
            print(f"❌ Varlık dağılımı analiz hatası: {str(e)}")
            return []
    
    def _calculate_max_drawdown(self, assets: List[PortfolioAsset]) -> float:
        """Maximum drawdown hesapla"""
        try:
            # Basit drawdown hesaplama
            total_value = sum(asset.quantity * asset.current_price for asset in assets)
            total_cost = sum(asset.quantity * asset.purchase_price for asset in assets)
            
            if total_cost <= 0:
                return 0.0
            
            # En yüksek değer (purchase price)
            peak_value = total_cost
            
            # Drawdown
            drawdown = (total_value - peak_value) / peak_value
            
            return abs(drawdown) if drawdown < 0 else 0.0
            
        except Exception:
            return 0.0
    
    def get_portfolio_summary(self, portfolio_id: int) -> Dict[str, Any]:
        """
        Portföy özetini al
        
        Args:
            portfolio_id: Portföy ID
            
        Returns:
            Dict[str, Any]: Portföy özeti
        """
        try:
            if portfolio_id >= len(self.portfolio_history):
                return {'error': 'Geçersiz portföy ID'}
            
            portfolio = self.portfolio_history[portfolio_id]
            
            summary = {
                'portfolio_id': portfolio_id,
                'total_value': portfolio['total_value'],
                'total_assets': portfolio['total_assets'],
                'created_at': portfolio['created_at'],
                'last_updated': portfolio['last_updated'],
                'metrics': {
                    'total_return_pct': portfolio['metrics'].total_return_pct,
                    'volatility': portfolio['metrics'].volatility,
                    'sharpe_ratio': portfolio['metrics'].sharpe_ratio,
                    'max_drawdown': portfolio['metrics'].max_drawdown
                },
                'risk_metrics': {
                    'var_95': portfolio['risk_metrics'].var_95,
                    'var_99': portfolio['risk_metrics'].var_99,
                    'beta': portfolio['metrics'].beta,
                    'alpha': portfolio['metrics'].alpha
                },
                'top_assets': sorted(portfolio['assets'], 
                                   key=lambda x: x.weight, reverse=True)[:5]
            }
            
            return summary
            
        except Exception as e:
            print(f"❌ Portföy özeti alma hatası: {str(e)}")
            return {'error': str(e)}
    
    def get_portfolio_history(self) -> List[Dict[str, Any]]:
        """Portföy geçmişini al"""
        return self.portfolio_history
    
    def calculate_rebalancing_recommendations(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """
        Yeniden dengeleme önerilerini hesapla
        
        Args:
            portfolio_id: Portföy ID
            
        Returns:
            List[Dict[str, Any]]: Yeniden dengeleme önerileri
        """
        try:
            if portfolio_id >= len(self.portfolio_history):
                return [{'error': 'Geçersiz portföy ID'}]
            
            portfolio = self.portfolio_history[portfolio_id]
            allocation = portfolio['asset_allocation']
            
            recommendations = []
            
            for asset_alloc in allocation:
                if asset_alloc.rebalance_needed:
                    recommendation = {
                        'asset_class': asset_alloc.asset_class,
                        'current_weight': asset_alloc.current_weight,
                        'target_weight': asset_alloc.target_weight,
                        'deviation': asset_alloc.deviation,
                        'action': asset_alloc.suggested_action,
                        'priority': 'high' if abs(asset_alloc.deviation) > 0.1 else 'medium',
                        'expected_impact': abs(asset_alloc.deviation) * 100
                    }
                    recommendations.append(recommendation)
            
            # Önceliğe göre sırala
            recommendations.sort(key=lambda x: x['expected_impact'], reverse=True)
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Yeniden dengeleme önerileri hesaplama hatası: {str(e)}")
            return [{'error': str(e)}]
    
    def stress_test_portfolio(self, portfolio_id: int, scenarios: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Portföy stress testi yap
        
        Args:
            portfolio_id: Portföy ID
            scenarios: Senaryo listesi
            
        Returns:
            Dict[str, Any]: Stress test sonuçları
        """
        try:
            if portfolio_id >= len(self.portfolio_history):
                return {'error': 'Geçersiz portföy ID'}
            
            portfolio = self.portfolio_history[portfolio_id]
            assets = portfolio['assets']
            
            stress_results = {}
            
            for scenario in scenarios:
                scenario_name = scenario.get('name', 'Unknown')
                price_change = scenario.get('price_change', 0.0)
                
                # Yeni portföy değeri hesapla
                new_total_value = 0
                for asset in assets:
                    new_price = asset.current_price * (1 + price_change)
                    new_total_value += asset.quantity * new_price
                
                # Getiri hesapla
                original_value = portfolio['total_value']
                scenario_return = (new_total_value - original_value) / original_value
                
                stress_results[scenario_name] = {
                    'price_change': price_change,
                    'new_total_value': new_total_value,
                    'scenario_return': scenario_return,
                    'impact': abs(scenario_return)
                }
            
            return {
                'portfolio_id': portfolio_id,
                'scenarios': stress_results,
                'worst_case': min(stress_results.values(), key=lambda x: x['scenario_return']),
                'best_case': max(stress_results.values(), key=lambda x: x['scenario_return'])
            }
            
        except Exception as e:
            print(f"❌ Stress test hatası: {str(e)}")
            return {'error': str(e)}

# Test fonksiyonu
def test_portfolio_analytics_engine():
    """Portfolio Analytics Engine test fonksiyonu"""
    print("🧪 Portfolio Analytics Engine Test Başlıyor...")
    
    # Portfolio Analytics Engine başlat
    engine = PortfolioAnalyticsEngine()
    
    # Test varlıkları oluştur
    print("\n📊 Test Varlıkları Oluşturuluyor:")
    test_assets = [
        PortfolioAsset(
            symbol="SISE.IS",
            quantity=1000,
            current_price=45.50,
            purchase_price=42.00,
            purchase_date=datetime.now() - timedelta(days=30),
            sector="INDUSTRIAL",
            market_cap=50000000000
        ),
        PortfolioAsset(
            symbol="EREGL.IS",
            quantity=500,
            current_price=28.75,
            purchase_price=30.00,
            purchase_date=datetime.now() - timedelta(days=45),
            sector="INDUSTRIAL",
            market_cap=80000000000
        ),
        PortfolioAsset(
            symbol="TUPRS.IS",
            quantity=800,
            current_price=125.00,
            purchase_price=120.00,
            purchase_date=datetime.now() - timedelta(days=20),
            sector="ENERGY",
            market_cap=120000000000
        ),
        PortfolioAsset(
            symbol="GARAN.IS",
            quantity=2000,
            current_price=18.25,
            purchase_price=17.50,
            purchase_date=datetime.now() - timedelta(days=60),
            sector="FINANCIAL",
            market_cap=150000000000
        )
    ]
    
    print(f"   ✅ {len(test_assets)} test varlığı oluşturuldu")
    
    # Portföy oluştur test
    print("\n🏗️ Portföy Oluşturma Test:")
    portfolio = engine.create_portfolio(test_assets)
    
    if 'error' not in portfolio:
        print(f"   ✅ Portföy oluşturuldu: {portfolio['total_value']:,.2f} TL")
        print(f"   📊 Toplam varlık: {portfolio['total_assets']}")
        print(f"   📈 Toplam getiri: {portfolio['metrics'].total_return_pct:.2f}%")
        print(f"   📊 Sharpe Ratio: {portfolio['metrics'].sharpe_ratio:.3f}")
        print(f"   ⚠️ Volatilite: {portfolio['metrics'].volatility:.3f}")
        print(f"   📉 Max Drawdown: {portfolio['metrics'].max_drawdown:.3f}")
    
    # Risk metrikleri test
    print("\n⚠️ Risk Metrikleri Test:")
    if 'error' not in portfolio:
        risk_metrics = portfolio['risk_metrics']
        print(f"   ✅ VaR 95%: {risk_metrics.var_95:.4f}")
        print(f"   ✅ VaR 99%: {risk_metrics.var_99:.4f}")
        print(f"   ✅ CVaR 95%: {risk_metrics.cvar_95:.4f}")
        print(f"   ✅ Skewness: {risk_metrics.skewness:.3f}")
        print(f"   ✅ Kurtosis: {risk_metrics.kurtosis:.3f}")
    
    # Varlık dağılımı test
    print("\n📊 Varlık Dağılımı Test:")
    if 'error' not in portfolio:
        allocation = portfolio['asset_allocation']
        for alloc in allocation:
            print(f"   {alloc.asset_class}: {alloc.current_weight:.1%} "
                  f"(Hedef: {alloc.target_weight:.1%}, Sapma: {alloc.deviation:.1%})")
            if alloc.rebalance_needed:
                print(f"     🔄 Yeniden dengeleme gerekli: {alloc.suggested_action}")
    
    # Portföy özeti test
    print("\n📋 Portföy Özeti Test:")
    summary = engine.get_portfolio_summary(0)
    if 'error' not in summary:
        print(f"   ✅ Özet alındı: {summary['total_value']:,.2f} TL")
        print(f"   📊 Top 5 varlık: {len(summary['top_assets'])}")
    
    # Yeniden dengeleme önerileri test
    print("\n🔄 Yeniden Dengeleme Önerileri Test:")
    recommendations = engine.calculate_rebalancing_recommendations(0)
    if recommendations and 'error' not in recommendations[0]:
        print(f"   ✅ {len(recommendations)} öneri hesaplandı")
        for rec in recommendations[:3]:  # İlk 3 öneri
            print(f"     {rec['asset_class']}: {rec['action']} "
                  f"(Öncelik: {rec['priority']}, Etki: {rec['expected_impact']:.1f}%)")
    
    # Stress test test
    print("\n💥 Stress Test Test:")
    scenarios = [
        {'name': 'Küresel Kriz', 'price_change': -0.20},
        {'name': 'Piyasa Düşüşü', 'price_change': -0.10},
        {'name': 'Hafif Düşüş', 'price_change': -0.05},
        {'name': 'Hafif Yükseliş', 'price_change': 0.05},
        {'name': 'Piyasa Yükselişi', 'price_change': 0.10},
        {'name': 'Boom', 'price_change': 0.20}
    ]
    
    stress_results = engine.stress_test_portfolio(0, scenarios)
    if 'error' not in stress_results:
        print(f"   ✅ {len(stress_results['scenarios'])} senaryo test edildi")
        worst_case = stress_results['worst_case']
        best_case = stress_results['best_case']
        print(f"   📉 En kötü senaryo: {worst_case['scenario_return']:.1%}")
        print(f"   📈 En iyi senaryo: {best_case['scenario_return']:.1%}")
    
    # Portföy güncelleme test
    print("\n🔄 Portföy Güncelleme Test:")
    new_prices = {
        "SISE.IS": 46.00,
        "EREGL.IS": 29.00,
        "TUPRS.IS": 126.00,
        "GARAN.IS": 18.50
    }
    
    updated_portfolio = engine.update_portfolio(0, new_prices)
    if 'error' not in updated_portfolio:
        print(f"   ✅ Portföy güncellendi: {updated_portfolio['total_value']:,.2f} TL")
        print(f"   📈 Yeni getiri: {updated_portfolio['metrics'].total_return_pct:.2f}%")
    
    # Portföy geçmişi test
    print("\n📚 Portföy Geçmişi Test:")
    history = engine.get_portfolio_history()
    print(f"   ✅ Geçmiş kayıtları: {len(history)}")
    
    print("\n✅ Portfolio Analytics Engine Test Tamamlandı!")
    
    return engine

if __name__ == "__main__":
    test_portfolio_analytics_engine()
