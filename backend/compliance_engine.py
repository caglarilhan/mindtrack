"""
Compliance Engine - Sprint 13: Advanced Risk Management & Compliance Engine

Bu modül, ticaret faaliyetlerinin düzenleyici gerekliliklere uygunluğunu sağlar,
trading kısıtlamalarını yönetir ve compliance monitoring yapar.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
import json
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ComplianceRule:
    """Compliance kural tanımı"""
    rule_id: str
    name: str
    description: str
    rule_type: str  # trading_limit, position_limit, time_restriction, etc.
    category: str  # regulatory, internal, risk_management
    parameters: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class ComplianceViolation:
    """Compliance ihlali kaydı"""
    violation_id: str
    rule_id: str
    symbol: str
    violation_type: str
    severity: str  # low, medium, high, critical
    description: str
    current_value: float
    limit_value: float
    timestamp: datetime
    status: str = "open"  # open, acknowledged, resolved, false_positive
    action_taken: str = ""
    resolved_at: Optional[datetime] = None

@dataclass
class TradingRestriction:
    """Trading kısıtlaması"""
    restriction_id: str
    symbol: str
    restriction_type: str  # halt, suspension, limit_up, limit_down
    reason: str
    start_time: datetime
    parameters: Dict[str, Any]
    end_time: Optional[datetime] = None
    is_active: bool = True

@dataclass
class ComplianceReport:
    """Compliance raporu"""
    report_id: str
    period: str
    start_date: datetime
    end_date: datetime
    total_violations: int
    critical_violations: int
    high_violations: int
    medium_violations: int
    low_violations: int
    compliance_score: float
    summary: str
    details: Dict[str, Any]
    generated_at: datetime = None

class ComplianceEngine:
    """Compliance Engine ana sınıfı"""
    
    def __init__(self):
        self.compliance_rules = {}
        self.violations = []
        self.trading_restrictions = {}
        self.compliance_reports = {}
        self.regulatory_limits = {}
        self.internal_policies = {}
        self.compliance_history = []
        
        # Varsayılan compliance kuralları
        self._add_default_rules()
        
        # Varsayılan trading kısıtlamaları
        self._add_default_restrictions()
        
        # Varsayılan düzenleyici limitler
        self._add_default_regulatory_limits()
    
    def _add_default_rules(self):
        """Varsayılan compliance kuralları ekle"""
        default_rules = [
            {
                "rule_id": "POSITION_SIZE_LIMIT",
                "name": "Pozisyon Büyüklüğü Limiti",
                "description": "Tek pozisyon için maksimum büyüklük",
                "rule_type": "position_limit",
                "category": "risk_management",
                "parameters": {
                    "max_position_size": 0.10,  # Portföyün %10'u
                    "max_sector_exposure": 0.25,  # Sektörün %25'i
                    "max_single_stock": 0.05  # Tek hisse %5'i
                }
            },
            {
                "rule_id": "TRADING_HOURS",
                "name": "Trading Saatleri",
                "description": "İzin verilen trading saatleri",
                "rule_type": "time_restriction",
                "category": "regulatory",
                "parameters": {
                    "start_time": "09:30",
                    "end_time": "18:00",
                    "timezone": "Europe/Istanbul"
                }
            },
            {
                "rule_id": "WASH_TRADING",
                "name": "Wash Trading Koruması",
                "description": "Aynı gün al-sat işlemleri kısıtlaması",
                "rule_type": "trading_pattern",
                "category": "regulatory",
                "parameters": {
                    "min_hold_time": 1,  # Gün
                    "max_daily_trades": 10,
                    "penalty_multiplier": 2.0
                }
            },
            {
                "rule_id": "INSIDER_TRADING",
                "name": "İçeriden Bilgi Ticareti",
                "description": "İçeriden bilgi ile trading kısıtlaması",
                "rule_type": "information_restriction",
                "category": "regulatory",
                "parameters": {
                    "restricted_symbols": [],
                    "restricted_periods": [],
                    "monitoring_enabled": True
                }
            },
            {
                "rule_id": "RISK_LIMITS",
                "name": "Risk Limitleri",
                "description": "Portföy risk limitleri",
                "rule_type": "risk_limit",
                "category": "risk_management",
                "parameters": {
                    "max_daily_loss": 0.05,  # Günlük maksimum %5 kayıp
                    "max_drawdown": 0.20,  # Maksimum %20 drawdown
                    "max_leverage": 1.0,  # Maksimum 1x kaldıraç
                    "max_correlation": 0.7  # Maksimum %70 korelasyon
                }
            }
        ]
        
        for rule_data in default_rules:
            rule = ComplianceRule(
                rule_id=rule_data["rule_id"],
                name=rule_data["name"],
                description=rule_data["description"],
                rule_type=rule_data["rule_type"],
                category=rule_data["category"],
                parameters=rule_data["parameters"],
                created_at=datetime.now()
            )
            self.compliance_rules[rule.rule_id] = rule
    
    def _add_default_restrictions(self):
        """Varsayılan trading kısıtlamaları ekle"""
        default_restrictions = [
            {
                "restriction_id": "MARKET_HALT",
                "symbol": "ALL",
                "restriction_type": "halt",
                "reason": "Piyasa durması",
                "start_time": datetime.now(),
                "parameters": {
                    "halt_reason": "market_volatility",
                    "expected_duration": 30  # dakika
                }
            }
        ]
        
        for restriction_data in default_restrictions:
            restriction = TradingRestriction(
                restriction_id=restriction_data["restriction_id"],
                symbol=restriction_data["symbol"],
                restriction_type=restriction_data["restriction_type"],
                reason=restriction_data["reason"],
                start_time=restriction_data["start_time"],
                parameters=restriction_data["parameters"]
            )
            self.trading_restrictions[restriction.restriction_id] = restriction
    
    def _add_default_regulatory_limits(self):
        """Varsayılan düzenleyici limitler ekle"""
        self.regulatory_limits = {
            "position_limits": {
                "max_single_position": 0.05,  # Tek pozisyon %5
                "max_sector_exposure": 0.30,  # Sektör %30
                "max_foreign_exposure": 0.40,  # Yabancı %40
            },
            "trading_limits": {
                "max_daily_turnover": 0.50,  # Günlük ciro %50
                "max_intraday_trades": 100,  # Günlük işlem sayısı
                "min_holding_period": 1,  # Minimum tutma süresi (gün)
            },
            "risk_limits": {
                "max_leverage": 1.0,  # Maksimum kaldıraç
                "max_drawdown": 0.25,  # Maksimum drawdown
                "max_var": 0.03,  # Maksimum VaR
            }
        }
    
    def add_compliance_rule(self, rule: ComplianceRule) -> bool:
        """Yeni compliance kuralı ekle"""
        try:
            if rule.rule_id in self.compliance_rules:
                logger.warning(f"Rule {rule.rule_id} already exists, updating...")
                rule.updated_at = datetime.now()
            else:
                rule.created_at = datetime.now()
            
            self.compliance_rules[rule.rule_id] = rule
            logger.info(f"Compliance rule added: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding compliance rule: {e}")
            return False
    
    def check_position_compliance(self, portfolio_data: Dict[str, Any]) -> List[ComplianceViolation]:
        """Pozisyon compliance kontrolü"""
        violations = []
        
        try:
            total_value = portfolio_data.get("total_value", 0)
            positions = portfolio_data.get("positions", {})
            
            # Pozisyon büyüklüğü kontrolü
            position_rule = self.compliance_rules.get("POSITION_SIZE_LIMIT")
            if position_rule and position_rule.is_active:
                max_position_size = position_rule.parameters.get("max_position_size", 0.10)
                max_sector_exposure = position_rule.parameters.get("max_sector_exposure", 0.25)
                
                sector_exposure = {}
                
                for symbol, position in positions.items():
                    position_value = position.get("current_value", 0)
                    sector = position.get("sector", "unknown")
                    
                    # Tek pozisyon limiti
                    if total_value > 0:
                        position_weight = position_value / total_value
                        if position_weight > max_position_size:
                            violation = ComplianceViolation(
                                violation_id=f"POS_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                rule_id="POSITION_SIZE_LIMIT",
                                symbol=symbol,
                                violation_type="position_size_exceeded",
                                severity="high",
                                description=f"Pozisyon büyüklüğü limiti aşıldı: {position_weight:.2%} > {max_position_size:.2%}",
                                current_value=position_weight,
                                limit_value=max_position_size,
                                timestamp=datetime.now()
                            )
                            violations.append(violation)
                    
                    # Sektör exposure hesaplama
                    if sector not in sector_exposure:
                        sector_exposure[sector] = 0
                    sector_exposure[sector] += position_value
                
                # Sektör exposure kontrolü
                for sector, exposure in sector_exposure.items():
                    if total_value > 0:
                        sector_weight = exposure / total_value
                        if sector_weight > max_sector_exposure:
                            violation = ComplianceViolation(
                                violation_id=f"SECTOR_{sector}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                rule_id="POSITION_SIZE_LIMIT",
                                symbol=sector,
                                violation_type="sector_exposure_exceeded",
                                severity="medium",
                                description=f"Sektör exposure limiti aşıldı: {sector_weight:.2%} > {max_sector_exposure:.2%}",
                                current_value=sector_weight,
                                limit_value=max_sector_exposure,
                                timestamp=datetime.now()
                            )
                            violations.append(violation)
            
            # Risk limitleri kontrolü
            risk_rule = self.compliance_rules.get("RISK_LIMITS")
            if risk_rule and risk_rule.is_active:
                max_daily_loss = risk_rule.parameters.get("max_daily_loss", 0.05)
                max_drawdown = risk_rule.parameters.get("max_drawdown", 0.20)
                
                daily_return = portfolio_data.get("daily_return_pct", 0)
                current_drawdown = portfolio_data.get("max_drawdown", 0)
                
                if abs(daily_return) > max_daily_loss:
                    violation = ComplianceViolation(
                        violation_id=f"DAILY_LOSS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        rule_id="RISK_LIMITS",
                        symbol="PORTFOLIO",
                        violation_type="daily_loss_exceeded",
                        severity="high",
                        description=f"Günlük kayıp limiti aşıldı: {abs(daily_return):.2%} > {max_daily_loss:.2%}",
                        current_value=abs(daily_return),
                        limit_value=max_daily_loss,
                        timestamp=datetime.now()
                    )
                    violations.append(violation)
                
                if current_drawdown > max_drawdown:
                    violation = ComplianceViolation(
                        violation_id=f"DRAWDOWN_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        rule_id="RISK_LIMITS",
                        symbol="PORTFOLIO",
                        violation_type="drawdown_exceeded",
                        severity="critical",
                        description=f"Drawdown limiti aşıldı: {current_drawdown:.2%} > {max_drawdown:.2%}",
                        current_value=current_drawdown,
                        limit_value=max_drawdown,
                        timestamp=datetime.now()
                    )
                    violations.append(violation)
        
        except Exception as e:
            logger.error(f"Error checking position compliance: {e}")
        
        return violations
    
    def check_trading_compliance(self, order_data: Dict[str, Any]) -> List[ComplianceViolation]:
        """Trading compliance kontrolü"""
        violations = []
        
        try:
            symbol = order_data.get("symbol", "")
            order_type = order_data.get("order_type", "")
            side = order_data.get("side", "")
            quantity = order_data.get("quantity", 0)
            price = order_data.get("price", 0)
            
            # Trading saatleri kontrolü
            trading_rule = self.compliance_rules.get("TRADING_HOURS")
            if trading_rule and trading_rule.is_active:
                current_time = datetime.now().time()
                start_time = datetime.strptime(trading_rule.parameters.get("start_time", "09:30"), "%H:%M").time()
                end_time = datetime.strptime(trading_rule.parameters.get("end_time", "18:00"), "%H:%M").time()
                
                if not (start_time <= current_time <= end_time):
                    violation = ComplianceViolation(
                        violation_id=f"TRADING_HOURS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        rule_id="TRADING_HOURS",
                        symbol=symbol,
                        violation_type="trading_hours_violation",
                        severity="medium",
                        description=f"Trading saatleri dışında işlem: {current_time}",
                        current_value=current_time.hour + current_time.minute/60,
                        limit_value=start_time.hour + start_time.minute/60,
                        timestamp=datetime.now()
                    )
                    violations.append(violation)
            
            # Wash trading kontrolü
            wash_rule = self.compliance_rules.get("WASH_TRADING")
            if wash_rule and wash_rule.is_active:
                # Bu kontrol için trading geçmişi gerekli
                # Şimdilik basit bir kontrol yapıyoruz
                pass
            
            # Trading kısıtlamaları kontrolü
            for restriction in self.trading_restrictions.values():
                if restriction.is_active:
                    if (restriction.symbol == "ALL" or restriction.symbol == symbol):
                        if restriction.restriction_type == "halt":
                            violation = ComplianceViolation(
                                violation_id=f"TRADING_HALT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                rule_id="TRADING_RESTRICTION",
                                symbol=symbol,
                                violation_type="trading_halt",
                                severity="critical",
                                description=f"Trading durduruldu: {restriction.reason}",
                                current_value=1,
                                limit_value=0,
                                timestamp=datetime.now()
                            )
                            violations.append(violation)
        
        except Exception as e:
            logger.error(f"Error checking trading compliance: {e}")
        
        return violations
    
    def add_trading_restriction(self, restriction: TradingRestriction) -> bool:
        """Trading kısıtlaması ekle"""
        try:
            self.trading_restrictions[restriction.restriction_id] = restriction
            logger.info(f"Trading restriction added: {restriction.symbol} - {restriction.restriction_type}")
            return True
        except Exception as e:
            logger.error(f"Error adding trading restriction: {e}")
            return False
    
    def remove_trading_restriction(self, restriction_id: str) -> bool:
        """Trading kısıtlaması kaldır"""
        try:
            if restriction_id in self.trading_restrictions:
                del self.trading_restrictions[restriction_id]
                logger.info(f"Trading restriction removed: {restriction_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing trading restriction: {e}")
            return False
    
    def get_active_restrictions(self, symbol: str = None) -> List[TradingRestriction]:
        """Aktif trading kısıtlamalarını getir"""
        active_restrictions = []
        
        for restriction in self.trading_restrictions.values():
            if restriction.is_active:
                if symbol is None or restriction.symbol == "ALL" or restriction.symbol == symbol:
                    active_restrictions.append(restriction)
        
        return active_restrictions
    
    def record_violation(self, violation: ComplianceViolation) -> bool:
        """Compliance ihlali kaydet"""
        try:
            self.violations.append(violation)
            self.compliance_history.append({
                "timestamp": datetime.now(),
                "action": "violation_recorded",
                "violation_id": violation.violation_id,
                "rule_id": violation.rule_id,
                "symbol": violation.symbol,
                "severity": violation.severity
            })
            
            logger.warning(f"Compliance violation recorded: {violation.violation_type} - {violation.symbol}")
            return True
        except Exception as e:
            logger.error(f"Error recording violation: {e}")
            return False
    
    def resolve_violation(self, violation_id: str, action_taken: str) -> bool:
        """Compliance ihlalini çöz"""
        try:
            for violation in self.violations:
                if violation.violation_id == violation_id:
                    violation.status = "resolved"
                    violation.action_taken = action_taken
                    violation.resolved_at = datetime.now()
                    
                    self.compliance_history.append({
                        "timestamp": datetime.now(),
                        "action": "violation_resolved",
                        "violation_id": violation_id,
                        "action_taken": action_taken
                    })
                    
                    logger.info(f"Violation resolved: {violation_id}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error resolving violation: {e}")
            return False
    
    def generate_compliance_report(self, start_date: datetime, end_date: datetime) -> ComplianceReport:
        """Compliance raporu oluştur"""
        try:
            period_violations = [
                v for v in self.violations
                if start_date <= v.timestamp <= end_date
            ]
            
            critical_violations = [v for v in period_violations if v.severity == "critical"]
            high_violations = [v for v in period_violations if v.severity == "high"]
            medium_violations = [v for v in period_violations if v.severity == "medium"]
            low_violations = [v for v in period_violations if v.severity == "low"]
            
            total_violations = len(period_violations)
            compliance_score = 100.0
            
            if total_violations > 0:
                # Basit compliance skoru hesaplama
                critical_weight = 0.4
                high_weight = 0.3
                medium_weight = 0.2
                low_weight = 0.1
                
                penalty = (
                    len(critical_violations) * critical_weight * 25 +
                    len(high_violations) * high_weight * 15 +
                    len(medium_violations) * medium_weight * 10 +
                    len(low_violations) * low_weight * 5
                )
                
                compliance_score = max(0, 100 - penalty)
            
            # Violation detayları
            violation_details = {}
            for violation in period_violations:
                rule_type = violation.rule_id
                if rule_type not in violation_details:
                    violation_details[rule_type] = []
                violation_details[rule_type].append({
                    "symbol": violation.symbol,
                    "type": violation.violation_type,
                    "severity": violation.severity,
                    "description": violation.description,
                    "timestamp": violation.timestamp.isoformat()
                })
            
            report = ComplianceReport(
                report_id=f"COMP_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}",
                period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                start_date=start_date,
                end_date=end_date,
                total_violations=total_violations,
                critical_violations=len(critical_violations),
                high_violations=len(high_violations),
                medium_violations=len(medium_violations),
                low_violations=len(low_violations),
                compliance_score=compliance_score,
                summary=f"Compliance score: {compliance_score:.1f}% with {total_violations} violations",
                details=violation_details,
                generated_at=datetime.now()
            )
            
            self.compliance_reports[report.report_id] = report
            logger.info(f"Compliance report generated: {report.report_id}")
            
            return report
        
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return None
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Compliance özeti getir"""
        try:
            open_violations = [v for v in self.violations if v.status == "open"]
            resolved_violations = [v for v in self.violations if v.status == "resolved"]
            
            active_rules = [r for r in self.compliance_rules.values() if r.is_active]
            active_restrictions = [r for r in self.trading_restrictions.values() if r.is_active]
            
            summary = {
                "total_rules": len(self.compliance_rules),
                "active_rules": len(active_rules),
                "total_violations": len(self.violations),
                "open_violations": len(open_violations),
                "resolved_violations": len(resolved_violations),
                "active_restrictions": len(active_restrictions),
                "total_reports": len(self.compliance_reports),
                "last_violation": None,
                "compliance_score": 100.0
            }
            
            if self.violations:
                summary["last_violation"] = max(v.timestamp for v in self.violations).isoformat()
            
            if open_violations:
                # Basit compliance skoru hesaplama
                critical_count = len([v for v in open_violations if v.severity == "critical"])
                high_count = len([v for v in open_violations if v.severity == "high"])
                medium_count = len([v for v in open_violations if v.severity == "medium"])
                low_count = len([v for v in open_violations if v.severity == "low"])
                
                penalty = critical_count * 25 + high_count * 15 + medium_count * 10 + low_count * 5
                summary["compliance_score"] = max(0, 100 - penalty)
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting compliance summary: {e}")
            return {}
    
    def export_compliance_data(self, format_type: str = "json") -> str:
        """Compliance verilerini export et"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "compliance_rules": [],
                "violations": [],
                "trading_restrictions": [],
                "compliance_reports": []
            }
            
            # Compliance kuralları
            for rule in self.compliance_rules.values():
                export_data["compliance_rules"].append({
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "description": rule.description,
                    "rule_type": rule.rule_type,
                    "category": rule.category,
                    "parameters": rule.parameters,
                    "is_active": rule.is_active,
                    "created_at": rule.created_at.isoformat() if rule.created_at else None,
                    "updated_at": rule.updated_at.isoformat() if rule.updated_at else None
                })
            
            # Violations
            for violation in self.violations:
                export_data["violations"].append({
                    "violation_id": violation.violation_id,
                    "rule_id": violation.rule_id,
                    "symbol": violation.symbol,
                    "violation_type": violation.violation_type,
                    "severity": violation.severity,
                    "description": violation.description,
                    "current_value": violation.current_value,
                    "limit_value": violation.limit_value,
                    "timestamp": violation.timestamp.isoformat(),
                    "status": violation.status,
                    "action_taken": violation.action_taken,
                    "resolved_at": violation.resolved_at.isoformat() if violation.resolved_at else None
                })
            
            # Trading kısıtlamaları
            for restriction in self.trading_restrictions.values():
                export_data["trading_restrictions"].append({
                    "restriction_id": restriction.restriction_id,
                    "symbol": restriction.symbol,
                    "restriction_type": restriction.restriction_type,
                    "reason": restriction.reason,
                    "start_time": restriction.start_time.isoformat(),
                    "end_time": restriction.end_time.isoformat() if restriction.end_time else None,
                    "parameters": restriction.parameters,
                    "is_active": restriction.is_active
                })
            
            # Compliance raporları
            for report in self.compliance_reports.values():
                export_data["compliance_reports"].append({
                    "report_id": report.report_id,
                    "period": report.period,
                    "start_date": report.start_date.isoformat(),
                    "end_date": report.end_date.isoformat(),
                    "total_violations": report.total_violations,
                    "critical_violations": report.critical_violations,
                    "high_violations": report.high_violations,
                    "medium_violations": report.medium_violations,
                    "low_violations": report.low_violations,
                    "compliance_score": report.compliance_score,
                    "summary": report.summary,
                    "details": report.details,
                    "generated_at": report.generated_at.isoformat() if report.generated_at else None
                })
            
            if format_type.lower() == "json":
                return json.dumps(export_data, indent=2, ensure_ascii=False)
            else:
                return str(export_data)
        
        except Exception as e:
            logger.error(f"Error exporting compliance data: {e}")
            return ""


def test_compliance_engine():
    """Compliance Engine test fonksiyonu"""
    print("\n🧪 Compliance Engine Test Başlıyor...")
    
    # Compliance Engine oluştur
    engine = ComplianceEngine()
    
    print("✅ Varsayılan compliance kuralları eklendi")
    print(f"📊 Toplam kural sayısı: {len(engine.compliance_rules)}")
    
    # Test verisi oluştur
    test_portfolio = {
        "total_value": 100000,
        "daily_return_pct": -0.06,  # %6 kayıp
        "max_drawdown": 0.22,  # %22 drawdown
        "positions": {
            "SISE.IS": {
                "current_value": 8000,
                "sector": "industrial"
            },
            "EREGL.IS": {
                "current_value": 12000,
                "sector": "industrial"
            },
            "TUPRS.IS": {
                "current_value": 15000,
                "sector": "energy"
            }
        }
    }
    
    test_order = {
        "symbol": "SISE.IS",
        "order_type": "market",
        "side": "buy",
        "quantity": 100,
        "price": 80.0
    }
    
    print("\n📊 Test Verisi Oluşturma:")
    print(f"   ✅ Test portföyü oluşturuldu: {test_portfolio['total_value']:,} TL")
    print(f"   📊 Günlük getiri: {test_portfolio['daily_return_pct']:.2%}")
    print(f"   📊 Max drawdown: {test_portfolio['max_drawdown']:.2%}")
    
    # Position compliance kontrolü
    print("\n📊 Position Compliance Kontrolü:")
    position_violations = engine.check_position_compliance(test_portfolio)
    print(f"   ✅ {len(position_violations)} ihlal tespit edildi")
    
    for violation in position_violations:
        print(f"     🚨 {violation.violation_type}: {violation.description}")
        print(f"        📊 Severity: {violation.severity}")
        print(f"        📊 Current: {violation.current_value:.2%}")
        print(f"        📊 Limit: {violation.limit_value:.2%}")
    
    # Trading compliance kontrolü
    print("\n📊 Trading Compliance Kontrolü:")
    trading_violations = engine.check_trading_compliance(test_order)
    print(f"   ✅ {len(trading_violations)} ihlal tespit edildi")
    
    for violation in trading_violations:
        print(f"     🚨 {violation.violation_type}: {violation.description}")
        print(f"        📊 Severity: {violation.severity}")
    
    # Violations kaydet
    print("\n📊 Violations Kaydetme:")
    for violation in position_violations + trading_violations:
        engine.record_violation(violation)
    
    print(f"   ✅ {len(engine.violations)} violation kaydedildi")
    
    # Trading kısıtlaması ekle
    print("\n📊 Trading Kısıtlaması Ekleme:")
    new_restriction = TradingRestriction(
        restriction_id="TEST_RESTRICTION",
        symbol="SISE.IS",
        restriction_type="limit_down",
        reason="Test kısıtlaması",
        start_time=datetime.now(),
        parameters={"limit_price": 75.0}
    )
    
    engine.add_trading_restriction(new_restriction)
    print(f"   ✅ Trading kısıtlaması eklendi: {new_restriction.symbol}")
    
    # Compliance raporu oluştur
    print("\n📊 Compliance Raporu Oluşturma:")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    report = engine.generate_compliance_report(start_date, end_date)
    if report:
        print(f"   ✅ Rapor oluşturuldu: {report.report_id}")
        print(f"   📊 Compliance Score: {report.compliance_score:.1f}%")
        print(f"   📊 Toplam ihlal: {report.total_violations}")
        print(f"   📊 Kritik ihlal: {report.critical_violations}")
        print(f"   📊 Yüksek ihlal: {report.high_violations}")
    
    # Compliance özeti
    print("\n📊 Compliance Özeti:")
    summary = engine.get_compliance_summary()
    print(f"   ✅ Compliance özeti alındı")
    print(f"   📊 Toplam kural: {summary['total_rules']}")
    print(f"   📊 Aktif kural: {summary['active_rules']}")
    print(f"   📊 Toplam ihlal: {summary['total_violations']}")
    print(f"   📊 Açık ihlal: {summary['open_violations']}")
    print(f"   📊 Compliance Score: {summary['compliance_score']:.1f}%")
    
    # Export test
    print("\n📊 Export Test:")
    export_data = engine.export_compliance_data("json")
    print(f"   ✅ Compliance verisi export edildi")
    print(f"   📊 Export boyutu: {len(export_data)} karakter")
    
    print("\n✅ Compliance Engine Test Tamamlandı!")


if __name__ == "__main__":
    test_compliance_engine()
