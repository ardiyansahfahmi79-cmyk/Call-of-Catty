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
  --purple:     #6020cc;
  --bullish:    #00d090;
  --bearish:    #ff3060;
  --neutral:    #3380ff;
  --warn:       #f0a800;
  --neon:       #00ffcc;
}

*, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }
html, body, .stApp { background: var(--bg) !important; color: var(--text); font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton, [data-testid="stToolbar"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 0.7rem 3rem !important; max-width: 100% !important; }

/* ── HEADER ── */
.aero-header { text-align:center; padding:1.6rem 1rem 1.1rem; }
.aero-header h1 {
  font-size:clamp(1.7rem,5vw,2.8rem); font-weight:800; letter-spacing:4px; line-height:1.1; margin-bottom:.4rem;
  background:linear-gradient(120deg,#fff 20%,#00c8f0 55%,#6020cc 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.aero-header .sub   { font-size:.8rem; color:var(--text-muted); letter-spacing:1.5px; margin-bottom:.15rem; }
.aero-header .credit{ font-family:'JetBrains Mono',monospace; font-size:.58rem; color:var(--text-dim); }
.aero-divider { height:1px; background:linear-gradient(90deg,transparent,var(--accent) 40%,var(--purple) 60%,transparent); opacity:.3; max-width:420px; margin:.9rem auto 0; }

/* ── KATEGORI — Streamlit columns override ── */
div[data-testid="stHorizontalBlock"] {
  display:flex !important; flex-direction:row !important;
  flex-wrap:nowrap !important; overflow-x:auto !important;
  gap:.35rem !important; padding-bottom:4px !important;
  scrollbar-width:none !important; -webkit-overflow-scrolling:touch !important;
  justify-content:flex-start !important;
}
div[data-testid="stHorizontalBlock"]::-webkit-scrollbar { display:none !important; }
div[data-testid="column"] { padding:0 !important; flex:0 0 auto !important; min-width:0 !important; width:auto !important; }

/* Semua tombol Streamlit — base style */
div[data-testid="stButton"] > button {
  font-family:'JetBrains Mono',monospace !important;
  font-size:.64rem !important; font-weight:600 !important;
  letter-spacing:1.5px !important; text-transform:uppercase !important;
  background:var(--surface) !important; color:var(--text-muted) !important;
  border:1px solid var(--border) !important; border-radius:3px !important;
  padding:.38rem .8rem !important; white-space:nowrap !important;
  height:auto !important; width:auto !important;
  min-width:0 !important; transition:all .18s !important;
}
div[data-testid="stButton"] > button:hover {
  background:rgba(0,200,240,.08) !important; color:var(--accent) !important;
  border-color:rgba(0,200,240,.45) !important;
}
div[data-testid="stButton"] > button:focus,
div[data-testid="stButton"] > button:active {
  background:rgba(0,200,240,.12) !important; color:var(--accent) !important;
  border-color:var(--accent) !important;
}

/* Tombol detail — full width */
.btn-detail div[data-testid="stButton"] > button { width:100% !important; }

/* Tombol publish — styling khusus */
.btn-publish div[data-testid="stButton"] > button {
  width:100% !important;
  background:linear-gradient(135deg,rgba(0,200,240,.16),rgba(96,32,204,.12)) !important;
  color:var(--accent) !important; border-color:rgba(0,200,240,.5) !important;
  box-shadow:0 0 16px rgba(0,200,240,.1) !important; font-size:.66rem !important;
  padding:.46rem 1rem !important;
}
.btn-publish div[data-testid="stButton"] > button:hover {
  box-shadow:0 0 24px rgba(0,200,240,.2) !important;
}

/* ── SECTION LABEL ── */
.section-label {
  display:flex; align-items:center; gap:.7rem;
  font-family:'JetBrains Mono',monospace; font-size:.6rem;
  color:var(--text-dim); letter-spacing:2.5px; text-transform:uppercase;
  margin:.5rem 0 .8rem;
}
.section-label::before { content:''; flex:1; height:1px; background:var(--border); }
.section-label .count { color:var(--accent); font-weight:700; }
.tim-count { font-family:'JetBrains Mono',monospace; font-size:.54rem; color:var(--warn); background:rgba(240,168,0,.1); border:1px solid rgba(240,168,0,.2); border-radius:2px; padding:.03rem .3rem; margin-left:.2rem; }

/* ── NEWS CARD ── */
.news-card {
  background:var(--surface); border:1px solid var(--border);
  border-left:3px solid var(--neutral); border-radius:6px;
  margin-bottom:.7rem; overflow:hidden;
  transition:transform .2s,border-color .2s,box-shadow .2s;
}
.news-card.bullish { border-left-color:var(--bullish); }
.news-card.bearish { border-left-color:var(--bearish); }
.news-card.neutral { border-left-color:var(--neutral); }
.news-card.tim     { border-left-color:var(--warn); background:linear-gradient(135deg,var(--surface),rgba(240,168,0,.03)); }
.news-card:hover   { transform:translateY(-2px); border-color:rgba(0,200,240,.28); box-shadow:0 4px 18px rgba(0,200,240,.05); }

.card-body { padding:.85rem .95rem .75rem 1.1rem; }
.card-top  { display:flex; align-items:center; justify-content:space-between; margin-bottom:.5rem; gap:.35rem; flex-wrap:wrap; }
.cat-badge { font-family:'JetBrains Mono',monospace; font-size:.53rem; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:var(--accent); background:rgba(0,200,240,.07); border:1px solid rgba(0,200,240,.2); border-radius:2px; padding:.08rem .4rem; flex-shrink:0; }
.tim-badge { font-family:'JetBrains Mono',monospace; font-size:.53rem; font-weight:700; letter-spacing:2px; color:var(--warn); background:rgba(240,168,0,.08); border:1px solid rgba(240,168,0,.25); border-radius:2px; padding:.08rem .4rem; flex-shrink:0; }
.src-chip  { font-family:'JetBrains Mono',monospace; font-size:.5rem; color:var(--text-dim); background:rgba(255,255,255,.03); border:1px solid var(--border); border-radius:2px; padding:.05rem .32rem; flex-shrink:0; }
.sent-badge{ font-family:'JetBrains Mono',monospace; font-size:.52rem; font-weight:700; letter-spacing:1px; text-transform:uppercase; padding:.08rem .38rem; border-radius:2px; flex-shrink:0; }
.sent-badge.bullish { color:var(--bullish); background:rgba(0,208,144,.09); border:1px solid rgba(0,208,144,.25); }
.sent-badge.bearish { color:var(--bearish); background:rgba(255,48,96,.09);  border:1px solid rgba(255,48,96,.25); }
.sent-badge.neutral { color:var(--neutral); background:rgba(51,128,255,.09); border:1px solid rgba(51,128,255,.25); }

.instr-row { display:flex; flex-wrap:wrap; gap:.28rem; margin-bottom:.5rem; }
.instr-tag { font-family:'JetBrains Mono',monospace; font-size:.5rem; font-weight:600; color:var(--purple); background:rgba(96,32,204,.1); border:1px solid rgba(96,32,204,.25); border-radius:2px; padding:.05rem .35rem; }

.news-title { font-size:.88rem; font-weight:700; color:var(--text); line-height:1.45; margin-bottom:.45rem; }
.news-desc  { font-size:.78rem; color:var(--text-muted); line-height:1.62; margin-bottom:.6rem; }
.card-meta  { display:flex; align-items:center; gap:.35rem; font-family:'JetBrains Mono',monospace; font-size:.56rem; color:var(--text-dim); flex-wrap:wrap; }
.meta-src   { color:var(--text-muted); font-weight:600; }
.meta-dot   { width:3px; height:3px; border-radius:50%; background:var(--text-dim); flex-shrink:0; }

/* ── DETAIL PANEL ── */
.detail-panel { border-top:1px solid rgba(0,200,240,.1); background:rgba(0,8,20,.5); padding:.7rem .95rem .7rem 1.1rem; }
.detail-label { font-family:'JetBrains Mono',monospace; font-size:.52rem; letter-spacing:2.5px; text-transform:uppercase; color:var(--text-dim); margin-bottom:.38rem; }
.detail-text  { font-size:.79rem; color:var(--text-muted); line-height:1.7; }
.detail-foot  { margin-top:.38rem; font-family:'JetBrains Mono',monospace; font-size:.51rem; color:var(--text-dim); }

/* ── ADMIN PANEL ── */
.admin-box { background:var(--surface); border:1px solid var(--border2); border-radius:8px; overflow:hidden; }
.admin-head { background:linear-gradient(135deg,rgba(240,168,0,.08),rgba(96,32,204,.05)); border-bottom:1px solid var(--border2); padding:.65rem .9rem; display:flex; align-items:center; gap:.45rem; }
.admin-head-dot { width:6px; height:6px; border-radius:50%; background:var(--warn); box-shadow:0 0 8px var(--warn); flex-shrink:0; }
.admin-head-title { font-family:'JetBrains Mono',monospace; font-size:.62rem; font-weight:700; letter-spacing:2.5px; text-transform:uppercase; color:var(--warn); }
.admin-body { padding:.75rem .9rem .9rem; }
.field-lbl  { font-family:'JetBrains Mono',monospace; font-size:.54rem; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:var(--text-dim); margin-bottom:.25rem; margin-top:.55rem; }
.field-lbl:first-child { margin-top:0; }
.admin-sep  { height:1px; background:var(--border); margin:.6rem 0; }

.saved-item { font-size:.74rem; color:var(--text-muted); padding:.28rem 0; border-bottom:1px solid var(--border); font-family:'Inter',sans-serif; }

/* Streamlit widget override untuk admin */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
  background:var(--surface2) !important; color:var(--text) !important;
  border:1px solid var(--border2) !important; border-radius:4px !important;
  font-family:'Inter',sans-serif !important; font-size:.82rem !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus { border-color:rgba(0,200,240,.5) !important; }
div[data-baseweb="select"] > div { background:var(--surface2) !important; border-color:var(--border2) !important; border-radius:4px !important; color:var(--text) !important; }
div[data-baseweb="tag"] { background:rgba(96,32,204,.2) !important; }

/* ── EMPTY ── */
.empty-wrap { text-align:center; padding:2.5rem 1.5rem; border:1px solid var(--border); border-radius:6px; margin:.8rem 0; }
.empty-wrap h3 { font-family:'JetBrains Mono',monospace; font-size:.66rem; letter-spacing:2.5px; text-transform:uppercase; color:var(--text-muted); margin-bottom:.4rem; }
.empty-wrap p  { font-size:.78rem; color:var(--text-dim); line-height:1.65; }

/* ── FOOTER ── */
.aero-footer { margin-top:2rem; padding:1rem; border-top:1px solid var(--border); text-align:center; font-family:'JetBrains Mono',monospace; font-size:.57rem; color:var(--text-dim); line-height:1.9; }
.aero-footer .brand { color:var(--accent); font-weight:700; letter-spacing:2px; }

@media (max-width:900px) {
  .news-title { font-size:.84rem; }
  .block-container { padding-left:.35rem !important; padding-right:.35rem !important; }
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
marketaux_key = st.secrets.get("MARKETAUX_API_KEY","")
newsapi_key   = st.secrets.get("NEWSAPI_API_KEY","")
fmp_key       = st.secrets.get("FMP_API_KEY","")

# ══════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════
initialize_news_cache()
for key, default in [
    ("kategori_terpilih","all"),
    ("show_detail",{}),
    ("tim_news",[]),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════════════════════════════
# DATA INSTRUMEN & KATEGORI ADMIN
# ══════════════════════════════════════════════════════════════════
INSTRUMEN_OPTIONS = [
    "XAUUSD","XAGUSD","EURUSD","GBPUSD","USDJPY","AUDUSD","USDCAD","USDCHF","NZDUSD",
    "DXY (Dolar Index)","US10Y (Treasury)","US30Y",
    "BTC/USD","ETH/USD","BNB/USD","SOL/USD","XRP/USD",
    "S&P 500","NASDAQ","Dow Jones","IHSG","Nikkei 225","Hang Seng",
    "Minyak WTI","Minyak Brent","Gas Alam",
]
KATEGORI_ADMIN = {
    "stock":"Saham","crypto":"Aset Digital","geopolitics":"Geopolitik",
    "forex":"Valuta Asing","indonesia":"Indonesia","economy_us":"Ekonomi AS","fed":"Federal Reserve",
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

def sentimen_teks(text: str) -> str:
    t = (text or "").lower()
    if any(x in t for x in ["naik","lonjak","kuat","rekor","untung","pulih","tinggi","peningkatan","reli","bullish"]): return "bullish"
    if any(x in t for x in ["turun","jatuh","lemah","merosot","anjlok","tumbang","rendah","lambat","bearish"]): return "bearish"
    return "neutral"

SENT_LBL = {"bullish":"+ BULLISH","bearish":"- BEARISH","neutral":"~ NETRAL"}

def clean(v: str) -> str:
    """Bersihkan teks untuk HTML — tidak double-escape."""
    return escape(str(v)) if v else ""

def fmt_dt(s: str) -> str:
    try:
        dt = datetime.fromisoformat(s.replace("Z","+00:00"))
        return dt.strftime("%d %b %Y %H:%M")
    except: return s or ""

# ══════════════════════════════════════════════════════════════════
# KATEGORI — pakai st.columns + st.button (bukan onclick HTML)
# Ini satu-satunya cara yang reliabel di Streamlit mobile
# ══════════════════════════════════════════════════════════════════
kat_aktif = st.session_state.kategori_terpilih
kat_list  = list(KATEGORI.items())
cat_cols  = st.columns(len(kat_list))
for i, (k, v) in enumerate(kat_list):
    with cat_cols[i]:
        # Tandai kategori aktif dengan styling khusus via markdown
        if k == kat_aktif:
            st.markdown(f'<div style="text-align:center;font-family:\'JetBrains Mono\',monospace;font-size:.62rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#00c8f0;background:rgba(0,200,240,.12);border:1px solid #00c8f0;border-radius:3px;padding:.38rem .5rem;margin-bottom:.3rem;box-shadow:0 0 14px rgba(0,200,240,.15);">{escape(v)}</div>', unsafe_allow_html=True)
        if st.button(v, key=f"cat_{k}", use_container_width=True):
            st.session_state.kategori_terpilih = k
            st.session_state.show_detail = {}
            st.rerun()

# ══════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════
with st.spinner("Memuat berita..."):
    data_kategori = muat_data(st.session_state.kategori_terpilih)

kat_aktif = st.session_state.kategori_terpilih  # refresh setelah rerun

if kat_aktif == "all":
    api_items = []
    for k, arr in data_kategori.items():
        for x in arr:
            xx = dict(x); xx["kategori_asli"] = k
            api_items.append(xx)
    api_items = hapus_duplikat(api_items)
else:
    api_items = data_kategori.get(kat_aktif, [])

# Filter 7 hari
batas = datetime.now(timezone.utc) - timedelta(days=7)
filtered_api = []
for item in api_items:
    try:
        wt = datetime.fromisoformat(item.get("waktu_terbit","").replace("Z","+00:00"))
        if wt >= batas: filtered_api.append(item)
    except: filtered_api.append(item)

# TIM NEWS filter kategori
tim_filtered = [
    tn for tn in st.session_state.tim_news
    if kat_aktif == "all" or tn.get("kategori_key") == kat_aktif
]

all_items = tim_filtered + filtered_api

# ══════════════════════════════════════════════════════════════════
# LAYOUT: FEED kiri | ADMIN kanan
# ══════════════════════════════════════════════════════════════════
col_feed, col_admin = st.columns([3, 1], gap="medium")

# ── KOLOM FEED ──
with col_feed:
    cat_lbl   = KATEGORI.get(kat_aktif, "Semua")
    tim_count = len(tim_filtered)
    tim_badge = f'<span class="tim-count">+{tim_count} TIM</span>' if tim_count else ""

    if not all_items:
        st.markdown(f"""
        <div class="empty-wrap">
          <h3>Tidak Ada Data</h3>
          <p>Belum ada berita untuk kategori <strong>{clean(cat_lbl)}</strong>.<br>
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
            is_tim   = item.get("sumber") == "T.I.M NEWS"
            kid      = f"{kat_aktif}_{i}"

            if is_tim:
                judul_id = item.get("judul","")
                desc_id  = item.get("deskripsi","")
                warna    = item.get("sentimen","neutral")
                tag      = item.get("kategori_label","T.I.M NEWS")
                wkt      = item.get("waktu_terbit","")
                instrumen= item.get("instrumen",[])
            else:
                # BUG FIX: terjemahkan() sudah return plain string, jangan di-escape lagi
                judul_id = terjemahkan(item.get("judul",""))
                desc_id  = terjemahkan(item.get("deskripsi",""))
                warna    = sentimen_teks(judul_id + " " + desc_id)
                tag      = item.get("kategori_label") or KATEGORI.get(
                    item.get("kategori_asli", kat_aktif),
                    KATEGORI.get(kat_aktif,"LAINNYA")
                )
                wkt      = fmt_dt(item.get("waktu_terbit",""))
                instrumen= []

            sent_lbl  = SENT_LBL.get(warna,"~ NETRAL")
            src_label = "T.I.M NEWS" if is_tim else (item.get("sumber","")[:14] or "--")

            badge_html = f'<span class="tim-badge">T.I.M NEWS</span>' if is_tim else f'<span class="cat-badge">{clean(tag)}</span>'

            instr_html = ""
            if instrumen:
                instr_html = '<div class="instr-row">' + "".join(
                    f'<span class="instr-tag">{escape(ins)}</span>' for ins in instrumen
                ) + '</div>'

            card_cls = f"news-card {warna}" + (" tim" if is_tim else "")

            # RENDER KARTU — judul dan desc sudah plain text, escape manual
            st.markdown(f"""
            <div class="{card_cls}">
              <div class="card-body">
                <div class="card-top">
                  {badge_html}
                  <span class="src-chip">{clean(src_label)}</span>
                  <span class="sent-badge {warna}">{clean(sent_lbl)}</span>
                </div>
                {instr_html}
                <div class="news-title">{clean(judul_id)}</div>
                <div class="news-desc">{clean(desc_id)}</div>
                <div class="card-meta">
                  <span class="meta-src">{clean(src_label)}</span>
                  <span class="meta-dot"></span>
                  <span>{clean(wkt)}</span>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            # Tombol Detail
            lbl_d = "TUTUP DETAIL" if st.session_state.show_detail.get(kid) else "LIHAT DETAIL"
            st.markdown('<div class="btn-detail">', unsafe_allow_html=True)
            if st.button(lbl_d, key=f"d_{kid}", use_container_width=True):
                st.session_state.show_detail[kid] = not st.session_state.show_detail.get(kid, False)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            if st.session_state.show_detail.get(kid, False):
                instr_str = ", ".join(instrumen) if instrumen else ""
                instr_line = f"<br><strong>Instrumen:</strong> {escape(instr_str)}" if instr_str else ""
                st.markdown(f"""
                <div class="detail-panel">
                  <div class="detail-label">Detail Berita</div>
                  <div class="detail-text">{clean(desc_id)}{instr_line}</div>
                  <div class="detail-foot">Sumber: {clean(src_label)} &nbsp;|&nbsp; {clean(wkt)}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="aero-footer">
      <span class="brand">AEROVULPIS</span> | 2026 Market Intelligence Terminal<br>
      Dikembangkan oleh DynamiHatch | Teknologi Intelijensi Pasar Masa Depan
    </div>""", unsafe_allow_html=True)

# ── KOLOM ADMIN ──
with col_admin:
    st.markdown("""
    <div class="admin-box">
      <div class="admin-head">
        <div class="admin-head-dot"></div>
        <div class="admin-head-title">T.I.M NEWS</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="admin-body">', unsafe_allow_html=True)

    st.markdown('<div class="field-lbl">Judul Berita</div>', unsafe_allow_html=True)
    judul_input = st.text_input("judul", label_visibility="collapsed",
        placeholder="Masukkan judul berita...", key="admin_judul")

    st.markdown('<div class="field-lbl">Deskripsi / Isi</div>', unsafe_allow_html=True)
    desk_input = st.text_area("deskripsi", label_visibility="collapsed",
        placeholder="Tulis isi berita di sini...", height=100, key="admin_desk")

    st.markdown('<div class="admin-sep"></div>', unsafe_allow_html=True)

    # TANGGAL — text input string, aman tanpa React error
    st.markdown('<div class="field-lbl">Tanggal</div>', unsafe_allow_html=True)
    tgl_input = st.date_input("tgl", label_visibility="collapsed",
        value=datetime.now(timezone.utc).date(), key="admin_tgl")

    # JAM & MENIT — selectbox, hindari st.time_input (React error #185)
    st.markdown('<div class="field-lbl">Waktu (WIB)</div>', unsafe_allow_html=True)
    now_wib = datetime.now(timezone(timedelta(hours=7)))
    col_h, col_m = st.columns(2)
    with col_h:
        jam_sel = st.selectbox("jam", label_visibility="collapsed",
            options=[f"{h:02d}" for h in range(24)],
            index=now_wib.hour, key="admin_jam")
    with col_m:
        menit_sel = st.selectbox("menit", label_visibility="collapsed",
            options=[f"{m:02d}" for m in range(0,60,5)],
            index=now_wib.minute // 5, key="admin_mnt")

    st.markdown('<div class="admin-sep"></div>', unsafe_allow_html=True)

    st.markdown('<div class="field-lbl">Kategori</div>', unsafe_allow_html=True)
    kat_sel = st.selectbox("kat", label_visibility="collapsed",
        options=list(KATEGORI_ADMIN.keys()),
        format_func=lambda x: KATEGORI_ADMIN[x], key="admin_kat")

    st.markdown('<div class="field-lbl">Sentimen</div>', unsafe_allow_html=True)
    sent_sel = st.selectbox("sent", label_visibility="collapsed",
        options=["bullish","bearish","neutral"],
        format_func=lambda x: {"bullish":"+ Bullish","bearish":"- Bearish","neutral":"~ Netral"}[x],
        key="admin_sent")

    st.markdown('<div class="field-lbl">Instrumen Terdampak</div>', unsafe_allow_html=True)
    instr_sel = st.multiselect("instr", label_visibility="collapsed",
        options=INSTRUMEN_OPTIONS, placeholder="Pilih instrumen...", key="admin_instr")

    st.markdown('<div class="admin-sep"></div>', unsafe_allow_html=True)

    st.markdown('<div class="btn-publish">', unsafe_allow_html=True)
    if st.button("PUBLISH BERITA", key="admin_pub", use_container_width=True):
        if judul_input.strip() and desk_input.strip():
            wkt_str = f"{tgl_input.strftime('%d %b %Y')} {jam_sel}:{menit_sel} WIB"
            berita = {
                "judul":         judul_input.strip(),
                "deskripsi":     desk_input.strip(),
                "sumber":        "T.I.M NEWS",
                "waktu_terbit":  wkt_str,
                "sentimen":      sent_sel,
                "kategori_key":  kat_sel,
                "kategori_label":KATEGORI_ADMIN[kat_sel].upper(),
                "instrumen":     instr_sel,
                "url":           f"tim_{len(st.session_state.tim_news)}",
            }
            st.session_state.tim_news.insert(0, berita)
            # Reset input
            for k in ["admin_judul","admin_desk","admin_instr"]:
                if k in st.session_state: del st.session_state[k]
            st.success("Berita berhasil dipublish!")
            st.rerun()
        else:
            st.error("Judul dan deskripsi wajib diisi.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Daftar T.I.M NEWS tersimpan
    if st.session_state.tim_news:
        st.markdown('<div class="admin-sep"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-lbl">Tersimpan ({len(st.session_state.tim_news)})</div>', unsafe_allow_html=True)
        for idx, tn in enumerate(st.session_state.tim_news):
            preview = tn["judul"][:35] + "..." if len(tn["judul"]) > 35 else tn["judul"]
            c1, c2 = st.columns([5,1])
            with c1:
                st.markdown(f'<div class="saved-item">{escape(preview)}</div>', unsafe_allow_html=True)
            with c2:
                if st.button("X", key=f"del_{idx}", use_container_width=True):
                    st.session_state.tim_news.pop(idx)
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)