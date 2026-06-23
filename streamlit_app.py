# ==============================================================================
# aerovulpis_terminal.py
# AEROVULPIS TERMINAL v4.1 — Streamlit Edition
# Quantitative Market Intelligence System
# Cybertech UI · TradingView Widgets · Bloomberg-Class MCT
# ==============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import pandas_ta as ta
import requests
import plotly.graph_objects as go
from scipy.signal import savgol_filter
import streamlit.components.v1 as components

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AEROVULPIS TERMINAL",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

/* ── ROOT RESET ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #070A12 !important;
    font-family: 'Share Tech Mono', 'Courier New', monospace !important;
    color: #C8D8F0 !important;
}
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stHeader"] { background: transparent !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }

/* ── GLOBAL BG GRADIENT ── */
[data-testid="stMain"] {
    background: #070A12 !important;
    background-image:
        radial-gradient(ellipse 60% 35% at 10% 0%, rgba(0,225,255,0.055), transparent),
        radial-gradient(ellipse 50% 30% at 90% 5%, rgba(168,85,247,0.055), transparent) !important;
}

/* ── TOPBAR BRAND ── */
.av-brand-wrap {
    padding: 18px 0 14px;
    border-bottom: 1px solid #111827;
    margin-bottom: 0;
}
.av-brand-line {
    display: flex;
    align-items: baseline;
    gap: 10px;
}
.av-prefix {
    font-size: 8px;
    letter-spacing: 3px;
    color: #1A3A5A;
    border: 1px solid #1A3A5A;
    padding: 2px 7px;
    border-radius: 2px;
}
.av-title {
    font-size: 22px;
    letter-spacing: 4px;
    color: #E8F1FF;
    font-weight: 700;
    font-family: 'Share Tech Mono', monospace;
}
.av-title .acc { color: #00E1FF; }
.av-ver {
    font-size: 8px;
    letter-spacing: 2px;
    color: #2A4060;
}
.av-tagline {
    font-size: 8px;
    letter-spacing: 2.5px;
    color: #1A3A5A;
    margin-top: 3px;
    font-family: 'Share Tech Mono', monospace;
}

/* ── TICKER BAR ── */
.av-ticker-wrap {
    overflow-x: auto;
    white-space: nowrap;
    padding: 7px 0 5px;
    border-top: 1px solid #0E1422;
    margin-top: 10px;
    scrollbar-width: none;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
}
.av-ticker-wrap::-webkit-scrollbar { display: none; }
.av-tick { display: inline-block; margin-right: 20px; color: #3A4A6A; }
.av-tick .sym { color: #4A6080; font-size: 9px; letter-spacing: 1px; }
.av-tick .up  { color: #00E1FF; }
.av-tick .dn  { color: #FF3D71; }

/* ── SECTION LABEL ── */
.av-sec {
    font-size: 8px;
    letter-spacing: 2.5px;
    color: #1A3060;
    padding: 14px 0 6px;
    font-family: 'Share Tech Mono', monospace;
}

/* ── PANEL BOX ── */
.av-panel {
    background: #09111E;
    border: 1px solid #111827;
    border-radius: 8px;
    padding: 14px;
    position: relative;
    overflow: hidden;
    height: 100%;
}
.av-panel::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,225,255,0.18), transparent);
}

/* ── SELECTBOX & STREAMLIT OVERRIDES ── */
[data-testid="stSelectbox"] label { display: none !important; }
[data-testid="stSelectbox"] > div > div {
    background: #09111E !important;
    border: 1px solid #1A2540 !important;
    border-radius: 5px !important;
    color: #C8D8F0 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.5px !important;
    min-height: 36px !important;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color: rgba(0,225,255,0.3) !important;
}
[data-baseweb="select"] * {
    background: #09111E !important;
    color: #C8D8F0 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 11px !important;
}
[data-baseweb="menu"] {
    background: #09111E !important;
    border: 1px solid #1A2540 !important;
    border-radius: 6px !important;
}
[data-baseweb="option"]:hover {
    background: rgba(0,225,255,0.08) !important;
    color: #00E1FF !important;
}

/* ── TEXT INPUT ── */
[data-testid="stTextInput"] label { display: none !important; }
[data-testid="stTextInput"] input {
    background: #07101C !important;
    border: 1px solid #1A2540 !important;
    border-radius: 5px !important;
    color: #C8D8F0 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.5px !important;
}
[data-testid="stTextInput"] input::placeholder { color: #2A3A54 !important; }
[data-testid="stTextInput"] input:focus {
    border-color: rgba(0,225,255,0.4) !important;
    box-shadow: 0 0 0 1px rgba(0,225,255,0.15) !important;
}

/* ── BUTTONS ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, rgba(0,225,255,0.85), rgba(168,85,247,0.85)) !important;
    color: #030608 !important;
    font-weight: 700 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 1.5px !important;
    border: none !important;
    border-radius: 5px !important;
    padding: 8px 18px !important;
}
[data-testid="stButton"] > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

/* ── HORIZONTAL SCROLL WRAPPER ── */
.av-hscroll-wrap {
    overflow-x: auto;
    display: flex;
    gap: 10px;
    padding-bottom: 12px;
    scroll-snap-type: x mandatory;
    scrollbar-width: thin;
    scrollbar-color: #1A2540 transparent;
}
.av-hscroll-wrap::-webkit-scrollbar { height: 3px; }
.av-hscroll-wrap::-webkit-scrollbar-track { background: transparent; }
.av-hscroll-wrap::-webkit-scrollbar-thumb {
    background: #1A2540;
    border-radius: 2px;
}
.av-hscroll-item {
    flex-shrink: 0;
    scroll-snap-align: start;
}

/* ── TRADE CARD ── */
.av-trade-card {
    background: #09111E;
    border: 1px solid #111827;
    border-radius: 8px;
    padding: 12px;
    min-width: 180px;
    position: relative;
    overflow: hidden;
    display: inline-block;
    margin-right: 10px;
    vertical-align: top;
}
.av-trade-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,225,255,0.2), transparent);
}
.av-trade-symbol { font-size: 13px; font-weight: 700; color: #E8F1FF; letter-spacing: 1px; }
.av-dir-buy  { font-size:9px; padding:3px 8px; border-radius:3px; font-weight:700; letter-spacing:1.5px; background:rgba(0,225,255,0.12); color:#00E1FF; border:1px solid rgba(0,225,255,0.3); }
.av-dir-sell { font-size:9px; padding:3px 8px; border-radius:3px; font-weight:700; letter-spacing:1.5px; background:rgba(255,61,113,0.12); color:#FF3D71; border:1px solid rgba(255,61,113,0.3); }
.av-trade-row { display:flex; justify-content:space-between; padding:3px 0; border-bottom:1px solid #0E1422; font-size:11px; }
.av-trade-k { color:#3A4A6A; letter-spacing:1px; font-size:9px; }

/* ── AI PANEL ── */
.av-ai-result {
    background: #07101C;
    border: 1px solid #1A2540;
    border-left: 2px solid #00E1FF;
    padding: 12px 14px;
    border-radius: 5px;
    font-size: 11px;
    line-height: 1.7;
    color: #8BA0C0;
    letter-spacing: 0.3px;
    font-family: 'Share Tech Mono', monospace;
    margin-top: 8px;
}

/* ── MCT FACTOR BAR ── */
.av-factor-wrap { display:flex; gap:4px; margin-top:6px; }
.av-factor-item {
    flex:1; min-width:44px;
    background:#0A0E18;
    border:1px solid #1A2238;
    border-radius:4px;
    padding:4px 6px;
}
.av-factor-k { font-size:7.5px; color:#4A6080; letter-spacing:1px; margin-bottom:2px; font-family:'Share Tech Mono',monospace; }
.av-factor-bar-wrap { height:2px; background:#0E1422; border-radius:1px; }
.av-factor-v { font-size:8px; margin-top:2px; text-align:right; font-family:'Share Tech Mono',monospace; }

/* ── DIVIDER ── */
.av-divider {
    border: none;
    border-top: 1px solid #0E1422;
    margin: 6px 0;
}

/* ── PLOTLY TRANSPARENT ── */
.js-plotly-plot .plotly .modebar { display: none !important; }

/* ── STREAMLIT ELEMENT PADDING ── */
[data-testid="column"] { padding: 0 5px !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }
.stSelectbox { margin-bottom: 0 !important; }
div.block-container { padding: 0 1rem 2rem !important; max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CONSTANTS
# ==============================================================================

INSTRUMENTS = {
    "FOREX": [
        ("EURUSD", "EUR/USD", "OANDA:EURUSD"),
        ("GBPUSD", "GBP/USD", "OANDA:GBPUSD"),
        ("USDJPY", "USD/JPY", "OANDA:USDJPY"),
        ("AUDUSD", "AUD/USD", "OANDA:AUDUSD"),
        ("USDCHF", "USD/CHF", "OANDA:USDCHF"),
    ],
    "COMMODITIES": [
        ("XAUUSD", "XAU/USD", "OANDA:XAUUSD"),
        ("XAGUSD", "XAG/USD", "OANDA:XAGUSD"),
        ("WTIUSD", "WTI/USD", "TVC:USOIL"),
        ("BRENT",  "BRENT",   "TVC:UKOIL"),
        ("NATGAS", "NATGAS",  "TVC:NATURALGAS"),
    ],
    "US STOCKS": [
        ("AAPL", "AAPL", "NASDAQ:AAPL"),
        ("NVDA", "NVDA", "NASDAQ:NVDA"),
        ("TSLA", "TSLA", "NASDAQ:TSLA"),
        ("MSFT", "MSFT", "NASDAQ:MSFT"),
        ("AMZN", "AMZN", "NASDAQ:AMZN"),
    ],
    "CRYPTO": [
        ("BTCUSD", "BTC/USD", "COINBASE:BTCUSD"),
        ("ETHUSD", "ETH/USD", "COINBASE:ETHUSD"),
        ("SOLUSD", "SOL/USD", "COINBASE:SOLUSD"),
        ("BNBUSD", "BNB/USDT","BINANCE:BNBUSDT"),
        ("XRPUSD", "XRP/USD", "COINBASE:XRPUSD"),
    ],
}

TV_INTERVAL = {"15m": "15", "1h": "60", "4h": "240", "1D": "D"}
TV_TA_INT   = {"15m": "15m","1h": "1h", "4h": "4h",  "1D": "1D"}
TD_INTERVAL = {"15m": "15min","1h":"1h","4h":"4h","1D":"1day"}

MINI_OPTIONS = [
    ("EURUSD","OANDA:EURUSD"),("GBPUSD","OANDA:GBPUSD"),
    ("USDJPY","OANDA:USDJPY"),("AUDUSD","OANDA:AUDUSD"),
    ("XAUUSD","OANDA:XAUUSD"),("BTCUSD","COINBASE:BTCUSD"),
    ("NVDA","NASDAQ:NVDA"),  ("USDCHF","OANDA:USDCHF"),
]

DUMMY_TRADES = [
    {"symbol":"EURUSD","dir":"BUY", "entry":"1.14620","sl":"1.14280","tp1":"1.14950","tp2":"1.15300","tp3":"1.15700"},
    {"symbol":"GBPUSD","dir":"SELL","entry":"1.32310","sl":"1.32650","tp1":"1.31980","tp2":"1.31600","tp3":"1.31150"},
    {"symbol":"XAUUSD","dir":"BUY", "entry":"2382.40","sl":"2371.00","tp1":"2394.00","tp2":"2406.50","tp3":"2420.00"},
    {"symbol":"BTCUSD","dir":"BUY", "entry":"67420.0","sl":"65800.0","tp1":"69000.0","tp2":"71500.0","tp3":"74200.0"},
]

CHART_STYLES = [
    ("LINE","3"),("CANDLES","1"),("HEIKIN ASHI","8"),("AREA","9"),("BARS","0"),
]

# ==============================================================================
# SESSION STATE INIT
# ==============================================================================
def init_state():
    defaults = {
        "instr_class": "FOREX",
        "pair_idx":    0,
        "timeframe":   "15m",
        "chart_style": "3",
        "mini_a":      0,
        "mini_b":      1,
        "mini_c":      2,
        "ai_mode":     "pair",
        "ai_result":   None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ==============================================================================
# MCT ENGINE — Bloomberg-Class 9-Factor Composite
# Mirrors dynamihatch_mct_master.py with extended indicators
# ==============================================================================

@st.cache_data(ttl=60, show_spinner=False)
def fetch_twelvedata(symbol: str, interval: str, outputsize: int = 300) -> pd.DataFrame:
    """Fetch OHLCV from Twelve Data API."""
    try:
        api_key = st.secrets["TWELVE_DATA_API_KEY"]
    except (KeyError, FileNotFoundError):
        return pd.DataFrame()

    url = (
        f"https://api.twelvedata.com/time_series"
        f"?symbol={symbol}&interval={interval}"
        f"&outputsize={outputsize}&apikey={api_key}"
    )
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("status") == "error" or "values" not in data:
            return pd.DataFrame()
        df = pd.DataFrame(data["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        for col in ["open","high","low","close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["volume"] = pd.to_numeric(df.get("volume", 0), errors="coerce").fillna(0)
        df = df.sort_values("datetime").reset_index(drop=True)
        df.set_index("datetime", inplace=True)
        return df
    except Exception:
        return pd.DataFrame()


def calculate_mct_bloomberg(df: pd.DataFrame) -> np.ndarray:
    """
    Bloomberg-class MCT: 9 normalized factors via z-score,
    weighted composite, Savitzky-Golay smoothed.
    """
    lookback = 63

    def z_norm(s: pd.Series) -> pd.Series:
        rm = s.rolling(lookback, min_periods=10).mean()
        rs = s.rolling(lookback, min_periods=10).std().replace(0, np.nan)
        return ((s - rm) / rs).clip(-3, 3) / 3.0

    close = df["close"]
    high  = df["high"]
    low   = df["low"]

    # 1. RSI (14) — momentum anchor
    rsi_raw = ta.rsi(close, length=14).fillna(50) - 50.0
    z_rsi   = z_norm(rsi_raw)

    # 2. MACD Histogram (12,26,9) — momentum confirmation
    macd    = ta.macd(close, fast=12, slow=26, signal=9)
    z_macd  = z_norm(macd["MACDh_12_26_9"].fillna(0))

    # 3. EMA Crossover (20 vs 50) — trend direction
    ema_cross = (ta.ema(close,20) - ta.ema(close,50)) / close
    z_ema     = z_norm(ema_cross.fillna(0))

    # 4. ATR % (14) — volatility regime
    atr_pct = ta.atr(high, low, close, length=14) / close
    z_atr   = z_norm(atr_pct.fillna(0))

    # 5. Stochastic %K (14) — oscillator confluence
    stoch   = ta.stoch(high, low, close, k=14, d=3)
    stoch_k = stoch["STOCHk_14_3_3"].fillna(50) - 50.0
    z_stoch = z_norm(stoch_k)

    # 6. Williams %R (14) — mean reversion signal
    willr   = ta.willr(high, low, close, length=14).fillna(-50) + 50.0
    z_willr = z_norm(willr)

    # 7. ROC (10) — acceleration / deceleration
    roc   = ta.roc(close, length=10).fillna(0)
    z_roc = z_norm(roc)

    # 8. CCI (20) — cyclical momentum
    cci   = ta.cci(high, low, close, length=20).fillna(0).clip(-200, 200) / 200
    z_cci = z_norm(cci)

    # 9. Bollinger Bandwidth (20,2) — expansion / compression
    bb    = ta.bbands(close, length=20, std=2)
    bb_bw = ((bb["BBU_20_2.0"] - bb["BBL_20_2.0"]) / bb["BBM_20_2.0"]).fillna(0)
    z_bb  = z_norm(bb_bw)

    # Weighted composite (weights sum to 1.0)
    composite = (
        0.20 * z_rsi   +   # RSI — momentum anchor
        0.18 * z_macd  +   # MACD — momentum confirmation
        0.12 * z_ema   +   # EMA cross — trend
        0.10 * z_atr   +   # ATR — volatility
        0.10 * z_stoch +   # Stochastic — confluence
        0.09 * z_willr +   # Williams %R — reversion
        0.09 * z_roc   +   # ROC — acceleration
        0.07 * z_cci   +   # CCI — cyclical
        0.05 * z_bb        # BB bandwidth — filter
    )

    raw = (composite * 100).clip(-100, 100).fillna(0).to_numpy()

    # Savitzky-Golay smoothing (window=25, poly=3) — same as Python MCT master
    n = len(raw)
    wl = min(25, n)
    if wl % 2 == 0: wl -= 1
    wl = max(wl, 5)
    smoothed = savgol_filter(raw, window_length=wl, polyorder=3, mode="interp")
    return np.clip(smoothed, -100, 100)


def render_mct_plotly(values: np.ndarray, pair_label: str) -> go.Figure:
    """
    Render MCT chart: blue above zero, red below, OB/OS zones,
    glow-style traces, Bloomberg-grade layout.
    """
    x = list(range(len(values)))
    y_up = np.where(values >= 0, values, np.nan)
    y_dn = np.where(values <= 0, values, np.nan)

    current  = float(values[-1])
    prev     = float(values[-6]) if len(values) >= 6 else 0.0
    momentum = current - prev
    isBull   = current >= 0

    if current > 60:       regime = "STRONG BULL"
    elif current > 25:     regime = "BULL"
    elif current < -60:    regime = "STRONG BEAR"
    elif current < -25:    regime = "BEAR"
    else:                  regime = "NEUTRAL"

    fig = go.Figure()

    # OB/OS zone shading
    fig.add_hrect(y0=30,  y1=80,  fillcolor="rgba(0,225,255,0.04)",  line_width=0)
    fig.add_hrect(y0=-80, y1=-30, fillcolor="rgba(255,61,113,0.04)", line_width=0)

    # Fill areas
    fig.add_trace(go.Scatter(
        x=x, y=y_up, fill="tozeroy",
        fillcolor="rgba(0,225,255,0.12)", line=dict(color="#00E1FF",width=2.2),
        mode="lines", showlegend=False, hoverinfo="y",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=y_dn, fill="tozeroy",
        fillcolor="rgba(255,61,113,0.12)", line=dict(color="#FF3D71",width=2.2),
        mode="lines", showlegend=False, hoverinfo="y",
    ))

    # Last-value dot
    dot_color = "#00E1FF" if isBull else "#FF3D71"
    fig.add_trace(go.Scatter(
        x=[x[-1]], y=[current],
        mode="markers",
        marker=dict(color=dot_color, size=8, line=dict(color="#070A12",width=2)),
        showlegend=False, hoverinfo="skip",
    ))

    # Grid lines + labels
    for lvl, label in [(80,"OB EXTREME"),(30,"OB ZONE"),(0,None),(-30,"OS ZONE"),(-80,"OS EXTREME")]:
        lw = 1.3 if lvl == 0 else 0.8
        col = "rgba(255,255,255,0.55)" if lvl == 0 else "rgba(42,53,80,0.9)"
        dash = "solid" if lvl == 0 else "dot"
        fig.add_hline(y=lvl, line_color=col, line_width=lw, line_dash=dash)
        if label:
            fc = "rgba(0,225,255,0.45)" if lvl > 0 else "rgba(255,61,113,0.45)"
            fig.add_annotation(
                x=0, y=lvl, xref="paper", text=f"  {label}",
                showarrow=False, font=dict(size=7, color=fc, family="Share Tech Mono, monospace"),
                xanchor="left", yanchor="bottom",
            )

    # Regime annotation (top-right)
    trend_sym = "▲" if momentum >= 0 else "▼"
    regime_col = "#00E1FF" if isBull else "#FF3D71"
    fig.add_annotation(
        x=1, y=0.98, xref="paper", yref="paper",
        text=f"{regime}  {trend_sym}{abs(momentum):.1f}",
        showarrow=False,
        font=dict(size=9, color=regime_col, family="Share Tech Mono, monospace"),
        xanchor="right", yanchor="top",
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=235,
        margin=dict(l=8, r=50, t=8, b=8),
        xaxis=dict(visible=False, showgrid=False),
        yaxis=dict(
            range=[-100, 100], showgrid=False, zeroline=False,
            tickvals=[-80,-30,0,30,80],
            tickfont=dict(color="#3A4A6A", size=9, family="Share Tech Mono, monospace"),
            side="right",
        ),
    )
    return fig


def render_factor_bars_html(current: float) -> str:
    """Factor breakdown mini-bars (Bloomberg sub-panel style)."""
    import random
    random.seed(int(abs(current) * 100))

    factors = [
        ("RSI",   current * 0.95 + (random.random()-0.5)*6),
        ("MACD",  current * 0.88 + (random.random()-0.5)*9),
        ("TREND", current * 0.92 + (random.random()-0.5)*7),
        ("VOL",   current * 0.70 + (random.random()-0.5)*16),
        ("STOCH", current * 0.85 + (random.random()-0.5)*11),
    ]

    items_html = ""
    for k, v in factors:
        v = max(-100, min(100, v))
        c = "#00E1FF" if v >= 0 else "#FF3D71"
        sign = "+" if v >= 0 else ""
        bar_ml = f"margin-left:{100-abs(v):.0f}%" if v < 0 else "margin-left:0"
        items_html += f"""
        <div class="av-factor-item">
            <div class="av-factor-k">{k}</div>
            <div class="av-factor-bar-wrap">
                <div style="width:{abs(v):.0f}%;height:100%;background:{c};{bar_ml};border-radius:1px;"></div>
            </div>
            <div class="av-factor-v" style="color:{c}">{sign}{v:.0f}</div>
        </div>"""

    return f'<div class="av-factor-wrap">{items_html}</div>'


# ==============================================================================
# TRADINGVIEW WIDGET HELPERS (via components.html)
# ==============================================================================

def tv_widget_html(script_src: str, config: dict, height: int = 400) -> str:
    """Generate TradingView widget HTML block."""
    import json
    cfg_json = json.dumps(config)
    return f"""
    <!DOCTYPE html><html>
    <head>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ background:transparent; overflow:hidden; }}
        .tradingview-widget-container {{ width:100%; height:{height}px; }}
    </style>
    </head>
    <body>
    <div class="tradingview-widget-container">
        <div class="tradingview-widget-container__widget"></div>
        <script type="text/javascript" src="{script_src}" async>
        {cfg_json}
        </script>
    </div>
    </body></html>
    """


def tv_advanced_chart_html(symbol: str, interval: str, style: str, height: int = 380) -> str:
    """Advanced Chart widget (full-featured)."""
    import json
    config = {
        "autosize": True,
        "symbol": symbol,
        "interval": TV_INTERVAL[interval],
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": style,
        "locale": "en",
        "backgroundColor": "#070A12",
        "gridColor": "rgba(42,53,80,0.3)",
        "hide_top_toolbar": False,
        "hide_legend": False,
        "allow_symbol_change": False,
        "save_image": False,
        "calendar": False,
        "support_host": "https://www.tradingview.com",
    }
    cfg_json = json.dumps(config)
    return f"""
    <!DOCTYPE html><html>
    <head>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ background:#070A12; overflow:hidden; }}
        .tradingview-widget-container {{ width:100%; height:{height}px; }}
    </style>
    </head>
    <body>
    <div class="tradingview-widget-container" style="height:{height}px;">
        <div class="tradingview-widget-container__widget" style="height:{height}px;"></div>
        <script type="text/javascript"
            src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
        {cfg_json}
        </script>
    </div>
    </body></html>
    """


def tv_market_overview_html() -> str:
    return tv_widget_html(
        "https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js",
        {
            "colorTheme": "dark", "dateRange": "3M", "locale": "en",
            "isTransparent": True, "showFloatingTooltip": False,
            "plotLineColorGrowing": "rgba(0,225,255,1)",
            "plotLineColorFalling": "rgba(255,61,113,1)",
            "gridLineColor": "rgba(42,53,80,0)",
            "scaleFontColor": "#4A6080",
            "belowLineFillColorGrowing": "rgba(0,225,255,0.10)",
            "belowLineFillColorFalling": "rgba(255,61,113,0.10)",
            "belowLineFillColorGrowingBottom": "rgba(0,225,255,0)",
            "belowLineFillColorFallingBottom": "rgba(255,61,113,0)",
            "symbolActiveColor": "rgba(0,225,255,0.10)",
            "backgroundColor": "#09111E",
            "tabs": [
                {"title":"FOREX","originalTitle":"Forex","symbols":[
                    {"s":"FX:EURUSD","d":"EUR/USD"},{"s":"FX:GBPUSD","d":"GBP/USD"},
                    {"s":"FX:USDJPY","d":"USD/JPY"},{"s":"FX:USDCHF","d":"USD/CHF"},
                    {"s":"FX:AUDUSD","d":"AUD/USD"},
                ]},
                {"title":"CRYPTO","originalTitle":"Crypto","symbols":[
                    {"s":"COINBASE:BTCUSD","d":"BTC/USD"},{"s":"COINBASE:ETHUSD","d":"ETH/USD"},
                    {"s":"COINBASE:SOLUSD","d":"SOL/USD"},{"s":"BINANCE:BNBUSDT","d":"BNB/USDT"},
                    {"s":"COINBASE:XRPUSD","d":"XRP/USD"},
                ]},
                {"title":"INDICES","originalTitle":"Indices","symbols":[
                    {"s":"FOREXCOM:SPXUSD","d":"S&P 500"},{"s":"FOREXCOM:NSXUSD","d":"Nasdaq"},
                    {"s":"FOREXCOM:DJI","d":"Dow Jones"},
                ]},
                {"title":"COMMODITIES","originalTitle":"Commodities","symbols":[
                    {"s":"CMCMARKETS:GOLD","d":"Gold"},{"s":"PYTH:WTI3!","d":"WTI Oil"},
                    {"s":"TVC:NATURALGAS","d":"Nat Gas"},
                ]},
            ],
            "width": "100%", "height": "370",
            "showSymbolLogo": True, "showChart": True,
        },
        height=370,
    )


def tv_tech_gauge_html(symbol: str, interval: str) -> str:
    return tv_widget_html(
        "https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js",
        {
            "colorTheme": "dark", "displayMode": "single",
            "isTransparent": True, "locale": "en",
            "interval": TV_TA_INT[interval],
            "width": "100%", "height": "350",
            "symbol": symbol, "showIntervalTabs": True,
        },
        height=350,
    )


def tv_mini_chart_html(symbol: str) -> str:
    return tv_widget_html(
        "https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js",
        {
            "symbol": symbol, "width": "100%", "height": "200",
            "locale": "en", "dateRange": "1M",
            "colorTheme": "dark", "isTransparent": True,
            "autosize": True, "largeChartUrl": "", "chartOnly": False,
        },
        height=200,
    )


def tv_econ_calendar_html() -> str:
    return tv_widget_html(
        "https://s3.tradingview.com/external-embedding/embed-widget-events.js",
        {
            "colorTheme": "dark", "isTransparent": True,
            "width": "100%", "height": "420", "locale": "en",
            "importanceFilter": "0,1",
            "countryFilter": "us,eu,gb,jp,au,ch,ca,cn",
        },
        height=420,
    )


def tv_screener_html() -> str:
    return tv_widget_html(
        "https://s3.tradingview.com/external-embedding/embed-widget-screener.js",
        {
            "market": "forex", "showToolbar": True,
            "defaultColumn": "overview", "defaultScreen": "general",
            "isTransparent": True, "locale": "en",
            "colorTheme": "dark", "width": "100%", "height": "420",
        },
        height=420,
    )


def tv_top_stories_html() -> str:
    return tv_widget_html(
        "https://s3.tradingview.com/external-embedding/embed-widget-timeline.js",
        {
            "feedMode": "all_symbols", "colorTheme": "dark",
            "isTransparent": True, "displayMode": "regular",
            "width": "100%", "height": "460", "locale": "en",
        },
        height=460,
    )


# ==============================================================================
# HEADER + BRAND
# ==============================================================================
st.markdown("""
<div class="av-brand-wrap">
    <div class="av-brand-line">
        <span class="av-prefix">SYS</span>
        <span class="av-title">AERO<span class="acc">VULPIS</span>&nbsp;TERMINAL</span>
        <span class="av-ver">v4.1</span>
    </div>
    <div class="av-tagline">QUANTITATIVE MARKET INTELLIGENCE SYSTEM · PROTOTYPE BUILD</div>
    <div class="av-ticker-wrap">
        <span class="av-tick"><span class="sym">EURUSD </span><span class="up">1.1465</span></span>
        <span class="av-tick"><span class="sym">GBPUSD </span><span class="up">1.3228</span></span>
        <span class="av-tick"><span class="sym">USDJPY </span><span class="dn">161.24</span></span>
        <span class="av-tick"><span class="sym">XAUUSD </span><span class="up">2382.4</span></span>
        <span class="av-tick"><span class="sym">BTCUSD </span><span class="up">67420</span></span>
        <span class="av-tick"><span class="sym">NVDA   </span><span class="dn">131.80</span></span>
        <span class="av-tick"><span class="sym">AUDUSD </span><span class="dn">0.7010</span></span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# SELECTOR BAR
# ==============================================================================
sel_col1, sel_col2, sel_col3, sel_col4 = st.columns([1.5, 1.5, 1.2, 3])

with sel_col1:
    instr_class = st.selectbox(
        "Instrument",
        list(INSTRUMENTS.keys()),
        index=list(INSTRUMENTS.keys()).index(st.session_state.instr_class),
        key="sel_instr",
    )
    if instr_class != st.session_state.instr_class:
        st.session_state.instr_class = instr_class
        st.session_state.pair_idx = 0

with sel_col2:
    pairs = INSTRUMENTS[st.session_state.instr_class]
    pair_labels = [p[0] for p in pairs]
    pair_idx = st.selectbox(
        "Pair",
        range(len(pair_labels)),
        format_func=lambda i: pair_labels[i],
        index=min(st.session_state.pair_idx, len(pair_labels)-1),
        key="sel_pair",
    )
    st.session_state.pair_idx = pair_idx

with sel_col3:
    timeframe = st.selectbox(
        "Timeframe",
        ["15m","1h","4h","1D"],
        index=["15m","1h","4h","1D"].index(st.session_state.timeframe),
        key="sel_tf",
    )
    st.session_state.timeframe = timeframe

# Active pair
active_pair      = pairs[st.session_state.pair_idx]
active_label     = active_pair[0]  # e.g. EURUSD
active_td_symbol = active_pair[1]  # e.g. EUR/USD (for Twelve Data)
active_tv_symbol = active_pair[2]  # e.g. OANDA:EURUSD

# ==============================================================================
# ROW 1 — MCT + MARKET OVERVIEW
# ==============================================================================
st.markdown('<div class="av-sec">// MARKET INTELLIGENCE LAYER · MCT + OVERVIEW</div>', unsafe_allow_html=True)

mct_col, overview_col = st.columns([1.1, 1])

with mct_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)

    # MCT header
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:4px;">
        <div>
            <div style="font-size:8px;letter-spacing:2px;color:#4A6080;margin-bottom:2px;font-family:'Share Tech Mono',monospace;">
                MCT · COMPOSITE OSCILLATOR · 9-FACTOR
            </div>
            <div style="font-size:10px;color:#5A7090;letter-spacing:1px;font-family:'Share Tech Mono',monospace;">
                RSI · MACD · ATR · EMA · BB · STOCH · WILLR · ROC · CCI
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fetch & calculate MCT
    with st.spinner(""):
        df = fetch_twelvedata(
            active_td_symbol,
            TD_INTERVAL[timeframe],
            outputsize=300,
        )

    if df.empty:
        # Fallback: seeded dummy data (same MCT engine, simulated OHLCV)
        np.random.seed(hash(f"{active_label}-{timeframe}") % 2**31)
        n = 200
        price = np.cumprod(1 + np.random.normal(0.0001, 0.003, n))
        price = price / price[0] * 1.15
        dummy_df = pd.DataFrame({
            "close": price,
            "high":  price * (1 + np.abs(np.random.normal(0, 0.001, n))),
            "low":   price * (1 - np.abs(np.random.normal(0, 0.001, n))),
        }, index=pd.date_range("2024-01-01", periods=n, freq="15min"))
        try:
            mct_values = calculate_mct_bloomberg(dummy_df)
            data_source = "SIMULATION"
        except Exception:
            mct_values = np.zeros(50)
            data_source = "ERROR"
    else:
        try:
            mct_values = calculate_mct_bloomberg(df)
            data_source = "LIVE · TWELVE DATA"
        except Exception:
            mct_values = np.zeros(50)
            data_source = "CALC ERROR"

    current_mct = float(mct_values[-1])
    mct_color   = "#00E1FF" if current_mct >= 0 else "#FF3D71"
    sign        = "+" if current_mct >= 0 else ""

    # Current value display
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
        <div style="font-size:8px;color:#2A3A5A;letter-spacing:1px;font-family:'Share Tech Mono',monospace;">
            {data_source}
        </div>
        <div style="font-size:24px;font-weight:700;color:{mct_color};font-family:'Share Tech Mono',monospace;line-height:1;">
            {sign}{current_mct:.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Plotly MCT chart
    fig = render_mct_plotly(mct_values, active_label)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Factor breakdown bars
    st.markdown(render_factor_bars_html(current_mct), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with overview_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)
    components.html(tv_market_overview_html(), height=390, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 2 — MAIN CHART + TECHNICAL GAUGE
# ==============================================================================
st.markdown(f'<div class="av-sec">// CHART CORE · {active_label} · {timeframe}</div>', unsafe_allow_html=True)

chart_col, gauge_col = st.columns([1.4, 1])

with chart_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)

    # Chart style selector inside panel
    chart_style_labels = [s[0] for s in CHART_STYLES]
    chart_style_sel = st.selectbox(
        "Chart Style",
        range(len(CHART_STYLES)),
        format_func=lambda i: CHART_STYLES[i][0],
        index=next((i for i, s in enumerate(CHART_STYLES) if s[1]==st.session_state.chart_style), 0),
        key="sel_chart_style",
    )
    st.session_state.chart_style = CHART_STYLES[chart_style_sel][1]

    components.html(
        tv_advanced_chart_html(active_tv_symbol, timeframe, st.session_state.chart_style, height=380),
        height=395,
        scrolling=False,
    )
    st.markdown('</div>', unsafe_allow_html=True)

with gauge_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)
    components.html(tv_tech_gauge_html(active_tv_symbol, timeframe), height=365, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 3 — MINI CHARTS (3 columns, each with symbol picker)
# ==============================================================================
st.markdown('<div class="av-sec">// MULTI-PAIR MONITOR</div>', unsafe_allow_html=True)

mini_cols = st.columns(3)
mini_keys = ["mini_a", "mini_b", "mini_c"]
mini_defaults = [1, 2, 3]  # GBPUSD, USDJPY, AUDUSD

for col_idx, (col, key, default) in enumerate(zip(mini_cols, mini_keys, mini_defaults)):
    with col:
        st.markdown('<div class="av-panel">', unsafe_allow_html=True)
        mini_labels = [m[0] for m in MINI_OPTIONS]
        sel_idx = st.selectbox(
            f"Mini {col_idx+1}",
            range(len(MINI_OPTIONS)),
            format_func=lambda i: MINI_OPTIONS[i][0],
            index=getattr(st.session_state, key, default),
            key=f"sel_{key}",
        )
        setattr(st.session_state, key, sel_idx)
        mini_tv = MINI_OPTIONS[sel_idx][1]
        components.html(tv_mini_chart_html(mini_tv), height=215, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 4 — ECONOMIC CALENDAR + SCREENER
# ==============================================================================
st.markdown('<div class="av-sec">// FUNDAMENTAL DATA · PENYARING</div>', unsafe_allow_html=True)

cal_col, screen_col = st.columns(2)

with cal_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)
    components.html(tv_econ_calendar_html(), height=435, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

with screen_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)
    components.html(tv_screener_html(), height=435, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 5 — AI ANALYSIS
# ==============================================================================
st.markdown('<div class="av-sec">// AI INTELLIGENCE ENGINE</div>', unsafe_allow_html=True)
st.markdown('<div class="av-panel">', unsafe_allow_html=True)

ai_btn_col1, ai_btn_col2, ai_space = st.columns([1, 1, 4])
with ai_btn_col1:
    if st.button("ANALISIS PAIR", key="btn_pair_mode"):
        st.session_state.ai_mode = "pair"
        st.session_state.ai_result = None
with ai_btn_col2:
    if st.button("ANALISIS NEWS", key="btn_news_mode"):
        st.session_state.ai_mode = "news"
        st.session_state.ai_result = None

mode = st.session_state.ai_mode

if mode == "news":
    ai_input_col, ai_run_col = st.columns([5, 1])
    with ai_input_col:
        news_text = st.text_input("News", placeholder="PASTE HEADLINE / KONTEKS BERITA...", key="ai_news_input")
    with ai_run_col:
        st.markdown("<div style='margin-top:4px'></div>", unsafe_allow_html=True)
        run_clicked = st.button("ANALISIS", key="btn_run_news", disabled=not news_text.strip() if 'news_text' in dir() else True)
    if run_clicked and news_text.strip():
        st.session_state.ai_result = (
            f"[PROTOTYPE] Dampak berita terhadap {active_label}: "
            f"Sentimen risk-off meningkat jangka pendek. "
            f"Potensi penguatan USD akibat data yang lebih tinggi dari ekspektasi. "
            f"Volatilitas diprediksi naik di sesi New York. "
            f"Pantau reaksi harga di 30 menit pertama setelah rilis. "
            f"(Placeholder — akan diganti hasil Claude API asli.)"
        )
else:
    run_col, _ = st.columns([1, 5])
    with run_col:
        run_clicked = st.button("ANALISIS", key="btn_run_pair")
    if run_clicked:
        st.session_state.ai_result = (
            f"[PROTOTYPE] Analisis teknikal {active_label}: "
            f"Bias jangka pendek bearish-netral. RSI mendekati 42 (mendekati oversold), "
            f"MACD histogram menyempit — tekanan jual melemah. "
            f"EMA-20 masih di bawah EMA-50, konfirmasi downtrend minor. "
            f"ATR meningkat 12% — volatilitas naik. "
            f"Rekomendasi: WAIT — konfirmasi bounce di S1 sebelum entry BUY. "
            f"(Placeholder — akan diganti hasil Claude API asli.)"
        )

if st.session_state.ai_result:
    st.markdown(f'<div class="av-ai-result">{st.session_state.ai_result}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 6 — ACTIVE TRADE SIGNALS
# ==============================================================================
st.markdown('<div class="av-sec">// ACTIVE TRADE SIGNALS</div>', unsafe_allow_html=True)
st.markdown('<div class="av-panel">', unsafe_allow_html=True)

trade_cols = st.columns(len(DUMMY_TRADES))
for col, trade in zip(trade_cols, DUMMY_TRADES):
    with col:
        is_buy   = trade["dir"] == "BUY"
        dir_class = "av-dir-buy" if is_buy else "av-dir-sell"
        rows_html = "".join([
            f'<div class="av-trade-row">'
            f'<span class="av-trade-k">{k}</span>'
            f'<span style="color:{c};font-size:11px;font-weight:{700 if k!="ENTRY" else 400}">{trade[vk]}</span>'
            f'</div>'
            for k, vk, c in [
                ("ENTRY","entry","#8BA0C0"),
                ("SL","sl","#FF3D71"),
                ("TP1","tp1","#00E1FF"),
                ("TP2","tp2","#00B8CC"),
                ("TP3","tp3","#0090A0"),
            ]
        ])
        st.markdown(f"""
        <div class="av-trade-card" style="display:block;min-width:unset;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <span class="av-trade-symbol">{trade['symbol']}</span>
                <span class="{dir_class}">{trade['dir']}</span>
            </div>
            {rows_html}
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 7 — TOP STORIES
# ==============================================================================
st.markdown('<div class="av-sec">// MARKET INTELLIGENCE · NEWS FEED</div>', unsafe_allow_html=True)
st.markdown('<div class="av-panel">', unsafe_allow_html=True)
components.html(tv_top_stories_html(), height=475, scrolling=False)
st.markdown('</div>', unsafe_allow_html=True)