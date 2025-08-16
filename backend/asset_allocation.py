"""
PRD v2.0 - BIST AI Smart Trader
Asset Allocation Module

Varlık dağılımı modülü:
- Portfolio optimization
- Asset allocation strategies
- Risk-based allocation
- Rebalancing strategies
- Modern Portfolio Theory
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class AssetClass:
    """Varlık sınıfı"""
    name: str
    symbol: str
    weight: float
    expected_return: float
    volatility: float
    risk_score: float
    correlation_matrix: Optional[pd.DataFrame] = None

@dataclass
class AllocationStrategy:
    """Dağılım stratejisi"""
    strategy_id: str
    name: str
    description: str
    risk_tolerance: str  # low, medium, high
    target_volatility: float
    target_return: float
    rebalancing_frequency: str  # daily, weekly, monthly, quarterly
    created_at: datetime = None

@dataclass
class PortfolioAllocation:
    """Portföy dağılımı"""
    allocation_id: str
    strategy_id: str
    total_value: float
    assets: List[AssetClass]
    target_weights: Dict[str, float]
    current_weights: Dict[str, float]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    created_at: datetime = None
    last_rebalanced: datetime = None

@dataclass
class RebalancingRecommendation:
    """Yeniden dengeleme önerisi"""
    recommendation_id: str
    asset_symbol: str
    current_weight: float
    target_weight: float
    deviation: float
    action: str  # buy, sell, hold
    quantity: float
    priority: str  # low, medium, high, critical
    expected_impact: float
    timestamp: datetime = None

class AssetAllocation:
    """
    Varlık Dağılımı Sistemi
    
    PRD v2.0 gereksinimleri:
    - Portföy optimizasyonu
    - Varlık dağılım stratejileri
    - Risk bazlı dağılım
    - Yeniden dengeleme stratejileri
    - Modern Portföy Teorisi
    """
    
    def __init__(self):
        """Asset Allocation başlatıcı"""
        # Varlık sınıfları
        self.asset_classes = {}
        
        # Dağılım stratejileri
        self.allocation_strategies = {}
        
        # Portföy dağılımları
        self.portfolio_allocations = {}
        
        # Yeniden dengeleme önerileri
        self.rebalancing_recommendations = []
        
        # Varsayılan varlık sınıflarını ve stratejileri ekle
        self._add_default_asset_classes()
        self._add_default_strategies()
    
    def _add_default_asset_classes(self):
        """Varsayılan varlık sınıflarını ekle"""
        default_assets = {
            'equity_turkey': AssetClass(
                name='Türkiye Hisse Senedi',
                symbol='BIST',
                weight=0.0,
                expected_return=0.18,
                volatility=0.25,
                risk_score=0.7
            ),
            'equity_global': AssetClass(
                name='Küresel Hisse Senedi',
                symbol='GLOBAL',
                weight=0.0,
                expected_return=0.12,
                volatility=0.18,
                risk_score=0.6
            ),
            'bonds_turkey': AssetClass(
                name='Türkiye Tahvil',
                symbol='TRBOND',
                weight=0.0,
                expected_return=0.15,
                volatility=0.12,
                risk_score=0.4
            ),
            'bonds_global': AssetClass(
                name='Küresel Tahvil',
                symbol='GLBOND',
                weight=0.0,
                expected_return=0.06,
                volatility=0.08,
                risk_score=0.3
            ),
            'commodities': AssetClass(
                name='Emtia',
                symbol='COMM',
                weight=0.0,
                expected_return=0.08,
                volatility=0.20,
                risk_score=0.8
            ),
            'real_estate': AssetClass(
                name='Gayrimenkul',
                symbol='REIT',
                weight=0.0,
                expected_return=0.10,
                volatility=0.15,
                risk_score=0.5
            ),
            'cash': AssetClass(
                name='Nakit',
                symbol='CASH',
                weight=0.0,
                expected_return=0.15,
                volatility=0.02,
                risk_score=0.1
            ),
            'crypto': AssetClass(
                name='Kripto Para',
                symbol='CRYPTO',
                weight=0.0,
                expected_return=0.25,
                volatility=0.40,
                risk_score=0.9
            )
        }
        
        self.asset_classes.update(default_assets)
        print("✅ Varsayılan varlık sınıfları eklendi")
    
    def _add_default_strategies(self):
        """Varsayılan stratejileri ekle"""
        strategies = {
            'conservative': AllocationStrategy(
                strategy_id='conservative',
                name='Muhafazakar',
                description='Düşük risk, düşük getiri hedefi',
                risk_tolerance='low',
                target_volatility=0.08,
                target_return=0.12,
                rebalancing_frequency='monthly',
                created_at=datetime.now()
            ),
            'moderate': AllocationStrategy(
                strategy_id='moderate',
                name='Orta',
                description='Orta risk, orta getiri hedefi',
                risk_tolerance='medium',
                target_volatility=0.15,
                target_return=0.15,
                rebalancing_frequency='monthly',
                created_at=datetime.now()
            ),
            'aggressive': AllocationStrategy(
                strategy_id='aggressive',
                name='Agresif',
                description='Yüksek risk, yüksek getiri hedefi',
                risk_tolerance='high',
                target_volatility=0.25,
                target_return=0.20,
                rebalancing_frequency='weekly',
                created_at=datetime.now()
            ),
            'balanced': AllocationStrategy(
                strategy_id='balanced',
                name='Dengeli',
                description='Risk-getiri dengesi',
                risk_tolerance='medium',
                target_volatility=0.12,
                target_return=0.14,
                rebalancing_frequency='monthly',
                created_at=datetime.now()
            )
        }
        
        self.allocation_strategies.update(strategies)
        print("✅ Varsayılan stratejiler eklendi")
    
    def create_allocation_strategy(self, strategy: AllocationStrategy) -> bool:
        """
        Dağılım stratejisi oluştur
        
        Args:
            strategy: Strateji
            
        Returns:
            bool: Başarı durumu
        """
        try:
            if strategy.strategy_id in self.allocation_strategies:
                print(f"⚠️ Strateji zaten mevcut: {strategy.strategy_id}")
                return False
            
            self.allocation_strategies[strategy.strategy_id] = strategy
            print(f"✅ Dağılım stratejisi oluşturuldu: {strategy.name}")
            return True
            
        except Exception as e:
            print(f"❌ Strateji oluşturma hatası: {str(e)}")
            return False
    
    def get_allocation_strategy(self, strategy_id: str) -> Optional[AllocationStrategy]:
        """
        Dağılım stratejisini al
        
        Args:
            strategy_id: Strateji ID
            
        Returns:
            Optional[AllocationStrategy]: Strateji
        """
        return self.allocation_strategies.get(strategy_id)
    
    def calculate_optimal_allocation(self, strategy_id: str, total_value: float,
                                     risk_constraints: Optional[Dict[str, float]] = None) -> PortfolioAllocation:
        """
        Optimal dağılımı hesapla
        
        Args:
            strategy_id: Strateji ID
            total_value: Toplam değer
            risk_constraints: Risk kısıtları
            
        Returns:
            PortfolioAllocation: Optimal dağılım
        """
        try:
            strategy = self.allocation_strategies.get(strategy_id)
            if not strategy:
                raise ValueError(f"Strateji bulunamadı: {strategy_id}")
            
            # Strateji bazında ağırlıkları belirle
            if strategy_id == 'conservative':
                weights = {
                    'equity_turkey': 0.20,
                    'equity_global': 0.15,
                    'bonds_turkey': 0.30,
                    'bonds_global': 0.20,
                    'commodities': 0.05,
                    'real_estate': 0.05,
                    'cash': 0.05,
                    'crypto': 0.00
                }
            elif strategy_id == 'moderate':
                weights = {
                    'equity_turkey': 0.35,
                    'equity_global': 0.25,
                    'bonds_turkey': 0.20,
                    'bonds_global': 0.10,
                    'commodities': 0.05,
                    'real_estate': 0.03,
                    'cash': 0.02,
                    'crypto': 0.00
                }
            elif strategy_id == 'aggressive':
                weights = {
                    'equity_turkey': 0.45,
                    'equity_global': 0.30,
                    'bonds_turkey': 0.10,
                    'bonds_global': 0.05,
                    'commodities': 0.05,
                    'real_estate': 0.03,
                    'cash': 0.02,
                    'crypto': 0.00
                }
            elif strategy_id == 'balanced':
                weights = {
                    'equity_turkey': 0.30,
                    'equity_global': 0.20,
                    'bonds_turkey': 0.25,
                    'bonds_global': 0.15,
                    'commodities': 0.05,
                    'real_estate': 0.03,
                    'cash': 0.02,
                    'crypto': 0.00
                }
            else:
                # Özel strateji için varsayılan ağırlıklar
                weights = {asset: 1.0 / len(self.asset_classes) for asset in self.asset_classes.keys()}
            
            # Risk kısıtlarını uygula
            if risk_constraints:
                for asset, max_weight in risk_constraints.items():
                    if asset in weights:
                        weights[asset] = min(weights[asset], max_weight)
                
                # Ağırlıkları normalize et
                total_weight = sum(weights.values())
                if total_weight > 0:
                    weights = {k: v / total_weight for k, v in weights.items()}
            
            # Varlık sınıflarını güncelle
            assets = []
            for asset_id, weight in weights.items():
                if asset_id in self.asset_classes:
                    asset = self.asset_classes[asset_id]
                    asset.weight = weight
                    assets.append(asset)
            
            # Beklenen getiri ve volatilite hesapla
            expected_return = sum(asset.weight * asset.expected_return for asset in assets)
            expected_volatility = sum(asset.weight * asset.volatility for asset in assets)
            
            # Sharpe ratio (risk-free rate: %15)
            risk_free_rate = 0.15
            sharpe_ratio = (expected_return - risk_free_rate) / expected_volatility if expected_volatility > 0 else 0
            
            # Maximum drawdown (basit hesaplama)
            max_drawdown = expected_volatility * 2  # Basit yaklaşım
            
            allocation = PortfolioAllocation(
                allocation_id=f"allocation_{strategy_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                strategy_id=strategy_id,
                total_value=total_value,
                assets=assets,
                target_weights=weights,
                current_weights=weights.copy(),
                expected_return=expected_return,
                expected_volatility=expected_volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                created_at=datetime.now(),
                last_rebalanced=datetime.now()
            )
            
            self.portfolio_allocations[allocation.allocation_id] = allocation
            print(f"✅ Optimal dağılım hesaplandı: {strategy_id}")
            
            return allocation
            
        except Exception as e:
            print(f"❌ Optimal dağılım hesaplama hatası: {str(e)}")
            return PortfolioAllocation(
                allocation_id="", strategy_id="", total_value=0, assets=[],
                target_weights={}, current_weights={}, expected_return=0,
                expected_volatility=0, sharpe_ratio=0, max_drawdown=0
            )
    
    def calculate_rebalancing_needs(self, allocation_id: str, 
                                    tolerance: float = 0.05) -> List[RebalancingRecommendation]:
        """
        Yeniden dengeleme ihtiyaçlarını hesapla
        
        Args:
            allocation_id: Dağılım ID
            tolerance: Tolerans (%)
            
        Returns:
            List[RebalancingRecommendation]: Yeniden dengeleme önerileri
        """
        try:
            if allocation_id not in self.portfolio_allocations:
                return []
            
            allocation = self.portfolio_allocations[allocation_id]
            recommendations = []
            
            for asset in allocation.assets:
                current_weight = asset.weight
                target_weight = allocation.target_weights.get(asset.symbol, 0)
                deviation = abs(current_weight - target_weight)
                
                if deviation > tolerance:
                    # Önerilen aksiyon
                    if current_weight > target_weight:
                        action = "sell"
                        quantity = (current_weight - target_weight) * allocation.total_value
                    else:
                        action = "buy"
                        quantity = (target_weight - current_weight) * allocation.total_value
                    
                    # Öncelik belirleme
                    if deviation > tolerance * 2:
                        priority = "critical"
                    elif deviation > tolerance * 1.5:
                        priority = "high"
                    else:
                        priority = "medium"
                    
                    # Beklenen etki
                    expected_impact = deviation * 100
                    
                    recommendation = RebalancingRecommendation(
                        recommendation_id=f"rebal_{asset.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        asset_symbol=asset.symbol,
                        current_weight=current_weight,
                        target_weight=target_weight,
                        deviation=deviation,
                        action=action,
                        quantity=quantity,
                        priority=priority,
                        expected_impact=expected_impact,
                        timestamp=datetime.now()
                    )
                    
                    recommendations.append(recommendation)
            
            # Önceliğe göre sırala
            recommendations.sort(key=lambda x: x.priority == 'critical', reverse=True)
            recommendations.sort(key=lambda x: x.expected_impact, reverse=True)
            
            # Önerileri kaydet
            self.rebalancing_recommendations.extend(recommendations)
            
            print(f"✅ {len(recommendations)} yeniden dengeleme önerisi hesaplandı")
            return recommendations
            
        except Exception as e:
            print(f"❌ Yeniden dengeleme hesaplama hatası: {str(e)}")
            return []
    
    def apply_rebalancing(self, allocation_id: str, 
                          rebalancing_actions: List[Dict[str, Any]]) -> bool:
        """
        Yeniden dengeleme uygula
        
        Args:
            allocation_id: Dağılım ID
            rebalancing_actions: Yeniden dengeleme aksiyonları
            
        Returns:
            bool: Başarı durumu
        """
        try:
            if allocation_id not in self.portfolio_allocations:
                print(f"❌ Dağılım bulunamadı: {allocation_id}")
                return False
            
            allocation = self.portfolio_allocations[allocation_id]
            
            # Ağırlıkları güncelle
            for action in rebalancing_actions:
                asset_symbol = action.get('asset_symbol')
                new_weight = action.get('new_weight')
                
                if asset_symbol and new_weight is not None:
                    # Varlık sınıfını bul ve güncelle
                    for asset in allocation.assets:
                        if asset.symbol == asset_symbol:
                            asset.weight = new_weight
                            allocation.current_weights[asset_symbol] = new_weight
                            break
            
            # Metrikleri yeniden hesapla
            expected_return = sum(asset.weight * asset.expected_return for asset in allocation.assets)
            expected_volatility = sum(asset.weight * asset.volatility for asset in allocation.assets)
            
            # Sharpe ratio güncelle
            risk_free_rate = 0.15
            sharpe_ratio = (expected_return - risk_free_rate) / expected_volatility if expected_volatility > 0 else 0
            
            # Maximum drawdown güncelle
            max_drawdown = expected_volatility * 2
            
            # Dağılımı güncelle
            allocation.expected_return = expected_return
            allocation.expected_volatility = expected_volatility
            allocation.sharpe_ratio = sharpe_ratio
            allocation.max_drawdown = max_drawdown
            allocation.last_rebalanced = datetime.now()
            
            print(f"✅ Yeniden dengeleme uygulandı: {allocation_id}")
            return True
            
        except Exception as e:
            print(f"❌ Yeniden dengeleme uygulama hatası: {str(e)}")
            return False
    
    def get_portfolio_allocation(self, allocation_id: str) -> Optional[PortfolioAllocation]:
        """
        Portföy dağılımını al
        
        Args:
            allocation_id: Dağılım ID
            
        Returns:
            Optional[PortfolioAllocation]: Portföy dağılımı
        """
        return self.portfolio_allocations.get(allocation_id)
    
    def get_all_allocations(self) -> List[str]:
        """Tüm dağılım ID'lerini listele"""
        return list(self.portfolio_allocations.keys())
    
    def get_rebalancing_recommendations(self, status: Optional[str] = None,
                                        priority: Optional[str] = None) -> List[RebalancingRecommendation]:
        """
        Yeniden dengeleme önerilerini al
        
        Args:
            status: Durum
            priority: Öncelik
            
        Returns:
            List[RebalancingRecommendation]: Öneriler
        """
        recommendations = self.rebalancing_recommendations
        
        if status:
            recommendations = [r for r in recommendations if r.priority == status]
        
        if priority:
            recommendations = [r for r in recommendations if r.priority == priority]
        
        return recommendations
    
    def get_allocation_summary(self) -> Dict[str, Any]:
        """Dağılım özetini al"""
        try:
            summary = {
                'total_allocations': len(self.portfolio_allocations),
                'total_strategies': len(self.allocation_strategies),
                'total_asset_classes': len(self.asset_classes),
                'total_rebalancing_recommendations': len(self.rebalancing_recommendations),
                'allocations_by_strategy': {},
                'asset_class_weights': {},
                'performance_metrics': {}
            }
            
            # Strateji bazında dağılım sayısı
            for allocation in self.portfolio_allocations.values():
                strategy = allocation.strategy_id
                if strategy not in summary['allocations_by_strategy']:
                    summary['allocations_by_strategy'][strategy] = 0
                summary['allocations_by_strategy'][strategy] += 1
            
            # Varlık sınıfı ağırlıkları (ortalama)
            for asset_class in self.asset_classes.values():
                summary['asset_class_weights'][asset_class.name] = asset_class.weight
            
            # Performans metrikleri (ortalama)
            if self.portfolio_allocations:
                avg_return = np.mean([a.expected_return for a in self.portfolio_allocations.values()])
                avg_volatility = np.mean([a.expected_volatility for a in self.portfolio_allocations.values()])
                avg_sharpe = np.mean([a.sharpe_ratio for a in self.portfolio_allocations.values()])
                
                summary['performance_metrics'] = {
                    'average_return': avg_return,
                    'average_volatility': avg_volatility,
                    'average_sharpe_ratio': avg_sharpe
                }
            
            return summary
            
        except Exception as e:
            print(f"❌ Dağılım özeti alma hatası: {str(e)}")
            return {'error': str(e)}

# Test fonksiyonu
def test_asset_allocation():
    """Asset Allocation test fonksiyonu"""
    print("🧪 Asset Allocation Test Başlıyor...")
    
    # Asset Allocation başlat
    allocation_system = AssetAllocation()
    
    # Varlık sınıfları test
    print("\n📊 Varlık Sınıfları Test:")
    asset_classes = allocation_system.asset_classes
    print(f"   ✅ {len(asset_classes)} varlık sınıfı mevcut")
    for name, asset in list(asset_classes.items())[:5]:  # İlk 5'i göster
        print(f"     {asset.name}: Beklenen getiri {asset.expected_return:.1%}, Risk {asset.risk_score:.1f}")
    
    # Stratejiler test
    print("\n🎯 Stratejiler Test:")
    strategies = allocation_system.allocation_strategies
    print(f"   ✅ {len(strategies)} strateji mevcut")
    for strategy_id, strategy in strategies.items():
        print(f"     {strategy.name}: Risk toleransı {strategy.risk_tolerance}, "
              f"Hedef volatilite {strategy.target_volatility:.1%}")
    
    # Yeni strateji oluştur test
    print("\n🏗️ Yeni Strateji Test:")
    custom_strategy = AllocationStrategy(
        strategy_id='custom',
        name='Özel Strateji',
        description='Özel risk-getiri profili',
        risk_tolerance='medium',
        target_volatility=0.18,
        target_return=0.16,
        rebalancing_frequency='weekly'
    )
    
    strategy_created = allocation_system.create_allocation_strategy(custom_strategy)
    print(f"   Yeni strateji oluşturuldu: {strategy_created}")
    
    # Optimal dağılım hesaplama test
    print("\n🧮 Optimal Dağılım Hesaplama Test:")
    allocation = allocation_system.calculate_optimal_allocation(
        strategy_id='moderate',
        total_value=1000000
    )
    
    if allocation.allocation_id:
        print(f"   ✅ Optimal dağılım hesaplandı: {allocation.strategy_id}")
        print(f"   📊 Beklenen getiri: {allocation.expected_return:.1%}")
        print(f"   ⚠️ Beklenen volatilite: {allocation.expected_volatility:.1%}")
        print(f"   📈 Sharpe ratio: {allocation.sharpe_ratio:.3f}")
        print(f"   📉 Maximum drawdown: {allocation.max_drawdown:.1%}")
        
        # Varlık dağılımını göster
        print("\n   📋 Varlık Dağılımı:")
        for asset in allocation.assets[:5]:  # İlk 5'i göster
            print(f"     {asset.name}: {asset.weight:.1%}")
    
    # Yeniden dengeleme ihtiyaçları test
    print("\n🔄 Yeniden Dengeleme İhtiyaçları Test:")
    rebalancing_needs = allocation_system.calculate_rebalancing_needs(
        allocation_id=allocation.allocation_id,
        tolerance=0.05
    )
    
    print(f"   ✅ {len(rebalancing_needs)} yeniden dengeleme önerisi hesaplandı")
    
    if rebalancing_needs:
        for rec in rebalancing_needs[:3]:  # İlk 3 öneri
            print(f"     {rec.asset_symbol}: {rec.action} "
                  f"(Öncelik: {rec.priority}, Etki: {rec.expected_impact:.1f}%)")
    
    # Yeniden dengeleme uygulama test
    print("\n⚙️ Yeniden Dengeleme Uygulama Test:")
    if rebalancing_needs:
        # İlk öneriyi uygula
        first_rec = rebalancing_needs[0]
        rebalancing_actions = [{
            'asset_symbol': first_rec.asset_symbol,
            'new_weight': first_rec.target_weight
        }]
        
        rebalancing_applied = allocation_system.apply_rebalancing(
            allocation_id=allocation.allocation_id,
            rebalancing_actions=rebalancing_actions
        )
        print(f"   Yeniden dengeleme uygulandı: {rebalancing_applied}")
    
    # Portföy dağılımı alma test
    print("\n📥 Portföy Dağılımı Alma Test:")
    retrieved_allocation = allocation_system.get_portfolio_allocation(allocation.allocation_id)
    if retrieved_allocation:
        print(f"   ✅ Dağılım alındı: {retrieved_allocation.allocation_id}")
        print(f"   📅 Son yeniden dengeleme: {retrieved_allocation.last_rebalanced}")
    
    # Tüm dağılımlar test
    print("\n📋 Tüm Dağılımlar Test:")
    all_allocations = allocation_system.get_all_allocations()
    print(f"   ✅ Toplam dağılım: {len(all_allocations)}")
    
    # Yeniden dengeleme önerileri test
    print("\n💡 Yeniden Dengeleme Önerileri Test:")
    all_recommendations = allocation_system.get_rebalancing_recommendations()
    print(f"   ✅ Toplam öneri: {len(all_recommendations)}")
    
    # Dağılım özeti test
    print("\n📊 Dağılım Özeti Test:")
    allocation_summary = allocation_system.get_allocation_summary()
    if 'error' not in allocation_summary:
        print(f"   ✅ Dağılım özeti alındı")
        print(f"   📊 Toplam dağılım: {allocation_summary['total_allocations']}")
        print(f"   🎯 Toplam strateji: {allocation_summary['total_strategies']}")
        print(f"   📈 Ortalama getiri: {allocation_summary['performance_metrics']['average_return']:.1%}")
        print(f"   ⚠️ Ortalama volatilite: {allocation_summary['performance_metrics']['average_volatility']:.1%}")
    
    print("\n✅ Asset Allocation Test Tamamlandı!")
    
    return allocation_system

if __name__ == "__main__":
    test_asset_allocation()
