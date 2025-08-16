import pandas as pd
import numpy as np
from pymcdm import methods, weights, normalizations
from financetoolkit import Toolkit
import yfinance as yf
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialRankingEngine:
    """
    Çok kriterli finansal sıralama motoru
    Grey TOPSIS + Entropi ağırlık ile
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.criteria_weights = None
        self.criteria_types = None
        
    def get_financial_ratios(self, symbols: List[str]) -> pd.DataFrame:
        """
        Hisse senetleri için finansal oranları çeker
        """
        try:
            if self.api_key:
                # FMP API ile premium veri
                toolkit = Toolkit(symbols, api_key=self.api_key)
                ratios = toolkit.ratios.get_all_ratios()
                return ratios
            else:
                # yfinance ile ücretsiz veri
                return self._get_yfinance_ratios(symbols)
        except Exception as e:
            logger.error(f"Finansal oran çekme hatası: {e}")
            return self._get_yfinance_ratios(symbols)
    
    def _get_yfinance_ratios(self, symbols: List[str]) -> pd.DataFrame:
        """
        yfinance ile temel finansal oranları çeker
        """
        ratios_data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Temel finansal oranlar
                ratios_data[symbol] = {
                    'ROE': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0,
                    'ROA': info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else 0,
                    'ProfitMargin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0,
                    'DebtToEquity': info.get('debtToEquity', 0) if info.get('debtToEquity') else 0,
                    'CurrentRatio': info.get('currentRatio', 0) if info.get('currentRatio') else 0,
                    'QuickRatio': info.get('quickRatio', 0) if info.get('quickRatio') else 0,
                    'PEGRatio': info.get('pegRatio', 0) if info.get('pegRatio') else 0,
                    'PriceToBook': info.get('priceToBook', 0) if info.get('priceToBook') else 0
                }
                
            except Exception as e:
                logger.warning(f"{symbol} için veri çekilemedi: {e}")
                ratios_data[symbol] = {key: 0 for key in ['ROE', 'ROA', 'ProfitMargin', 'DebtToEquity', 'CurrentRatio', 'QuickRatio', 'PEGRatio', 'PriceToBook']}
        
        return pd.DataFrame(ratios_data).T
    
    def calculate_entropy_weights(self, criteria_matrix: pd.DataFrame) -> np.ndarray:
        """
        Entropi yöntemi ile kriter ağırlıklarını hesaplar
        """
        try:
            # Min-max normalizasyon
            scaler = (criteria_matrix - criteria_matrix.min()) / (criteria_matrix.max() - criteria_matrix.min())
            
            # Entropi hesaplama
            p_ij = scaler / scaler.sum(axis=0)
            p_ij = p_ij.replace([np.inf, -np.inf], 0)
            
            # Log hesaplama (0 log 0 = 0)
            log_p = np.log(p_ij + 1e-10)
            e_j = -np.sum(p_ij * log_p, axis=0) / np.log(len(criteria_matrix))
            
            # Ağırlık hesaplama
            d_j = 1 - e_j
            weights = d_j / d_j.sum()
            
            return weights.values
            
        except Exception as e:
            logger.error(f"Entropi ağırlık hesaplama hatası: {e}")
            # Eşit ağırlık fallback
            return np.ones(len(criteria_matrix.columns)) / len(criteria_matrix.columns)
    
    def grey_topsis_ranking(self, criteria_matrix: pd.DataFrame) -> Tuple[pd.Series, np.ndarray]:
        """
        Grey TOPSIS ile hisse sıralaması
        """
        try:
            # Entropi ağırlıkları
            weights = self.calculate_entropy_weights(criteria_matrix)
            
            # Kriter tipleri (1 = büyük daha iyi, 0 = küçük daha iyi)
            self.criteria_types = np.array([
                1,  # ROE - büyük daha iyi
                1,  # ROA - büyük daha iyi
                1,  # ProfitMargin - büyük daha iyi
                0,  # DebtToEquity - küçük daha iyi
                1,  # CurrentRatio - büyük daha iyi
                1,  # QuickRatio - büyük daha iyi
                0,  # PEGRatio - küçük daha iyi
                0   # PriceToBook - küçük daha iyi
            ])
            
            # TOPSIS hesaplama
            topsis = methods.TOPSIS()
            scores = topsis(criteria_matrix.values, weights, self.criteria_types)
            
            # Sonuçları DataFrame'e ekle
            result_df = criteria_matrix.copy()
            result_df['TOPSIS_Score'] = scores
            result_df['Rank'] = result_df['TOPSIS_Score'].rank(ascending=False)
            
            return result_df.sort_values('Rank'), weights
            
        except Exception as e:
            logger.error(f"TOPSIS hesaplama hatası: {e}")
            return pd.DataFrame(), np.array([])
    
    def get_dupont_analysis(self, symbols: List[str]) -> pd.DataFrame:
        """
        DuPont analizi ile detaylı ROE ayrıştırması
        """
        try:
            if not self.api_key:
                logger.warning("DuPont analizi için FMP API key gerekli")
                return pd.DataFrame()
            
            toolkit = Toolkit(symbols, api_key=self.api_key)
            dupont = toolkit.models.get_extended_dupont_analysis()
            return dupont.T
            
        except Exception as e:
            logger.error(f"DuPont analizi hatası: {e}")
            return pd.DataFrame()
    
    def get_piotroski_score(self, symbols: List[str]) -> pd.DataFrame:
        """
        Piotroski F-Score hesaplama
        """
        try:
            if not self.api_key:
                logger.warning("Piotroski F-Score için FMP API key gerekli")
                return pd.DataFrame()
            
            toolkit = Toolkit(symbols, api_key=self.api_key)
            piotroski = toolkit.models.get_piotroski_score()
            return piotroski.T
            
        except Exception as e:
            logger.error(f"Piotroski F-Score hatası: {e}")
            return pd.DataFrame()
    
    def rank_stocks(self, symbols: List[str], include_dupont: bool = False) -> Dict:
        """
        Ana sıralama fonksiyonu
        """
        logger.info(f"{len(symbols)} hisse için finansal sıralama başlatılıyor...")
        
        # Finansal oranları çek
        ratios = self.get_financial_ratios(symbols)
        
        if ratios.empty:
            return {"error": "Finansal veri çekilemedi"}
        
        # NaN değerleri temizle
        ratios = ratios.dropna()
        
        if len(ratios) < 2:
            return {"error": "Yeterli veri yok"}
        
        # TOPSIS sıralama
        ranked_stocks, weights = self.grey_topsis_ranking(ratios)
        
        # DuPont analizi (opsiyonel)
        dupont_data = None
        if include_dupont and self.api_key:
            dupont_data = self.get_dupont_analysis(symbols)
        
        # Piotroski F-Score (opsiyonel)
        piotroski_data = None
        if include_dupont and self.api_key:
            piotroski_data = self.get_piotroski_score(symbols)
        
        return {
            "ranked_stocks": ranked_stocks.to_dict('index'),
            "criteria_weights": {col: float(weight) for col, weight in zip(ratios.columns, weights)},
            "dupont_analysis": dupont_data.to_dict('index') if dupont_data is not None else None,
            "piotroski_scores": piotroski_data.to_dict('index') if piotroski_data is not None else None,
            "total_stocks": len(ranked_stocks),
            "ranking_date": pd.Timestamp.now().isoformat()
        }

# Test fonksiyonu
if __name__ == "__main__":
    # Test hisseleri
    test_symbols = ["SISE.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "GARAN.IS"]
    
    # Ranking engine'i başlat
    engine = FinancialRankingEngine()
    
    # Sıralama yap
    result = engine.rank_stocks(test_symbols)
    
    if "error" not in result:
        print("🎯 Finansal Sıralama Sonuçları:")
        print("=" * 50)
        
        for symbol, data in result["ranked_stocks"].items():
            print(f"#{data['Rank']:.0f} {symbol}: {data['TOPSIS_Score']:.4f}")
            print(f"   ROE: {data['ROE']:.2f}% | ROA: {data['ROA']:.2f}% | Debt/Equity: {data['DebtToEquity']:.2f}")
        
        print("\n📊 Kriter Ağırlıkları:")
        for criterion, weight in result["criteria_weights"].items():
            print(f"   {criterion}: {weight:.4f}")
    else:
        print(f"❌ Hata: {result['error']}")
