"""
PRD v2.0 - BIST AI Smart Trader
Advanced Charts Module

Gelişmiş grafik modülü:
- Interactive charts
- Multiple chart types
- Real-time updates
- Custom styling
- Export capabilities
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

@dataclass
class ChartConfig:
    """Grafik konfigürasyonu"""
    title: str
    xlabel: str
    ylabel: str
    figsize: Tuple[int, int] = (12, 8)
    style: str = "seaborn-v0_8"
    colors: List[str] = None
    grid: bool = True
    legend: bool = True
    annotations: bool = True

@dataclass
class ChartData:
    """Grafik verisi"""
    x: Union[pd.Series, np.ndarray]
    y: Union[pd.Series, np.ndarray]
    labels: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    metadata: Optional[Dict] = None

class AdvancedCharts:
    """
    Gelişmiş Grafik Sistemi
    
    PRD v2.0 gereksinimleri:
    - Etkileşimli grafikler
    - Çoklu grafik türleri
    - Gerçek zamanlı güncellemeler
    - Özel stil
    - Dışa aktarma özellikleri
    """
    
    def __init__(self):
        """Advanced Charts başlatıcı"""
        # Varsayılan renkler
        self.DEFAULT_COLORS = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        
        # Grafik stilleri
        self.AVAILABLE_STYLES = plt.style.available
        
        # Varsayılan stil
        plt.style.use('seaborn-v0_8')
        
        # Türkçe karakter desteği
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
    
    def create_candlestick_chart(self, data: pd.DataFrame, 
                                 config: ChartConfig,
                                 show_volume: bool = True,
                                 show_indicators: bool = True) -> plt.Figure:
        """
        Candlestick grafik oluşturma
        
        Args:
            data: OHLCV verisi
            config: Grafik konfigürasyonu
            show_volume: Hacim göster
            show_indicators: Teknik indikatörler göster
            
        Returns:
            plt.Figure: Oluşturulan grafik
        """
        fig, axes = plt.subplots(2 if show_volume else 1, 1, 
                                figsize=config.figsize,
                                gridspec_kw={'height_ratios': [3, 1]} if show_volume else None)
        
        if show_volume:
            ax1, ax2 = axes
        else:
            ax1 = axes
        
        # Ana grafik (candlestick)
        self._plot_candlesticks(ax1, data)
        
        # Teknik indikatörler
        if show_indicators:
            self._add_technical_indicators(ax1, data)
        
        # Grafik ayarları
        ax1.set_title(config.title, fontsize=16, fontweight='bold')
        ax1.set_xlabel(config.xlabel)
        ax1.set_ylabel(config.ylabel)
        ax1.grid(config.grid, alpha=0.3)
        
        # X ekseni formatı
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Hacim grafiği
        if show_volume:
            self._plot_volume(ax2, data)
            ax2.set_xlabel('Tarih')
            ax2.set_ylabel('Hacim')
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def _plot_candlesticks(self, ax: plt.Axes, data: pd.DataFrame):
        """Candlestick çizimi"""
        # Renk belirleme
        colors = ['green' if close >= open else 'red' 
                 for open, close in zip(data['Open'], data['Close'])]
        
        # Candlestick çizimi
        for i, (date, open_price, high, low, close, volume) in enumerate(
            zip(data.index, data['Open'], data['High'], data['Low'], data['Close'], data['Volume'])
        ):
            # Gövde
            body_height = close - open_price
            body_bottom = min(open_price, close)
            
            # Gövde dikdörtgeni
            rect = Rectangle((i-0.3, body_bottom), 0.6, abs(body_height),
                           facecolor=colors[i], edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
            
            # Fitil çizgisi
            ax.plot([i, i], [low, high], color='black', linewidth=1)
            
            # Açılış/kapanış işaretleri
            if open_price != close:
                ax.plot([i-0.3, i+0.3], [open_price, open_price], color='black', linewidth=1)
                ax.plot([i-0.3, i+0.3], [close, close], color='black', linewidth=1)
    
    def _add_technical_indicators(self, ax: plt.Axes, data: pd.DataFrame):
        """Teknik indikatörler ekleme"""
        # SMA 20
        if len(data) >= 20:
            sma_20 = data['Close'].rolling(window=20).mean()
            ax.plot(range(len(data)), sma_20, color='blue', linewidth=2, label='SMA 20', alpha=0.7)
        
        # SMA 50
        if len(data) >= 50:
            sma_50 = data['Close'].rolling(window=50).mean()
            ax.plot(range(len(data)), sma_50, color='red', linewidth=2, label='SMA 50', alpha=0.7)
        
        # Bollinger Bands
        if len(data) >= 20:
            sma = data['Close'].rolling(window=20).mean()
            std = data['Close'].rolling(window=20).std()
            upper_band = sma + (std * 2)
            lower_band = sma - (std * 2)
            
            ax.plot(range(len(data)), upper_band, color='gray', linewidth=1, 
                   label='Bollinger Upper', alpha=0.5, linestyle='--')
            ax.plot(range(len(data)), lower_band, color='gray', linewidth=1, 
                   label='Bollinger Lower', alpha=0.5, linestyle='--')
        
        if ax.get_legend():
            ax.legend()
    
    def _plot_volume(self, ax: plt.Axes, data: pd.DataFrame):
        """Hacim grafiği"""
        colors = ['green' if close >= open else 'red' 
                 for open, close in zip(data['Open'], data['Close'])]
        
        ax.bar(range(len(data)), data['Volume'], color=colors, alpha=0.7)
    
    def create_technical_analysis_chart(self, data: pd.DataFrame,
                                       config: ChartConfig,
                                       indicators: List[str] = None) -> plt.Figure:
        """
        Teknik analiz grafiği oluşturma
        
        Args:
            data: Fiyat verisi
            config: Grafik konfigürasyonu
            indicators: Gösterilecek indikatörler
            
        Returns:
            plt.Figure: Oluşturulan grafik
        """
        if indicators is None:
            indicators = ['rsi', 'macd', 'bollinger']
        
        # Alt grafik sayısı
        n_subplots = len(indicators) + 1
        
        fig, axes = plt.subplots(n_subplots, 1, figsize=config.figsize)
        if n_subplots == 1:
            axes = [axes]
        
        # Ana fiyat grafiği
        ax_main = axes[0]
        ax_main.plot(data.index, data['Close'], color='blue', linewidth=2)
        ax_main.set_title(f"{config.title} - Fiyat", fontweight='bold')
        ax_main.grid(True, alpha=0.3)
        
        # Teknik indikatörler
        for i, indicator in enumerate(indicators):
            ax = axes[i + 1]
            
            if indicator == 'rsi':
                self._plot_rsi(ax, data)
            elif indicator == 'macd':
                self._plot_macd(ax, data)
            elif indicator == 'bollinger':
                self._plot_bollinger(ax, data)
            elif indicator == 'volume':
                self._plot_volume(ax, data)
            
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def _plot_rsi(self, ax: plt.Axes, data: pd.DataFrame):
        """RSI grafiği"""
        # RSI hesaplama
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        ax.plot(data.index, rsi, color='purple', linewidth=2)
        ax.axhline(y=70, color='red', linestyle='--', alpha=0.7)
        ax.axhline(y=30, color='green', linestyle='--', alpha=0.7)
        ax.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
        ax.set_title('RSI (14)', fontweight='bold')
        ax.set_ylabel('RSI')
        ax.set_ylim(0, 100)
    
    def _plot_macd(self, ax: plt.Axes, data: pd.DataFrame):
        """MACD grafiği"""
        # MACD hesaplama
        ema_12 = data['Close'].ewm(span=12).mean()
        ema_26 = data['Close'].ewm(span=26).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal
        
        ax.plot(data.index, macd, color='blue', linewidth=2, label='MACD')
        ax.plot(data.index, signal, color='red', linewidth=2, label='Signal')
        ax.bar(data.index, histogram, color='gray', alpha=0.5, label='Histogram')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax.set_title('MACD', fontweight='bold')
        ax.set_ylabel('MACD')
        ax.legend()
    
    def _plot_bollinger(self, ax: plt.Axes, data: pd.DataFrame):
        """Bollinger Bands grafiği"""
        # Bollinger Bands hesaplama
        sma = data['Close'].rolling(window=20).mean()
        std = data['Close'].rolling(window=20).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        
        ax.plot(data.index, data['Close'], color='blue', linewidth=2, label='Fiyat')
        ax.plot(data.index, upper_band, color='red', linewidth=1, label='Upper Band', linestyle='--')
        ax.plot(data.index, lower_band, color='red', linewidth=1, label='Lower Band', linestyle='--')
        ax.plot(data.index, sma, color='orange', linewidth=2, label='SMA 20')
        ax.set_title('Bollinger Bands', fontweight='bold')
        ax.set_ylabel('Fiyat')
        ax.legend()
    
    def create_correlation_heatmap(self, data: pd.DataFrame,
                                   config: ChartConfig,
                                   method: str = 'pearson') -> plt.Figure:
        """
        Korelasyon heatmap oluşturma
        
        Args:
            data: Sayısal veri
            config: Grafik konfigürasyonu
            method: Korelasyon metodu
            
        Returns:
            plt.Figure: Oluşturulan grafik
        """
        fig, ax = plt.subplots(figsize=config.figsize)
        
        # Korelasyon matrisi
        corr_matrix = data.corr(method=method)
        
        # Heatmap
        im = ax.imshow(corr_matrix, cmap='RdYlBu_r', aspect='auto')
        
        # Renk çubuğu
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel('Korelasyon', rotation=-90, va="bottom")
        
        # Eksen etiketleri
        ax.set_xticks(range(len(corr_matrix.columns)))
        ax.set_yticks(range(len(corr_matrix.columns)))
        ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
        ax.set_yticklabels(corr_matrix.columns)
        
        # Değer etiketleri
        for i in range(len(corr_matrix.columns)):
            for j in range(len(corr_matrix.columns)):
                text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                              ha="center", va="center", color="black", fontsize=8)
        
        ax.set_title(config.title, fontsize=16, fontweight='bold')
        ax.set_xlabel(config.xlabel)
        ax.set_ylabel(config.ylabel)
        
        plt.tight_layout()
        return fig
    
    def create_performance_chart(self, data: pd.DataFrame,
                                 config: ChartConfig,
                                 benchmark: Optional[pd.Series] = None) -> plt.Figure:
        """
        Performans grafiği oluşturma
        
        Args:
            data: Performans verisi
            config: Grafik konfigürasyonu
            benchmark: Karşılaştırma verisi
            
        Returns:
            plt.Figure: Oluşturulan grafik
        """
        fig, ax = plt.subplots(figsize=config.figsize)
        
        # Kümülatif getiri
        if 'returns' in data.columns:
            cumulative_returns = (1 + data['returns']).cumprod()
            ax.plot(data.index, cumulative_returns, color='blue', linewidth=2, label='Portföy')
        
        # Benchmark
        if benchmark is not None:
            benchmark_cumulative = (1 + benchmark).cumprod()
            ax.plot(data.index, benchmark_cumulative, color='red', linewidth=2, label='Benchmark')
        
        # Grafik ayarları
        ax.set_title(config.title, fontsize=16, fontweight='bold')
        ax.set_xlabel(config.xlabel)
        ax.set_ylabel(config.ylabel)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # X ekseni formatı
        if hasattr(data.index[0], 'strftime'):
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return fig
    
    def create_risk_metrics_chart(self, data: pd.DataFrame,
                                   config: ChartConfig) -> plt.Figure:
        """
        Risk metrikleri grafiği oluşturma
        
        Args:
            data: Risk verisi
            config: Grafik konfigürasyonu
            
        Returns:
            plt.Figure: Oluşturulan grafik
        """
        fig, axes = plt.subplots(2, 2, figsize=config.figsize)
        axes = axes.flatten()
        
        # Volatilite
        if 'volatility' in data.columns:
            axes[0].plot(data.index, data['volatility'], color='blue', linewidth=2)
            axes[0].set_title('Volatilite', fontweight='bold')
            axes[0].set_ylabel('Volatilite')
            axes[0].grid(True, alpha=0.3)
        
        # VaR
        if 'var' in data.columns:
            axes[1].plot(data.index, data['var'], color='red', linewidth=2)
            axes[1].set_title('Value at Risk', fontweight='bold')
            axes[1].set_ylabel('VaR')
            axes[1].grid(True, alpha=0.3)
        
        # Sharpe Ratio
        if 'sharpe' in data.columns:
            axes[2].plot(data.index, data['sharpe'], color='green', linewidth=2)
            axes[2].set_title('Sharpe Ratio', fontweight='bold')
            axes[2].set_ylabel('Sharpe')
            axes[2].grid(True, alpha=0.3)
        
        # Maximum Drawdown
        if 'drawdown' in data.columns:
            axes[3].fill_between(data.index, data['drawdown'], 0, color='red', alpha=0.3)
            axes[3].set_title('Maximum Drawdown', fontweight='bold')
            axes[3].set_ylabel('Drawdown')
            axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_sector_analysis_chart(self, data: pd.DataFrame,
                                     config: ChartConfig) -> plt.Figure:
        """
        Sektör analizi grafiği oluşturma
        
        Args:
            data: Sektör verisi
            config: Grafik konfigürasyonu
            
        Returns:
            plt.Figure: Oluşturulan grafik
        """
        fig, axes = plt.subplots(2, 2, figsize=config.figsize)
        axes = axes.flatten()
        
        # Sektör performansı
        if 'sector_performance' in data.columns:
            sector_data = data['sector_performance']
            colors = self.DEFAULT_COLORS[:len(sector_data)]
            
            axes[0].bar(range(len(sector_data)), sector_data.values, color=colors)
            axes[0].set_title('Sektör Performansı', fontweight='bold')
            axes[0].set_ylabel('Performans (%)')
            axes[0].set_xticks(range(len(sector_data)))
            axes[0].set_xticklabels(sector_data.index, rotation=45)
            axes[0].grid(True, alpha=0.3)
        
        # Sektör ağırlıkları
        if 'sector_weights' in data.columns:
            weights_data = data['sector_weights']
            axes[1].pie(weights_data.values, labels=weights_data.index, autopct='%1.1f%%',
                       colors=self.DEFAULT_COLORS[:len(weights_data)])
            axes[1].set_title('Sektör Ağırlıkları', fontweight='bold')
        
        # Sektör korelasyonu
        if 'sector_correlation' in data.columns:
            corr_data = data['sector_correlation']
            im = axes[2].imshow(corr_data, cmap='RdYlBu_r', aspect='auto')
            axes[2].set_title('Sektör Korelasyonu', fontweight='bold')
            
            # Renk çubuğu
            cbar = fig.colorbar(im, ax=axes[2])
            cbar.ax.set_ylabel('Korelasyon', rotation=-90, va="bottom")
        
        # Sektör trendi
        if 'sector_trend' in data.columns:
            trend_data = data['sector_trend']
            for sector in trend_data.columns:
                axes[3].plot(trend_data.index, trend_data[sector], label=sector, linewidth=2)
            axes[3].set_title('Sektör Trendi', fontweight='bold')
            axes[3].set_ylabel('Trend')
            axes[3].legend()
            axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def export_chart(self, fig: plt.Figure, filename: str, 
                     format: str = 'png', dpi: int = 300) -> bool:
        """
        Grafiği dışa aktarma
        
        Args:
            fig: Grafik figürü
            filename: Dosya adı
            format: Dosya formatı
            dpi: Çözünürlük
            
        Returns:
            bool: Başarı durumu
        """
        try:
            fig.savefig(filename, format=format, dpi=dpi, bbox_inches='tight')
            return True
        except Exception as e:
            print(f"Grafik dışa aktarma hatası: {str(e)}")
            return False
    
    def create_dashboard_layout(self, charts: List[plt.Figure],
                                layout: str = 'grid',
                                figsize: Tuple[int, int] = (20, 12)) -> plt.Figure:
        """
        Dashboard düzeni oluşturma
        
        Args:
            charts: Grafik listesi
            layout: Düzen türü
            figsize: Figür boyutu
            
        Returns:
            plt.Figure: Dashboard figürü
        """
        if layout == 'grid':
            n_charts = len(charts)
            n_cols = min(3, n_charts)
            n_rows = (n_charts + n_cols - 1) // n_cols
            
            fig = plt.figure(figsize=figsize)
            
            for i, chart in enumerate(charts):
                # Alt grafik pozisyonu
                pos = n_rows * 100 + n_cols * 10 + (i + 1)
                ax = fig.add_subplot(pos)
                
                # Grafik içeriğini kopyala
                for line in chart.axes[0].get_lines():
                    ax.plot(line.get_xdata(), line.get_ydata(), 
                           color=line.get_color(), linewidth=line.get_linewidth())
                
                ax.set_title(chart.axes[0].get_title())
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            return fig
        
        else:
            # Tek sütun düzeni
            fig, axes = plt.subplots(len(charts), 1, figsize=figsize)
            if len(charts) == 1:
                axes = [axes]
            
            for i, chart in enumerate(charts):
                ax = axes[i]
                
                # Grafik içeriğini kopyala
                for line in chart.axes[0].get_lines():
                    ax.plot(line.get_xdata(), line.get_ydata(), 
                           color=line.get_color(), linewidth=line.get_linewidth())
                
                ax.set_title(chart.axes[0].get_title())
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            return fig

# Test fonksiyonu
def test_advanced_charts():
    """Advanced Charts test fonksiyonu"""
    print("🧪 Advanced Charts Test Başlıyor...")
    
    # Test verisi oluştur
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    # OHLCV verisi
    close_prices = 100 + np.cumsum(np.random.randn(100) * 0.02)
    open_prices = close_prices + np.random.randn(100) * 0.5
    high_prices = np.maximum(open_prices, close_prices) + np.random.rand(100) * 0.5
    low_prices = np.minimum(open_prices, close_prices) - np.random.rand(100) * 0.5
    volumes = np.random.randint(1000000, 10000000, 100)
    
    test_data = pd.DataFrame({
        'Open': open_prices,
        'High': high_prices,
        'Low': low_prices,
        'Close': close_prices,
        'Volume': volumes
    }, index=dates)
    
    # Returns hesapla
    test_data['returns'] = test_data['Close'].pct_change()
    
    # Advanced Charts başlat
    charts = AdvancedCharts()
    
    # Candlestick grafik test
    print("\n📈 Candlestick Grafik Test:")
    candlestick_config = ChartConfig(
        title="Test Hisse - Candlestick Grafik",
        xlabel="Tarih",
        ylabel="Fiyat (TL)"
    )
    
    candlestick_fig = charts.create_candlestick_chart(test_data, candlestick_config)
    print("   ✅ Candlestick grafik oluşturuldu")
    
    # Teknik analiz grafik test
    print("\n🔍 Teknik Analiz Grafik Test:")
    technical_config = ChartConfig(
        title="Test Hisse - Teknik Analiz",
        xlabel="Tarih",
        ylabel="Değer"
    )
    
    technical_fig = charts.create_technical_analysis_chart(
        test_data, technical_config, ['rsi', 'macd']
    )
    print("   ✅ Teknik analiz grafik oluşturuldu")
    
    # Korelasyon heatmap test
    print("\n🔥 Korelasyon Heatmap Test:")
    # Korelasyon için sayısal veri
    numeric_data = test_data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    numeric_data['Returns'] = test_data['returns']
    numeric_data = numeric_data.dropna()
    
    correlation_config = ChartConfig(
        title="Test Hisse - Korelasyon Matrisi",
        xlabel="Özellikler",
        ylabel="Özellikler"
    )
    
    correlation_fig = charts.create_correlation_heatmap(numeric_data, correlation_config)
    print("   ✅ Korelasyon heatmap oluşturuldu")
    
    # Performans grafik test
    print("\n📊 Performans Grafik Test:")
    performance_config = ChartConfig(
        title="Test Hisse - Performans",
        xlabel="Tarih",
        ylabel="Kümülatif Getiri"
    )
    
    performance_fig = charts.create_performance_chart(test_data, performance_config)
    print("   ✅ Performans grafik oluşturuldu")
    
    # Risk metrikleri test
    print("\n⚠️ Risk Metrikleri Test:")
    # Risk verisi oluştur
    risk_data = pd.DataFrame({
        'volatility': test_data['returns'].rolling(20).std() * np.sqrt(252),
        'var': test_data['returns'].rolling(20).quantile(0.05),
        'sharpe': test_data['returns'].rolling(20).mean() / test_data['returns'].rolling(20).std() * np.sqrt(252),
        'drawdown': (test_data['Close'] / test_data['Close'].cummax() - 1) * 100
    }, index=test_data.index)
    
    risk_config = ChartConfig(
        title="Test Hisse - Risk Metrikleri",
        xlabel="Tarih",
        ylabel="Değer"
    )
    
    risk_fig = charts.create_risk_metrics_chart(risk_data, risk_config)
    print("   ✅ Risk metrikleri grafik oluşturuldu")
    
    # Grafik dışa aktarma test
    print("\n💾 Grafik Dışa Aktarma Test:")
    export_success = charts.export_chart(candlestick_fig, "test_candlestick.png")
    print(f"   Grafik dışa aktarıldı: {export_success}")
    
    # Dashboard düzeni test
    print("\n🎛️ Dashboard Düzeni Test:")
    dashboard_fig = charts.create_dashboard_layout(
        [candlestick_fig, technical_fig, correlation_fig, performance_fig, risk_fig],
        layout='grid'
    )
    print("   ✅ Dashboard düzeni oluşturuldu")
    
    print("\n✅ Advanced Charts Test Tamamlandı!")
    
    # Test dosyasını temizle
    import os
    if os.path.exists("test_candlestick.png"):
        os.remove("test_candlestick.png")
    
    return charts

if __name__ == "__main__":
    test_advanced_charts()
