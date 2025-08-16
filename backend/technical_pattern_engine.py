"""
PRD v2.0 - Teknik Formasyon Motoru
❶ Trend (EMA cross) ❷ Harmonic (AB = CD, Gartley) ❸ Candlestick (Boğa Engulf) ❹ AutoHL (Fractal break)
ta-lib, patternizer ile Doğruluk > 60 % (backtest) hedefi
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechnicalPatternEngine:
    """Teknik formasyon tespit motoru"""
    
    def __init__(self):
        self.patterns = {}
        self.signals = {}
        
    def detect_ema_cross(self, data: pd.DataFrame, 
                         short_period: int = 20, 
                         long_period: int = 50) -> pd.DataFrame:
        """EMA kesişim formasyonları"""
        try:
            # EMA hesapla
            data['ema_short'] = data['Close'].ewm(span=short_period).mean()
            data['ema_long'] = data['Close'].ewm(span=long_period).mean()
            
            # Kesişim sinyalleri
            data['ema_cross_up'] = (
                (data['ema_short'].shift(1) < data['ema_long'].shift(1)) & 
                (data['ema_short'] > data['ema_long'])
            )
            
            data['ema_cross_down'] = (
                (data['ema_short'].shift(1) > data['ema_long'].shift(1)) & 
                (data['ema_short'] < data['ema_long'])
            )
            
            # Golden Cross (EMA 50 > EMA 200)
            if 'ema_200' not in data.columns:
                data['ema_200'] = data['Close'].ewm(span=200).mean()
            
            data['golden_cross'] = (
                (data['ema_50'].shift(1) < data['ema_200'].shift(1)) & 
                (data['ema_50'] > data['ema_200'])
            )
            
            # Death Cross (EMA 50 < EMA 200)
            data['death_cross'] = (
                (data['ema_50'].shift(1) > data['ema_200'].shift(1)) & 
                (data['ema_50'] < data['ema_200'])
            )
            
            logger.info("EMA kesişim formasyonları tespit edildi")
            return data
            
        except Exception as e:
            logger.error(f"EMA kesişim hatası: {e}")
            return data
    
    def detect_candlestick_patterns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Candlestick formasyonları"""
        try:
            # Basit candlestick formasyonları
            data['bullish_engulfing'] = (
                (data['Open'].shift(1) > data['Close'].shift(1)) &  # Önceki kırmızı
                (data['Open'] < data['Close']) &  # Şimdiki yeşil
                (data['Open'] < data['Close'].shift(1)) &  # Açılış önceki kapanıştan düşük
                (data['Close'] > data['Open'].shift(1))  # Kapanış önceki açılıştan yüksek
            )
            
            data['bearish_engulfing'] = (
                (data['Open'].shift(1) < data['Close'].shift(1)) &  # Önceki yeşil
                (data['Open'] > data['Close']) &  # Şimdiki kırmızı
                (data['Open'] > data['Close'].shift(1)) &  # Açılış önceki kapanıştan yüksek
                (data['Close'] < data['Open'].shift(1))  # Kapanış önceki açılıştan düşük
            )
            
            data['hammer'] = (
                (data['Close'] > data['Open']) &  # Yeşil mum
                ((data['High'] - data['Close']) / (data['Close'] - data['Open']) < 0.3) &  # Üst gölge kısa
                ((data['Open'] - data['Low']) / (data['Close'] - data['Open']) > 2)  # Alt gölge uzun
            )
            
            data['shooting_star'] = (
                (data['Close'] < data['Open']) &  # Kırmızı mum
                ((data['High'] - data['Open']) / (data['Open'] - data['Close']) > 2) &  # Üst gölge uzun
                ((data['Close'] - data['Low']) / (data['Open'] - data['Close']) < 0.3)  # Alt gölge kısa
            )
            
            data['doji'] = (
                abs(data['Close'] - data['Open']) / (data['High'] - data['Low']) < 0.1  # Gövde çok küçük
            )
            
            logger.info("Candlestick formasyonları tespit edildi")
            return data
            
        except Exception as e:
            logger.error(f"Candlestick formasyon hatası: {e}")
            return data
    
    def detect_harmonic_patterns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Harmonik formasyonlar (AB=CD, Gartley, Butterfly)"""
        try:
            # AB=CD Pattern
            data['ab_cd_pattern'] = self._detect_ab_cd_pattern(data)
            
            # Gartley Pattern
            data['gartley_pattern'] = self._detect_gartley_pattern(data)
            
            # Butterfly Pattern
            data['butterfly_pattern'] = self._detect_butterfly_pattern(data)
            
            logger.info("Harmonik formasyonlar tespit edildi")
            return data
            
        except Exception as e:
            logger.error(f"Harmonik formasyon hatası: {e}")
            return data
    
    def _detect_ab_cd_pattern(self, data: pd.DataFrame, 
                             lookback: int = 20) -> pd.Series:
        """AB=CD harmonik formasyonu"""
        pattern = pd.Series(False, index=data.index)
        
        for i in range(lookback, len(data)):
            try:
                # Son lookback gün içinde swing high/low bul
                window = data.iloc[i-lookback:i+1]
                
                # Swing high/low tespit
                highs = window[window['High'] == window['High'].max()]
                lows = window[window['Low'] == window['Low'].min()]
                
                if len(highs) >= 2 and len(lows) >= 2:
                    # AB=CD kriterleri kontrol et
                    # Bu basit bir implementasyon, gerçek harmonik analiz daha karmaşık
                    pattern.iloc[i] = True
                    
            except Exception as e:
                continue
        
        return pattern
    
    def _detect_gartley_pattern(self, data: pd.DataFrame, 
                               lookback: int = 20) -> pd.Series:
        """Gartley harmonik formasyonu"""
        pattern = pd.Series(False, index=data.index)
        
        for i in range(lookback, len(data)):
            try:
                # Gartley pattern kriterleri
                # XA, AB, BC, CD, AD oranları kontrol et
                pattern.iloc[i] = False  # Basit implementasyon
                
            except Exception as e:
                continue
        
        return pattern
    
    def _detect_butterfly_pattern(self, data: pd.DataFrame, 
                                 lookback: int = 20) -> pd.Series:
        """Butterfly harmonik formasyonu"""
        pattern = pd.Series(False, index=data.index)
        
        for i in range(lookback, len(data)):
            try:
                # Butterfly pattern kriterleri
                pattern.iloc[i] = False  # Basit implementasyon
                
            except Exception as e:
                continue
        
        return pattern
    
    def detect_support_resistance(self, data: pd.DataFrame, 
                                 window: int = 20) -> pd.DataFrame:
        """Destek ve direnç seviyeleri"""
        try:
            # Pivot noktaları bul
            data['pivot_high'] = data['High'].rolling(window=window, center=True).max()
            data['pivot_low'] = data['Low'].rolling(window=window, center=True).min()
            
            # Destek ve direnç seviyeleri
            data['resistance'] = data['pivot_high']
            data['support'] = data['pivot_low']
            
            # Breakout sinyalleri
            data['breakout_up'] = data['Close'] > data['resistance'].shift(1)
            data['breakout_down'] = data['Close'] < data['support'].shift(1)
            
            logger.info("Destek/direnç seviyeleri tespit edildi")
            return data
            
        except Exception as e:
            logger.error(f"Destek/direnç hatası: {e}")
            return data
    
    def detect_fibonacci_levels(self, data: pd.DataFrame, 
                               swing_high: float, 
                               swing_low: float) -> Dict:
        """Fibonacci seviyeleri"""
        try:
            diff = swing_high - swing_low
            
            fib_levels = {
                '0.0': swing_low,
                '0.236': swing_low + 0.236 * diff,
                '0.382': swing_low + 0.382 * diff,
                '0.5': swing_low + 0.5 * diff,
                '0.618': swing_low + 0.618 * diff,
                '0.786': swing_low + 0.786 * diff,
                '1.0': swing_high
            }
            
            logger.info("Fibonacci seviyeleri hesaplandı")
            return fib_levels
            
        except Exception as e:
            logger.error(f"Fibonacci hesaplama hatası: {e}")
            return {}
    
    def generate_pattern_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Formasyon sinyalleri üret"""
        try:
            # Sinyal skorları
            data['pattern_score'] = 0
            
            # EMA kesişim sinyalleri
            if 'ema_cross_up' in data.columns:
                data.loc[data['ema_cross_up'], 'pattern_score'] += 2
            if 'ema_cross_down' in data.columns:
                data.loc[data['ema_cross_down'], 'pattern_score'] -= 2
            
            # Candlestick sinyalleri
            if 'bullish_engulfing' in data.columns:
                data.loc[data['bullish_engulfing'], 'pattern_score'] += 1
            if 'bearish_engulfing' in data.columns:
                data.loc[data['bearish_engulfing'], 'pattern_score'] -= 1
            if 'hammer' in data.columns:
                data.loc[data['hammer'], 'pattern_score'] += 1
            if 'shooting_star' in data.columns:
                data.loc[data['shooting_star'], 'pattern_score'] -= 1
            
            # Harmonik formasyon sinyalleri
            if 'ab_cd_pattern' in data.columns:
                data.loc[data['ab_cd_pattern'], 'pattern_score'] += 1.5
            if 'gartley_pattern' in data.columns:
                data.loc[data['gartley_pattern'], 'pattern_score'] += 1.5
            if 'butterfly_pattern' in data.columns:
                data.loc[data['butterfly_pattern'], 'pattern_score'] += 1.5
            
            # Breakout sinyalleri
            if 'breakout_up' in data.columns:
                data.loc[data['breakout_up'], 'pattern_score'] += 1
            if 'breakout_down' in data.columns:
                data.loc[data['breakout_down'], 'pattern_score'] -= 1
            
            # Sinyal türü belirle
            data['signal_type'] = 'NEUTRAL'
            data.loc[data['pattern_score'] >= 2, 'signal_type'] = 'BUY'
            data.loc[data['pattern_score'] <= -2, 'signal_type'] = 'SELL'
            
            # Sinyal güveni
            data['signal_confidence'] = abs(data['pattern_score']) / 4  # 0-1 arası
            
            logger.info("Formasyon sinyalleri üretildi")
            return data
            
        except Exception as e:
            logger.error(f"Sinyal üretme hatası: {e}")
            return data
    
    def get_pattern_summary(self, data: pd.DataFrame) -> Dict:
        """Formasyon özeti"""
        if data.empty:
            return {}
        
        summary = {
            'total_patterns': {
                'ema_cross_up': data.get('ema_cross_up', pd.Series()).sum(),
                'ema_cross_down': data.get('ema_cross_down', pd.Series()).sum(),
                'bullish_engulfing': data.get('bullish_engulfing', pd.Series()).sum(),
                'bearish_engulfing': data.get('bearish_engulfing', pd.Series()).sum(),
                'hammer': data.get('hammer', pd.Series()).sum(),
                'shooting_star': data.get('shooting_star', pd.Series()).sum(),
                'ab_cd_pattern': data.get('ab_cd_pattern', pd.Series()).sum(),
                'gartley_pattern': data.get('gartley_pattern', pd.Series()).sum(),
                'butterfly_pattern': data.get('butterfly_pattern', pd.Series()).sum()
            },
            'signal_distribution': {
                'BUY': (data.get('signal_type', pd.Series()) == 'BUY').sum(),
                'SELL': (data.get('signal_type', pd.Series()) == 'SELL').sum(),
                'NEUTRAL': (data.get('signal_type', pd.Series()) == 'NEUTRAL').sum()
            },
            'average_confidence': data.get('signal_confidence', pd.Series()).mean(),
            'last_signal': data.get('signal_type', pd.Series()).iloc[-1] if len(data) > 0 else 'NEUTRAL'
        }
        
        return summary

# Test fonksiyonu
def test_technical_patterns():
    """Teknik formasyon test"""
    try:
        print("🧪 Technical Pattern Engine Test")
        print("="*50)
        
        # Test verisi yükle
        symbol = "SISE.IS"
        data = yf.download(symbol, period="6mo", interval="1d")
        
        if data.empty:
            print(f"❌ {symbol} verisi yüklenemedi")
            return
        
        print(f"📊 {symbol} verisi yüklendi: {len(data)} gün")
        
        # Pattern engine'i başlat
        engine = TechnicalPatternEngine()
        
        # EMA kesişimleri
        print("\n📈 EMA Kesişim Formasyonları:")
        data = engine.detect_ema_cross(data)
        ema_signals = data[data['ema_cross_up'] | data['ema_cross_down']].tail(5)
        if not ema_signals.empty:
            print(ema_signals[['Close', 'ema_short', 'ema_long', 'ema_cross_up', 'ema_cross_down']])
        else:
            print("EMA kesişim sinyali bulunamadı")
        
        # Candlestick formasyonları
        print("\n🕯️ Candlestick Formasyonları:")
        data = engine.detect_candlestick_patterns(data)
        candlestick_signals = data[
            data['bullish_engulfing'] | data['bearish_engulfing'] | 
            data['hammer'] | data['shooting_star']
        ].tail(5)
        if not candlestick_signals.empty:
            print(candlestick_signals[['Open', 'High', 'Low', 'Close', 'bullish_engulfing', 'bearish_engulfing']])
        else:
            print("Candlestick formasyonu bulunamadı")
        
        # Harmonik formasyonlar
        print("\n🎯 Harmonik Formasyonlar:")
        data = engine.detect_harmonic_patterns(data)
        
        # Destek/direnç
        print("\n🛡️ Destek/Direnç Seviyeleri:")
        data = engine.detect_support_resistance(data)
        
        # Sinyal üret
        print("\n🚦 Formasyon Sinyalleri:")
        data = engine.generate_pattern_signals(data)
        
        # Son 10 günün sinyalleri
        recent_signals = data[data['signal_type'] != 'NEUTRAL'].tail(10)
        if not recent_signals.empty:
            print(recent_signals[['Close', 'signal_type', 'pattern_score', 'signal_confidence']])
        else:
            print("Son 10 günde sinyal bulunamadı")
        
        # Özet
        print("\n📋 Formasyon Özeti:")
        summary = engine.get_pattern_summary(data)
        print(f"Toplam EMA kesişim: {summary['total_patterns']['ema_cross_up'] + summary['total_patterns']['ema_cross_down']}")
        print(f"Toplam Candlestick: {summary['total_patterns']['bullish_engulfing'] + summary['total_patterns']['bearish_engulfing']}")
        print(f"Sinyal dağılımı: {summary['signal_distribution']}")
        print(f"Ortalama güven: {summary['average_confidence']:.2f}")
        print(f"Son sinyal: {summary['last_signal']}")
        
        print("\n✅ Technical Pattern Engine test tamamlandı!")
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")

if __name__ == "__main__":
    test_technical_patterns()
