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

/* ── BRAND ── */
.av-brand-wrap { padding:12px 0 0; }
.av-brand-line { display:flex; align-items:baseline; gap:10px; }
.av-prefix {
    font-size:8px; letter-spacing:3px; color:#1A3A5A;
    border:1px solid #1A3A5A; padding:2px 7px; border-radius:2px;
}
.av-title {
    font-size:20px; letter-spacing:4px; color:#E8F1FF;
    font-weight:700; font-family:'Share Tech Mono',monospace;
}
.av-title .acc { color:#00E1FF; }
.av-ver { font-size:8px; letter-spacing:2px; color:#2A4060; }
.av-tagline { font-size:8px; letter-spacing:2.5px; color:#1A3A5A; margin-top:2px; }

/* ── SECTION LABEL ── */
.av-sec {
    font-size:8px; letter-spacing:2.5px; color:#1A3060;
    padding:8px 0 4px; font-family:'Share Tech Mono',monospace;
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

/* ── RADIO → neon cyan pill buttons, NO text input possible ── */
[data-testid="stRadio"] label { display:none !important; }
[data-testid="stRadio"] > div {
    display:flex !important;
    flex-direction:row !important;
    flex-wrap:wrap !important;
    gap:5px !important;
}
[data-testid="stRadio"] > div > label {
    display:flex !important;
    align-items:center !important;
    background:#09111E !important;
    border:1px solid #1A3A5A !important;
    border-radius:5px !important;
    padding:6px 13px !important;
    cursor:pointer !important;
    font-family:'Share Tech Mono',monospace !important;
    font-size:10px !important;
    letter-spacing:1px !important;
    color:#5A7898 !important;
    transition:all 0.15s ease !important;
    white-space:nowrap !important;
}
[data-testid="stRadio"] > div > label:hover {
    border-color:rgba(0,225,255,0.6) !important;
    color:#00E1FF !important;
    background:rgba(0,225,255,0.06) !important;
}
/* Hide the actual radio circle */
[data-testid="stRadio"] > div > label > div:first-child {
    display:none !important;
}
/* Active/selected pill */
[data-testid="stRadio"] > div > label[data-checked="true"],
[data-testid="stRadio"] > div > label:has(input:checked) {
    border-color:#00E1FF !important;
    color:#00E1FF !important;
    background:rgba(0,225,255,0.10) !important;
    box-shadow:0 0 10px rgba(0,225,255,0.25),inset 0 0 8px rgba(0,225,255,0.05) !important;
}
[data-testid="stRadio"] input[type="radio"] {
    display:none !important;
}

/* ── SELECTOR LABEL above radio ── */
.av-sel-label {
    font-size:8px; letter-spacing:1.5px; color:#2A4060;
    margin-bottom:3px; font-family:'Share Tech Mono',monospace;
}

/* ── BUTTONS (AI, etc) ── */
[data-testid="stButton"] > button {
    background:linear-gradient(135deg,rgba(0,225,255,0.85),rgba(168,85,247,0.85)) !important;
    color:#030608 !important; font-weight:700 !important;
    font-family:'Share Tech Mono',monospace !important;
    font-size:10px !important; letter-spacing:1.5px !important;
    border:none !important; border-radius:5px !important;
    padding:8px 18px !important;
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

# Mini chart options — DXY pakai CAPITALCOM, Oil pakai CAPITALCOM
MINI_OPTIONS = [
    ("EURUSD","OANDA:EURUSD"),
    ("GBPUSD","OANDA:GBPUSD"),
    ("USDJPY","OANDA:USDJPY"),
    ("AUDUSD","OANDA:AUDUSD"),
    ("XAUUSD","OANDA:XAUUSD"),
    ("BTCUSD","COINBASE:BTCUSD"),
    ("NVDA",  "NASDAQ:NVDA"),
    ("USDCHF","OANDA:USDCHF"),
    ("DXY",   "CAPITALCOM:DXY"),
    ("US10Y", "TVC:US10Y"),
    ("OIL",   "CAPITALCOM:OIL_CRUDE"),
    ("AAPL",  "NASDAQ:AAPL"),
]

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
    return pd.DataFrame({
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
            {"proName":"FX:EURUSD","title":"EUR/USD"},
            {"proName":"FX:GBPUSD","title":"GBP/USD"},
            {"proName":"FX:USDJPY","title":"USD/JPY"},
            {"proName":"FX:AUDUSD","title":"AUD/USD"},
            {"proName":"FX:USDCHF","title":"USD/CHF"},
            {"proName":"OANDA:XAUUSD","title":"XAU/USD"},
            {"proName":"TVC:DXY","title":"DXY"},
            {"proName":"TVC:US10Y","title":"US10Y"},
            {"proName":"COINBASE:BTCUSD","title":"BTC/USD"},
            {"proName":"COINBASE:ETHUSD","title":"ETH/USD"},
            {"proName":"NASDAQ:NVDA","title":"NVDA"},
            {"proName":"FOREXCOM:SPXUSD","title":"S&P 500"},
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


def tv_advanced_chart(symbol: str, interval: str, style: str) -> str:
    cfg = json.dumps({
        "autosize":True,"symbol":symbol,"interval":TV_INTERVAL[interval],
        "timezone":"Etc/UTC","theme":"dark","style":style,"locale":"en",
        "backgroundColor":"#070A12","gridColor":"rgba(42,53,80,0.3)",
        "hide_top_toolbar":False,"hide_legend":False,
        "allow_symbol_change":False,"save_image":False,
        "calendar":False,"support_host":"https://www.tradingview.com",
    })
    return f"""<!DOCTYPE html><html><head>
<style>*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{height:100%;background:#070A12;overflow:hidden}}</style>
</head><body>
<div class="tradingview-widget-container" style="height:430px;width:100%">
  <div class="tradingview-widget-container__widget" style="height:430px;width:100%"></div>
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
# HELPER: radio horizontal (tidak bisa diketik, murni klik)
# ==============================================================================
def av_radio(label_text: str, key: str, options: list, current: str) -> str:
    idx = options.index(current) if current in options else 0
    if label_text:
        st.markdown(f'<div class="av-sel-label">{label_text}</div>', unsafe_allow_html=True)
    chosen = st.radio("_", options, index=idx, key=key,
                      label_visibility="collapsed", horizontal=True)
    return chosen

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

# Ticker tape — tight, no gap
components.html(tv_ticker_tape(), height=58, scrolling=False)

# ==============================================================================
# SELECTOR BAR — dropdown style (judul saja, klik baru muncul pilihan)
# ==============================================================================
st.markdown('<div class="av-sec">// INSTRUMENT · PAIR · TIMEFRAME</div>', unsafe_allow_html=True)
sc1, sc2, sc3, sc4 = st.columns([1.4, 1.4, 1.1, 1.1])

with sc1:
    instr_class = av_radio("INSTRUMENT", "sel_instr", list(INSTRUMENTS.keys()), st.session_state.instr_class)
    if instr_class != st.session_state.instr_class:
        st.session_state.instr_class = instr_class
        # reset pair to first of new class
        st.session_state.pair_label = INSTRUMENTS[instr_class][0][0]
        st.rerun()

pairs       = INSTRUMENTS[st.session_state.instr_class]
pair_labels = [p[0] for p in pairs]

with sc2:
    pair_label = av_radio("PAIR", "sel_pair", pair_labels, st.session_state.pair_label)
    if pair_label != st.session_state.pair_label:
        st.session_state.pair_label = pair_label
        st.rerun()

with sc3:
    timeframe = av_radio("TIMEFRAME", "sel_tf", TIMEFRAMES, st.session_state.timeframe)
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
# ROW 2 — MAIN CHART + TECH GAUGE
# ==============================================================================
st.markdown(f'<div class="av-sec">// CHART CORE · {active_label} · {tf}</div>', unsafe_allow_html=True)
ch_col, ga_col = st.columns([1.45, 1])

with ch_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)
    cs_labels = [s[0] for s in CHART_STYLES]
    cs_vals   = {s[0]: s[1] for s in CHART_STYLES}
    cur_cs_lbl = next((s[0] for s in CHART_STYLES if s[1]==st.session_state.chart_style), "LINE")

    chart_style_lbl = av_radio("CHART TYPE", "sel_cs", cs_labels, cur_cs_lbl)
    chosen_style    = cs_vals[chart_style_lbl]
    if chosen_style != st.session_state.chart_style:
        st.session_state.chart_style = chosen_style
        st.rerun()

    # Chart keyed so Streamlit reloads the iframe when symbol/interval/style changes
    components.html(
        tv_advanced_chart(active_tv, tf, st.session_state.chart_style),
        height=445, scrolling=False,
    )
    st.markdown('</div>', unsafe_allow_html=True)

with ga_col:
    st.markdown('<div class="av-panel" style="padding-top:8px">', unsafe_allow_html=True)
    components.html(tv_tech_gauge(active_tv, tf), height=445, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 3 — MINI CHARTS × 3 (each with dropdown selector)
# ==============================================================================
st.markdown('<div class="av-sec">// MULTI-PAIR MONITOR</div>', unsafe_allow_html=True)
m1, m2, m3 = st.columns(3)
mini_labels = [m[0] for m in MINI_OPTIONS]
mini_tv_map = {m[0]: m[1] for m in MINI_OPTIONS}

for col, state_key, sel_key, default in [
    (m1, "mini_a", "sel_ma", "GBPUSD"),
    (m2, "mini_b", "sel_mb", "USDJPY"),
    (m3, "mini_c", "sel_mc", "AUDUSD"),
]:
    with col:
        st.markdown('<div class="av-panel">', unsafe_allow_html=True)
        chosen = av_radio("", sel_key, mini_labels, st.session_state.get(state_key, default))
        if chosen != st.session_state.get(state_key):
            st.session_state[state_key] = chosen
            st.rerun()
        components.html(tv_mini_chart(mini_tv_map[chosen]), height=215, scrolling=False)
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
# ROW 5 — AI ANALYSIS
# ==============================================================================
st.markdown('<div class="av-sec">// AI INTELLIGENCE ENGINE</div>', unsafe_allow_html=True)
st.markdown('<div class="av-panel">', unsafe_allow_html=True)

ai1, ai2, _ = st.columns([1,1,4])
with ai1:
    if st.button("ANALISIS PAIR", key="btn_pair"):
        st.session_state.ai_mode = "pair"
        st.session_state.ai_result = None
with ai2:
    if st.button("ANALISIS NEWS", key="btn_news"):
        st.session_state.ai_mode = "news"
        st.session_state.ai_result = None

if st.session_state.ai_mode == "news":
    ni, nr = st.columns([5,1])
    with ni:
        news_text = st.text_input("n", placeholder="PASTE HEADLINE / KONTEKS BERITA...", key="news_inp")
    with nr:
        st.markdown("<div style='margin-top:4px'></div>", unsafe_allow_html=True)
        if st.button("ANALISIS", key="btn_run_n") and news_text.strip():
            st.session_state.ai_result = (
                f"[PROTOTYPE] Dampak berita terhadap {active_label}: Sentimen risk-off meningkat. "
                f"Potensi volatilitas naik di sesi New York. "
                f"Pantau reaksi harga 30 menit pertama pasca rilis. "
                f"(Placeholder — akan diganti Claude API asli.)"
            )
else:
    rc, _ = st.columns([1,5])
    with rc:
        if st.button("ANALISIS", key="btn_run_p"):
            st.session_state.ai_result = (
                f"[PROTOTYPE] Analisis teknikal {active_label} · {tf}: "
                f"Bias bearish-netral jangka pendek. RSI ~42, MACD histogram menyempit. "
                f"EMA-20 di bawah EMA-50. ATR naik — volatilitas meningkat. "
                f"WAIT — konfirmasi bounce di S1 sebelum entry BUY. "
                f"(Placeholder — akan diganti Claude API asli.)"
            )

if st.session_state.ai_result:
    st.markdown(f'<div class="av-ai-result">{st.session_state.ai_result}</div>', unsafe_allow_html=True)
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