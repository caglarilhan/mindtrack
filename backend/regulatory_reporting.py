"""
Regulatory Reporting - Sprint 13: Advanced Risk Management & Compliance Engine

Bu modül, düzenleyici raporlama gereksinimlerini karşılar, veri toplama yapar
ve compliance amaçlı raporlar üretir.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
import json
import logging
import csv
from pathlib import Path

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RegulatoryReport:
    """Düzenleyici rapor tanımı"""
    report_id: str
    report_type: str  # daily, weekly, monthly, quarterly, annual
    period: str
    start_date: datetime
    end_date: datetime
    status: str  # draft, submitted, approved, rejected
    submission_date: Optional[datetime] = None
    approval_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    data_sources: List[str] = None
    generated_at: datetime = None

@dataclass
class ReportData:
    """Rapor verisi"""
    data_id: str
    report_id: str
    data_type: str  # portfolio, trading, risk, compliance
    data_source: str
    data_content: Dict[str, Any]
    data_quality_score: float
    validation_status: str  # valid, warning, error
    validation_errors: List[str] = None
    timestamp: datetime = None

@dataclass
class RegulatoryRequirement:
    """Düzenleyici gereksinim"""
    requirement_id: str
    name: str
    description: str
    regulator: str  # SPK, BDDK, TCMB, etc.
    report_type: str
    frequency: str  # daily, weekly, monthly, quarterly, annual
    deadline_days: int  # Rapor döneminden kaç gün sonra
    required_fields: List[str]
    validation_rules: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = None

@dataclass
class ReportSubmission:
    """Rapor gönderimi"""
    submission_id: str
    report_id: str
    regulator: str
    submission_method: str  # electronic, manual, api
    submission_status: str  # pending, submitted, confirmed, failed
    submission_timestamp: datetime
    confirmation_reference: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0

class RegulatoryReporting:
    """Regulatory Reporting ana sınıfı"""
    
    def __init__(self):
        self.regulatory_reports = {}
        self.report_data = {}
        self.regulatory_requirements = {}
        self.report_submissions = {}
        self.data_sources = {}
        self.validation_rules = {}
        self.report_templates = {}
        
        # Varsayılan düzenleyici gereksinimleri
        self._add_default_requirements()
        
        # Varsayılan rapor şablonları
        self._add_default_templates()
        
        # Varsayılan validation kuralları
        self._add_default_validation_rules()
    
    def _add_default_requirements(self):
        """Varsayılan düzenleyici gereksinimleri ekle"""
        default_requirements = [
            {
                "requirement_id": "SPK_DAILY_PORTFOLIO",
                "name": "SPK Günlük Portföy Raporu",
                "description": "Günlük portföy pozisyonları ve değerleri",
                "regulator": "SPK",
                "report_type": "portfolio",
                "frequency": "daily",
                "deadline_days": 1,
                "required_fields": [
                    "portfolio_value", "total_positions", "cash_balance",
                    "margin_used", "unrealized_pnl", "realized_pnl"
                ],
                "validation_rules": {
                    "portfolio_value": {"min": 0, "max": 1000000000},
                    "total_positions": {"min": 0, "max": 1000},
                    "cash_balance": {"min": -1000000, "max": 100000000}
                }
            },
            {
                "requirement_id": "SPK_WEEKLY_TRADING",
                "name": "SPK Haftalık Trading Raporu",
                "description": "Haftalık trading aktiviteleri ve işlem detayları",
                "regulator": "SPK",
                "report_type": "trading",
                "frequency": "weekly",
                "deadline_days": 3,
                "required_fields": [
                    "total_trades", "total_volume", "total_commission",
                    "winning_trades", "losing_trades", "avg_trade_size"
                ],
                "validation_rules": {
                    "total_trades": {"min": 0, "max": 10000},
                    "total_volume": {"min": 0, "max": 1000000000},
                    "total_commission": {"min": 0, "max": 1000000}
                }
            },
            {
                "requirement_id": "BDDK_RISK_METRICS",
                "name": "BDDK Risk Metrikleri Raporu",
                "description": "Aylık risk metrikleri ve limitler",
                "regulator": "BDDK",
                "report_type": "risk",
                "frequency": "monthly",
                "deadline_days": 15,
                "required_fields": [
                    "var_95", "var_99", "max_drawdown", "volatility",
                    "sharpe_ratio", "beta", "correlation_matrix"
                ],
                "validation_rules": {
                    "var_95": {"min": 0, "max": 0.5},
                    "var_99": {"min": 0, "max": 0.7},
                    "max_drawdown": {"min": 0, "max": 1.0}
                }
            },
            {
                "requirement_id": "TCMB_FOREIGN_EXPOSURE",
                "name": "TCMB Yabancı Exposure Raporu",
                "description": "Çeyreklik yabancı para ve varlık exposure'ı",
                "regulator": "TCMB",
                "report_type": "exposure",
                "frequency": "quarterly",
                "deadline_days": 30,
                "required_fields": [
                    "total_foreign_exposure", "currency_breakdown",
                    "hedging_ratio", "exchange_rate_risk"
                ],
                "validation_rules": {
                    "total_foreign_exposure": {"min": 0, "max": 1000000000},
                    "hedging_ratio": {"min": 0, "max": 1.0}
                }
            }
        ]
        
        for req_data in default_requirements:
            requirement = RegulatoryRequirement(
                requirement_id=req_data["requirement_id"],
                name=req_data["name"],
                description=req_data["description"],
                regulator=req_data["regulator"],
                report_type=req_data["report_type"],
                frequency=req_data["frequency"],
                deadline_days=req_data["deadline_days"],
                required_fields=req_data["required_fields"],
                validation_rules=req_data["validation_rules"],
                created_at=datetime.now()
            )
            self.regulatory_requirements[requirement.requirement_id] = requirement
    
    def _add_default_templates(self):
        """Varsayılan rapor şablonları ekle"""
        self.report_templates = {
            "portfolio": {
                "header": ["Tarih", "Portföy Değeri", "Nakit", "Pozisyonlar", "Margin", "P&L"],
                "format": "table",
                "style": "financial"
            },
            "trading": {
                "header": ["Tarih", "İşlem Sayısı", "Hacim", "Komisyon", "Kazanan", "Kaybeden"],
                "format": "table",
                "style": "trading"
            },
            "risk": {
                "header": ["Metrik", "Değer", "Limit", "Durum"],
                "format": "key_value",
                "style": "risk"
            },
            "exposure": {
                "header": ["Varlık Türü", "Tutar", "Para Birimi", "Risk"],
                "format": "table",
                "style": "exposure"
            }
        }
    
    def _add_default_validation_rules(self):
        """Varsayılan validation kuralları ekle"""
        self.validation_rules = {
            "data_completeness": {
                "required_fields_present": True,
                "no_null_values": True,
                "data_format_valid": True
            },
            "data_consistency": {
                "cross_field_validation": True,
                "business_logic_check": True,
                "historical_comparison": True
            },
            "data_quality": {
                "outlier_detection": True,
                "range_validation": True,
                "pattern_recognition": True
            }
        }
    
    def create_regulatory_report(self, report_type: str, start_date: datetime, end_date: datetime) -> RegulatoryReport:
        """Yeni düzenleyici rapor oluştur"""
        try:
            period = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            report_id = f"REG_{report_type.upper()}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
            
            report = RegulatoryReport(
                report_id=report_id,
                report_type=report_type,
                period=period,
                start_date=start_date,
                end_date=end_date,
                status="draft",
                data_sources=[],
                generated_at=datetime.now()
            )
            
            self.regulatory_reports[report.report_id] = report
            logger.info(f"Regulatory report created: {report_id}")
            
            return report
        
        except Exception as e:
            logger.error(f"Error creating regulatory report: {e}")
            return None
    
    def add_report_data(self, report_id: str, data_type: str, data_source: str, data_content: Dict[str, Any]) -> bool:
        """Rapor verisi ekle"""
        try:
            if report_id not in self.regulatory_reports:
                logger.error(f"Report {report_id} not found")
                return False
            
            data_id = f"DATA_{data_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Veri kalitesi skoru hesapla
            data_quality_score = self._calculate_data_quality_score(data_content)
            
            # Validation yap
            validation_status, validation_errors = self._validate_data(data_type, data_content)
            
            report_data = ReportData(
                data_id=data_id,
                report_id=report_id,
                data_type=data_type,
                data_source=data_source,
                data_content=data_content,
                data_quality_score=data_quality_score,
                validation_status=validation_status,
                validation_errors=validation_errors,
                timestamp=datetime.now()
            )
            
            if report_id not in self.report_data:
                self.report_data[report_id] = []
            
            self.report_data[report_id].append(report_data)
            
            # Rapor veri kaynaklarını güncelle
            if data_source not in self.regulatory_reports[report_id].data_sources:
                self.regulatory_reports[report_id].data_sources.append(data_source)
            
            logger.info(f"Report data added: {data_id} to {report_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error adding report data: {e}")
            return False
    
    def _calculate_data_quality_score(self, data_content: Dict[str, Any]) -> float:
        """Veri kalitesi skoru hesapla"""
        try:
            score = 100.0
            
            # Null değer kontrolü
            null_count = sum(1 for v in data_content.values() if v is None)
            total_fields = len(data_content)
            
            if total_fields > 0:
                null_penalty = (null_count / total_fields) * 30
                score -= null_penalty
            
            # Veri tipi kontrolü
            type_errors = 0
            for key, value in data_content.items():
                if isinstance(value, (int, float)) and value < 0:
                    if key not in ['pnl', 'return', 'drawdown']:  # Negatif olabilir
                        type_errors += 1
            
            type_penalty = (type_errors / total_fields) * 20 if total_fields > 0 else 0
            score -= type_penalty
            
            return max(0, score)
        
        except Exception as e:
            logger.error(f"Error calculating data quality score: {e}")
            return 0.0
    
    def _validate_data(self, data_type: str, data_content: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Veri validation yap"""
        try:
            errors = []
            status = "valid"
            
            # Gerekli alanlar kontrolü
            if data_type in self.report_templates:
                required_fields = self.report_templates[data_type].get("header", [])
                missing_fields = [field for field in required_fields if field not in data_content]
                
                if missing_fields:
                    errors.append(f"Missing required fields: {missing_fields}")
                    status = "error"
            
            # Veri format kontrolü
            for key, value in data_content.items():
                if isinstance(value, str) and len(value) > 1000:
                    errors.append(f"Field {key} value too long")
                    status = "warning"
                
                if isinstance(value, (int, float)) and abs(value) > 1e12:
                    errors.append(f"Field {key} value out of reasonable range")
                    status = "warning"
            
            # Business logic kontrolü
            if data_type == "portfolio":
                if "portfolio_value" in data_content and "cash_balance" in data_content:
                    portfolio_value = data_content["portfolio_value"]
                    cash_balance = data_content["cash_balance"]
                    
                    if portfolio_value < 0:
                        errors.append("Portfolio value cannot be negative")
                        status = "error"
                    
                    if abs(cash_balance) > portfolio_value * 2:
                        errors.append("Cash balance seems unrealistic")
                        status = "warning"
            
            return status, errors
        
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            return "error", [f"Validation error: {str(e)}"]
    
    def generate_report_content(self, report_id: str, format_type: str = "json") -> str:
        """Rapor içeriği oluştur"""
        try:
            if report_id not in self.regulatory_reports:
                logger.error(f"Report {report_id} not found")
                return ""
            
            report = self.regulatory_reports[report_id]
            report_data = self.report_data.get(report_id, [])
            
            if not report_data:
                logger.warning(f"No data found for report {report_id}")
                return ""
            
            # Rapor içeriği oluştur
            content = {
                "report_info": {
                    "report_id": report.report_id,
                    "report_type": report.report_type,
                    "period": report.period,
                    "start_date": report.start_date.isoformat(),
                    "end_date": report.end_date.isoformat(),
                    "status": report.status,
                    "generated_at": report.generated_at.isoformat() if report.generated_at else None
                },
                "data_summary": {
                    "total_data_sources": len(report.data_sources),
                    "total_data_points": len(report_data),
                    "data_quality_score": np.mean([d.data_quality_score for d in report_data]),
                    "validation_status": {
                        "valid": len([d for d in report_data if d.validation_status == "valid"]),
                        "warning": len([d for d in report_data if d.validation_status == "warning"]),
                        "error": len([d for d in report_data if d.validation_status == "error"])
                    }
                },
                "data_content": {}
            }
            
            # Veri içeriğini organize et
            for data in report_data:
                data_type = data.data_type
                if data_type not in content["data_content"]:
                    content["data_content"][data_type] = []
                
                content["data_content"][data_type].append({
                    "data_id": data.data_id,
                    "data_source": data.data_source,
                    "data_content": data.data_content,
                    "data_quality_score": data.data_quality_score,
                    "validation_status": data.validation_status,
                    "validation_errors": data.validation_errors,
                    "timestamp": data.timestamp.isoformat() if data.timestamp else None
                })
            
            if format_type.lower() == "json":
                return json.dumps(content, indent=2, ensure_ascii=False)
            elif format_type.lower() == "csv":
                return self._convert_to_csv(content)
            else:
                return str(content)
        
        except Exception as e:
            logger.error(f"Error generating report content: {e}")
            return ""
    
    def _convert_to_csv(self, content: Dict[str, Any]) -> str:
        """JSON içeriği CSV formatına çevir"""
        try:
            output = []
            
            # Report info
            output.append("Report Information")
            output.append("Field,Value")
            for key, value in content["report_info"].items():
                output.append(f"{key},{value}")
            
            output.append("")
            
            # Data summary
            output.append("Data Summary")
            output.append("Field,Value")
            for key, value in content["data_summary"].items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        output.append(f"{key}_{sub_key},{sub_value}")
                else:
                    output.append(f"{key},{value}")
            
            output.append("")
            
            # Data content
            for data_type, data_list in content["data_content"].items():
                output.append(f"{data_type.upper()} Data")
                if data_list:
                    headers = list(data_list[0].keys())
                    output.append(",".join(headers))
                    
                    for data in data_list:
                        row = []
                        for header in headers:
                            value = data.get(header, "")
                            if isinstance(value, (dict, list)):
                                value = str(value)
                            row.append(str(value))
                        output.append(",".join(row))
                
                output.append("")
            
            return "\n".join(output)
        
        except Exception as e:
            logger.error(f"Error converting to CSV: {e}")
            return ""
    
    def submit_report(self, report_id: str, regulator: str, submission_method: str = "electronic") -> bool:
        """Raporu düzenleyiciye gönder"""
        try:
            if report_id not in self.regulatory_reports:
                logger.error(f"Report {report_id} not found")
                return False
            
            report = self.regulatory_reports[report_id]
            
            # Rapor durumunu güncelle
            report.status = "submitted"
            report.submission_date = datetime.now()
            
            # Submission kaydı oluştur
            submission_id = f"SUB_{regulator}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            submission = ReportSubmission(
                submission_id=submission_id,
                report_id=report_id,
                regulator=regulator,
                submission_method=submission_method,
                submission_status="submitted",
                submission_timestamp=datetime.now()
            )
            
            self.report_submissions[submission_id] = submission
            
            logger.info(f"Report submitted: {report_id} to {regulator}")
            return True
        
        except Exception as e:
            logger.error(f"Error submitting report: {e}")
            return False
    
    def get_pending_reports(self) -> List[RegulatoryRequirement]:
        """Bekleyen raporları getir"""
        try:
            pending_reports = []
            current_date = datetime.now()
            
            for requirement in self.regulatory_requirements.values():
                if not requirement.is_active:
                    continue
                
                # Son rapor tarihini bul
                last_report_date = None
                for report in self.regulatory_reports.values():
                    if (report.report_type == requirement.report_type and 
                        report.status in ["submitted", "approved"]):
                        if last_report_date is None or report.end_date > last_report_date:
                            last_report_date = report.end_date
                
                # Yeni rapor gerekli mi kontrol et
                if last_report_date is None:
                    # Hiç rapor yok, hemen oluştur
                    pending_reports.append(requirement)
                else:
                    # Son rapordan sonra geçen süre
                    days_since_last = (current_date - last_report_date).days
                    
                    if requirement.frequency == "daily" and days_since_last >= 1:
                        pending_reports.append(requirement)
                    elif requirement.frequency == "weekly" and days_since_last >= 7:
                        pending_reports.append(requirement)
                    elif requirement.frequency == "monthly" and days_since_last >= 30:
                        pending_reports.append(requirement)
                    elif requirement.frequency == "quarterly" and days_since_last >= 90:
                        pending_reports.append(requirement)
                    elif requirement.frequency == "annual" and days_since_last >= 365:
                        pending_reports.append(requirement)
            
            return pending_reports
        
        except Exception as e:
            logger.error(f"Error getting pending reports: {e}")
            return []
    
    def get_regulatory_summary(self) -> Dict[str, Any]:
        """Düzenleyici raporlama özeti getir"""
        try:
            total_reports = len(self.regulatory_reports)
            total_submissions = len(self.report_submissions)
            total_requirements = len(self.regulatory_requirements)
            
            # Durum dağılımı
            status_counts = {}
            for report in self.regulatory_reports.values():
                status = report.status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Regulator dağılımı
            regulator_counts = {}
            for submission in self.report_submissions.values():
                regulator = submission.regulator
                regulator_counts[regulator] = regulator_counts.get(regulator, 0) + 1
            
            # Bekleyen raporlar
            pending_reports = self.get_pending_reports()
            
            summary = {
                "total_reports": total_reports,
                "total_submissions": total_submissions,
                "total_requirements": total_requirements,
                "pending_reports": len(pending_reports),
                "status_distribution": status_counts,
                "regulator_distribution": regulator_counts,
                "compliance_rate": (total_reports / total_requirements * 100) if total_requirements > 0 else 0,
                "last_submission": None,
                "next_deadline": None
            }
            
            if self.report_submissions:
                summary["last_submission"] = max(s.submission_timestamp for s in self.report_submissions.values()).isoformat()
            
            if pending_reports:
                # En yakın deadline'ı bul
                current_date = datetime.now()
                min_deadline = None
                
                for requirement in pending_reports:
                    if requirement.frequency == "daily":
                        deadline = current_date + timedelta(days=requirement.deadline_days)
                    elif requirement.frequency == "weekly":
                        deadline = current_date + timedelta(days=requirement.deadline_days)
                    elif requirement.frequency == "monthly":
                        deadline = current_date + timedelta(days=requirement.deadline_days)
                    elif requirement.frequency == "quarterly":
                        deadline = current_date + timedelta(days=requirement.deadline_days)
                    elif requirement.frequency == "annual":
                        deadline = current_date + timedelta(days=requirement.deadline_days)
                    
                    if min_deadline is None or deadline < min_deadline:
                        min_deadline = deadline
                
                if min_deadline:
                    summary["next_deadline"] = min_deadline.isoformat()
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting regulatory summary: {e}")
            return {}


def test_regulatory_reporting():
    """Regulatory Reporting test fonksiyonu"""
    print("\n🧪 Regulatory Reporting Test Başlıyor...")
    
    # Regulatory Reporting oluştur
    reporting = RegulatoryReporting()
    
    print("✅ Varsayılan düzenleyici gereksinimleri eklendi")
    print(f"📊 Toplam gereksinim sayısı: {len(reporting.regulatory_requirements)}")
    
    # Test raporu oluştur
    print("\n📊 Test Raporu Oluşturma:")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    portfolio_report = reporting.create_regulatory_report("portfolio", start_date, end_date)
    if portfolio_report:
        print(f"   ✅ Portfolio raporu oluşturuldu: {portfolio_report.report_id}")
    
    # Test verisi ekle
    print("\n📊 Test Verisi Ekleme:")
    portfolio_data = {
        "portfolio_value": 100000,
        "cash_balance": 15000,
        "total_positions": 5,
        "margin_used": 5000,
        "unrealized_pnl": 2500,
        "realized_pnl": -500
    }
    
    success = reporting.add_report_data(
        portfolio_report.report_id, 
        "portfolio", 
        "portfolio_engine", 
        portfolio_data
    )
    
    if success:
        print("   ✅ Portfolio verisi eklendi")
    
    # Trading verisi ekle
    trading_data = {
        "total_trades": 25,
        "total_volume": 50000,
        "total_commission": 125,
        "winning_trades": 15,
        "losing_trades": 10,
        "avg_trade_size": 2000
    }
    
    success = reporting.add_report_data(
        portfolio_report.report_id, 
        "trading", 
        "trading_engine", 
        trading_data
    )
    
    if success:
        print("   ✅ Trading verisi eklendi")
    
    # Risk verisi ekle
    risk_data = {
        "var_95": 0.025,
        "var_99": 0.035,
        "max_drawdown": 0.15,
        "volatility": 0.18,
        "sharpe_ratio": 1.2,
        "beta": 0.8
    }
    
    success = reporting.add_report_data(
        portfolio_report.report_id, 
        "risk", 
        "risk_engine", 
        risk_data
    )
    
    if success:
        print("   ✅ Risk verisi eklendi")
    
    # Rapor içeriği oluştur
    print("\n📊 Rapor İçeriği Oluşturma:")
    json_content = reporting.generate_report_content(portfolio_report.report_id, "json")
    csv_content = reporting.generate_report_content(portfolio_report.report_id, "csv")
    
    print(f"   ✅ JSON formatında rapor oluşturuldu")
    print(f"   📊 JSON boyutu: {len(json_content)} karakter")
    print(f"   ✅ CSV formatında rapor oluşturuldu")
    print(f"   📊 CSV boyutu: {len(csv_content)} karakter")
    
    # Rapor gönderimi
    print("\n📊 Rapor Gönderimi:")
    success = reporting.submit_report(portfolio_report.report_id, "SPK", "electronic")
    if success:
        print("   ✅ Rapor SPK'ya gönderildi")
    
    # Bekleyen raporlar
    print("\n📊 Bekleyen Raporlar:")
    pending_reports = reporting.get_pending_reports()
    print(f"   ✅ {len(pending_reports)} bekleyen rapor tespit edildi")
    
    for req in pending_reports[:3]:  # İlk 3'ünü göster
        print(f"     📋 {req.name} ({req.frequency})")
    
    # Düzenleyici özeti
    print("\n📊 Düzenleyici Özeti:")
    summary = reporting.get_regulatory_summary()
    print(f"   ✅ Düzenleyici özeti alındı")
    print(f"   📊 Toplam rapor: {summary['total_reports']}")
    print(f"   📊 Toplam gönderim: {summary['total_submissions']}")
    print(f"   📊 Bekleyen rapor: {summary['pending_reports']}")
    print(f"   📊 Compliance oranı: {summary['compliance_rate']:.1f}%")
    
    print("\n✅ Regulatory Reporting Test Tamamlandı!")


if __name__ == "__main__":
    test_regulatory_reporting()
