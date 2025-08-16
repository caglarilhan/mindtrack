"""
PRD v2.0 - BIST AI Smart Trader
Risk Management System Module

Risk yönetim sistemi:
- Risk assessment
- Position sizing
- Stop loss management
- Risk limits
- Portfolio protection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class RiskProfile:
    """Risk profili"""
    profile_id: str
    name: str
    risk_tolerance: str  # low, medium, high, aggressive
    max_portfolio_risk: float  # % cinsinden
    max_position_size: float  # % cinsinden
    max_drawdown: float  # % cinsinden
    target_volatility: float  # % cinsinden
    stop_loss_pct: float  # % cinsinden
    take_profit_pct: float  # % cinsinden
    max_correlation: float  # 0-1 arası
    created_at: datetime = None

@dataclass
class PositionRisk:
    """Pozisyon riski"""
    symbol: str
    current_value: float
    position_size: float  # % cinsinden
    risk_exposure: float  # % cinsinden
    stop_loss_price: float
    take_profit_price: float
    max_loss: float
    risk_reward_ratio: float
    correlation_risk: float
    sector_concentration: float
    timestamp: datetime = None

@dataclass
class RiskAlert:
    """Risk uyarısı"""
    alert_id: str
    type: str  # position_limit, correlation, drawdown, volatility
    severity: str  # low, medium, high, critical
    message: str
    symbol: Optional[str] = None
    current_value: Optional[float] = None
    threshold: Optional[float] = None
    recommendation: str = ""
    created_at: datetime = None
    status: str = "active"  # active, acknowledged, resolved

@dataclass
class RiskMetrics:
    """Risk metrikleri"""
    portfolio_var: float  # Portfolio Value at Risk
    portfolio_cvar: float  # Portfolio Conditional VaR
    concentration_risk: float  # Konsantrasyon riski
    sector_risk: float  # Sektör riski
    correlation_risk: float  # Korelasyon riski
    liquidity_risk: float  # Likidite riski
    market_risk: float  # Piyasa riski
    credit_risk: float  # Kredi riski
    operational_risk: float  # Operasyonel risk
    total_risk_score: float  # Toplam risk skoru (0-100)
    timestamp: datetime = None

class RiskManagementSystem:
    """
    Risk Yönetim Sistemi
    
    PRD v2.0 gereksinimleri:
    - Risk değerlendirmesi
    - Pozisyon boyutlandırma
    - Stop loss yönetimi
    - Risk limitleri
    - Portföy koruması
    """
    
    def __init__(self):
        """Risk Management System başlatıcı"""
        # Risk profilleri
        self.risk_profiles = {}
        
        # Risk limitleri
        self.risk_limits = {
            'max_total_risk': 0.20,  # %20
            'max_sector_concentration': 0.40,  # %40
            'max_single_position': 0.15,  # %15
            'max_correlation_threshold': 0.70,  # 0.70
            'min_risk_reward_ratio': 1.5,  # 1.5
            'max_drawdown_threshold': 0.15,  # %15
            'max_volatility_threshold': 0.25  # %25
        }
        
        # Risk uyarıları
        self.risk_alerts = []
        
        # Risk geçmişi
        self.risk_history = []
        
        # Varsayılan risk profillerini oluştur
        self._create_default_risk_profiles()
    
    def _create_default_risk_profiles(self):
        """Varsayılan risk profillerini oluştur"""
        profiles = {
            'conservative': RiskProfile(
                profile_id='conservative',
                name='Muhafazakar',
                risk_tolerance='low',
                max_portfolio_risk=0.10,
                max_position_size=0.05,
                max_drawdown=0.08,
                target_volatility=0.12,
                stop_loss_pct=0.05,
                take_profit_pct=0.15,
                max_correlation=0.50,
                created_at=datetime.now()
            ),
            'moderate': RiskProfile(
                profile_id='moderate',
                name='Orta',
                risk_tolerance='medium',
                max_portfolio_risk=0.15,
                max_position_size=0.08,
                max_drawdown=0.12,
                target_volatility=0.18,
                stop_loss_pct=0.08,
                take_profit_pct=0.20,
                max_correlation=0.60,
                created_at=datetime.now()
            ),
            'aggressive': RiskProfile(
                profile_id='aggressive',
                name='Agresif',
                risk_tolerance='high',
                max_portfolio_risk=0.25,
                max_position_size=0.12,
                max_drawdown=0.20,
                target_volatility=0.30,
                stop_loss_pct=0.12,
                take_profit_pct=0.30,
                max_correlation=0.75,
                created_at=datetime.now()
            )
        }
        
        self.risk_profiles.update(profiles)
        print("✅ Varsayılan risk profilleri oluşturuldu")
    
    def create_risk_profile(self, profile: RiskProfile) -> bool:
        """
        Risk profili oluştur
        
        Args:
            profile: Risk profili
            
        Returns:
            bool: Başarı durumu
        """
        try:
            if profile.profile_id in self.risk_profiles:
                print(f"⚠️ Risk profili zaten mevcut: {profile.profile_id}")
                return False
            
            self.risk_profiles[profile.profile_id] = profile
            print(f"✅ Risk profili oluşturuldu: {profile.name}")
            return True
            
        except Exception as e:
            print(f"❌ Risk profili oluşturma hatası: {str(e)}")
            return False
    
    def get_risk_profile(self, profile_id: str) -> Optional[RiskProfile]:
        """
        Risk profilini al
        
        Args:
            profile_id: Profil ID
            
        Returns:
            Optional[RiskProfile]: Risk profili
        """
        return self.risk_profiles.get(profile_id)
    
    def calculate_position_risk(self, symbol: str, current_price: float, 
                                quantity: float, portfolio_value: float,
                                purchase_price: float, sector: str = "",
                                market_data: Optional[Dict[str, Any]] = None) -> PositionRisk:
        """
        Pozisyon riskini hesapla
        
        Args:
            symbol: Sembol
            current_price: Mevcut fiyat
            quantity: Miktar
            portfolio_value: Portföy değeri
            purchase_price: Alış fiyatı
            sector: Sektör
            market_data: Piyasa verisi
            
        Returns:
            PositionRisk: Pozisyon riski
        """
        try:
            # Temel hesaplamalar
            current_value = current_price * quantity
            position_size = (current_value / portfolio_value) * 100
            
            # Risk maruziyeti
            risk_exposure = position_size
            
            # Stop loss ve take profit (varsayılan risk profili)
            default_profile = self.risk_profiles['moderate']
            stop_loss_pct = default_profile.stop_loss_pct
            take_profit_pct = default_profile.take_profit_pct
            
            stop_loss_price = purchase_price * (1 - stop_loss_pct)
            take_profit_price = purchase_price * (1 + take_profit_pct)
            
            # Maksimum kayıp
            max_loss = (stop_loss_price - purchase_price) * quantity
            
            # Risk-ödül oranı
            potential_gain = (take_profit_price - purchase_price) * quantity
            risk_reward_ratio = abs(potential_gain / max_loss) if max_loss != 0 else 0
            
            # Korelasyon riski (basit hesaplama)
            correlation_risk = 0.5  # Varsayılan değer
            
            # Sektör konsantrasyonu
            sector_concentration = position_size if sector else 0
            
            return PositionRisk(
                symbol=symbol,
                current_value=current_value,
                position_size=position_size,
                risk_exposure=risk_exposure,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                max_loss=max_loss,
                risk_reward_ratio=risk_reward_ratio,
                correlation_risk=correlation_risk,
                sector_concentration=sector_concentration,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"❌ Pozisyon riski hesaplama hatası: {str(e)}")
            return PositionRisk(
                symbol=symbol, current_value=0, position_size=0, risk_exposure=0,
                stop_loss_price=0, take_profit_price=0, max_loss=0, risk_reward_ratio=0,
                correlation_risk=0, sector_concentration=0
            )
    
    def assess_portfolio_risk(self, positions: List[PositionRisk], 
                              portfolio_value: float, risk_profile_id: str = 'moderate') -> RiskMetrics:
        """
        Portföy riskini değerlendir
        
        Args:
            positions: Pozisyon listesi
            portfolio_value: Portföy değeri
            risk_profile_id: Risk profili ID
            
        Returns:
            RiskMetrics: Risk metrikleri
        """
        try:
            if not positions:
                return RiskMetrics(
                    portfolio_var=0, portfolio_cvar=0, concentration_risk=0,
                    sector_risk=0, correlation_risk=0, liquidity_risk=0,
                    market_risk=0, credit_risk=0, operational_risk=0,
                    total_risk_score=0
                )
            
            # Portfolio VaR hesaplama (basit)
            total_exposure = sum(pos.risk_exposure for pos in positions)
            portfolio_var = total_exposure * 0.05  # %5 varsayılan
            
            # Portfolio CVaR
            portfolio_cvar = portfolio_var * 1.5  # Basit hesaplama
            
            # Konsantrasyon riski
            max_position = max(pos.position_size for pos in positions) if positions else 0
            concentration_risk = max_position / 100
            
            # Sektör riski
            sector_exposures = {}
            for pos in positions:
                # Sembol'den sektör çıkar (basit)
                sector = pos.symbol.split('.')[0] if '.' in pos.symbol else 'Unknown'
                if sector not in sector_exposures:
                    sector_exposures[sector] = 0
                sector_exposures[sector] += pos.position_size
            
            sector_risk = max(sector_exposures.values()) / 100 if sector_exposures else 0
            
            # Korelasyon riski
            correlation_risk = np.mean([pos.correlation_risk for pos in positions])
            
            # Likidite riski (basit)
            liquidity_risk = 0.3  # Varsayılan değer
            
            # Piyasa riski
            market_risk = portfolio_var / 100
            
            # Kredi riski (basit)
            credit_risk = 0.1  # Varsayılan değer
            
            # Operasyonel risk
            operational_risk = 0.05  # Varsayılan değer
            
            # Toplam risk skoru (0-100)
            risk_factors = [
                concentration_risk * 25,
                sector_risk * 20,
                correlation_risk * 15,
                market_risk * 20,
                liquidity_risk * 10,
                credit_risk * 5,
                operational_risk * 5
            ]
            
            total_risk_score = min(100, sum(risk_factors))
            
            return RiskMetrics(
                portfolio_var=portfolio_var,
                portfolio_cvar=portfolio_cvar,
                concentration_risk=concentration_risk,
                sector_risk=sector_risk,
                correlation_risk=correlation_risk,
                liquidity_risk=liquidity_risk,
                market_risk=market_risk,
                credit_risk=credit_risk,
                operational_risk=operational_risk,
                total_risk_score=total_risk_score,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"❌ Portföy riski değerlendirme hatası: {str(e)}")
            return RiskMetrics(
                portfolio_var=0, portfolio_cvar=0, concentration_risk=0,
                sector_risk=0, correlation_risk=0, liquidity_risk=0,
                market_risk=0, credit_risk=0, operational_risk=0,
                total_risk_score=0
            )
    
    def check_risk_limits(self, positions: List[PositionRisk], 
                           portfolio_value: float, risk_profile_id: str = 'moderate') -> List[RiskAlert]:
        """
        Risk limitlerini kontrol et
        
        Args:
            positions: Pozisyon listesi
            portfolio_value: Portföy değeri
            risk_profile_id: Risk profili ID
            
        Returns:
            List[RiskAlert]: Risk uyarıları
        """
        try:
            alerts = []
            risk_profile = self.risk_profiles.get(risk_profile_id)
            
            if not risk_profile:
                return alerts
            
            # Pozisyon boyutu kontrolü
            for pos in positions:
                if pos.position_size > risk_profile.max_position_size * 100:
                    alert = RiskAlert(
                        alert_id=f"position_limit_{pos.symbol}",
                        type="position_limit",
                        severity="high" if pos.position_size > risk_profile.max_position_size * 150 else "medium",
                        message=f"Pozisyon boyutu limiti aşıldı: {pos.symbol}",
                        symbol=pos.symbol,
                        current_value=pos.position_size,
                        threshold=risk_profile.max_position_size * 100,
                        recommendation="Pozisyon boyutunu azaltın",
                        created_at=datetime.now()
                    )
                    alerts.append(alert)
                
                # Risk-ödül oranı kontrolü
                if pos.risk_reward_ratio < self.risk_limits['min_risk_reward_ratio']:
                    alert = RiskAlert(
                        alert_id=f"risk_reward_{pos.symbol}",
                        type="risk_reward",
                        severity="medium",
                        message=f"Risk-ödül oranı düşük: {pos.symbol}",
                        symbol=pos.symbol,
                        current_value=pos.risk_reward_ratio,
                        threshold=self.risk_limits['min_risk_reward_ratio'],
                        recommendation="Stop loss veya take profit seviyelerini ayarlayın",
                        created_at=datetime.now()
                    )
                    alerts.append(alert)
            
            # Sektör konsantrasyon kontrolü
            sector_exposures = {}
            for pos in positions:
                sector = pos.symbol.split('.')[0] if '.' in pos.symbol else 'Unknown'
                if sector not in sector_exposures:
                    sector_exposures[sector] = 0
                sector_exposures[sector] += pos.position_size
            
            for sector, exposure in sector_exposures.items():
                if exposure > self.risk_limits['max_sector_concentration'] * 100:
                    alert = RiskAlert(
                        alert_id=f"sector_concentration_{sector}",
                        type="sector_concentration",
                        severity="high",
                        message=f"Sektör konsantrasyonu yüksek: {sector}",
                        symbol=sector,
                        current_value=exposure,
                        threshold=self.risk_limits['max_sector_concentration'] * 100,
                        recommendation="Sektör çeşitlendirmesi yapın",
                        created_at=datetime.now()
                    )
                    alerts.append(alert)
            
            # Toplam risk kontrolü
            total_exposure = sum(pos.risk_exposure for pos in positions)
            if total_exposure > risk_profile.max_portfolio_risk * 100:
                alert = RiskAlert(
                    alert_id="total_portfolio_risk",
                    type="total_portfolio_risk",
                    severity="critical",
                    message="Toplam portföy riski limiti aşıldı",
                    current_value=total_exposure,
                    threshold=risk_profile.max_portfolio_risk * 100,
                    recommendation="Genel risk maruziyetini azaltın",
                    created_at=datetime.now()
                )
                alerts.append(alert)
            
            # Uyarıları kaydet
            self.risk_alerts.extend(alerts)
            
            return alerts
            
        except Exception as e:
            print(f"❌ Risk limitleri kontrol hatası: {str(e)}")
            return []
    
    def calculate_position_size(self, available_capital: float, risk_per_trade: float,
                                stop_loss_pct: float, risk_profile_id: str = 'moderate') -> Dict[str, Any]:
        """
        Pozisyon boyutunu hesapla
        
        Args:
            available_capital: Mevcut sermaye
            risk_per_trade: İşlem başına risk
            stop_loss_pct: Stop loss yüzdesi
            risk_profile_id: Risk profili ID
            
        Returns:
            Dict[str, Any]: Pozisyon boyutu bilgileri
        """
        try:
            risk_profile = self.risk_profiles.get(risk_profile_id)
            if not risk_profile:
                return {'error': 'Risk profili bulunamadı'}
            
            # Risk bazlı pozisyon boyutlandırma
            max_risk_amount = available_capital * (risk_per_trade / 100)
            
            # Stop loss bazlı pozisyon boyutu
            if stop_loss_pct > 0:
                position_size = max_risk_amount / (stop_loss_pct / 100)
            else:
                position_size = available_capital * (risk_profile.max_position_size / 100)
            
            # Risk profili limitlerini kontrol et
            max_position_size = available_capital * (risk_profile.max_position_size / 100)
            position_size = min(position_size, max_position_size)
            
            # Risk-ödül oranı
            risk_reward_ratio = risk_profile.take_profit_pct / stop_loss_pct if stop_loss_pct > 0 else 0
            
            return {
                'position_size': position_size,
                'risk_amount': max_risk_amount,
                'risk_percentage': risk_per_trade,
                'stop_loss_pct': stop_loss_pct,
                'risk_reward_ratio': risk_reward_ratio,
                'max_allowed_size': max_position_size,
                'recommendation': 'Pozisyon boyutu hesaplandı'
            }
            
        except Exception as e:
            print(f"❌ Pozisyon boyutu hesaplama hatası: {str(e)}")
            return {'error': str(e)}
    
    def get_risk_alerts(self, status: Optional[str] = None, 
                         severity: Optional[str] = None) -> List[RiskAlert]:
        """
        Risk uyarılarını al
        
        Args:
            status: Uyarı durumu
            severity: Uyarı şiddeti
            
        Returns:
            List[RiskAlert]: Risk uyarıları
        """
        alerts = self.risk_alerts
        
        if status:
            alerts = [alert for alert in alerts if alert.status == status]
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        return alerts
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Uyarıyı onayla
        
        Args:
            alert_id: Uyarı ID
            
        Returns:
            bool: Başarı durumu
        """
        try:
            for alert in self.risk_alerts:
                if alert.alert_id == alert_id:
                    alert.status = "acknowledged"
                    print(f"✅ Uyarı onaylandı: {alert_id}")
                    return True
            
            print(f"❌ Uyarı bulunamadı: {alert_id}")
            return False
            
        except Exception as e:
            print(f"❌ Uyarı onaylama hatası: {str(e)}")
            return False
    
    def resolve_alert(self, alert_id: str, resolution_note: str = "") -> bool:
        """
        Uyarıyı çöz
        
        Args:
            alert_id: Uyarı ID
            resolution_note: Çözüm notu
            
        Returns:
            bool: Başarı durumu
        """
        try:
            for alert in self.risk_alerts:
                if alert.alert_id == alert_id:
                    alert.status = "resolved"
                    if resolution_note:
                        alert.recommendation += f" [Çözüm: {resolution_note}]"
                    print(f"✅ Uyarı çözüldü: {alert_id}")
                    return True
            
            print(f"❌ Uyarı bulunamadı: {alert_id}")
            return False
            
        except Exception as e:
            print(f"❌ Uyarı çözme hatası: {str(e)}")
            return False
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Risk özetini al"""
        try:
            active_alerts = [alert for alert in self.risk_alerts if alert.status == "active"]
            
            summary = {
                'total_alerts': len(self.risk_alerts),
                'active_alerts': len(active_alerts),
                'acknowledged_alerts': len([alert for alert in self.risk_alerts if alert.status == "acknowledged"]),
                'resolved_alerts': len([alert for alert in self.risk_alerts if alert.status == "resolved"]),
                'alerts_by_severity': {},
                'alerts_by_type': {},
                'risk_profiles': list(self.risk_profiles.keys()),
                'risk_limits': self.risk_limits
            }
            
            # Şiddet bazında uyarı sayısı
            for alert in self.risk_alerts:
                if alert.severity not in summary['alerts_by_severity']:
                    summary['alerts_by_severity'][alert.severity] = 0
                summary['alerts_by_severity'][alert.severity] += 1
                
                if alert.type not in summary['alerts_by_type']:
                    summary['alerts_by_type'][alert.type] = 0
                summary['alerts_by_type'][alert.type] += 1
            
            return summary
            
        except Exception as e:
            print(f"❌ Risk özeti alma hatası: {str(e)}")
            return {'error': str(e)}

# Test fonksiyonu
def test_risk_management_system():
    """Risk Management System test fonksiyonu"""
    print("🧪 Risk Management System Test Başlıyor...")
    
    # Risk Management System başlat
    risk_system = RiskManagementSystem()
    
    # Risk profilleri test
    print("\n👤 Risk Profilleri Test:")
    profiles = risk_system.risk_profiles
    print(f"   ✅ {len(profiles)} risk profili mevcut")
    for profile_id, profile in profiles.items():
        print(f"     {profile.name}: Risk toleransı {profile.risk_tolerance}")
    
    # Yeni risk profili oluştur test
    print("\n🏗️ Yeni Risk Profili Test:")
    custom_profile = RiskProfile(
        profile_id='custom',
        name='Özel Profil',
        risk_tolerance='medium',
        max_portfolio_risk=0.18,
        max_position_size=0.10,
        max_drawdown=0.15,
        target_volatility=0.20,
        stop_loss_pct=0.10,
        take_profit_pct=0.25,
        max_correlation=0.65
    )
    
    profile_created = risk_system.create_risk_profile(custom_profile)
    print(f"   Yeni risk profili oluşturuldu: {profile_created}")
    
    # Pozisyon riski hesaplama test
    print("\n📊 Pozisyon Risk Hesaplama Test:")
    position_risk = risk_system.calculate_position_risk(
        symbol="SISE.IS",
        current_price=45.50,
        quantity=1000,
        portfolio_value=1000000,
        purchase_price=42.00,
        sector="INDUSTRIAL"
    )
    
    print(f"   ✅ Pozisyon riski hesaplandı: {position_risk.symbol}")
    print(f"   📊 Pozisyon boyutu: {position_risk.position_size:.2f}%")
    print(f"   ⚠️ Risk maruziyeti: {position_risk.risk_exposure:.2f}%")
    print(f"   🛑 Stop loss: {position_risk.stop_loss_price:.2f}")
    print(f"   🎯 Take profit: {position_risk.take_profit_price:.2f}")
    print(f"   📈 Risk-ödül oranı: {position_risk.risk_reward_ratio:.2f}")
    
    # Portföy riski değerlendirme test
    print("\n🔍 Portföy Risk Değerlendirme Test:")
    positions = [position_risk]
    
    # İkinci pozisyon ekle
    position_risk2 = risk_system.calculate_position_risk(
        symbol="EREGL.IS",
        current_price=28.75,
        quantity=500,
        portfolio_value=1000000,
        purchase_price=30.00,
        sector="INDUSTRIAL"
    )
    positions.append(position_risk2)
    
    portfolio_risk = risk_system.assess_portfolio_risk(positions, 1000000, 'moderate')
    print(f"   ✅ Portföy riski değerlendirildi")
    print(f"   📊 Portfolio VaR: {portfolio_risk.portfolio_var:.2f}%")
    print(f"   📊 Portfolio CVaR: {portfolio_risk.portfolio_cvar:.2f}%")
    print(f"   ⚠️ Konsantrasyon riski: {portfolio_risk.concentration_risk:.3f}")
    print(f"   🏭 Sektör riski: {portfolio_risk.sector_risk:.3f}")
    print(f"   📊 Toplam risk skoru: {portfolio_risk.total_risk_score:.1f}/100")
    
    # Risk limitleri kontrol test
    print("\n⚠️ Risk Limitleri Kontrol Test:")
    alerts = risk_system.check_risk_limits(positions, 1000000, 'moderate')
    print(f"   ✅ {len(alerts)} risk uyarısı tespit edildi")
    
    for alert in alerts:
        print(f"     {alert.type}: {alert.message} (Şiddet: {alert.severity})")
    
    # Pozisyon boyutu hesaplama test
    print("\n📏 Pozisyon Boyutu Hesaplama Test:")
    position_size_result = risk_system.calculate_position_size(
        available_capital=100000,
        risk_per_trade=2.0,
        stop_loss_pct=8.0,
        risk_profile_id='moderate'
    )
    
    if 'error' not in position_size_result:
        print(f"   ✅ Pozisyon boyutu hesaplandı")
        print(f"   📊 Önerilen boyut: {position_size_result['position_size']:,.2f} TL")
        print(f"   ⚠️ Risk miktarı: {position_size_result['risk_amount']:,.2f} TL")
        print(f"   📈 Risk-ödül oranı: {position_size_result['risk_reward_ratio']:.2f}")
    
    # Risk uyarıları test
    print("\n🚨 Risk Uyarıları Test:")
    active_alerts = risk_system.get_risk_alerts(status="active")
    print(f"   ✅ Aktif uyarılar: {len(active_alerts)}")
    
    # Uyarı onaylama test
    if active_alerts:
        first_alert = active_alerts[0]
        alert_acknowledged = risk_system.acknowledge_alert(first_alert.alert_id)
        print(f"   Uyarı onaylandı: {alert_acknowledged}")
    
    # Risk özeti test
    print("\n📋 Risk Özeti Test:")
    risk_summary = risk_system.get_risk_summary()
    if 'error' not in risk_summary:
        print(f"   ✅ Risk özeti alındı")
        print(f"   📊 Toplam uyarı: {risk_summary['total_alerts']}")
        print(f"   🚨 Aktif uyarı: {risk_summary['active_alerts']}")
        print(f"   ✅ Çözülen uyarı: {risk_summary['resolved_alerts']}")
        print(f"   👤 Risk profilleri: {len(risk_summary['risk_profiles'])}")
    
    print("\n✅ Risk Management System Test Tamamlandı!")
    
    return risk_system

if __name__ == "__main__":
    test_risk_management_system()
