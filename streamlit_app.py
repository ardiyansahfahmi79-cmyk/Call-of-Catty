import time
from datetime import datetime, timezone
from html import escape

import streamlit as st

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
  margin-bottom: 1.05rem;
}

.top-title h1 {
  font-size: 2rem;
  font-weight: 600;
  letter-spacing: 0.3px;
  color: var(--text);
}

.top-title p {
  color: var(--text-muted);
  margin-top: 0.35rem;
}

.category-wrap {
  margin: 0.8rem 0 2.1rem;
}

.category-row {
  display: flex;
  flex-wrap: nowrap;
  gap: 0.7rem;
  justify-content: center;
  align-items: center;
  overflow-x: auto;
  padding: 0.15rem 0 0.4rem;
  scrollbar-width: none;
}

.category-row::-webkit-scrollbar {
  display: none;
}

.category-btn {
  flex: 0 0 auto;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-muted);
  padding: 0.55rem 1rem;
  font-size: 0.87rem;
  cursor: pointer;
  border-radius: 4px;
  white-space: nowrap;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.category-btn.active {
  background: rgba(0, 168, 214, 0.05);
  color: var(--accent);
  border-color: var(--accent);
  font-weight: 500;
}

.section-label {
  color: var(--text-muted);
  font-size: 0.85rem;
  text-align: center;
  margin-top: -0.25rem;
  margin-bottom: 0.35rem;
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1.4rem;
}

.news-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
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
  padding: 1.4rem 1.4rem 1.25rem 1.1rem;
}

.category-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 0.77rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.9px;
  margin-bottom: 0.85rem;
  color: var(--text-muted);
}

.category-tag::before {
  content: "";
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
}

.news-title-row {
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
  margin-bottom: 0.85rem;
}

.news-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text);
  line-height: 1.42;
  flex: 1;
}

.expand-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--neon-blue);
  font-size: 1.05rem;
  cursor: pointer;
}

.expand-btn.collapsed::after { content: "▼"; }
.expand-btn.expanded::after { content: "▲"; }

.keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-bottom: 1rem;
}

.keyword {
  font-size: 0.75rem;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.05);
  padding: 0.22rem 0.55rem;
  border-radius: 3px;
}

.news-excerpt {
  font-size: 0.96rem;
  color: var(--text-muted);
  margin-bottom: 1.15rem;
  line-height: 1.55;
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
  border-radius: 6px;
  padding: 2rem;
  text-align: center;
  color: var(--text-muted);
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
  margin-top: 0.3rem;
  display: block;
}

@media (max-width: 768px) {
  .news-grid {
    grid-template-columns: 1fr;
  }
  .news-title {
    font-size: 1.12rem;
  }
  .top-title h1 {
    font-size: 1.7rem;
  }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-title">
  <h1>MARKET INTELLIGENCE</h1>
  <p>Analisis Mendalam untuk Trader Modern</p>
  <p>Dirancang oleh Tim Aerovulpis</p>
</div>
""", unsafe_allow_html=True)

marketaux_key = st.secrets["MARKETAUX_API_KEY"]
openrouter_key = st.secrets["OPENROUTER_API_KEY"]
tanggal_target = datetime.now(timezone.utc).date().isoformat()

if "kategori_terpilih" not in st.session_state:
    st.session_state.kategori_terpilih = "all"
if "show_detail" not in st.session_state:
    st.session_state.show_detail = {}
if "ai_result" not in st.session_state:
    st.session_state.ai_result = {}

@st.cache_data(ttl=1800)
def muat_data_kategori(kategori, tanggal_target):
    if kategori == "all":
        return ambil_semua_kategori(marketaux_key, tanggal_target=tanggal_target)
    return {kategori: ambil_berita_kategori(kategori, marketaux_key, tanggal_target=tanggal_target)}

def sentiment_from_text(text):
    t = (text or "").lower()
    if any(x in t for x in [
        "rise", "surge", "beats", "strong", "record", "gain", "rebound",
        "higher", "increase", "jump", "rally", "growth"
    ]):
        return "bullish"
    if any(x in t for x in [
        "fall", "drop", "miss", "weak", "decline", "slump", "tumble",
        "lower", "reduce", "down", "slowdown"
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

def render_category_buttons(active):
    html = ['<div class="category-wrap"><div class="category-row">']
    for k, v in KATEGORI.items():
        cls = "category-btn active" if k == active else "category-btn"
        html.append(f'<span class="{cls}">{safe_text(v)}</span>')
    html.append('</div></div>')
    st.markdown("".join(html), unsafe_allow_html=True)

render_category_buttons(st.session_state.kategori_terpilih)

data_kategori = muat_data_kategori(st.session_state.kategori_terpilih, tanggal_target)

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

if not items:
    st.markdown(
        '<div class="empty-state">Tidak ada berita tersedia untuk hari ini pada kategori ini. Coba kategori lain atau tunggu update berikutnya.</div>',
        unsafe_allow_html=True
    )
else:
    st.markdown('<div class="news-grid">', unsafe_allow_html=True)
    cols_news = st.columns(2)
    for i, item in enumerate(items):
        warna = sentiment_from_text(item.get("judul", "") + " " + item.get("deskripsi", ""))
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
                <div class="category-tag">{safe_text(tag_label)}</div>
                <div class="news-title-row">
                  <h3 class="news-title">{safe_text(item.get('judul', ''))}</h3>
                  <button class="expand-btn {'expanded' if st.session_state.show_detail.get(key_id) else 'collapsed'}"></button>
                </div>
                <div class="keywords"></div>
                <div class="news-excerpt">{safe_text(item.get('deskripsi', ''))}</div>
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
                        hasil = analisis_ai(openrouter_key, item, tag_label)
                    st.session_state.ai_result[key_id] = hasil
                    st.rerun()

            if st.session_state.show_detail.get(key_id, False):
                st.markdown(f"""
                <div class="detail-panel active">
                  <div class="detail-content">{safe_text(item.get('deskripsi', ''))}</div>
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