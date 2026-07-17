import time
import html  # Menangani pembersihan entitas HTML mentah
from datetime import datetime, timezone, timedelta
from html import escape

import streamlit as st
from deep_translator import GoogleTranslator

from config import KATEGORI
from news_fetcher import ambil_berita_kategori, ambil_semua_kategori
from ai_analyzer import analisis_ai
from utils import hapus_duplikat

st.set_page_config(page_title="Market Intelligence | Aerovulpis", layout="wide")

st.markdown("""
<style>
:root {
  --bg: #0a0f1a;
  --surface: #121826;
  --border: #2a364a;
  --text: #e6eef7;
  --text-muted: #94a3b8;
  --accent: #00a8d6;
  --neon-blue: #00f3ff;
  --card-bg: #151d2d;
  --divider: #2d3a52;
  --bullish: #00c896;
  --bearish: #ff5555;
  --neutral: #88ccff;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body, .stApp {
  background: var(--bg);
  color: var(--text);
  font-family: 'Inter', sans-serif;
}

.block-container {
  padding-top: 1.4rem;
  padding-bottom: 2rem;
  max-width: 1200px;
}

.top-title {
  text-align: center;
  margin-bottom: 2rem;
}

.top-title h1 {
  font-size: 2.2rem;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--text);
  margin-bottom: 1.5rem;
}

.top-title p {
  color: var(--text-muted);
  margin-top: 1rem;
  font-size: 1.05rem;
}

.category-wrap {
  margin: 1.5rem 0 3rem;
  display: flex;
  justify-content: center;
}

/* Modifikasi tombol Streamlit bawaan agar mirip dengan desain UI Aerovulpis */
div[data-testid="column"] {
    padding: 0 0.3rem;
    min-width: fit-content !important;
    flex: none !important;
}

div[data-testid="stButton"] button {
    background-color: transparent;
    border: 1px solid var(--border);
    color: var(--text-muted);
    border-radius: 6px;
    font-size: 0.9rem;
    padding: 0.4rem 1.2rem;
    transition: all 0.2s;
    height: auto;
}

div[data-testid="stButton"] button:hover {
    border-color: var(--accent);
    color: var(--accent);
    transform: translateY(-1px);
}

div[data-testid="stButton"] button:active,
div[data-testid="stButton"] button:focus {
    background: rgba(0, 168, 214, 0.1);
    color: var(--accent);
    border-color: var(--accent);
    font-weight: 600;
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1.5rem;
}

.news-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
  margin-bottom: 0.8rem;
}

.news-card:hover {
  border-color: var(--accent);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 168, 214, 0.08);
}

.sentiment-indicator {
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: var(--neutral);
}

.sentiment-bullish { background: var(--bullish); }
.sentiment-bearish { background: var(--bearish); }
.sentiment-neutral { background: var(--neutral); }

.card-body {
  padding: 1.5rem 1.4rem 1.25rem 1.4rem;
}

.category-tag {
  display: inline-flex;
  align-items: center;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  margin-bottom: 1rem;
  color: var(--text-muted);
}

.category-tag .dot {
  color: var(--accent);
  font-size: 1.5rem;
  line-height: 0;
  margin-right: 0.5rem;
}

.news-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.4;
  margin-bottom: 0.5rem;
}

.expand-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
  margin-top: 0.5rem;
}

.expand-btn {
  width: 32px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--accent);
  font-size: 1.3rem;
  cursor: pointer;
}

.expand-btn.collapsed::after { content: "▼"; }
.expand-btn.expanded::after { content: "▲"; }

.keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.2rem;
}

.news-excerpt {
  font-size: 1rem;
  color: var(--text-muted);
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  font-size: 0.86rem;
  color: var(--text-muted);
}

.source-meta {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  flex-wrap: wrap;
}

.source-name {
  font-weight: 500;
}

.time-divider {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--text-muted);
}

.detail-panel {
  display: none;
  background: rgba(20, 28, 44, 0.95);
  border-top: 1px solid var(--neon-blue);
  padding: 1.25rem 1.2rem 1.2rem;
  margin-top: 0;
  border-radius: 0 0 6px 6px;
  border-left: 1px solid var(--border);
  border-right: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}

.detail-panel.active {
  display: block;
}

.detail-content {
  font-size: 1rem;
  color: var(--text);
  line-height: 1.7;
}

.detail-meta {
  margin-top: 1rem;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.ai-status {
  display: none;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  margin-top: 1rem;
  font-size: 0.86rem;
  color: var(--text-muted);
}

.ai-status.active {
  display: block;
}

.ai-status.loading::after {
  content: " ...";
  color: var(--neon-blue);
}

.empty-state {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 3rem 2rem;
  text-align: center;
  color: var(--text-muted);
  max-width: 700px;
  margin: 2rem auto;
  font-size: 1.05rem;
  line-height: 1.6;
}

footer {
  text-align: center;
  padding-top: 2.6rem;
  margin-top: 3.2rem;
  border-top: 1px solid var(--divider);
  color: var(--text-muted);
  font-size: 0.86rem;
}

.dynamiHatch {
  font-style: italic;
  color: var(--accent);
  margin-top: 0.5rem;
  display: block;
}

@media (max-width: 768px) {
  .news-grid {
    grid-template-columns: 1fr;
  }
  .news-title {
    font-size: 1.2rem;
  }
  .top-title h1 {
    font-size: 1.8rem;
  }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-title">
  <h1>MARKET INTELLIGENCE</h1>
  <p>Analisis Mendalam untuk Trader Modern</p>
  <br>
  <p>Dirancang oleh Tim Aerovulpis</p>
</div>
""", unsafe_allow_html=True)

marketaux_key = st.secrets["MARKETAUX_API_KEY"]
openrouter_key = st.secrets["OPENROUTER_API_KEY"]

if "kategori_terpilih" not in st.session_state:
    st.session_state.kategori_terpilih = "all"
if "show_detail" not in st.session_state:
    st.session_state.show_detail = {}
if "ai_result" not in st.session_state:
    st.session_state.ai_result = {}

# Fungsi Cache untuk Terjemahan yang sudah diperbaiki dari bug kode mentah HTML
@st.cache_data(ttl=3600, max_entries=200)
def terjemahkan_teks(teks):
    if not teks: return ""
    try:
        # PENTING: Bersihkan entitas HTML mentah sebelum diterjemahkan oleh Google Translator
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
    if any(x in t for x in [
        "naik", "lonjak", "kuat", "rekor", "untung", "pulih",
        "tinggi", "peningkatan", "lompat", "reli", "pertumbuhan", "bullish"
    ]):
        return "bullish"
    if any(x in t for x in [
        "turun", "jatuh", "lemah", "merosot", "anjlok", "tumbang",
        "rendah", "kurang", "lambat", "bearish"
    ]):
        return "bearish"
    return "neutral"

def render_loading_animation(ph):
    steps = [
        "AI Menganalisa...",
        "Mengidentifikasi pola pasar...",
        "Menyusun hubungan antar variabel...",
        "Membandingkan dengan historis terbaru...",
        "Merangkum inti berita...",
        "Selesai — Executive Summary siap",
    ]
    for s in steps:
        ph.markdown(f"""
        <div class="ai-status active loading">
          <strong>{s}</strong>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.65)

def safe_text(v):
    return escape("" if v is None else str(v))

st.markdown('<div class="category-wrap">', unsafe_allow_html=True)
cols_btn = st.columns(len(KATEGORI))
for i, (k, v) in enumerate(KATEGORI.items()):
    with cols_btn[i]:
        if st.button(v, key=f"btn_cat_{k}", use_container_width=True):
            st.session_state.kategori_terpilih = k
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

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
    items = data_kategori.get(st.session_state.kategori_terpilled, [])

# --- FITUR FILTER RENTANG WAKTU (4 HARI TERAKHIR HINGGA SEKARANG) ---
items_terbaru = []
waktu_sekarang = datetime.now(timezone.utc)
batas_waktu = waktu_sekarang - timedelta(days=4)

for item in items:
    waktu_str = item.get("waktu_terbit", "")
    try:
        # Konversi format waktu ISO 8601 dari API ke format Datetime Python
        waktu_dt = datetime.fromisoformat(waktu_str.replace("Z", "+00:00"))
        # Berita valid jika berada dalam 4 hari terakhir
        if waktu_dt >= batas_waktu:
            items_terbaru.append(item)
    except Exception:
        # Jika format waktu dari API bermasalah, tetap simpan sebagai fallback aman
        items_terbaru.append(item)

items = items_terbaru
# ------------------------------------------------------------------

if not items:
    st.markdown(
        '<div class="empty-state">Tidak ada berita tersedia dalam 4 hari terakhir untuk kategori ini. Coba kategori lain atau tunggu update berikutnya dari pasar.</div>',
        unsafe_allow_html=True
    )
else:
    st.markdown('<div class="news-grid">', unsafe_allow_html=True)
    cols_news = st.columns(2)
    for i, item in enumerate(items):
        
        judul_id = terjemahkan_teks(item.get("judul", ""))
        deskripsi_id = terjemahkan_teks(item.get("deskripsi", ""))
        
        warna = sentiment_from_text(judul_id + " " + deskripsi_id)
        tag_label = item.get("kategori_label") or KATEGORI.get(
            item.get("kategori_asli", st.session_state.kategori_terpilih),
            KATEGORI.get(st.session_state.kategori_terpilih, "LAINNYA")
        )
        key_prefix = f"{st.session_state.kategori_terpilih}_{i}"
        key_id = safe_text(key_prefix)

        with cols_news[i % 2]:
            st.markdown(f"""
            <div class="news-card">
              <div class="sentiment-indicator sentiment-{warna}"></div>
              <div class="card-body">
                <div class="category-tag"><span class="dot">•</span>{safe_text(tag_label)}</div>
                
                <h3 class="news-title">{safe_text(judul_id)}</h3>
                
                <div class="expand-wrapper">
                  <button class="expand-btn {'expanded' if st.session_state.show_detail.get(key_id) else 'collapsed'}"></button>
                </div>
                
                <div class="keywords"></div>
                <div class="news-excerpt">{safe_text(deskripsi_id)}</div>
                
                <div class="card-footer">
                  <div class="source-meta">
                    <span class="source-name">{safe_text(item.get('sumber', ''))}</span>
                    <span class="time-divider"></span>
                    <span>{safe_text(item.get('waktu_terbit', ''))}</span>
                  </div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("Detail", key=f"detail_btn_{key_id}"):
                    st.session_state.show_detail[key_id] = not st.session_state.show_detail.get(key_id, False)
                    st.rerun()

            with c2:
                if st.button("AI Analisis", key=f"ai_btn_{key_id}"):
                    ph = st.empty()
                    with st.spinner("AI sedang menganalisis berita...", show_time=True):
                        render_loading_animation(ph)
                        item_id = item.copy()
                        item_id["judul"] = judul_id
                        item_id["deskripsi"] = deskripsi_id
                        hasil = analisis_ai(openrouter_key, item_id, tag_label)
                    st.session_state.ai_result[key_id] = hasil
                    st.rerun()

            if st.session_state.show_detail.get(key_id, False):
                st.markdown(f"""
                <div class="detail-panel active">
                  <div class="detail-content">{safe_text(deskripsi_id)}</div>
                  <div class="detail-meta">Durasi Baca: 2 Menit</div>
                </div>
                """, unsafe_allow_html=True)

            if st.session_state.ai_result.get(key_id):
                st.markdown(f"""
                <div class="ai-status active">
                  {safe_text(st.session_state.ai_result[key_id])}
                </div>
                """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<footer>
  © 2026 Aerovulpis
  <span class="dynamiHatch">Dikembangkan oleh DynamiHatch • Teknologi Intelijensi Pasar Masa Depan</span>
</footer>
""", unsafe_allow_html=True)
