import investpy
import logging
import pandas as pd
import ta
from datetime import datetime
from google.cloud import firestore
from indicators import (
    detect_rsi_bullish_divergence,
    detect_macd_bullish_momentum,
    detect_obv_increase,
    detect_vwap_breakout,
    detect_bullish_engulfing,
    detect_morning_star,
    detect_three_white_soldiers,
    detect_volume_spike
)
import yfinance as yf

from pymcdm import methods, weights, normalizations
import numpy as np

import firebase_admin
from firebase_admin import credentials, firestore

import json
import os

logger = logging.getLogger(__name__)

def fetch_prices_modular(symbols, source="yfinance", country="turkey"):
    """
    Modüler fiyat çekme fonksiyonu. source: 'yfinance', 'investpy' veya ileride 'finnhub'.
    country: 'turkey' (BIST) veya 'usa' (ABD borsaları) gibi.
    """
    prices = {}
    if source == "investpy":
        for sym in symbols:
            ticker = sym.replace(".IS", "")
            try:
                df = investpy.get_stock_recent_data(stock=ticker, country=country)
                if not df.empty:
                    last_price = float(df['Close'].iloc[-1])
                    prices[sym] = last_price
                    logger.info(f"{sym}: fiyat alındı - {last_price}")
                else:
                    logger.warning(f"{sym}: investpy boş DataFrame döndürdü")
            except Exception as e:
                logger.warning(f"{sym}: Investing.com veri hatası: {e}")
    elif source == "yfinance":
        for sym in symbols:
            yf_symbol = sym
            # BIST için .IS, ABD için direkt sembol (ör: AAPL, MSFT)
            if country == "turkey" and not sym.endswith(".IS"):
                yf_symbol = sym + ".IS"
            try:
                ticker = yf.Ticker(yf_symbol)
                df = ticker.history(period="1d", interval="5m")
                if not df.empty:
                    last_price = float(df['Close'].iloc[-1])
                    prices[sym] = last_price
                    logger.info(f"{sym}: yfinance fiyat alındı - {last_price}")
                else:
                    logger.warning(f"{sym}: yfinance boş DataFrame döndürdü")
            except Exception as e:
                logger.warning(f"{sym}: yfinance veri hatası: {e}")
    # Finnhub ve diğer kaynaklar ileride eklenebilir
    else:
        logger.error(f"Bilinmeyen veri kaynağı: {source}")
    return prices

# --- Teknik analiz ve sinyal üretimi ---
def detect_bullish_signals(symbols):
    db = firestore.Client()
    for sym in symbols:
        ticker = sym.replace(".IS", "")
        try:
            df = investpy.get_stock_recent_data(stock=ticker, country="turkey")
            if df.empty or len(df) < 50:
                continue
            # Kolon isimlerini normalize et
            df = df.rename(columns={
                'Close': 'close', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Volume': 'volume'
            })
            # Göstergeleri çalıştır
            results = {
                'rsi_divergence': detect_rsi_bullish_divergence(df),
                'macd_momentum': detect_macd_bullish_momentum(df),
                'obv_increase': detect_obv_increase(df),
                'vwap_breakout': detect_vwap_breakout(df),
                'bullish_engulfing': detect_bullish_engulfing(df),
                'morning_star': detect_morning_star(df),
                'three_white_soldiers': detect_three_white_soldiers(df),
                'volume_spike': detect_volume_spike(df)
            }
            true_signals = [k for k, v in results.items() if v]
            # En az 2 gösterge aynı anda sinyal veriyorsa
            if len(true_signals) >= 2:
                last = df.iloc[-1]
                signal = {
                    "symbol": sym,
                    "price": float(last['close']),
                    "signal": "BUY",
                    "confidence": 0.90 + 0.01 * (len(true_signals)-2),
                    "timestamp": datetime.now(),
                    "model": "MultiTA-8",
                    "reason": f"{', '.join(true_signals)} bullish sinyali",
                    "formation": "bullish",
                    "indicators": true_signals
                }
                logger.info(f"{sym}: Gelişmiş YÜKSELİŞ SİNYALİ! {signal}")
                db.collection('latest_signals').document(sym).set(signal)
        except Exception as e:
            logger.warning(f"{sym}: Teknik analiz/sinyal hatası: {e}")

def calculate_topsis_entropy_score(df, criteria_types):
    """
    df: Finansal oranlar DataFrame'i (satırlar: semboller, sütunlar: oranlar)
    criteria_types: np.array, 1=benefit, 0=cost
    """
    # Entropi ağırlık
    w = weights.entropy_weights(df.values)
    # TOPSIS skor
    topsis = methods.TOPSIS(normalization_function=normalizations.vector_normalization)
    score = topsis(df.values, w, criteria_types)
    return pd.Series(score, index=df.index)

def load_criteria_config(config_path="backend/criteria_config.json"):
    """
    Kriter isimleri ve tiplerini config dosyasından okur.
    Dönüş: (isim listesi, tip numpy array)
    """
    if not os.path.exists(config_path):
        logger.error(f"Kriter config dosyası bulunamadı: {config_path}")
        return [], np.array([])
    with open(config_path, "r") as f:
        config = json.load(f)
    names = [c["name"] for c in config["criteria"]]
    types = np.array([1 if c["type"] == "benefit" else 0 for c in config["criteria"]])
    return names, types

def fetch_financial_ratios_from_firestore(collection="financials", quarter="2024Q1", required_fields=None):
    """
    Firestore'dan belirtilen koleksiyondan finansal oranları çeker.
    Eksik/null alanları otomatik atar. DataFrame döndürür.
    required_fields: zorunlu oranlar listesi (örn. ["NetProfitMargin", "ROE", "DebtEquity"])
    """
    if required_fields is None:
        required_fields = ["NetProfitMargin", "ROE", "DebtEquity"]
    # Firestore bağlantısı
    try:
        cred = credentials.Certificate("/Users/caglarilhan/borsailhanos/backend/bist-backend-key.json")
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        logger.error(f"Firestore bağlantı hatası: {e}")
        return pd.DataFrame()
    # Veri çekme
    docs = db.collection(collection).where("quarter", "==", quarter).stream()
    records = []
    for doc in docs:
        data = doc.to_dict()
        symbol = data.get("symbol")
        if not symbol:
            continue
        # Null/eksik kontrolü
        if any(data.get(f) is None for f in required_fields):
            logger.warning(f"{symbol}: Eksik oran/alan, atlandı.")
            continue
        record = {f: data.get(f) for f in required_fields}
        record["symbol"] = symbol
        records.append(record)
    if not records:
        logger.error("Firestore'dan uygun veri çekilemedi!")
        return pd.DataFrame()
    df = pd.DataFrame(records).set_index("symbol")
    logger.info(f"{len(df)} şirketin oranları başarıyla çekildi.")
    return df

# Test fonksiyonu
if __name__ == "__main__":
    bist_symbols = ["SISE.IS", "THYAO.IS", "GARAN.IS"]
    print("BIST fiyatları (yfinance):")
    prices = fetch_prices_modular(bist_symbols, source="yfinance", country="turkey")
    for sym, price in prices.items():
        print(f"{sym}: {price}")

    us_symbols = ["AAPL", "MSFT", "TSLA"]
    print("\nABD fiyatları (yfinance):")
    us_prices = fetch_prices_modular(us_symbols, source="yfinance", country="usa")
    for sym, price in us_prices.items():
        print(f"{sym}: {price}")

    print("\n--- Kriter Config Okuma Testi ---")
    criteria_names, criteria_types = load_criteria_config()
    print("Kriterler:", criteria_names)
    print("Tipler:", criteria_types)

    print("\n--- TOPSIS + Entropi Skor Testi ---")
    # Örnek finansal oranlar
    data = {
        'NetProfitMargin': [12.3, 8.4, 15.2],
        'ROE': [18, 12, 22],
        'DebtEquity': [0.4, 0.8, 0.6]
    }
    symbols = ['SISE', 'EREGL', 'TUPRS']
    df = pd.DataFrame(data, index=symbols)
    # Kriter tipleri: 1=benefit, 0=cost
    # criteria_types = np.array([1, 1, 0]) # Bu satır artık load_criteria_config'dan alınacak
    scores = calculate_topsis_entropy_score(df, criteria_types)
    print(scores.sort_values(ascending=False))

    print("\n--- Firestore'dan Finansal Oran Çekme Testi (Config ile) ---")
    df = fetch_financial_ratios_from_firestore(required_fields=criteria_names)
    print(df.head())

    if not df.empty:
        print("\n--- TOPSIS + Entropi Skor (Config ile) ---")
        scores = calculate_topsis_entropy_score(df, criteria_types)
        print(scores.sort_values(ascending=False))
