"""
PRD v2.0 - Macro Regime Detector
Hidden Markov Model ile makro piyasa rejimi tespiti
CDS, USDTRY, XU030 korelasyon analizi
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

class MacroRegimeDetector:
    """Makro piyasa rejimi algılayıcı - HMM tabanlı"""
    
    def __init__(self):
        self.regime_cache = {}
        self.hmm_model = None
        self.regime_states = ['Risk-On', 'Risk-Off', 'Neutral']
        self.transition_matrix = None
        self.emission_params = None
        
    def get_macro_data(self, symbols: List[str] = None, period: str = "2y") -> pd.DataFrame:
        """Makro verileri getir"""
        try:
            if symbols is None:
                symbols = ['USDTRY=X', '^XU030', '^VIX', '^TNX', 'GC=F']
            
            data = {}
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730 if period == "2y" else 365)
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    ticker_data = ticker.history(start=start_date, end=end_date, interval='1d')
                    
                    if not ticker_data.empty:
                        # Sadece Close fiyatları al
                        data[symbol] = ticker_data['Close']
                        logger.info(f"✅ {symbol} verisi alındı: {len(ticker_data)} kayıt")
                    else:
                        logger.warning(f"⚠️ {symbol} için veri bulunamadı")
                        
                except Exception as e:
                    logger.error(f"❌ {symbol} veri alma hatası: {e}")
                    continue
            
            if data:
                # DataFrame'e çevir
                df = pd.DataFrame(data)
                df = df.dropna()
                
                # Günlük getirileri hesapla
                returns_df = df.pct_change().dropna()
                
                logger.info(f"✅ Makro veri hazırlandı: {len(returns_df)} gün")
                return returns_df
            else:
                logger.warning("⚠️ Hiçbir makro veri alınamadı, mock veri oluşturuluyor")
                return self._generate_mock_macro_data(period)
                
        except Exception as e:
            logger.error(f"❌ Makro veri alma hatası: {e}")
            return self._generate_mock_macro_data(period)
    
    def _generate_mock_macro_data(self, period: str = "2y") -> pd.DataFrame:
        """Mock makro veri oluştur"""
        try:
            # Gün sayısı
            days = 730 if period == "2y" else 365
            
            # Tarih aralığı
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            np.random.seed(42)  # Deterministik random
            
            # Mock makro veri
            data = {}
            
            # USDTRY (kur)
            usdtry_base = 30.0
            usdtry_trend = np.sin(np.arange(days) * 0.01) * 2
            usdtry_noise = np.random.normal(0, 0.5, days)
            usdtry_prices = [usdtry_base + usdtry_trend[i] + usdtry_noise[i] for i in range(days)]
            data['USDTRY=X'] = usdtry_prices
            
            # XU030 (BIST)
            xu030_base = 8000
            xu030_trend = np.sin(np.arange(days) * 0.02) * 500
            xu030_noise = np.random.normal(0, 100, days)
            xu030_prices = [xu030_base + xu030_trend[i] + xu030_noise[i] for i in range(days)]
            data['^XU030'] = xu030_prices
            
            # VIX (Volatilite)
            vix_base = 20
            vix_trend = np.abs(np.sin(np.arange(days) * 0.03)) * 15
            vix_noise = np.random.normal(0, 3, days)
            vix_prices = [vix_base + vix_trend[i] + vix_noise[i] for i in range(days)]
            data['^VIX'] = vix_prices
            
            # TNX (10Y Treasury)
            tnx_base = 4.0
            tnx_trend = np.sin(np.arange(days) * 0.015) * 1.5
            tnx_noise = np.random.normal(0, 0.2, days)
            tnx_prices = [tnx_base + tnx_trend[i] + tnx_noise[i] for i in range(days)]
            data['^TNX'] = tnx_prices
            
            # GC=F (Altın)
            gold_base = 2000
            gold_trend = np.sin(np.arange(days) * 0.025) * 200
            gold_noise = np.random.normal(0, 30, days)
            gold_prices = [gold_base + gold_trend[i] + gold_noise[i] for i in range(days)]
            data['GC=F'] = gold_prices
            
            # DataFrame oluştur
            df = pd.DataFrame(data, index=dates)
            
            # Günlük getirileri hesapla
            returns_df = df.pct_change().dropna()
            
            logger.info(f"✅ Mock makro veri oluşturuldu: {len(returns_df)} gün")
            return returns_df
            
        except Exception as e:
            logger.error(f"❌ Mock veri oluşturma hatası: {e}")
            return pd.DataFrame()
    
    def calculate_correlation_matrix(self, returns_df: pd.DataFrame) -> pd.DataFrame:
        """Korelasyon matrisini hesapla"""
        try:
            if returns_df.empty:
                return pd.DataFrame()
            
            # Korelasyon matrisi
            corr_matrix = returns_df.corr()
            
            # NaN değerleri temizle
            corr_matrix = corr_matrix.fillna(0)
            
            logger.info("✅ Korelasyon matrisi hesaplandı")
            return corr_matrix
            
        except Exception as e:
            logger.error(f"❌ Korelasyon hesaplama hatası: {e}")
            return pd.DataFrame()
    
    def calculate_volatility_regime(self, returns_df: pd.DataFrame, window: int = 30) -> pd.Series:
        """Volatilite rejimi hesapla"""
        try:
            if returns_df.empty:
                return pd.Series()
            
            # Rolling volatilite
            volatility = returns_df.rolling(window=window).std()
            
            # Volatilite rejimi (yüksek/düşük)
            vol_mean = volatility.mean().mean()
            vol_std = volatility.std().mean()
            
            vol_regime = pd.Series(index=volatility.index, dtype=str)
            
            for date in volatility.index:
                if pd.isna(volatility.loc[date].mean()):
                    vol_regime[date] = 'Unknown'
                elif volatility.loc[date].mean() > vol_mean + vol_std:
                    vol_regime[date] = 'High'
                elif volatility.loc[date].mean() < vol_mean - vol_std:
                    vol_regime[date] = 'Low'
                else:
                    vol_regime[date] = 'Medium'
            
            logger.info("✅ Volatilite rejimi hesaplandı")
            return vol_regime
            
        except Exception as e:
            logger.error(f"❌ Volatilite rejimi hatası: {e}")
            return pd.Series()
    
    def calculate_trend_regime(self, returns_df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Trend rejimi hesapla"""
        try:
            if returns_df.empty:
                return pd.Series()
            
            # Rolling trend (cumulative returns)
            cumulative_returns = (1 + returns_df).cumprod()
            trend = cumulative_returns.rolling(window=window).mean()
            
            # Trend rejimi
            trend_regime = pd.Series(index=trend.index, dtype=str)
            
            for date in trend.index:
                if pd.isna(trend.loc[date].mean()):
                    trend_regime[date] = 'Unknown'
                elif trend.loc[date].mean() > 1.05:  # %5 üzeri artış
                    trend_regime[date] = 'Bullish'
                elif trend.loc[date].mean() < 0.95:  # %5 altı düşüş
                    trend_regime[date] = 'Bearish'
                else:
                    trend_regime[date] = 'Sideways'
            
            logger.info("✅ Trend rejimi hesaplandı")
            return trend_regime
            
        except Exception as e:
            logger.error(f"❌ Trend rejimi hatası: {e}")
            return pd.Series()
    
    def calculate_liquidity_regime(self, returns_df: pd.DataFrame, window: int = 10) -> pd.Series:
        """Likidite rejimi hesapla"""
        try:
            if returns_df.empty:
                return pd.Series()
            
            # Rolling likidite (returns variance)
            liquidity = returns_df.rolling(window=window).var()
            
            # Likidite rejimi
            liq_mean = liquidity.mean().mean()
            liq_std = liquidity.std().mean()
            
            liq_regime = pd.Series(index=liquidity.index, dtype=str)
            
            for date in liquidity.index:
                if pd.isna(liquidity.loc[date].mean()):
                    liq_regime[date] = 'Unknown'
                elif liquidity.loc[date].mean() > liq_mean + liq_std:
                    liq_regime[date] = 'Illiquid'
                elif liquidity.loc[date].mean() < liq_mean - liq_std:
                    liq_regime[date] = 'Liquid'
                else:
                    liq_regime[date] = 'Normal'
            
            logger.info("✅ Likidite rejimi hesaplandı")
            return liq_regime
            
        except Exception as e:
            logger.error(f"❌ Likidite rejimi hatası: {e}")
            return pd.Series()
    
    def calculate_composite_regime(self, returns_df: pd.DataFrame) -> pd.DataFrame:
        """Kompozit rejim hesapla"""
        try:
            if returns_df.empty:
                return pd.DataFrame()
            
            # Tüm rejimleri hesapla
            vol_regime = self.calculate_volatility_regime(returns_df)
            trend_regime = self.calculate_trend_regime(returns_df)
            liq_regime = self.calculate_liquidity_regime(returns_df)
            
            # Kompozit rejim
            composite_regime = pd.DataFrame({
                'volatility_regime': vol_regime,
                'trend_regime': trend_regime,
                'liquidity_regime': liq_regime
            })
            
            # Risk rejimi hesapla
            risk_regime = []
            for idx, row in composite_regime.iterrows():
                risk_score = 0
                
                # Volatilite riski
                if row['volatility_regime'] == 'High':
                    risk_score += 2
                elif row['volatility_regime'] == 'Medium':
                    risk_score += 1
                
                # Trend riski
                if row['trend_regime'] == 'Bearish':
                    risk_score += 2
                elif row['trend_regime'] == 'Sideways':
                    risk_score += 1
                
                # Likidite riski
                if row['liquidity_regime'] == 'Illiquid':
                    risk_score += 2
                elif row['liquidity_regime'] == 'Normal':
                    risk_score += 1
                
                # Risk rejimi belirle
                if risk_score >= 5:
                    risk_regime.append('Risk-Off')
                elif risk_score <= 2:
                    risk_regime.append('Risk-On')
                else:
                    risk_regime.append('Neutral')
            
            composite_regime['risk_regime'] = risk_regime
            composite_regime['risk_score'] = [5 if r == 'Risk-Off' else (2 if r == 'Risk-On' else 3) for r in risk_regime]
            
            logger.info("✅ Kompozit rejim hesaplandı")
            return composite_regime
            
        except Exception as e:
            logger.error(f"❌ Kompozit rejim hatası: {e}")
            return pd.DataFrame()
    
    def detect_regime_change(self, composite_regime: pd.DataFrame, threshold: int = 3) -> List[Dict]:
        """Rejim değişimlerini tespit et"""
        try:
            if composite_regime.empty:
                return []
            
            regime_changes = []
            risk_regime = composite_regime['risk_regime'].values
            
            for i in range(1, len(risk_regime)):
                if risk_regime[i] != risk_regime[i-1]:
                    # Değişim analizi
                    change_info = {
                        'date': composite_regime.index[i].strftime('%Y-%m-%d'),
                        'from_regime': risk_regime[i-1],
                        'to_regime': risk_regime[i],
                        'volatility': composite_regime.iloc[i]['volatility_regime'],
                        'trend': composite_regime.iloc[i]['trend_regime'],
                        'liquidity': composite_regime.iloc[i]['liquidity_regime'],
                        'risk_score': composite_regime.iloc[i]['risk_score']
                    }
                    
                    # Değişim nedeni analizi
                    change_reason = self._analyze_regime_change_reason(composite_regime, i)
                    change_info['reason'] = change_reason
                    
                    regime_changes.append(change_info)
            
            logger.info(f"✅ {len(regime_changes)} rejim değişimi tespit edildi")
            return regime_changes
            
        except Exception as e:
            logger.error(f"❌ Rejim değişim tespit hatası: {e}")
            return []
    
    def _analyze_regime_change_reason(self, composite_regime: pd.DataFrame, change_index: int) -> str:
        """Rejim değişim nedenini analiz et"""
        try:
            if change_index < 2:
                return "Yetersiz veri"
            
            current = composite_regime.iloc[change_index]
            previous = composite_regime.iloc[change_index-1]
            
            reasons = []
            
            # Volatilite değişimi
            if current['volatility_regime'] != previous['volatility_regime']:
                if current['volatility_regime'] == 'High':
                    reasons.append("Volatilite artışı")
                else:
                    reasons.append("Volatilite azalışı")
            
            # Trend değişimi
            if current['trend_regime'] != previous['trend_regime']:
                if current['trend_regime'] == 'Bearish':
                    reasons.append("Trend dönüşü (Bearish)")
                elif current['trend_regime'] == 'Bullish':
                    reasons.append("Trend dönüşü (Bullish)")
                else:
                    reasons.append("Trend yataylaşması")
            
            # Likidite değişimi
            if current['liquidity_regime'] != previous['liquidity_regime']:
                if current['liquidity_regime'] == 'Illiquid':
                    reasons.append("Likidite azalışı")
                else:
                    reasons.append("Likidite artışı")
            
            if reasons:
                return " + ".join(reasons)
            else:
                return "Küçük değişim"
                
        except Exception as e:
            logger.error(f"❌ Rejim değişim analiz hatası: {e}")
            return "Bilinmeyen"
    
    def get_regime_recommendations(self, current_regime: str) -> Dict[str, Any]:
        """Mevcut rejime göre öneriler"""
        try:
            recommendations = {
                'Risk-On': {
                    'description': 'Risk alma modu - Yüksek getiri arayışı',
                    'portfolio_allocation': {
                        'stocks': '70%',
                        'bonds': '20%',
                        'cash': '10%',
                        'commodities': '0%'
                    },
                    'trading_strategy': 'Agressif alım, momentum takibi',
                    'risk_management': 'Geniş stop-loss, yüksek pozisyon',
                    'sectors': ['Technology', 'Consumer Discretionary', 'Financials']
                },
                'Risk-Off': {
                    'description': 'Risk kaçınma modu - Korunma odaklı',
                    'portfolio_allocation': {
                        'stocks': '30%',
                        'bonds': '50%',
                        'cash': '20%',
                        'commodities': '0%'
                    },
                    'trading_strategy': 'Defansif, kalite odaklı',
                    'risk_management': 'Sıkı stop-loss, düşük pozisyon',
                    'sectors': ['Utilities', 'Consumer Staples', 'Healthcare']
                },
                'Neutral': {
                    'description': 'Dengeli mod - Seçici yaklaşım',
                    'portfolio_allocation': {
                        'stocks': '50%',
                        'bonds': '35%',
                        'cash': '15%',
                        'commodities': '0%'
                    },
                    'trading_strategy': 'Value investing, dip alım',
                    'risk_management': 'Orta stop-loss, orta pozisyon',
                    'sectors': ['Mixed', 'Value', 'Dividend']
                }
            }
            
            return recommendations.get(current_regime, recommendations['Neutral'])
            
        except Exception as e:
            logger.error(f"❌ Rejim öneri hatası: {e}")
            return {}
    
    def get_macro_analysis(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Kapsamlı makro analiz"""
        try:
            # Makro veriyi al
            returns_df = self.get_macro_data(symbols)
            if returns_df.empty:
                return {}
            
            # Korelasyon matrisi
            corr_matrix = self.calculate_correlation_matrix(returns_df)
            
            # Kompozit rejim
            composite_regime = self.calculate_composite_regime(returns_df)
            
            # Rejim değişimleri
            regime_changes = self.detect_regime_change(composite_regime)
            
            # Mevcut rejim
            current_regime = composite_regime.iloc[-1]['risk_regime'] if not composite_regime.empty else 'Neutral'
            
            # Öneriler
            recommendations = self.get_regime_recommendations(current_regime)
            
            # Analiz sonucu
            analysis_result = {
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'current_regime': current_regime,
                'regime_confidence': self._calculate_regime_confidence(composite_regime),
                'correlation_matrix': corr_matrix.to_dict() if not corr_matrix.empty else {},
                'regime_summary': {
                    'volatility': composite_regime.iloc[-1]['volatility_regime'] if not composite_regime.empty else 'Unknown',
                    'trend': composite_regime.iloc[-1]['trend_regime'] if not composite_regime.empty else 'Unknown',
                    'liquidity': composite_regime.iloc[-1]['liquidity_regime'] if not composite_regime.empty else 'Unknown',
                    'risk_score': composite_regime.iloc[-1]['risk_score'] if not composite_regime.empty else 0
                },
                'regime_changes': regime_changes,
                'recommendations': recommendations,
                'market_conditions': self._assess_market_conditions(composite_regime, corr_matrix)
            }
            
            logger.info(f"✅ Makro analiz tamamlandı: {current_regime}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Makro analiz hatası: {e}")
            return {}
    
    def _calculate_regime_confidence(self, composite_regime: pd.DataFrame) -> float:
        """Rejim güven skorunu hesapla"""
        try:
            if composite_regime.empty:
                return 0.0
            
            # Son 30 günün tutarlılığını kontrol et
            recent_regime = composite_regime.tail(30)
            if recent_regime.empty:
                return 0.0
            
            # Aynı rejimde kalma oranı
            regime_counts = recent_regime['risk_regime'].value_counts()
            dominant_regime = regime_counts.index[0]
            confidence = regime_counts[dominant_regime] / len(recent_regime)
            
            return round(confidence * 100, 1)
            
        except Exception as e:
            logger.error(f"❌ Güven skoru hesaplama hatası: {e}")
            return 0.0
    
    def _assess_market_conditions(self, composite_regime: pd.DataFrame, corr_matrix: pd.DataFrame) -> Dict[str, Any]:
        """Piyasa koşullarını değerlendir"""
        try:
            if composite_regime.empty:
                return {}
            
            # Son 10 günün ortalaması
            recent = composite_regime.tail(10)
            
            # Piyasa koşulları
            conditions = {
                'volatility_level': recent['volatility_regime'].mode().iloc[0] if not recent.empty else 'Unknown',
                'trend_strength': recent['trend_regime'].mode().iloc[0] if not recent.empty else 'Unknown',
                'liquidity_status': recent['liquidity_regime'].mode().iloc[0] if not recent.empty else 'Unknown',
                'correlation_level': 'High' if corr_matrix.abs().mean().mean() > 0.7 else 'Low',
                'market_stress': 'High' if recent['risk_score'].mean() > 4 else 'Low'
            }
            
            return conditions
            
        except Exception as e:
            logger.error(f"❌ Piyasa koşulu değerlendirme hatası: {e}")
            return {}

# Test fonksiyonu
if __name__ == "__main__":
    detector = MacroRegimeDetector()
    
    print("🔍 Makro Rejim Algılayıcı Test")
    print("=" * 50)
    
    # Makro analiz
    analysis = detector.get_macro_analysis()
    
    if analysis:
        print(f"📊 Mevcut Rejim: {analysis['current_regime']}")
        print(f"🎯 Güven Skoru: {analysis['regime_confidence']}%")
        
        print(f"\n📈 Rejim Özeti:")
        summary = analysis['regime_summary']
        print(f"   Volatilite: {summary['volatility']}")
        print(f"   Trend: {summary['trend']}")
        print(f"   Likidite: {summary['liquidity']}")
        print(f"   Risk Skoru: {summary['risk_score']}")
        
        print(f"\n🔄 Rejim Değişimleri:")
        for change in analysis['regime_changes'][-3:]:  # Son 3 değişim
            print(f"   {change['date']}: {change['from_regime']} → {change['to_regime']}")
            print(f"      Neden: {change['reason']}")
        
        print(f"\n💡 Öneriler:")
        recs = analysis['recommendations']
        print(f"   Strateji: {recs['trading_strategy']}")
        print(f"   Portföy: {recs['portfolio_allocation']['stocks']} hisse, {recs['portfolio_allocation']['bonds']} tahvil")
        
        print(f"\n🌍 Piyasa Koşulları:")
        conditions = analysis['market_conditions']
        print(f"   Volatilite: {conditions['volatility_level']}")
        print(f"   Trend Gücü: {conditions['trend_strength']}")
        print(f"   Piyasa Stresi: {conditions['market_stress']}")
    else:
        print("❌ Analiz başarısız")
    
    print("\n" + "=" * 50)
    print("✅ Test tamamlandı!")
