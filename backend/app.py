import os
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from backend.config import HOST, PORT, DEBUG, BASE_DIR
from backend.binance_client import binance_client
from backend.indicators import enrich_klines_dataframe
from backend.screener import screener_engine

app = FastAPI(
    title="Binance Crypto Screener & Analysis API",
    description="Real-Time Crypto Market Screener, Technical Analysis, and Trading Signals powered by Binance API.",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = BASE_DIR / "frontend"

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Binance Crypto Screener API"}

@app.get("/api/market-summary")
def get_market_summary():
    """Returns top volume pairs and 24h market stats."""
    try:
        usdt_tickers = binance_client.get_usdt_tickers()
        sorted_by_vol = sorted(usdt_tickers, key=lambda t: float(t.get("quoteVolume", 0)), reverse=True)[:10]
        sorted_by_gain = sorted(usdt_tickers, key=lambda t: float(t.get("priceChangePercent", 0)), reverse=True)[:5]
        sorted_by_loss = sorted(usdt_tickers, key=lambda t: float(t.get("priceChangePercent", 0)))[:5]

        total_usdt_volume = sum(float(t.get("quoteVolume", 0)) for t in usdt_tickers)
        btc_ticker = next((t for t in usdt_tickers if t["symbol"] == "BTCUSDT"), None)
        eth_ticker = next((t for t in usdt_tickers if t["symbol"] == "ETHUSDT"), None)

        return {
            "btc": btc_ticker,
            "eth": eth_ticker,
            "total_pairs_tracked": len(usdt_tickers),
            "total_24h_usdt_volume": round(total_usdt_volume, 2),
            "top_volume": sorted_by_vol,
            "top_gainers": sorted_by_gain,
            "top_losers": sorted_by_loss,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/screener")
def run_screener(
    interval: str = Query("1h", description="Candle timeframe: 15m, 1h, 4h, 1d"),
    category: str = Query("ALL", description="Filter by category: ALL, Layer 1, AI, DeFi, Meme"),
    min_volume: float = Query(0, description="Minimum 24h quote volume in USDT")
):
    """Run real-time technical analysis screener on top Binance USDT pairs."""
    try:
        results = screener_engine.run_screener(interval=interval, max_pairs=60)
        
        # Filtering
        if category and category != "ALL":
            results = [r for r in results if r["category"].upper() == category.upper()]
            
        if min_volume > 0:
            results = [r for r in results if r["quote_volume_24h"] >= min_volume]

        return {
            "timestamp": int(os.times().elapsed if hasattr(os, 'times') else 0),
            "total_results": len(results),
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/klines/{symbol}")
def get_symbol_klines(
    symbol: str,
    interval: str = Query("1h", description="Timeframe"),
    limit: int = Query(100, ge=10, le=500)
):
    """Fetch raw klines and computed indicators (RSI, MACD, EMA, BB, RVOL) for charting."""
    try:
        raw_klines = binance_client.get_klines(symbol.upper(), interval=interval, limit=limit)
        df = enrich_klines_dataframe(raw_klines)
        if df.empty:
            raise HTTPException(status_code=444, detail="No kline data found for symbol.")

        # Format clean JSON output
        records = []
        for idx, row in df.iterrows():
            records.append({
                "time": int(row["open_time"].timestamp()),
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": row["volume"],
                "rsi": None if np_isnan(row["rsi"]) else round(row["rsi"], 2),
                "macd": None if np_isnan(row["macd"]) else round(row["macd"], 4),
                "macd_signal": None if np_isnan(row["macd_signal"]) else round(row["macd_signal"], 4),
                "macd_hist": None if np_isnan(row["macd_hist"]) else round(row["macd_hist"], 4),
                "ema_9": None if np_isnan(row["ema_9"]) else round(row["ema_9"], 4),
                "ema_21": None if np_isnan(row["ema_21"]) else round(row["ema_21"], 4),
                "ema_50": None if np_isnan(row["ema_50"]) else round(row["ema_50"], 4),
                "bb_upper": None if np_isnan(row["bb_upper"]) else round(row["bb_upper"], 4),
                "bb_middle": None if np_isnan(row["bb_middle"]) else round(row["bb_middle"], 4),
                "bb_lower": None if np_isnan(row["bb_lower"]) else round(row["bb_lower"], 4),
            })

        return {
            "symbol": symbol.upper(),
            "interval": interval,
            "count": len(records),
            "klines": records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/account")
def get_account_balances():
    """Fetch private Binance account balances (Requires valid API_KEY and SECRET_KEY in .env)."""
    try:
        account_data = binance_client.get_account_info()
        balances = [
            b for b in account_data.get("balances", [])
            if float(b["free"]) > 0 or float(b["locked"]) > 0
        ]
        return {
            "can_trade": account_data.get("canTrade", False),
            "account_type": account_data.get("accountType", "SPOT"),
            "balances": balances
        }
    except ValueError as ve:
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to fetch account info: {str(e)}"})

def np_isnan(val: Any) -> bool:
    try:
        import numpy as np
        return np.isnan(val)
    except Exception:
        return False

# Serve static frontend files if directory exists
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def read_root():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Binance Crypto Screener API is running. Frontend index.html not found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host=HOST, port=PORT, reload=DEBUG)
