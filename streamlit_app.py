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
  --bg:         #060b14;
  --surface:    #0d1523;
  --border:     #1e2d45;
  --text:       #cdd9e8;
  --text-muted: #5f7a96;
  --text-dim:   #3d5470;
  --accent:     #00d4ff;
  --accent3:    #7b2fff;
  --bullish:    #00e5a0;
  --bearish:    #ff3d6b;
  --neutral:    #4d9fff;
}

* { margin:0; padding:0; box-sizing:border-box; }

body, .stApp {
  background: var(--bg) !important;
  color: var(--text);
  font-family: 'Inter', sans-serif;
}

/* Hapus semua pseudo-element background bawaan */
.stApp::before, .stApp::after { display: none !important; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

.block-container {
  padding-top: 1.2rem !important;
  padding-bottom: 3rem !important;
  max-width: 1280px !important;
}

/* ═══ HEADER ═══ */
.cyber-header {
  text-align: center;
  padding: 2rem 1rem 1.5rem;
}

.cyber-header h1 {
  font-size: clamp(1.8rem, 5vw, 3rem);
  font-weight: 800;
  letter-spacing: 3px;
  background: linear-gradient(135deg, #fff 30%, var(--accent) 70%, var(--accent3) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.15;
  margin-bottom: 0.5rem;
}

.cyber-header .tagline {
  font-size: 0.92rem;
  color: var(--text-muted);
  letter-spacing: 1px;
  margin-bottom: 0.2rem;
}

.cyber-header .by-line {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  color: var(--text-dim);
}

.header-line {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), var(--accent3), transparent);
  margin: 1.2rem auto 0;
  max-width: 500px;
  opacity: 0.4;
}

/* ═══ CATEGORY BUTTONS ═══ */
.cat-wrap { margin: 1.4rem 0 1rem; }

div[data-testid="stHorizontalBlock"] {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: wrap !important;
  justify-content: center !important;
  gap: 0.45rem !important;
  align-items: center !important;
}

div[data-testid="column"] {
  padding: 0 !important;
  width: auto !important;
  flex: 0 0 auto !important;
  min-width: 0 !important;
}

div[data-testid="stButton"] > button {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.72rem !important;
  font-weight: 500 !important;
  letter-spacing: 1.5px !important;
  text-transform: uppercase !important;
  background: var(--surface) !important;
  color: var(--text-muted) !important;
  border: 1px solid var(--border) !important;
  border-radius: 3px !important;
  padding: 0.42rem 1rem !important;
  width: auto !important;
  min-width: 0 !important;
  height: auto !important;
  white-space: nowrap !important;
  transition: all 0.18s !important;
}

div[data-testid="stButton"] > button:hover {
  background: rgba(0,212,255,0.07) !important;
  color: var(--accent) !important;
  border-color: rgba(0,212,255,0.5) !important;
  box-shadow: 0 0 10px rgba(0,212,255,0.12) !important;
  transform: translateY(-1px) !important;
}

div[data-testid="stButton"] > button:focus,
div[data-testid="stButton"] > button:active {
  background: rgba(0,212,255,0.1) !important;
  color: var(--accent) !important;
  border-color: var(--accent) !important;
  box-shadow: 0 0 16px rgba(0,212,255,0.18) !important;
}

/* ═══ SECTION LABEL ═══ */
.section-label {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  color: var(--text-dim);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin: 0.8rem 0 1rem;
}
.section-label::before { content:''; flex:1; height:1px; background:var(--border); }
.section-label .count { color: var(--accent); }

/* ═══ NEWS CARD ═══ */
.news-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
  position: relative;
  transition: all 0.22s ease;
  margin-bottom: 0.9rem;
}

.news-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 3px; height: 100%;
}

.news-card.bullish::before  { background: var(--bullish); }
.news-card.bearish::before  { background: var(--bearish); }
.news-card.neutral::before  { background: var(--neutral); }

.news-card:hover {
  border-color: rgba(0,212,255,0.35);
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(0,212,255,0.05);
}

.card-inner { padding: 1.1rem 1.2rem 0.9rem 1.4rem; }

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.65rem;
}

.cat-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--accent);
  background: rgba(0,212,255,0.07);
  border: 1px solid rgba(0,212,255,0.18);
  border-radius: 2px;
  padding: 0.12rem 0.5rem;
}

.sentiment-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.58rem;
  font-weight: 600;
  padding: 0.12rem 0.45rem;
  border-radius: 2px;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.sentiment-badge.bullish { color:var(--bullish); background:rgba(0,229,160,0.08); border:1px solid rgba(0,229,160,0.22); }
.sentiment-badge.bearish { color:var(--bearish); background:rgba(255,61,107,0.08); border:1px solid rgba(255,61,107,0.22); }
.sentiment-badge.neutral { color:var(--neutral); background:rgba(77,159,255,0.08); border:1px solid rgba(77,159,255,0.22); }

.news-title {
  font-size: 0.97rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.45;
  margin-bottom: 0.65rem;
}

.news-excerpt {
  font-size: 0.83rem;
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 0.85rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem;
  color: var(--text-dim);
  flex-wrap: wrap;
}
.meta-source { color: var(--text-muted); font-weight: 500; }
.meta-dot { width:3px; height:3px; border-radius:50%; background:var(--text-dim); flex-shrink:0; }

/* ═══ DETAIL PANEL ═══ */
.detail-panel {
  background: rgba(0,5,15,0.6);
  border-top: 1px solid rgba(0,212,255,0.15);
  padding: 1rem 1.2rem 1rem 1.4rem;
}
.detail-panel-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.58rem;
  color: var(--text-dim);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}
.detail-panel p {
  font-size: 0.85rem;
  color: var(--text-muted);
  line-height: 1.7;
}
.detail-panel-meta {
  margin-top: 0.5rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.58rem;
  color: var(--text-dim);
}

/* ═══ AI LOADING ═══ */
.ai-loading {
  padding: 1rem 1.2rem 1rem 1.4rem;
  background: rgba(0,212,255,0.02);
  border-top: 1px solid rgba(0,212,255,0.12);
}
.ai-loading-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem;
  color: var(--accent);
  letter-spacing: 2px;
  margin-bottom: 0.7rem;
}
.ai-progress-bar {
  height: 2px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.7rem;
}
.ai-progress-fill {
  height: 100%;
  border-radius: 2px;
  background: linear-gradient(90deg, #0070ff, #00d4ff, #00ffcc);
  transition: width 0.4s ease;
}
.ai-step {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: var(--text-dim);
  margin-bottom: 0.22rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.ai-step.done  { color: var(--bullish); }
.ai-step.active { color: var(--accent); }

/* ═══ AI RESULT PANEL ═══ */
.ai-panel {
  background: linear-gradient(135deg, rgba(0,212,255,0.025) 0%, rgba(123,47,255,0.025) 100%);
  border-top: 1px solid rgba(0,212,255,0.13);
  padding: 1rem 1.2rem 1.1rem 1.4rem;
}
.ai-panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  color: var(--accent);
  letter-spacing: 2px;
  text-transform: uppercase;
}
.ai-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 7px var(--accent);
  animation: pulse-dot 2s infinite;
  flex-shrink: 0;
}
@keyframes pulse-dot {
  0%,100% { opacity:1; box-shadow:0 0 6px var(--accent); }
  50%      { opacity:0.5; box-shadow:0 0 14px var(--accent); }
}
.ai-content {
  font-size: 0.84rem;
  color: var(--text);
  line-height: 1.75;
  white-space: pre-wrap;
}

/* ═══ EMPTY STATE ═══ */
.empty-state {
  text-align: center;
  padding: 3.5rem 2rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  margin: 1.5rem auto;
  max-width: 550px;
}
.empty-icon { font-size: 1.8rem; opacity: 0.25; margin-bottom: 1rem; }
.empty-state h3 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: var(--text-muted);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}
.empty-state p { font-size: 0.84rem; color: var(--text-dim); line-height: 1.6; }

/* ═══ FOOTER ═══ */
.cyber-footer {
  margin-top: 2.5rem;
  padding: 1.2rem;
  border-top: 1px solid var(--border);
  text-align: center;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.63rem;
  color: var(--text-dim);
  line-height: 1.8;
}
.cyber-footer .brand { color: var(--accent); font-weight: 600; }

/* ═══ RESPONSIVE ═══ */
@media (max-width: 768px) {
  .block-container { padding-left: 0.7rem !important; padding-right: 0.7rem !important; }
  .news-title { font-size: 0.92rem; }
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# HEADER — bersih, tanpa sys-label dan status bar
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div class="cyber-header">
  <h1>MARKET INTELLIGENCE</h1>
  <div class="tagline">Analisis Mendalam untuk Trader Modern</div>
  <div class="by-line">Dirancang oleh Tim Aerovulpis</div>
  <div class="header-line"></div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# SECRETS — ambil di sini, pass sebagai parameter ke cache
# ═══════════════════════════════════════════════════════════
marketaux_key   = st.secrets["MARKETAUX_API_KEY"]
openrouter_key  = st.secrets["OPENROUTER_API_KEY"]

# ═══════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════
if "kategori_terpilih" not in st.session_state:
    st.session_state.kategori_terpilih = "all"
if "show_detail" not in st.session_state:
    st.session_state.show_detail = {}
if "ai_result" not in st.session_state:
    st.session_state.ai_result = {}

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, max_entries=200)
def terjemahkan_teks(teks: str) -> str:
    if not teks:
        return ""
    try:
        teks_bersih = html.unescape(teks)
        return GoogleTranslator(source='en', target='id').translate(teks_bersih)
    except Exception:
        return teks

# FIX UTAMA: key API dipass sebagai parameter agar cache bekerja benar
@st.cache_data(ttl=1800)
def muat_data_kategori(kategori: str, api_key: str):
    if kategori == "all":
        return ambil_semua_kategori(api_key)
    return {kategori: ambil_berita_kategori(kategori, api_key)}

def sentiment_from_text(text: str) -> str:
    t = (text or "").lower()
    if any(x in t for x in ["naik","lonjak","kuat","rekor","untung","pulih","tinggi",
                              "peningkatan","lompat","reli","pertumbuhan","bullish"]):
        return "bullish"
    if any(x in t for x in ["turun","jatuh","lemah","merosot","anjlok","tumbang",
                              "rendah","kurang","lambat","bearish"]):
        return "bearish"
    return "neutral"

SENTIMENT_LABEL = {"bullish": "▲ BULLISH", "bearish": "▼ BEARISH", "neutral": "● NETRAL"}

def safe_text(v) -> str:
    return escape("" if v is None else str(v))

def fmt_waktu(s: str) -> str:
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y %H:%M")
    except Exception:
        return s or ""

# ═══════════════════════════════════════════════════════════
# CATEGORY BUTTONS
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="cat-wrap">', unsafe_allow_html=True)
cols_btn = st.columns(len(KATEGORI))
for i, (k, v) in enumerate(KATEGORI.items()):
    with cols_btn[i]:
        if st.button(v, key=f"btn_cat_{k}", use_container_width=False):
            st.session_state.kategori_terpilih = k
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# LOAD & FILTER DATA
# ═══════════════════════════════════════════════════════════
# API key dipass langsung — ini yang menyebabkan berita tidak muncul sebelumnya
data_kategori = muat_data_kategori(st.session_state.kategori_terpilih, marketaux_key)

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
batas_waktu = datetime.now(timezone.utc) - timedelta(days=4)
items_terbaru = []
for item in items:
    try:
        wt = datetime.fromisoformat(item.get("waktu_terbit", "").replace("Z", "+00:00"))
        if wt >= batas_waktu:
            items_terbaru.append(item)
    except Exception:
        items_terbaru.append(item)
items = items_terbaru

# ═══════════════════════════════════════════════════════════
# RENDER BERITA
# ═══════════════════════════════════════════════════════════
cat_label = KATEGORI.get(st.session_state.kategori_terpilih, "Semua")

if not items:
    st.markdown(f"""
    <div class="empty-state">
      <div class="empty-icon">◈</div>
      <h3>Tidak Ada Data</h3>
      <p>Tidak ada berita tersedia dalam 4 hari terakhir<br>
         untuk kategori <strong>{safe_text(cat_label)}</strong>.<br>
         Coba kategori lain atau tunggu update berikutnya.</p>
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
        judul_id      = terjemahkan_teks(item.get("judul", ""))
        deskripsi_id  = terjemahkan_teks(item.get("deskripsi", ""))

        warna     = sentiment_from_text(judul_id + " " + deskripsi_id)
        sent_lbl  = SENTIMENT_LABEL.get(warna, "● NETRAL")

        tag_label = item.get("kategori_label") or KATEGORI.get(
            item.get("kategori_asli", st.session_state.kategori_terpilih),
            KATEGORI.get(st.session_state.kategori_terpilih, "LAINNYA")
        )
        key_id = safe_text(f"{st.session_state.kategori_terpilih}_{i}")
        waktu_fmt = fmt_waktu(item.get("waktu_terbit", ""))

        with cols_news[i % 2]:
            # ── KARTU ──
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

            # ── TOMBOL AKSI ──
            c1, c2 = st.columns([1, 1])
            with c1:
                lbl_detail = "▲ TUTUP" if st.session_state.show_detail.get(key_id) else "▼ DETAIL"
                if st.button(lbl_detail, key=f"detail_btn_{key_id}", use_container_width=True):
                    st.session_state.show_detail[key_id] = not st.session_state.show_detail.get(key_id, False)
                    st.rerun()

            with c2:
                if st.button("◈ AI ANALISIS", key=f"ai_btn_{key_id}", use_container_width=True):
                    # Animasi loading step-by-step
                    AI_STEPS = [
                        "Menghubungi AI Engine...",
                        "Mengidentifikasi pola pasar...",
                        "Menyusun hubungan variabel...",
                        "Membandingkan data historis...",
                        "Merangkum inti berita...",
                    ]
                    ph = st.empty()
                    for idx, step in enumerate(AI_STEPS):
                        pct = int((idx + 1) / len(AI_STEPS) * 100)
                        rows_html = ""
                        for j, s in enumerate(AI_STEPS):
                            if j < idx:
                                cls, icon = "done", "✓"
                            elif j == idx:
                                cls, icon = "active", "▶"
                            else:
                                cls, icon = "", "○"
                            rows_html += f'<div class="ai-step {cls}"><span>{icon}</span>{escape(s)}</div>'

                        ph.markdown(f"""
                        <div class="ai-loading">
                          <div class="ai-loading-title">◈ AI ENGINE — MEMPROSES</div>
                          <div class="ai-progress-bar">
                            <div class="ai-progress-fill" style="width:{pct}%"></div>
                          </div>
                          {rows_html}
                        </div>
                        """, unsafe_allow_html=True)
                        time.sleep(0.5)

                    ph.empty()

                    # Panggil AI dengan key openrouter yang sudah ada
                    item_terjemah = item.copy()
                    item_terjemah["judul"]     = judul_id
                    item_terjemah["deskripsi"] = deskripsi_id
                    try:
                        hasil = analisis_ai(openrouter_key, item_terjemah, tag_label)
                    except Exception as e:
                        hasil = f"Gagal menganalisis: {str(e)}"

                    st.session_state.ai_result[key_id] = hasil
                    st.rerun()

            # ── PANEL DETAIL ──
            if st.session_state.show_detail.get(key_id, False):
                st.markdown(f"""
                <div class="detail-panel">
                  <div class="detail-panel-label">Detail Berita</div>
                  <p>{safe_text(deskripsi_id)}</p>
                  <div class="detail-panel-meta">Sumber: {safe_text(item.get('sumber',''))} • Est. baca ~2 menit</div>
                </div>
                """, unsafe_allow_html=True)

            # ── PANEL HASIL AI ──
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

# ═══════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div class="cyber-footer">
  <span class="brand">AEROVULPIS</span> &nbsp;•&nbsp; © 2026 Market Intelligence Terminal<br>
  Dikembangkan oleh DynamiHatch • Teknologi Intelijensi Pasar Masa Depan
</div>
""", unsafe_allow_html=True)