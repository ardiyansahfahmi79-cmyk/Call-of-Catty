import html
from datetime import datetime, timezone, timedelta
from html import escape

import streamlit as st
from deep_translator import GoogleTranslator

from config import KATEGORI
from news_fetcher import ambil_berita_kategori, ambil_semua_kategori
from utils import hapus_duplikat
from news_cache_manager import (
    initialize_news_cache,
    should_update_news,
    get_cached_news,
    update_news_cache,
)

st.set_page_config(
    page_title="Market Intelligence | Aerovulpis",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg:         #060b14;
  --surface:    #0d1523;
  --surface2:   #0a1220;
  --border:     #1a2840;
  --border2:    #243550;
  --text:       #c8d8ea;
  --text-muted: #5a7490;
  --text-dim:   #2e4460;
  --accent:     #00c8f0;
  --accent2:    #0055cc;
  --purple:     #6020cc;
  --bullish:    #00d090;
  --bearish:    #ff3060;
  --neutral:    #3380ff;
  --neon:       #00ffcc;
  --warn:       #f0a800;
}

*, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }
html, body, .stApp { background: var(--bg) !important; color: var(--text); font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton, [data-testid="stToolbar"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

.block-container { padding: 0 0.8rem 3rem !important; max-width: 100% !important; }

/* ── HEADER ── */
.aero-header { text-align:center; padding:1.8rem 1rem 1.2rem; }
.aero-header h1 {
  font-size: clamp(1.8rem,5vw,2.8rem);
  font-weight: 800; letter-spacing: 4px; line-height: 1.1; margin-bottom: 0.4rem;
  background: linear-gradient(120deg,#fff 20%,#00c8f0 55%,#6020cc 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.aero-header .sub  { font-size:.82rem; color:var(--text-muted); letter-spacing:1.5px; margin-bottom:.15rem; }
.aero-header .credit { font-family:'JetBrains Mono',monospace; font-size:.6rem; color:var(--text-dim); }
.aero-divider {
  height:1px;
  background:linear-gradient(90deg,transparent,var(--accent) 40%,var(--purple) 60%,transparent);
  opacity:.3; max-width:420px; margin:.9rem auto 0;
}

/* ── LAYOUT: kiri (feed) | kanan (admin) ── */
.main-layout { display:flex; gap:1rem; align-items:flex-start; }
.col-feed  { flex:1; min-width:0; }
.col-admin { width:320px; flex-shrink:0; position:sticky; top:1rem; }

@media (max-width:900px) {
  .main-layout { flex-direction:column; }
  .col-admin { width:100%; position:static; }
}

/* ── KATEGORI SCROLL ── */
.cat-outer {
  width:100%; overflow-x:auto; overflow-y:hidden;
  -webkit-overflow-scrolling:touch; scrollbar-width:none;
  margin:1rem 0 0.6rem;
}
.cat-outer::-webkit-scrollbar { display:none; }
.cat-inner { display:flex; flex-wrap:nowrap; gap:.35rem; padding:.1rem .05rem .25rem; width:max-content; }
.cat-btn {
  font-family:'JetBrains Mono',monospace;
  font-size:.65rem; font-weight:600; letter-spacing:1.8px; text-transform:uppercase;
  background:var(--surface); color:var(--text-muted);
  border:1px solid var(--border); border-radius:3px;
  padding:.38rem .9rem; white-space:nowrap; cursor:pointer;
  transition:all .18s; -webkit-tap-highlight-color:transparent;
}
.cat-btn:hover { background:rgba(0,200,240,.08); color:var(--accent); border-color:rgba(0,200,240,.4); }
.cat-btn.active { background:rgba(0,200,240,.12); color:var(--accent); border-color:var(--accent); box-shadow:0 0 14px rgba(0,200,240,.15); }

/* ── SECTION LABEL ── */
.section-label {
  display:flex; align-items:center; gap:.7rem;
  font-family:'JetBrains Mono',monospace;
  font-size:.6rem; color:var(--text-dim); letter-spacing:2.5px; text-transform:uppercase;
  margin:.4rem 0 .8rem;
}
.section-label::before { content:''; flex:1; height:1px; background:var(--border); }
.section-label .count { color:var(--accent); font-weight:700; }

/* ── NEWS CARD ── */
.news-card {
  background:var(--surface); border:1px solid var(--border);
  border-left:3px solid var(--neutral); border-radius:6px;
  margin-bottom:.75rem; overflow:hidden;
  transition:transform .2s, border-color .2s, box-shadow .2s;
}
.news-card.bullish { border-left-color:var(--bullish); }
.news-card.bearish { border-left-color:var(--bearish); }
.news-card.neutral { border-left-color:var(--neutral); }
.news-card.tim     { border-left-color:var(--warn); border-top:1px solid rgba(240,168,0,.15); }
.news-card:hover   { transform:translateY(-2px); border-color:rgba(0,200,240,.28); box-shadow:0 4px 20px rgba(0,200,240,.05); }

.card-body { padding:.9rem 1rem .8rem 1.15rem; }
.card-top  { display:flex; align-items:center; justify-content:space-between; margin-bottom:.55rem; gap:.4rem; flex-wrap:wrap; }

.cat-badge {
  font-family:'JetBrains Mono',monospace; font-size:.54rem; font-weight:700;
  letter-spacing:2px; text-transform:uppercase;
  color:var(--accent); background:rgba(0,200,240,.07);
  border:1px solid rgba(0,200,240,.2); border-radius:2px; padding:.08rem .42rem; flex-shrink:0;
}
.tim-badge {
  font-family:'JetBrains Mono',monospace; font-size:.54rem; font-weight:700;
  letter-spacing:2px; color:var(--warn);
  background:rgba(240,168,0,.08); border:1px solid rgba(240,168,0,.25);
  border-radius:2px; padding:.08rem .42rem; flex-shrink:0;
}
.src-chip {
  font-family:'JetBrains Mono',monospace; font-size:.5rem; color:var(--text-dim);
  background:rgba(255,255,255,.03); border:1px solid var(--border);
  border-radius:2px; padding:.06rem .35rem; flex-shrink:0;
}
.sent-badge {
  font-family:'JetBrains Mono',monospace; font-size:.52rem; font-weight:700;
  letter-spacing:1px; text-transform:uppercase; padding:.08rem .38rem; border-radius:2px; flex-shrink:0;
}
.sent-badge.bullish { color:var(--bullish); background:rgba(0,208,144,.09); border:1px solid rgba(0,208,144,.25); }
.sent-badge.bearish { color:var(--bearish); background:rgba(255,48,96,.09);  border:1px solid rgba(255,48,96,.25); }
.sent-badge.neutral { color:var(--neutral); background:rgba(51,128,255,.09); border:1px solid rgba(51,128,255,.25); }

/* Instrumen terdampak */
.instr-row { display:flex; flex-wrap:wrap; gap:.3rem; margin-bottom:.55rem; }
.instr-tag {
  font-family:'JetBrains Mono',monospace; font-size:.52rem; font-weight:600;
  color:var(--purple); background:rgba(96,32,204,.1);
  border:1px solid rgba(96,32,204,.25); border-radius:2px; padding:.06rem .38rem;
}

.news-title { font-size:.9rem; font-weight:700; color:var(--text); line-height:1.45; margin-bottom:.5rem; }
.news-desc  { font-size:.79rem; color:var(--text-muted); line-height:1.62; margin-bottom:.65rem; }
.card-meta  {
  display:flex; align-items:center; gap:.38rem;
  font-family:'JetBrains Mono',monospace; font-size:.56rem; color:var(--text-dim); flex-wrap:wrap;
}
.meta-src { color:var(--text-muted); font-weight:600; }
.meta-dot { width:3px; height:3px; border-radius:50%; background:var(--text-dim); flex-shrink:0; }

/* DETAIL PANEL */
.detail-panel {
  border-top:1px solid rgba(0,200,240,.1); background:rgba(0,8,20,.5);
  padding:.75rem 1rem .75rem 1.15rem;
}
.detail-label { font-family:'JetBrains Mono',monospace; font-size:.52rem; letter-spacing:2.5px; text-transform:uppercase; color:var(--text-dim); margin-bottom:.4rem; }
.detail-text  { font-size:.8rem; color:var(--text-muted); line-height:1.7; }
.detail-foot  { margin-top:.4rem; font-family:'JetBrains Mono',monospace; font-size:.52rem; color:var(--text-dim); }

/* ── TOMBOL DETAIL ── */
div[data-testid="stButton"] > button {
  font-family:'JetBrains Mono',monospace !important;
  font-size:.63rem !important; font-weight:600 !important;
  letter-spacing:1.5px !important; text-transform:uppercase !important;
  background:var(--surface2) !important; color:var(--text-muted) !important;
  border:1px solid var(--border) !important; border-radius:3px !important;
  padding:.35rem .7rem !important; white-space:nowrap !important;
  height:auto !important; width:100% !important; transition:all .18s !important;
}
div[data-testid="stButton"] > button:hover {
  background:rgba(0,200,240,.07) !important; color:var(--accent) !important; border-color:rgba(0,200,240,.4) !important;
}
div[data-testid="stButton"] > button:focus,
div[data-testid="stButton"] > button:active {
  background:rgba(0,200,240,.12) !important; color:var(--accent) !important; border-color:var(--accent) !important;
}

/* ── ADMIN PANEL ── */
.admin-panel {
  background:var(--surface); border:1px solid var(--border2);
  border-radius:8px; overflow:hidden;
}
.admin-header {
  background:linear-gradient(135deg,rgba(0,200,240,.08),rgba(96,32,204,.06));
  border-bottom:1px solid var(--border2);
  padding:.75rem 1rem;
  display:flex; align-items:center; gap:.5rem;
}
.admin-header-dot { width:6px; height:6px; border-radius:50%; background:var(--warn); box-shadow:0 0 8px var(--warn); flex-shrink:0; }
.admin-header-title {
  font-family:'JetBrains Mono',monospace; font-size:.65rem; font-weight:700;
  letter-spacing:2.5px; text-transform:uppercase; color:var(--warn);
}
.admin-body { padding:.85rem 1rem 1rem; }
.admin-field-label {
  font-family:'JetBrains Mono',monospace; font-size:.57rem; font-weight:600;
  letter-spacing:2px; text-transform:uppercase; color:var(--text-dim); margin-bottom:.3rem;
}

/* Override Streamlit form elements */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
  background:var(--surface2) !important; color:var(--text) !important;
  border:1px solid var(--border2) !important; border-radius:4px !important;
  font-family:'Inter',sans-serif !important; font-size:.83rem !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
  border-color:var(--accent) !important; box-shadow:0 0 12px rgba(0,200,240,.1) !important;
}
div[data-testid="stSelectbox"] > div > div {
  background:var(--surface2) !important; border:1px solid var(--border2) !important;
  border-radius:4px !important; color:var(--text) !important;
}
div[data-testid="stMultiSelect"] > div > div {
  background:var(--surface2) !important; border:1px solid var(--border2) !important; border-radius:4px !important;
}
div[data-testid="stDateInput"] input,
div[data-testid="stTimeInput"] input {
  background:var(--surface2) !important; color:var(--text) !important;
  border:1px solid var(--border2) !important; border-radius:4px !important;
}

/* Post button khusus */
.post-btn div[data-testid="stButton"] > button {
  background:linear-gradient(135deg,rgba(0,200,240,.18),rgba(96,32,204,.15)) !important;
  color:var(--accent) !important;
  border-color:rgba(0,200,240,.5) !important;
  box-shadow:0 0 18px rgba(0,200,240,.12) !important;
  font-size:.68rem !important; padding:.5rem 1rem !important;
}
.post-btn div[data-testid="stButton"] > button:hover {
  background:linear-gradient(135deg,rgba(0,200,240,.25),rgba(96,32,204,.2)) !important;
  box-shadow:0 0 24px rgba(0,200,240,.2) !important;
}

/* Admin divider */
.admin-sep {
  height:1px; background:var(--border); margin:.7rem 0;
}

/* TIM NEWS count badge */
.tim-count {
  font-family:'JetBrains Mono',monospace; font-size:.55rem;
  color:var(--warn); background:rgba(240,168,0,.1);
  border:1px solid rgba(240,168,0,.2); border-radius:2px;
  padding:.05rem .35rem; margin-left:.3rem;
}

/* EMPTY */
.empty-wrap { text-align:center; padding:2.5rem 1.5rem; border:1px solid var(--border); border-radius:6px; margin:.8rem 0; }
.empty-wrap h3 { font-family:'JetBrains Mono',monospace; font-size:.68rem; letter-spacing:2.5px; text-transform:uppercase; color:var(--text-muted); margin-bottom:.4rem; }
.empty-wrap p  { font-size:.79rem; color:var(--text-dim); line-height:1.65; }

/* FOOTER */
.aero-footer { margin-top:2rem; padding:1rem; border-top:1px solid var(--border); text-align:center; font-family:'JetBrains Mono',monospace; font-size:.58rem; color:var(--text-dim); line-height:1.9; }
.aero-footer .brand { color:var(--accent); font-weight:700; letter-spacing:2px; }

@media (max-width:900px) {
  .col-feed { order:1; } .col-admin { order:0; }
}
@media (max-width:768px) {
  .news-title { font-size:.85rem; }
  .block-container { padding-left:.4rem !important; padding-right:.4rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="aero-header">
  <h1>MARKET INTELLIGENCE</h1>
  <div class="sub">Analisis Mendalam untuk Trader Modern</div>
  <div class="credit">Dirancang oleh Tim Aerovulpis</div>
  <div class="aero-divider"></div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# SECRETS
# ══════════════════════════════════════════════════════════════════
marketaux_key = st.secrets.get("MARKETAUX_API_KEY", "")
newsapi_key   = st.secrets.get("NEWSAPI_API_KEY", "")
fmp_key       = st.secrets.get("FMP_API_KEY", "")

# ══════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════
initialize_news_cache()
if "kategori_terpilih" not in st.session_state:
    st.session_state.kategori_terpilih = "all"
if "show_detail" not in st.session_state:
    st.session_state.show_detail = {}
if "tim_news" not in st.session_state:
    st.session_state.tim_news = []   # list berita dari admin

# ══════════════════════════════════════════════════════════════════
# DAFTAR INSTRUMEN
# ══════════════════════════════════════════════════════════════════
INSTRUMEN_OPTIONS = [
    "XAUUSD","EURUSD","GBPUSD","USDJPY","AUDUSD","USDCAD","USDCHF",
    "DXY (Dolar Index)","US10Y (Treasury)","US30Y",
    "BTC/USD","ETH/USD","BNB/USD","SOL/USD","XRP/USD",
    "S&P 500","NASDAQ","Dow Jones","IHSG","Nikkei 225","Hang Seng",
    "Minyak Mentah (WTI)","Minyak Brent","Gas Alam",
]

KATEGORI_ADMIN = {
    "stock": "Saham", "crypto": "Aset Digital", "geopolitics": "Geopolitik",
    "forex": "Valuta Asing", "indonesia": "Indonesia",
    "economy_us": "Ekonomi AS", "fed": "Federal Reserve",
}

# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, max_entries=200)
def terjemahkan(teks: str) -> str:
    if not teks: return ""
    try:
        return GoogleTranslator(source='en', target='id').translate(html.unescape(teks))
    except Exception:
        return teks

def muat_data(kategori: str) -> dict:
    initialize_news_cache()
    cache_key = f"data_{kategori}"
    if not should_update_news(cache_key):
        cached = get_cached_news(cache_key)
        if cached: return cached
    if kategori == "all":
        data = ambil_semua_kategori(marketaux_key=marketaux_key, newsapi_key=newsapi_key, fmp_key=fmp_key)
    else:
        data = {kategori: ambil_berita_kategori(kategori=kategori, marketaux_key=marketaux_key, newsapi_key=newsapi_key, fmp_key=fmp_key)}
    update_news_cache(cache_key, data)
    return data

def sentimen(text: str) -> str:
    t = (text or "").lower()
    if any(x in t for x in ["naik","lonjak","kuat","rekor","untung","pulih","tinggi","peningkatan","reli","bullish"]): return "bullish"
    if any(x in t for x in ["turun","jatuh","lemah","merosot","anjlok","tumbang","rendah","lambat","bearish"]): return "bearish"
    return "neutral"

SENT_LBL = {"bullish":"+ BULLISH","bearish":"- BEARISH","neutral":"~ NETRAL"}

def sx(v) -> str: return escape("" if v is None else str(v))

def fmt_dt(s: str) -> str:
    try:
        dt = datetime.fromisoformat(s.replace("Z","+00:00"))
        return dt.strftime("%d %b %Y %H:%M")
    except: return s or ""

# ══════════════════════════════════════════════════════════════════
# KATEGORI NAV — HTML scroll
# ══════════════════════════════════════════════════════════════════
kat_aktif = st.session_state.kategori_terpilih
btns_html = '<div class="cat-outer"><div class="cat-inner">'
for k, v in KATEGORI.items():
    cls = "cat-btn active" if k == kat_aktif else "cat-btn"
    btns_html += f'<button class="{cls}" onclick="window.location.href=\'?kat={k}\'">{escape(v)}</button>'
btns_html += '</div></div>'
st.markdown(btns_html, unsafe_allow_html=True)

qp = st.query_params
if "kat" in qp and qp["kat"] in KATEGORI:
    new_kat = qp["kat"]
    if new_kat != st.session_state.kategori_terpilih:
        st.session_state.kategori_terpilih = new_kat
        st.session_state.show_detail = {}
        st.query_params.clear()
        st.rerun()

# ══════════════════════════════════════════════════════════════════
# LOAD & FILTER DATA API
# ══════════════════════════════════════════════════════════════════
with st.spinner("Memuat berita..."):
    data_kategori = muat_data(st.session_state.kategori_terpilih)

if st.session_state.kategori_terpilih == "all":
    api_items = []
    for k, arr in data_kategori.items():
        for x in arr:
            xx = dict(x); xx["kategori_asli"] = k
            api_items.append(xx)
    api_items = hapus_duplikat(api_items)
else:
    api_items = data_kategori.get(st.session_state.kategori_terpilih, [])

batas = datetime.now(timezone.utc) - timedelta(days=7)
filtered_api = []
for item in api_items:
    try:
        wt = datetime.fromisoformat(item.get("waktu_terbit","").replace("Z","+00:00"))
        if wt >= batas: filtered_api.append(item)
    except: filtered_api.append(item)

# ══════════════════════════════════════════════════════════════════
# FILTER TIM NEWS sesuai kategori aktif
# ══════════════════════════════════════════════════════════════════
tim_filtered = []
for tn in st.session_state.tim_news:
    if kat_aktif == "all" or tn.get("kategori_key") == kat_aktif:
        tim_filtered.append(tn)

# Gabung: TIM NEWS tampil duluan
all_items = tim_filtered + filtered_api

# ══════════════════════════════════════════════════════════════════
# MAIN LAYOUT: FEED (kiri) + ADMIN (kanan)
# ══════════════════════════════════════════════════════════════════
col_feed, col_admin = st.columns([3, 1], gap="medium")

# ══════════════════════════════════════════════════════════════════
# KOLOM KIRI — FEED BERITA
# ══════════════════════════════════════════════════════════════════
with col_feed:
    cat_lbl = KATEGORI.get(kat_aktif, "Semua")
    tim_count = len(tim_filtered)
    tim_badge = f'<span class="tim-count">+{tim_count} TIM</span>' if tim_count else ""

    if not all_items:
        st.markdown(f"""
        <div class="empty-wrap">
          <h3>Tidak Ada Data</h3>
          <p>Belum ada berita untuk kategori <strong>{sx(cat_lbl)}</strong>.<br>
             Tambahkan berita manual atau tunggu update berikutnya.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="section-label">
          <span>FEED BERITA</span>
          <span class="count">{len(all_items)} artikel</span>
          {tim_badge}
        </div>""", unsafe_allow_html=True)

        for i, item in enumerate(all_items):
            is_tim = item.get("sumber") == "T.I.M NEWS"
            kid = f"{kat_aktif}_{i}"

            if is_tim:
                judul_id = item.get("judul","")
                desc_id  = item.get("deskripsi","")
                warna    = item.get("sentimen","neutral")
                tag      = item.get("kategori_label","TIM NEWS")
                wkt      = item.get("waktu_terbit","")
                instrumen= item.get("instrumen",[])
            else:
                judul_id = terjemahkan(item.get("judul",""))
                desc_id  = terjemahkan(item.get("deskripsi",""))
                warna    = sentimen(judul_id + " " + desc_id)
                tag      = item.get("kategori_label") or KATEGORI.get(
                    item.get("kategori_asli", kat_aktif),
                    KATEGORI.get(kat_aktif,"LAINNYA")
                )
                wkt      = fmt_dt(item.get("waktu_terbit",""))
                instrumen= []

            sent_lbl  = SENT_LBL.get(warna,"~ NETRAL")
            src_label = "T.I.M NEWS" if is_tim else sx(item.get("sumber",""))[:14]

            # Badge kategori
            if is_tim:
                badge_html = f'<span class="tim-badge">T.I.M NEWS</span>'
            else:
                badge_html = f'<span class="cat-badge">{sx(tag)}</span>'

            # Instrumen terdampak (hanya TIM NEWS)
            instr_html = ""
            if instrumen:
                tags = "".join([f'<span class="instr-tag">{escape(ins)}</span>' for ins in instrumen])
                instr_html = f'<div class="instr-row">{tags}</div>'

            card_cls = f"news-card {warna}" + (" tim" if is_tim else "")

            st.markdown(f"""
            <div class="{card_cls}">
              <div class="card-body">
                <div class="card-top">
                  {badge_html}
                  <span class="src-chip">{sx(src_label)}</span>
                  <span class="sent-badge {warna}">{sx(sent_lbl)}</span>
                </div>
                {instr_html}
                <div class="news-title">{sx(judul_id)}</div>
                <div class="news-desc">{sx(desc_id)}</div>
                <div class="card-meta">
                  <span class="meta-src">{sx(src_label)}</span>
                  <span class="meta-dot"></span>
                  <span>{sx(wkt)}</span>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            # Tombol DETAIL
            lbl_d = "TUTUP DETAIL" if st.session_state.show_detail.get(kid) else "LIHAT DETAIL"
            if st.button(lbl_d, key=f"d_{kid}", use_container_width=True):
                st.session_state.show_detail[kid] = not st.session_state.show_detail.get(kid, False)
                st.rerun()

            if st.session_state.show_detail.get(kid, False):
                instr_detail = ""
                if instrumen:
                    instr_detail = "<br><strong>Instrumen terdampak:</strong> " + ", ".join(instrumen)
                st.markdown(f"""
                <div class="detail-panel">
                  <div class="detail-label">Detail Berita</div>
                  <div class="detail-text">{sx(desc_id)}{instr_detail}</div>
                  <div class="detail-foot">Sumber: {sx(src_label)} | {sx(wkt)}</div>
                </div>""", unsafe_allow_html=True)

    # Footer dalam kolom feed
    st.markdown("""
    <div class="aero-footer">
      <span class="brand">AEROVULPIS</span> | 2026 Market Intelligence Terminal<br>
      Dikembangkan oleh DynamiHatch | Teknologi Intelijensi Pasar Masa Depan
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# KOLOM KANAN — ADMIN PANEL
# ══════════════════════════════════════════════════════════════════
with col_admin:
    st.markdown("""
    <div class="admin-panel">
      <div class="admin-header">
        <div class="admin-header-dot"></div>
        <div class="admin-header-title">T.I.M NEWS — ADMIN</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="admin-body">', unsafe_allow_html=True)

        st.markdown('<div class="admin-field-label">Judul Berita</div>', unsafe_allow_html=True)
        judul_input = st.text_input(
            label="judul", label_visibility="collapsed",
            placeholder="Masukkan judul berita...",
            key="admin_judul"
        )

        st.markdown('<div class="admin-field-label">Deskripsi / Isi</div>', unsafe_allow_html=True)
        desk_input = st.text_area(
            label="deskripsi", label_visibility="collapsed",
            placeholder="Tulis isi berita di sini...",
            height=110, key="admin_deskripsi"
        )

        st.markdown('<div class="admin-sep"></div>', unsafe_allow_html=True)

        col_d, col_t = st.columns(2)
        with col_d:
            st.markdown('<div class="admin-field-label">Tanggal</div>', unsafe_allow_html=True)
            tgl_input = st.date_input(
                label="tgl", label_visibility="collapsed",
                value=datetime.now(timezone.utc).date(),
                key="admin_tgl"
            )
        with col_t:
            st.markdown('<div class="admin-field-label">Waktu (WIB)</div>', unsafe_allow_html=True)
            jam_input = st.time_input(
                label="jam", label_visibility="collapsed",
                value=datetime.now(timezone.utc).time().replace(second=0, microsecond=0),
                key="admin_jam"
            )

        st.markdown('<div class="admin-sep"></div>', unsafe_allow_html=True)

        st.markdown('<div class="admin-field-label">Kategori</div>', unsafe_allow_html=True)
        kat_input = st.selectbox(
            label="kat", label_visibility="collapsed",
            options=list(KATEGORI_ADMIN.keys()),
            format_func=lambda x: KATEGORI_ADMIN[x],
            key="admin_kat"
        )

        st.markdown('<div class="admin-field-label">Sentimen</div>', unsafe_allow_html=True)
        sent_input = st.selectbox(
            label="sent", label_visibility="collapsed",
            options=["bullish","bearish","neutral"],
            format_func=lambda x: {"bullish":"+ Bullish","bearish":"- Bearish","neutral":"~ Netral"}[x],
            key="admin_sent"
        )

        st.markdown('<div class="admin-field-label">Instrumen Terdampak</div>', unsafe_allow_html=True)
        instr_input = st.multiselect(
            label="instr", label_visibility="collapsed",
            options=INSTRUMEN_OPTIONS,
            placeholder="Pilih instrumen...",
            key="admin_instr"
        )

        st.markdown('<div class="admin-sep"></div>', unsafe_allow_html=True)

        # Tombol POST
        st.markdown('<div class="post-btn">', unsafe_allow_html=True)
        if st.button("PUBLISH BERITA", key="admin_publish", use_container_width=True):
            if judul_input.strip() and desk_input.strip():
                waktu_str = f"{tgl_input.strftime('%d %b %Y')} {jam_input.strftime('%H:%M')} WIB"
                berita_baru = {
                    "judul":         judul_input.strip(),
                    "deskripsi":     desk_input.strip(),
                    "sumber":        "T.I.M NEWS",
                    "waktu_terbit":  waktu_str,
                    "sentimen":      sent_input,
                    "kategori_key":  kat_input,
                    "kategori_label":KATEGORI_ADMIN[kat_input].upper(),
                    "instrumen":     instr_input,
                    "url":           f"tim_{len(st.session_state.tim_news)}",
                    "is_tim":        True,
                }
                # Sisipkan di posisi terdepan
                st.session_state.tim_news.insert(0, berita_baru)
                # Reset form
                for k in ["admin_judul","admin_deskripsi","admin_instr"]:
                    if k in st.session_state: del st.session_state[k]
                st.success("Berita berhasil dipublish!")
                st.rerun()
            else:
                st.error("Judul dan deskripsi wajib diisi.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Daftar TIM NEWS yang sudah ada
        if st.session_state.tim_news:
            st.markdown('<div class="admin-sep"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="admin-field-label">BERITA TERSIMPAN ({len(st.session_state.tim_news)})</div>', unsafe_allow_html=True)
            for idx, tn in enumerate(st.session_state.tim_news):
                judul_preview = tn["judul"][:38] + "..." if len(tn["judul"]) > 38 else tn["judul"]
                col_p, col_x = st.columns([4,1])
                with col_p:
                    st.markdown(f"""
                    <div style="font-family:'Inter',sans-serif;font-size:.75rem;color:var(--text-muted);
                                padding:.3rem 0;border-bottom:1px solid var(--border);">
                      {escape(judul_preview)}
                    </div>""", unsafe_allow_html=True)
                with col_x:
                    if st.button("X", key=f"del_tim_{idx}", use_container_width=True):
                        st.session_state.tim_news.pop(idx)
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)