import pandas as pd
import numpy as np
from typing import List, Any, Dict

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index (RSI)."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    # Wilder's Smoothing for RSI
    gain = gain.combine_first(series.diff().clip(lower=0).ewm(alpha=1/period, adjust=False).mean())
    loss = loss.combine_first((-series.diff()).clip(lower=0).ewm(alpha=1/period, adjust=False).mean())
    
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
    """Calculate Moving Average Convergence Divergence (MACD)."""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return {
        "macd": macd_line,
        "signal": signal_line,
        "hist": histogram
    }

def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """Calculate Exponential Moving Average (EMA)."""
    return series.ewm(span=period, adjust=False).mean()

def calculate_sma(series: pd.Series, period: int) -> pd.Series:
    """Calculate Simple Moving Average (SMA)."""
    return series.rolling(window=period).mean()

def calculate_bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0) -> Dict[str, pd.Series]:
    """Calculate Bollinger Bands (Middle, Upper, Lower, Bandwidth %)."""
    sma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    bandwidth = ((upper - lower) / sma) * 100
    return {
        "middle": sma,
        "upper": upper,
        "lower": lower,
        "bandwidth": bandwidth
    }

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Average True Range (ATR)."""
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/period, adjust=False).mean()
    return atr

def calculate_rvol(volume: pd.Series, period: int = 20) -> pd.Series:
    """Calculate Relative Volume (RVOL = current volume / N-period average volume)."""
    avg_vol = volume.rolling(window=period).mean()
    rvol = volume / (avg_vol + 1e-10)
    return rvol

def enrich_klines_dataframe(raw_klines: List[List[Any]]) -> pd.DataFrame:
    """
    Parse raw Binance klines raw array into a structured DataFrame and calculate 
    all technical indicators.
    """
    if not raw_klines or len(raw_klines) == 0:
        return pd.DataFrame()

    columns = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ]
    df = pd.DataFrame(raw_klines, columns=columns)
    
    # Cast numerical columns
    for col in ["open", "high", "low", "close", "volume", "quote_asset_volume"]:
        df[col] = df[col].astype(float)
        
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")

    # Compute Indicators
    df["rsi"] = calculate_rsi(df["close"], period=14)
    
    macd_dict = calculate_macd(df["close"])
    df["macd"] = macd_dict["macd"]
    df["macd_signal"] = macd_dict["signal"]
    df["macd_hist"] = macd_dict["hist"]
    
    df["ema_9"] = calculate_ema(df["close"], 9)
    df["ema_21"] = calculate_ema(df["close"], 21)
    df["ema_50"] = calculate_ema(df["close"], 50)
    df["ema_200"] = calculate_ema(df["close"], 200)
    
    bb = calculate_bollinger_bands(df["close"], period=20, std_dev=2.0)
    df["bb_middle"] = bb["middle"]
    df["bb_upper"] = bb["upper"]
    df["bb_lower"] = bb["lower"]
    df["bb_bandwidth"] = bb["bandwidth"]
    
    df["atr"] = calculate_atr(df["high"], df["low"], df["close"], period=14)
    df["rvol"] = calculate_rvol(df["volume"], period=20)

    return df
