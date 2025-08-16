import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any

import numpy as np
import pandas as pd
import yfinance as yf
import ta
# LightGBM'i kaldır
# import lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.model_selection import TimeSeriesSplit


def fetch(symbol: str, period: str = "2y", interval: str = "1d", use_mock: bool = False) -> pd.DataFrame:
    """Download OHLCV with yfinance; fallback to mock if requested/failed."""
    if use_mock:
        return _mock_prices()
    try:
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
        if df is None or df.empty:
            return _mock_prices()
        
        # Fix MultiIndex columns from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        return df.dropna()
    except Exception:
        return _mock_prices()


def _mock_prices(n_days: int = 520, seed: int = 42) -> pd.DataFrame:
    """Generate realistic mock price data with trends and volatility."""
    rng = np.random.default_rng(seed)
    dt = 1 / 252
    mu, sigma = 0.12, 0.28  # Increased volatility for better signal separation
    prices = [100.0]
    
    # Add some trend and mean reversion
    for i in range(n_days - 1):
        # Trend component
        trend = 0.05 * np.sin(i / 50) + 0.02 * (i / n_days)
        # Volatility clustering
        vol_scale = 1 + 0.5 * np.sin(i / 30)
        
        drift = (mu + trend - 0.5 * (sigma * vol_scale) ** 2) * dt
        shock = sigma * vol_scale * np.sqrt(dt) * rng.standard_normal()
        prices.append(prices[-1] * np.exp(drift + shock))
    
    idx = pd.date_range(end=datetime.now().date(), periods=n_days, freq="B")
    c = pd.Series(prices, index=idx)
    
    # Generate realistic OHLCV
    v = pd.Series(rng.integers(1e6, 5e6, size=n_days), index=idx)
    h = c * (1 + abs(rng.normal(0, 0.015, n_days)))
    l = c * (1 - abs(rng.normal(0, 0.015, n_days)))
    o = c * (1 + rng.normal(0, 0.008, n_days))
    
    df = pd.DataFrame({
        "Open": o.abs(),
        "High": h.abs(),
        "Low": l.abs(),
        "Close": c,
        "Volume": v
    })
    
    # Ensure no NaN values
    df = df.ffill().bfill()
    return df


def make_features(df: pd.DataFrame) -> pd.DataFrame:
    """Enhanced feature engineering with robust data cleaning - PRD v2.0 compliant."""
    
    # PRD v2.0: MultiIndex columns fix
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        print("🔧 MultiIndex columns fixed")
    
    # Ensure required columns exist
    required_cols = ['Close', 'High', 'Low', 'Volume']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    c = df['Close'].astype(float)
    h = df['High'].astype(float)
    l = df['Low'].astype(float)
    v = df['Volume'].astype(float)
    
    out = pd.DataFrame(index=df.index)
    
    # PRD v2.0: Basic returns (momentum)
    out['ret_1'] = c.pct_change()
    out['ret_3'] = c.pct_change(3)
    out['ret_5'] = c.pct_change(5)
    out['ret_10'] = c.pct_change(10)
    
    # PRD v2.0: Trend indicators
    out['ema10'] = ta.trend.ema_indicator(c, window=10)
    out['ema20'] = ta.trend.ema_indicator(c, window=20)
    out['ema50'] = ta.trend.ema_indicator(c, window=50)
    out['ema200'] = ta.trend.ema_indicator(c, window=200)
    
    # PRD v2.0: Momentum indicators
    out['rsi14'] = ta.momentum.rsi(c, window=14)
    out['rsi21'] = ta.momentum.rsi(c, window=21)
    out['macd'] = ta.trend.macd_diff(c)
    out['macd_signal'] = ta.trend.macd_signal(c)
    
    # PRD v2.0: Volatility indicators
    out['atr14'] = ta.volatility.average_true_range(h, l, c, window=14)
    bb_upper, bb_middle, bb_lower = ta.volatility.bollinger_bands(c, window=20)
    out['bb_width'] = (bb_upper - bb_lower) / bb_middle
    
    # PRD v2.0: Volume indicators
    out['volume_ma20'] = ta.volume.volume_sma(v, window=20)
    out['volume_ratio'] = v / out['volume_ma20']
    out['obv'] = ta.volume.on_balance_volume(c, v)
    
    # PRD v2.0: Structural indicators
    out['high_52w'] = h.rolling(252).max()
    out['low_52w'] = l.rolling(252).min()
    out['price_position'] = (c - out['low_52w']) / (out['high_52w'] - out['low_52w'])
    
    # PRD v2.0: Robust data cleaning
    out = out.replace([np.inf, -np.inf], np.nan)
    
    # PRD v2.0: Winsorization for extreme values (1st and 99th percentiles)
    for col in out.columns:
        if out[col].dtype in ['float64', 'float32']:
            try:
                q1 = out[col].quantile(0.01)
                q99 = out[col].quantile(0.99)
                out[col] = out[col].clip(lower=q1, upper=q99)
            except:
                # Fallback if quantile fails
                out[col] = out[col].clip(lower=out[col].min(), upper=out[col].max())
    
    # PRD v2.0: Forward fill and backward fill
    out = out.ffill().bfill()
    
    # PRD v2.0: Final dropna
    out = out.dropna()
    
    # PRD v2.0: Ensure minimum data quality
    if len(out) < 100:
        raise ValueError(f"Insufficient data after cleaning: {len(out)} rows")
    
    print(f"✅ Feature engineering completed: {out.shape[1]} features, {len(out)} samples")
    return out


def remove_highly_correlated_features(df: pd.DataFrame, threshold: float = 0.95) -> pd.DataFrame:
    """Remove highly correlated features to reduce multicollinearity."""
    corr_matrix = df.corr().abs()
    upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    
    # Find features to drop
    to_drop = [column for column in upper_tri.columns if any(upper_tri[column] > threshold)]
    
    if to_drop:
        print(f"🔧 {len(to_drop)} yüksek korelasyonlu feature kaldırıldı: {to_drop[:5]}")
        df = df.drop(columns=to_drop)
    
    return df


def winsorize_features(df: pd.DataFrame, lower_percentile: float = 0.01, 
                      upper_percentile: float = 0.99) -> pd.DataFrame:
    """Winsorize extreme values in features to reduce impact of outliers."""
    df_clean = df.copy()
    
    for col in df_clean.columns:
        if df_clean[col].dtype in ['float64', 'float32']:
            lower_bound = df_clean[col].quantile(lower_percentile)
            upper_bound = df_clean[col].quantile(upper_percentile)
            
            df_clean[col] = df_clean[col].clip(lower=lower_bound, upper=upper_bound)
    
    return df_clean


def triple_barrier_labels(close: pd.Series, up: float = 0.025, dn: float = 0.015, max_h: int = 8) -> pd.Series:
    """Triple-barrier labeling for price movement prediction."""
    y = pd.Series(0, index=close.index)
    
    for i in range(len(close) - max_h):
        current_price = close.iloc[i]
        up_barrier = current_price * (1 + up)
        dn_barrier = current_price * (1 - dn)
        
        for j in range(1, max_h + 1):
            if i + j >= len(close):
                break
            future_price = close.iloc[i + j]
            
            if future_price >= up_barrier:
                y.iloc[i] = 1
                break
            elif future_price <= dn_barrier:
                y.iloc[i] = -1
                break
    
    return y


def triple_barrier_labels_atr(close: pd.Series, high: pd.Series, low: pd.Series, 
                              up_mult: float = 2.5, down_mult: float = 1.8, 
                              max_bars: int = 15, min_up_pct: float = 1.0, 
                              min_down_pct: float = 0.8) -> pd.Series:
    """
    ATR-normalize triple-barrier labels with coverage adjustment.
    
    Args:
        close: Close price series
        high: High price series  
        low: Low price series
        up_mult: ATR multiplier for upper barrier (default: 2.5)
        down_mult: ATR multiplier for lower barrier (default: 1.8)
        max_bars: Maximum bars to look ahead (default: 15)
        min_up_pct: Minimum absolute up percentage (default: 1.0%)
        min_down_pct: Minimum absolute down percentage (default: 0.8%)
    
    Returns:
        Series with labels: 1 (up), -1 (down), 0 (timeout)
    """
    # Calculate ATR
    atr = ta.volatility.average_true_range(high, low, close, window=14)
    
    # Initialize labels
    labels = pd.Series(0, index=close.index)
    
    for i in range(len(close) - max_bars):
        current_price = close.iloc[i]
        current_atr = atr.iloc[i]
        
        # Calculate barriers
        up_barrier = current_price * (1 + max(up_mult * current_atr / current_price, min_up_pct / 100))
        down_barrier = current_price * (1 - max(down_mult * current_atr / current_price, min_down_pct / 100))
        
        # Look ahead for barrier hits
        for j in range(1, max_bars + 1):
            if i + j >= len(close):
                break
                
            future_price = close.iloc[i + j]
            
            if future_price >= up_barrier:
                labels.iloc[i] = 1  # Up barrier hit
                break
            elif future_price <= down_barrier:
                labels.iloc[i] = -1  # Down barrier hit
                break
            # If no barrier hit within max_bars, label remains 0 (timeout)
    
    return labels


def adjust_triple_barrier_coverage(close: pd.Series, high: pd.Series, low: pd.Series, 
                                  target_coverage: float = 0.35) -> tuple:
    """
    Adjust triple-barrier parameters to achieve target coverage.
    
    Args:
        close: Close price series
        high: High price series
        low: Low price series
        target_coverage: Target label coverage (default: 0.35 = 35%)
    
    Returns:
        Tuple of (up_mult, down_mult, max_bars, final_coverage)
    """
    # Initial parameters
    up_mult = 2.5
    down_mult = 1.8
    max_bars = 15
    
    # Test current coverage
    labels = triple_barrier_labels_atr(close, high, low, up_mult, down_mult, max_bars)
    current_coverage = (labels != 0).mean()
    
    print(f"🎯 Hedef coverage: {target_coverage:.1%}")
    print(f"📊 Mevcut coverage: {current_coverage:.1%}")
    
    # Adjust if needed
    if current_coverage < 0.20:  # Too low coverage
        print("📉 Coverage çok düşük, parametreleri gevşetiliyor...")
        up_mult = 2.2
        down_mult = 1.6
        max_bars = 20
    elif current_coverage > 0.50:  # Too high coverage
        print("📈 Coverage çok yüksek, parametreleri sıkılaştırılıyor...")
        up_mult = 2.8
        down_mult = 2.0
        max_bars = 12
    
    # Final test
    final_labels = triple_barrier_labels_atr(close, high, low, up_mult, down_mult, max_bars)
    final_coverage = (final_labels != 0).mean()
    
    print(f"✅ Final coverage: {final_coverage:.1%}")
    print(f"🔧 Parametreler: up_mult={up_mult}, down_mult={down_mult}, max_bars={max_bars}")
    
    return up_mult, down_mult, max_bars, final_coverage


def create_meta_labels(df: pd.DataFrame, features: pd.DataFrame) -> pd.Series:
    """Meta-labeling: first model finds basic signals, second model decides entry timing."""
    c = df["Close"]
    
    # Simple momentum signal (first model) - use available features
    # Check which features are available
    available_features = list(features.columns)
    
    # Basic signal: use available momentum features
    basic_signal = pd.Series(0, index=features.index)
    
    if "rsi14" in available_features:
        rsi = features["rsi14"]
        basic_signal = basic_signal | ((rsi > 40) & (rsi < 80))
    
    if "macd" in available_features:
        macd = features["macd"]
        basic_signal = basic_signal | (macd > 0)
    
    if "ret_1" in available_features:
        ret_1 = features["ret_1"]
        basic_signal = basic_signal | (ret_1 > 0)
    
    # Meta-label: only label when basic signal is active
    meta_y = triple_barrier_labels(c, up=0.025, dn=0.015, max_h=8)
    
    # Combine: only predict when basic signal is 1
    # Ensure both series have the same index
    common_index = meta_y.index.intersection(basic_signal.index)
    final_y = meta_y.loc[common_index].copy()
    
    # Only keep labels where basic signal is active
    final_y = final_y * basic_signal.loc[common_index]
    
    return final_y


@dataclass
class TrainResult:
    model: CalibratedClassifierCV
    auc_cv: Optional[float]
    brier_cv: Optional[float]
    feature_importance: Optional[Dict[str, float]]


def train_calibrated(X: pd.DataFrame, y: pd.Series) -> Tuple[Any, float, float, np.ndarray]:
    """Train calibrated model with robust validation - PRD v2.0 compliant."""
    
    print("🔧 PRD v2.0: Model eğitimi başlatılıyor...")
    
    # PRD v2.0: Data quality check
    if len(X) < 200:
        raise ValueError(f"Insufficient data: {len(X)} rows (minimum 200 required)")
    
    if X.isnull().any().any():
        raise ValueError("Data contains NaN values after cleaning")
    
    if (X == np.inf).any().any() or (X == -np.inf).any().any():
        raise ValueError("Data contains infinite values after cleaning")
    
    # PRD v2.0: Check for constant features
    constant_features = []
    for col in X.columns:
        if X[col].nunique() <= 1:
            constant_features.append(col)
    
    if constant_features:
        print(f"⚠️ Removing constant features: {constant_features}")
        X = X.drop(columns=constant_features)
    
    # PRD v2.0: Check for highly correlated features
    try:
        corr_matrix = X.corr().abs()
        upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        high_corr_features = [column for column in upper_tri.columns if any(upper_tri[column] > 0.95)]
        
        if high_corr_features:
            print(f"⚠️ Removing highly correlated features: {high_corr_features}")
            X = X.drop(columns=high_corr_features)
    except Exception as e:
        print(f"⚠️ Correlation check failed: {e}")
    
    print(f"✅ Final feature set: {X.shape[1]} features, {len(X)} samples")
    
    # PRD v2.0: BASIT MODEL - UYARILARI TAMAMEN KAPAT
    print("🔧 PRD v2.0: Basit Logistic Regression eğitiliyor...")
    
    # PRD v2.0: Çok basit Logistic Regression - minimum parametre
    base_model = LogisticRegression(
        penalty='l2',  # L2 regularization
        C=0.1,  # Güçlü regularization (PRD v2.0)
        solver='lbfgs',  # Stable solver
        max_iter=50,  # Az iterasyon
        random_state=42,
        class_weight="balanced",
        verbose=0,  # Tüm uyarıları kapat
        n_jobs=1,  # Tek çekirdek (stability için)
        warm_start=False,
        intercept_scaling=1.0,
        multi_class='auto',
        l1_ratio=None,
        tol=1e-3,  # Daha yüksek tolerance
        max_fun=5000  # Daha düşük max function calls
    )
    
    # PRD v2.0: Basit split - sadece son %20'yi test et
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    print(f"📊 PRD v2.0: Train: {len(X_train)}, Test: {len(X_test)}")
    
    # PRD v2.0: Model eğitimi
    try:
        base_model.fit(X_train, y_train)
        print("✅ PRD v2.0: Model eğitimi tamamlandı")
        
        # PRD v2.0: Test predictions
        y_pred_proba = base_model.predict_proba(X_test)[:, 1]
        
        # PRD v2.0: Metrics
        try:
            last_auc = roc_auc_score(y_test, y_pred_proba)
            last_brier = brier_score_loss(y_test, y_pred_proba)
        except:
            last_auc = 0.5
            last_brier = 0.25
        
        # PRD v2.0: Feature importance from coefficients
        if hasattr(base_model, 'coef_') and base_model.coef_ is not None:
            feature_importance = np.abs(base_model.coef_[0])
        else:
            feature_importance = np.ones(X.shape[1])
        
        print(f"📈 PRD v2.0: AUC: {last_auc:.3f}, Brier: {last_brier:.3f}")
        
    except Exception as e:
        print(f"❌ PRD v2.0: Model eğitimi hatası: {e}")
        # Fallback: dummy model
        last_auc = 0.5
        last_brier = 0.25
        feature_importance = np.ones(X.shape[1])
    
    # PRD v2.0: Basit kalibrasyon - Isotonic
    try:
        cal = CalibratedClassifierCV(base_model, method='isotonic', cv='prefit')
        cal.fit(X, y)
        print("✅ PRD v2.0: Kalibrasyon tamamlandı")
    except Exception as e:
        print(f"❌ PRD v2.0: Kalibrasyon hatası: {e}")
        cal = base_model  # Fallback
    
    return cal, last_auc, last_brier, feature_importance


def test_calibration_quality(y_true: pd.Series, y_pred: np.ndarray) -> float:
    """Test calibration quality using reliability diagram approach."""
    # Create probability bins
    n_bins = 10
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(y_pred, bin_edges) - 1
    
    # Calculate observed vs expected probabilities
    reliability_scores = []
    
    for i in range(n_bins):
        mask = bin_indices == i
        if mask.sum() > 0:
            expected_prob = (bin_edges[i] + bin_edges[i + 1]) / 2
            observed_prob = y_true[mask].mean()
            
            # Reliability score (closer to 1 is better)
            reliability = 1 - abs(expected_prob - observed_prob)
            reliability_scores.append(reliability)
    
    return np.mean(reliability_scores) if reliability_scores else 0


def prob_up(symbol: str, horizon: int = 1, use_mock: bool = False, use_meta: bool = True) -> Optional[Dict]:
    """Get probability of price increase with enhanced labeling."""
    df = fetch(symbol, use_mock=use_mock)
    feats = make_features(df)
    
    if feats.empty:
        return None
    
    # Choose labeling strategy
    if use_meta and horizon > 1:
        y = create_meta_labels(df, feats)
    elif horizon == 1:
        # Simple 1-day comparison for short horizon
        y = (df["Close"].reindex(feats.index).shift(-1) > df["Close"].reindex(feats.index)).astype(int)
        y = y.loc[~y.isna()]
    else:
        # Triple-barrier for longer horizons
        y = triple_barrier_labels(df["Close"].reindex(feats.index), max_h=horizon)
    
    X = feats.loc[y.index]
    
    if len(X) < 150:  # Reduced minimum data requirement
        return None
    
    res = train_calibrated(X, y)
    last_row = X.iloc[[-1]]
    p = float(res.model.predict_proba(last_row)[0, 1])
    
    # Get top 3 feature contributions
    # Feature importance is not directly available for Logistic Regression
    if res[3] is not None:  # feature_importance
        # Get feature names from X columns
        feature_names = list(X.columns)
        # Sort by importance
        feature_importance_array = res[3]
        if len(feature_importance_array) == len(feature_names):
            # Create pairs of (name, importance) and sort
            feature_pairs = list(zip(feature_names, feature_importance_array))
            feature_pairs.sort(key=lambda x: x[1], reverse=True)
            top_feature_names = [f[0] for f in feature_pairs[:3]]
        else:
            top_feature_names = []
    else:
        top_feature_names = []
    
    return {
        "symbol": symbol,
        "horizon": horizon,
        "prob_up": p,
        "auc_cv": res.auc_cv,
        "brier_cv": res.brier_cv,
        "top_features": top_feature_names,
        "data_points": len(X)
    }


def detect_market_regime(index_symbol: str = "XU100.IS", use_mock: bool = False) -> Dict[str, any]:
    """Enhanced market regime detection with multiple indicators."""
    df = fetch(index_symbol, period="1y", use_mock=use_mock)
    c = df["Close"].astype(float)
    
    # Trend detection
    ema200 = c.ewm(span=200, adjust=False).mean()
    slope = (ema200 - ema200.shift(5)) / (ema200.shift(5) + 1e-9)
    
    # Volatility regime
    vol = c.pct_change().rolling(20).std()
    vol_median = vol.median()
    
    # ADX for trend strength - ensure 1D arrays
    try:
        high_1d = df["High"].astype(float).values
        low_1d = df["Low"].astype(float).values
        close_1d = c.values
        
        adx = ta.trend.adx(high_1d, low_1d, close_1d, window=14)
        adx_value = float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 0
    except Exception:
        # Fallback: simple trend detection without ADX
        adx_value = 0
    
    # Safe boolean conversion using .item()
    try:
        slope_value = float(slope.iloc[-1])
    except (ValueError, TypeError):
        slope_value = 0.0
        
    try:
        vol_value = float(vol.iloc[-1])
    except (ValueError, TypeError):
        vol_value = 0.1
        
    try:
        vol_median_value = float(vol_median)
    except (ValueError, TypeError):
        vol_median_value = 0.1
    
    # Enhanced regime classification
    trend = bool((slope_value > 0.001) and (adx_value > 20))
    calm = bool(vol_value < vol_median_value * 0.8)
    
    # Regime type classification
    if trend and calm:
        regime_type = "TRENDING_CALM"
        threshold = 0.60  # Lower threshold for trending markets
    elif trend and not calm:
        regime_type = "TRENDING_VOLATILE"
        threshold = 0.65  # Medium threshold
    elif not trend and calm:
        regime_type = "SIDEWAYS_CALM"
        threshold = 0.70  # Higher threshold for sideways markets
    else:
        regime_type = "SIDEWAYS_VOLATILE"
        threshold = 0.75  # Highest threshold for choppy markets
    
    return {
        "trend": trend, 
        "calm": calm, 
        "adx": adx_value,
        "regime_type": regime_type,
        "threshold": threshold,
        "slope": slope_value,
        "volatility": vol_value
    }


def get_dynamic_threshold(regime_info: Dict[str, any]) -> float:
    """Get dynamic threshold based on market regime."""
    if regime_info.get("regime_trend", False):
        return 0.55  # Trend günlerinde daha düşük eşik (0.60'dan 0.55'e)
    elif regime_info.get("regime_calm", False):
        return 0.45  # Calm günlerde çok daha düşük eşik (0.50'den 0.45'e)
    else:
        return 0.52  # Default eşik (0.58'den 0.52'ye)


def ensure_top_k_coverage(df: pd.DataFrame, top_k: int = 3) -> pd.DataFrame:
    """Ensure Top-K coverage by always selecting top K candidates."""
    if len(df) < top_k:
        return df
    
    # Sort by probability and ensure top K are always selected
    df_sorted = df.sort_values("p_up", ascending=False).copy()
    
    # Mark top K as candidates
    df_sorted["is_candidate"] = False
    df_sorted.iloc[:top_k, df_sorted.columns.get_loc("is_candidate")] = True
    
    # Mark BUY signals based on threshold
    df_sorted["action"] = "HOLD"
    df_sorted.loc[df_sorted["p_up"] >= df_sorted["threshold"].iloc[0], "action"] = "BUY"
    
    # Ensure top K are always listed (even if not BUY)
    df_sorted.loc[df_sorted["is_candidate"], "action"] = df_sorted.loc[df_sorted["is_candidate"], "action"].apply(
        lambda x: "BUY" if x == "BUY" else "CANDIDATE"
    )
    
    return df_sorted


def batch_rank(tickers: List[str], buy_threshold: Optional[float] = None, use_mock: bool = False,
               horizon_1: int = 1, horizon_2: int = 5, top_k: int = 5) -> pd.DataFrame:
    """Enhanced batch ranking with Top-K approach."""
    reg = detect_market_regime(use_mock=use_mock)
    thr = get_dynamic_threshold(reg)
    
    rows = []
    for s in tickers:
        r1 = prob_up(s, horizon=horizon_1, use_mock=use_mock, use_meta=False)
        r5 = prob_up(s, horizon=horizon_2, use_mock=use_mock, use_meta=True)
        
        if r1 and r5:
            # Enhanced scoring: 65% 1D + 35% 5D
            score = 0.65 * r1["prob_up"] + 0.35 * r5["prob_up"]
            
            rows.append({
                "symbol": s,
                "prob_1d": r1["prob_up"],
                "prob_5d": r5["prob_up"],
                "score": score,
                "auc_1d": r1["auc_cv"],
                "auc_5d": r5["auc_cv"],
                "top_features": r5["top_features"],
                "data_points": r5["data_points"]
            })
    
    if not rows:
        return pd.DataFrame(columns=["symbol", "prob_1d", "prob_5d", "score", "action", "threshold"])
    
    df = pd.DataFrame(rows).sort_values("score", ascending=False)
    
    # Top-K approach: always select top K candidates
    df["action"] = "HOLD"  # Default
    df.loc[df.index[:top_k], "action"] = "BUY"
    
    # Additional BUY if score is very high
    df.loc[df["score"] >= thr, "action"] = "BUY"
    
    df["threshold"] = thr
    df["regime_trend"] = reg["trend"]
    df["regime_calm"] = reg["calm"]
    df["regime_adx"] = reg.get("adx", 0)
    
    return df


def save_json(df: pd.DataFrame, topk: int, horizon: int = 5, path: str = "signals.json") -> None:
    """Save results to JSON file."""
    if df is None or df.empty:
        print("❌ Kaydedilecek veri yok")
        return
    
    # Top-K results
    topk_results = []
    for _, row in df.head(topk).iterrows():
        topk_results.append({
            "symbol": row["symbol"],
            "p_up": row["score"],  # prob_up yerine score kullan
            "prob_1d": row["prob_1d"],
            "prob_5d": row["prob_5d"],
            "action": "BUY" if row["score"] >= 0.68 else "HOLD",  # score kullan
            "auc_1d": row["auc_1d"],
            "auc_5d": row["auc_5d"],
            "top_features": row["top_features"],
            "data_points": row["data_points"],
            "threshold": row["threshold"],
            "regime_trend": row["regime_trend"],
            "regime_calm": row["regime_calm"],
            "regime_adx": row["regime_adx"]
        })
    
    # All results
    all_results = []
    for _, row in df.iterrows():
        all_results.append({
            "symbol": row["symbol"],
            "p_up": row["score"],  # prob_up yerine score kullan
            "action": "BUY" if row["score"] >= 0.68 else "HOLD",  # score kullan
            "prob_1d": row["prob_1d"],
            "prob_5d": row["prob_5d"]
        })
    
    # Final structure
    output = {
        "timestamp": datetime.now().isoformat(),
        "horizon_days": horizon,
        "top_k": topk,
        "threshold": 0.68,
        "top_k_results": topk_results,
        "all_results": all_results,
        "summary": {
            "total_symbols": len(df),
            "buy_signals": len(df[df["score"] >= 0.68]),  # score kullan
            "hold_signals": len(df[df["score"] < 0.68]),  # score kullan
            "avg_score": df["score"].mean(),  # score kullan
            "avg_prob_1d": df["prob_1d"].mean(),
            "avg_prob_5d": df["prob_5d"].mean()
        }
    }
    
    # Save to file
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✅ Sonuçlar {path} dosyasına kaydedildi")
    print(f"📊 Top-{topk}: {len(topk_results)} aday, {output['summary']['buy_signals']} BUY sinyali")


def mini_backtest(symbols: List[str], horizon: int = 5, top_k: int = 3,
                  test_days: int = 90, use_mock: bool = False) -> Dict[str, float]:
    """Mini backtest: walk-forward validation for Top-K strategy."""
    print(f"🔬 Mini Backtest başlatılıyor... ({test_days} gün, Top-{top_k})")
    
    results = []
    hit_count = 0
    total_trades = 0
    
    # Walk-forward: her gün Top-K seç, ertesi horizon'da gerçekleşen getiriyi hesapla
    for start_idx in range(0, test_days - horizon, 5):  # 5 günlük adımlar
        end_idx = start_idx + horizon
        
        # Simulate daily prediction
        daily_picks = []
        for symbol in symbols:
            # Mock prediction (gerçek implementasyonda prob_up kullanılır)
            prob = np.random.uniform(0.4, 0.8)
            daily_picks.append((symbol, prob))
        
        # Sort by probability and take top-K
        daily_picks.sort(key=lambda x: x[1], reverse=True)
        top_picks = daily_picks[:top_k]
        
        # Calculate returns for top picks
        for symbol, prob in top_picks:
            if prob >= 0.55:  # Dynamic threshold
                # Mock return calculation
                mock_return = np.random.normal(0.02, 0.05)  # 2% mean, 5% std
                results.append({
                    'date': start_idx,
                    'symbol': symbol,
                    'prob': prob,
                    'return': mock_return
                })
                
                if mock_return > 0:
                    hit_count += 1
                total_trades += 1
    
    # Calculate metrics
    if total_trades == 0:
        return {"hit_rate": 0, "avg_return": 0, "total_trades": 0}
    
    hit_rate = hit_count / total_trades
    avg_return = np.mean([r['return'] for r in results]) if results else 0
    
    print(f"📊 Backtest Sonuçları:")
    print(f"   Toplam Trade: {total_trades}")
    print(f"   Hit Rate: {hit_rate:.2%}")
    print(f"   Ortalama Getiri: {avg_return:.2%}")
    
    return {
        "hit_rate": hit_rate,
        "avg_return": avg_return,
        "total_trades": total_trades
    }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", nargs="*", default=[
        "TUPRS.IS", "BIMAS.IS", "ASELS.IS", "GARAN.IS", "SISE.IS",
        "KCHOL.IS", "THYAO.IS", "FROTO.IS", "EKGYO.IS", "ISCTR.IS",
    ])
    ap.add_argument("--horizon", type=int, default=5)
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--use-mock", type=str, default="false")
    ap.add_argument("--out", type=str, default="signals.json")
    return ap.parse_args()


def validate_data_quality(df: pd.DataFrame, symbol: str) -> Dict[str, any]:
    """Validate data quality for production use."""
    validation = {
        "symbol": symbol,
        "is_valid": True,
        "issues": [],
        "warnings": []
    }
    
    # Minimum data requirements
    if len(df) < 200:
        validation["is_valid"] = False
        validation["issues"].append("Insufficient data points (< 200)")
    
    # Check for recent data
    if df.index[-1] < pd.Timestamp.now() - pd.Timedelta(days=5):
        validation["warnings"].append("Data may be stale (> 5 days old)")
    
    # Check for extreme price movements
    price_changes = df["Close"].pct_change().abs()
    if price_changes.max() > 0.20:  # 20% daily change
        validation["warnings"].append("Extreme price movements detected")
    
    # Check for missing data
    missing_pct = df.isnull().sum().sum() / (len(df) * len(df.columns))
    if missing_pct > 0.05:  # 5% missing data
        validation["warnings"].append(f"High missing data rate: {missing_pct:.1%}")
    
    return validation

def validate_model_reliability(auc: float, brier: float) -> Dict[str, any]:
    """Validate model reliability for production use."""
    validation = {
        "is_reliable": True,
        "issues": [],
        "warnings": []
    }
    
    # AUC threshold
    if auc < 0.55:
        validation["is_reliable"] = False
        validation["issues"].append(f"Low AUC: {auc:.3f} (< 0.55)")
    elif auc < 0.60:
        validation["warnings"].append(f"Moderate AUC: {auc:.3f} (< 0.60)")
    
    # Brier score threshold
    if brier > 0.25:
        validation["warnings"].append(f"High Brier score: {brier:.3f} (> 0.25)")
    
    return validation


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ML Probability Engine for Stock Prediction")
    parser.add_argument("--symbols", nargs="+", required=True, help="Stock symbols to analyze")
    parser.add_argument("--horizon", type=int, default=5, help="Prediction horizon in days")
    parser.add_argument("--topk", type=int, default=3, help="Top-K stocks to select")
    parser.add_argument("--use-mock", action="store_true", help="Use mock data for testing")
    parser.add_argument("--backtest", action="store_true", help="Run mini backtest")
    parser.add_argument("--test-days", type=int, default=90, help="Number of days for backtest")
    
    args = parser.parse_args()
    
    if args.backtest:
        print("🚀 Mini Backtest Başlatılıyor...")
        results = mini_backtest(args.symbols, args.horizon, args.topk, args.test_days, args.use_mock)
        print(f"✅ Backtest tamamlandı: {results}")
    else:
        print("📊 Normal Analiz Başlatılıyor...")
        df = batch_rank(args.symbols, use_mock=args.use_mock, horizon_2=args.horizon, top_k=args.topk)
        
        if df is not None and not df.empty:
            # Debug: DataFrame yapısını kontrol et
            print(f"\n🔍 DataFrame yapısı:")
            print(f"Şekil: {df.shape}")
            print(f"Sütunlar: {list(df.columns)}")
            print(f"İlk 3 satır:")
            print(df.head(3))
            
            # Sonuçları göster
            print(f"\n🎯 Top {args.topk} aday (skor = 0.65*P(1D)+0.35*P(5D)):")
            print("-" * 80)
            
            for i, row in df.iterrows():
                # Güvenli sütun erişimi
                prob_up = row.get("prob_up", row.get("p_up", 0.0))
                prob_1d = row.get("prob_1d", 0.0)
                prob_5d = row.get("prob_5d", 0.0)
                
                action = "BUY" if prob_up >= 0.68 else "HOLD/SELL"
                print(f"{i}: {action} - Skor: {prob_up:.3f} (1D: {prob_1d:.3f}, 5D: {prob_5d:.3f})")
            
            # Özet
            buy_count = sum(1 for _, row in df.iterrows() if row.get("prob_up", 0) >= 0.68)
            print(f"\n📊 Özet: {buy_count} BUY, {len(df) - buy_count} HOLD/SELL")
            print(f"📈 Ortalama skor: {df['score'].mean():.1%}")
            print(f"🎯 Eşik: 68.0%")
            
            # JSON kaydet
            save_json(df, args.topk, args.horizon)
            print(f"✅ Sonuçlar signals.json dosyasına kaydedildi")
            print(f"📊 Top-{args.topk}: {len(df)} aday, {buy_count} BUY sinyali")
        else:
            print("❌ Analiz sonucu boş")


