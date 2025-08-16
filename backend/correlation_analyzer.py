"""
PRD v2.0 - BIST AI Smart Trader
Correlation Analyzer Module

Portföy korelasyon analizi modülü:
- Varlık korelasyon matrisi
- Rolling correlation analizi
- Korelasyon clustering
- Çeşitlendirme metrikleri
- Korelasyon rejimi tespiti
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

@dataclass
class CorrelationResult:
    """Korelasyon analiz sonucu"""
    correlation_matrix: pd.DataFrame
    method: str
    additional_info: Dict = None

class CorrelationAnalyzer:
    """
    Portföy Korelasyon Analizörü
    
    PRD v2.0 gereksinimleri:
    - Varlık korelasyon matrisi analizi
    - Rolling correlation hesaplama
    - Korelasyon clustering ve gruplandırma
    - Portföy çeşitlendirme metrikleri
    - Korelasyon rejimi tespiti
    """
    
    def __init__(self, min_periods: int = 30, method: str = "pearson"):
        """
        Correlation Analyzer başlatıcı
        
        Args:
            min_periods: Minimum veri noktası
            method: Korelasyon metodu (pearson, spearman, kendall)
        """
        self.min_periods = min_periods
        self.method = method
        
        # Korelasyon analizi için sabitler
        self.CORRELATION_METHODS = ["pearson", "spearman", "kendall"]
        self.ROLLING_WINDOWS = [21, 63, 126, 252]  # 1a, 3a, 6a, 1y
        
    def calculate_correlation_matrix(self, returns: pd.DataFrame,
                                   method: Optional[str] = None) -> CorrelationResult:
        """
        Varlık korelasyon matrisi hesaplama
        
        Args:
            returns: Getiri matrisi (her sütun bir varlık)
            method: Korelasyon metodu
            
        Returns:
            CorrelationResult: Korelasyon analiz sonucu
        """
        if method is None:
            method = self.method
            
        if method not in self.CORRELATION_METHODS:
            raise ValueError(f"Desteklenmeyen metod: {method}")
        
        # Korelasyon matrisi hesapla
        corr_matrix = returns.corr(method=method, min_periods=self.min_periods)
        
        # NaN değerleri temizle
        corr_matrix = corr_matrix.fillna(0)
        
        # Diagonal'i 1 yap
        np.fill_diagonal(corr_matrix.values, 1.0)
        
        # Ek bilgiler
        additional_info = {
            "method": method,
            "min_periods": self.min_periods,
            "data_shape": returns.shape,
            "missing_values": returns.isnull().sum().sum(),
            "correlation_stats": {
                "mean_correlation": corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean(),
                "std_correlation": corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].std(),
                "min_correlation": corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].min(),
                "max_correlation": corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].max()
            }
        }
        
        return CorrelationResult(
            correlation_matrix=corr_matrix,
            method=method,
            additional_info=additional_info
        )
    
    def calculate_rolling_correlation(self, returns: pd.DataFrame,
                                    window: int = 63,
                                    method: Optional[str] = None) -> Dict[str, pd.Series]:
        """
        Rolling correlation hesaplama
        
        Args:
            returns: Getiri matrisi
            window: Rolling window boyutu
            method: Korelasyon metodu
            
        Returns:
            Dict: Rolling correlation sonuçları
        """
        if method is None:
            method = self.method
            
        rolling_corrs = {}
        
        # Her varlık çifti için rolling correlation
        for i, asset1 in enumerate(returns.columns):
            for j, asset2 in enumerate(returns.columns):
                if i < j:  # Üst üçgen matris
                    pair_name = f"{asset1}_vs_{asset2}"
                    
                    # Rolling correlation hesapla
                    rolling_corr = returns[asset1].rolling(
                        window=window, 
                        min_periods=self.min_periods
                    ).corr(returns[asset2])
                    
                    rolling_corrs[pair_name] = rolling_corr
        
        return rolling_corrs
    
    def calculate_correlation_clusters(self, correlation_matrix: pd.DataFrame,
                                     n_clusters: int = 5,
                                     method: str = "hierarchical") -> Dict:
        """
        Korelasyon clustering analizi
        
        Args:
            correlation_matrix: Korelasyon matrisi
            n_clusters: Cluster sayısı
            method: Clustering metodu (hierarchical, kmeans)
            
        Returns:
            Dict: Clustering sonuçları
        """
        # Korelasyon matrisini distance matrix'e çevir
        # Korelasyon 1'e yaklaştıkça distance 0'a yaklaşır
        distance_matrix = np.sqrt(2 * (1 - correlation_matrix.values))
        
        if method == "hierarchical":
            # Hierarchical clustering
            linkage_matrix = linkage(squareform(distance_matrix), method='ward')
            
            # Cluster'ları belirle
            cluster_labels = fcluster(linkage_matrix, n_clusters, criterion='maxclust')
            
            # Dendrogram bilgileri
            dendrogram_info = {
                "linkage_matrix": linkage_matrix,
                "cluster_labels": cluster_labels,
                "n_clusters": len(np.unique(cluster_labels))
            }
            
        elif method == "kmeans":
            # K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(distance_matrix)
            
            dendrogram_info = {
                "cluster_labels": cluster_labels,
                "n_clusters": n_clusters,
                "kmeans_model": kmeans
            }
            
        else:
            raise ValueError(f"Desteklenmeyen clustering metodu: {method}")
        
        # Her cluster için varlıkları grupla
        clusters = {}
        for i, label in enumerate(cluster_labels):
            asset_name = correlation_matrix.index[i]
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(asset_name)
        
        # Cluster analizi
        cluster_analysis = {}
        for cluster_id, assets in clusters.items():
            if len(assets) > 1:
                # Cluster içi ortalama korelasyon
                cluster_corr = correlation_matrix.loc[assets, assets].values
                cluster_corr = cluster_corr[np.triu_indices_from(cluster_corr, k=1)]
                avg_correlation = cluster_corr.mean()
                
                cluster_analysis[cluster_id] = {
                    "assets": assets,
                    "size": len(assets),
                    "avg_internal_correlation": avg_correlation,
                    "representative_asset": assets[0]  # İlk varlık temsili
                }
        
        return {
            "clusters": clusters,
            "cluster_analysis": cluster_analysis,
            "dendrogram_info": dendrogram_info,
            "method": method,
            "n_clusters": n_clusters
        }
    
    def calculate_diversification_metrics(self, correlation_matrix: pd.DataFrame,
                                       weights: Optional[List[float]] = None) -> Dict:
        """
        Portföy çeşitlendirme metrikleri
        
        Args:
            correlation_matrix: Korelasyon matrisi
            weights: Varlık ağırlıkları (None ise eşit ağırlık)
            
        Returns:
            Dict: Çeşitlendirme metrikleri
        """
        if weights is None:
            # Eşit ağırlık
            weights = [1.0 / len(correlation_matrix)] * len(correlation_matrix)
        
        weights = np.array(weights)
        
        # Portföy korelasyon ortalaması
        portfolio_correlation = np.sum(
            weights.reshape(-1, 1) * weights.reshape(1, -1) * correlation_matrix.values
        )
        
        # Effective N (effective number of assets)
        # Bu, portföydeki bağımsız varlık sayısını gösterir
        effective_n = 1 / np.sum(weights ** 2)
        
        # Diversification ratio
        # Portföy riski / Ağırlıklı bireysel risk
        individual_risks = np.ones(len(weights))  # Basit yaklaşım
        portfolio_risk = np.sqrt(weights.T @ correlation_matrix.values @ weights)
        weighted_individual_risk = np.sum(weights * individual_risks)
        diversification_ratio = portfolio_risk / weighted_individual_risk
        
        # Concentration index (Herfindahl-Hirschman Index)
        concentration_index = np.sum(weights ** 2)
        
        # Maximum correlation in portfolio
        max_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].max()
        
        return {
            "portfolio_correlation": portfolio_correlation,
            "effective_n": effective_n,
            "diversification_ratio": diversification_ratio,
            "concentration_index": concentration_index,
            "max_correlation": max_correlation,
            "weights": weights.tolist(),
            "diversification_score": 1 - concentration_index,  # 0-1 arası, yüksek = iyi
            "correlation_quality": 1 - max_correlation  # 0-1 arası, yüksek = iyi
        }
    
    def detect_correlation_regime(self, returns: pd.DataFrame,
                                window: int = 63,
                                threshold: float = 0.7) -> Dict:
        """
        Korelasyon rejimi tespiti
        
        Args:
            returns: Getiri matrisi
            window: Rolling window boyutu
            threshold: Yüksek korelasyon eşiği
            
        Returns:
            Dict: Korelasyon rejimi analizi
        """
        # Rolling correlation hesapla
        rolling_corrs = self.calculate_rolling_correlation(returns, window)
        
        # Her zaman noktası için ortalama korelasyon
        all_corrs = []
        dates = []
        
        for pair_name, rolling_corr in rolling_corrs.items():
            if not rolling_corr.isna().all():
                all_corrs.append(rolling_corr)
                dates.append(rolling_corr.index)
        
        if not all_corrs:
            return {"error": "Yeterli veri yok"}
        
        # Ortak tarih aralığını bul
        common_dates = set.intersection(*[set(dates[i]) for i in range(len(dates))])
        common_dates = sorted(list(common_dates))
        
        if len(common_dates) < window:
            return {"error": "Yeterli tarih verisi yok"}
        
        # Her tarih için ortalama korelasyon
        avg_correlations = []
        high_corr_periods = []
        
        for date in common_dates:
            date_corrs = []
            for corr_series in all_corrs:
                if date in corr_series.index and not pd.isna(corr_series[date]):
                    date_corrs.append(corr_series[date])
            
            if date_corrs:
                avg_corr = np.mean(date_corrs)
                avg_correlations.append(avg_corr)
                
                # Yüksek korelasyon dönemleri
                if avg_corr > threshold:
                    high_corr_periods.append({
                        "date": date,
                        "correlation": avg_corr,
                        "regime": "high_correlation"
                    })
                elif avg_corr < 0.3:
                    high_corr_periods.append({
                        "date": date,
                        "correlation": avg_corr,
                        "regime": "low_correlation"
                    })
                else:
                    high_corr_periods.append({
                        "date": date,
                        "correlation": avg_corr,
                        "regime": "normal_correlation"
                    })
        
        # Rejim istatistikleri
        regime_stats = {}
        for regime in ["high_correlation", "normal_correlation", "low_correlation"]:
            regime_data = [p for p in high_corr_periods if p["regime"] == regime]
            if regime_data:
                regime_stats[regime] = {
                    "count": len(regime_data),
                    "percentage": len(regime_data) / len(high_corr_periods) * 100,
                    "avg_correlation": np.mean([p["correlation"] for p in regime_data])
                }
        
        return {
            "avg_correlations": avg_correlations,
            "dates": common_dates,
            "regime_periods": high_corr_periods,
            "regime_stats": regime_stats,
            "window": window,
            "threshold": threshold,
            "total_periods": len(common_dates)
        }
    
    def calculate_correlation_heatmap(self, correlation_matrix: pd.DataFrame,
                                    save_path: Optional[str] = None) -> None:
        """
        Korelasyon heatmap oluşturma (matplotlib ile)
        
        Args:
            correlation_matrix: Korelasyon matrisi
            save_path: Kaydetme yolu (None ise gösterme)
        """
        plt.figure(figsize=(12, 10))
        
        # Heatmap oluştur (matplotlib ile)
        im = plt.imshow(correlation_matrix.values, cmap='RdBu_r', aspect='auto')
        plt.colorbar(im)
        
        # Axis labels
        plt.xticks(range(len(correlation_matrix.columns)), correlation_matrix.columns, rotation=45)
        plt.yticks(range(len(correlation_matrix.index)), correlation_matrix.index)
        
        # Korelasyon değerlerini ekle
        for i in range(len(correlation_matrix.index)):
            for j in range(len(correlation_matrix.columns)):
                plt.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                        ha='center', va='center', fontsize=8)
        
        plt.title(f'Varlık Korelasyon Matrisi ({correlation_matrix.shape[0]} varlık)')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 Heatmap kaydedildi: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def generate_correlation_report(self, returns: pd.DataFrame,
                                  weights: Optional[List[float]] = None) -> Dict:
        """
        Kapsamlı korelasyon raporu oluşturma
        
        Args:
            returns: Getiri matrisi
            weights: Varlık ağırlıkları
            
        Returns:
            Dict: Kapsamlı korelasyon raporu
        """
        print("📊 Korelasyon Raporu Oluşturuluyor...")
        
        # Temel korelasyon matrisi
        corr_result = self.calculate_correlation_matrix(returns)
        correlation_matrix = corr_result.correlation_matrix
        
        # Çeşitlendirme metrikleri
        diversification_metrics = self.calculate_diversification_metrics(
            correlation_matrix, weights
        )
        
        # Clustering analizi
        clustering_result = self.calculate_correlation_clusters(correlation_matrix, n_clusters=5)
        
        # Rolling correlation analizi
        rolling_corrs = self.calculate_rolling_correlation(returns, window=63)
        
        # Korelasyon rejimi tespiti
        regime_analysis = self.detect_correlation_regime(returns)
        
        # Rapor oluştur
        report = {
            "correlation_matrix": correlation_matrix.to_dict(),
            "diversification_metrics": diversification_metrics,
            "clustering_analysis": clustering_result,
            "rolling_correlation_summary": {
                "n_pairs": len(rolling_corrs),
                "window_size": 63,
                "method": self.method
            },
            "regime_analysis": regime_analysis,
            "summary": {
                "n_assets": len(returns.columns),
                "n_periods": len(returns),
                "correlation_method": self.method,
                "min_periods": self.min_periods,
                "diversification_score": diversification_metrics["diversification_score"],
                "correlation_quality": diversification_metrics["correlation_quality"]
            }
        }
        
        print("✅ Korelasyon Raporu Tamamlandı!")
        return report

# Test fonksiyonu
def test_correlation_analyzer():
    """Correlation Analyzer test fonksiyonu"""
    print("🧪 Correlation Analyzer Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    n_days = 252  # 1 yıl
    n_assets = 10
    
    # Korele edilmiş getiri verisi
    returns_data = {}
    for i in range(n_assets):
        if i == 0:
            base_returns = np.random.normal(0.001, 0.02, n_days)
            returns_data[f'Asset_{i+1}'] = base_returns
        else:
            # Korelasyon ekle
            correlation = 0.3 + 0.4 * np.random.random()  # 0.3-0.7 arası
            noise = np.random.normal(0, 0.01, n_days)
            returns_data[f'Asset_{i+1}'] = correlation * base_returns + (1-correlation) * noise
    
    returns = pd.DataFrame(returns_data, 
                          index=pd.date_range('2023-01-01', periods=n_days, freq='D'))
    
    # Correlation Analyzer başlat
    corr_analyzer = CorrelationAnalyzer(min_periods=30, method="pearson")
    
    # Temel korelasyon matrisi test
    print("\n📊 Korelasyon Matrisi Test:")
    corr_result = corr_analyzer.calculate_correlation_matrix(returns)
    print(f"   Matris boyutu: {corr_result.correlation_matrix.shape}")
    print(f"   Metod: {corr_result.method}")
    print(f"   Ortalama korelasyon: {corr_result.additional_info['correlation_stats']['mean_correlation']:.4f}")
    
    # Çeşitlendirme metrikleri test
    print("\n🔄 Çeşitlendirme Metrikleri Test:")
    div_metrics = corr_analyzer.calculate_diversification_metrics(corr_result.correlation_matrix)
    print(f"   Çeşitlendirme skoru: {div_metrics['diversification_score']:.4f}")
    print(f"   Effective N: {div_metrics['effective_n']:.2f}")
    print(f"   Maksimum korelasyon: {div_metrics['max_correlation']:.4f}")
    
    # Clustering test
    print("\n🎯 Clustering Test:")
    clustering = corr_analyzer.calculate_correlation_clusters(corr_result.correlation_matrix, n_clusters=3)
    print(f"   Cluster sayısı: {clustering['n_clusters']}")
    for cluster_id, info in clustering['cluster_analysis'].items():
        print(f"   Cluster {cluster_id}: {len(info['assets'])} varlık, "
              f"Ort. korelasyon: {info['avg_internal_correlation']:.4f}")
    
    # Rolling correlation test
    print("\n📈 Rolling Correlation Test:")
    rolling_corrs = corr_analyzer.calculate_rolling_correlation(returns, window=63)
    print(f"   Varlık çifti sayısı: {len(rolling_corrs)}")
    
    # Korelasyon rejimi test
    print("\n🔄 Korelasyon Rejimi Test:")
    regime = corr_analyzer.detect_correlation_regime(returns)
    if "error" not in regime:
        print(f"   Toplam dönem: {regime['total_periods']}")
        for regime_name, stats in regime['regime_stats'].items():
            print(f"   {regime_name}: {stats['count']} dönem ({stats['percentage']:.1f}%)")
    
    print("\n✅ Correlation Analyzer Test Tamamlandı!")
    return corr_analyzer

if __name__ == "__main__":
    test_correlation_analyzer()
