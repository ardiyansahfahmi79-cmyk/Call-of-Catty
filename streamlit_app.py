"""
market_sessions_page.py — Aerovulpis · Market Sessions (Standalone Prototype)
Run : streamlit run market_sessions_page.py
Deps: streamlit plotly pandas (zoneinfo stdlib)
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, time as dtime, timedelta
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Market Sessions · Aerovulpis",
    page_icon="🕐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION DATA (local open/close + pytz → akurat ke WIB, termasuk DST)
# ══════════════════════════════════════════════════════════════════════════════

SESSIONS = [
    {
        "id": "sydney",
        "name": "SYDNEY",
        "region": "PACIFIC",
        "city": "Sydney",
        "tz": "Australia/Sydney",
        "open_local": 8,
        "close_local": 17,
        "color": "#00FFC8",
        "vol": "LOW",
        "vol_pct": 8,
        "share": "5%",
        "desc": "Sesi pembuka minggu. Volume rendah, spread lebar. Fokus pada AUD, NZD, dan JPY.",
        "pairs": ["AUD/USD", "NZD/USD", "AUD/JPY", "AUD/NZD", "USD/JPY"],
        "strategy": "Range trading — breakout jarang terjadi. Spread lebih lebar, gunakan limit order.",
        "risk": "Likuiditas rendah = slippage lebih besar. Hindari market order pada pair minor.",
        "news_focus": ["RBA statement", "AU Employment", "NZ CPI", "China PMI"],
    },
    {
        "id": "tokyo",
        "name": "TOKYO",
        "region": "ASIA",
        "city": "Tokyo",
        "tz": "Asia/Tokyo",
        "open_local": 9,
        "close_local": 18,
        "color": "#C77DFF",
        "vol": "MEDIUM",
        "vol_pct": 21,
        "share": "21%",
        "desc": "Sesi Asia dengan volume signifikan. JPY mendominasi. BoJ sering merilis statement.",
        "pairs": ["USD/JPY", "EUR/JPY", "GBP/JPY", "AUD/JPY", "USD/SGD", "USD/CNH"],
        "strategy": "Trend-following pada JPY pairs. Range bound untuk EUR/USD dan GBP/USD.",
        "risk": "Berita BoJ bisa memicu spike tiba-tiba pada JPY. Gunakan SL lebih lebar.",
        "news_focus": ["BoJ Rate Decision", "Tokyo CPI", "Japan GDP", "China Trade Balance"],
    },
    {
        "id": "london",
        "name": "LONDON",
        "region": "EUROPE",
        "city": "London",
        "tz": "Europe/London",
        "open_local": 8,
        "close_local": 17,
        "color": "#FF9F43",
        "vol": "HIGH",
        "vol_pct": 85,
        "share": "38%",
        "desc": "Sesi terbesar — ~38% volume forex harian. EUR, GBP, CHF paling aktif. Trend harian sering dimulai di sini.",
        "pairs": ["EUR/USD", "GBP/USD", "EUR/GBP", "USD/CHF", "EUR/CHF", "EUR/JPY", "GBP/JPY"],
        "strategy": "Breakout dan trend-following. London Open Breakout adalah strategi klasik institusional.",
        "risk": "Volatilitas tinggi di open. Spread bisa melebar sesaat saat open.",
        "news_focus": ["ECB Rate", "UK CPI", "Eurozone GDP", "PMI Manufacturing", "German IFO"],
    },
    {
        "id": "newyork",
        "name": "NEW YORK",
        "region": "AMERICA",
        "city": "New York",
        "tz": "America/New_York",
        "open_local": 8,
        "close_local": 17,
        "color": "#FF6B6B",
        "vol": "HIGH",
        "vol_pct": 78,
        "share": "17%",
        "desc": "Volume US terbesar. USD mendominasi semua pair. Data NFP dan FOMC paling market-moving.",
        "pairs": ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CAD", "USD/CHF", "XAU/USD"],
        "strategy": "News trading dan momentum. NFP Friday, CPI, FOMC = event volatilitas ekstrem.",
        "risk": "Reversal mendadak umum terjadi saat data AS dirilis. Jangan hold posisi tanpa SL.",
        "news_focus": ["FOMC Decision", "NFP", "US CPI", "Retail Sales", "GDP", "Fed Speak"],
    },
]

# Overlap windows — dihitung dinamis dari sesi lokal (DST-aware)
OVERLAPS = [
    {
        "name": "TOKYO / LONDON OVERLAP",
        "session_ids": ("tokyo", "london"),
        "color": "#FFD93D",
        "label": "POWER ZONE I",
        "desc": "Overlap singkat — JPY crosses paling aktif. EUR/JPY dan GBP/JPY sering breakout.",
        "vol": "HIGH",
    },
    {
        "name": "LONDON / NEW YORK OVERLAP",
        "session_ids": ("london", "newyork"),
        "color": "#FF6B6B",
        "label": "POWER ZONE II",
        "desc": "4 jam paling volatile dalam sehari — 70%+ volume harian terkonsentrasi di sini. Spread terkecil, likuiditas terbesar.",
        "vol": "EXTREME",
    },
]

SESSION_PAIR_DATA = {
    "sydney": {
        "typical_range_pips": {"AUD/USD": 40, "NZD/USD": 35, "USD/JPY": 30, "AUD/JPY": 45, "AUD/NZD": 25},
        "spread_condition": "WIDE",
        "institutional_activity": "LOW",
        "best_strategy": "RANGE",
    },
    "tokyo": {
        "typical_range_pips": {"USD/JPY": 55, "EUR/JPY": 60, "GBP/JPY": 70, "AUD/JPY": 50, "USD/CNH": 45},
        "spread_condition": "NORMAL",
        "institutional_activity": "MEDIUM",
        "best_strategy": "TREND (JPY), RANGE (EUR/USD)",
    },
    "london": {
        "typical_range_pips": {"EUR/USD": 80, "GBP/USD": 100, "EUR/GBP": 60, "EUR/JPY": 110, "GBP/JPY": 130},
        "spread_condition": "TIGHT",
        "institutional_activity": "VERY HIGH",
        "best_strategy": "BREAKOUT / TREND",
    },
    "newyork": {
        "typical_range_pips": {"EUR/USD": 70, "GBP/USD": 90, "USD/JPY": 65, "USD/CAD": 60, "XAU/USD": 1200},
        "spread_condition": "TIGHT",
        "institutional_activity": "HIGH",
        "best_strategy": "NEWS / MOMENTUM",
    },
}

# Volatilitas relatif per jam WIB (0-100) — berdasarkan pola historis
HOURLY_VOLATILITY = {
    0: 10, 1: 8, 2: 6, 3: 5, 4: 5, 5: 12, 6: 18, 7: 30,
    8: 38, 9: 42, 10: 40, 11: 38, 12: 35, 13: 32, 14: 30,
    15: 75, 16: 80, 17: 78, 18: 72, 19: 68, 20: 88,
    21: 95, 22: 92, 23: 85,
}

# ══════════════════════════════════════════════════════════════════════════════
#  TIME ENGINE — semua output dalam WIB
# ══════════════════════════════════════════════════════════════════════════════

WIB = ZoneInfo("Asia/Jakarta")

def now_wib() -> datetime:
    return datetime.now(WIB)

def wib_hour_float() -> float:
    n = now_wib()
    return n.hour + n.minute / 60.0

def session_wib_window(s: dict, reference: datetime | None = None) -> tuple[float, float]:
    """Hitung window sesi hari ini dalam jam float WIB (bisa >24 jika melewati midnight)."""
    reference_wib = (reference or now_wib()).astimezone(WIB)
    local_tz = ZoneInfo(s["tz"])
    local_date = reference_wib.astimezone(local_tz).date()

    local_open = datetime.combine(local_date, dtime(hour=s["open_local"]), tzinfo=local_tz)
    if s["close_local"] <= s["open_local"]:
        close_date = local_date + timedelta(days=1)
    else:
        close_date = local_date
    local_close = datetime.combine(close_date, dtime(hour=s["close_local"]), tzinfo=local_tz)

    open_wib = local_open.astimezone(WIB)
    close_wib = local_close.astimezone(WIB)

    base_date = open_wib.date()
    open_hour = open_wib.hour + open_wib.minute / 60.0
    close_hour = (
        (close_wib.date() - base_date).days * 24
        + close_wib.hour
        + close_wib.minute / 60.0
    )
    return open_hour, close_hour

def session_active(s: dict, h: float) -> bool:
    o, c = session_wib_window(s)
    if c > 24:
        return h >= o or h < (c - 24)
    return o <= h < c

def session_progress(s: dict, h: float) -> float:
    o, c = session_wib_window(s)
    duration = c - o
    if duration <= 0:
        return 0.0
    if c > 24:
        elapsed = (h - o) % 24
    else:
        elapsed = h - o
    return max(0.0, min(1.0, elapsed / duration))

def resolved_overlap(ov: dict, reference: datetime | None = None) -> dict:
    if not ov.get("session_ids"):
        return dict(ov)
    windows = {
        sid: session_wib_window(next(s for s in SESSIONS if s["id"] == sid), reference)
        for sid in ov["session_ids"]
    }
    starts = [windows[sid][0] for sid in ov["session_ids"]]
    ends = [windows[sid][1] for sid in ov["session_ids"]]
    return {**ov, "start": max(starts), "end": min(ends)}

def resolved_overlaps(reference: datetime | None = None) -> list[dict]:
    return [resolved_overlap(ov, reference) for ov in OVERLAPS]

def overlap_active(ov: dict, h: float) -> bool:
    current = resolved_overlap(ov)
    s, e = current["start"], current["end"]
    if e <= s:  # invalid
        return False
    if e > 24:
        return h >= s or h < (e - 24)
    return s <= h < e

def time_until_open(s: dict, h: float) -> str:
    if session_active(s, h):
        return "ACTIVE"
    o, _ = session_wib_window(s)
    diff = (o - h) % 24
    hrs = int(diff)
    mins = int((diff - hrs) * 60)
    return f"OPENS IN {hrs:02d}h {mins:02d}m"

def city_local_time(tz_name: str) -> str:
    try:
        tz = ZoneInfo(tz_name)
        return datetime.now(tz).strftime("%H:%M")
    except Exception:
        return "--:--"

def fmt_wib_range(o: float, c: float) -> str:
    """Format range jam WIB, handle midnight wrap."""
    def hh(v):
        v = v % 24
        return f"{int(v):02d}:{int((v % 1) * 60):02d}"
    return f"{hh(o)} – {hh(c)} WIB"

# ══════════════════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════════════════

def css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

html,body,.stApp{background:#080B12!important;}
.block-container{padding:1rem 1.5rem 3rem!important;max-width:100%!important;}
*{box-sizing:border-box;}
body{font-family:'Exo 2',sans-serif;}

.aero-build{font-family:'Share Tech Mono',monospace;font-size:.55rem;letter-spacing:.25em;color:#0F3028;margin-bottom:.3rem;}
.aero-title{font-family:'Share Tech Mono',monospace;font-size:1.6rem;color:#00FFC8;letter-spacing:.06em;line-height:1;}
.aero-sub{font-size:.72rem;color:#8EA3B8;margin-top:.25rem;font-family:'Share Tech Mono',monospace;letter-spacing:.08em;}

.sec-title{font-family:'Share Tech Mono',monospace;color:#00FFC8;font-size:.78rem;
    letter-spacing:.22em;border-left:2px solid #00FFC8;padding-left:.7rem;
    margin:1.5rem 0 .2rem;text-transform:uppercase;}
.sec-sub{font-family:'Share Tech Mono',monospace;color:#8298AD;font-size:.56rem;
    letter-spacing:.12em;margin-bottom:.8rem;padding-left:.9rem;}
.hr{border:none;border-top:1px solid #0E1826;margin:.8rem 0;}

.clock-wrap{text-align:center;padding:.5rem 0 .8rem;}
.clock-time{font-family:'Share Tech Mono',monospace;font-size:2.8rem;
    color:#00FFC8;letter-spacing:.1em;line-height:1;}
.clock-date{font-family:'Share Tech Mono',monospace;font-size:.6rem;
    color:#87A0B7;letter-spacing:.18em;margin-top:.2rem;}
.clock-label{font-family:'Share Tech Mono',monospace;font-size:.52rem;
    color:#7F95AA;letter-spacing:.2em;}

.city-clocks{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1rem;}
.city-clock{background:#0A1018;border:1px solid #141E2D;border-radius:2px;
    padding:.5rem .7rem;flex:1;min-width:100px;text-align:center;position:relative;overflow:hidden;}
.city-clock-accent{position:absolute;bottom:0;left:0;right:0;height:1px;background:var(--cc,#00FFC8);}
.city-clock-name{font-family:'Share Tech Mono',monospace;font-size:.58rem;
    color:#B7C7D9;letter-spacing:.12em;margin-bottom:.2rem;font-weight:700;}
.city-clock-time{font-family:'Share Tech Mono',monospace;font-size:1.1rem;
    font-weight:700;color:var(--cc,#00FFC8);line-height:1;}
.city-clock-status{font-family:'Share Tech Mono',monospace;font-size:.48rem;
    margin-top:.2rem;padding:1px 5px;border-radius:1px;display:inline-block;}
.cs-active{background:rgba(0,255,200,.08);color:#00FFC8;border:1px solid #00FFC830;}
.cs-closed{background:rgba(30,42,58,.7);color:#8298AD;border:1px solid #26384A;}

.sess-card{background:linear-gradient(160deg,#0A1018 0%,#0C1220 100%);
    border:1px solid #141E2D;border-radius:3px;padding:1rem 1.1rem;
    position:relative;overflow:hidden;margin-bottom:.5rem;}
.sess-card-active{border-color:var(--sc,#00FFC8);box-shadow:0 0 12px var(--sc,#00FFC8)18;}
.sess-left-bar{position:absolute;left:0;top:0;bottom:0;width:2px;background:var(--sc,#00FFC8);}
.sess-header{display:flex;align-items:flex-start;gap:.6rem;flex-wrap:wrap;margin-bottom:.6rem;}
.sess-name{font-family:'Share Tech Mono',monospace;font-size:1rem;font-weight:700;
    color:var(--sc,#00FFC8);letter-spacing:.12em;}
.sess-region{font-family:'Share Tech Mono',monospace;font-size:.55rem;
    color:#1A3040;letter-spacing:.15em;margin-top:.15rem;}
.sess-time{font-family:'Share Tech Mono',monospace;font-size:.62rem;color:#2D4050;}
.sess-status-active{font-family:'Share Tech Mono',monospace;font-size:.55rem;
    padding:2px 8px;border-radius:1px;font-weight:700;
    background:rgba(0,255,200,.1);color:#00FFC8;border:1px solid #00FFC840;}
.sess-status-closed{font-family:'Share Tech Mono',monospace;font-size:.55rem;
    padding:2px 8px;border-radius:1px;font-weight:700;
    background:rgba(30,42,58,.5);color:#2D4050;border:1px solid #141E2D;}
.sess-countdown{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:#2D5040;margin-left:auto;}

.prog-wrap{margin:.5rem 0;}
.prog-track{height:4px;background:#0E1826;border-radius:2px;position:relative;}
.prog-fill{height:4px;border-radius:2px;}
.prog-pct{font-family:'Share Tech Mono',monospace;font-size:.52rem;
    color:var(--sc,#00FFC8);text-align:right;margin-top:.2rem;}

.sess-body{display:grid;grid-template-columns:1fr 1fr;gap:.6rem;margin-top:.6rem;}
.sess-info-block{background:#080B12;border:1px solid #0E1826;border-radius:2px;padding:.5rem .65rem;}
.sib-label{font-family:'Share Tech Mono',monospace;font-size:.5rem;color:#1A2D3A;
    letter-spacing:.12em;margin-bottom:.25rem;text-transform:uppercase;}
.sib-val{font-family:'Share Tech Mono',monospace;font-size:.62rem;color:#4A6070;line-height:1.5;}
.sib-val b{color:#00FFC8;}

.vol-low   {display:inline-block;font-family:'Share Tech Mono',monospace;font-size:.5rem;padding:1px 6px;
    border-radius:1px;font-weight:700;background:rgba(74,158,191,.08);color:#4FC3F7;border:1px solid #4FC3F730;}
.vol-med   {display:inline-block;font-family:'Share Tech Mono',monospace;font-size:.5rem;padding:1px 6px;
    border-radius:1px;font-weight:700;background:rgba(255,217,61,.08);color:#FFD93D;border:1px solid #FFD93D30;}
.vol-high  {display:inline-block;font-family:'Share Tech Mono',monospace;font-size:.5rem;padding:1px 6px;
    border-radius:1px;font-weight:700;background:rgba(255,107,107,.08);color:#FF6B6B;border:1px solid #FF6B6B30;}
.vol-ext   {display:inline-block;font-family:'Share Tech Mono',monospace;font-size:.5rem;padding:1px 6px;
    border-radius:1px;font-weight:700;background:rgba(255,159,67,.15);color:#FF9F43;border:1px solid #FF9F4360;}

.pair-tag{display:inline-block;font-family:'Share Tech Mono',monospace;font-size:.52rem;
    padding:2px 6px;border-radius:1px;background:#0E1826;color:var(--sc,#00FFC8);
    border:1px solid #1A2D3A;margin:.15rem .1rem;}

.ov-card{background:#0A1018;border:1px solid #141E2D;border-radius:2px;
    padding:.75rem .9rem;margin-bottom:.4rem;position:relative;overflow:hidden;}
.ov-card-accent{position:absolute;top:0;left:0;right:0;height:1px;background:var(--oc,#FFD93D);}
.ov-header{display:flex;align-items:center;gap:.6rem;margin-bottom:.35rem;flex-wrap:wrap;}
.ov-name{font-family:'Share Tech Mono',monospace;font-size:.72rem;
    font-weight:700;color:var(--oc,#FFD93D);letter-spacing:.08em;}
.ov-label{font-family:'Share Tech Mono',monospace;font-size:.52rem;
    padding:1px 7px;border-radius:1px;font-weight:700;
    background:rgba(255,217,61,.08);color:#FFD93D;border:1px solid #FFD93D30;}
.ov-time{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:#2D4050;margin-left:auto;}
.ov-desc{font-size:.7rem;color:#3A5060;line-height:1.6;}
.ov-active-badge{background:rgba(255,159,67,.12);color:#FF9F43;border:1px solid #FF9F4340;
    font-family:'Share Tech Mono',monospace;font-size:.5rem;padding:1px 6px;border-radius:1px;font-weight:700;}

.strat-card{background:#0A1018;border:1px solid #141E2D;border-radius:2px;
    padding:.65rem .8rem;margin-bottom:.35rem;}
.strat-header{font-family:'Share Tech Mono',monospace;font-size:.6rem;
    color:#00FFC8;letter-spacing:.12em;margin-bottom:.3rem;}
.strat-body{font-size:.72rem;color:#3A5060;line-height:1.65;}

.range-table{width:100%;border-collapse:separate;border-spacing:0 2px;}
.range-th{font-family:'Share Tech Mono',monospace;font-size:.5rem;color:#1A3040;
    letter-spacing:.1em;padding:.25rem .4rem;text-align:left;}
.range-td{font-family:'Share Tech Mono',monospace;font-size:.6rem;color:#4A6070;
    background:#0A1018;border:1px solid #0E1826;padding:.25rem .4rem;border-radius:1px;}
.range-td-pair{color:#00FFC8;}
.range-td-pips{color:#FFD93D;text-align:right;}

.heat-wrap{display:flex;gap:2px;align-items:flex-end;height:60px;margin:.5rem 0;}
.heat-bar{flex:1;border-radius:1px 1px 0 0;min-width:3px;}
.heat-labels{display:flex;justify-content:space-between;
    font-family:'Share Tech Mono',monospace;font-size:.45rem;color:#1A2D3A;margin-top:.2rem;}

.ibox{background:#0A1018;border:1px solid #141E2D;border-left:2px solid var(--lc,#C77DFF);
    border-radius:0 2px 2px 0;padding:.7rem .9rem;margin:.4rem 0;}
.ibox-t{font-family:'Share Tech Mono',monospace;font-size:.56rem;color:var(--lc,#C77DFF);
    letter-spacing:.14em;margin-bottom:.35rem;text-transform:uppercase;}
.ibox-b{font-size:.72rem;color:#4A6070;line-height:1.7;}

.tip-row{display:flex;gap:.5rem;align-items:flex-start;
    padding:.45rem .6rem;border-bottom:1px solid #0E1826;}
.tip-row:last-child{border-bottom:none;}
.tip-num{font-family:'Share Tech Mono',monospace;font-size:.55rem;
    color:#1A3040;min-width:22px;}
.tip-txt{font-size:.7rem;color:#3A5060;line-height:1.55;flex:1;}
.tip-txt b{color:#00FFC8;}

@media(max-width:768px){
    .block-container{padding:.5rem .6rem 3rem!important;}
    .aero-title{font-size:1.2rem;}
    .clock-time{font-size:2rem;}
    .sess-body{grid-template-columns:1fr;}
    .city-clocks{gap:.3rem;}
    .sess-name{font-size:.85rem;}
}

.stSelectbox label,.stMultiSelect label,.stRadio label{
    font-family:'Share Tech Mono',monospace!important;font-size:.65rem!important;
    color:#2D5040!important;letter-spacing:.1em!important;}
div[data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid #0E1826!important;}
div[data-baseweb="tab"]{font-family:'Share Tech Mono',monospace!important;font-size:.62rem!important;
    letter-spacing:.1em!important;color:#1E3040!important;background:transparent!important;}
div[data-baseweb="tab"][aria-selected="true"]{color:#00FFC8!important;border-bottom:2px solid #00FFC8!important;}
button[data-testid="baseButton-secondary"]{
    background:#0A1018!important;border:1px solid #141E2D!important;
    color:#2D5040!important;font-family:'Share Tech Mono',monospace!important;
    border-radius:2px!important;font-size:.62rem!important;}
</style>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  CHART HELPERS — layout dibuat bersih, tanpa shared BASE bermasalah
# ══════════════════════════════════════════════════════════════════════════════

def hex_to_rgba(color: str, alpha: float) -> str:
    value = color.lstrip("#")
    if len(value) != 6:
        return color
    try:
        r, g, b = (int(value[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return color
    return f"rgba({r},{g},{b},{alpha})"

def build_timeline_chart(h_now: float):
    fig = go.Figure()

    for s in SESSIONS:
        o, c = session_wib_window(s)
        segments = []
        if c > 24:
            segments = [(o, 24), (0, c - 24)]
        else:
            segments = [(o, c)]
        for start, end in segments:
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor=hex_to_rgba(s["color"], 0.13),
                layer="below", line_width=0,
            )
        label_x = (o + min(c, 24)) / 2 if c <= 24 else (o + 24) / 2
        fig.add_annotation(
            x=label_x, y=95,
            text=s["name"],
            font=dict(family="Share Tech Mono, monospace", color=s["color"], size=8),
            showarrow=False, yref="y",
        )

    hours_list = list(range(24))
    vol_list = [HOURLY_VOLATILITY.get(h, 10) for h in hours_list]
    fig.add_trace(go.Scatter(
        x=hours_list, y=vol_list,
        mode="lines",
        line=dict(color="#00FFC8", width=2, shape="spline", smoothing=1.2),
        fill="tozeroy", fillcolor="rgba(0,255,200,0.04)",
        name="Volatilitas",
        hovertemplate="<b>%{x}:00 WIB</b> — Vol: %{y}<extra></extra>",
    ))

    for ov in resolved_overlaps():
        s, e = ov["start"], min(ov["end"], 24)
        if e > s:
            fig.add_vrect(
                x0=s, x1=e,
                fillcolor=hex_to_rgba(ov["color"], 0.10),
                layer="below",
                line=dict(color=ov["color"], width=1, dash="dot"),
            )
            fig.add_annotation(
                x=(s + e) / 2, y=102,
                text=ov["label"],
                font=dict(family="Share Tech Mono, monospace", color=ov["color"], size=7),
                showarrow=False, yref="y",
            )

    fig.add_vline(x=h_now, line=dict(color="#FFFFFF", width=1.5, dash="dash"))
    fig.add_annotation(
        x=h_now, y=110,
        text=f"NOW {int(h_now):02d}:{int((h_now % 1) * 60):02d}",
        font=dict(family="Share Tech Mono, monospace", color="#FFFFFF", size=8),
        showarrow=False, bgcolor="#080B12", bordercolor="#FFFFFF", borderwidth=1,
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Share Tech Mono, monospace", color="#1E3D50", size=9),
        margin=dict(l=8, r=8, t=28, b=8),
        height=200,
        xaxis=dict(
            range=[0, 24],
            tickvals=list(range(0, 25, 2)),
            ticktext=[f"{h:02d}:00" for h in range(0, 25, 2)],
            gridcolor="#0A1220",
            linecolor="#0E1826",
            tickfont=dict(size=7),
            title=dict(text="WAKTU WIB", font=dict(size=8, color="#8298AD")),
        ),
        yaxis=dict(range=[0, 115], showgrid=False, showticklabels=False),
        showlegend=False,
        title=dict(text="SESI AKTIF · VOLATILITAS PER JAM (WIB)", font=dict(size=9, color="#00FFC8"), x=0),
        hovermode="x unified",
    )
    return fig

def build_vol_radar(session_id: str):
    radar_data = {
        "sydney":  {"Volatilitas": 20, "Likuiditas": 25, "Spread": 30, "Peluang": 25, "Risiko": 20, "Volume": 15},
        "tokyo":   {"Volatilitas": 50, "Likuiditas": 55, "Spread": 60, "Peluang": 55, "Risiko": 45, "Volume": 50},
        "london":  {"Volatilitas": 88, "Likuiditas": 95, "Spread": 92, "Peluang": 90, "Risiko": 75, "Volume": 95},
        "newyork": {"Volatilitas": 82, "Likuiditas": 85, "Spread": 88, "Peluang": 85, "Risiko": 80, "Volume": 80},
    }
    d = radar_data.get(session_id, {})
    labels = list(d.keys())
    values = list(d.values())
    color = next((s["color"] for s in SESSIONS if s["id"] == session_id), "#00FFC8")

    fig = go.Figure(go.Scatterpolar(
        r=values, theta=labels, fill="toself",
        fillcolor=hex_to_rgba(color, 0.08),
        line=dict(color=color, width=1.8),
        marker=dict(color=color, size=4),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Share Tech Mono, monospace", color="#1E3D50", size=8),
        margin=dict(l=15, r=15, t=15, b=15),
        height=220,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, gridcolor="#0A1220", linecolor="#0E1826",
                color="#1A2D3A", range=[0, 100], tickfont=dict(size=6),
            ),
            angularaxis=dict(gridcolor="#0A1220", linecolor="#0E1826"),
        ),
        showlegend=False,
    )
    return fig

def build_global_vol_bar():
    names = [s["name"] for s in SESSIONS]
    shares = [int(s["share"].replace("%", "")) for s in SESSIONS]
    colors = [s["color"] for s in SESSIONS]

    fig = go.Figure(go.Bar(
        x=shares, y=names,
        orientation="h",
        marker=dict(
            color=[hex_to_rgba(c, 0.7) for c in colors],
            line=dict(color=colors, width=1),
        ),
        text=[f"{v}%" for v in shares],
        textposition="inside",
        textfont=dict(family="Share Tech Mono, monospace", size=9, color="#080B12"),
        hovertemplate="%{y}: <b>%{x}%</b> volume FX harian<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Share Tech Mono, monospace", color="#1E3D50", size=9),
        margin=dict(l=60, r=8, t=28, b=8),
        height=140,
        xaxis=dict(range=[0, 45], showgrid=False, showticklabels=False, linecolor="#0E1826"),
        yaxis=dict(showgrid=False, tickfont=dict(size=9, family="Share Tech Mono, monospace")),
        title=dict(text="SHARE VOLUME FX HARIAN PER SESI", font=dict(size=9, color="#00FFC8"), x=0),
        bargap=0.3,
        showlegend=False,
    )
    return fig

def build_session_vol_bar():
    sess_names = [s["name"] for s in SESSIONS]
    sess_vols = [s["vol_pct"] for s in SESSIONS]
    sess_colors = [s["color"] for s in SESSIONS]
    fig = go.Figure(go.Bar(
        x=sess_names, y=sess_vols,
        marker=dict(
            color=[hex_to_rgba(c, 0.7) for c in sess_colors],
            line=dict(color=sess_colors, width=1),
        ),
        text=[f"{v}%" for v in sess_vols],
        textposition="outside",
        textfont=dict(family="Share Tech Mono, monospace", size=9),
        hovertemplate="%{x}: <b>%{y}%</b> volatilitas relatif<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Share Tech Mono, monospace", color="#1E3D50", size=9),
        margin=dict(l=8, r=8, t=28, b=8),
        height=200,
        xaxis=dict(showgrid=False, tickfont=dict(size=9, family="Share Tech Mono, monospace")),
        yaxis=dict(
            range=[0, 115], showgrid=True, gridcolor="#0A1220",
            tickfont=dict(size=8),
            title=dict(text="VOLATILITAS RELATIF (%)", font=dict(size=8, color="#8298AD")),
        ),
        title=dict(text="VOLATILITAS RELATIF PER SESI", font=dict(size=9, color="#00FFC8"), x=0),
        bargap=0.35,
        showlegend=False,
    )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
#  RENDER HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def vol_badge(level: str) -> str:
    cls = {
        "LOW": "vol-low",
        "MEDIUM": "vol-med",
        "HIGH": "vol-high",
        "EXTREME": "vol-ext",
    }.get(level, "vol-low")
    return f'<span class="{cls}">{level}</span>'

def render_session_card(s: dict, h: float):
    active = session_active(s, h)
    prog = session_progress(s, h) if active else 0.0
    prog_w = f"{prog * 100:.0f}%"
    status = "ACTIVE" if active else "CLOSED"
    s_cls = "sess-card-active" if active else ""
    st_cls = "sess-status-active" if active else "sess-status-closed"
    ctd = f"PROGRESS: {prog * 100:.0f}%" if active else time_until_open(s, h)
    open_wib, close_wib = session_wib_window(s)
    time_str = fmt_wib_range(open_wib, close_wib)
    v_badge = vol_badge(s["vol"])
    pairs_html = " ".join(
        f'<span class="pair-tag" style="--sc:{s["color"]};">{p}</span>' for p in s["pairs"]
    )

    pair_data = SESSION_PAIR_DATA.get(s["id"], {})
    range_rows = ""
    for pair, pips in list(pair_data.get("typical_range_pips", {}).items())[:5]:
        bar_w = min(pips / 150 * 100, 100)
        range_rows += f"""
<tr>
<td class="range-td range-td-pair">{pair}</td>
<td class="range-td">
<div style="height:3px;background:#0E1826;border-radius:1px;">
<div style="height:3px;width:{bar_w:.0f}%;background:{s['color']};border-radius:1px;"></div>
</div>
</td>
<td class="range-td range-td-pips">{pips} pips</td>
</tr>"""

    st.markdown(f"""
<div class="sess-card {s_cls}" style="--sc:{s['color']};">
<div class="sess-left-bar"></div>
<div class="sess-header">
<div style="flex:1;">
<div style="display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;">
<span class="sess-name">{s['name']}</span>
<span class="sess-region">{s['region']}</span>
{v_badge}
</div>
<div class="sess-time" style="margin-top:.2rem;">{time_str} · {s['city']} Local: {city_local_time(s['tz'])}</div>
</div>
<div style="display:flex;flex-direction:column;align-items:flex-end;gap:.25rem;">
<span class="{st_cls}">{status}</span>
<span class="sess-countdown">{ctd}</span>
</div>
</div>

<div class="prog-wrap">
<div class="prog-track">
<div class="prog-fill" style="width:{prog_w};background:{s['color']};"></div>
</div>
<div class="prog-pct">{'PROGRESS: ' + f'{prog*100:.0f}%' if active else 'STANDBY'}</div>
</div>

<div style="font-size:.68rem;color:#2D4050;margin-bottom:.5rem;">{s['desc']}</div>

<div class="sess-body">
<div class="sess-info-block">
<div class="sib-label">PAIR AKTIF</div>
<div>{pairs_html}</div>
</div>
<div class="sess-info-block">
<div class="sib-label">STRATEGI</div>
<div class="sib-val">{s['strategy']}</div>
</div>
<div class="sess-info-block">
<div class="sib-label">TYPICAL RANGE PER PAIR</div>
<table class="range-table">
<tr><th class="range-th">PAIR</th><th class="range-th"></th><th class="range-th">RANGE</th></tr>
{range_rows}
</table>
</div>
<div class="sess-info-block">
<div class="sib-label">NEWS FOCUS</div>
<div class="sib-val">{"<br>".join(f"<b>·</b> {n}" for n in s['news_focus'])}</div>
<div class="sib-label" style="margin-top:.4rem;">RISK NOTE</div>
<div class="sib-val" style="color:#FF6B6B;">{s['risk']}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

def render_overlap_cards(h: float):
    for ov in resolved_overlaps():
        active = overlap_active(ov, h)
        oc = ov["color"]
        a_badge = '<span class="ov-active-badge">ACTIVE NOW</span>' if active else ""
        time_str = fmt_wib_range(ov["start"], ov["end"])
        vol_b = vol_badge(ov["vol"])
        st.markdown(f"""
<div class="ov-card" style="--oc:{oc};">
<div class="ov-card-accent"></div>
<div class="ov-header">
<span class="ov-name">{ov['name']}</span>
<span class="ov-label">{ov['label']}</span>
{vol_b}
{a_badge}
<span class="ov-time">{time_str}</span>
</div>
<div class="ov-desc">{ov['desc']}</div>
</div>""", unsafe_allow_html=True)

def render_volatility_heatmap(h_now: float):
    bars = ""
    for hr in range(24):
        v = HOURLY_VOLATILITY.get(hr, 10)
        h_pct = v * 0.6
        if v >= 80:
            col = "#FF6B6B"
        elif v >= 60:
            col = "#FF9F43"
        elif v >= 40:
            col = "#FFD93D"
        elif v >= 20:
            col = "#00FFC8"
        else:
            col = "#1A3040"
        is_now = abs(hr - int(h_now)) < 1
        border = f"border:1px solid {col};" if is_now else ""
        bars += (
            f'<div class="heat-bar" style="height:{h_pct:.0f}%;background:{col};'
            f'opacity:{0.5 + v / 200:.2f};{border}" title="{hr:02d}:00 WIB — Vol: {v}"></div>'
        )

    labels = " ".join(
        f'<span>{h:02d}</span>' if h % 4 == 0 else '<span></span>'
        for h in range(24)
    )
    st.markdown(f"""
<div class="sec-title">VOLATILITAS INTRADAY</div>
<div class="sec-sub">INTENSITAS PERGERAKAN PASAR PER JAM WIB · MERAH=EKSTREM · HIJAU=RENDAH</div>
<div class="heat-wrap">{bars}</div>
<div class="heat-labels">{labels}</div>
""", unsafe_allow_html=True)

def render_trader_guide():
    tips = [
        ("SESI TERBAIK UNTUK FOREX", "London / New York Overlap (Power Zone II) = peak liquidity, spread paling ketat, pergerakan paling besar. Ideal untuk breakout dan trend-following."),
        ("HINDARI TRADING DI JAM INI", "00:00–06:00 WIB — Volume paling rendah, spread lebar, pergerakan tidak menentu. Risiko stop hunt lebih tinggi."),
        ("PILIH PAIR SESUAI SESI", "JPY pairs saat Tokyo aktif. EUR/GBP pairs saat London. USD pairs saat New York."),
        ("NEWS TRADING TIMING", "Masuk posisi 15–30 menit SETELAH data dirilis, bukan saat rilis. Slippage ekstrem di detik pertama high-impact."),
        ("POWER ZONE II", "London/NY Overlap = mayoritas volume harian terkonsentrasi di sini. Gunakan momentum strategy, bukan counter-trend."),
        ("RANGE TRADING DI SESI SEPI", "Sydney dan awal Tokyo = kondisi ideal untuk range trading. Support/resistance lebih dihormati."),
        ("SPREAD AWARENESS", "Spread paling lebar: Minggu malam dan saat rollover. Selalu cek spread sebelum entry, terutama pair minor."),
    ]
    html = '<div class="strat-card">'
    for i, (title, body) in enumerate(tips, 1):
        html += (
            f'<div class="tip-row"><div class="tip-num">{i:02d}</div>'
            f'<div class="tip-txt"><b style="color:#00FFC8;">{title}</b><br>{body}</div></div>'
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    css()
    h_now = wib_hour_float()
    now_dt = now_wib()
    active_sessions = [s for s in SESSIONS if session_active(s, h_now)]
    active_overlaps = [o for o in OVERLAPS if overlap_active(o, h_now)]

    # HEADER
    st.markdown("""
<div style="padding:.3rem 0 .6rem;">
<div class="aero-build">AEROVULPIS · PROTOTYPE · MARKET SESSIONS MODULE · BUILD STABLE 02 SEP 2026</div>
<div class="aero-title">MARKET SESSIONS</div>
<div class="aero-sub">GLOBAL TRADING WINDOWS · LIQUIDITY INTELLIGENCE · PAIR RECOMMENDATIONS · WIB ONLY</div>
</div>
<hr style="border:none;border-top:1px solid #0E1826;margin:.4rem 0 .8rem;">
""", unsafe_allow_html=True)

    # LIVE CLOCK + STATUS
    col_clk, col_status = st.columns([1, 2])
    with col_clk:
        st.markdown(f"""
<div class="clock-wrap">
<div class="clock-label">WAKTU INDONESIA BARAT (WIB)</div>
<div class="clock-time">{now_dt.strftime('%H:%M')}</div>
<div class="clock-date">{now_dt.strftime('%A, %d %B %Y')}</div>
</div>""", unsafe_allow_html=True)

    with col_status:
        if active_sessions:
            for s in active_sessions:
                prog = session_progress(s, h_now)
                st.markdown(f"""
<div style="display:flex;align-items:center;gap:.6rem;background:#0A1018;border:1px solid {s['color']}40;
    border-radius:2px;padding:.5rem .75rem;margin-bottom:.3rem;">
<span style="font-family:'Share Tech Mono',monospace;font-size:.62rem;font-weight:700;
    color:{s['color']};min-width:90px;">{s['name']}</span>
<div style="flex:1;height:4px;background:#0E1826;border-radius:2px;">
<div style="height:4px;width:{prog*100:.0f}%;background:{s['color']};border-radius:2px;"></div>
</div>
<span style="font-family:'Share Tech Mono',monospace;font-size:.55rem;color:{s['color']};">{prog*100:.0f}%</span>
</div>""", unsafe_allow_html=True)
        if active_overlaps:
            for ov in active_overlaps:
                resolved = resolved_overlap(ov)
                st.markdown(
                    f'<div class="ov-card" style="--oc:{resolved["color"]};padding:.45rem .75rem;">'
                    f'<div class="ov-card-accent"></div>'
                    f'<span class="ov-name" style="font-size:.65rem;">{resolved["name"]}</span> '
                    f'<span class="ov-active-badge">ACTIVE NOW</span> '
                    f'<span class="ov-label" style="margin-left:.3rem;">{resolved["label"]}</span></div>',
                    unsafe_allow_html=True,
                )
        if not active_sessions and not active_overlaps:
            st.markdown(
                '<div class="ibox" style="--lc:#1A2D3A;">'
                '<div class="ibox-t">MARKET STATUS</div>'
                '<div class="ibox-b">Semua sesi mayor sedang tutup. Volume sangat rendah. Tidak disarankan untuk trading.</div></div>',
                unsafe_allow_html=True,
            )

    # CITY CLOCKS (hanya local city + WIB, tanpa UTC)
    city_html = '<div class="city-clocks">'
    for s in SESSIONS:
        active = session_active(s, h_now)
        sc = "cs-active" if active else "cs-closed"
        st_lbl = "ACTIVE" if active else "CLOSED"
        city_html += f"""
<div class="city-clock" style="--cc:{s['color']};">
<div class="city-clock-accent"></div>
<div class="city-clock-name">{s['city'].upper()}</div>
<div class="city-clock-time">{city_local_time(s['tz'])}</div>
<span class="city-clock-status {sc}">{st_lbl}</span>
</div>"""
    wib_time = now_wib().strftime("%H:%M")
    city_html += f"""
<div class="city-clock" style="--cc:#4FC3F7;">
<div class="city-clock-accent"></div>
<div class="city-clock-name">WIB / JAKARTA</div>
<div class="city-clock-time">{wib_time}</div>
<span class="city-clock-status cs-active">LOCAL REF</span>
</div>"""
    city_html += "</div>"
    st.markdown(city_html, unsafe_allow_html=True)

    st.markdown('<hr class="hr">', unsafe_allow_html=True)

    # TABS
    tabs = st.tabs(["SESSION MAP", "SESSIONS DETAIL", "POWER ZONES", "VOLATILITY", "PANDUAN TRADER"])

    # TAB 1
    with tabs[0]:
        st.markdown('<div class="sec-title">SESSION TIMELINE MAP</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sec-sub">PETA WAKTU 24 JAM WIB · OVERLAY VOLATILITAS · GARIS = WAKTU SEKARANG</div>',
            unsafe_allow_html=True,
        )
        fig_tl = build_timeline_chart(h_now)
        st.plotly_chart(fig_tl, use_container_width=True, config={"staticPlot": True, "displayModeBar": False})

        st.markdown('<hr class="hr">', unsafe_allow_html=True)

        col_v, col_r = st.columns([1.2, 1])
        with col_v:
            st.plotly_chart(
                build_global_vol_bar(),
                use_container_width=True,
                config={"staticPlot": True, "displayModeBar": False},
            )
        with col_r:
            st.markdown('<div class="sec-title">OVERLAP WINDOWS</div>', unsafe_allow_html=True)
            for ov in resolved_overlaps():
                time_str = fmt_wib_range(ov["start"], ov["end"])
                active = overlap_active(ov, h_now)
                badge = '<span class="ov-active-badge">LIVE</span>' if active else ""
                st.markdown(f"""
<div style="background:#0A1018;border:1px solid {ov['color']}30;border-radius:2px;
    padding:.5rem .7rem;margin-bottom:.35rem;">
<div style="display:flex;align-items:center;gap:.5rem;flex-wrap:wrap;">
<span style="font-family:'Share Tech Mono',monospace;font-size:.65rem;font-weight:700;color:{ov['color']};">{ov['label']}</span>
{badge}
{vol_badge(ov['vol'])}
<span style="font-family:'Share Tech Mono',monospace;font-size:.55rem;color:#2D4050;margin-left:auto;">{time_str}</span>
</div>
<div style="font-size:.65rem;color:#3A5060;margin-top:.25rem;">{ov['desc'][:90]}...</div>
</div>""", unsafe_allow_html=True)

    # TAB 2
    with tabs[1]:
        st.markdown('<div class="sec-title">SESSIONS INTELLIGENCE</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sec-sub">KARAKTERISTIK LENGKAP · PAIR RECOMMENDATIONS · RANGE TYPICAL · STRATEGI</div>',
            unsafe_allow_html=True,
        )
        show_all = st.toggle("Tampilkan semua sesi (termasuk yang tutup)", value=True, key="sess_all")
        for s in SESSIONS:
            if not show_all and not session_active(s, h_now):
                continue
            render_session_card(s, h_now)
            with st.expander(f"PROFIL KARAKTERISTIK — {s['name']} (RADAR)", expanded=False):
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.plotly_chart(
                        build_vol_radar(s["id"]),
                        use_container_width=True,
                        config={"displayModeBar": False, "scrollZoom": False},
                    )
                with c2:
                    pd_data = SESSION_PAIR_DATA.get(s["id"], {})
                    st.markdown(f"""
<div class="ibox" style="--lc:{s['color']};">
<div class="ibox-t">KARAKTERISTIK SESI</div>
<div class="ibox-b">
<b style="color:{s['color']};">Kondisi Spread:</b> {pd_data.get('spread_condition', '—')}<br>
<b style="color:{s['color']};">Aktivitas Institusional:</b> {pd_data.get('institutional_activity', '—')}<br>
<b style="color:{s['color']};">Strategi Terbaik:</b> {pd_data.get('best_strategy', '—')}<br>
<b style="color:{s['color']};">Volume Share Global:</b> {s['share']}
</div>
</div>""", unsafe_allow_html=True)

    # TAB 3
    with tabs[2]:
        st.markdown('<div class="sec-title">POWER ZONES — SESSION OVERLAPS</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sec-sub">PERIODE LIKUIDITAS TERTINGGI · SPREAD TERKECIL · PELUANG TERBESAR</div>',
            unsafe_allow_html=True,
        )
        render_overlap_cards(h_now)

        st.markdown('<hr class="hr">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">STRATEGI PER POWER ZONE</div>', unsafe_allow_html=True)
        cols_pz = st.columns(2)
        strategies = [
            {
                "zone": "POWER ZONE I — TOKYO/LONDON",
                "color": "#FFD93D",
                "content": [
                    ("Pair Terbaik", "EUR/JPY, GBP/JPY, AUD/JPY — JPY crosses paling reaktif"),
                    ("Strategi", "Breakout dari range Tokyo. London sering reverse atau extend trend Asia"),
                    ("Durasi", "Singkat tapi volatile. Gunakan pending order di high/low Tokyo"),
                    ("Risk", "False breakout umum. Konfirmasi dengan volume dan candle close"),
                ],
            },
            {
                "zone": "POWER ZONE II — LONDON/NEW YORK",
                "color": "#FF6B6B",
                "content": [
                    ("Pair Terbaik", "EUR/USD, GBP/USD, USD/JPY, XAU/USD — semua pair major liquid"),
                    ("Strategi", "Trend-following dan breakout momentum. Hindari counter-trend tanpa strong signal"),
                    ("Durasi", "Window paling panjang dan paling profitable untuk day trader"),
                    ("Risk", "Data AS sering dirilis di sini. SL wajib sebelum masuk posisi"),
                ],
            },
        ]
        for col, strat in zip(cols_pz, strategies):
            with col:
                rows = "".join(
                    f'<div class="tip-row"><div class="tip-num" style="color:{strat["color"]};min-width:80px;font-size:.55rem;">{k}</div>'
                    f'<div class="tip-txt">{v}</div></div>'
                    for k, v in strat["content"]
                )
                st.markdown(f"""
<div class="strat-card">
<div class="strat-header" style="color:{strat['color']};">{strat['zone']}</div>
{rows}
</div>""", unsafe_allow_html=True)

        st.markdown("""
<div class="ibox" style="--lc:#FF9F43;margin-top:.5rem;">
<div class="ibox-t">INSTITUTIONAL BEHAVIOR DI OVERLAP PERIOD</div>
<div class="ibox-b">
Institusi besar paling aktif saat dua sesi overlap karena likuiditas cukup untuk mengeksekusi order besar tanpa slippage signifikan.
Pada Power Zone II, bid-ask spread EUR/USD bisa turun hingga <b style="color:#00FFC8;">0.1–0.3 pips</b>.
Ini berarti biaya trading turun drastis — kondisi ideal untuk frekuensi trading tinggi.
</div>
</div>""", unsafe_allow_html=True)

    # TAB 4
    with tabs[3]:
        render_volatility_heatmap(h_now)
        st.markdown('<hr class="hr">', unsafe_allow_html=True)

        curr_hr = int(h_now)
        curr_vol = HOURLY_VOLATILITY.get(curr_hr, 10)
        if curr_vol >= 80:
            vol_state, vol_color, vol_advice = (
                "EKSTREM", "#FF6B6B",
                "Volume dan pergerakan sangat tinggi. Gunakan SL lebih lebar. Peluang besar tapi risiko spike tinggi.",
            )
        elif curr_vol >= 60:
            vol_state, vol_color, vol_advice = (
                "TINGGI", "#FF9F43",
                "Kondisi aktif. Trend dan breakout lebih reliable. Manajemen posisi sangat penting.",
            )
        elif curr_vol >= 35:
            vol_state, vol_color, vol_advice = (
                "SEDANG", "#FFD93D",
                "Volume moderat. Campuran antara range dan trending. Konfirmasi sinyal dengan indikator tambahan.",
            )
        elif curr_vol >= 15:
            vol_state, vol_color, vol_advice = (
                "RENDAH", "#00FFC8",
                "Pasar tenang. Range trading lebih optimal. Spread bisa lebih lebar dari biasanya.",
            )
        else:
            vol_state, vol_color, vol_advice = (
                "SANGAT RENDAH", "#4FC3F7",
                "Volume minimum. Sebaiknya tunggu sesi berikutnya. Risiko whipsaw dan spread lebar.",
            )

        col_cv, col_ca = st.columns([1, 2])
        with col_cv:
            st.markdown(f"""
<div style="text-align:center;background:#0A1018;border:1px solid {vol_color}40;
    border-radius:2px;padding:1rem;">
<div style="font-family:'Share Tech Mono',monospace;font-size:.55rem;color:#1A3040;letter-spacing:.18em;margin-bottom:.3rem;">
VOLATILITAS JAM INI
</div>
<div style="font-family:'Share Tech Mono',monospace;font-size:2.5rem;font-weight:700;
    color:{vol_color};line-height:1;">{curr_vol}</div>
<div style="font-family:'Share Tech Mono',monospace;font-size:.55rem;color:{vol_color};
    letter-spacing:.15em;margin:.3rem 0;">{vol_state}</div>
<div style="height:5px;background:#0E1826;border-radius:2px;margin:.4rem 0;">
<div style="height:5px;width:{curr_vol}%;background:{vol_color};border-radius:2px;"></div>
</div>
<div style="font-family:'Share Tech Mono',monospace;font-size:.52rem;color:#1A3040;">{curr_hr:02d}:00 WIB</div>
</div>""", unsafe_allow_html=True)
        with col_ca:
            st.markdown(f"""
<div class="ibox" style="--lc:{vol_color};">
<div class="ibox-t">ANALISIS KONDISI PASAR SAAT INI</div>
<div class="ibox-b">{vol_advice}</div>
</div>""", unsafe_allow_html=True)

            active_now = [s["name"] for s in SESSIONS if session_active(s, h_now)]
            overlap_now = [resolved_overlap(o)["label"] for o in OVERLAPS if overlap_active(o, h_now)]
            st.markdown(f"""
<div class="ibox" style="--lc:#4A9EBF;">
<div class="ibox-t">STATUS PASAR</div>
<div class="ibox-b">
<b style="color:#00FFC8;">Sesi Aktif:</b> {', '.join(active_now) if active_now else 'Tidak ada sesi aktif'}<br>
<b style="color:#FFD93D;">Overlap:</b> {', '.join(overlap_now) if overlap_now else 'Tidak ada overlap aktif'}<br>
<b style="color:#C77DFF;">Kondisi:</b> {'Peak liquidity — kondisi ideal trading' if curr_vol >= 80 else 'Suboptimal — pertimbangkan menunggu Power Zone'}
</div>
</div>""", unsafe_allow_html=True)

        st.markdown('<hr class="hr">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">VOLATILITAS PER SESI — PERBANDINGAN</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sec-sub">RATA-RATA INTENSITAS PERGERAKAN PER SESI TRADING</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            build_session_vol_bar(),
            use_container_width=True,
            config={"staticPlot": True, "displayModeBar": False},
        )

    # TAB 5
    with tabs[4]:
        st.markdown('<div class="sec-title">PANDUAN TRADER — SESSION MASTERY</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sec-sub">7 PRINSIP TIMING TRADING BERBASIS SESI PASAR</div>',
            unsafe_allow_html=True,
        )
        render_trader_guide()

        st.markdown('<hr class="hr">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">QUICK REFERENCE — PAIR TERBAIK PER SESI</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sec-sub">PAIR DENGAN LIKUIDITAS DAN RANGE OPTIMAL SESUAI JAM TRADING</div>',
            unsafe_allow_html=True,
        )

        cols_ref = st.columns(4)
        for col, s in zip(cols_ref, SESSIONS):
            active = session_active(s, h_now)
            border = f"border-color:{s['color']}80;" if active else ""
            o, c = session_wib_window(s)
            time_str = fmt_wib_range(o, c)
            with col:
                pairs_html = "".join(
                    f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:.6rem;color:{s["color"]};'
                    f'padding:.15rem 0;border-bottom:1px solid #0E1826;">{p}</div>'
                    for p in s["pairs"]
                )
                st.markdown(f"""
<div style="background:#0A1018;border:1px solid #141E2D;{border}border-radius:2px;padding:.7rem .8rem;">
<div style="font-family:'Share Tech Mono',monospace;font-size:.65rem;font-weight:700;
    color:{s['color']};letter-spacing:.1em;margin-bottom:.1rem;">{s['name']}</div>
<div style="font-family:'Share Tech Mono',monospace;font-size:.52rem;color:#1A3040;
    margin-bottom:.4rem;">{time_str}</div>
{pairs_html}
</div>""", unsafe_allow_html=True)

    # FOOTER SNAPSHOT
    st.markdown('<hr class="hr">', unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:.52rem;color:#8298AD;letter-spacing:.1em;">'
        f'SNAPSHOT WAKTU WIB: {now_dt.strftime("%H:%M WIB")} · Semua waktu ditampilkan dalam WIB (UTC+7) · '
        f'Sesi dihitung dari jam lokal masing-masing pusat finansial (DST-aware)</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
