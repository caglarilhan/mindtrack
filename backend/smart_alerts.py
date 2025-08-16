"""
PRD v2.0 - BIST AI Smart Trader
Smart Alerts Module

Akıllı uyarı sistemi:
- Price alerts
- Pattern alerts
- News alerts
- Risk alerts
- Smart notification system
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import asyncio
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

class AlertType(Enum):
    """Uyarı türleri"""
    PRICE = "price"
    PATTERN = "pattern"
    NEWS = "news"
    RISK = "risk"
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"

class AlertSeverity(Enum):
    """Uyarı önem dereceleri"""
    INFO = "info"
    WARNING = "warning"
    ALERT = "alert"
    CRITICAL = "critical"

@dataclass
class Alert:
    """Uyarı nesnesi"""
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    asset: str
    timestamp: datetime
    data: Dict
    is_active: bool = True
    is_read: bool = False
    expires_at: Optional[datetime] = None

@dataclass
class AlertRule:
    """Uyarı kuralı"""
    id: str
    name: str
    type: AlertType
    conditions: Dict
    actions: List[str]
    is_active: bool = True
    priority: int = 1

class SmartAlerts:
    """
    Akıllı Uyarı Sistemi
    
    PRD v2.0 gereksinimleri:
    - Fiyat tabanlı uyarılar
    - Teknik formasyon uyarıları
    - Haber ve sentiment uyarıları
    - Risk tabanlı uyarılar
    - Akıllı bildirim sistemi
    """
    
    def __init__(self, notification_callback: Optional[Callable] = None):
        """
        Smart Alerts başlatıcı
        
        Args:
            notification_callback: Bildirim callback fonksiyonu
        """
        self.notification_callback = notification_callback
        self.alerts: List[Alert] = []
        self.alert_rules: List[AlertRule] = []
        self.alert_counter = 0
        
        # Varsayılan uyarı kuralları
        self._setup_default_rules()
        
        # Uyarı geçmişi
        self.alert_history: List[Alert] = []
        
    def _setup_default_rules(self):
        """Varsayılan uyarı kurallarını kur"""
        default_rules = [
            AlertRule(
                id="price_breakout",
                name="Fiyat Kırılımı",
                type=AlertType.PRICE,
                conditions={
                    "price_change_pct": 5.0,
                    "volume_increase": 2.0,
                    "timeframe": "1d"
                },
                actions=["notify", "log"],
                priority=2
            ),
            AlertRule(
                id="pattern_detection",
                name="Formasyon Tespiti",
                type=AlertType.PATTERN,
                conditions={
                    "pattern_types": ["bullish_engulfing", "golden_cross", "support_break"],
                    "confidence_threshold": 0.7
                },
                actions=["notify", "log", "portfolio_check"],
                priority=3
            ),
            AlertRule(
                id="risk_limit",
                name="Risk Limiti",
                type=AlertType.RISK,
                conditions={
                    "var_threshold": 0.05,
                    "drawdown_threshold": 0.15,
                    "volatility_threshold": 0.25
                },
                actions=["notify", "log", "risk_mitigation"],
                priority=1
            ),
            AlertRule(
                id="news_sentiment",
                name="Haber Sentiment",
                type=AlertType.NEWS,
                conditions={
                    "sentiment_threshold": 0.6,
                    "impact_threshold": 0.4,
                    "asset_relevance": 0.8
                },
                actions=["notify", "log", "sentiment_analysis"],
                priority=2
            )
        ]
        
        self.alert_rules.extend(default_rules)
    
    def create_price_alert(self, asset: str, price: float, 
                          alert_type: str = "breakout",
                          threshold: float = 5.0,
                          timeframe: str = "1d") -> Alert:
        """
        Fiyat uyarısı oluşturma
        
        Args:
            asset: Varlık sembolü
            price: Mevcut fiyat
            alert_type: Uyarı türü (breakout, support, resistance)
            threshold: Eşik değeri
            timeframe: Zaman dilimi
            
        Returns:
            Alert: Oluşturulan uyarı
        """
        self.alert_counter += 1
        alert_id = f"price_{self.alert_counter}"
        
        # Uyarı türüne göre mesaj oluştur
        if alert_type == "breakout":
            title = f"Fiyat Kırılımı: {asset}"
            message = f"{asset} fiyatı %{threshold:.1f} değişim gösterdi. Mevcut fiyat: {price:.2f}"
            severity = AlertSeverity.ALERT
        elif alert_type == "support":
            title = f"Destek Seviyesi: {asset}"
            message = f"{asset} destek seviyesine yaklaştı. Mevcut fiyat: {price:.2f}"
            severity = AlertSeverity.WARNING
        elif alert_type == "resistance":
            title = f"Direnç Seviyesi: {asset}"
            message = f"{asset} direnç seviyesine yaklaştı. Mevcut fiyat: {price:.2f}"
            severity = AlertSeverity.WARNING
        else:
            title = f"Fiyat Uyarısı: {asset}"
            message = f"{asset} için fiyat uyarısı. Mevcut fiyat: {price:.2f}"
            severity = AlertSeverity.INFO
        
        alert = Alert(
            id=alert_id,
            type=AlertType.PRICE,
            severity=severity,
            title=title,
            message=message,
            asset=asset,
            timestamp=datetime.now(),
            data={
                "price": price,
                "alert_type": alert_type,
                "threshold": threshold,
                "timeframe": timeframe,
                "price_change_pct": threshold
            },
            expires_at=datetime.now() + timedelta(days=1)
        )
        
        self.alerts.append(alert)
        self._process_alert(alert)
        
        return alert
    
    def create_pattern_alert(self, asset: str, pattern_type: str,
                            confidence: float, price: float,
                            additional_data: Optional[Dict] = None) -> Alert:
        """
        Formasyon uyarısı oluşturma
        
        Args:
            asset: Varlık sembolü
            pattern_type: Formasyon türü
            confidence: Güven skoru
            price: Mevcut fiyat
            additional_data: Ek veri
            
        Returns:
            Alert: Oluşturulan uyarı
        """
        self.alert_counter += 1
        alert_id = f"pattern_{self.alert_counter}"
        
        # Formasyon türüne göre mesaj oluştur
        pattern_names = {
            "bullish_engulfing": "Boğa Yutma",
            "bearish_engulfing": "Ayı Yutma",
            "golden_cross": "Altın Kesişim",
            "death_cross": "Ölüm Kesişimi",
            "support_break": "Destek Kırılımı",
            "resistance_break": "Direnç Kırılımı",
            "double_bottom": "Çifte Dip",
            "double_top": "Çifte Tepe"
        }
        
        pattern_name = pattern_names.get(pattern_type, pattern_type)
        
        if confidence > 0.8:
            severity = AlertSeverity.ALERT
        elif confidence > 0.6:
            severity = AlertSeverity.WARNING
        else:
            severity = AlertSeverity.INFO
        
        title = f"Formasyon Tespiti: {asset}"
        message = f"{asset} için {pattern_name} formasyonu tespit edildi. Güven: %{confidence*100:.1f}, Fiyat: {price:.2f}"
        
        alert = Alert(
            id=alert_id,
            type=AlertType.PATTERN,
            severity=severity,
            title=title,
            message=message,
            asset=asset,
            timestamp=datetime.now(),
            data={
                "pattern_type": pattern_type,
                "pattern_name": pattern_name,
                "confidence": confidence,
                "price": price,
                "additional_data": additional_data or {}
            },
            expires_at=datetime.now() + timedelta(hours=6)
        )
        
        self.alerts.append(alert)
        self._process_alert(alert)
        
        return alert
    
    def create_news_alert(self, asset: str, news_title: str,
                          sentiment_score: float, impact_score: float,
                          source: str = "unknown") -> Alert:
        """
        Haber uyarısı oluşturma
        
        Args:
            asset: Varlık sembolü
            news_title: Haber başlığı
            sentiment_score: Sentiment skoru (-1 ile 1 arası)
            impact_score: Etki skoru (0 ile 1 arası)
            source: Haber kaynağı
            
        Returns:
            Alert: Oluşturulan uyarı
        """
        self.alert_counter += 1
        alert_id = f"news_{self.alert_counter}"
        
        # Sentiment skoruna göre mesaj oluştur
        if sentiment_score > 0.5:
            sentiment_text = "Pozitif"
            severity = AlertSeverity.INFO
        elif sentiment_score < -0.5:
            sentiment_text = "Negatif"
            severity = AlertSeverity.WARNING
        else:
            sentiment_text = "Nötr"
            severity = AlertSeverity.INFO
        
        # Etki skoruna göre önem derecesini artır
        if impact_score > 0.7:
            severity = AlertSeverity.ALERT
        elif impact_score > 0.5:
            severity = AlertSeverity.WARNING
        
        title = f"Haber Uyarısı: {asset}"
        message = f"{asset} için {sentiment_text} haber: {news_title[:100]}... (Etki: %{impact_score*100:.1f})"
        
        alert = Alert(
            id=alert_id,
            type=AlertType.NEWS,
            severity=severity,
            title=title,
            message=message,
            asset=asset,
            timestamp=datetime.now(),
            data={
                "news_title": news_title,
                "sentiment_score": sentiment_score,
                "impact_score": impact_score,
                "source": source,
                "sentiment_text": sentiment_text
            },
            expires_at=datetime.now() + timedelta(hours=12)
        )
        
        self.alerts.append(alert)
        self._process_alert(alert)
        
        return alert
    
    def create_risk_alert(self, asset: str, risk_type: str,
                          current_value: float, threshold: float,
                          portfolio_impact: Optional[float] = None) -> Alert:
        """
        Risk uyarısı oluşturma
        
        Args:
            asset: Varlık sembolü
            risk_type: Risk türü
            current_value: Mevcut değer
            threshold: Eşik değeri
            portfolio_impact: Portföy etkisi
            
        Returns:
            Alert: Oluşturulan uyarı
        """
        self.alert_counter += 1
        alert_id = f"risk_{self.alert_counter}"
        
        # Risk türüne göre mesaj oluştur
        risk_names = {
            "var_limit": "VaR Limiti",
            "drawdown_limit": "Drawdown Limiti",
            "volatility_limit": "Volatilite Limiti",
            "concentration_limit": "Konsantrasyon Limiti",
            "correlation_limit": "Korelasyon Limiti"
        }
        
        risk_name = risk_names.get(risk_type, risk_type)
        
        # Risk seviyesine göre önem derecesi
        if current_value > threshold * 1.5:
            severity = AlertSeverity.CRITICAL
        elif current_value > threshold:
            severity = AlertSeverity.ALERT
        else:
            severity = AlertSeverity.WARNING
        
        title = f"Risk Uyarısı: {asset}"
        message = f"{asset} için {risk_name} aşıldı. Mevcut: {current_value:.4f}, Eşik: {threshold:.4f}"
        
        if portfolio_impact:
            message += f" (Portföy Etkisi: %{portfolio_impact*100:.2f})"
        
        alert = Alert(
            id=alert_id,
            type=AlertType.RISK,
            severity=severity,
            title=title,
            message=message,
            asset=asset,
            timestamp=datetime.now(),
            data={
                "risk_type": risk_type,
                "risk_name": risk_name,
                "current_value": current_value,
                "threshold": threshold,
                "portfolio_impact": portfolio_impact,
                "exceedance_ratio": current_value / threshold if threshold > 0 else 0
            },
            expires_at=datetime.now() + timedelta(hours=2)
        )
        
        self.alerts.append(alert)
        self._process_alert(alert)
        
        return alert
    
    def create_technical_alert(self, asset: str, indicator: str,
                              signal: str, value: float,
                              additional_info: Optional[Dict] = None) -> Alert:
        """
        Teknik indikatör uyarısı oluşturma
        
        Args:
            asset: Varlık sembolü
            indicator: İndikatör adı
            signal: Sinyal türü (buy, sell, neutral)
            value: İndikatör değeri
            additional_info: Ek bilgi
            
        Returns:
            Alert: Oluşturulan uyarı
        """
        self.alert_counter += 1
        alert_id = f"technical_{self.alert_counter}"
        
        # Sinyal türüne göre mesaj oluştur
        if signal == "buy":
            signal_text = "ALIŞ"
            severity = AlertSeverity.ALERT
        elif signal == "sell":
            signal_text = "SATIŞ"
            severity = AlertSeverity.ALERT
        else:
            signal_text = "NÖTR"
            severity = AlertSeverity.INFO
        
        title = f"Teknik Sinyal: {asset}"
        message = f"{asset} için {indicator} indikatörü {signal_text} sinyali verdi. Değer: {value:.4f}"
        
        alert = Alert(
            id=alert_id,
            type=AlertType.TECHNICAL,
            severity=severity,
            title=title,
            message=message,
            asset=asset,
            timestamp=datetime.now(),
            data={
                "indicator": indicator,
                "signal": signal,
                "signal_text": signal_text,
                "value": value,
                "additional_info": additional_info or {}
            },
            expires_at=datetime.now() + timedelta(hours=4)
        )
        
        self.alerts.append(alert)
        self._process_alert(alert)
        
        return alert
    
    def _process_alert(self, alert: Alert):
        """Uyarıyı işle"""
        # Uyarı kurallarını kontrol et
        matching_rules = self._find_matching_rules(alert)
        
        for rule in matching_rules:
            self._execute_rule_actions(rule, alert)
        
        # Bildirim gönder
        if self.notification_callback:
            try:
                self.notification_callback(alert)
            except Exception as e:
                print(f"Bildirim hatası: {e}")
        
        # Uyarıyı geçmişe ekle
        self.alert_history.append(alert)
    
    def _find_matching_rules(self, alert: Alert) -> List[AlertRule]:
        """Uyarıya uygun kuralları bul"""
        matching_rules = []
        
        for rule in self.alert_rules:
            if not rule.is_active:
                continue
                
            if rule.type != alert.type:
                continue
            
            # Kural koşullarını kontrol et
            if self._check_rule_conditions(rule, alert):
                matching_rules.append(rule)
        
        # Önceliğe göre sırala
        matching_rules.sort(key=lambda x: x.priority, reverse=True)
        
        return matching_rules
    
    def _check_rule_conditions(self, rule: AlertRule, alert: Alert) -> bool:
        """Kural koşullarını kontrol et"""
        conditions = rule.conditions
        
        if rule.type == AlertType.PRICE:
            # Fiyat koşulları
            if "price_change_pct" in conditions:
                if alert.data.get("price_change_pct", 0) < conditions["price_change_pct"]:
                    return False
            
            if "volume_increase" in conditions:
                # Volume kontrolü (basit yaklaşım)
                pass
        
        elif rule.type == AlertType.PATTERN:
            # Formasyon koşulları
            if "pattern_types" in conditions:
                if alert.data.get("pattern_type") not in conditions["pattern_types"]:
                    return False
            
            if "confidence_threshold" in conditions:
                if alert.data.get("confidence", 0) < conditions["confidence_threshold"]:
                    return False
        
        elif rule.type == AlertType.RISK:
            # Risk koşulları
            if "var_threshold" in conditions:
                if alert.data.get("current_value", 0) < conditions["var_threshold"]:
                    return False
        
        elif rule.type == AlertType.NEWS:
            # Haber koşulları
            if "sentiment_threshold" in conditions:
                sentiment = abs(alert.data.get("sentiment_score", 0))
                if sentiment < conditions["sentiment_threshold"]:
                    return False
            
            if "impact_threshold" in conditions:
                if alert.data.get("impact_score", 0) < conditions["impact_threshold"]:
                    return False
        
        return True
    
    def _execute_rule_actions(self, rule: AlertRule, alert: Alert):
        """Kural aksiyonlarını çalıştır"""
        for action in rule.actions:
            if action == "notify":
                self._send_notification(alert)
            elif action == "log":
                self._log_alert(alert)
            elif action == "portfolio_check":
                self._check_portfolio_impact(alert)
            elif action == "risk_mitigation":
                self._suggest_risk_mitigation(alert)
            elif action == "sentiment_analysis":
                self._analyze_sentiment_impact(alert)
    
    def _send_notification(self, alert: Alert):
        """Bildirim gönder"""
        print(f"🔔 BİLDİRİM: {alert.title}")
        print(f"   {alert.message}")
        print(f"   Önem: {alert.severity.value}")
        print(f"   Zaman: {alert.timestamp.strftime('%H:%M:%S')}")
        print()
    
    def _log_alert(self, alert: Alert):
        """Uyarıyı logla"""
        log_entry = {
            "timestamp": alert.timestamp.isoformat(),
            "type": alert.type.value,
            "severity": alert.severity.value,
            "asset": alert.asset,
            "title": alert.title,
            "message": alert.message
        }
        # Gerçek uygulamada bu veritabanına yazılır
        print(f"📝 LOG: {alert.id} - {alert.type.value} - {alert.asset}")
    
    def _check_portfolio_impact(self, alert: Alert):
        """Portföy etkisini kontrol et"""
        # Basit portföy etki analizi
        print(f"📊 Portföy Etki Analizi: {alert.asset}")
    
    def _suggest_risk_mitigation(self, alert: Alert):
        """Risk azaltma önerisi"""
        if alert.type == AlertType.RISK:
            print(f"⚠️ Risk Azaltma Önerisi: {alert.asset}")
            print(f"   Önerilen Aksiyon: Pozisyon büyüklüğünü azalt")
    
    def _analyze_sentiment_impact(self, alert: Alert):
        """Sentiment etki analizi"""
        if alert.type == AlertType.NEWS:
            sentiment = alert.data.get("sentiment_score", 0)
            impact = alert.data.get("impact_score", 0)
            print(f"📰 Sentiment Analizi: {alert.asset}")
            print(f"   Sentiment: {sentiment:.3f}, Etki: {impact:.3f}")
    
    def get_active_alerts(self, asset: Optional[str] = None,
                         alert_type: Optional[AlertType] = None,
                         severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Aktif uyarıları getir"""
        filtered_alerts = [alert for alert in self.alerts if alert.is_active]
        
        if asset:
            filtered_alerts = [a for a in filtered_alerts if a.asset == asset]
        
        if alert_type:
            filtered_alerts = [a for a in filtered_alerts if a.type == alert_type]
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
        
        return filtered_alerts
    
    def mark_alert_as_read(self, alert_id: str):
        """Uyarıyı okundu olarak işaretle"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.is_read = True
                break
    
    def deactivate_alert(self, alert_id: str):
        """Uyarıyı deaktif et"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.is_active = False
                break
    
    def cleanup_expired_alerts(self):
        """Süresi dolmuş uyarıları temizle"""
        current_time = datetime.now()
        expired_alerts = []
        
        for alert in self.alerts:
            if alert.expires_at and alert.expires_at < current_time:
                expired_alerts.append(alert.id)
        
        for alert_id in expired_alerts:
            self.deactivate_alert(alert_id)
        
        if expired_alerts:
            print(f"🧹 {len(expired_alerts)} süresi dolmuş uyarı temizlendi")
    
    def generate_alerts_summary(self) -> Dict:
        """Uyarı özeti oluştur"""
        active_alerts = [a for a in self.alerts if a.is_active]
        
        summary = {
            "total_active_alerts": len(active_alerts),
            "alerts_by_type": {},
            "alerts_by_severity": {},
            "alerts_by_asset": {},
            "recent_alerts": []
        }
        
        # Tür bazında grupla
        for alert_type in AlertType:
            summary["alerts_by_type"][alert_type.value] = len(
                [a for a in active_alerts if a.type == alert_type]
            )
        
        # Önem derecesi bazında grupla
        for severity in AlertSeverity:
            summary["alerts_by_severity"][severity.value] = len(
                [a for a in active_alerts if a.severity == severity]
            )
        
        # Varlık bazında grupla
        assets = set(a.asset for a in active_alerts)
        for asset in assets:
            summary["alerts_by_asset"][asset] = len(
                [a for a in active_alerts if a.asset == asset]
            )
        
        # Son uyarılar
        recent_alerts = sorted(active_alerts, key=lambda x: x.timestamp, reverse=True)[:5]
        summary["recent_alerts"] = [
            {
                "id": a.id,
                "title": a.title,
                "asset": a.asset,
                "severity": a.severity.value,
                "timestamp": a.timestamp.isoformat()
            }
            for a in recent_alerts
        ]
        
        return summary

# Test fonksiyonu
def test_smart_alerts():
    """Smart Alerts test fonksiyonu"""
    print("🧪 Smart Alerts Test Başlıyor...")
    
    # Smart Alerts başlat
    smart_alerts = SmartAlerts()
    
    # Fiyat uyarısı test
    print("\n💰 Fiyat Uyarısı Test:")
    price_alert = smart_alerts.create_price_alert(
        asset="SISE.IS",
        price=45.80,
        alert_type="breakout",
        threshold=5.0
    )
    print(f"   Oluşturulan uyarı: {price_alert.title}")
    
    # Formasyon uyarısı test
    print("\n📊 Formasyon Uyarısı Test:")
    pattern_alert = smart_alerts.create_pattern_alert(
        asset="EREGL.IS",
        pattern_type="golden_cross",
        confidence=0.85,
        price=32.45
    )
    print(f"   Oluşturulan uyarı: {pattern_alert.title}")
    
    # Haber uyarısı test
    print("\n📰 Haber Uyarısı Test:")
    news_alert = smart_alerts.create_news_alert(
        asset="TUPRS.IS",
        news_title="TUPRAS'ta yeni yatırım planı açıklandı",
        sentiment_score=0.7,
        impact_score=0.8,
        source="Bloomberg"
    )
    print(f"   Oluşturulan uyarı: {news_alert.title}")
    
    # Risk uyarısı test
    print("\n⚠️ Risk Uyarısı Test:")
    risk_alert = smart_alerts.create_risk_alert(
        asset="AKBNK.IS",
        risk_type="var_limit",
        current_value=0.06,
        threshold=0.05,
        portfolio_impact=0.12
    )
    print(f"   Oluşturulan uyarı: {risk_alert.title}")
    
    # Teknik uyarısı test
    print("\n🔧 Teknik Uyarısı Test:")
    technical_alert = smart_alerts.create_technical_alert(
        asset="GARAN.IS",
        indicator="RSI",
        signal="buy",
        value=25.5
    )
    print(f"   Oluşturulan uyarı: {technical_alert.title}")
    
    # Aktif uyarıları listele
    print("\n📋 Aktif Uyarılar:")
    active_alerts = smart_alerts.get_active_alerts()
    for alert in active_alerts:
        print(f"   {alert.severity.value.upper()}: {alert.asset} - {alert.title}")
    
    # Uyarı özeti
    print("\n📊 Uyarı Özeti:")
    summary = smart_alerts.generate_alerts_summary()
    print(f"   Toplam aktif uyarı: {summary['total_active_alerts']}")
    print(f"   Tür bazında: {summary['alerts_by_type']}")
    print(f"   Önem derecesi: {summary['alerts_by_severity']}")
    
    # Süresi dolmuş uyarıları temizle
    print("\n🧹 Uyarı Temizliği:")
    smart_alerts.cleanup_expired_alerts()
    
    print("\n✅ Smart Alerts Test Tamamlandı!")
    return smart_alerts

if __name__ == "__main__":
    test_smart_alerts()
