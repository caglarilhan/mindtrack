from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from market_data_service import fetch_prices_modular, detect_bullish_signals
from news_sentiment_service import NewsSentimentService
from early_warning_engine import scan_and_write_early_warnings

app = FastAPI(title="BIST AI Kazanç Asistanı API", version="1.0.0")

# CORS ayarları - Flutter app için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

news_service = NewsSentimentService()

@app.on_event("startup")
async def startup_event():
    print("680 BIST AI Backend başlatıldı!")

@app.get("/")
async def root():
    return {
        "message": "BIST AI Kazanç Asistanı API",
        "version": "1.0.0",
        "status": "🟢 Aktif"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/price/{symbol}")
def get_price(symbol: str):
    prices = fetch_prices_modular([symbol])
    return { "symbol": symbol, "price": prices.get(symbol) }

@app.get("/api/news-sentiment")
async def get_news_sentiment(symbol: str, lang: str = "tr"):
    try:
        news_list = news_service.fetch_newsapi_headlines(symbol, lang=lang, max_results=10)
        sentiments = [news_service.analyze_sentiment(news, lang=lang) for news in news_list]
        if sentiments:
            avg_score = sum([s[1] for s in sentiments]) / len(sentiments)
            pos_count = sum([1 for s in sentiments if s[0] == "POSITIVE"])
            neg_count = sum([1 for s in sentiments if s[0] == "NEGATIVE"])
            neu_count = sum([1 for s in sentiments if s[0] == "NEUTRAL"])
        else:
            avg_score = 0.0
            pos_count = neg_count = neu_count = 0
        return {
            "symbol": symbol,
            "lang": lang,
            "news_count": len(news_list),
            "avg_sentiment_score": avg_score,
            "positive": pos_count,
            "negative": neg_count,
            "neutral": neu_count,
            "news_samples": news_list[:3]
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/detect-signals")
def detect_signals(mode: str = "technical"):
    symbols = [
        "THYAO.IS", "ASELS.IS", "KRDMD.IS", "TUPRS.IS", "EKGYO.IS",
        "SAHOL.IS", "VAKBN.IS", "BIMAS.IS", "EREGL.IS", "TKFEN.IS",
        "PGSUS.IS", "SISE.IS", "AKBNK.IS", "GARAN.IS", "HALKB.IS",
        "ISCTR.IS", "TCELL.IS", "ENKAI.IS", "KOZAL.IS", "FROTO.IS",
        "TAVHL.IS", "SOKM.IS", "TOASO.IS", "GUBRF.IS", "OYAKC.IS",
        "MGROS.IS", "ULKER.IS", "ARCLK.IS", "KOZAA.IS", "VESTL.IS"
    ]
    if mode == "early_warning":
        scan_and_write_early_warnings(symbols)
        return {"status": "ok", "message": "Erken uyarı skorları Firestore'a yazıldı."}
    else:
        detect_bullish_signals(symbols)
        return {"status": "ok", "message": "Yükseliş formasyonları tarandı ve sinyaller Firestore'a yazıldı."}

@app.post("/api/early-warning-scan")
def early_warning_scan():
    symbols = [
        "THYAO.IS", "ASELS.IS", "KRDMD.IS", "TUPRS.IS", "EKGYO.IS",
        "SAHOL.IS", "VAKBN.IS", "BIMAS.IS", "EREGL.IS", "TKFEN.IS",
        "PGSUS.IS", "SISE.IS", "AKBNK.IS", "GARAN.IS", "HALKB.IS",
        "ISCTR.IS", "TCELL.IS", "ENKAI.IS", "KOZAL.IS", "FROTO.IS",
        "TAVHL.IS", "SOKM.IS", "TOASO.IS", "GUBRF.IS", "OYAKC.IS",
        "MGROS.IS", "ULKER.IS", "ARCLK.IS", "KOZAA.IS", "VESTL.IS"
    ]
    scan_and_write_early_warnings(symbols)
    return {"status": "ok", "message": "Erken uyarı skorları Firestore'a yazıldı."}

# Render için port ayarı
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
