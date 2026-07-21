#  Binance Live Crypto Analysis & Screener

> A high-performance, real-time Cryptocurrency Market Screener and Technical Analysis platform powered by the Binance REST API. Features parallel multi-factor pair screening, vectorized technical indicators, signal scoring, interactive web dashboard, and dedicated Jupyter notebooks for exploratory data analysis.

---

## 🌟 Key Features

1. **🔒 Secure Credential Management**:
   - Strictly git-ignored `.env` file for private `API_KEY` and `SECRET_KEY`.
   - `.env.example` template for public repository deployment without secret leaks.
2. **📈 Real-Time Technical Analysis Engine**:
   - **RSI (14)**: Relative Strength Index oversold (<30) and overbought (>70) detection.
   - **MACD (12, 26, 9)**: Bullish & Bearish signal line crossover tracking.
   - **EMA Stack (9, 21, 50, 200)**: Trend direction stack & Golden Cross identification.
   - **Bollinger Bands (20, 2)**: Bandwidth % calculation and volatility compression.
   - **RVOL (Relative Volume)**: Volume spike detection vs 20-period moving average.
   - **ATR (14)**: Average True Range calculation for dynamic Stop Loss & Take Profit targets.
3. **⚡ Multi-Factor Crypto Screener**:
   - Parallel multi-threaded scanning across Binance USDT pairs.
   - Composite Signal Scoring model (-100 to +100) categorizing pairs into **STRONG BUY**, **BUY**, **NEUTRAL**, **SELL**, or **STRONG SELL**.
   - Sector/Category filters (Layer 1, AI / Data, DeFi, Meme, Layer 2).
4. **📊 Interactive Web Dashboard**:
   - Glassmorphic dark trading UI built with vanilla HTML/CSS/JS.
   - Live header ticker strip for top market assets.
   - Multi-column sortable table with instant search and filter controls.
   - Canvas-based candlestick charting modal with EMA overlays and interactive risk position calculator.
5. **📓 Interactive Jupyter Notebooks**:
   - `01_binance_data_exploration.ipynb`: Market summary, 24h volume leaders, and candlestick ingestion.
   - `02_indicator_deep_dive.ipynb`: Multi-indicator plotting with Plotly dark themes.
   - `03_screener_backtest.ipynb`: Backtesting technical signal rules against historical klines.

---

## 📁 Repository Structure

```
crypto-analysis/
├── .env                               # Private API credentials (GIT IGNORED)
├── .env.example                       # Safe environment variable template
├── .gitignore                         # Standard exclusion rules
├── README.md                          # Documentation & project guide
├── requirements.txt                   # Dependencies (FastAPI, Pandas, Jupyter, Plotly)
├── notebooks/                         # Jupyter Notebooks for analysis
│   ├── 01_binance_data_exploration.ipynb
│   ├── 02_indicator_deep_dive.ipynb
│   └── 03_screener_backtest.ipynb
├── backend/
│   ├── config.py                      # Environment configuration loader
│   ├── binance_client.py              # REST API client with failover endpoints
│   ├── indicators.py                  # Vectorized Technical Indicators Engine
│   ├── screener.py                    # Multi-pair Screener & Signal Scoring
│   └── app.py                         # FastAPI Web Server & Static File Host
└── frontend/
    ├── index.html                     # Web Dashboard layout
    ├── css/
    │   └── styles.css                 # Dark mode glassmorphic CSS theme
    └── js/
        ├── api.js                     # API communications client
        ├── chart.js                   # Canvas candlestick charting renderer
        └── app.js                     # Interactive table UI & position calculator
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure you have **Python 3.10+** installed.

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and enter your Binance API Key and Secret:
```bash
cp .env.example .env
```
*(Your `.env` file is protected by `.gitignore` and will never be committed to Git.)*

### 3. Install Dependencies
Install required packages using `pip`:
```bash
pip install -r requirements.txt
```

### 4. Run the Screener Server & Web Dashboard
Launch the FastAPI server:
```bash
python -m backend.app
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:8000`**

---

## 📓 Using Jupyter Notebooks

Launch Jupyter Notebook to perform custom research and backtesting:
```bash
jupyter notebook
```
Navigate to the `notebooks/` directory and open any of the notebooks:
- **`01_binance_data_exploration.ipynb`**: Fetch 24h market metrics & ticker statistics.
- **`02_indicator_deep_dive.ipynb`**: Plot RSI, MACD, and EMA charts interactively.
- **`03_screener_backtest.ipynb`**: Test technical signal win-rates against historical candles.

---

## 🛡️ Security Best Practices

- **Never hardcode API Keys**: Always read credentials from `.env` via `backend/config.py`.
- **Binance API Key Permissions**: For read-only screening, enable **only Read Info / Market Data** permissions on Binance. Disable Withdrawal permissions on your API key.
- **Git Verification**: Run `git status` before committing to confirm `.env` is un-tracked.

---

## 📜 License
This project is open source and available under the [MIT License](LICENSE).
