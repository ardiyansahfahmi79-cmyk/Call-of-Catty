"""
economic_radar_page_v2.py
Aerovulpis — Economic Radar Module (Standalone Prototype)
Run: streamlit run economic_radar_page_v2.py
Dependencies: streamlit requests pandas plotly
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Economic Radar · Aerovulpis",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────

WB_URL = "https://api.worldbank.org/v2/country/{iso}/indicator/{ind}?format=json&mrv=10&per_page=10"

INDICATORS = {
    "GDP":      {"code": "NY.GDP.MKTP.CD",   "unit": "USD",  "fmt": "triliun", "label": "GDP (PDB)",            "color": "#00FFC8", "icon": "📊", "desc": "Total output ekonomi negara."},
    "Inflasi":  {"code": "FP.CPI.TOTL.ZG",   "unit": "%",    "fmt": "persen",  "label": "Inflasi",              "color": "#FF6B6B", "icon": "🔥", "desc": "Kenaikan harga tahunan."},
    "Unemp":    {"code": "SL.UEM.TOTL.ZS",   "unit": "%",    "fmt": "persen",  "label": "Pengangguran",         "color": "#FFD93D", "icon": "👥", "desc": "% angkatan kerja tanpa pekerjaan."},
    "Debt":     {"code": "GC.DOD.TOTL.GD.ZS","unit": "%",    "fmt": "persen",  "label": "Utang/PDB",            "color": "#C77DFF", "icon": "💰", "desc": "Rasio utang terhadap PDB."},
    "Trade":    {"code": "BN.CAB.XOKA.CD",   "unit": "USD",  "fmt": "miliar",  "label": "Neraca Perdagangan",   "color": "#4FC3F7", "icon": "⚖️", "desc": "Ekspor minus impor."},
}

IND_WEIGHTS = {"GDP": 0.25, "Inflasi": 0.25, "Unemp": 0.20, "Debt": 0.15, "Trade": 0.15}

COUNTRIES = {
    "🇮🇩 Indonesia":       "ID",
    "🇺🇸 Amerika Serikat": "US",
    "🇨🇳 China":           "CN",
    "🇯🇵 Jepang":          "JP",
    "🇩🇪 Jerman":          "DE",
    "🇬🇧 Inggris":         "GB",
    "🇦🇺 Australia":       "AU",
    "🇮🇳 India":           "IN",
    "🇰🇷 Korea Selatan":   "KR",
    "🇸🇬 Singapura":       "SG",
    "🇲🇾 Malaysia":        "MY",
    "🇹🇭 Thailand":        "TH",
    "🇧🇷 Brasil":          "BR",
    "🇿🇦 Afrika Selatan":  "ZA",
    "🇸🇦 Arab Saudi":      "SA",
}

RISK_THRESH = {
    "Inflasi": {"low": 3,  "med": 6},
    "Unemp":   {"low": 5,  "med": 10},
    "Debt":    {"low": 60, "med": 90},
}

# Central bank stance data (static, updated manually)
CB_DATA = {
    "ID": {"name": "Bank Indonesia",    "rate": 6.25, "stance": "NEUTRAL",  "next": "18 Sep 2026", "trend": "→"},
    "US": {"name": "Federal Reserve",   "rate": 5.25, "stance": "HAWKISH",  "next": "18 Sep 2026", "trend": "↓"},
    "CN": {"name": "PBoC",              "rate": 3.10, "stance": "DOVISH",   "next": "20 Sep 2026", "trend": "↓"},
    "JP": {"name": "Bank of Japan",     "rate": 0.25, "stance": "HAWKISH",  "next": "20 Sep 2026", "trend": "↑"},
    "DE": {"name": "ECB",               "rate": 3.65, "stance": "DOVISH",   "next": "12 Sep 2026", "trend": "↓"},
    "GB": {"name": "Bank of England",   "rate": 5.00, "stance": "NEUTRAL",  "next": "19 Sep 2026", "trend": "↓"},
    "AU": {"name": "RBA",               "rate": 4.35, "stance": "NEUTRAL",  "next": "04 Sep 2026", "trend": "→"},
    "IN": {"name": "Reserve Bank India","rate": 6.50, "stance": "NEUTRAL",  "next": "06 Sep 2026", "trend": "↓"},
    "KR": {"name": "Bank of Korea",     "rate": 3.25, "stance": "DOVISH",   "next": "22 Sep 2026", "trend": "↓"},
    "SG": {"name": "MAS",               "rate": 3.68, "stance": "NEUTRAL",  "next": "Oct 2026",    "trend": "→"},
    "MY": {"name": "Bank Negara",       "rate": 3.00, "stance": "NEUTRAL",  "next": "05 Sep 2026", "trend": "→"},
    "TH": {"name": "Bank of Thailand",  "rate": 2.50, "stance": "DOVISH",   "next": "17 Sep 2026", "trend": "↓"},
    "BR": {"name": "BCB",               "rate": 10.50,"stance": "HAWKISH",  "next": "17 Sep 2026", "trend": "↑"},
    "ZA": {"name": "SARB",              "rate": 8.25, "stance": "NEUTRAL",  "next": "19 Sep 2026", "trend": "↓"},
    "SA": {"name": "SAMA",              "rate": 6.00, "stance": "HAWKISH",  "next": "Nov 2026",    "trend": "→"},
}

# Economic surprise index (mock — in production: fetch from Bloomberg/Reuters consensus)
SURPRISE_DATA = {
    "ID": [("GDP Q2",   4.90, 5.10, "2 Agu"),("Inflasi",  2.13, 2.00, "1 Agu"),("PMI Mfg", 51.2, 50.8, "1 Agu")],
    "US": [("NFP",      175,  206,  "2 Agu"),("CPI",      2.90, 3.10, "13 Jul"),("GDP",     2.80, 2.40, "26 Jul")],
    "CN": [("CPI",      0.20, 0.50, "9 Agu"),("GDP",      4.70, 5.10, "15 Jul"),("PMI",    49.40,49.50,"31 Jul")],
    "JP": [("CPI",      2.80, 2.60, "19 Jul"),("GDP",     0.40, 0.50, "15 Aug"),("PMI",    49.90,50.10,"1 Agu")],
    "DE": [("CPI",      2.30, 2.50, "14 Agu"),("GDP",    -0.10, 0.10, "30 Agu"),("PMI",   42.40,43.00,"1 Agu")],
    "GB": [("CPI",      2.00, 2.20, "16 Jul"),("GDP",     0.60, 0.50, "10 Agu"),("PMI",   52.10,51.50,"1 Agu")],
    "AU": [("CPI",      3.80, 3.60, "31 Jul"),("GDP",     1.10, 1.30, "5 Jun"), ("Unemp",  4.10, 4.00,"15 Aug")],
    "IN": [("GDP",      6.70, 6.50, "30 Mei"),("CPI",     3.54, 3.70, "12 Jul"),("PMI",   57.50,57.00,"1 Agu")],
    "KR": [("GDP",      0.60, 0.50, "25 Jul"),("CPI",     2.60, 2.40, "2 Agu"), ("Exp",    -9.9, -5.0,"1 Agu")],
    "SG": [("GDP",      2.90, 2.50, "12 Jul"),("CPI",     2.40, 2.60, "23 Jul"),("Exp",    7.30, 5.00,"17 Jul")],
    "MY": [("GDP",      4.40, 4.20, "16 Agu"),("CPI",     1.90, 2.00, "23 Jul"),("Exp",    4.10, 3.50,"30 Jul")],
    "TH": [("GDP",      2.30, 2.50, "19 Agu"),("CPI",     0.50, 0.60, "5 Agu"), ("Exp",    8.10, 6.00,"22 Jul")],
    "BR": [("CPI",      4.50, 4.20, "9 Agu"), ("GDP",     2.50, 2.20, "30 Agu"),("Unemp",  6.90, 7.20,"30 Agu")],
    "ZA": [("CPI",      4.60, 4.90, "24 Jul"),("GDP",     0.40, 0.30, "4 Jun"), ("Unemp", 32.90,33.50,"30 Jun")],
    "SA": [("GDP",      2.60, 2.30, "30 Jul"),("CPI",     2.30, 2.50, "11 Jul"),("PMI",   56.40,55.00,"5 Agu")],
}

ASSET_PAIRS = {
    "EURUSD":  {"countries": ["DE","US"],  "drivers": ["Inflasi","Debt"],      "bias_logic": "ecb_vs_fed"},
    "USDJPY":  {"countries": ["US","JP"],  "drivers": ["Inflasi","Unemp"],     "bias_logic": "fed_vs_boj"},
    "GBPUSD":  {"countries": ["GB","US"],  "drivers": ["Inflasi","GDP"],       "bias_logic": "boe_vs_fed"},
    "AUDUSD":  {"countries": ["AU","US"],  "drivers": ["Trade","Inflasi"],     "bias_logic": "rba_vs_fed"},
    "USDCNH":  {"countries": ["US","CN"],  "drivers": ["Trade","GDP"],         "bias_logic": "fed_vs_pboc"},
    "USDIDR":  {"countries": ["US","ID"],  "drivers": ["Inflasi","Debt"],      "bias_logic": "fed_vs_bi"},
    "XAUUSD":  {"countries": ["US"],       "drivers": ["Inflasi","Debt"],      "bias_logic": "gold_usd"},
    "US500":   {"countries": ["US"],       "drivers": ["GDP","Unemp","Inflasi"],"bias_logic": "us_equity"},
    "BTCUSD":  {"countries": ["US"],       "drivers": ["Inflasi","Debt"],      "bias_logic": "risk_asset"},
}

CALENDAR_EVENTS = [
    {"date":"01 Sep","event":"ISM Manufacturing PMI","country":"🇺🇸","impact":"HIGH",  "est":"49.8","prev":"49.0"},
    {"date":"04 Sep","event":"RBA Rate Decision",    "country":"🇦🇺","impact":"HIGH",  "est":"4.35%","prev":"4.35%"},
    {"date":"05 Sep","event":"GDP Q2 Indonesia",     "country":"🇮🇩","impact":"HIGH",  "est":"4.9%","prev":"5.1%"},
    {"date":"05 Sep","event":"Bank Negara Decision", "country":"🇲🇾","impact":"HIGH",  "est":"3.00%","prev":"3.00%"},
    {"date":"06 Sep","event":"Nonfarm Payrolls",     "country":"🇺🇸","impact":"HIGH",  "est":"180K","prev":"206K"},
    {"date":"09 Sep","event":"Inflasi CPI China",    "country":"🇨🇳","impact":"MEDIUM","est":"0.5%","prev":"0.2%"},
    {"date":"11 Sep","event":"Inflasi CPI AS",       "country":"🇺🇸","impact":"HIGH",  "est":"3.1%","prev":"2.9%"},
    {"date":"12 Sep","event":"ECB Rate Decision",    "country":"🇪🇺","impact":"HIGH",  "est":"3.65%","prev":"3.75%"},
    {"date":"17 Sep","event":"BoT Rate Decision",    "country":"🇹🇭","impact":"MEDIUM","est":"2.25%","prev":"2.50%"},
    {"date":"17 Sep","event":"BCB Rate Decision",    "country":"🇧🇷","impact":"HIGH",  "est":"10.75%","prev":"10.50%"},
    {"date":"18 Sep","event":"FOMC Rate Decision",   "country":"🇺🇸","impact":"HIGH",  "est":"5.00%","prev":"5.25%"},
    {"date":"18 Sep","event":"Bank Indonesia Rate",  "country":"🇮🇩","impact":"HIGH",  "est":"6.25%","prev":"6.25%"},
    {"date":"19 Sep","event":"Bank of England Rate", "country":"🇬🇧","impact":"HIGH",  "est":"4.75%","prev":"5.00%"},
    {"date":"19 Sep","event":"SARB Rate Decision",   "country":"🇿🇦","impact":"MEDIUM","est":"8.00%","prev":"8.25%"},
    {"date":"20 Sep","event":"BoJ Rate Decision",    "country":"🇯🇵","impact":"HIGH",  "est":"0.25%","prev":"0.25%"},
    {"date":"22 Sep","event":"BoK Rate Decision",    "country":"🇰🇷","impact":"HIGH",  "est":"3.00%","prev":"3.25%"},
    {"date":"25 Sep","event":"Core PCE Price Index", "country":"🇺🇸","impact":"HIGH",  "est":"2.7%","prev":"2.6%"},
    {"date":"30 Sep","event":"Inflasi CPI Indonesia","country":"🇮🇩","impact":"HIGH",  "est":"2.2%","prev":"2.13%"},
]

# ─── CSS ──────────────────────────────────────────────────────────────────────

def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

html, body, .stApp { background:#0A0D14 !important; }
section[data-testid="stSidebar"] { background:#0D1018 !important; }
.block-container { padding:1rem 1.2rem 2rem 1.2rem !important; max-width:100% !important; }

/* ─ Typography ─ */
* { box-sizing:border-box; }
body { font-family:'Exo 2',sans-serif; }

/* ─ Nav tabs ─ */
.nav-wrap {
    display:flex; gap:0.4rem; flex-wrap:wrap;
    border-bottom:1px solid #1A2332;
    padding-bottom:0.6rem; margin-bottom:1.2rem;
}
.nav-btn {
    font-family:'Share Tech Mono',monospace;
    font-size:0.65rem; letter-spacing:0.12em;
    padding:0.35rem 0.8rem;
    border:1px solid #1A2332; border-radius:2px;
    color:#4A5568; background:#0F1520;
    cursor:pointer; transition:all 0.15s;
    white-space:nowrap;
}
.nav-btn:hover  { border-color:#00FFC880; color:#00FFC8; }
.nav-btn.active { border-color:#00FFC8; color:#00FFC8; background:#00FFC810; }

/* ─ Section header ─ */
.sec-title {
    font-family:'Share Tech Mono',monospace;
    color:#00FFC8; font-size:0.85rem;
    letter-spacing:0.2em; text-transform:uppercase;
    border-left:3px solid #00FFC8;
    padding-left:0.75rem; margin:1.4rem 0 0.25rem 0;
}
.sec-sub {
    font-family:'Share Tech Mono',monospace;
    color:#374151; font-size:0.62rem;
    letter-spacing:0.1em; margin-bottom:1rem;
    padding-left:0.85rem;
}

/* ─ KPI Card ─ */
.kpi { background:linear-gradient(145deg,#0F1520,#111827);
    border:1px solid #1E2A3A; border-radius:3px;
    padding:1rem; position:relative; overflow:hidden; height:100%; }
.kpi:before { content:''; position:absolute; top:0; left:0; right:0;
    height:2px; background:var(--c,#00FFC8); opacity:.65; }
.kpi-lbl { font-family:'Share Tech Mono',monospace; font-size:0.58rem;
    letter-spacing:0.14em; color:#4A9EBF; margin-bottom:0.3rem; }
.kpi-val { font-family:'Share Tech Mono',monospace; font-size:1.25rem;
    font-weight:700; color:var(--c,#00FFC8); line-height:1; margin-bottom:0.25rem; }
.kpi-yr  { font-size:0.6rem; color:#374151; }
.badge { display:inline-block; font-family:'Share Tech Mono',monospace;
    font-size:0.55rem; letter-spacing:0.08em; padding:2px 7px;
    border-radius:2px; margin-top:0.4rem; font-weight:600; }
.b-low    { background:rgba(0,255,200,.1);  color:#00FFC8; border:1px solid #00FFC840; }
.b-mid    { background:rgba(255,217,61,.1); color:#FFD93D; border:1px solid #FFD93D40; }
.b-high   { background:rgba(255,107,107,.1);color:#FF6B6B; border:1px solid #FF6B6B40; }
.b-neu    { background:rgba(74,158,191,.1); color:#4A9EBF; border:1px solid #4A9EBF40; }

/* ─ Divider ─ */
.div { border:none; border-top:1px solid #1A2332; margin:1rem 0; }

/* ─ Info box ─ */
.ibox { background:#0F1520; border:1px solid #1E2A3A;
    border-left:3px solid var(--lc,#C77DFF);
    border-radius:0 3px 3px 0; padding:0.8rem 1rem; margin:0.5rem 0; }
.ibox-t { font-family:'Share Tech Mono',monospace; font-size:0.6rem;
    color:var(--lc,#C77DFF); letter-spacing:0.12em; margin-bottom:0.45rem; }
.ibox-b { font-size:0.78rem; color:#9CA3AF; line-height:1.65; }

/* ─ Heatmap cell ─ */
.hm-grid { display:grid; gap:3px; }
.hm-cell {
    border-radius:2px; padding:0.35rem 0.3rem;
    font-family:'Share Tech Mono',monospace;
    font-size:0.6rem; text-align:center;
    line-height:1.3; transition:opacity .2s;
}
.hm-cell:hover { opacity:.8; cursor:default; }
.hm-g  { background:rgba(0,255,200,.15); color:#00FFC8; border:1px solid #00FFC840; }
.hm-y  { background:rgba(255,217,61,.15);color:#FFD93D; border:1px solid #FFD93D40; }
.hm-r  { background:rgba(255,107,107,.15);color:#FF6B6B; border:1px solid #FF6B6B40; }
.hm-n  { background:rgba(30,42,58,.5);   color:#374151; border:1px solid #1A2332;   }
.hm-hdr{ font-family:'Share Tech Mono',monospace; font-size:0.55rem;
    color:#374151; text-align:center; padding:0.2rem; letter-spacing:.06em; }

/* ─ CB Table ─ */
.cb-row { display:flex; align-items:center; gap:0.6rem;
    background:#0F1520; border:1px solid #1E2A3A;
    border-radius:3px; padding:0.6rem 0.8rem; margin-bottom:0.4rem; flex-wrap:wrap; }
.cb-name { font-family:'Share Tech Mono',monospace; font-size:0.68rem;
    color:#D1D5DB; min-width:140px; }
.cb-rate { font-family:'Share Tech Mono',monospace; font-size:0.9rem;
    font-weight:700; color:#00FFC8; min-width:55px; }
.cb-hawk { font-family:'Share Tech Mono',monospace; font-size:0.58rem;
    padding:2px 8px; border-radius:2px; font-weight:700; }
.hawk    { background:rgba(255,107,107,.12); color:#FF6B6B; border:1px solid #FF6B6B40; }
.dove    { background:rgba(0,255,200,.12);   color:#00FFC8; border:1px solid #00FFC840; }
.neut    { background:rgba(255,217,61,.12);  color:#FFD93D; border:1px solid #FFD93D40; }
.cb-next { font-family:'Share Tech Mono',monospace; font-size:0.58rem; color:#374151; margin-left:auto; }
.trend-u { color:#FF6B6B; font-weight:700; }
.trend-d { color:#00FFC8; font-weight:700; }
.trend-n { color:#FFD93D; }

/* ─ Surprise bar ─ */
.surp-item { background:#0F1520; border:1px solid #1E2A3A;
    border-radius:3px; padding:0.65rem 0.8rem; margin-bottom:0.4rem; }
.surp-name { font-family:'Share Tech Mono',monospace; font-size:0.62rem; color:#D1D5DB; }
.surp-bar-wrap { height:4px; background:#1A2332; border-radius:2px; margin:0.4rem 0 0.2rem 0; }
.surp-bar { height:4px; border-radius:2px; }
.surp-nums { display:flex; justify-content:space-between;
    font-family:'Share Tech Mono',monospace; font-size:0.58rem; }

/* ─ Cycle badge ─ */
.cycle-card { background:#0F1520; border:1px solid #1E2A3A; border-radius:3px;
    padding:1rem; text-align:center; }
.cycle-icon { font-size:2rem; margin-bottom:0.4rem; }
.cycle-lbl  { font-family:'Share Tech Mono',monospace; font-size:0.65rem; color:#4A9EBF; }
.cycle-val  { font-family:'Share Tech Mono',monospace; font-size:1rem; font-weight:700;
    margin:0.2rem 0; letter-spacing:.1em; }
.cycle-sub  { font-size:0.68rem; color:#9CA3AF; line-height:1.5; margin-top:0.4rem; }

/* ─ Score ring ─ */
.score-wrap { text-align:center; padding:0.5rem 0; }
.score-num  { font-family:'Share Tech Mono',monospace; font-size:2.5rem;
    font-weight:700; line-height:1; }
.score-lbl  { font-family:'Share Tech Mono',monospace; font-size:0.6rem;
    color:#4A9EBF; letter-spacing:.15em; margin-top:0.2rem; }
.score-bar  { height:6px; background:#1A2332; border-radius:3px; margin:0.5rem 0; }
.score-fill { height:6px; border-radius:3px; transition:width .5s; }

/* ─ Calendar ─ */
.cal-item { display:flex; align-items:flex-start; gap:0.6rem;
    background:#0F1520; border:1px solid #1E2A3A;
    border-radius:3px; padding:0.6rem 0.8rem; margin-bottom:0.4rem; flex-wrap:wrap; }
.cal-dt  { font-family:'Share Tech Mono',monospace; font-size:0.6rem; color:#4A9EBF; min-width:50px; }
.cal-evt { font-size:0.75rem; color:#D1D5DB; flex:1; }
.cal-ctr { font-size:0.75rem; min-width:24px; }
.cal-nums{ font-family:'Share Tech Mono',monospace; font-size:0.58rem; color:#374151; margin-top:0.2rem; }
.imp-h   { font-family:'Share Tech Mono',monospace; font-size:0.58rem; color:#FF6B6B; font-weight:700; }
.imp-m   { font-family:'Share Tech Mono',monospace; font-size:0.58rem; color:#FFD93D; font-weight:700; }
.imp-l   { font-family:'Share Tech Mono',monospace; font-size:0.58rem; color:#4A9EBF; }

/* ─ Bias card ─ */
.bias-card { background:#0F1520; border:1px solid #1E2A3A; border-radius:3px; padding:1rem; }
.bias-pair { font-family:'Share Tech Mono',monospace; font-size:1.2rem;
    color:#00FFC8; letter-spacing:.08em; margin-bottom:0.3rem; }
.bias-val  { font-family:'Share Tech Mono',monospace; font-size:0.75rem;
    font-weight:700; padding:3px 10px; border-radius:2px; display:inline-block; margin-bottom:.5rem; }
.bias-bull { background:rgba(0,255,200,.12);   color:#00FFC8; border:1px solid #00FFC840; }
.bias-bear { background:rgba(255,107,107,.12); color:#FF6B6B; border:1px solid #FF6B6B40; }
.bias-neut { background:rgba(255,217,61,.12);  color:#FFD93D; border:1px solid #FFD93D40; }
.bias-txt  { font-size:0.73rem; color:#9CA3AF; line-height:1.6; }

/* ─ Footer ─ */
.footer { margin-top:2rem; padding-top:0.8rem; border-top:1px solid #1A2332;
    display:flex; justify-content:space-between; flex-wrap:wrap; gap:0.3rem; }
.footer span { font-family:'Share Tech Mono',monospace; font-size:0.58rem; color:#1E3A4A; letter-spacing:.08em; }

/* ─ Responsive ─ */
@media(max-width:768px){
    .block-container { padding:0.6rem 0.5rem 2rem !important; }
    .kpi-val { font-size:1rem; }
    .nav-btn { font-size:0.58rem; padding:0.3rem 0.6rem; }
    .cb-row  { gap:0.4rem; }
    .cb-next { margin-left:0; width:100%; margin-top:0.2rem; }
    .footer  { flex-direction:column; }
}
@media(max-width:480px){
    .sec-title { font-size:0.75rem; }
    .kpi-val   { font-size:0.9rem; }
}

/* ─ Streamlit overrides ─ */
div[data-testid="stMetric"] { display:none; }
.stSelectbox label,.stMultiSelect label,.stRadio label {
    font-family:'Share Tech Mono',monospace !important;
    font-size:0.68rem !important; color:#4A9EBF !important; letter-spacing:.1em !important;
}
button[data-testid="baseButton-secondary"] {
    background:#0F1520 !important; border:1px solid #1E2A3A !important;
    color:#4A9EBF !important; font-family:'Share Tech Mono',monospace !important;
    border-radius:2px !important;
}
</style>
""", unsafe_allow_html=True)

# ─── DATA LAYER ───────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_wb(iso: str, code: str) -> list[dict]:
    try:
        r = requests.get(WB_URL.format(iso=iso, ind=code), timeout=8)
        raw = r.json()
        if len(raw) < 2 or not raw[1]:
            return []
        return sorted(
            [{"year": int(x["date"]), "value": x["value"]}
             for x in raw[1] if x.get("value") is not None],
            key=lambda x: x["year"]
        )
    except Exception:
        return []

def latest(data):
    for d in reversed(data):
        if d["value"] is not None:
            return d["value"], d["year"]
    return None, None

def fmt_val(v, fmt, unit):
    if v is None:
        return "N/A"
    if fmt == "triliun":
        return f"{v/1e12:.2f}T {unit}"
    if fmt == "miliar":
        return f"{v/1e9:.1f}B {unit}"
    return f"{v:.2f}{unit}"

def risk_cls(key, v):
    if v is None or key not in RISK_THRESH:
        return "N/A", "b-neu"
    t = RISK_THRESH[key]
    if v <= t["low"]:  return "RENDAH", "b-low"
    if v <= t["med"]:  return "SEDANG",  "b-mid"
    return "TINGGI", "b-high"

# ─── PLOTLY THEME ─────────────────────────────────────────────────────────────

BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Share Tech Mono, monospace", color="#4A9EBF", size=10),
    margin=dict(l=8, r=8, t=28, b=8),
    xaxis=dict(gridcolor="#1A2332", linecolor="#1A2332", tickcolor="#1A2332"),
    yaxis=dict(gridcolor="#1A2332", linecolor="#1A2332", tickcolor="#1A2332"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    dragmode="pan",
)

# Pan only — scroll/drag to pan, no zoom, no modebar
CHART_CONFIG = {
    "displayModeBar": False,
    "scrollZoom": False,
    "doubleClick": "reset",
    "modeBarButtonsToRemove": [
        "zoom2d","zoomIn2d","zoomOut2d","autoScale2d",
        "select2d","lasso2d","zoomInGeo","zoomOutGeo",
        "zoomInMapbox","zoomOutMapbox",
    ],
    "dragmode": "pan",
}

def sparkline(data, color, title):
    if not data:
        return None
    years = [d["year"] for d in data]
    vals  = [d["value"] for d in data]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=vals, mode="lines+markers",
        line=dict(color=color, width=2),
        marker=dict(color=color, size=3.5),
        fill="tozeroy", fillcolor=f"{color}12",
        hovertemplate="<b>%{x}</b>: %{y:.2f}<extra></extra>",
    ))
    fig.update_layout(**BASE_LAYOUT, title=dict(text=title, font=dict(size=9.5, color=color), x=0))
    fig.update_xaxes(tickformat="d")
    return fig

def radar_fig(labels, values, name, color="#00FFC8"):
    fig = go.Figure(go.Scatterpolar(
        r=values, theta=labels, fill="toself",
        fillcolor=f"{color}0D",
        line=dict(color=color, width=2),
        marker=dict(color=color, size=4.5),
        name=name,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Share Tech Mono, monospace", color="#4A9EBF", size=9),
        margin=dict(l=25, r=25, t=25, b=25),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, gridcolor="#1A2332", linecolor="#1A2332", color="#374151", range=[0, 100]),
            angularaxis=dict(gridcolor="#1A2332", linecolor="#1A2332"),
        ),
        showlegend=False,
        dragmode="pan",
    )
    return fig

def bar_fig(labels, values, color, title):
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker=dict(color=color, opacity=0.7, line=dict(color=color, width=1)),
        hovertemplate="%{x}: <b>%{y:.2f}</b><extra></extra>",
    ))
    fig.update_layout(**BASE_LAYOUT,
        title=dict(text=title, font=dict(size=9.5, color=color), x=0))
    fig.update_xaxes(tickangle=-30, tickfont=dict(size=8))
    return fig

# ─── ANALYTICS ────────────────────────────────────────────────────────────────

def normalize(key, v):
    if v is None: return 0
    NORMS = {
        "GDP":    (0, 5e12), "Inflasi": (0, 15), "Unemp":  (0, 20),
        "Debt":   (0, 150),  "Trade":   (-5e11, 5e11),
    }
    lo, hi = NORMS.get(key, (0, 100))
    return round(min(max((v - lo) / (hi - lo) * 100, 0), 100), 1)

def macro_score(dm: dict) -> tuple[float, str, str]:
    """Weighted macro score 0–100."""
    gdp_v   = dm.get("GDP",    {}).get("val")
    inf_v   = dm.get("Inflasi",{}).get("val")
    unemp_v = dm.get("Unemp",  {}).get("val")
    debt_v  = dm.get("Debt",   {}).get("val")
    trade_v = dm.get("Trade",  {}).get("val")

    def s_gdp(v):   return min(v/1e12*10, 100) if v else 50
    def s_inf(v):   return max(0, 100-(v-2)**2*3) if v else 50
    def s_unemp(v): return max(0, 100-v*7) if v else 50
    def s_debt(v):  return max(0, 100-v*0.6) if v else 50
    def s_trade(v): return 60 if v is None else (70 if v>=0 else 40)

    scores = {
        "GDP":    s_gdp(gdp_v),
        "Inflasi":s_inf(inf_v),
        "Unemp":  s_unemp(unemp_v),
        "Debt":   s_debt(debt_v),
        "Trade":  s_trade(trade_v),
    }
    total = sum(scores[k] * IND_WEIGHTS[k] for k in scores)
    total = round(total, 1)

    if total >= 72:   grade, gcolor = "STRONG",  "#00FFC8"
    elif total >= 55: grade, gcolor = "STABLE",  "#4FC3F7"
    elif total >= 38: grade, gcolor = "FRAGILE", "#FFD93D"
    else:             grade, gcolor = "WEAK",    "#FF6B6B"
    return total, grade, gcolor

def detect_cycle(dm: dict) -> tuple[str, str, str, str]:
    inf_v   = dm.get("Inflasi",{}).get("val")
    unemp_v = dm.get("Unemp",  {}).get("val")
    gdp_s   = dm.get("GDP",    {}).get("series", [])

    gdp_growing = False
    if len(gdp_s) >= 2:
        gdp_growing = gdp_s[-1]["value"] > gdp_s[-2]["value"]

    if gdp_growing and (inf_v or 0) < 4 and (unemp_v or 100) < 6:
        return "EKSPANSI", "🚀", "#00FFC8", "Ekonomi tumbuh, inflasi terkendali, pasar kerja kuat. Favorable untuk ekuitas dan aset risiko."
    if gdp_growing and (inf_v or 0) >= 4:
        return "PUNCAK", "🌡️", "#FFD93D", "Pertumbuhan tinggi tapi inflasi memanas. Bank sentral cenderung hawkish. Waspada koreksi."
    if not gdp_growing and (inf_v or 0) >= 4:
        return "STAGFLASI", "⚠️", "#FF6B6B", "Stagflasi — pertumbuhan melambat tapi inflasi tinggi. Kondisi paling sulit untuk pasar."
    if not gdp_growing and (unemp_v or 0) > 7:
        return "KONTRAKSI", "📉", "#FF6B6B", "Ekonomi menyusut, pengangguran naik. Kondisi resesi. Aset safe-haven menguat."
    return "PEMULIHAN", "🌱", "#4FC3F7", "Kontraksi mereda, pertumbuhan mulai kembali. Awal siklus baru — peluang akumulasi."

def macro_bias(pair: str, all_data: dict) -> tuple[str, str, str]:
    cfg = ASSET_PAIRS.get(pair)
    if not cfg:
        return "NEUTRAL", "#FFD93D", "Data tidak tersedia untuk pair ini."

    logic = cfg["bias_logic"]
    countries = cfg["countries"]

    if logic in ("ecb_vs_fed", "boe_vs_fed", "rba_vs_fed", "fed_vs_boj",
                 "fed_vs_pboc", "fed_vs_bi"):
        # base vs quote rate differential
        iso_a, iso_b = countries[0], countries[1]
        cb_a = CB_DATA.get(iso_a, {})
        cb_b = CB_DATA.get(iso_b, {})
        r_a  = cb_a.get("rate", 0)
        r_b  = cb_b.get("rate", 0)
        diff = r_a - r_b

        dm_b = all_data.get(iso_b, {})
        inf_b = dm_b.get("Inflasi", {}).get("val") or 0

        stance_a = cb_a.get("stance","NEUTRAL")
        stance_b = cb_b.get("stance","NEUTRAL")

        if pair in ("EURUSD","GBPUSD","AUDUSD"):
            # quote = USD, base = foreign
            if r_b > r_a and stance_b == "HAWKISH":
                return "BEARISH", "#FF6B6B", f"Rate diferensial menguntungkan USD ({cb_b['name']} hawkish, rate {r_b}%). Tekanan pada base currency. Bias jual {pair}."
            if r_a > r_b or stance_a == "HAWKISH":
                return "BULLISH", "#00FFC8", f"Rate base currency lebih kompetitif vs USD. {cb_a['name']} stance {stance_a}. Bias beli {pair}."
            return "NEUTRAL", "#FFD93D", f"Rate diferensial sempit — {r_a}% vs {r_b}%. Kedua bank sentral neutral. Tunggu katalis."

        if pair == "USDJPY":
            if r_b > 0.5 and stance_b == "HAWKISH":
                return "BEARISH", "#FF6B6B", f"BoJ menaikkan suku bunga ({r_b}%) — JPY menguat. Bias jual USDJPY."
            return "BULLISH", "#00FFC8", f"Fed ({r_a}%) jauh di atas BoJ ({r_b}%). Carry trade USD/JPY masih menarik. Bias beli USDJPY."

        if pair in ("USDCNH","USDIDR"):
            if diff > 2:
                return "BULLISH", "#00FFC8", f"Fed rate ({r_b}%) signifikan di atas {cb_a['name']} ({r_a}%). Tekanan depresiasi pada {pair.replace('USD','')}."
            return "NEUTRAL", "#FFD93D", f"Rate gap mengecil. Monitor stance {cb_b['name']} untuk arah selanjutnya."

    if logic == "gold_usd":
        dm_us = all_data.get("US", {})
        inf_us = dm_us.get("Inflasi", {}).get("val") or 0
        debt_us = dm_us.get("Debt", {}).get("val") or 0
        if inf_us > 3.5 or debt_us > 100:
            return "BULLISH", "#00FFC8", f"Inflasi AS {inf_us:.1f}% dan utang/PDB {debt_us:.0f}% mendukung permintaan safe-haven emas. Bias beli XAUUSD."
        return "NEUTRAL", "#FFD93D", f"Inflasi AS {inf_us:.1f}% terkendali. Emas dalam mode ranging. Tunggu katalis geopolitik atau inflasi."

    if logic == "us_equity":
        dm_us = all_data.get("US", {})
        inf_us = dm_us.get("Inflasi",{}).get("val") or 0
        unemp_us = dm_us.get("Unemp",{}).get("val") or 0
        if inf_us < 4 and unemp_us < 5:
            return "BULLISH", "#00FFC8", f"Makro AS kondusif — inflasi {inf_us:.1f}%, pengangguran {unemp_us:.1f}%. Goldilocks environment untuk ekuitas AS."
        if inf_us > 5:
            return "BEARISH", "#FF6B6B", f"Inflasi AS {inf_us:.1f}% meningkat risiko hawkish Fed — headwind untuk valuasi ekuitas."
        return "NEUTRAL", "#FFD93D", "Makro campuran. Selektif pada sektor defensif dan kualitas earnings."

    if logic == "risk_asset":
        dm_us = all_data.get("US", {})
        inf_us = dm_us.get("Inflasi",{}).get("val") or 0
        if inf_us < 3.5:
            return "BULLISH", "#00FFC8", "Likuiditas membaik, inflasi terkendali — favorable untuk aset risiko termasuk kripto."
        return "BEARISH", "#FF6B6B", f"Inflasi {inf_us:.1f}% menekan ekspektasi likuiditas. Risk-off environment. Waspada volatilitas kripto."

    return "NEUTRAL", "#FFD93D", "Analisis bias tidak tersedia untuk pair ini."

def interpret(name, dm):
    lines = []
    gdp_v  = dm.get("GDP",    {}).get("val")
    inf_v  = dm.get("Inflasi",{}).get("val")
    unemp_v= dm.get("Unemp",  {}).get("val")
    debt_v = dm.get("Debt",   {}).get("val")
    trade_v= dm.get("Trade",  {}).get("val")
    n = name.split()[-1]

    if gdp_v:
        lines.append(f"PDB {n} senilai {gdp_v/1e12:.2f}T USD {'menempatkannya sebagai ekonomi signifikan di kawasan' if gdp_v>5e11 else 'menunjukkan potensi ekspansi yang masih besar'}.")
    if inf_v is not None:
        if inf_v < 2:   lines.append(f"Inflasi {inf_v:.1f}% di bawah target — risiko deflasi perlu dipantau bank sentral.")
        elif inf_v <= 4: lines.append(f"Inflasi {inf_v:.1f}% dalam kisaran sehat — kondusif untuk pertumbuhan.")
        elif inf_v <= 7: lines.append(f"Inflasi {inf_v:.1f}% zona kuning — stance hawkish bank sentral kemungkinan berlanjut.")
        else:            lines.append(f"⚠️ Inflasi {inf_v:.1f}% kritis — tekanan besar pada obligasi dan daya beli.")
    if unemp_v is not None:
        if unemp_v < 4:  lines.append(f"Pengangguran {unemp_v:.1f}% sangat rendah — pasar kerja ketat, potensi tekanan upah.")
        elif unemp_v <= 7: lines.append(f"Pengangguran {unemp_v:.1f}% dalam batas normal.")
        else:              lines.append(f"Pengangguran {unemp_v:.1f}% tinggi — konsumsi domestik berpotensi tertekan.")
    if debt_v is not None:
        if debt_v < 60:   lines.append(f"Rasio utang/PDB {debt_v:.0f}% aman — ruang fiskal luas.")
        elif debt_v <= 90: lines.append(f"Rasio utang/PDB {debt_v:.0f}% mendekati zona waspada IMF.")
        else:              lines.append(f"⚠️ Utang/PDB {debt_v:.0f}% — risiko fiskal tinggi, yield obligasi tertekan naik.")
    if trade_v is not None:
        tv = trade_v/1e9
        lines.append(f"Neraca perdagangan {'surplus' if tv>=0 else 'defisit'} {abs(tv):.1f}B USD — {'tekanan depresiasi terbatas' if tv>=0 else 'potensi tekanan pada nilai tukar'}.")
    return " ".join(lines) if lines else "Data tidak lengkap untuk interpretasi."

# ─── PAGE SECTIONS ────────────────────────────────────────────────────────────

def header():
    st.markdown("""
<div style="padding:0.3rem 0 0.8rem 0;">
<div style="font-family:'Share Tech Mono',monospace;font-size:0.58rem;letter-spacing:.2em;color:#1A2D20;margin-bottom:.2rem;">
AEROVULPIS · PROTOTYPE · ECONOMIC RADAR MODULE
</div>
<div style="font-family:'Share Tech Mono',monospace;font-size:1.5rem;color:#00FFC8;letter-spacing:.06em;line-height:1.1;">
📡 ECONOMIC RADAR
</div>
<div style="font-family:'Exo 2',sans-serif;font-size:0.78rem;color:#374151;margin-top:.25rem;">
Pantau kondisi makroekonomi global · Baca sinyal pasar sebelum pasar bergerak.
</div>
</div>
<hr class="div">
""", unsafe_allow_html=True)

def kpi_section(country_label, iso, dm):
    name = country_label.split(" ",1)[1]
    st.markdown(f'<div class="sec-title">▸ INDIKATOR UTAMA — {name.upper()}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Sumber: World Bank Open Data · Cache 1 jam</div>', unsafe_allow_html=True)

    cols = st.columns(5)
    keys = ["GDP","Inflasi","Unemp","Debt","Trade"]
    for col, key in zip(cols, keys):
        d = dm[key]
        meta = INDICATORS[key]
        v, yr = d["val"], d["year"]
        fv = fmt_val(v, meta["fmt"], meta["unit"])
        rl, rc = risk_cls(key, v)
        yr_str = f"({yr})" if yr else ""
        with col:
            st.markdown(f"""
<div class="kpi" style="--c:{meta['color']};">
<div class="kpi-lbl">{meta['icon']} {meta['label']}</div>
<div class="kpi-val">{fv}</div>
<div class="kpi-yr">{yr_str} {meta['desc']}</div>
<span class="badge {rc}">{rl}</span>
</div>""", unsafe_allow_html=True)

def trend_section(dm):
    st.markdown('<div class="sec-title">▸ TREN HISTORIS (10 TAHUN)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Identifikasi siklus dan momentum makro</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    keys = ["GDP","Inflasi","Unemp","Debt","Trade"]
    for col, key in zip(cols, keys):
        d = dm[key]
        meta = INDICATORS[key]
        with col:
            fig = sparkline(d["series"], meta["color"], meta["label"])
            if fig:
                st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
            else:
                st.markdown(f'<div class="kpi" style="--c:{meta["color"]};text-align:center;"><span style="font-family:\'Share Tech Mono\',monospace;font-size:.6rem;color:#374151;">DATA<br>TIDAK<br>TERSEDIA</span></div>', unsafe_allow_html=True)

def radar_score_section(country_label, dm):
    name = country_label.split(" ",1)[1]
    st.markdown('<div class="sec-title">▸ RADAR MAKRO & MACRO SCORE CARD</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Profil risiko multi-dimensi + skor kesehatan ekonomi 0–100</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.4, 0.9, 1.7])

    with c1:
        keys   = ["GDP","Inflasi","Unemp","Debt","Trade"]
        labels = [INDICATORS[k]["label"] for k in keys]
        vals   = [normalize(k, dm[k]["val"]) for k in keys]
        fig = radar_fig(labels, vals, name)
        st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:.58rem;color:#374151;text-align:center;margin-top:-.5rem;">NORMALISASI 0–100 · {name.upper()}</div>', unsafe_allow_html=True)

    with c2:
        total, grade, gcolor = macro_score(dm)
        bar_w = f"{total:.0f}%"
        st.markdown(f"""
<div class="score-wrap">
<div class="score-num" style="color:{gcolor};">{total:.0f}</div>
<div class="score-lbl">MACRO SCORE</div>
<div class="score-bar"><div class="score-fill" style="width:{bar_w};background:{gcolor};"></div></div>
<span class="badge" style="background:{gcolor}18;color:{gcolor};border:1px solid {gcolor}40;font-size:.62rem;letter-spacing:.12em;">{grade}</span>
</div>
<div style="font-size:.68rem;color:#9CA3AF;margin-top:.8rem;line-height:1.6;text-align:center;">
Skor gabungan dari 5 indikator makro dengan bobot berbeda.<br>
<span style="color:#374151;font-size:.6rem;">72+ STRONG · 55+ STABLE<br>38+ FRAGILE · &lt;38 WEAK</span>
</div>
""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
<div class="ibox" style="--lc:#C77DFF;">
<div class="ibox-t">◈ INTERPRETASI KONDISI MAKRO — {name.upper()}</div>
<div class="ibox-b">{interpret(name, dm)}</div>
</div>
<div class="ibox" style="--lc:#00FFC8;margin-top:.5rem;">
<div class="ibox-t">◈ IMPLIKASI TRADING</div>
<div class="ibox-b">
<b style="color:#00FFC8;">Forex:</b> Divergensi inflasi &amp; suku bunga antar negara = peluang carry trade.<br>
<b style="color:#FFD93D;">Saham:</b> Inflasi rendah + pengangguran rendah = goldilocks untuk ekuitas.<br>
<b style="color:#C77DFF;">Obligasi:</b> Utang tinggi → yield jangka pendek tertekan naik.<br>
<b style="color:#FF6B6B;">Komoditas:</b> Surplus neraca dagang → support mata uang komoditas.
</div>
</div>
""", unsafe_allow_html=True)

def heatmap_section(all_data):
    st.markdown('<div class="sec-title">▸ COUNTRY HEAT MAP RISIKO</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Grid visual 15 negara × 5 indikator · Hijau=Aman · Kuning=Waspada · Merah=Bahaya</div>', unsafe_allow_html=True)

    IND_DISPLAY = ["Inflasi","Pengangguran","Utang/PDB","Neraca Dag.","Macro Score"]

    def cell_class(key, val, score=None):
        if score is not None:
            if score >= 65: return "hm-g"
            if score >= 45: return "hm-y"
            return "hm-r"
        if val is None: return "hm-n"
        th = RISK_THRESH.get(key)
        if th is None:
            tv = val/1e9
            if tv >= 5:  return "hm-g"
            if tv >= 0:  return "hm-y"
            return "hm-r"
        if val <= th["low"]: return "hm-g"
        if val <= th["med"]: return "hm-y"
        return "hm-r"

    def cell_txt(key, val, meta, score=None):
        if score is not None:
            return f"{score:.0f}"
        if val is None: return "N/A"
        if key == "GDP": return f"{val/1e12:.1f}T"
        if key == "Trade": return f"{val/1e9:.0f}B"
        return f"{val:.1f}%"

    # Header row
    hdr_cols = st.columns([1.4] + [1]*5)
    hdr_cols[0].markdown('<div class="hm-hdr" style="text-align:left;">NEGARA</div>', unsafe_allow_html=True)
    for i, lbl in enumerate(IND_DISPLAY):
        hdr_cols[i+1].markdown(f'<div class="hm-hdr">{lbl}</div>', unsafe_allow_html=True)

    for lbl, iso in COUNTRIES.items():
        dm = all_data.get(iso, {})
        inf_v   = dm.get("Inflasi",{}).get("val")
        unemp_v = dm.get("Unemp",  {}).get("val")
        debt_v  = dm.get("Debt",   {}).get("val")
        trade_v = dm.get("Trade",  {}).get("val")
        total, _, _ = macro_score(dm)
        short = lbl.split(" ",1)[1]

        row_cols = st.columns([1.4]+[1]*5)
        row_cols[0].markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:.65rem;color:#D1D5DB;padding:.3rem 0;">{lbl[:2]} {short[:12]}</div>', unsafe_allow_html=True)

        cells = [
            ("Inflasi",  inf_v,   "Inflasi"),
            ("Unemp",    unemp_v, "Pengangguran"),
            ("Debt",     debt_v,  "Debt"),
            ("Trade",    trade_v, "Trade"),
        ]
        for i, (key, val, _) in enumerate(cells):
            cls = cell_class(key, val)
            txt = cell_txt(key, val, INDICATORS[key])
            row_cols[i+1].markdown(f'<div class="hm-cell {cls}">{txt}</div>', unsafe_allow_html=True)

        sc_cls = cell_class(None, None, None, score=total)
        row_cols[5].markdown(f'<div class="hm-cell {sc_cls}">{total:.0f}</div>', unsafe_allow_html=True)

def cb_section(selected_isos):
    st.markdown('<div class="sec-title">▸ CENTRAL BANK POLICY TRACKER</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Stance kebijakan moneter · Carry trade opportunities · Meeting berikutnya</div>', unsafe_allow_html=True)

    stance_map = {
        "HAWKISH": ("hawk", "🦅 HAWKISH"),
        "DOVISH":  ("dove", "🕊️ DOVISH"),
        "NEUTRAL": ("neut", "⚖️ NEUTRAL"),
    }
    trend_cls = {"↑":"trend-u","↓":"trend-d","→":"trend-n"}

    # Sort by rate desc for carry opportunities
    sorted_isos = sorted(selected_isos, key=lambda x: CB_DATA.get(x,{}).get("rate",0), reverse=True)

    cols = st.columns(2)
    for i, iso in enumerate(sorted_isos):
        cb = CB_DATA.get(iso)
        if not cb: continue
        scls, slbl = stance_map.get(cb["stance"], ("neut","⚖️ NEUTRAL"))
        tcls = trend_cls.get(cb["trend"], "trend-n")
        flag = [k for k,v in COUNTRIES.items() if v==iso]
        flag_str = flag[0].split(" ")[0] if flag else ""

        with cols[i % 2]:
            st.markdown(f"""
<div class="cb-row">
<div class="cb-name">{flag_str} {cb['name']}</div>
<div class="cb-rate">{cb['rate']:.2f}%</div>
<span class="cb-hawk {scls}">{slbl}</span>
<span class="cb-hawk neut" style="font-size:.58rem;">TREND <span class="{tcls}">{cb['trend']}</span></span>
<div class="cb-next">📅 {cb['next']}</div>
</div>""", unsafe_allow_html=True)

    # Carry trade matrix
    st.markdown('<div class="sec-sub" style="margin-top:1rem;">💡 TOP CARRY TRADE OPPORTUNITIES (Long High-Rate / Short Low-Rate)</div>', unsafe_allow_html=True)
    sorted_all = sorted(CB_DATA.items(), key=lambda x: x[1]["rate"], reverse=True)
    if len(sorted_all) >= 2:
        top2_high = sorted_all[:3]
        top2_low  = sorted_all[-3:]
        carry_html = '<div style="display:flex;flex-wrap:wrap;gap:.5rem;">'
        for (iso_h, cb_h) in top2_high:
            for (iso_l, cb_l) in top2_low[:2]:
                if iso_h == iso_l: continue
                diff = cb_h["rate"] - cb_l["rate"]
                flag_h = [k for k,v in COUNTRIES.items() if v==iso_h]
                flag_l = [k for k,v in COUNTRIES.items() if v==iso_l]
                fh = flag_h[0].split()[0] if flag_h else ""
                fl = flag_l[0].split()[0] if flag_l else ""
                carry_html += f'<div class="ibox" style="--lc:#00FFC8;flex:1;min-width:180px;"><div class="ibox-t">{fh} vs {fl}</div><div class="ibox-b"><b style="color:#00FFC8;">+{diff:.2f}%</b> spread · Long {cb_h["name"]} / Short {cb_l["name"]}</div></div>'
        carry_html += '</div>'
        st.markdown(carry_html, unsafe_allow_html=True)

def surprise_section(iso):
    events = SURPRISE_DATA.get(iso, [])
    flag = [k for k,v in COUNTRIES.items() if v==iso]
    name = flag[0].split(" ",1)[1] if flag else iso

    st.markdown('<div class="sec-title">▸ ECONOMIC SURPRISE INDEX</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Aktual vs Konsensus Forecast · Divergensi = potensi volatilitas pasar</div>', unsafe_allow_html=True)

    if not events:
        st.markdown('<div class="ibox" style="--lc:#374151;"><div class="ibox-b">Data surprise tidak tersedia untuk negara ini.</div></div>', unsafe_allow_html=True)
        return

    cols = st.columns(len(events))
    for col, (evt_name, actual, forecast, date) in zip(cols, events):
        diff = actual - forecast
        pct  = diff / max(abs(forecast), 0.001) * 100
        beat = diff > 0
        bar_color = "#00FFC8" if beat else "#FF6B6B"
        bar_w  = min(abs(pct)*2, 100)
        status = f"BEAT +{diff:.2f}" if beat else f"MISS {diff:.2f}"
        scls   = "b-low" if beat else "b-high"

        with col:
            st.markdown(f"""
<div class="surp-item">
<div class="surp-name">{evt_name}</div>
<div style="font-size:.58rem;color:#374151;font-family:'Share Tech Mono',monospace;">{date}</div>
<div class="surp-bar-wrap">
<div class="surp-bar" style="width:{bar_w:.0f}%;background:{bar_color};"></div>
</div>
<div class="surp-nums">
<span style="color:{bar_color};">{actual}</span>
<span>est {forecast}</span>
</div>
<span class="badge {scls}" style="margin-top:.3rem;font-size:.54rem;">{status}</span>
</div>""", unsafe_allow_html=True)

    # Aggregate surprise score
    total_surprise = sum(
        (a - f) / max(abs(f), 0.001) * 100
        for _, a, f, _ in events
    )
    avg = total_surprise / len(events)
    agg_color = "#00FFC8" if avg > 0 else "#FF6B6B"
    agg_label = f"MACRO BEAT +{avg:.1f}%" if avg > 0 else f"MACRO MISS {avg:.1f}%"

    st.markdown(f"""
<div class="ibox" style="--lc:{agg_color};margin-top:.5rem;">
<div class="ibox-t">◈ AGGREGATE SURPRISE — {name.upper()}</div>
<div class="ibox-b">
<b style="color:{agg_color};">{agg_label}</b><br>
{"Data ekonomi secara keseluruhan lebih baik dari ekspektasi — potensi penguatan mata uang dan aset domestik." if avg > 0
 else "Data ekonomi secara keseluruhan di bawah ekspektasi — tekanan pada mata uang dan aset risiko domestik."}
</div>
</div>
""", unsafe_allow_html=True)

def cycle_section(all_data, selected_labels):
    st.markdown('<div class="sec-title">▸ SIKLUS EKONOMI DETECTOR</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Klasifikasi posisi siklus: Ekspansi · Puncak · Stagflasi · Kontraksi · Pemulihan</div>', unsafe_allow_html=True)

    cols = st.columns(min(len(selected_labels), 5))
    for col, lbl in zip(cols, selected_labels[:5]):
        iso = COUNTRIES[lbl]
        dm  = all_data.get(iso, {})
        cycle, icon, color, desc = detect_cycle(dm)
        flag = lbl.split(" ")[0]
        name = lbl.split(" ",1)[1]
        with col:
            st.markdown(f"""
<div class="cycle-card">
<div style="font-size:1.5rem;">{icon}</div>
<div class="cycle-lbl">{flag} {name[:12]}</div>
<div class="cycle-val" style="color:{color};">{cycle}</div>
<div class="cycle-sub">{desc}</div>
</div>""", unsafe_allow_html=True)

    # Siklus → rotasi sektor
    st.markdown("""
<div class="ibox" style="--lc:#4FC3F7;margin-top:.8rem;">
<div class="ibox-t">◈ PANDUAN ROTASI SEKTOR PER FASE SIKLUS</div>
<div class="ibox-b">
<b style="color:#00FFC8;">🚀 Ekspansi:</b> Overweight Teknologi, Diskresi Konsumen, Industri. Underweight Utilities.<br>
<b style="color:#FFD93D;">🌡️ Puncak:</b> Rotasi ke Energi, Material, Staples. Kurangi durasi obligasi.<br>
<b style="color:#FF6B6B;">📉 Kontraksi:</b> Pindah ke Utilities, Healthcare, Obligasi Pemerintah, Emas.<br>
<b style="color:#4FC3F7;">🌱 Pemulihan:</b> Akumulasi Keuangan, Industri, Small-cap. Tingkatkan risk appetite.
</div>
</div>
""", unsafe_allow_html=True)

def bias_section(all_data):
    st.markdown('<div class="sec-title">▸ MACRO BIAS SCANNER</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Filter konteks fundamental per aset · Jangan trade melawan makro</div>', unsafe_allow_html=True)

    pair = st.selectbox("Pilih Pair / Aset", list(ASSET_PAIRS.keys()), key="bias_pair")
    bias, bcolor, btext = macro_bias(pair, all_data)
    bias_cls = {"BULLISH":"bias-bull","BEARISH":"bias-bear","NEUTRAL":"bias-neut"}[bias]

    # Collect relevant countries
    cfg = ASSET_PAIRS[pair]
    relevant_isos = cfg["countries"]

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"""
<div class="bias-card">
<div class="bias-pair">{pair}</div>
<div class="bias-val {bias_cls}">{'🟢' if bias=='BULLISH' else '🔴' if bias=='BEARISH' else '🟡'} {bias}</div>
<div class="bias-txt">{btext}</div>
</div>""", unsafe_allow_html=True)

        # CB stances for relevant countries
        st.markdown('<div style="margin-top:.5rem;">', unsafe_allow_html=True)
        for iso in relevant_isos:
            cb = CB_DATA.get(iso,{})
            if cb:
                flag = [k for k,v in COUNTRIES.items() if v==iso]
                fstr = flag[0].split()[0] if flag else ""
                scls = {"HAWKISH":"hawk","DOVISH":"dove","NEUTRAL":"neut"}.get(cb["stance"],"neut")
                st.markdown(f'<div style="margin:.3rem 0;"><span style="font-family:\'Share Tech Mono\',monospace;font-size:.62rem;color:#D1D5DB;">{fstr} {cb["name"]}: </span><span class="cb-hawk {scls}">{cb["stance"]}</span> <span style="font-family:\'Share Tech Mono\',monospace;font-size:.7rem;color:#00FFC8;"> {cb["rate"]:.2f}%</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        # Relevant indicators chart
        driver_keys = cfg["drivers"]
        if len(relevant_isos) >= 2:
            iso_a, iso_b = relevant_isos[0], relevant_isos[1]
            for dk in driver_keys[:2]:
                dm_a = all_data.get(iso_a,{}).get(dk,{})
                dm_b = all_data.get(iso_b,{}).get(dk,{})
                ser_a = dm_a.get("series",[])
                ser_b = dm_b.get("series",[])
                if ser_a and ser_b:
                    fig = go.Figure()
                    flag_a = [k for k,v in COUNTRIES.items() if v==iso_a]
                    flag_b = [k for k,v in COUNTRIES.items() if v==iso_b]
                    n_a = flag_a[0].split()[0]+" "+flag_a[0].split(" ",1)[1][:8] if flag_a else iso_a
                    n_b = flag_b[0].split()[0]+" "+flag_b[0].split(" ",1)[1][:8] if flag_b else iso_b
                    fig.add_trace(go.Scatter(x=[d["year"] for d in ser_a], y=[d["value"] for d in ser_a],
                        mode="lines", name=n_a, line=dict(color="#00FFC8",width=2)))
                    fig.add_trace(go.Scatter(x=[d["year"] for d in ser_b], y=[d["value"] for d in ser_b],
                        mode="lines", name=n_b, line=dict(color="#FF6B6B",width=2)))
                    fig.update_layout(**BASE_LAYOUT,
                        title=dict(text=f"{INDICATORS[dk]['label']} — {n_a} vs {n_b}", font=dict(size=9.5,color="#4A9EBF"),x=0),
                        legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(size=8)),
                        margin=dict(l=8,r=8,t=28,b=8))
                    fig.update_xaxes(tickformat="d")
                    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
        elif relevant_isos:
            iso_a = relevant_isos[0]
            for dk in driver_keys[:2]:
                dm_a = all_data.get(iso_a,{}).get(dk,{})
                ser_a = dm_a.get("series",[])
                if ser_a:
                    fig = sparkline(ser_a, INDICATORS[dk]["color"], INDICATORS[dk]["label"])
                    if fig: st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

def compare_section(all_data, compare_labels, main_label):
    st.markdown('<div class="sec-title">▸ PERBANDINGAN MULTI-NEGARA</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Benchmark posisi makro antar ekonomi</div>', unsafe_allow_html=True)

    all_labels  = [main_label] + compare_labels
    all_isos    = [COUNTRIES[l] for l in all_labels]
    short_names = [l.split(" ",1)[1][:12] for l in all_labels]

    ind_select = st.selectbox("Indikator", list(INDICATORS.keys()), index=1, key="cmp_ind")
    meta = INDICATORS[ind_select]

    vals = []
    for iso in all_isos:
        v, _ = latest(all_data.get(iso,{}).get(ind_select,{}).get("series",[]))
        if ind_select == "GDP": vals.append(v/1e12 if v else 0)
        elif ind_select == "Trade": vals.append(v/1e9 if v else 0)
        else: vals.append(v if v else 0)

    fig = bar_fig(short_names, vals, meta["color"], meta["label"])
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)

    # Full comparison table
    st.markdown('<div class="sec-sub">Tabel lengkap semua indikator</div>', unsafe_allow_html=True)
    rows = []
    for lbl, iso in zip(all_labels, all_isos):
        dm = all_data.get(iso, {})
        total, grade, _ = macro_score(dm)
        row = {"Negara": lbl.split(" ",1)[1]}
        for key, meta2 in INDICATORS.items():
            v, _ = latest(dm.get(key,{}).get("series",[]))
            row[meta2["label"]] = fmt_val(v, meta2["fmt"], meta2["unit"])
        row["Macro Score"] = f"{total:.0f} ({grade})"
        rows.append(row)
    df = pd.DataFrame(rows).set_index("Negara")
    st.dataframe(df, use_container_width=True)

def calendar_section():
    st.markdown('<div class="sec-title">▸ KALENDER EKONOMI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Event makro berdampak tinggi · September 2026</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1,3])
    with c1:
        impact_f = st.radio("Filter", ["SEMUA","🔴 TINGGI","🟡 SEDANG"], key="cal_f")
    with c2:
        country_f = st.multiselect("Negara", list(set(e["country"] for e in CALENDAR_EVENTS)), key="cal_country")

    imp_cls = {"HIGH":"imp-h","MEDIUM":"imp-m","LOW":"imp-l"}
    imp_lbl = {"HIGH":"🔴 HIGH","MEDIUM":"🟡 MED","LOW":"🔵 LOW"}

    for ev in CALENDAR_EVENTS:
        if impact_f == "🔴 TINGGI" and ev["impact"] != "HIGH": continue
        if impact_f == "🟡 SEDANG" and ev["impact"] not in ("HIGH","MEDIUM"): continue
        if country_f and ev["country"] not in country_f: continue
        ic = imp_cls.get(ev["impact"],"imp-l")
        il = imp_lbl.get(ev["impact"],"🔵 LOW")
        st.markdown(f"""
<div class="cal-item">
<div class="cal-dt">{ev['date']}</div>
<div class="cal-ctr">{ev['country']}</div>
<div style="flex:1;">
<div class="cal-evt">{ev['event']}</div>
<div class="cal-nums">Est: <b>{ev['est']}</b> · Prev: {ev['prev']}</div>
</div>
<span class="{ic}">{il}</span>
</div>""", unsafe_allow_html=True)

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    inject_css()
    header()

    # ── Controls ──────────────────────────────────────────────────────────────
    ctrl_c1, ctrl_c2, ctrl_c3 = st.columns([1.2, 2, 0.8])
    with ctrl_c1:
        main_label = st.selectbox("🌏 Negara Utama", list(COUNTRIES.keys()), key="main_country")
    with ctrl_c2:
        compare_labels = st.multiselect(
            "📊 Bandingkan (maks 5)",
            [k for k in COUNTRIES if k != main_label],
            default=["🇺🇸 Amerika Serikat","🇨🇳 China"],
            max_selections=5, key="compare_countries"
        )
    with ctrl_c3:
        st.markdown('<div style="height:1.6rem;"></div>', unsafe_allow_html=True)
        run_btn = st.button("🔄 Refresh Data", use_container_width=True)
        if run_btn:
            st.cache_data.clear()

    main_iso  = COUNTRIES[main_label]
    all_isos  = list(set([main_iso] + [COUNTRIES[l] for l in compare_labels] + list(COUNTRIES.values())))

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "📊 Overview",
        "🌡️ Heat Map",
        "🧭 Bias Scanner",
        "⚡ Surprise Index",
        "🔄 Siklus Ekonomi",
        "🏦 Central Banks",
        "📅 Kalender",
        "📈 Perbandingan",
    ])

    # ── Fetch all data ─────────────────────────────────────────────────────────
    with st.spinner("Mengambil data dari World Bank…"):
        all_data: dict[str, dict] = {}
        for iso in all_isos:
            all_data[iso] = {}
            for key, meta in INDICATORS.items():
                series = fetch_wb(iso, meta["code"])
                v, yr = latest(series)
                all_data[iso][key] = {"val": v, "year": yr, "series": series}

    main_dm = all_data[main_iso]

    # ── TAB 1: Overview ────────────────────────────────────────────────────────
    with tabs[0]:
        kpi_section(main_label, main_iso, main_dm)
        st.markdown('<hr class="div">', unsafe_allow_html=True)
        trend_section(main_dm)
        st.markdown('<hr class="div">', unsafe_allow_html=True)
        radar_score_section(main_label, main_dm)

    # ── TAB 2: Heat Map ────────────────────────────────────────────────────────
    with tabs[1]:
        heatmap_section(all_data)

    # ── TAB 3: Bias Scanner ────────────────────────────────────────────────────
    with tabs[2]:
        bias_section(all_data)

    # ── TAB 4: Surprise Index ──────────────────────────────────────────────────
    with tabs[3]:
        surprise_section(main_iso)
        st.markdown('<hr class="div">', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">PILIH NEGARA LAIN UNTUK SURPRISE INDEX</div>', unsafe_allow_html=True)
        other_iso_lbl = st.selectbox("Negara Surprise", list(COUNTRIES.keys()), index=1, key="surp_country")
        if other_iso_lbl != main_label:
            surprise_section(COUNTRIES[other_iso_lbl])

    # ── TAB 5: Siklus ──────────────────────────────────────────────────────────
    with tabs[4]:
        all_selected = [main_label] + compare_labels
        cycle_section(all_data, all_selected)

    # ── TAB 6: Central Banks ───────────────────────────────────────────────────
    with tabs[5]:
        cb_selected = [main_iso] + [COUNTRIES[l] for l in compare_labels] + ["US","CN","JP","DE"]
        cb_section(list(dict.fromkeys(cb_selected)))

    # ── TAB 7: Kalender ────────────────────────────────────────────────────────
    with tabs[6]:
        calendar_section()

    # ── TAB 8: Perbandingan ────────────────────────────────────────────────────
    with tabs[7]:
        if compare_labels:
            compare_section(all_data, compare_labels, main_label)
        else:
            st.markdown('<div class="ibox" style="--lc:#374151;"><div class="ibox-b">Pilih minimal 1 negara pembanding di bagian atas.</div></div>', unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="footer">
<span>AEROVULPIS · ECONOMIC RADAR PROTOTYPE · BUILD STABLE 29 AUG 2026</span>
<span>SUMBER: WORLD BANK OPEN DATA · DATA CACHE 1 JAM</span>
<span>STANDALONE — BERDIRI SENDIRI · TIDAK PERLU FILE LAIN</span>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()