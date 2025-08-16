"""
PRD v2.0 - BIST AI Smart Trader
UI/UX Improvements Module

UI/UX iyileştirmeleri modülü:
- User experience enhancements
- Interface improvements
- Accessibility features
- Performance optimizations
- User feedback system
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class UserPreference:
    """Kullanıcı tercihi"""
    user_id: str
    category: str
    key: str
    value: Any
    description: str = ""
    created_at: datetime = None
    last_modified: datetime = None

@dataclass
class AccessibilityConfig:
    """Erişilebilirlik konfigürasyonu"""
    high_contrast: bool = False
    large_fonts: bool = False
    screen_reader: bool = False
    keyboard_navigation: bool = True
    color_blind_friendly: bool = False
    reduced_motion: bool = False

@dataclass
class PerformanceMetric:
    """Performans metriği"""
    component_id: str
    load_time: float
    render_time: float
    memory_usage: float
    cpu_usage: float
    timestamp: datetime = None

@dataclass
class UserFeedback:
    """Kullanıcı geri bildirimi"""
    user_id: str
    component_id: str
    rating: int  # 1-5
    comment: str = ""
    category: str = "general"
    priority: str = "medium"  # low, medium, high, critical
    status: str = "open"  # open, in_progress, resolved, closed
    created_at: datetime = None
    resolved_at: datetime = None

class UIUXImprovements:
    """
    UI/UX İyileştirmeleri Sistemi
    
    PRD v2.0 gereksinimleri:
    - Kullanıcı deneyimi iyileştirmeleri
    - Arayüz iyileştirmeleri
    - Erişilebilirlik özellikleri
    - Performans optimizasyonları
    - Kullanıcı geri bildirim sistemi
    """
    
    def __init__(self):
        """UI/UX Improvements başlatıcı"""
        # Kullanıcı tercihleri
        self.user_preferences = {}
        
        # Erişilebilirlik konfigürasyonları
        self.accessibility_configs = {}
        
        # Performans metrikleri
        self.performance_metrics = []
        
        # Kullanıcı geri bildirimleri
        self.user_feedbacks = []
        
        # UI tema konfigürasyonları
        self.ui_themes = {
            'default': {
                'primary_color': '#1f77b4',
                'secondary_color': '#ff7f0e',
                'background_color': '#ffffff',
                'text_color': '#333333',
                'accent_color': '#2ca02c',
                'error_color': '#d62728',
                'warning_color': '#ff7f0e',
                'success_color': '#2ca02c'
            },
            'dark': {
                'primary_color': '#4a9eff',
                'secondary_color': '#ff9f4a',
                'background_color': '#1a1a1a',
                'text_color': '#ffffff',
                'accent_color': '#4aff4a',
                'error_color': '#ff4a4a',
                'warning_color': '#ff9f4a',
                'success_color': '#4aff4a'
            },
            'high_contrast': {
                'primary_color': '#000000',
                'secondary_color': '#ffffff',
                'background_color': '#ffffff',
                'text_color': '#000000',
                'accent_color': '#000000',
                'error_color': '#ff0000',
                'warning_color': '#ffff00',
                'success_color': '#00ff00'
            }
        }
        
        # Performans hedefleri
        self.performance_targets = {
            'page_load_time': 2.0,  # saniye
            'component_render_time': 0.5,  # saniye
            'memory_usage_limit': 100,  # MB
            'cpu_usage_limit': 50  # %
        }
        
        # Varsayılan erişilebilirlik ayarları
        self._create_default_accessibility_configs()
    
    def _create_default_accessibility_configs(self):
        """Varsayılan erişilebilirlik ayarlarını oluştur"""
        default_config = AccessibilityConfig()
        self.accessibility_configs['default'] = default_config
        
        # Yüksek kontrast konfigürasyonu
        high_contrast_config = AccessibilityConfig(
            high_contrast=True,
            large_fonts=True,
            color_blind_friendly=True
        )
        self.accessibility_configs['high_contrast'] = high_contrast_config
        
        # Büyük font konfigürasyonu
        large_fonts_config = AccessibilityConfig(
            large_fonts=True,
            keyboard_navigation=True
        )
        self.accessibility_configs['large_fonts'] = large_fonts_config
    
    def set_user_preference(self, user_id: str, category: str, key: str, 
                           value: Any, description: str = "") -> bool:
        """
        Kullanıcı tercihi ayarla
        
        Args:
            user_id: Kullanıcı ID
            category: Tercih kategorisi
            key: Tercih anahtarı
            value: Tercih değeri
            description: Açıklama
            
        Returns:
            bool: Başarı durumu
        """
        try:
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {}
            
            if category not in self.user_preferences[user_id]:
                self.user_preferences[user_id][category] = {}
            
            preference = UserPreference(
                user_id=user_id,
                category=category,
                key=key,
                value=value,
                description=description,
                created_at=datetime.now(),
                last_modified=datetime.now()
            )
            
            self.user_preferences[user_id][category][key] = preference
            print(f"✅ Kullanıcı tercihi ayarlandı: {user_id} -> {category}.{key}")
            return True
            
        except Exception as e:
            print(f"❌ Kullanıcı tercihi ayarlama hatası: {str(e)}")
            return False
    
    def get_user_preference(self, user_id: str, category: str, key: str) -> Optional[Any]:
        """
        Kullanıcı tercihini al
        
        Args:
            user_id: Kullanıcı ID
            category: Tercih kategorisi
            key: Tercih anahtarı
            
        Returns:
            Optional[Any]: Tercih değeri
        """
        try:
            if (user_id in self.user_preferences and 
                category in self.user_preferences[user_id] and 
                key in self.user_preferences[user_id][category]):
                return self.user_preferences[user_id][category][key].value
            return None
            
        except Exception as e:
            print(f"❌ Kullanıcı tercihi alma hatası: {str(e)}")
            return None
    
    def get_user_preferences(self, user_id: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Kullanıcı tercihlerini al
        
        Args:
            user_id: Kullanıcı ID
            category: Tercih kategorisi (opsiyonel)
            
        Returns:
            Dict[str, Any]: Tercihler
        """
        try:
            if user_id not in self.user_preferences:
                return {}
            
            if category:
                if category in self.user_preferences[user_id]:
                    return {key: pref.value for key, pref in 
                           self.user_preferences[user_id][category].items()}
                return {}
            else:
                # Tüm kategoriler
                all_preferences = {}
                for cat, prefs in self.user_preferences[user_id].items():
                    all_preferences[cat] = {key: pref.value for key, pref in prefs.items()}
                return all_preferences
                
        except Exception as e:
            print(f"❌ Kullanıcı tercihleri alma hatası: {str(e)}")
            return {}
    
    def set_accessibility_config(self, user_id: str, config: AccessibilityConfig) -> bool:
        """
        Erişilebilirlik konfigürasyonu ayarla
        
        Args:
            user_id: Kullanıcı ID
            config: Erişilebilirlik konfigürasyonu
            
        Returns:
            bool: Başarı durumu
        """
        try:
            self.accessibility_configs[user_id] = config
            print(f"✅ Erişilebilirlik konfigürasyonu ayarlandı: {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erişilebilirlik konfigürasyonu ayarlama hatası: {str(e)}")
            return False
    
    def get_accessibility_config(self, user_id: str) -> AccessibilityConfig:
        """
        Erişilebilirlik konfigürasyonunu al
        
        Args:
            user_id: Kullanıcı ID
            
        Returns:
            AccessibilityConfig: Erişilebilirlik konfigürasyonu
        """
        return self.accessibility_configs.get(user_id, self.accessibility_configs['default'])
    
    def get_ui_theme(self, theme_name: str = 'default') -> Dict[str, str]:
        """
        UI temasını al
        
        Args:
            theme_name: Tema adı
            
        Returns:
            Dict[str, str]: Tema renkleri
        """
        return self.ui_themes.get(theme_name, self.ui_themes['default'])
    
    def create_custom_theme(self, name: str, colors: Dict[str, str]) -> bool:
        """
        Özel tema oluştur
        
        Args:
            name: Tema adı
            colors: Renk konfigürasyonu
            
        Returns:
            bool: Başarı durumu
        """
        try:
            # Gerekli renkleri kontrol et
            required_colors = ['primary_color', 'secondary_color', 'background_color', 'text_color']
            for color in required_colors:
                if color not in colors:
                    print(f"❌ Gerekli renk eksik: {color}")
                    return False
            
            self.ui_themes[name] = colors
            print(f"✅ Özel tema oluşturuldu: {name}")
            return True
            
        except Exception as e:
            print(f"❌ Tema oluşturma hatası: {str(e)}")
            return False
    
    def record_performance_metric(self, component_id: str, load_time: float, 
                                  render_time: float, memory_usage: float, 
                                  cpu_usage: float) -> bool:
        """
        Performans metriği kaydet
        
        Args:
            component_id: Bileşen ID
            load_time: Yükleme süresi
            render_time: Render süresi
            memory_usage: Bellek kullanımı
            cpu_usage: CPU kullanımı
            
        Returns:
            bool: Başarı durumu
        """
        try:
            metric = PerformanceMetric(
                component_id=component_id,
                load_time=load_time,
                render_time=render_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                timestamp=datetime.now()
            )
            
            self.performance_metrics.append(metric)
            
            # Performans hedeflerini kontrol et
            self._check_performance_targets(metric)
            
            return True
            
        except Exception as e:
            print(f"❌ Performans metriği kaydetme hatası: {str(e)}")
            return False
    
    def _check_performance_targets(self, metric: PerformanceMetric):
        """Performans hedeflerini kontrol et"""
        warnings = []
        
        if metric.load_time > self.performance_targets['page_load_time']:
            warnings.append(f"Yükleme süresi hedefi aşıldı: {metric.load_time:.2f}s")
        
        if metric.render_time > self.performance_targets['component_render_time']:
            warnings.append(f"Render süresi hedefi aşıldı: {metric.render_time:.2f}s")
        
        if metric.memory_usage > self.performance_targets['memory_usage_limit']:
            warnings.append(f"Bellek kullanımı hedefi aşıldı: {metric.memory_usage:.2f}MB")
        
        if metric.cpu_usage > self.performance_targets['cpu_usage_limit']:
            warnings.append(f"CPU kullanımı hedefi aşıldı: {metric.cpu_usage:.2f}%")
        
        if warnings:
            print(f"⚠️ Performans uyarıları ({metric.component_id}):")
            for warning in warnings:
                print(f"   {warning}")
    
    def get_performance_summary(self, component_id: Optional[str] = None, 
                                time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Performans özetini al
        
        Args:
            component_id: Bileşen ID (opsiyonel)
            time_range: Zaman aralığı (opsiyonel)
            
        Returns:
            Dict[str, Any]: Performans özeti
        """
        try:
            # Filtreleme
            metrics = self.performance_metrics
            
            if component_id:
                metrics = [m for m in metrics if m.component_id == component_id]
            
            if time_range:
                cutoff_time = datetime.now() - time_range
                metrics = [m for m in metrics if m.timestamp >= cutoff_time]
            
            if not metrics:
                return {'error': 'Veri bulunamadı'}
            
            # İstatistikler
            summary = {
                'total_metrics': len(metrics),
                'components': list(set(m.component_id for m in metrics)),
                'load_time': {
                    'mean': np.mean([m.load_time for m in metrics]),
                    'median': np.median([m.load_time for m in metrics]),
                    'min': np.min([m.load_time for m in metrics]),
                    'max': np.max([m.load_time for m in metrics])
                },
                'render_time': {
                    'mean': np.mean([m.render_time for m in metrics]),
                    'median': np.median([m.render_time for m in metrics]),
                    'min': np.min([m.render_time for m in metrics]),
                    'max': np.max([m.render_time for m in metrics])
                },
                'memory_usage': {
                    'mean': np.mean([m.memory_usage for m in metrics]),
                    'median': np.median([m.memory_usage for m in metrics]),
                    'min': np.min([m.memory_usage for m in metrics]),
                    'max': np.max([m.memory_usage for m in metrics])
                },
                'cpu_usage': {
                    'mean': np.mean([m.cpu_usage for m in metrics]),
                    'median': np.median([m.cpu_usage for m in metrics]),
                    'min': np.min([m.cpu_usage for m in metrics]),
                    'max': np.max([m.cpu_usage for m in metrics])
                }
            }
            
            return summary
            
        except Exception as e:
            print(f"❌ Performans özeti alma hatası: {str(e)}")
            return {'error': str(e)}
    
    def submit_user_feedback(self, user_id: str, component_id: str, rating: int,
                             comment: str = "", category: str = "general",
                             priority: str = "medium") -> bool:
        """
        Kullanıcı geri bildirimi gönder
        
        Args:
            user_id: Kullanıcı ID
            component_id: Bileşen ID
            rating: Değerlendirme (1-5)
            comment: Yorum
            category: Kategori
            priority: Öncelik
            
        Returns:
            bool: Başarı durumu
        """
        try:
            # Rating kontrolü
            if not 1 <= rating <= 5:
                print(f"❌ Geçersiz rating: {rating} (1-5 arası olmalı)")
                return False
            
            feedback = UserFeedback(
                user_id=user_id,
                component_id=component_id,
                rating=rating,
                comment=comment,
                category=category,
                priority=priority,
                status="open",
                created_at=datetime.now()
            )
            
            self.user_feedbacks.append(feedback)
            print(f"✅ Kullanıcı geri bildirimi gönderildi: {user_id} -> {component_id}")
            return True
            
        except Exception as e:
            print(f"❌ Geri bildirim gönderme hatası: {str(e)}")
            return False
    
    def get_user_feedbacks(self, component_id: Optional[str] = None,
                           status: Optional[str] = None,
                           priority: Optional[str] = None) -> List[UserFeedback]:
        """
        Kullanıcı geri bildirimlerini al
        
        Args:
            component_id: Bileşen ID (opsiyonel)
            status: Durum (opsiyonel)
            priority: Öncelik (opsiyonel)
            
        Returns:
            List[UserFeedback]: Geri bildirimler
        """
        try:
            feedbacks = self.user_feedbacks
            
            if component_id:
                feedbacks = [f for f in feedbacks if f.component_id == component_id]
            
            if status:
                feedbacks = [f for f in feedbacks if f.status == status]
            
            if priority:
                feedbacks = [f for f in feedbacks if f.priority == priority]
            
            return feedbacks
            
        except Exception as e:
            print(f"❌ Geri bildirim alma hatası: {str(e)}")
            return []
    
    def update_feedback_status(self, feedback_id: int, new_status: str,
                               resolution_comment: str = "") -> bool:
        """
        Geri bildirim durumunu güncelle
        
        Args:
            feedback_id: Geri bildirim ID
            new_status: Yeni durum
            resolution_comment: Çözüm yorumu
            
        Returns:
            bool: Başarı durumu
        """
        try:
            if feedback_id >= len(self.user_feedbacks):
                print(f"❌ Geçersiz feedback ID: {feedback_id}")
                return False
            
            feedback = self.user_feedbacks[feedback_id]
            feedback.status = new_status
            
            if new_status == "resolved":
                feedback.resolved_at = datetime.now()
                if resolution_comment:
                    feedback.comment += f"\n[Çözüm: {resolution_comment}]"
            
            print(f"✅ Geri bildirim durumu güncellendi: {feedback_id} -> {new_status}")
            return True
            
        except Exception as e:
            print(f"❌ Geri bildirim durumu güncelleme hatası: {str(e)}")
            return False
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Geri bildirim istatistiklerini al"""
        try:
            if not self.user_feedbacks:
                return {'error': 'Geri bildirim bulunamadı'}
            
            stats = {
                'total_feedbacks': len(self.user_feedbacks),
                'average_rating': np.mean([f.rating for f in self.user_feedbacks]),
                'ratings_distribution': {
                    '1': len([f for f in self.user_feedbacks if f.rating == 1]),
                    '2': len([f for f in self.user_feedbacks if f.rating == 2]),
                    '3': len([f for f in self.user_feedbacks if f.rating == 3]),
                    '4': len([f for f in self.user_feedbacks if f.rating == 4]),
                    '5': len([f for f in self.user_feedbacks if f.rating == 5])
                },
                'status_distribution': {},
                'priority_distribution': {},
                'category_distribution': {},
                'component_feedback_count': {}
            }
            
            # Durum dağılımı
            for feedback in self.user_feedbacks:
                if feedback.status not in stats['status_distribution']:
                    stats['status_distribution'][feedback.status] = 0
                stats['status_distribution'][feedback.status] += 1
                
                if feedback.priority not in stats['priority_distribution']:
                    stats['priority_distribution'][feedback.priority] = 0
                stats['priority_distribution'][feedback.priority] += 1
                
                if feedback.category not in stats['category_distribution']:
                    stats['category_distribution'][feedback.category] = 0
                stats['category_distribution'][feedback.category] += 1
                
                if feedback.component_id not in stats['component_feedback_count']:
                    stats['component_feedback_count'][feedback.component_id] = 0
                stats['component_feedback_count'][feedback.component_id] += 1
            
            return stats
            
        except Exception as e:
            print(f"❌ Geri bildirim istatistikleri alma hatası: {str(e)}")
            return {'error': str(e)}
    
    def optimize_performance(self, component_id: str) -> Dict[str, Any]:
        """
        Bileşen performansını optimize et
        
        Args:
            component_id: Bileşen ID
            
        Returns:
            Dict[str, Any]: Optimizasyon önerileri
        """
        try:
            # Bileşen performans metriklerini al
            metrics = [m for m in self.performance_metrics if m.component_id == component_id]
            
            if not metrics:
                return {'error': 'Performans verisi bulunamadı'}
            
            # Son 10 metrik
            recent_metrics = sorted(metrics, key=lambda x: x.timestamp)[-10:]
            
            recommendations = []
            
            # Yükleme süresi optimizasyonu
            avg_load_time = np.mean([m.load_time for m in recent_metrics])
            if avg_load_time > self.performance_targets['page_load_time']:
                recommendations.append({
                    'type': 'load_time',
                    'severity': 'high' if avg_load_time > 5.0 else 'medium',
                    'current': f"{avg_load_time:.2f}s",
                    'target': f"{self.performance_targets['page_load_time']:.2f}s",
                    'suggestion': 'Lazy loading, code splitting, CDN kullanımı'
                })
            
            # Render süresi optimizasyonu
            avg_render_time = np.mean([m.render_time for m in recent_metrics])
            if avg_render_time > self.performance_targets['component_render_time']:
                recommendations.append({
                    'type': 'render_time',
                    'severity': 'high' if avg_render_time > 1.0 else 'medium',
                    'current': f"{avg_render_time:.2f}s",
                    'target': f"{self.performance_targets['component_render_time']:.2f}s",
                    'suggestion': 'Virtual scrolling, memoization, render optimization'
                })
            
            # Bellek kullanımı optimizasyonu
            avg_memory = np.mean([m.memory_usage for m in recent_metrics])
            if avg_memory > self.performance_targets['memory_usage_limit']:
                recommendations.append({
                    'type': 'memory_usage',
                    'severity': 'high' if avg_memory > 200 else 'medium',
                    'current': f"{avg_memory:.2f}MB",
                    'target': f"{self.performance_targets['memory_usage_limit']:.2f}MB",
                    'suggestion': 'Memory leaks kontrolü, garbage collection, data cleanup'
                })
            
            return {
                'component_id': component_id,
                'analysis_date': datetime.now().isoformat(),
                'metrics_analyzed': len(recent_metrics),
                'recommendations': recommendations,
                'overall_score': self._calculate_performance_score(recent_metrics)
            }
            
        except Exception as e:
            print(f"❌ Performans optimizasyon hatası: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_performance_score(self, metrics: List[PerformanceMetric]) -> float:
        """Performans skoru hesapla (0-100)"""
        try:
            if not metrics:
                return 0.0
            
            # Her metrik için skor hesapla
            scores = []
            
            for metric in metrics:
                load_score = max(0, 100 - (metric.load_time / self.performance_targets['page_load_time']) * 100)
                render_score = max(0, 100 - (metric.render_time / self.performance_targets['component_render_time']) * 100)
                memory_score = max(0, 100 - (metric.memory_usage / self.performance_targets['memory_usage_limit']) * 100)
                cpu_score = max(0, 100 - (metric.cpu_usage / self.performance_targets['cpu_usage_limit']) * 100)
                
                # Ağırlıklı ortalama
                metric_score = (load_score * 0.3 + render_score * 0.3 + 
                              memory_score * 0.2 + cpu_score * 0.2)
                scores.append(metric_score)
            
            return np.mean(scores)
            
        except Exception:
            return 0.0

# Test fonksiyonu
def test_ui_ux_improvements():
    """UI/UX Improvements test fonksiyonu"""
    print("🧪 UI/UX Improvements Test Başlıyor...")
    
    # UI/UX Improvements başlat
    ui_ux = UIUXImprovements()
    
    # Kullanıcı tercihi test
    print("\n⚙️ Kullanıcı Tercihi Test:")
    preference_set = ui_ux.set_user_preference(
        "test_user_1",
        "theme",
        "color_scheme",
        "dark",
        "Koyu tema tercihi"
    )
    print(f"   Kullanıcı tercihi ayarlandı: {preference_set}")
    
    # Tercih alma test
    preference_value = ui_ux.get_user_preference("test_user_1", "theme", "color_scheme")
    print(f"   Tercih değeri alındı: {preference_value}")
    
    # Erişilebilirlik test
    print("\n♿ Erişilebilirlik Test:")
    accessibility_config = AccessibilityConfig(
        high_contrast=True,
        large_fonts=True,
        color_blind_friendly=True
    )
    
    config_set = ui_ux.set_accessibility_config("test_user_1", accessibility_config)
    print(f"   Erişilebilirlik konfigürasyonu ayarlandı: {config_set}")
    
    # UI tema test
    print("\n🎨 UI Tema Test:")
    default_theme = ui_ux.get_ui_theme()
    print(f"   Varsayılan tema: {len(default_theme)} renk")
    
    # Özel tema oluştur test
    custom_colors = {
        'primary_color': '#ff6b6b',
        'secondary_color': '#4ecdc4',
        'background_color': '#f7f7f7',
        'text_color': '#2d3436',
        'accent_color': '#45b7d1',
        'error_color': '#e74c3c',
        'warning_color': '#f39c12',
        'success_color': '#27ae60'
    }
    
    custom_theme_created = ui_ux.create_custom_theme("custom_theme", custom_colors)
    print(f"   Özel tema oluşturuldu: {custom_theme_created}")
    
    # Performans metrik test
    print("\n📊 Performans Metrik Test:")
    for i in range(5):
        metric_recorded = ui_ux.record_performance_metric(
            f"component_{i}",
            load_time=np.random.uniform(0.5, 3.0),
            render_time=np.random.uniform(0.1, 1.0),
            memory_usage=np.random.uniform(20, 150),
            cpu_usage=np.random.uniform(10, 80)
        )
        print(f"   Metrik {i+1} kaydedildi: {metric_recorded}")
    
    # Performans özeti test
    print("\n📈 Performans Özeti Test:")
    performance_summary = ui_ux.get_performance_summary()
    if 'error' not in performance_summary:
        print(f"   ✅ Performans özeti alındı: {performance_summary['total_metrics']} metrik")
        print(f"   📊 Ortalama yükleme süresi: {performance_summary['load_time']['mean']:.2f}s")
    
    # Kullanıcı geri bildirim test
    print("\n💬 Kullanıcı Geri Bildirim Test:")
    for i in range(3):
        feedback_submitted = ui_ux.submit_user_feedback(
            f"user_{i}",
            f"component_{i}",
            rating=np.random.randint(1, 6),
            comment=f"Test geri bildirimi {i+1}",
            category="test",
            priority=np.random.choice(["low", "medium", "high"])
        )
        print(f"   Geri bildirim {i+1} gönderildi: {feedback_submitted}")
    
    # Geri bildirim istatistikleri test
    print("\n📋 Geri Bildirim İstatistikleri Test:")
    feedback_stats = ui_ux.get_feedback_statistics()
    if 'error' not in feedback_stats:
        print(f"   ✅ İstatistikler alındı: {feedback_stats['total_feedbacks']} geri bildirim")
        print(f"   ⭐ Ortalama rating: {feedback_stats['average_rating']:.2f}")
    
    # Performans optimizasyon test
    print("\n🔧 Performans Optimizasyon Test:")
    optimization_result = ui_ux.optimize_performance("component_0")
    if 'error' not in optimization_result:
        print(f"   ✅ Optimizasyon analizi tamamlandı")
        print(f"   📊 Performans skoru: {optimization_result['overall_score']:.1f}/100")
        print(f"   💡 Öneri sayısı: {len(optimization_result['recommendations'])}")
    
    # Kullanıcı tercihleri test
    print("\n👤 Kullanıcı Tercihleri Test:")
    all_preferences = ui_ux.get_user_preferences("test_user_1")
    print(f"   ✅ Tüm tercihler alındı: {len(all_preferences)} kategori")
    
    print("\n✅ UI/UX Improvements Test Tamamlandı!")
    
    return ui_ux

if __name__ == "__main__":
    test_ui_ux_improvements()
