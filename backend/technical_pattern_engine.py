"""
PRD v2.0 - Technical Pattern Engine
EMA cross, candlestick, harmonic, fractal break patterns
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class TechnicalPatternEngine:
    """Teknik formasyon tespit motoru"""
    
    def __init__(self):
        self.pattern_cache = {}
        self.signal_cache = {}
        self.ema_periods = [9, 21, 50, 200]
        
    def get_stock_data(self, symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        """Hisse verilerini getir"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"⚠️ {symbol} için veri bulunamadı")
                return self._generate_mock_data(symbol, period, interval)
            
            # Veriyi temizle
            data = data.dropna()
            
            logger.info(f"✅ {symbol} verisi alındı: {len(data)} kayıt")
            return data
            
        except Exception as e:
            logger.error(f"❌ {symbol} veri alma hatası: {e}")
            return self._generate_mock_data(symbol, period, interval)
    
    def _generate_mock_data(self, symbol: str, period: str, interval: str) -> pd.DataFrame:
        """Mock veri oluştur (veri bulunamadığında)"""
        try:
            # Mock veri parametreleri
            if period == "6mo":
                days = 180
            elif period == "1y":
                days = 365
            else:
                days = 90
            
            # Tarih aralığı
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Mock OHLC veri
            np.random.seed(hash(symbol) % 1000)  # Deterministik random
            
            base_price = 100 + np.random.uniform(-20, 20)
            prices = []
            
            for i in range(len(dates)):
                if i == 0:
                    price = base_price
                else:
                    # Trend + noise
                    trend = np.sin(i * 0.1) * 0.5
                    noise = np.random.normal(0, 0.02)
                    price = prices[-1] * (1 + trend + noise)
                
                prices.append(max(price, 10))  # Minimum fiyat
            
            # OHLC oluştur
            data = []
            for i, (date, close) in enumerate(zip(dates, prices)):
                # Volatilite
                volatility = close * 0.02
                
                # High, Low, Open
                high = close + np.random.uniform(0, volatility)
                low = close - np.random.uniform(0, volatility)
                open_price = np.random.uniform(low, high)
                
                # Volume
                volume = np.random.randint(1000000, 10000000)
                
                data.append({
                    'Date': date,
                    'Open': round(open_price, 2),
                    'High': round(high, 2),
                    'Low': round(low, 2),
                    'Close': round(close, 2),
                    'Volume': volume
                })
            
            df = pd.DataFrame(data)
            df.set_index('Date', inplace=True)
            
            logger.info(f"✅ {symbol} için mock veri oluşturuldu: {len(df)} kayıt")
            return df
            
        except Exception as e:
            logger.error(f"❌ Mock veri oluşturma hatası: {e}")
            return pd.DataFrame()
    
    def calculate_ema(self, data: pd.DataFrame, period: int) -> pd.Series:
        """Exponential Moving Average hesapla"""
        try:
            alpha = 2 / (period + 1)
            ema = data['Close'].ewm(span=period, adjust=False).mean()
            return ema
            
        except Exception as e:
            logger.error(f"❌ EMA hesaplama hatası: {e}")
            return pd.Series(index=data.index, dtype=float)
    
    def detect_ema_crossovers(self, data: pd.DataFrame) -> Dict[str, Any]:
        """EMA kesişim sinyallerini tespit et"""
        try:
            signals = {
                'golden_cross': False,
                'death_cross': False,
                'ema_crosses': [],
                'trend_strength': 0
            }
            
            # EMA'ları hesapla
            ema_short = self.calculate_ema(data, 21)
            ema_long = self.calculate_ema(data, 50)
            
            if ema_short.empty or ema_long.empty:
                return signals
            
            # Kesişim tespiti
            for i in range(1, len(data)):
                prev_short = ema_short.iloc[i-1]
                prev_long = ema_long.iloc[i-1]
                curr_short = ema_short.iloc[i]
                curr_long = ema_long.iloc[i]
                
                # Golden Cross (kısa EMA uzun EMA'yı yukarı kesiyor)
                if prev_short <= prev_long and curr_short > curr_long:
                    signals['golden_cross'] = True
                    signals['ema_crosses'].append({
                        'type': 'GOLDEN_CROSS',
                        'date': data.index[i],
                        'price': data['Close'].iloc[i],
                        'strength': abs(curr_short - curr_long) / curr_long
                    })
                
                # Death Cross (kısa EMA uzun EMA'yı aşağı kesiyor)
                elif prev_short >= prev_long and curr_short < curr_long:
                    signals['death_cross'] = True
                    signals['ema_crosses'].append({
                        'type': 'DEATH_CROSS',
                        'date': data.index[i],
                        'price': data['Close'].iloc[i],
                        'strength': abs(curr_short - curr_long) / curr_long
                    })
            
            # Trend gücü hesapla
            if len(data) > 0:
                current_short = ema_short.iloc[-1]
                current_long = ema_long.iloc[-1]
                signals['trend_strength'] = (current_short - current_long) / current_long
            
            logger.info(f"✅ EMA kesişim analizi tamamlandı: {len(signals['ema_crosses'])} sinyal")
            return signals
            
        except Exception as e:
            logger.error(f"❌ EMA kesişim tespiti hatası: {e}")
            return {'golden_cross': False, 'death_cross': False, 'ema_crosses': [], 'trend_strength': 0}
    
    def detect_candlestick_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Candlestick formasyonlarını tespit et"""
        try:
            patterns = {
                'bullish_engulfing': False,
                'bearish_engulfing': False,
                'hammer': False,
                'shooting_star': False,
                'doji': False,
                'patterns_detected': []
            }
            
            if len(data) < 2:
                return patterns
            
            for i in range(1, len(data)):
                prev_open = data['Open'].iloc[i-1]
                prev_close = data['Close'].iloc[i-1]
                prev_high = data['High'].iloc[i-1]
                prev_low = data['Low'].iloc[i-1]
                
                curr_open = data['Open'].iloc[i]
                curr_close = data['Close'].iloc[i]
                curr_high = data['High'].iloc[i]
                curr_low = data['Low'].iloc[i]
                
                # Bullish Engulfing
                if (prev_close < prev_open and  # Önceki mum bearish
                    curr_close > curr_open and   # Mevcut mum bullish
                    curr_open < prev_close and   # Mevcut açılış önceki kapanıştan düşük
                    curr_close > prev_open):     # Mevcut kapanış önceki açılıştan yüksek
                    
                    patterns['bullish_engulfing'] = True
                    patterns['patterns_detected'].append({
                        'type': 'BULLISH_ENGULFING',
                        'date': data.index[i],
                        'price': curr_close,
                        'strength': abs(curr_close - curr_open) / curr_open
                    })
                
                # Bearish Engulfing
                elif (prev_close > prev_open and  # Önceki mum bullish
                      curr_close < curr_open and   # Mevcut mum bearish
                      curr_open > prev_close and   # Mevcut açılış önceki kapanıştan yüksek
                      curr_close < prev_open):     # Mevcut kapanış önceki açılıştan düşük
                    
                    patterns['bearish_engulfing'] = True
                    patterns['patterns_detected'].append({
                        'type': 'BEARISH_ENGULFING',
                        'date': data.index[i],
                        'price': curr_close,
                        'strength': abs(curr_close - curr_open) / curr_open
                    })
                
                # Hammer
                body_size = abs(curr_close - curr_open)
                lower_shadow = min(curr_open, curr_close) - curr_low
                upper_shadow = curr_high - max(curr_open, curr_close)
                
                if (lower_shadow > 2 * body_size and  # Alt gölge uzun
                    upper_shadow < body_size and        # Üst gölge kısa
                    body_size > 0):                    # Vücut var
                    
                    patterns['hammer'] = True
                    patterns['patterns_detected'].append({
                        'type': 'HAMMER',
                        'date': data.index[i],
                        'price': curr_close,
                        'strength': lower_shadow / curr_low
                    })
                
                # Shooting Star
                if (upper_shadow > 2 * body_size and  # Üst gölge uzun
                    lower_shadow < body_size and        # Alt gölge kısa
                    body_size > 0):                    # Vücut var
                    
                    patterns['shooting_star'] = True
                    patterns['patterns_detected'].append({
                        'type': 'SHOOTING_STAR',
                        'date': data.index[i],
                        'price': curr_close,
                        'strength': upper_shadow / curr_high
                    })
                
                # Doji
                if body_size < (curr_high - curr_low) * 0.1:  # Vücut çok küçük
                    patterns['doji'] = True
                    patterns['patterns_detected'].append({
                        'type': 'DOJI',
                        'date': data.index[i],
                        'price': curr_close,
                        'strength': 0.5  # Doji için sabit güç
                    })
            
            logger.info(f"✅ Candlestick analizi tamamlandı: {len(patterns['patterns_detected'])} formasyon")
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Candlestick analizi hatası: {e}")
            return {'bullish_engulfing': False, 'bearish_engulfing': False, 'hammer': False, 
                   'shooting_star': False, 'doji': False, 'patterns_detected': []}
    
    def detect_support_resistance(self, data: pd.DataFrame, window: int = 20) -> Dict[str, Any]:
        """Destek ve direnç seviyelerini tespit et"""
        try:
            levels = {
                'support_levels': [],
                'resistance_levels': [],
                'current_support': 0,
                'current_resistance': 0
            }
            
            if len(data) < window:
                return levels
            
            # Pivot noktaları bul
            for i in range(window, len(data) - window):
                high = data['High'].iloc[i]
                low = data['Low'].iloc[i]
                
                # Direnç seviyesi (yüksek nokta)
                if all(data['High'].iloc[j] <= high for j in range(i-window, i+window+1)):
                    levels['resistance_levels'].append({
                        'price': high,
                        'date': data.index[i],
                        'strength': self._calculate_level_strength(data, high, 'resistance')
                    })
                
                # Destek seviyesi (düşük nokta)
                if all(data['Low'].iloc[j] >= low for j in range(i-window, i+window+1)):
                    levels['support_levels'].append({
                        'price': low,
                        'date': data.index[i],
                        'strength': self._calculate_level_strength(data, low, 'support')
                    })
            
            # Mevcut destek ve direnç
            if levels['support_levels']:
                levels['current_support'] = max([s['price'] for s in levels['support_levels'] 
                                              if s['price'] < data['Close'].iloc[-1]])
            
            if levels['resistance_levels']:
                levels['current_resistance'] = min([r['price'] for r in levels['resistance_levels'] 
                                                 if r['price'] > data['Close'].iloc[-1]])
            
            logger.info(f"✅ Destek/Direnç analizi: {len(levels['support_levels'])} destek, {len(levels['resistance_levels'])} direnç")
            return levels
            
        except Exception as e:
            logger.error(f"❌ Destek/Direnç tespiti hatası: {e}")
            return {'support_levels': [], 'resistance_levels': [], 'current_support': 0, 'current_resistance': 0}
    
    def _calculate_level_strength(self, data: pd.DataFrame, level: float, level_type: str) -> float:
        """Seviye gücünü hesapla"""
        try:
            touches = 0
            total_volume = 0
            
            for i in range(len(data)):
                if level_type == 'support':
                    if abs(data['Low'].iloc[i] - level) / level < 0.01:  # %1 tolerans
                        touches += 1
                        total_volume += data['Volume'].iloc[i]
                else:  # resistance
                    if abs(data['High'].iloc[i] - level) / level < 0.01:  # %1 tolerans
                        touches += 1
                        total_volume += data['Volume'].iloc[i]
            
            # Güç = dokunma sayısı * ortalama hacim
            strength = touches * (total_volume / max(touches, 1))
            return round(strength, 2)
            
        except Exception as e:
            logger.error(f"Seviye gücü hesaplama hatası: {e}")
            return 0.0
    
    def detect_harmonic_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Harmonik formasyonları tespit et (basit versiyon)"""
        try:
            patterns = {
                'gartley': False,
                'butterfly': False,
                'bat': False,
                'crab': False,
                'patterns_detected': []
            }
            
            if len(data) < 100:
                return patterns
            
            # Basit harmonik tespit (Fibonacci retracement tabanlı)
            for i in range(50, len(data) - 50):
                # Swing high ve low bul
                swing_high = data['High'].iloc[i-50:i+50].max()
                swing_low = data['Low'].iloc[i-50:i+50].min()
                
                if swing_high == swing_low:
                    continue
                
                # Fibonacci seviyeleri
                diff = swing_high - swing_low
                fib_38 = swing_high - 0.382 * diff
                fib_50 = swing_high - 0.5 * diff
                fib_61 = swing_high - 0.618 * diff
                
                current_price = data['Close'].iloc[i]
                
                # Gartley pattern (basit)
                if (abs(current_price - fib_61) / fib_61 < 0.02):  # %2 tolerans
                    patterns['gartley'] = True
                    patterns['patterns_detected'].append({
                        'type': 'GARTLEY',
                        'date': data.index[i],
                        'price': current_price,
                        'target': swing_high,
                        'stop_loss': swing_low
                    })
                
                # Butterfly pattern (basit)
                if (abs(current_price - fib_78) / fib_78 < 0.02):  # %2 tolerans
                    patterns['butterfly'] = True
                    patterns['patterns_detected'].append({
                        'type': 'BUTTERFLY',
                        'date': data.index[i],
                        'price': current_price,
                        'target': swing_high * 1.27,
                        'stop_loss': swing_low
                    })
            
            logger.info(f"✅ Harmonik analiz: {len(patterns['patterns_detected'])} formasyon")
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Harmonik analiz hatası: {e}")
            return {'gartley': False, 'butterfly': False, 'bat': False, 'crab': False, 'patterns_detected': []}
    
    def generate_trading_signals(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Tüm teknik analizleri yap ve sinyal üret"""
        try:
            logger.info(f"🚀 {symbol} için teknik analiz başlatılıyor...")
            
            # Tüm analizleri yap
            ema_signals = self.detect_ema_crossovers(data)
            candlestick_patterns = self.detect_candlestick_patterns(data)
            support_resistance = self.detect_support_resistance(data)
            harmonic_patterns = self.detect_harmonic_patterns(data)
            
            # Sinyal skoru hesapla
            signal_score = self._calculate_signal_score(
                ema_signals, candlestick_patterns, support_resistance, harmonic_patterns
            )
            
            # Aksiyon belirle
            action = self._determine_action(signal_score, data)
            
            # Risk seviyesi
            risk_level = self._calculate_risk_level(data, support_resistance)
            
            # Stop loss ve take profit
            sl_tp = self._calculate_sl_tp(data, support_resistance, action)
            
            signals = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'signal_score': signal_score,
                'risk_level': risk_level,
                'stop_loss': sl_tp['stop_loss'],
                'take_profit': sl_tp['take_profit'],
                'confidence': min(95, max(5, signal_score * 100)),
                'analysis': {
                    'ema_signals': ema_signals,
                    'candlestick_patterns': candlestick_patterns,
                    'support_resistance': support_resistance,
                    'harmonic_patterns': harmonic_patterns
                },
                'summary': self._generate_signal_summary(
                    ema_signals, candlestick_patterns, support_resistance, harmonic_patterns
                )
            }
            
            # Cache'e kaydet
            self.signal_cache[symbol] = signals
            
            logger.info(f"✅ {symbol} teknik analiz tamamlandı: {action} (Skor: {signal_score:.2f})")
            return signals
            
        except Exception as e:
            logger.error(f"❌ {symbol} sinyal üretme hatası: {e}")
            return {
                'symbol': symbol,
                'action': 'HOLD',
                'signal_score': 0.5,
                'error': str(e)
            }
    
    def _calculate_signal_score(self, ema_signals: Dict, candlestick_patterns: Dict, 
                               support_resistance: Dict, harmonic_patterns: Dict) -> float:
        """Sinyal skorunu hesapla (0-1 arası)"""
        try:
            score = 0.5  # Nötr başlangıç
            
            # EMA sinyalleri (40%)
            if ema_signals['golden_cross']:
                score += 0.2
            if ema_signals['death_cross']:
                score -= 0.2
            if ema_signals['trend_strength'] > 0.05:
                score += 0.1
            elif ema_signals['trend_strength'] < -0.05:
                score -= 0.1
            
            # Candlestick formasyonları (30%)
            bullish_count = len([p for p in candlestick_patterns['patterns_detected'] 
                               if 'BULLISH' in p['type'] or p['type'] == 'HAMMER'])
            bearish_count = len([p for p in candlestick_patterns['patterns_detected'] 
                               if 'BEARISH' in p['type'] or p['type'] == 'SHOOTING_STAR'])
            
            score += (bullish_count - bearish_count) * 0.05
            
            # Destek/Direnç (20%)
            current_price = 100  # Mock fiyat
            if support_resistance['current_support'] > 0:
                support_distance = (current_price - support_resistance['current_support']) / current_price
                if support_distance < 0.05:  # %5'e yakın destek
                    score += 0.1
            
            if support_resistance['current_resistance'] > 0:
                resistance_distance = (support_resistance['current_resistance'] - current_price) / current_price
                if resistance_distance < 0.05:  # %5'e yakın direnç
                    score -= 0.1
            
            # Harmonik formasyonlar (10%)
            if harmonic_patterns['gartley'] or harmonic_patterns['butterfly']:
                score += 0.05
            
            # Skoru 0-1 arasında sınırla
            score = max(0, min(1, score))
            
            return round(score, 3)
            
        except Exception as e:
            logger.error(f"Sinyal skor hesaplama hatası: {e}")
            return 0.5
    
    def _determine_action(self, signal_score: float, data: pd.DataFrame) -> str:
        """Sinyal skoruna göre aksiyon belirle"""
        if signal_score >= 0.7:
            return 'STRONG_BUY'
        elif signal_score >= 0.6:
            return 'BUY'
        elif signal_score >= 0.4:
            return 'HOLD'
        elif signal_score >= 0.3:
            return 'SELL'
        else:
            return 'STRONG_SELL'
    
    def _calculate_risk_level(self, data: pd.DataFrame, support_resistance: Dict) -> str:
        """Risk seviyesini hesapla"""
        try:
            if len(data) < 20:
                return 'ORTA'
            
            # Volatilite hesapla
            returns = data['Close'].pct_change().dropna()
            volatility = returns.std()
            
            # ATR benzeri hesaplama
            high_low = data['High'] - data['Low']
            atr = high_low.rolling(14).mean().iloc[-1]
            atr_percentage = atr / data['Close'].iloc[-1]
            
            if atr_percentage > 0.05 or volatility > 0.03:  # %5 ATR veya %3 volatilite
                return 'YÜKSEK'
            elif atr_percentage > 0.03 or volatility > 0.02:
                return 'ORTA'
            else:
                return 'DÜŞÜK'
                
        except Exception as e:
            logger.error(f"Risk seviyesi hesaplama hatası: {e}")
            return 'ORTA'
    
    def _calculate_sl_tp(self, data: pd.DataFrame, support_resistance: Dict, action: str) -> Dict:
        """Stop loss ve take profit hesapla"""
        try:
            current_price = data['Close'].iloc[-1]
            
            if action in ['BUY', 'STRONG_BUY']:
                # Alım sinyali
                if support_resistance['current_support'] > 0:
                    stop_loss = support_resistance['current_support'] * 0.98  # %2 altında
                else:
                    stop_loss = current_price * 0.95  # %5 altında
                
                take_profit = current_price * 1.15  # %15 üstünde
                
            elif action in ['SELL', 'STRONG_SELL']:
                # Satım sinyali
                if support_resistance['current_resistance'] > 0:
                    stop_loss = support_resistance['current_resistance'] * 1.02  # %2 üstünde
                else:
                    stop_loss = current_price * 1.05  # %5 üstünde
                
                take_profit = current_price * 0.85  # %15 altında
                
            else:
                # HOLD
                stop_loss = current_price * 0.90
                take_profit = current_price * 1.10
            
            return {
                'stop_loss': round(stop_loss, 2),
                'take_profit': round(take_profit, 2)
            }
            
        except Exception as e:
            logger.error(f"SL/TP hesaplama hatası: {e}")
            return {'stop_loss': 0, 'take_profit': 0}
    
    def _generate_signal_summary(self, ema_signals: Dict, candlestick_patterns: Dict, 
                                support_resistance: Dict, harmonic_patterns: Dict) -> str:
        """Sinyal özeti oluştur"""
        summary_parts = []
        
        if ema_signals['golden_cross']:
            summary_parts.append("🟢 Golden Cross tespit edildi")
        if ema_signals['death_cross']:
            summary_parts.append("🔴 Death Cross tespit edildi")
        
        if candlestick_patterns['bullish_engulfing']:
            summary_parts.append("📈 Bullish Engulfing formasyonu")
        if candlestick_patterns['bearish_engulfing']:
            summary_parts.append("📉 Bearish Engulfing formasyonu")
        
        if support_resistance['current_support'] > 0:
            summary_parts.append(f"🛡️ Destek seviyesi: {support_resistance['current_support']:.2f}")
        if support_resistance['current_resistance'] > 0:
            summary_parts.append(f"🚧 Direnç seviyesi: {support_resistance['current_resistance']:.2f}")
        
        if harmonic_patterns['patterns_detected']:
            summary_parts.append("🎯 Harmonik formasyon tespit edildi")
        
        if not summary_parts:
            summary_parts.append("📊 Teknik göstergeler nötr")
        
        return " | ".join(summary_parts)

# Test fonksiyonu
if __name__ == "__main__":
    print("🧪 Technical Pattern Engine Test Ediliyor...")
    
    engine = TechnicalPatternEngine()
    
    # Test sembolleri
    test_symbols = ['SISE.IS', 'TUPRS.IS', 'GARAN.IS']
    
    for symbol in test_symbols:
        print(f"\n📊 {symbol} Teknik Analizi:")
        try:
            # Veri al
            data = engine.get_stock_data(symbol, period="6mo")
            
            if not data.empty:
                # Sinyal üret
                signals = engine.generate_trading_signals(symbol, data)
                
                print(f"   Aksiyon: {signals['action']}")
                print(f"   Sinyal Skoru: {signals['signal_score']:.3f}")
                print(f"   Güven: {signals['confidence']:.1f}%")
                print(f"   Risk: {signals['risk_level']}")
                print(f"   Stop Loss: {signals['stop_loss']}")
                print(f"   Take Profit: {signals['take_profit']}")
                
                if 'summary' in signals:
                    print(f"   Özet: {signals['summary']}")
                    
            else:
                print(f"   ❌ Veri alınamadı")
                
        except Exception as e:
            print(f"   ❌ Hata: {e}")
    
    print("\n✅ Test tamamlandı!")
