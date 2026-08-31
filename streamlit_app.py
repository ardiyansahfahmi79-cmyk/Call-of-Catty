"""
economic_radar_v4.py — Aerovulpis · Economic Radar (Standalone Prototype)
Run : streamlit run economic_radar_v4.py
Deps: streamlit requests pandas plotly
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Economic Radar · Aerovulpis",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

# mrv=15: ambil 15 tahun terakhir agar selalu dapat data 2025/2026 jika tersedia
WB = "https://api.worldbank.org/v2/country/{iso}/indicator/{ind}?format=json&mrv=15&per_page=15"

INDICATORS = {
    "GDP":   {"code":"NY.GDP.MKTP.CD",    "unit":"USD","fmt":"T",  "label":"GDP (PDB)",         "color":"#00FFC8","sym":"[G]"},
    "INF":   {"code":"FP.CPI.TOTL.ZG",    "unit":"%",  "fmt":"%",  "label":"Inflasi",            "color":"#FF6B6B","sym":"[I]"},
    "UNP":   {"code":"SL.UEM.TOTL.ZS",    "unit":"%",  "fmt":"%",  "label":"Pengangguran",       "color":"#FFD93D","sym":"[U]"},
    "DEBT":  {"code":"GC.DOD.TOTL.GD.ZS", "unit":"%",  "fmt":"%",  "label":"Utang/PDB",          "color":"#C77DFF","sym":"[D]"},
    "TRADE": {"code":"BN.CAB.XOKA.CD",    "unit":"USD","fmt":"B",  "label":"Neraca Perdagangan", "color":"#4FC3F7","sym":"[T]"},
}

WEIGHTS = {"GDP":0.25,"INF":0.25,"UNP":0.20,"DEBT":0.15,"TRADE":0.15}

# Warna per-negara untuk dual_line — beda tiap ISO
ISO_COLORS = {
    "ID":"#00FFC8","US":"#FF6B6B","CN":"#FFD93D","JP":"#C77DFF",
    "DE":"#4FC3F7","GB":"#FF9F43","AU":"#26de81","IN":"#fd79a8",
    "KR":"#a29bfe","SG":"#00cec9","MY":"#fdcb6e","TH":"#e17055",
    "BR":"#74b9ff","ZA":"#55efc4","SA":"#ffeaa7",
}

COUNTRIES = {
    "Indonesia":       "ID",
    "Amerika Serikat": "US",
    "China":           "CN",
    "Jepang":          "JP",
    "Jerman":          "DE",
    "Inggris":         "GB",
    "Australia":       "AU",
    "India":           "IN",
    "Korea Selatan":   "KR",
    "Singapura":       "SG",
    "Malaysia":        "MY",
    "Thailand":        "TH",
    "Brasil":          "BR",
    "Afrika Selatan":  "ZA",
    "Arab Saudi":      "SA",
}

RISK = {
    "INF":  {"low":3,  "med":6},
    "UNP":  {"low":5,  "med":10},
    "DEBT": {"low":60, "med":90},
}

CB = {
    "ID":{"name":"Bank Indonesia",    "rate":6.25,"stance":"NEUTRAL","next":"18 Sep 2026","trend":"HOLD"},
    "US":{"name":"Federal Reserve",   "rate":5.25,"stance":"HAWKISH","next":"18 Sep 2026","trend":"CUT"},
    "CN":{"name":"PBoC",              "rate":3.10,"stance":"DOVISH", "next":"20 Sep 2026","trend":"CUT"},
    "JP":{"name":"Bank of Japan",     "rate":0.25,"stance":"HAWKISH","next":"20 Sep 2026","trend":"HIKE"},
    "DE":{"name":"ECB",               "rate":3.65,"stance":"DOVISH", "next":"12 Sep 2026","trend":"CUT"},
    "GB":{"name":"Bank of England",   "rate":5.00,"stance":"NEUTRAL","next":"19 Sep 2026","trend":"CUT"},
    "AU":{"name":"RBA",               "rate":4.35,"stance":"NEUTRAL","next":"04 Sep 2026","trend":"HOLD"},
    "IN":{"name":"Reserve Bank India","rate":6.50,"stance":"NEUTRAL","next":"06 Sep 2026","trend":"CUT"},
    "KR":{"name":"Bank of Korea",     "rate":3.25,"stance":"DOVISH", "next":"22 Sep 2026","trend":"CUT"},
    "SG":{"name":"MAS",               "rate":3.68,"stance":"NEUTRAL","next":"Oct 2026",   "trend":"HOLD"},
    "MY":{"name":"Bank Negara",       "rate":3.00,"stance":"NEUTRAL","next":"05 Sep 2026","trend":"HOLD"},
    "TH":{"name":"Bank of Thailand",  "rate":2.50,"stance":"DOVISH", "next":"17 Sep 2026","trend":"CUT"},
    "BR":{"name":"BCB",               "rate":10.50,"stance":"HAWKISH","next":"17 Sep 2026","trend":"HIKE"},
    "ZA":{"name":"SARB",              "rate":8.25,"stance":"NEUTRAL","next":"19 Sep 2026","trend":"CUT"},
    "SA":{"name":"SAMA",              "rate":6.00,"stance":"HAWKISH","next":"Nov 2026",   "trend":"HOLD"},
}

SURPRISE = {
    "ID":[("GDP Q2",4.90,5.10,"2 Agu"),("Inflasi CPI",2.13,2.00,"1 Agu"),("PMI Manufaktur",51.2,50.8,"1 Agu")],
    "US":[("Nonfarm Payrolls",175,206,"2 Agu"),("CPI",2.90,3.10,"13 Jul"),("GDP",2.80,2.40,"26 Jul")],
    "CN":[("CPI",0.20,0.50,"9 Agu"),("GDP",4.70,5.10,"15 Jul"),("PMI",49.40,49.50,"31 Jul")],
    "JP":[("CPI",2.80,2.60,"19 Jul"),("GDP",0.40,0.50,"15 Agu"),("PMI",49.90,50.10,"1 Agu")],
    "DE":[("CPI",2.30,2.50,"14 Agu"),("GDP",-0.10,0.10,"30 Agu"),("PMI",42.40,43.00,"1 Agu")],
    "GB":[("CPI",2.00,2.20,"16 Jul"),("GDP",0.60,0.50,"10 Agu"),("PMI",52.10,51.50,"1 Agu")],
    "AU":[("CPI",3.80,3.60,"31 Jul"),("GDP",1.10,1.30,"5 Jun"),("Pengangguran",4.10,4.00,"15 Agu")],
    "IN":[("GDP",6.70,6.50,"30 Mei"),("CPI",3.54,3.70,"12 Jul"),("PMI",57.50,57.00,"1 Agu")],
    "KR":[("GDP",0.60,0.50,"25 Jul"),("CPI",2.60,2.40,"2 Agu"),("Ekspor",-9.9,-5.0,"1 Agu")],
    "SG":[("GDP",2.90,2.50,"12 Jul"),("CPI",2.40,2.60,"23 Jul"),("Ekspor",7.30,5.00,"17 Jul")],
    "MY":[("GDP",4.40,4.20,"16 Agu"),("CPI",1.90,2.00,"23 Jul"),("Ekspor",4.10,3.50,"30 Jul")],
    "TH":[("GDP",2.30,2.50,"19 Agu"),("CPI",0.50,0.60,"5 Agu"),("Ekspor",8.10,6.00,"22 Jul")],
    "BR":[("CPI",4.50,4.20,"9 Agu"),("GDP",2.50,2.20,"30 Agu"),("Pengangguran",6.90,7.20,"30 Agu")],
    "ZA":[("CPI",4.60,4.90,"24 Jul"),("GDP",0.40,0.30,"4 Jun"),("Pengangguran",32.90,33.50,"30 Jun")],
    "SA":[("GDP",2.60,2.30,"30 Jul"),("CPI",2.30,2.50,"11 Jul"),("PMI",56.40,55.00,"5 Agu")],
}

PAIRS = {
    "EUR/USD": {"iso":["DE","US"],"drivers":["INF","DEBT"],     "logic":"eur_usd"},
    "USD/JPY": {"iso":["US","JP"],"drivers":["INF","UNP"],      "logic":"usd_jpy"},
    "GBP/USD": {"iso":["GB","US"],"drivers":["INF","GDP"],      "logic":"gbp_usd"},
    "AUD/USD": {"iso":["AU","US"],"drivers":["TRADE","INF"],    "logic":"aud_usd"},
    "USD/CNH": {"iso":["US","CN"],"drivers":["TRADE","GDP"],    "logic":"usd_cnh"},
    "USD/IDR": {"iso":["US","ID"],"drivers":["INF","DEBT"],     "logic":"usd_idr"},
    "XAU/USD": {"iso":["US"],     "drivers":["INF","DEBT"],     "logic":"gold"},
    "US500":   {"iso":["US"],     "drivers":["GDP","UNP","INF"],"logic":"equity"},
    "BTC/USD": {"iso":["US"],     "drivers":["INF","DEBT"],     "logic":"crypto"},
}

# Kalender dengan jam WIB dan tanggal lengkap
CALENDAR = [
    {"date":"01 Sep 2026","time":"21:00 WIB","event":"ISM Manufacturing PMI",  "iso":"US","impact":"HIGH",  "forecast":"49.8","prev":"49.0", "unit":"index"},
    {"date":"04 Sep 2026","time":"11:30 WIB","event":"RBA Rate Decision",       "iso":"AU","impact":"HIGH",  "forecast":"4.35%","prev":"4.35%","unit":"%"},
    {"date":"05 Sep 2026","time":"11:00 WIB","event":"GDP Q2 Indonesia",        "iso":"ID","impact":"HIGH",  "forecast":"4.9%", "prev":"5.1%", "unit":"% YoY"},
    {"date":"05 Sep 2026","time":"14:00 WIB","event":"Bank Negara Rate Decision","iso":"MY","impact":"HIGH", "forecast":"3.00%","prev":"3.00%","unit":"%"},
    {"date":"06 Sep 2026","time":"19:30 WIB","event":"Nonfarm Payrolls",        "iso":"US","impact":"HIGH",  "forecast":"180K", "prev":"206K", "unit":"ribu"},
    {"date":"09 Sep 2026","time":"10:30 WIB","event":"CPI Tiongkok",            "iso":"CN","impact":"MEDIUM","forecast":"0.5%", "prev":"0.2%", "unit":"% YoY"},
    {"date":"11 Sep 2026","time":"19:30 WIB","event":"CPI Amerika Serikat",     "iso":"US","impact":"HIGH",  "forecast":"3.1%", "prev":"2.9%", "unit":"% YoY"},
    {"date":"12 Sep 2026","time":"20:15 WIB","event":"ECB Rate Decision",       "iso":"DE","impact":"HIGH",  "forecast":"3.65%","prev":"3.75%","unit":"%"},
    {"date":"17 Sep 2026","time":"14:00 WIB","event":"Bank of Thailand Rate",   "iso":"TH","impact":"MEDIUM","forecast":"2.25%","prev":"2.50%","unit":"%"},
    {"date":"17 Sep 2026","time":"23:00 WIB","event":"BCB Rate Decision",       "iso":"BR","impact":"HIGH",  "forecast":"10.75%","prev":"10.50%","unit":"%"},
    {"date":"18 Sep 2026","time":"01:00 WIB","event":"FOMC Rate Decision",      "iso":"US","impact":"HIGH",  "forecast":"5.00%","prev":"5.25%","unit":"%"},
    {"date":"18 Sep 2026","time":"14:00 WIB","event":"BI Rate Decision",        "iso":"ID","impact":"HIGH",  "forecast":"6.25%","prev":"6.25%","unit":"%"},
    {"date":"19 Sep 2026","time":"20:00 WIB","event":"Bank of England Rate",    "iso":"GB","impact":"HIGH",  "forecast":"4.75%","prev":"5.00%","unit":"%"},
    {"date":"19 Sep 2026","time":"21:00 WIB","event":"SARB Rate Decision",      "iso":"ZA","impact":"MEDIUM","forecast":"8.00%","prev":"8.25%","unit":"%"},
    {"date":"20 Sep 2026","time":"12:00 WIB","event":"BoJ Rate Decision",       "iso":"JP","impact":"HIGH",  "forecast":"0.25%","prev":"0.25%","unit":"%"},
    {"date":"22 Sep 2026","time":"09:00 WIB","event":"Bank of Korea Rate",      "iso":"KR","impact":"HIGH",  "forecast":"3.00%","prev":"3.25%","unit":"%"},
    {"date":"25 Sep 2026","time":"19:30 WIB","event":"Core PCE Price Index",    "iso":"US","impact":"HIGH",  "forecast":"2.7%", "prev":"2.6%", "unit":"% YoY"},
    {"date":"30 Sep 2026","time":"11:00 WIB","event":"CPI Indonesia",           "iso":"ID","impact":"HIGH",  "forecast":"2.2%", "prev":"2.13%","unit":"% YoY"},
]

# Warna per-event berdasarkan ISO (cybertech accent)
ISO_EVENT_COLORS = {
    "US":"#FF6B6B","ID":"#00FFC8","CN":"#FFD93D","JP":"#C77DFF",
    "DE":"#4FC3F7","GB":"#FF9F43","AU":"#26de81","IN":"#fd79a8",
    "KR":"#a29bfe","SG":"#00cec9","MY":"#fdcb6e","TH":"#e17055",
    "BR":"#74b9ff","ZA":"#55efc4","SA":"#ffeaa7",
}

# ══════════════════════════════════════════════════════════════════════════════
#  SENTIMENT ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def cal_sentiment(ev: dict, all_data: dict) -> tuple[str, str, str]:
    iso    = ev["iso"]
    event  = ev["event"].upper()
    fcast  = ev["forecast"].replace("%","").replace("K","000").replace("M","000000")
    prev   = ev["prev"].replace("%","").replace("K","000").replace("M","000000")
    cb     = CB.get(iso, {})
    stance = cb.get("stance","NEUTRAL")
    trend  = cb.get("trend","HOLD")
    dm     = all_data.get(iso, {})

    try:
        f_n = float(fcast)
        p_n = float(prev)
        has_num = True
    except Exception:
        f_n = p_n = 0
        has_num = False

    diff = f_n - p_n if has_num else 0

    is_rate  = any(x in event for x in ["RATE DECISION","FOMC","RBA","BOJ","ECB","BOE","BCB","BOK","MAS","SARB","SAMA","BANK NEGARA","BANK INDONESIA","BANK OF","BI RATE"])
    is_cpi   = any(x in event for x in ["CPI","INFLASI","PCE"])
    is_gdp   = "GDP" in event
    is_pmi   = "PMI" in event
    is_jobs  = any(x in event for x in ["PAYROLL","PENGANGGURAN","EMPLOYMENT","NONFARM"])
    is_trade = any(x in event for x in ["TRADE","EKSPOR","NERACA"])

    def bull(reason): return "BULLISH","sent-bull", reason
    def bear(reason): return "BEARISH","sent-bear", reason
    def neu(reason):  return "NEUTRAL","sent-neu",  reason

    if is_rate and has_num:
        if diff > 0:
            return bull(f"Rate naik {p_n:.2f}% menjadi {f_n:.2f}% — kebijakan hawkish mendukung penguatan {iso}.")
        elif diff < 0:
            return bear(f"Rate dipangkas {p_n:.2f}% menjadi {f_n:.2f}% — dovish, tekanan pada {iso}.")
        else:
            return neu(f"Rate dipertahankan {f_n:.2f}% — pasar akan fokus pada forward guidance dan proyeksi inflasi.")

    if is_cpi and has_num:
        if diff > 0:
            if stance == "HAWKISH":
                return bull(f"CPI {f_n:.1f}% (prev {p_n:.1f}%) — akselerasi inflasi konfirmasi stance hawkish {cb.get('name',iso)}, bullish {iso}.")
            elif stance == "DOVISH":
                return bear(f"CPI {f_n:.1f}% naik saat CB dovish — mismatch kebijakan, tekanan pada {iso}.")
            return neu(f"CPI naik ke {f_n:.1f}% — pasar menunggu respons kebijakan {cb.get('name',iso)}.")
        elif diff < 0:
            if stance == "DOVISH":
                return bull(f"CPI turun ke {f_n:.1f}% — membuka ruang pelonggaran lebih lanjut, risk-on untuk aset {iso}.")
            elif stance == "HAWKISH":
                return bear(f"CPI turun ke {f_n:.1f}% — narratif hawkish melemah, tekanan pada {iso}.")
            return neu(f"CPI turun ke {f_n:.1f}% — disinflasi berlanjut, tunggu sinyal CB.")
        return neu("CPI sesuai ekspektasi — dampak terbatas pada pasar.")

    if is_gdp and has_num:
        if diff > 0:
            return bull(f"GDP {f_n:.1f}% melampaui prev {p_n:.1f}% — akselerasi pertumbuhan, bullish ekuitas dan mata uang {iso}.")
        elif diff < 0:
            return bear(f"GDP {f_n:.1f}% di bawah prev {p_n:.1f}% — perlambatan ekonomi, bearish risiko aset {iso}.")
        return neu("GDP sesuai ekspektasi — dampak terbatas.")

    if is_pmi and has_num:
        if f_n > 50 and diff > 0:
            return bull(f"PMI {f_n:.1f} — ekspansi dan membaik dari {p_n:.1f}. Sektor manufaktur solid, bullish.")
        elif f_n > 50:
            return neu(f"PMI {f_n:.1f} masih ekspansi namun melambat dari {p_n:.1f}.")
        elif diff > 0:
            return neu(f"PMI {f_n:.1f} kontraksi namun membaik dari {p_n:.1f} — sinyal pemulihan awal.")
        return bear(f"PMI {f_n:.1f} kontraksi dan memburuk dari {p_n:.1f} — sektor manufaktur tertekan.")

    if is_jobs and has_num:
        is_unemp = "PENGANGGURAN" in event
        if is_unemp:
            if diff < 0: return bull(f"Pengangguran turun ke {f_n:.1f}% dari {p_n:.1f}% — pasar kerja menguat, bullish.")
            elif diff > 0: return bear(f"Pengangguran naik ke {f_n:.1f}% — pelemahan lapangan kerja, bearish.")
            return neu("Pengangguran stagnan — pasar kerja stabil.")
        else:
            if diff > 0: return bull(f"Payrolls {ev['forecast']} melampaui prev {ev['prev']} — pasar kerja solid, bullish USD.")
            elif diff < 0: return bear(f"Payrolls {ev['forecast']} di bawah prev {ev['prev']} — perlambatan tenaga kerja, bearish USD.")
            return neu("Payrolls sesuai ekspektasi.")

    # Fallback ke CB stance
    if stance == "HAWKISH" and trend in ("HIKE","HOLD"):
        return bull(f"{cb.get('name',iso)} hawkish dengan rate {cb.get('rate',0):.2f}% — supportive untuk {iso}.")
    if stance == "DOVISH" or trend == "CUT":
        return bear(f"{cb.get('name',iso)} dovish / arah cut — tekanan pada {iso}.")
    return neu("Dampak tergantung data aktual versus ekspektasi pasar.")

# ══════════════════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════════════════

def css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

html,body,.stApp{background:#080B12!important;}
.block-container{padding:1rem 1.5rem 3rem!important;max-width:100%!important;}
section[data-testid="stSidebar"]{background:#0A0D14!important;}
*{box-sizing:border-box;}
body{font-family:'Exo 2',sans-serif;}

/* HEADER */
.aero-build{font-family:'Share Tech Mono',monospace;font-size:.55rem;letter-spacing:.25em;color:#0F3028;margin-bottom:.4rem;}
.aero-title{font-family:'Share Tech Mono',monospace;font-size:1.6rem;color:#00FFC8;letter-spacing:.06em;line-height:1;}
.aero-sub{font-size:.75rem;color:#1A3020;margin-top:.3rem;font-family:'Share Tech Mono',monospace;letter-spacing:.08em;}

/* SECTION */
.sec-title{font-family:'Share Tech Mono',monospace;color:#00FFC8;font-size:.8rem;
    letter-spacing:.22em;border-left:2px solid #00FFC8;padding-left:.7rem;
    margin:1.6rem 0 .2rem;text-transform:uppercase;}
.sec-sub{font-family:'Share Tech Mono',monospace;color:#1E3A2F;font-size:.58rem;
    letter-spacing:.12em;margin-bottom:.9rem;padding-left:.9rem;}

/* KPI */
.kpi{background:linear-gradient(160deg,#0B1119 0%,#0E1520 100%);
    border:1px solid #141E2D;border-top:1px solid #00FFC820;
    border-radius:2px;padding:.95rem .9rem;position:relative;overflow:hidden;height:100%;}
.kpi-accent{position:absolute;top:0;left:0;right:0;height:1px;background:var(--c,#00FFC8);}
.kpi-sym{font-family:'Share Tech Mono',monospace;font-size:.55rem;color:#1A3D30;
    letter-spacing:.15em;margin-bottom:.25rem;}
.kpi-val{font-family:'Share Tech Mono',monospace;font-size:1.2rem;font-weight:700;
    color:var(--c,#00FFC8);line-height:1;margin-bottom:.2rem;}
.kpi-yr{font-family:'Share Tech Mono',monospace;font-size:.55rem;color:#1E3040;}
.kpi-desc{font-size:.62rem;color:#2D4040;margin-top:.15rem;line-height:1.4;}
.badge{display:inline-block;font-family:'Share Tech Mono',monospace;font-size:.52rem;
    letter-spacing:.1em;padding:1px 6px;border-radius:1px;margin-top:.35rem;font-weight:700;}
.b-ok {background:rgba(0,255,200,.08);color:#00FFC8;border:1px solid #00FFC830;}
.b-mid{background:rgba(255,217,61,.08);color:#FFD93D;border:1px solid #FFD93D30;}
.b-bad{background:rgba(255,107,107,.08);color:#FF6B6B;border:1px solid #FF6B6B30;}
.b-na {background:rgba(30,42,58,.5);color:#2D4050;border:1px solid #141E2D;}

/* DIVIDER */
.hr{border:none;border-top:1px solid #0E1826;margin:.8rem 0;}

/* INFO BOX */
.ibox{background:#0A1018;border:1px solid #141E2D;border-left:2px solid var(--lc,#C77DFF);
    border-radius:0 2px 2px 0;padding:.75rem .9rem;margin:.4rem 0;}
.ibox-t{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:var(--lc,#C77DFF);
    letter-spacing:.14em;margin-bottom:.4rem;text-transform:uppercase;}
.ibox-b{font-size:.75rem;color:#5A6E7A;line-height:1.7;}

/* HEATMAP */
.hm-wrap{overflow-x:auto;padding-bottom:.3rem;}
.hm-table{min-width:620px;width:100%;border-collapse:separate;border-spacing:2px;}
.hm-th{font-family:'Share Tech Mono',monospace;font-size:.52rem;color:#1A3040;
    letter-spacing:.1em;text-align:center;padding:.3rem .2rem;text-transform:uppercase;}
.hm-country{font-family:'Share Tech Mono',monospace;font-size:.6rem;color:#4A6070;
    padding:.35rem .4rem;white-space:nowrap;}
.hm-cell{border-radius:1px;padding:.3rem .2rem;font-family:'Share Tech Mono',monospace;
    font-size:.62rem;text-align:center;line-height:1.2;font-weight:600;cursor:default;}
.hm-g{background:rgba(0,255,200,.1);color:#00FFC8;border:1px solid #00FFC820;}
.hm-y{background:rgba(255,217,61,.1);color:#FFD93D;border:1px solid #FFD93D20;}
.hm-r{background:rgba(255,107,107,.1);color:#FF6B6B;border:1px solid #FF6B6B20;}
.hm-n{background:rgba(14,24,38,.6);color:#1A2D3A;border:1px solid #0E1826;}

/* CENTRAL BANKS */
.cb-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:.4rem;}
.cb-card{background:#0A1018;border:1px solid #141E2D;border-radius:2px;
    padding:.65rem .8rem;display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;}
.cb-name{font-family:'Share Tech Mono',monospace;font-size:.62rem;color:#5A7080;flex:1;min-width:120px;}
.cb-rate{font-family:'Share Tech Mono',monospace;font-size:.95rem;font-weight:700;color:#00FFC8;min-width:50px;}
.stance-h{font-family:'Share Tech Mono',monospace;font-size:.52rem;padding:1px 7px;border-radius:1px;
    font-weight:700;background:rgba(255,107,107,.08);color:#FF6B6B;border:1px solid #FF6B6B30;}
.stance-d{font-family:'Share Tech Mono',monospace;font-size:.52rem;padding:1px 7px;border-radius:1px;
    font-weight:700;background:rgba(0,255,200,.08);color:#00FFC8;border:1px solid #00FFC830;}
.stance-n{font-family:'Share Tech Mono',monospace;font-size:.52rem;padding:1px 7px;border-radius:1px;
    font-weight:700;background:rgba(255,217,61,.08);color:#FFD93D;border:1px solid #FFD93D30;}
.trend-hike{font-family:'Share Tech Mono',monospace;font-size:.52rem;color:#FF6B6B;font-weight:700;}
.trend-cut {font-family:'Share Tech Mono',monospace;font-size:.52rem;color:#00FFC8;font-weight:700;}
.trend-hold{font-family:'Share Tech Mono',monospace;font-size:.52rem;color:#FFD93D;font-weight:700;}
.cb-next{font-family:'Share Tech Mono',monospace;font-size:.52rem;color:#1A2D3A;margin-left:auto;}

/* SURPRISE */
.surp-card{background:#0A1018;border:1px solid #141E2D;border-radius:2px;padding:.7rem .85rem;}
.surp-name{font-family:'Share Tech Mono',monospace;font-size:.62rem;color:#4A6070;}
.surp-date{font-family:'Share Tech Mono',monospace;font-size:.52rem;color:#1A2D3A;margin-bottom:.35rem;}
.surp-track{height:3px;background:#0E1826;border-radius:2px;margin:.3rem 0;}
.surp-fill{height:3px;border-radius:2px;}
.surp-nums{display:flex;justify-content:space-between;
    font-family:'Share Tech Mono',monospace;font-size:.58rem;margin-top:.15rem;}

/* CYCLE */
.cyc-card{background:#0A1018;border:1px solid #141E2D;border-radius:2px;padding:.9rem;text-align:center;}
.cyc-phase{font-family:'Share Tech Mono',monospace;font-size:.85rem;font-weight:700;letter-spacing:.12em;margin:.3rem 0;}
.cyc-country{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:#2D4050;letter-spacing:.12em;margin-bottom:.2rem;}
.cyc-desc{font-size:.68rem;color:#3A5060;line-height:1.55;margin-top:.4rem;}

/* SCORE */
.score-num{font-family:'Share Tech Mono',monospace;font-size:2.8rem;font-weight:700;line-height:1;}
.score-lbl{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:#1E3040;letter-spacing:.18em;}
.score-bar{height:5px;background:#0E1826;border-radius:2px;margin:.45rem 0;}
.score-fill{height:5px;border-radius:2px;}

/* BIAS */
.bias-wrap{background:#0A1018;border:1px solid #141E2D;border-radius:2px;padding:.9rem;}
.bias-pair{font-family:'Share Tech Mono',monospace;font-size:1.1rem;color:#4A9EBF;
    letter-spacing:.06em;margin-bottom:.25rem;}
.bias-val{display:inline-block;font-family:'Share Tech Mono',monospace;font-size:.65rem;
    font-weight:700;padding:2px 10px;border-radius:1px;margin-bottom:.45rem;letter-spacing:.1em;}
.bias-bull{background:rgba(0,255,200,.08);color:#00FFC8;border:1px solid #00FFC830;}
.bias-bear{background:rgba(255,107,107,.08);color:#FF6B6B;border:1px solid #FF6B6B30;}
.bias-neut{background:rgba(255,217,61,.08);color:#FFD93D;border:1px solid #FFD93D30;}
.bias-txt{font-size:.73rem;color:#4A6070;line-height:1.65;}

/* CALENDAR — cybertech style */
.cal-row{background:#0A1018;border:1px solid #141E2D;border-radius:2px;
    padding:.65rem .85rem;margin-bottom:.35rem;position:relative;overflow:hidden;}
.cal-accent{position:absolute;left:0;top:0;bottom:0;width:2px;background:var(--ec,#00FFC8);}
.cal-header{display:flex;align-items:flex-start;gap:.6rem;flex-wrap:wrap;}
.cal-dt{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:#2D4050;min-width:90px;}
.cal-time{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:var(--ec,#00FFC8);
    font-weight:700;min-width:80px;}
.cal-iso-tag{font-family:'Share Tech Mono',monospace;font-size:.52rem;
    padding:1px 5px;border-radius:1px;border:1px solid var(--ec,#00FFC8);
    color:var(--ec,#00FFC8);background:rgba(0,255,200,.05);min-width:28px;text-align:center;}
.cal-title{font-family:'Share Tech Mono',monospace;font-size:.75rem;
    color:var(--ec,#00FFC8);font-weight:700;letter-spacing:.05em;flex:1;line-height:1.3;}
.cal-badges{display:flex;gap:.3rem;align-items:center;margin-left:auto;}
.cal-data{display:flex;gap:1.2rem;margin-top:.4rem;padding-top:.35rem;
    border-top:1px solid #0E1826;flex-wrap:wrap;}
.cal-data-item{font-family:'Share Tech Mono',monospace;font-size:.58rem;}
.cal-data-lbl{color:#1A2D3A;font-size:.52rem;letter-spacing:.1em;display:block;}
.cal-data-val{color:#4A6070;font-weight:700;font-size:.65rem;}
.cal-reason{font-family:'Share Tech Mono',monospace;font-size:.55rem;color:#2D4050;
    margin-top:.3rem;line-height:1.5;font-style:italic;}

.imp-h{font-family:'Share Tech Mono',monospace;font-size:.5rem;padding:1px 5px;
    border-radius:1px;font-weight:700;background:rgba(255,107,107,.1);
    color:#FF6B6B;border:1px solid #FF6B6B30;}
.imp-m{font-family:'Share Tech Mono',monospace;font-size:.5rem;padding:1px 5px;
    border-radius:1px;font-weight:700;background:rgba(255,217,61,.1);
    color:#FFD93D;border:1px solid #FFD93D30;}
.imp-l{font-family:'Share Tech Mono',monospace;font-size:.5rem;padding:1px 5px;
    border-radius:1px;background:rgba(14,24,38,.6);color:#1E3D50;border:1px solid #0E1826;}

/* SENTIMENT */
.sent-bull{font-family:'Share Tech Mono',monospace;font-size:.5rem;padding:1px 6px;
    border-radius:1px;font-weight:700;background:rgba(0,255,200,.08);
    color:#00FFC8;border:1px solid #00FFC830;}
.sent-bear{font-family:'Share Tech Mono',monospace;font-size:.5rem;padding:1px 6px;
    border-radius:1px;font-weight:700;background:rgba(255,107,107,.08);
    color:#FF6B6B;border:1px solid #FF6B6B30;}
.sent-neu{font-family:'Share Tech Mono',monospace;font-size:.5rem;padding:1px 6px;
    border-radius:1px;font-weight:700;background:rgba(255,217,61,.08);
    color:#FFD93D;border:1px solid #FFD93D30;}

/* CARRY */
.carry-row{display:flex;align-items:center;gap:.5rem;background:#0A1018;
    border:1px solid #141E2D;border-radius:2px;padding:.5rem .75rem;margin-bottom:.3rem;flex-wrap:wrap;}
.carry-pair{font-family:'Share Tech Mono',monospace;font-size:.65rem;color:#4A9EBF;min-width:120px;}
.carry-diff{font-family:'Share Tech Mono',monospace;font-size:.85rem;font-weight:700;color:#00FFC8;min-width:55px;}
.carry-desc{font-size:.65rem;color:#2D4050;flex:1;}

/* STREAMLIT OVERRIDES */
.stSelectbox label,.stMultiSelect label,.stRadio label,.stCheckbox label{
    font-family:'Share Tech Mono',monospace!important;font-size:.65rem!important;
    color:#2D5040!important;letter-spacing:.1em!important;}
div[data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid #0E1826!important;}
div[data-baseweb="tab"]{font-family:'Share Tech Mono',monospace!important;font-size:.62rem!important;
    letter-spacing:.1em!important;color:#1E3040!important;background:transparent!important;}
div[data-baseweb="tab"][aria-selected="true"]{color:#00FFC8!important;border-bottom:2px solid #00FFC8!important;}
button[data-testid="baseButton-secondary"]{
    background:#0A1018!important;border:1px solid #141E2D!important;
    color:#2D5040!important;font-family:'Share Tech Mono',monospace!important;
    border-radius:2px!important;font-size:.62rem!important;letter-spacing:.08em!important;}
.stDataFrame{border:1px solid #141E2D!important;}

@media(max-width:768px){
    .block-container{padding:.5rem .6rem 3rem!important;}
    .aero-title{font-size:1.2rem;}
    .kpi-val{font-size:1rem;}
    .cb-card{gap:.3rem;}
    .cb-next{margin-left:0;width:100%;}
    .carry-row{flex-wrap:wrap;}
    .cal-header{gap:.4rem;}
}
</style>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def fetch(iso: str, code: str) -> list[dict]:
    try:
        r = requests.get(WB.format(iso=iso, ind=code), timeout=10)
        raw = r.json()
        if len(raw) < 2 or not raw[1]:
            return []
        # Filter None, sort ascending, ambil 10 terbaru
        entries = sorted(
            [{"year":int(x["date"]),"value":x["value"]}
             for x in raw[1] if x.get("value") is not None],
            key=lambda x: x["year"]
        )
        return entries[-10:]  # 10 data terbaru yang tersedia
    except Exception:
        return []

def latest(series):
    for d in reversed(series):
        if d["value"] is not None:
            return d["value"], d["year"]
    return None, None

def fmt(v, f):
    if v is None: return "N/A"
    if f == "T":  return f"{v/1e12:.2f} T USD"
    if f == "B":
        # Tampilkan tanda negatif dengan jelas beserta keterangan
        if v < 0:
            return f"-{abs(v)/1e9:.1f} B USD"
        return f"{v/1e9:.1f} B USD"
    return f"{v:.2f}%"

def risk(key, v):
    if v is None: return "N/A","b-na"
    th = RISK.get(key)
    if th is None:
        tv = v/1e9
        if tv >= 5:  return "SURPLUS","b-ok"
        if tv >= 0:  return "SEIMBANG","b-mid"
        return "DEFISIT","b-bad"
    if v <= th["low"]: return "RENDAH","b-ok"
    if v <= th["med"]: return "SEDANG","b-mid"
    return "TINGGI","b-bad"

def hm_cls(key, v):
    if v is None: return "hm-n"
    if key == "SCORE":
        if v >= 65: return "hm-g"
        if v >= 45: return "hm-y"
        return "hm-r"
    if key == "GDP":
        if v >= 1e12: return "hm-g"
        if v >= 3e11: return "hm-y"
        return "hm-r"
    if key == "TRADE":
        tv = v/1e9
        if tv >= 5:  return "hm-g"
        if tv >= 0:  return "hm-y"
        return "hm-r"
    th = RISK.get(key)
    if th is None: return "hm-n"
    if v <= th["low"]: return "hm-g"
    if v <= th["med"]: return "hm-y"
    return "hm-r"

def hm_txt(key, v):
    if v is None: return "—"
    if key == "SCORE": return f"{v:.0f}"
    if key == "GDP":   return f"{v/1e12:.1f}T"
    if key == "TRADE": return f"{v/1e9:.0f}B"
    return f"{v:.1f}%"

def norm(key, v):
    if v is None: return 0
    NORMS = {"GDP":(0,5e12),"INF":(0,15),"UNP":(0,20),"DEBT":(0,150),"TRADE":(-5e11,5e11)}
    lo, hi = NORMS.get(key,(0,100))
    return round(min(max((v-lo)/(hi-lo)*100,0),100),1)

def macro_score(dm):
    def s_gdp(v):   return min(v/1e12*10,100) if v else 50
    def s_inf(v):   return max(0,100-(v-2)**2*3) if v else 50
    def s_unp(v):   return max(0,100-v*7) if v else 50
    def s_debt(v):  return max(0,100-v*0.6) if v else 50
    def s_trade(v): return 65 if v is None else (70 if v>=0 else 38)
    s = {
        "GDP":  s_gdp(dm.get("GDP",{}).get("val")),
        "INF":  s_inf(dm.get("INF",{}).get("val")),
        "UNP":  s_unp(dm.get("UNP",{}).get("val")),
        "DEBT": s_debt(dm.get("DEBT",{}).get("val")),
        "TRADE":s_trade(dm.get("TRADE",{}).get("val")),
    }
    total = round(sum(s[k]*WEIGHTS[k] for k in s),1)
    if total>=72: grade,gc="STRONG","#00FFC8"
    elif total>=55: grade,gc="STABLE","#4FC3F7"
    elif total>=38: grade,gc="FRAGILE","#FFD93D"
    else: grade,gc="WEAK","#FF6B6B"
    return total,grade,gc

def detect_cycle(dm):
    inf=dm.get("INF",{}).get("val"); unp=dm.get("UNP",{}).get("val")
    gdp_s=dm.get("GDP",{}).get("series",[])
    growing=len(gdp_s)>=2 and gdp_s[-1]["value"]>gdp_s[-2]["value"]
    i=inf or 0; u=unp or 100
    if growing and i<4 and u<6: return "EKSPANSI","#00FFC8","Pertumbuhan solid, inflasi terkendali, lapangan kerja kuat. Favorable untuk ekuitas dan aset risiko."
    if growing and i>=4: return "PUNCAK","#FFD93D","Pertumbuhan tinggi namun inflasi memanas. CB cenderung hawkish. Monitor potensi koreksi."
    if not growing and i>=4: return "STAGFLASI","#FF6B6B","Pertumbuhan melambat namun inflasi persisten. Kondisi paling sulit — safe-haven outperform."
    if not growing and u>7: return "KONTRAKSI","#FF6B6B","Ekonomi menyusut, pengangguran naik. Safe-haven dan obligasi jangka pendek menguat."
    return "PEMULIHAN","#4FC3F7","Kontraksi mereda, pertumbuhan mulai kembali. Sinyal akumulasi awal siklus."

def interpret(name, dm):
    out=[]
    g=dm.get("GDP",{}).get("val"); i=dm.get("INF",{}).get("val")
    u=dm.get("UNP",{}).get("val"); d=dm.get("DEBT",{}).get("val")
    t=dm.get("TRADE",{}).get("val")
    if g: out.append(f"PDB {name} {g/1e12:.2f}T USD — {'ekonomi signifikan di kawasan' if g>5e11 else 'ekonomi berkembang dengan ruang ekspansi luas'}.")
    if i is not None:
        if i<2: out.append(f"Inflasi {i:.1f}% di bawah target — risiko deflasi perlu dicermati.")
        elif i<=4: out.append(f"Inflasi {i:.1f}% terkendali — kondusif untuk pertumbuhan.")
        elif i<=7: out.append(f"Inflasi {i:.1f}% zona waspada — stance hawkish CB kemungkinan berlanjut.")
        else: out.append(f"Inflasi {i:.1f}% kritis — tekanan signifikan pada obligasi dan daya beli.")
    if u is not None:
        if u<4: out.append(f"Pengangguran {u:.1f}% sangat rendah — pasar kerja ketat, risiko tekanan upah.")
        elif u<=7: out.append(f"Pengangguran {u:.1f}% dalam batas normal.")
        else: out.append(f"Pengangguran {u:.1f}% tinggi — konsumsi domestik berpotensi tertekan.")
    if d is not None:
        if d<60: out.append(f"Utang/PDB {d:.0f}% aman — ruang fiskal luas.")
        elif d<=90: out.append(f"Utang/PDB {d:.0f}% mendekati batas waspada IMF.")
        else: out.append(f"Utang/PDB {d:.0f}% melewati 90% — risiko fiskal tinggi.")
    if t is not None:
        tv=t/1e9
        status="surplus" if tv>=0 else "defisit"
        out.append(f"Neraca perdagangan {status} {abs(tv):.1f}B USD — {'tekanan depresiasi terbatas' if tv>=0 else 'tekanan pada nilai tukar domestik'}.")
    return " ".join(out) if out else "Data tidak lengkap."

def macro_bias(pair, all_data):
    cfg=PAIRS.get(pair)
    if not cfg: return "NEUTRAL","#FFD93D","Data tidak tersedia."
    logic=cfg["logic"]; isos=cfg["iso"]
    cb_a=CB.get(isos[0],{}); cb_b=CB.get(isos[1],{}) if len(isos)>1 else {}
    r_a=cb_a.get("rate",0); r_b=cb_b.get("rate",0)
    if logic in ("eur_usd","gbp_usd","aud_usd"):
        if r_b>r_a and cb_b.get("stance")=="HAWKISH":
            return "BEARISH","#FF6B6B",f"Rate diferensial menguntungkan USD ({CB.get(isos[1],{}).get('name','')} hawkish, {r_b:.2f}%). Tekanan pada base currency."
        if r_a>r_b or cb_a.get("stance")=="HAWKISH":
            return "BULLISH","#00FFC8",f"Rate base lebih kompetitif ({cb_a.get('name','')} {cb_a.get('stance','')} {r_a:.2f}%). Bias beli {pair}."
        return "NEUTRAL","#FFD93D",f"Rate diferensial sempit ({r_a:.2f}% vs {r_b:.2f}%). Tunggu katalis."
    if logic=="usd_jpy":
        if r_b>0.5 and cb_b.get("stance")=="HAWKISH":
            return "BEARISH","#FF6B6B",f"BoJ normalisasi ({r_b:.2f}%) — JPY menguat. Bias jual USD/JPY."
        return "BULLISH","#00FFC8",f"Spread Fed-BoJ masih lebar ({r_a:.2f}% vs {r_b:.2f}%). Carry trade menarik."
    if logic in ("usd_cnh","usd_idr"):
        diff=r_a-r_b
        if diff>2: return "BULLISH","#00FFC8",f"Fed ({r_a:.2f}%) di atas {cb_b.get('name','')} ({r_b:.2f}%). Tekanan depresiasi {pair.split('/')[1]}."
        return "NEUTRAL","#FFD93D",f"Rate gap mengecil. Monitor stance {cb_b.get('name','')}."
    if logic=="gold":
        dm_us=all_data.get("US",{}); iv=dm_us.get("INF",{}).get("val") or 0; dv=dm_us.get("DEBT",{}).get("val") or 0
        if iv>3.5 or dv>100: return "BULLISH","#00FFC8",f"Inflasi AS {iv:.1f}% + utang/PDB {dv:.0f}% mendukung permintaan safe-haven emas."
        return "NEUTRAL","#FFD93D",f"Inflasi AS {iv:.1f}% terkendali. Emas ranging."
    if logic=="equity":
        dm_us=all_data.get("US",{}); iv=dm_us.get("INF",{}).get("val") or 0; uv=dm_us.get("UNP",{}).get("val") or 0
        if iv<4 and uv<5: return "BULLISH","#00FFC8",f"Makro AS goldilocks — inflasi {iv:.1f}%, pengangguran {uv:.1f}%."
        if iv>5: return "BEARISH","#FF6B6B",f"Inflasi AS {iv:.1f}% — headwind untuk valuasi ekuitas."
        return "NEUTRAL","#FFD93D","Makro campuran. Selektif sektor defensif."
    if logic=="crypto":
        dm_us=all_data.get("US",{}); iv=dm_us.get("INF",{}).get("val") or 0
        if iv<3.5: return "BULLISH","#00FFC8","Likuiditas membaik, inflasi terkendali — favorable untuk kripto."
        return "BEARISH","#FF6B6B",f"Inflasi {iv:.1f}% menekan likuiditas. Risk-off environment."
    return "NEUTRAL","#FFD93D","Analisis tidak tersedia."

# ══════════════════════════════════════════════════════════════════════════════
#  PLOTLY THEME
# ══════════════════════════════════════════════════════════════════════════════

BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Share Tech Mono, monospace", color="#1E3D50", size=9),
    margin=dict(l=8, r=8, t=30, b=8),
    xaxis=dict(gridcolor="#0A1220", linecolor="#0E1826", tickcolor="#0E1826",
               tickfont=dict(size=8), showgrid=True),
    yaxis=dict(gridcolor="#0A1220", linecolor="#0E1826", tickcolor="#0E1826",
               tickfont=dict(size=8), showgrid=True),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=8)),
    hovermode="x unified",
)

# Chart static (tidak bisa digerakkan), Radar tetap interaktif
CHART_CFG = {"staticPlot": True}
RADAR_CFG = {"displayModeBar": False, "scrollZoom": False}

def sparkline(series, color, title, fmt_key=""):
    """Chart smooth dengan gradient fill — lebih menarik dari garis kaku."""
    if not series: return None
    years = [d["year"] for d in series]
    vals  = [d["value"] for d in series]
    fig = go.Figure()
    # Area gradient
    fig.add_trace(go.Scatter(
        x=years, y=vals,
        mode="lines",
        line=dict(color=color, width=2, shape="spline", smoothing=1.2),
        fill="tozeroy",
        fillcolor=f"{color}15",
        hovertemplate=f"<b>%{{x}}</b> — %{{y:.2f}}<extra></extra>",
        showlegend=False,
    ))
    # Titik highlight di ujung
    fig.add_trace(go.Scatter(
        x=[years[-1]], y=[vals[-1]],
        mode="markers",
        marker=dict(color=color, size=6, line=dict(color="#080B12", width=1.5)),
        hoverinfo="skip", showlegend=False,
    ))
    fig.update_layout(**BASE,
        title=dict(text=title, font=dict(size=9, color=color), x=0, y=0.98),
        margin=dict(l=8, r=8, t=28, b=8),
    )
    fig.update_xaxes(tickformat="d")
    return fig

def radar_chart(labels, values, name):
    fig = go.Figure(go.Scatterpolar(
        r=values, theta=labels, fill="toself",
        fillcolor="rgba(0,255,200,0.05)",
        line=dict(color="#00FFC8", width=1.8),
        marker=dict(color="#00FFC8", size=5, line=dict(color="#080B12", width=1)),
        name=name,
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Share Tech Mono, monospace", color="#1E3D50", size=9),
        margin=dict(l=22, r=22, t=22, b=22),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, gridcolor="#0A1220", linecolor="#0E1826",
                color="#1A2D3A", range=[0,100], tickfont=dict(size=7)),
            angularaxis=dict(gridcolor="#0A1220", linecolor="#0E1826"),
        ),
        showlegend=False,
    )
    return fig

def bar_chart(labels, values, color, title):
    # Bar dengan warna gradient per-bar
    n = len(values)
    colors = [f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},{0.4+0.5*i/max(n-1,1):.2f})" for i in range(n)]
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker=dict(color=colors, line=dict(color=color, width=0.8)),
        hovertemplate="%{x}: <b>%{y:.2f}</b><extra></extra>",
    ))
    fig.update_layout(**BASE,
        title=dict(text=title, font=dict(size=9, color=color), x=0),
        bargap=0.3,
    )
    fig.update_xaxes(tickangle=-30, tickfont=dict(size=8))
    return fig

def dual_line(ser_a, ser_b, color_a, color_b, label_a, label_b, title):
    """Dual line dengan warna berbeda, smooth spline, marker ujung."""
    fig = go.Figure()
    for ser, col, lbl in [(ser_a, color_a, label_a), (ser_b, color_b, label_b)]:
        if not ser: continue
        years = [d["year"] for d in ser]
        vals  = [d["value"] for d in ser]
        fig.add_trace(go.Scatter(
            x=years, y=vals,
            mode="lines",
            name=lbl,
            line=dict(color=col, width=2, shape="spline", smoothing=1.0),
            hovertemplate=f"<b>{lbl}</b> %{{x}}: %{{y:.2f}}<extra></extra>",
        ))
        # Titik ujung
        fig.add_trace(go.Scatter(
            x=[years[-1]], y=[vals[-1]],
            mode="markers",
            marker=dict(color=col, size=6, line=dict(color="#080B12", width=1.5)),
            showlegend=False, hoverinfo="skip",
        ))
    fig.update_layout(**BASE,
        title=dict(text=title, font=dict(size=9, color="#4A9EBF"), x=0),
    )
    fig.update_xaxes(tickformat="d")
    return fig

# ══════════════════════════════════════════════════════════════════════════════
#  SECTIONS
# ══════════════════════════════════════════════════════════════════════════════

def s_overview(country_name, dm):
    st.markdown(f'<div class="sec-title">INDIKATOR UTAMA — {country_name.upper()}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">WORLD BANK OPEN DATA · CACHE 1 JAM · DATA TERBARU TERSEDIA</div>', unsafe_allow_html=True)

    cols = st.columns(5)
    keys = ["GDP","INF","UNP","DEBT","TRADE"]
    for col, key in zip(cols, keys):
        d=dm[key]; meta=INDICATORS[key]; v=d["val"]; yr=d["year"]
        fv=fmt(v,meta["fmt"]); rl,rc=risk(key,v)
        # Catatan khusus untuk TRADE negatif
        trade_note = ""
        if key == "TRADE" and v is not None and v < 0:
            trade_note = '<div style="font-family:\'Share Tech Mono\',monospace;font-size:.5rem;color:#FF6B6B;margin-top:.2rem;">* Defisit: impor &gt; ekspor</div>'
        with col:
            st.markdown(f"""
<div class="kpi" style="--c:{meta['color']};">
<div class="kpi-accent"></div>
<div class="kpi-sym">{meta['sym']} {meta['label'].upper()}</div>
<div class="kpi-val">{fv}</div>
<div class="kpi-yr">{f'({yr})' if yr else ''}</div>
<div class="kpi-desc">{meta['label']}</div>
<span class="badge {rc}">{rl}</span>
{trade_note}
</div>""", unsafe_allow_html=True)

    st.markdown('<hr class="hr">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">TREN HISTORIS (10 TAHUN)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">IDENTIFIKASI SIKLUS DAN MOMENTUM MAKRO · DATA TERBARU WORLD BANK</div>', unsafe_allow_html=True)

    cols2 = st.columns(5)
    for col, key in zip(cols2, keys):
        d=dm[key]; meta=INDICATORS[key]
        with col:
            fig = sparkline(d["series"], meta["color"], meta["label"])
            if fig:
                st.plotly_chart(fig, use_container_width=True, config=CHART_CFG)
            else:
                st.markdown(f'<div class="kpi" style="--c:{meta["color"]};text-align:center;min-height:130px;display:flex;align-items:center;justify-content:center;"><span style="font-family:\'Share Tech Mono\',monospace;font-size:.52rem;color:#1A2D3A;">DATA TIDAK<br>TERSEDIA</span></div>', unsafe_allow_html=True)

    st.markdown('<hr class="hr">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">RADAR MAKRO + MACRO SCORE CARD</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">PROFIL RISIKO MULTI-DIMENSI · SKOR KESEHATAN EKONOMI 0–100</div>', unsafe_allow_html=True)

    c1,c2,c3 = st.columns([1.3,0.8,1.9])
    with c1:
        labels=[INDICATORS[k]["label"] for k in keys]
        vals=[norm(k,dm[k]["val"]) for k in keys]
        fig=radar_chart(labels,vals,country_name)
        st.plotly_chart(fig,use_container_width=True,config=RADAR_CFG)
        st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:.52rem;color:#1A2D3A;text-align:center;margin-top:-.4rem;">NORMALISASI 0–100 · {country_name.upper()}</div>', unsafe_allow_html=True)

    with c2:
        total,grade,gc=macro_score(dm)
        st.markdown(f"""
<div style="text-align:center;padding:.5rem 0;">
<div class="score-num" style="color:{gc};">{total:.0f}</div>
<div class="score-lbl">MACRO SCORE</div>
<div class="score-bar"><div class="score-fill" style="width:{total:.0f}%;background:{gc};"></div></div>
<span class="badge" style="background:{gc}10;color:{gc};border:1px solid {gc}30;font-size:.58rem;letter-spacing:.12em;">{grade}</span>
<div style="font-family:'Share Tech Mono',monospace;font-size:.52rem;color:#1A2D3A;margin-top:.8rem;line-height:1.8;">
72+ STRONG<br>55+ STABLE<br>38+ FRAGILE<br>&lt;38 WEAK
</div>
</div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
<div class="ibox" style="--lc:#C77DFF;">
<div class="ibox-t">ANALISIS KONDISI MAKRO — {country_name.upper()}</div>
<div class="ibox-b">{interpret(country_name, dm)}</div>
</div>
<div class="ibox" style="--lc:#00FFC8;margin-top:.4rem;">
<div class="ibox-t">IMPLIKASI UNTUK TRADER &amp; INVESTOR</div>
<div class="ibox-b">
<b style="color:#00FFC8;">FOREX</b> — Divergensi inflasi &amp; suku bunga antar negara menciptakan peluang carry trade.<br>
<b style="color:#FFD93D;">SAHAM</b> — Inflasi rendah + pengangguran rendah = goldilocks environment untuk ekuitas.<br>
<b style="color:#C77DFF;">OBLIGASI</b> — Rasio utang tinggi menekan yield jangka pendek ke atas.<br>
<b style="color:#FF6B6B;">KOMODITAS</b> — Surplus neraca dagang mendukung penguatan mata uang komoditas.
</div>
</div>""", unsafe_allow_html=True)

def s_heatmap(all_data):
    st.markdown('<div class="sec-title">COUNTRY HEAT MAP RISIKO</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">15 NEGARA × 5 INDIKATOR + MACRO SCORE · HIJAU=AMAN · KUNING=WASPADA · MERAH=BAHAYA</div>', unsafe_allow_html=True)

    col_keys=["GDP","INF","UNP","DEBT","TRADE","SCORE"]
    col_heads=["GDP","INFLASI","PENGANGGURAN","UTANG/PDB","NERACA DAG.","MACRO SCORE"]
    html='<div class="hm-wrap"><table class="hm-table"><thead><tr>'
    html+='<th class="hm-th" style="text-align:left;min-width:120px;">NEGARA</th>'
    for h in col_heads:
        html+=f'<th class="hm-th">{h}</th>'
    html+='</tr></thead><tbody>'

    for name,iso in COUNTRIES.items():
        dm=all_data.get(iso,{})
        vals={"GDP":dm.get("GDP",{}).get("val"),"INF":dm.get("INF",{}).get("val"),
              "UNP":dm.get("UNP",{}).get("val"),"DEBT":dm.get("DEBT",{}).get("val"),
              "TRADE":dm.get("TRADE",{}).get("val")}
        total,_,_=macro_score(dm)
        vals["SCORE"]=total
        html+=f'<tr><td class="hm-country">{name}</td>'
        for key in col_keys:
            v=vals.get(key); cls=hm_cls(key,v); txt=hm_txt(key,v)
            html+=f'<td class="hm-cell {cls}">{txt}</td>'
        html+='</tr>'
    st.markdown(html+"</tbody></table></div>", unsafe_allow_html=True)

def s_bias(all_data):
    st.markdown('<div class="sec-title">MACRO BIAS SCANNER</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">ANALISIS FUNDAMENTAL PER INSTRUMEN — JANGAN TRADE MELAWAN MAKRO</div>', unsafe_allow_html=True)

    pair=st.selectbox("Instrumen",list(PAIRS.keys()),key="bias_pair_v4")
    bias,bc,btxt=macro_bias(pair,all_data)
    bclass={"BULLISH":"bias-bull","BEARISH":"bias-bear","NEUTRAL":"bias-neut"}[bias]
    cfg=PAIRS[pair]; isos=cfg["iso"]

    c1,c2=st.columns([1,2])
    with c1:
        cb_html=""
        for iso in isos:
            cb=CB.get(iso,{})
            if cb:
                sc={"HAWKISH":"stance-h","DOVISH":"stance-d","NEUTRAL":"stance-n"}.get(cb["stance"],"stance-n")
                tr={"HIKE":"trend-hike","CUT":"trend-cut","HOLD":"trend-hold"}.get(cb["trend"],"trend-hold")
                cb_html+=f'<div style="margin:.3rem 0;display:flex;align-items:center;gap:.4rem;flex-wrap:wrap;"><span style="font-family:\'Share Tech Mono\',monospace;font-size:.6rem;color:#3A5060;">{cb["name"]}</span><span class="cb-rate" style="font-size:.8rem;">{cb["rate"]:.2f}%</span><span class="{sc}">{cb["stance"]}</span><span class="{tr}">{cb["trend"]}</span></div>'
        st.markdown(f"""
<div class="bias-wrap">
<div class="bias-pair">{pair}</div>
<div class="bias-val {bclass}">{bias}</div>
<div class="bias-txt">{btxt}</div>
<hr class="hr" style="margin:.5rem 0;">
{cb_html}
</div>""", unsafe_allow_html=True)

    with c2:
        drivers=cfg["drivers"]
        if len(isos)>=2:
            iso_a,iso_b=isos[0],isos[1]
            # Gunakan ISO_COLORS untuk warna yang berbeda
            ca=ISO_COLORS.get(iso_a,"#00FFC8")
            cb_col=ISO_COLORS.get(iso_b,"#FF6B6B")
            n_a=[k for k,v in COUNTRIES.items() if v==iso_a]
            n_b=[k for k,v in COUNTRIES.items() if v==iso_b]
            la=n_a[0] if n_a else iso_a
            lb=n_b[0] if n_b else iso_b
            for dk in drivers[:2]:
                sa=all_data.get(iso_a,{}).get(dk,{}).get("series",[])
                sb=all_data.get(iso_b,{}).get(dk,{}).get("series",[])
                if sa and sb:
                    fig=dual_line(sa,sb,ca,cb_col,la,lb,INDICATORS[dk]["label"])
                    st.plotly_chart(fig,use_container_width=True,config=CHART_CFG)
                elif sa:
                    fig=sparkline(sa,ca,f"{INDICATORS[dk]['label']} — {la}")
                    if fig: st.plotly_chart(fig,use_container_width=True,config=CHART_CFG)
        elif isos:
            ca=ISO_COLORS.get(isos[0],"#00FFC8")
            for dk in drivers[:2]:
                sa=all_data.get(isos[0],{}).get(dk,{}).get("series",[])
                if sa:
                    fig=sparkline(sa,ca,INDICATORS[dk]["label"])
                    if fig: st.plotly_chart(fig,use_container_width=True,config=CHART_CFG)

def s_surprise(iso):
    name=[k for k,v in COUNTRIES.items() if v==iso]; name=name[0] if name else iso
    st.markdown('<div class="sec-title">ECONOMIC SURPRISE INDEX</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">AKTUAL VS KONSENSUS FORECAST · DIVERGENSI = POTENSI VOLATILITAS</div>', unsafe_allow_html=True)

    evts=SURPRISE.get(iso,[])
    if not evts:
        st.markdown('<div class="ibox" style="--lc:#1A2D3A;"><div class="ibox-b">Data surprise tidak tersedia.</div></div>', unsafe_allow_html=True)
        return

    cols=st.columns(len(evts)); agg=0
    for col,(ename,actual,forecast,date) in zip(cols,evts):
        diff=actual-forecast
        pct=diff/max(abs(forecast),0.001)*100
        agg+=pct; beat=diff>0
        bc="#00FFC8" if beat else "#FF6B6B"
        bw=min(abs(pct)*2,100)
        scls="b-ok" if beat else "b-bad"
        slbl=f"BEAT +{diff:.2f}" if beat else f"MISS {diff:.2f}"
        with col:
            st.markdown(f"""
<div class="surp-card">
<div class="surp-name">{ename}</div>
<div class="surp-date">{date}</div>
<div class="surp-track"><div class="surp-fill" style="width:{bw:.0f}%;background:{bc};"></div></div>
<div class="surp-nums">
<span style="color:{bc};font-weight:700;">A: {actual}</span>
<span style="color:#1A2D3A;">F: {forecast}</span>
</div>
<span class="badge {scls}" style="margin-top:.3rem;font-size:.5rem;">{slbl}</span>
</div>""", unsafe_allow_html=True)

    avg=agg/len(evts); ac="#00FFC8" if avg>0 else "#FF6B6B"
    albl=f"MACRO BEAT +{avg:.1f}%" if avg>0 else f"MACRO MISS {avg:.1f}%"
    adesc="Data ekonomi di atas ekspektasi — potensi penguatan aset domestik." if avg>0 else "Data ekonomi di bawah ekspektasi — tekanan pada mata uang dan aset risiko."
    st.markdown(f"""
<div class="ibox" style="--lc:{ac};margin-top:.5rem;">
<div class="ibox-t">AGGREGATE SURPRISE — {name.upper()}</div>
<div class="ibox-b"><b style="color:{ac};">{albl}</b> — {adesc}</div>
</div>""", unsafe_allow_html=True)

    st.markdown('<hr class="hr">', unsafe_allow_html=True)
    other=st.selectbox("Surprise Index Negara Lain",list(COUNTRIES.keys()),index=1,key="surp_other_v4")
    if COUNTRIES[other]!=iso:
        evts2=SURPRISE.get(COUNTRIES[other],[])
        if evts2:
            cols2=st.columns(len(evts2))
            for col,(ename,actual,forecast,date) in zip(cols2,evts2):
                diff=actual-forecast; beat=diff>0
                bc="#00FFC8" if beat else "#FF6B6B"
                bw=min(abs(diff/max(abs(forecast),0.001))*200,100)
                scls="b-ok" if beat else "b-bad"
                with col:
                    st.markdown(f"""
<div class="surp-card">
<div class="surp-name">{ename}</div>
<div class="surp-date">{date}</div>
<div class="surp-track"><div class="surp-fill" style="width:{bw:.0f}%;background:{bc};"></div></div>
<div class="surp-nums">
<span style="color:{bc};font-weight:700;">A: {actual}</span>
<span style="color:#1A2D3A;">F: {forecast}</span>
</div>
<span class="badge {scls}" style="font-size:.5rem;">{'BEAT' if beat else 'MISS'} {diff:+.2f}</span>
</div>""", unsafe_allow_html=True)

def s_cycle(all_data,selected_names):
    st.markdown('<div class="sec-title">SIKLUS EKONOMI DETECTOR</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">KLASIFIKASI FASE SIKLUS: EKSPANSI · PUNCAK · STAGFLASI · KONTRAKSI · PEMULIHAN</div>', unsafe_allow_html=True)
    cols=st.columns(min(len(selected_names),5))
    for col,name in zip(cols,selected_names[:5]):
        iso=COUNTRIES[name]; dm=all_data.get(iso,{})
        phase,pc,desc=detect_cycle(dm)
        with col:
            st.markdown(f"""
<div class="cyc-card">
<div class="cyc-country">{name.upper()[:14]}</div>
<div class="cyc-phase" style="color:{pc};">{phase}</div>
<div class="cyc-desc">{desc}</div>
</div>""", unsafe_allow_html=True)
    st.markdown("""
<div class="ibox" style="--lc:#4FC3F7;margin-top:.8rem;">
<div class="ibox-t">PANDUAN ROTASI SEKTOR PER FASE SIKLUS</div>
<div class="ibox-b">
<b style="color:#00FFC8;">EKSPANSI</b> — Overweight Teknologi, Diskresi Konsumen, Industri. Underweight Utilities.<br>
<b style="color:#FFD93D;">PUNCAK</b> — Rotasi ke Energi, Material, Consumer Staples. Kurangi durasi obligasi.<br>
<b style="color:#FF6B6B;">KONTRAKSI / STAGFLASI</b> — Utilities, Healthcare, Obligasi Pemerintah, Emas.<br>
<b style="color:#4FC3F7;">PEMULIHAN</b> — Akumulasi Keuangan, Industri, Small-cap. Tingkatkan risk appetite.
</div>
</div>""", unsafe_allow_html=True)

def s_cb(selected_isos):
    st.markdown('<div class="sec-title">CENTRAL BANK POLICY TRACKER</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">STANCE KEBIJAKAN MONETER · SUKU BUNGA · MEETING BERIKUTNYA · CARRY TRADE</div>', unsafe_allow_html=True)
    sc_map={"HAWKISH":"stance-h","DOVISH":"stance-d","NEUTRAL":"stance-n"}
    tr_map={"HIKE":"trend-hike","CUT":"trend-cut","HOLD":"trend-hold"}
    sorted_isos=sorted(set(selected_isos),key=lambda x: CB.get(x,{}).get("rate",0),reverse=True)
    html='<div class="cb-grid">'
    for iso in sorted_isos:
        cb=CB.get(iso)
        if not cb: continue
        sc=sc_map.get(cb["stance"],"stance-n"); tr=tr_map.get(cb["trend"],"trend-hold")
        html+=f'<div class="cb-card"><div class="cb-name">{iso} · {cb["name"]}</div><div class="cb-rate">{cb["rate"]:.2f}%</div><span class="{sc}">{cb["stance"]}</span><span class="{tr}">{cb["trend"]}</span><div class="cb-next">{cb["next"]}</div></div>'
    html+="</div>"
    st.markdown(html, unsafe_allow_html=True)
    st.markdown('<div class="sec-title" style="margin-top:1.2rem;">CARRY TRADE MATRIX</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">LONG HIGH-RATE / SHORT LOW-RATE · SPREAD TERBESAR</div>', unsafe_allow_html=True)
    all_cb=sorted(CB.items(),key=lambda x:x[1]["rate"],reverse=True)
    for ih,cbh in all_cb[:3]:
        for il,cbl in all_cb[-3:]:
            if ih==il: continue
            diff=cbh["rate"]-cbl["rate"]
            st.markdown(f"""
<div class="carry-row">
<div class="carry-pair">LONG {ih} / SHORT {il}</div>
<div class="carry-diff">+{diff:.2f}%</div>
<div class="carry-desc">Long {cbh['name']} ({cbh['rate']:.2f}%) · Short {cbl['name']} ({cbl['rate']:.2f}%)</div>
</div>""", unsafe_allow_html=True)

def s_calendar(all_data):
    st.markdown('<div class="sec-title">KALENDER EKONOMI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">EVENT MAKRO BERDAMPAK TINGGI · PREDIKSI SENTIMENT · SEPTEMBER 2026 · WAKTU INDONESIA BARAT (WIB)</div>', unsafe_allow_html=True)

    # Hitung sentiment semua event
    rows=[]
    bull_n=bear_n=neu_n=0
    for ev in CALENDAR:
        slbl,scls,sreason=cal_sentiment(ev,all_data)
        if slbl=="BULLISH": bull_n+=1
        elif slbl=="BEARISH": bear_n+=1
        else: neu_n+=1
        rows.append((ev,slbl,scls,sreason))

    total_ev=len(rows)
    bp=round(bull_n/total_ev*100); rp=round(bear_n/total_ev*100); np_=100-bp-rp
    st.markdown(f"""
<div class="ibox" style="--lc:#4FC3F7;margin-bottom:.8rem;">
<div class="ibox-t">AGGREGATE MARKET SENTIMENT — SEPTEMBER 2026 ({total_ev} EVENT)</div>
<div style="display:flex;gap:.5rem;align-items:center;margin-bottom:.4rem;flex-wrap:wrap;">
<span class="sent-bull">{bull_n} BULLISH</span>
<span class="sent-bear">{bear_n} BEARISH</span>
<span class="sent-neu">{neu_n} NEUTRAL</span>
</div>
<div style="height:5px;background:#0E1826;border-radius:2px;display:flex;overflow:hidden;">
<div style="height:5px;width:{bp}%;background:#00FFC8;"></div>
<div style="height:5px;width:{np_}%;background:#FFD93D;"></div>
<div style="height:5px;width:{rp}%;background:#FF6B6B;"></div>
</div>
<div style="font-family:'Share Tech Mono',monospace;font-size:.52rem;color:#1A2D3A;margin-top:.3rem;">
BULLISH {bp}% · NEUTRAL {np_}% · BEARISH {rp}%
</div>
</div>""", unsafe_allow_html=True)

    # Filter controls
    fc1,fc2,fc3=st.columns([1,1.5,1.5])
    with fc1: imp_f=st.radio("Filter Dampak",["SEMUA","HIGH","MEDIUM"],key="cal_imp_v4",horizontal=False)
    with fc2: iso_f=st.multiselect("Filter Negara",list(set(e["iso"] for e in CALENDAR)),key="cal_iso_v4")
    with fc3: sent_f=st.radio("Filter Sentiment",["SEMUA","BULLISH","BEARISH","NEUTRAL"],key="cal_sent_v4",horizontal=False)

    imp_cls={"HIGH":"imp-h","MEDIUM":"imp-m","LOW":"imp-l"}
    imp_lbl={"HIGH":"HIGH","MEDIUM":"MED","LOW":"LOW"}

    for ev,slbl,scls,sreason in rows:
        if imp_f!="SEMUA" and ev["impact"]!=imp_f: continue
        if iso_f and ev["iso"] not in iso_f: continue
        if sent_f!="SEMUA" and slbl!=sent_f: continue

        ec=ISO_EVENT_COLORS.get(ev["iso"],"#00FFC8")
        ic=imp_cls.get(ev["impact"],"imp-l")
        il=imp_lbl.get(ev["impact"],"LOW")
        country_name=[k for k,v in COUNTRIES.items() if v==ev["iso"]]
        country_name=country_name[0] if country_name else ev["iso"]

        st.markdown(f"""
<div class="cal-row" style="--ec:{ec};">
<div class="cal-accent"></div>
<div class="cal-header">
<div>
<div class="cal-dt">{ev['date']}</div>
<div class="cal-time">{ev['time']}</div>
</div>
<span class="cal-iso-tag">{ev['iso']}</span>
<div class="cal-title">{ev['event']}</div>
<div class="cal-badges">
<span class="{ic}">{il}</span>
<span class="{scls}">{slbl}</span>
</div>
</div>
<div class="cal-data">
<div class="cal-data-item">
<span class="cal-data-lbl">FORECAST</span>
<span class="cal-data-val" style="color:{ec};">{ev['forecast']} <span style="font-size:.5rem;color:#1A2D3A;">{ev.get('unit','')}</span></span>
</div>
<div class="cal-data-item">
<span class="cal-data-lbl">PREVIOUS</span>
<span class="cal-data-val">{ev['prev']} <span style="font-size:.5rem;color:#1A2D3A;">{ev.get('unit','')}</span></span>
</div>
<div class="cal-data-item" style="flex:1;">
<span class="cal-data-lbl">ANALISIS PREDIKSI</span>
<span class="cal-reason">{sreason}</span>
</div>
</div>
</div>""", unsafe_allow_html=True)

def s_compare(all_data,compare_names,main_name):
    st.markdown('<div class="sec-title">PERBANDINGAN MULTI-NEGARA</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">BENCHMARK POSISI MAKRO ANTAR EKONOMI</div>', unsafe_allow_html=True)
    all_names=[main_name]+compare_names
    all_isos=[COUNTRIES[n] for n in all_names]
    short=[n[:14] for n in all_names]
    ind_sel=st.selectbox("Indikator",list(INDICATORS.keys()),index=1,key="cmp_ind_v4")
    meta=INDICATORS[ind_sel]
    vals=[]
    for iso in all_isos:
        v,_=latest(all_data.get(iso,{}).get(ind_sel,{}).get("series",[]))
        if ind_sel=="GDP": vals.append(v/1e12 if v else 0)
        elif ind_sel=="TRADE": vals.append(v/1e9 if v else 0)
        else: vals.append(v if v else 0)
    fig=bar_chart(short,vals,meta["color"],meta["label"])
    st.plotly_chart(fig,use_container_width=True,config=CHART_CFG)
    rows=[]
    for name,iso in zip(all_names,all_isos):
        dm=all_data.get(iso,{})
        total,grade,_=macro_score(dm)
        row={"Negara":name}
        for key,m2 in INDICATORS.items():
            v,_=latest(dm.get(key,{}).get("series",[]))
            row[m2["label"]]=fmt(v,m2["fmt"])
        row["Macro Score"]=f"{total:.0f} ({grade})"
        rows.append(row)
    df=pd.DataFrame(rows).set_index("Negara")
    st.dataframe(df,use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def sanitize(values, options, limit=5):
    opt_set=set(options)
    out=[]
    for v in (values if isinstance(values,(list,tuple)) else [values]):
        if v in opt_set and v not in out: out.append(v)
    return out[:limit]

def main():
    css()
    st.markdown("""
<div style="padding:.5rem 0 .8rem;">
<div class="aero-build">AEROVULPIS · PROTOTYPE · ECONOMIC RADAR MODULE · BUILD STABLE 30 AUG 2026</div>
<div class="aero-title">ECONOMIC RADAR</div>
<div class="aero-sub">PANTAU KONDISI MAKROEKONOMI GLOBAL · BACA SINYAL PASAR SEBELUM PASAR BERGERAK</div>
</div>
<hr style="border:none;border-top:1px solid #0E1826;margin:.5rem 0 1rem;">""", unsafe_allow_html=True)

    c1,c2,c3=st.columns([1.2,2.2,0.6])
    with c1:
        main_name=st.selectbox("Negara Utama",list(COUNTRIES.keys()),key="main_v4")
    with c2:
        compare_opts=[k for k in COUNTRIES if k!=main_name]
        if "cmp_v4" not in st.session_state:
            st.session_state["cmp_v4"]=sanitize(["Amerika Serikat","China"],compare_opts)
        else:
            st.session_state["cmp_v4"]=sanitize(st.session_state["cmp_v4"],compare_opts)
        cmp_names=st.multiselect("Bandingkan (maks 5)",compare_opts,max_selections=5,key="cmp_v4")
    with c3:
        st.markdown('<div style="height:1.75rem;"></div>',unsafe_allow_html=True)
        if st.button("REFRESH DATA",use_container_width=True):
            st.cache_data.clear(); st.rerun()

    main_iso=COUNTRIES[main_name]
    all_isos=list(dict.fromkeys([main_iso]+[COUNTRIES[n] for n in cmp_names]+list(COUNTRIES.values())))

    with st.spinner("Mengambil data dari World Bank…"):
        all_data={}
        for iso in all_isos:
            all_data[iso]={}
            for key,meta in INDICATORS.items():
                series=fetch(iso,meta["code"])
                v,yr=latest(series)
                all_data[iso][key]={"val":v,"year":yr,"series":series}

    dm=all_data[main_iso]
    tabs=st.tabs(["OVERVIEW","HEAT MAP","BIAS SCANNER","SURPRISE INDEX","SIKLUS EKONOMI","CENTRAL BANKS","KALENDER","PERBANDINGAN"])

    with tabs[0]: s_overview(main_name,dm)
    with tabs[1]: s_heatmap(all_data)
    with tabs[2]: s_bias(all_data)
    with tabs[3]: s_surprise(main_iso)
    with tabs[4]: s_cycle(all_data,[main_name]+cmp_names)
    with tabs[5]:
        cb_isos=list(dict.fromkeys([main_iso]+[COUNTRIES[n] for n in cmp_names]+["US","CN","JP","DE","GB"]))
        s_cb(cb_isos)
    with tabs[6]: s_calendar(all_data)
    with tabs[7]:
        if cmp_names: s_compare(all_data,cmp_names,main_name)
        else: st.markdown('<div class="ibox" style="--lc:#1A2D3A;"><div class="ibox-b">Pilih minimal 1 negara pembanding di atas.</div></div>',unsafe_allow_html=True)

if __name__=="__main__":
    main()