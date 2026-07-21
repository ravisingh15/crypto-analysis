import concurrent.futures
from typing import List, Dict, Any, Optional
from backend.binance_client import binance_client
from backend.indicators import enrich_klines_dataframe

CATEGORY_MAP = {
    "BTCUSDT": "Layer 1", "ETHUSDT": "Layer 1", "SOLUSDT": "Layer 1", "BNBUSDT": "Layer 1", 
    "ADAUSDT": "Layer 1", "AVAXUSDT": "Layer 1", "NEARUSDT": "Layer 1", "SUIUSDT": "Layer 1",
    "APTUSDT": "Layer 1", "INJUSDT": "Layer 1", "DOTUSDT": "Layer 1", "SEIUSDT": "Layer 1",
    "FETUSDT": "AI", "RENDERUSDT": "AI", "TAOUSDT": "AI", "AGIXUSDT": "AI", "WLDUSDT": "AI",
    "UNIUSDT": "DeFi", "AAVEUSDT": "DeFi", "PENDLEUSDT": "DeFi", "MKRUSDT": "DeFi", "CRVUSDT": "DeFi",
    "DOGEUSDT": "Meme", "PEPEUSDT": "Meme", "SHIBUSDT": "Meme", "WIFUSDT": "Meme", "BONKUSDT": "Meme",
    "ARBUSDT": "Layer 2", "OPUSDT": "Layer 2", "MATICUSDT": "Layer 2", "STRKUSDT": "Layer 2"
}

def analyze_single_pair(ticker: Dict[str, Any], interval: str = "1h") -> Optional[Dict[str, Any]]:
    """Fetch klines and analyze technical signals for a single ticker."""
    symbol = ticker["symbol"]
    try:
        raw_klines = binance_client.get_klines(symbol, interval=interval, limit=100)
        if not raw_klines or len(raw_klines) < 30:
            return None
            
        df = enrich_klines_dataframe(raw_klines)
        if df.empty:
            return None
            
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        price = float(ticker["lastPrice"])
        price_change_24h = float(ticker["priceChangePercent"])
        quote_volume_24h = float(ticker["quoteVolume"])
        
        rsi = float(latest["rsi"]) if not np_isnan(latest["rsi"]) else 50.0
        macd = float(latest["macd"]) if not np_isnan(latest["macd"]) else 0.0
        macd_signal = float(latest["macd_signal"]) if not np_isnan(latest["macd_signal"]) else 0.0
        macd_hist = float(latest["macd_hist"]) if not np_isnan(latest["macd_hist"]) else 0.0
        prev_macd_hist = float(prev["macd_hist"]) if not np_isnan(prev["macd_hist"]) else 0.0
        
        ema_9 = float(latest["ema_9"]) if not np_isnan(latest["ema_9"]) else price
        ema_21 = float(latest["ema_21"]) if not np_isnan(latest["ema_21"]) else price
        ema_50 = float(latest["ema_50"]) if not np_isnan(latest["ema_50"]) else price
        rvol = float(latest["rvol"]) if not np_isnan(latest["rvol"]) else 1.0
        atr = float(latest["atr"]) if not np_isnan(latest["atr"]) else 0.0

        # Signal Logic Scoring (-100 to +100)
        score = 0
        signals = []

        # RSI Conditions
        if rsi < 30:
            score += 35
            signals.append("RSI Oversold")
        elif rsi > 70:
            score -= 35
            signals.append("RSI Overbought")

        # MACD Crossover
        if prev_macd_hist <= 0 and macd_hist > 0:
            score += 30
            signals.append("Bullish MACD Cross")
        elif prev_macd_hist >= 0 and macd_hist < 0:
            score -= 30
            signals.append("Bearish MACD Cross")

        # Trend Alignment (EMA 9 > EMA 21 > EMA 50)
        if price > ema_9 and ema_9 > ema_21 and ema_21 > ema_50:
            score += 25
            signals.append("Uptrend Stack")
        elif price < ema_9 and ema_9 < ema_21 and ema_21 < ema_50:
            score -= 25
            signals.append("Downtrend Stack")

        # Volume Surge
        if rvol > 2.0:
            score += 15
            signals.append("Volume Surge (>2x)")

        # Recommendation Category
        if score >= 40:
            recommendation = "STRONG BUY"
        elif score >= 15:
            recommendation = "BUY"
        elif score <= -40:
            recommendation = "STRONG SELL"
        elif score <= -15:
            recommendation = "SELL"
        else:
            recommendation = "NEUTRAL"

        category = CATEGORY_MAP.get(symbol, "Altcoin")

        return {
            "symbol": symbol,
            "category": category,
            "price": price,
            "price_change_24h": round(price_change_24h, 2),
            "quote_volume_24h": round(quote_volume_24h, 2),
            "rsi": round(rsi, 1),
            "macd": round(macd, 4),
            "macd_signal": round(macd_signal, 4),
            "macd_hist": round(macd_hist, 4),
            "ema_9": round(ema_9, 4),
            "ema_21": round(ema_21, 4),
            "ema_50": round(ema_50, 4),
            "rvol": round(rvol, 2),
            "atr": round(atr, 4),
            "score": score,
            "recommendation": recommendation,
            "signals": signals
        }
    except Exception as e:
        return None

def np_isnan(val: Any) -> bool:
    try:
        import numpy as np
        return np.isnan(val)
    except Exception:
        return False

class CryptoScreener:
    def __init__(self):
        pass

    def run_screener(self, interval: str = "1h", max_pairs: int = 60) -> List[Dict[str, Any]]:
        """Fetch all USDT pairs, rank by 24h volume, and run parallel indicator analysis."""
        tickers = binance_client.get_usdt_tickers()
        # Sort by 24h volume descending
        tickers = sorted(tickers, key=lambda t: float(t.get("quoteVolume", 0)), reverse=True)[:max_pairs]
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_symbol = {
                executor.submit(analyze_single_pair, ticker, interval): ticker["symbol"]
                for ticker in tickers
            }
            for future in concurrent.futures.as_completed(future_to_symbol):
                res = future.result()
                if res:
                    results.append(res)
                    
        # Sort final results by recommendation score descending
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        return results

screener_engine = CryptoScreener()
