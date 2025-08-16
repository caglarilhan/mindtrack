"""
PRD v2.0 - BIST AI Smart Trader
Feature Engineering Module

Özellik mühendisliği modülü:
- Technical indicators
- Fundamental features
- Market features
- Sentiment features
- Feature selection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from scipy import stats
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class TechnicalIndicator:
    """Teknik indikatör"""
    name: str
    values: pd.Series
    parameters: Dict
    description: str

@dataclass
class FeatureSet:
    """Özellik seti"""
    technical_features: pd.DataFrame
    fundamental_features: pd.DataFrame
    market_features: pd.DataFrame
    sentiment_features: pd.DataFrame
    combined_features: pd.DataFrame
    feature_names: List[str]

@dataclass
class FeatureImportance:
    """Özellik önem sırası"""
    feature_name: str
    importance_score: float
    rank: int
    category: str

class FeatureEngineering:
    """
    Özellik Mühendisliği Motoru
    
    PRD v2.0 gereksinimleri:
    - Teknik indikatör hesaplama
    - Temel özellik çıkarımı
    - Piyasa özellikleri
    - Duygu özellikleri
    - Özellik seçimi ve optimizasyonu
    """
    
    def __init__(self, lookback_period: int = 20):
        """
        Feature Engineering başlatıcı
        
        Args:
            lookback_period: Geriye dönük analiz periyodu
        """
        self.lookback_period = lookback_period
        
        # Teknik indikatör parametreleri
        self.TECHNICAL_INDICATORS = {
            "SMA": {"name": "Simple Moving Average", "params": [5, 10, 20, 50, 100, 200]},
            "EMA": {"name": "Exponential Moving Average", "params": [5, 10, 20, 50, 100, 200]},
            "RSI": {"name": "Relative Strength Index", "params": [14, 21]},
            "MACD": {"name": "MACD", "params": [12, 26, 9]},
            "BB": {"name": "Bollinger Bands", "params": [20, 2]},
            "STOCH": {"name": "Stochastic Oscillator", "params": [14, 3, 3]},
            "ATR": {"name": "Average True Range", "params": [14]},
            "CCI": {"name": "Commodity Channel Index", "params": [20]},
            "WILLIAMS_R": {"name": "Williams %R", "params": [14]},
            "ROC": {"name": "Rate of Change", "params": [10, 20]},
            "MOMENTUM": {"name": "Momentum", "params": [10, 20]},
            "OBV": {"name": "On Balance Volume", "params": []}
        }
        
        # Temel özellik türleri
        self.FUNDAMENTAL_FEATURES = {
            "RATIOS": ["PE", "PB", "PS", "PEG", "ROE", "ROA", "DEBT_EQUITY"],
            "GROWTH": ["REVENUE_GROWTH", "EPS_GROWTH", "BOOK_VALUE_GROWTH"],
            "PROFITABILITY": ["GROSS_MARGIN", "OPERATING_MARGIN", "NET_MARGIN"],
            "EFFICIENCY": ["ASSET_TURNOVER", "INVENTORY_TURNOVER", "RECEIVABLES_TURNOVER"]
        }
        
        # Piyasa özellikleri
        self.MARKET_FEATURES = {
            "VOLATILITY": ["HISTORICAL_VOL", "IMPLIED_VOL", "VOL_OF_VOL"],
            "LIQUIDITY": ["BID_ASK_SPREAD", "TURNOVER_RATIO", "AMIHUD_ILLIQUIDITY"],
            "CORRELATION": ["MARKET_CORRELATION", "SECTOR_CORRELATION", "BETA"],
            "SENTIMENT": ["PUT_CALL_RATIO", "SHORT_INTEREST", "INSIDER_TRADING"]
        }
    
    def calculate_sma(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Simple Moving Average hesaplama
        
        Args:
            prices: Fiyat serisi
            period: Periyot
            
        Returns:
            pd.Series: SMA değerleri
        """
        return prices.rolling(window=period).mean()
    
    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Exponential Moving Average hesaplama
        
        Args:
            prices: Fiyat serisi
            period: Periyot
            
        Returns:
            pd.Series: EMA değerleri
        """
        return prices.ewm(span=period).mean()
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Relative Strength Index hesaplama
        
        Args:
            prices: Fiyat serisi
            period: Periyot
            
        Returns:
            pd.Series: RSI değerleri
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """
        MACD hesaplama
        
        Args:
            prices: Fiyat serisi
            fast: Hızlı EMA periyodu
            slow: Yavaş EMA periyodu
            signal: Sinyal çizgisi periyodu
            
        Returns:
            Dict: MACD bileşenleri
        """
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return {
            "MACD": macd_line,
            "Signal": signal_line,
            "Histogram": histogram
        }
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """
        Bollinger Bands hesaplama
        
        Args:
            prices: Fiyat serisi
            period: Periyot
            std_dev: Standart sapma çarpanı
            
        Returns:
            Dict: Bollinger Bands bileşenleri
        """
        sma = self.calculate_sma(prices, period)
        std = prices.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            "Upper": upper_band,
            "Middle": sma,
            "Lower": lower_band,
            "BB_Width": (upper_band - lower_band) / sma,
            "BB_Position": (prices - lower_band) / (upper_band - lower_band)
        }
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                           k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """
        Stochastic Oscillator hesaplama
        
        Args:
            high: Yüksek fiyat serisi
            low: Düşük fiyat serisi
            close: Kapanış fiyat serisi
            k_period: %K periyodu
            d_period: %D periyodu
            
        Returns:
            Dict: Stochastic bileşenleri
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            "K": k_percent,
            "D": d_percent
        }
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Average True Range hesaplama
        
        Args:
            high: Yüksek fiyat serisi
            low: Düşük fiyat serisi
            close: Kapanış fiyat serisi
            period: Periyot
            
        Returns:
            pd.Series: ATR değerleri
        """
        prev_close = close.shift(1)
        
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def calculate_cci(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
        """
        Commodity Channel Index hesaplama
        
        Args:
            high: Yüksek fiyat serisi
            low: Düşük fiyat serisi
            close: Kapanış fiyat serisi
            period: Periyot
            
        Returns:
            pd.Series: CCI değerleri
        """
        typical_price = (high + low + close) / 3
        sma_tp = self.calculate_sma(typical_price, period)
        mean_deviation = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        
        cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
        return cci
    
    def calculate_williams_r(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Williams %R hesaplama
        
        Args:
            high: Yüksek fiyat serisi
            low: Düşük fiyat serisi
            close: Kapanış fiyat serisi
            period: Periyot
            
        Returns:
            pd.Series: Williams %R değerleri
        """
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        return williams_r
    
    def calculate_roc(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Rate of Change hesaplama
        
        Args:
            prices: Fiyat serisi
            period: Periyot
            
        Returns:
            pd.Series: ROC değerleri
        """
        return ((prices - prices.shift(period)) / prices.shift(period)) * 100
    
    def calculate_momentum(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Momentum hesaplama
        
        Args:
            prices: Fiyat serisi
            period: Periyot
            
        Returns:
            pd.Series: Momentum değerleri
        """
        return prices - prices.shift(period)
    
    def calculate_obv(self, prices: pd.Series, volume: pd.Series) -> pd.Series:
        """
        On Balance Volume hesaplama
        
        Args:
            prices: Fiyat serisi
            volume: Hacim serisi
            
        Returns:
            pd.Series: OBV değerleri
        """
        price_change = prices.diff()
        obv = pd.Series(index=prices.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(prices)):
            if price_change.iloc[i] > 0:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif price_change.iloc[i] < 0:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    
    def create_technical_features(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Teknik özellikler oluşturma
        
        Args:
            prices: OHLCV fiyat verisi
            
        Returns:
            pd.DataFrame: Teknik özellikler
        """
        features = pd.DataFrame(index=prices.index)
        
        # OHLCV verilerini ayır
        open_prices = prices['Open'] if 'Open' in prices.columns else prices.iloc[:, 0]
        high_prices = prices['High'] if 'High' in prices.columns else prices.iloc[:, 1]
        low_prices = prices['Low'] if 'Low' in prices.columns else prices.iloc[:, 2]
        close_prices = prices['Close'] if 'Close' in prices.columns else prices.iloc[:, 3]
        volume = prices['Volume'] if 'Volume' in prices.columns else pd.Series(1, index=prices.index)
        
        # SMA özellikleri
        for period in self.TECHNICAL_INDICATORS["SMA"]["params"]:
            features[f'SMA_{period}'] = self.calculate_sma(close_prices, period)
            features[f'Price_SMA_{period}_Ratio'] = close_prices / features[f'SMA_{period}']
        
        # EMA özellikleri
        for period in self.TECHNICAL_INDICATORS["EMA"]["params"]:
            features[f'EMA_{period}'] = self.calculate_ema(close_prices, period)
            features[f'Price_EMA_{period}_Ratio'] = close_prices / features[f'EMA_{period}']
        
        # RSI özellikleri
        for period in self.TECHNICAL_INDICATORS["RSI"]["params"]:
            features[f'RSI_{period}'] = self.calculate_rsi(close_prices, period)
        
        # MACD özellikleri
        macd_data = self.calculate_macd(close_prices)
        features['MACD'] = macd_data['MACD']
        features['MACD_Signal'] = macd_data['Signal']
        features['MACD_Histogram'] = macd_data['Histogram']
        
        # Bollinger Bands özellikleri
        bb_data = self.calculate_bollinger_bands(close_prices)
        features['BB_Upper'] = bb_data['Upper']
        features['BB_Middle'] = bb_data['Middle']
        features['BB_Lower'] = bb_data['Lower']
        features['BB_Width'] = bb_data['BB_Width']
        features['BB_Position'] = bb_data['BB_Position']
        
        # Stochastic özellikleri
        stoch_data = self.calculate_stochastic(high_prices, low_prices, close_prices)
        features['Stoch_K'] = stoch_data['K']
        features['Stoch_D'] = stoch_data['D']
        
        # ATR özellikleri
        atr = self.calculate_atr(high_prices, low_prices, close_prices)
        features['ATR'] = atr
        features['ATR_Ratio'] = atr / close_prices
        
        # CCI özellikleri
        features['CCI'] = self.calculate_cci(high_prices, low_prices, close_prices)
        
        # Williams %R özellikleri
        features['Williams_R'] = self.calculate_williams_r(high_prices, low_prices, close_prices)
        
        # ROC özellikleri
        for period in self.TECHNICAL_INDICATORS["ROC"]["params"]:
            features[f'ROC_{period}'] = self.calculate_roc(close_prices, period)
        
        # Momentum özellikleri
        for period in self.TECHNICAL_INDICATORS["MOMENTUM"]["params"]:
            features[f'Momentum_{period}'] = self.calculate_momentum(close_prices, period)
        
        # OBV özellikleri
        features['OBV'] = self.calculate_obv(close_prices, volume)
        
        # Fiyat değişim özellikleri
        features['Price_Change'] = close_prices.pct_change()
        features['Price_Change_2D'] = close_prices.pct_change(2)
        features['Price_Change_5D'] = close_prices.pct_change(5)
        
        # Volatilite özellikleri
        features['Volatility_5D'] = close_prices.pct_change().rolling(window=5).std()
        features['Volatility_20D'] = close_prices.pct_change().rolling(window=20).std()
        
        # Hacim özellikleri
        features['Volume_MA_5'] = volume.rolling(window=5).mean()
        features['Volume_MA_20'] = volume.rolling(window=20).mean()
        features['Volume_Ratio'] = volume / features['Volume_MA_20']
        
        return features
    
    def create_fundamental_features(self, fundamental_data: pd.DataFrame) -> pd.DataFrame:
        """
        Temel özellikler oluşturma
        
        Args:
            fundamental_data: Temel veri
            
        Returns:
            pd.DataFrame: Temel özellikler
        """
        features = pd.DataFrame(index=fundamental_data.index)
        
        # Temel oranlar
        if 'PE' in fundamental_data.columns:
            features['PE'] = fundamental_data['PE']
            features['PE_MA'] = fundamental_data['PE'].rolling(window=20).mean()
            features['PE_Ratio'] = fundamental_data['PE'] / features['PE_MA']
        
        if 'PB' in fundamental_data.columns:
            features['PB'] = fundamental_data['PB']
            features['PB_MA'] = fundamental_data['PB'].rolling(window=20).mean()
            features['PB_Ratio'] = fundamental_data['PB'] / features['PB_MA']
        
        if 'ROE' in fundamental_data.columns:
            features['ROE'] = fundamental_data['ROE']
            features['ROE_MA'] = fundamental_data['ROE'].rolling(window=20).mean()
            features['ROE_Change'] = fundamental_data['ROE'].pct_change()
        
        # Büyüme özellikleri
        if 'REVENUE_GROWTH' in fundamental_data.columns:
            features['Revenue_Growth'] = fundamental_data['REVENUE_GROWTH']
            features['Revenue_Growth_MA'] = fundamental_data['REVENUE_GROWTH'].rolling(window=20).mean()
        
        if 'EPS_GROWTH' in fundamental_data.columns:
            features['EPS_Growth'] = fundamental_data['EPS_GROWTH']
            features['EPS_Growth_MA'] = fundamental_data['EPS_GROWTH'].rolling(window=20).mean()
        
        return features
    
    def create_market_features(self, market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Piyasa özellikleri oluşturma
        
        Args:
            market_data: Piyasa verisi
            
        Returns:
            pd.DataFrame: Piyasa özellikleri
        """
        features = pd.DataFrame(index=market_data.index)
        
        # Volatilite özellikleri
        if 'HISTORICAL_VOL' in market_data.columns:
            features['Historical_Vol'] = market_data['HISTORICAL_VOL']
            features['Vol_MA'] = market_data['HISTORICAL_VOL'].rolling(window=20).mean()
            features['Vol_Ratio'] = market_data['HISTORICAL_VOL'] / features['Vol_MA']
        
        # Korelasyon özellikleri
        if 'MARKET_CORRELATION' in market_data.columns:
            features['Market_Correlation'] = market_data['MARKET_CORRELATION']
            features['Correlation_MA'] = market_data['MARKET_CORRELATION'].rolling(window=20).mean()
        
        if 'BETA' in market_data.columns:
            features['Beta'] = market_data['BETA']
            features['Beta_MA'] = market_data['BETA'].rolling(window=20).mean()
        
        return features
    
    def create_sentiment_features(self, sentiment_data: pd.DataFrame) -> pd.DataFrame:
        """
        Duygu özellikleri oluşturma
        
        Args:
            sentiment_data: Duygu verisi
            
        Returns:
            pd.DataFrame: Duygu özellikleri
        """
        features = pd.DataFrame(index=sentiment_data.index)
        
        # Haber duygu özellikleri
        if 'NEWS_SENTIMENT' in sentiment_data.columns:
            features['News_Sentiment'] = sentiment_data['NEWS_SENTIMENT']
            features['News_Sentiment_MA'] = sentiment_data['NEWS_SENTIMENT'].rolling(window=20).mean()
            features['News_Sentiment_Change'] = sentiment_data['NEWS_SENTIMENT'].pct_change()
        
        # Sosyal medya duygu özellikleri
        if 'SOCIAL_SENTIMENT' in sentiment_data.columns:
            features['Social_Sentiment'] = sentiment_data['SOCIAL_SENTIMENT']
            features['Social_Sentiment_MA'] = sentiment_data['SOCIAL_SENTIMENT'].rolling(window=20).mean()
            features['Social_Sentiment_Change'] = sentiment_data['SOCIAL_SENTIMENT'].pct_change()
        
        # Analist önerileri
        if 'ANALYST_RECOMMENDATIONS' in sentiment_data.columns:
            features['Analyst_Recommendations'] = sentiment_data['ANALYST_RECOMMENDATIONS']
            features['Analyst_Recommendations_MA'] = sentiment_data['ANALYST_RECOMMENDATIONS'].rolling(window=20).mean()
        
        return features
    
    def select_features(self, features: pd.DataFrame, target: pd.Series,
                       method: str = "correlation", threshold: float = 0.1) -> List[str]:
        """
        Özellik seçimi
        
        Args:
            features: Özellik matrisi
            target: Hedef değişken
            method: Seçim metodu
            threshold: Eşik değeri
            
        Returns:
            List: Seçilen özellik isimleri
        """
        if method == "correlation":
            # Korelasyon bazlı özellik seçimi
            correlations = features.corrwith(target).abs()
            selected_features = correlations[correlations > threshold].index.tolist()
            
        elif method == "variance":
            # Varyans bazlı özellik seçimi
            variances = features.var()
            selected_features = variances[variances > threshold].index.tolist()
            
        elif method == "mutual_info":
            # Mutual information bazlı seçim (basit yaklaşım)
            correlations = features.corrwith(target).abs()
            selected_features = correlations[correlations > threshold].index.tolist()
            
        else:
            raise ValueError(f"Desteklenmeyen metod: {method}")
        
        return selected_features
    
    def generate_feature_report(self, features: pd.DataFrame, target: pd.Series) -> Dict:
        """
        Özellik raporu oluşturma
        
        Args:
            features: Özellik matrisi
            target: Hedef değişken
            
        Returns:
            Dict: Özellik raporu
        """
        print("📊 Özellik Raporu Oluşturuluyor...")
        
        # Özellik istatistikleri
        feature_stats = features.describe()
        
        # Korelasyon analizi
        correlations = features.corrwith(target).abs().sort_values(ascending=False)
        
        # Özellik seçimi
        selected_features_corr = self.select_features(features, target, method="correlation", threshold=0.1)
        selected_features_var = self.select_features(features, target, method="variance", threshold=0.01)
        
        # Rapor oluştur
        report = {
            "feature_statistics": feature_stats.to_dict(),
            "correlation_analysis": {
                "top_correlations": correlations.head(10).to_dict(),
                "correlation_summary": {
                    "mean_correlation": correlations.mean(),
                    "max_correlation": correlations.max(),
                    "min_correlation": correlations.min()
                }
            },
            "feature_selection": {
                "correlation_based": selected_features_corr,
                "variance_based": selected_features_var,
                "total_features": len(features.columns),
                "selected_correlation": len(selected_features_corr),
                "selected_variance": len(selected_features_var)
            },
            "summary": {
                "n_features": len(features.columns),
                "n_samples": len(features),
                "missing_values": features.isnull().sum().sum(),
                "feature_categories": {
                    "technical": len([f for f in features.columns if any(ind in f for ind in ['SMA', 'EMA', 'RSI', 'MACD'])]),
                    "fundamental": len([f for f in features.columns if any(ind in f for ind in ['PE', 'PB', 'ROE'])]),
                    "market": len([f for f in features.columns if any(ind in f for ind in ['Vol', 'Correlation', 'Beta'])]),
                    "sentiment": len([f for f in features.columns if any(ind in f for ind in ['Sentiment', 'Recommendations'])])
                }
            }
        }
        
        print("✅ Özellik Raporu Tamamlandı!")
        return report

# Test fonksiyonu
def test_feature_engineering():
    """Feature Engineering test fonksiyonu"""
    print("🧪 Feature Engineering Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    n_days = 252  # 1 yıl
    
    # Tarih aralığı
    dates = pd.date_range('2023-01-01', periods=n_days, freq='D')
    
    # OHLCV verisi
    base_price = 100.0
    trend = 0.0005
    volatility = 0.02
    
    prices_data = []
    for i in range(n_days):
        # Trend + noise
        price = base_price * (1 + trend * i + np.random.normal(0, volatility))
        
        # OHLCV oluştur
        open_price = price * (1 + np.random.normal(0, 0.005))
        high_price = max(open_price, price) * (1 + abs(np.random.normal(0, 0.01)))
        low_price = min(open_price, price) * (1 - abs(np.random.normal(0, 0.01)))
        close_price = price
        volume = np.random.uniform(1000000, 5000000)
        
        prices_data.append([open_price, high_price, low_price, close_price, volume])
        base_price = price
    
    prices_df = pd.DataFrame(prices_data, 
                            columns=['Open', 'High', 'Low', 'Close', 'Volume'],
                            index=dates)
    
    # Hedef değişken (gelecek getiri)
    target = prices_df['Close'].pct_change().shift(-1)  # 1 gün sonraki getiri
    
    # Feature Engineering başlat
    feature_engine = FeatureEngineering(lookback_period=20)
    
    # Teknik özellikler test
    print("\n📊 Teknik Özellikler Test:")
    technical_features = feature_engine.create_technical_features(prices_df)
    print(f"   Oluşturulan teknik özellik sayısı: {len(technical_features.columns)}")
    print(f"   Örnek özellikler: {list(technical_features.columns[:5])}")
    
    # Temel özellikler test (simüle edilmiş)
    print("\n🏢 Temel Özellikler Test:")
    fundamental_data = pd.DataFrame({
        'PE': np.random.uniform(10, 30, n_days),
        'PB': np.random.uniform(1, 5, n_days),
        'ROE': np.random.uniform(0.05, 0.25, n_days),
        'REVENUE_GROWTH': np.random.uniform(-0.1, 0.3, n_days),
        'EPS_GROWTH': np.random.uniform(-0.15, 0.25, n_days)
    }, index=dates)
    
    fundamental_features = feature_engine.create_fundamental_features(fundamental_data)
    print(f"   Oluşturulan temel özellik sayısı: {len(fundamental_features.columns)}")
    
    # Piyasa özellikleri test (simüle edilmiş)
    print("\n📈 Piyasa Özellikleri Test:")
    market_data = pd.DataFrame({
        'HISTORICAL_VOL': np.random.uniform(0.15, 0.35, n_days),
        'MARKET_CORRELATION': np.random.uniform(0.3, 0.8, n_days),
        'BETA': np.random.uniform(0.8, 1.2, n_days)
    }, index=dates)
    
    market_features = feature_engine.create_market_features(market_data)
    print(f"   Oluşturulan piyasa özellik sayısı: {len(market_features.columns)}")
    
    # Duygu özellikleri test (simüle edilmiş)
    print("\n😊 Duygu Özellikleri Test:")
    sentiment_data = pd.DataFrame({
        'NEWS_SENTIMENT': np.random.uniform(-1, 1, n_days),
        'SOCIAL_SENTIMENT': np.random.uniform(-1, 1, n_days),
        'ANALYST_RECOMMENDATIONS': np.random.uniform(1, 5, n_days)
    }, index=dates)
    
    sentiment_features = feature_engine.create_sentiment_features(sentiment_data)
    print(f"   Oluşturulan duygu özellik sayısı: {len(sentiment_features.columns)}")
    
    # Özellik seçimi test
    print("\n🎯 Özellik Seçimi Test:")
    # NaN değerleri temizle
    all_features = pd.concat([technical_features, fundamental_features, market_features, sentiment_features], axis=1)
    all_features = all_features.dropna()
    target_clean = target.loc[all_features.index].dropna()
    
    # Ortak indeks bul
    common_index = all_features.index.intersection(target_clean.index)
    all_features_clean = all_features.loc[common_index]
    target_clean = target_clean.loc[common_index]
    
    selected_features = feature_engine.select_features(all_features_clean, target_clean, method="correlation", threshold=0.05)
    print(f"   Seçilen özellik sayısı: {len(selected_features)}")
    print(f"   Toplam özellik sayısı: {len(all_features_clean.columns)}")
    
    # Kapsamlı rapor test
    print("\n📋 Kapsamlı Özellik Raporu Test:")
    feature_report = feature_engine.generate_feature_report(all_features_clean, target_clean)
    print(f"   Toplam özellik: {feature_report['summary']['n_features']}")
    print(f"   Örnek sayısı: {feature_report['summary']['n_samples']}")
    print(f"   Eksik değer: {feature_report['summary']['missing_values']}")
    
    print("\n✅ Feature Engineering Test Tamamlandı!")
    return feature_engine

if __name__ == "__main__":
    test_feature_engineering()

