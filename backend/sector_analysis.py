"""
PRD v2.0 - BIST AI Smart Trader
Sector Analysis Module

Sektör analizi modülü:
- Sector classification
- Sector performance
- Sector rotation
- Sector correlation
- Sector risk analysis
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
class SectorInfo:
    """Sektör bilgisi"""
    name: str
    code: str
    description: str
    market_cap: float
    constituents: List[str]

@dataclass
class SectorPerformance:
    """Sektör performans metrikleri"""
    sector_name: str
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    beta: float
    alpha: float

class SectorAnalysis:
    """
    Sektör Analiz Motoru
    
    PRD v2.0 gereksinimleri:
    - Sektör sınıflandırması ve kategorizasyon
    - Sektör performans analizi
    - Sektör rotasyon stratejileri
    - Sektör korelasyon analizi
    - Sektör risk değerlendirmesi
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Sector Analysis başlatıcı
        
        Args:
            risk_free_rate: Risksiz faiz oranı
        """
        self.risk_free_rate = risk_free_rate
        
        # BIST sektör tanımları
        self.BIST_SECTORS = {
            "FINANCIAL": {
                "name": "Finansal Hizmetler",
                "description": "Banka, sigorta, leasing şirketleri",
                "keywords": ["bank", "sigorta", "leasing", "finans", "kredi"]
            },
            "INDUSTRIAL": {
                "name": "Sanayi",
                "description": "Üretim, otomotiv, makine",
                "keywords": ["sanayi", "üretim", "otomotiv", "makine", "fabrika"]
            },
            "TECHNOLOGY": {
                "name": "Teknoloji",
                "description": "Yazılım, elektronik, telekomünikasyon",
                "keywords": ["teknoloji", "yazılım", "elektronik", "telekom", "internet"]
            },
            "ENERGY": {
                "name": "Enerji",
                "description": "Petrol, doğalgaz, elektrik",
                "keywords": ["enerji", "petrol", "doğalgaz", "elektrik", "yakıt"]
            },
            "MATERIALS": {
                "name": "Hammaddeler",
                "description": "Çimento, demir-çelik, kimya",
                "keywords": ["çimento", "demir", "çelik", "kimya", "hammadde"]
            },
            "CONSUMER_DISCRETIONARY": {
                "name": "Tüketici İsteğe Bağlı",
                "description": "Perakende, eğlence, otomotiv",
                "keywords": ["perakende", "eğlence", "otomotiv", "giyim", "yemek"]
            },
            "CONSUMER_STAPLES": {
                "name": "Tüketici Temel İhtiyaçları",
                "description": "Gıda, içecek, temizlik",
                "keywords": ["gıda", "içecek", "temizlik", "sağlık", "temel"]
            },
            "HEALTHCARE": {
                "name": "Sağlık",
                "description": "İlaç, hastane, medikal cihaz",
                "keywords": ["sağlık", "ilaç", "hastane", "medikal", "tıp"]
            },
            "UTILITIES": {
                "name": "Kamu Hizmetleri",
                "description": "Su, elektrik, doğalgaz dağıtımı",
                "keywords": ["kamu", "su", "elektrik", "dağıtım", "altyapı"]
            },
            "REAL_ESTATE": {
                "name": "Gayrimenkul",
                "description": "İnşaat, emlak, REIT",
                "keywords": ["gayrimenkul", "inşaat", "emlak", "REIT", "konut"]
            }
        }
        
        # Sektör rotasyon stratejileri
        self.ROTATION_STRATEGIES = {
            "MOMENTUM": "Momentum bazlı rotasyon",
            "MEAN_REVERSION": "Ortalama dönüş rotasyonu",
            "ECONOMIC_CYCLE": "Ekonomik döngü rotasyonu",
            "RISK_ADJUSTED": "Risk-ayarlı rotasyon"
        }
    
    def classify_assets_by_sector(self, asset_names: List[str],
                                 sector_mapping: Optional[Dict[str, str]] = None) -> Dict[str, List[str]]:
        """
        Varlıkları sektöre göre sınıflandırma
        
        Args:
            asset_names: Varlık isimleri listesi
            sector_mapping: Manuel sektör eşleştirmesi
            
        Returns:
            Dict: Sektör bazında varlık grupları
        """
        if sector_mapping is None:
            # Otomatik sektör sınıflandırması
            sector_assets = {sector: [] for sector in self.BIST_SECTORS.keys()}
            
            for asset in asset_names:
                asset_upper = asset.upper()
                best_sector = "UNKNOWN"
                best_score = 0
                
                for sector, info in self.BIST_SECTORS.items():
                    score = 0
                    for keyword in info["keywords"]:
                        if keyword.upper() in asset_upper:
                            score += 1
                    
                    if score > best_score:
                        best_score = score
                        best_sector = sector
                
                if best_score > 0:
                    sector_assets[best_sector].append(asset)
                else:
                    # Bilinmeyen sektör
                    if "UNKNOWN" not in sector_assets:
                        sector_assets["UNKNOWN"] = []
                    sector_assets["UNKNOWN"].append(asset)
        else:
            # Manuel sektör eşleştirmesi kullan
            sector_assets = {sector: [] for sector in set(sector_mapping.values())}
            
            for asset, sector in sector_mapping.items():
                if sector in sector_assets:
                    sector_assets[sector].append(asset)
        
        return sector_assets
    
    def calculate_sector_performance(self, sector_returns: pd.DataFrame,
                                   benchmark_returns: Optional[pd.Series] = None) -> Dict[str, SectorPerformance]:
        """
        Sektör performans metrikleri hesaplama
        
        Args:
            sector_returns: Sektör getiri matrisi
            benchmark_returns: Benchmark getiri serisi
            
        Returns:
            Dict: Sektör performans metrikleri
        """
        sector_performance = {}
        
        for sector in sector_returns.columns:
            returns = sector_returns[sector].dropna()
            
            if len(returns) == 0:
                continue
            
            # Temel metrikler
            total_return = (1 + returns).prod() - 1
            annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
            volatility = returns.std() * np.sqrt(252)
            
            # Sharpe ratio
            excess_returns = returns - self.risk_free_rate / 252
            sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
            
            # Maximum drawdown
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = abs(drawdown.min())
            
            # Beta ve Alpha (benchmark varsa)
            beta = 1.0
            alpha = 0.0
            if benchmark_returns is not None and len(benchmark_returns) > 0:
                # Ortak tarih aralığını bul
                common_dates = returns.index.intersection(benchmark_returns.index)
                if len(common_dates) > 10:
                    sector_common = returns.loc[common_dates]
                    benchmark_common = benchmark_returns.loc[common_dates]
                    
                    # Beta hesaplama
                    covariance = np.cov(sector_common, benchmark_common)[0, 1]
                    benchmark_variance = benchmark_common.var()
                    beta = covariance / benchmark_variance if benchmark_variance > 0 else 1.0
                    
                    # Alpha hesaplama
                    alpha = sector_common.mean() - beta * benchmark_common.mean()
            
            sector_performance[sector] = SectorPerformance(
                sector_name=sector,
                total_return=total_return,
                annualized_return=annualized_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                beta=beta,
                alpha=alpha
            )
        
        return sector_performance
    
    def analyze_sector_rotation(self, sector_returns: pd.DataFrame,
                               strategy: str = "MOMENTUM",
                               lookback_period: int = 63,
                               rebalance_frequency: int = 21) -> Dict:
        """
        Sektör rotasyon analizi
        
        Args:
            sector_returns: Sektör getiri matrisi
            strategy: Rotasyon stratejisi
            lookback_period: Geriye dönük analiz periyodu
            rebalance_frequency: Yeniden dengeleme sıklığı
            
        Returns:
            Dict: Sektör rotasyon analizi
        """
        print(f"🔄 Sektör rotasyon analizi: {strategy} stratejisi")
        
        # Rolling performans hesapla
        rolling_performance = {}
        for sector in sector_returns.columns:
            if strategy == "MOMENTUM":
                # Momentum: Son N günlük toplam getiri
                rolling_performance[sector] = sector_returns[sector].rolling(
                    window=lookback_period
                ).apply(lambda x: (1 + x).prod() - 1)
            
            elif strategy == "MEAN_REVERSION":
                # Mean reversion: Z-score (getiri - ortalama) / standart sapma
                rolling_mean = sector_returns[sector].rolling(window=lookback_period).mean()
                rolling_std = sector_returns[sector].rolling(window=lookback_period).std()
                rolling_performance[sector] = (sector_returns[sector] - rolling_mean) / rolling_std
            
            elif strategy == "ECONOMIC_CYCLE":
                # Basit ekonomik döngü: Volatilite bazlı
                rolling_performance[sector] = sector_returns[sector].rolling(
                    window=lookback_period
                ).std()
            
            elif strategy == "RISK_ADJUSTED":
                # Risk-ayarlı: Sharpe ratio
                rolling_mean = sector_returns[sector].rolling(window=lookback_period).mean()
                rolling_std = sector_returns[sector].rolling(window=lookback_period).std()
                rolling_performance[sector] = rolling_mean / rolling_std
        
        # Performans DataFrame'i oluştur
        performance_df = pd.DataFrame(rolling_performance)
        
        # Rotasyon sinyalleri
        rotation_signals = {}
        for i, date in enumerate(performance_df.index[lookback_period:]):
            if i % rebalance_frequency == 0:  # Yeniden dengeleme günü
                current_performance = performance_df.loc[date]
                
                if strategy == "MOMENTUM":
                    # En yüksek momentum'lu sektörleri seç
                    top_sectors = current_performance.nlargest(3)
                    rotation_signals[date] = {
                        "action": "BUY",
                        "sectors": top_sectors.index.tolist(),
                        "weights": [0.4, 0.35, 0.25],  # Ağırlıklar
                        "strategy": strategy
                    }
                
                elif strategy == "MEAN_REVERSION":
                    # En düşük z-score'lu sektörleri seç (aşırı satım)
                    bottom_sectors = current_performance.nsmallest(3)
                    rotation_signals[date] = {
                        "action": "BUY",
                        "sectors": bottom_sectors.index.tolist(),
                        "weights": [0.4, 0.35, 0.25],
                        "strategy": strategy
                    }
                
                elif strategy == "ECONOMIC_CYCLE":
                    # Düşük volatiliteli sektörleri seç (risk-off)
                    low_vol_sectors = current_performance.nsmallest(3)
                    rotation_signals[date] = {
                        "action": "BUY",
                        "sectors": low_vol_sectors.index.tolist(),
                        "weights": [0.4, 0.35, 0.25],
                        "strategy": strategy
                    }
                
                elif strategy == "RISK_ADJUSTED":
                    # En yüksek Sharpe ratio'lu sektörleri seç
                    top_sharpe_sectors = current_performance.nlargest(3)
                    rotation_signals[date] = {
                        "action": "BUY",
                        "sectors": top_sharpe_sectors.index.tolist(),
                        "weights": [0.4, 0.35, 0.25],
                        "strategy": strategy
                    }
        
        return {
            "strategy": strategy,
            "lookback_period": lookback_period,
            "rebalance_frequency": rebalance_frequency,
            "rolling_performance": performance_df,
            "rotation_signals": rotation_signals,
            "total_signals": len(rotation_signals)
        }
    
    def calculate_sector_correlation(self, sector_returns: pd.DataFrame,
                                   rolling_window: int = 63) -> Dict:
        """
        Sektör korelasyon analizi
        
        Args:
            sector_returns: Sektör getiri matrisi
            rolling_window: Rolling korelasyon penceresi
            
        Returns:
            Dict: Sektör korelasyon analizi
        """
        print("📊 Sektör korelasyon analizi hesaplanıyor...")
        
        # Tam dönem korelasyon matrisi
        full_correlation = sector_returns.corr()
        
        # Rolling korelasyon analizi
        rolling_correlations = {}
        for sector1 in sector_returns.columns:
            for sector2 in sector_returns.columns:
                if sector1 < sector2:  # Üst üçgen matris
                    pair_name = f"{sector1}_vs_{sector2}"
                    
                    rolling_corr = sector_returns[sector1].rolling(
                        window=rolling_window
                    ).corr(sector_returns[sector2])
                    
                    rolling_correlations[pair_name] = rolling_corr
        
        # Sektör korelasyon istatistikleri
        correlation_stats = {}
        for sector in sector_returns.columns:
            sector_corrs = []
            for other_sector in sector_returns.columns:
                if sector != other_sector:
                    sector_corrs.append(full_correlation.loc[sector, other_sector])
            
            correlation_stats[sector] = {
                "avg_correlation": np.mean(sector_corrs),
                "min_correlation": np.min(sector_corrs),
                "max_correlation": np.max(sector_corrs),
                "correlation_std": np.std(sector_corrs)
            }
        
        return {
            "full_correlation_matrix": full_correlation,
            "rolling_correlations": rolling_correlations,
            "correlation_statistics": correlation_stats,
            "rolling_window": rolling_window
        }
    
    def analyze_sector_risk(self, sector_returns: pd.DataFrame,
                           sector_weights: Optional[Dict[str, float]] = None) -> Dict:
        """
        Sektör risk analizi
        
        Args:
            sector_returns: Sektör getiri matrisi
            sector_weights: Sektör ağırlıkları (None ise eşit ağırlık)
            
        Returns:
            Dict: Sektör risk analizi
        """
        print("⚠️ Sektör risk analizi hesaplanıyor...")
        
        if sector_weights is None:
            # Eşit ağırlık
            sectors = sector_returns.columns
            sector_weights = {sector: 1.0 / len(sectors) for sector in sectors}
        
        # Sektör bazında risk metrikleri
        sector_risk_metrics = {}
        for sector in sector_returns.columns:
            returns = sector_returns[sector].dropna()
            
            if len(returns) == 0:
                continue
            
            # Risk metrikleri
            volatility = returns.std() * np.sqrt(252)
            var_95 = np.percentile(returns, 5)
            cvar_95 = returns[returns <= var_95].mean()
            
            # Maximum drawdown
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = abs(drawdown.min())
            
            sector_risk_metrics[sector] = {
                "volatility": volatility,
                "var_95": abs(var_95),
                "cvar_95": abs(cvar_95),
                "max_drawdown": max_drawdown,
                "weight": sector_weights.get(sector, 0)
            }
        
        # Portföy seviyesinde risk
        portfolio_returns = pd.Series(0.0, index=sector_returns.index)
        for sector, weight in sector_weights.items():
            if sector in sector_returns.columns:
                portfolio_returns += weight * sector_returns[sector]
        
        portfolio_volatility = portfolio_returns.std() * np.sqrt(252)
        portfolio_var_95 = np.percentile(portfolio_returns, 5)
        
        # Risk katkısı analizi
        risk_contribution = {}
        for sector, weight in sector_weights.items():
            if sector in sector_returns.columns:
                sector_vol = sector_returns[sector].std() * np.sqrt(252)
                risk_contribution[sector] = weight * sector_vol / portfolio_volatility if portfolio_volatility > 0 else 0
        
        return {
            "sector_risk_metrics": sector_risk_metrics,
            "portfolio_risk": {
                "volatility": portfolio_volatility,
                "var_95": abs(portfolio_var_95),
                "total_weight": sum(sector_weights.values())
            },
            "risk_contribution": risk_contribution,
            "sector_weights": sector_weights
        }
    
    def generate_sector_report(self, sector_returns: pd.DataFrame,
                              benchmark_returns: Optional[pd.Series] = None,
                              sector_mapping: Optional[Dict[str, str]] = None) -> Dict:
        """
        Kapsamlı sektör raporu oluşturma
        
        Args:
            sector_returns: Sektör getiri matrisi
            benchmark_returns: Benchmark getiri serisi
            sector_mapping: Sektör eşleştirmesi
            
        Returns:
            Dict: Kapsamlı sektör raporu
        """
        print("📊 Sektör Raporu Oluşturuluyor...")
        
        # Sektör sınıflandırması
        asset_names = list(sector_returns.columns)
        sector_classification = self.classify_assets_by_sector(asset_names, sector_mapping)
        
        # Sektör performans analizi
        sector_performance = self.calculate_sector_performance(sector_returns, benchmark_returns)
        
        # Sektör rotasyon analizi
        rotation_analysis = self.analyze_sector_rotation(sector_returns, strategy="MOMENTUM")
        
        # Sektör korelasyon analizi
        correlation_analysis = self.calculate_sector_correlation(sector_returns)
        
        # Sektör risk analizi
        risk_analysis = self.analyze_sector_risk(sector_returns)
        
        # Rapor oluştur
        report = {
            "sector_classification": sector_classification,
            "sector_performance": {
                sector: {
                    "total_return": perf.total_return,
                    "annualized_return": perf.annualized_return,
                    "volatility": perf.volatility,
                    "sharpe_ratio": perf.sharpe_ratio,
                    "max_drawdown": perf.max_drawdown,
                    "beta": perf.beta,
                    "alpha": perf.alpha
                }
                for sector, perf in sector_performance.items()
            },
            "rotation_analysis": {
                "strategy": rotation_analysis["strategy"],
                "total_signals": rotation_analysis["total_signals"],
                "last_signals": list(rotation_analysis["rotation_signals"].values())[-3:] if rotation_analysis["rotation_signals"] else []
            },
            "correlation_analysis": {
                "avg_correlation": np.mean([
                    stats["avg_correlation"] for stats in correlation_analysis["correlation_statistics"].values()
                ]),
                "sector_correlations": correlation_analysis["correlation_statistics"]
            },
            "risk_analysis": {
                "portfolio_volatility": risk_analysis["portfolio_risk"]["volatility"],
                "portfolio_var_95": risk_analysis["portfolio_risk"]["var_95"],
                "sector_risk_summary": {
                    sector: {
                        "volatility": metrics["volatility"],
                        "weight": metrics["weight"],
                        "risk_contribution": risk_analysis["risk_contribution"].get(sector, 0)
                    }
                    for sector, metrics in risk_analysis["sector_risk_metrics"].items()
                }
            },
            "summary": {
                "n_sectors": len(sector_classification),
                "best_performing_sector": max(sector_performance.keys(), 
                                           key=lambda x: sector_performance[x].sharpe_ratio),
                "highest_volatility_sector": max(sector_performance.keys(), 
                                               key=lambda x: sector_performance[x].volatility),
                "total_assets": len(asset_names)
            }
        }
        
        print("✅ Sektör Raporu Tamamlandı!")
        return report

# Test fonksiyonu
def test_sector_analysis():
    """Sector Analysis test fonksiyonu"""
    print("🧪 Sector Analysis Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    n_days = 252  # 1 yıl
    n_sectors = 8
    
    # Sektör isimleri
    sector_names = [
        "FINANCIAL", "INDUSTRIAL", "TECHNOLOGY", "ENERGY",
        "MATERIALS", "CONSUMER_DISCRETIONARY", "CONSUMER_STAPLES", "HEALTHCARE"
    ]
    
    # Tarih aralığı
    dates = pd.date_range('2023-01-01', periods=n_days, freq='D')
    
    # Sektör getiri verisi
    sector_returns_data = {}
    for i, sector in enumerate(sector_names):
        # Her sektör için farklı volatilite ve trend
        base_return = 0.0005 + i * 0.0001  # Farklı trend
        volatility = 0.015 + i * 0.002     # Farklı volatilite
        
        returns = np.random.normal(base_return, volatility, n_days)
        sector_returns_data[sector] = returns
    
    sector_returns = pd.DataFrame(sector_returns_data, index=dates)
    
    # Benchmark (piyasa ortalaması)
    benchmark_returns = sector_returns.mean(axis=1)
    
    # Sector Analysis başlat
    sector_analyzer = SectorAnalysis(risk_free_rate=0.03)
    
    # Sektör sınıflandırması test
    print("\n🏷️ Sektör Sınıflandırması Test:")
    asset_names = ["SISE.IS", "EREGL.IS", "AKBNK.IS", "GARAN.IS", "TUPRS.IS"]
    sector_classification = sector_analyzer.classify_assets_by_sector(asset_names)
    print(f"   Sınıflandırılan sektör sayısı: {len(sector_classification)}")
    for sector, assets in sector_classification.items():
        if assets:
            print(f"   {sector}: {len(assets)} varlık")
    
    # Sektör performans analizi test
    print("\n📈 Sektör Performans Analizi Test:")
    sector_performance = sector_analyzer.calculate_sector_performance(sector_returns, benchmark_returns)
    print(f"   Analiz edilen sektör sayısı: {len(sector_performance)}")
    
    # En iyi performans gösteren sektör
    best_sector = max(sector_performance.keys(), 
                     key=lambda x: sector_performance[x].sharpe_ratio)
    print(f"   En iyi Sharpe ratio: {best_sector} ({sector_performance[best_sector].sharpe_ratio:.4f})")
    
    # Sektör rotasyon analizi test
    print("\n🔄 Sektör Rotasyon Analizi Test:")
    rotation_analysis = sector_analyzer.analyze_sector_rotation(sector_returns, strategy="MOMENTUM")
    print(f"   Strateji: {rotation_analysis['strategy']}")
    print(f"   Toplam sinyal: {rotation_analysis['total_signals']}")
    
    # Sektör korelasyon analizi test
    print("\n📊 Sektör Korelasyon Analizi Test:")
    correlation_analysis = sector_analyzer.calculate_sector_correlation(sector_returns)
    print(f"   Ortalama korelasyon: {correlation_analysis['correlation_statistics']['FINANCIAL']['avg_correlation']:.4f}")
    
    # Sektör risk analizi test
    print("\n⚠️ Sektör Risk Analizi Test:")
    risk_analysis = sector_analyzer.analyze_sector_risk(sector_returns)
    print(f"   Portföy volatilitesi: {risk_analysis['portfolio_risk']['volatility']:.4f}")
    print(f"   Portföy VaR %95: {risk_analysis['portfolio_risk']['var_95']:.4f}")
    
    # Kapsamlı rapor test
    print("\n📋 Kapsamlı Sektör Raporu Test:")
    sector_report = sector_analyzer.generate_sector_report(sector_returns, benchmark_returns)
    print(f"   Sektör sayısı: {sector_report['summary']['n_sectors']}")
    print(f"   En iyi performans: {sector_report['summary']['best_performing_sector']}")
    print(f"   En yüksek volatilite: {sector_report['summary']['highest_volatility_sector']}")
    print(f"   Toplam varlık: {sector_report['summary']['total_assets']}")
    
    print("\n✅ Sector Analysis Test Tamamlandı!")
    return sector_analyzer

if __name__ == "__main__":
    test_sector_analysis()
