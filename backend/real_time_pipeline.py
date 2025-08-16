"""
PRD v2.0 - Real-time Data Pipeline
WebSocket, Redis cache, event streaming
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import websockets
import aiohttp
import yfinance as yf
from collections import deque
import time

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeDataPipeline:
    """Real-time veri pipeline - WebSocket + Cache + Event Streaming"""
    
    def __init__(self, finnhub_api_key: str = "demo"):
        self.finnhub_api_key = finnhub_api_key
        self.websocket_connection = None
        self.is_connected = False
        self.price_cache = {}
        self.event_subscribers = []
        self.data_buffer = deque(maxlen=1000)  # Son 1000 veri
        self.last_update = {}
        self.connection_retries = 0
        self.max_retries = 5
        
        # Performance metrics
        self.metrics = {
            'messages_received': 0,
            'messages_processed': 0,
            'errors': 0,
            'last_message_time': None,
            'avg_processing_time': 0.0
        }
    
    async def start_pipeline(self):
        """Pipeline'ı başlat"""
        try:
            logger.info("🚀 Real-time data pipeline başlatılıyor...")
            
            # WebSocket bağlantısı
            await self._connect_websocket()
            
            # Fallback polling
            asyncio.create_task(self._start_fallback_polling())
            
            # Event streaming
            asyncio.create_task(self._start_event_streaming())
            
            logger.info("✅ Real-time data pipeline başlatıldı")
            
        except Exception as e:
            logger.error(f"Pipeline başlatma hatası: {e}")
            await self._start_fallback_polling()
    
    async def _connect_websocket(self):
        """Finnhub WebSocket bağlantısı"""
        try:
            if self.finnhub_api_key == "demo":
                logger.warning("Demo API key kullanılıyor, gerçek veri yok")
                return
            
            ws_url = f"wss://ws.finnhub.io?token={self.finnhub_api_key}"
            self.websocket_connection = await websockets.connect(ws_url)
            self.is_connected = True
            self.connection_retries = 0
            
            # Symbol subscription
            symbols = ["SISE.IS", "EREGL.IS", "TUPRS.IS", "AAPL", "MSFT", "GOOGL"]
            for symbol in symbols:
                subscribe_msg = {
                    "type": "subscribe",
                    "symbol": symbol
                }
                await self.websocket_connection.send(json.dumps(subscribe_msg))
                logger.info(f"Subscribed to {symbol}")
            
            # Listen for messages
            asyncio.create_task(self._listen_websocket())
            
        except Exception as e:
            logger.error(f"WebSocket bağlantı hatası: {e}")
            self.is_connected = False
            self.connection_retries += 1
    
    async def _listen_websocket(self):
        """WebSocket mesajlarını dinle"""
        try:
            async for message in self.websocket_connection:
                start_time = time.time()
                
                try:
                    data = json.loads(message)
                    await self._process_websocket_message(data)
                    
                    # Performance metrics
                    processing_time = time.time() - start_time
                    self.metrics['messages_received'] += 1
                    self.metrics['messages_processed'] += 1
                    self.metrics['last_message_time'] = datetime.now()
                    
                    # Average processing time
                    if self.metrics['avg_processing_time'] == 0:
                        self.metrics['avg_processing_time'] = processing_time
                    else:
                        self.metrics['avg_processing_time'] = (
                            self.metrics['avg_processing_time'] * 0.9 + processing_time * 0.1
                        )
                    
                except json.JSONDecodeError:
                    logger.error("JSON decode hatası")
                    self.metrics['errors'] += 1
                except Exception as e:
                    logger.error(f"Mesaj işleme hatası: {e}")
                    self.metrics['errors'] += 1
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket bağlantısı kapandı")
            self.is_connected = False
            await self._reconnect_websocket()
        except Exception as e:
            logger.error(f"WebSocket dinleme hatası: {e}")
            self.is_connected = False
    
    async def _reconnect_websocket(self):
        """WebSocket yeniden bağlanma"""
        if self.connection_retries < self.max_retries:
            logger.info(f"WebSocket yeniden bağlanılıyor... (Attempt {self.connection_retries + 1})")
            await asyncio.sleep(2 ** self.connection_retries)  # Exponential backoff
            await self._connect_websocket()
        else:
            logger.error("Maksimum yeniden bağlanma denemesi aşıldı")
    
    async def _process_websocket_message(self, data: Dict):
        """WebSocket mesajını işle"""
        try:
            if data.get("type") == "trade":
                symbol = data.get("data", [{}])[0].get("s")
                price = data.get("data", [{}])[0].get("p")
                volume = data.get("data", [{}])[0].get("v")
                timestamp = data.get("data", [{}])[0].get("t")
                
                if symbol and price:
                    # Price cache güncelle
                    price_data = {
                        'symbol': symbol,
                        'price': price,
                        'volume': volume,
                        'timestamp': datetime.fromtimestamp(timestamp/1000).isoformat(),
                        'source': 'finnhub_ws'
                    }
                    
                    self.price_cache[symbol] = price_data
                    self.last_update[symbol] = datetime.now()
                    
                    # Data buffer'a ekle
                    self.data_buffer.append(price_data)
                    
                    # Event subscribers'ları bilgilendir
                    await self._notify_subscribers(price_data)
                    
                    # Latency kontrolü
                    latency = (datetime.now() - datetime.fromtimestamp(timestamp/1000)).total_seconds() * 1000
                    if latency > 250:
                        logger.warning(f"Yüksek latency: {latency:.2f}ms for {symbol}")
                        
        except Exception as e:
            logger.error(f"WebSocket mesaj işleme hatası: {e}")
    
    async def _start_fallback_polling(self):
        """yfinance fallback polling"""
        logger.info("🔄 yfinance fallback polling başlatılıyor...")
        
        symbols = ["SISE.IS", "EREGL.IS", "TUPRS.IS", "AAPL", "MSFT", "GOOGL"]
        
        while not self.is_connected:
            try:
                for symbol in symbols:
                    await self._update_price_yfinance(symbol)
                
                await asyncio.sleep(5)  # 5 saniyede bir güncelle
                
            except Exception as e:
                logger.error(f"Fallback polling hatası: {e}")
                await asyncio.sleep(10)
    
    async def _update_price_yfinance(self, symbol: str):
        """yfinance ile fiyat güncelleme"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if 'regularMarketPrice' in info and info['regularMarketPrice']:
                price_data = {
                    'symbol': symbol,
                    'price': info['regularMarketPrice'],
                    'volume': info.get('volume', 0),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'yfinance'
                }
                
                self.price_cache[symbol] = price_data
                self.last_update[symbol] = datetime.now()
                
                # Data buffer'a ekle
                self.data_buffer.append(price_data)
                
                # Event subscribers'ları bilgilendir
                await self._notify_subscribers(price_data)
                
        except Exception as e:
            logger.error(f"yfinance güncelleme hatası {symbol}: {e}")
    
    async def _start_event_streaming(self):
        """Event streaming başlat"""
        logger.info("📡 Event streaming başlatılıyor...")
        
        while True:
            try:
                # System health check
                health_data = {
                    'type': 'health_check',
                    'timestamp': datetime.now().isoformat(),
                    'metrics': self.metrics,
                    'connected_symbols': len(self.price_cache),
                    'buffer_size': len(self.data_buffer)
                }
                
                await self._notify_subscribers(health_data)
                
                await asyncio.sleep(30)  # 30 saniyede bir health check
                
            except Exception as e:
                logger.error(f"Event streaming hatası: {e}")
                await asyncio.sleep(60)
    
    def subscribe_to_events(self, callback: Callable):
        """Event subscription"""
        self.event_subscribers.append(callback)
        logger.info(f"Event subscriber eklendi: {len(self.event_subscribers)}")
    
    async def _notify_subscribers(self, data: Dict):
        """Event subscribers'ları bilgilendir"""
        for callback in self.event_subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Subscriber notification hatası: {e}")
    
    def get_price(self, symbol: str) -> Optional[Dict]:
        """Sembol için son fiyat bilgisi"""
        return self.price_cache.get(symbol)
    
    def get_all_prices(self) -> Dict:
        """Tüm fiyat bilgileri"""
        return self.price_cache.copy()
    
    def get_recent_data(self, symbol: str = None, limit: int = 100) -> List[Dict]:
        """Son verileri getir"""
        if symbol:
            return [data for data in self.data_buffer if data.get('symbol') == symbol][-limit:]
        else:
            return list(self.data_buffer)[-limit:]
    
    def get_metrics(self) -> Dict:
        """Performance metrics"""
        return self.metrics.copy()
    
    async def stop_pipeline(self):
        """Pipeline'ı durdur"""
        try:
            if self.websocket_connection:
                await self.websocket_connection.close()
            
            self.is_connected = False
            logger.info("🛑 Real-time data pipeline durduruldu")
            
        except Exception as e:
            logger.error(f"Pipeline durdurma hatası: {e}")

# Global pipeline instance
pipeline = RealTimeDataPipeline()

async def start_real_time_pipeline():
    """Global pipeline'ı başlat"""
    await pipeline.start_pipeline()

async def stop_real_time_pipeline():
    """Global pipeline'ı durdur"""
    await pipeline.stop_pipeline()
