class CryptoAPI {
    constructor(baseURL = "") {
        this.baseURL = baseURL;
    }

    async getMarketSummary() {
        try {
            const response = await fetch(`${this.baseURL}/api/market-summary`);
            if (!response.ok) throw new Error("Failed to fetch market summary");
            return await response.json();
        } catch (error) {
            console.warn("Backend market summary error, attempting fallback", error);
            return null;
        }
    }

    async getScreenerData(interval = "1h", category = "ALL", minVolume = 0) {
        try {
            const params = new URLSearchParams({ interval, category, min_volume: minVolume });
            const response = await fetch(`${this.baseURL}/api/screener?${params}`);
            if (!response.ok) throw new Error("Failed to fetch screener data");
            return await response.json();
        } catch (error) {
            console.error("Backend screener API error:", error);
            return { data: [] };
        }
    }

    async getSymbolKlines(symbol, interval = "1h", limit = 100) {
        try {
            const response = await fetch(`${this.baseURL}/api/klines/${symbol}?interval=${interval}&limit=${limit}`);
            if (!response.ok) throw new Error(`Failed to fetch klines for ${symbol}`);
            return await response.json();
        } catch (error) {
            console.error("Backend klines API error:", error);
            return null;
        }
    }
}

window.cryptoAPI = new CryptoAPI();
