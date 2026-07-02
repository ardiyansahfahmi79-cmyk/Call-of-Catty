# ==============================================================================
# aerovulpis_terminal.py — AEROVULPIS TERMINAL v4.1
# Quantitative Market Intelligence System · Streamlit Edition
# ==============================================================================

import streamlit as st
import numpy as np
import pandas as pd
import pandas_ta as ta
import requests
import plotly.graph_objects as go
from scipy.signal import savgol_filter
import streamlit.components.v1 as components
import json
from datetime import datetime, timezone
from urllib.parse import quote as _url_quote

st.set_page_config(
    page_title="AEROVULPIS TERMINAL",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# GLOBAL CSS
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background:#070A12 !important;
    font-family:'Share Tech Mono','Courier New',monospace !important;
    color:#C8D8F0 !important;
}
[data-testid="stSidebar"]        { display:none !important; }
[data-testid="collapsedControl"] { display:none !important; }
[data-testid="stDecoration"]     { display:none !important; }
[data-testid="stHeader"]         { background:transparent !important; height:0 !important; }
footer { display:none !important; }
#MainMenu { display:none !important; }

[data-testid="stMain"] {
    background:#070A12 !important;
    background-image:
        radial-gradient(ellipse 60% 35% at 10% 0%,rgba(0,225,255,0.05),transparent),
        radial-gradient(ellipse 50% 30% at 90% 5%,rgba(168,85,247,0.05),transparent) !important;
}

div.block-container { padding:0 1rem 1.5rem !important; max-width:100% !important; }
[data-testid="stVerticalBlock"] > div { gap:0 !important; }
[data-testid="column"] { padding:0 4px !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { padding:0 !important; }
.stMarkdown { margin:0 !important; padding:0 !important; }
div[data-testid="stHorizontalBlock"] { gap:8px !important; }

/* ── BRAND compact — rapat ke ticker ── */
.av-brand-wrap { padding:4px 0 0; margin-bottom:0; }
.av-brand-line { display:flex; align-items:baseline; gap:8px; }
.av-prefix {
    font-size:7px; letter-spacing:3px; color:#1A3A5A;
    border:1px solid #1A3A5A; padding:1px 5px; border-radius:2px;
}
.av-title {
    font-size:16px; letter-spacing:3px; color:#E8F1FF;
    font-weight:700; font-family:'Share Tech Mono',monospace; line-height:1.2;
}
.av-title .acc { color:#00E1FF; }
.av-ver { font-size:7px; letter-spacing:2px; color:#2A4060; }
.av-tagline { font-size:6px; letter-spacing:2px; color:#1A3A5A; margin-top:1px; margin-bottom:0; }

/* Zero gap antara semua elemen atas */
div.block-container > div > div > div { margin-bottom:0 !important; }
iframe { display:block; margin:0 !important; }

/* ── SECTION LABEL ── */
.av-sec {
    font-size:7px; letter-spacing:2px; color:#1A3060;
    padding:4px 0 2px; font-family:'Share Tech Mono',monospace;
    margin:0;
}

/* ── PANEL ── */
.av-panel {
    background:#09111E; border:1px solid #111827; border-radius:8px;
    padding:12px; position:relative; overflow:hidden; margin-bottom:8px;
}
.av-panel::before {
    content:""; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,225,255,0.18),transparent);
}

/* ── SELECTBOX → neon cyan dropdown, tidak bisa diketik (mobile-proof) ── */
[data-testid="stSelectbox"] label { display:none !important; }
[data-testid="stSelectbox"] { margin-bottom:0 !important; }
[data-testid="stSelectbox"] > div > div {
    background:#09111E !important;
    border:1px solid rgba(0,225,255,0.3) !important;
    border-radius:5px !important;
    color:#00E1FF !important;
    font-family:'Share Tech Mono',monospace !important;
    font-size:11px !important;
    letter-spacing:1px !important;
    min-height:36px !important;
    box-shadow:0 0 8px rgba(0,225,255,0.12) !important;
    cursor:pointer !important;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color:#00E1FF !important;
    box-shadow:0 0 14px rgba(0,225,255,0.28) !important;
}
/* Arrow */
[data-testid="stSelectbox"] svg { fill:#00E1FF !important; }
/* Input field di dalam selectbox — benar-benar diblokir dari keyboard mobile */
[data-baseweb="select"] {
    pointer-events:auto !important;
}
[data-baseweb="select"] input {
    pointer-events:none !important;
    caret-color:transparent !important;
    cursor:pointer !important;
    user-select:none !important;
    -webkit-user-select:none !important;
    font-size:11px !important;
}
/* Paksa browser mobile tidak membuka keyboard sama sekali */
[data-baseweb="select"] input[type="text"],
[data-baseweb="select"] input:not([type]) {
    -webkit-touch-callout:none !important;
}
/* Value text */
[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
[data-baseweb="select"] span {
    color:#00E1FF !important;
    font-family:'Share Tech Mono',monospace !important;
    letter-spacing:1px !important;
    pointer-events:none !important;
}
/* Dropdown menu */
[data-baseweb="popover"] [data-baseweb="menu"] {
    background:#09111E !important;
    border:1px solid rgba(0,225,255,0.25) !important;
    border-radius:6px !important;
}
[data-baseweb="option"] {
    background:#09111E !important;
    color:#8BA0C0 !important;
    font-family:'Share Tech Mono',monospace !important;
    font-size:11px !important;
    border-bottom:1px solid #0E1422 !important;
    cursor:pointer !important;
}
[data-baseweb="option"]:hover,
[data-baseweb="option"][aria-selected="true"] {
    background:rgba(0,225,255,0.10) !important;
    color:#00E1FF !important;
}

/* ── SELECTOR LABEL ── */
.av-sel-label {
    font-size:8px; letter-spacing:1.5px; color:#2A4060;
    margin-bottom:3px; font-family:'Share Tech Mono',monospace;
}

/* ── BUTTONS (AI, trade, dll) ── */
[data-testid="stButton"] > button {
    background:linear-gradient(135deg,rgba(0,225,255,0.15),rgba(168,85,247,0.15)) !important;
    color:#00E1FF !important; font-weight:700 !important;
    font-family:'Share Tech Mono',monospace !important;
    font-size:10px !important; letter-spacing:0.5px !important;
    border:1px solid rgba(0,225,255,0.4) !important;
    border-radius:4px !important;
    padding:6px 8px !important;
    transition:all 0.15s ease !important;
    white-space:nowrap !important;
    overflow:hidden !important;
    text-overflow:ellipsis !important;
}
[data-testid="stButton"] > button:hover {
    background:rgba(0,225,255,0.22) !important;
    border-color:#00E1FF !important;
    box-shadow:0 0 10px rgba(0,225,255,0.3) !important;
}
[data-testid="stButton"] > button p {
    white-space:nowrap !important;
    font-size:10px !important;
    letter-spacing:0.5px !important;
}

/* ── TEXT INPUT ── */
[data-testid="stTextInput"] label { display:none !important; }
[data-testid="stTextInput"] input {
    background:#07101C !important; border:1px solid #1A2540 !important;
    border-radius:5px !important; color:#C8D8F0 !important;
    font-family:'Share Tech Mono',monospace !important; font-size:11px !important;
}
[data-testid="stTextInput"] input::placeholder { color:#2A3A54 !important; }

/* ── AI RESULT ── */
.av-ai-result {
    background:#07101C; border:1px solid #1A2540;
    border-left:2px solid #00E1FF; padding:12px 14px;
    border-radius:5px; font-size:11px; line-height:1.7; color:#8BA0C0;
    letter-spacing:0.3px; font-family:'Share Tech Mono',monospace; margin-top:8px;
}

/* ── TRADE CARD ── */
.av-trade-card {
    background:#09111E; border:1px solid #111827;
    border-radius:8px; padding:12px; position:relative; overflow:hidden;
}
.av-trade-card::before {
    content:""; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,225,255,0.2),transparent);
}
.av-trade-symbol { font-size:13px; font-weight:700; color:#E8F1FF; letter-spacing:1px; }
.av-dir-buy  { font-size:9px; padding:3px 8px; border-radius:3px; font-weight:700;
    letter-spacing:1.5px; background:rgba(0,225,255,0.12); color:#00E1FF;
    border:1px solid rgba(0,225,255,0.35); }
.av-dir-sell { font-size:9px; padding:3px 8px; border-radius:3px; font-weight:700;
    letter-spacing:1.5px; background:rgba(255,61,113,0.12); color:#FF3D71;
    border:1px solid rgba(255,61,113,0.35); }
.av-trade-row { display:flex; justify-content:space-between; padding:3px 0;
    border-bottom:1px solid #0E1422; font-size:11px; }
.av-trade-k { color:#3A4A6A; letter-spacing:1px; font-size:9px; }

/* ── MCT FACTOR BARS ── */
.av-factor-wrap { display:flex; gap:4px; margin-top:6px; }
.av-factor-item { flex:1; background:#0A0E18; border:1px solid #1A2238; border-radius:4px; padding:4px 6px; }
.av-factor-k { font-size:7.5px; color:#4A6080; letter-spacing:1px; margin-bottom:2px; }
.av-factor-bar-wrap { height:2px; background:#0E1422; border-radius:1px; }
.av-factor-v { font-size:8px; margin-top:2px; text-align:right; }

/* ── PLOTLY modebar hide ── */
.js-plotly-plot .plotly .modebar { display:none !important; }

/* ── REPORT TERMINAL STYLE ── */
.av-report-wrap {
    background:#05080F; border:1px solid rgba(0,225,255,0.25);
    border-radius:6px; padding:0; margin-top:10px; overflow:hidden;
    box-shadow:0 0 25px rgba(0,225,255,0.06), inset 0 0 40px rgba(0,225,255,0.02);
}
.av-report-header {
    background:linear-gradient(90deg,rgba(0,225,255,0.08),rgba(168,85,247,0.05));
    border-bottom:1px solid rgba(0,225,255,0.25); padding:10px 14px;
    display:flex; justify-content:space-between; align-items:center;
}
.av-report-title {
    font-size:10px; letter-spacing:3px; color:#00E1FF; font-weight:700;
    font-family:'Share Tech Mono',monospace; text-shadow:0 0 10px rgba(0,225,255,0.5);
}
.av-report-badge {
    font-size:7px; letter-spacing:1.5px; color:#4A6080;
    border:1px solid #1A3A5A; padding:2px 7px; border-radius:3px;
}
.av-report-body {
    padding:14px; font-family:'Share Tech Mono',monospace;
    font-size:10.5px; line-height:1.85; color:#9AB0CC;
}
.av-report-section-title {
    font-size:9px; letter-spacing:2px; color:#00E1FF; font-weight:700;
    margin:14px 0 8px; padding-bottom:4px; border-bottom:1px solid rgba(0,225,255,0.15);
}
.av-report-section-title:first-child { margin-top:0; }
.av-report-row {
    display:flex; justify-content:space-between; padding:2px 0;
    border-bottom:1px dotted rgba(42,53,80,0.5);
}
.av-report-k { color:#3A5070; letter-spacing:0.5px; font-size:9.5px; }
.av-report-v { color:#C8D8F0; font-weight:700; font-size:10px; }
.av-report-v.buy { color:#00E1FF; }
.av-report-v.sell { color:#FF3D71; }
.av-report-v.neutral { color:#A855F7; }
.av-report-narrative {
    color:#8BA0C0; font-size:10px; line-height:1.9; margin-top:4px;
    padding:10px 12px; background:rgba(0,225,255,0.03);
    border-left:2px solid rgba(0,225,255,0.3); border-radius:3px;
}
.av-score-big {
    font-size:26px; font-weight:700; font-family:'Share Tech Mono',monospace;
    text-shadow:0 0 14px currentColor;
}
.av-matrix-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:4px 0; border-bottom:1px solid #0E1422;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CONSTANTS
# ==============================================================================
INSTRUMENTS = {
    "FOREX": [
        ("EURUSD","EUR/USD","OANDA:EURUSD"),
        ("GBPUSD","GBP/USD","OANDA:GBPUSD"),
        ("USDJPY","USD/JPY","OANDA:USDJPY"),
        ("AUDUSD","AUD/USD","OANDA:AUDUSD"),
        ("USDCHF","USD/CHF","OANDA:USDCHF"),
    ],
    "COMMODITIES": [
        ("XAUUSD","XAU/USD","OANDA:XAUUSD"),
        ("XAGUSD","XAG/USD","OANDA:XAGUSD"),
        ("WTIUSD","WTI/USD","TVC:USOIL"),
        ("BRENT", "BRENT",  "TVC:UKOIL"),
        ("NATGAS","NATGAS", "TVC:NATURALGAS"),
    ],
    "US STOCKS": [
        ("AAPL","AAPL","NASDAQ:AAPL"),
        ("NVDA","NVDA","NASDAQ:NVDA"),
        ("TSLA","TSLA","NASDAQ:TSLA"),
        ("MSFT","MSFT","NASDAQ:MSFT"),
        ("AMZN","AMZN","NASDAQ:AMZN"),
    ],
    "CRYPTO": [
        ("BTCUSD","BTC/USD","COINBASE:BTCUSD"),
        ("ETHUSD","ETH/USD","COINBASE:ETHUSD"),
        ("SOLUSD","SOL/USD","COINBASE:SOLUSD"),
        ("BNBUSD","BNB/USDT","BINANCE:BNBUSDT"),
        ("XRPUSD","XRP/USD","COINBASE:XRPUSD"),
    ],
}

TIMEFRAMES  = ["15m","30m","1h","4h","1D"]
TV_INTERVAL = {"15m":"15","30m":"30","1h":"60","4h":"240","1D":"D"}
TV_TA_INT   = {"15m":"15m","30m":"30m","1h":"1h","4h":"4h","1D":"1D"}
TD_INTERVAL = {"15m":"15min","30m":"30min","1h":"1h","4h":"4h","1D":"1day"}

CHART_STYLES = [("LINE","3"),("CANDLES","1"),("HEIKIN","8"),("AREA","9"),("BARS","0")]

# Mini chart options — dipisah per instrumen class
MINI_OPTIONS = {
    "FOREX": [
        ("EURUSD","OANDA:EURUSD"),
        ("GBPUSD","OANDA:GBPUSD"),
        ("USDJPY","OANDA:USDJPY"),
        ("AUDUSD","OANDA:AUDUSD"),
        ("USDCHF","OANDA:USDCHF"),
        ("NZDUSD","OANDA:NZDUSD"),
        ("USDCAD","OANDA:USDCAD"),
        ("EURGBP","OANDA:EURGBP"),
    ],
    "COMMODITIES": [
        ("XAUUSD","OANDA:XAUUSD"),
        ("XAGUSD","OANDA:XAGUSD"),
        ("OIL",   "CAPITALCOM:OIL_CRUDE"),
        ("DXY",   "CAPITALCOM:DXY"),
        ("US10Y", "TVC:US10Y"),
        ("NATGAS","TVC:NATURALGAS"),
    ],
    "US STOCKS": [
        ("AAPL",  "NASDAQ:AAPL"),
        ("NVDA",  "NASDAQ:NVDA"),
        ("TSLA",  "NASDAQ:TSLA"),
        ("MSFT",  "NASDAQ:MSFT"),
        ("AMZN",  "NASDAQ:AMZN"),
        ("GOOGL", "NASDAQ:GOOGL"),
        ("META",  "NASDAQ:META"),
        ("SPX",   "FOREXCOM:SPXUSD"),
    ],
    "CRYPTO": [
        ("BTCUSD","COINBASE:BTCUSD"),
        ("ETHUSD","COINBASE:ETHUSD"),
        ("SOLUSD","COINBASE:SOLUSD"),
        ("BNBUSD","BINANCE:BNBUSDT"),
        ("XRPUSD","COINBASE:XRPUSD"),
        ("ADAUSD","COINBASE:ADAUSD"),
        ("DOTUSD","COINBASE:DOTUSD"),
        ("AVAXUSD","COINBASE:AVAXUSD"),
    ],
}

DUMMY_TRADES = [
    {"symbol":"EURUSD","dir":"BUY", "entry":"1.14620","sl":"1.14280","tp1":"1.14950","tp2":"1.15300","tp3":"1.15700"},
    {"symbol":"GBPUSD","dir":"SELL","entry":"1.32310","sl":"1.32650","tp1":"1.31980","tp2":"1.31600","tp3":"1.31150"},
    {"symbol":"XAUUSD","dir":"BUY", "entry":"2382.40","sl":"2371.00","tp1":"2394.00","tp2":"2406.50","tp3":"2420.00"},
    {"symbol":"BTCUSD","dir":"BUY", "entry":"67420.0","sl":"65800.0","tp1":"69000.0","tp2":"71500.0","tp3":"74200.0"},
]

# ==============================================================================
# SESSION STATE INIT
# ==============================================================================
_DEFAULTS = {
    "instr_class": "FOREX",
    "pair_label":  "EURUSD",
    "timeframe":   "15m",
    "chart_style": "3",
    "indicator_mode": "NO MODE",
    "mini_a":      "GBPUSD",
    "mini_b":      "USDJPY",
    "mini_c":      "AUDUSD",
    "ai_mode":     "pair",
    "ai_result":   None,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ==============================================================================
# MCT ENGINE — Real data from Twelve Data, RSI+MACD+Volume, Bloomberg-grade
# ==============================================================================
@st.cache_data(ttl=60, show_spinner=False)
def fetch_twelvedata(symbol: str, interval: str, outputsize: int = 300) -> pd.DataFrame:
    """Fetch OHLCV from Twelve Data. Keyed by symbol+interval so each TF gets fresh data."""
    try:
        api_key = st.secrets["TWELVE_DATA_API_KEY"]
    except Exception:
        return pd.DataFrame()
    url = (
        f"https://api.twelvedata.com/time_series"
        f"?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={api_key}"
    )
    try:
        r = requests.get(url, timeout=10).json()
        if r.get("status") == "error" or "values" not in r:
            return pd.DataFrame()
        df = pd.DataFrame(r["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        for c in ["open","high","low","close"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["volume"] = pd.to_numeric(df.get("volume", 0), errors="coerce").fillna(0)
        df = df.sort_values("datetime").reset_index(drop=True)
        df.set_index("datetime", inplace=True)
        return df
    except Exception:
        return pd.DataFrame()


def _make_dummy_df(seed_str: str, n: int = 300) -> pd.DataFrame:
    """Deterministic OHLCV — differs per pair+timeframe combination."""
    rng   = np.random.default_rng(abs(hash(seed_str)) % 2**32)
    price = np.cumprod(1 + rng.normal(0.0002, 0.004, n))
    price = price / price[0] * 1.15
    vol   = rng.uniform(300, 2500, n)
    freq_map = {"15m":"15min","30m":"30min","1h":"1h","4h":"4h","1D":"1D"}
    freq  = freq_map.get(seed_str.split("-")[-1], "15min")
    open_ = np.roll(price, 1)
    open_[0] = price[0]
    return pd.DataFrame({
        "open":   open_,
        "close":  price,
        "high":   price * (1 + np.abs(rng.normal(0, 0.0015, n))),
        "low":    price * (1 - np.abs(rng.normal(0, 0.0015, n))),
        "volume": vol,
    }, index=pd.date_range("2024-01-01", periods=n, freq=freq))



def calculate_mct(df: pd.DataFrame) -> dict:
    """
    Bloomberg-class MCT oscillator:
      RSI(14)  z-score  → weight 40%
      MACD histogram    → weight 40%
      Volume pressure   → weight 20%
    Composite scaled -100..+100 then Savitzky-Golay smoothed (w=25, p=3).
    Returns smoothed array + per-factor last values for Bloomberg sub-panel.
    """
    lookback = 63

    def z_norm(s: pd.Series) -> pd.Series:
        rm = s.rolling(lookback, min_periods=10).mean()
        rs = s.rolling(lookback, min_periods=10).std().replace(0, np.nan)
        return ((s - rm) / rs).clip(-3, 3) / 3.0

    close  = df["close"]
    volume = df.get("volume", pd.Series(np.ones(len(df)), index=df.index))

    # Factor 1 — RSI(14) centered
    rsi_raw   = ta.rsi(close, length=14).fillna(50) - 50.0
    z_rsi     = z_norm(rsi_raw)
    rsi_score = float(np.clip(z_rsi.iloc[-1] * 100, -100, 100))

    # Factor 2 — MACD Histogram(12,26,9)
    macd_df    = ta.macd(close, fast=12, slow=26, signal=9)
    macd_hist  = macd_df["MACDh_12_26_9"].fillna(0)
    z_macd     = z_norm(macd_hist)
    macd_score = float(np.clip(z_macd.iloc[-1] * 100, -100, 100))

    # Factor 3 — Volume pressure vs 20-bar MA
    vol_ma    = volume.rolling(20, min_periods=5).mean().replace(0, np.nan)
    vol_mom   = ((volume / vol_ma) - 1.0).fillna(0).clip(-2, 2)
    z_vol     = z_norm(vol_mom)
    vol_score = float(np.clip(z_vol.iloc[-1] * 100, -100, 100))

    # Composite
    comp = (0.40 * z_rsi) + (0.40 * z_macd) + (0.20 * z_vol)
    raw  = np.clip((comp * 100).fillna(0).to_numpy(), -100, 100)

    # Savitzky-Golay smoothing
    n  = len(raw)
    wl = min(25, n)
    if wl % 2 == 0: wl -= 1
    wl = max(wl, 5)
    smoothed = np.clip(savgol_filter(raw, window_length=wl, polyorder=3, mode="interp"), -100, 100)

    return {
        "values":     smoothed,
        "current":    float(smoothed[-1]),
        "rsi_score":  rsi_score,
        "macd_score": macd_score,
        "vol_score":  vol_score,
    }


def render_mct(result: dict) -> go.Figure:
    values   = result["values"]
    current  = result["current"]
    prev     = float(values[max(0, len(values)-6)])
    momentum = current - prev
    isBull   = current >= 0
    dot_c    = "#00E1FF" if isBull else "#FF3D71"
    x        = list(range(len(values)))
    y_up     = np.where(values >= 0, values, np.nan)
    y_dn     = np.where(values <= 0, values, np.nan)

    if   current >  60: regime = "STRONG BULL"
    elif current >  25: regime = "BULL"
    elif current < -60: regime = "STRONG BEAR"
    elif current < -25: regime = "BEAR"
    else:               regime = "NEUTRAL"

    fig = go.Figure()
    fig.add_hrect(y0=30,  y1=80,  fillcolor="rgba(0,225,255,0.04)",  line_width=0)
    fig.add_hrect(y0=-80, y1=-30, fillcolor="rgba(255,61,113,0.04)", line_width=0)

    fig.add_trace(go.Scatter(
        x=x, y=y_up, fill="tozeroy", fillcolor="rgba(0,225,255,0.13)",
        line=dict(color="#00E1FF", width=2.4, shape="spline", smoothing=0.5),
        mode="lines", showlegend=False, hovertemplate="MCT: %{y:.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=y_dn, fill="tozeroy", fillcolor="rgba(255,61,113,0.13)",
        line=dict(color="#FF3D71", width=2.4, shape="spline", smoothing=0.5),
        mode="lines", showlegend=False, hovertemplate="MCT: %{y:.2f}<extra></extra>",
    ))
    # Glow ring + dot
    fig.add_trace(go.Scatter(x=[x[-1]], y=[current], mode="markers",
        marker=dict(color=dot_c, size=13, opacity=0.2, line=dict(width=0)),
        showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[x[-1]], y=[current], mode="markers",
        marker=dict(color=dot_c, size=7, line=dict(color="#070A12", width=2)),
        showlegend=False, hoverinfo="skip"))

    for lvl, lbl in [(80,"OB EXTREME"),(30,"OB ZONE"),(0,None),(-30,"OS ZONE"),(-80,"OS EXTREME")]:
        lc   = "rgba(255,255,255,0.45)" if lvl==0 else "rgba(42,53,80,0.8)"
        dash = "solid" if lvl==0 else "dot"
        fig.add_hline(y=lvl, line_color=lc, line_width=1.1 if lvl==0 else 0.65, line_dash=dash)
        if lbl:
            fc = "rgba(0,225,255,0.45)" if lvl>0 else "rgba(255,61,113,0.45)"
            fig.add_annotation(x=0, y=lvl, xref="paper", text=f"  {lbl}",
                showarrow=False, font=dict(size=7, color=fc, family="Share Tech Mono,monospace"),
                xanchor="left", yanchor="bottom")

    sym = "▲" if momentum >= 0 else "▼"
    fig.add_annotation(x=1, y=0.97, xref="paper", yref="paper",
        text=f"{regime}  {sym} {abs(momentum):.1f}", showarrow=False,
        font=dict(size=9, color=dot_c, family="Share Tech Mono,monospace"),
        xanchor="right", yanchor="top")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=235, margin=dict(l=8,r=54,t=8,b=8),
        dragmode=False, hovermode="x",
        xaxis=dict(visible=False, showgrid=False, fixedrange=True),
        yaxis=dict(range=[-100,100], showgrid=False, zeroline=False,
            fixedrange=True, tickvals=[-80,-30,0,30,80],
            tickfont=dict(color="#3A4A6A",size=9,family="Share Tech Mono,monospace"),
            side="right"),
    )
    return fig


def factor_bars_html(r: dict) -> str:
    factors = [
        ("RSI",   r["rsi_score"]),
        ("MACD",  r["macd_score"]),
        ("VOL",   r["vol_score"]),
    ]
    items = ""
    for k, v in factors:
        v   = float(np.clip(v, -100, 100))
        c   = "#00E1FF" if v >= 0 else "#FF3D71"
        sgn = "+" if v >= 0 else ""
        ml  = f"margin-left:{100-abs(v):.0f}%" if v < 0 else ""
        items += f"""
        <div class="av-factor-item">
            <div class="av-factor-k">{k}</div>
            <div class="av-factor-bar-wrap">
                <div style="width:{abs(v):.0f}%;height:100%;background:{c};{ml};border-radius:1px"></div>
            </div>
            <div class="av-factor-v" style="color:{c}">{sgn}{v:.0f}</div>
        </div>"""
    return f'<div class="av-factor-wrap">{items}</div>'

# ==============================================================================
# TV WIDGET HELPERS
# ==============================================================================
def _tv(src: str, cfg: dict, h: int) -> str:
    cj = json.dumps(cfg)
    return f"""<!DOCTYPE html><html><head>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{background:transparent;overflow:hidden}}</style>
</head><body>
<div class="tradingview-widget-container" style="width:100%;height:{h}px">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="{src}" async>{cj}</script>
</div></body></html>"""


def tv_ticker_tape() -> str:
    return _tv("https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js", {
        "symbols":[
            {"proName":"FX:EURUSD",          "title":"EUR/USD"},
            {"proName":"FX:GBPUSD",          "title":"GBP/USD"},
            {"proName":"FX:USDJPY",          "title":"USD/JPY"},
            {"proName":"FX:AUDUSD",          "title":"AUD/USD"},
            {"proName":"OANDA:XAUUSD",       "title":"XAU/USD"},
            {"proName":"CAPITALCOM:DXY",     "title":"DXY"},
            {"proName":"TVC:US10Y",          "title":"US10Y"},
            {"proName":"CAPITALCOM:OIL_CRUDE","title":"OIL"},
            {"proName":"COINBASE:BTCUSD",    "title":"BTC/USD"},
            {"proName":"COINBASE:ETHUSD",    "title":"ETH/USD"},
            {"proName":"NASDAQ:NVDA",        "title":"NVDA"},
            {"proName":"FOREXCOM:SPXUSD",    "title":"S&P 500"},
        ],
        "showSymbolLogo":True,"isTransparent":True,
        "displayMode":"adaptive","colorTheme":"dark","locale":"en",
    }, 54)


def tv_market_overview() -> str:
    return _tv("https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js", {
        "colorTheme":"dark","dateRange":"3M","locale":"en","isTransparent":True,
        "plotLineColorGrowing":"rgba(0,225,255,1)","plotLineColorFalling":"rgba(255,61,113,1)",
        "gridLineColor":"rgba(42,53,80,0)","scaleFontColor":"#4A6080",
        "belowLineFillColorGrowing":"rgba(0,225,255,0.10)",
        "belowLineFillColorFalling":"rgba(255,61,113,0.10)",
        "belowLineFillColorGrowingBottom":"rgba(0,225,255,0)",
        "belowLineFillColorFallingBottom":"rgba(255,61,113,0)",
        "symbolActiveColor":"rgba(0,225,255,0.10)","backgroundColor":"#09111E",
        "tabs":[
            {"title":"FOREX","originalTitle":"Forex","symbols":[
                {"s":"FX:EURUSD","d":"EUR/USD"},{"s":"FX:GBPUSD","d":"GBP/USD"},
                {"s":"FX:USDJPY","d":"USD/JPY"},{"s":"FX:USDCHF","d":"USD/CHF"},{"s":"FX:AUDUSD","d":"AUD/USD"},
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
        "width":"100%","height":"390","showSymbolLogo":True,"showChart":True,
    }, 390)


# Indikator mode untuk main chart (Pine Script public IDs)
INDICATOR_MODES = {
    "NO MODE":  None,
    "VOFS":     "PUB;LuxAlgo/Volumetric-Order-Flow-Structure",
    "OBMTE":    "PUB;AlphaExtract/Order-Block-Matrix-Trade-Engine",
    "OFVB":     "PUB;QuantumEdge/Volume-bubbles",
    "BOB":      "PUB;TradingIQ/Big-Order-Bubbles-IQ",
    "OI":       "PUB;LeviathanCapital/Volume-Open-Interest-Footprint",
    "BSS":      "PUB;Bjorgum/Bjorgum-SuperScript",
}


def tv_advanced_chart(symbol: str, interval: str, style: str, studies: list = None) -> str:
    cfg = json.dumps({
        "autosize":True,"symbol":symbol,"interval":TV_INTERVAL[interval],
        "timezone":"Etc/UTC","theme":"dark","style":style,"locale":"en",
        "backgroundColor":"#070A12","gridColor":"rgba(42,53,80,0.3)",
        "hide_top_toolbar":False,"hide_legend":False,
        "allow_symbol_change":False,"save_image":False,
        "calendar":False,"support_host":"https://www.tradingview.com",
        "studies": studies if studies else [],
    })
    return f"""<!DOCTYPE html><html><head>
<style>*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{height:100%;background:#070A12;overflow:hidden}}</style>
</head><body>
<div class="tradingview-widget-container" style="height:490px;width:100%">
  <div class="tradingview-widget-container__widget" style="height:490px;width:100%"></div>
  <script type="text/javascript"
    src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
  {cfg}</script>
</div></body></html>"""


def tv_tech_gauge(symbol: str, interval: str) -> str:
    return _tv("https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js", {
        "colorTheme":"dark","displayMode":"single","isTransparent":True,"locale":"en",
        "interval":TV_TA_INT[interval],"width":"100%","height":"360",
        "symbol":symbol,"showIntervalTabs":True,
    }, 360)


def tv_mini_chart(symbol: str) -> str:
    return _tv("https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js", {
        "symbol":symbol,"width":"100%","height":200,"locale":"en","dateRange":"1M",
        "colorTheme":"dark","isTransparent":True,"autosize":True,
        "largeChartUrl":"","chartOnly":False,
    }, 200)


def tv_econ_calendar() -> str:
    return _tv("https://s3.tradingview.com/external-embedding/embed-widget-events.js", {
        "colorTheme":"dark","isTransparent":True,"width":"100%","height":"430","locale":"en",
        "importanceFilter":"0,1","countryFilter":"us,eu,gb,jp,au,ch,ca,cn",
    }, 430)


def tv_screener() -> str:
    return _tv("https://s3.tradingview.com/external-embedding/embed-widget-screener.js", {
        "market":"forex","showToolbar":True,"defaultColumn":"overview","defaultScreen":"general",
        "isTransparent":True,"locale":"en","colorTheme":"dark","width":"100%","height":"430",
    }, 430)


def tv_top_stories() -> str:
    return _tv("https://s3.tradingview.com/external-embedding/embed-widget-timeline.js", {
        "feedMode":"all_symbols","colorTheme":"dark","isTransparent":True,
        "displayMode":"regular","width":"100%","height":"460","locale":"en",
    }, 460)

# ==============================================================================
# HELPER: selectbox neon cyan (tidak bisa diketik via CSS)
# ==============================================================================
def av_select(label_text: str, key: str, options: list, current: str) -> str:
    idx = options.index(current) if current in options else 0
    if label_text:
        st.markdown(f'<div class="av-sel-label">{label_text}</div>', unsafe_allow_html=True)
    chosen = st.selectbox("_", options, index=idx, key=key, label_visibility="collapsed")
    return chosen

# ==============================================================================================
# ══════════════════════════════════════════════════════════════════════════════════════════════
#  AEROVULPIS INTELLIGENCE PIPELINE
#  6 Engine untuk Analisis Pair · 7 Engine untuk Analisis News
#  Python menghitung secara deterministik — AI (NVIDIA Nemotron) hanya menerjemahkan menjadi narasi
# ══════════════════════════════════════════════════════════════════════════════════════════════
# ==============================================================================================

PAIR_DECIMALS = {
    "XAUUSD": 2, "XAGUSD": 3, "WTIUSD": 2, "BRENT": 2, "NATGAS": 3,
    "USDJPY": 3,
    "BTCUSD": 1, "ETHUSD": 2, "SOLUSD": 3, "BNBUSD": 2, "XRPUSD": 4,
}
def _decimals_for(pair: str) -> int:
    return PAIR_DECIMALS.get(pair, 5)

def _fmt_price(val: float, pair: str) -> str:
    d = _decimals_for(pair)
    return f"{val:.{d}f}"

# ──────────────────────────────────────────────────────────────────────────────────────────────
# A. MARKET DATA ENGINE — murni ambil & bersihkan data, tidak ada perhitungan analitis
# ──────────────────────────────────────────────────────────────────────────────────────────────
def market_data_engine(df: pd.DataFrame, pair: str, tf: str) -> dict:
    last   = df.iloc[-1]
    close  = float(last["close"])
    high   = float(df["high"].tail(50).max())
    low    = float(df["low"].tail(50).min())
    vol    = float(last.get("volume", 0))
    atr_series = ta.atr(df["high"], df["low"], df["close"], length=14)
    atr_val = float(atr_series.iloc[-1]) if atr_series is not None and not pd.isna(atr_series.iloc[-1]) else (high-low)*0.05

    now_utc = datetime.now(timezone.utc)
    hour = now_utc.hour
    if 7 <= hour < 12:
        session = "LONDON"
    elif 12 <= hour < 16:
        session = "LONDON/NEW YORK OVERLAP"
    elif 16 <= hour < 21:
        session = "NEW YORK"
    elif 0 <= hour < 7:
        session = "ASIA"
    else:
        session = "TRANSISI SESI"

    return {
        "pair": pair, "timeframe": tf,
        "price": close, "high_50": high, "low_50": low,
        "volume": vol, "atr": atr_val,
        "session": session,
        "timestamp": now_utc.strftime("%d %b %Y"),
    }

# ──────────────────────────────────────────────────────────────────────────────────────────────
# B. QUANTITATIVE ENGINE — EMA, RSI, MACD, ADX, Bollinger, Momentum → semua skor numerik 0-100
# ──────────────────────────────────────────────────────────────────────────────────────────────
def quantitative_engine(df: pd.DataFrame) -> dict:
    close = df["close"]; high = df["high"]; low = df["low"]
    volume = df.get("volume", pd.Series(np.ones(len(df)), index=df.index))

    ema20  = ta.ema(close, length=20)
    ema50  = ta.ema(close, length=50)
    ema200 = ta.ema(close, length=200) if len(df) >= 200 else ta.ema(close, length=min(100, len(df)-1))
    rsi    = ta.rsi(close, length=14)
    macd_df = ta.macd(close, fast=12, slow=26, signal=9)
    adx_df  = ta.adx(high, low, close, length=14)
    bb      = ta.bbands(close, length=20, std=2)
    roc     = ta.roc(close, length=10)

    c       = float(close.iloc[-1])
    e20     = float(ema20.iloc[-1]) if not pd.isna(ema20.iloc[-1]) else c
    e50     = float(ema50.iloc[-1]) if not pd.isna(ema50.iloc[-1]) else c
    e200    = float(ema200.iloc[-1]) if ema200 is not None and not pd.isna(ema200.iloc[-1]) else c
    r       = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
    macd_h  = float(macd_df["MACDh_12_26_9"].iloc[-1]) if macd_df is not None and not pd.isna(macd_df["MACDh_12_26_9"].iloc[-1]) else 0.0
    adx_v   = float(adx_df["ADX_14"].iloc[-1]) if adx_df is not None and not pd.isna(adx_df["ADX_14"].iloc[-1]) else 20.0
    roc_v   = float(roc.iloc[-1]) if not pd.isna(roc.iloc[-1]) else 0.0

    trend_align = (1 if c > e20 else -1) + (1 if e20 > e50 else -1) + (1 if e50 > e200 else -1)
    trend_score = 50 + (trend_align * 12) + min(20, max(-20, (adx_v - 20)))
    trend_score = float(np.clip(trend_score, 0, 100))

    momentum_score = 50 + (r - 50) * 0.7 + np.clip(macd_h * 800, -20, 20) + np.clip(roc_v * 3, -10, 10)
    momentum_score = float(np.clip(momentum_score, 0, 100))

    vol_ma = volume.rolling(20, min_periods=5).mean()
    vol_ratio = float(volume.iloc[-1] / vol_ma.iloc[-1]) if not pd.isna(vol_ma.iloc[-1]) and vol_ma.iloc[-1] > 0 else 1.0
    volume_score = float(np.clip(50 + (vol_ratio - 1) * 40, 0, 100))

    if bb is not None:
        bb_upper = bb.filter(like="BBU").iloc[-1].values[0] if len(bb.filter(like="BBU").columns) else c*1.01
        bb_lower = bb.filter(like="BBL").iloc[-1].values[0] if len(bb.filter(like="BBL").columns) else c*0.99
        bb_width_pct = (bb_upper - bb_lower) / c * 100 if c else 1.0
    else:
        bb_width_pct = 1.0
    volatility_score = float(np.clip(bb_width_pct * 18, 0, 100))

    composite = (trend_score*0.35 + momentum_score*0.30 + volume_score*0.15 + volatility_score*0.10 + min(adx_v,50)*0.10)
    composite = float(np.clip(composite, 0, 100))

    return {
        "ema20": e20, "ema50": e50, "ema200": e200,
        "rsi": r, "macd_hist": macd_h, "adx": adx_v, "roc": roc_v,
        "trend_score": trend_score, "momentum_score": momentum_score,
        "volume_score": volume_score, "volatility_score": volatility_score,
        "composite": composite,
        "bb_width_pct": bb_width_pct,
    }

# ──────────────────────────────────────────────────────────────────────────────────────────────
# C. INSTITUTIONAL ENGINE (SMC sederhana) — swing high/low → BOS, CHoCH, liquidity, order block, FVG
# ──────────────────────────────────────────────────────────────────────────────────────────────
def institutional_engine(df: pd.DataFrame, swing_window: int = 5) -> dict:
    highs = df["high"].values
    lows  = df["low"].values
    closes = df["close"].values
    n = len(df)

    swing_highs, swing_lows = [], []
    for i in range(swing_window, n - swing_window):
        window_h = highs[i-swing_window:i+swing_window+1]
        window_l = lows[i-swing_window:i+swing_window+1]
        if highs[i] == window_h.max():
            swing_highs.append((i, highs[i]))
        if lows[i] == window_l.min():
            swing_lows.append((i, lows[i]))

    last_swing_high = swing_highs[-1][1] if swing_highs else float(highs.max())
    last_swing_low  = swing_lows[-1][1]  if swing_lows  else float(lows.min())

    last_close = float(closes[-1])

    bos_bull = last_close > last_swing_high
    bos_bear = last_close < last_swing_low

    choch_bull = (len(swing_lows) >= 2 and swing_lows[-1][1] > swing_lows[-2][1] and last_close > last_swing_high)
    choch_bear = (len(swing_highs) >= 2 and swing_highs[-1][1] < swing_highs[-2][1] and last_close < last_swing_low)

    if bos_bull and not choch_bear:
        bos_status, structure = "BULLISH CONFIRMED", "Bullish Continuation"
    elif bos_bear and not choch_bull:
        bos_status, structure = "BEARISH CONFIRMED", "Bearish Continuation"
    else:
        bos_status, structure = "BELUM TERKONFIRMASI", "Konsolidasi / Sideways"

    if choch_bull:
        choch_status = "BULLISH REVERSAL"
    elif choch_bear:
        choch_status = "BEARISH REVERSAL"
    else:
        choch_status = "TIDAK ADA"

    recent = df.tail(10)
    liquidity_side = "NEUTRAL"
    if (recent["low"] < last_swing_low).any() and last_close > last_swing_low:
        liquidity_side = "BUY-SIDE TERAMBIL"
    elif (recent["high"] > last_swing_high).any() and last_close < last_swing_high:
        liquidity_side = "SELL-SIDE TERAMBIL"

    ob_valid = False
    ob_zone = (last_swing_low, last_swing_high)
    if len(df) >= 4:
        if "open" in df.columns:
            open_series = df["open"]
        else:
            open_series = df["close"].shift(1).fillna(df["close"].iloc[0])
        body_sizes = (df["close"] - open_series).abs().tail(20)
        avg_body = body_sizes.mean()
        impulse_idx = body_sizes[body_sizes > avg_body * 1.8].index
        if len(impulse_idx) > 0:
            ob_valid = True
            ob_pos = df.index.get_loc(impulse_idx[-1])
            ob_candle_idx = max(0, ob_pos - 1)
            ob_zone = (float(df["low"].iloc[ob_candle_idx]), float(df["high"].iloc[ob_candle_idx]))

    fvg_active = False
    fvg_zone = None
    for i in range(n-1, max(n-15, 2), -1):
        gap_up   = lows[i] > highs[i-2]
        gap_down = highs[i] < lows[i-2]
        if gap_up or gap_down:
            fvg_active = True
            fvg_zone = (float(highs[i-2]), float(lows[i])) if gap_up else (float(highs[i]), float(lows[i-2]))
            break

    rng = last_swing_high - last_swing_low if last_swing_high > last_swing_low else 1e-9
    pos_in_range = (last_close - last_swing_low) / rng
    if pos_in_range >= 0.55:
        pd_zone = "PREMIUM ZONE"
    elif pos_in_range <= 0.45:
        pd_zone = "DISCOUNT ZONE"
    else:
        pd_zone = "EQUILIBRIUM"

    inst_score = 50.0
    if bos_status == "BULLISH CONFIRMED": inst_score += 20
    elif bos_status == "BEARISH CONFIRMED": inst_score -= 20
    if choch_status == "BULLISH REVERSAL": inst_score += 10
    elif choch_status == "BEARISH REVERSAL": inst_score -= 10
    if liquidity_side == "BUY-SIDE TERAMBIL": inst_score += 8
    elif liquidity_side == "SELL-SIDE TERAMBIL": inst_score -= 8
    if pd_zone == "DISCOUNT ZONE": inst_score += 6
    elif pd_zone == "PREMIUM ZONE": inst_score -= 6
    inst_score = float(np.clip(inst_score, 0, 100))

    return {
        "bos_status": bos_status, "structure": structure,
        "choch_status": choch_status,
        "liquidity_side": liquidity_side,
        "order_block_valid": ob_valid, "order_block_zone": ob_zone,
        "fvg_active": fvg_active, "fvg_zone": fvg_zone,
        "pd_zone": pd_zone,
        "last_swing_high": last_swing_high, "last_swing_low": last_swing_low,
        "institutional_score": inst_score,
    }

# ──────────────────────────────────────────────────────────────────────────────────────────────
# D. RISK ENGINE — ATR based SL/TP, RR ratio, probabilitas eksekusi
# ──────────────────────────────────────────────────────────────────────────────────────────────
def risk_engine(market: dict, quant: dict, inst: dict, pair: str) -> dict:
    price = market["price"]
    atr   = market["atr"]

    bullish = quant["trend_score"] >= 50 and inst["institutional_score"] >= 50
    direction = "BUY" if bullish else "SELL"

    if direction == "BUY":
        entry = price
        sl    = price - atr * 1.5
        tp1   = price + atr * 1.5
        tp2   = price + atr * 2.5
        tp3   = price + atr * 4.0
    else:
        entry = price
        sl    = price + atr * 1.5
        tp1   = price - atr * 1.5
        tp2   = price - atr * 2.5
        tp3   = price - atr * 4.0

    risk_dist   = abs(entry - sl)
    reward_dist = abs(tp2 - entry)
    rr_ratio    = round(reward_dist / risk_dist, 2) if risk_dist > 0 else 0.0

    base_conf = (quant["composite"] * 0.5 + inst["institutional_score"] * 0.5)
    probability = float(np.clip(base_conf, 35, 95))

    if atr / price * 100 < 0.15:
        atr_risk = "LOW"
    elif atr / price * 100 < 0.40:
        atr_risk = "MEDIUM"
    else:
        atr_risk = "HIGH"

    contingency_dir = "SELL" if direction == "BUY" else "BUY"
    if contingency_dir == "BUY":
        c_entry = sl; c_sl = sl - atr*1.0
        c_tp1, c_tp2, c_tp3 = sl + atr*1.5, sl + atr*2.5, sl + atr*3.8
    else:
        c_entry = sl; c_sl = sl + atr*1.0
        c_tp1, c_tp2, c_tp3 = sl - atr*1.5, sl - atr*2.5, sl - atr*3.8

    return {
        "direction": direction,
        "entry": entry, "sl": sl, "tp1": tp1, "tp2": tp2, "tp3": tp3,
        "rr_ratio": rr_ratio, "probability": round(probability, 0),
        "atr_risk": atr_risk,
        "contingency_dir": contingency_dir,
        "c_entry": c_entry, "c_sl": c_sl,
        "c_tp1": c_tp1, "c_tp2": c_tp2, "c_tp3": c_tp3,
        "contingency_probability": round(100 - probability, 0),
    }

# ──────────────────────────────────────────────────────────────────────────────────────────────
# SCORING ENGINE — gabungkan semua skor jadi Institutional Score akhir
# ──────────────────────────────────────────────────────────────────────────────────────────────
def scoring_engine(quant: dict, inst: dict, risk: dict) -> dict:
    weights = {"trend":0.25, "momentum":0.15, "volume":0.10, "smc":0.30, "volatility":0.10, "risk":0.10}
    risk_component = float(np.clip(risk["probability"], 0, 100))
    final_score = (
        quant["trend_score"]      * weights["trend"] +
        quant["momentum_score"]   * weights["momentum"] +
        quant["volume_score"]     * weights["volume"] +
        inst["institutional_score"]* weights["smc"] +
        quant["volatility_score"] * weights["volatility"] +
        risk_component             * weights["risk"]
    )
    final_score = float(np.clip(final_score, 0, 100))

    if final_score >= 80: conviction = "HIGH CONVICTION"
    elif final_score >= 60: conviction = "MODERATE CONVICTION"
    elif final_score >= 40: conviction = "LOW CONVICTION"
    else: conviction = "NO TRADE SETUP"

    return {"composite_rating": round(final_score, 1), "conviction": conviction, "weights": weights}

# ──────────────────────────────────────────────────────────────────────────────────────────────
# E. AI INTERPRETATION ENGINE (Groq — llama-3.3-70b-versatile)
# ──────────────────────────────────────────────────────────────────────────────────────────────
def call_groq_llm(system_prompt: str, user_prompt: str, max_tokens: int = 500) -> str:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        return "__AI_UNAVAILABLE__"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
        "top_p": 0.9,
        "max_tokens": max_tokens,
        "stream": False,
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return "__AI_UNAVAILABLE__"


def ai_interpret_pair(market: dict, quant: dict, inst: dict, risk: dict, score: dict) -> str:
    system_prompt = (
        "Kamu adalah AI Interpretation Engine pada terminal trading institusional bernama "
        "AEROVULPIS TERMINAL, khusus modul analisis teknikal & struktur pasar (Smart Money Concept). "
        "Tugasmu HANYA menerjemahkan data numerik yang sudah dihitung mesin kuantitatif menjadi "
        "narasi analisis yang mendalam, tajam, dan dalam Bahasa Indonesia formal ala trading desk "
        "institusi (gaya riset teknikal Bloomberg/Reuters). Kamu TIDAK BOLEH menghitung ulang "
        "indikator apapun — semua angka sudah final, tugasmu murni menginterpretasikan maknanya. "
        "Tulis narasi sepanjang 3 paragraf (total sekitar 9-12 kalimat), TANPA heading, TANPA "
        "bullet point, TANPA markdown — paragraf mengalir seperti catatan analis profesional:\n"
        "Paragraf 1: kondisi pasar saat ini secara umum (trend, momentum, volatilitas) dan apa "
        "artinya bagi arah harga.\n"
        "Paragraf 2: pembacaan struktur pasar institusional (BOS, CHoCH, order block, liquidity, "
        "zona premium/discount) dan bagaimana ini memperkuat atau melemahkan bias arah.\n"
        "Paragraf 3: kesimpulan rekomendasi eksekusi — mengapa level entry/SL/TP masuk akal secara "
        "risk management, serta kondisi apa yang bisa membatalkan skenario ini."
    )
    user_prompt = f"""
Data hasil perhitungan kuantitatif untuk {market['pair']} timeframe {market['timeframe']}:

Trend Score: {quant['trend_score']:.0f}/100
Momentum Score: {quant['momentum_score']:.0f}/100
Volume Score: {quant['volume_score']:.0f}/100
Volatility Score: {quant['volatility_score']:.0f}/100
RSI: {quant['rsi']:.1f}
ADX: {quant['adx']:.1f}

Market Structure: {inst['structure']}
BOS: {inst['bos_status']}
CHoCH: {inst['choch_status']}
Liquidity: {inst['liquidity_side']}
Premium/Discount Zone: {inst['pd_zone']}
Order Block Valid: {inst['order_block_valid']}
FVG Aktif: {inst['fvg_active']}

Risk Engine:
Direction: {risk['direction']}
Entry: {_fmt_price(risk['entry'], market['pair'])}
Stop Loss: {_fmt_price(risk['sl'], market['pair'])}
Take Profit 2: {_fmt_price(risk['tp2'], market['pair'])}
Risk/Reward: 1:{risk['rr_ratio']}
Probabilitas Eksekusi: {risk['probability']:.0f}%
ATR Risk Level: {risk['atr_risk']}

Composite Rating: {score['composite_rating']}/100
Conviction Level: {score['conviction']}
Sesi pasar saat ini: {market['session']}

Tulis narasi analisis pasar 3 paragraf sesuai instruksi sistem, dalam Bahasa Indonesia formal,
berdasarkan data di atas untuk bias arah {risk['direction']}.
"""
    result = call_groq_llm(system_prompt, user_prompt, max_tokens=650)
    if result == "__AI_UNAVAILABLE__":
        return _fallback_narrative_pair(market, quant, inst, risk, score)
    return result


def _fallback_narrative_pair(market, quant, inst, risk, score) -> str:
    """Narasi cadangan berbasis rule Python — dipakai saat lapisan interpretasi AI sedang tidak tersedia."""
    arah = "penguatan" if risk["direction"] == "BUY" else "pelemahan"
    p1 = (
        f"Struktur pasar {market['pair']} pada timeframe {market['timeframe']} menunjukkan "
        f"{inst['structure'].lower()}, dengan Trend Score berada di {quant['trend_score']:.0f}/100 "
        f"dan Momentum Score {quant['momentum_score']:.0f}/100. Kombinasi ini mengindikasikan potensi "
        f"{arah} harga dalam waktu dekat, didukung Volatility Index {quant['volatility_score']:.0f}/100 "
        f"yang menggambarkan tingkat pergerakan harga saat ini berada pada sesi {market['session']}."
    )
    p2 = (
        f"Dari sisi struktur institusional, sistem mendeteksi {inst['bos_status'].lower()} dengan "
        f"Change of Character {inst['choch_status'].lower()}. Zona harga saat ini berada pada "
        f"{inst['pd_zone'].lower()} dengan kondisi likuiditas {inst['liquidity_side'].lower()}, yang "
        f"secara historis menjadi area di mana pelaku pasar institusional cenderung membuka atau "
        f"menutup posisi besar."
    )
    p3 = (
        f"Rating komposit sistem tercatat {score['composite_rating']}/100 dengan klasifikasi "
        f"{score['conviction'].lower()}, memberikan probabilitas eksekusi sebesar {risk['probability']:.0f}% "
        f"untuk skenario {risk['direction']}. Rasio risk/reward 1:{risk['rr_ratio']} pada level ATR "
        f"{risk['atr_risk'].lower()} menjadikan setup ini layak dipertimbangkan dengan manajemen risiko "
        f"yang disiplin, mengingat skenario ini dapat berubah apabila struktur pasar mengalami reversal."
    )
    return f"{p1}\n\n{p2}\n\n{p3}"


def ai_interpret_news(news_summary: dict, sample_titles: list = None) -> str:
    system_prompt = (
        "Kamu adalah AI Interpretation Engine pada terminal trading institusional bernama "
        "AEROVULPIS TERMINAL, khusus modul News Intelligence & analisis makroekonomi. Beberapa "
        "judul artikel sumber diberikan dalam Bahasa Inggris — tugasmu adalah membaca makna "
        "artikel-artikel tersebut dan menerjemahkan intisarinya ke Bahasa Indonesia formal ala "
        "jurnalis riset makro (gaya Reuters/Bloomberg Indonesia), DIGABUNGKAN dengan hasil "
        "perhitungan statistik sistem (sentimen, dampak, klasifikasi) yang sudah final — kamu "
        "TIDAK BOLEH mengubah angka statistik tersebut, hanya menjelaskan maknanya. "
        "Tulis narasi sepanjang 3 paragraf (total sekitar 9-12 kalimat), TANPA heading, TANPA "
        "bullet point, TANPA markdown, TANPA menyebut nama media/sumber artikel secara spesifik:\n"
        "Paragraf 1: ringkasan inti dari berita/topik ini — apa yang sebenarnya terjadi, dalam "
        "bahasa yang mudah dipahami trader awam.\n"
        "Paragraf 2: konteks makroekonomi — mengapa ini penting bagi bank sentral, kebijakan "
        "moneter, dan bagaimana ini membentuk sentimen risk-on/risk-off pasar saat ini.\n"
        "Paragraf 3: implikasi konkret terhadap aset-aset yang terdampak, dan skenario mana yang "
        "lebih mungkin terjadi ke depan berdasarkan bias institusional yang terdeteksi sistem."
    )

    titles_block = ""
    if sample_titles:
        titles_block = "\n".join(f"- {t}" for t in sample_titles[:8])
    else:
        titles_block = "(tidak ada judul artikel spesifik tersedia — gunakan data statistik saja)"

    user_prompt = f"""
Topik yang dianalisis: "{news_summary['query']}"

Judul artikel sumber (Bahasa Inggris, untuk kamu pahami maknanya):
{titles_block}

Hasil perhitungan statistik sistem:
Jumlah artikel diproses: {news_summary['total_articles']}
Sumber unik: {news_summary['unique_sources']}
Tingkat konsensus lintas sumber: {news_summary['consensus_pct']}%

Klasifikasi berita: {news_summary['classification']}
Tingkat dampak: {news_summary['impact']}
Sensitivitas pasar: {news_summary['sensitivity']}

Tema makro: {news_summary['macro_theme']}
Outlook kebijakan: {news_summary['policy_outlook']}
Sentimen Risk-On/Risk-Off: {news_summary['risk_env']}

Probabilitas Bullish: {news_summary['bullish_pct']}%
Probabilitas Bearish: {news_summary['bearish_pct']}%
Bias institusional: {news_summary['institutional_bias']}

Aset paling terdampak: {', '.join(news_summary['top_assets'])}

Tulis narasi interpretasi pasar 3 paragraf sesuai instruksi sistem, dalam Bahasa Indonesia formal.
"""
    result = call_groq_llm(system_prompt, user_prompt, max_tokens=650)
    if result == "__AI_UNAVAILABLE__":
        return _fallback_narrative_news(news_summary)
    return result


def _fallback_narrative_news(summary: dict) -> str:
    """Narasi cadangan berbasis rule Python — dipakai saat lapisan interpretasi AI sedang tidak tersedia."""
    p1 = (
        f"Analisis terhadap topik \"{summary['query']}\" memproses {summary['total_articles']} artikel "
        f"dari {summary['unique_sources']} sumber berbeda, dengan tingkat konsensus lintas sumber "
        f"sebesar {summary['consensus_pct']:.0f}%. Berita ini tergolong dalam klasifikasi "
        f"{summary['classification'].lower()} dengan tingkat dampak {summary['impact'].lower()} "
        f"terhadap pergerakan pasar dalam waktu dekat."
    )
    p2 = (
        f"Dari sisi makroekonomi, tema yang mendominasi adalah {summary['macro_theme'].lower()} dengan "
        f"outlook kebijakan {summary['policy_outlook'].lower()}. Kondisi ini menciptakan lingkungan "
        f"sentimen {summary['risk_env'].lower()} di pasar global, yang secara historis memengaruhi "
        f"alokasi modal institusional antara aset berisiko dan aset lindung nilai."
    )
    p3 = (
        f"Model sentimen sistem mencatat probabilitas bullish {summary['bullish_pct']:.0f}% berbanding "
        f"bearish {summary['bearish_pct']:.0f}%, mengarahkan bias institusional ke arah "
        f"{summary['institutional_bias'].lower()}. Aset yang paling berpotensi terdampak meliputi "
        f"{', '.join(summary['top_assets'][:4])}, sehingga pelaku pasar disarankan memantau "
        f"pergerakan pada instrumen tersebut secara khusus dalam waktu dekat."
    )
    return f"{p1}\n\n{p2}\n\n{p3}"

# ──────────────────────────────────────────────────────────────────────────────────────────────
# NEWS PIPELINE — News Engine → Validation → Fundamental → Macro → Sentiment → Impact
# ──────────────────────────────────────────────────────────────────────────────────────────────

CURRENCY_KEYWORDS = {
    "USD": ["dollar","fed","federal reserve","fomc","nonfarm","nfp","cpi","treasury","powell"],
    "EUR": ["euro","ecb","lagarde","eurozone"],
    "GBP": ["pound","boe","bank of england","sterling"],
    "JPY": ["yen","boj","bank of japan","ueda"],
    "AUD": ["aussie","rba","australia"],
    "XAU": ["gold","xau"],
    "OIL": ["oil","opec","crude","wti","brent"],
}
HAWKISH_WORDS = ["rate hike","higher for longer","hawkish","tightening","inflation persists","raise rates"]
DOVISH_WORDS  = ["rate cut","dovish","easing","pause","lower rates","stimulus"]
POSITIVE_WORDS = ["surge","rally","beat expectations","strong","growth","optimis","bullish"]
NEGATIVE_WORDS = ["plunge","crash","recession","weak","miss expectations","bearish","risk-off","concern"]

# Kamus terjemahan istilah trading Indonesia → Inggris, agar query tetap match
# dengan bahasa mayoritas artikel di sumber berita global.
ID_EN_TERMS = {
    "inflasi": "inflation", "suku bunga": "interest rate", "bank sentral": "central bank",
    "nilai tukar": "exchange rate", "ekonomi": "economy", "resesi": "recession",
    "pengangguran": "unemployment", "gaji": "payroll", "data ketenagakerjaan": "employment data",
    "kenaikan": "hike", "penurunan": "cut", "kebijakan moneter": "monetary policy",
    "the fed": "federal reserve", "bank indonesia": "bank indonesia", "rupiah": "rupiah",
    "dolar": "dollar", "emas": "gold", "minyak": "oil", "harga": "price",
    "pasar saham": "stock market", "obligasi": "bond", "yield": "yield",
    "gdp": "gdp", "pdb": "gdp", "cpi": "cpi", "nfp": "non-farm payrolls",
}

def _translate_query_for_search(query: str) -> str:
    """Terjemahkan istilah Indonesia umum dalam query ke Inggris agar hasil pencarian
    berita internasional lebih relevan. Istilah yang tidak dikenali dibiarkan apa adanya
    (mis. nama pair EURUSD, XAUUSD tetap valid di kedua bahasa)."""
    q_lower = query.lower()
    translated = q_lower
    for id_term, en_term in ID_EN_TERMS.items():
        if id_term in translated:
            translated = translated.replace(id_term, en_term)
    return translated if translated != q_lower else query


@st.cache_data(ttl=300, show_spinner=False)
def fetch_news_newsapi(query: str) -> list:
    try:
        api_key = st.secrets["NEWSAPI_KEY"]
        q = _url_quote(query)
        url = f"https://newsapi.org/v2/everything?q={q}&language=en&sortBy=publishedAt&pageSize=15&apiKey={api_key}"
        r = requests.get(url, timeout=10).json()
        arts = r.get("articles", [])
        return [{"title":a.get("title",""), "desc":a.get("description","") or "", "source":a.get("source",{}).get("name","NewsAPI")} for a in arts]
    except Exception:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def fetch_news_marketaux(query: str) -> list:
    try:
        api_key = st.secrets["MARKETAUX_KEY"]
        q = _url_quote(query)
        url = f"https://api.marketaux.com/v1/news/all?search={q}&language=en&limit=15&api_token={api_key}"
        r = requests.get(url, timeout=10).json()
        arts = r.get("data", [])
        return [{"title":a.get("title",""), "desc":a.get("description","") or "", "source":a.get("source","MarketAux")} for a in arts]
    except Exception:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def fetch_news_gnews(query: str) -> list:
    try:
        api_key = st.secrets["GNEWS_KEY"]
        q = _url_quote(query)
        url = f"https://gnews.io/api/v4/search?q={q}&lang=en&max=15&apikey={api_key}"
        r = requests.get(url, timeout=10).json()
        arts = r.get("articles", [])
        return [{"title":a.get("title",""), "desc":a.get("description","") or "", "source":a.get("source",{}).get("name","GNews")} for a in arts]
    except Exception:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def fetch_news_currentnews(query: str) -> list:
    try:
        api_key = st.secrets["CURRENT_NEWS_KEY"]
        q = _url_quote(query)
        url = f"https://currentsapi.services/v1/search?keywords={q}&language=en&apiKey={api_key}"
        r = requests.get(url, timeout=10).json()
        arts = r.get("news", [])
        return [{"title":a.get("title",""), "desc":a.get("description","") or "", "source":a.get("author","CurrentNews") or "CurrentNews"} for a in arts]
    except Exception:
        return []


def news_engine(query: str) -> list:
    """A. News Engine — terjemahkan query ID->EN dulu, lalu ambil dari 4 sumber sekaligus."""
    search_query = _translate_query_for_search(query)

    all_articles = []
    all_articles += fetch_news_newsapi(search_query)
    all_articles += fetch_news_marketaux(search_query)
    all_articles += fetch_news_gnews(search_query)
    all_articles += fetch_news_currentnews(search_query)

    # Fallback: kalau query spesifik tidak menghasilkan apapun (mis. terlalu niche),
    # coba lagi dengan kata kunci pertama saja agar tetap ada artikel relevan.
    if not all_articles and len(search_query.split()) > 1:
        broad_query = search_query.split()[0]
        all_articles += fetch_news_newsapi(broad_query)
        all_articles += fetch_news_marketaux(broad_query)
        all_articles += fetch_news_gnews(broad_query)
        all_articles += fetch_news_currentnews(broad_query)

    return all_articles


def news_validation_engine(articles: list) -> dict:
    seen_titles = set()
    clean = []
    duplicates = 0
    for a in articles:
        title = (a.get("title") or "").strip()
        if not title or len(title) < 10:
            continue
        norm = title.lower()[:60]
        if norm in seen_titles:
            duplicates += 1
            continue
        seen_titles.add(norm)
        clean.append(a)

    unique_sources = len(set(a.get("source","") for a in clean))
    consensus_pct = float(np.clip(70 + min(unique_sources, 10)*2.5, 50, 98)) if clean else 0.0

    return {
        "clean_articles": clean,
        "total_processed": len(articles),
        "duplicates": duplicates,
        "unique_sources": unique_sources,
        "consensus_pct": round(consensus_pct, 0),
    }


def fundamental_engine(clean_articles: list, query: str) -> dict:
    text_blob = " ".join([(a.get("title","")+" "+a.get("desc","")) for a in clean_articles]).lower()
    if not text_blob.strip():
        text_blob = query.lower()

    affected = []
    for cur, kws in CURRENCY_KEYWORDS.items():
        if any(kw in text_blob for kw in kws):
            affected.append(cur)
    if not affected:
        affected = ["USD"]

    central_bank = "FED" if "fed" in text_blob or "federal reserve" in text_blob or "fomc" in text_blob else (
        "ECB" if "ecb" in text_blob else ("BOE" if "boe" in text_blob else ("BOJ" if "boj" in text_blob else "—"))
    )
    inflation_flag = any(w in text_blob for w in ["inflation","cpi","price index"])
    employment_flag = any(w in text_blob for w in ["employment","nonfarm","payroll","jobless"])
    gdp_flag = "gdp" in text_blob

    impact = "HIGH" if (central_bank != "—" and inflation_flag) else ("MEDIUM" if affected else "LOW")

    return {
        "affected_currencies": affected,
        "central_bank": central_bank,
        "inflation": inflation_flag, "employment": employment_flag, "gdp": gdp_flag,
        "impact": impact,
    }


def macro_engine(clean_articles: list, query: str) -> dict:
    text_blob = " ".join([(a.get("title","")+" "+a.get("desc","")) for a in clean_articles]).lower()
    if not text_blob.strip():
        text_blob = query.lower()

    hawkish_hits = sum(text_blob.count(w) for w in HAWKISH_WORDS)
    dovish_hits  = sum(text_blob.count(w) for w in DOVISH_WORDS)

    if hawkish_hits > dovish_hits:
        policy_outlook = "HAWKISH"
        policy_theme = "Monetary Tightening"
        yield_env = "RISING"
    elif dovish_hits > hawkish_hits:
        policy_outlook = "DOVISH"
        policy_theme = "Monetary Easing"
        yield_env = "FALLING"
    else:
        policy_outlook = "NEUTRAL"
        policy_theme = "Wait and See"
        yield_env = "STABIL"

    neg_hits = sum(text_blob.count(w) for w in NEGATIVE_WORDS)
    pos_hits = sum(text_blob.count(w) for w in POSITIVE_WORDS)
    risk_env = "RISK-OFF" if neg_hits > pos_hits else ("RISK-ON" if pos_hits > neg_hits else "NETRAL")

    return {
        "policy_theme": policy_theme, "policy_outlook": policy_outlook,
        "yield_env": yield_env, "risk_env": risk_env,
    }


def sentiment_engine(clean_articles: list) -> dict:
    pos, neg, neu = 0, 0, 0
    for a in clean_articles:
        text = (a.get("title","")+" "+a.get("desc","")).lower()
        p = sum(text.count(w) for w in POSITIVE_WORDS)
        n = sum(text.count(w) for w in NEGATIVE_WORDS)
        if p > n: pos += 1
        elif n > p: neg += 1
        else: neu += 1

    total = max(pos+neg+neu, 1)
    bullish_pct = round(pos/total*100, 0)
    bearish_pct = round(neg/total*100, 0)
    if bullish_pct + bearish_pct == 0:
        bullish_pct, bearish_pct = 50.0, 50.0
    else:
        scale = 100.0 / (bullish_pct + bearish_pct) if (bullish_pct+bearish_pct) > 0 else 1
        bullish_pct = round(bullish_pct * scale, 0)
        bearish_pct = round(100 - bullish_pct, 0)

    return {"positive": pos, "negative": neg, "neutral": neu,
            "bullish_pct": bullish_pct, "bearish_pct": bearish_pct}


def impact_engine(fundamental: dict, macro: dict, sentiment: dict) -> dict:
    severity = fundamental["impact"]
    horizon = "IMMEDIATE" if severity == "HIGH" else ("MEDIUM" if severity == "MEDIUM" else "LONG TERM")

    asset_map = {
        "USD": ["EURUSD","GBPUSD","USDJPY","DXY"],
        "EUR": ["EURUSD"], "GBP": ["GBPUSD"], "JPY": ["USDJPY"], "AUD": ["AUDUSD"],
        "XAU": ["XAUUSD"], "OIL": ["WTIUSD","BRENT"],
    }
    affected_assets = []
    for cur in fundamental["affected_currencies"]:
        affected_assets += asset_map.get(cur, [])
    if not affected_assets:
        affected_assets = ["EURUSD","XAUUSD"]
    affected_assets = list(dict.fromkeys(affected_assets))[:6]

    if macro["risk_env"] == "RISK-OFF":
        institutional_bias = "USD Strength / Safe Haven Demand"
    elif macro["risk_env"] == "RISK-ON":
        institutional_bias = "Risk Asset Strength"
    else:
        institutional_bias = "Wait and See"

    return {"horizon": horizon, "top_assets": affected_assets, "institutional_bias": institutional_bias}


def run_news_pipeline(query: str) -> dict:
    raw_articles = news_engine(query)
    validation   = news_validation_engine(raw_articles)
    clean        = validation["clean_articles"]
    fundamental  = fundamental_engine(clean, query)
    macro        = macro_engine(clean, query)
    sentiment    = sentiment_engine(clean)
    impact       = impact_engine(fundamental, macro, sentiment)

    classification = fundamental["central_bank"] + " Policy" if fundamental["central_bank"] != "—" else "Market Update"
    sensitivity = "ELEVATED" if fundamental["impact"] == "HIGH" else "NORMAL"

    sample_titles = [a.get("title","").strip() for a in clean[:8] if a.get("title","").strip()]

    summary = {
        "query": query,
        "total_articles": validation["total_processed"],
        "unique_sources": validation["unique_sources"],
        "consensus_pct": validation["consensus_pct"],
        "classification": classification,
        "impact": fundamental["impact"],
        "sensitivity": sensitivity,
        "macro_theme": macro["policy_theme"],
        "risk_env": macro["risk_env"],
        "bullish_pct": sentiment["bullish_pct"],
        "bearish_pct": sentiment["bearish_pct"],
        "institutional_bias": impact["institutional_bias"],
        "top_assets": impact["top_assets"],
        "policy_outlook": macro["policy_outlook"],
        "yield_env": macro["yield_env"],
        "horizon": impact["horizon"],
        "central_bank": fundamental["central_bank"],
        "affected_currencies": fundamental["affected_currencies"],
        "duplicates_removed": validation["duplicates"],
        "sample_titles": sample_titles,
    }
    return summary

# ──────────────────────────────────────────────────────────────────────────────────────────────
# REPORT RENDERER — render hasil pipeline jadi tampilan Market Intelligence Report cybertech
# ──────────────────────────────────────────────────────────────────────────────────────────────
def render_pair_report(market, quant, inst, risk, score, narrative, pair):
    now_str = market["timestamp"]
    bias_cls = "buy" if risk["direction"] == "BUY" else "sell"
    narrative_html = narrative.replace("\n\n", "<br><br>").replace("\n", " ")

    html = f"""
    <div class="av-report-wrap">
      <div class="av-report-header">
        <span class="av-report-title">◈ MARKET INTELLIGENCE REPORT</span>
        <span class="av-report-badge">AEROVULPIS v4.1</span>
      </div>
      <div class="av-report-body">

        <div class="av-report-section-title">RINGKASAN EKSEKUTIF</div>
        <div class="av-report-row"><span class="av-report-k">Instrumen</span><span class="av-report-v">{pair}</span></div>
        <div class="av-report-row"><span class="av-report-k">Timeframe</span><span class="av-report-v">{market['timeframe']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Tanggal Analisis</span><span class="av-report-v">{now_str}</span></div>
        <div class="av-report-row"><span class="av-report-k">Bias Arah</span><span class="av-report-v {bias_cls}">{risk['direction']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Struktur Pasar</span><span class="av-report-v">{inst['structure']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Sesi Aktif</span><span class="av-report-v">{market['session']}</span></div>
        <div style="text-align:center;margin:14px 0">
          <div style="font-size:8px;color:#3A5070;letter-spacing:2px;margin-bottom:4px">PROBABILITAS EKSEKUSI</div>
          <span class="av-score-big" style="color:{'#00E1FF' if risk['direction']=='BUY' else '#FF3D71'}">{risk['probability']:.0f}%</span>
        </div>

        <div class="av-report-section-title">MODEL KUANTITATIF</div>
        <div class="av-report-row"><span class="av-report-k">Trend Strength</span><span class="av-report-v">{quant['trend_score']:.0f} /100</span></div>
        <div class="av-report-row"><span class="av-report-k">Momentum Factor</span><span class="av-report-v">{quant['momentum_score']:.0f} /100</span></div>
        <div class="av-report-row"><span class="av-report-k">Volume Participation</span><span class="av-report-v">{quant['volume_score']:.0f} /100</span></div>
        <div class="av-report-row"><span class="av-report-k">Volatility Index</span><span class="av-report-v">{quant['volatility_score']:.0f} /100</span></div>
        <div class="av-report-row"><span class="av-report-k">Composite Rating</span><span class="av-report-v" style="color:#00E1FF">{score['composite_rating']} /100</span></div>
        <div class="av-report-row"><span class="av-report-k">Klasifikasi Model</span><span class="av-report-v" style="color:#A855F7">{score['conviction']}</span></div>

        <div class="av-report-section-title">ANALISIS STRUKTUR PASAR (SMC)</div>
        <div class="av-report-row"><span class="av-report-k">Break of Structure</span><span class="av-report-v">{inst['bos_status']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Change of Character</span><span class="av-report-v">{inst['choch_status']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Order Block</span><span class="av-report-v">{'AKTIF' if inst['order_block_valid'] else 'TIDAK ADA'}</span></div>
        <div class="av-report-row"><span class="av-report-k">Fair Value Gap</span><span class="av-report-v">{'AKTIF' if inst['fvg_active'] else 'TIDAK ADA'}</span></div>
        <div class="av-report-row"><span class="av-report-k">Liquidity</span><span class="av-report-v">{inst['liquidity_side']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Zona Harga</span><span class="av-report-v">{inst['pd_zone']}</span></div>

        <div class="av-report-section-title">RENCANA EKSEKUSI UTAMA — {risk['direction']}</div>
        <div class="av-report-row"><span class="av-report-k">Zona Eksekusi</span><span class="av-report-v">{_fmt_price(risk['entry'], pair)}</span></div>
        <div class="av-report-row"><span class="av-report-k">Stop Loss</span><span class="av-report-v sell">{_fmt_price(risk['sl'], pair)}</span></div>
        <div class="av-report-row"><span class="av-report-k">Target 1</span><span class="av-report-v buy">{_fmt_price(risk['tp1'], pair)}</span></div>
        <div class="av-report-row"><span class="av-report-k">Target 2</span><span class="av-report-v buy">{_fmt_price(risk['tp2'], pair)}</span></div>
        <div class="av-report-row"><span class="av-report-k">Target 3</span><span class="av-report-v buy">{_fmt_price(risk['tp3'], pair)}</span></div>
        <div class="av-report-row"><span class="av-report-k">Risk / Reward</span><span class="av-report-v">1 : {risk['rr_ratio']}</span></div>
        <div class="av-report-row"><span class="av-report-k">ATR Risk Level</span><span class="av-report-v">{risk['atr_risk']}</span></div>

        <div class="av-report-section-title">SKENARIO ALTERNATIF — {risk['contingency_dir']}</div>
        <div class="av-report-row"><span class="av-report-k">Level Aktivasi</span><span class="av-report-v">{_fmt_price(risk['c_entry'], pair)}</span></div>
        <div class="av-report-row"><span class="av-report-k">Stop Loss</span><span class="av-report-v sell">{_fmt_price(risk['c_sl'], pair)}</span></div>
        <div class="av-report-row"><span class="av-report-k">Target 1</span><span class="av-report-v">{_fmt_price(risk['c_tp1'], pair)}</span></div>
        <div class="av-report-row"><span class="av-report-k">Probabilitas Skenario</span><span class="av-report-v">{risk['contingency_probability']:.0f}%</span></div>

        <div class="av-report-section-title">INTERPRETASI AI</div>
        <div class="av-report-narrative">{narrative_html}</div>

        <div class="av-report-section-title" style="margin-top:18px;font-size:7px;color:#2A3A5A">DISCLAIMER</div>
        <div style="font-size:8px;color:#3A4A60;line-height:1.7">
          Laporan ini merupakan estimasi probabilistik dari model kuantitatif, struktur pasar,
          likuiditas, dan interpretasi kecerdasan buatan. Seluruh rencana eksekusi bersifat skenario
          dan perlu divalidasi terhadap kondisi pasar terkini sebelum implementasi transaksi nyata.
        </div>

      </div>
    </div>
    """
    # Strip indentasi tiap baris — mencegah Markdown mendeteksinya sebagai code block
    html = "\n".join(line.strip() for line in html.split("\n"))
    return html


def render_news_report(summary, narrative):
    bull_cls = "buy" if summary["bullish_pct"] >= summary["bearish_pct"] else "sell"
    now_str = datetime.now(timezone.utc).strftime("%d %b %Y")
    narrative_html = narrative.replace("\n\n", "<br><br>").replace("\n", " ")

    assets_html = "".join([
        f'<div class="av-matrix-row"><span class="av-report-k">{a}</span>'
        f'<span class="av-matrix-arrow" style="color:{"#00E1FF" if summary["institutional_bias"].startswith("USD") or "Strength" in summary["institutional_bias"] else "#A855F7"}">●</span></div>'
        for a in summary["top_assets"]
    ])

    html = f"""
    <div class="av-report-wrap">
      <div class="av-report-header">
        <span class="av-report-title">◈ MARKET NEWS INTELLIGENCE REPORT</span>
        <span class="av-report-badge">AEROVULPIS v4.1</span>
      </div>
      <div class="av-report-body">

        <div class="av-report-section-title">HEADLINE UTAMA</div>
        <div style="color:#C8D8F0;font-size:11px;font-weight:700;margin-bottom:8px">{summary['query']}</div>
        <div class="av-report-row"><span class="av-report-k">Tanggal Analisis</span><span class="av-report-v">{now_str}</span></div>

        <div class="av-report-section-title">NEWS VALIDATION ENGINE</div>
        <div class="av-report-row"><span class="av-report-k">Artikel Diproses</span><span class="av-report-v">{summary['total_articles']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Sumber Unik</span><span class="av-report-v">{summary['unique_sources']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Duplikat Dihapus</span><span class="av-report-v">{summary['duplicates_removed']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Konsensus Lintas Sumber</span><span class="av-report-v" style="color:#00E1FF">{summary['consensus_pct']:.0f}%</span></div>

        <div class="av-report-section-title">PENILAIAN INTELIJEN</div>
        <div class="av-report-row"><span class="av-report-k">Klasifikasi Berita</span><span class="av-report-v">{summary['classification']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Tingkat Dampak</span><span class="av-report-v" style="color:{'#FF3D71' if summary['impact']=='HIGH' else '#00E1FF'}">{summary['impact']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Sensitivitas Pasar</span><span class="av-report-v">{summary['sensitivity']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Cakrawala Dampak</span><span class="av-report-v">{summary['horizon']}</span></div>

        <div class="av-report-section-title">MATRIKS DAMPAK LINTAS ASET</div>
        {assets_html}

        <div class="av-report-section-title">KERANGKA MAKROEKONOMI</div>
        <div class="av-report-row"><span class="av-report-k">Tema Kebijakan</span><span class="av-report-v">{summary['macro_theme']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Bank Sentral</span><span class="av-report-v">{summary['central_bank']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Outlook Kebijakan</span><span class="av-report-v">{summary['policy_outlook']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Lingkungan Yield</span><span class="av-report-v">{summary['yield_env']}</span></div>
        <div class="av-report-row"><span class="av-report-k">Lingkungan Risiko</span><span class="av-report-v" style="color:{'#FF3D71' if summary['risk_env']=='RISK-OFF' else '#00E1FF'}">{summary['risk_env']}</span></div>

        <div class="av-report-section-title">MODEL SENTIMEN PASAR</div>
        <div class="av-report-row"><span class="av-report-k">Probabilitas Bullish</span><span class="av-report-v buy">{summary['bullish_pct']:.0f}%</span></div>
        <div class="av-report-row"><span class="av-report-k">Probabilitas Bearish</span><span class="av-report-v sell">{summary['bearish_pct']:.0f}%</span></div>
        <div class="av-report-row"><span class="av-report-k">Bias Institusional</span><span class="av-report-v {bull_cls}">{summary['institutional_bias']}</span></div>

        <div class="av-report-section-title">INTERPRETASI AI</div>
        <div class="av-report-narrative">{narrative_html}</div>

        <div class="av-report-section-title" style="margin-top:18px;font-size:7px;color:#2A3A5A">DISCLAIMER</div>
        <div style="font-size:8px;color:#3A4A60;line-height:1.7">
          Laporan ini dihasilkan menggunakan agregasi berita multi-sumber otomatis, verifikasi
          lintas-sumber, klasifikasi makroekonomi, pemodelan sentimen, dan interpretasi berbasis
          kecerdasan buatan. Seluruh kesimpulan bersifat probabilistik dan bukan jaminan hasil
          pasar di masa depan.
        </div>

      </div>
    </div>
    """
    # Strip indentasi tiap baris — mencegah Markdown mendeteksinya sebagai code block
    html = "\n".join(line.strip() for line in html.split("\n"))
    return html

# ══════════════════════════════════════════════════════════════════════════════════════════════
# END OF AEROVULPIS INTELLIGENCE PIPELINE
# ══════════════════════════════════════════════════════════════════════════════════════════════

# ==============================================================================
# BRAND
# ==============================================================================
st.markdown("""
<div class="av-brand-wrap">
  <div class="av-brand-line">
    <span class="av-prefix">SYS</span>
    <span class="av-title">AERO<span class="acc">VULPIS</span>&nbsp;TERMINAL</span>
    <span class="av-ver">v4.1</span>
  </div>
  <div class="av-tagline">QUANTITATIVE MARKET INTELLIGENCE SYSTEM · PROTOTYPE BUILD</div>
</div>
""", unsafe_allow_html=True)

# Ticker tape — zero gap ke brand dan selector
components.html(tv_ticker_tape(), height=46, scrolling=False)

# Selector bar — langsung setelah ticker
sc1, sc2, sc3 = st.columns([1.4, 1.4, 1.1])

with sc1:
    instr_class = av_select("INSTRUMENT", "sel_instr", list(INSTRUMENTS.keys()), st.session_state.instr_class)
    if instr_class != st.session_state.instr_class:
        st.session_state.instr_class = instr_class
        st.session_state.pair_label = INSTRUMENTS[instr_class][0][0]
        st.rerun()

pairs       = INSTRUMENTS[st.session_state.instr_class]
pair_labels = [p[0] for p in pairs]

with sc2:
    pair_label = av_select("PAIR", "sel_pair", pair_labels, st.session_state.pair_label)
    if pair_label != st.session_state.pair_label:
        st.session_state.pair_label = pair_label
        st.rerun()

with sc3:
    timeframe = av_select("TIMEFRAME", "sel_tf", TIMEFRAMES, st.session_state.timeframe)
    if timeframe != st.session_state.timeframe:
        st.session_state.timeframe = timeframe
        st.rerun()

# Resolve active pair
active_pair  = next(p for p in pairs if p[0] == st.session_state.pair_label)
active_label = active_pair[0]
active_td    = active_pair[1]   # Twelve Data symbol
active_tv    = active_pair[2]   # TradingView symbol
tf           = st.session_state.timeframe

# ==============================================================================
# ROW 1 — MCT + MARKET OVERVIEW
# ==============================================================================
st.markdown('<div class="av-sec">// MARKET INTELLIGENCE LAYER</div>', unsafe_allow_html=True)
mct_col, ov_col = st.columns([1.1, 1])

with mct_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
      <div style="font-size:11px;font-weight:700;letter-spacing:2px;color:#00E1FF;
                  font-family:'Share Tech Mono',monospace;
                  text-shadow:0 0 10px rgba(0,225,255,0.5);">
        MARKET CORE THERMOMETER
      </div>
      <div style="font-size:9px;color:#3A5070;letter-spacing:1px;
                  font-family:'Share Tech Mono',monospace;margin-top:2px">
        RSI · MACD · VOLUME
      </div>
    </div>""", unsafe_allow_html=True)

    # Fetch per symbol+timeframe (cache key includes both)
    seed_str = f"{active_label}-{tf}"
    df = fetch_twelvedata(active_td, TD_INTERVAL[tf], outputsize=300)
    if df.empty:
        df = _make_dummy_df(seed_str)
        data_src = "SIMULATION MODE"
    else:
        data_src = "LIVE · TWELVE DATA"

    mct = calculate_mct(df)
    cur = mct["current"]
    clr = "#00E1FF" if cur >= 0 else "#FF3D71"
    sgn = "+" if cur >= 0 else ""

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
      <div style="font-size:8px;color:#2A3A5A;letter-spacing:1px;font-family:'Share Tech Mono',monospace">
        {data_src} · {active_label} · {tf}
      </div>
      <div style="font-size:24px;font-weight:700;color:{clr};font-family:'Share Tech Mono',monospace;line-height:1">
        {sgn}{cur:.2f}
      </div>
    </div>""", unsafe_allow_html=True)

    st.plotly_chart(render_mct(mct), use_container_width=True,
                    config={"displayModeBar":False, "scrollZoom":False,
                            "doubleClick":False, "showTips":False})
    st.markdown(factor_bars_html(mct), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with ov_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)
    components.html(tv_market_overview(), height=405, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 2 — MAIN CHART + (BANK SENTRAL atas, TECH GAUGE bawah)
# ==============================================================================
st.markdown(f'<div class="av-sec">// CHART CORE · {active_label} · {tf}</div>', unsafe_allow_html=True)

# ── Init indicator state ──
if "chart_indic" not in st.session_state:
    st.session_state.chart_indic = []   # max 2
if "show_indic_modal" not in st.session_state:
    st.session_state.show_indic_modal = False

INDIC_LIST = ["RSI","MACD","STOCHASTIC","VOLUME"]
INDIC_STUDY = {
    "RSI":        "RSI@tv-basicstudies",
    "MACD":       "MACD@tv-basicstudies",
    "STOCHASTIC": "Stochastic@tv-basicstudies",
    "VOLUME":     "Volume@tv-basicstudies",
}

ch_col, ga_col = st.columns([1.75, 1])

with ch_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)

    # ── Row kontrol: CHART TYPE + INDIKATOR AKTIF + TOMBOL + ──
    ctrl_l, ctrl_mid, ctrl_r = st.columns([1.2, 2, 0.5])

    with ctrl_l:
        cs_labels  = [s[0] for s in CHART_STYLES]
        cs_vals    = {s[0]: s[1] for s in CHART_STYLES}
        cur_cs_lbl = next((s[0] for s in CHART_STYLES if s[1]==st.session_state.chart_style), "LINE")
        chart_style_lbl = av_select("CHART TYPE", "sel_cs", cs_labels, cur_cs_lbl)
        chosen_style    = cs_vals[chart_style_lbl]
        if chosen_style != st.session_state.chart_style:
            st.session_state.chart_style = chosen_style
            st.rerun()

    with ctrl_mid:
        # Tampilkan indikator aktif sebagai pill yang bisa dihapus (X)
        active_indics = st.session_state.chart_indic
        if active_indics:
            pills_html = '<div style="display:flex;gap:5px;align-items:center;margin-top:18px;flex-wrap:wrap">'
            for ind in active_indics:
                pills_html += f"""
                <span style="background:rgba(0,225,255,0.1);border:1px solid rgba(0,225,255,0.4);
                             color:#00E1FF;font-family:\'Share Tech Mono\',monospace;
                             font-size:9px;letter-spacing:0.5px;padding:3px 8px;
                             border-radius:3px;white-space:nowrap">
                    {ind}
                </span>"""
            pills_html += '</div>'
            st.markdown(pills_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="margin-top:18px;font-size:8px;color:#2A3A5A;
                        font-family:'Share Tech Mono',monospace;letter-spacing:1px">
                NO INDICATOR ACTIVE
            </div>""", unsafe_allow_html=True)

    with ctrl_r:
        st.markdown('<div style="margin-top:14px">', unsafe_allow_html=True)
        if st.button("＋", key="btn_add_indic", help="Tambah indikator ke chart",
                     use_container_width=True):
            st.session_state.show_indic_modal = not st.session_state.show_indic_modal
        st.markdown('</div>', unsafe_allow_html=True)

    # ── MODAL POPUP INDIKATOR ──
    if st.session_state.show_indic_modal:
        st.markdown("""
        <div style="background:#07101C;border:1px solid rgba(0,225,255,0.3);
                    border-radius:8px;padding:14px;margin:6px 0;
                    box-shadow:0 0 20px rgba(0,225,255,0.1);position:relative">
          <div style="font-size:9px;letter-spacing:2px;color:#00E1FF;
                      font-family:'Share Tech Mono',monospace;margin-bottom:10px;
                      text-shadow:0 0 8px rgba(0,225,255,0.4)">
            ◈ TAMBAH INDIKATOR KE GRAFIK
          </div>
          <div style="font-size:8px;color:#4A6080;font-family:'Share Tech Mono',monospace;
                      margin-bottom:10px;line-height:1.6">
            Pilih maks. 2 indikator · Klik nama untuk buka dokumentasi TradingView
          </div>
        </div>""", unsafe_allow_html=True)

        ic = st.columns(len(INDIC_LIST))
        for col_i, ind in zip(ic, INDIC_LIST):
            with col_i:
                is_on    = ind in st.session_state.chart_indic
                can_add  = len(st.session_state.chart_indic) < 2
                btn_lbl  = f"✓ {ind}" if is_on else ind
                if is_on:
                    if st.button(btn_lbl, key=f"indic_{ind}", use_container_width=True):
                        st.session_state.chart_indic.remove(ind)
                        st.rerun()
                elif can_add:
                    if st.button(btn_lbl, key=f"indic_{ind}", use_container_width=True):
                        st.session_state.chart_indic.append(ind)
                        st.session_state.show_indic_modal = False
                        st.rerun()
                else:
                    st.markdown(f"""
                    <div style="background:#07101C;border:1px solid #1A2238;
                                color:#2A3A5A;font-family:'Share Tech Mono',monospace;
                                font-size:9px;padding:6px;border-radius:4px;
                                text-align:center">
                        {ind}
                    </div>""", unsafe_allow_html=True)

        # Tombol clear semua + tutup modal
        cl1, cl2, _ = st.columns([0.8, 0.8, 3])
        with cl1:
            if st.button("✕ CLEAR", key="btn_clear_indic", use_container_width=True):
                st.session_state.chart_indic = []
                st.session_state.show_indic_modal = False
                st.rerun()
        with cl2:
            if st.button("TUTUP", key="btn_close_modal", use_container_width=True):
                st.session_state.show_indic_modal = False
                st.rerun()

    # ── Main Chart dengan studies dari pilihan user ──
    active_studies = [INDIC_STUDY[i] for i in st.session_state.chart_indic]
    components.html(
        tv_advanced_chart(active_tv, tf, st.session_state.chart_style, active_studies),
        height=520, scrolling=False,
    )
    st.markdown('</div>', unsafe_allow_html=True)

with ga_col:
    # ── Panel atas: Bunga Bank Sentral (iframe seputarforex) ──
    st.markdown("""
    <div class="av-panel" style="padding:10px;margin-bottom:6px">
      <div style="font-size:8px;letter-spacing:2px;color:#00E1FF;
                  font-family:'Share Tech Mono',monospace;margin-bottom:6px;
                  text-shadow:0 0 8px rgba(0,225,255,0.4)">
        ◈ BUNGA BANK SENTRAL
      </div>
      <style>
        .bank-table-wrap iframe {
            filter: invert(1) hue-rotate(180deg) brightness(0.85) saturate(1.2);
            border-radius:4px;
        }
      </style>
      <div class="bank-table-wrap">
        <iframe src="https://www.seputarforex.org/widget/bank_central_interest.php"
          width="100%" height="220" frameborder="0" scrolling="no"
          style="overflow:hidden;border-radius:4px;">
        </iframe>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Panel bawah: Technical Analysis Gauge ──
    st.markdown('<div class="av-panel" style="padding-top:6px">', unsafe_allow_html=True)
    components.html(tv_tech_gauge(active_tv, tf), height=370, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 3 — MINI CHARTS × 3 (filter sesuai instrumen aktif)
# ==============================================================================
st.markdown('<div class="av-sec">// MULTI-PAIR MONITOR</div>', unsafe_allow_html=True)

# Ambil options sesuai instrumen yang dipilih user
active_mini_opts  = MINI_OPTIONS[st.session_state.instr_class]
active_mini_labels = [m[0] for m in active_mini_opts]
active_mini_map    = {m[0]: m[1] for m in active_mini_opts}

# Reset mini state jika instrumen berubah dan nilai lama tidak ada di list baru
for sk, default_idx in [("mini_a", 0), ("mini_b", 1), ("mini_c", 2)]:
    cur = st.session_state.get(sk, active_mini_labels[default_idx])
    if cur not in active_mini_labels:
        st.session_state[sk] = active_mini_labels[min(default_idx, len(active_mini_labels)-1)]

m1, m2, m3 = st.columns(3)

for col, state_key, sel_key, def_idx in [
    (m1, "mini_a", "sel_ma", 0),
    (m2, "mini_b", "sel_mb", 1),
    (m3, "mini_c", "sel_mc", 2),
]:
    with col:
        st.markdown('<div class="av-panel">', unsafe_allow_html=True)
        cur_val = st.session_state.get(state_key, active_mini_labels[def_idx])
        if cur_val not in active_mini_labels:
            cur_val = active_mini_labels[def_idx]
        chosen = av_select("", sel_key, active_mini_labels, cur_val)
        if chosen != st.session_state.get(state_key):
            st.session_state[state_key] = chosen
            st.rerun()
        components.html(tv_mini_chart(active_mini_map[chosen]), height=215, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 4 — ECONOMIC CALENDAR + SCREENER
# ==============================================================================
st.markdown('<div class="av-sec">// FUNDAMENTAL DATA · PENYARING</div>', unsafe_allow_html=True)
ec_col, sc_col = st.columns(2)
with ec_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)
    components.html(tv_econ_calendar(), height=445, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)
with sc_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)
    components.html(tv_screener(), height=445, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 5 — AI ANALYSIS (Pipeline Institusional: Python menghitung, AI menerjemahkan)
# ==============================================================================
st.markdown('<div class="av-sec">// AI INTELLIGENCE ENGINE</div>', unsafe_allow_html=True)
st.markdown('<div class="av-panel">', unsafe_allow_html=True)

# Tombol mode berdekatan di satu row — kolom diperlebar agar teks tidak wrap
btn_row_l, btn_row_r, _ = st.columns([1.3, 1.3, 2.4])
with btn_row_l:
    if st.button("◈ ANALISIS PAIR", key="btn_pair", use_container_width=True):
        st.session_state.ai_mode = "pair"
        st.session_state.ai_result = None
with btn_row_r:
    if st.button("◈ ANALISIS NEWS", key="btn_news", use_container_width=True):
        st.session_state.ai_mode = "news"
        st.session_state.ai_result = None

# Mode indicator
mode_color = "#00E1FF" if st.session_state.ai_mode == "pair" else "#A855F7"
mode_label = "PAIR MODE — TEKNIKAL & SMC" if st.session_state.ai_mode == "pair" else "NEWS MODE — FUNDAMENTAL & SENTIMEN"
st.markdown(f"""
<div style="font-size:8px;letter-spacing:1px;color:{mode_color};
            font-family:'Share Tech Mono',monospace;margin:4px 0 8px;
            border-left:2px solid {mode_color};padding-left:8px">
    {mode_label}
</div>""", unsafe_allow_html=True)

if st.session_state.ai_mode == "news":
    # ── ANALISIS NEWS: kolom input topik singkat, maksimal 30 karakter ──
    ni, nr = st.columns([5, 1])
    with ni:
        news_text = st.text_input(
            "n", placeholder="TOPIK BERITA (MAKS 30 HURUF)...",
            key="news_inp", max_chars=30,
        )
    with nr:
        run_news_clicked = st.button("RUN", key="btn_run_n")

    if run_news_clicked and news_text.strip():
        with st.spinner("◈ Menyisir jaringan sumber intelijen pasar global..."):
            news_summary = run_news_pipeline(news_text.strip())
            narrative = ai_interpret_news(news_summary, news_summary.get("sample_titles"))
            st.session_state.ai_result = render_news_report(news_summary, narrative)
    elif run_news_clicked and not news_text.strip():
        st.markdown(
            '<div style="font-size:9px;color:#FF3D71;font-family:\'Share Tech Mono\',monospace;margin-top:4px">'
            'Masukkan topik berita terlebih dahulu.</div>', unsafe_allow_html=True
        )

else:
    # ── ANALISIS PAIR: TIDAK ADA kolom input, langsung pakai pair aktif dari selector atas ──
    st.markdown(f"""
    <div style="font-size:9px;color:#4A6080;font-family:'Share Tech Mono',monospace;
                margin-bottom:8px">
        Instrumen aktif: <span style="color:#00E1FF;font-weight:700">{active_label}</span>
        · Timeframe <span style="color:#00E1FF;font-weight:700">{tf}</span>
        — diambil otomatis dari selector di atas.
    </div>""", unsafe_allow_html=True)

    rc, _ = st.columns([0.7, 5])
    with rc:
        run_pair_clicked = st.button("RUN", key="btn_run_p")

    if run_pair_clicked:
        with st.spinner("◈ Memindai struktur pasar & menghitung model kuantitatif..."):
            pair_df = fetch_twelvedata(active_td, TD_INTERVAL[tf], outputsize=300)
            if pair_df.empty:
                pair_df = _make_dummy_df(f"{active_label}-{tf}")

            m_data  = market_data_engine(pair_df, active_label, tf)
            q_data  = quantitative_engine(pair_df)
            i_data  = institutional_engine(pair_df)
            r_data  = risk_engine(m_data, q_data, i_data, active_label)
            s_data  = scoring_engine(q_data, i_data, r_data)
            narrative = ai_interpret_pair(m_data, q_data, i_data, r_data, s_data)

            st.session_state.ai_result = render_pair_report(
                m_data, q_data, i_data, r_data, s_data, narrative, active_label
            )

if st.session_state.ai_result:
    st.markdown(st.session_state.ai_result, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 6 — ACTIVE TRADE SIGNALS
# ==============================================================================
st.markdown('<div class="av-sec">// ACTIVE TRADE SIGNALS</div>', unsafe_allow_html=True)
st.markdown('<div class="av-panel">', unsafe_allow_html=True)
tc = st.columns(len(DUMMY_TRADES))
for col, t in zip(tc, DUMMY_TRADES):
    with col:
        buy  = t["dir"] == "BUY"
        dc   = "av-dir-buy" if buy else "av-dir-sell"
        rows = "".join([
            f'<div class="av-trade-row"><span class="av-trade-k">{k}</span>'
            f'<span style="color:{c};font-size:11px;font-weight:{700 if k!="ENTRY" else 400}">{t[vk]}</span></div>'
            for k,vk,c in [("ENTRY","entry","#8BA0C0"),("SL","sl","#FF3D71"),
                ("TP1","tp1","#00E1FF"),("TP2","tp2","#00B8CC"),("TP3","tp3","#0090A0")]
        ])
        st.markdown(f"""<div class="av-trade-card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <span class="av-trade-symbol">{t['symbol']}</span>
            <span class="{dc}">{t['dir']}</span>
          </div>{rows}</div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 7 — TOP STORIES
# ==============================================================================
st.markdown('<div class="av-sec">// MARKET INTELLIGENCE · NEWS FEED</div>', unsafe_allow_html=True)
st.markdown('<div class="av-panel">', unsafe_allow_html=True)
components.html(tv_top_stories(), height=475, scrolling=False)
st.markdown('</div>', unsafe_allow_html=True)
