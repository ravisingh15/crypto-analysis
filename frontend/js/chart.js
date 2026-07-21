class CanvasCandleChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
    }

    render(klines, symbol = "BTCUSDT") {
        if (!this.canvas || !klines || klines.length === 0) return;
        
        const width = this.canvas.width;
        const height = this.canvas.height;
        const ctx = this.ctx;

        // Clear Canvas
        ctx.fillStyle = '#07090e';
        ctx.fillRect(0, 0, width, height);

        const padding = { top: 30, right: 60, bottom: 40, left: 20 };
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;

        // Price range
        const highs = klines.map(k => k.high);
        const lows = klines.map(k => k.low);
        const maxPrice = Math.max(...highs);
        const minPrice = Math.min(...lows);
        const priceSpan = maxPrice - minPrice || 1;

        const candleCount = klines.length;
        const candleWidth = Math.max(2, (chartWidth / candleCount) - 2);

        // Draw Price Grid Lines
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 4; i++) {
            const y = padding.top + (chartHeight * (i / 4));
            const priceVal = maxPrice - (priceSpan * (i / 4));
            
            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(width - padding.right, y);
            ctx.stroke();

            ctx.fillStyle = '#64748b';
            ctx.font = '10px monospace';
            ctx.fillText(priceVal > 10 ? priceVal.toFixed(2) : priceVal.toFixed(4), width - padding.right + 5, y + 4);
        }

        // Draw Candlesticks & EMA Lines
        const getX = (index) => padding.left + (index * (chartWidth / candleCount)) + (candleWidth / 2);
        const getY = (price) => padding.top + chartHeight - (((price - minPrice) / priceSpan) * chartHeight);

        klines.forEach((k, i) => {
            const x = getX(i);
            const openY = getY(k.open);
            const closeY = getY(k.close);
            const highY = getY(k.high);
            const lowY = getY(k.low);

            const isBullish = k.close >= k.open;
            const color = isBullish ? '#00f5a0' : '#ff495c';

            // Wick
            ctx.strokeStyle = color;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(x, highY);
            ctx.lineTo(x, lowY);
            ctx.stroke();

            // Body
            ctx.fillStyle = color;
            const bodyY = Math.min(openY, closeY);
            const bodyHeight = Math.max(2, Math.abs(closeY - openY));
            ctx.fillRect(x - (candleWidth / 2), bodyY, candleWidth, bodyHeight);
        });

        // Draw EMA 9 Overlay
        ctx.strokeStyle = '#00d2ff';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        let started = false;
        klines.forEach((k, i) => {
            if (k.ema_9) {
                const x = getX(i);
                const y = getY(k.ema_9);
                if (!started) { ctx.moveTo(x, y); started = true; }
                else { ctx.lineTo(x, y); }
            }
        });
        ctx.stroke();

        // Draw EMA 21 Overlay
        ctx.strokeStyle = '#ffb703';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        started = false;
        klines.forEach((k, i) => {
            if (k.ema_21) {
                const x = getX(i);
                const y = getY(k.ema_21);
                if (!started) { ctx.moveTo(x, y); started = true; }
                else { ctx.lineTo(x, y); }
            }
        });
        ctx.stroke();

        // Legend Title
        ctx.fillStyle = '#f8fafc';
        ctx.font = '12px var(--font-heading)';
        ctx.fillText(`${symbol} (1h) - Price & EMA Overlay (Cyan=EMA9, Orange=EMA21)`, padding.left, 20);
    }
}

window.CanvasCandleChart = CanvasCandleChart;
