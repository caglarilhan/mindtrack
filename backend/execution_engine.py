"""
PRD v2.0 - BIST AI Smart Trader
Execution Engine Module

İcra motoru:
- Order execution
- Market simulation
- Execution strategies
- Slippage management
- Market impact analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class ExecutionResult:
    """İcra sonucu"""
    execution_id: str
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    execution_time: datetime
    slippage: float
    market_impact: float
    commission: float
    total_cost: float
    status: str = "executed"
    message: str = ""

@dataclass
class MarketData:
    """Piyasa verisi"""
    symbol: str
    bid: float
    ask: float
    last: float
    volume: float
    timestamp: datetime
    spread: float
    volatility: float

@dataclass
class ExecutionStrategy:
    """İcra stratejisi"""
    strategy_id: str
    name: str
    description: str
    execution_type: str  # market, limit, twap, vwap, ice
    parameters: Dict[str, Any]
    risk_level: str  # low, medium, high
    created_at: datetime = None

@dataclass
class MarketImpact:
    """Piyasa etkisi"""
    symbol: str
    order_size: float
    market_volume: float
    impact_score: float
    estimated_slippage: float
    recommended_strategy: str
    timestamp: datetime = None

class ExecutionEngine:
    """
    İcra Motoru
    
    PRD v2.0 gereksinimleri:
    - Sipariş icrası
    - Piyasa simülasyonu
    - İcra stratejileri
    - Slippage yönetimi
    - Piyasa etki analizi
    """
    
    def __init__(self):
        """Execution Engine başlatıcı"""
        # İcra sonuçları
        self.execution_results = {}
        
        # Piyasa verileri
        self.market_data = {}
        
        # İcra stratejileri
        self.execution_strategies = {}
        
        # Piyasa etki analizleri
        self.market_impacts = {}
        
        # Varsayılan stratejileri ekle
        self._add_default_strategies()
        
        # Simülasyon parametreleri
        self.simulation_params = {
            'slippage_model': 'linear',
            'market_impact_model': 'square_root',
            'execution_delay': 0.1,  # saniye
            'random_seed': 42
        }
        
        # Random seed ayarla
        np.random.seed(self.simulation_params['random_seed'])
    
    def _add_default_strategies(self):
        """Varsayılan stratejileri ekle"""
        strategies = {
            'market': ExecutionStrategy(
                strategy_id='market',
                name='Market Order',
                description='Anında piyasa fiyatından icra',
                execution_type='market',
                parameters={'priority': 'speed'},
                risk_level='medium',
                created_at=datetime.now()
            ),
            'limit': ExecutionStrategy(
                strategy_id='limit',
                name='Limit Order',
                description='Belirli fiyattan icra',
                execution_type='limit',
                parameters={'timeout': 300},  # 5 dakika
                risk_level='low',
                created_at=datetime.now()
            ),
            'twap': ExecutionStrategy(
                strategy_id='twap',
                name='Time Weighted Average Price',
                description='Zaman ağırlıklı ortalama fiyat',
                execution_type='twap',
                parameters={'duration': 3600, 'intervals': 12},  # 1 saat, 12 aralık
                risk_level='low',
                created_at=datetime.now()
            ),
            'vwap': ExecutionStrategy(
                strategy_id='vwap',
                name='Volume Weighted Average Price',
                description='Hacim ağırlıklı ortalama fiyat',
                execution_type='vwap',
                parameters={'volume_target': 0.8},  # %80 hacim hedefi
                risk_level='low',
                created_at=datetime.now()
            ),
            'ice': ExecutionStrategy(
                strategy_id='ice',
                name='Iceberg Order',
                description='Buzdağı siparişi',
                execution_type='ice',
                parameters={'visible_size': 0.1, 'total_size': 1.0},  # %10 görünür
                risk_level='medium',
                created_at=datetime.now()
            )
        }
        
        self.execution_strategies.update(strategies)
        print("✅ Varsayılan icra stratejileri eklendi")
    
    def create_execution_strategy(self, strategy: ExecutionStrategy) -> bool:
        """
        İcra stratejisi oluştur
        
        Args:
            strategy: Strateji
            
        Returns:
            bool: Başarı durumu
        """
        try:
            if strategy.strategy_id in self.execution_strategies:
                print(f"⚠️ Strateji zaten mevcut: {strategy.strategy_id}")
                return False
            
            self.execution_strategies[strategy.strategy_id] = strategy
            print(f"✅ İcra stratejisi oluşturuldu: {strategy.name}")
            return True
            
        except Exception as e:
            print(f"❌ Strateji oluşturma hatası: {str(e)}")
            return False
    
    def get_execution_strategy(self, strategy_id: str) -> Optional[ExecutionStrategy]:
        """
        İcra stratejisini al
        
        Args:
            strategy_id: Strateji ID
            
        Returns:
            Optional[ExecutionStrategy]: Strateji
        """
        return self.execution_strategies.get(strategy_id)
    
    def update_market_data(self, symbol: str, bid: float, ask: float, last: float,
                           volume: float, volatility: float = 0.0) -> bool:
        """
        Piyasa verisini güncelle
        
        Args:
            symbol: Sembol
            bid: Alış fiyatı
            ask: Satış fiyatı
            last: Son fiyat
            volume: Hacim
            volatility: Volatilite
            
        Returns:
            bool: Başarı durumu
        """
        try:
            spread = ask - bid
            timestamp = datetime.now()
            
            market_data = MarketData(
                symbol=symbol,
                bid=bid,
                ask=ask,
                last=last,
                volume=volume,
                timestamp=timestamp,
                spread=spread,
                volatility=volatility
            )
            
            self.market_data[symbol] = market_data
            return True
            
        except Exception as e:
            print(f"❌ Piyasa verisi güncelleme hatası: {str(e)}")
            return False
    
    def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """
        Piyasa verisini al
        
        Args:
            symbol: Sembol
            
        Returns:
            Optional[MarketData]: Piyasa verisi
        """
        return self.market_data.get(symbol)
    
    def execute_order(self, order_id: str, symbol: str, side: str, quantity: float,
                      strategy_id: str = "market", custom_params: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """
        Siparişi icra et
        
        Args:
            order_id: Sipariş ID
            symbol: Sembol
            side: Yön (buy/sell)
            quantity: Miktar
            strategy_id: Strateji ID
            custom_params: Özel parametreler
            
        Returns:
            ExecutionResult: İcra sonucu
        """
        try:
            # Stratejiyi al
            strategy = self.execution_strategies.get(strategy_id)
            if not strategy:
                raise ValueError(f"Strateji bulunamadı: {strategy_id}")
            
            # Piyasa verisini al
            market_data = self.market_data.get(symbol)
            if not market_data:
                # Varsayılan piyasa verisi oluştur
                market_data = MarketData(
                    symbol=symbol,
                    bid=100.0,
                    ask=100.5,
                    last=100.25,
                    volume=1000000,
                    timestamp=datetime.now(),
                    spread=0.5,
                    volatility=0.15
                )
            
            # İcra fiyatını hesapla
            execution_price = self._calculate_execution_price(
                strategy, market_data, side, quantity, custom_params
            )
            
            # Slippage hesapla
            slippage = self._calculate_slippage(market_data, side, execution_price)
            
            # Piyasa etkisi hesapla
            market_impact = self._calculate_market_impact(symbol, quantity, market_data.volume)
            
            # Komisyon hesapla
            commission = self._calculate_commission(symbol, quantity, execution_price)
            
            # Toplam maliyet
            total_cost = (execution_price * quantity) + commission
            
            # İcra sonucu oluştur
            execution_id = f"exec_{order_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            execution_result = ExecutionResult(
                execution_id=execution_id,
                order_id=order_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=execution_price,
                execution_time=datetime.now(),
                slippage=slippage,
                market_impact=market_impact,
                commission=commission,
                total_cost=total_cost
            )
            
            # Sonucu kaydet
            self.execution_results[execution_id] = execution_result
            
            print(f"✅ Sipariş icra edildi: {execution_id}")
            return execution_result
            
        except Exception as e:
            print(f"❌ Sipariş icra hatası: {str(e)}")
            return ExecutionResult(
                execution_id="", order_id="", symbol="", side="", quantity=0,
                price=0, execution_time=datetime.now(), slippage=0,
                market_impact=0, commission=0, total_cost=0, status="failed",
                message=str(e)
            )
    
    def _calculate_execution_price(self, strategy: ExecutionStrategy, market_data: MarketData,
                                   side: str, quantity: float, custom_params: Optional[Dict[str, Any]]) -> float:
        """İcra fiyatını hesapla"""
        try:
            if strategy.execution_type == "market":
                # Market order: spread ortası
                if side == "buy":
                    return market_data.ask
                else:
                    return market_data.bid
            
            elif strategy.execution_type == "limit":
                # Limit order: belirtilen fiyat
                if custom_params and 'limit_price' in custom_params:
                    return custom_params['limit_price']
                else:
                    # Varsayılan: spread ortası
                    return (market_data.bid + market_data.ask) / 2
            
            elif strategy.execution_type == "twap":
                # TWAP: zaman ağırlıklı ortalama
                duration = strategy.parameters.get('duration', 3600)
                intervals = strategy.parameters.get('intervals', 12)
                
                # Basit TWAP simülasyonu
                base_price = (market_data.bid + market_data.ask) / 2
                time_weights = np.linspace(0, 1, intervals)
                prices = base_price + (np.random.randn(intervals) * market_data.volatility * 0.1)
                
                twap_price = np.average(prices, weights=time_weights)
                return twap_price
            
            elif strategy.execution_type == "vwap":
                # VWAP: hacim ağırlıklı ortalama
                volume_target = strategy.parameters.get('volume_target', 0.8)
                base_price = (market_data.bid + market_data.ask) / 2
                
                # Basit VWAP simülasyonu
                volume_weights = np.random.rand(10)
                volume_weights = volume_weights / volume_weights.sum()
                prices = base_price + (np.random.randn(10) * market_data.volatility * 0.1)
                
                vwap_price = np.average(prices, weights=volume_weights)
                return vwap_price
            
            elif strategy.execution_type == "ice":
                # Iceberg order: görünür miktar
                visible_size = strategy.parameters.get('visible_size', 0.1)
                visible_quantity = quantity * visible_size
                
                # Görünür miktar için fiyat
                if side == "buy":
                    return market_data.ask * (1 + visible_size * 0.01)
                else:
                    return market_data.bid * (1 - visible_size * 0.01)
            
            else:
                # Varsayılan: spread ortası
                return (market_data.bid + market_data.ask) / 2
                
        except Exception as e:
            print(f"❌ İcra fiyatı hesaplama hatası: {str(e)}")
            return (market_data.bid + market_data.ask) / 2
    
    def _calculate_slippage(self, market_data: MarketData, side: str, execution_price: float) -> float:
        """Slippage hesapla"""
        try:
            if side == "buy":
                reference_price = market_data.ask
            else:
                reference_price = market_data.bid
            
            slippage = abs(execution_price - reference_price) / reference_price
            
            # Rastgele slippage ekle
            random_slippage = np.random.normal(0, market_data.volatility * 0.01)
            slippage += abs(random_slippage)
            
            return slippage
            
        except Exception:
            return 0.0
    
    def _calculate_market_impact(self, symbol: str, quantity: float, market_volume: float) -> float:
        """Piyasa etkisini hesapla"""
        try:
            # Basit square root model
            volume_ratio = quantity / market_volume
            impact_score = np.sqrt(volume_ratio)
            
            # Piyasa etki analizi kaydet
            market_impact = MarketImpact(
                symbol=symbol,
                order_size=quantity,
                market_volume=market_volume,
                impact_score=impact_score,
                estimated_slippage=impact_score * 0.01,
                recommended_strategy="twap" if impact_score > 0.1 else "market",
                timestamp=datetime.now()
            )
            
            self.market_impacts[f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"] = market_impact
            
            return impact_score
            
        except Exception:
            return 0.0
    
    def _calculate_commission(self, symbol: str, quantity: float, price: float) -> float:
        """Komisyon hesapla"""
        try:
            # Basit komisyon hesaplama
            commission_rate = 0.0015  # %0.15
            commission = quantity * price * commission_rate
            
            return commission
            
        except Exception:
            return 0.0
    
    def analyze_market_impact(self, symbol: str, order_size: float) -> Dict[str, Any]:
        """
        Piyasa etkisini analiz et
        
        Args:
            symbol: Sembol
            order_size: Sipariş boyutu
            
        Returns:
            Dict[str, Any]: Analiz sonucu
        """
        try:
            market_data = self.market_data.get(symbol)
            if not market_data:
                return {'error': 'Piyasa verisi bulunamadı'}
            
            # Piyasa etki skoru
            volume_ratio = order_size / market_data.volume
            impact_score = np.sqrt(volume_ratio)
            
            # Slippage tahmini
            estimated_slippage = impact_score * 0.01
            
            # Önerilen strateji
            if impact_score > 0.1:
                recommended_strategy = "twap"
            elif impact_score > 0.05:
                recommended_strategy = "vwap"
            else:
                recommended_strategy = "market"
            
            # Risk seviyesi
            if impact_score > 0.15:
                risk_level = "high"
            elif impact_score > 0.08:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            analysis = {
                'symbol': symbol,
                'order_size': order_size,
                'market_volume': market_data.volume,
                'volume_ratio': volume_ratio,
                'impact_score': impact_score,
                'estimated_slippage': estimated_slippage,
                'recommended_strategy': recommended_strategy,
                'risk_level': risk_level,
                'timestamp': datetime.now()
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Piyasa etki analizi hatası: {str(e)}")
            return {'error': str(e)}
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """İcra özetini al"""
        try:
            summary = {
                'total_executions': len(self.execution_results),
                'executions_by_strategy': {},
                'total_volume': 0.0,
                'total_commission': 0.0,
                'total_slippage': 0.0,
                'average_market_impact': 0.0,
                'execution_times': [],
                'symbols_traded': set()
            }
            
            if not self.execution_results:
                return summary
            
            # İstatistikleri hesapla
            for execution in self.execution_results.values():
                summary['total_volume'] += execution.quantity * execution.price
                summary['total_commission'] += execution.commission
                summary['total_slippage'] += execution.slippage
                summary['average_market_impact'] += execution.market_impact
                summary['execution_times'].append(execution.execution_time)
                summary['symbols_traded'].add(execution.symbol)
            
            # Ortalamalar
            summary['average_market_impact'] /= len(self.execution_results)
            summary['symbols_traded'] = list(summary['symbols_traded'])
            
            # Strateji bazında grupla
            for execution in self.execution_results.values():
                strategy = "unknown"
                summary['executions_by_strategy'][strategy] = summary['executions_by_strategy'].get(strategy, 0) + 1
            
            return summary
            
        except Exception as e:
            print(f"❌ İcra özeti alma hatası: {str(e)}")
            return {'error': str(e)}
    
    def get_execution_result(self, execution_id: str) -> Optional[ExecutionResult]:
        """
        İcra sonucunu al
        
        Args:
            execution_id: İcra ID
            
        Returns:
            Optional[ExecutionResult]: İcra sonucu
        """
        return self.execution_results.get(execution_id)
    
    def get_all_execution_results(self) -> List[ExecutionResult]:
        """Tüm icra sonuçlarını al"""
        return list(self.execution_results.values())
    
    def get_market_impact_analysis(self, symbol: str) -> List[MarketImpact]:
        """
        Sembol için piyasa etki analizlerini al
        
        Args:
            symbol: Sembol
            
        Returns:
            List[MarketImpact]: Piyasa etki analizleri
        """
        return [impact for impact in self.market_impacts.values() if impact.symbol == symbol]

# Test fonksiyonu
def test_execution_engine():
    """Execution Engine test fonksiyonu"""
    print("🧪 Execution Engine Test Başlıyor...")
    
    # Execution Engine başlat
    engine = ExecutionEngine()
    
    # Stratejiler test
    print("\n🎯 İcra Stratejileri Test:")
    strategies = engine.execution_strategies
    print(f"   ✅ {len(strategies)} strateji mevcut")
    for strategy_id, strategy in strategies.items():
        print(f"     {strategy.name}: {strategy.description}")
    
    # Yeni strateji oluştur test
    print("\n🏗️ Yeni Strateji Test:")
    custom_strategy = ExecutionStrategy(
        strategy_id='custom',
        name='Özel Strateji',
        description='Özel icra parametreleri',
        execution_type='limit',
        parameters={'custom_param': 'value'},
        risk_level='medium'
    )
    
    strategy_created = engine.create_execution_strategy(custom_strategy)
    print(f"   Yeni strateji oluşturuldu: {strategy_created}")
    
    # Piyasa verisi güncelleme test
    print("\n📊 Piyasa Verisi Güncelleme Test:")
    market_updated = engine.update_market_data(
        symbol="SISE.IS",
        bid=45.00,
        ask=45.50,
        last=45.25,
        volume=1000000,
        volatility=0.15
    )
    
    print(f"   Piyasa verisi güncellendi: {market_updated}")
    
    # Piyasa verisi alma test
    print("\n📥 Piyasa Verisi Alma Test:")
    market_data = engine.get_market_data("SISE.IS")
    if market_data:
        print(f"   ✅ Piyasa verisi alındı: {market_data.symbol}")
        print(f"   📊 Bid: {market_data.bid}, Ask: {market_data.ask}")
        print(f"   📈 Son: {market_data.last}, Hacim: {market_data.volume:,.0f}")
        print(f"   📊 Spread: {market_data.spread:.2f}, Volatilite: {market_data.volatility:.3f}")
    
    # Sipariş icra test
    print("\n⚡ Sipariş İcra Test:")
    execution_result = engine.execute_order(
        order_id="order_1",
        symbol="SISE.IS",
        side="buy",
        quantity=1000,
        strategy_id="market"
    )
    
    if execution_result.execution_id:
        print(f"   ✅ Sipariş icra edildi: {execution_result.execution_id}")
        print(f"   📊 İcra fiyatı: {execution_result.price:.2f}")
        print(f"   ⚠️ Slippage: {execution_result.slippage:.4f}")
        print(f"   📈 Piyasa etkisi: {execution_result.market_impact:.4f}")
        print(f"   💰 Komisyon: {execution_result.commission:.2f}")
        print(f"   💵 Toplam maliyet: {execution_result.total_cost:,.2f}")
    
    # Limit order icra test
    print("\n🛑 Limit Order İcra Test:")
    limit_execution = engine.execute_order(
        order_id="order_2",
        symbol="EREGL.IS",
        side="sell",
        quantity=500,
        strategy_id="limit",
        custom_params={'limit_price': 28.50}
    )
    
    if limit_execution.execution_id:
        print(f"   ✅ Limit order icra edildi: {limit_execution.execution_id}")
        print(f"   📊 İcra fiyatı: {limit_execution.price:.2f}")
    
    # TWAP icra test
    print("\n⏰ TWAP İcra Test:")
    twap_execution = engine.execute_order(
        order_id="order_3",
        symbol="TUPRS.IS",
        side="buy",
        quantity=800,
        strategy_id="twap"
    )
    
    if twap_execution.execution_id:
        print(f"   ✅ TWAP icra edildi: {twap_execution.execution_id}")
        print(f"   📊 İcra fiyatı: {twap_execution.price:.2f}")
    
    # Piyasa etki analizi test
    print("\n🔍 Piyasa Etki Analizi Test:")
    impact_analysis = engine.analyze_market_impact("SISE.IS", 5000)
    if 'error' not in impact_analysis:
        print(f"   ✅ Piyasa etki analizi tamamlandı")
        print(f"   📊 Etki skoru: {impact_analysis['impact_score']:.4f}")
        print(f"   ⚠️ Tahmini slippage: {impact_analysis['estimated_slippage']:.4f}")
        print(f"   🎯 Önerilen strateji: {impact_analysis['recommended_strategy']}")
        print(f"   ⚠️ Risk seviyesi: {impact_analysis['risk_level']}")
    
    # İcra sonucu alma test
    print("\n📥 İcra Sonucu Alma Test:")
    execution_result_retrieved = engine.get_execution_result(execution_result.execution_id)
    if execution_result_retrieved:
        print(f"   ✅ İcra sonucu alındı: {execution_result_retrieved.execution_id}")
    
    # Tüm icra sonuçları test
    print("\n📋 Tüm İcra Sonuçları Test:")
    all_executions = engine.get_all_execution_results()
    print(f"   ✅ Toplam icra: {len(all_executions)}")
    
    # İcra özeti test
    print("\n📊 İcra Özeti Test:")
    execution_summary = engine.get_execution_summary()
    if 'error' not in execution_summary:
        print(f"   ✅ İcra özeti alındı")
        print(f"   📊 Toplam icra: {execution_summary['total_executions']}")
        print(f"   📈 Toplam hacim: {execution_summary['total_volume']:,.2f} TL")
        print(f"   💰 Toplam komisyon: {execution_summary['total_commission']:,.2f} TL")
        print(f"   ⚠️ Toplam slippage: {execution_summary['total_slippage']:.4f}")
        print(f"   📊 Ortalama piyasa etkisi: {execution_summary['average_market_impact']:.4f}")
    
    # Piyasa etki analizleri test
    print("\n📊 Piyasa Etki Analizleri Test:")
    market_impacts = engine.get_market_impact_analysis("SISE.IS")
    print(f"   ✅ {len(market_impacts)} piyasa etki analizi bulundu")
    
    print("\n✅ Execution Engine Test Tamamlandı!")
    
    return engine

if __name__ == "__main__":
    test_execution_engine()
