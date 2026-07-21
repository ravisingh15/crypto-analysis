document.addEventListener("DOMContentLoaded", () => {
    let currentScreenerData = [];
    let currentSortColumn = "score";
    let currentSortAscending = false;
    let selectedSymbolData = null;

    const chartRenderer = new CanvasCandleChart('candle-chart');

    // DOM Elements
    const searchInput = document.getElementById("search-input");
    const categorySelect = document.getElementById("category-select");
    const timeframeSelect = document.getElementById("timeframe-select");
    const signalFilterSelect = document.getElementById("signal-filter-select");
    const tableBody = document.getElementById("table-body");
    const recordsCount = document.getElementById("records-count");
    const btnRefresh = document.getElementById("btn-refresh");

    // Ticker & Stats
    const liveTickerStrip = document.getElementById("live-ticker-strip");
    const topVolSymbol = document.getElementById("top-vol-symbol");
    const topVolVal = document.getElementById("top-vol-val");
    const topGainerSymbol = document.getElementById("top-gainer-symbol");
    const topGainerVal = document.getElementById("top-gainer-val");
    const strongBuyCount = document.getElementById("strong-buy-count");
    const sentimentVal = document.getElementById("sentiment-val");
    const sentimentSub = document.getElementById("sentiment-sub");

    // Modal Elements
    const chartModal = document.getElementById("chart-modal");
    const modalSymbol = document.getElementById("modal-symbol");
    const modalCategory = document.getElementById("modal-category");
    const modalRecommendation = document.getElementById("modal-recommendation");
    const modalSignalsList = document.getElementById("modal-signals-list");
    const btnCloseModal = document.getElementById("btn-close-modal");

    // Risk Calculator
    const calcAccount = document.getElementById("calc-account");
    const calcRisk = document.getElementById("calc-risk");
    const calcPosSize = document.getElementById("calc-pos-size");
    const calcSlTarget = document.getElementById("calc-sl-target");
    const calcTpTarget = document.getElementById("calc-tp-target");

    // Event Listeners
    btnRefresh.addEventListener("click", refreshData);
    categorySelect.addEventListener("change", refreshData);
    timeframeSelect.addEventListener("change", refreshData);
    signalFilterSelect.addEventListener("change", renderTable);
    searchInput.addEventListener("input", renderTable);
    btnCloseModal.addEventListener("click", closeModal);

    calcAccount.addEventListener("input", updateRiskCalculator);
    calcRisk.addEventListener("input", updateRiskCalculator);

    // Sort Headers Click Listener
    document.querySelectorAll("th.sortable").forEach(th => {
        th.addEventListener("click", () => {
            const col = th.dataset.sort;
            if (currentSortColumn === col) {
                currentSortAscending = !currentSortAscending;
            } else {
                currentSortColumn = col;
                currentSortAscending = false;
            }
            renderTable();
        });
    });

    // Initial Load
    fetchMarketSummary();
    refreshData();

    // Auto Refresh every 30 seconds
    setInterval(() => {
        fetchMarketSummary();
        refreshData();
    }, 30000);

    async function fetchMarketSummary() {
        const summary = await window.cryptoAPI.getMarketSummary();
        if (!summary) return;

        // Render Live Ticker Pills
        if (summary.top_volume && summary.top_volume.length > 0) {
            liveTickerStrip.innerHTML = summary.top_volume.slice(0, 6).map(t => {
                const change = parseFloat(t.priceChangePercent);
                const colorClass = change >= 0 ? 'positive' : 'negative';
                const sign = change >= 0 ? '+' : '';
                return `
                    <div class="ticker-pill">
                        <span class="symbol">${t.symbol.replace('USDT', '')}</span>
                        <span class="price">$${parseFloat(t.lastPrice).toLocaleString()}</span>
                        <span class="${colorClass}">${sign}${change.toFixed(2)}%</span>
                    </div>
                `;
            }).join('');
        }

        // Stats Cards
        if (summary.top_volume && summary.top_volume[0]) {
            const topVol = summary.top_volume[0];
            topVolSymbol.textContent = topVol.symbol;
            topVolVal.textContent = `24h Vol: $${(parseFloat(topVol.quoteVolume) / 1e6).toFixed(1)}M`;
        }

        if (summary.top_gainers && summary.top_gainers[0]) {
            const topG = summary.top_gainers[0];
            topGainerSymbol.textContent = topG.symbol;
            topGainerVal.textContent = `+${parseFloat(topG.priceChangePercent).toFixed(2)}%`;
        }
    }

    async function refreshData() {
        tableBody.innerHTML = `
            <tr>
                <td colspan="11" class="loading-cell">
                    <div class="spinner"></div> Scanning Binance pairs & calculating technical indicators...
                </td>
            </tr>
        `;

        const timeframe = timeframeSelect.value;
        const category = categorySelect.value;
        const res = await window.cryptoAPI.getScreenerData(timeframe, category);

        currentScreenerData = res.data || [];
        updateSentimentStats();
        renderTable();
    }

    function updateSentimentStats() {
        const strongBuy = currentScreenerData.filter(d => d.recommendation === "STRONG BUY").length;
        const buy = currentScreenerData.filter(d => d.recommendation === "BUY").length;
        const sell = currentScreenerData.filter(d => d.recommendation.includes("SELL")).length;

        strongBuyCount.textContent = strongBuy;

        const total = currentScreenerData.length || 1;
        const bullishRatio = ((strongBuy + buy) / total) * 100;

        if (bullishRatio >= 50) {
            sentimentVal.textContent = "BULLISH 🚀";
            sentimentVal.style.color = "var(--green-bull)";
            sentimentSub.textContent = `${bullishRatio.toFixed(0)}% pairs with Buy signals`;
        } else if (bullishRatio <= 20) {
            sentimentVal.textContent = "BEARISH 📉";
            sentimentVal.style.color = "var(--red-bear)";
            sentimentSub.textContent = `${(100 - bullishRatio).toFixed(0)}% neutral/sell bias`;
        } else {
            sentimentVal.textContent = "NEUTRAL ⚖️";
            sentimentVal.style.color = "var(--text-secondary)";
            sentimentSub.textContent = "Balanced market state";
        }
    }

    function renderTable() {
        if (!currentScreenerData || currentScreenerData.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="11" style="text-align:center;">No crypto pairs matched the filter criteria.</td></tr>`;
            recordsCount.textContent = "0 Pairs";
            return;
        }

        let filtered = [...currentScreenerData];

        // Search Filter
        const query = searchInput.value.trim().toUpperCase();
        if (query) {
            filtered = filtered.filter(item => item.symbol.toUpperCase().includes(query));
        }

        // Signal Filter
        const signalFilter = signalFilterSelect.value;
        if (signalFilter === "STRONG BUY") {
            filtered = filtered.filter(item => item.recommendation === "STRONG BUY");
        } else if (signalFilter === "BUY") {
            filtered = filtered.filter(item => item.recommendation === "STRONG BUY" || item.recommendation === "BUY");
        } else if (signalFilter === "SELL") {
            filtered = filtered.filter(item => item.recommendation.includes("SELL"));
        }

        // Sorting
        filtered.sort((a, b) => {
            let valA = a[currentSortColumn];
            let valB = b[currentSortColumn];

            if (typeof valA === "string") {
                valA = valA.toLowerCase();
                valB = valB.toLowerCase();
            }

            if (valA < valB) return currentSortAscending ? -1 : 1;
            if (valA > valB) return currentSortAscending ? 1 : -1;
            return 0;
        });

        recordsCount.textContent = `Showing ${filtered.length} Pairs`;

        tableBody.innerHTML = filtered.map(item => {
            const priceChangeClass = item.price_change_24h >= 0 ? "positive" : "negative";
            const priceChangeSign = item.price_change_24h >= 0 ? "+" : "";
            const volFormatted = (item.quote_volume_24h / 1e6).toFixed(2) + "M";

            let recBadge = "badge-neutral";
            if (item.recommendation === "STRONG BUY") recBadge = "badge-strong-buy";
            else if (item.recommendation === "BUY") recBadge = "badge-buy";
            else if (item.recommendation.includes("SELL")) recBadge = "badge-sell";

            // RSI Color Code
            let rsiClass = "";
            if (item.rsi < 30) rsiClass = "positive";
            else if (item.rsi > 70) rsiClass = "negative";

            return `
                <tr>
                    <td><strong>${item.symbol}</strong></td>
                    <td><span class="badge badge-neutral">${item.category}</span></td>
                    <td style="font-family: monospace;">$${item.price < 1 ? item.price : item.price.toLocaleString()}</td>
                    <td class="${priceChangeClass}">${priceChangeSign}${item.price_change_24h}%</td>
                    <td class="${rsiClass}">${item.rsi}</td>
                    <td style="font-family: monospace;" class="${item.macd_hist >= 0 ? 'positive' : 'negative'}">${item.macd_hist}</td>
                    <td>${item.rvol}x</td>
                    <td style="font-family: monospace;">$${volFormatted}</td>
                    <td><strong>${item.score}</strong></td>
                    <td><span class="badge ${recBadge}">${item.recommendation}</span></td>
                    <td>
                        <button class="btn btn-outline btn-chart" data-symbol="${item.symbol}">Chart 📈</button>
                    </td>
                </tr>
            `;
        }).join("");

        // Attach Chart Click Handlers
        document.querySelectorAll(".btn-chart").forEach(btn => {
            btn.addEventListener("click", () => {
                const sym = btn.dataset.symbol;
                const match = currentScreenerData.find(d => d.symbol === sym);
                if (match) openModal(match);
            });
        });
    }

    async function openModal(data) {
        selectedSymbolData = data;
        modalSymbol.textContent = data.symbol;
        modalCategory.textContent = data.category;
        modalRecommendation.textContent = data.recommendation;

        modalSignalsList.innerHTML = data.signals.map(sig => `
            <div class="signal-tag" style="background:rgba(255,255,255,0.05); padding:6px 10px; border-radius:6px; font-size:12px; border:1px solid var(--border-color);">
                ⚡ ${sig}
            </div>
        `).join('') || '<div style="font-size:12px; color:var(--text-muted);">No major alert flags active</div>';

        updateRiskCalculator();
        chartModal.classList.add("active");

        // Fetch & Draw Chart
        const timeframe = timeframeSelect.value;
        const klineRes = await window.cryptoAPI.getSymbolKlines(data.symbol, timeframe, 100);
        if (klineRes && klineRes.klines) {
            chartRenderer.render(klineRes.klines, data.symbol);
        }
    }

    function closeModal() {
        chartModal.classList.remove("active");
    }

    function updateRiskCalculator() {
        if (!selectedSymbolData) return;

        const account = parseFloat(calcAccount.value) || 1000;
        const riskPct = parseFloat(calcRisk.value) || 2;
        const price = selectedSymbolData.price;
        const atr = selectedSymbolData.atr || (price * 0.02);

        const dollarRisk = account * (riskPct / 100);
        const stopDistance = 1.5 * atr;
        const stopLossPrice = Math.max(0, price - stopDistance);
        const takeProfitPrice = price + (2 * stopDistance);

        const sharesOrUnits = stopDistance > 0 ? (dollarRisk / stopDistance) : 0;
        const positionSizeDollars = sharesOrUnits * price;

        calcPosSize.textContent = `$${positionSizeDollars.toFixed(2)}`;
        calcSlTarget.textContent = `$${stopLossPrice.toFixed(4)} (-${((stopDistance / price) * 100).toFixed(2)}%)`;
        calcTpTarget.textContent = `$${takeProfitPrice.toFixed(4)} (+${(((2 * stopDistance) / price) * 100).toFixed(2)}%)`;
    }
});
