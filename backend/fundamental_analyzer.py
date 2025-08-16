"""
PRD v2.0 - DuPont & Piotroski F-Score
ROE bileşen ayrıştırma ✚ doğan skor
FinanceToolkit ile Hisse filtresi N → Top 10
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from financetoolkit import Toolkit
import yfinance as yf
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FundamentalAnalyzer:
    """DuPont ve Piotroski F-Score analizi"""
    
    def __init__(self, fmp_api_key: Optional[str] = None):
        self.fmp_api_key = fmp_api_key
        self.toolkit = None
        self.dupont_data = {}
        self.piotroski_data = {}
        
        if fmp_api_key:
            try:
                self.toolkit = Toolkit(api_key=fmp_api_key)
                logger.info("FinanceToolkit başlatıldı")
            except Exception as e:
                logger.warning(f"FinanceToolkit başlatılamadı: {e}")
    
    def get_dupont_analysis(self, symbols: List[str]) -> pd.DataFrame:
        """DuPont analizi yap"""
        try:
            if not self.toolkit:
                logger.warning("FinanceToolkit mevcut değil, yfinance kullanılıyor")
                return self._get_dupont_yfinance(symbols)
            
            # FinanceToolkit ile DuPont analizi
            dupont_df = self.toolkit.models.get_extended_dupont_analysis(symbols)
            
            if not dupont_df.empty:
                # Veriyi temizle ve formatla
                dupont_df = dupont_df.T  # Transpose
                dupont_df.index.name = 'symbol'
                dupont_df.reset_index(inplace=True)
                
                # DuPont skoru hesapla
                dupont_df['dupont_score'] = self._calculate_dupont_score(dupont_df)
                
                logger.info(f"DuPont analizi tamamlandı: {len(symbols)} hisse")
                return dupont_df
            else:
                logger.warning("DuPont verisi alınamadı, yfinance kullanılıyor")
                return self._get_dupont_yfinance(symbols)
                
        except Exception as e:
            logger.error(f"DuPont analizi hatası: {e}")
            return self._get_dupont_yfinance(symbols)
    
    def _get_dupont_yfinance(self, symbols: List[str]) -> pd.DataFrame:
        """yfinance ile DuPont analizi (fallback)"""
        dupont_data = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Temel finansal oranlar
                roe = info.get('returnOnEquity', 0)
                roa = info.get('returnOnAssets', 0)
                net_profit_margin = info.get('profitMargins', 0)
                asset_turnover = info.get('revenueGrowth', 0)  # Yaklaşık
                financial_leverage = info.get('debtToEquity', 0)
                
                # DuPont skoru hesapla
                dupont_score = self._calculate_dupont_score_simple(
                    roe, roa, net_profit_margin, asset_turnover, financial_leverage
                )
                
                dupont_data.append({
                    'symbol': symbol,
                    'roe': roe,
                    'roa': roa,
                    'net_profit_margin': net_profit_margin,
                    'asset_turnover': asset_turnover,
                    'financial_leverage': financial_leverage,
                    'dupont_score': dupont_score
                })
                
            except Exception as e:
                logger.warning(f"{symbol} DuPont analizi hatası: {e}")
                continue
        
        if dupont_data:
            df = pd.DataFrame(dupont_data)
            df.set_index('symbol', inplace=True)
            return df
        else:
            return pd.DataFrame()
    
    def _calculate_dupont_score(self, dupont_df: pd.DataFrame) -> pd.Series:
        """DuPont skoru hesapla (FinanceToolkit verisi için)"""
        try:
            # DuPont bileşenlerini normalize et
            roe_norm = self._normalize_ratio(dupont_df['ROE'])
            roa_norm = self._normalize_ratio(dupont_df['ROA'])
            net_margin_norm = self._normalize_ratio(dupont_df['Net Income Margin'])
            asset_turnover_norm = self._normalize_ratio(dupont_df['Asset Turnover'])
            financial_leverage_norm = self._normalize_ratio(dupont_df['Financial Leverage'])
            
            # Ağırlıklı skor hesapla
            dupont_score = (
                roe_norm * 0.3 +
                roa_norm * 0.25 +
                net_margin_norm * 0.2 +
                asset_turnover_norm * 0.15 +
                financial_leverage_norm * 0.1
            )
            
            return dupont_score
            
        except Exception as e:
            logger.error(f"DuPont skor hesaplama hatası: {e}")
            return pd.Series([0] * len(dupont_df))
    
    def _calculate_dupont_score_simple(self, roe: float, roa: float, 
                                     net_margin: float, asset_turnover: float, 
                                     financial_leverage: float) -> float:
        """Basit DuPont skoru hesapla"""
        try:
            # Oranları normalize et (0-100 arası)
            roe_score = min(max(roe * 100, 0), 100) if roe else 0
            roa_score = min(max(roa * 100, 0), 100) if roa else 0
            net_margin_score = min(max(net_margin * 100, 0), 100) if net_margin else 0
            asset_turnover_score = min(max(asset_turnover * 100, 0), 100) if asset_turnover else 0
            
            # Financial leverage için ters skor (düşük daha iyi)
            if financial_leverage:
                leverage_score = max(100 - (financial_leverage * 100), 0)
            else:
                leverage_score = 50  # Varsayılan
            
            # Ağırlıklı ortalama
            dupont_score = (
                roe_score * 0.3 +
                roa_score * 0.25 +
                net_margin_score * 0.2 +
                asset_turnover_score * 0.15 +
                leverage_score * 0.1
            )
            
            return dupont_score
            
        except Exception as e:
            logger.error(f"Basit DuPont skor hatası: {e}")
            return 0
    
    def calculate_piotroski_f_score(self, symbols: List[str]) -> pd.DataFrame:
        """Piotroski F-Score hesapla"""
        piotroski_data = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Piotroski F-Score kriterleri
                f_score = self._calculate_piotroski_criteria(info)
                
                piotroski_data.append({
                    'symbol': symbol,
                    'piotroski_score': f_score,
                    'piotroski_details': self._get_piotroski_details(info)
                })
                
            except Exception as e:
                logger.warning(f"{symbol} Piotroski analizi hatası: {e}")
                continue
        
        if piotroski_data:
            df = pd.DataFrame(piotroski_data)
            df.set_index('symbol', inplace=True)
            return df
        else:
            return pd.DataFrame()
    
    def _calculate_piotroski_criteria(self, info: Dict) -> int:
        """Piotroski F-Score kriterlerini hesapla"""
        f_score = 0
        
        try:
            # 1. Net Income (NI)
            if info.get('netIncomeToCommon', 0) > 0:
                f_score += 1
            
            # 2. Operating Cash Flow (OCF)
            if info.get('operatingCashflow', 0) > 0:
                f_score += 1
            
            # 3. Return on Assets (ROA)
            if info.get('returnOnAssets', 0) > 0:
                f_score += 1
            
            # 4. Quality of Earnings (OCF > NI)
            ocf = info.get('operatingCashflow', 0)
            ni = info.get('netIncomeToCommon', 0)
            if ocf > ni:
                f_score += 1
            
            # 5. Long-term Debt (LTD) decrease
            # Bu veri yfinance'da mevcut değil, varsayılan olarak 0
            f_score += 0
            
            # 6. Current Ratio (CR) increase
            # Bu veri yfinance'da mevcut değil, varsayılan olarak 0
            f_score += 0
            
            # 7. Shares Outstanding (SO) decrease
            # Bu veri yfinance'da mevcut değil, varsayılan olarak 0
            f_score += 0
            
            # 8. Gross Margin (GM) increase
            # Bu veri yfinance'da mevcut değil, varsayılan olarak 0
            f_score += 0
            
            # 9. Asset Turnover (AT) increase
            # Bu veri yfinance'da mevcut değil, varsayılan olarak 0
            f_score += 0
            
        except Exception as e:
            logger.error(f"Piotroski kriter hesaplama hatası: {e}")
        
        return f_score
    
    def _get_piotroski_details(self, info: Dict) -> Dict:
        """Piotroski detay bilgileri"""
        details = {
            'net_income_positive': info.get('netIncomeToCommon', 0) > 0,
            'operating_cash_flow_positive': info.get('operatingCashflow', 0) > 0,
            'roa_positive': info.get('returnOnAssets', 0) > 0,
            'quality_earnings': info.get('operatingCashflow', 0) > info.get('netIncomeToCommon', 0),
            'current_ratio': info.get('currentRatio', 0),
            'debt_to_equity': info.get('debtToEquity', 0),
            'gross_margin': info.get('grossMargins', 0),
            'profit_margins': info.get('profitMargins', 0)
        }
        
        return details
    
    def _normalize_ratio(self, series: pd.Series) -> pd.Series:
        """Oranları normalize et (0-1 arası)"""
        try:
            min_val = series.min()
            max_val = series.max()
            
            if max_val == min_val:
                return pd.Series([0.5] * len(series), index=series.index)
            
            normalized = (series - min_val) / (max_val - min_val)
            return normalized
            
        except Exception as e:
            logger.error(f"Normalizasyon hatası: {e}")
            return pd.Series([0.5] * len(series), index=series.index)
    
    def get_comprehensive_fundamental_analysis(self, symbols: List[str]) -> pd.DataFrame:
        """Kapsamlı fundamental analiz"""
        try:
            # DuPont analizi
            dupont_df = self.get_dupont_analysis(symbols)
            
            # Piotroski F-Score
            piotroski_df = self.calculate_piotroski_f_score(symbols)
            
            # Verileri birleştir
            if not dupont_df.empty and not piotroski_df.empty:
                # Index'leri eşleştir
                common_symbols = set(dupont_df.index) & set(piotroski_df.index)
                
                if common_symbols:
                    # Ortak sembolleri birleştir
                    combined_df = dupont_df.loc[list(common_symbols)].copy()
                    combined_df['piotroski_score'] = piotroski_df.loc[list(common_symbols), 'piotroski_score']
                    combined_df['piotroski_details'] = piotroski_df.loc[list(common_symbols), 'piotroski_details']
                    
                    # Toplam fundamental skor hesapla
                    combined_df['fundamental_score'] = (
                        combined_df['dupont_score'] * 0.6 +
                        combined_df['piotroski_score'] * 0.4
                    )
                    
                    # Skora göre sırala
                    combined_df = combined_df.sort_values('fundamental_score', ascending=False)
                    
                    logger.info(f"Kapsamlı fundamental analiz tamamlandı: {len(combined_df)} hisse")
                    return combined_df
            
            # Fallback: Sadece DuPont verisi varsa
            if not dupont_df.empty:
                dupont_df['fundamental_score'] = dupont_df['dupont_score']
                return dupont_df
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Kapsamlı fundamental analiz hatası: {e}")
            return pd.DataFrame()
    
    def filter_top_stocks(self, fundamental_df: pd.DataFrame, 
                         top_n: int = 10, 
                         min_score: float = 0.0) -> pd.DataFrame:
        """En iyi hisseleri filtrele"""
        try:
            if fundamental_df.empty:
                return pd.DataFrame()
            
            # Minimum skor filtresi
            filtered_df = fundamental_df[fundamental_df['fundamental_score'] >= min_score].copy()
            
            # Top N hisse
            if len(filtered_df) > top_n:
                filtered_df = filtered_df.head(top_n)
            
            logger.info(f"Top {len(filtered_df)} hisse filtrelendi")
            return filtered_df
            
        except Exception as e:
            logger.error(f"Hisse filtreleme hatası: {e}")
            return pd.DataFrame()

# Test fonksiyonu
def test_fundamental_analyzer():
    """Fundamental analyzer test"""
    try:
        # Test sembolleri
        test_symbols = ['SISE.IS', 'EREGL.IS', 'TUPRS.IS', 'AKBNK.IS', 'GARAN.IS']
        
        print("🧪 Fundamental Analyzer Test")
        print("="*50)
        
        # Analyzer'ı başlat
        analyzer = FundamentalAnalyzer()
        
        # DuPont analizi
        print("\n📊 DuPont Analizi:")
        dupont_df = analyzer.get_dupont_analysis(test_symbols)
        if not dupont_df.empty:
            print(dupont_df[['roe', 'roa', 'net_profit_margin', 'dupont_score']].round(4))
        else:
            print("❌ DuPont analizi başarısız")
        
        # Piotroski F-Score
        print("\n🎯 Piotroski F-Score:")
        piotroski_df = analyzer.calculate_piotroski_f_score(test_symbols)
        if not piotroski_df.empty:
            print(piotroski_df[['piotroski_score']])
        else:
            print("❌ Piotroski analizi başarısız")
        
        # Kapsamlı analiz
        print("\n🔍 Kapsamlı Fundamental Analiz:")
        comprehensive_df = analyzer.get_comprehensive_fundamental_analysis(test_symbols)
        if not comprehensive_df.empty:
            print(comprehensive_df[['dupont_score', 'piotroski_score', 'fundamental_score']].round(4))
            
            # Top 3 hisse
            top_stocks = analyzer.filter_top_stocks(comprehensive_df, top_n=3)
            print(f"\n🏆 Top 3 Hisse:")
            print(top_stocks[['fundamental_score']].round(4))
        else:
            print("❌ Kapsamlı analiz başarısız")
            
    except Exception as e:
        print(f"❌ Test hatası: {e}")

if __name__ == "__main__":
    test_fundamental_analyzer()
