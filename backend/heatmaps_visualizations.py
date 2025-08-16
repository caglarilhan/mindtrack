"""
PRD v2.0 - BIST AI Smart Trader
Heatmaps & Visualizations Module

Görsel analiz araçları:
- Correlation heatmaps
- Performance heatmaps
- Risk heatmaps
- Interactive charts
- Custom visualizations
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class ChartConfig:
    """Grafik konfigürasyonu"""
    figsize: Tuple[int, int] = (12, 8)
    dpi: int = 100
    style: str = "default"
    color_palette: str = "viridis"
    save_format: str = "png"
    annotations: bool = True

@dataclass
class HeatmapData:
    """Isı haritası verisi"""
    data: pd.DataFrame
    title: str
    x_label: str
    y_label: str
    color_map: str
    annotations: bool = True

class HeatmapsVisualizations:
    """
    Isı Haritaları ve Görselleştirme Motoru
    
    PRD v2.0 gereksinimleri:
    - Korelasyon ısı haritaları
    - Performans ısı haritaları
    - Risk ısı haritaları
    - Etkileşimli grafikler
    - Özel görselleştirmeler
    """
    
    def __init__(self, chart_config: Optional[ChartConfig] = None):
        """
        Heatmaps & Visualizations başlatıcı
        
        Args:
            chart_config: Grafik konfigürasyonu
        """
        self.chart_config = chart_config or ChartConfig()
        
        # Matplotlib stil ayarları
        plt.style.use(self.chart_config.style)
        
        # Renk paletleri
        self.COLOR_PALETTES = {
            "correlation": "RdBu_r",
            "performance": "RdYlGn",
            "risk": "Reds",
            "volatility": "Blues",
            "default": "viridis"
        }
        
        # Grafik türleri
        self.CHART_TYPES = ["heatmap", "line", "bar", "scatter", "area", "candlestick"]
    
    def create_correlation_heatmap(self, correlation_matrix: pd.DataFrame,
                                  title: str = "Varlık Korelasyon Matrisi",
                                  save_path: Optional[str] = None,
                                  show_plot: bool = True) -> plt.Figure:
        """
        Korelasyon ısı haritası oluşturma
        
        Args:
            correlation_matrix: Korelasyon matrisi
            title: Grafik başlığı
            save_path: Kaydetme yolu
            show_plot: Grafiği gösterme
            
        Returns:
            plt.Figure: Oluşturulan grafik
        """
        fig, ax = plt.subplots(figsize=self.chart_config.figsize, dpi=self.chart_config.dpi)
        
        # Isı haritası oluştur
        im = ax.imshow(correlation_matrix.values, 
                      cmap=self.COLOR_PALETTES["correlation"],
                      aspect='auto',
                      vmin=-1, vmax=1)
        
        # Renk çubuğu ekle
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Korelasyon Katsayısı', rotation=270, labelpad=20)
        
        # Axis etiketleri
        ax.set_xticks(range(len(correlation_matrix.columns)))
        ax.set_yticks(range(len(correlation_matrix.index)))
        ax.set_xticklabels(correlation_matrix.columns, rotation=45, ha='right')
        ax.set_yticklabels(correlation_matrix.index)
        
        # Korelasyon değerlerini ekle
        if self.chart_config.annotations:
            for i in range(len(correlation_matrix.index)):
                for j in range(len(correlation_matrix.columns)):
                    value = correlation_matrix.iloc[i, j]
                    color = "white" if abs(value) > 0.5 else "black"
                    ax.text(j, i, f'{value:.2f}',
                           ha='center', va='center', 
                           color=color, fontsize=8, fontweight='bold')
        
        # Grafik başlığı ve etiketler
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Varlıklar', fontsize=12)
        ax.set_ylabel('Varlıklar', fontsize=12)
        
        # Grid çizgileri
        ax.grid(False)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.chart_config.dpi, 
                       bbox_inches='tight', format=self.chart_config.save_format)
            print(f"📊 Korelasyon ısı haritası kaydedildi: {save_path}")
        
        if show_plot:
            plt.show()
        
        return fig
    
    def create_performance_heatmap(self, performance_data: pd.DataFrame,
                                  title: str = "Performans Isı Haritası",
                                  save_path: Optional[str] = None,
                                  show_plot: bool = True) -> plt.Figure:
        """
        Performans ısı haritası oluşturma
        
        Args:
            performance_data: Performans verisi (varlık x zaman)
            title: Grafik başlığı
            save_path: Kaydetme yolu
            show_plot: Grafiği gösterme
            
        Returns:
            plt.Figure: Oluşturulan grafik
        """
        fig, ax = plt.subplots(figsize=self.chart_config.figsize, dpi=self.chart_config.dpi)
        
        # Performans verisini normalize et (-1 ile 1 arası)
        normalized_data = performance_data.copy()
        for col in normalized_data.columns:
            col_data = normalized_data[col]
            if col_data.std() > 0:
                normalized_data[col] = (col_data - col_data.mean()) / col_data.std()
        
        # Isı haritası oluştur
        im = ax.imshow(normalized_data.values.T, 
                      cmap=self.COLOR_PALETTES["performance"],
                      aspect='auto',
                      vmin=-2, vmax=2)
        
        # Renk çubuğu ekle
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Normalize Edilmiş Performans', rotation=270, labelpad=20)
        
        # Axis etiketleri
        ax.set_xticks(range(len(performance_data.index)))
        ax.set_yticks(range(len(performance_data.columns)))
        
        # Tarih etiketleri (x-axis)
        if len(performance_data.index) > 20:
            # Çok fazla tarih varsa her 5'te birini göster
            step = max(1, len(performance_data.index) // 20)
            x_labels = [performance_data.index[i].strftime('%m-%d') 
                       for i in range(0, len(performance_data.index), step)]
            x_positions = range(0, len(performance_data.index), step)
            ax.set_xticks(x_positions)
            ax.set_xticklabels(x_labels, rotation=45, ha='right')
        else:
            x_labels = [idx.strftime('%m-%d') for idx in performance_data.index]
            ax.set_xticklabels(x_labels, rotation=45, ha='right')
        
        ax.set_yticklabels(performance_data.columns)
        
        # Grafik başlığı ve etiketler
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Tarih', fontsize=12)
        ax.set_ylabel('Varlıklar', fontsize=12)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.chart_config.dpi, 
                       bbox_inches='tight', format=self.chart_config.save_format)
            print(f"📊 Performans ısı haritası kaydedildi: {save_path}")
        
        if show_plot:
            plt.show()
        
        return fig
    
    def create_risk_heatmap(self, risk_data: pd.DataFrame,
                            title: str = "Risk Isı Haritası",
                            save_path: Optional[str] = None,
                            show_plot: bool = True) -> plt.Figure:
        """
        Risk ısı haritası oluşturma
        
        Args:
            risk_data: Risk verisi (varlık x risk_metrik)
            title: Grafik başlığı
            save_path: Kaydetme yolu
            show_plot: Grafiği gösterme
            
        Returns:
            plt.Figure: Oluşturulan grafik
        """
        fig, ax = plt.subplots(figsize=self.chart_config.figsize, dpi=self.chart_config.dpi)
        
        # Risk verisini normalize et (0 ile 1 arası)
        normalized_data = risk_data.copy()
        for col in normalized_data.columns:
            col_data = normalized_data[col]
            if col_data.max() > col_data.min():
                normalized_data[col] = (col_data - col_data.min()) / (col_data.max() - col_data.min())
        
        # Isı haritası oluştur
        im = ax.imshow(normalized_data.values, 
                      cmap=self.COLOR_PALETTES["risk"],
                      aspect='auto',
                      vmin=0, vmax=1)
        
        # Renk çubuğu ekle
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Normalize Edilmiş Risk', rotation=270, labelpad=20)
        
        # Axis etiketleri
        ax.set_xticks(range(len(risk_data.columns)))
        ax.set_yticks(range(len(risk_data.index)))
        ax.set_xticklabels(risk_data.columns, rotation=45, ha='right')
        ax.set_yticklabels(risk_data.index)
        
        # Risk değerlerini ekle
        if self.chart_config.annotations:
            for i in range(len(risk_data.index)):
                for j in range(len(risk_data.columns)):
                    value = risk_data.iloc[i, j]
                    color = "white" if normalized_data.iloc[i, j] > 0.5 else "black"
                    ax.text(j, i, f'{value:.3f}',
                           ha='center', va='center', 
                           color=color, fontsize=8, fontweight='bold')
        
        # Grafik başlığı ve etiketler
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Risk Metrikleri', fontsize=12)
        ax.set_ylabel('Varlıklar', fontsize=12)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.chart_config.dpi, 
                       bbox_inches='tight', format=self.chart_config.save_format)
            print(f"📊 Risk ısı haritası kaydedildi: {save_path}")
        
        if show_plot:
            plt.show()
        
        return fig
    
    def create_volatility_heatmap(self, volatility_data: pd.DataFrame,
                                 title: str = "Volatilite Isı Haritası",
                                 save_path: Optional[str] = None,
                                 show_plot: bool = True) -> plt.Figure:
        """
        Volatilite ısı haritası oluşturma
        
        Args:
            volatility_data: Volatilite verisi (varlık x zaman)
            title: Grafik başlığı
            save_path: Kaydetme yolu
            show_plot: Grafiği gösterme
            
        Returns:
            plt.Figure: Oluşturulan grafik
        """
        fig, ax = plt.subplots(figsize=self.chart_config.figsize, dpi=self.chart_config.dpi)
        
        # Volatilite verisini normalize et
        normalized_data = volatility_data.copy()
        for col in normalized_data.columns:
            col_data = normalized_data[col]
            if col_data.max() > col_data.min():
                normalized_data[col] = (col_data - col_data.min()) / (col_data.max() - col_data.min())
        
        # Isı haritası oluştur
        im = ax.imshow(normalized_data.values.T, 
                      cmap=self.COLOR_PALETTES["volatility"],
                      aspect='auto',
                      vmin=0, vmax=1)
        
        # Renk çubuğu ekle
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Normalize Edilmiş Volatilite', rotation=270, labelpad=20)
        
        # Axis etiketleri
        ax.set_xticks(range(len(volatility_data.index)))
        ax.set_yticks(range(len(volatility_data.columns)))
        
        # Tarih etiketleri (x-axis)
        if len(volatility_data.index) > 20:
            step = max(1, len(volatility_data.index) // 20)
            x_labels = [volatility_data.index[i].strftime('%m-%d') 
                       for i in range(0, len(volatility_data.index), step)]
            x_positions = range(0, len(volatility_data.index), step)
            ax.set_xticks(x_positions)
            ax.set_xticklabels(x_labels, rotation=45, ha='right')
        else:
            x_labels = [idx.strftime('%m-%d') for idx in volatility_data.index]
            ax.set_xticklabels(x_labels, rotation=45, ha='right')
        
        ax.set_yticklabels(volatility_data.columns)
        
        # Grafik başlığı ve etiketler
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Tarih', fontsize=12)
        ax.set_ylabel('Varlıklar', fontsize=12)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.chart_config.dpi, 
                       bbox_inches='tight', format=self.chart_config.save_format)
            print(f"📊 Volatilite ısı haritası kaydedildi: {save_path}")
        
        if show_plot:
            plt.show()
        
        return fig
    
    def create_performance_chart(self, performance_data: pd.Series,
                                title: str = "Performans Grafiği",
                                chart_type: str = "line",
                                save_path: Optional[str] = None,
                                show_plot: bool = True) -> plt.Figure:
        """
        Performans grafiği oluşturma
        
        Args:
            performance_data: Performans verisi
            title: Grafik başlığı
            chart_type: Grafik türü (line, bar, area)
            save_path: Kaydetme yolu
            show_plot: Grafiği gösterme
            
        Returns:
            plt.Figure: Oluşturulan grafik
        """
        fig, ax = plt.subplots(figsize=self.chart_config.figsize, dpi=self.chart_config.dpi)
        
        if chart_type == "line":
            ax.plot(performance_data.index, performance_data.values, 
                   linewidth=2, color='blue', alpha=0.8)
            ax.fill_between(performance_data.index, performance_data.values, 
                           alpha=0.3, color='blue')
            
        elif chart_type == "bar":
            ax.bar(performance_data.index, performance_data.values, 
                  alpha=0.7, color='green')
            
        elif chart_type == "area":
            ax.fill_between(performance_data.index, performance_data.values, 
                           alpha=0.6, color='orange')
            ax.plot(performance_data.index, performance_data.values, 
                   linewidth=1, color='darkorange')
        
        # X-axis tarih formatı
        if len(performance_data.index) > 20:
            step = max(1, len(performance_data.index) // 20)
            x_labels = [performance_data.index[i].strftime('%m-%d') 
                       for i in range(0, len(performance_data.index), step)]
            x_positions = range(0, len(performance_data.index), step)
            ax.set_xticks(x_positions)
            ax.set_xticklabels(x_labels, rotation=45, ha='right')
        
        # Grafik başlığı ve etiketler
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Tarih', fontsize=12)
        ax.set_ylabel('Performans', fontsize=12)
        
        # Grid
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.chart_config.dpi, 
                       bbox_inches='tight', format=self.chart_config.save_format)
            print(f"📊 Performans grafiği kaydedildi: {save_path}")
        
        if show_plot:
            plt.show()
        
        return fig
    
    def create_risk_metrics_chart(self, risk_metrics: Dict[str, float],
                                 title: str = "Risk Metrikleri",
                                 chart_type: str = "bar",
                                 save_path: Optional[str] = None,
                                 show_plot: bool = True) -> plt.Figure:
        """
        Risk metrikleri grafiği oluşturma
        
        Args:
            risk_metrics: Risk metrikleri sözlüğü
            title: Grafik başlığı
            chart_type: Grafik türü (bar, radar)
            save_path: Kaydetme yolu
            show_plot: Grafiği gösterme
            
        Returns:
            plt.Figure: Oluşturulan grafik
        """
        fig, ax = plt.subplots(figsize=self.chart_config.figsize, dpi=self.chart_config.dpi)
        
        metrics_names = list(risk_metrics.keys())
        metrics_values = list(risk_metrics.values())
        
        if chart_type == "bar":
            bars = ax.bar(metrics_names, metrics_values, 
                         alpha=0.7, color='red')
            
            # Değerleri çubukların üzerine yaz
            for bar, value in zip(bars, metrics_values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                       f'{value:.4f}', ha='center', va='bottom', fontsize=10)
        
        elif chart_type == "radar":
            # Radar chart için açıları hesapla
            angles = np.linspace(0, 2 * np.pi, len(metrics_names), endpoint=False).tolist()
            angles += angles[:1]  # İlk noktayı sona ekle
            
            # Değerleri normalize et (0-1 arası)
            max_val = max(metrics_values)
            normalized_values = [v / max_val for v in metrics_values]
            normalized_values += normalized_values[:1]  # İlk noktayı sona ekle
            
            # Radar chart çiz
            ax.plot(angles, normalized_values, 'o-', linewidth=2, color='red')
            ax.fill(angles, normalized_values, alpha=0.25, color='red')
            
            # Axis etiketleri
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metrics_names)
            ax.set_ylim(0, 1)
        
        # Grafik başlığı ve etiketler
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        if chart_type == "bar":
            ax.set_xlabel('Risk Metrikleri', fontsize=12)
            ax.set_ylabel('Değer', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
        
        # Grid
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.chart_config.dpi, 
                       bbox_inches='tight', format=self.chart_config.save_format)
            print(f"📊 Risk metrikleri grafiği kaydedildi: {save_path}")
        
        if show_plot:
            plt.show()
        
        return fig
    
    def create_dashboard(self, data_dict: Dict[str, Union[pd.DataFrame, pd.Series]],
                        titles: Dict[str, str],
                        save_path: Optional[str] = None,
                        show_plot: bool = True) -> plt.Figure:
        """
        Dashboard oluşturma (birden fazla grafik)
        
        Args:
            data_dict: Veri sözlüğü
            titles: Başlık sözlüğü
            save_path: Kaydetme yolu
            show_plot: Grafiği gösterme
            
        Returns:
            plt.Figure: Oluşturulan dashboard
        """
        n_plots = len(data_dict)
        n_cols = min(3, n_plots)
        n_rows = (n_plots + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, 
                                figsize=(self.chart_config.figsize[0], 
                                        self.chart_config.figsize[1] * n_rows),
                                dpi=self.chart_config.dpi)
        
        if n_plots == 1:
            axes = [axes]
        elif n_rows == 1:
            axes = axes
        else:
            axes = axes.flatten()
        
        # Her veri için grafik oluştur
        for i, (key, data) in enumerate(data_dict.items()):
            if i >= len(axes):
                break
                
            ax = axes[i]
            title = titles.get(key, key)
            
            if isinstance(data, pd.DataFrame):
                if data.shape[0] == data.shape[1]:  # Kare matris - ısı haritası
                    im = ax.imshow(data.values, cmap=self.COLOR_PALETTES["default"])
                    ax.set_title(title, fontsize=12, fontweight='bold')
                    ax.set_xticks(range(len(data.columns)))
                    ax.set_yticks(range(len(data.index)))
                    ax.set_xticklabels(data.columns, rotation=45, ha='right', fontsize=8)
                    ax.set_yticklabels(data.index, fontsize=8)
                else:  # Dikdörtgen matris - performans ısı haritası
                    im = ax.imshow(data.values.T, cmap=self.COLOR_PALETTES["performance"])
                    ax.set_title(title, fontsize=12, fontweight='bold')
                    ax.set_xticks(range(len(data.index)))
                    ax.set_yticks(range(len(data.columns)))
                    
                    # Tarih etiketleri için kontrol
                    if hasattr(data.index[0], 'strftime'):
                        x_labels = [idx.strftime('%m-%d') for idx in data.index]
                    else:
                        x_labels = [str(idx) for idx in data.index]
                    
                    ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=8)
                    ax.set_yticklabels(data.columns, fontsize=8)
            else:  # Series - çizgi grafik
                ax.plot(data.index, data.values, linewidth=2, color='blue', alpha=0.8)
                ax.set_title(title, fontsize=12, fontweight='bold')
                ax.set_xlabel('Tarih', fontsize=10)
                ax.set_ylabel('Değer', fontsize=10)
                ax.grid(True, alpha=0.3)
        
        # Kullanılmayan subplot'ları gizle
        for i in range(n_plots, len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle("BIST AI Smart Trader - Analytics Dashboard", 
                     fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.chart_config.dpi, 
                       bbox_inches='tight', format=self.chart_config.save_format)
            print(f"📊 Dashboard kaydedildi: {save_path}")
        
        if show_plot:
            plt.show()
        
        return fig

# Test fonksiyonu
def test_heatmaps_visualizations():
    """Heatmaps & Visualizations test fonksiyonu"""
    print("🧪 Heatmaps & Visualizations Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    n_days = 60  # 2 ay
    n_assets = 8
    
    # Tarih aralığı
    dates = pd.date_range('2023-01-01', periods=n_days, freq='D')
    
    # Varlık isimleri
    asset_names = [f'Asset_{i+1}' for i in range(n_assets)]
    
    # Korelasyon matrisi
    correlation_data = np.random.uniform(-0.8, 0.8, (n_assets, n_assets))
    np.fill_diagonal(correlation_data, 1.0)  # Diagonal'i 1 yap
    correlation_matrix = pd.DataFrame(correlation_data, 
                                    index=asset_names, columns=asset_names)
    
    # Performans verisi
    performance_data = pd.DataFrame(
        np.random.normal(0.001, 0.02, (n_days, n_assets)),
        index=dates, columns=asset_names
    )
    # Kümülatif performans
    cumulative_performance = (1 + performance_data).cumprod()
    
    # Risk verisi
    risk_metrics = ['VaR_95', 'CVaR_95', 'Volatility', 'Max_Drawdown', 'Beta']
    risk_data = pd.DataFrame(
        np.random.uniform(0.01, 0.15, (n_assets, len(risk_metrics))),
        index=asset_names, columns=risk_metrics
    )
    
    # Volatilite verisi
    volatility_data = pd.DataFrame(
        np.random.uniform(0.05, 0.25, (n_days, n_assets)),
        index=dates, columns=asset_names
    )
    
    # Heatmaps & Visualizations başlat
    viz_engine = HeatmapsVisualizations()
    
    # Korelasyon ısı haritası test
    print("\n📊 Korelasyon Isı Haritası Test:")
    correlation_fig = viz_engine.create_correlation_heatmap(
        correlation_matrix,
        title="Test Korelasyon Matrisi",
        show_plot=False
    )
    print("   ✅ Korelasyon ısı haritası oluşturuldu")
    
    # Performans ısı haritası test
    print("\n📈 Performans Isı Haritası Test:")
    performance_fig = viz_engine.create_performance_heatmap(
        cumulative_performance,
        title="Test Performans Isı Haritası",
        show_plot=False
    )
    print("   ✅ Performans ısı haritası oluşturuldu")
    
    # Risk ısı haritası test
    print("\n⚠️ Risk Isı Haritası Test:")
    risk_fig = viz_engine.create_risk_heatmap(
        risk_data,
        title="Test Risk Isı Haritası",
        show_plot=False
    )
    print("   ✅ Risk ısı haritası oluşturuldu")
    
    # Volatilite ısı haritası test
    print("\n📊 Volatilite Isı Haritası Test:")
    volatility_fig = viz_engine.create_volatility_heatmap(
        volatility_data,
        title="Test Volatilite Isı Haritası",
        show_plot=False
    )
    print("   ✅ Volatilite ısı haritası oluşturuldu")
    
    # Performans grafiği test
    print("\n📈 Performans Grafiği Test:")
    performance_chart = viz_engine.create_performance_chart(
        cumulative_performance.iloc[:, 0],  # İlk varlık
        title="Test Performans Grafiği",
        chart_type="line",
        show_plot=False
    )
    print("   ✅ Performans grafiği oluşturuldu")
    
    # Risk metrikleri grafiği test
    print("\n⚠️ Risk Metrikleri Grafiği Test:")
    risk_chart = viz_engine.create_risk_metrics_chart(
        risk_data.iloc[0].to_dict(),  # İlk varlığın risk metrikleri
        title="Test Risk Metrikleri",
        chart_type="bar",
        show_plot=False
    )
    print("   ✅ Risk metrikleri grafiği oluşturuldu")
    
    # Dashboard test
    print("\n📊 Dashboard Test:")
    dashboard_data = {
        "correlation": correlation_matrix,
        "performance": cumulative_performance,
        "risk": risk_data,
        "volatility": volatility_data
    }
    dashboard_titles = {
        "correlation": "Korelasyon Matrisi",
        "performance": "Kümülatif Performans",
        "risk": "Risk Metrikleri",
        "volatility": "Volatilite Analizi"
    }
    
    dashboard_fig = viz_engine.create_dashboard(
        dashboard_data,
        dashboard_titles,
        show_plot=False
    )
    print("   ✅ Dashboard oluşturuldu")
    
    print("\n✅ Heatmaps & Visualizations Test Tamamlandı!")
    return viz_engine

if __name__ == "__main__":
    test_heatmaps_visualizations()
