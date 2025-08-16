"""
PRD v2.0 - Canlı Fiyat Katmanı
Finnhub WS (≤ 30 sembol) + yfinance fallback
WebSocket + AsyncIO ile Latency < 250 ms hedefi
"""

import asyncio
import json
import logging
import websockets
import aiohttp
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import time

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketConnector:
    """BIST ve ABD borsaları için real-time fiyat connector"""
    
    def __init__(self, finnhub_api_key: str, symbols: List[str] = None):
        self.finnhub_api_key = finnhub_api_key
        self.symbols = symbols or self._get_default_symbols()
        self.ws_connection = None
        self.price_cache = {}
        self.last_update = {}
        self.callbacks = []
        self.is_connected = False
        
    def _get_default_symbols(self) -> List[str]:
        """Varsayılan BIST ve ABD sembolleri"""
        return [
            # BIST 30
            "SISE.IS", "EREGL.IS", "TUPRS.IS", "AKBNK.IS", "GARAN.IS",
            "THYAO.IS", "ASELS.IS", "KRDMD.IS", "BIMAS.IS", "SAHOL.IS",
            # ABD Tech
            "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META"
        ]
    
    async def connect(self):
        """Finnhub WebSocket bağlantısı"""
        try:
            # Finnhub WebSocket URL
            ws_url = f"wss://ws.finnhub.io?token={self.finnhub_api_key}"
            
            self.ws_connection = await websockets.connect(ws_url)
            self.is_connected = True
            logger.info("Finnhub WebSocket bağlandı")
            
            # Symbol subscription
            for symbol in self.symbols:
                subscribe_msg = {
                    "type": "subscribe",
                    "symbol": symbol
                }
                await self.ws_connection.send(json.dumps(subscribe_msg))
                logger.info(f"Subscribed to {symbol}")
                
        except Exception as e:
            logger.error(f"WebSocket bağlantı hatası: {e}")
            self.is_connected = False
            # Fallback to yfinance
            await self._start_yfinance_fallback()
    
    async def _start_yfinance_fallback(self):
        """yfinance fallback başlat"""
        logger.info("yfinance fallback başlatılıyor...")
        while not self.is_connected:
            try:
                await self._update_prices_yfinance()
                await asyncio.sleep(5)  # 5 saniyede bir güncelle
            except Exception as e:
                logger.error(f"yfinance fallback hatası: {e}")
                await asyncio.sleep(10)
    
    async def _update_prices_yfinance(self):
        """yfinance ile fiyat güncelleme"""
        try:
            for symbol in self.symbols:
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
                    
                    # Callback'leri çağır
                    await self._notify_callbacks(price_data)
                    
        except Exception as e:
            logger.error(f"yfinance güncelleme hatası: {e}")
    
    async def listen(self):
        """WebSocket mesajlarını dinle"""
        if not self.ws_connection:
            return
            
        try:
            async for message in self.ws_connection:
                try:
                    data = json.loads(message)
                    
                    if data.get('type') == 'trade':
                        trades = data.get('data', [])
                        for trade in trades:
                            symbol = trade.get('s')
                            price = trade.get('p')
                            volume = trade.get('v')
                            timestamp = trade.get('t')
                            
                            if symbol and price:
                                price_data = {
                                    'symbol': symbol,
                                    'price': price,
                                    'volume': volume,
                                    'timestamp': datetime.fromtimestamp(timestamp/1000).isoformat(),
                                    'source': 'finnhub_ws'
                                }
                                
                                self.price_cache[symbol] = price_data
                                self.last_update[symbol] = datetime.now()
                                
                                # Latency ölçümü
                                latency = (datetime.now() - datetime.fromtimestamp(timestamp/1000)).total_seconds() * 1000
                                if latency > 250:
                                    logger.warning(f"Yüksek latency: {latency:.2f}ms for {symbol}")
                                
                                # Callback'leri çağır
                                await self._notify_callbacks(price_data)
                                
                except json.JSONDecodeError:
                    logger.error("JSON decode hatası")
                except Exception as e:
                    logger.error(f"Mesaj işleme hatası: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket bağlantısı kapandı, yfinance fallback'e geçiliyor")
            self.is_connected = False
            await self._start_yfinance_fallback()
        except Exception as e:
            logger.error(f"WebSocket dinleme hatası: {e}")
    
    def add_callback(self, callback: Callable):
        """Fiyat güncellemeleri için callback ekle"""
        self.callbacks.append(callback)
    
    async def _notify_callbacks(self, price_data: Dict):
        """Tüm callback'leri çağır"""
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(price_data)
                else:
                    callback(price_data)
            except Exception as e:
                logger.error(f"Callback hatası: {e}")
    
    def get_price(self, symbol: str) -> Optional[Dict]:
        """Sembol için son fiyat bilgisi"""
        return self.price_cache.get(symbol)
    
    def get_all_prices(self) -> Dict:
        """Tüm fiyat bilgileri"""
        return self.price_cache.copy()
    
    def get_latency_stats(self) -> Dict:
        """Latency istatistikleri"""
        stats = {}
        for symbol, last_update in self.last_update.items():
            latency = (datetime.now() - last_update).total_seconds() * 1000
            stats[symbol] = {
                'latency_ms': latency,
                'last_update': last_update.isoformat(),
                'source': self.price_cache.get(symbol, {}).get('source', 'unknown')
            }
        return stats
    
    async def disconnect(self):
        """Bağlantıyı kapat"""
        if self.ws_connection:
            await self.ws_connection.close()
        self.is_connected = False
        logger.info("WebSocket bağlantısı kapatıldı")

# Test fonksiyonu
async def test_websocket():
    """WebSocket connector test"""
    # API key'i environment'tan al
    import os
    finnhub_key = os.getenv('FINNHUB_API_KEY', 'demo')
    
    connector = WebSocketConnector(finnhub_key)
    
    # Test callback
    def price_callback(price_data):
        print(f"🔄 Fiyat güncellendi: {price_data}")
    
    connector.add_callback(price_callback)
    
    try:
        await connector.connect()
        await connector.listen()
    except KeyboardInterrupt:
        print("\n🛑 Test durduruldu")
    finally:
        await connector.disconnect()

if __name__ == "__main__":
    asyncio.run(test_websocket())
