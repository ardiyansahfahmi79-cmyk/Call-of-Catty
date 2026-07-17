import time
import html
from datetime import datetime, timezone, timedelta
from html import escape

import streamlit as st
from deep_translator import GoogleTranslator

from config import KATEGORI
from news_fetcher import ambil_berita_kategori, ambil_semua_kategori
from ai_analyzer import analisis_ai
from utils import hapus_duplikat

st.set_page_config(page_title="Market Intelligence | Aerovulpis", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg:           #060b14;
  --surface:      #0d1523;
  --surface2:     #111c2e;
  --border:       #1e2d45;
  --border-glow:  #00d4ff;
  --text:         #cdd9e8;
  --text-muted:   #5f7a96;
  --text-dim:     #3d5470;
  --accent:       #00d4ff;
  --accent2:      #0070ff;
  --accent3:      #7b2fff;
  --neon:         #00ffcc;
  --bullish:      #00e5a0;
  --bearish:      #ff3d6b;
  --neutral:      #4d9fff;
  --warn:         #ffb020;
  --grid-line:    rgba(0,212,255,0.04);
}

* { margin:0; padding:0; box-sizing:border-box; }

body, .stApp {
  background: var(--bg);
  color: var(--text);
  font-family: 'Inter', sans-serif;
}

/* HIDE streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* GRID BACKGROUND */
.stApp::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(var(--grid-line) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
}

.block-container {
  padding-top: 1.5rem !important;
  padding-bottom: 3rem !important;
  max-width: 1280px !important;
  position: relative;
  z-index: 1;
}

/* ═══════════════════════════════════════
   HEADER
═══════════════════════════════════════ */
.cyber-header {
  text-align: center;
  padding: 2.5rem 1rem 2rem;
  position: relative;
}

.cyber-header .sys-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: var(--accent);
  letter-spacing: 4px;
  text-transform: uppercase;
  margin-bottom: 0.8rem;
  opacity: 0.8;
}

.cyber-header h1 {
  font-size: clamp(1.8rem, 5vw, 3rem);
  font-weight: 800;
  letter-spacing: 3px;
  background: linear-gradient(135deg, #fff 30%, var(--accent) 70%, var(--accent3) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.1;
  margin-bottom: 0.6rem;
}

.cyber-header .tagline {
  font-size: 0.92rem;
  color: var(--text-muted);
  letter-spacing: 1.5px;
  margin-bottom: 0.3rem;
}

.cyber-header .by-line {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: var(--text-dim);
}

.header-line {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), var(--accent3), transparent);
  margin: 1.5rem auto 0;
  max-width: 600px;
  opacity: 0.5;
}

/* STATUS BAR */
.status-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  padding: 0.5rem 1.5rem;
  background: rgba(0,212,255,0.03);
  border: 1px solid var(--border);
  border-radius: 4px;
  margin: 1rem auto;
  max-width: 700px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: var(--text-dim);
  flex-wrap: wrap;
}

.status-bar .dot-live {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--neon);
  box-shadow: 0 0 8px var(--neon);
  animation: pulse 2s infinite;
  flex-shrink: 0;
}

@keyframes pulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 6px var(--neon); }
  50% { opacity: 0.5; box-shadow: 0 0 16px var(--neon); }
}

.status-bar span { color: var(--accent); }

/* ═══════════════════════════════════════
   CATEGORY BUTTONS
═══════════════════════════════════════ */
.cat-wrap {
  margin: 1.5rem 0;
}

/* Override Streamlit column layout for category buttons */
div[data-testid="stHorizontalBlock"] {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: wrap !important;
  justify-content: center !important;
  gap: 0.5rem !important;
  align-items: center !important;
}

div[data-testid="column"] {
  padding: 0 !important;
  min-width: unset !important;
  width: auto !important;
  flex: 0 0 auto !important;
}

div[data-testid="stButton"] > button {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.75rem !important;
  font-weight: 500 !important;
  letter-spacing: 1.5px !important;
  text-transform: uppercase !important;
  background: var(--surface) !important;
  color: var(--text-muted) !important;
  border: 1px solid var(--border) !important;
  border-radius: 3px !important;
  padding: 0.45rem 1.1rem !important;
  width: auto !important;
  min-width: 0 !important;
  height: auto !important;
  transition: all 0.2s !important;
  white-space: nowrap !important;
}

div[data-testid="stButton"] > button:hover {
  background: rgba(0,212,255,0.08) !important;
  color: var(--accent) !important;
  border-color: var(--accent) !important;
  box-shadow: 0 0 12px rgba(0,212,255,0.15) !important;
  transform: translateY(-1px) !important;
}

/* ACTIVE CATEGORY — target focused/active button */
div[data-testid="stButton"] > button:focus,
div[data-testid="stButton"] > button[kind="primary"] {
  background: rgba(0,212,255,0.12) !important;
  color: var(--accent) !important;
  border-color: var(--accent) !important;
  box-shadow: 0 0 20px rgba(0,212,255,0.2) !important;
}

/* ═══════════════════════════════════════
   SECTION LABEL
═══════════════════════════════════════ */
.section-label {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: var(--text-dim);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin: 1rem 0 1.2rem;
}

.section-label::before {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

.section-label .count {
  color: var(--accent);
}

/* ═══════════════════════════════════════
   NEWS CARD
═══════════════════════════════════════ */
.news-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
  position: relative;
  transition: all 0.25s ease;
  margin-bottom: 1rem;
}

.news-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 3px; height: 100%;
  background: var(--neutral);
}

.news-card.bullish::before { background: var(--bullish); }
.news-card.bearish::before { background: var(--bearish); }
.news-card.neutral::before { background: var(--neutral); }

.news-card:hover {
  border-color: rgba(0,212,255,0.4);
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0,212,255,0.06);
}

.card-inner {
  padding: 1.2rem 1.3rem 1rem 1.5rem;
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.cat-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--accent);
  background: rgba(0,212,255,0.08);
  border: 1px solid rgba(0,212,255,0.2);
  border-radius: 2px;
  padding: 0.15rem 0.55rem;
}

.sentiment-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 2px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.sentiment-badge.bullish {
  color: var(--bullish);
  background: rgba(0,229,160,0.1);
  border: 1px solid rgba(0,229,160,0.25);
}

.sentiment-badge.bearish {
  color: var(--bearish);
  background: rgba(255,61,107,0.1);
  border: 1px solid rgba(255,61,107,0.25);
}

.sentiment-badge.neutral {
  color: var(--neutral);
  background: rgba(77,159,255,0.1);
  border: 1px solid rgba(77,159,255,0.25);
}

.news-title {
  font-size: 1.0rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.45;
  margin-bottom: 0.75rem;
}

.news-excerpt {
  font-size: 0.85rem;
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: var(--text-dim);
  flex-wrap: wrap;
}

.meta-source { color: var(--text-muted); font-weight: 500; }
.meta-dot { width: 3px; height: 3px; border-radius: 50%; background: var(--text-dim); }

/* ═══════════════════════════════════════
   ACTION BUTTONS (Detail & AI)
═══════════════════════════════════════ */
.action-row {
  display: flex;
  gap: 0.5rem;
  padding: 0 1.3rem 1rem 1.5rem;
}

/* Override untuk action buttons spesifik */
div[data-testid="stButton"][class*="action"] > button,
.action-btn-wrap div[data-testid="stButton"] > button {
  font-size: 0.72rem !important;
  padding: 0.35rem 0.9rem !important;
}

/* ═══════════════════════════════════════
   DETAIL PANEL
═══════════════════════════════════════ */
.detail-panel {
  background: rgba(0,5,15,0.8);
  border-top: 1px solid rgba(0,212,255,0.2);
  padding: 1.1rem 1.3rem 1.1rem 1.5rem;
  position: relative;
}

.detail-panel::before {
  content: 'DETAIL BERITA';
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  color: var(--text-dim);
  letter-spacing: 2px;
  display: block;
  margin-bottom: 0.6rem;
}

.detail-panel p {
  font-size: 0.88rem;
  color: var(--text-muted);
  line-height: 1.7;
}

/* ═══════════════════════════════════════
   AI PANEL
═══════════════════════════════════════ */
.ai-panel {
  background: linear-gradient(135deg, rgba(0,212,255,0.03) 0%, rgba(123,47,255,0.03) 100%);
  border-top: 1px solid rgba(0,212,255,0.15);
  padding: 1.1rem 1.3rem 1.2rem 1.5rem;
}

.ai-panel-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.9rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem;
  color: var(--accent);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.ai-panel-header .ai-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 8px var(--accent);
  animation: pulse 2s infinite;
}

.ai-content {
  font-size: 0.86rem;
  color: var(--text);
  line-height: 1.75;
  white-space: pre-wrap;
}

/* ═══════════════════════════════════════
   AI LOADING ANIMATION
═══════════════════════════════════════ */
.ai-loading {
  padding: 1.1rem 1.3rem 1.2rem 1.5rem;
  background: linear-gradient(135deg, rgba(0,212,255,0.02) 0%, rgba(123,47,255,0.02) 100%);
  border-top: 1px solid rgba(0,212,255,0.15);
}

.ai-loading-header {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: var(--accent);
  letter-spacing: 2px;
  margin-bottom: 0.8rem;
}

.ai-progress-bar {
  height: 2px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.8rem;
}

.ai-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent2), var(--accent), var(--neon));
  border-radius: 2px;
  animation: progress-anim 2s ease-in-out infinite;
}

@keyframes progress-anim {
  0% { width: 0%; margin-left: 0%; }
  50% { width: 60%; margin-left: 20%; }
  100% { width: 0%; margin-left: 100%; }
}

.ai-step {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: var(--text-dim);
}

.ai-step.active { color: var(--accent); }

/* ═══════════════════════════════════════
   EMPTY STATE
═══════════════════════════════════════ */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  margin: 2rem auto;
  max-width: 600px;
}

.empty-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
  opacity: 0.3;
}

.empty-state h3 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  color: var(--text-muted);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.empty-state p {
  font-size: 0.85rem;
  color: var(--text-dim);
}

/* ═══════════════════════════════════════
   FOOTER
═══════════════════════════════════════ */
.cyber-footer {
  margin-top: 3rem;
  padding: 1.5rem;
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: var(--text-dim);
}

.cyber-footer .brand { color: var(--accent); }
.cyber-footer .dev { color: var(--text-dim); }

/* ═══════════════════════════════════════
   RESPONSIVE
═══════════════════════════════════════ */
@media (max-width: 768px) {
  .block-container { padding-left: 0.8rem !important; padding-right: 0.8rem !important; }
  .news-title { font-size: 0.95rem; }
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════
now_utc = datetime.now(timezone.utc)
ts_str = now_utc.strftime("%Y-%m-%d %H:%M UTC")

st.markdown(f"""
<div class="cyber-header">
  <div class="sys-label">// SYS: AEROVULPIS MARKET INTEL v2.0</div>
  <h1>MARKET INTELLIGENCE</h1>
  <div class="tagline">Analisis Mendalam untuk Trader Modern</div>
  <div class="by-line">Dirancang oleh Tim Aerovulpis • Powered by DynamiHatch</div>
  <div class="header-line"></div>
</div>
<div class="status-bar">
  <div class="dot-live"></div>
  <span>LIVE</span>
  <span>|</span>
  <span>{ts_str}</span>
  <span>|</span>
  AEROVULPIS INTELLIGENCE ENGINE
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════
marketaux_key = st.secrets["MARKETAUX_API_KEY"]
openrouter_key = st.secrets["OPENROUTER_API_KEY"]

if "kategori_terpilih" not in st.session_state:
    st.session_state.kategori_terpilih = "all"
if "show_detail" not in st.session_state:
    st.session_state.show_detail = {}
if "ai_result" not in st.session_state:
    st.session_state.ai_result = {}
if "ai_loading" not in st.session_state:
    st.session_state.ai_loading = {}

# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, max_entries=200)
def terjemahkan_teks(teks):
    if not teks: return ""
    try:
        teks_bersih = html.unescape(teks)
        return GoogleTranslator(source='en', target='id').translate(teks_bersih)
    except:
        return teks

@st.cache_data(ttl=1800)
def muat_data_kategori(kategori):
    if kategori == "all":
        return ambil_semua_kategori(marketaux_key)
    return {kategori: ambil_berita_kategori(kategori, marketaux_key)}

def sentiment_from_text(text):
    t = (text or "").lower()
    if any(x in t for x in ["naik","lonjak","kuat","rekor","untung","pulih","tinggi","peningkatan","lompat","reli","pertumbuhan","bullish"]):
        return "bullish"
    if any(x in t for x in ["turun","jatuh","lemah","merosot","anjlok","tumbang","rendah","kurang","lambat","bearish"]):
        return "bearish"
    return "neutral"

def sentiment_label(s):
    return {"bullish": "▲ BULLISH", "bearish": "▼ BEARISH", "neutral": "● NETRAL"}.get(s, "● NETRAL")

def safe_text(v):
    return escape("" if v is None else str(v))

def fmt_waktu(s):
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y %H:%M")
    except:
        return s or ""

# ═══════════════════════════════════════════════════════════════════
# CATEGORY BUTTONS
# ═══════════════════════════════════════════════════════════════════
st.markdown('<div class="cat-wrap">', unsafe_allow_html=True)
cols_btn = st.columns(len(KATEGORI))
for i, (k, v) in enumerate(KATEGORI.items()):
    with cols_btn[i]:
        if st.button(v, key=f"btn_cat_{k}", use_container_width=False):
            st.session_state.kategori_terpilih = k
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════════════════════════
data_kategori = muat_data_kategori(st.session_state.kategori_terpilih)

if st.session_state.kategori_terpilih == "all":
    items = []
    for k, arr in data_kategori.items():
        for x in arr:
            xx = dict(x)
            xx["kategori_asli"] = k
            items.append(xx)
    items = hapus_duplikat(items)
else:
    items = data_kategori.get(st.session_state.kategori_terpilih, [])

# Filter 4 hari terakhir
items_terbaru = []
batas_waktu = datetime.now(timezone.utc) - timedelta(days=4)
for item in items:
    try:
        wt = datetime.fromisoformat(item.get("waktu_terbit","").replace("Z","+00:00"))
        if wt >= batas_waktu:
            items_terbaru.append(item)
    except:
        items_terbaru.append(item)
items = items_terbaru

# ═══════════════════════════════════════════════════════════════════
# RENDER NEWS
# ═══════════════════════════════════════════════════════════════════
cat_label = KATEGORI.get(st.session_state.kategori_terpilih, "Semua")

if not items:
    st.markdown(f"""
    <div class="empty-state">
      <div class="empty-icon">◈</div>
      <h3>Tidak Ada Data</h3>
      <p>Tidak ada berita tersedia dalam 4 hari terakhir<br>untuk kategori <strong>{safe_text(cat_label)}</strong>.<br>Coba kategori lain atau tunggu update berikutnya.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="section-label">
      <span>FEED BERITA</span>
      <span class="count">{len(items)} artikel</span>
    </div>
    """, unsafe_allow_html=True)

    cols_news = st.columns(2)
    for i, item in enumerate(items):
        judul_id = terjemahkan_teks(item.get("judul", ""))
        deskripsi_id = terjemahkan_teks(item.get("deskripsi", ""))

        warna = sentiment_from_text(judul_id + " " + deskripsi_id)
        sent_lbl = sentiment_label(warna)

        tag_label = item.get("kategori_label") or KATEGORI.get(
            item.get("kategori_asli", st.session_state.kategori_terpilih),
            KATEGORI.get(st.session_state.kategori_terpilih, "LAINNYA")
        )
        key_prefix = f"{st.session_state.kategori_terpilih}_{i}"
        key_id = safe_text(key_prefix)

        waktu_fmt = fmt_waktu(item.get("waktu_terbit",""))

        with cols_news[i % 2]:
            # CARD HTML
            st.markdown(f"""
            <div class="news-card {warna}">
              <div class="card-inner">
                <div class="card-top">
                  <span class="cat-badge">{safe_text(tag_label)}</span>
                  <span class="sentiment-badge {warna}">{sent_lbl}</span>
                </div>
                <div class="news-title">{safe_text(judul_id)}</div>
                <div class="news-excerpt">{safe_text(deskripsi_id)}</div>
                <div class="card-meta">
                  <span class="meta-source">{safe_text(item.get('sumber',''))}</span>
                  <span class="meta-dot"></span>
                  <span>{safe_text(waktu_fmt)}</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ACTION BUTTONS
            c1, c2 = st.columns([1, 1])
            with c1:
                lbl_detail = "▲ TUTUP" if st.session_state.show_detail.get(key_id) else "▼ DETAIL"
                if st.button(lbl_detail, key=f"detail_btn_{key_id}", use_container_width=True):
                    st.session_state.show_detail[key_id] = not st.session_state.show_detail.get(key_id, False)
                    st.rerun()
            with c2:
                lbl_ai = "◈ AI ANALISIS"
                if st.button(lbl_ai, key=f"ai_btn_{key_id}", use_container_width=True):
                    # Trigger animasi loading → analisis
                    ai_steps = [
                        "Menghubungi AI Engine...",
                        "Mengidentifikasi pola pasar...",
                        "Menyusun hubungan variabel...",
                        "Membandingkan historis terbaru...",
                        "Merangkum inti berita...",
                    ]
                    ph = st.empty()
                    for step_idx, step in enumerate(ai_steps):
                        pct = int((step_idx + 1) / len(ai_steps) * 100)
                        steps_html = "".join([
                            f'<div class="ai-step {"active" if j == step_idx else ""}">'
                            f'{"▶" if j == step_idx else "✓" if j < step_idx else "○"} {s}'
                            f'</div>'
                            for j, s in enumerate(ai_steps)
                        ])
                        ph.markdown(f"""
                        <div class="ai-loading">
                          <div class="ai-loading-header">◈ AI ENGINE — MEMPROSES</div>
                          <div class="ai-progress-bar"><div class="ai-progress-fill" style="width:{pct}%; animation:none;"></div></div>
                          {steps_html}
                        </div>
                        """, unsafe_allow_html=True)
                        time.sleep(0.55)

                    ph.empty()

                    item_id = item.copy()
                    item_id["judul"] = judul_id
                    item_id["deskripsi"] = deskripsi_id
                    try:
                        hasil = analisis_ai(openrouter_key, item_id, tag_label)
                    except Exception as e:
                        hasil = f"Gagal menganalisis: {str(e)}"
                    st.session_state.ai_result[key_id] = hasil
                    st.rerun()

            # DETAIL PANEL
            if st.session_state.show_detail.get(key_id, False):
                st.markdown(f"""
                <div class="detail-panel">
                  <p>{safe_text(deskripsi_id)}</p>
                  <div style="margin-top:0.6rem; font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:var(--text-dim);">
                    EST. BACA ~2 MENIT • SUMBER: {safe_text(item.get('sumber',''))}
                  </div>
                </div>
                """, unsafe_allow_html=True)

            # AI RESULT PANEL
            if st.session_state.ai_result.get(key_id):
                st.markdown(f"""
                <div class="ai-panel">
                  <div class="ai-panel-header">
                    <div class="ai-dot"></div>
                    AEROVULPIS AI — ANALISIS PASAR
                  </div>
                  <div class="ai-content">{safe_text(st.session_state.ai_result[key_id])}</div>
                </div>
                """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="cyber-footer">
  <span class="brand">AEROVULPIS</span>
  <span>•</span>
  <span>© 2026 Market Intelligence Terminal</span>
  <span>•</span>
  <span class="dev">Dikembangkan oleh DynamiHatch • Teknologi Intelijensi Pasar Masa Depan</span>
</div>
""", unsafe_allow_html=True)