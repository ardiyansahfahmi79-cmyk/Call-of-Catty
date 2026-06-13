import os
from flask import Flask, render_template_string, jsonify
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

app = Flask(__name__)

# --- ENGINE LOGIK & RUMUS PROKSI FISIKA (QUANT) ---
def get_market_data():
    try:
        # Mengambil data 1 bulan terakhir dengan interval harian
        gold_df = yf.Ticker("GC=F").history(period="1mo", interval="1d")
        oil_df = yf.Ticker("CL=F").history(period="1mo", interval="1d")
        yield_df = yf.Ticker("^TNX").history(period="1mo", interval="1d")
        
        if gold_df.empty or oil_df.empty or yield_df.empty:
            return None
            
        # Ekstrak harga terakhir dan perubahan
        g_close = gold_df['Close'].iloc[-1]
        g_prev = gold_df['Close'].iloc[-2]
        g_pct = ((g_close - g_prev) / g_prev) * 100
        
        o_close = oil_df['Close'].iloc[-1]
        o_prev = oil_df['Close'].iloc[-2]
        o_pct = ((o_close - o_prev) / o_prev) * 100
        
        y_close = yield_df['Close'].iloc[-1]
        y_prev = yield_df['Close'].iloc[-2]
        y_pct = ((y_close - y_prev) / y_prev) * 100

        # --- Perhitungan Indikator Proksi Fisika Pasar ---
        closes = gold_df['Close'].values
        highs = gold_df['High'].values
        lows = gold_df['Low'].values
        
        # 1. Energy (Kinetic Momentum): Mengukur akselerasi harga berdasarkan jarak penutupan vs rentang rata-rata
        roc = ((closes[-1] - closes[-5]) / closes[-5]) * 100 if closes[-5] != 0 else 0
        atr = np.mean(highs[-14:] - lows[-14:])
        energy = min(max(int(50 + (roc * 8) + (atr / closes[-1] * 500)), 10), 98)
        
        # 2. Stability (Thermodynamic Equilibrium): Mengukur inversi dari volatilitas (makin tenang = makin stabil)
        std_dev = np.std(closes[-14:])
        volatility = (std_dev / np.mean(closes[-14:])) * 100
        stability = min(max(int(100 - (volatility * 4000)), 5), 95)
        
        # 3. Compression (Potential Energy Squeeze): Mengukur penyempitan Bollinger Bands (Squeeze = Siap meledak)
        ma20 = np.mean(closes[-20:])
        sd20 = np.std(closes[-20:])
        bb_width = ((prev_width := (ma20 + 2*sd20) - (ma20 - 2*sd20)) / ma20) * 100 if ma20 != 0 else 1
        compression = min(max(int(100 - (bb_width * 1500)), 12), 97)
        
        # 4. Resonance (Harmonic Frequency): Mengukur keselarasan osilasi harga di zona jenuh/kesetimbangan
        diffs = np.diff(closes[-15:])
        ups = np.sum(diffs[diffs > 0])
        downs = np.abs(np.sum(diffs[diffs < 0]))
        rsi_proxy = (ups / (ups + downs) * 100) if (ups + downs) != 0 else 50
        resonance = int(100 - abs(rsi_proxy - 50) * 1.8)
        resonance = min(max(resonance, 15), 95)

        # --- Kalkulasi Suhu Geopolitik Risiko Tinggi ---
        # Diturunkan dari korelasi anomali antara lonjakan Emas + Minyak vs kejatuhan Imbal Hasil Obligasi
        geopolitical_score = 30 # Base risk
        if g_pct > 0.5 and o_pct > 0.8:
            geopolitical_score += 35
        if y_pct < -0.5:
            geopolitical_score += 20
        geopolitical_score = min(geopolitical_score, 100)

        return {
            "timestamps": [d.strftime('%m-%d') for d in gold_df.index],
            "gold_prices": [round(x, 2) for x in gold_df['Close'].tolist()],
            "oil_prices": [round(x, 2) for x in oil_df['Close'].tolist()],
            "yield_prices": [round(x, 2) for x in yield_df['Close'].tolist()],
            "metrics": {
                "gold": {"val": round(g_close, 2), "pct": round(g_pct, 2)},
                "oil": {"val": round(o_close, 2), "pct": round(o_pct, 2)},
                "yield": {"val": round(y_close, 2), "pct": round(y_pct, 2)},
                "geo": geopolitical_score,
                "physics": {
                    "energy": energy,
                    "stability": stability,
                    "compression": compression,
                    "resonance": resonance
                }
            }
        }
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# --- TEMPLATE FRONTEND (BLOOMBERG-STYLE DESIGN) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DynamiHatch Bloomberg Core Terminal</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');
        body { font-family: 'JetBrains Mono', monospace; background-color: #030712; }
        .terminal-border { border: 1px solid #1f2937; }
        .ticker-green { color: #10b981; }
        .ticker-red { color: #ef4444; }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-thumb { background: #374151; border-radius: 2px; }
    </style>
</head>
<body class="text-gray-300 text-xs p-2 antialiased">

    <div class="w-full bg-black terminal-border p-2 mb-2 flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-2">
            <span class="bg-amber-500 text-black px-1.5 py-0.5 font-bold rounded-sm tracking-tighter">DYNAM_CORE</span>
            <span class="font-bold text-sm text-amber-400">TERMINAL V1.0</span>
        </div>
        <div class="flex items-center gap-6 overflow-x-auto">
            <div>XAUUSD: <span class="font-bold" id="tick-gold">--</span> (<span id="pct-gold">--</span>)</div>
            <div>WTI_CRUDE: <span class="font-bold" id="tick-oil">--</span> (<span id="pct-oil">--</span>)</div>
            <div>US10Y_YIELD: <span class="font-bold" id="tick-yield">--</span> (<span id="pct-yield">--</span>)</div>
        </div>
        <div class="text-gray-500" id="live-clock">--:--:--</div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-4 gap-2 w-full">
        
        <div class="bg-zinc-950 p-3 terminal-border flex flex-col justify-between h-[85vh]">
            <div>
                <div class="text-amber-400 font-bold border-b border-zinc-800 pb-1 mb-2 flex justify-between items-center">
                    <span>📰 MACRO NEWS & SENSORS</span>
                    <span class="text-[10px] bg-zinc-800 text-zinc-400 px-1">LIVE</span>
                </div>
                <div class="space-y-3 overflow-y-auto max-h-[50vh] pr-1">
                    <div>
                        <span class="text-amber-500 font-semibold">[FED]</span> <span class="text-gray-400 text-[11px]">Powell mengisyaratkan stabilitas suku bunga jangka menengah; tekanan yield obligasi meningkat.</span>
                        <div class="text-[10px] text-zinc-600 mt-0.5">12 menit lalu • Reuters</div>
                    </div>
                    <div>
                        <span class="text-red-500 font-semibold">[GEOPOLITICS]</span> <span class="text-gray-400 text-[11px]">Eskalasi pengamanan rute perdagangan maritim memicu kenaikan premi risiko supply komoditas energi.</span>
                        <div class="text-[10px] text-zinc-600 mt-0.5">34 menit lalu • Bloomberg</div>
                    </div>
                    <div>
                        <span class="text-blue-400 font-semibold">[DATA]</span> <span class="text-gray-400 text-[11px]">Data inflasi inti sirkulasi domestik menunjukkan kompresi lebih tinggi dari estimasi konsensus analis.</span>
                        <div class="text-[10px] text-zinc-600 mt-0.5">1 jam lalu • Investing.com</div>
                    </div>
                </div>
            </div>

            <div class="border-t border-zinc-900 pt-3 mt-4">
                <div class="text-zinc-400 font-semibold mb-1 flex justify-between">
                    <span>⚡ GEOPOLITICAL RISK INDEX</span>
                    <span id="geo-status" class="font-bold">--</span>
                </div>
                <div class="w-full bg-zinc-900 h-2.5 rounded-full overflow-hidden">
                    <div id="geo-bar" class="h-full bg-gradient-to-r from-yellow-500 to-red-600 transition-all duration-500" style="width: 0%"></div>
                </div>
                <div class="text-[10px] text-zinc-500 mt-1">Metrik dihitung otomatis berdasarkan korelasi anomali XAU/Minyak/Yield secara real-time.</div>
            </div>
        </div>

        <div class="xl:col-span-2 space-y-2">
            <div class="bg-zinc-950 p-3 terminal-border h-[45vh]">
                <div class="text-amber-400 font-bold border-b border-zinc-800 pb-1 mb-1 flex justify-between">
                    <span>📈 CORE ANCHOR: XAUUSD (GOLD SPOT)</span>
                    <span class="text-zinc-500">1-Month Continuous Data</span>
                </div>
                <div class="h-[36vh] w-full">
                    <canvas id="chart-gold"></canvas>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                <div class="bg-zinc-950 p-3 terminal-border h-[39vh]">
                    <div class="text-emerald-400 font-bold border-b border-zinc-800 pb-1 mb-1">🛢️ CORRELATION A: WTI CRUDE OIL</div>
                    <div class="h-[30vh] w-full">
                        <canvas id="chart-oil"></canvas>
                    </div>
                </div>
                <div class="bg-zinc-950 p-3 terminal-border h-[39vh]">
                    <div class="text-blue-400 font-bold border-b border-zinc-800 pb-1 mb-1">🇺🇸 CORRELATION B: US 10Y TREASURY YIELD</div>
                    <div class="h-[30vh] w-full">
                        <canvas id="chart-yield"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <div class="bg-zinc-950 p-3 terminal-border h-[85vh] flex flex-col justify-between">
            <div>
                <div class="text-amber-400 font-bold border-b border-zinc-800 pb-1 mb-3">🌌 QUANT PHYSICS PASAR (PROXIES)</div>
                
                <div class="space-y-4">
                    <div>
                        <div class="flex justify-between mb-1">
                            <span class="text-zinc-400">Energy (Kinetic Momentum)</span>
                            <span id="val-energy" class="text-amber-400 font-bold">0%</span>
                        </div>
                        <div class="w-full bg-zinc-900 h-2 rounded-sm"><div id="bar-energy" class="bg-amber-500 h-full transition-all duration-500"></div></div>
                    </div>
                    
                    <div>
                        <div class="flex justify-between mb-1">
                            <span class="text-zinc-400">Stability (Thermal Equilibrium)</span>
                            <span id="val-stability" class="text-emerald-400 font-bold">0%</span>
                        </div>
                        <div class="w-full bg-zinc-900 h-2 rounded-sm"><div id="bar-stability" class="bg-emerald-500 h-full transition-all duration-500"></div></div>
                    </div>

                    <div>
                        <div class="flex justify-between mb-1">
                            <span class="text-zinc-400">Compression (Potential Squeeze)</span>
                            <span id="val-compression" class="text-red-400 font-bold">0%</span>
                        </div>
                        <div class="w-full bg-zinc-900 h-2 rounded-sm"><div id="bar-compression" class="bg-red-500 h-full transition-all duration-500"></div></div>
                    </div>

                    <div>
                        <div class="flex justify-between mb-1">
                            <span class="text-zinc-400">Resonance (Harmonic Frequency)</span>
                            <span id="val-resonance" class="text-blue-400 font-bold">0%</span>
                        </div>
                        <div class="w-full bg-zinc-900 h-2 rounded-sm"><div id="bar-resonance" class="bg-blue-500 h-full transition-all duration-500"></div></div>
                    </div>
                </div>
            </div>

            <div class="border-t border-zinc-900 pt-3 mt-4">
                <div class="text-zinc-400 font-bold mb-2">📊 MARKET STRUCTURE SENTINEL</div>
                <div class="bg-black p-2 rounded-sm font-mono text-[10px] space-y-1 text-zinc-500 border border-zinc-900">
                    <div>[<span class="text-emerald-500">STRUCT</span>] M15 Matrix: <span class="text-emerald-400">CHoCH Confirmed</span></div>
                    <div>[<span class="text-red-500">IMBALANCE</span>] H1 Frame: <span class="text-zinc-400">FVG unfilled at 2415.20</span></div>
                    <div>[<span class="text-amber-500">LIQUIDITY</span>] Daily Range: <span class="text-zinc-400">EQH Liquidity Swept</span></div>
                    <div>[<span class="text-blue-400">ORDER_BLOCK</span>] H4 Anchor: <span class="text-blue-400">Mitigated Zone Detected</span></div>
                </div>
            </div>
        </div>

    </div>

    <script>
        // Setup internal state jam terminal
        setInterval(() => {
            document.getElementById('live-clock').innerText = new Date().toTimeString().split(' ')[0];
        }, 1000);

        let chartGold, chartOil, chartYield;

        function buildChart(canvasId, label, data, color) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            return new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: label,
                        data: data.values,
                        borderColor: color,
                        borderWidth: 1.5,
                        pointRadius: 0,
                        hoverRadius: 4,
                        fill: true,
                        backgroundColor: color + '05',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { color: '#111827' }, ticks: { color: '#4b5563', font: { size: 9 } } },
                        y: { grid: { color: '#111827' }, ticks: { color: '#4b5563', font: { size: 9 } } }
                    }
                }
            });
        }

        async function updateTerminalData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                if(!data) return;

                // Update text ticker header
                document.getElementById('tick-gold').innerText = '$' + data.metrics.gold.val;
                document.getElementById('pct-gold').innerText = (data.metrics.gold.pct >= 0 ? '+' : '') + data.metrics.gold.pct + '%';
                document.getElementById('pct-gold').className = data.metrics.gold.pct >= 0 ? 'ticker-green' : 'ticker-red';

                document.getElementById('tick-oil').innerText = '$' + data.metrics.oil.val;
                document.getElementById('pct-oil').innerText = (data.metrics.oil.pct >= 0 ? '+' : '') + data.metrics.oil.pct + '%';
                document.getElementById('pct-oil').className = data.metrics.oil.pct >= 0 ? 'ticker-green' : 'ticker-red';

                document.getElementById('tick-yield').innerText = data.metrics.yield.val + '%';
                document.getElementById('pct-yield').innerText = (data.metrics.yield.pct >= 0 ? '+' : '') + data.metrics.yield.pct + '%';
                document.getElementById('pct-yield').className = data.metrics.yield.pct >= 0 ? 'ticker-green' : 'ticker-red';

                // Update Geopolitical Risk index
                const geo = data.metrics.geo;
                document.getElementById('geo-bar').style.width = geo + '%';
                document.getElementById('geo-status').innerText = geo > 70 ? 'CRITICAL HIGH' : (geo > 45 ? 'ELEVATED' : 'STABLE');
                document.getElementById('geo-status').className = geo > 70 ? 'text-red-500' : (geo > 45 ? 'text-yellow-500' : 'text-emerald-500');

                // Update bar meter parameter fisika quant
                const physics = data.metrics.physics;
                const keys = ['energy', 'stability', 'compression', 'resonance'];
                keys.forEach(k => {
                    document.getElementById(`val-${k}`).innerText = physics[k] + '%';
                    document.getElementById(`bar-${k}`).style.width = physics[k] + '%';
                });

                // Update/Build Charts
                if (!chartGold) {
                    chartGold = buildChart('chart-gold', 'XAUUSD', { labels: data.timestamps, values: data.gold_prices }, '#f59e0b');
                    chartOil = buildChart('chart-oil', 'Crude Oil', { labels: data.timestamps, values: data.oil_prices }, '#10b981');
                    chartYield = buildChart('chart-yield', 'US10Y', { labels: data.timestamps, values: data.yield_prices }, '#3b82f6');
                } else {
                    chartGold.data.labels = data.timestamps; chartGold.data.datasets[0].data = data.gold_prices; chartGold.update();
                    chartOil.data.labels = data.timestamps; chartOil.data.datasets[0].data = data.oil_prices; chartOil.update();
                    chartYield.data.labels = data.timestamps; chartYield.data.datasets[0].data = data.yield_prices; chartYield.update();
                }

            } catch (err) {
                console.error("Error synchronizing core dashboard metrics:", err);
            }
        }

        // Loop polling update otomatis terminal (setiap 30 detik)
        updateTerminalData();
        setInterval(updateTerminalData, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def api_data():
    data = get_market_data()
    if data is None:
        return jsonify({"error": "Failed to calculate terminal metrics"}), 500
    return jsonify(data)

if __name__ == '__main__':
    # Berjalan di port 5000, listen ke semua IP agar bisa diakses dari perangkat luar/HP
    app.run(host='0.0.0.0', port=5000, debug=True)
