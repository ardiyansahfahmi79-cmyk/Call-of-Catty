# ==============================================================================
#  aerovulpis_terminal.py — AEROVULPIS TERMINAL v4.2
#  Quantitative Market Intelligence System · Streamlit Edition
#  Powered by NVIDIA NIM (Free Models from build.nvidia.com)
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
from datetime import datetime, timedelta

st.set_page_config(
    page_title="AEROVULPIS TERMINAL",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
#  GLOBAL CSS
# ==============================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background:#070A12 !important;
    font-family:'Share Tech Mono','Courier New',monospace !important;
    color:#C8D8F0 !important;
}

[data-testid="stSidebar"] { display:none !important; }
[data-testid="collapsedControl"] { display:none !important; }
[data-testid="stDecoration"] { display:none !important; }
[data-testid="stHeader"] { background:transparent !important; height:0 !important; }
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
div[data-testid="stHorizontalBlock"] { gap:0px !important; }

.av-brand-wrap { padding:4px 0 0; margin-bottom:0; }
.av-brand-line { display:flex; align-items:baseline; gap:8px; }
.av-prefix { font-size:7px; letter-spacing:3px; color:#1A3A5A; border:1px solid #1A3A5A; padding:1px 5px; border-radius:2px; }
.av-title { font-size:16px; letter-spacing:3px; color:#E8F1FF; font-weight:700; font-family:'Share Tech Mono',monospace; line-height:1.2; }
.av-title .acc { color:#00E1FF; }
.av-ver { font-size:7px; letter-spacing:2px; color:#2A4060; }
.av-tagline { font-size:6px; letter-spacing:2px; color:#1A3A5A; margin-top:1px; margin-bottom:0; }
div.block-container > div > div > div { margin-bottom:0 !important; }
iframe { display:block; margin:0 !important; }
.av-sec { font-size:7px; letter-spacing:2px; color:#1A3060; padding:4px 0 2px; font-family:'Share Tech Mono',monospace; margin:0; }

.av-panel {
    background:#09111E; border:1px solid #111827; border-radius:8px;
    padding:12px; position:relative; overflow:hidden; margin-bottom:8px;
}
.av-panel::before {
    content:""; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,225,255,0.18),transparent);
}

[data-testid="stSelectbox"] label { display:none !important; }
[data-testid="stSelectbox"] { margin-bottom:0 !important; }
[data-testid="stSelectbox"] > div > div {
    background:#09111E !important; border:1px solid rgba(0,225,255,0.3) !important;
    border-radius:5px !important; color:#00E1FF !important;
    font-family:'Share Tech Mono',monospace !important; font-size:11px !important;
    letter-spacing:1px !important; min-height:36px !important;
    box-shadow:0 0 8px rgba(0,225,255,0.12) !important; cursor:pointer !important;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color:#00E1FF !important; box-shadow:0 0 14px rgba(0,225,255,0.28) !important;
}
[data-testid="stSelectbox"] svg { fill:#00E1FF !important; }
[data-baseweb="select"] input { pointer-events:none !important; caret-color:transparent !important; cursor:pointer !important; user-select:none !important; }
[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
[data-baseweb="select"] span { color:#00E1FF !important; font-family:'Share Tech Mono',monospace !important; letter-spacing:1px !important; }
[data-baseweb="popover"] [data-baseweb="menu"] {
    background:#09111E !important; border:1px solid rgba(0,225,255,0.25) !important; border-radius:6px !important;
}
[data-baseweb="option"] {
    background:#09111E !important; color:#8BA0C0 !important;
    font-family:'Share Tech Mono',monospace !important; font-size:11px !important;
    border-bottom:1px solid #0E1422 !important; cursor:pointer !important;
}
[data-baseweb="option"]:hover, [data-baseweb="option"][aria-selected="true"] {
    background:rgba(0,225,255,0.10) !important; color:#00E1FF !important;
}
.av-sel-label { font-size:8px; letter-spacing:1.5px; color:#2A4060; margin-bottom:3px; font-family:'Share Tech Mono',monospace; }

[data-testid="stButton"] > button {
    background:linear-gradient(135deg,rgba(0,225,255,0.15),rgba(168,85,247,0.15)) !important;
    color:#00E1FF !important; font-weight:700 !important;
    font-family:'Share Tech Mono',monospace !important; font-size:10px !important;
    letter-spacing:1px !important; border:1px solid rgba(0,225,255,0.4) !important;
    border-radius:4px !important; padding:6px 10px !important; transition:all 0.15s ease !important;
}
[data-testid="stButton"] > button:hover {
    background:rgba(0,225,255,0.22) !important; border-color:#00E1FF !important;
    box-shadow:0 0 10px rgba(0,225,255,0.3) !important;
}

[data-testid="stTextInput"] label { display:none !important; }
[data-testid="stTextInput"] input {
    background:#07101C !important; border:1px solid #1A2540 !important;
    border-radius:5px !important; color:#C8D8F0 !important;
    font-family:'Share Tech Mono',monospace !important; font-size:11px !important;
}
[data-testid="stTextInput"] input::placeholder { color:#2A3A54 !important; }

.av-ai-result {
    background:#07101C; border:1px solid #1A2540; border-left:2px solid #00E1FF;
    padding:12px 14px; border-radius:5px; font-size:11px; line-height:1.7;
    color:#8BA0C0; letter-spacing:0.3px; font-family:'Share Tech Mono',monospace; margin-top:8px;
    white-space: pre-wrap; word-wrap: break-word;
}
.av-ai-result-news {
    background:#07101C; border:1px solid #1A2540; border-left:2px solid #A855F7;
    padding:12px 14px; border-radius:5px; font-size:11px; line-height:1.7;
    color:#8BA0C0; letter-spacing:0.3px; font-family:'Share Tech Mono',monospace; margin-top:8px;
    white-space: pre-wrap; word-wrap: break-word;
}

.av-trade-card {
    background:#09111E; border:1px solid #111827; border-radius:8px;
    padding:12px; position:relative; overflow:hidden; margin-bottom:8px;
}
.av-trade-card::before {
    content:""; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,225,255,0.2),transparent);
}
.av-trade-symbol { font-size:13px; font-weight:700; color:#E8F1FF; letter-spacing:1px; }
.av-dir-buy {
    font-size:9px; padding:3px 8px; border-radius:3px; font-weight:700; letter-spacing:1.5px;
    background:rgba(0,225,255,0.12); color:#00E1FF; border:1px solid rgba(0,225,255,0.35);
}
.av-dir-sell {
    font-size:9px; padding:3px 8px; border-radius:3px; font-weight:700; letter-spacing:1.5px;
    background:rgba(255,61,113,0.12); color:#FF3D71; border:1px solid rgba(255,61,113,0.35);
}
.av-trade-row { display:flex; justify-content:space-between; padding:3px 0; border-bottom:1px solid #0E1422; font-size:11px; }
.av-trade-k { color:#3A4A6A; letter-spacing:1px; font-size:9px; }

.av-factor-wrap { display:flex; gap:4px; margin-top:6px; }
.av-factor-item { flex:1; background:#0A0E18; border:1px solid #1A2238; border-radius:4px; padding:4px 6px; }
.av-factor-k { font-size:7.5px; color:#4A6080; letter-spacing:1px; margin-bottom:2px; }
.av-factor-bar-wrap { height:2px; background:#0E1422; border-radius:1px; }
.av-factor-v { font-size:8px; margin-top:2px; text-align:right; }

.js-plotly-plot .plotly .modebar { display:none !important; }
div[data-testid="column"]:has(.mct-shift) { padding-top: 30px !important; }
div[data-testid="column"]:has(.main-chart-shift) { margin-top: -60px !important; position: relative; z-index: 10; }

.av-model-badge {
    display:inline-block; font-size:7px; letter-spacing:1px; color:#A855F7;
    background:rgba(168,85,247,0.08); border:1px solid rgba(168,85,247,0.25);
    padding:2px 6px; border-radius:3px; margin-left:8px;
}

.av-loading {
    color:#4A6080; font-size:10px; letter-spacing:1px;
    animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
#  CONSTANTS
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
        ("BRENT", "BRENT", "TVC:UKOIL"),
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

TIMEFRAMES = ["15m","30m","1h","4h","1D"]
TV_INTERVAL = {"15m":"15","30m":"30","1h":"60","4h":"240","1D":"D"}
TV_TA_INT  = {"15m":"15m","30m":"30m","1h":"1h","4h":"4h","1D":"1D"}
TD_INTERVAL = {"15m":"15min","30m":"30min","1h":"1h","4h":"4h","1D":"1day"}
CHART_STYLES = [("LINE","3"),("CANDLES","1"),("HEIKIN","8"),("AREA","9"),("BARS","0")]

MINI_OPTIONS = {
    "FOREX": [
        ("EURUSD","OANDA:EURUSD"), ("GBPUSD","OANDA:GBPUSD"),
        ("USDJPY","OANDA:USDJPY"), ("AUDUSD","OANDA:AUDUSD"),
        ("USDCHF","OANDA:USDCHF"), ("NZDUSD","OANDA:NZDUSD"),
        ("USDCAD","OANDA:USDCAD"), ("EURGBP","OANDA:EURGBP"),
    ],
    "COMMODITIES": [
        ("XAUUSD","OANDA:XAUUSD"), ("XAGUSD","OANDA:XAGUSD"),
        ("OIL", "CAPITALCOM:OIL_CRUDE"), ("DXY", "CAPITALCOM:DXY"),
        ("US10Y", "TVC:US10Y"), ("NATGAS","TVC:NATURALGAS"),
    ],
    "US STOCKS": [
        ("AAPL", "NASDAQ:AAPL"), ("NVDA", "NASDAQ:NVDA"),
        ("TSLA", "NASDAQ:TSLA"), ("MSFT", "NASDAQ:MSFT"),
        ("AMZN", "NASDAQ:AMZN"), ("GOOGL", "NASDAQ:GOOGL"),
        ("META", "NASDAQ:META"), ("SPX", "FOREXCOM:SPXUSD"),
    ],
    "CRYPTO": [
        ("BTCUSD","COINBASE:BTCUSD"), ("ETHUSD","COINBASE:ETHUSD"),
        ("SOLUSD","COINBASE:SOLUSD"), ("BNBUSD","BINANCE:BNBUSDT"),
        ("XRPUSD","COINBASE:XRPUSD"), ("ADAUSD","COINBASE:ADAUSD"),
        ("DOTUSD","COINBASE:DOTUSD"), ("AVAXUSD","COINBASE:AVAXUSD"),
    ],
}

DUMMY_TRADES = [
    {"symbol":"EURUSD","dir":"BUY", "entry":"1.14620","sl":"1.14280","tp1":"1.14950","tp2":"1.15300","tp3":"1.15700"},
    {"symbol":"GBPUSD","dir":"SELL","entry":"1.32310","sl":"1.32650","tp1":"1.31980","tp2":"1.31600","tp3":"1.31150"},
    {"symbol":"XAUUSD","dir":"BUY", "entry":"2382.40","sl":"2371.00","tp1":"2394.00","tp2":"2406.50","tp3":"2420.00"},
    {"symbol":"BTCUSD","dir":"BUY", "entry":"67420.0","sl":"65800.0","tp1":"69000.0","tp2":"71500.0","tp3":"74200.0"},
]

PAIR_CURRENCY_MAP = {
    "EURUSD": ("EUR","USD"), "GBPUSD": ("GBP","USD"), "USDJPY": ("USD","JPY"),
    "AUDUSD": ("AUD","USD"), "USDCHF": ("USD","CHF"), "NZDUSD": ("NZD","USD"),
    "USDCAD": ("USD","CAD"), "EURGBP": ("EUR","GBP"),
    "XAUUSD": ("XAU","USD"), "XAGUSD": ("XAG","USD"), "WTIUSD": ("OIL","USD"),
    "BRENT": ("OIL","USD"), "NATGAS": ("NATGAS","USD"),
    "AAPL": ("AAPL","USD"), "NVDA": ("NVDA","USD"), "TSLA": ("TSLA","USD"),
    "MSFT": ("MSFT","USD"), "AMZN": ("AMZN","USD"), "GOOGL": ("GOOGL","USD"),
    "META": ("META","USD"), "SPX": ("SPX","USD"),
    "BTCUSD": ("BTC","USD"), "ETHUSD": ("ETH","USD"), "SOLUSD": ("SOL","USD"),
    "BNBUSD": ("BNB","USD"), "XRPUSD": ("XRP","USD"), "ADAUSD": ("ADA","USD"),
    "DOTUSD": ("DOT","USD"), "AVAXUSD": ("AVAX","USD"),
}

# ==============================================================================
#  NVIDIA NIM — Free Models (Terbaru dari build.nvidia.com)
# ==============================================================================

NVIDIA_FREE_MODELS = {
    "LLaMA 3.3 70B ★": "meta/llama-3.3-70b-instruct",
    "Nemotron 70B": "nvidia/llama-3.1-nemotron-70b-instruct",
    "Qwen 2.5 72B ★": "qwen/qwen2.5-72b-instruct",
    "Gemma 2 27B": "google/gemma-2-27b-it",
    "Mixtral 8x22B": "mistralai/mixtral-8x22b-instruct-v0.1",
    "LLaMA 3.1 8B": "meta/llama-3.1-8b-instruct",
}

NVIDIA_BEST_FOR_PAIR = "meta/llama-3.3-70b-instruct"
NVIDIA_BEST_FOR_NEWS = "qwen/qwen2.5-72b-instruct"

# ==============================================================================
#  SESSION STATE INIT
# ==============================================================================

_DEFAULTS = {
    "instr_class": "FOREX",
    "pair_label": "EURUSD",
    "timeframe": "15m",
    "chart_style": "3",
    "indicator_mode": "NO MODE",
    "mini_a": "GBPUSD",
    "mini_b": "USDJPY",
    "mini_c": "AUDUSD",
    "ai_mode": "pair",
    "ai_result": None,
    "ai_result_class": "av-ai-result",
    "nvidia_model": "LLaMA 3.3 70B ★",
    "ai_loading": False,
}

for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ==============================================================================
#  API KEY HELPER
# ==============================================================================

def _get_secret(key, default=""):
    try:
        val = st.secrets.get(key, default)
        return val if val else default
    except Exception:
        return default

# ==============================================================================
#  NVIDIA NIM API
# ==============================================================================

def call_nvidia_nim(prompt: str, model_name: str = None, force_model: str = None) -> str:
    if force_model:
        model_id = force_model
    elif model_name:
        model_id = NVIDIA_FREE_MODELS.get(model_name, "meta/llama-3.3-70b-instruct")
    else:
        if st.session_state.get("ai_mode") == "news":
            model_id = NVIDIA_BEST_FOR_NEWS
        else:
            model_id = NVIDIA_BEST_FOR_PAIR

    api_key = _get_secret("NVIDIA_API_KEY", "")
    if not api_key:
        return "⚠ CONFIG ERROR — NVIDIA_API_KEY tidak ditemukan di secrets.\n\nCara mendapatkan (GRATIS):\n1. Buka https://build.nvidia.com\n2. Sign in dengan Google / GitHub\n3. Klik model 'LLaMA 3.3 70B Instruct'\n4. Klik 'Get API Key'\n5. Copy key (format: nvapi-...)\n6. Tambahkan ke .streamlit/secrets.toml:\n   NVIDIA_API_KEY = \"nvapi-xxxxx\""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "model": model_id,
        "messages": [
            {
                "role": "system",
                "content": """You are AEROVULPIS, a senior quantitative analyst at a tier-1 institutional desk. Your output style mirrors internal research notes from Goldman Sachs, JP Morgan, or Bloomberg Intelligence.

MANDATORY OUTPUT RULES:
- Use the EXACT structural format provided in the user prompt — do not deviate
- Use box-drawing characters (━ ┃ ┣ ┫ ┗ ┛ ┏ ┓ ┌ ┐ └ ┘ ├ ┤) for visual structure
- Use tree-drawing characters (├─ └─ │) for sub-items
- Reference SPECIFIC price levels from the data — never fabricate
- Use institutional terminology: confluence, thesis, invalidation, conviction, structural, participation rate
- Keep every section concise — no filler sentences
- The ONE-LINE SUMMARY must be exactly 1 line, max 15 words, ending with a period
- Do NOT use markdown bold (**). Use UPPERCASE for emphasis instead
- Do NOT use bullet points (-). Use tree characters (├─ └─) instead
- Write in English only"""
            },
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2048,
        "temperature": 0.2,
        "top_p": 0.85,
        "frequency_penalty": 0.4,
        "presence_penalty": 0.1,
    }

    try:
        resp = requests.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        elif "error" in data:
            return f"⚠ NVIDIA NIM Error: {data['error'].get('message', 'Unknown error')}"
        return "⚠ NVIDIA NIM: Empty response"

    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response else "?"
        try:
            error_detail = e.response.json()
            error_msg = error_detail.get("detail", error_detail.get("error", {}).get("message", str(e)[:300]))
        except:
            error_msg = str(e)[:300]

        if code == 429:
            return "⚠ RATE LIMIT — Terlalu banyak request. Tunggu 1-2 menit, atau ganti model (Gemma 2 27B paling cepat)."
        if code == 401:
            return "⚠ AUTH ERROR — NVIDIA_API_KEY tidak valid. Cek di https://build.nvidia.com"
        if code == 403:
            return "⚠ ACCESS DENIED — Model tidak tersedia. Coba: LLaMA 3.1 8B atau Gemma 2 27B."
        if code == 503:
            return "⚠ MODEL UNAVAILABLE — Server sedang sibuk. Coba lagi dalam 30 detik, atau ganti model."
        return f"⚠ NVIDIA NIM Error {code}: {error_msg}"

    except requests.exceptions.Timeout:
        return "⚠ TIMEOUT — Model terlalu lambat. Coba ganti ke Gemma 2 27B atau LLaMA 3.1 8B."
    except requests.exceptions.ConnectionError:
        return "⚠ CONNECTION ERROR — Periksa koneksi internet."
    except Exception as e:
        return f"⚠ NVIDIA NIM Error: {str(e)[:300]}"

# ==============================================================================
#  MCT ENGINE
# ==============================================================================

@st.cache_data(ttl=60, show_spinner=False)
def fetch_twelvedata(symbol: str, interval: str, outputsize: int = 300) -> pd.DataFrame:
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
    rng = np.random.default_rng(abs(hash(seed_str)) % 2**32)
    price = np.cumprod(1 + rng.normal(0.0002, 0.004, n))
    price = price / price[0] * 1.15
    vol = rng.uniform(300, 2500, n)
    freq_map = {"15m":"15min","30m":"30min","1h":"1h","4h":"4h","1D":"1D"}
    freq = freq_map.get(seed_str.split("-")[-1], "15min")
    return pd.DataFrame({
        "close": price,
        "high": price * (1 + np.abs(rng.normal(0, 0.0015, n))),
        "low": price * (1 - np.abs(rng.normal(0, 0.0015, n))),
        "volume": vol,
    }, index=pd.date_range("2024-01-01", periods=n, freq=freq))

def calculate_mct(df: pd.DataFrame) -> dict:
    lookback = 63

    def z_norm(s: pd.Series) -> pd.Series:
        rm = s.rolling(lookback, min_periods=10).mean()
        rs = s.rolling(lookback, min_periods=10).std().replace(0, np.nan)
        return ((s - rm) / rs).clip(-3, 3) / 3.0

    close = df["close"]
    volume = df.get("volume", pd.Series(np.ones(len(df)), index=df.index))

    rsi_raw = ta.rsi(close, length=14).fillna(50) - 50.0
    z_rsi = z_norm(rsi_raw)
    rsi_score = float(np.clip(z_rsi.iloc[-1] * 100, -100, 100))

    macd_df = ta.macd(close, fast=12, slow=26, signal=9)
    macd_hist = macd_df["MACDh_12_26_9"].fillna(0)
    z_macd = z_norm(macd_hist)
    macd_score = float(np.clip(z_macd.iloc[-1] * 100, -100, 100))

    vol_ma = volume.rolling(20, min_periods=5).mean().replace(0, np.nan)
    vol_mom = ((volume / vol_ma) - 1.0).fillna(0).clip(-2, 2)
    z_vol = z_norm(vol_mom)
    vol_score = float(np.clip(z_vol.iloc[-1] * 100, -100, 100))

    comp = (0.40 * z_rsi) + (0.40 * z_macd) + (0.20 * z_vol)
    raw = np.clip((comp * 100).fillna(0).to_numpy(), -100, 100)

    n = len(raw)
    wl = min(25, n)
    if wl % 2 == 0: wl -= 1
    wl = max(wl, 5)

    smoothed = np.clip(savgol_filter(raw, window_length=wl, polyorder=3, mode="interp"), -100, 100)

    return {
        "values": smoothed,
        "current": float(smoothed[-1]),
        "rsi_score": rsi_score,
        "macd_score": macd_score,
        "vol_score": vol_score,
    }

def render_mct(result: dict) -> go.Figure:
    values = result["values"]
    current = result["current"]
    prev = float(values[max(0, len(values)-6)])
    momentum = current - prev

    isBull = current >= 0
    dot_c = "#00E1FF" if isBull else "#FF3D71"

    x = list(range(len(values)))
    y_up = np.where(values >= 0, values, np.nan)
    y_dn = np.where(values <= 0, values, np.nan)

    if current > 60: regime = "STRONG BULL"
    elif current > 25: regime = "BULL"
    elif current < -60: regime = "STRONG BEAR"
    elif current < -25: regime = "BEAR"
    else: regime = "NEUTRAL"

    fig = go.Figure()

    fig.add_hrect(y0=30, y1=80, fillcolor="rgba(0,225,255,0.04)", line_width=0)
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

    fig.add_trace(go.Scatter(x=[x[-1]], y=[current], mode="markers",
                             marker=dict(color=dot_c, size=13, opacity=0.2, line=dict(width=0)),
                             showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[x[-1]], y=[current], mode="markers",
                             marker=dict(color=dot_c, size=7, line=dict(color="#070A12", width=2)),
                             showlegend=False, hoverinfo="skip"))

    for lvl, lbl in [(80,"OB EXTREME"),(30,"OB ZONE"),(0,None),(-30,"OS ZONE"),(-80,"OS EXTREME")]:
        lc = "rgba(255,255,255,0.45)" if lvl==0 else "rgba(42,53,80,0.8)"
        dash = "solid" if lvl==0 else "dot"
        fig.add_hline(y=lvl, line_color=lc, line_width=1.1 if lvl==0 else 0.65, line_dash=dash)

        if lbl:
            fc = "rgba(0,225,255,0.45)" if lvl>0 else "rgba(255,61,113,0.45)"
            fig.add_annotation(x=0, y=lvl, xref="paper", text=f" {lbl}", showarrow=False,
                               font=dict(size=7, color=fc, family="Share Tech Mono,monospace"),
                               xanchor="left", yanchor="bottom")

    sym = "▲" if momentum >= 0 else "▼"
    fig.add_annotation(x=1, y=0.97, xref="paper", yref="paper",
                       text=f"{regime} {sym} {abs(momentum):.1f}",
                       showarrow=False, font=dict(size=9, color=dot_c, family="Share Tech Mono,monospace"),
                       xanchor="right", yanchor="top")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=235, margin=dict(l=8,r=54,t=8,b=8),
        dragmode=False, hovermode="x",
        xaxis=dict(visible=False, showgrid=False, fixedrange=True),
        yaxis=dict(range=[-100,100], showgrid=False, zeroline=False, fixedrange=True,
                   tickvals=[-80,-30,0,30,80], tickfont=dict(color="#3A4A6A",size=9,family="Share Tech Mono,monospace"), side="right"),
    )
    return fig

def factor_bars_html(r: dict) -> str:
    factors = [
        ("RSI", r["rsi_score"]),
        ("MACD", r["macd_score"]),
        ("VOL", r["vol_score"]),
    ]
    items = ""
    for k, v in factors:
        v = float(np.clip(v, -100, 100))
        c = "#00E1FF" if v >= 0 else "#FF3D71"
        sgn = "+" if v >= 0 else ""
        ml = f"margin-left:{100-abs(v):.0f}%" if v < 0 else ""
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
#  NEWS AGGREGATOR ENGINE (4 Sumber API)
# ==============================================================================

@st.cache_data(ttl=300, show_spinner=False)
def fetch_newsapi(query: str, api_key: str) -> list:
    if not api_key:
        return []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 15,
            "apiKey": api_key,
        }
        r = requests.get(url, params=params, timeout=10).json()
        if r.get("status") != "ok":
            return []
        articles = []
        for a in r.get("articles", []):
            articles.append({
                "title": a.get("title", "") or "",
                "source": a.get("source", {}).get("name", "Unknown"),
                "publishedAt": a.get("publishedAt", ""),
                "description": a.get("description", "") or "",
                "url": a.get("url", ""),
                "aggregator": "NewsAPI",
            })
        return articles
    except Exception:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def fetch_marketaux(symbols: str, api_key: str) -> list:
    if not api_key:
        return []
    try:
        url = "https://api.marketaux.com/v1/news/all"
        params = {
            "symbols": symbols,
            "filter_entities": "true",
            "language": "en",
            "limit": 15,
            "api_token": api_key,
        }
        r = requests.get(url, params=params, timeout=10).json()
        articles = []
        for a in r.get("data", []):
            entities = a.get("entities", [])
            sent = 0.0
            if entities:
                sent = np.mean([e.get("sentiment_score", 0) for e in entities if e.get("sentiment_score") is not None])
            articles.append({
                "title": a.get("title", "") or "",
                "source": a.get("source", "") or "Unknown",
                "publishedAt": a.get("published_at", ""),
                "description": a.get("description", "") or "",
                "url": a.get("url", ""),
                "sentiment": sent,
                "aggregator": "MarketAux",
            })
        return articles
    except Exception:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def fetch_gnews(query: str, api_key: str) -> list:
    if not api_key:
        return []
    try:
        url = "https://gnews.io/api/v4/search"
        params = {
            "q": query,
            "lang": "en",
            "max": 15,
            "token": api_key,
        }
        r = requests.get(url, params=params, timeout=10).json()
        articles = []
        for a in r.get("articles", []):
            articles.append({
                "title": a.get("title", "") or "",
                "source": a.get("source", {}).get("name", "Unknown"),
                "publishedAt": a.get("publishedAt", ""),
                "description": a.get("description", "") or "",
                "url": a.get("url", ""),
                "aggregator": "GNews",
            })
        return articles
    except Exception:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def fetch_current_news(api_key: str) -> list:
    if not api_key:
        return []
    try:
        url = "https://api.currentsapi.services/v1/latest-news"
        params = {
            "language": "en",
            "apiKey": api_key,
        }
        r = requests.get(url, params=params, timeout=10).json()
        articles = []
        for a in r.get("news", []):
            articles.append({
                "title": a.get("title", "") or "",
                "source": a.get("author", "") or "Unknown",
                "publishedAt": a.get("published", ""),
                "description": a.get("description", "") or "",
                "url": a.get("url", ""),
                "aggregator": "Current News API",
            })
        return articles
    except Exception:
        return []

# ==============================================================================
#  NEWS PROCESSOR
# ==============================================================================

SOURCE_RANK = {
    "Reuters": 10, "Bloomberg": 9, "CNBC": 8, "Financial Times": 8,
    "MarketWatch": 6, "The Wall Street Journal": 8, "Barron's": 6,
    "MarketAux": 5, "GNews": 4, "Current News API": 3, "NewsAPI": 3,
}

def process_news_articles(articles: list) -> list:
    if not articles:
        return []

    seen_titles = set()
    unique = []
    for a in articles:
        key = a.get("title", "")[:40].lower().strip()
        if not key or key in seen_titles:
            continue
        seen_titles.add(key)
        unique.append(a)

    def _parse_time(a):
        t = a.get("publishedAt", "")
        if not t:
            return datetime.min
        try:
            return datetime.fromisoformat(t.replace("Z", "+00:00"))
        except Exception:
            try:
                return datetime.strptime(t[:19], "%Y-%m-%dT%H:%M:%S")
            except Exception:
                return datetime.min

    unique.sort(key=_parse_time, reverse=True)

    for a in unique:
        src = a.get("source", "")
        a["source_rank"] = SOURCE_RANK.get(src, 3)
        conf = 0.2
        if a.get("title"):
            conf += 0.3
        if a.get("description"):
            conf += 0.2
        conf += (a["source_rank"] / 10) * 0.3
        a["confidence"] = round(min(conf, 1.0), 2)

    return unique

def filter_institutional(articles: list) -> list:
    inst_sources = ["reuters", "bloomberg", "cnbc"]
    result = []
    for a in articles:
        src = a.get("source", "").lower()
        if any(s in src for s in inst_sources):
            result.append(a)
    return result

# ==============================================================================
#  SMC MODULE (Smart Money Concepts)
# ==============================================================================

def detect_swing_points(df: pd.DataFrame, left: int = 3, right: int = 3) -> dict:
    highs = df["high"].values
    lows = df["low"].values
    n = len(highs)
    swing_highs = []
    swing_lows = []

    for i in range(left, n - right):
        is_sh = all(highs[i] >= highs[j] for j in range(i - left, i + right + 1) if j != i)
        is_sl = all(lows[i] <= lows[j] for j in range(i - left, i + right + 1) if j != i)
        if is_sh:
            swing_highs.append({"idx": i, "price": float(highs[i])})
        if is_sl:
            swing_lows.append({"idx": i, "price": float(lows[i])})

    return {"swing_highs": swing_highs, "swing_lows": swing_lows}

def detect_structure(swing_data: dict) -> dict:
    shs = swing_data["swing_highs"]
    sls = swing_data["swing_lows"]

    events = []
    all_pts = []
    for s in shs:
        all_pts.append({"idx": s["idx"], "price": s["price"], "type": "high"})
    for s in sls:
        all_pts.append({"idx": s["idx"], "price": s["price"], "type": "low"})
    all_pts.sort(key=lambda x: x["idx"])

    trend = "ranging"
    last_hh = None
    last_ll = None

    for pt in all_pts:
        if pt["type"] == "high":
            if last_hh is None or pt["price"] > last_hh["price"]:
                if trend == "bullish" and last_hh:
                    events.append({"type": "BOS", "dir": "bullish", "idx": pt["idx"], "price": pt["price"]})
                elif last_hh and pt["price"] > last_hh["price"]:
                    events.append({"type": "CHoCH", "dir": "bullish", "idx": pt["idx"], "price": pt["price"]})
                last_hh = pt
                trend = "bullish"
        else:
            if last_ll is None or pt["price"] < last_ll["price"]:
                if trend == "bearish" and last_ll:
                    events.append({"type": "BOS", "dir": "bearish", "idx": pt["idx"], "price": pt["price"]})
                elif last_ll and pt["price"] < last_ll["price"]:
                    events.append({"type": "CHoCH", "dir": "bearish", "idx": pt["idx"], "price": pt["price"]})
                last_ll = pt
                trend = "bearish"

    return {"events": events[-5:], "trend": trend}

def detect_order_blocks(df: pd.DataFrame, count: int = 3) -> list:
    obs = []
    o = df["open"].values
    c = df["close"].values
    h = df["high"].values
    l = df["low"].values

    for i in range(2, len(df)):
        move = abs(c[i] - o[i])
        avg_move = np.mean(np.abs(c[:i+1] - o[:i+1][-20:])) if i >= 20 else move
        if move < avg_move * 1.5:
            continue

        if c[i] > o[i] and c[i-1] < o[i-1]:
            obs.append({"type": "bullish", "idx": i-1, "high": float(h[i-1]), "low": float(l[i-1])})
        elif c[i] < o[i] and c[i-1] > o[i-1]:
            obs.append({"type": "bearish", "idx": i-1, "high": float(h[i-1]), "low": float(l[i-1])})

    return obs[-count:]

def detect_fvg(df: pd.DataFrame, count: int = 3) -> list:
    fvgs = []
    h = df["high"].values
    l = df["low"].values

    for i in range(2, len(df)):
        if l[i] > h[i-2]:
            fvgs.append({"type": "bullish", "idx": i, "top": float(l[i]), "bottom": float(h[i-2])})
        elif h[i] < l[i-2]:
            fvgs.append({"type": "bearish", "idx": i, "top": float(l[i-2]), "bottom": float(h[i])})

    return fvgs[-count:]

def detect_liquidity_zones(swing_data: dict) -> dict:
    return {
        "buy_side": [s["price"] for s in swing_data["swing_highs"][-4:]],
        "sell_side": [s["price"] for s in swing_data["swing_lows"][-4:]],
    }

# ==============================================================================
#  SIGNAL PROCESSOR (Pair)
# ==============================================================================

def process_pair_signals(df: pd.DataFrame) -> dict:
    close = df["close"]
    volume = df.get("volume", pd.Series(np.ones(len(df)), index=df.index))

    rsi = ta.rsi(close, length=14).fillna(50)
    macd_df = ta.macd(close, fast=12, slow=26, signal=9)
    macd_hist = macd_df["MACDh_12_26_9"].fillna(0)
    ema20 = ta.ema(close, length=20)
    ema50 = ta.ema(close, length=50)
    ema200 = ta.ema(close, length=200)
    atr = ta.atr(df["high"], df["low"], close, length=14)

    swing = detect_swing_points(df)
    structure = detect_structure(swing)
    obs = detect_order_blocks(df)
    fvgs = detect_fvg(df)
    liq = detect_liquidity_zones(swing)

    last_rsi = float(rsi.iloc[-1])
    last_hist = float(macd_hist.iloc[-1])
    prev_hist = float(macd_hist.iloc[-2]) if len(macd_hist) > 1 else 0
    last_close = float(close.iloc[-1])
    last_ema20 = float(ema20.iloc[-1])
    last_ema50 = float(ema50.iloc[-1])
    last_ema200 = float(ema200.iloc[-1]) if not pd.isna(ema200.iloc[-1]) else last_close
    last_atr = float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else 0

    trend_score = 0
    if last_ema20 > last_ema50 and last_ema50 > last_ema200:
        trend_score += 2
    elif last_ema20 < last_ema50 and last_ema50 < last_ema200:
        trend_score -= 2
    elif last_ema20 > last_ema50:
        trend_score += 1
    elif last_ema20 < last_ema50:
        trend_score -= 1

    if last_close > last_ema200:
        trend_score += 1
    elif last_close < last_ema200:
        trend_score -= 1

    trend = "BULLISH" if trend_score >= 2 else "BEARISH" if trend_score <= -2 else "NEUTRAL"

    mom_score = 0
    if last_rsi > 60: mom_score += 1.5
    elif last_rsi > 50: mom_score += 0.5
    elif last_rsi < 40: mom_score -= 1.5
    elif last_rsi < 50: mom_score -= 0.5

    if last_hist > 0 and last_hist > prev_hist: mom_score += 1.5
    elif last_hist > 0: mom_score += 0.5
    elif last_hist < 0 and last_hist < prev_hist: mom_score -= 1.5
    elif last_hist < 0: mom_score -= 0.5

    momentum = "STRONG BULLISH" if mom_score >= 2 else "BULLISH" if mom_score >= 1 else \
               "STRONG BEARISH" if mom_score <= -2 else "BEARISH" if mom_score <= -1 else "NEUTRAL"

    liq_status = "NO SWEEP"
    if liq["buy_side"] and last_close > max(liq["buy_side"][-2:]):
        liq_status = "BUY-SIDE SWEPT"
    elif liq["sell_side"] and last_close < min(liq["sell_side"][-2:]):
        liq_status = "SELL-SIDE SWEPT"
    elif liq["buy_side"] and abs(last_close - max(liq["buy_side"][-2:])) < last_atr * 2:
        liq_status = "NEAR BUY-SIDE"
    elif liq["sell_side"] and abs(last_close - min(liq["sell_side"][-2:])) < last_atr * 2:
        liq_status = "NEAR SELL-SIDE"

    struct_events = structure["events"]
    last_struct = struct_events[-1] if struct_events else None
    struct_type = f"{last_struct['type']} {last_struct['dir'].upper()}" if last_struct else "NO CLEAR STRUCTURE"

    prob = 50
    prob += trend_score * 8
    prob += mom_score * 6
    if "SWEPT" in liq_status:
        if "SELL" in liq_status and trend == "BULLISH": prob += 10
        if "BUY" in liq_status and trend == "BEARISH": prob += 10
    if last_struct:
        if last_struct["dir"] == "bullish" and trend == "BULLISH": prob += 8
        if last_struct["dir"] == "bearish" and trend == "BEARISH": prob += 8
    if last_rsi > 70 and trend == "BULLISH": prob -= 5
    if last_rsi < 30 and trend == "BEARISH": prob -= 5
    prob = int(np.clip(prob, 10, 95))

    direction = "BULLISH" if prob >= 60 else "BEARISH" if prob <= 40 else "NEUTRAL"

    bullish_obs = [o for o in obs if o["type"] == "bullish"]
    bearish_obs = [o for o in obs if o["type"] == "bearish"]

    if direction in ("BULLISH", "NEUTRAL"):
        s1 = bullish_obs[-1]["low"] if bullish_obs else last_close - last_atr * 2
        s2 = s1 - last_atr * 2
        r1 = max(liq["buy_side"][-2:]) if len(liq["buy_side"]) >= 2 else last_close + last_atr * 2
        r2 = r1 + last_atr * 2
    else:
        r1 = bearish_obs[-1]["high"] if bearish_obs else last_close + last_atr * 2
        r2 = r1 + last_atr * 2
        s1 = min(liq["sell_side"][-2:]) if len(liq["sell_side"]) >= 2 else last_close - last_atr * 2
        s2 = s1 - last_atr * 2

    return {
        "trend": trend, "momentum": momentum, "liq_status": liq_status,
        "struct_type": struct_type, "direction": direction, "probability": prob,
        "rsi": last_rsi, "macd_hist": last_hist, "macd_prev": prev_hist,
        "ema20": last_ema20, "ema50": last_ema50, "ema200": last_ema200,
        "atr": last_atr, "close": last_close,
        "order_blocks": obs, "fvgs": fvgs, "liquidity": liq,
        "structure": structure, "swing": swing,
        "support1": s1, "support2": s2, "resist1": r1, "resist2": r2,
        "vol_status": _vol_status(df),
    }

def _vol_status(df):
    v = df.get("volume", pd.Series(np.ones(len(df))))
    if len(v) < 20:
        return {"status": "N/A", "ratio": 0}
    avg20 = float(v.iloc[-20:].mean())
    cur = float(v.iloc[-1])
    ratio = cur / avg20 if avg20 > 0 else 1
    status = "VERY HIGH" if ratio > 1.5 else "ABOVE AVERAGE" if ratio > 1.2 else \
             "BELOW AVERAGE" if ratio < 0.7 else "AVERAGE"
    return {"status": status, "ratio": round(ratio, 2)}

# ==============================================================================
#  AI PROMPT BUILDER — INSTITUTIONAL GRADE
# ==============================================================================

def build_pair_prompt(pair_label: str, tf: str, sig: dict) -> str:
    d = sig
    ob_str = " | ".join([f"{o['type'].upper()} {o['low']:.5f}-{o['high']:.5f}" for o in d["order_blocks"]]) or "None detected"
    fvg_str = " | ".join([f"{f['type'].upper()} {f['bottom']:.5f}-{f['top']:.5f}" for f in d["fvgs"]]) or "None detected"

    rsi_desc = "Overbought" if d["rsi"] > 70 else "Bullish zone" if d["rsi"] > 55 else \
               "Oversold" if d["rsi"] < 30 else "Bearish zone" if d["rsi"] < 45 else "Neutral"
    macd_desc = "Bullish expanding" if d["macd_hist"] > 0 and d["macd_hist"] > d["macd_prev"] else \
                "Bullish fading" if d["macd_hist"] > 0 else \
                "Bearish expanding" if d["macd_hist"] < 0 and d["macd_hist"] < d["macd_prev"] else "Bearish fading"
    ema_desc = "Bullish alignment (20>50>200)" if d["ema20"]>d["ema50"]>d["ema200"] else \
               "Bearish alignment (20<50<200)" if d["ema20"]<d["ema50"]<d["ema200"] else "Mixed"

    return f"""[AEROVULPIS INSTITUTIONAL PAIR INTELLIGENCE]
Instrument: {pair_label} | Timeframe: {tf} | Price: {d['close']:.5f} | UTC: {datetime.utcnow().isoformat()}

[INPUT DATA]
RSI(14): {d['rsi']:.1f} ({rsi_desc})
MACD Histogram: {d['macd_hist']:.6f} ({macd_desc})
EMA Stack: EMA20={d['ema20']:.5f} EMA50={d['ema50']:.5f} EMA200={d['ema200']:.5f} — {ema_desc}
ATR(14): {d['atr']:.5f}
Volume: {d['vol_status']['status']} ({d['vol_status']['ratio']}x mean)
Structure: {d['struct_type']} | Trend: {d['structure']['trend'].upper()} | Liquidity: {d['liq_status']}
Order Blocks: {ob_str}
Fair Value Gaps: {fvg_str}
Signal: {d['direction']} | Trend: {d['trend']} | Momentum: {d['momentum']} | Probability: {d['probability']}%
R2: {d['resist2']:.5f} R1: {d['resist1']:.5f} S1: {d['support1']:.5f} S2: {d['support2']:.5f}

Output EXACTLY this structure — use box-drawing and tree characters, no markdown bold, no bullet points:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AEROVULPIS — INSTITUTIONAL PAIR INTELLIGENCE
  {pair_label} · {tf} · {datetime.utcnow().strftime('%Y-%m-%dT%H:%M')}Z
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▸ PRIMARY THESIS
  Directional Bias: [BULLISH/BEARISH/NEUTRAL] ([High/Medium/Low] Conviction)
  Confidence Interval: [{d['probability']}% ± X%]
  Thesis: [2-3 sentences connecting structure, momentum, and key level into one coherent thesis]

▸ MULTI-FACTOR CONFLUENCE
  ├─ Structure:   [SMC assessment with specific event and level]
  ├─ Momentum:    [RSI and MACD assessment with values]
  ├─ Trend:       [EMA assessment]
  ├─ Volume:      [Volume profile assessment]
  └─ Liquidity:   [Liquidity pool proximity and implication]

▸ RISK ASSESSMENT
  ├─ Invalidation: [Exact price level that breaks the thesis]
  ├─ Secondary:    [What else could go wrong]
  └─ Exogenous:    [External factor risk]

▸ EXECUTION FRAMEWORK
  ┌──────────────────────────────────────────┐
  │  ENTRY ZONE    │  [price range]           │
  │  STOP LOSS     │  [price]   (−X.XXR)     │
  │  TP1           │  [price]   (+X.XXR)     │
  │  TP2           │  [price]   (+X.XXR)     │
  │  TP3           │  [price]   (+X.XXR)     │
  └──────────────────────────────────────────┘

▸ ONE-LINE SUMMARY
  [Max 15 words, actionable, ending with period.]"""

def build_news_prompt(pair_label: str, tf: str, articles: list, inst_articles: list, user_context: str = "") -> str:
    top_arts = articles[:10]
    art_text = ""
    for i, a in enumerate(top_arts, 1):
        src = a.get("source", "Unknown")
        title = a.get("title", "No title")
        desc = a.get("description", "")
        conf = a.get("confidence", 0)
        sent = a.get("sentiment", 0)
        sent_label = "BULLISH" if sent > 0.1 else "BEARISH" if sent < -0.1 else "NEUTRAL"
        art_text += f"\n{i}. [{src}] conf:{conf:.0%} sent:{sent_label} — {title}"
        if desc and len(desc) > 10:
            art_text += f"\n   {desc[:130]}"

    inst_text = ""
    for a in inst_articles[:5]:
        src = a.get("source", "Unknown")
        title = a.get("title", "No title")
        inst_text += f"\n  └─ [{src}] {title}"

    context_addon = f"\n[USER CONTEXT]: {user_context}" if user_context.strip() else ""

    return f"""[AEROVULPIS INSTITUTIONAL NEWS INTELLIGENCE]
Instrument: {pair_label} | Timeframe: {tf} | UTC: {datetime.utcnow().isoformat()}{context_addon}

[AGGREGATED FEED — {len(articles)} articles processed, top 10 below]
{art_text if art_text else "  └─ No articles retrieved. Check news API keys."}

[INSTITUTIONAL WIRES — Reuters/Bloomberg/CNBC]
{inst_text if inst_text else "  └─ No institutional sources in current batch."}

Output EXACTLY this structure — use box-drawing and tree characters, no markdown bold, no bullet points:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AEROVULPIS — INSTITUTIONAL NEWS INTELLIGENCE
  {pair_label} · {tf} · {datetime.utcnow().strftime('%Y-%m-%dT%H:%M')}Z
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▸ SENTIMENT VECTOR
  Aggregate: [BULLISH/BEARISH/NEUTRAL] ([High/Medium/Low] Conviction)
  Institutional Alignment: [Aligned/Misaligned/No institutional data]
  Retail Alignment: [Aligned/Misaligned/Neutral]
  Consensus Strength: [Strong/Moderate/Fragmented]

▸ NARRATIVE DRIVERS
  ├─ Primary:   [Headline reference] — [impact explanation]
  ├─ Secondary: [Headline reference] — [impact explanation]
  └─ Tertiary:  [Headline reference] — [impact explanation]

▸ CROSS-ASSET IMPLICATIONS
  ├─ DXY:       [Expected direction and rationale]
  ├─ Yields:    [Expected direction and rationale]
  └─ Equities:  [Risk-on or risk-off implication]

▸ CATALYST TIMELINE
  ├─ [Event 1] — [Timing] — IMPACT: [HIGH/MEDIUM/LOW]
  ├─ [Event 2] — [Timing] — IMPACT: [HIGH/MEDIUM/LOW]
  └─ [Event 3] — [Timing] — IMPACT: [HIGH/MEDIUM/LOW]

▸ FUNDAMENTAL VERDICT
  Bias: [BUY/SELL/HOLD {pair_label}]
  Rationale: [1-2 sentences connecting news flow to directional bias]
  Caveat: [What could flip this verdict]

▸ ONE-LINE SUMMARY
  [Max 15 words, actionable, ending with period.]"""

# ==============================================================================
#  TV WIDGET HELPERS
# ==============================================================================

def _tv(src: str, cfg: dict, h: int) -> str:
    cj = json.dumps(cfg)
    return f"""<!DOCTYPE html><html><head>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html, body{{background:transparent;overflow:hidden;height:100%;}}
.av-panel-iframe {{
background:#09111E;
border:1px solid #111827;
border-radius:8px;
padding:8px;
position:relative;
height:100%;
}}
.av-panel-iframe::before {{
content:"";
position:absolute;
top:0; left:0; right:0;
height:1px;
background:linear-gradient(90deg,transparent,rgba(0,225,255,0.18),transparent);
}}
</style>
</head><body>
<div class="av-panel-iframe">
<div class="tradingview-widget-container" style="width:100%;height:100%">
<div class="tradingview-widget-container__widget" style="width:100%;height:100%"></div>
<script type="text/javascript" src="{src}" async>{cj}</script>
</div>
</div></body></html>"""

def tv_ticker_tape() -> str:
    return _tv("https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js", {
        "symbols":[
            {"proName":"FX:EURUSD", "title":"EUR/USD"},
            {"proName":"FX:GBPUSD", "title":"GBP/USD"},
            {"proName":"FX:USDJPY", "title":"USD/JPY"},
            {"proName":"FX:AUDUSD", "title":"AUD/USD"},
            {"proName":"OANDA:XAUUSD", "title":"XAU/USD"},
            {"proName":"CAPITALCOM:DXY", "title":"DXY"},
            {"proName":"TVC:US10Y", "title":"US10Y"},
            {"proName":"CAPITALCOM:OIL_CRUDE","title":"OIL"},
            {"proName":"COINBASE:BTCUSD", "title":"BTC/USD"},
            {"proName":"COINBASE:ETHUSD", "title":"ETH/USD"},
            {"proName":"NASDAQ:NVDA", "title":"NVDA"},
            {"proName":"FOREXCOM:SPXUSD", "title":"S&P 500"},
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

INDICATOR_MODES = {
    "NO MODE": None,
    "VOFS": "PUB;LuxAlgo/Volumetric-Order-Flow-Structure",
    "OBMTE": "PUB;AlphaExtract/Order-Block-Matrix-Trade-Engine",
    "OFVB": "PUB;QuantumEdge/Volume-bubbles",
    "BOB": "PUB;TradingIQ/Big-Order-Bubbles-IQ",
    "OI": "PUB;LeviathanCapital/Volume-Open-Interest-Footprint",
    "BSS": "PUB;Bjorgum/Bjorgum-SuperScript",
}

def tv_advanced_chart(symbol: str, interval: str, style: str, studies: list = None) -> str:
    cfg = json.dumps({
        "autosize":True,"symbol":symbol,"interval":TV_INTERVAL[interval],
        "timezone":"Etc/UTC","theme":"dark","style":style,"locale":"en",
        "backgroundColor":"#09111E","gridColor":"rgba(42,53,80,0.3)",
        "hide_top_toolbar":False,"hide_legend":False,
        "allow_symbol_change":False,"save_image":False,
        "calendar":False,"support_host":"https://www.tradingview.com",
        "studies": studies if studies else [],
    })
    return f"""<!DOCTYPE html><html><head>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{height:100%;background:transparent;overflow:hidden}}
.av-panel-iframe {{
background:#09111E;
border:1px solid #111827;
border-radius:8px;
padding:8px;
position:relative;
height:100%;
}}
.av-panel-iframe::before {{
content:"";
position:absolute;
top:0; left:0; right:0;
height:1px;
background:linear-gradient(90deg,transparent,rgba(0,225,255,0.18),transparent);
}}
</style>
</head><body>
<div class="av-panel-iframe">
<div class="tradingview-widget-container" style="height:100%;width:100%">
<div class="tradingview-widget-container__widget" style="height:100%;width:100%"></div>
<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
{cfg}</script>
</div>
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
        "feedMode": "all_symbols",
        "isTransparent": True,
        "displayMode": "adaptive",
        "width": "100%",
        "height": 450,
        "colorTheme": "dark",
        "locale": "en"
    }, 450)

def tv_market_movers() -> str:
    return _tv("https://s3.tradingview.com/external-embedding/embed-widget-market-movers.js", {
        "colorTheme": "dark",
        "dateRange": "1D",
        "showChart": True,
        "locale": "en",
        "largeChartUrl": "",
        "isTransparent": True,
        "showSymbolLogo": True,
        "isZoomEnabled": True,
        "symbolUrl": "",
        "width": "100%",
        "height": 450
    }, 450)

# ==============================================================================
#  HELPER: Resolve symbol info
# ==============================================================================

def _resolve_pair(label: str, instr_class: str):
    for ic, pairs in INSTRUMENTS.items():
        for p in pairs:
            if p[0] == label:
                return p
    return (label, label, label)

def _resolve_mini(label: str, instr_class: str):
    opts = MINI_OPTIONS.get(instr_class, [])
    for m in opts:
        if m[0] == label:
            return m[1]
    return label

# ==============================================================================
#  MAIN APP
# ==============================================================================

def main():
    # ── BRAND ──
    st.markdown("""
    <div class="av-brand-wrap">
        <div class="av-brand-line">
            <span class="av-prefix">QUANT SYS</span>
            <span class="av-title"><span class="acc">AERO</span>VULPIS TERMINAL</span>
            <span class="av-ver">v4.2 NVIDIA NIM</span>
        </div>
        <div class="av-tagline">QUANTITATIVE MARKET INTELLIGENCE · POWERED BY NVIDIA FREE AI</div>
    </div>
    """, unsafe_allow_html=True)

    # ── TICKER TAPE ──
    components.html(tv_ticker_tape(), height=54)

    # ── CONTROLS ROW ──
    col1, col2, col3, col4, col5, col6 = st.columns([1.5, 1.2, 0.8, 1.2, 1.2, 0.8])

    with col1:
        st.markdown('<div class="av-sel-label">INSTRUMENT CLASS</div>', unsafe_allow_html=True)
        ic = st.selectbox("ic", list(INSTRUMENTS.keys()), index=list(INSTRUMENTS.keys()).index(st.session_state.instr_class),
                          label_visibility="collapsed", key="_ic")
        if ic != st.session_state.instr_class:
            st.session_state.instr_class = ic
            st.session_state.pair_label = INSTRUMENTS[ic][0][0]
            st.session_state.mini_a = MINI_OPTIONS[ic][0][0]
            st.session_state.mini_b = MINI_OPTIONS[ic][1][0] if len(MINI_OPTIONS[ic]) > 1 else MINI_OPTIONS[ic][0][0]
            st.session_state.mini_c = MINI_OPTIONS[ic][2][0] if len(MINI_OPTIONS[ic]) > 2 else MINI_OPTIONS[ic][0][0]
            st.rerun()

    with col2:
        st.markdown('<div class="av-sel-label">PAIR</div>', unsafe_allow_html=True)
        pair_opts = [p[1] for p in INSTRUMENTS[st.session_state.instr_class]]
        pair_keys = [p[0] for p in INSTRUMENTS[st.session_state.instr_class]]
        cur_idx = pair_keys.index(st.session_state.pair_label) if st.session_state.pair_label in pair_keys else 0
        sel_pair = st.selectbox("pair", pair_opts, index=cur_idx, label_visibility="collapsed", key="_pair")
        new_label = pair_keys[pair_opts.index(sel_pair)]
        if new_label != st.session_state.pair_label:
            st.session_state.pair_label = new_label
            st.session_state.ai_result = None
            st.rerun()

    with col3:
        st.markdown('<div class="av-sel-label">TIMEFRAME</div>', unsafe_allow_html=True)
        tf = st.selectbox("tf", TIMEFRAMES, index=TIMEFRAMES.index(st.session_state.timeframe),
                          label_visibility="collapsed", key="_tf")
        if tf != st.session_state.timeframe:
            st.session_state.timeframe = tf
            st.session_state.ai_result = None
            st.rerun()

    with col4:
        st.markdown('<div class="av-sel-label">CHART STYLE</div>', unsafe_allow_html=True)
        cs_opts = [c[0] for c in CHART_STYLES]
        cs_vals = [c[1] for c in CHART_STYLES]
        cur_cs_idx = cs_vals.index(st.session_state.chart_style) if st.session_state.chart_style in cs_vals else 0
        sel_cs = st.selectbox("cs", cs_opts, index=cur_cs_idx, label_visibility="collapsed", key="_cs")
        if cs_vals[cs_opts.index(sel_cs)] != st.session_state.chart_style:
            st.session_state.chart_style = cs_vals[cs_opts.index(sel_cs)]
            st.rerun()

    with col5:
        st.markdown('<div class="av-sel-label">INDICATOR MODE</div>', unsafe_allow_html=True)
        im = st.selectbox("im", list(INDICATOR_MODES.keys()), index=list(INDICATOR_MODES.keys()).index(st.session_state.indicator_mode),
                          label_visibility="collapsed", key="_im")
        if im != st.session_state.indicator_mode:
            st.session_state.indicator_mode = im
            st.rerun()

    with col6:
        st.markdown('<div class="av-sel-label">AI MODEL</div>', unsafe_allow_html=True)
        nmodel = st.selectbox("nmodel", list(NVIDIA_FREE_MODELS.keys()),
                              index=list(NVIDIA_FREE_MODELS.keys()).index(st.session_state.nvidia_model),
                              label_visibility="collapsed", key="_nmodel",
                              format_func=lambda x: f"{x}  {'[AUTO]' if '★' in x else ''}")
        if nmodel != st.session_state.nvidia_model:
            st.session_state.nvidia_model = nmodel
            st.session_state.ai_result = None
            st.rerun()

    # ── RESOLVE CURRENT PAIR ──
    pair_info = _resolve_pair(st.session_state.pair_label, st.session_state.instr_class)
    tv_symbol = pair_info[2]
    td_symbol = pair_info[0]
    pair_display = pair_info[1]

    # ── ROW 2: MAIN CHART + TECH GAUGE ──
    r2c1, r2c2 = st.columns([3, 1.1])

    with r2c1:
        studies = []
        if st.session_state.indicator_mode != "NO MODE":
            studies.append({"id": INDICATOR_MODES[st.session_state.indicator_mode]})
        components.html(tv_advanced_chart(tv_symbol, st.session_state.timeframe, st.session_state.chart_style, studies), height=520)

    with r2c2:
        components.html(tv_tech_gauge(tv_symbol, st.session_state.timeframe), height=520)

    # ── ROW 3: MCT + MINI CHARTS ──
    r3c1, r3c2, r3c3, r3c4 = st.columns([1.1, 1, 1, 1])

    td_sym = td_symbol.replace("/", "")
    df = fetch_twelvedata(td_sym, TD_INTERVAL[st.session_state.timeframe])
    if df.empty or len(df) < 50:
        df = _make_dummy_df(f"{td_sym}-{st.session_state.timeframe}")

    mct_result = calculate_mct(df)

    with r3c1:
        st.markdown('<div class="av-sec mct-shift">◈ MCT ENGINE</div>', unsafe_allow_html=True)
        st.plotly_chart(render_mct(mct_result), use_container_width=True, config={"displayModeBar": False})
        st.markdown(factor_bars_html(mct_result), unsafe_allow_html=True)

    with r3c2:
        st.markdown('<div class="av-sec">◈ MINI CHART A</div>', unsafe_allow_html=True)
        mini_sym_a = _resolve_mini(st.session_state.mini_a, st.session_state.instr_class)
        components.html(tv_mini_chart(mini_sym_a), height=240)
        st.markdown('<div class="av-sec" style="margin-top:8px">◈ MINI CHART B</div>', unsafe_allow_html=True)
        mini_sym_b = _resolve_mini(st.session_state.mini_b, st.session_state.instr_class)
        components.html(tv_mini_chart(mini_sym_b), height=240)

    with r3c3:
        st.markdown('<div class="av-sec">◈ MINI CHART C</div>', unsafe_allow_html=True)
        mini_sym_c = _resolve_mini(st.session_state.mini_c, st.session_state.instr_class)
        components.html(tv_mini_chart(mini_sym_c), height=240)

        mini_opts = [m[0] for m in MINI_OPTIONS.get(st.session_state.instr_class, [])]
        if mini_opts:
            cur_mini = st.session_state.mini_c
            sel_mini = st.selectbox("mini_sel", mini_opts, index=mini_opts.index(cur_mini) if cur_mini in mini_opts else 0,
                                    label_visibility="collapsed", key="_mini_sel")
            if sel_mini != st.session_state.mini_c:
                st.session_state.mini_c = sel_mini
                st.rerun()

    with r3c4:
        st.markdown('<div class="av-sec">◈ SIGNAL SUMMARY</div>', unsafe_allow_html=True)
        sig = process_pair_signals(df)

        dir_color = "#00E1FF" if sig["direction"] == "BULLISH" else "#FF3D71" if sig["direction"] == "BEARISH" else "#A855F7"
        prob_color = "#00E1FF" if sig["probability"] >= 60 else "#FF3D71" if sig["probability"] <= 40 else "#A855F7"

        signal_html = f"""
        <div class="av-panel">
            <div style="font-size:9px;letter-spacing:1px;color:#3A4A6A;margin-bottom:8px">{pair_display} · {st.session_state.timeframe}</div>
            <div style="font-size:18px;font-weight:700;color:{dir_color};letter-spacing:2px;margin-bottom:4px">{sig['direction']}</div>
            <div style="font-size:10px;color:#4A6080;margin-bottom:10px">TREND: {sig['trend']} | MOM: {sig['momentum']}</div>
            <div style="font-size:11px;color:{prob_color};font-weight:700;margin-bottom:12px">PROBABILITY: {sig['probability']}%</div>
            <div class="av-trade-row"><span class="av-trade-k">RSI(14)</span><span style="color:#8BA0C0">{sig['rsi']:.1f}</span></div>
            <div class="av-trade-row"><span class="av-trade-k">MACD HIST</span><span style="color:#8BA0C0">{sig['macd_hist']:.5f}</span></div>
            <div class="av-trade-row"><span class="av-trade-k">STRUCTURE</span><span style="color:#8BA0C0;font-size:9px">{sig['struct_type']}</span></div>
            <div class="av-trade-row"><span class="av-trade-k">LIQUIDITY</span><span style="color:#8BA0C0;font-size:9px">{sig['liq_status']}</span></div>
            <div class="av-trade-row"><span class="av-trade-k">VOLUME</span><span style="color:#8BA0C0">{sig['vol_status']['status']} ({sig['vol_status']['ratio']}x)</span></div>
            <div style="margin-top:10px;border-top:1px solid #111827;padding-top:8px">
                <div class="av-trade-row"><span class="av-trade-k">RESIST 2</span><span style="color:#FF3D71">{sig['resist2']:.5f}</span></div>
                <div class="av-trade-row"><span class="av-trade-k">RESIST 1</span><span style="color:#FF3D71">{sig['resist1']:.5f}</span></div>
                <div class="av-trade-row"><span class="av-trade-k">SUPPORT 1</span><span style="color:#00E1FF">{sig['support1']:.5f}</span></div>
                <div class="av-trade-row"><span class="av-trade-k">SUPPORT 2</span><span style="color:#00E1FF">{sig['support2']:.5f}</span></div>
            </div>
        </div>
        """
        st.markdown(signal_html, unsafe_allow_html=True)

    # ── ROW 4: AI ANALYSIS ──
    st.markdown(f'<div class="av-sec" style="margin-top:12px">◈ AI ANALYSIS ENGINE <span class="av-model-badge">NVIDIA NIM — {st.session_state.nvidia_model}</span></div>', unsafe_allow_html=True)

    ai_col1, ai_col2, ai_col3 = st.columns([0.6, 0.3, 1.5])

    with ai_col1:
        ai_mode = st.selectbox(
            "ai_mode",
            ["pair", "news"],
            format_func=lambda x: "ANALISIS PAIR" if x == "pair" else "ANALISIS NEWS",
            index=0 if st.session_state.ai_mode == "pair" else 1,
            label_visibility="collapsed",
            key="_ai_mode"
        )
        if ai_mode != st.session_state.ai_mode:
            st.session_state.ai_mode = ai_mode
            st.session_state.ai_result = None
            st.rerun()

    with ai_col2:
        user_context = st.text_input(
            "context",
            placeholder="Max 20 chars",
            label_visibility="collapsed",
            key="_ctx",
            max_chars=20
        )

    with ai_col3:
        if st.button("◈ EXECUTE AI ANALYSIS", key="_ai_btn"):
            st.session_state.ai_result = None
            st.session_state.ai_loading = True
            st.rerun()

    # ── AI RESULT DISPLAY ──
    if st.session_state.ai_loading and st.session_state.ai_result is None:
        st.markdown(f'<div class="av-loading">◇ Querying NVIDIA NIM — {st.session_state.nvidia_model}...</div>', unsafe_allow_html=True)

        if st.session_state.ai_mode == "pair":
            sig = process_pair_signals(df)
            prompt = build_pair_prompt(pair_display, st.session_state.timeframe, sig)
            result_class = "av-ai-result"
        else:
            all_articles = []
            inst_articles = []

            try:
                newsapi_key = _get_secret("NEWSAPI_KEY")
                if newsapi_key:
                    base, quote = PAIR_CURRENCY_MAP.get(st.session_state.pair_label, (st.session_state.pair_label, "USD"))
                    q = f"{base} OR {quote} OR forex OR trading"
                    all_articles.extend(fetch_newsapi(q, newsapi_key))
            except: pass

            try:
                marketaux_key = _get_secret("MARKETAUX_KEY")
                if marketaux_key:
                    base, _ = PAIR_CURRENCY_MAP.get(st.session_state.pair_label, (st.session_state.pair_label, "USD"))
                    all_articles.extend(fetch_marketaux(base, marketaux_key))
            except: pass

            try:
                gnews_key = _get_secret("GNEWS_KEY")
                if gnews_key:
                    base, quote = PAIR_CURRENCY_MAP.get(st.session_state.pair_label, (st.session_state.pair_label, "USD"))
                    q = f"{base} {quote} market"
                    all_articles.extend(fetch_gnews(q, gnews_key))
            except: pass

            try:
                current_key = _get_secret("CURRENT_NEWS_KEY")
                if current_key:
                    all_articles.extend(fetch_current_news(current_key))
            except: pass

            all_articles = process_news_articles(all_articles)
            inst_articles = filter_institutional(all_articles)

            prompt = build_news_prompt(pair_display, st.session_state.timeframe, all_articles, inst_articles, user_context)
            result_class = "av-ai-result-news"

        # Auto-select model terbaik per mode
        selected_name = st.session_state.nvidia_model
        if "★" in selected_name:
            result = call_nvidia_nim(prompt, force_model=None)
        else:
            result = call_nvidia_nim(prompt, model_name=selected_name)

        st.session_state.ai_result = result
        st.session_state.ai_result_class = result_class
        st.session_state.ai_loading = False
        st.rerun()

    elif st.session_state.ai_result is not None:
        cls = st.session_state.ai_result_class
        st.markdown(f'<div class="{cls}">{st.session_state.ai_result}</div>', unsafe_allow_html=True)

    # ── ROW 5: MARKET OVERVIEW + TRADE SIGNALS ──
    st.markdown('<div class="av-sec" style="margin-top:12px">◈ MARKET OVERVIEW & TRADE SIGNALS</div>', unsafe_allow_html=True)

    r5c1, r5c2 = st.columns([2, 1])

    with r5c1:
        components.html(tv_market_overview(), height=390)

    with r5c2:
        for trade in DUMMY_TRADES:
            dir_cls = "av-dir-buy" if trade["dir"] == "BUY" else "av-dir-sell"
            trade_html = f"""
            <div class="av-trade-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                    <span class="av-trade-symbol">{trade['symbol']}</span>
                    <span class="{dir_cls}">{trade['dir']}</span>
                </div>
                <div class="av-trade-row"><span class="av-trade-k">ENTRY</span><span style="color:#E8F1FF">{trade['entry']}</span></div>
                <div class="av-trade-row"><span class="av-trade-k">STOP LOSS</span><span style="color:#FF3D71">{trade['sl']}</span></div>
                <div class="av-trade-row"><span class="av-trade-k">TP1</span><span style="color:#00E1FF">{trade['tp1']}</span></div>
                <div class="av-trade-row"><span class="av-trade-k">TP2</span><span style="color:#00E1FF">{trade['tp2']}</span></div>
                <div class="av-trade-row" style="border:none"><span class="av-trade-k">TP3</span><span style="color:#00E1FF">{trade['tp3']}</span></div>
            </div>
            """
            st.markdown(trade_html, unsafe_allow_html=True)

    # ── ROW 6: ECON CALENDAR + SCREENER ──
    st.markdown('<div class="av-sec" style="margin-top:12px">◈ ECONOMIC CALENDAR & SCREENER</div>', unsafe_allow_html=True)

    r6c1, r6c2 = st.columns([1, 1])

    with r6c1:
        components.html(tv_econ_calendar(), height=430)

    with r6c2:
        components.html(tv_screener(), height=430)

    # ── ROW 7: TOP STORIES & MARKET MOVERS ──
    st.markdown('<div class="av-sec" style="margin-top:12px">◈ TOP STORIES & MARKET MOVERS</div>', unsafe_allow_html=True)

    r7c1, r7c2 = st.columns([1.4, 1])

    with r7c1:
        components.html(tv_top_stories(), height=450)

    with r7c2:
        components.html(tv_market_movers(), height=450)

    # ── FOOTER ──
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px;font-size:7px;letter-spacing:2px;color:#1A2A40">
        AEROVULPIS TERMINAL v4.2 · NVIDIA NIM INTEGRATION · QUANTITATIVE MARKET INTELLIGENCE
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()