"""
signal_analysis.py — Signal Analysis · Aerovulpis v4.1
Standalone prototype dengan dummy data.
Cybertech / institutional-grade design.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="Signal Analysis · Aerovulpis",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── DUMMY DATA ──
PAIRS = [
    {
        "symbol": "XAUUSD", "name": "Gold", "direction": "BULLISH",
        "entry": 3321.50, "sl": 3305.00, "tp1": 3338.00, "tp2": 3355.50, "tp3": 3380.00,
        "confidence": 82, "rr1": "1:1.0", "rr2": "1:2.0", "rr3": "1:3.5",
        "bull_prob": 82, "bear_prob": 18,
        "tp1_hit": False, "tp2_hit": False, "tp3_hit": False, "sl_hit": False,
        "updated": "03 Aug 2026 · 13:00 WIB",
        "explanation": "Harga Gold bergerak dalam struktur higher-high higher-low di timeframe H4. EMA 21 bertindak sebagai support dinamis yang masih terjaga. Volume beli meningkat signifikan pada sesi London open. RSI (14) berada di 58 — masih dalam zona netral menuju bullish tanpa overbought. MACD crossover positif terkonfirmasi di H1. Area entry optimal berada di retrace Fibonacci 0.382 dari swing terakhir.",
        "session": "LONDON / NEW YORK",
        "timeframe": "H4",
        "tag": "TREND FOLLOW",
    },
    {
        "symbol": "BTCUSD", "name": "Bitcoin", "direction": "BULLISH",
        "entry": 95840.00, "sl": 93200.00, "tp1": 98500.00, "tp2": 101200.00, "tp3": 105000.00,
        "confidence": 74, "rr1": "1:1.0", "rr2": "1:2.0", "rr3": "1:3.5",
        "bull_prob": 74, "bear_prob": 26,
        "tp1_hit": True, "tp2_hit": False, "tp3_hit": False, "sl_hit": False,
        "updated": "03 Aug 2026 · 08:00 WIB",
        "explanation": "BTC menunjukkan konsolidasi sehat setelah breakout dari range 90K–95K minggu lalu. On-chain data menunjukkan akumulasi oleh wallet besar (>1000 BTC). Struktur market H4 bullish dengan support kuat di 93.2K. Dominasi BTC naik ke 54.2%, mengindikasikan risk-on sentiment. TP1 sudah tercapai, potensi lanjut ke TP2 dengan trailing SL ke entry.",
        "session": "CRYPTO 24H",
        "timeframe": "H4",
        "tag": "BREAKOUT",
    },
    {
        "symbol": "BNBUSD", "name": "BNB", "direction": "BULLISH",
        "entry": 589.92, "sl": 586.43, "tp1": 593.41, "tp2": 595.73, "tp3": 599.22,
        "confidence": 69, "rr1": "1:1.0", "rr2": "1:2.0", "rr3": "1:3.0",
        "bull_prob": 74, "bear_prob": 26,
        "tp1_hit": True, "tp2_hit": True, "tp3_hit": False, "sl_hit": False,
        "updated": "03 Aug 2026 · 06:00 WIB",
        "explanation": "BNB membentuk pola ascending triangle di H1 dengan resistance di 595. Volume breakout di atas rata-rata 20 periode. Korelasi positif dengan BTC yang sedang bullish. RSI divergence bullish terdeteksi di M30. Entry zone ideal di area 588–591.",
        "session": "CRYPTO 24H",
        "timeframe": "H1",
        "tag": "PATTERN",
    },
    {
        "symbol": "EURUSD", "name": "Euro / Dollar", "direction": "BEARISH",
        "entry": 1.08420, "sl": 1.08750, "tp1": 1.08090, "tp2": 1.07760, "tp3": 1.07300,
        "confidence": 77, "rr1": "1:1.0", "rr2": "1:2.0", "rr3": "1:3.5",
        "bull_prob": 31, "bear_prob": 69,
        "tp1_hit": False, "tp2_hit": False, "tp3_hit": False, "sl_hit": True,
        "updated": "02 Aug 2026 · 20:00 WIB",
        "explanation": "EURUSD menguji resistance kuat di 1.0875 yang bertepatan dengan EMA 200 D1. Data NFP AS lebih kuat dari ekspektasi menekan Euro. Struktur bearish engulfing candle di H4 terkonfirmasi. DXY rebound dari support kritis 103.50. Signal SL telah terkena — posisi ditutup.",
        "session": "LONDON / NEW YORK",
        "timeframe": "H4",
        "tag": "REVERSAL",
    },
    {
        "symbol": "GBPUSD", "name": "Pound / Dollar", "direction": "BULLISH",
        "entry": 1.29150, "sl": 1.28600, "tp1": 1.29700, "tp2": 1.30250, "tp3": 1.31000,
        "confidence": 65, "rr1": "1:1.0", "rr2": "1:2.0", "rr3": "1:3.5",
        "bull_prob": 65, "bear_prob": 35,
        "tp1_hit": False, "tp2_hit": False, "tp3_hit": False, "sl_hit": False,
        "updated": "03 Aug 2026 · 10:00 WIB",
        "explanation": "GBP mendapat dukungan dari data CPI UK yang lebih tinggi dari ekspektasi, memperkuat ekspektasi BoE untuk mempertahankan suku bunga. Struktur bullish di D1 dengan higher low terbentuk di 1.2860. EMA 50 & 100 golden cross terkonfirmasi di H4.",
        "session": "LONDON",
        "timeframe": "H4",
        "tag": "TREND FOLLOW",
    },
    {
        "symbol": "ETHUSD", "name": "Ethereum", "direction": "BEARISH",
        "entry": 3180.00, "sl": 3280.00, "tp1": 3080.00, "tp2": 2980.00, "tp3": 2850.00,
        "confidence": 58, "rr1": "1:1.0", "rr2": "1:2.0", "rr3": "1:3.3",
        "bull_prob": 42, "bear_prob": 58,
        "tp1_hit": False, "tp2_hit": False, "tp3_hit": False, "sl_hit": False,
        "updated": "03 Aug 2026 · 07:00 WIB",
        "explanation": "ETH menunjukkan divergence bearish RSI di H4 dengan harga membentuk lower high. Dominasi BTC meningkat menekan altcoin. Resistance kuat di 3250 belum berhasil ditembus dalam 3 kali pengujian. Volume jual meningkat di sesi Asia. Risk lebih tinggi, manajemen posisi ketat diperlukan.",
        "session": "CRYPTO 24H",
        "timeframe": "H4",
        "tag": "DIVERGENCE",
    },
]

def make_forecast_chart(direction, entry, sl, tp1, tp2, tp3, symbol):
    """Generate dummy price history + forecast chart."""
    random.seed(hash(symbol) % 1000)
    n_hist = 60
    price_range = abs(tp3 - sl)
    noise = price_range * 0.04

    # History: random walk menuju entry
    hist = [entry - price_range * 0.3]
    for _ in range(n_hist - 1):
        drift = (entry - hist[-1]) * 0.03
        step = drift + random.gauss(0, noise * 0.3)
        hist.append(hist[-1] + step)
    hist[-1] = entry

    times_hist = [datetime.now() - timedelta(hours=(n_hist - i)) for i in range(n_hist)]

    # Forecast: 3 skenario
    n_fc = 30
    times_fc = [datetime.now() + timedelta(hours=i) for i in range(n_fc + 1)]

    def interp(start, end, n, noise_scale=0.3):
        pts = [start]
        for i in range(1, n + 1):
            t = i / n
            smooth = start + (end - start) * (t ** 0.7)
            pts.append(smooth + random.gauss(0, abs(end - start) * noise_scale * (1 - t * 0.5)))
        return pts

    if direction == "BULLISH":
        fc_bull = interp(entry, tp3, n_fc, 0.15)
        fc_mid  = interp(entry, tp1, n_fc, 0.1)
        fc_bear = interp(entry, sl - (tp1 - entry) * 0.5, n_fc, 0.1)
    else:
        fc_bull = interp(entry, sl + (entry - tp1) * 0.5, n_fc, 0.1)
        fc_mid  = interp(entry, tp1, n_fc, 0.1)
        fc_bear = interp(entry, tp3, n_fc, 0.15)

    fig = go.Figure()

    # History line
    fig.add_trace(go.Scatter(
        x=times_hist, y=hist,
        mode='lines',
        line=dict(color='#00d4ff', width=2),
        name='Price History',
        hovertemplate='%{y:.5g}<extra></extra>',
    ))

    # Forecast bearish
    fig.add_trace(go.Scatter(
        x=times_fc, y=fc_bear,
        mode='lines',
        line=dict(color='#ff4466', width=1.5, dash='dot'),
        name='Bearish Scenario',
        hovertemplate='%{y:.5g}<extra></extra>',
    ))

    # Forecast bullish
    fig.add_trace(go.Scatter(
        x=times_fc, y=fc_bull,
        mode='lines',
        line=dict(color='#00ff88', width=1.5, dash='dot'),
        name='Bullish Scenario',
        hovertemplate='%{y:.5g}<extra></extra>',
    ))

    # Entry marker
    fig.add_hline(y=entry, line=dict(color='#ffffff', width=1, dash='dash'), opacity=0.3)
    fig.add_hline(y=sl,    line=dict(color='#ff4466', width=1, dash='dash'), opacity=0.4)
    fig.add_hline(y=tp1,   line=dict(color='#00ff88', width=1, dash='dash'), opacity=0.25)
    fig.add_hline(y=tp3,   line=dict(color='#00ff88', width=1, dash='dash'), opacity=0.4)

    # Entry dot
    fig.add_trace(go.Scatter(
        x=[datetime.now()], y=[entry],
        mode='markers',
        marker=dict(color='#ffffff', size=8, symbol='circle',
                    line=dict(color='#00d4ff', width=2)),
        showlegend=False,
        hovertemplate=f'Entry: {entry}<extra></extra>',
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Share Tech Mono', color='rgba(136,153,187,0.7)', size=10),
        margin=dict(l=0, r=0, t=10, b=0),
        height=200,
        legend=dict(
            orientation='h', x=0, y=-0.15,
            font=dict(size=9, color='rgba(136,153,187,0.6)'),
            bgcolor='rgba(0,0,0,0)',
        ),
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(size=8),
            color='rgba(136,153,187,0.4)',
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.04)',
            zeroline=False,
            tickfont=dict(size=8),
            color='rgba(136,153,187,0.4)',
            side='right',
        ),
        hovermode='x unified',
    )
    return fig


# ── CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Share+Tech+Mono&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── BASE ── */
html, body, [class*="css"] {
    background-color: #030810 !important;
}
.block-container {
    padding: 0 1.2rem 2rem !important;
    max-width: 1400px !important;
}
#MainMenu, footer, header { visibility: hidden; }
* { box-sizing: border-box; }

/* ── TOP BAR ── */
.sm-topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: .9rem 0 1.2rem;
    border-bottom: 1px solid rgba(0,212,255,.08);
    margin-bottom: 1.4rem;
}
.sm-brand {
    font-family: 'Orbitron', sans-serif;
    font-size: .7rem; font-weight: 700; letter-spacing: 4px;
    color: #00d4ff;
}
.sm-brand span { color: rgba(136,153,187,.4); font-weight: 400; }
.sm-topbar-right {
    display: flex; align-items: center; gap: 1.2rem;
}
.sm-live-pill {
    display: inline-flex; align-items: center; gap: .4rem;
    background: rgba(0,255,136,.06);
    border: 1px solid rgba(0,255,136,.2);
    border-radius: 20px; padding: .2rem .7rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: .58rem; letter-spacing: 2px; color: #00ff88;
}
.sm-live-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: #00ff88; box-shadow: 0 0 8px #00ff88;
    animation: sm-pulse 2s ease-in-out infinite;
}
@keyframes sm-pulse {
    0%,100%{opacity:1;} 50%{opacity:.3;}
}
.sm-time {
    font-family: 'Share Tech Mono', monospace;
    font-size: .58rem; color: rgba(136,153,187,.4); letter-spacing: 1px;
}

/* ── PAGE TITLE ── */
.sm-page-title {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(1.4rem, 4vw, 2.2rem);
    font-weight: 900; letter-spacing: 5px;
    color: #e8f4ff; margin-bottom: .2rem; line-height: 1;
}
.sm-page-title span { color: #00d4ff; }
.sm-page-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: .65rem; color: rgba(136,153,187,.5);
    letter-spacing: 2px; margin-bottom: 1.4rem;
}

/* ── TICKER STRIP ── */
.sm-ticker-wrap {
    background: rgba(0,212,255,.03);
    border-top: 1px solid rgba(0,212,255,.08);
    border-bottom: 1px solid rgba(0,212,255,.08);
    padding: .45rem 0; margin-bottom: 1.6rem;
    overflow: hidden;
}
.sm-ticker-inner {
    display: flex; gap: 2.5rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: .62rem; letter-spacing: 1.5px;
    white-space: nowrap;
}
.sm-tick-item { display: flex; align-items: center; gap: .5rem; }
.sm-tick-sym { color: rgba(136,153,187,.6); }
.sm-tick-bull { color: #00ff88; }
.sm-tick-bear { color: #ff4466; }
.sm-tick-dir-bull {
    background: rgba(0,255,136,.1); color: #00ff88;
    border: 1px solid rgba(0,255,136,.25); border-radius: 2px;
    padding: 0 .35rem; font-size: .52rem; letter-spacing: 1px;
}
.sm-tick-dir-bear {
    background: rgba(255,68,102,.1); color: #ff4466;
    border: 1px solid rgba(255,68,102,.25); border-radius: 2px;
    padding: 0 .35rem; font-size: .52rem; letter-spacing: 1px;
}

/* ── STAT ROW ── */
.sm-stats-row {
    display: flex; gap: .8rem; flex-wrap: wrap;
    margin-bottom: 1.6rem;
}
.sm-stat-box {
    flex: 1; min-width: 120px;
    background: linear-gradient(160deg, #07101f, #040c18);
    border: 1px solid rgba(0,212,255,.1);
    border-radius: 6px; padding: .8rem 1rem;
    position: relative; overflow: hidden;
}
.sm-stat-box::before {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent, linear-gradient(90deg,#00d4ff,#00ff88));
    opacity: .5;
}
.sm-stat-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: .52rem; letter-spacing: 2px;
    color: rgba(136,153,187,.45); margin-bottom: .3rem;
    text-transform: uppercase;
}
.sm-stat-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.4rem; font-weight: 700;
    color: #e8f4ff; line-height: 1;
}
.sm-stat-value.bull { color: #00ff88; }
.sm-stat-value.bear { color: #ff4466; }
.sm-stat-value.warn { color: #e8b000; }

/* ── FILTER ROW ── */
.sm-filter-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: .58rem; letter-spacing: 2px;
    color: rgba(136,153,187,.4); margin-bottom: .5rem;
    text-transform: uppercase;
}

/* ── SIGNAL CARD ── */
.sm-card {
    background: linear-gradient(160deg, #070f1e 0%, #040b16 100%);
    border-radius: 10px; margin-bottom: 1.2rem;
    position: relative; overflow: hidden;
    border-top: 1px solid rgba(255,255,255,.04);
}
.sm-card.bull-card {
    border: 1px solid rgba(0,255,136,.15);
    border-left: 3px solid #00ff88;
}
.sm-card.bear-card {
    border: 1px solid rgba(255,68,102,.15);
    border-left: 3px solid #ff4466;
}
.sm-card.sl-hit {
    opacity: .6;
    border-left-color: rgba(255,68,102,.4) !important;
}

/* Card header */
.sm-card-header {
    display: flex; align-items: flex-start;
    justify-content: space-between;
    padding: 1rem 1.2rem .7rem;
    border-bottom: 1px solid rgba(255,255,255,.04);
}
.sm-card-header-left { display: flex; flex-direction: column; gap: .15rem; }
.sm-symbol {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem; font-weight: 700; letter-spacing: 2px;
    color: #e8f4ff;
}
.sm-pair-name {
    font-family: 'Share Tech Mono', monospace;
    font-size: .6rem; color: rgba(136,153,187,.5); letter-spacing: 1.5px;
}
.sm-card-header-right {
    display: flex; flex-direction: column; align-items: flex-end; gap: .35rem;
}
.sm-dir-badge-bull {
    font-family: 'Orbitron', sans-serif; font-size: .62rem;
    font-weight: 700; letter-spacing: 3px;
    background: rgba(0,255,136,.1);
    border: 1px solid rgba(0,255,136,.3);
    color: #00ff88; padding: .25rem .7rem; border-radius: 3px;
}
.sm-dir-badge-bear {
    font-family: 'Orbitron', sans-serif; font-size: .62rem;
    font-weight: 700; letter-spacing: 3px;
    background: rgba(255,68,102,.1);
    border: 1px solid rgba(255,68,102,.3);
    color: #ff4466; padding: .25rem .7rem; border-radius: 3px;
}
.sm-meta-row {
    display: flex; gap: .5rem; align-items: center;
}
.sm-meta-pill {
    font-family: 'Share Tech Mono', monospace; font-size: .52rem;
    letter-spacing: 1.5px; color: rgba(136,153,187,.4);
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.06);
    border-radius: 2px; padding: .1rem .4rem;
}
.sm-tag-pill {
    font-family: 'Share Tech Mono', monospace; font-size: .52rem;
    letter-spacing: 1.5px; color: #00d4ff;
    background: rgba(0,212,255,.06);
    border: 1px solid rgba(0,212,255,.15);
    border-radius: 2px; padding: .1rem .4rem;
}

/* Card body: entry/sl/tp grid */
.sm-card-body { padding: .9rem 1.2rem; }
.sm-price-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: .6rem .8rem; margin-bottom: .9rem;
}
.sm-price-block {}
.sm-price-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: .52rem; letter-spacing: 2px;
    color: rgba(136,153,187,.4); text-transform: uppercase;
    margin-bottom: .2rem;
}
.sm-price-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.4rem; font-weight: 700; letter-spacing: 1px;
    color: #e8f4ff; line-height: 1;
}
.sm-price-value.cyan { color: #00d4ff; }
.sm-price-value.red  { color: #ff4466; }

/* SL hit badge */
.sm-sl-badge {
    display: inline-flex; align-items: center; gap: .3rem;
    background: rgba(255,68,102,.1); border: 1px solid rgba(255,68,102,.35);
    border-radius: 3px; padding: .15rem .5rem; margin-left: .5rem;
    font-family: 'Share Tech Mono', monospace; font-size: .55rem;
    letter-spacing: 1.5px; color: #ff4466; vertical-align: middle;
}

/* Confidence bar */
.sm-conf-row {
    display: flex; align-items: center; gap: .8rem;
    margin-bottom: 1rem;
}
.sm-conf-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: .52rem; letter-spacing: 2px;
    color: rgba(136,153,187,.4); width: 80px; flex-shrink: 0;
}
.sm-conf-bar-wrap {
    flex: 1; height: 4px; background: rgba(255,255,255,.05);
    border-radius: 4px; overflow: hidden;
}
.sm-conf-fill {
    height: 100%; border-radius: 4px;
}
.sm-conf-pct {
    font-family: 'Orbitron', sans-serif; font-size: .7rem;
    font-weight: 700; width: 40px; text-align: right; flex-shrink: 0;
}
.sm-rr-label {
    font-family: 'Share Tech Mono', monospace; font-size: .55rem;
    letter-spacing: 1.5px; color: rgba(136,153,187,.4);
    width: 60px; flex-shrink: 0; text-align: right;
}

/* TP rows */
.sm-tp-grid { display: flex; flex-direction: column; gap: .5rem; margin-bottom: .9rem; }
.sm-tp-row {
    display: flex; align-items: center; gap: .6rem;
}
.sm-tp-badge {
    font-family: 'Orbitron', sans-serif; font-size: .55rem;
    font-weight: 700; letter-spacing: 1px;
    background: rgba(0,255,136,.1); border: 1px solid rgba(0,255,136,.25);
    color: #00ff88; padding: .2rem .5rem; border-radius: 3px;
    width: 44px; text-align: center; flex-shrink: 0;
}
.sm-tp-price {
    font-family: 'Orbitron', sans-serif; font-size: 1.05rem;
    font-weight: 700; color: #e8f4ff; flex: 1;
}
.sm-tp-hit {
    display: inline-flex; align-items: center; gap: .25rem;
    background: rgba(255,68,102,.08); border: 1px solid rgba(255,68,102,.25);
    border-radius: 3px; padding: .1rem .4rem;
    font-family: 'Share Tech Mono', monospace; font-size: .52rem;
    letter-spacing: 1px; color: #ff4466;
}
.sm-tp-ok {
    display: inline-flex; align-items: center; gap: .25rem;
    background: rgba(0,255,136,.08); border: 1px solid rgba(0,255,136,.25);
    border-radius: 3px; padding: .1rem .4rem;
    font-family: 'Share Tech Mono', monospace; font-size: .52rem;
    letter-spacing: 1px; color: #00ff88;
}
.sm-rr-chip {
    font-family: 'Share Tech Mono', monospace; font-size: .58rem;
    color: rgba(0,212,255,.7); background: rgba(0,212,255,.07);
    border: 1px solid rgba(0,212,255,.15);
    border-radius: 3px; padding: .1rem .45rem;
    flex-shrink: 0;
}

/* Trend forecast bar */
.sm-forecast-row {
    display: flex; gap: .5rem; margin-bottom: .9rem;
}
.sm-forecast-box {
    flex: 1; padding: .55rem .8rem; border-radius: 5px;
    font-family: 'Share Tech Mono', monospace;
    font-size: .62rem; letter-spacing: 1.5px;
}
.sm-forecast-bull {
    background: rgba(0,255,136,.06);
    border: 1px solid rgba(0,255,136,.2); color: #00ff88;
}
.sm-forecast-bear {
    background: rgba(255,68,102,.06);
    border: 1px solid rgba(255,68,102,.2); color: #ff4466;
    text-align: right;
}
.sm-forecast-val {
    font-family: 'Orbitron', sans-serif;
    font-size: .9rem; font-weight: 700;
}

/* Explanation section */
.sm-explanation {
    background: rgba(0,212,255,.02);
    border: 1px solid rgba(0,212,255,.08);
    border-radius: 6px; padding: .9rem 1rem;
    margin-top: .4rem;
}
.sm-expl-label {
    font-family: 'Orbitron', sans-serif; font-size: .52rem;
    letter-spacing: 3px; text-transform: uppercase;
    color: rgba(0,212,255,.4); margin-bottom: .5rem; font-weight: 700;
}
.sm-expl-text {
    font-family: 'Inter', sans-serif; font-size: .8rem;
    color: rgba(160,185,210,.7); line-height: 1.75;
}

/* updated */
.sm-updated {
    font-family: 'Share Tech Mono', monospace; font-size: .55rem;
    color: rgba(136,153,187,.3); letter-spacing: 1.5px;
    padding: .5rem 1.2rem .9rem; text-align: right;
}

/* Divider */
.sm-section-title {
    font-family: 'Orbitron', sans-serif;
    font-size: .72rem; font-weight: 700; letter-spacing: 4px;
    text-transform: uppercase; color: #00d4ff;
    display: flex; align-items: center; gap: .7rem;
    margin-bottom: 1rem; margin-top: .5rem;
}
.sm-section-title::before { content:''; width:24px; height:1px; background:#00d4ff; opacity:.5; }
.sm-section-title::after  { content:''; flex:1; height:1px; background:rgba(0,212,255,.1); }

/* responsive */
@media(max-width:700px) {
    .sm-price-value { font-size: 1.1rem; }
    .sm-stat-value  { font-size: 1.1rem; }
    .sm-stats-row   { gap: .5rem; }
}
</style>
""", unsafe_allow_html=True)


# ── TOPBAR ──
now_str = datetime.now().strftime("%d %b %Y · %H:%M WIB")
st.markdown(f"""
<div class="sm-topbar">
<div class="sm-brand">AEROVULPIS <span>· SIGNAL MATRIX v4.1</span></div>
<div class="sm-topbar-right">
<div class="sm-live-pill"><div class="sm-live-dot"></div> LIVE FEED</div>
<div class="sm-time">{now_str}</div>
</div>
</div>
""", unsafe_allow_html=True)

# ── PAGE TITLE ──
st.markdown("""
<div class="sm-page-title">SIGNAL <span>ANALYSIS</span></div>
<div class="sm-page-sub">Live trading signal untuk XAUUSD, BTCUSD, ETHUSD, SOLUSD, BNBUSD, XRPUSD, EURUSD, GBPUSD, AUDUSD, USDJPY &nbsp;|&nbsp; Update otomatis setiap 19 jam</div>
""", unsafe_allow_html=True)

# ── TICKER STRIP ──
ticker_html = '<div class="sm-ticker-wrap"><div class="sm-ticker-inner">'
for p in PAIRS:
    d_class = "sm-tick-bull" if p["direction"] == "BULLISH" else "sm-tick-bear"
    dir_class = "sm-tick-dir-bull" if p["direction"] == "BULLISH" else "sm-tick-dir-bear"
    ticker_html += f"""
<div class="sm-tick-item">
<span class="sm-tick-sym">{p['symbol']}</span>
<span class="{d_class}">{p['entry']}</span>
<span class="{dir_class}">{p['direction'][:4]}</span>
</div>"""
ticker_html += '</div></div>'
st.markdown(ticker_html, unsafe_allow_html=True)

# ── STATS ──
total = len(PAIRS)
bull_count = sum(1 for p in PAIRS if p["direction"] == "BULLISH")
bear_count = total - bull_count
sl_count = sum(1 for p in PAIRS if p["sl_hit"])
tp_count = sum(1 for p in PAIRS if p["tp1_hit"] or p["tp2_hit"] or p["tp3_hit"])
avg_conf = int(sum(p["confidence"] for p in PAIRS) / total)

st.markdown(f"""
<div class="sm-stats-row">
<div class="sm-stat-box" style="--accent:linear-gradient(90deg,#00d4ff,#00ff88)">
<div class="sm-stat-label">Total Signal</div>
<div class="sm-stat-value">{total}</div>
</div>
<div class="sm-stat-box" style="--accent:linear-gradient(90deg,#00ff88,#00ff88)">
<div class="sm-stat-label">Bullish</div>
<div class="sm-stat-value bull">{bull_count}</div>
</div>
<div class="sm-stat-box" style="--accent:linear-gradient(90deg,#ff4466,#ff4466)">
<div class="sm-stat-label">Bearish</div>
<div class="sm-stat-value bear">{bear_count}</div>
</div>
<div class="sm-stat-box" style="--accent:linear-gradient(90deg,#00ff88,#00d4ff)">
<div class="sm-stat-label">TP Tercapai</div>
<div class="sm-stat-value cyan">{tp_count}</div>
</div>
<div class="sm-stat-box" style="--accent:linear-gradient(90deg,#ff4466,#e8b000)">
<div class="sm-stat-label">SL Terkena</div>
<div class="sm-stat-value warn">{sl_count}</div>
</div>
<div class="sm-stat-box" style="--accent:linear-gradient(90deg,#00d4ff,#7b61ff)">
<div class="sm-stat-label">Avg Confidence</div>
<div class="sm-stat-value">{avg_conf}%</div>
</div>
</div>
""", unsafe_allow_html=True)

# ── FILTER ──
col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
with col_f1:
    st.markdown('<div class="sm-filter-label">Direction Filter</div>', unsafe_allow_html=True)
    dir_filter = st.selectbox("direction", ["ALL", "BULLISH", "BEARISH"], label_visibility="collapsed")
with col_f2:
    st.markdown('<div class="sm-filter-label">Status Filter</div>', unsafe_allow_html=True)
    status_filter = st.selectbox("status", ["ALL", "ACTIVE", "TP HIT", "SL HIT"], label_visibility="collapsed")
with col_f3:
    st.markdown('<div class="sm-filter-label">Pairs</div>', unsafe_allow_html=True)
    all_syms = [p["symbol"] for p in PAIRS]
    sym_filter = st.multiselect("pairs", all_syms, default=all_syms, label_visibility="collapsed")

# Filter logic
filtered = []
for p in PAIRS:
    if sym_filter and p["symbol"] not in sym_filter:
        continue
    if dir_filter != "ALL" and p["direction"] != dir_filter:
        continue
    if status_filter == "ACTIVE" and (p["sl_hit"] or p["tp3_hit"]):
        continue
    if status_filter == "TP HIT" and not (p["tp1_hit"] or p["tp2_hit"] or p["tp3_hit"]):
        continue
    if status_filter == "SL HIT" and not p["sl_hit"]:
        continue
    filtered.append(p)

st.markdown('<br>', unsafe_allow_html=True)
st.markdown(f'<div class="sm-section-title">Signal Feed &nbsp;<span style="color:rgba(136,153,187,.3);font-size:.65rem;letter-spacing:2px">({len(filtered)} SINYAL)</span></div>', unsafe_allow_html=True)

# ── SIGNAL CARDS ──
if not filtered:
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:.75rem;color:rgba(136,153,187,.4);text-align:center;padding:3rem 0;">— Tidak ada sinyal yang cocok dengan filter —</div>', unsafe_allow_html=True)

for p in filtered:
    is_bull = p["direction"] == "BULLISH"
    card_class = ("bull-card" if is_bull else "bear-card") + (" sl-hit" if p["sl_hit"] else "")
    dir_badge_class = "sm-dir-badge-bull" if is_bull else "sm-dir-badge-bear"
    conf = p["confidence"]
    conf_color = "#00ff88" if conf >= 70 else ("#e8b000" if conf >= 55 else "#ff4466")

    # TP/SL status badges
    def tp_badge(hit):
        return '<span class="sm-tp-ok">✓ HIT</span>' if hit else '<span class="sm-tp-hit">✗ OPEN</span>'

    sl_badge_html = '<span class="sm-sl-badge">✗ SL HIT</span>' if p["sl_hit"] else ""

    st.markdown(f"""
<div class="sm-card {card_class}">
<div class="sm-card-header">
<div class="sm-card-header-left">
<div class="sm-symbol">{p['symbol']}</div>
<div class="sm-pair-name">{p['name']}</div>
</div>
<div class="sm-card-header-right">
<span class="{dir_badge_class}">{p['direction']}</span>
<div class="sm-meta-row">
<span class="sm-meta-pill">{p['timeframe']}</span>
<span class="sm-meta-pill">{p['session']}</span>
<span class="sm-tag-pill">{p['tag']}</span>
</div>
</div>
</div>
<div class="sm-card-body">
<div class="sm-price-grid">
<div class="sm-price-block">
<div class="sm-price-label">Entry</div>
<div class="sm-price-value cyan">{p['entry']}</div>
</div>
<div class="sm-price-block">
<div class="sm-price-label">Stop Loss</div>
<div class="sm-price-value red">{p['sl']}{sl_badge_html}</div>
</div>
<div class="sm-price-block">
<div class="sm-price-label">Risk : Reward</div>
<div class="sm-price-value" style="font-size:1.1rem">{p['rr1']}</div>
</div>
<div class="sm-price-block">
<div class="sm-price-label">Confidence</div>
<div class="sm-price-value" style="color:{conf_color};font-size:1.4rem">{conf}%</div>
</div>
</div>

<div class="sm-conf-row">
<div class="sm-conf-label">CONFIDENCE</div>
<div class="sm-conf-bar-wrap">
<div class="sm-conf-fill" style="width:{conf}%;background:linear-gradient(90deg,#00d4ff,{conf_color})"></div>
</div>
<div class="sm-conf-pct" style="color:{conf_color}">{conf}%</div>
</div>

<div class="sm-tp-grid">
<div class="sm-tp-row">
<span class="sm-tp-badge">TP 1</span>
<span class="sm-tp-price">{p['tp1']}</span>
{tp_badge(p['tp1_hit'])}
<span class="sm-rr-chip">R:R {p['rr1']}</span>
</div>
<div class="sm-tp-row">
<span class="sm-tp-badge">TP 2</span>
<span class="sm-tp-price">{p['tp2']}</span>
{tp_badge(p['tp2_hit'])}
<span class="sm-rr-chip">R:R {p['rr2']}</span>
</div>
<div class="sm-tp-row">
<span class="sm-tp-badge">TP 3</span>
<span class="sm-tp-price">{p['tp3']}</span>
{tp_badge(p['tp3_hit'])}
<span class="sm-rr-chip">R:R {p['rr3']}</span>
</div>
</div>

<div class="sm-forecast-row">
<div class="sm-forecast-box sm-forecast-bull">
<div style="font-size:.52rem;letter-spacing:2px;opacity:.6;margin-bottom:.2rem">BULLISH PROB</div>
<div class="sm-forecast-val">[{p['bull_prob']}%]</div>
</div>
<div class="sm-forecast-box sm-forecast-bear">
<div style="font-size:.52rem;letter-spacing:2px;opacity:.6;margin-bottom:.2rem">BEARISH PROB</div>
<div class="sm-forecast-val">[{p['bear_prob']}%]</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

    # Chart
    with st.container():
        fig = make_forecast_chart(
            p["direction"], p["entry"], p["sl"],
            p["tp1"], p["tp2"], p["tp3"], p["symbol"]
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Explanation
    st.markdown(f"""
<div class="sm-explanation" style="margin: 0 1.2rem .5rem">
<div class="sm-expl-label">Signal Analysis Explanation</div>
<div class="sm-expl-text">{p['explanation']}</div>
</div>
<div class="sm-updated">LAST UPDATE · {p['updated']}</div>
</div>
""", unsafe_allow_html=True)

# ── FOOTER ──
st.markdown("""
<div style="text-align:center;padding:1.5rem 0 .5rem;border-top:1px solid rgba(0,212,255,.06);margin-top:1rem">
<div style="font-family:'Orbitron',sans-serif;font-size:.65rem;letter-spacing:3px;color:#00d4ff;font-weight:700;margin-bottom:.3rem">AEROVULPIS · SIGNAL MATRIX</div>
<div style="font-family:'Share Tech Mono',monospace;font-size:.55rem;color:rgba(136,153,187,.3);letter-spacing:1.5px">Data dummy untuk prototype · Integrasi Supabase menyusul · aerovulpis.my.id</div>
</div>
""", unsafe_allow_html=True)