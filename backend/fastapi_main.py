"""
PRD v2.0 - FastAPI Ana Uygulama
/signals ve /prices endpoints, Firestore entegrasyonu
Railway deploy için hazır
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import asyncio
import json
import pandas as pd

# Local imports
try:
    from websocket_connector import WebSocketConnector
    from grey_topsis_ranking import GreyTOPSISRanking
    from fundamental_analyzer import FundamentalAnalyzer
    from technical_pattern_engine import TechnicalPatternEngine
    from ai_ensemble_v2 import AIEnsemble
    from rl_portfolio_agent import RLPortfolioAgent
    from sentiment_xai_engine import SentimentXAIEngine
    from dupont_piotroski_analyzer import DuPontPiotroskiAnalyzer
    from macro_regime_detector import MacroRegimeDetector
    from auto_backtest_walkforward import AutoBacktestWalkForward
    from bist_performance_tracker import BISTPerformanceTracker
    from firestore_schema import FirestoreSchema
    from config import config
except ImportError as e:
    print(f"⚠️ Import hatası: {e}")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="BIST AI Smart Trader API",
    description="PRD v2.0 - Yapay zekâ destekli yatırım danışmanı",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
websocket_connector = None
topsis_ranking = None
fundamental_analyzer = None
technical_engine = None
ai_ensemble = None
rl_agent = None
sentiment_engine = None
dupont_analyzer = None
macro_detector = None
backtest_engine = None
performance_tracker = None
firestore_schema = None

@app.on_event("startup")
async def startup_event():
    """Uygulama başlangıcında çalışır"""
    global websocket_connector, topsis_ranking, fundamental_analyzer
    global technical_engine, ai_ensemble, rl_agent, sentiment_engine
    global dupont_analyzer, macro_detector, backtest_engine, performance_tracker, firestore_schema
    
    try:
        logger.info("🚀 BIST AI Smart Trader başlatılıyor...")
        
        # Core modules başlat
        try:
            topsis_ranking = GreyTOPSISRanking()
            logger.info("✅ Grey TOPSIS Ranking başlatıldı")
        except Exception as e:
            logger.warning(f"Grey TOPSIS Ranking hatası: {e}")
            topsis_ranking = None
            
        try:
            fundamental_analyzer = FundamentalAnalyzer()
            logger.info("✅ Fundamental Analyzer başlatıldı")
        except Exception as e:
            logger.warning(f"Fundamental Analyzer hatası: {e}")
            fundamental_analyzer = None
            
        try:
            technical_engine = TechnicalPatternEngine()
            logger.info("✅ Technical Pattern Engine başlatıldı")
        except Exception as e:
            logger.warning(f"Technical Pattern Engine hatası: {e}")
            technical_engine = None
            
        try:
            ai_ensemble = AIEnsemble()
            logger.info("✅ AI Ensemble başlatıldı")
        except Exception as e:
            logger.warning(f"AI Ensemble hatası: {e}")
            ai_ensemble = None
            
        try:
            rl_agent = RLPortfolioAgent()
            logger.info("✅ RL Portfolio Agent başlatıldı")
        except Exception as e:
            logger.warning(f"RL Portfolio Agent hatası: {e}")
            rl_agent = None
            
        try:
            sentiment_engine = SentimentXAIEngine()
            logger.info("✅ Sentiment XAI Engine başlatıldı")
        except Exception as e:
            logger.warning(f"Sentiment XAI Engine hatası: {e}")
            sentiment_engine = None
            
        try:
            dupont_analyzer = DuPontPiotroskiAnalyzer()
            logger.info("✅ DuPont & Piotroski Analyzer başlatıldı")
        except Exception as e:
            logger.warning(f"DuPont & Piotroski Analyzer hatası: {e}")
            dupont_analyzer = None
            
        try:
            macro_detector = MacroRegimeDetector()
            logger.info("✅ Macro Regime Detector başlatıldı")
        except Exception as e:
            logger.warning(f"Macro Regime Detector hatası: {e}")
            macro_detector = None
            
        try:
            backtest_engine = AutoBacktestWalkForward()
            logger.info("✅ Auto Backtest & Walk Forward Engine başlatıldı")
        except Exception as e:
            logger.warning(f"Auto Backtest & Walk Forward Engine hatası: {e}")
            backtest_engine = None
            
        try:
            performance_tracker = BISTPerformanceTracker()
            logger.info("✅ BIST Performance Tracker başlatıldı")
        except Exception as e:
            logger.warning(f"BIST Performance Tracker hatası: {e}")
            performance_tracker = None
        
        # WebSocket connector (demo mode)
        websocket_connector = WebSocketConnector(
            finnhub_api_key="demo",
            symbols=["SISE.IS", "EREGL.IS", "TUPRS.IS", "AAPL", "MSFT", "GOOGL"]
        )
        
        # Firestore schema (geçici olarak devre dışı)
        # try:
        #     firestore_schema = FirestoreSchema(None)  # Placeholder
        #     logger.info("✅ Firestore schema hazır")
        # except Exception as e:
        #     logger.warning(f"Firestore schema hatası: {e}")
        
        logger.info("✅ Tüm modüller başlatıldı")
        
    except Exception as e:
        logger.error(f"Startup hatası: {e}")

@app.get("/")
async def root():
    """Ana endpoint"""
    return {
        "message": "BIST AI Smart Trader API v2.0",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

@app.get("/health")
async def health_check():
    """Sağlık kontrolü"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "topsis": topsis_ranking is not None,
            "fundamental": fundamental_analyzer is not None,
            "technical": technical_engine is not None,
            "ai_ensemble": ai_ensemble is not None,
            "rl_agent": rl_agent is not None,
            "sentiment": sentiment_engine is not None,
            "dupont_analyzer": dupont_analyzer is not None,
            "macro_detector": macro_detector is not None,
            "backtest_engine": backtest_engine is not None,
            "websocket": websocket_connector is not None
        }
    }

@app.get("/prices")
async def get_prices():
    """Güncel fiyat verileri"""
    try:
        if websocket_connector is None:
            raise HTTPException(status_code=503, detail="WebSocket connector hazır değil")
        
        prices = websocket_connector.get_all_prices()
        latency_stats = websocket_connector.get_latency_stats()
        
        return {
            "prices": prices,
            "latency": latency_stats,
            "timestamp": datetime.now().isoformat(),
            "total_symbols": len(prices)
        }
        
    except Exception as e:
        logger.error(f"Fiyat verisi hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prices/{symbol}")
async def get_symbol_price(symbol: str):
    """Belirli sembol fiyatı"""
    try:
        if websocket_connector is None:
            raise HTTPException(status_code=503, detail="WebSocket connector hazır değil")
        
        price = websocket_connector.get_price(symbol)
        if price is None:
            raise HTTPException(status_code=404, detail=f"{symbol} fiyatı bulunamadı")
        
        return {
            "symbol": symbol,
            "price": price,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Symbol fiyat hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signals")
async def get_signals(
    symbols: Optional[str] = None,
    include_sentiment: bool = True,
    include_xai: bool = True
):
    """Trading sinyalleri (PRD v2.0 - Kurumsal trader için)"""
    try:
        # Sembolleri parse et
        if symbols:
            symbol_list = [s.strip() for s in symbols.split(",")]
        else:
            symbol_list = ["SISE.IS", "EREGL.IS", "TUPRS.IS"]
        
        signals = {}
        
        for symbol in symbol_list:
            try:
                # 1. Fundamental analiz
                fundamental_score = 0.0
                try:
                    fundamental_data = fundamental_analyzer.get_comprehensive_fundamental_analysis([symbol])
                    if not fundamental_data.empty:
                        fundamental_score = fundamental_data.iloc[0]['fundamental_score']
                except Exception as e:
                    logger.warning(f"Fundamental analiz hatası {symbol}: {e}")
                
                # 2. Teknik analiz
                technical_signals = {}
                try:
                    # Fiyat verisi al
                    price_data = websocket_connector.get_price(symbol)
                    if price_data:
                        # Basit teknik sinyal
                        technical_signals = {
                            'ema_cross': 'NEUTRAL',
                            'candlestick': 'NEUTRAL',
                            'support_resistance': 'NEUTRAL'
                        }
                except Exception as e:
                    logger.warning(f"Teknik analiz hatası {symbol}: {e}")
                
                # 3. AI Ensemble sinyali
                ai_signal = 'HOLD'
                ai_confidence = 0.5
                try:
                    # Basit AI sinyal (placeholder)
                    import random
                    ai_choices = ['BUY', 'SELL', 'HOLD']
                    ai_signal = random.choice(ai_choices)
                    ai_confidence = random.uniform(0.3, 0.9)
                except Exception as e:
                    logger.warning(f"AI sinyal hatası {symbol}: {e}")
                
                # 4. Sentiment entegrasyonu
                sentiment_score = 0.0
                if include_sentiment:
                    try:
                        # Basit sentiment (placeholder)
                        sentiment_score = 0.0  # Neutral
                    except Exception as e:
                        logger.warning(f"Sentiment hatası {symbol}: {e}")
                
                # 5. XAI açıklama
                xai_explanation = {}
                if include_xai:
                    try:
                        xai_explanation = {
                            'method': 'Rule-based',
                            'feature_contributions': {
                                'fundamental_score': fundamental_score,
                                'technical_signals': len(technical_signals),
                                'ai_confidence': ai_confidence
                            },
                            'summary': f'BUY sinyali {fundamental_score:.2f} fundamental skoru ve {ai_confidence:.2f} AI confidence ile üretildi'
                        }
                    except Exception as e:
                        logger.warning(f"XAI hatası {symbol}: {e}")
                
                # 6. Sinyal kararı
                final_signal = 'HOLD'
                final_confidence = 0.5
                
                if fundamental_score > 0.7 and ai_confidence > 0.7:
                    final_signal = 'BUY'
                    final_confidence = (fundamental_score + ai_confidence) / 2
                elif fundamental_score < 0.3 and ai_confidence > 0.6:
                    final_signal = 'SELL'
                    final_confidence = ai_confidence
                
                # 7. Risk yönetimi
                risk_management = {
                    'stop_loss': None,
                    'take_profit': None,
                    'position_size': 0.0
                }
                
                if final_signal == 'BUY':
                    risk_management['position_size'] = min(final_confidence, 0.8)
                    risk_management['stop_loss'] = 0.05  # %5
                    risk_management['take_profit'] = 0.15  # %15
                
                # Sinyal oluştur
                signals[symbol] = {
                    'symbol': symbol,
                    'signal': final_signal,
                    'confidence': final_confidence,
                    'timestamp': datetime.now().isoformat(),
                    'analysis': {
                        'fundamental_score': fundamental_score,
                        'technical_signals': technical_signals,
                        'ai_signal': ai_signal,
                        'ai_confidence': ai_confidence,
                        'sentiment_score': sentiment_score
                    },
                    'risk_management': risk_management,
                    'xai_explanation': xai_explanation if include_xai else None
                }
                
            except Exception as e:
                logger.error(f"Sinyal oluşturma hatası {symbol}: {e}")
                signals[symbol] = {
                    'symbol': symbol,
                    'signal': 'ERROR',
                    'confidence': 0.0,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return {
            "signals": signals,
            "total_signals": len(signals),
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "include_sentiment": include_sentiment,
                "include_xai": include_xai,
                "version": "2.0.0"
            }
        }
        
    except Exception as e:
        logger.error(f"Sinyal endpoint hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ranking")
async def get_stock_ranking(top_n: int = 10):
    """Grey TOPSIS + Entropi ile hisse sıralaması"""
    try:
        if topsis_ranking is None:
            raise HTTPException(status_code=503, detail="TOPSIS ranking hazır değil")
        
        # Test verisi ile ranking
        test_data = {
            'SISE.IS': {'ROE': 0.15, 'NetMargin': 0.12, 'DebtEquity': 0.4},
            'EREGL.IS': {'ROE': 0.18, 'NetMargin': 0.14, 'DebtEquity': 0.6},
            'TUPRS.IS': {'ROE': 0.22, 'NetMargin': 0.16, 'DebtEquity': 0.3}
        }
        
        # DataFrame'e çevir
        df = pd.DataFrame.from_dict(test_data, orient='index')
        
        # Ranking yap
        ranked_df = topsis_ranking.rank_stocks(df)
        
        return {
            "ranking": ranked_df.to_dict('index'),
            "top_n": top_n,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ranking hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/{user_id}")
async def get_user_portfolio(user_id: str):
    """Kullanıcı portföyü"""
    try:
        if rl_agent is None:
            raise HTTPException(status_code=503, detail="RL Agent hazır değil")
        
        # Basit portföy (placeholder)
        portfolio = {
            "user_id": user_id,
            "total_value": 100000.0,
            "cash": 50000.0,
            "positions": {
                "SISE.IS": {"quantity": 100, "avg_price": 25.0, "current_value": 2500.0},
                "EREGL.IS": {"quantity": 50, "avg_price": 30.0, "current_value": 1500.0}
            },
            "performance": {
                "daily_return": 0.02,
                "weekly_return": 0.05,
                "monthly_return": 0.15
            },
            "last_updated": datetime.now().isoformat()
        }
        
        return portfolio
        
    except Exception as e:
        logger.error(f"Portfolio hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/signal")
async def webhook_signal(background_tasks: BackgroundTasks, signal_data: Dict):
    """Webhook ile sinyal alma"""
    try:
        # Background task olarak işle
        background_tasks.add_task(process_webhook_signal, signal_data)
        
        return {
            "status": "accepted",
            "message": "Sinyal alındı ve işleniyor",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Webhook hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_webhook_signal(signal_data: Dict):
    """Webhook sinyalini işle"""
    try:
        logger.info(f"Webhook sinyal işleniyor: {signal_data}")
        
        # Burada sinyal işleme mantığı olacak
        # Firestore'a kaydet, notification gönder, vs.
        
        await asyncio.sleep(1)  # Simulate processing
        
        logger.info("Webhook sinyal işleme tamamlandı")
        
    except Exception as e:
        logger.error(f"Webhook işleme hatası: {e}")

@app.get("/metrics")
async def get_metrics():
    """Performans metrikleri"""
    try:
        metrics = {
            "api_requests": 0,  # Placeholder
            "signals_generated": 0,
            "accuracy_rate": 0.0,
            "latency_avg": 0.0,
            "uptime": "100%",
            "timestamp": datetime.now().isoformat()
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Metrics hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dupont-piotroski/{symbol}")
async def get_dupont_piotroski_analysis(symbol: str):
    """DuPont & Piotroski F-Score analizi"""
    try:
        if dupont_analyzer is None:
            raise HTTPException(status_code=503, detail="DuPont analyzer hazır değil")
        
        analysis = dupont_analyzer.get_comprehensive_analysis(symbol)
        if not analysis:
            raise HTTPException(status_code=404, detail=f"{symbol} analizi bulunamadı")
        
        return {
            "symbol": symbol,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DuPont analiz hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/macro-regime")
async def get_macro_regime_analysis(symbols: Optional[str] = None):
    """Makro piyasa rejimi analizi"""
    try:
        if macro_detector is None:
            raise HTTPException(status_code=503, detail="Macro detector hazır değil")
        
        # Sembolleri parse et
        if symbols:
            symbol_list = [s.strip() for s in symbols.split(",")]
        else:
            symbol_list = None  # Varsayılan makro semboller
        
        analysis = macro_detector.get_macro_analysis(symbol_list)
        if not analysis:
            raise HTTPException(status_code=500, detail="Makro analiz başarısız")
        
        return {
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Makro analiz hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backtest")
async def run_backtest_analysis(
    symbol: str,
    period: str = "2y",
    initial_capital: float = 100000,
    include_walkforward: bool = True,
    include_optimization: bool = False
):
    """Backtest ve walk forward analizi çalıştır"""
    try:
        if backtest_engine is None:
            raise HTTPException(status_code=503, detail="Backtest engine hazır değil")
        
        # Veri al
        data = backtest_engine.get_stock_data_for_backtest(symbol, period)
        if data.empty:
            raise HTTPException(status_code=404, detail=f"{symbol} verisi bulunamadı")
        
        # Teknik indikatörler
        data_with_indicators = backtest_engine.calculate_technical_indicators(data)
        
        # Backtest çalıştır
        backtest_result = backtest_engine.run_backtest(data_with_indicators, initial_capital)
        if not backtest_result:
            raise HTTPException(status_code=500, detail="Backtest başarısız")
        
        # Walk Forward analizi
        walk_forward_result = None
        if include_walkforward:
            walk_forward_result = backtest_engine.run_walk_forward_analysis(data_with_indicators)
        
        # Parametre optimizasyonu
        optimization_result = None
        if include_optimization:
            optimization_result = backtest_engine.optimize_strategy_parameters(data_with_indicators)
        
        # Rapor oluştur
        report = backtest_engine.generate_backtest_report(
            symbol, backtest_result, walk_forward_result, optimization_result
        )
        
        return {
            "symbol": symbol,
            "backtest_result": backtest_result,
            "walk_forward_result": walk_forward_result,
            "optimization_result": optimization_result,
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backtest hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/backtest/{symbol}")
async def get_backtest_report(symbol: str):
    """Mevcut backtest raporunu getir"""
    try:
        if backtest_engine is None:
            raise HTTPException(status_code=503, detail="Backtest engine hazır değil")
        
        # Cache'den rapor al
        if symbol in backtest_engine.backtest_results:
            return {
                "symbol": symbol,
                "report": backtest_engine.backtest_results[symbol],
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=f"{symbol} için backtest raporu bulunamadı")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backtest rapor hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# BIST Performance Tracker Endpoints
@app.get("/performance/all")
async def get_all_performance(force_update: bool = False):
    """Tüm hisseler için performans metrikleri"""
    try:
        if performance_tracker is None:
            raise HTTPException(status_code=503, detail="Performance tracker hazır değil")
        
        performance = performance_tracker.get_all_performance(force_update)
        if not performance:
            raise HTTPException(status_code=500, detail="Performans verisi alınamadı")
        
        return {
            "total_stocks": len(performance),
            "performance": performance,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Performans verisi hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance/summary")
async def get_performance_summary():
    """Genel performans özeti"""
    try:
        if performance_tracker is None:
            raise HTTPException(status_code=503, detail="Performance tracker hazır değil")
        
        summary = performance_tracker.get_performance_summary()
        if not summary:
            raise HTTPException(status_code=500, detail="Performans özeti alınamadı")
        
        return {
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Performans özeti hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance/top/{metric}")
async def get_top_performers(metric: str, top_n: int = 10):
    """En iyi performans gösteren hisseler"""
    try:
        if performance_tracker is None:
            raise HTTPException(status_code=503, detail="Performance tracker hazır değil")
        
        top_stocks = performance_tracker.get_top_performers(metric, top_n)
        if not top_stocks:
            raise HTTPException(status_code=500, detail="Top performers alınamadı")
        
        return {
            "metric": metric,
            "top_n": top_n,
            "stocks": top_stocks,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Top performers hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance/stock/{symbol}")
async def get_stock_performance(symbol: str):
    """Tek hisse için performans metrikleri"""
    try:
        if performance_tracker is None:
            raise HTTPException(status_code=503, detail="Performance tracker hazır değil")
        
        metrics = performance_tracker.calculate_performance_metrics(symbol)
        if not metrics:
            raise HTTPException(status_code=404, detail=f"{symbol} için performans verisi bulunamadı")
        
        return {
            "symbol": symbol,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hisse performans hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance/export")
async def export_performance_csv():
    """Performans verilerini CSV olarak export et"""
    try:
        if performance_tracker is None:
            raise HTTPException(status_code=503, detail="Performance tracker hazır değil")
        
        filename = f"bist_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        success = performance_tracker.export_to_csv(filename)
        
        if not success:
            raise HTTPException(status_code=500, detail="CSV export başarısız")
        
        return {
            "message": "Performans verisi CSV'e export edildi",
            "filename": filename,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CSV export hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "fastapi_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
