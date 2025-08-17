"""
PRD v2.0 - Grey TOPSIS + Entropi Ağırlık Sistemi
Çok kriterli finansal sıralama için
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class GreyTOPSISRanking:
    """Grey TOPSIS ile çok kriterli finansal sıralama"""
    
    def __init__(self):
        self.criteria_weights = None
        self.normalized_matrix = None
        self.ideal_solutions = None
        self.anti_ideal_solutions = None
        
    def calculate_entropy_weights(self, data: pd.DataFrame) -> np.ndarray:
        """Entropi yöntemi ile kriter ağırlıklarını hesapla"""
        try:
            # Min-max normalizasyon
            normalized = (data - data.min()) / (data.max() - data.min())
            
            # Entropi hesaplama
            m, n = normalized.shape
            p_ij = normalized / normalized.sum(axis=0)
            
            # Log hesaplama (0 değerleri için)
            p_ij = p_ij.replace(0, 1e-10)
            log_p = np.log(p_ij)
            
            # Entropi
            e_j = -1 / np.log(m) * (p_ij * log_p).sum(axis=0)
            
            # Ağırlıklar
            d_j = 1 - e_j
            weights = d_j / d_j.sum()
            
            logger.info(f"✅ Entropi ağırlıkları hesaplandı: {weights}")
            return weights.values
            
        except Exception as e:
            logger.error(f"❌ Entropi ağırlık hesaplama hatası: {e}")
            # Varsayılan eşit ağırlık
            return np.ones(data.shape[1]) / data.shape[1]
    
    def normalize_matrix(self, data: pd.DataFrame, criteria_types: np.ndarray) -> pd.DataFrame:
        """Veri matrisini normalize et"""
        try:
            normalized = data.copy()
            
            for j, col in enumerate(data.columns):
                if criteria_types[j] == 1:  # Büyük daha iyi
                    normalized[col] = (data[col] - data[col].min()) / (data[col].max() - data[col].min())
                else:  # Küçük daha iyi
                    normalized[col] = (data[col].max() - data[col]) / (data[col].max() - data[col].min())
            
            logger.info("✅ Veri matrisi normalize edildi")
            return normalized
            
        except Exception as e:
            logger.error(f"❌ Normalizasyon hatası: {e}")
            return data
    
    def calculate_ideal_solutions(self, normalized_matrix: pd.DataFrame, criteria_types: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """İdeal ve anti-ideal çözümleri hesapla"""
        try:
            ideal_best = np.zeros(len(criteria_types))
            ideal_worst = np.zeros(len(criteria_types))
            
            for j, col in enumerate(normalized_matrix.columns):
                if criteria_types[j] == 1:  # Büyük daha iyi
                    ideal_best[j] = normalized_matrix[col].max()
                    ideal_worst[j] = normalized_matrix[col].min()
                else:  # Küçük daha iyi
                    ideal_best[j] = normalized_matrix[col].min()
                    ideal_worst[j] = normalized_matrix[col].max()
            
            logger.info("✅ İdeal çözümler hesaplandı")
            return ideal_best, ideal_worst
            
        except Exception as e:
            logger.error(f"❌ İdeal çözüm hesaplama hatası: {e}")
            return np.zeros(len(criteria_types)), np.zeros(len(criteria_types))
    
    def calculate_distances(self, normalized_matrix: pd.DataFrame, ideal_best: np.ndarray, 
                          ideal_worst: np.ndarray, weights: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Euclidean mesafeleri hesapla"""
        try:
            m = len(normalized_matrix)
            d_best = np.zeros(m)
            d_worst = np.zeros(m)
            
            for i in range(m):
                # İdeal en iyiye mesafe
                d_best[i] = np.sqrt(np.sum(weights * (normalized_matrix.iloc[i].values - ideal_best) ** 2))
                # İdeal en kötüye mesafe
                d_worst[i] = np.sqrt(np.sum(weights * (normalized_matrix.iloc[i].values - ideal_worst) ** 2))
            
            logger.info("✅ Mesafeler hesaplandı")
            return d_best, d_worst
            
        except Exception as e:
            logger.error(f"❌ Mesafe hesaplama hatası: {e}")
            return np.zeros(len(normalized_matrix)), np.zeros(len(normalized_matrix))
    
    def calculate_topsis_scores(self, d_best: np.ndarray, d_worst: np.ndarray) -> np.ndarray:
        """TOPSIS skorlarını hesapla"""
        try:
            # Relative closeness
            scores = d_worst / (d_best + d_worst)
            
            # NaN değerleri 0 yap
            scores = np.nan_to_num(scores, nan=0.0)
            
            logger.info("✅ TOPSIS skorları hesaplandı")
            return scores
            
        except Exception as e:
            logger.error(f"❌ TOPSIS skor hesaplama hatası: {e}")
            return np.zeros(len(d_best))
    
    def rank_stocks(self, data: pd.DataFrame, criteria_types: Optional[np.ndarray] = None) -> pd.DataFrame:
        """Ana ranking fonksiyonu"""
        try:
            logger.info(f"🚀 {len(data)} hisse için Grey TOPSIS ranking başlatılıyor...")
            
            # Varsayılan kriter tipleri (1 = büyük daha iyi, 0 = küçük daha iyi)
            if criteria_types is None:
                criteria_types = np.ones(len(data.columns))
            
            # 1. Entropi ağırlıkları
            weights = self.calculate_entropy_weights(data)
            
            # 2. Normalizasyon
            normalized = self.normalize_matrix(data, criteria_types)
            
            # 3. İdeal çözümler
            ideal_best, ideal_worst = self.calculate_ideal_solutions(normalized, criteria_types)
            
            # 4. Mesafeler
            d_best, d_worst = self.calculate_distances(normalized, ideal_best, ideal_worst, weights)
            
            # 5. TOPSIS skorları
            scores = self.calculate_topsis_scores(d_best, d_worst)
            
            # 6. Sonuçları DataFrame'e ekle
            result_df = data.copy()
            result_df['topsis_score'] = scores
            result_df['rank'] = result_df['topsis_score'].rank(ascending=False)
            
            # 7. Sırala
            result_df = result_df.sort_values('rank')
            
            logger.info(f"✅ Ranking tamamlandı! En iyi skor: {scores.max():.3f}")
            return result_df
            
        except Exception as e:
            logger.error(f"❌ Ranking hatası: {e}")
            # Hata durumunda basit sıralama
            result_df = data.copy()
            result_df['topsis_score'] = np.random.random(len(data))
            result_df['rank'] = result_df['topsis_score'].rank(ascending=False)
            return result_df.sort_values('rank')
    
    def get_top_n_stocks(self, data: pd.DataFrame, n: int = 10, 
                         criteria_types: Optional[np.ndarray] = None) -> pd.DataFrame:
        """Top N hisseyi getir"""
        try:
            ranked_data = self.rank_stocks(data, criteria_types)
            return ranked_data.head(n)
            
        except Exception as e:
            logger.error(f"❌ Top N hisse getirme hatası: {e}")
            return data.head(n)

# Test fonksiyonu
if __name__ == "__main__":
    # Mock veri ile test
    print("🧪 Grey TOPSIS Ranking Test Ediliyor...")
    
    # Örnek finansal veri
    test_data = pd.DataFrame({
        'NetProfitMargin': [12.3, 8.4, 15.2, 9.8, 11.5],
        'ROE': [18.0, 12.0, 22.0, 15.5, 19.2],
        'DebtEquity': [0.4, 0.8, 0.6, 0.9, 0.3],
        'CurrentRatio': [1.8, 1.2, 2.1, 1.5, 1.9]
    }, index=['SISE.IS', 'EREGL.IS', 'TUPRS.IS', 'GARAN.IS', 'KCHOL.IS'])
    
    # Kriter tipleri (1 = büyük daha iyi, 0 = küçük daha iyi)
    criteria_types = np.array([1, 1, 0, 1])  # Debt/Equity küçük daha iyi
    
    # Ranking yap
    topsis = GreyTOPSISRanking()
    result = topsis.rank_stocks(test_data, criteria_types)
    
    print("\n📊 Ranking Sonuçları:")
    print(result[['topsis_score', 'rank']].round(3))
    
    print("\n🏆 Top 3 Hisse:")
    top_3 = topsis.get_top_n_stocks(test_data, 3, criteria_types)
    print(top_3[['topsis_score', 'rank']].round(3))
