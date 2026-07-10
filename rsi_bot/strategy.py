from __future__ import annotations

import numpy as np
import pandas as pd


def _ensure_columns(candles: pd.DataFrame) -> pd.DataFrame:
    frame = candles.copy()
    if "close" not in frame.columns:
        raise ValueError("candles must include a 'close' column")
    if "high" not in frame.columns:
        raise ValueError("candles must include a 'high' column")
    if "low" not in frame.columns:
        raise ValueError("candles must include a 'low' column")
    return frame


def analyze_candles(candles: pd.DataFrame) -> pd.DataFrame:
    frame = _ensure_columns(candles)
    frame = frame.reset_index(drop=True)

    delta = frame["close"].diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)

    avg_gain = gain.ewm(alpha=1 / 14, min_periods=1, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, min_periods=1, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    frame["rsi"] = 100 - (100 / (1 + rs))
    frame["rsi"] = frame["rsi"].fillna(50)

    high_low = frame["high"] - frame["low"]
    high_close = (frame["high"] - frame["close"].shift()).abs()
    low_close = (frame["low"] - frame["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    frame["atr"] = tr.rolling(window=14, min_periods=14).mean()
    frame["atr"] = frame["atr"].fillna(0)

    chandelier_exit = frame["high"].rolling(window=22, min_periods=22).max() - (3 * frame["atr"])
    frame["chandelier_exit"] = chandelier_exit.ffill().fillna(0)
    return frame


def build_signal(candles: pd.DataFrame, oversold: float = 30.0, overbought: float = 70.0) -> str:
    features = analyze_candles(candles)
    if features["rsi"].dropna().empty:
        return "hold"

    current_rsi = float(features["rsi"].iloc[-1])
    if current_rsi <= oversold:
        return "buy"
    if current_rsi >= overbought:
        return "sell"
    return "hold"


def build_trade_plan(
    candles: pd.DataFrame,
    oversold: float = 50.0,
    overbought: float = 55.0,
) -> dict[str, object]:
    features = analyze_candles(candles)
    close_price = float(features["close"].iloc[-1])
    current_rsi = float(features["rsi"].iloc[-1])
    chandelier_exit = float(features["chandelier_exit"].iloc[-1])
    signal = build_signal(features, oversold=oversold, overbought=overbought)

    latest_close = features["close"].iloc[-1]
    prev_close = features["close"].iloc[-2] if len(features) > 1 else latest_close
    if latest_close > prev_close:
        trend = "uptrend"
    elif latest_close < prev_close:
        trend = "downtrend"
    else:
        trend = "range"

    if trend == "range":
        stop_loss = close_price * 0.98
        use_chandelier_stop = False
    else:
        stop_loss = chandelier_exit if chandelier_exit > 0 else close_price * 0.98
        use_chandelier_stop = True

    return {
        "signal": signal,
        "trend": trend,
        "stop_loss": stop_loss,
        "use_chandelier_stop": use_chandelier_stop,
        "rsi": current_rsi,
        "chandelier_exit": chandelier_exit,
    }
