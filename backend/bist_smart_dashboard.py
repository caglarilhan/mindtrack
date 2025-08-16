import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

from bist_smart_indicator import BISTSmartIndicator
from visual_analyzer import VisualAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BISTSmartDashboard:
    """
    BIST Smart Indicator + Görsel Analiz Dashboard
    - Tek sayfada tüm analizler
    - Portföy önerileri + grafikler
    - Performans takibi
    """
    
    def __init__(self):
        self.indicator = BISTSmartIndicator()
        self.visual_analyzer = VisualAnalyzer()
        self.dashboard_data = {}
        
        # Grafik ayarları
        plt.style.use('seaborn-v0_8')
        plt.rcParams['figure.figsize'] = (16, 10)
        plt.rcParams['font.size'] = 10
        
    def create_comprehensive_dashboard(self, save_dir: str = "bist_dashboard") -> Dict:
        """
        Kapsamlı dashboard oluşturur
        """
        try:
            logger.info("🎨 BIST Smart Dashboard oluşturuluyor...")
            
            # Klasör oluştur
            import os
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # 1. Tüm hisseleri analiz et
            analysis_results = self.indicator.analyze_all_stocks(period="6mo")
            
            if "error" in analysis_results:
                return {"error": analysis_results["error"]}
            
            # 2. Dashboard verilerini hazırla
            self.dashboard_data = analysis_results
            
            # 3. Ana dashboard grafiği
            main_dashboard_path = f"{save_dir}/bist_main_dashboard.png"
            self._create_main_dashboard(main_dashboard_path)
            
            # 4. Top picks detay grafikleri
            top_picks_charts = self._create_top_picks_charts(save_dir)
            
            # 5. Portföy dağılım grafiği
            portfolio_chart_path = f"{save_dir}/portfolio_allocation.png"
            self._create_portfolio_chart(portfolio_chart_path)
            
            # 6. Performans trend grafiği
            performance_chart_path = f"{save_dir}/performance_trends.png"
            self._create_performance_trends(performance_chart_path)
            
            return {
                "dashboard_created": True,
                "main_dashboard": main_dashboard_path,
                "top_picks_charts": top_picks_charts,
                "portfolio_chart": portfolio_chart_path,
                "performance_chart": performance_chart_path,
                "save_directory": save_dir,
                "analysis_date": datetime.now().isoformat(),
                "total_stocks": analysis_results["total_stocks"],
                "top_picks_count": len(analysis_results["top_picks"])
            }
            
        except Exception as e:
            logger.error(f"Dashboard oluşturma hatası: {e}")
            return {"error": str(e)}
    
    def _create_main_dashboard(self, save_path: str):
        """
        Ana dashboard grafiği oluşturur
        """
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
            
            # 1. Skor dağılımı (Sol üst)
            self._plot_score_distribution(ax1)
            
            # 2. Risk seviyesi dağılımı (Sağ üst)
            self._plot_risk_distribution(ax2)
            
            # 3. Sinyal dağılımı (Sol alt)
            self._plot_signal_distribution(ax3)
            
            # 4. Top picks skorları (Sağ alt)
            self._plot_top_picks_scores(ax4)
            
            # Başlık
            fig.suptitle('🚀 BIST SMART INDICATOR - ANA DASHBOARD', 
                        fontsize=20, fontweight='bold', y=0.98)
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Ana dashboard kaydedildi: {save_path}")
            
        except Exception as e:
            logger.error(f"Ana dashboard oluşturma hatası: {e}")
    
    def _plot_score_distribution(self, ax):
        """Skor dağılımı grafiği"""
        try:
            scores = [stock['scores']['composite'] for stock in self.dashboard_data['all_results']]
            symbols = [stock['symbol'] for stock in self.dashboard_data['all_results']]
            
            # Renk kodlaması
            colors = []
            for score in scores:
                if score >= 80:
                    colors.append('darkgreen')
                elif score >= 60:
                    colors.append('green')
                elif score >= 40:
                    colors.append('orange')
                else:
                    colors.append('red')
            
            bars = ax.barh(symbols, scores, color=colors, alpha=0.7)
            ax.set_xlabel('Kompozit Skor')
            ax.set_title('📊 Hisse Skor Dağılımı')
            ax.grid(True, alpha=0.3)
            
            # Skor değerlerini ekle
            for i, (bar, score) in enumerate(zip(bars, scores)):
                ax.text(score + 1, bar.get_y() + bar.get_height()/2, 
                       f'{score:.1f}', va='center', fontweight='bold')
            
        except Exception as e:
            logger.error(f"Skor dağılım grafiği hatası: {e}")
    
    def _plot_risk_distribution(self, ax):
        """Risk seviyesi dağılımı grafiği"""
        try:
            risk_counts = {}
            for stock in self.dashboard_data['all_results']:
                risk = stock['risk_level']
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            
            # Renk kodlaması
            risk_colors = {
                'LOW': 'darkgreen',
                'MEDIUM-LOW': 'green',
                'MEDIUM': 'orange',
                'MEDIUM-HIGH': 'red',
                'HIGH': 'darkred'
            }
            
            risks = list(risk_counts.keys())
            counts = list(risk_counts.values())
            colors = [risk_colors.get(risk, 'gray') for risk in risks]
            
            wedges, texts, autotexts = ax.pie(counts, labels=risks, colors=colors, 
                                             autopct='%1.1f%%', startangle=90)
            ax.set_title('⚖️ Risk Seviyesi Dağılımı')
            
        except Exception as e:
            logger.error(f"Risk dağılım grafiği hatası: {e}")
    
    def _plot_signal_distribution(self, ax):
        """Sinyal dağılımı grafiği"""
        try:
            signal_counts = {}
            for stock in self.dashboard_data['all_results']:
                signal = stock['recommendation']
                signal_counts[signal] = signal_counts.get(signal, 0) + 1
            
            # Renk kodlaması
            signal_colors = {
                'STRONG BUY': 'darkgreen',
                'BUY': 'green',
                'HOLD': 'orange',
                'SELL': 'red',
                'STRONG SELL': 'darkred'
            }
            
            signals = list(signal_counts.keys())
            counts = list(signal_counts.values())
            colors = [signal_colors.get(signal, 'gray') for signal in signals]
            
            bars = ax.bar(signals, counts, color=colors, alpha=0.7)
            ax.set_ylabel('Hisse Sayısı')
            ax.set_title('🎯 Sinyal Dağılımı')
            ax.grid(True, alpha=0.3)
            
            # Değerleri ekle
            for bar, count in zip(bars, counts):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                       str(count), ha='center', va='bottom', fontweight='bold')
            
        except Exception as e:
            logger.error(f"Sinyal dağılım grafiği hatası: {e}")
    
    def _plot_top_picks_scores(self, ax):
        """Top picks skorları grafiği"""
        try:
            top_picks = self.dashboard_data['top_picks'][:5]
            
            symbols = [stock['symbol'] for stock in top_picks]
            composite_scores = [stock['scores']['composite'] for stock in top_picks]
            fundamental_scores = [stock['scores']['fundamental'] for stock in top_picks]
            technical_scores = [stock['scores']['technical'] for stock in top_picks]
            momentum_scores = [stock['scores']['momentum'] for stock in top_picks]
            
            x = np.arange(len(symbols))
            width = 0.2
            
            ax.bar(x - width*1.5, fundamental_scores, width, label='Fundamental', 
                   color='darkblue', alpha=0.7)
            ax.bar(x - width*0.5, technical_scores, width, label='Technical', 
                   color='green', alpha=0.7)
            ax.bar(x + width*0.5, momentum_scores, width, label='Momentum', 
                   color='orange', alpha=0.7)
            ax.bar(x + width*1.5, composite_scores, width, label='Composite', 
                   color='red', alpha=0.7)
            
            ax.set_xlabel('Hisse')
            ax.set_ylabel('Skor')
            ax.set_title('🏆 Top 5 Hisse - Detaylı Skor Analizi')
            ax.set_xticks(x)
            ax.set_xticklabels(symbols, rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            logger.error(f"Top picks skor grafiği hatası: {e}")
    
    def _create_top_picks_charts(self, save_dir: str) -> List[str]:
        """
        Top picks için detay grafikleri oluşturur
        """
        try:
            chart_paths = []
            top_picks = self.dashboard_data['top_picks'][:5]
            
            for stock in top_picks:
                symbol = stock['symbol']
                logger.info(f"🎨 {symbol} için detay grafikleri oluşturuluyor...")
                
                try:
                    # Veri çek
                    data = self.visual_analyzer.get_stock_data(symbol, period="6mo")
                    
                    if not data.empty:
                        # Candlestick grafiği
                        candlestick_path = f"{save_dir}/{symbol}_candlestick.png"
                        self.visual_analyzer.create_candlestick_chart(
                            data, symbol, save_path=candlestick_path
                        )
                        
                        # Support/Resistance grafiği
                        sr_path = f"{save_dir}/{symbol}_support_resistance.png"
                        self.visual_analyzer.create_support_resistance_chart(
                            data, symbol, save_path=sr_path
                        )
                        
                        chart_paths.extend([candlestick_path, sr_path])
                        
                except Exception as e:
                    logger.warning(f"{symbol} grafik oluşturma hatası: {e}")
                    continue
            
            return chart_paths
            
        except Exception as e:
            logger.error(f"Top picks grafikleri oluşturma hatası: {e}")
            return []
    
    def _create_portfolio_chart(self, save_path: str):
        """
        Portföy dağılım grafiği oluşturur
        """
        try:
            portfolio = self.indicator.get_portfolio_recommendations()
            
            if "error" in portfolio:
                logger.warning("Portföy verisi bulunamadı")
                return
            
            symbols = list(portfolio['portfolio'].keys())
            weights = [alloc['weight'] for alloc in portfolio['portfolio'].values()]
            risk_levels = [alloc['risk_level'] for alloc in portfolio['portfolio'].values()]
            
            # Risk bazlı renk kodlaması
            risk_colors = {
                'LOW': 'darkgreen',
                'MEDIUM-LOW': 'green',
                'MEDIUM': 'orange',
                'MEDIUM-HIGH': 'red',
                'HIGH': 'darkred'
            }
            
            colors = [risk_colors.get(risk, 'gray') for risk in risk_levels]
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
            
            # 1. Pasta grafik
            wedges, texts, autotexts = ax1.pie(weights, labels=symbols, colors=colors,
                                               autopct='%1.1f%%', startangle=90)
            ax1.set_title('💼 Portföy Dağılımı (%)', fontsize=14, fontweight='bold')
            
            # 2. Bar grafik
            bars = ax2.bar(symbols, weights, color=colors, alpha=0.7)
            ax2.set_ylabel('Ağırlık (%)')
            ax2.set_title('📊 Portföy Ağırlıkları', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            
            # Değerleri ekle
            for bar, weight in zip(bars, weights):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        f'{weight:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Portföy grafiği kaydedildi: {save_path}")
            
        except Exception as e:
            logger.error(f"Portföy grafiği oluşturma hatası: {e}")
    
    def _create_performance_trends(self, save_path: str):
        """
        Performans trend grafiği oluşturur
        """
        try:
            # Son 20 günlük performans analizi
            performance_data = {}
            
            for stock in self.dashboard_data['top_picks'][:5]:
                symbol = stock['symbol']
                data = self.visual_analyzer.get_stock_data(symbol, period="1mo")
                
                if not data.empty and len(data) >= 20:
                    # Normalize edilmiş fiyat (ilk gün = 100)
                    normalized_price = (data['Close'] / data['Close'].iloc[0]) * 100
                    performance_data[symbol] = normalized_price
            
            if not performance_data:
                logger.warning("Performans verisi bulunamadı")
                return
            
            # Grafik oluştur
            fig, ax = plt.subplots(figsize=(16, 10))
            
            for symbol, prices in performance_data.items():
                ax.plot(prices.index, prices.values, label=symbol, linewidth=2, marker='o', markersize=4)
            
            ax.set_xlabel('Tarih')
            ax.set_ylabel('Normalize Edilmiş Fiyat (İlk Gün = 100)')
            ax.set_title('📈 Top 5 Hisse - 20 Günlük Performans Karşılaştırması', 
                        fontsize=14, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # X ekseni tarih formatı
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ Performans trend grafiği kaydedildi: {save_path}")
            
        except Exception as e:
            logger.error(f"Performans trend grafiği oluşturma hatası: {e}")
    
    def generate_dashboard_report(self) -> str:
        """
        Dashboard raporu oluşturur
        """
        try:
            if not self.dashboard_data:
                return "❌ Henüz dashboard oluşturulmamış!"
            
            report = []
            report.append("🚀 BIST SMART INDICATOR - DASHBOARD RAPORU")
            report.append("=" * 80)
            report.append(f"📅 Analiz Tarihi: {self.dashboard_data['analysis_date']}")
            report.append(f"📊 Toplam Hisse: {self.dashboard_data['total_stocks']}")
            report.append(f"✅ Başarılı Analiz: {self.dashboard_data['successful_analyses']}")
            
            # Performans istatistikleri
            if 'performance_stats' in self.dashboard_data:
                stats = self.dashboard_data['performance_stats']
                report.append(f"\n📈 PERFORMANS İSTATİSTİKLERİ:")
                report.append(f"   Ortalama Skor: {stats.get('average_score', 0):.1f}")
                report.append(f"   Medyan Skor: {stats.get('median_score', 0):.1f}")
                report.append(f"   Min Skor: {stats.get('min_score', 0):.1f}")
                report.append(f"   Max Skor: {stats.get('max_score', 0):.1f}")
            
            # Top picks
            report.append(f"\n🏆 TOP {len(self.dashboard_data['top_picks'])} HİSSE:")
            report.append("-" * 80)
            for i, stock in enumerate(self.dashboard_data['top_picks'], 1):
                report.append(f"{i:2d}. {stock['symbol']:<10} | {stock['grade']:>3} | "
                            f"{stock['recommendation']:<12} | Skor: {stock['scores']['composite']:>6.1f} | "
                            f"Risk: {stock['risk_level']:<12}")
            
            # Portföy önerileri
            portfolio = self.indicator.get_portfolio_recommendations()
            if "error" not in portfolio:
                report.append(f"\n💼 PORTFÖY ÖNERİLERİ:")
                report.append("-" * 80)
                for symbol, alloc in portfolio['portfolio'].items():
                    report.append(f"   {symbol:<10} | %{alloc['weight']:>5.1f} | "
                                f"{alloc['recommendation']:<12} | Risk: {alloc['risk_level']:<12}")
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"Dashboard rapor oluşturma hatası: {e}")
            return f"❌ Rapor oluşturma hatası: {e}"

# Test fonksiyonu
if __name__ == "__main__":
    print("🎨 BIST SMART DASHBOARD - TEST BAŞLATILIYOR...")
    print("=" * 60)
    
    # Dashboard'u başlat
    dashboard = BISTSmartDashboard()
    
    # Kapsamlı dashboard oluştur
    print("📊 Kapsamlı dashboard oluşturuluyor...")
    result = dashboard.create_comprehensive_dashboard()
    
    if "error" not in result:
        print("✅ Dashboard başarıyla oluşturuldu!")
        print(f"📁 Kayıt Klasörü: {result['save_directory']}")
        print(f"📊 Toplam Hisse: {result['total_stocks']}")
        print(f"🏆 Top Picks: {result['top_picks_count']}")
        
        # Rapor yazdır
        print("\n" + "="*80)
        report = dashboard.generate_dashboard_report()
        print(report)
        
        print(f"\n🎨 GRAFİKLER:")
        print(f"   📊 Ana Dashboard: {result['main_dashboard']}")
        print(f"   💼 Portföy Dağılımı: {result['portfolio_chart']}")
        print(f"   📈 Performans Trendleri: {result['performance_chart']}")
        print(f"   🎯 Top Picks Grafikleri: {len(result['top_picks_charts'])} adet")
        
    else:
        print(f"❌ Dashboard hatası: {result['error']}")
    
    print("\n✅ Test tamamlandı!")
