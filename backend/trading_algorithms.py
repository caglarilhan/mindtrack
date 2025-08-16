"""
PRD v2.0 - BIST AI Smart Trader
Trading Algorithms Module

Alım-satım algoritmaları:
- Technical analysis strategies
- Mean reversion strategies
- Momentum strategies
- Arbitrage strategies
- Algorithmic execution
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class TradingSignal:
    """Alım-satım sinyali"""
    signal_id: str
    symbol: str
    signal_type: str  # buy, sell, hold
    strength: float  # 0-1
    confidence: float  # 0-1
    strategy: str
    timestamp: datetime
    price: float
    quantity: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    metadata: Dict[str, Any] = None

@dataclass
class StrategyPerformance:
    """Strateji performansı"""
    strategy_id: str
    symbol: str
    total_signals: int
    winning_signals: int
    losing_signals: int
    win_rate: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    start_date: datetime
    end_date: datetime
    last_updated: datetime = None

@dataclass
class AlgorithmicOrder:
    """Algoritmik sipariş"""
    order_id: str
    symbol: str
    strategy: str
    order_type: str  # market, limit, stop
    side: str  # buy, sell
    quantity: float
    execution_conditions: Dict[str, Any]
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    status: str = "pending"  # pending, active, filled, cancelled
    created_at: datetime = None
    executed_at: Optional[datetime] = None

@dataclass
class MarketCondition:
    """Piyasa durumu"""
    symbol: str
    timestamp: datetime
    trend: str  # bullish, bearish, sideways
    volatility: float
    volume_trend: str  # increasing, decreasing, stable
    market_regime: str  # trending, ranging, volatile
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None

class TradingAlgorithms:
    """
    Alım-Satım Algoritmaları
    
    PRD v2.0 gereksinimleri:
    - Teknik analiz stratejileri
    - Mean reversion stratejileri
    - Momentum stratejileri
    - Arbitraj stratejileri
    - Algoritmik icra
    """
    
    def __init__(self):
        """Trading Algorithms başlatıcı"""
        # Stratejiler
        self.strategies = {}
        
        # Sinyaller
        self.signals = {}
        
        # Performans
        self.performance = {}
        
        # Algoritmik siparişler
        self.algorithmic_orders = {}
        
        # Piyasa durumları
        self.market_conditions = {}
        
        # Varsayılan stratejileri ekle
        self._add_default_strategies()
        
        # Strateji parametreleri
        self.strategy_params = {
            'ma_short': 20,
            'ma_long': 50,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'bollinger_period': 20,
            'bollinger_std': 2,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9
        }
    
    def _add_default_strategies(self):
        """Varsayılan stratejileri ekle"""
        strategies = {
            'ma_crossover': {
                'name': 'Moving Average Crossover',
                'description': 'Kısa ve uzun vadeli hareketli ortalama kesişimi',
                'type': 'trend_following',
                'parameters': ['ma_short', 'ma_long']
            },
            'rsi_mean_reversion': {
                'name': 'RSI Mean Reversion',
                'description': 'RSI aşırı alım/satım seviyelerinde mean reversion',
                'type': 'mean_reversion',
                'parameters': ['rsi_period', 'rsi_oversold', 'rsi_overbought']
            },
            'bollinger_bands': {
                'name': 'Bollinger Bands',
                'description': 'Bollinger Bands destek/direnç seviyeleri',
                'type': 'mean_reversion',
                'parameters': ['bollinger_period', 'bollinger_std']
            },
            'macd_momentum': {
                'name': 'MACD Momentum',
                'description': 'MACD momentum ve trend değişimi',
                'type': 'momentum',
                'parameters': ['macd_fast', 'macd_slow', 'macd_signal']
            },
            'volume_price_trend': {
                'name': 'Volume Price Trend',
                'description': 'Hacim ve fiyat trendi uyumu',
                'type': 'trend_following',
                'parameters': ['volume_threshold']
            }
        }
        
        self.strategies.update(strategies)
        print("✅ Varsayılan alım-satım stratejileri eklendi")
    
    def calculate_moving_averages(self, prices: pd.Series, short_period: int = 20, long_period: int = 50) -> Tuple[pd.Series, pd.Series]:
        """
        Hareketli ortalamaları hesapla
        
        Args:
            prices: Fiyat serisi
            short_period: Kısa vadeli periyot
            long_period: Uzun vadeli periyot
            
        Returns:
            Tuple[pd.Series, pd.Series]: Kısa ve uzun vadeli ortalamalar
        """
        try:
            ma_short = prices.rolling(window=short_period).mean()
            ma_long = prices.rolling(window=long_period).mean()
            
            return ma_short, ma_long
            
        except Exception as e:
            print(f"❌ Hareketli ortalama hesaplama hatası: {str(e)}")
            return pd.Series(), pd.Series()
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        RSI hesapla
        
        Args:
            prices: Fiyat serisi
            period: Periyot
            
        Returns:
            pd.Series: RSI değerleri
        """
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            print(f"❌ RSI hesaplama hatası: {str(e)}")
            return pd.Series()
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Bollinger Bands hesapla
        
        Args:
            prices: Fiyat serisi
            period: Periyot
            std_dev: Standart sapma çarpanı
            
        Returns:
            Tuple[pd.Series, pd.Series, pd.Series]: Üst, orta, alt bantlar
        """
        try:
            ma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            
            upper_band = ma + (std * std_dev)
            lower_band = ma - (std * std_dev)
            
            return upper_band, ma, lower_band
            
        except Exception as e:
            print(f"❌ Bollinger Bands hesaplama hatası: {str(e)}")
            return pd.Series(), pd.Series(), pd.Series()
    
    def calculate_macd(self, prices: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        MACD hesapla
        
        Args:
            prices: Fiyat serisi
            fast_period: Hızlı periyot
            slow_period: Yavaş periyot
            signal_period: Sinyal periyodu
            
        Returns:
            Tuple[pd.Series, pd.Series, pd.Series]: MACD, sinyal, histogram
        """
        try:
            ema_fast = prices.ewm(span=fast_period).mean()
            ema_slow = prices.ewm(span=slow_period).mean()
            
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal_period).mean()
            histogram = macd_line - signal_line
            
            return macd_line, signal_line, histogram
            
        except Exception as e:
            print(f"❌ MACD hesaplama hatası: {str(e)}")
            return pd.Series(), pd.Series(), pd.Series()
    
    def generate_ma_crossover_signal(self, symbol: str, prices: pd.Series, short_period: int = 20, long_period: int = 50) -> Optional[TradingSignal]:
        """
        MA Crossover sinyali üret
        
        Args:
            symbol: Sembol
            prices: Fiyat serisi
            short_period: Kısa vadeli periyot
            long_period: Uzun vadeli periyot
            
        Returns:
            Optional[TradingSignal]: Alım-satım sinyali
        """
        try:
            if len(prices) < long_period:
                return None
            
            ma_short, ma_long = self.calculate_moving_averages(prices, short_period, long_period)
            
            if ma_short.empty or ma_long.empty:
                return None
            
            # Son iki değer
            current_short = ma_short.iloc[-1]
            current_long = ma_long.iloc[-1]
            prev_short = ma_short.iloc[-2]
            prev_long = ma_long.iloc[-2]
            
            # Kesişim kontrolü
            signal_type = "hold"
            strength = 0.0
            
            if current_short > current_long and prev_short <= prev_long:
                # Bullish crossover
                signal_type = "buy"
                strength = min(1.0, abs(current_short - current_long) / current_long)
            elif current_short < current_long and prev_short >= prev_long:
                # Bearish crossover
                signal_type = "sell"
                strength = min(1.0, abs(current_short - current_long) / current_long)
            
            if signal_type != "hold":
                signal = TradingSignal(
                    signal_id=f"signal_{symbol}_{signal_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    symbol=symbol,
                    signal_type=signal_type,
                    strength=strength,
                    confidence=min(0.9, strength + 0.3),
                    strategy="ma_crossover",
                    timestamp=datetime.now(),
                    price=prices.iloc[-1],
                    metadata={
                        'ma_short': current_short,
                        'ma_long': current_long,
                        'short_period': short_period,
                        'long_period': long_period
                    }
                )
                
                self.signals[signal.signal_id] = signal
                return signal
            
            return None
            
        except Exception as e:
            print(f"❌ MA Crossover sinyal hatası: {str(e)}")
            return None
    
    def generate_rsi_signal(self, symbol: str, prices: pd.Series, period: int = 14, oversold: int = 30, overbought: int = 70) -> Optional[TradingSignal]:
        """
        RSI sinyali üret
        
        Args:
            symbol: Sembol
            prices: Fiyat serisi
            period: RSI periyodu
            oversold: Aşırı satım seviyesi
            overbought: Aşırı alım seviyesi
            
        Returns:
            Optional[TradingSignal]: Alım-satım sinyali
        """
        try:
            if len(prices) < period:
                return None
            
            rsi = self.calculate_rsi(prices, period)
            
            if rsi.empty:
                return None
            
            current_rsi = rsi.iloc[-1]
            prev_rsi = rsi.iloc[-2]
            
            signal_type = "hold"
            strength = 0.0
            
            if current_rsi < oversold and prev_rsi >= oversold:
                # Oversold - buy signal
                signal_type = "buy"
                strength = (oversold - current_rsi) / oversold
            elif current_rsi > overbought and prev_rsi <= overbought:
                # Overbought - sell signal
                signal_type = "sell"
                strength = (current_rsi - overbought) / (100 - overbought)
            
            if signal_type != "hold":
                signal = TradingSignal(
                    signal_id=f"signal_{symbol}_{signal_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    symbol=symbol,
                    signal_type=signal_type,
                    strength=strength,
                    confidence=min(0.8, strength + 0.4),
                    strategy="rsi_mean_reversion",
                    timestamp=datetime.now(),
                    price=prices.iloc[-1],
                    metadata={
                        'rsi': current_rsi,
                        'period': period,
                        'oversold': oversold,
                        'overbought': overbought
                    }
                )
                
                self.signals[signal.signal_id] = signal
                return signal
            
            return None
            
        except Exception as e:
            print(f"❌ RSI sinyal hatası: {str(e)}")
            return None
    
    def generate_bollinger_signal(self, symbol: str, prices: pd.Series, period: int = 20, std_dev: float = 2) -> Optional[TradingSignal]:
        """
        Bollinger Bands sinyali üret
        
        Args:
            symbol: Sembol
            prices: Fiyat serisi
            period: Periyot
            std_dev: Standart sapma çarpanı
            
        Returns:
            Optional[TradingSignal]: Alım-satım sinyali
        """
        try:
            if len(prices) < period:
                return None
            
            upper_band, middle_band, lower_band = self.calculate_bollinger_bands(prices, period, std_dev)
            
            if upper_band.empty or lower_band.empty:
                return None
            
            current_price = prices.iloc[-1]
            current_upper = upper_band.iloc[-1]
            current_lower = lower_band.iloc[-1]
            current_middle = middle_band.iloc[-1]
            
            signal_type = "hold"
            strength = 0.0
            
            if current_price <= current_lower:
                # Price at lower band - buy signal
                signal_type = "buy"
                strength = (current_middle - current_price) / (current_middle - current_lower)
            elif current_price >= current_upper:
                # Price at upper band - sell signal
                signal_type = "sell"
                strength = (current_price - current_middle) / (current_upper - current_middle)
            
            if signal_type != "hold":
                signal = TradingSignal(
                    signal_id=f"signal_{symbol}_{signal_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    symbol=symbol,
                    signal_type=signal_type,
                    strength=strength,
                    confidence=min(0.85, strength + 0.35),
                    strategy="bollinger_bands",
                    timestamp=datetime.now(),
                    price=current_price,
                    metadata={
                        'upper_band': current_upper,
                        'middle_band': current_middle,
                        'lower_band': current_lower,
                        'period': period,
                        'std_dev': std_dev
                    }
                )
                
                self.signals[signal.signal_id] = signal
                return signal
            
            return None
            
        except Exception as e:
            print(f"❌ Bollinger Bands sinyal hatası: {str(e)}")
            return None
    
    def generate_macd_signal(self, symbol: str, prices: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Optional[TradingSignal]:
        """
        MACD sinyali üret
        
        Args:
            symbol: Sembol
            prices: Fiyat serisi
            fast_period: Hızlı periyot
            slow_period: Yavaş periyot
            signal_period: Sinyal periyodu
            
        Returns:
            Optional[TradingSignal]: Alım-satım sinyali
        """
        try:
            if len(prices) < slow_period:
                return None
            
            macd_line, signal_line, histogram = self.calculate_macd(prices, fast_period, slow_period, signal_period)
            
            if macd_line.empty or signal_line.empty:
                return None
            
            current_macd = macd_line.iloc[-1]
            current_signal = signal_line.iloc[-1]
            prev_macd = macd_line.iloc[-2]
            prev_signal = signal_line.iloc[-2]
            
            signal_type = "hold"
            strength = 0.0
            
            if current_macd > current_signal and prev_macd <= prev_signal:
                # Bullish crossover
                signal_type = "buy"
                strength = min(1.0, abs(current_macd - current_signal) / abs(current_signal) if current_signal != 0 else 0.5)
            elif current_macd < current_signal and prev_macd >= prev_signal:
                # Bearish crossover
                signal_type = "sell"
                strength = min(1.0, abs(current_macd - current_signal) / abs(current_signal) if current_signal != 0 else 0.5)
            
            if signal_type != "hold":
                signal = TradingSignal(
                    signal_id=f"signal_{symbol}_{signal_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    symbol=symbol,
                    signal_type=signal_type,
                    strength=strength,
                    confidence=min(0.9, strength + 0.3),
                    strategy="macd_momentum",
                    timestamp=datetime.now(),
                    price=prices.iloc[-1],
                    metadata={
                        'macd': current_macd,
                        'signal': current_signal,
                        'histogram': histogram.iloc[-1] if not histogram.empty else 0,
                        'fast_period': fast_period,
                        'slow_period': slow_period,
                        'signal_period': signal_period
                    }
                )
                
                self.signals[signal.signal_id] = signal
                return signal
            
            return None
            
        except Exception as e:
            print(f"❌ MACD sinyal hatası: {str(e)}")
            return None
    
    def analyze_market_condition(self, symbol: str, prices: pd.Series, volumes: pd.Series) -> MarketCondition:
        """
        Piyasa durumunu analiz et
        
        Args:
            symbol: Sembol
            prices: Fiyat serisi
            volumes: Hacim serisi
            
        Returns:
            MarketCondition: Piyasa durumu
        """
        try:
            if len(prices) < 20:
                return MarketCondition(
                    symbol=symbol,
                    timestamp=datetime.now(),
                    trend="unknown",
                    volatility=0.0,
                    volume_trend="unknown",
                    market_regime="unknown"
                )
            
            # Trend analizi
            ma_20 = prices.rolling(window=20).mean()
            ma_50 = prices.rolling(window=50).mean() if len(prices) >= 50 else ma_20
            
            current_price = prices.iloc[-1]
            current_ma20 = ma_20.iloc[-1]
            current_ma50 = ma_50.iloc[-1]
            
            if current_price > current_ma20 > current_ma50:
                trend = "bullish"
            elif current_price < current_ma20 < current_ma50:
                trend = "bearish"
            else:
                trend = "sideways"
            
            # Volatilite
            returns = prices.pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # Yıllık volatilite
            
            # Hacim trendi
            recent_volumes = volumes.tail(10)
            volume_trend = "stable"
            if len(recent_volumes) >= 5:
                first_half = recent_volumes.head(5).mean()
                second_half = recent_volumes.tail(5).mean()
                
                if second_half > first_half * 1.2:
                    volume_trend = "increasing"
                elif second_half < first_half * 0.8:
                    volume_trend = "decreasing"
            
            # Piyasa rejimi
            if volatility > 0.3:
                market_regime = "volatile"
            elif trend in ["bullish", "bearish"]:
                market_regime = "trending"
            else:
                market_regime = "ranging"
            
            # Destek/direnç seviyeleri
            support_level = prices.tail(20).min()
            resistance_level = prices.tail(20).max()
            
            market_condition = MarketCondition(
                symbol=symbol,
                timestamp=datetime.now(),
                trend=trend,
                volatility=volatility,
                volume_trend=volume_trend,
                market_regime=market_regime,
                support_level=support_level,
                resistance_level=resistance_level
            )
            
            self.market_conditions[f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"] = market_condition
            
            return market_condition
            
        except Exception as e:
            print(f"❌ Piyasa durumu analiz hatası: {str(e)}")
            return MarketCondition(
                symbol=symbol,
                timestamp=datetime.now(),
                trend="unknown",
                volatility=0.0,
                volume_trend="unknown",
                market_regime="unknown"
            )
    
    def create_algorithmic_order(self, signal: TradingSignal, order_type: str = "market",
                                 execution_conditions: Optional[Dict[str, Any]] = None) -> AlgorithmicOrder:
        """
        Algoritmik sipariş oluştur
        
        Args:
            signal: Alım-satım sinyali
            order_type: Sipariş türü
            execution_conditions: İcra koşulları
            
        Returns:
            AlgorithmicOrder: Algoritmik sipariş
        """
        try:
            if execution_conditions is None:
                execution_conditions = {
                    'time_limit': 3600,  # 1 saat
                    'price_limit': signal.price * 0.02,  # %2 fiyat limiti
                    'volume_condition': 'market_open'
                }
            
            order = AlgorithmicOrder(
                order_id=f"algo_{signal.signal_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                symbol=signal.symbol,
                strategy=signal.strategy,
                order_type=order_type,
                side=signal.signal_type,
                quantity=1000,  # Varsayılan miktar
                price=signal.price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                execution_conditions=execution_conditions,
                created_at=datetime.now()
            )
            
            self.algorithmic_orders[order.order_id] = order
            print(f"✅ Algoritmik sipariş oluşturuldu: {order.order_id}")
            
            return order
            
        except Exception as e:
            print(f"❌ Algoritmik sipariş oluşturma hatası: {str(e)}")
            return AlgorithmicOrder(
                order_id="", symbol="", strategy="", order_type="", side="", quantity=0
            )
    
    def get_signals_by_strategy(self, strategy: str) -> List[TradingSignal]:
        """
        Stratejiye göre sinyalleri al
        
        Args:
            strategy: Strateji adı
            
        Returns:
            List[TradingSignal]: Sinyal listesi
        """
        return [signal for signal in self.signals.values() if signal.strategy == strategy]
    
    def get_signals_by_symbol(self, symbol: str) -> List[TradingSignal]:
        """
        Sembole göre sinyalleri al
        
        Args:
            symbol: Sembol
            
        Returns:
            List[TradingSignal]: Sinyal listesi
        """
        return [signal for signal in self.signals.values() if signal.symbol == symbol]
    
    def get_algorithmic_orders(self, status: Optional[str] = None) -> List[AlgorithmicOrder]:
        """
        Algoritmik siparişleri al
        
        Args:
            status: Sipariş durumu
            
        Returns:
            List[AlgorithmicOrder]: Sipariş listesi
        """
        if status:
            return [order for order in self.algorithmic_orders.values() if order.status == status]
        return list(self.algorithmic_orders.values())
    
    def get_trading_summary(self) -> Dict[str, Any]:
        """Alım-satım özetini al"""
        try:
            summary = {
                'total_signals': len(self.signals),
                'signals_by_type': {},
                'signals_by_strategy': {},
                'total_orders': len(self.algorithmic_orders),
                'orders_by_status': {},
                'total_strategies': len(self.strategies),
                'market_conditions': len(self.market_conditions)
            }
            
            # Sinyal türü bazında grupla
            for signal in self.signals.values():
                if signal.signal_type not in summary['signals_by_type']:
                    summary['signals_by_type'][signal.signal_type] = 0
                summary['signals_by_type'][signal.signal_type] += 1
                
                if signal.strategy not in summary['signals_by_strategy']:
                    summary['signals_by_strategy'][signal.strategy] = 0
                summary['signals_by_strategy'][signal.strategy] += 1
            
            # Sipariş durumu bazında grupla
            for order in self.algorithmic_orders.values():
                if order.status not in summary['orders_by_status']:
                    summary['orders_by_status'][order.status] = 0
                summary['orders_by_status'][order.status] += 1
            
            return summary
            
        except Exception as e:
            print(f"❌ Alım-satım özeti alma hatası: {str(e)}")
            return {'error': str(e)}

# Test fonksiyonu
def test_trading_algorithms():
    """Trading Algorithms test fonksiyonu"""
    print("🧪 Trading Algorithms Test Başlıyor...")
    
    # Trading Algorithms başlat
    ta = TradingAlgorithms()
    
    # Stratejiler test
    print("\n🎯 Alım-Satım Stratejileri Test:")
    strategies = ta.strategies
    print(f"   ✅ {len(strategies)} strateji mevcut")
    for strategy_id, strategy in strategies.items():
        print(f"     {strategy['name']}: {strategy['description']}")
        print(f"       Tür: {strategy['type']}, Parametreler: {strategy['parameters']}")
    
    # Test verisi oluştur
    print("\n📊 Test Verisi Oluşturma:")
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)
    
    # Trendli fiyat verisi
    trend = np.linspace(100, 120, len(dates))
    noise = np.random.normal(0, 2, len(dates))
    prices = pd.Series(trend + noise, index=dates)
    
    # Hacim verisi
    volumes = pd.Series(np.random.randint(1000000, 5000000, len(dates)), index=dates)
    
    print(f"   ✅ Test verisi oluşturuldu: {len(prices)} gün")
    print(f"   📊 Fiyat aralığı: {prices.min():.2f} - {prices.max():.2f}")
    print(f"   📊 Hacim aralığı: {volumes.min():,} - {volumes.max():,}")
    
    # Teknik indikatör hesaplama test
    print("\n🧮 Teknik İndikatör Hesaplama Test:")
    
    # Moving Average
    ma_short, ma_long = ta.calculate_moving_averages(prices, 20, 50)
    print(f"   ✅ Moving Average hesaplandı: {len(ma_short)} değer")
    
    # RSI
    rsi = ta.calculate_rsi(prices, 14)
    print(f"   ✅ RSI hesaplandı: {len(rsi)} değer")
    
    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = ta.calculate_bollinger_bands(prices, 20, 2)
    print(f"   ✅ Bollinger Bands hesaplandı: {len(bb_upper)} değer")
    
    # MACD
    macd_line, macd_signal, macd_histogram = ta.calculate_macd(prices, 12, 26, 9)
    print(f"   ✅ MACD hesaplandı: {len(macd_line)} değer")
    
    # Sinyal üretme test
    print("\n📡 Sinyal Üretme Test:")
    
    # MA Crossover sinyali
    ma_signal = ta.generate_ma_crossover_signal("SISE.IS", prices, 20, 50)
    if ma_signal:
        print(f"   ✅ MA Crossover sinyali: {ma_signal.signal_type} (güç: {ma_signal.strength:.3f})")
    else:
        print("   ⚠️ MA Crossover sinyali üretilemedi")
    
    # RSI sinyali
    rsi_signal = ta.generate_rsi_signal("SISE.IS", prices, 14, 30, 70)
    if rsi_signal:
        print(f"   ✅ RSI sinyali: {rsi_signal.signal_type} (güç: {rsi_signal.strength:.3f})")
    else:
        print("   ⚠️ RSI sinyali üretilemedi")
    
    # Bollinger Bands sinyali
    bb_signal = ta.generate_bollinger_signal("SISE.IS", prices, 20, 2)
    if bb_signal:
        print(f"   ✅ Bollinger Bands sinyali: {bb_signal.signal_type} (güç: {bb_signal.strength:.3f})")
    else:
        print("   ⚠️ Bollinger Bands sinyali üretilemedi")
    
    # MACD sinyali
    macd_signal = ta.generate_macd_signal("SISE.IS", prices, 12, 26, 9)
    if macd_signal:
        print(f"   ✅ MACD sinyali: {macd_signal.signal_type} (güç: {macd_signal.strength:.3f})")
    else:
        print("   ⚠️ MACD sinyali üretilemedi")
    
    # Piyasa durumu analizi test
    print("\n🔍 Piyasa Durumu Analizi Test:")
    market_condition = ta.analyze_market_condition("SISE.IS", prices, volumes)
    print(f"   ✅ Piyasa durumu analiz edildi")
    print(f"   📊 Trend: {market_condition.trend}")
    print(f"   📊 Volatilite: {market_condition.volatility:.3f}")
    print(f"   📊 Hacim trendi: {market_condition.volume_trend}")
    print(f"   📊 Piyasa rejimi: {market_condition.market_regime}")
    
    # Algoritmik sipariş oluşturma test
    print("\n🤖 Algoritmik Sipariş Test:")
    if ma_signal:
        algo_order = ta.create_algorithmic_order(ma_signal, "limit")
        print(f"   ✅ Algoritmik sipariş oluşturuldu: {algo_order.order_id}")
        print(f"   📊 Sipariş türü: {algo_order.order_type}")
        print(f"   📊 Yön: {algo_order.side}")
        print(f"   📊 Miktar: {algo_order.quantity}")
    
    # Sinyal listesi test
    print("\n📋 Sinyal Listesi Test:")
    all_signals = list(ta.signals.values())
    print(f"   ✅ Toplam sinyal: {len(all_signals)}")
    
    for signal in all_signals:
        print(f"     {signal.symbol}: {signal.signal_type} ({signal.strategy}) - Güç: {signal.strength:.3f}")
    
    # Strateji bazında sinyaller test
    print("\n🎯 Strateji Bazında Sinyaller Test:")
    for strategy_name in ta.strategies.keys():
        strategy_signals = ta.get_signals_by_strategy(strategy_name)
        print(f"   {strategy_name}: {len(strategy_signals)} sinyal")
    
    # Algoritmik siparişler test
    print("\n🤖 Algoritmik Siparişler Test:")
    all_orders = ta.get_algorithmic_orders()
    print(f"   ✅ Toplam sipariş: {len(all_orders)}")
    
    for order in all_orders:
        print(f"     {order.order_id}: {order.side} {order.quantity} {order.symbol}")
    
    # Alım-satım özeti test
    print("\n📊 Alım-Satım Özeti Test:")
    trading_summary = ta.get_trading_summary()
    if 'error' not in trading_summary:
        print(f"   ✅ Alım-satım özeti alındı")
        print(f"   📊 Toplam sinyal: {trading_summary['total_signals']}")
        print(f"   📊 Toplam sipariş: {trading_summary['total_orders']}")
        print(f"   📊 Toplam strateji: {trading_summary['total_strategies']}")
        print(f"   📊 Piyasa durumları: {trading_summary['market_conditions']}")
        
        print(f"   📊 Sinyal türleri: {trading_summary['signals_by_type']}")
        print(f"   📊 Strateji bazında: {trading_summary['signals_by_strategy']}")
        print(f"   📊 Sipariş durumları: {trading_summary['orders_by_status']}")
    
    print("\n✅ Trading Algorithms Test Tamamlandı!")
    
    return ta

if __name__ == "__main__":
    test_trading_algorithms()
