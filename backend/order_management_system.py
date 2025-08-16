"""
PRD v2.0 - BIST AI Smart Trader
Order Management System Module

Sipariş yönetim sistemi:
- Order creation and management
- Order types and status tracking
- Risk checks and validation
- Order execution monitoring
- Position tracking
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class Order:
    """Sipariş"""
    order_id: str
    symbol: str
    order_type: str  # market, limit, stop, stop_limit
    side: str  # buy, sell
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    limit_price: Optional[float] = None
    status: str = "pending"  # pending, filled, cancelled, rejected, partial
    filled_quantity: float = 0.0
    filled_price: float = 0.0
    commission: float = 0.0
    timestamp: datetime = None
    user_id: str = ""
    strategy_id: str = ""
    risk_profile: str = "moderate"

@dataclass
class OrderStatus:
    """Sipariş durumu"""
    order_id: str
    status: str
    message: str
    timestamp: datetime = None
    details: Dict[str, Any] = None

@dataclass
class Position:
    """Pozisyon"""
    position_id: str
    symbol: str
    side: str  # long, short
    quantity: float
    average_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    total_pnl: float
    margin_used: float
    timestamp: datetime = None
    last_updated: datetime = None

@dataclass
class OrderValidation:
    """Sipariş doğrulama"""
    is_valid: bool
    validation_errors: List[str]
    risk_score: float
    margin_requirement: float
    warnings: List[str]
    timestamp: datetime = None

class OrderManagementSystem:
    """
    Sipariş Yönetim Sistemi
    
    PRD v2.0 gereksinimleri:
    - Sipariş oluşturma ve yönetimi
    - Sipariş türleri ve durum takibi
    - Risk kontrolleri ve doğrulama
    - Sipariş icra izleme
    - Pozisyon takibi
    """
    
    def __init__(self):
        """Order Management System başlatıcı"""
        # Siparişler
        self.orders = {}
        
        # Pozisyonlar
        self.positions = {}
        
        # Sipariş durumları
        self.order_statuses = {}
        
        # Risk limitleri
        self.risk_limits = {
            'max_order_size': 100000,  # TL
            'max_position_size': 500000,  # TL
            'max_daily_loss': 50000,  # TL
            'max_order_value': 50000,  # TL
            'min_order_value': 1000,  # TL
            'max_orders_per_day': 100,
            'max_symbols': 20
        }
        
        # Komisyon oranları
        self.commission_rates = {
            'equity': 0.0015,  # %0.15
            'bond': 0.0010,    # %0.10
            'etf': 0.0012,     # %0.12
            'forex': 0.0005,   # %0.05
            'commodity': 0.0020  # %0.20
        }
        
        # Günlük istatistikler
        self.daily_stats = {
            'total_orders': 0,
            'total_volume': 0.0,
            'total_commission': 0.0,
            'total_pnl': 0.0,
            'date': datetime.now().date()
        }
    
    def create_order(self, symbol: str, order_type: str, side: str, quantity: float,
                     price: Optional[float] = None, stop_price: Optional[float] = None,
                     user_id: str = "", strategy_id: str = "", risk_profile: str = "moderate") -> Order:
        """
        Sipariş oluştur
        
        Args:
            symbol: Sembol
            order_type: Sipariş türü
            side: Yön (buy/sell)
            quantity: Miktar
            price: Fiyat
            stop_price: Stop fiyatı
            user_id: Kullanıcı ID
            strategy_id: Strateji ID
            risk_profile: Risk profili
            
        Returns:
            Order: Oluşturulan sipariş
        """
        try:
            # Sipariş ID oluştur
            order_id = f"order_{symbol}_{side}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Limit fiyatı hesapla
            limit_price = None
            if order_type == "limit":
                limit_price = price
            elif order_type == "stop_limit":
                limit_price = price
            
            # Sipariş oluştur
            order = Order(
                order_id=order_id,
                symbol=symbol,
                order_type=order_type,
                side=side,
                quantity=quantity,
                price=price,
                stop_price=stop_price,
                limit_price=limit_price,
                timestamp=datetime.now(),
                user_id=user_id,
                strategy_id=strategy_id,
                risk_profile=risk_profile
            )
            
            # Siparişi kaydet
            self.orders[order_id] = order
            
            # Günlük istatistikleri güncelle
            self._update_daily_stats(order)
            
            print(f"✅ Sipariş oluşturuldu: {order_id}")
            return order
            
        except Exception as e:
            print(f"❌ Sipariş oluşturma hatası: {str(e)}")
            return Order(
                order_id="", symbol="", order_type="", side="", quantity=0
            )
    
    def validate_order(self, order: Order) -> OrderValidation:
        """
        Siparişi doğrula
        
        Args:
            order: Sipariş
            
        Returns:
            OrderValidation: Doğrulama sonucu
        """
        try:
            validation_errors = []
            warnings = []
            
            # Temel doğrulamalar
            if not order.symbol:
                validation_errors.append("Sembol boş olamaz")
            
            if order.quantity <= 0:
                validation_errors.append("Miktar pozitif olmalı")
            
            if order.side not in ["buy", "sell"]:
                validation_errors.append("Geçersiz yön")
            
            if order.order_type not in ["market", "limit", "stop", "stop_limit"]:
                validation_errors.append("Geçersiz sipariş türü")
            
            # Fiyat doğrulamaları
            if order.order_type in ["limit", "stop_limit"] and not order.price:
                validation_errors.append("Limit fiyatı gerekli")
            
            if order.order_type in ["stop", "stop_limit"] and not order.stop_price:
                validation_errors.append("Stop fiyatı gerekli")
            
            # Risk limitleri kontrolü
            order_value = order.quantity * (order.price or 0)
            if order_value > self.risk_limits['max_order_value']:
                validation_errors.append(f"Sipariş değeri çok yüksek: {order_value:,.2f} TL")
            
            if order.quantity > self.risk_limits['max_order_size']:
                validation_errors.append(f"Sipariş miktarı çok yüksek: {order.quantity:,.0f}")
            
            # Günlük limit kontrolü
            if self.daily_stats['total_orders'] >= self.risk_limits['max_orders_per_day']:
                validation_errors.append("Günlük sipariş limiti aşıldı")
            
            # Pozisyon limiti kontrolü
            current_position = self._get_position_value(order.symbol)
            if current_position + order_value > self.risk_limits['max_position_size']:
                warnings.append(f"Pozisyon limiti yaklaşıyor: {current_position + order_value:,.2f} TL")
            
            # Risk skoru hesapla
            risk_score = self._calculate_order_risk(order)
            
            # Margin gereksinimi hesapla
            margin_requirement = self._calculate_margin_requirement(order)
            
            is_valid = len(validation_errors) == 0
            
            validation = OrderValidation(
                is_valid=is_valid,
                validation_errors=validation_errors,
                risk_score=risk_score,
                margin_requirement=margin_requirement,
                warnings=warnings,
                timestamp=datetime.now()
            )
            
            if is_valid:
                print(f"✅ Sipariş doğrulandı: {order.order_id}")
            else:
                print(f"❌ Sipariş doğrulanamadı: {order.order_id}")
                for error in validation_errors:
                    print(f"   Hata: {error}")
            
            return validation
            
        except Exception as e:
            print(f"❌ Sipariş doğrulama hatası: {str(e)}")
            return OrderValidation(
                is_valid=False,
                validation_errors=[str(e)],
                risk_score=1.0,
                margin_requirement=0.0,
                warnings=[]
            )
    
    def execute_order(self, order_id: str, execution_price: float, 
                      execution_quantity: Optional[float] = None) -> bool:
        """
        Siparişi icra et
        
        Args:
            order_id: Sipariş ID
            execution_price: İcra fiyatı
            execution_quantity: İcra miktarı
            
        Returns:
            bool: Başarı durumu
        """
        try:
            if order_id not in self.orders:
                print(f"❌ Sipariş bulunamadı: {order_id}")
                return False
            
            order = self.orders[order_id]
            
            # İcra miktarı
            if execution_quantity is None:
                execution_quantity = order.quantity
            
            # Komisyon hesapla
            commission = self._calculate_commission(order.symbol, execution_quantity, execution_price)
            
            # Sipariş durumunu güncelle
            if execution_quantity >= order.quantity:
                order.status = "filled"
                order.filled_quantity = order.quantity
            else:
                order.status = "partial"
                order.filled_quantity = execution_quantity
            
            order.filled_price = execution_price
            order.commission = commission
            
            # Pozisyon güncelle
            self._update_position(order, execution_price, execution_quantity)
            
            # Sipariş durumu kaydet
            status = OrderStatus(
                order_id=order_id,
                status=order.status,
                message=f"Sipariş icra edildi: {execution_quantity} @ {execution_price}",
                timestamp=datetime.now(),
                details={
                    'execution_price': execution_price,
                    'execution_quantity': execution_quantity,
                    'commission': commission
                }
            )
            
            self.order_statuses[order_id] = status
            
            print(f"✅ Sipariş icra edildi: {order_id}")
            return True
            
        except Exception as e:
            print(f"❌ Sipariş icra hatası: {str(e)}")
            return False
    
    def cancel_order(self, order_id: str, reason: str = "") -> bool:
        """
        Siparişi iptal et
        
        Args:
            order_id: Sipariş ID
            reason: İptal nedeni
            
        Returns:
            bool: Başarı durumu
        """
        try:
            if order_id not in self.orders:
                print(f"❌ Sipariş bulunamadı: {order_id}")
                return False
            
            order = self.orders[order_id]
            
            if order.status in ["filled", "cancelled"]:
                print(f"⚠️ Sipariş zaten {order.status}: {order_id}")
                return False
            
            # Sipariş durumunu güncelle
            order.status = "cancelled"
            
            # Sipariş durumu kaydet
            status = OrderStatus(
                order_id=order_id,
                status="cancelled",
                message=f"Sipariş iptal edildi: {reason}",
                timestamp=datetime.now(),
                details={'reason': reason}
            )
            
            self.order_statuses[order_id] = status
            
            print(f"✅ Sipariş iptal edildi: {order_id}")
            return True
            
        except Exception as e:
            print(f"❌ Sipariş iptal hatası: {str(e)}")
            return False
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        Siparişi al
        
        Args:
            order_id: Sipariş ID
            
        Returns:
            Optional[Order]: Sipariş
        """
        return self.orders.get(order_id)
    
    def get_orders_by_status(self, status: str) -> List[Order]:
        """
        Duruma göre siparişleri al
        
        Args:
            status: Sipariş durumu
            
        Returns:
            List[Order]: Sipariş listesi
        """
        return [order for order in self.orders.values() if order.status == status]
    
    def get_orders_by_symbol(self, symbol: str) -> List[Order]:
        """
        Sembole göre siparişleri al
        
        Args:
            symbol: Sembol
            
        Returns:
            List[Order]: Sipariş listesi
        """
        return [order for order in self.orders.values() if order.symbol == symbol]
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Pozisyonu al
        
        Args:
            symbol: Sembol
            
        Returns:
            Optional[Position]: Pozisyon
        """
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> List[Position]:
        """Tüm pozisyonları al"""
        return list(self.positions.values())
    
    def get_order_status(self, order_id: str) -> Optional[OrderStatus]:
        """
        Sipariş durumunu al
        
        Args:
            order_id: Sipariş ID
            
        Returns:
            Optional[OrderStatus]: Sipariş durumu
        """
        return self.order_statuses.get(order_id)
    
    def get_trading_summary(self) -> Dict[str, Any]:
        """Ticaret özetini al"""
        try:
            summary = {
                'total_orders': len(self.orders),
                'orders_by_status': {},
                'orders_by_type': {},
                'total_positions': len(self.positions),
                'total_volume': 0.0,
                'total_commission': 0.0,
                'total_pnl': 0.0,
                'daily_stats': self.daily_stats.copy()
            }
            
            # Durum bazında sipariş sayısı
            for order in self.orders.values():
                if order.status not in summary['orders_by_status']:
                    summary['orders_by_status'][order.status] = 0
                summary['orders_by_status'][order.status] += 1
                
                if order.order_type not in summary['orders_by_type']:
                    summary['orders_by_type'][order.order_type] = 0
                summary['orders_by_type'][order.order_type] += 1
                
                summary['total_volume'] += order.filled_quantity * order.filled_price
                summary['total_commission'] += order.commission
            
            # Pozisyon P&L
            for position in self.positions.values():
                summary['total_pnl'] += position.total_pnl
            
            return summary
            
        except Exception as e:
            print(f"❌ Ticaret özeti alma hatası: {str(e)}")
            return {'error': str(e)}
    
    def _update_daily_stats(self, order: Order):
        """Günlük istatistikleri güncelle"""
        try:
            current_date = datetime.now().date()
            
            # Yeni gün başladıysa sıfırla
            if current_date != self.daily_stats['date']:
                self.daily_stats = {
                    'total_orders': 0,
                    'total_volume': 0.0,
                    'total_commission': 0.0,
                    'total_pnl': 0.0,
                    'date': current_date
                }
            
            self.daily_stats['total_orders'] += 1
            
        except Exception as e:
            print(f"❌ Günlük istatistik güncelleme hatası: {str(e)}")
    
    def _calculate_order_risk(self, order: Order) -> float:
        """Sipariş risk skorunu hesapla"""
        try:
            risk_score = 0.0
            
            # Sipariş türü riski
            if order.order_type == "market":
                risk_score += 0.3
            elif order.order_type == "stop":
                risk_score += 0.2
            elif order.order_type == "limit":
                risk_score += 0.1
            
            # Miktar riski
            if order.quantity > 10000:
                risk_score += 0.2
            elif order.quantity > 5000:
                risk_score += 0.1
            
            # Risk profili
            if order.risk_profile == "aggressive":
                risk_score += 0.2
            elif order.risk_profile == "conservative":
                risk_score -= 0.1
            
            return min(1.0, max(0.0, risk_score))
            
        except Exception:
            return 0.5
    
    def _calculate_margin_requirement(self, order: Order) -> float:
        """Margin gereksinimini hesapla"""
        try:
            # Basit margin hesaplama
            order_value = order.quantity * (order.price or 100)  # Varsayılan fiyat
            margin_rate = 0.15  # %15 margin
            
            return order_value * margin_rate
            
        except Exception:
            return 0.0
    
    def _calculate_commission(self, symbol: str, quantity: float, price: float) -> float:
        """Komisyon hesapla"""
        try:
            # Sembol tipini belirle (basit)
            if "BOND" in symbol:
                asset_type = "bond"
            elif "ETF" in symbol:
                asset_type = "etf"
            else:
                asset_type = "equity"
            
            commission_rate = self.commission_rates.get(asset_type, 0.0015)
            commission = quantity * price * commission_rate
            
            return commission
            
        except Exception:
            return 0.0
    
    def _get_position_value(self, symbol: str) -> float:
        """Pozisyon değerini al"""
        try:
            position = self.positions.get(symbol)
            if position:
                return position.quantity * position.current_price
            return 0.0
            
        except Exception:
            return 0.0
    
    def _update_position(self, order: Order, execution_price: float, execution_quantity: float):
        """Pozisyonu güncelle"""
        try:
            symbol = order.symbol
            
            if symbol not in self.positions:
                # Yeni pozisyon oluştur
                position = Position(
                    position_id=f"pos_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    symbol=symbol,
                    side="long" if order.side == "buy" else "short",
                    quantity=execution_quantity,
                    average_price=execution_price,
                    current_price=execution_price,
                    unrealized_pnl=0.0,
                    realized_pnl=0.0,
                    total_pnl=0.0,
                    margin_used=execution_quantity * execution_price * 0.15,
                    timestamp=datetime.now(),
                    last_updated=datetime.now()
                )
                self.positions[symbol] = position
            else:
                # Mevcut pozisyonu güncelle
                position = self.positions[symbol]
                
                if order.side == "buy":
                    # Long pozisyon ekle
                    total_quantity = position.quantity + execution_quantity
                    total_value = (position.quantity * position.average_price) + (execution_quantity * execution_price)
                    position.average_price = total_value / total_quantity if total_quantity > 0 else 0
                    position.quantity = total_quantity
                else:
                    # Short pozisyon ekle veya long pozisyonu azalt
                    if position.side == "long":
                        if execution_quantity >= position.quantity:
                            # Pozisyonu kapat
                            realized_pnl = (execution_price - position.average_price) * position.quantity
                            position.realized_pnl += realized_pnl
                            position.quantity = 0
                        else:
                            # Pozisyonu azalt
                            realized_pnl = (execution_price - position.average_price) * execution_quantity
                            position.realized_pnl += realized_pnl
                            position.quantity -= execution_quantity
                
                position.current_price = execution_price
                position.last_updated = datetime.now()
                
                # P&L güncelle
                position.unrealized_pnl = (position.current_price - position.average_price) * position.quantity
                position.total_pnl = position.realized_pnl + position.unrealized_pnl
                
        except Exception as e:
            print(f"❌ Pozisyon güncelleme hatası: {str(e)}")

# Test fonksiyonu
def test_order_management_system():
    """Order Management System test fonksiyonu"""
    print("🧪 Order Management System Test Başlıyor...")
    
    # Order Management System başlat
    oms = OrderManagementSystem()
    
    # Sipariş oluşturma test
    print("\n📝 Sipariş Oluşturma Test:")
    order1 = oms.create_order(
        symbol="SISE.IS",
        order_type="limit",
        side="buy",
        quantity=1000,
        price=45.50,
        user_id="user_1",
        strategy_id="strategy_1"
    )
    
    print(f"   ✅ Sipariş 1 oluşturuldu: {order1.order_id}")
    
    order2 = oms.create_order(
        symbol="EREGL.IS",
        order_type="market",
        side="sell",
        quantity=500,
        user_id="user_1",
        strategy_id="strategy_2"
    )
    
    print(f"   ✅ Sipariş 2 oluşturuldu: {order2.order_id}")
    
    # Sipariş doğrulama test
    print("\n✅ Sipariş Doğrulama Test:")
    validation1 = oms.validate_order(order1)
    print(f"   Sipariş 1 doğrulandı: {validation1.is_valid}")
    
    validation2 = oms.validate_order(order2)
    print(f"   Sipariş 2 doğrulandı: {validation2.is_valid}")
    
    # Sipariş icra test
    print("\n⚡ Sipariş İcra Test:")
    execution1 = oms.execute_order(order1.order_id, 45.50, 1000)
    print(f"   Sipariş 1 icra edildi: {execution1}")
    
    execution2 = oms.execute_order(order2.order_id, 28.75, 500)
    print(f"   Sipariş 2 icra edildi: {execution2}")
    
    # Pozisyon test
    print("\n📊 Pozisyon Test:")
    position1 = oms.get_position("SISE.IS")
    if position1:
        print(f"   ✅ SISE.IS pozisyonu: {position1.quantity} adet @ {position1.average_price:.2f}")
        print(f"   📈 P&L: {position1.total_pnl:.2f} TL")
    
    position2 = oms.get_position("EREGL.IS")
    if position2:
        print(f"   ✅ EREGL.IS pozisyonu: {position2.quantity} adet @ {position2.average_price:.2f}")
        print(f"   📈 P&L: {position2.total_pnl:.2f} TL")
    
    # Sipariş durumu test
    print("\n📋 Sipariş Durumu Test:")
    status1 = oms.get_order_status(order1.order_id)
    if status1:
        print(f"   ✅ Sipariş 1 durumu: {status1.status}")
        print(f"   📝 Mesaj: {status1.message}")
    
    # Sipariş listesi test
    print("\n📋 Sipariş Listesi Test:")
    filled_orders = oms.get_orders_by_status("filled")
    print(f"   ✅ Doldurulan siparişler: {len(filled_orders)}")
    
    pending_orders = oms.get_orders_by_status("pending")
    print(f"   ⏳ Bekleyen siparişler: {len(pending_orders)}")
    
    # Sembol bazında siparişler test
    print("\n🔍 Sembol Bazında Siparişler Test:")
    sise_orders = oms.get_orders_by_symbol("SISE.IS")
    print(f"   ✅ SISE.IS siparişleri: {len(sise_orders)}")
    
    # Ticaret özeti test
    print("\n📊 Ticaret Özeti Test:")
    trading_summary = oms.get_trading_summary()
    if 'error' not in trading_summary:
        print(f"   ✅ Ticaret özeti alındı")
        print(f"   📊 Toplam sipariş: {trading_summary['total_orders']}")
        print(f"   📈 Toplam hacim: {trading_summary['total_volume']:,.2f} TL")
        print(f"   💰 Toplam komisyon: {trading_summary['total_commission']:,.2f} TL")
        print(f"   📊 Toplam P&L: {trading_summary['total_pnl']:,.2f} TL")
    
    # Pozisyon listesi test
    print("\n📋 Pozisyon Listesi Test:")
    all_positions = oms.get_all_positions()
    print(f"   ✅ Toplam pozisyon: {len(all_positions)}")
    
    for pos in all_positions:
        print(f"     {pos.symbol}: {pos.quantity} adet, P&L: {pos.total_pnl:.2f} TL")
    
    print("\n✅ Order Management System Test Tamamlandı!")
    
    return oms

if __name__ == "__main__":
    test_order_management_system()
