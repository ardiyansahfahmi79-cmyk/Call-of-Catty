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
    background: #070A12 !important;
    font-family: 'Share Tech Mono','Courier New',monospace !important;
    color: #C8D8F0 !important;
}
[data-testid="stSidebar"]        { display:none !important; }
[data-testid="collapsedControl"] { display:none !important; }
[data-testid="stDecoration"]     { display:none !important; }
[data-testid="stHeader"]         { background:transparent !important; height:0 !important; }
footer { display:none !important; }
#MainMenu { display:none !important; }

[data-testid="stMain"] {
    background: #070A12 !important;
    background-image:
        radial-gradient(ellipse 60% 35% at 10% 0%,rgba(0,225,255,0.05),transparent),
        radial-gradient(ellipse 50% 30% at 90% 5%,rgba(168,85,247,0.05),transparent) !important;
}

/* ── NO GAP ── */
div.block-container {
    padding: 0 1rem 1.5rem !important;
    max-width: 100% !important;
}
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }
[data-testid="column"] { padding: 0 4px !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { padding: 0 !important; }

/* ── BRAND ── */
.av-brand-wrap {
    padding: 14px 0 10px;
    border-bottom: 1px solid #111827;
    margin-bottom: 0;
}
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
.av-tagline { font-size:8px; letter-spacing:2.5px; color:#1A3A5A; margin-top:3px; }

/* ── TICKER (TV widget host) ── */
.av-ticker-host { border-top:1px solid #0E1422; margin-top:8px; }

/* ── SECTION LABEL ── */
.av-sec {
    font-size:8px; letter-spacing:2.5px; color:#1A3060;
    padding:10px 0 5px;
    font-family:'Share Tech Mono',monospace;
}

/* ── PANEL ── */
.av-panel {
    background:#09111E;
    border:1px solid #111827;
    border-radius:8px;
    padding:12px;
    position:relative;
    overflow:hidden;
    margin-bottom: 8px;
}
.av-panel::before {
    content:""; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,225,255,0.18),transparent);
}

/* ── CUSTOM SELECTOR BUTTONS (no typing!) ── */
.av-sel-wrap { display:flex; gap:0; margin-bottom:10px; flex-wrap:wrap; gap:6px; }
.av-sel-btn {
    background:#09111E;
    border:1px solid #1A2E4A;
    border-radius:5px;
    color:#6A90B0;
    font-family:'Share Tech Mono',monospace;
    font-size:10px;
    letter-spacing:1px;
    padding:7px 14px;
    cursor:pointer;
    transition: all 0.15s ease;
    white-space:nowrap;
    user-select:none;
}
.av-sel-btn:hover {
    border-color:rgba(0,225,255,0.5);
    color:#00E1FF;
    background:rgba(0,225,255,0.06);
}
.av-sel-btn.active {
    border-color:#00E1FF;
    color:#00E1FF;
    background:rgba(0,225,255,0.10);
    box-shadow: 0 0 10px rgba(0,225,255,0.25), inset 0 0 8px rgba(0,225,255,0.05);
}
.av-sel-label {
    font-size:8px; letter-spacing:1.5px; color:#2A4060;
    margin-bottom:5px; font-family:'Share Tech Mono',monospace;
}

/* ── STREAMLIT NATIVE SELECTBOX — hide (we use custom buttons) ── */
[data-testid="stSelectbox"] { display:none !important; }

/* ── TEXT INPUT ── */
[data-testid="stTextInput"] label { display:none !important; }
[data-testid="stTextInput"] input {
    background:#07101C !important; border:1px solid #1A2540 !important;
    border-radius:5px !important; color:#C8D8F0 !important;
    font-family:'Share Tech Mono',monospace !important; font-size:11px !important;
}
[data-testid="stTextInput"] input::placeholder { color:#2A3A54 !important; }

/* ── BUTTONS ── */
[data-testid="stButton"] > button {
    background:linear-gradient(135deg,rgba(0,225,255,0.85),rgba(168,85,247,0.85)) !important;
    color:#030608 !important; font-weight:700 !important;
    font-family:'Share Tech Mono',monospace !important;
    font-size:10px !important; letter-spacing:1.5px !important;
    border:none !important; border-radius:5px !important;
    padding:8px 18px !important;
}

/* ── AI RESULT ── */
.av-ai-result {
    background:#07101C; border:1px solid #1A2540;
    border-left:2px solid #00E1FF;
    padding:12px 14px; border-radius:5px;
    font-size:11px; line-height:1.7; color:#8BA0C0;
    letter-spacing:0.3px; font-family:'Share Tech Mono',monospace;
    margin-top:8px;
}

/* ── TRADE CARD ── */
.av-trade-card {
    background:#09111E; border:1px solid #111827;
    border-radius:8px; padding:12px;
    position:relative; overflow:hidden;
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
.av-trade-row {
    display:flex; justify-content:space-between; padding:3px 0;
    border-bottom:1px solid #0E1422; font-size:11px;
}
.av-trade-k { color:#3A4A6A; letter-spacing:1px; font-size:9px; }

/* ── MCT FACTOR BARS ── */
.av-factor-wrap { display:flex; gap:4px; margin-top:6px; }
.av-factor-item {
    flex:1; background:#0A0E18; border:1px solid #1A2238;
    border-radius:4px; padding:4px 6px;
}
.av-factor-k { font-size:7.5px; color:#4A6080; letter-spacing:1px; margin-bottom:2px; }
.av-factor-bar-wrap { height:2px; background:#0E1422; border-radius:1px; }
.av-factor-v { font-size:8px; margin-top:2px; text-align:right; }

/* ── PLOTLY modebar hide ── */
.js-plotly-plot .plotly .modebar { display:none !important; }

/* ── REMOVE STREAMLIT GAPS ── */
.stMarkdown { margin:0 !important; padding:0 !important; }
div[data-testid="stHorizontalBlock"] { gap:8px !important; }
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

TIMEFRAMES   = ["15m","30m","1h","4h","1D"]
TV_INTERVAL  = {"15m":"15","30m":"30","1h":"60","4h":"240","1D":"D"}
TV_TA_INT    = {"15m":"15m","30m":"30m","1h":"1h","4h":"4h","1D":"1D"}
TD_INTERVAL  = {"15m":"15min","30m":"30min","1h":"1h","4h":"4h","1D":"1day"}

CHART_STYLES = [("LINE","3"),("CANDLES","1"),("HEIKIN","8"),("AREA","9"),("BARS","0")]

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

# ==============================================================================
# SESSION STATE
# ==============================================================================
def _init():
    d = {
        "instr_class":"FOREX","pair_idx":0,"timeframe":"15m",
        "chart_style":"3","mini_a":1,"mini_b":2,"mini_c":3,
        "ai_mode":"pair","ai_result":None,
    }
    for k,v in d.items():
        if k not in st.session_state:
            st.session_state[k] = v
_init()

# ==============================================================================
# MCT ENGINE — RSI + MACD + Volume (simplified, clean)
# ==============================================================================
@st.cache_data(ttl=60, show_spinner=False)
def fetch_twelvedata(symbol:str, interval:str, outputsize:int=300) -> pd.DataFrame:
    try:
        api_key = st.secrets["TWELVE_DATA_API_KEY"]
    except Exception:
        return pd.DataFrame()
    url = (f"https://api.twelvedata.com/time_series"
           f"?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={api_key}")
    try:
        r = requests.get(url, timeout=10).json()
        if r.get("status") == "error" or "values" not in r:
            return pd.DataFrame()
        df = pd.DataFrame(r["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        for c in ["open","high","low","close"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["volume"] = pd.to_numeric(df.get("volume",0), errors="coerce").fillna(0)
        df = df.sort_values("datetime").reset_index(drop=True)
        df.set_index("datetime", inplace=True)
        return df
    except Exception:
        return pd.DataFrame()


def calculate_mct_simple(df: pd.DataFrame) -> np.ndarray:
    """
    MCT: RSI (40%) + MACD Histogram (40%) + Volume MA (20%)
    Z-score normalized, Savitzky-Golay smoothed.
    Simple, clean, like a proper oscillator.
    """
    lookback = 63

    def z_norm(s: pd.Series) -> pd.Series:
        rm  = s.rolling(lookback, min_periods=10).mean()
        rs  = s.rolling(lookback, min_periods=10).std().replace(0, np.nan)
        return ((s - rm) / rs).clip(-3, 3) / 3.0

    close  = df["close"]
    volume = df["volume"] if "volume" in df.columns else pd.Series(np.ones(len(df)), index=df.index)

    # RSI centered at 0
    rsi_raw = ta.rsi(close, length=14).fillna(50) - 50.0
    z_rsi   = z_norm(rsi_raw)

    # MACD histogram
    macd_df  = ta.macd(close, fast=12, slow=26, signal=9)
    z_macd   = z_norm(macd_df["MACDh_12_26_9"].fillna(0))

    # Volume momentum (volume vs its MA — measures buying/selling pressure)
    vol_ma   = volume.rolling(20, min_periods=5).mean().replace(0, np.nan)
    vol_mom  = ((volume / vol_ma) - 1.0).fillna(0).clip(-2, 2)
    z_vol    = z_norm(vol_mom)

    # Weighted composite
    composite = (0.40 * z_rsi) + (0.40 * z_macd) + (0.20 * z_vol)
    raw = (composite * 100).clip(-100, 100).fillna(0).to_numpy()

    # Savitzky-Golay smooth
    n  = len(raw)
    wl = min(25, n)
    if wl % 2 == 0: wl -= 1
    wl = max(wl, 5)
    smoothed = savgol_filter(raw, window_length=wl, polyorder=3, mode="interp")
    return np.clip(smoothed, -100, 100)


def render_mct_plotly(values: np.ndarray) -> go.Figure:
    x    = list(range(len(values)))
    y_up = np.where(values >= 0, values, np.nan)
    y_dn = np.where(values <= 0, values, np.nan)

    current  = float(values[-1])
    prev     = float(values[max(0, len(values)-6)])
    momentum = current - prev
    isBull   = current >= 0

    if   current >  60: regime = "STRONG BULL"
    elif current >  25: regime = "BULL"
    elif current < -60: regime = "STRONG BEAR"
    elif current < -25: regime = "BEAR"
    else:               regime = "NEUTRAL"

    fig = go.Figure()

    # OB/OS shading
    fig.add_hrect(y0=30,  y1=80,  fillcolor="rgba(0,225,255,0.04)",  line_width=0)
    fig.add_hrect(y0=-80, y1=-30, fillcolor="rgba(255,61,113,0.04)", line_width=0)

    # Bullish fill + line
    fig.add_trace(go.Scatter(
        x=x, y=y_up, fill="tozeroy",
        fillcolor="rgba(0,225,255,0.13)",
        line=dict(color="#00E1FF", width=2.5),
        mode="lines", showlegend=False, hovertemplate="%{y:.1f}<extra></extra>",
    ))
    # Bearish fill + line
    fig.add_trace(go.Scatter(
        x=x, y=y_dn, fill="tozeroy",
        fillcolor="rgba(255,61,113,0.13)",
        line=dict(color="#FF3D71", width=2.5),
        mode="lines", showlegend=False, hovertemplate="%{y:.1f}<extra></extra>",
    ))
    # Live dot
    dot_c = "#00E1FF" if isBull else "#FF3D71"
    fig.add_trace(go.Scatter(
        x=[x[-1]], y=[current], mode="markers",
        marker=dict(color=dot_c, size=9, line=dict(color="#070A12",width=2)),
        showlegend=False, hoverinfo="skip",
    ))

    # Grid lines + zone labels
    for lvl, lbl in [(80,"OB EXTREME"),(30,"OB ZONE"),(0,None),(-30,"OS ZONE"),(-80,"OS EXTREME")]:
        col  = "rgba(255,255,255,0.5)" if lvl==0 else "rgba(42,53,80,0.85)"
        dash = "solid" if lvl==0 else "dot"
        lw   = 1.2 if lvl==0 else 0.7
        fig.add_hline(y=lvl, line_color=col, line_width=lw, line_dash=dash)
        if lbl:
            fc = "rgba(0,225,255,0.5)" if lvl>0 else "rgba(255,61,113,0.5)"
            fig.add_annotation(
                x=0, y=lvl, xref="paper",
                text=f"  {lbl}", showarrow=False,
                font=dict(size=7, color=fc, family="Share Tech Mono,monospace"),
                xanchor="left", yanchor="bottom",
            )

    # Regime top-right
    sym = "▲" if momentum>=0 else "▼"
    fig.add_annotation(
        x=1, y=0.98, xref="paper", yref="paper",
        text=f"{regime}  {sym}{abs(momentum):.1f}",
        showarrow=False,
        font=dict(size=9, color=dot_c, family="Share Tech Mono,monospace"),
        xanchor="right", yanchor="top",
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=230, margin=dict(l=8,r=52,t=8,b=8),
        xaxis=dict(visible=False, showgrid=False),
        yaxis=dict(
            range=[-100,100], showgrid=False, zeroline=False,
            tickvals=[-80,-30,0,30,80],
            tickfont=dict(color="#3A4A6A",size=9,family="Share Tech Mono,monospace"),
            side="right",
        ),
    )
    return fig


def factor_bars_html(current: float, seed_str: str) -> str:
    rng = np.random.default_rng(abs(hash(seed_str)) % 2**32)
    factors = [
        ("RSI",   current*0.95 + rng.uniform(-5,5)),
        ("MACD",  current*0.90 + rng.uniform(-8,8)),
        ("VOL",   current*0.70 + rng.uniform(-15,15)),
    ]
    items = ""
    for k,v in factors:
        v   = float(np.clip(v,-100,100))
        c   = "#00E1FF" if v>=0 else "#FF3D71"
        sgn = "+" if v>=0 else ""
        ml  = f"margin-left:{100-abs(v):.0f}%" if v<0 else ""
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
def tv_html(src:str, cfg:dict, h:int) -> str:
    cj = json.dumps(cfg)
    return f"""<!DOCTYPE html><html><head>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{background:transparent;overflow:hidden}}</style>
</head><body>
<div class="tradingview-widget-container" style="width:100%;height:{h}px">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="{src}" async>{cj}</script>
</div></body></html>"""


def tv_ticker_tape() -> str:
    """TradingView Ticker Tape — scrolls right to left automatically."""
    cfg = {
        "symbols":[
            {"proName":"FX:EURUSD","title":"EUR/USD"},
            {"proName":"FX:GBPUSD","title":"GBP/USD"},
            {"proName":"FX:USDJPY","title":"USD/JPY"},
            {"proName":"FX:AUDUSD","title":"AUD/USD"},
            {"proName":"FX:USDCHF","title":"USD/CHF"},
            {"proName":"OANDA:XAUUSD","title":"XAU/USD"},
            {"proName":"COINBASE:BTCUSD","title":"BTC/USD"},
            {"proName":"COINBASE:ETHUSD","title":"ETH/USD"},
            {"proName":"NASDAQ:NVDA","title":"NVDA"},
            {"proName":"NASDAQ:AAPL","title":"AAPL"},
            {"proName":"FOREXCOM:SPXUSD","title":"S&P 500"},
        ],
        "showSymbolLogo":True,
        "isTransparent":True,
        "displayMode":"adaptive",
        "colorTheme":"dark",
        "locale":"en",
    }
    return tv_html(
        "https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js",
        cfg, 56
    )


def tv_market_overview() -> str:
    cfg = {
        "colorTheme":"dark","dateRange":"3M","locale":"en","isTransparent":True,
        "plotLineColorGrowing":"rgba(0,225,255,1)",
        "plotLineColorFalling":"rgba(255,61,113,1)",
        "gridLineColor":"rgba(42,53,80,0)","scaleFontColor":"#4A6080",
        "belowLineFillColorGrowing":"rgba(0,225,255,0.10)",
        "belowLineFillColorFalling":"rgba(255,61,113,0.10)",
        "belowLineFillColorGrowingBottom":"rgba(0,225,255,0)",
        "belowLineFillColorFallingBottom":"rgba(255,61,113,0)",
        "symbolActiveColor":"rgba(0,225,255,0.10)",
        "backgroundColor":"#09111E",
        "tabs":[
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
        "width":"100%","height":"390","showSymbolLogo":True,"showChart":True,
    }
    return tv_html("https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js",cfg,390)


def tv_advanced_chart(symbol:str, interval:str, style:str) -> str:
    cfg = {
        "autosize":True,"symbol":symbol,
        "interval":TV_INTERVAL[interval],
        "timezone":"Etc/UTC","theme":"dark","style":style,"locale":"en",
        "backgroundColor":"#070A12",
        "gridColor":"rgba(42,53,80,0.3)",
        "hide_top_toolbar":False,"hide_legend":False,
        "allow_symbol_change":False,"save_image":False,
        "calendar":False,"support_host":"https://www.tradingview.com",
    }
    cj = json.dumps(cfg)
    # Advanced chart needs autosize container
    return f"""<!DOCTYPE html><html><head>
<style>*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{height:100%;background:#070A12;overflow:hidden}}
.tv-wrap{{height:420px;width:100%}}
</style></head><body>
<div class="tradingview-widget-container tv-wrap">
  <div class="tradingview-widget-container__widget" style="height:420px;width:100%"></div>
  <script type="text/javascript"
    src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
  {cj}</script>
</div></body></html>"""


def tv_tech_gauge(symbol:str, interval:str) -> str:
    cfg = {
        "colorTheme":"dark","displayMode":"single","isTransparent":True,
        "locale":"en","interval":TV_TA_INT[interval],
        "width":"100%","height":"360","symbol":symbol,"showIntervalTabs":True,
    }
    return tv_html("https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js",cfg,360)


def tv_mini_chart(symbol:str) -> str:
    cfg = {
        "symbol":symbol,"width":"100%","height":200,"locale":"en",
        "dateRange":"1M","colorTheme":"dark","isTransparent":True,
        "autosize":True,"largeChartUrl":"","chartOnly":False,
    }
    return tv_html("https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js",cfg,200)


def tv_econ_calendar() -> str:
    cfg = {
        "colorTheme":"dark","isTransparent":True,
        "width":"100%","height":"430","locale":"en",
        "importanceFilter":"0,1","countryFilter":"us,eu,gb,jp,au,ch,ca,cn",
    }
    return tv_html("https://s3.tradingview.com/external-embedding/embed-widget-events.js",cfg,430)


def tv_screener() -> str:
    cfg = {
        "market":"forex","showToolbar":True,"defaultColumn":"overview",
        "defaultScreen":"general","isTransparent":True,
        "locale":"en","colorTheme":"dark","width":"100%","height":"430",
    }
    return tv_html("https://s3.tradingview.com/external-embedding/embed-widget-screener.js",cfg,430)


def tv_top_stories() -> str:
    cfg = {
        "feedMode":"all_symbols","colorTheme":"dark","isTransparent":True,
        "displayMode":"regular","width":"100%","height":"460","locale":"en",
    }
    return tv_html("https://s3.tradingview.com/external-embedding/embed-widget-timeline.js",cfg,460)

# ==============================================================================
# CUSTOM SELECTOR HELPER (no typing, pure HTML buttons via query params)
# ==============================================================================
def sel_buttons(key:str, options:list, current:str, label:str="") -> str:
    """Render neon cyan button group. Selection handled via st.query_params."""
    btns = ""
    for opt in options:
        active = "active" if opt==current else ""
        btns += f'<button class="av-sel-btn {active}" onclick="window.location.href=\'?{key}={opt}\'">{opt}</button>'
    lbl = f'<div class="av-sel-label">{label}</div>' if label else ""
    return f'{lbl}<div class="av-sel-wrap">{btns}</div>'

# ==============================================================================
# READ QUERY PARAMS → update session state
# ==============================================================================
qp = st.query_params

def qp_get(key:str, default:str) -> str:
    return qp.get(key, default)

instr_class = qp_get("instr", st.session_state.instr_class)
if instr_class not in INSTRUMENTS:
    instr_class = "FOREX"
st.session_state.instr_class = instr_class

pairs       = INSTRUMENTS[instr_class]
pair_labels = [p[0] for p in pairs]
pair_sel    = qp_get("pair", pairs[0][0])
if pair_sel not in pair_labels:
    pair_sel = pair_labels[0]
pair_idx    = pair_labels.index(pair_sel)
st.session_state.pair_idx = pair_idx

tf_sel = qp_get("tf", st.session_state.timeframe)
if tf_sel not in TIMEFRAMES:
    tf_sel = "15m"
st.session_state.timeframe = tf_sel

cs_sel = qp_get("cs", st.session_state.chart_style)
if cs_sel not in [s[1] for s in CHART_STYLES]:
    cs_sel = "3"
st.session_state.chart_style = cs_sel

ma_sel = int(qp_get("ma", str(st.session_state.mini_a)))
mb_sel = int(qp_get("mb", str(st.session_state.mini_b)))
mc_sel = int(qp_get("mc", str(st.session_state.mini_c)))
for v,k in [(ma_sel,"mini_a"),(mb_sel,"mini_b"),(mc_sel,"mini_c")]:
    if 0 <= v < len(MINI_OPTIONS):
        st.session_state[k] = v

active_pair      = pairs[pair_idx]
active_label     = active_pair[0]
active_td_symbol = active_pair[1]
active_tv_symbol = active_pair[2]

# ==============================================================================
# BRAND + TICKER TAPE
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

# TradingView Ticker Tape (scrolls right→left, live prices)
components.html(tv_ticker_tape(), height=60, scrolling=False)

# ==============================================================================
# SELECTOR BAR — custom HTML buttons (no text input!)
# ==============================================================================
st.markdown('<div class="av-sec">// INSTRUMENT · PAIR · TIMEFRAME</div>', unsafe_allow_html=True)

sel_c1, sel_c2, sel_c3 = st.columns([2.5, 2.5, 2])

with sel_c1:
    st.markdown(sel_buttons("instr", list(INSTRUMENTS.keys()), instr_class, "INSTRUMENT"), unsafe_allow_html=True)

with sel_c2:
    st.markdown(sel_buttons("pair", pair_labels, active_label, "PAIR"), unsafe_allow_html=True)

with sel_c3:
    st.markdown(sel_buttons("tf", TIMEFRAMES, tf_sel, "TIMEFRAME"), unsafe_allow_html=True)

# ==============================================================================
# ROW 1 — MCT + MARKET OVERVIEW
# ==============================================================================
st.markdown('<div class="av-sec">// MARKET INTELLIGENCE LAYER</div>', unsafe_allow_html=True)

mct_col, overview_col = st.columns([1.1, 1])

with mct_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:4px">
      <div>
        <div style="font-size:8px;letter-spacing:2px;color:#4A6080;margin-bottom:2px;font-family:'Share Tech Mono',monospace">
          MCT · COMPOSITE OSCILLATOR · 3-FACTOR
        </div>
        <div style="font-size:10px;color:#5A7090;letter-spacing:1px;font-family:'Share Tech Mono',monospace">
          RSI · MACD · VOLUME
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    with st.spinner(""):
        df = fetch_twelvedata(active_td_symbol, TD_INTERVAL[tf_sel])

    seed_str = f"{active_label}-{tf_sel}"
    if df.empty:
        # Seeded dummy OHLCV
        rng   = np.random.default_rng(abs(hash(seed_str)) % 2**32)
        n     = 200
        price = np.cumprod(1 + rng.normal(0.0001, 0.003, n))
        price = price / price[0] * 1.15
        dummy_df = pd.DataFrame({
            "close":  price,
            "high":   price * (1 + np.abs(rng.normal(0,0.001,n))),
            "low":    price * (1 - np.abs(rng.normal(0,0.001,n))),
            "volume": rng.uniform(500,2000,n),
        }, index=pd.date_range("2024-01-01", periods=n, freq="15min"))
        mct_values  = calculate_mct_simple(dummy_df)
        data_source = "SIMULATION MODE"
    else:
        mct_values  = calculate_mct_simple(df)
        data_source = "LIVE · TWELVE DATA"

    current_mct = float(mct_values[-1])
    mct_color   = "#00E1FF" if current_mct >= 0 else "#FF3D71"
    sign        = "+" if current_mct >= 0 else ""

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
      <div style="font-size:8px;color:#2A3A5A;letter-spacing:1px;font-family:'Share Tech Mono',monospace">{data_source}</div>
      <div style="font-size:24px;font-weight:700;color:{mct_color};font-family:'Share Tech Mono',monospace;line-height:1">
        {sign}{current_mct:.2f}
      </div>
    </div>""", unsafe_allow_html=True)

    fig = render_mct_plotly(mct_values)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    st.markdown(factor_bars_html(current_mct, seed_str), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with overview_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)
    components.html(tv_market_overview(), height=405, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 2 — MAIN CHART + TECH GAUGE
# ==============================================================================
st.markdown(f'<div class="av-sec">// CHART CORE · {active_label} · {tf_sel}</div>', unsafe_allow_html=True)

chart_col, gauge_col = st.columns([1.45, 1])

with chart_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)
    # Chart style selector (no typing — HTML buttons)
    cs_labels = [s[0] for s in CHART_STYLES]
    cs_cur    = next((s[0] for s in CHART_STYLES if s[1]==cs_sel), "LINE")
    st.markdown(sel_buttons("cs", cs_labels, cs_cur, "CHART TYPE"), unsafe_allow_html=True)
    components.html(tv_advanced_chart(active_tv_symbol, tf_sel, cs_sel), height=435, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

with gauge_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)
    components.html(tv_tech_gauge(active_tv_symbol, tf_sel), height=435, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 3 — MINI CHARTS × 3
# ==============================================================================
st.markdown('<div class="av-sec">// MULTI-PAIR MONITOR</div>', unsafe_allow_html=True)

mini_cols = st.columns(3)
mini_keys = [("ma","mini_a"),("mb","mini_b"),("mc","mini_c")]

for col, (qk, sk) in zip(mini_cols, mini_keys):
    with col:
        st.markdown('<div class="av-panel">', unsafe_allow_html=True)
        idx      = st.session_state[sk]
        mini_lbl = [m[0] for m in MINI_OPTIONS]
        cur_lbl  = MINI_OPTIONS[idx][0]
        # Render mini symbol selector buttons
        btns = ""
        for i, (lbl, _) in enumerate(MINI_OPTIONS):
            active = "active" if lbl==cur_lbl else ""
            btns += f'<button class="av-sel-btn {active}" style="font-size:9px;padding:4px 8px" onclick="window.location.href=\'?{qk}={i}&instr={instr_class}&pair={active_label}&tf={tf_sel}&cs={cs_sel}\'">{lbl}</button>'
        st.markdown(f'<div class="av-sel-wrap" style="margin-bottom:6px">{btns}</div>', unsafe_allow_html=True)
        components.html(tv_mini_chart(MINI_OPTIONS[idx][1]), height=215, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 4 — ECONOMIC CALENDAR + SCREENER
# ==============================================================================
st.markdown('<div class="av-sec">// FUNDAMENTAL DATA · PENYARING</div>', unsafe_allow_html=True)

cal_col, screen_col = st.columns(2)
with cal_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)
    components.html(tv_econ_calendar(), height=445, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

with screen_col:
    st.markdown('<div class="av-panel">', unsafe_allow_html=True)
    components.html(tv_screener(), height=445, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 5 — AI ANALYSIS
# ==============================================================================
st.markdown('<div class="av-sec">// AI INTELLIGENCE ENGINE</div>', unsafe_allow_html=True)
st.markdown('<div class="av-panel">', unsafe_allow_html=True)

ai_m1, ai_m2, _ = st.columns([1,1,4])
with ai_m1:
    if st.button("ANALISIS PAIR", key="btn_pair"):
        st.session_state.ai_mode   = "pair"
        st.session_state.ai_result = None
with ai_m2:
    if st.button("ANALISIS NEWS", key="btn_news"):
        st.session_state.ai_mode   = "news"
        st.session_state.ai_result = None

if st.session_state.ai_mode == "news":
    inp_col, run_col = st.columns([5,1])
    with inp_col:
        news_text = st.text_input("n", placeholder="PASTE HEADLINE / KONTEKS BERITA...", key="news_inp")
    with run_col:
        st.markdown("<div style='margin-top:4px'></div>", unsafe_allow_html=True)
        if st.button("ANALISIS", key="btn_run_n"):
            if news_text.strip():
                st.session_state.ai_result = (
                    f"[PROTOTYPE] Dampak berita terhadap {active_label}: Sentimen risk-off meningkat jangka pendek. "
                    f"Potensi volatilitas naik di sesi New York. Pantau reaksi harga 30 menit pertama pasca rilis. "
                    f"(Placeholder — akan diganti Claude API asli.)"
                )
else:
    run_c, _ = st.columns([1,5])
    with run_c:
        if st.button("ANALISIS", key="btn_run_p"):
            st.session_state.ai_result = (
                f"[PROTOTYPE] Analisis teknikal {active_label}: Bias bearish-netral jangka pendek. "
                f"RSI mendekati 42, MACD histogram menyempit. EMA-20 di bawah EMA-50. "
                f"ATR naik 12% — volatilitas meningkat. WAIT — konfirmasi bounce di S1 sebelum entry. "
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

trade_cols = st.columns(len(DUMMY_TRADES))
for col, t in zip(trade_cols, DUMMY_TRADES):
    with col:
        is_buy = t["dir"]=="BUY"
        dc     = "av-dir-buy" if is_buy else "av-dir-sell"
        rows   = "".join([
            f'<div class="av-trade-row"><span class="av-trade-k">{k}</span>'
            f'<span style="color:{c};font-size:11px;font-weight:{700 if k!="ENTRY" else 400}">{t[vk]}</span></div>'
            for k,vk,c in [
                ("ENTRY","entry","#8BA0C0"),("SL","sl","#FF3D71"),
                ("TP1","tp1","#00E1FF"),("TP2","tp2","#00B8CC"),("TP3","tp3","#0090A0"),
            ]
        ])
        st.markdown(f"""
        <div class="av-trade-card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <span class="av-trade-symbol">{t['symbol']}</span>
            <span class="{dc}">{t['dir']}</span>
          </div>
          {rows}
        </div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# ROW 7 — TOP STORIES
# ==============================================================================
st.markdown('<div class="av-sec">// MARKET INTELLIGENCE · NEWS FEED</div>', unsafe_allow_html=True)
st.markdown('<div class="av-panel">', unsafe_allow_html=True)
components.html(tv_top_stories(), height=475, scrolling=False)
st.markdown('</div>', unsafe_allow_html=True)