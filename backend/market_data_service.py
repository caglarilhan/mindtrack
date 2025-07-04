import asyncio
import json
import os
from datetime import datetime
from google.cloud import firestore
import yfinance as yf
from typing import List, Dict

class MarketDataService:
    def __init__(self):
        # BIST'te en popüler 30 sembol (volume bazlı)
        self.tracked_symbols = [
            "THYAO.IS", "ASELS.IS", "KRDMD.IS", "TUPRS.IS", "EKGYO.IS",
            "SAHOL.IS", "VAKBN.IS", "BIMAS.IS", "EREGL.IS", "TKFEN.IS",
            "PGSUS.IS", "SISE.IS", "AKBNK.IS", "GARAN.IS", "HALKB.IS",
            "ISCTR.IS", "TCELL.IS", "ENKAI.IS", "KOZAL.IS", "FROTO.IS",
            "TAVHL.IS", "SOKM.IS", "TOASO.IS", "GUBRF.IS", "OYAKC.IS",
            "MGROS.IS", "ULKER.IS", "ARCLK.IS", "KOZAA.IS", "VESTL.IS"
        ]
        
        # Firestore client
        self.db = None
        self.init_firestore()
        
        # Son fiyatlar cache
        self.latest_prices = {}
        
    def init_firestore(self):
        """Firestore client başlat"""
        try:
            self.db = firestore.Client()
            print("✅ Firestore bağlantısı kuruldu")
        except Exception as e:
            print(f"❌ Firestore bağlantı hatası: {e}")
            self.db = None

    async def start_realtime_data(self):
        """Canlı veri akışını başlat"""
        await asyncio.gather(
            self.start_yfinance_polling(),  # yfinance ile REST polling
            self.start_signal_generator()   # AI sinyal üretici (mock)
        )

    async def start_yfinance_polling(self):
        """yfinance ile 30 saniyede bir fiyat çek"""
        while True:
            try:
                # 5'er sembol gruplar halinde çek (rate limit için)
                for i in range(0, len(self.tracked_symbols), 5):
                    batch = self.tracked_symbols[i:i+5]
                    await self.fetch_batch_prices(batch)
                    await asyncio.sleep(2)  # Batch'ler arası 2 saniye bekle
                
                print(f"📊 {len(self.tracked_symbols)} sembol fiyatı güncellendi")
                await asyncio.sleep(30)  # 30 saniye bekle
                
            except Exception as e:
                print(f"❌ Fiyat çekme hatası: {e}")
                await asyncio.sleep(60)  # Hata durumunda 1 dakika bekle

    async def fetch_batch_prices(self, symbols: List[str]):
        """Belirli sembollerin fiyatlarını çek ve Firestore'a yaz"""
        try:
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                info = ticker.history(period="1d", interval="1m")
                
                if not info.empty:
                    latest = info.iloc[-1]
                    price_data = {
                        "symbol": symbol,
                        "price": float(latest['Close']),
                        "volume": int(latest['Volume']),
                        "timestamp": datetime.now(),
                        "change": 0.0,  # TODO: Önceki kapanışa göre hesapla
                        "change_percent": 0.0
                    }
                    
                    # Cache'e kaydet
                    self.latest_prices[symbol] = price_data
                    
                    # Firestore'a yaz
                    if self.db:
                        await self.save_price_to_firestore(price_data)
                        
        except Exception as e:
            print(f"❌ Batch fiyat hatası: {e}")

    async def save_price_to_firestore(self, price_data: Dict):
        """Fiyat verisini Firestore'a kaydet"""
        try:
            # raw_prices koleksiyonuna yaz
            doc_ref = self.db.collection('raw_prices').add(price_data)
            
            # latest_prices koleksiyonuna da güncel fiyatı yaz
            latest_ref = self.db.collection('latest_prices').document(price_data['symbol'])
            latest_ref.set(price_data)
            
        except Exception as e:
            print(f"❌ Firestore yazma hatası: {e}")

    async def start_signal_generator(self):
        """AI sinyal üretici (şimdilik mock - SPRINT-1'de gerçek AI gelecek)"""
        while True:
            try:
                await asyncio.sleep(120)  # 2 dakikada bir sinyal üret
                
                # Rastgele 3-5 sembol seç ve mock sinyal üret
                import random
                selected_symbols = random.sample(self.tracked_symbols, random.randint(3, 5))
                
                for symbol in selected_symbols:
                    signal = self.generate_mock_signal(symbol)
                    await self.save_signal_to_firestore(signal)
                    
                print(f"🤖 {len(selected_symbols)} mock AI sinyali üretildi")
                
            except Exception as e:
                print(f"❌ Sinyal üretme hatası: {e}")
                await asyncio.sleep(300)  # Hata durumunda 5 dakika bekle

    def generate_mock_signal(self, symbol: str) -> Dict:
        """Mock AI sinyali üret (SPRINT-1'de gerçek LightGBM gelecek)"""
        import random
        
        signal_types = ["BUY", "SELL", "HOLD"]
        signal_type = random.choice(signal_types)
        
        # BUY/SELL için mock confidence
        confidence = random.uniform(0.6, 0.95) if signal_type != "HOLD" else random.uniform(0.4, 0.7)
        
        return {
            "symbol": symbol,
            "signal": signal_type,
            "confidence": round(confidence, 3),
            "timestamp": datetime.now(),
            "model": "MockLGBM_v0.1",
            "price": self.latest_prices.get(symbol, {}).get("price", 0.0),
            "reason": f"Mock {signal_type} sinyali - RSI ve MACD bazlı",
            "sl_percent": round(random.uniform(3, 8), 1) if signal_type == "BUY" else 0,
            "tp_percent": round(random.uniform(8, 15), 1) if signal_type == "BUY" else 0
        }

    async def save_signal_to_firestore(self, signal: Dict):
        """AI sinyalini Firestore'a kaydet"""
        try:
            if self.db:
                # signals koleksiyonuna yaz
                self.db.collection('signals').add(signal)
                
                # latest_signals koleksiyonuna da güncel sinyali yaz
                latest_ref = self.db.collection('latest_signals').document(signal['symbol'])
                latest_ref.set(signal)
                
        except Exception as e:
            print(f"❌ Sinyal kaydetme hatası: {e}")

    async def get_latest_signals(self) -> List[Dict]:
        """En son sinyalleri Firestore'dan çek"""
        try:
            if not self.db:
                return []
                
            signals_ref = self.db.collection('latest_signals')
            docs = signals_ref.stream()
            
            signals = []
            for doc in docs:
                signal_data = doc.to_dict()
                # Timestamp'ı string'e çevir (JSON serializable)
                if 'timestamp' in signal_data:
                    signal_data['timestamp'] = signal_data['timestamp'].isoformat()
                signals.append(signal_data)
                
            return signals
            
        except Exception as e:
            print(f"❌ Sinyal çekme hatası: {e}")
            return []
