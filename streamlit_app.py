"""
economic_radar_page.py
Aerovulpis V4.1 — Economic Radar Module
Fitur: Pemantauan indikator makroekonomi global secara real-time untuk trader dan investor.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json

# ─── CONSTANTS ────────────────────────────────────────────────────────────────

WORLD_BANK_BASE = "https://api.worldbank.org/v2/country/{iso}/indicator/{ind}?format=json&mrv=10&per_page=10"

INDICATORS = {
    "GDP (PDB)": {
        "code": "NY.GDP.MKTP.CD",
        "unit": "USD",
        "format": "triliun",
        "desc": "Produk Domestik Bruto — ukuran total output ekonomi.",
        "color": "#00FFC8",
        "icon": "📊",
    },
    "Inflasi": {
        "code": "FP.CPI.TOTL.ZG",
        "unit": "%",
        "format": "persen",
        "desc": "Tingkat inflasi tahunan — menggerus daya beli.",
        "color": "#FF6B6B",
        "icon": "🔥",
    },
    "Pengangguran": {
        "code": "SL.UEM.TOTL.ZS",
        "unit": "%",
        "format": "persen",
        "desc": "Persentase angkatan kerja tanpa pekerjaan.",
        "color": "#FFD93D",
        "icon": "👥",
    },
    "Utang/PDB": {
        "code": "GC.DOD.TOTL.GD.ZS",
        "unit": "%",
        "format": "persen",
        "desc": "Rasio utang pemerintah terhadap PDB — keberlanjutan fiskal.",
        "color": "#C77DFF",
        "icon": "💰",
    },
    "Neraca Perdagangan": {
        "code": "BN.CAB.XOKA.CD",
        "unit": "USD",
        "format": "miliar",
        "desc": "Selisih ekspor dan impor barang/jasa.",
        "color": "#4FC3F7",
        "icon": "⚖️",
    },
}

COUNTRIES = {
    "🇮🇩 Indonesia": "ID",
    "🇺🇸 Amerika Serikat": "US",
    "🇨🇳 China": "CN",
    "🇯🇵 Jepang": "JP",
    "🇩🇪 Jerman": "DE",
    "🇬🇧 Inggris": "GB",
    "🇦🇺 Australia": "AU",
    "🇮🇳 India": "IN",
    "🇰🇷 Korea Selatan": "KR",
    "🇸🇬 Singapura": "SG",
    "🇲🇾 Malaysia": "MY",
    "🇹🇭 Thailand": "TH",
    "🇧🇷 Brasil": "BR",
    "🇿🇦 Afrika Selatan": "ZA",
    "🇸🇦 Arab Saudi": "SA",
}

RISK_THRESHOLDS = {
    "Inflasi":        {"low": 3, "medium": 6},
    "Pengangguran":   {"low": 5, "medium": 10},
    "Utang/PDB":      {"low": 60, "medium": 90},
}

# ─── STYLES ───────────────────────────────────────────────────────────────────

def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

/* ── Base ── */
.stApp { background: #0A0D14 !important; }
section[data-testid="stSidebar"] { background: #0D1018 !important; }
* { font-family: 'Exo 2', sans-serif; }

/* ── Section header ── */
.aero-section-title {
    font-family: 'Share Tech Mono', monospace;
    color: #00FFC8;
    font-size: 1.05rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    border-left: 3px solid #00FFC8;
    padding-left: 0.75rem;
    margin: 1.5rem 0 0.4rem 0;
}
.aero-section-sub {
    font-family: 'Share Tech Mono', monospace;
    color: #4A5568;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    margin-bottom: 1rem;
}

/* ── KPI Card ── */
.kpi-card {
    background: linear-gradient(145deg, #0F1520 0%, #111827 100%);
    border: 1px solid #1E2A3A;
    border-radius: 4px;
    padding: 1.1rem 1rem 0.9rem 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card:hover { border-color: #00FFC8; }
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent, #00FFC8);
    opacity: 0.7;
}
.kpi-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.15em;
    color: #4A9EBF;
    margin-bottom: 0.35rem;
    text-transform: uppercase;
}
.kpi-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent, #00FFC8);
    line-height: 1;
    margin-bottom: 0.3rem;
}
.kpi-desc {
    font-size: 0.65rem;
    color: #374151;
    line-height: 1.4;
}
.kpi-risk {
    display: inline-block;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.1em;
    padding: 2px 8px;
    border-radius: 2px;
    margin-top: 0.4rem;
    font-weight: 600;
}
.risk-low    { background: rgba(0,255,200,0.12); color: #00FFC8; border: 1px solid #00FFC840; }
.risk-medium { background: rgba(255,217,61,0.12); color: #FFD93D; border: 1px solid #FFD93D40; }
.risk-high   { background: rgba(255,107,107,0.12); color: #FF6B6B; border: 1px solid #FF6B6B40; }
.risk-neutral { background: rgba(74,158,191,0.12); color: #4A9EBF; border: 1px solid #4A9EBF40; }

/* ── Divider ── */
.aero-divider {
    border: none;
    border-top: 1px solid #1A2332;
    margin: 1.2rem 0;
}

/* ── Radar label ── */
.radar-note {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #374151;
    text-align: center;
    margin-top: -0.5rem;
    margin-bottom: 1rem;
    letter-spacing: 0.08em;
}

/* ── Compare table ── */
.compare-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #4A9EBF;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.trend-up   { color: #FF6B6B; font-weight: 700; }
.trend-down { color: #00FFC8; font-weight: 700; }

/* ── Interpretation box ── */
.interp-box {
    background: #0F1520;
    border: 1px solid #1E2A3A;
    border-left: 3px solid #C77DFF;
    border-radius: 0 4px 4px 0;
    padding: 0.85rem 1rem;
    margin-top: 0.5rem;
}
.interp-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #C77DFF;
    letter-spacing: 0.12em;
    margin-bottom: 0.5rem;
}
.interp-text {
    font-size: 0.8rem;
    color: #9CA3AF;
    line-height: 1.65;
}

/* ── Calendar item ── */
.cal-item {
    background: #0F1520;
    border: 1px solid #1E2A3A;
    border-radius: 4px;
    padding: 0.7rem 0.9rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.cal-date {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #4A9EBF;
    min-width: 60px;
}
.cal-impact-high   { color: #FF6B6B; font-size: 0.7rem; font-weight: 700; }
.cal-impact-medium { color: #FFD93D; font-size: 0.7rem; font-weight: 700; }
.cal-impact-low    { color: #4A9EBF; font-size: 0.7rem; }
.cal-event { font-size: 0.78rem; color: #D1D5DB; }

/* ── Build tag ── */
.build-tag {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    color: #1E3A2F;
    text-align: right;
    letter-spacing: 0.1em;
    padding-top: 0.3rem;
}

/* ── Selectbox cleanup ── */
div[data-baseweb="select"] { background: #0F1520 !important; }
.stSelectbox label { color: #4A9EBF !important; font-family: 'Share Tech Mono', monospace !important; font-size: 0.72rem !important; letter-spacing: 0.1em !important; }
</style>
""", unsafe_allow_html=True)

# ─── DATA FETCH ───────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_wb(iso: str, indicator_code: str) -> list[dict]:
    """Ambil data World Bank, kembalikan list dicts {year, value}."""
    try:
        url = WORLD_BANK_BASE.format(iso=iso, ind=indicator_code)
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        raw = r.json()
        if len(raw) < 2 or not raw[1]:
            return []
        entries = []
        for item in raw[1]:
            if item.get("value") is not None:
                entries.append({"year": int(item["date"]), "value": item["value"]})
        return sorted(entries, key=lambda x: x["year"])
    except Exception:
        return []


def latest_value(data: list[dict]) -> tuple[float | None, int | None]:
    if not data:
        return None, None
    for item in reversed(data):
        if item["value"] is not None:
            return item["value"], item["year"]
    return None, None


def format_value(val: float, fmt: str, unit: str) -> str:
    if val is None:
        return "N/A"
    if fmt == "triliun":
        return f"{val / 1e12:.2f}T {unit}"
    if fmt == "miliar":
        return f"{val / 1e9:.1f}B {unit}"
    return f"{val:.2f} {unit}"


def risk_level(indicator_name: str, val: float | None) -> str:
    if val is None or indicator_name not in RISK_THRESHOLDS:
        return "neutral"
    t = RISK_THRESHOLDS[indicator_name]
    if val <= t["low"]:
        return "low"
    if val <= t["medium"]:
        return "medium"
    return "high"


RISK_LABELS = {
    "low": ("RENDAH", "risk-low"),
    "medium": ("SEDANG", "risk-medium"),
    "high": ("TINGGI", "risk-high"),
    "neutral": ("DATA", "risk-neutral"),
}

# ─── CHART HELPERS ────────────────────────────────────────────────────────────

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Share Tech Mono, monospace", color="#4A9EBF", size=10),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(gridcolor="#1A2332", tickcolor="#1A2332", linecolor="#1A2332"),
    yaxis=dict(gridcolor="#1A2332", tickcolor="#1A2332", linecolor="#1A2332"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1A2332"),
)


def sparkline_chart(data: list[dict], color: str, title: str, unit: str, fmt: str) -> go.Figure:
    years = [d["year"] for d in data]
    vals  = [d["value"] for d in data]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=vals,
        mode="lines+markers",
        line=dict(color=color, width=2),
        marker=dict(color=color, size=4),
        fill="tozeroy",
        fillcolor=f"{color}15",
        hovertemplate=f"<b>%{{x}}</b><br>{format_value(None, fmt, unit).replace('N/A', '')}%{{y:.2f}}<extra></extra>",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=title, font=dict(size=10, color=color), x=0))
    fig.update_xaxes(tickformat="d")
    return fig


def radar_chart(labels: list[str], values: list[float], country: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill="toself",
        fillcolor="rgba(0,255,200,0.08)",
        line=dict(color="#00FFC8", width=2),
        marker=dict(color="#00FFC8", size=5),
        name=country,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Share Tech Mono, monospace", color="#4A9EBF", size=9),
        margin=dict(l=30, r=30, t=30, b=30),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, gridcolor="#1A2332", linecolor="#1A2332", color="#374151"),
            angularaxis=dict(gridcolor="#1A2332", linecolor="#1A2332"),
        ),
        showlegend=False,
    )
    return fig


def bar_compare_chart(country_labels: list[str], values: list[float], color: str, indicator: str) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=country_labels,
        y=values,
        marker=dict(color=color, opacity=0.75, line=dict(color=color, width=1)),
        hovertemplate="%{x}<br><b>%{y:.2f}</b><extra></extra>",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=indicator, font=dict(size=10, color=color), x=0))
    fig.update_xaxes(tickangle=-30)
    return fig

# ─── INTERPRETATION ENGINE ────────────────────────────────────────────────────

def interpret_macro(country: str, data_map: dict) -> str:
    """Buat interpretasi singkat kondisi makro berdasarkan data live."""
    lines = []

    gdp = data_map.get("GDP (PDB)", {})
    inf = data_map.get("Inflasi", {})
    unemp = data_map.get("Pengangguran", {})
    debt = data_map.get("Utang/PDB", {})
    trade = data_map.get("Neraca Perdagangan", {})

    # GDP
    if gdp.get("val") is not None:
        gdp_t = gdp["val"] / 1e12
        lines.append(f"PDB {country.split()[-1]} berada di {gdp_t:.2f}T USD — "
                     f"{'skala ekonomi signifikan di kawasan' if gdp_t > 0.5 else 'ekonomi berkembang dengan ruang ekspansi luas'}.")

    # Inflasi
    if inf.get("val") is not None:
        iv = inf["val"]
        if iv < 2:
            lines.append(f"Inflasi {iv:.1f}% berada di bawah target ideal — risiko deflasi perlu dipantau.")
        elif iv <= 4:
            lines.append(f"Inflasi {iv:.1f}% terkendali dalam kisaran sehat — sinyal positif untuk daya beli.")
        elif iv <= 7:
            lines.append(f"Inflasi {iv:.1f}% dalam zona kuning — bank sentral kemungkinan mempertahankan stance hawkish.")
        else:
            lines.append(f"⚠️ Inflasi {iv:.1f}% di zona kritis — tekanan kenaikan suku bunga tinggi, waspada dampak ke pasar obligasi dan ekuitas.")

    # Pengangguran
    if unemp.get("val") is not None:
        uv = unemp["val"]
        if uv < 4:
            lines.append(f"Tingkat pengangguran {uv:.1f}% menunjukkan pasar tenaga kerja sangat ketat — potensi tekanan upah inflasioner.")
        elif uv <= 7:
            lines.append(f"Pengangguran {uv:.1f}% dalam batas wajar — pasar kerja relatif stabil.")
        else:
            lines.append(f"Pengangguran {uv:.1f}% di atas rata-rata — konsumsi domestik berpotensi tertekan.")

    # Utang
    if debt.get("val") is not None:
        dv = debt["val"]
        if dv < 60:
            lines.append(f"Rasio utang/PDB {dv:.1f}% dalam batas aman IMF — ruang fiskal cukup lebar.")
        elif dv <= 90:
            lines.append(f"Rasio utang/PDB {dv:.1f}% mendekati zona waspada — keberlanjutan fiskal patut dicermati.")
        else:
            lines.append(f"⚠️ Rasio utang/PDB {dv:.1f}% melewati 90% — risiko fiskal tinggi, yield obligasi berpotensi tertekan ke atas.")

    # Neraca dagang
    if trade.get("val") is not None:
        tv = trade["val"] / 1e9
        if tv >= 0:
            lines.append(f"Neraca perdagangan surplus {tv:.1f}B USD — tekanan depresiasi mata uang relatif terbatas.")
        else:
            lines.append(f"Neraca perdagangan defisit {abs(tv):.1f}B USD — potensi tekanan pada nilai tukar domestik.")

    if not lines:
        return "Data belum tersedia untuk interpretasi otomatis."

    return " ".join(lines)

# ─── KALENDER EKONOMI (STATIC PLACEHOLDER) ───────────────────────────────────

CALENDAR_EVENTS = [
    {"date": "01 Sep", "event": "ISM Manufacturing PMI (AS)", "impact": "HIGH",   "forecast": "49.8", "prev": "49.0"},
    {"date": "04 Sep", "event": "RBA Rate Decision (Australia)", "impact": "HIGH",  "forecast": "4.35%","prev": "4.35%"},
    {"date": "05 Sep", "event": "GDP Kuartal Q2 (Indonesia)",    "impact": "HIGH",  "forecast": "4.9%", "prev": "5.1%"},
    {"date": "06 Sep", "event": "Nonfarm Payrolls (AS)",          "impact": "HIGH",  "forecast": "180K", "prev": "206K"},
    {"date": "09 Sep", "event": "Inflasi CPI (China)",            "impact": "MEDIUM","forecast": "0.5%", "prev": "0.2%"},
    {"date": "11 Sep", "event": "Inflasi CPI (AS)",               "impact": "HIGH",  "forecast": "3.1%", "prev": "2.9%"},
    {"date": "12 Sep", "event": "ECB Rate Decision (Eropa)",      "impact": "HIGH",  "forecast": "3.65%","prev": "3.75%"},
    {"date": "18 Sep", "event": "FOMC Rate Decision (AS)",        "impact": "HIGH",  "forecast": "5.25%","prev": "5.50%"},
    {"date": "19 Sep", "event": "BI Rate Decision (Indonesia)",   "impact": "HIGH",  "forecast": "6.25%","prev": "6.25%"},
    {"date": "25 Sep", "event": "Core PCE Price Index (AS)",      "impact": "HIGH",  "forecast": "2.7%", "prev": "2.6%"},
]

IMPACT_CLASS = {"HIGH": "cal-impact-high", "MEDIUM": "cal-impact-medium", "LOW": "cal-impact-low"}
IMPACT_LABEL = {"HIGH": "🔴 TINGGI", "MEDIUM": "🟡 SEDANG", "LOW": "🔵 RENDAH"}

# ─── MAIN PAGE ────────────────────────────────────────────────────────────────

def show():
    inject_css()

    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown("""
<div style="padding:0.5rem 0 0.2rem 0;">
<div style="font-family:'Share Tech Mono',monospace;font-size:0.62rem;letter-spacing:0.2em;color:#1E3A4A;margin-bottom:0.3rem;">
AEROVULPIS V4.1 ULTIMATE · ECONOMIC RADAR
</div>
<div style="font-family:'Share Tech Mono',monospace;font-size:1.4rem;color:#00FFC8;letter-spacing:0.08em;line-height:1.1;">
► ECONOMIC RADAR
</div>
<div style="font-family:'Exo 2',sans-serif;font-size:0.78rem;color:#4A5568;margin-top:0.3rem;margin-bottom:0.2rem;">
Pantau kondisi makroekonomi global. Baca sinyal pasar sebelum pasar bergerak.
</div>
</div>
<hr style="border:none;border-top:1px solid #1A2332;margin:0.8rem 0 1rem 0;">
""", unsafe_allow_html=True)

    # ── Sidebar controls ─────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
<div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#00FFC8;letter-spacing:0.15em;margin-bottom:0.8rem;">
◈ ECONOMIC RADAR CONFIG
</div>
""", unsafe_allow_html=True)

        selected_country_label = st.selectbox(
            "Negara Utama",
            list(COUNTRIES.keys()),
            index=0,
        )
        iso = COUNTRIES[selected_country_label]
        country_name = selected_country_label.split(" ", 1)[1]

        st.markdown("<hr style='border:none;border-top:1px solid #1A2332;margin:0.6rem 0;'>", unsafe_allow_html=True)

        compare_labels = st.multiselect(
            "Bandingkan Negara (maks. 5)",
            [k for k in COUNTRIES if k != selected_country_label],
            default=["🇺🇸 Amerika Serikat", "🇨🇳 China"],
            max_selections=5,
        )
        compare_isos = {k: COUNTRIES[k] for k in compare_labels}

        st.markdown("<hr style='border:none;border-top:1px solid #1A2332;margin:0.6rem 0;'>", unsafe_allow_html=True)
        show_calendar = st.toggle("Tampilkan Kalender Ekonomi", value=True)
        show_interpret = st.toggle("Interpretasi Otomatis", value=True)

        st.markdown(f"""
<div class="build-tag" style="margin-top:2rem;">
BUILD STABLE · 13 JUL 2026<br>
DATA: WORLD BANK OPEN DATA
</div>
""", unsafe_allow_html=True)

    # ── Fetch data utama ─────────────────────────────────────────────────────
    data_map: dict[str, dict] = {}
    with st.spinner("Mengambil data makro…"):
        for ind_name, ind_meta in INDICATORS.items():
            series = fetch_wb(iso, ind_meta["code"])
            val, year = latest_value(series)
            data_map[ind_name] = {
                "val": val, "year": year,
                "series": series,
                **ind_meta
            }

    # ── KPI Cards ────────────────────────────────────────────────────────────
    st.markdown(f'<div class="aero-section-title">▸ INDIKATOR UTAMA — {country_name.upper()}</div>', unsafe_allow_html=True)
    st.markdown('<div class="aero-section-sub">Sumber: World Bank Open Data · Data terbaru tersedia</div>', unsafe_allow_html=True)

    cols = st.columns(len(INDICATORS))
    for col, (ind_name, d) in zip(cols, data_map.items()):
        val = d["val"]
        year = d["year"]
        formatted = format_value(val, d["format"], d["unit"])
        rl = risk_level(ind_name, val)
        rl_label, rl_class = RISK_LABELS[rl]
        year_str = f"({year})" if year else ""

        with col:
            st.markdown(f"""
<div class="kpi-card" style="--accent:{d['color']};">
<div class="kpi-label">{d['icon']} {ind_name}</div>
<div class="kpi-value" style="color:{d['color']};">{formatted}</div>
<div class="kpi-desc">{year_str} {d['desc']}</div>
<span class="kpi-risk {rl_class}">{rl_label}</span>
</div>
""", unsafe_allow_html=True)

    st.markdown('<hr class="aero-divider">', unsafe_allow_html=True)

    # ── Trend Charts ────────────────────────────────────────────────────────
    st.markdown('<div class="aero-section-title">▸ TREN HISTORIS (10 TAHUN)</div>', unsafe_allow_html=True)
    st.markdown('<div class="aero-section-sub">Data dekade terakhir — identifikasi siklus makro</div>', unsafe_allow_html=True)

    chart_cols = st.columns(len(INDICATORS))
    for col, (ind_name, d) in zip(chart_cols, data_map.items()):
        with col:
            if d["series"]:
                fig = sparkline_chart(d["series"], d["color"], ind_name, d["unit"], d["format"])
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.markdown(f"""
<div style="background:#0F1520;border:1px solid #1E2A3A;border-radius:4px;padding:1rem;text-align:center;">
<span style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#374151;">DATA TIDAK TERSEDIA</span>
</div>""", unsafe_allow_html=True)

    st.markdown('<hr class="aero-divider">', unsafe_allow_html=True)

    # ── Radar + Interpretasi ────────────────────────────────────────────────
    left, right = st.columns([1, 1])

    with left:
        st.markdown('<div class="aero-section-title">▸ RADAR MAKRO</div>', unsafe_allow_html=True)
        st.markdown('<div class="aero-section-sub">Profil risiko multi-dimensi — normalisasi 0–100</div>', unsafe_allow_html=True)

        def normalize(ind_name: str, val: float | None) -> float:
            if val is None:
                return 0
            NORMS = {
                "GDP (PDB)":         (0, 5e12),
                "Inflasi":           (0, 15),
                "Pengangguran":      (0, 20),
                "Utang/PDB":         (0, 150),
                "Neraca Perdagangan":(-5e11, 5e11),
            }
            lo, hi = NORMS.get(ind_name, (0, 100))
            return round(min(max((val - lo) / (hi - lo) * 100, 0), 100), 1)

        radar_labels = list(INDICATORS.keys())
        radar_vals   = [normalize(k, data_map[k]["val"]) for k in radar_labels]
        fig_radar    = radar_chart(radar_labels, radar_vals, country_name)
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
        st.markdown(f'<div class="radar-note">NORMALISASI RELATIF · SKALA 0–100 · {country_name.upper()}</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="aero-section-title">▸ INTERPRETASI KONDISI MAKRO</div>', unsafe_allow_html=True)
        st.markdown('<div class="aero-section-sub">Analisis otomatis berbasis data live</div>', unsafe_allow_html=True)

        if show_interpret:
            interp_text = interpret_macro(country_name, data_map)
            st.markdown(f"""
<div class="interp-box">
<div class="interp-title">◈ ANALISIS MAKROEKONOMI — {country_name.upper()}</div>
<div class="interp-text">{interp_text}</div>
</div>
""", unsafe_allow_html=True)

        # Implikasi trading
        st.markdown("""
<div class="interp-box" style="border-left-color:#00FFC8;margin-top:0.8rem;">
<div class="interp-title" style="color:#00FFC8;">◈ IMPLIKASI UNTUK TRADER</div>
<div class="interp-text">
<b style="color:#00FFC8;">Forex:</b> Divergensi inflasi & suku bunga antar negara menciptakan peluang carry trade.<br>
<b style="color:#FFD93D;">Saham:</b> Inflasi rendah + pengangguran rendah = kondisi ideal untuk rally ekuitas.<br>
<b style="color:#C77DFF;">Obligasi:</b> Rasio utang tinggi berpotensi menekan yield jangka pendek naik.<br>
<b style="color:#FF6B6B;">Komoditas:</b> Neraca dagang surplus mendukung penguatan mata uang komoditas.
</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<hr class="aero-divider">', unsafe_allow_html=True)

    # ── Perbandingan Multi-Negara ────────────────────────────────────────────
    if compare_labels:
        st.markdown('<div class="aero-section-title">▸ PERBANDINGAN MULTI-NEGARA</div>', unsafe_allow_html=True)
        st.markdown('<div class="aero-section-sub">Bandingkan indikator kunci lintas negara yang dipilih</div>', unsafe_allow_html=True)

        compare_indicator = st.selectbox(
            "Indikator untuk Perbandingan",
            list(INDICATORS.keys()),
            index=1,  # Default: Inflasi
            key="compare_ind_select",
        )
        ci = INDICATORS[compare_indicator]

        all_compare = {selected_country_label: iso, **compare_isos}
        comp_labels, comp_vals = [], []

        with st.spinner("Memuat data perbandingan…"):
            for lbl, c_iso in all_compare.items():
                s = fetch_wb(c_iso, ci["code"])
                v, _ = latest_value(s)
                short_lbl = lbl.split(" ", 1)[1]
                comp_labels.append(short_lbl)
                comp_vals.append(v if v is not None else 0)

        if comp_vals:
            fig_bar = bar_compare_chart(comp_labels, comp_vals, ci["color"], compare_indicator)
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

        # Tabel perbandingan
        table_data = []
        with st.spinner("Memuat tabel lengkap…"):
            for lbl, c_iso in all_compare.items():
                row = {"Negara": lbl.split(" ", 1)[1]}
                for ind_name, ind_meta in INDICATORS.items():
                    if ind_name == "GDP (PDB)":
                        s = fetch_wb(c_iso, ind_meta["code"])
                        v, yr = latest_value(s)
                        row[ind_name] = f"{v/1e12:.2f}T" if v else "N/A"
                    elif ind_name == "Neraca Perdagangan":
                        s = fetch_wb(c_iso, ind_meta["code"])
                        v, yr = latest_value(s)
                        row[ind_name] = f"{v/1e9:.1f}B" if v else "N/A"
                    else:
                        s = fetch_wb(c_iso, ind_meta["code"])
                        v, yr = latest_value(s)
                        row[ind_name] = f"{v:.2f}%" if v else "N/A"
                table_data.append(row)

        if table_data:
            df = pd.DataFrame(table_data).set_index("Negara")
            st.dataframe(
                df,
                use_container_width=True,
            )

        st.markdown('<hr class="aero-divider">', unsafe_allow_html=True)

    # ── Kalender Ekonomi ─────────────────────────────────────────────────────
    if show_calendar:
        st.markdown('<div class="aero-section-title">▸ KALENDER EKONOMI</div>', unsafe_allow_html=True)
        st.markdown('<div class="aero-section-sub">Event makro berdampak tinggi — September 2026</div>', unsafe_allow_html=True)

        filter_impact = st.radio(
            "Filter Dampak",
            ["SEMUA", "🔴 TINGGI", "🟡 SEDANG"],
            horizontal=True,
            key="cal_filter",
        )

        for ev in CALENDAR_EVENTS:
            if filter_impact == "🔴 TINGGI" and ev["impact"] != "HIGH":
                continue
            if filter_impact == "🟡 SEDANG" and ev["impact"] not in ("HIGH", "MEDIUM"):
                continue
            ic = IMPACT_CLASS.get(ev["impact"], "cal-impact-low")
            il = IMPACT_LABEL.get(ev["impact"], "🔵 RENDAH")
            st.markdown(f"""
<div class="cal-item">
<div class="cal-date">{ev['date']}</div>
<span class="{ic}">{il}</span>
<div class="cal-event">
<b style="color:#D1D5DB;">{ev['event']}</b>
<span style="color:#374151;font-size:0.68rem;margin-left:0.5rem;">
Est: {ev['forecast']} | Prev: {ev['prev']}
</span>
</div>
</div>
""", unsafe_allow_html=True)

    # ── Footer ──────────────────────────────────────────────────────────────
    st.markdown("""
<div style="margin-top:2rem;padding-top:0.8rem;border-top:1px solid #1A2332;display:flex;justify-content:space-between;align-items:center;">
<span style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#1E3A4A;letter-spacing:0.1em;">
AEROVULPIS V4.1 ULTIMATE · ECONOMIC RADAR MODULE · BUILD STABLE
</span>
<span style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#1E3A4A;">
SUMBER DATA: WORLD BANK OPEN DATA · IMF
</span>
</div>
""", unsafe_allow_html=True)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Economic Radar · Aerovulpis",
        page_icon="📡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    show()