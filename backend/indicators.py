import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volume import OnBalanceVolumeIndicator

# RSI Divergence (Basit versiyon: Fiyat yeni dip yaparken RSI daha yüksek dip yapıyor mu?)
def detect_rsi_bullish_divergence(df, rsi_period=14, lookback=20):
    rsi = RSIIndicator(df['close'], window=rsi_period).rsi()
    recent_lows = df['close'].rolling(window=lookback).min()
    recent_rsi_lows = rsi.rolling(window=lookback).min()
    # Son dipte fiyat yeni dip, RSI daha yüksek dip mi?
    if df['close'].iloc[-1] <= recent_lows.iloc[-2] and rsi.iloc[-1] > recent_rsi_lows.iloc[-2]:
        return True
    return False

# MACD Histogram Momentum Değişimi (Negatiften pozitife geçiş)
def detect_macd_bullish_momentum(df):
    macd = MACD(df['close'])
    hist = macd.macd_diff()
    # Son iki bar: histogram negatiften pozitife geçti mi?
    if hist.iloc[-2] < 0 and hist.iloc[-1] > 0:
        return True
    return False

# OBV Artış Sinyali (OBV son günlerde yükseliyor mu?)
def detect_obv_increase(df, lookback=5):
    obv = OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()
    return obv.iloc[-1] > obv.iloc[-lookback]

# VWAP fiyatın üstüne çıkma (Günlük veri için basit VWAP)
def detect_vwap_breakout(df):
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
    return df['close'].iloc[-1] > vwap.iloc[-1]

# Bullish Engulfing Mum Formasyonu
def detect_bullish_engulfing(df):
    if len(df) < 2:
        return False
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    return (prev['close'] < prev['open'] and curr['close'] > curr['open'] and
            curr['close'] > prev['open'] and curr['open'] < prev['close'])

# Morning Star Formasyonu
def detect_morning_star(df):
    if len(df) < 3:
        return False
    a, b, c = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    return (a['close'] < a['open'] and
            abs(b['close'] - b['open']) < (a['open'] - a['close']) * 0.5 and
            c['close'] > c['open'] and c['close'] > ((a['open'] + a['close']) / 2))

# Three White Soldiers Formasyonu
def detect_three_white_soldiers(df):
    if len(df) < 3:
        return False
    last3 = df.iloc[-3:]
    return all(row['close'] > row['open'] for _, row in last3.iterrows()) and \
           all(last3.iloc[i]['close'] > last3.iloc[i-1]['close'] for i in range(1, 3))

# Hacim Spike (Son bar, önceki N barın ortalamasının X katı mı?)
def detect_volume_spike(df, lookback=10, spike_ratio=2):
    avg_vol = df['volume'].iloc[-lookback-1:-1].mean()
    return df['volume'].iloc[-1] > avg_vol * spike_ratio 

def detect_bearish_engulfing(df):
    if len(df) < 2:
        return False
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    return (prev['close'] > prev['open'] and curr['close'] < curr['open'] and
            curr['open'] > prev['close'] and curr['close'] < prev['open'])

def detect_evening_star(df):
    if len(df) < 3:
        return False
    a, b, c = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    return (a['close'] > a['open'] and
            abs(b['close'] - b['open']) < (a['close'] - a['open']) * 0.5 and
            c['close'] < c['open'] and c['close'] < ((a['open'] + a['close']) / 2))

def detect_three_black_crows(df):
    if len(df) < 3:
        return False
    last3 = df.iloc[-3:]
    return all(row['close'] < row['open'] for _, row in last3.iterrows()) and \
           all(last3.iloc[i]['close'] < last3.iloc[i-1]['close'] for i in range(1, 3))

def detect_volume_drop(df, lookback=10, drop_ratio=0.5):
    avg_vol = df['volume'].iloc[-lookback-1:-1].mean()
    return df['volume'].iloc[-1] < avg_vol * drop_ratio

def detect_rsi_bearish(df, threshold=30):
    from ta.momentum import RSIIndicator
    rsi = RSIIndicator(df['close'], window=14).rsi()
    return rsi.iloc[-1] < threshold

def detect_macd_bearish(df):
    from ta.trend import MACD
    macd = MACD(df['close'])
    return macd.macd().iloc[-1] < 0 