"""
PRD v2.0 - BIST AI Smart Trader
Dashboard Components Module

Dashboard bileşenleri modülü:
- Reusable components
- Layout management
- Component interactions
- Data binding
- Responsive design
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class ComponentConfig:
    """Bileşen konfigürasyonu"""
    id: str
    type: str
    title: str
    position: Tuple[int, int]  # (row, col)
    size: Tuple[int, int] = (1, 1)  # (height, width)
    data_source: Optional[str] = None
    refresh_interval: Optional[int] = None  # saniye
    visible: bool = True
    config: Optional[Dict[str, Any]] = None

@dataclass
class DashboardLayout:
    """Dashboard düzeni"""
    name: str
    components: List[ComponentConfig]
    grid_size: Tuple[int, int] = (12, 12)  # (rows, cols)
    theme: str = "default"
    responsive: bool = True
    created_at: datetime = None
    last_modified: datetime = None

@dataclass
class ComponentData:
    """Bileşen verisi"""
    component_id: str
    data: Any
    metadata: Dict[str, Any]
    last_updated: datetime
    status: str = "success"  # success, error, loading

class DashboardComponents:
    """
    Dashboard Bileşenleri Sistemi
    
    PRD v2.0 gereksinimleri:
    - Yeniden kullanılabilir bileşenler
    - Düzen yönetimi
    - Bileşen etkileşimleri
    - Veri bağlama
    - Duyarlı tasarım
    """
    
    def __init__(self):
        """Dashboard Components başlatıcı"""
        # Mevcut bileşen türleri
        self.COMPONENT_TYPES = {
            'chart': 'Grafik Bileşeni',
            'table': 'Tablo Bileşeni',
            'metric': 'Metrik Bileşeni',
            'gauge': 'Gösterge Bileşeni',
            'progress': 'İlerleme Çubuğu',
            'alert': 'Uyarı Bileşeni',
            'filter': 'Filtre Bileşeni',
            'summary': 'Özet Bileşeni',
            'news': 'Haber Bileşeni',
            'portfolio': 'Portföy Bileşeni'
        }
        
        # Dashboard düzenleri
        self.layouts = {}
        
        # Bileşen verileri
        self.component_data = {}
        
        # Bileşen etkileşimleri
        self.component_interactions = {}
        
        # Varsayılan bileşenleri oluştur
        self._create_default_components()
    
    def _create_default_components(self):
        """Varsayılan bileşenleri oluştur"""
        # Ana dashboard düzeni
        main_layout = DashboardLayout(
            name="main_dashboard",
            components=[],  # Boş liste ile başlat
            grid_size=(8, 12),
            theme="default",
            responsive=True,
            created_at=datetime.now(),
            last_modified=datetime.now()
        )
        
        # Bileşenleri ekle
        components = [
            # Üst satır - Metrikler
            ComponentConfig(
                id="market_summary",
                type="summary",
                title="Piyasa Özeti",
                position=(0, 0),
                size=(1, 3),
                data_source="market_data",
                refresh_interval=60
            ),
            ComponentConfig(
                id="portfolio_value",
                type="metric",
                title="Portföy Değeri",
                position=(0, 3),
                size=(1, 2),
                data_source="portfolio_data",
                refresh_interval=30
            ),
            ComponentConfig(
                id="risk_metrics",
                type="gauge",
                title="Risk Metrikleri",
                position=(0, 5),
                size=(1, 2),
                data_source="risk_data",
                refresh_interval=120
            ),
            ComponentConfig(
                id="alerts",
                type="alert",
                title="Uyarılar",
                position=(0, 7),
                size=(1, 2),
                data_source="alert_data",
                refresh_interval=15
            ),
            
            # İkinci satır - Ana grafikler
            ComponentConfig(
                id="price_chart",
                type="chart",
                title="Fiyat Grafiği",
                position=(1, 0),
                size=(3, 6),
                data_source="price_data",
                refresh_interval=30
            ),
            ComponentConfig(
                id="technical_indicators",
                type="chart",
                title="Teknik İndikatörler",
                position=(1, 6),
                size=(3, 6),
                data_source="technical_data",
                refresh_interval=60
            ),
            
            # Dördüncü satır - Tablolar
            ComponentConfig(
                id="signals_table",
                type="table",
                title="Sinyal Tablosu",
                position=(4, 0),
                size=(2, 6),
                data_source="signals_data",
                refresh_interval=60
            ),
            ComponentConfig(
                id="portfolio_table",
                type="table",
                title="Portföy Tablosu",
                position=(4, 6),
                size=(2, 6),
                data_source="portfolio_data",
                refresh_interval=120
            ),
            
            # Alt satır - Filtreler ve özet
            ComponentConfig(
                id="filters",
                type="filter",
                title="Filtreler",
                position=(6, 0),
                size=(1, 4),
                data_source="filter_data"
            ),
            ComponentConfig(
                id="news_feed",
                type="news",
                title="Haber Akışı",
                position=(6, 4),
                size=(1, 8),
                data_source="news_data",
                refresh_interval=300
            )
        ]
        
        main_layout.components = components
        self.layouts["main_dashboard"] = main_layout
        
        print("✅ Varsayılan dashboard bileşenleri oluşturuldu")
    
    def create_component(self, config: ComponentConfig) -> bool:
        """
        Yeni bileşen oluştur
        
        Args:
            config: Bileşen konfigürasyonu
            
        Returns:
            bool: Başarı durumu
        """
        try:
            # Bileşen ID kontrolü
            if config.id in [comp.id for comp in self._get_all_components()]:
                print(f"⚠️ Bileşen ID zaten mevcut: {config.id}")
                return False
            
            # Bileşen türü kontrolü
            if config.type not in self.COMPONENT_TYPES:
                print(f"❌ Desteklenmeyen bileşen türü: {config.type}")
                return False
            
            # Pozisyon kontrolü
            if not self._is_valid_position(config.position, config.size):
                print(f"❌ Geçersiz pozisyon: {config.position}")
                return False
            
            # Bileşeni uygun layout'a ekle
            layout_name = self._find_layout_for_component(config.id)
            if layout_name:
                self.layouts[layout_name].components.append(config)
                print(f"✅ Bileşen oluşturuldu: {config.id} ({config.type})")
                return True
            else:
                print(f"❌ Layout bulunamadı")
                return False
                
        except Exception as e:
            print(f"❌ Bileşen oluşturma hatası: {str(e)}")
            return False
    
    def update_component(self, component_id: str, updates: Dict[str, Any]) -> bool:
        """
        Bileşen güncelle
        
        Args:
            component_id: Bileşen ID
            updates: Güncellenecek alanlar
            
        Returns:
            bool: Başarı durumu
        """
        try:
            component = self._find_component(component_id)
            if not component:
                print(f"❌ Bileşen bulunamadı: {component_id}")
                return False
            
            # Güncellemeleri uygula
            for field, value in updates.items():
                if hasattr(component, field):
                    setattr(component, field, value)
            
            # Son güncelleme zamanını güncelle
            if hasattr(component, 'last_modified'):
                component.last_modified = datetime.now()
            
            print(f"✅ Bileşen güncellendi: {component_id}")
            return True
            
        except Exception as e:
            print(f"❌ Bileşen güncelleme hatası: {str(e)}")
            return False
    
    def delete_component(self, component_id: str) -> bool:
        """
        Bileşen sil
        
        Args:
            component_id: Bileşen ID
            
        Returns:
            bool: Başarı durumu
        """
        try:
            component = self._find_component(component_id)
            if not component:
                print(f"❌ Bileşen bulunamadı: {component_id}")
                return False
            
            # Bileşeni layout'tan kaldır
            for layout in self.layouts.values():
                layout.components = [comp for comp in layout.components if comp.id != component_id]
            
            # Bileşen verisini temizle
            if component_id in self.component_data:
                del self.component_data[component_id]
            
            print(f"✅ Bileşen silindi: {component_id}")
            return True
            
        except Exception as e:
            print(f"❌ Bileşen silme hatası: {str(e)}")
            return False
    
    def create_layout(self, name: str, grid_size: Tuple[int, int] = (12, 12),
                      theme: str = "default", responsive: bool = True) -> bool:
        """
        Yeni layout oluştur
        
        Args:
            name: Layout adı
            grid_size: Grid boyutu
            theme: Tema
            responsive: Duyarlı tasarım
            
        Returns:
            bool: Başarı durumu
        """
        try:
            if name in self.layouts:
                print(f"⚠️ Layout adı zaten mevcut: {name}")
                return False
            
            layout = DashboardLayout(
                name=name,
                components=[],
                grid_size=grid_size,
                theme=theme,
                responsive=responsive,
                created_at=datetime.now(),
                last_modified=datetime.now()
            )
            
            self.layouts[name] = layout
            print(f"✅ Layout oluşturuldu: {name}")
            return True
            
        except Exception as e:
            print(f"❌ Layout oluşturma hatası: {str(e)}")
            return False
    
    def add_component_to_layout(self, layout_name: str, component_config: ComponentConfig) -> bool:
        """
        Layout'a bileşen ekle
        
        Args:
            layout_name: Layout adı
            component_config: Bileşen konfigürasyonu
            
        Returns:
            bool: Başarı durumu
        """
        try:
            if layout_name not in self.layouts:
                print(f"❌ Layout bulunamadı: {layout_name}")
                return False
            
            layout = self.layouts[layout_name]
            
            # Pozisyon kontrolü
            if not self._is_valid_position_in_layout(component_config.position, 
                                                    component_config.size, layout):
                print(f"❌ Geçersiz pozisyon layout'ta: {component_config.position}")
                return False
            
            # Bileşeni ekle
            layout.components.append(component_config)
            layout.last_modified = datetime.now()
            
            print(f"✅ Bileşen layout'a eklendi: {component_config.id} -> {layout_name}")
            return True
            
        except Exception as e:
            print(f"❌ Bileşen ekleme hatası: {str(e)}")
            return False
    
    def update_component_data(self, component_id: str, data: Any, 
                              metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Bileşen verisini güncelle
        
        Args:
            component_id: Bileşen ID
            data: Yeni veri
            metadata: Ek bilgiler
            
        Returns:
            bool: Başarı durumu
        """
        try:
            component_data = ComponentData(
                component_id=component_id,
                data=data,
                metadata=metadata or {},
                last_updated=datetime.now(),
                status="success"
            )
            
            self.component_data[component_id] = component_data
            return True
            
        except Exception as e:
            print(f"❌ Veri güncelleme hatası: {str(e)}")
            return False
    
    def get_component_data(self, component_id: str) -> Optional[ComponentData]:
        """
        Bileşen verisini al
        
        Args:
            component_id: Bileşen ID
            
        Returns:
            Optional[ComponentData]: Bileşen verisi
        """
        return self.component_data.get(component_id)
    
    def get_layout(self, layout_name: str) -> Optional[DashboardLayout]:
        """
        Layout'u al
        
        Args:
            layout_name: Layout adı
            
        Returns:
            Optional[DashboardLayout]: Layout
        """
        return self.layouts.get(layout_name)
    
    def get_all_layouts(self) -> List[str]:
        """Tüm layout adlarını listele"""
        return list(self.layouts.keys())
    
    def export_layout(self, layout_name: str, format: str = 'json') -> Optional[str]:
        """
        Layout'u dışa aktar
        
        Args:
            layout_name: Layout adı
            format: Dışa aktarma formatı
            
        Returns:
            Optional[str]: Dışa aktarılan veri
        """
        if layout_name not in self.layouts:
            print(f"❌ Layout bulunamadı: {layout_name}")
            return None
        
        layout = self.layouts[layout_name]
        
        try:
            if format == 'json':
                import json
                layout_dict = {
                    'name': layout.name,
                    'grid_size': layout.grid_size,
                    'theme': layout.theme,
                    'responsive': layout.responsive,
                    'components': [
                        {
                            'id': comp.id,
                            'type': comp.type,
                            'title': comp.title,
                            'position': comp.position,
                            'size': comp.size,
                            'data_source': comp.data_source,
                            'refresh_interval': comp.refresh_interval,
                            'visible': comp.visible,
                            'config': comp.config
                        }
                        for comp in layout.components
                    ],
                    'created_at': layout.created_at.isoformat() if layout.created_at else None,
                    'last_modified': layout.last_modified.isoformat() if layout.last_modified else None
                }
                return json.dumps(layout_dict, indent=2, ensure_ascii=False)
            else:
                print(f"⚠️ Desteklenmeyen format: {format}")
                return None
                
        except Exception as e:
            print(f"❌ Dışa aktarma hatası: {str(e)}")
            return None
    
    def _find_component(self, component_id: str) -> Optional[ComponentConfig]:
        """Bileşeni bul"""
        for layout in self.layouts.values():
            for component in layout.components:
                if component.id == component_id:
                    return component
        return None
    
    def _find_layout_for_component(self, component_id: str) -> Optional[str]:
        """Bileşenin bulunduğu layout'u bul"""
        for layout_name, layout in self.layouts.items():
            for component in layout.components:
                if component.id == component_id:
                    return layout_name
        return None
    
    def _get_all_components(self) -> List[ComponentConfig]:
        """Tüm bileşenleri al"""
        components = []
        for layout in self.layouts.values():
            components.extend(layout.components)
        return components
    
    def _is_valid_position(self, position: Tuple[int, int], size: Tuple[int, int]) -> bool:
        """Pozisyon geçerliliğini kontrol et"""
        row, col = position
        height, width = size
        
        if row < 0 or col < 0 or height <= 0 or width <= 0:
            return False
        
        return True
    
    def _is_valid_position_in_layout(self, position: Tuple[int, int], 
                                    size: Tuple[int, int], layout: DashboardLayout) -> bool:
        """Layout'ta pozisyon geçerliliğini kontrol et"""
        row, col = position
        height, width = size
        max_rows, max_cols = layout.grid_size
        
        if row + height > max_rows or col + width > max_cols:
            return False
        
        # Çakışma kontrolü
        for component in layout.components:
            if component.id != "temp":  # Geçici bileşen kontrolü
                comp_row, comp_col = component.position
                comp_height, comp_width = component.size
                
                # Çakışma kontrolü
                if not (row + height <= comp_row or comp_row + comp_height <= row or
                       col + width <= comp_col or comp_col + comp_width <= col):
                    return False
        
        return True
    
    def get_component_statistics(self) -> Dict[str, Any]:
        """Bileşen istatistiklerini al"""
        stats = {
            'total_components': 0,
            'components_by_type': {},
            'total_layouts': len(self.layouts),
            'components_by_layout': {},
            'data_sources': set(),
            'refresh_intervals': set()
        }
        
        for layout_name, layout in self.layouts.items():
            stats['components_by_layout'][layout_name] = len(layout.components)
            stats['total_components'] += len(layout.components)
            
            for component in layout.components:
                # Tür bazında sayım
                if component.type not in stats['components_by_type']:
                    stats['components_by_type'][component.type] = 0
                stats['components_by_type'][component.type] += 1
                
                # Veri kaynakları
                if component.data_source:
                    stats['data_sources'].add(component.data_source)
                
                # Yenileme aralıkları
                if component.refresh_interval:
                    stats['refresh_intervals'].add(component.refresh_interval)
        
        # Set'leri listeye çevir
        stats['data_sources'] = list(stats['data_sources'])
        stats['refresh_intervals'] = list(stats['refresh_intervals'])
        
        return stats

# Test fonksiyonu
def test_dashboard_components():
    """Dashboard Components test fonksiyonu"""
    print("🧪 Dashboard Components Test Başlıyor...")
    
    # Dashboard Components başlat
    dashboard = DashboardComponents()
    
    # Layout listesi test
    print("\n📋 Layout Listesi Test:")
    layouts = dashboard.get_all_layouts()
    print(f"   ✅ Mevcut layout'lar: {layouts}")
    
    # Ana dashboard layout'unu al
    main_layout = dashboard.get_layout("main_dashboard")
    if main_layout:
        print(f"   ✅ Ana dashboard: {len(main_layout.components)} bileşen")
    
    # Yeni layout oluştur test
    print("\n🏗️ Yeni Layout Test:")
    new_layout_created = dashboard.create_layout(
        "custom_dashboard",
        grid_size=(6, 8),
        theme="dark",
        responsive=True
    )
    print(f"   Yeni layout oluşturuldu: {new_layout_created}")
    
    # Yeni bileşen oluştur test
    print("\n🔧 Yeni Bileşen Test:")
    new_component = ComponentConfig(
        id="custom_chart",
        type="chart",
        title="Özel Grafik",
        position=(0, 0),
        size=(2, 3),
        data_source="custom_data",
        refresh_interval=45
    )
    
    component_created = dashboard.create_component(new_component)
    print(f"   Yeni bileşen oluşturuldu: {component_created}")
    
    # Layout'a bileşen ekle test
    print("\n📌 Layout'a Bileşen Ekleme Test:")
    custom_component = ComponentConfig(
        id="portfolio_summary",
        type="summary",
        title="Portföy Özeti",
        position=(0, 0),
        size=(1, 2),
        data_source="portfolio_summary_data"
    )
    
    component_added = dashboard.add_component_to_layout("custom_dashboard", custom_component)
    print(f"   Bileşen layout'a eklendi: {component_added}")
    
    # Bileşen verisi güncelle test
    print("\n📊 Bileşen Verisi Test:")
    test_data = pd.DataFrame({
        'Metric': ['Değer', 'Getiri', 'Risk'],
        'Value': [100000, 0.15, 0.08]
    })
    
    data_updated = dashboard.update_component_data("portfolio_summary", test_data, 
                                                  {'source': 'test', 'timestamp': datetime.now()})
    print(f"   Veri güncellendi: {data_updated}")
    
    # Bileşen verisi al test
    print("\n📥 Bileşen Verisi Alma Test:")
    component_data = dashboard.get_component_data("portfolio_summary")
    if component_data:
        print(f"   ✅ Veri alındı: {len(component_data.data)} satır")
        print(f"   📅 Son güncelleme: {component_data.last_updated}")
    
    # Bileşen güncelle test
    print("\n✏️ Bileşen Güncelleme Test:")
    updates = {
        'title': 'Güncellenmiş Portföy Özeti',
        'refresh_interval': 60
    }
    
    component_updated = dashboard.update_component("portfolio_summary", updates)
    print(f"   Bileşen güncellendi: {component_updated}")
    
    # Layout dışa aktarma test
    print("\n💾 Layout Dışa Aktarma Test:")
    exported_layout = dashboard.export_layout("custom_dashboard", "json")
    if exported_layout:
        print("   ✅ Layout dışa aktarıldı")
    
    # İstatistikler test
    print("\n📈 İstatistikler Test:")
    stats = dashboard.get_component_statistics()
    print(f"   Toplam bileşen: {stats['total_components']}")
    print(f"   Toplam layout: {stats['total_layouts']}")
    print(f"   Bileşen türleri: {stats['components_by_type']}")
    
    # Bileşen sil test
    print("\n🗑️ Bileşen Silme Test:")
    component_deleted = dashboard.delete_component("custom_chart")
    print(f"   Bileşen silindi: {component_deleted}")
    
    print("\n✅ Dashboard Components Test Tamamlandı!")
    
    return dashboard

if __name__ == "__main__":
    test_dashboard_components()
