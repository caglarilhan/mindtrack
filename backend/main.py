from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os
from market_data_service import MarketDataService

app = FastAPI(title="BIST AI Kazanç Asistanı API", version="1.0.0")

# CORS ayarları - Flutter app için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da domain'leri belirt
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Market data service instance
market_service = MarketDataService()

# WebSocket bağlantıları için connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Bağlantı kopmuşsa listeden çıkar
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Uygulama başlatıldığında market data servisi başlat"""
    asyncio.create_task(market_service.start_realtime_data())
    print("🚀 BIST AI Backend başlatıldı!")

@app.get("/")
async def root():
    return {
        "message": "BIST AI Kazanç Asistanı API", 
        "version": "1.0.0",
        "status": "🟢 Aktif"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "ws_connections": len(manager.active_connections)}

@app.get("/symbols")
async def get_tracked_symbols():
    """Takip edilen semboller listesi"""
    return {"symbols": market_service.tracked_symbols}

@app.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """Flutter app için canlı fiyat WebSocket"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/latest-signals")
async def get_latest_signals():
    """En son AI sinyalleri (Firestore'dan çek)"""
    try:
        signals = await market_service.get_latest_signals()
        return {"signals": signals, "count": len(signals)}
    except Exception as e:
        return {"error": str(e), "signals": []}

# Render için port ayarı
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
