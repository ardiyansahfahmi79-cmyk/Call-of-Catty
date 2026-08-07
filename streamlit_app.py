"""
signal_analysis.py — Signal Analysis · Aerovulpis v4.1
Prototype: Mode User + Mode Admin
"""

import streamlit as st
from datetime import datetime
import random

st.set_page_config(
    page_title="Signal Analysis · Aerovulpis",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── SESSION STATE ──
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "signals" not in st.session_state:
    st.session_state.signals = [
        {
            "id": 1, "symbol": "XAUUSD", "name": "Gold",
            "direction": "BULLISH",
            "entry": 3321.50, "sl": 3305.00,
            "tp1": 3338.00, "tp2": 3355.50, "tp3": 3380.00,
            "confidence": 82,
            "rr1": "1:1.0", "rr2": "1:2.0", "rr3": "1:3.5",
            "bull_prob": 82, "bear_prob": 18,
            "tp1_hit": None, "tp2_hit": None, "tp3_hit": None, "sl_hit": None,
            "timeframe": "H4", "session": "LONDON / NEW YORK", "tag": "TREND FOLLOW",
            "explanation": "Harga Gold bergerak dalam struktur higher-high higher-low di timeframe H4. EMA 21 bertindak sebagai support dinamis yang masih terjaga. Volume beli meningkat signifikan pada sesi London open. RSI (14) berada di 58 — masih dalam zona netral menuju bullish tanpa overbought. MACD crossover positif terkonfirmasi di H1.",
            "updated": "03 Agu 2026 · 13:00 WIB",
            "published": True,
            "lm_bear": [
                {"low": "3.340,00", "high": "3.352,50", "pct": "0.84"},
                {"low": "3.318,00", "high": "3.328,00", "pct": "0.58"},
                {"low": "", "high": "", "pct": ""},
            ],
            "lm_bull": [
                {"low": "3.288,00", "high": "3.297,50", "pct": "0.61"},
                {"low": "3.275,00", "high": "3.283,00", "pct": "0.52"},
                {"low": "3.258,00", "high": "3.266,00", "pct": "0.59"},
            ],
        },
        {
            "id": 2, "symbol": "BTCUSD", "name": "Bitcoin",
            "direction": "BULLISH",
            "entry": 95840.00, "sl": 93200.00,
            "tp1": 98500.00, "tp2": 101200.00, "tp3": 105000.00,
            "confidence": 74,
            "rr1": "1:1.0", "rr2": "1:2.0", "rr3": "1:3.5",
            "bull_prob": 74, "bear_prob": 26,
            "tp1_hit": True, "tp2_hit": None, "tp3_hit": None, "sl_hit": None,
            "timeframe": "H4", "session": "CRYPTO 24H", "tag": "BREAKOUT",
            "explanation": "BTC menunjukkan konsolidasi sehat setelah breakout dari range 90K–95K minggu lalu. On-chain data menunjukkan akumulasi oleh wallet besar (>1000 BTC). Struktur market H4 bullish dengan support kuat di 93.2K. TP1 sudah tercapai, potensi lanjut ke TP2 dengan trailing SL ke entry.",
            "updated": "03 Agu 2026 · 08:00 WIB",
            "published": True,
            "lm_bear": [
                {"low": "97.200", "high": "98.500", "pct": "1.38"},
                {"low": "", "high": "", "pct": ""},
                {"low": "", "high": "", "pct": ""},
            ],
            "lm_bull": [
                {"low": "93.800", "high": "94.600", "pct": "0.82"},
                {"low": "", "high": "", "pct": ""},
                {"low": "", "high": "", "pct": ""},
            ],
        },
        {
            "id": 3, "symbol": "EURUSD", "name": "Euro / Dollar",
            "direction": "BEARISH",
            "entry": 1.08420, "sl": 1.08750,
            "tp1": 1.08090, "tp2": 1.07760, "tp3": 1.07300,
            "confidence": 77,
            "rr1": "1:1.0", "rr2": "1:2.0", "rr3": "1:3.5",
            "bull_prob": 31, "bear_prob": 69,
            "tp1_hit": None, "tp2_hit": None, "tp3_hit": None, "sl_hit": True,
            "timeframe": "H4", "session": "LONDON / NEW YORK", "tag": "REVERSAL",
            "explanation": "EURUSD menguji resistance kuat di 1.0875 yang bertepatan dengan EMA 200 D1. Data NFP AS lebih kuat dari ekspektasi menekan Euro. Struktur bearish engulfing candle di H4 terkonfirmasi. Signal SL telah terkena — posisi ditutup.",
            "updated": "02 Agu 2026 · 20:00 WIB",
            "published": True,
            "lm_bear": [
                {"low": "", "high": "", "pct": ""},
                {"low": "", "high": "", "pct": ""},
                {"low": "", "high": "", "pct": ""},
            ],
            "lm_bull": [
                {"low": "", "high": "", "pct": ""},
                {"low": "", "high": "", "pct": ""},
                {"low": "", "high": "", "pct": ""},
            ],
        },
    ]
if "next_id" not in st.session_state:
    st.session_state.next_id = 4

# ── Forex ──
FOREX_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD",
    "USDCHF", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY",
]
# ── Crypto ──
CRYPTO_PAIRS = [
    "BTCUSD", "ETHUSD", "BNBUSD", "SOLUSD", "XRPUSD",
    "ADAUSD", "DOTUSD", "MATICUSD", "LINKUSD", "AVAXUSD",
]
# ── Komoditas ──
COMMODITY_PAIRS = [
    "XAUUSD", "XAGUSD", "XBRUSD", "XNGUSD", "XPDUSD",
]
# ── Saham Indonesia ──
IDX_PAIRS = [
    "IHSG", "BBCA", "BBRI", "TLKM", "ASII",
    "BMRI", "UNVR", "GGRM", "HMSP", "ANTM",
]

PAIR_OPTIONS = (
    ["── FOREX ──"] + FOREX_PAIRS +
    ["── CRYPTO ──"] + CRYPTO_PAIRS +
    ["── KOMODITAS ──"] + COMMODITY_PAIRS +
    ["── SAHAM IDX ──"] + IDX_PAIRS +
    ["CUSTOM"]
)

PAIR_NAMES = {
    # Forex
    "EURUSD": "Euro / Dollar", "GBPUSD": "Pound / Dollar",
    "USDJPY": "Dollar / Yen", "AUDUSD": "Aussie / Dollar",
    "USDCAD": "Dollar / CAD", "USDCHF": "Dollar / Franc",
    "NZDUSD": "Kiwi / Dollar", "EURGBP": "Euro / Pound",
    "EURJPY": "Euro / Yen", "GBPJPY": "Pound / Yen",
    # Crypto
    "BTCUSD": "Bitcoin", "ETHUSD": "Ethereum", "BNBUSD": "BNB",
    "SOLUSD": "Solana", "XRPUSD": "Ripple", "ADAUSD": "Cardano",
    "DOTUSD": "Polkadot", "MATICUSD": "Polygon", "LINKUSD": "Chainlink",
    "AVAXUSD": "Avalanche",
    # Komoditas
    "XAUUSD": "Gold", "XAGUSD": "Silver", "XBRUSD": "Brent Crude Oil",
    "XNGUSD": "Natural Gas", "XPDUSD": "Palladium",
    # Saham IDX
    "IHSG": "Indeks Harga Saham Gabungan", "BBCA": "Bank BCA",
    "BBRI": "Bank BRI", "TLKM": "Telkom Indonesia",
    "ASII": "Astra International", "BMRI": "Bank Mandiri",
    "UNVR": "Unilever Indonesia", "GGRM": "Gudang Garam",
    "HMSP": "HM Sampoerna", "ANTM": "Aneka Tambang",
    "CUSTOM": "Custom Pair",
}
TIMEFRAMES = ["M15", "M30", "H1", "H4", "D1", "W1"]
SESSIONS   = ["LONDON", "NEW YORK", "LONDON / NEW YORK", "ASIA", "CRYPTO 24H", "ALL SESSION"]
TAGS       = ["TREND FOLLOW", "BREAKOUT", "REVERSAL", "PATTERN", "DIVERGENCE", "SCALP", "SWING"]




def calc_rr(entry, sl, tp):
    risk = abs(entry - sl)
    if risk == 0:
        return "1:0"
    reward = abs(tp - entry)
    ratio = reward / risk
    return f"1:{ratio:.1f}"


# ── CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Share+Tech+Mono&family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { background-color: #030810 !important; }
.block-container { padding: 0 1rem 2rem !important; max-width: 1400px !important; }
#MainMenu, footer, header { visibility: hidden; }
* { box-sizing: border-box; }

/* TOPBAR */
.sm-topbar {
    display:flex; align-items:center; justify-content:space-between;
    padding:.9rem 0 1.1rem;
    border-bottom:1px solid rgba(0,212,255,.08);
    margin-bottom:1.2rem;
}
.sm-brand {
    font-family:'Orbitron',sans-serif; font-size:.7rem;
    font-weight:700; letter-spacing:4px; color:#00d4ff;
}
.sm-brand span { color:rgba(136,153,187,.4); font-weight:400; }
.sm-topbar-right { display:flex; align-items:center; gap:1rem; }
.sm-live-pill {
    display:inline-flex; align-items:center; gap:.4rem;
    background:rgba(0,255,136,.06); border:1px solid rgba(0,255,136,.2);
    border-radius:20px; padding:.2rem .7rem;
    font-family:'Share Tech Mono',monospace;
    font-size:.58rem; letter-spacing:2px; color:#00ff88;
}
.sm-live-dot {
    width:5px; height:5px; border-radius:50%;
    background:#00ff88; box-shadow:0 0 8px #00ff88;
    animation:sm-pulse 2s ease-in-out infinite;
}
@keyframes sm-pulse { 0%,100%{opacity:1;} 50%{opacity:.3;} }
.sm-time { font-family:'Share Tech Mono',monospace; font-size:.58rem; color:rgba(136,153,187,.4); letter-spacing:1px; }

/* ADMIN BANNER */
.sm-admin-banner {
    background:linear-gradient(135deg,rgba(255,170,0,.06),rgba(255,100,0,.04));
    border:1px solid rgba(255,170,0,.25);
    border-radius:8px; padding:1rem 1.4rem; margin-bottom:1.2rem;
    display:flex; align-items:center; justify-content:space-between; gap:1rem;
}
.sm-admin-banner-left { display:flex; align-items:center; gap:.8rem; }
.sm-admin-icon {
    font-size:1.2rem;
    background:rgba(255,170,0,.1); border:1px solid rgba(255,170,0,.3);
    border-radius:6px; padding:.4rem .6rem;
}
.sm-admin-title {
    font-family:'Orbitron',sans-serif; font-size:.72rem;
    font-weight:700; letter-spacing:3px; color:#e8b000;
}
.sm-admin-sub {
    font-family:'Share Tech Mono',monospace; font-size:.58rem;
    color:rgba(255,170,0,.5); letter-spacing:1px; margin-top:.1rem;
}

/* PAGE TITLE */
.sm-page-title {
    font-family:'Orbitron',sans-serif;
    font-size:clamp(1.4rem,4vw,2.1rem);
    font-weight:900; letter-spacing:5px; color:#e8f4ff;
    margin-bottom:.2rem; line-height:1;
}
.sm-page-title span { color:#00d4ff; }
.sm-page-sub {
    font-family:'Share Tech Mono',monospace;
    font-size:.62rem; color:rgba(136,153,187,.5);
    letter-spacing:1.5px; margin-bottom:1.3rem;
}


/* STATS ROW */
.sm-stats-row { display:flex; gap:.7rem; flex-wrap:wrap; margin-bottom:1.4rem; }
.sm-stat-box {
    flex:1; min-width:110px;
    background:linear-gradient(160deg,#07101f,#040c18);
    border:1px solid rgba(0,212,255,.1);
    border-radius:6px; padding:.75rem .9rem;
    position:relative; overflow:hidden;
}
.sm-stat-box::before {
    content:''; position:absolute; bottom:0; left:0; right:0; height:2px;
    background:var(--accent,linear-gradient(90deg,#00d4ff,#00ff88)); opacity:.5;
}
.sm-stat-label {
    font-family:'Share Tech Mono',monospace; font-size:.5rem;
    letter-spacing:2px; color:rgba(136,153,187,.45);
    margin-bottom:.25rem; text-transform:uppercase;
}
.sm-stat-value {
    font-family:'Orbitron',sans-serif; font-size:1.3rem;
    font-weight:700; color:#e8f4ff; line-height:1;
}
.sm-stat-value.bull { color:#00ff88; }
.sm-stat-value.bear { color:#ff4466; }
.sm-stat-value.cyan { color:#00d4ff; }
.sm-stat-value.warn { color:#e8b000; }

/* FILTER */
.sm-filter-label {
    font-family:'Share Tech Mono',monospace; font-size:.55rem;
    letter-spacing:2px; color:rgba(136,153,187,.4);
    margin-bottom:.4rem; text-transform:uppercase;
}
.sm-section-title {
    font-family:'Orbitron',sans-serif; font-size:.7rem;
    font-weight:700; letter-spacing:4px; text-transform:uppercase; color:#00d4ff;
    display:flex; align-items:center; gap:.7rem;
    margin-bottom:.9rem; margin-top:.3rem;
}
.sm-section-title::before { content:''; width:24px; height:1px; background:#00d4ff; opacity:.5; }
.sm-section-title::after  { content:''; flex:1; height:1px; background:rgba(0,212,255,.1); }

/* SIGNAL CARD */
.sm-card {
    background:linear-gradient(160deg,#070f1e,#040b16);
    border-radius:10px; margin-bottom:1.2rem;
    position:relative; overflow:hidden;
    border-top:1px solid rgba(255,255,255,.04);
}
.sm-card.bull-card { border:1px solid rgba(0,255,136,.15); border-left:3px solid #00ff88; }
.sm-card.bear-card { border:1px solid rgba(255,68,102,.15); border-left:3px solid #ff4466; }
.sm-card.sl-hit    { opacity:.6; }
.sm-card-header {
    display:flex; align-items:flex-start; justify-content:space-between;
    padding:.9rem 1.1rem .65rem;
    border-bottom:1px solid rgba(255,255,255,.04);
}
.sm-card-header-left { display:flex; flex-direction:column; gap:.12rem; }
.sm-symbol { font-family:'Orbitron',sans-serif; font-size:1.05rem; font-weight:700; letter-spacing:2px; color:#e8f4ff; }
.sm-pair-name { font-family:'Share Tech Mono',monospace; font-size:.58rem; color:rgba(136,153,187,.5); letter-spacing:1.5px; }
.sm-card-header-right { display:flex; flex-direction:column; align-items:flex-end; gap:.3rem; }
.sm-dir-badge-bull {
    font-family:'Orbitron',sans-serif; font-size:.6rem; font-weight:700; letter-spacing:3px;
    background:rgba(0,255,136,.1); border:1px solid rgba(0,255,136,.3); color:#00ff88;
    padding:.22rem .65rem; border-radius:3px;
}
.sm-dir-badge-bear {
    font-family:'Orbitron',sans-serif; font-size:.6rem; font-weight:700; letter-spacing:3px;
    background:rgba(255,68,102,.1); border:1px solid rgba(255,68,102,.3); color:#ff4466;
    padding:.22rem .65rem; border-radius:3px;
}
.sm-meta-row { display:flex; gap:.4rem; align-items:center; }

.sm-card-body { padding:.85rem 1.1rem; }
.sm-price-grid { display:grid; grid-template-columns:1fr 1fr; gap:.55rem .7rem; margin-bottom:.85rem; }
.sm-price-label {
    font-family:'Share Tech Mono',monospace; font-size:.5rem;
    letter-spacing:2px; color:rgba(136,153,187,.4);
    text-transform:uppercase; margin-bottom:.18rem;
}
.sm-price-value { font-family:'Orbitron',sans-serif; font-size:1.35rem; font-weight:700; color:#e8f4ff; line-height:1; }
.sm-price-value.cyan { color:#00d4ff; }
.sm-price-value.red  { color:#ff4466; }
.sm-sl-badge {
    display:inline-flex; align-items:center; gap:.25rem;
    background:rgba(255,68,102,.1); border:1px solid rgba(255,68,102,.35);
    border-radius:3px; padding:.12rem .45rem; margin-left:.45rem;
    font-family:'Share Tech Mono',monospace; font-size:.52rem;
    letter-spacing:1.5px; color:#ff4466; vertical-align:middle;
}
.sm-conf-row { display:flex; align-items:center; gap:.75rem; margin-bottom:.9rem; }
.sm-conf-label { font-family:'Share Tech Mono',monospace; font-size:.5rem; letter-spacing:2px; color:rgba(136,153,187,.4); width:75px; flex-shrink:0; }
.sm-conf-bar-wrap { flex:1; height:4px; background:rgba(255,255,255,.05); border-radius:4px; overflow:hidden; }
.sm-conf-fill { height:100%; border-radius:4px; }
.sm-conf-pct { font-family:'Orbitron',sans-serif; font-size:.68rem; font-weight:700; width:38px; text-align:right; flex-shrink:0; }
.sm-tp-grid { display:flex; flex-direction:column; gap:.45rem; margin-bottom:.85rem; }
.sm-tp-row { display:flex; align-items:center; gap:.55rem; }
.sm-tp-badge {
    font-family:'Orbitron',sans-serif; font-size:.52rem; font-weight:700; letter-spacing:1px;
    background:rgba(0,255,136,.1); border:1px solid rgba(0,255,136,.25); color:#00ff88;
    padding:.18rem .45rem; border-radius:3px; width:42px; text-align:center; flex-shrink:0;
}
.sm-tp-price { font-family:'Orbitron',sans-serif; font-size:1rem; font-weight:700; color:#e8f4ff; flex:1; }
.sm-tp-hit {
    display:inline-flex; align-items:center; gap:.2rem;
    background:rgba(255,68,102,.08); border:1px solid rgba(255,68,102,.25);
    border-radius:3px; padding:.1rem .4rem;
    font-family:'Share Tech Mono',monospace; font-size:.5rem; letter-spacing:1px; color:#ff4466;
}
.sm-tp-ok {
    display:inline-flex; align-items:center; gap:.2rem;
    background:rgba(0,255,136,.08); border:1px solid rgba(0,255,136,.25);
    border-radius:3px; padding:.1rem .4rem;
    font-family:'Share Tech Mono',monospace; font-size:.5rem; letter-spacing:1px; color:#00ff88;
}
.sm-tp-pending {
    display:inline-flex; align-items:center; gap:.2rem;
    background:rgba(136,153,187,.05); border:1px solid rgba(136,153,187,.15);
    border-radius:3px; padding:.1rem .4rem;
    font-family:'Share Tech Mono',monospace; font-size:.5rem; letter-spacing:1px;
    color:rgba(136,153,187,.45);
}
.sm-tp-miss {
    display:inline-flex; align-items:center; gap:.2rem;
    background:rgba(255,68,102,.08); border:1px solid rgba(255,68,102,.25);
    border-radius:3px; padding:.1rem .4rem;
    font-family:'Share Tech Mono',monospace; font-size:.5rem; letter-spacing:1px; color:#ff4466;
}
.sm-sl-miss-badge {
    display:inline-flex; align-items:center; gap:.25rem;
    background:rgba(255,68,102,.06); border:1px solid rgba(255,68,102,.2);
    border-radius:3px; padding:.12rem .45rem; margin-left:.45rem;
    font-family:'Share Tech Mono',monospace; font-size:.52rem;
    letter-spacing:1.5px; color:rgba(255,68,102,.6); vertical-align:middle;
}

/* META PILL CYBERTECH GLOW */
.sm-meta-pill {
    font-family:'Share Tech Mono',monospace; font-size:.5rem; letter-spacing:1.5px;
    color:#00d4ff; background:rgba(0,212,255,.07);
    border:1px solid rgba(0,212,255,.25); border-radius:3px; padding:.08rem .38rem;
    text-shadow:0 0 8px rgba(0,212,255,.6);
    box-shadow:0 0 6px rgba(0,212,255,.15), inset 0 0 4px rgba(0,212,255,.05);
}
.sm-tag-pill {
    font-family:'Share Tech Mono',monospace; font-size:.5rem; letter-spacing:1.5px;
    color:#00ff88; background:rgba(0,255,136,.07);
    border:1px solid rgba(0,255,136,.3); border-radius:3px; padding:.08rem .38rem;
    text-shadow:0 0 8px rgba(0,255,136,.5);
    box-shadow:0 0 6px rgba(0,255,136,.12), inset 0 0 4px rgba(0,255,136,.05);
}
.sm-rr-chip {
    font-family:'Share Tech Mono',monospace; font-size:.55rem;
    color:rgba(0,212,255,.7); background:rgba(0,212,255,.07);
    border:1px solid rgba(0,212,255,.15); border-radius:3px; padding:.08rem .42rem; flex-shrink:0;
}
.sm-forecast-row { display:flex; gap:.5rem; margin-bottom:.85rem; }
.sm-forecast-box { flex:1; padding:.5rem .75rem; border-radius:5px; font-family:'Share Tech Mono',monospace; font-size:.6rem; letter-spacing:1.5px; }
.sm-forecast-bull { background:rgba(0,255,136,.06); border:1px solid rgba(0,255,136,.2); color:#00ff88; }
.sm-forecast-bear { background:rgba(255,68,102,.06); border:1px solid rgba(255,68,102,.2); color:#ff4466; text-align:right; }
.sm-forecast-val { font-family:'Orbitron',sans-serif; font-size:.88rem; font-weight:700; }
.sm-explanation {
    background:rgba(0,212,255,.02); border:1px solid rgba(0,212,255,.08);
    border-radius:6px; padding:.85rem .95rem; margin-top:.3rem;
}
.sm-expl-label {
    font-family:'Orbitron',sans-serif; font-size:.5rem; letter-spacing:3px;
    text-transform:uppercase; color:rgba(0,212,255,.4); margin-bottom:.45rem; font-weight:700;
}
.sm-expl-text { font-family:'Inter',sans-serif; font-size:.79rem; color:rgba(160,185,210,.7); line-height:1.75; }
.sm-updated { font-family:'Share Tech Mono',monospace; font-size:.52rem; color:rgba(136,153,187,.3); letter-spacing:1.5px; padding:.45rem 1.1rem .85rem; text-align:right; }

/* ADMIN PANEL */
.admin-panel {
    background:linear-gradient(160deg,#0a1020,#070d1a);
    border:1px solid rgba(255,170,0,.2);
    border-radius:10px; padding:1.3rem 1.4rem;
    margin-bottom:1.4rem;
}
.admin-panel-title {
    font-family:'Orbitron',sans-serif; font-size:.72rem;
    font-weight:700; letter-spacing:4px; color:#e8b000;
    display:flex; align-items:center; gap:.7rem; margin-bottom:1.1rem;
}
.admin-panel-title::before { content:''; width:24px; height:1px; background:#e8b000; opacity:.5; }
.admin-panel-title::after  { content:''; flex:1; height:1px; background:rgba(255,170,0,.1); }

/* Admin result card */
.admin-result-card {
    background:rgba(255,170,0,.03);
    border:1px solid rgba(255,170,0,.12);
    border-radius:8px; padding:.9rem 1.1rem; margin-bottom:.8rem;
}
.admin-result-title {
    font-family:'Orbitron',sans-serif; font-size:.75rem;
    font-weight:700; letter-spacing:2px; color:#e8f4ff; margin-bottom:.6rem;
    display:flex; align-items:center; gap:.6rem;
}
.admin-result-dir-bull {
    font-size:.58rem; letter-spacing:2px;
    background:rgba(0,255,136,.1); border:1px solid rgba(0,255,136,.3);
    color:#00ff88; padding:.15rem .5rem; border-radius:3px;
}
.admin-result-dir-bear {
    font-size:.58rem; letter-spacing:2px;
    background:rgba(255,68,102,.1); border:1px solid rgba(255,68,102,.3);
    color:#ff4466; padding:.15rem .5rem; border-radius:3px;
}
.admin-hit-grid { display:flex; gap:.5rem; flex-wrap:wrap; }
.hit-active-bull {
    font-family:'Share Tech Mono',monospace; font-size:.58rem; letter-spacing:1.5px;
    background:rgba(0,255,136,.12); border:1px solid rgba(0,255,136,.35);
    color:#00ff88; padding:.25rem .7rem; border-radius:4px; cursor:default;
}
.hit-active-red {
    font-family:'Share Tech Mono',monospace; font-size:.58rem; letter-spacing:1.5px;
    background:rgba(255,68,102,.12); border:1px solid rgba(255,68,102,.35);
    color:#ff4466; padding:.25rem .7rem; border-radius:4px; cursor:default;
}
.hit-inactive {
    font-family:'Share Tech Mono',monospace; font-size:.58rem; letter-spacing:1.5px;
    background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.08);
    color:rgba(136,153,187,.4); padding:.25rem .7rem; border-radius:4px; cursor:default;
}

/* ── LIQUIDITY MATRIX ── */
.lm-wrap {
    margin: 0 0 .85rem 0;
    background: linear-gradient(160deg, #050e1d, #040a15);
    border: 1px solid rgba(0,212,255,.12);
    border-radius: 8px; overflow: hidden;
}
.lm-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: .55rem .9rem .45rem;
    border-bottom: 1px solid rgba(0,212,255,.07);
    background: rgba(0,212,255,.03);
}
.lm-title {
    font-family: 'Orbitron', sans-serif; font-size: .58rem;
    font-weight: 700; letter-spacing: 3px; color: #00d4ff;
    text-transform: uppercase;
}
.lm-subtitle {
    font-family: 'Share Tech Mono', monospace; font-size: .5rem;
    letter-spacing: 1.5px; color: rgba(136,153,187,.4);
}
.lm-body { padding: .6rem .9rem .5rem; }
.lm-section-label {
    font-family: 'Share Tech Mono', monospace; font-size: .5rem;
    letter-spacing: 2.5px; text-transform: uppercase;
    margin-bottom: .35rem; margin-top: .45rem;
    display: flex; align-items: center; gap: .5rem;
}
.lm-section-label.bear { color: rgba(255,68,102,.6); }
.lm-section-label.bull { color: rgba(0,212,255,.6); }
.lm-section-label::after {
    content: ''; flex: 1; height: 1px;
    background: currentColor; opacity: .2;
}
.lm-zone-row {
    display: flex; align-items: center; gap: .6rem;
    margin-bottom: .32rem;
}
.lm-zone-bar-wrap {
    flex: 1; height: 5px; border-radius: 3px;
    background: rgba(255,255,255,.04); overflow: hidden; position: relative;
}
.lm-zone-bar-bear {
    height: 100%; border-radius: 3px;
    background: linear-gradient(90deg, #ff4466, #ff2244);
    box-shadow: 0 0 8px rgba(255,68,102,.5);
    animation: lm-glow-bear 2.5s ease-in-out infinite;
}
.lm-zone-bar-bull {
    height: 100%; border-radius: 3px;
    background: linear-gradient(90deg, #00d4ff, #00aaff);
    box-shadow: 0 0 8px rgba(0,212,255,.5);
    animation: lm-glow-bull 2.5s ease-in-out infinite;
}
@keyframes lm-glow-bear {
    0%,100%{box-shadow:0 0 6px rgba(255,68,102,.4);}
    50%{box-shadow:0 0 14px rgba(255,68,102,.8);}
}
@keyframes lm-glow-bull {
    0%,100%{box-shadow:0 0 6px rgba(0,212,255,.4);}
    50%{box-shadow:0 0 14px rgba(0,212,255,.8);}
}
.lm-zone-range {
    font-family: 'Share Tech Mono', monospace; font-size: .58rem;
    letter-spacing: .5px; flex: 1; white-space: nowrap;
}
.lm-zone-range.bear { color: #ff4466; }
.lm-zone-range.bull { color: #00d4ff; }
.lm-zone-pct {
    font-family: 'Orbitron', monospace; font-size: .6rem;
    font-weight: 700; width: 38px; text-align: right; flex-shrink: 0;
}
.lm-zone-pct.bear { color: rgba(255,68,102,.8); }
.lm-zone-pct.bull { color: rgba(0,212,255,.8); }
.lm-detect-text {
    font-family: 'Inter', sans-serif; font-size: .72rem;
    color: rgba(150,180,210,.65); line-height: 1.65;
    padding: .5rem .9rem .4rem;
    border-top: 1px solid rgba(0,212,255,.06);
}
.lm-detect-text strong { color: rgba(0,212,255,.8); }
.lm-disclaimer {
    font-family: 'Share Tech Mono', monospace; font-size: .52rem;
    letter-spacing: .8px; color: rgba(136,153,187,.3);
    padding: .3rem .9rem .55rem; line-height: 1.6;
    border-top: 1px solid rgba(255,255,255,.03);
}

/* Streamlit overrides */
div[data-testid="stSelectbox"] > div { background:#07101f !important; border-color:rgba(0,212,255,.15) !important; }
div[data-testid="stNumberInput"] input { background:#07101f !important; color:#e8f4ff !important; border-color:rgba(0,212,255,.15) !important; }
div[data-testid="stTextInput"] input { background:#07101f !important; color:#e8f4ff !important; border-color:rgba(0,212,255,.15) !important; }
div[data-testid="stTextArea"] textarea { background:#07101f !important; color:#e8f4ff !important; border-color:rgba(0,212,255,.15) !important; }
div[data-testid="stSlider"] { color:#00d4ff !important; }
.stButton > button {
    font-family:'Share Tech Mono',monospace !important;
    letter-spacing:2px !important; font-size:.65rem !important;
    border-radius:4px !important;
}

@media(max-width:700px) {
    .sm-price-value { font-size:1.05rem; }
    .sm-stat-value  { font-size:1.05rem; }
}
</style>
""", unsafe_allow_html=True)


# ── TOPBAR ──
st.markdown(f"""
<div class="sm-topbar">
<div class="sm-brand">AEROVULPIS <span>· SIGNAL MATRIX v4.1</span></div>
<div class="sm-topbar-right">
<div class="sm-live-pill"><div class="sm-live-dot"></div> LIVE FEED</div>
</div>
</div>
""", unsafe_allow_html=True)

# ── ADMIN TOGGLE BUTTON ──
col_a1, col_a2 = st.columns([6, 1])
with col_a2:
    if st.session_state.admin_mode:
        if st.button("✕ Tutup Admin", use_container_width=True):
            st.session_state.admin_mode = False
            st.rerun()
    else:
        if st.button("⚙ Mode Admin", use_container_width=True):
            st.session_state.admin_mode = True
            st.rerun()

# ── ADMIN BANNER ──
if st.session_state.admin_mode:
    st.markdown("""
<div class="sm-admin-banner">
<div class="sm-admin-banner-left">
<div class="sm-admin-icon">⚙</div>
<div>
<div class="sm-admin-title">ADMIN CONTROL PANEL</div>
<div class="sm-admin-sub">Buat · Edit · Publish sinyal · Update status TP/SL</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)


# ── PAGE TITLE ──
st.markdown("""
<div class="sm-page-title">SIGNAL <span>ANALYSIS</span></div>

""", unsafe_allow_html=True)


# ── STATS ──
published = [s for s in st.session_state.signals if s.get("published")]
total     = len(published)
bull_c    = sum(1 for p in published if p["direction"] == "BULLISH")
bear_c    = total - bull_c
tp_c      = sum(1 for p in published if p["tp1_hit"] is True or p["tp2_hit"] is True or p["tp3_hit"] is True)
sl_c      = sum(1 for p in published if p["sl_hit"] is True)
avg_conf  = int(sum(p["confidence"] for p in published) / total) if total else 0

st.markdown(f"""
<div class="sm-stats-row">
<div class="sm-stat-box" style="--accent:linear-gradient(90deg,#00d4ff,#00ff88)"><div class="sm-stat-label">Total Signal</div><div class="sm-stat-value">{total}</div></div>
<div class="sm-stat-box" style="--accent:#00ff88"><div class="sm-stat-label">Bullish</div><div class="sm-stat-value bull">{bull_c}</div></div>
<div class="sm-stat-box" style="--accent:#ff4466"><div class="sm-stat-label">Bearish</div><div class="sm-stat-value bear">{bear_c}</div></div>
<div class="sm-stat-box" style="--accent:linear-gradient(90deg,#00ff88,#00d4ff)"><div class="sm-stat-label">TP Tercapai</div><div class="sm-stat-value cyan">{tp_c}</div></div>
<div class="sm-stat-box" style="--accent:#ff4466"><div class="sm-stat-label">SL Terkena</div><div class="sm-stat-value warn">{sl_c}</div></div>
<div class="sm-stat-box" style="--accent:linear-gradient(90deg,#00d4ff,#7b61ff)"><div class="sm-stat-label">Avg Confidence</div><div class="sm-stat-value">{avg_conf}%</div></div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════
# ADMIN PANEL
# ════════════════════════════════════════════
if st.session_state.admin_mode:

    # ── BUAT SINYAL BARU ──
    st.markdown('<div class="admin-panel-title">Buat Sinyal Baru</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="admin-panel">', unsafe_allow_html=True)

        c1, c2, c3 = st.columns([2, 2, 2])
        with c1:
            sel_pair = st.selectbox("Pair", PAIR_OPTIONS, key="new_pair")
            if sel_pair == "CUSTOM":
                custom_sym  = st.text_input("Symbol custom (cth: SOLUSD)", key="custom_sym")
                custom_name = st.text_input("Nama pair", key="custom_name")
            new_direction = st.selectbox("Direction", ["BULLISH", "BEARISH"], key="new_dir")
        with c2:
            new_tf      = st.selectbox("Timeframe", TIMEFRAMES, index=3, key="new_tf")
            new_session = st.selectbox("Session", SESSIONS, key="new_session")
            new_tag     = st.selectbox("Tag Strategi", TAGS, key="new_tag")
        with c3:
            new_conf = st.slider("Confidence (%)", 10, 99, 70, key="new_conf")
            new_upd  = st.text_input("Jam Update", value=datetime.now().strftime("%d %b %Y · %H:%M WIB"), key="new_upd")

        st.markdown("**Level Harga**")
        p1, p2, p3, p4, p5 = st.columns(5)
        with p1: new_entry_str = st.text_input("Entry", value="0", key="new_entry")
        with p2: new_sl_str    = st.text_input("Stop Loss", value="0", key="new_sl")
        with p3: new_tp1_str   = st.text_input("TP 1", value="0", key="new_tp1")
        with p4: new_tp2_str   = st.text_input("TP 2", value="0", key="new_tp2")
        with p5: new_tp3_str   = st.text_input("TP 3", value="0", key="new_tp3")
        def to_float(s):
            try: return float(s.replace(",", ".").strip())
            except: return 0.0
        new_entry = to_float(new_entry_str)
        new_sl    = to_float(new_sl_str)
        new_tp1   = to_float(new_tp1_str)
        new_tp2   = to_float(new_tp2_str)
        new_tp3   = to_float(new_tp3_str)

        new_expl = st.text_area(
            "Deskripsi Analisis (kenapa Bullish/Bearish?)",
            height=110, key="new_expl",
            placeholder="Jelaskan alasan teknikal/fundamental: struktur market, indikator, level kunci, skenario..."
        )

        st.markdown("---")
        st.markdown("**⬡ LIQUIDITY MATRIX — Zona Institusional**")
        st.caption("Kosongkan range jika zona tidak terdeteksi — tidak akan ditampilkan di card.")

        lm_bear_zones = []
        lm_bull_zones = []

        lmc1, lmc2 = st.columns(2)
        with lmc1:
            st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:.62rem;letter-spacing:2px;color:#ff4466;margin-bottom:.4rem">▼ BEARISH ZONE</div>', unsafe_allow_html=True)
            for i in range(1, 4):
                bc1, bc2, bc3 = st.columns([2, 2, 1])
                with bc1: lo = st.text_input(f"Low {i}", value="", key=f"lm_bear_lo_{i}", placeholder="cth: 3.320,00")
                with bc2: hi = st.text_input(f"High {i}", value="", key=f"lm_bear_hi_{i}", placeholder="cth: 3.335,00")
                with bc3: pc = st.text_input(f"% {i}", value="", key=f"lm_bear_pc_{i}", placeholder="0.58")
                lm_bear_zones.append({"low": lo.strip(), "high": hi.strip(), "pct": pc.strip()})
        with lmc2:
            st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:.62rem;letter-spacing:2px;color:#00d4ff;margin-bottom:.4rem">▲ BULLISH ZONE</div>', unsafe_allow_html=True)
            for i in range(1, 4):
                bc1, bc2, bc3 = st.columns([2, 2, 1])
                with bc1: lo = st.text_input(f"Low {i}", value="", key=f"lm_bull_lo_{i}", placeholder="cth: 3.280,00")
                with bc2: hi = st.text_input(f"High {i}", value="", key=f"lm_bull_hi_{i}", placeholder="cth: 3.295,00")
                with bc3: pc = st.text_input(f"% {i}", value="", key=f"lm_bull_pc_{i}", placeholder="0.61")
                lm_bull_zones.append({"low": lo.strip(), "high": hi.strip(), "pct": pc.strip()})

        col_pub1, col_pub2 = st.columns([1, 5])
        with col_pub1:
            if st.button("🚀 Publish Sinyal", use_container_width=True, key="btn_publish"):
                sym  = custom_sym.strip().upper() if sel_pair == "CUSTOM" else sel_pair
                name = custom_name.strip() if sel_pair == "CUSTOM" else PAIR_NAMES.get(sel_pair, sel_pair)
                if sel_pair.startswith("──"):
                    st.error("Pilih pair yang valid, bukan kategori.")
                elif not sym or new_entry == 0:
                    st.error("Isi Symbol dan Entry terlebih dahulu.")
                else:
                    is_bull  = new_direction == "BULLISH"
                    bp = new_conf
                    brp = 100 - new_conf
                    st.session_state.signals.append({
                        "id": st.session_state.next_id,
                        "symbol": sym, "name": name,
                        "direction": new_direction,
                        "entry": new_entry, "sl": new_sl,
                        "tp1": new_tp1, "tp2": new_tp2, "tp3": new_tp3,
                        "entry_str": new_entry_str.strip(), "sl_str": new_sl_str.strip(),
                        "tp1_str": new_tp1_str.strip(), "tp2_str": new_tp2_str.strip(),
                        "tp3_str": new_tp3_str.strip(),
                        "confidence": new_conf,
                        "rr1": calc_rr(new_entry, new_sl, new_tp1),
                        "rr2": calc_rr(new_entry, new_sl, new_tp2),
                        "rr3": calc_rr(new_entry, new_sl, new_tp3),
                        "bull_prob": bp, "bear_prob": brp,
                        "tp1_hit": None, "tp2_hit": None, "tp3_hit": None, "sl_hit": None,
                        "timeframe": new_tf, "session": new_session, "tag": new_tag,
                        "explanation": new_expl,
                        "updated": new_upd,
                        "published": True,
                        "lm_bear": lm_bear_zones,
                        "lm_bull": lm_bull_zones,
                    })
                    st.session_state.next_id += 1
                    st.success(f"✓ Sinyal {sym} berhasil dipublish!")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ── UPDATE STATUS SINYAL ──
    st.markdown("")
    st.markdown('<div class="admin-panel-title">Update Status Sinyal</div>', unsafe_allow_html=True)

    pub_signals = [s for s in st.session_state.signals if s.get("published")]
    if not pub_signals:
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:.72rem;color:rgba(136,153,187,.35);padding:.5rem 0">Belum ada sinyal yang dipublish.</div>', unsafe_allow_html=True)
    else:
        for sig in pub_signals:
            is_bull = sig["direction"] == "BULLISH"
            dir_cls = "admin-result-dir-bull" if is_bull else "admin-result-dir-bear"
            st.markdown(f"""
<div class="admin-result-card">
<div class="admin-result-title">
{sig['symbol']}
<span class="{dir_cls}">{sig['direction']}</span>
<span style="font-family:Share Tech Mono,monospace;font-size:.6rem;color:rgba(136,153,187,.35);font-weight:400">entry {sig['entry']}</span>
</div>
</div>
""", unsafe_allow_html=True)

            hc1, hc2, hc3, hc4, hc5, hc6 = st.columns(6)
            sid = sig["id"]

            def cycle(val):
                if val is None: return True
                if val is True: return False
                return None

            def lbl_tp(val, n):
                if val is True:  return f"✓ TP{n} HIT"
                if val is False: return f"✗ TP{n} MISS"
                return f"– TP{n} PENDING"

            def lbl_sl(val):
                if val is True:  return "✓ SL HIT"
                if val is False: return "✗ SL MISS"
                return "– SL PENDING"

            with hc1:
                if st.button(lbl_tp(sig["tp1_hit"], 1), key=f"tp1_{sid}", use_container_width=True):
                    sig["tp1_hit"] = cycle(sig["tp1_hit"]); st.rerun()
            with hc2:
                if st.button(lbl_tp(sig["tp2_hit"], 2), key=f"tp2_{sid}", use_container_width=True):
                    sig["tp2_hit"] = cycle(sig["tp2_hit"]); st.rerun()
            with hc3:
                if st.button(lbl_tp(sig["tp3_hit"], 3), key=f"tp3_{sid}", use_container_width=True):
                    sig["tp3_hit"] = cycle(sig["tp3_hit"]); st.rerun()
            with hc4:
                if st.button(lbl_sl(sig["sl_hit"]), key=f"sl_{sid}", use_container_width=True):
                    new_sl_val = cycle(sig["sl_hit"])
                    sig["sl_hit"] = new_sl_val
                    # Jika SL kena (True), TP yang masih PENDING → otomatis MISS (False)
                    # TP yang sudah HIT (True) tetap tidak diubah
                    if new_sl_val is True:
                        if sig["tp1_hit"] is None: sig["tp1_hit"] = False
                        if sig["tp2_hit"] is None: sig["tp2_hit"] = False
                        if sig["tp3_hit"] is None: sig["tp3_hit"] = False
                    # Jika SL di-undo kembali ke None/False, kembalikan TP Miss → Pending
                    elif new_sl_val is None or new_sl_val is False:
                        if sig["tp1_hit"] is False: sig["tp1_hit"] = None
                        if sig["tp2_hit"] is False: sig["tp2_hit"] = None
                        if sig["tp3_hit"] is False: sig["tp3_hit"] = None
                    st.rerun()
            with hc5:
                if st.button("🗑 Hapus", key=f"del_{sid}", use_container_width=True):
                    st.session_state.signals = [s for s in st.session_state.signals if s["id"] != sid]
                    st.rerun()
            with hc6:
                st.markdown("")  # spacer

    st.markdown("---")


# ════════════════════════════════════════════
# SIGNAL FEED (USER VIEW)
# ════════════════════════════════════════════
col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
with col_f1:
    st.markdown('<div class="sm-filter-label">Direction</div>', unsafe_allow_html=True)
    dir_filter = st.selectbox("dir", ["ALL", "BULLISH", "BEARISH"], label_visibility="collapsed")
with col_f2:
    st.markdown('<div class="sm-filter-label">Status</div>', unsafe_allow_html=True)
    status_filter = st.selectbox("sts", ["ALL", "ACTIVE", "TP HIT", "SL HIT"], label_visibility="collapsed")
with col_f3:
    st.markdown('<div class="sm-filter-label">Pairs</div>', unsafe_allow_html=True)
    all_syms = [p["symbol"] for p in published]
    sym_filter = st.multiselect("pairs", all_syms, default=all_syms, label_visibility="collapsed")

filtered = []
for p in published:
    if sym_filter and p["symbol"] not in sym_filter: continue
    if dir_filter != "ALL" and p["direction"] != dir_filter: continue
    if status_filter == "ACTIVE" and (p["sl_hit"] is True or p["tp3_hit"] is True): continue
    if status_filter == "TP HIT" and not (p["tp1_hit"] is True or p["tp2_hit"] is True or p["tp3_hit"] is True): continue
    if status_filter == "SL HIT" and p["sl_hit"] is not True: continue
    filtered.append(p)

st.markdown("")
st.markdown(f'<div class="sm-section-title">Signal Feed &nbsp;<span style="color:rgba(136,153,187,.3);font-size:.62rem;letter-spacing:2px">({len(filtered)} SINYAL)</span></div>', unsafe_allow_html=True)

if not filtered:
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:.72rem;color:rgba(136,153,187,.35);text-align:center;padding:3rem 0">— Tidak ada sinyal yang cocok dengan filter —</div>', unsafe_allow_html=True)

for p in filtered:
    is_bull   = p["direction"] == "BULLISH"
    card_cls  = ("bull-card" if is_bull else "bear-card") + (" sl-hit" if p["sl_hit"] is True else "")
    dir_bcls  = "sm-dir-badge-bull" if is_bull else "sm-dir-badge-bear"
    conf      = p["confidence"]
    conf_col  = "#00ff88" if conf >= 70 else ("#e8b000" if conf >= 55 else "#ff4466")

    def tp_badge(hit):
        if hit is True:  return '<span class="sm-tp-ok">✓ HIT</span>'
        if hit is False: return '<span class="sm-tp-miss">✗ MISS</span>'
        return '<span class="sm-tp-pending">– PENDING</span>'

    if p["sl_hit"] is True:
        sl_badge = '<span class="sm-sl-badge">✗ SL HIT</span>'
    elif p["sl_hit"] is False:
        sl_badge = '<span class="sm-sl-miss-badge">✗ SL MISS</span>'
    else:
        sl_badge = ''
    

    st.markdown(f"""
<div class="sm-card {card_cls}">
<div class="sm-card-header">
<div class="sm-card-header-left">
<div class="sm-symbol">{p['symbol']}</div>
<div class="sm-pair-name">{p['name']}</div>
</div>
<div class="sm-card-header-right">
<span class="{dir_bcls}">{p['direction']}</span>
<div class="sm-meta-row">
<span class="sm-meta-pill">{p['timeframe']}</span>
<span class="sm-meta-pill">{p['session']}</span>
<span class="sm-tag-pill">{p['tag']}</span>
</div>
</div>
</div>
<div class="sm-card-body">
<div class="sm-price-grid">
<div><div class="sm-price-label">Entry</div><div class="sm-price-value cyan">{p.get('entry_str', p['entry'])}</div></div>
<div><div class="sm-price-label">Stop Loss</div><div class="sm-price-value red">{p.get('sl_str', p['sl'])}{sl_badge}</div></div>
<div><div class="sm-price-label">Risk : Reward</div><div class="sm-price-value" style="font-size:1.05rem">{p['rr1']}</div></div>
<div><div class="sm-price-label">Confidence</div><div class="sm-price-value" style="color:{conf_col};font-size:1.35rem">{conf}%</div></div>
</div>
<div class="sm-conf-row">
<div class="sm-conf-label">CONFIDENCE</div>
<div class="sm-conf-bar-wrap"><div class="sm-conf-fill" style="width:{conf}%;background:linear-gradient(90deg,#00d4ff,{conf_col})"></div></div>
<div class="sm-conf-pct" style="color:{conf_col}">{conf}%</div>
</div>
<div class="sm-tp-grid">
<div class="sm-tp-row"><span class="sm-tp-badge">TP 1</span><span class="sm-tp-price">{p.get('tp1_str', p['tp1'])}</span>{tp_badge(p['tp1_hit'])}<span class="sm-rr-chip">R:R {p['rr1']}</span></div>
<div class="sm-tp-row"><span class="sm-tp-badge">TP 2</span><span class="sm-tp-price">{p.get('tp2_str', p['tp2'])}</span>{tp_badge(p['tp2_hit'])}<span class="sm-rr-chip">R:R {p['rr2']}</span></div>
<div class="sm-tp-row"><span class="sm-tp-badge">TP 3</span><span class="sm-tp-price">{p.get('tp3_str', p['tp3'])}</span>{tp_badge(p['tp3_hit'])}<span class="sm-rr-chip">R:R {p['rr3']}</span></div>
</div>
<div class="sm-forecast-row">
<div class="sm-forecast-box sm-forecast-bull"><div style="font-size:.5rem;letter-spacing:2px;opacity:.6;margin-bottom:.18rem">BULLISH PROB</div><div class="sm-forecast-val">[{p['bull_prob']}%]</div></div>
<div class="sm-forecast-box sm-forecast-bear"><div style="font-size:.5rem;letter-spacing:2px;opacity:.6;margin-bottom:.18rem">BEARISH PROB</div><div class="sm-forecast-val">[{p['bear_prob']}%]</div></div>
</div>
</div>
""", unsafe_allow_html=True)

    # ── LIQUIDITY MATRIX ──
    lm_bear = p.get("lm_bear", [])
    lm_bull = p.get("lm_bull", [])
    bear_active = [z for z in lm_bear if z.get("low") and z.get("high")]
    bull_active = [z for z in lm_bull if z.get("low") and z.get("high")]

    if bear_active or bull_active:
        def lm_bar(pct_str, kind):
            try:
                val = float(pct_str.replace(",", ".")) if pct_str else 0
                val = min(val, 5.0)
                width = (val / 5.0) * 100
            except:
                width = 0
            return f'<div class="lm-zone-bar-wrap"><div class="lm-zone-bar-{kind}" style="width:{width:.1f}%"></div></div>'

        bear_rows = ""
        for z in bear_active:
            pct_disp = z["pct"] + "%" if z["pct"] else ""
            bear_rows += f'''
<div class="lm-zone-row">
{lm_bar(z["pct"], "bear")}
<div class="lm-zone-range bear">{z["low"]} – {z["high"]}</div>
<div class="lm-zone-pct bear">{pct_disp}</div>
</div>'''

        bull_rows = ""
        for z in bull_active:
            pct_disp = z["pct"] + "%" if z["pct"] else ""
            bull_rows += f'''
<div class="lm-zone-row">
{lm_bar(z["pct"], "bull")}
<div class="lm-zone-range bull">{z["low"]} – {z["high"]}</div>
<div class="lm-zone-pct bull">{pct_disp}</div>
</div>'''

        bear_section = f'''<div class="lm-section-label bear">▼ Bearish Zone</div>{bear_rows}''' if bear_active else ""
        bull_section = f'''<div class="lm-section-label bull">▲ Bullish Zone</div>{bull_rows}''' if bull_active else ""

        st.markdown(f'''
<div class="lm-wrap">
<div class="lm-header">
<div class="lm-title">⬡ Liquidity Matrix</div>
<div class="lm-subtitle">Institutional Order Flow Detection</div>
</div>
<div class="lm-body">
{bear_section}
{bull_section}
</div>
<div class="lm-detect-text">
Sistem mendeteksi <strong>zona akumulasi institusional</strong> pada level harga di atas.
Area ini mencerminkan potensi posisi besar dari smart money berdasarkan struktur FVG dan Order Block yang teridentifikasi.
</div>
<div class="lm-disclaimer">
⚠ Bukan rekomendasi investasi. Validasi zona ini dengan analisis mandiri sebelum mengambil keputusan trading.
</div>
</div>
''', unsafe_allow_html=True)

    st.markdown(f"""
<div class="sm-explanation" style="margin:0 1.1rem .45rem">
<div class="sm-expl-label">Signal Analysis Explanation</div>
<div class="sm-expl-text">{p['explanation'] if p['explanation'] else '—'}</div>
</div>
<div class="sm-updated">LAST UPDATE · {p['updated']}</div>
</div>
""", unsafe_allow_html=True)

# ── FOOTER ──
st.markdown("""
<div style="text-align:center;padding:1.4rem 0 .5rem;border-top:1px solid rgba(0,212,255,.06);margin-top:1rem">
<div style="font-family:'Orbitron',sans-serif;font-size:.62rem;letter-spacing:3px;color:#00d4ff;font-weight:700;margin-bottom:.25rem">AEROVULPIS · SIGNAL MATRIX</div>
<div style="font-family:'Share Tech Mono',monospace;font-size:.52rem;color:rgba(136,153,187,.3);letter-spacing:1.5px">Prototype · aerovulpis.my.id · 2026</div>
</div>
""", unsafe_allow_html=True)