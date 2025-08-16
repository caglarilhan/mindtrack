"""
PRD v2.0 - Çok-Kriterli Finansal Sıralama
GRA → Entropi ağırlık → TOPSIS skor
PyMCDM + pandas ile Günlük skor diff < 5 % hedefi
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from pymcdm import methods, weights, normalizations
from sklearn.preprocessing import MinMaxScaler
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GreyTOPSISRanking:
    """Grey TOPSIS + Entropi ağırlık ile finansal sıralama"""
    
    def __init__(self):
        self.criteria_weights = None
        self.criteria_types = None
        self.scaler = MinMaxScaler()
        
    def calculate_entropy_weights(self, criteria_matrix: pd.DataFrame) -> np.ndarray:
        """Entropi ağırlık hesaplama"""
        try:
            # Normalize et
            normalized_matrix = self.scaler.fit_transform(criteria_matrix.values)
            
            # Entropi ağırlık hesapla
            w = weights.entropy_weights(normalized_matrix)
            
            logger.info(f"Entropi ağırlıkları hesaplandı: {w}")
            return w
            
        except Exception as e:
            logger.error(f"Entropi ağırlık hesaplama hatası: {e}")
            # Varsayılan eşit ağırlık
            n_criteria = criteria_matrix.shape[1]
            return np.ones(n_criteria) / n_criteria
    
    def determine_criteria_types(self, criteria_names: List[str]) -> np.ndarray:
        """Kriter türlerini belirle (1 = büyük daha iyi, 0 = küçük daha iyi)"""
        # Finansal oranlar için kriter türleri
        positive_criteria = {
            'roe', 'roa', 'net_profit_margin', 'gross_margin', 'operating_margin',
            'ebitda_margin', 'current_ratio', 'quick_ratio', 'asset_turnover',
            'revenue_growth', 'earnings_growth', 'dividend_yield', 'dupont_score',
            'piotroski_score'
        }
        
        negative_criteria = {
            'debt_to_equity', 'debt_to_assets', 'pe_ratio', 'pb_ratio',
            'ps_ratio', 'beta', 'volatility', 'max_drawdown'
        }
        
        criteria_types = []
        for criterion in criteria_names:
            if criterion.lower() in positive_criteria:
                criteria_types.append(1)  # Büyük daha iyi
            elif criterion.lower() in negative_criteria:
                criteria_types.append(0)  # Küçük daha iyi
            else:
                # Varsayılan olarak büyük daha iyi
                criteria_types.append(1)
        
        logger.info(f"Kriter türleri belirlendi: {criteria_types}")
        return np.array(criteria_types)
    
    def grey_relational_analysis(self, criteria_matrix: pd.DataFrame) -> pd.DataFrame:
        """Grey Relational Analysis (GRA) uygula"""
        try:
            # Referans değerleri (en iyi değerler)
            reference_values = []
            for col in criteria_matrix.columns:
                if col.lower() in ['debt_to_equity', 'debt_to_assets', 'pe_ratio', 'pb_ratio', 'ps_ratio', 'beta', 'volatility']:
                    # Bu kriterler için en düşük değer referans
                    reference_values.append(criteria_matrix[col].min())
                else:
                    # Diğer kriterler için en yüksek değer referans
                    reference_values.append(criteria_matrix[col].max())
            
            # Grey relational coefficient hesapla
            grey_coefficients = []
            for _, row in criteria_matrix.iterrows():
                row_coefficients = []
                for i, value in enumerate(row):
                    ref_value = reference_values[i]
                    delta = abs(value - ref_value)
                    max_delta = criteria_matrix.iloc[:, i].max() - criteria_matrix.iloc[:, i].min()
                    
                    if max_delta == 0:
                        coefficient = 1.0
                    else:
                        # Distinguishing coefficient (genellikle 0.5)
                        rho = 0.5
                        min_delta = 0  # Minimum delta değeri
                        coefficient = (min_delta + rho * max_delta) / (delta + rho * max_delta)
                    
                    row_coefficients.append(coefficient)
                grey_coefficients.append(row_coefficients)
            
            grey_df = pd.DataFrame(grey_coefficients, 
                                 index=criteria_matrix.index,
                                 columns=criteria_matrix.columns)
            
            logger.info("Grey Relational Analysis tamamlandı")
            return grey_df
            
        except Exception as e:
            logger.error(f"GRA hesaplama hatası: {e}")
            return criteria_matrix
    
    def calculate_topsis_scores(self, criteria_matrix: pd.DataFrame, 
                               weights: np.ndarray, 
                               criteria_types: np.ndarray) -> Tuple[np.ndarray, pd.Series]:
        """TOPSIS skorları hesapla"""
        try:
            # TOPSIS metodunu uygula
            topsis = methods.TOPSIS()
            scores = topsis(criteria_matrix.values, weights, criteria_types)
            
            # Skorları Series olarak döndür
            score_series = pd.Series(scores, index=criteria_matrix.index)
            
            logger.info(f"TOPSIS skorları hesaplandı: {len(scores)} hisse")
            return scores, score_series
            
        except Exception as e:
            logger.error(f"TOPSIS hesaplama hatası: {e}")
            return np.array([]), pd.Series()
    
    def rank_stocks(self, fundamental_data: pd.DataFrame, 
                    criteria_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Hisse sıralaması yap"""
        try:
            if criteria_columns is None:
                # Varsayılan kriterler
                criteria_columns = [
                    'roe', 'roa', 'net_profit_margin', 'debt_to_equity',
                    'current_ratio', 'gross_margin', 'operating_margin',
                    'asset_turnover', 'dupont_score', 'piotroski_score'
                ]
            
            # Sadece mevcut kriterleri kullan
            available_criteria = [col for col in criteria_columns if col in fundamental_data.columns]
            
            if len(available_criteria) < 2:
                logger.warning(f"Yetersiz kriter sayısı: {len(available_criteria)}")
                return pd.DataFrame()
            
            # Kriter matrisini hazırla
            criteria_matrix = fundamental_data[available_criteria].copy()
            
            # NaN değerleri temizle
            criteria_matrix = criteria_matrix.dropna()
            
            if len(criteria_matrix) == 0:
                logger.warning("Kriter matrisinde veri kalmadı")
                return pd.DataFrame()
            
            # Kriter türlerini belirle
            self.criteria_types = self.determine_criteria_types(available_criteria)
            
            # Entropi ağırlıkları hesapla
            self.criteria_weights = self.calculate_entropy_weights(criteria_matrix)
            
            # Grey Relational Analysis uygula
            grey_matrix = self.grey_relational_analysis(criteria_matrix)
            
            # TOPSIS skorları hesapla
            topsis_scores, score_series = self.calculate_topsis_scores(
                grey_matrix, self.criteria_weights, self.criteria_types
            )
            
            if len(topsis_scores) == 0:
                return pd.DataFrame()
            
            # Sonuçları DataFrame'e ekle
            result_df = fundamental_data.loc[criteria_matrix.index].copy()
            result_df['topsis_score'] = topsis_scores
            result_df['grey_score'] = grey_matrix.mean(axis=1)
            result_df['entropy_weights'] = [self.criteria_weights.tolist()] * len(result_df)
            
            # Skora göre sırala
            result_df = result_df.sort_values('topsis_score', ascending=False)
            
            # Rank ekle
            result_df['rank'] = range(1, len(result_df) + 1)
            
            logger.info(f"Hisse sıralaması tamamlandı: {len(result_df)} hisse")
            return result_df
            
        except Exception as e:
            logger.error(f"Hisse sıralama hatası: {e}")
            return pd.DataFrame()
    
    def get_ranking_summary(self, ranked_df: pd.DataFrame) -> Dict:
        """Sıralama özeti"""
        if ranked_df.empty:
            return {}
        
        summary = {
            'total_stocks': len(ranked_df),
            'top_5_stocks': ranked_df.head(5)[['symbol', 'topsis_score', 'rank']].to_dict('records'),
            'bottom_5_stocks': ranked_df.tail(5)[['symbol', 'topsis_score', 'rank']].to_dict('records'),
            'score_statistics': {
                'mean': ranked_df['topsis_score'].mean(),
                'std': ranked_df['topsis_score'].std(),
                'min': ranked_df['topsis_score'].min(),
                'max': ranked_df['topsis_score'].max()
            },
            'criteria_weights': self.criteria_weights.tolist() if self.criteria_weights is not None else [],
            'criteria_types': self.criteria_types.tolist() if self.criteria_types is not None else []
        }
        
        return summary
    
    def validate_ranking(self, ranked_df: pd.DataFrame, 
                        previous_ranking: Optional[pd.DataFrame] = None) -> Dict:
        """Sıralama validasyonu"""
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        if ranked_df.empty:
            validation_results['is_valid'] = False
            validation_results['errors'].append("Sıralama sonucu boş")
            return validation_results
        
        # Skor aralığı kontrolü
        if ranked_df['topsis_score'].min() < 0 or ranked_df['topsis_score'].max() > 1:
            validation_results['warnings'].append("TOPSIS skorları 0-1 aralığında değil")
        
        # Önceki sıralama ile karşılaştır
        if previous_ranking is not None and not previous_ranking.empty:
            common_symbols = set(ranked_df.index) & set(previous_ranking.index)
            
            if len(common_symbols) > 0:
                for symbol in common_symbols:
                    current_rank = ranked_df.loc[symbol, 'rank']
                    previous_rank = previous_ranking.loc[symbol, 'rank']
                    rank_change = abs(current_rank - previous_rank)
                    
                    # %5'ten fazla değişim uyarısı
                    if rank_change > len(ranked_df) * 0.05:
                        validation_results['warnings'].append(
                            f"{symbol} rank değişimi yüksek: {previous_rank} → {current_rank}"
                        )
        
        return validation_results

# Test fonksiyonu
def test_grey_topsis():
    """Grey TOPSIS test"""
    try:
        # Test verisi oluştur
        test_data = pd.DataFrame({
            'roe': [18.5, 12.3, 22.1, 15.7, 19.8],
            'roa': [8.2, 5.1, 12.4, 7.8, 9.5],
            'net_profit_margin': [12.3, 8.4, 15.2, 10.1, 13.7],
            'debt_to_equity': [0.4, 0.8, 0.6, 0.9, 0.3],
            'current_ratio': [1.8, 1.2, 2.1, 1.5, 1.9],
            'gross_margin': [35.2, 28.7, 42.1, 31.5, 38.9]
        }, index=['SISE', 'EREGL', 'TUPRS', 'AKBNK', 'GARAN'])
        
        print("🧪 Test verisi:")
        print(test_data)
        print("\n" + "="*50)
        
        # Grey TOPSIS uygula
        ranking = GreyTOPSISRanking()
        ranked_stocks = ranking.rank_stocks(test_data)
        
        if not ranked_stocks.empty:
            print("🏆 Sıralama Sonuçları:")
            print(ranked_stocks[['topsis_score', 'rank']])
            
            print("\n📊 Sıralama Özeti:")
            summary = ranking.get_ranking_summary(ranked_stocks)
            print(f"Toplam hisse: {summary['total_stocks']}")
            print(f"En iyi 3: {[stock['symbol'] for stock in summary['top_5_stocks'][:3]]}")
            print(f"Skor ortalaması: {summary['score_statistics']['mean']:.4f}")
            
            print("\n⚖️ Kriter Ağırlıkları:")
            for i, weight in enumerate(summary['criteria_weights']):
                print(f"{test_data.columns[i]}: {weight:.4f}")
            
            # Validasyon
            validation = ranking.validate_ranking(ranked_stocks)
            print(f"\n✅ Validasyon: {'Başarılı' if validation['is_valid'] else 'Başarısız'}")
            if validation['warnings']:
                print(f"⚠️ Uyarılar: {validation['warnings']}")
                
        else:
            print("❌ Sıralama başarısız!")
            
    except Exception as e:
        print(f"❌ Test hatası: {e}")

if __name__ == "__main__":
    test_grey_topsis()
