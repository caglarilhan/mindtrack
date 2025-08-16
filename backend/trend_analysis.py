"""
PRD v2.0 - BIST AI Smart Trader
Trend Analysis Module

Trend analizi modülü:
- Trend detection
- Support/Resistance levels
- Moving averages
- Trend strength
- Breakout detection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from scipy import stats
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class TrendInfo:
    """Trend bilgisi"""
    trend_type: str  # "UPTREND", "DOWNTREND", "SIDEWAYS"
    strength: float  # 0-1 arası
    start_date: datetime
    end_date: datetime
    duration: int  # gün sayısı
    slope: float  # trend eğimi

@dataclass
class SupportResistance:
    """Destek/Direnç seviyesi"""
    level: float
    type: str  # "SUPPORT", "RESISTANCE"
    strength: float  # 0-1 arası
    touches: int  # kaç kez test edildi
    last_tested: datetime

@dataclass
class BreakoutSignal:
    """Kırılma sinyali"""
    date: datetime
    price: float
    level: float
    type: str  # "SUPPORT_BREAK", "RESISTANCE_BREAK"
    volume: Optional[float] = None
    strength: float = 1.0

class TrendAnalysis:
    """
    Trend Analiz Motoru
    
    PRD v2.0 gereksinimleri:
    - Trend tespiti ve sınıflandırması
    - Destek/direnç seviyeleri
    - Hareketli ortalama analizi
    - Trend gücü hesaplama
    - Kırılma sinyali tespiti
    """
    
    def __init__(self, min_trend_duration: int = 20):
        """
        Trend Analysis başlatıcı
        
        Args:
            min_trend_duration: Minimum trend süresi (gün)
        """
        self.min_trend_duration = min_trend_duration
        
        # Trend türleri
        self.TREND_TYPES = {
            "UPTREND": "Yükselen trend",
            "DOWNTREND": "Düşen trend",
            "SIDEWAYS": "Yatay trend"
        }
        
        # Hareketli ortalama periyotları
        self.MA_PERIODS = [5, 10, 20, 50, 100, 200]
        
        # Destek/direnç türleri
        self.LEVEL_TYPES = {
            "SUPPORT": "Destek seviyesi",
            "RESISTANCE": "Direnç seviyesi"
        }
    
    def detect_trend(self, prices: pd.Series,
                     method: str = "linear_regression",
                     window: int = 50) -> TrendInfo:
        """
        Trend tespiti
        
        Args:
            prices: Fiyat serisi
            method: Trend tespit metodu
            window: Analiz penceresi
            
        Returns:
            TrendInfo: Trend bilgisi
        """
        if len(prices) < window:
            return None
        
        # Son N günlük veriyi al
        recent_prices = prices.tail(window)
        
        if method == "linear_regression":
            # Linear regression ile trend
            x = np.arange(len(recent_prices))
            y = recent_prices.values
            
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Trend türünü belirle
            if abs(slope) < 0.001:  # Çok küçük eğim
                trend_type = "SIDEWAYS"
            elif slope > 0:
                trend_type = "UPTREND"
            else:
                trend_type = "DOWNTREND"
            
            # Trend gücü (R-squared)
            trend_strength = r_value ** 2
            
            # Trend süresi
            start_date = recent_prices.index[0]
            end_date = recent_prices.index[-1]
            duration = len(recent_prices)
            
        elif method == "moving_average":
            # Hareketli ortalama ile trend
            ma_short = recent_prices.rolling(window=10).mean()
            ma_long = recent_prices.rolling(window=30).mean()
            
            # Son değerleri karşılaştır
            last_short = ma_short.iloc[-1]
            last_long = ma_long.iloc[-1]
            
            if last_short > last_long * 1.02:  # %2 fark
                trend_type = "UPTREND"
                slope = 0.01
            elif last_short < last_long * 0.98:
                trend_type = "DOWNTREND"
                slope = -0.01
            else:
                trend_type = "SIDEWAYS"
                slope = 0.0
            
            # Basit trend gücü
            trend_strength = 0.7 if abs(last_short - last_long) / last_long > 0.05 else 0.3
            
            start_date = recent_prices.index[0]
            end_date = recent_prices.index[-1]
            duration = len(recent_prices)
        
        else:
            raise ValueError(f"Desteklenmeyen metod: {method}")
        
        return TrendInfo(
            trend_type=trend_type,
            strength=trend_strength,
            start_date=start_date,
            end_date=end_date,
            duration=duration,
            slope=slope
        )
    
    def find_support_resistance(self, prices: pd.Series,
                               window: int = 20,
                               min_touches: int = 2) -> List[SupportResistance]:
        """
        Destek/direnç seviyeleri bulma
        
        Args:
            prices: Fiyat serisi
            window: Peak bulma penceresi
            min_touches: Minimum dokunma sayısı
            
        Returns:
            List: Destek/direnç seviyeleri
        """
        levels = []
        
        # Peak'leri bul (direnç seviyeleri)
        peaks, _ = find_peaks(prices.values, distance=window)
        
        # Valley'leri bul (destek seviyeleri)
        valleys, _ = find_peaks(-prices.values, distance=window)
        
        # Direnç seviyeleri
        for peak in peaks:
            level = prices.iloc[peak]
            
            # Bu seviyeye kaç kez dokunuldu
            touches = 0
            last_tested = prices.index[peak]
            
            for i, price in enumerate(prices):
                if abs(price - level) / level < 0.02:  # %2 tolerans
                    touches += 1
                    last_tested = prices.index[i]
            
            if touches >= min_touches:
                strength = min(1.0, touches / 5.0)  # 5+ dokunma = maksimum güç
                
                levels.append(SupportResistance(
                    level=level,
                    type="RESISTANCE",
                    strength=strength,
                    touches=touches,
                    last_tested=last_tested
                ))
        
        # Destek seviyeleri
        for valley in valleys:
            level = prices.iloc[valley]
            
            # Bu seviyeye kaç kez dokunuldu
            touches = 0
            last_tested = prices.index[valley]
            
            for i, price in enumerate(prices):
                if abs(price - level) / level < 0.02:  # %2 tolerans
                    touches += 1
                    last_tested = prices.index[i]
            
            if touches >= min_touches:
                strength = min(1.0, touches / 5.0)
                
                levels.append(SupportResistance(
                    level=level,
                    type="SUPPORT",
                    strength=strength,
                    touches=touches,
                    last_tested=last_tested
                ))
        
        # Seviyeleri güce göre sırala
        levels.sort(key=lambda x: x.strength, reverse=True)
        
        return levels
    
    def calculate_moving_averages(self, prices: pd.Series,
                                 periods: Optional[List[int]] = None) -> pd.DataFrame:
        """
        Hareketli ortalamalar hesaplama
        
        Args:
            prices: Fiyat serisi
            periods: MA periyotları
            
        Returns:
            pd.DataFrame: Hareketli ortalamalar
        """
        if periods is None:
            periods = self.MA_PERIODS
        
        ma_data = {}
        
        for period in periods:
            if period <= len(prices):
                ma_data[f"MA_{period}"] = prices.rolling(window=period).mean()
        
        return pd.DataFrame(ma_data, index=prices.index)
    
    def analyze_ma_crossovers(self, prices: pd.Series,
                             short_period: int = 20,
                             long_period: int = 50) -> Dict:
        """
        Hareketli ortalama kesişim analizi
        
        Args:
            prices: Fiyat serisi
            short_period: Kısa periyot
            long_period: Uzun periyot
            
        Returns:
            Dict: MA kesişim analizi
        """
        if short_period >= long_period:
            raise ValueError("Kısa periyot uzun periyottan küçük olmalı")
        
        # Hareketli ortalamalar
        ma_short = prices.rolling(window=short_period).mean()
        ma_long = prices.rolling(window=long_period).mean()
        
        # Kesişim sinyalleri
        crossover_signals = []
        
        for i in range(1, len(prices)):
            # Bullish crossover (kısa MA uzun MA'yı yukarı kesiyor)
            if (ma_short.iloc[i-1] <= ma_long.iloc[i-1] and 
                ma_short.iloc[i] > ma_long.iloc[i]):
                crossover_signals.append({
                    "date": prices.index[i],
                    "type": "BULLISH",
                    "price": prices.iloc[i],
                    "short_ma": ma_short.iloc[i],
                    "long_ma": ma_long.iloc[i]
                })
            
            # Bearish crossover (kısa MA uzun MA'yı aşağı kesiyor)
            elif (ma_short.iloc[i-1] >= ma_long.iloc[i-1] and 
                  ma_short.iloc[i] < ma_long.iloc[i]):
                crossover_signals.append({
                    "date": prices.index[i],
                    "type": "BEARISH",
                    "price": prices.iloc[i],
                    "short_ma": ma_short.iloc[i],
                    "long_ma": ma_long.iloc[i]
                })
        
        return {
            "short_ma": ma_short,
            "long_ma": ma_long,
            "crossover_signals": crossover_signals,
            "total_signals": len(crossover_signals)
        }
    
    def calculate_trend_strength(self, prices: pd.Series,
                                window: int = 50) -> float:
        """
        Trend gücü hesaplama
        
        Args:
            prices: Fiyat serisi
            window: Analiz penceresi
            
        Returns:
            float: Trend gücü (0-1 arası)
        """
        if len(prices) < window:
            return 0.0
        
        recent_prices = prices.tail(window)
        
        # Linear regression
        x = np.arange(len(recent_prices))
        y = recent_prices.values
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # R-squared (trend gücü)
        trend_strength = r_value ** 2
        
        # Slope'a göre ek düzeltme
        if abs(slope) < 0.001:
            trend_strength *= 0.5  # Yatay trend için gücü azalt
        
        return min(1.0, trend_strength)
    
    def detect_breakouts(self, prices: pd.Series,
                         support_resistance: List[SupportResistance],
                         volume: Optional[pd.Series] = None,
                         threshold: float = 0.02) -> List[BreakoutSignal]:
        """
        Kırılma sinyali tespiti
        
        Args:
            prices: Fiyat serisi
            support_resistance: Destek/direnç seviyeleri
            volume: Hacim serisi (opsiyonel)
            threshold: Kırılma eşiği
            
        Returns:
            List: Kırılma sinyalleri
        """
        breakouts = []
        
        for level in support_resistance:
            # Son fiyatları kontrol et
            recent_prices = prices.tail(5)  # Son 5 gün
            
            for date, price in recent_prices.items():
                if level.type == "RESISTANCE":
                    # Direnç kırılıyor mu?
                    if price > level.level * (1 + threshold):
                        # Kırılma gücü
                        strength = min(1.0, (price - level.level) / level.level * 10)
                        
                        breakouts.append(BreakoutSignal(
                            date=date,
                            price=price,
                            level=level.level,
                            type="RESISTANCE_BREAK",
                            volume=volume[date] if volume is not None else None,
                            strength=strength
                        ))
                
                elif level.type == "SUPPORT":
                    # Destek kırılıyor mu?
                    if price < level.level * (1 - threshold):
                        # Kırılma gücü
                        strength = min(1.0, (level.level - price) / level.level * 10)
                        
                        breakouts.append(BreakoutSignal(
                            date=date,
                            price=price,
                            level=level.level,
                            type="SUPPORT_BREAK",
                            volume=volume[date] if volume is not None else None,
                            strength=strength
                        ))
        
        # Kırılmaları tarihe göre sırala
        breakouts.sort(key=lambda x: x.date)
        
        return breakouts
    
    def generate_trend_report(self, prices: pd.Series,
                             volume: Optional[pd.Series] = None) -> Dict:
        """
        Kapsamlı trend raporu oluşturma
        
        Args:
            prices: Fiyat serisi
            volume: Hacim serisi
            
        Returns:
            Dict: Kapsamlı trend raporu
        """
        print("📈 Trend Raporu Oluşturuluyor...")
        
        # Trend tespiti
        trend_info = self.detect_trend(prices, method="linear_regression")
        
        # Destek/direnç seviyeleri
        support_resistance = self.find_support_resistance(prices)
        
        # Hareketli ortalamalar
        moving_averages = self.calculate_moving_averages(prices)
        
        # MA kesişim analizi
        ma_analysis = self.analyze_ma_crossovers(prices)
        
        # Trend gücü
        trend_strength = self.calculate_trend_strength(prices)
        
        # Kırılma sinyalleri
        breakouts = self.detect_breakouts(prices, support_resistance, volume)
        
        # Rapor oluştur
        report = {
            "trend_analysis": {
                "trend_type": trend_info.trend_type if trend_info else "UNKNOWN",
                "trend_strength": trend_strength,
                "slope": trend_info.slope if trend_info else 0.0,
                "duration": trend_info.duration if trend_info else 0
            },
            "support_resistance": {
                "total_levels": len(support_resistance),
                "support_levels": [level for level in support_resistance if level.type == "SUPPORT"],
                "resistance_levels": [level for level in support_resistance if level.type == "RESISTANCE"],
                "strongest_levels": support_resistance[:3] if len(support_resistance) >= 3 else support_resistance
            },
            "moving_averages": {
                "periods": list(moving_averages.columns),
                "current_values": moving_averages.iloc[-1].to_dict() if not moving_averages.empty else {},
                "crossover_signals": ma_analysis["total_signals"]
            },
            "breakout_signals": {
                "total_breakouts": len(breakouts),
                "recent_breakouts": breakouts[-3:] if len(breakouts) >= 3 else breakouts,
                "breakout_types": {
                    "support_breaks": len([b for b in breakouts if b.type == "SUPPORT_BREAK"]),
                    "resistance_breaks": len([b for b in breakouts if b.type == "RESISTANCE_BREAK"])
                }
            },
            "summary": {
                "current_trend": trend_info.trend_type if trend_info else "UNKNOWN",
                "trend_strength_score": f"{trend_strength:.2f}",
                "key_levels": len(support_resistance),
                "breakout_opportunities": len(breakouts)
            }
        }
        
        print("✅ Trend Raporu Tamamlandı!")
        return report

# Test fonksiyonu
def test_trend_analysis():
    """Trend Analysis test fonksiyonu"""
    print("🧪 Trend Analysis Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    n_days = 252  # 1 yıl
    
    # Tarih aralığı
    dates = pd.date_range('2023-01-01', periods=n_days, freq='D')
    
    # Trend'li fiyat verisi oluştur
    base_price = 100.0
    trend = 0.0005  # Günlük trend
    volatility = 0.02  # Günlük volatilite
    
    prices = []
    for i in range(n_days):
        # Trend + noise
        price = base_price * (1 + trend * i + np.random.normal(0, volatility))
        prices.append(price)
        base_price = price
    
    price_series = pd.Series(prices, index=dates)
    
    # Hacim verisi (opsiyonel)
    volume_series = pd.Series(
        np.random.uniform(1000000, 5000000, n_days),
        index=dates
    )
    
    # Trend Analysis başlat
    trend_analyzer = TrendAnalysis(min_trend_duration=20)
    
    # Trend tespiti test
    print("\n📈 Trend Tespiti Test:")
    trend_info = trend_analyzer.detect_trend(price_series, method="linear_regression")
    if trend_info:
        print(f"   Trend türü: {trend_info.trend_type}")
        print(f"   Trend gücü: {trend_info.strength:.4f}")
        print(f"   Trend eğimi: {trend_info.slope:.6f}")
        print(f"   Trend süresi: {trend_info.duration} gün")
    
    # Destek/direnç seviyeleri test
    print("\n🔄 Destek/Direnç Seviyeleri Test:")
    support_resistance = trend_analyzer.find_support_resistance(price_series)
    print(f"   Toplam seviye: {len(support_resistance)}")
    
    support_levels = [level for level in support_resistance if level.type == "SUPPORT"]
    resistance_levels = [level for level in support_resistance if level.type == "RESISTANCE"]
    print(f"   Destek seviyeleri: {len(support_levels)}")
    print(f"   Direnç seviyeleri: {len(resistance_levels)}")
    
    if support_resistance:
        strongest = support_resistance[0]
        print(f"   En güçlü seviye: {strongest.type} - {strongest.level:.2f} (Güç: {strongest.strength:.2f})")
    
    # Hareketli ortalamalar test
    print("\n📊 Hareketli Ortalamalar Test:")
    moving_averages = trend_analyzer.calculate_moving_averages(price_series)
    print(f"   MA periyotları: {list(moving_averages.columns)}")
    
    if not moving_averages.empty:
        current_ma = moving_averages.iloc[-1]
        print(f"   Güncel MA20: {current_ma.get('MA_20', 'N/A'):.2f}")
        print(f"   Güncel MA50: {current_ma.get('MA_50', 'N/A'):.2f}")
    
    # MA kesişim analizi test
    print("\n🔄 MA Kesişim Analizi Test:")
    ma_analysis = trend_analyzer.analyze_ma_crossovers(price_series, short_period=20, long_period=50)
    print(f"   Toplam kesişim sinyali: {ma_analysis['total_signals']}")
    
    if ma_analysis['crossover_signals']:
        last_signal = ma_analysis['crossover_signals'][-1]
        print(f"   Son sinyal: {last_signal['type']} - {last_signal['date'].strftime('%Y-%m-%d')}")
    
    # Trend gücü test
    print("\n💪 Trend Gücü Test:")
    trend_strength = trend_analyzer.calculate_trend_strength(price_series)
    print(f"   Trend gücü: {trend_strength:.4f}")
    
    # Kırılma sinyalleri test
    print("\n🚨 Kırılma Sinyalleri Test:")
    breakouts = trend_analyzer.detect_breakouts(price_series, support_resistance, volume_series)
    print(f"   Toplam kırılma: {len(breakouts)}")
    
    if breakouts:
        support_breaks = len([b for b in breakouts if b.type == "SUPPORT_BREAK"])
        resistance_breaks = len([b for b in breakouts if b.type == "RESISTANCE_BREAK"])
        print(f"   Destek kırılmaları: {support_breaks}")
        print(f"   Direnç kırılmaları: {resistance_breaks}")
    
    # Kapsamlı rapor test
    print("\n📋 Kapsamlı Trend Raporu Test:")
    trend_report = trend_analyzer.generate_trend_report(price_series, volume_series)
    print(f"   Mevcut trend: {trend_report['summary']['current_trend']}")
    print(f"   Trend gücü skoru: {trend_report['summary']['trend_strength_score']}")
    print(f"   Anahtar seviyeler: {trend_report['summary']['key_levels']}")
    print(f"   Kırılma fırsatları: {trend_report['summary']['breakout_opportunities']}")
    
    print("\n✅ Trend Analysis Test Tamamlandı!")
    return trend_analyzer

if __name__ == "__main__":
    test_trend_analysis()

