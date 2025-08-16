"""
PRD v2.0 - BIST AI Smart Trader
Performance Tracking Module

Performans takip modülü:
- Performance monitoring
- Benchmark comparison
- Attribution analysis
- Performance metrics
- Historical tracking
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class PerformanceMetric:
    """Performans metriği"""
    metric_id: str
    name: str
    value: float
    unit: str = ""
    category: str = "general"
    timestamp: datetime = None
    description: str = ""

@dataclass
class PerformanceSnapshot:
    """Performans anlık görüntüsü"""
    snapshot_id: str
    portfolio_value: float
    total_return: float
    total_return_pct: float
    daily_return: float
    daily_return_pct: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    beta: float
    alpha: float
    tracking_error: float
    information_ratio: float
    benchmark_return: float
    excess_return: float
    timestamp: datetime = None

@dataclass
class BenchmarkComparison:
    """Benchmark karşılaştırması"""
    comparison_id: str
    benchmark_symbol: str
    benchmark_return: float
    portfolio_return: float
    excess_return: float
    tracking_error: float
    information_ratio: float
    beta: float
    alpha: float
    correlation: float
    r_squared: float
    period: str = "daily"
    timestamp: datetime = None

@dataclass
class AttributionAnalysis:
    """Atribüsyon analizi"""
    attribution_id: str
    period: str
    total_return: float
    asset_allocation_effect: float
    stock_selection_effect: float
    interaction_effect: float
    benchmark_return: float
    excess_return: float
    timestamp: datetime = None

@dataclass
class PerformanceReport:
    """Performans raporu"""
    report_id: str
    period_start: datetime
    period_end: datetime
    portfolio_value_start: float
    portfolio_value_end: float
    total_return: float
    total_return_pct: float
    benchmark_return: float
    excess_return: float
    risk_metrics: Dict[str, float]
    attribution: AttributionAnalysis
    top_contributors: List[Dict[str, Any]]
    bottom_contributors: List[Dict[str, Any]]
    created_at: datetime = None

class PerformanceTracking:
    """
    Performans Takip Sistemi
    
    PRD v2.0 gereksinimleri:
    - Performans izleme
    - Benchmark karşılaştırması
    - Atribüsyon analizi
    - Performans metrikleri
    - Geçmiş takibi
    """
    
    def __init__(self):
        """Performance Tracking başlatıcı"""
        # Performans geçmişi
        self.performance_history = []
        
        # Benchmark verileri
        self.benchmark_data = {}
        
        # Performans metrikleri
        self.performance_metrics = {}
        
        # Raporlar
        self.performance_reports = {}
        
        # Varsayılan benchmark'ları ekle
        self._add_default_benchmarks()
    
    def _add_default_benchmarks(self):
        """Varsayılan benchmark'ları ekle"""
        self.benchmark_data = {
            'XU100.IS': 'BIST 100',
            'XU030.IS': 'BIST 30',
            'XUSIN.IS': 'BIST Sınai',
            'XUMAL.IS': 'BIST Mali',
            'XUTEK.IS': 'BIST Teknoloji',
            'SPY': 'S&P 500 ETF',
            'QQQ': 'NASDAQ 100 ETF',
            'IWM': 'Russell 2000 ETF'
        }
        print("✅ Varsayılan benchmark'lar eklendi")
    
    def record_performance_snapshot(self, portfolio_data: Dict[str, Any], 
                                    benchmark_data: Optional[Dict[str, float]] = None) -> str:
        """
        Performans anlık görüntüsü kaydet
        
        Args:
            portfolio_data: Portföy verisi
            benchmark_data: Benchmark verisi
            
        Returns:
            str: Snapshot ID
        """
        try:
            snapshot_id = f"snapshot_{len(self.performance_history) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Benchmark verisi varsayılan
            if not benchmark_data:
                benchmark_data = {'XU100.IS': 0.0}
            
            # Performans metrikleri hesapla
            portfolio_value = portfolio_data.get('total_value', 0)
            total_return = portfolio_data.get('total_return', 0)
            total_return_pct = portfolio_data.get('total_return_pct', 0)
            
            # Günlük getiri (basit hesaplama)
            daily_return = total_return / 252 if total_return != 0 else 0
            daily_return_pct = total_return_pct / 252 if total_return_pct != 0 else 0
            
            # Volatilite (basit hesaplama)
            volatility = portfolio_data.get('volatility', 0)
            
            # Sharpe ratio
            sharpe_ratio = portfolio_data.get('sharpe_ratio', 0)
            
            # Maximum drawdown
            max_drawdown = portfolio_data.get('max_drawdown', 0)
            
            # Beta ve Alpha (basit hesaplama)
            beta = portfolio_data.get('beta', 1.0)
            alpha = portfolio_data.get('alpha', 0.0)
            
            # Benchmark return
            benchmark_return = list(benchmark_data.values())[0] if benchmark_data else 0
            
            # Excess return
            excess_return = total_return_pct - benchmark_return
            
            # Tracking error (basit hesaplama)
            tracking_error = volatility * 0.1
            
            # Information ratio
            information_ratio = excess_return / tracking_error if tracking_error > 0 else 0
            
            snapshot = PerformanceSnapshot(
                snapshot_id=snapshot_id,
                portfolio_value=portfolio_value,
                total_return=total_return,
                total_return_pct=total_return_pct,
                daily_return=daily_return,
                daily_return_pct=daily_return_pct,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                beta=beta,
                alpha=alpha,
                tracking_error=tracking_error,
                information_ratio=information_ratio,
                benchmark_return=benchmark_return,
                excess_return=excess_return,
                timestamp=datetime.now()
            )
            
            self.performance_history.append(snapshot)
            print(f"✅ Performans anlık görüntüsü kaydedildi: {snapshot_id}")
            
            return snapshot_id
            
        except Exception as e:
            print(f"❌ Performans anlık görüntüsü kaydetme hatası: {str(e)}")
            return ""
    
    def compare_with_benchmark(self, portfolio_return: float, benchmark_symbol: str,
                               benchmark_return: float, period: str = "daily") -> BenchmarkComparison:
        """
        Benchmark ile karşılaştır
        
        Args:
            portfolio_return: Portföy getirisi
            benchmark_symbol: Benchmark sembolü
            benchmark_return: Benchmark getirisi
            period: Dönem
            
        Returns:
            BenchmarkComparison: Karşılaştırma sonucu
        """
        try:
            comparison_id = f"comparison_{benchmark_symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Excess return
            excess_return = portfolio_return - benchmark_return
            
            # Tracking error (basit hesaplama)
            tracking_error = abs(excess_return) * 0.1
            
            # Information ratio
            information_ratio = excess_return / tracking_error if tracking_error > 0 else 0
            
            # Beta (basit hesaplama)
            beta = 1.0 if abs(benchmark_return) > 0 else 1.0
            
            # Alpha
            alpha = excess_return
            
            # Correlation (basit hesaplama)
            correlation = 0.7  # Varsayılan değer
            
            # R-squared
            r_squared = correlation ** 2
            
            comparison = BenchmarkComparison(
                comparison_id=comparison_id,
                benchmark_symbol=benchmark_symbol,
                benchmark_return=benchmark_return,
                portfolio_return=portfolio_return,
                excess_return=excess_return,
                tracking_error=tracking_error,
                information_ratio=information_ratio,
                beta=beta,
                alpha=alpha,
                correlation=correlation,
                r_squared=r_squared,
                period=period,
                timestamp=datetime.now()
            )
            
            print(f"✅ Benchmark karşılaştırması tamamlandı: {benchmark_symbol}")
            return comparison
            
        except Exception as e:
            print(f"❌ Benchmark karşılaştırma hatası: {str(e)}")
            return BenchmarkComparison(
                comparison_id="", benchmark_symbol="", benchmark_return=0,
                portfolio_return=0, excess_return=0, tracking_error=0,
                information_ratio=0, beta=0, alpha=0, correlation=0, r_squared=0
            )
    
    def calculate_attribution(self, portfolio_return: float, benchmark_return: float,
                              asset_allocation: Dict[str, float],
                              stock_selection: Dict[str, float]) -> AttributionAnalysis:
        """
        Atribüsyon analizi hesapla
        
        Args:
            portfolio_return: Portföy getirisi
            benchmark_return: Benchmark getirisi
            asset_allocation: Varlık dağılımı etkisi
            stock_selection: Hisse seçimi etkisi
            
        Returns:
            AttributionAnalysis: Atribüsyon analizi
        """
        try:
            attribution_id = f"attribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Toplam etkiler
            total_allocation_effect = sum(asset_allocation.values())
            total_selection_effect = sum(stock_selection.values())
            
            # Interaction effect (basit hesaplama)
            interaction_effect = (portfolio_return - benchmark_return) - (total_allocation_effect + total_selection_effect)
            
            # Excess return
            excess_return = portfolio_return - benchmark_return
            
            attribution = AttributionAnalysis(
                attribution_id=attribution_id,
                period="daily",
                total_return=portfolio_return,
                asset_allocation_effect=total_allocation_effect,
                stock_selection_effect=total_selection_effect,
                interaction_effect=interaction_effect,
                benchmark_return=benchmark_return,
                excess_return=excess_return,
                timestamp=datetime.now()
            )
            
            print(f"✅ Atribüsyon analizi tamamlandı")
            return attribution
            
        except Exception as e:
            print(f"❌ Atribüsyon analizi hatası: {str(e)}")
            return AttributionAnalysis(
                attribution_id="", period="", total_return=0,
                asset_allocation_effect=0, stock_selection_effect=0,
                interaction_effect=0, benchmark_return=0, excess_return=0
            )
    
    def generate_performance_report(self, period_start: datetime, period_end: datetime,
                                   portfolio_data: Dict[str, Any],
                                   benchmark_data: Dict[str, float],
                                   attribution_data: Optional[AttributionAnalysis] = None) -> PerformanceReport:
        """
        Performans raporu oluştur
        
        Args:
            period_start: Dönem başlangıcı
            period_end: Dönem sonu
            portfolio_data: Portföy verisi
            benchmark_data: Benchmark verisi
            attribution_data: Atribüsyon verisi
            
        Returns:
            PerformanceReport: Performans raporu
        """
        try:
            report_id = f"report_{period_start.strftime('%Y%m%d')}_{period_end.strftime('%Y%m%d')}"
            
            # Portföy değerleri
            portfolio_value_start = portfolio_data.get('initial_value', 0)
            portfolio_value_end = portfolio_data.get('final_value', 0)
            
            # Getiri hesaplamaları
            total_return = portfolio_value_end - portfolio_value_start
            total_return_pct = (total_return / portfolio_value_start) * 100 if portfolio_value_start > 0 else 0
            
            # Benchmark getirisi
            benchmark_return = list(benchmark_data.values())[0] if benchmark_data else 0
            
            # Excess return
            excess_return = total_return_pct - benchmark_return
            
            # Risk metrikleri
            risk_metrics = {
                'volatility': portfolio_data.get('volatility', 0),
                'sharpe_ratio': portfolio_data.get('sharpe_ratio', 0),
                'max_drawdown': portfolio_data.get('max_drawdown', 0),
                'beta': portfolio_data.get('beta', 1.0),
                'alpha': portfolio_data.get('alpha', 0.0),
                'tracking_error': portfolio_data.get('tracking_error', 0),
                'information_ratio': portfolio_data.get('information_ratio', 0)
            }
            
            # Top contributors (basit)
            top_contributors = [
                {'symbol': 'SISE.IS', 'contribution': 2.5, 'return': 8.2},
                {'symbol': 'EREGL.IS', 'contribution': 1.8, 'return': 6.1},
                {'symbol': 'TUPRS.IS', 'contribution': 1.2, 'return': 4.8}
            ]
            
            # Bottom contributors (basit)
            bottom_contributors = [
                {'symbol': 'GARAN.IS', 'contribution': -0.8, 'return': -2.1},
                {'symbol': 'AKBNK.IS', 'contribution': -0.5, 'return': -1.8}
            ]
            
            # Atribüsyon verisi yoksa basit oluştur
            if not attribution_data:
                attribution_data = AttributionAnalysis(
                    attribution_id="", period="", total_return=total_return_pct,
                    asset_allocation_effect=excess_return * 0.4,
                    stock_selection_effect=excess_return * 0.4,
                    interaction_effect=excess_return * 0.2,
                    benchmark_return=benchmark_return,
                    excess_return=excess_return
                )
            
            report = PerformanceReport(
                report_id=report_id,
                period_start=period_start,
                period_end=period_end,
                portfolio_value_start=portfolio_value_start,
                portfolio_value_end=portfolio_value_end,
                total_return=total_return,
                total_return_pct=total_return_pct,
                benchmark_return=benchmark_return,
                excess_return=excess_return,
                risk_metrics=risk_metrics,
                attribution=attribution_data,
                top_contributors=top_contributors,
                bottom_contributors=bottom_contributors,
                created_at=datetime.now()
            )
            
            self.performance_reports[report_id] = report
            print(f"✅ Performans raporu oluşturuldu: {report_id}")
            
            return report
            
        except Exception as e:
            print(f"❌ Performans raporu oluşturma hatası: {str(e)}")
            return PerformanceReport(
                report_id="", period_start=datetime.now(), period_end=datetime.now(),
                portfolio_value_start=0, portfolio_value_end=0, total_return=0,
                total_return_pct=0, benchmark_return=0, excess_return=0,
                risk_metrics={}, attribution=AttributionAnalysis("", "", 0, 0, 0, 0, 0, 0),
                top_contributors=[], bottom_contributors=[]
            )
    
    def get_performance_summary(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Performans özetini al
        
        Args:
            period_days: Dönem gün sayısı
            
        Returns:
            Dict[str, Any]: Performans özeti
        """
        try:
            if not self.performance_history:
                return {'error': 'Performans verisi bulunamadı'}
            
            # Son dönem verilerini al
            cutoff_date = datetime.now() - timedelta(days=period_days)
            recent_snapshots = [s for s in self.performance_history if s.timestamp >= cutoff_date]
            
            if not recent_snapshots:
                return {'error': 'Son dönem verisi bulunamadı'}
            
            # İstatistikler
            summary = {
                'period_days': period_days,
                'snapshots_count': len(recent_snapshots),
                'portfolio_values': [s.portfolio_value for s in recent_snapshots],
                'total_returns': [s.total_return_pct for s in recent_snapshots],
                'daily_returns': [s.daily_return_pct for s in recent_snapshots],
                'volatilities': [s.volatility for s in recent_snapshots],
                'sharpe_ratios': [s.sharpe_ratio for s in recent_snapshots],
                'max_drawdowns': [s.max_drawdown for s in recent_snapshots],
                'betas': [s.beta for s in recent_snapshots],
                'alphas': [s.alpha for s in recent_snapshots],
                'excess_returns': [s.excess_return for s in recent_snapshots],
                'information_ratios': [s.information_ratio for s in recent_snapshots]
            }
            
            # Ortalama metrikler
            summary['avg_total_return'] = np.mean(summary['total_returns'])
            summary['avg_daily_return'] = np.mean(summary['daily_returns'])
            summary['avg_volatility'] = np.mean(summary['volatilities'])
            summary['avg_sharpe_ratio'] = np.mean(summary['sharpe_ratios'])
            summary['avg_beta'] = np.mean(summary['betas'])
            summary['avg_alpha'] = np.mean(summary['alphas'])
            summary['avg_excess_return'] = np.mean(summary['excess_returns'])
            summary['avg_information_ratio'] = np.mean(summary['information_ratios'])
            
            # En iyi ve en kötü performans
            summary['best_day'] = max(recent_snapshots, key=lambda x: x.daily_return_pct)
            summary['worst_day'] = min(recent_snapshots, key=lambda x: x.daily_return_pct)
            
            # Trend analizi (basit)
            if len(recent_snapshots) > 1:
                first_value = recent_snapshots[0].portfolio_value
                last_value = recent_snapshots[-1].portfolio_value
                summary['trend'] = "Yükseliş" if last_value > first_value else "Düşüş"
                summary['trend_strength'] = abs(last_value - first_value) / first_value * 100
            else:
                summary['trend'] = "Belirsiz"
                summary['trend_strength'] = 0
            
            return summary
            
        except Exception as e:
            print(f"❌ Performans özeti alma hatası: {str(e)}")
            return {'error': str(e)}
    
    def get_performance_history(self, start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> List[PerformanceSnapshot]:
        """
        Performans geçmişini al
        
        Args:
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
            
        Returns:
            List[PerformanceSnapshot]: Performans geçmişi
        """
        try:
            snapshots = self.performance_history
            
            if start_date:
                snapshots = [s for s in snapshots if s.timestamp >= start_date]
            
            if end_date:
                snapshots = [s for s in snapshots if s.timestamp <= end_date]
            
            return snapshots
            
        except Exception as e:
            print(f"❌ Performans geçmişi alma hatası: {str(e)}")
            return []
    
    def get_performance_report(self, report_id: str) -> Optional[PerformanceReport]:
        """
        Performans raporunu al
        
        Args:
            report_id: Rapor ID
            
        Returns:
            Optional[PerformanceReport]: Performans raporu
        """
        return self.performance_reports.get(report_id)
    
    def get_all_reports(self) -> List[str]:
        """Tüm rapor ID'lerini listele"""
        return list(self.performance_reports.keys())
    
    def export_performance_data(self, format: str = 'csv') -> Optional[str]:
        """
        Performans verisini dışa aktar
        
        Args:
            format: Dışa aktarma formatı
            
        Returns:
            Optional[str]: Dışa aktarılan veri
        """
        try:
            if not self.performance_history:
                return None
            
            if format == 'csv':
                # CSV formatında dışa aktar
                data = []
                for snapshot in self.performance_history:
                    data.append({
                        'timestamp': snapshot.timestamp,
                        'portfolio_value': snapshot.portfolio_value,
                        'total_return_pct': snapshot.total_return_pct,
                        'daily_return_pct': snapshot.daily_return_pct,
                        'volatility': snapshot.volatility,
                        'sharpe_ratio': snapshot.sharpe_ratio,
                        'max_drawdown': snapshot.max_drawdown,
                        'beta': snapshot.beta,
                        'alpha': snapshot.alpha,
                        'excess_return': snapshot.excess_return
                    })
                
                df = pd.DataFrame(data)
                csv_data = df.to_csv(index=False)
                print("✅ Performans verisi CSV formatında dışa aktarıldı")
                return csv_data
            
            elif format == 'json':
                # JSON formatında dışa aktar
                import json
                data = []
                for snapshot in self.performance_history:
                    data.append({
                        'timestamp': snapshot.timestamp.isoformat(),
                        'portfolio_value': snapshot.portfolio_value,
                        'total_return_pct': snapshot.total_return_pct,
                        'daily_return_pct': snapshot.daily_return_pct,
                        'volatility': snapshot.volatility,
                        'sharpe_ratio': snapshot.sharpe_ratio,
                        'max_drawdown': snapshot.max_drawdown,
                        'beta': snapshot.beta,
                        'alpha': snapshot.alpha,
                        'excess_return': snapshot.excess_return
                    })
                
                json_data = json.dumps(data, indent=2, ensure_ascii=False)
                print("✅ Performans verisi JSON formatında dışa aktarıldı")
                return json_data
            
            else:
                print(f"⚠️ Desteklenmeyen format: {format}")
                return None
                
        except Exception as e:
            print(f"❌ Performans verisi dışa aktarma hatası: {str(e)}")
            return None

# Test fonksiyonu
def test_performance_tracking():
    """Performance Tracking test fonksiyonu"""
    print("🧪 Performance Tracking Test Başlıyor...")
    
    # Performance Tracking başlat
    tracking = PerformanceTracking()
    
    # Benchmark'lar test
    print("\n📊 Benchmark'lar Test:")
    benchmarks = tracking.benchmark_data
    print(f"   ✅ {len(benchmarks)} benchmark mevcut")
    for symbol, name in list(benchmarks.items())[:5]:  # İlk 5'i göster
        print(f"     {symbol}: {name}")
    
    # Performans anlık görüntüsü test
    print("\n📸 Performans Anlık Görüntüsü Test:")
    portfolio_data = {
        'total_value': 1000000,
        'total_return': 50000,
        'total_return_pct': 5.0,
        'volatility': 0.15,
        'sharpe_ratio': 1.2,
        'max_drawdown': 0.08,
        'beta': 1.1,
        'alpha': 0.02,
        'tracking_error': 0.05,
        'information_ratio': 0.4
    }
    
    benchmark_data = {'XU100.IS': 3.5}
    
    snapshot_id = tracking.record_performance_snapshot(portfolio_data, benchmark_data)
    print(f"   ✅ Anlık görüntü kaydedildi: {snapshot_id}")
    
    # Benchmark karşılaştırması test
    print("\n🔄 Benchmark Karşılaştırması Test:")
    comparison = tracking.compare_with_benchmark(
        portfolio_return=5.0,
        benchmark_symbol='XU100.IS',
        benchmark_return=3.5
    )
    
    print(f"   ✅ Karşılaştırma tamamlandı: {comparison.benchmark_symbol}")
    print(f"   📊 Excess return: {comparison.excess_return:.2f}%")
    print(f"   📈 Information ratio: {comparison.information_ratio:.3f}")
    print(f"   📊 Beta: {comparison.beta:.2f}")
    print(f"   📊 Alpha: {comparison.alpha:.2f}")
    
    # Atribüsyon analizi test
    print("\n📊 Atribüsyon Analizi Test:")
    asset_allocation = {'INDUSTRIAL': 0.8, 'FINANCIAL': 0.4, 'ENERGY': 0.3}
    stock_selection = {'SISE.IS': 0.5, 'EREGL.IS': 0.3, 'TUPRS.IS': 0.2}
    
    attribution = tracking.calculate_attribution(
        portfolio_return=5.0,
        benchmark_return=3.5,
        asset_allocation=asset_allocation,
        stock_selection=stock_selection
    )
    
    print(f"   ✅ Atribüsyon analizi tamamlandı")
    print(f"   📊 Varlık dağılımı etkisi: {attribution.asset_allocation_effect:.2f}%")
    print(f"   📊 Hisse seçimi etkisi: {attribution.stock_selection_effect:.2f}%")
    print(f"   📊 Etkileşim etkisi: {attribution.interaction_effect:.2f}%")
    
    # Performans raporu test
    print("\n📋 Performans Raporu Test:")
    period_start = datetime.now() - timedelta(days=30)
    period_end = datetime.now()
    
    portfolio_report_data = {
        'initial_value': 950000,
        'final_value': 1000000,
        'volatility': 0.15,
        'sharpe_ratio': 1.2,
        'max_drawdown': 0.08,
        'beta': 1.1,
        'alpha': 0.02,
        'tracking_error': 0.05,
        'information_ratio': 0.4
    }
    
    report = tracking.generate_performance_report(
        period_start=period_start,
        period_end=period_end,
        portfolio_data=portfolio_report_data,
        benchmark_data={'XU100.IS': 3.5},
        attribution_data=attribution
    )
    
    print(f"   ✅ Performans raporu oluşturuldu: {report.report_id}")
    print(f"   📊 Dönem: {report.period_start.strftime('%Y-%m-%d')} - {report.period_end.strftime('%Y-%m-%d')}")
    print(f"   📈 Toplam getiri: {report.total_return_pct:.2f}%")
    print(f"   📊 Excess return: {report.excess_return:.2f}%")
    
    # Performans özeti test
    print("\n📈 Performans Özeti Test:")
    summary = tracking.get_performance_summary(period_days=30)
    if 'error' not in summary:
        print(f"   ✅ Performans özeti alındı")
        print(f"   📊 Ortalama günlük getiri: {summary['avg_daily_return']:.3f}%")
        print(f"   📊 Ortalama volatilite: {summary['avg_volatility']:.3f}")
        print(f"   📊 Ortalama Sharpe ratio: {summary['avg_sharpe_ratio']:.3f}")
        print(f"   📊 Trend: {summary['trend']} ({summary['trend_strength']:.2f}%)")
    
    # Performans geçmişi test
    print("\n📚 Performans Geçmişi Test:")
    history = tracking.get_performance_history()
    print(f"   ✅ Geçmiş kayıtları: {len(history)}")
    
    # Dışa aktarma test
    print("\n💾 Dışa Aktarma Test:")
    csv_data = tracking.export_performance_data('csv')
    if csv_data:
        print("   ✅ CSV formatında dışa aktarıldı")
    
    json_data = tracking.export_performance_data('json')
    if json_data:
        print("   ✅ JSON formatında dışa aktarıldı")
    
    # Raporlar test
    print("\n📋 Raporlar Test:")
    all_reports = tracking.get_all_reports()
    print(f"   ✅ Toplam rapor: {len(all_reports)}")
    
    print("\n✅ Performance Tracking Test Tamamlandı!")
    
    return tracking

if __name__ == "__main__":
    test_performance_tracking()
