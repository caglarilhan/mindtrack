"""
PRD v2.0 - WebSocket Connector
Finnhub WS + yfinance fallback
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class WebSocketConnector:
    """WebSocket bağlantı yöneticisi"""
    
    def __init__(self):
        self.websocket = None
        self.is_connected = False
        self.subscribed_symbols = set()
        self.price_cache = {}
        self.callbacks = {}
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5  # saniye
        
    async def connect(self, url: str = None) -> bool:
        """WebSocket bağlantısı kur"""
        try:
            if url is None:
                # Mock WebSocket (gerçek implementasyonda websockets kütüphanesi kullanılır)
                logger.info("🔌 Mock WebSocket bağlantısı kuruluyor...")
                await asyncio.sleep(0.1)  # Simüle edilmiş bağlantı süresi
                
                self.is_connected = True
                self.websocket = MockWebSocket()
                logger.info("✅ Mock WebSocket bağlantısı kuruldu")
                return True
            else:
                # Gerçek WebSocket bağlantısı
                logger.info(f"🔌 WebSocket bağlantısı kuruluyor: {url}")
                # websockets kütüphanesi ile bağlantı
                # self.websocket = await websockets.connect(url)
                # self.is_connected = True
                # logger.info("✅ WebSocket bağlantısı kuruldu")
                # return True
                
                # Şimdilik mock
                await asyncio.sleep(0.1)
                self.is_connected = True
                self.websocket = MockWebSocket()
                logger.info("✅ Mock WebSocket bağlantısı kuruldu")
                return True
                
        except Exception as e:
            logger.error(f"❌ WebSocket bağlantı hatası: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self) -> bool:
        """WebSocket bağlantısını kapat"""
        try:
            if self.websocket:
                if hasattr(self.websocket, 'close'):
                    await self.websocket.close()
                
                self.is_connected = False
                self.websocket = None
                logger.info("✅ WebSocket bağlantısı kapatıldı")
                return True
            else:
                logger.warning("⚠️ WebSocket bağlantısı zaten kapalı")
                return True
                
        except Exception as e:
            logger.error(f"❌ WebSocket kapatma hatası: {e}")
            return False
    
    async def subscribe_to_symbols(self, symbols: List[str]) -> bool:
        """Sembollere abone ol"""
        try:
            if not self.is_connected:
                logger.warning("⚠️ WebSocket bağlantısı yok")
                return False
            
            # Abone olunacak sembolleri ekle
            for symbol in symbols:
                self.subscribed_symbols.add(symbol)
                logger.info(f"📡 {symbol} aboneliği eklendi")
            
            # Mock subscription mesajı gönder
            if hasattr(self.websocket, 'send'):
                subscription_msg = {
                    'type': 'subscribe',
                    'symbols': list(self.subscribed_symbols)
                }
                await self.websocket.send(json.dumps(subscription_msg))
            
            logger.info(f"✅ {len(symbols)} sembole abone olundu")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sembol abonelik hatası: {e}")
            return False
    
    async def unsubscribe_from_symbols(self, symbols: List[str]) -> bool:
        """Sembol aboneliklerini kaldır"""
        try:
            if not self.is_connected:
                logger.warning("⚠️ WebSocket bağlantısı yok")
                return False
            
            # Abonelikleri kaldır
            for symbol in symbols:
                if symbol in self.subscribed_symbols:
                    self.subscribed_symbols.remove(symbol)
                    logger.info(f"📡 {symbol} aboneliği kaldırıldı")
            
            # Mock unsubscribe mesajı gönder
            if hasattr(self.websocket, 'send'):
                unsubscribe_msg = {
                    'type': 'unsubscribe',
                    'symbols': symbols
                }
                await self.websocket.send(json.dumps(unsubscribe_msg))
            
            logger.info(f"✅ {len(symbols)} sembol aboneliği kaldırıldı")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sembol abonelik kaldırma hatası: {e}")
            return False
    
    def register_callback(self, event_type: str, callback: Callable) -> bool:
        """Callback fonksiyonu kaydet"""
        try:
            if event_type not in self.callbacks:
                self.callbacks[event_type] = []
            
            self.callbacks[event_type].append(callback)
            logger.info(f"✅ {event_type} callback'i kaydedildi")
            return True
            
        except Exception as e:
            logger.error(f"❌ Callback kayıt hatası: {e}")
            return False
    
    def unregister_callback(self, event_type: str, callback: Callable) -> bool:
        """Callback fonksiyonu kaldır"""
        try:
            if event_type in self.callbacks and callback in self.callbacks[event_type]:
                self.callbacks[event_type].remove(callback)
                logger.info(f"✅ {event_type} callback'i kaldırıldı")
                return True
            else:
                logger.warning(f"⚠️ {event_type} callback'i bulunamadı")
                return False
                
        except Exception as e:
            logger.error(f"❌ Callback kaldırma hatası: {e}")
            return False
    
    async def start_listening(self) -> bool:
        """WebSocket mesajlarını dinlemeye başla"""
        try:
            if not self.is_connected:
                logger.warning("⚠️ WebSocket bağlantısı yok")
                return False
            
            logger.info("🎧 WebSocket dinleme başlatılıyor...")
            
            # Mock dinleme döngüsü
            asyncio.create_task(self._mock_listening_loop())
            
            logger.info("✅ WebSocket dinleme başlatıldı")
            return True
            
        except Exception as e:
            logger.error(f"❌ WebSocket dinleme başlatma hatası: {e}")
            return False
    
    async def _mock_listening_loop(self):
        """Mock dinleme döngüsü"""
        try:
            while self.is_connected:
                # Mock fiyat verisi üret
                for symbol in self.subscribed_symbols:
                    mock_price_data = self._generate_mock_price_data(symbol)
                    
                    # Callback'leri çağır
                    await self._process_price_data(mock_price_data)
                
                # 5 saniye bekle
                await asyncio.sleep(5)
                
        except Exception as e:
            logger.error(f"❌ Mock dinleme döngüsü hatası: {e}")
    
    def _generate_mock_price_data(self, symbol: str) -> Dict[str, Any]:
        """Mock fiyat verisi oluştur"""
        try:
            import random
            
            # Deterministik random seed
            random.seed(hash(symbol) % 1000)
            
            # Base fiyat
            base_price = 50 + random.uniform(-20, 30)
            
            # Fiyat değişimi
            price_change = random.uniform(-0.05, 0.05)  # ±5%
            current_price = base_price * (1 + price_change)
            
            # Volume
            volume = random.randint(1000000, 10000000)
            
            # Timestamp
            timestamp = datetime.now().isoformat()
            
            price_data = {
                'symbol': symbol,
                'price': round(current_price, 2),
                'change': round(price_change * 100, 2),  # Yüzde
                'change_amount': round(base_price * price_change, 2),
                'volume': volume,
                'timestamp': timestamp,
                'source': 'mock_websocket'
            }
            
            # Cache'e kaydet
            self.price_cache[symbol] = price_data
            
            return price_data
            
        except Exception as e:
            logger.error(f"Mock fiyat veri oluşturma hatası: {e}")
            return {
                'symbol': symbol,
                'price': 0,
                'error': str(e)
            }
    
    async def _process_price_data(self, price_data: Dict[str, Any]):
        """Fiyat verisini işle"""
        try:
            # Price update callback'lerini çağır
            if 'price_update' in self.callbacks:
                for callback in self.callbacks['price_update']:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(price_data)
                        else:
                            callback(price_data)
                    except Exception as e:
                        logger.error(f"Callback hatası: {e}")
            
            # Genel data callback'lerini çağır
            if 'data' in self.callbacks:
                for callback in self.callbacks['data']:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(price_data)
                        else:
                            callback(price_data)
                    except Exception as e:
                        logger.error(f"Callback hatası: {e}")
                        
        except Exception as e:
            logger.error(f"Fiyat veri işleme hatası: {e}")
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """WebSocket'e mesaj gönder"""
        try:
            if not self.is_connected:
                logger.warning("⚠️ WebSocket bağlantısı yok")
                return False
            
            if hasattr(self.websocket, 'send'):
                await self.websocket.send(json.dumps(message))
                logger.info(f"✅ Mesaj gönderildi: {message.get('type', 'unknown')}")
                return True
            else:
                logger.warning("⚠️ WebSocket send metodu yok")
                return False
                
        except Exception as e:
            logger.error(f"❌ Mesaj gönderme hatası: {e}")
            return False
    
    def get_current_prices(self) -> Dict[str, Any]:
        """Mevcut fiyatları getir"""
        return self.price_cache.copy()
    
    def get_symbol_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Belirli sembolün fiyatını getir"""
        return self.price_cache.get(symbol)
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Bağlantı durumunu getir"""
        return {
            'is_connected': self.is_connected,
            'subscribed_symbols': list(self.subscribed_symbols),
            'total_symbols': len(self.subscribed_symbols),
            'price_cache_size': len(self.price_cache),
            'callback_count': sum(len(callbacks) for callbacks in self.callbacks.values()),
            'last_update': datetime.now().isoformat()
        }
    
    async def reconnect(self) -> bool:
        """Yeniden bağlan"""
        try:
            if self.reconnect_attempts >= self.max_reconnect_attempts:
                logger.error(f"❌ Maksimum yeniden bağlanma denemesi aşıldı: {self.max_reconnect_attempts}")
                return False
            
            logger.info(f"🔄 Yeniden bağlanma denemesi {self.reconnect_attempts + 1}/{self.max_reconnect_attempts}")
            
            # Mevcut bağlantıyı kapat
            await self.disconnect()
            
            # Yeniden bağlan
            success = await self.connect()
            
            if success:
                # Abonelikleri yeniden kur
                if self.subscribed_symbols:
                    await self.subscribe_to_symbols(list(self.subscribed_symbols))
                
                # Dinlemeyi yeniden başlat
                await self.start_listening()
                
                self.reconnect_attempts = 0
                logger.info("✅ Yeniden bağlanma başarılı")
                return True
            else:
                self.reconnect_attempts += 1
                logger.warning(f"⚠️ Yeniden bağlanma başarısız, {self.reconnect_delay} saniye sonra tekrar denenecek")
                
                # Delay sonra tekrar dene
                await asyncio.sleep(self.reconnect_delay)
                return await self.reconnect()
                
        except Exception as e:
            logger.error(f"❌ Yeniden bağlanma hatası: {e}")
            self.reconnect_attempts += 1
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Bağlantı sağlık kontrolü"""
        try:
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'is_connected': self.is_connected,
                'websocket_alive': self.websocket is not None,
                'subscribed_symbols_count': len(self.subscribed_symbols),
                'price_cache_count': len(self.price_cache),
                'callback_count': sum(len(callbacks) for callbacks in self.callbacks.values()),
                'reconnect_attempts': self.reconnect_attempts,
                'status': 'HEALTHY'
            }
            
            # Sağlık durumunu belirle
            if not self.is_connected:
                health_status['status'] = 'DISCONNECTED'
            elif self.reconnect_attempts > 0:
                health_status['status'] = 'UNSTABLE'
            elif len(self.price_cache) == 0:
                health_status['status'] = 'NO_DATA'
            
            logger.info(f"🏥 WebSocket sağlık kontrolü: {health_status['status']}")
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Sağlık kontrolü hatası: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'ERROR',
                'error': str(e)
            }

class MockWebSocket:
    """Mock WebSocket sınıfı"""
    
    def __init__(self):
        self.closed = False
        self.messages = []
    
    async def send(self, message: str):
        """Mock mesaj gönderme"""
        self.messages.append(message)
        await asyncio.sleep(0.01)  # Simüle edilmiş gecikme
    
    async def close(self):
        """Mock bağlantı kapatma"""
        self.closed = True
        await asyncio.sleep(0.01)
    
    async def recv(self):
        """Mock mesaj alma"""
        if self.messages:
            return self.messages.pop(0)
        else:
            return json.dumps({'type': 'ping', 'timestamp': datetime.now().isoformat()})

# Test fonksiyonu
async def test_websocket_connector():
    """WebSocket Connector test"""
    print("🧪 WebSocket Connector Test Ediliyor...")
    
    connector = WebSocketConnector()
    
    # Bağlantı kur
    print("\n🔌 Bağlantı kuruluyor...")
    connected = await connector.connect()
    
    if connected:
        print("✅ WebSocket bağlantısı kuruldu")
        
        # Test callback'i
        def price_callback(data):
            print(f"   📊 Fiyat güncellemesi: {data['symbol']} = {data['price']} TL")
        
        # Callback kaydet
        connector.register_callback('price_update', price_callback)
        
        # Sembollere abone ol
        test_symbols = ['SISE.IS', 'TUPRS.IS', 'GARAN.IS']
        print(f"\n📡 {len(test_symbols)} sembole abone olunuyor...")
        
        subscribed = await connector.subscribe_to_symbols(test_symbols)
        
        if subscribed:
            print("✅ Sembollere abone olundu")
            
            # Dinlemeyi başlat
            print("\n🎧 Dinleme başlatılıyor...")
            listening = await connector.start_listening()
            
            if listening:
                print("✅ Dinleme başlatıldı")
                
                # 10 saniye bekle (fiyat güncellemelerini görmek için)
                print("\n⏳ 10 saniye bekleniyor (fiyat güncellemeleri)...")
                await asyncio.sleep(10)
                
                # Mevcut fiyatları göster
                print("\n📊 Mevcut Fiyatlar:")
                current_prices = connector.get_current_prices()
                for symbol, price_data in current_prices.items():
                    print(f"   {symbol}: {price_data['price']} TL ({price_data['change']:+.2f}%)")
                
                # Bağlantı durumu
                print("\n🔍 Bağlantı Durumu:")
                status = connector.get_connection_status()
                print(f"   Bağlı: {status['is_connected']}")
                print(f"   Abone Sembol: {status['total_symbols']}")
                print(f"   Fiyat Cache: {status['price_cache_size']}")
                
                # Sağlık kontrolü
                print("\n🏥 Sağlık Kontrolü:")
                health = await connector.health_check()
                print(f"   Durum: {health['status']}")
                print(f"   Yeniden Bağlanma: {health['reconnect_attempts']}")
                
                # Bağlantıyı kapat
                print("\n🔌 Bağlantı kapatılıyor...")
                await connector.disconnect()
                print("✅ Bağlantı kapatıldı")
                
            else:
                print("❌ Dinleme başlatılamadı")
        else:
            print("❌ Sembollere abone olunamadı")
    else:
        print("❌ WebSocket bağlantısı kurulamadı")
    
    print("\n✅ Test tamamlandı!")

# Test çalıştır
if __name__ == "__main__":
    asyncio.run(test_websocket_connector())
