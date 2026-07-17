import streamlit as st
from datetime import datetime, timezone
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
* { margin:0; padding:0; box-sizing:border-box; }
body, .stApp {
  background: var(--bg);
  color: var(--text);
  font-family: 'Inter', sans-serif;
}
.block-container { padding-top: 2.2rem; padding-bottom: 2rem; max-width: 1200px; }
.container { max-width: 1200px; margin: 0 auto; padding: 2.2rem 1rem; }
header { text-align: center; margin-bottom: 2.2rem; }
h1 { font-size: 2rem; font-weight: 600; color: var(--text); letter-spacing: 0.3px; }
.subtitle { font-size: 1rem; color: var(--text-muted); margin-top: 0.4rem; }
.by-aerovulpis { font-size: 0.87rem; color: var(--text-muted); margin-top: 0.6rem; }
.categories { display:flex; flex-wrap:wrap; gap:.7rem; justify-content:center; margin-bottom:2.4rem; }
.category-btn {
  background: transparent; border: 1px solid var(--border); color: var(--text-muted);
  padding: 0.55rem 1rem; font-size: 0.87rem; border-radius: 4px; white-space: nowrap;
  display:inline-block; text-decoration:none;
}
.category-btn.active { background: rgba(0,168,214,.05); color: var(--accent); border-color: var(--accent); font-weight: 500; }
.news-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 1.3rem; }
.news-card {
  background: var(--card-bg); border: 1px solid var(--border); border-radius: 6px; overflow: hidden;
  position: relative; margin-bottom: 0.8rem;
}
.news-card:hover { border-color: var(--accent); box-shadow: 0 8px 20px rgba(0,168,214,.1); }
.sentiment-indicator { position:absolute; top:0; left:0; width:4px; height:100%; background: var(--neutral); }
.sentiment-bullish { background: var(--bullish); }
.sentiment-bearish { background: var(--bearish); }
.sentiment-neutral { background: var(--neutral); }
.card-body { padding: 1.5rem 1.45rem 1.3rem 1.15rem; }
.category-tag {
  display:inline-flex; align-items:center; gap:.6rem; font-size:.77rem; font-weight:500;
  text-transform:uppercase; letter-spacing:.9px; margin-bottom:.9rem; color: var(--text-muted);
}
.category-tag::before { content:""; width:5px; height:5px; border-radius:50%; background: var(--accent); }
.news-title { font-size:1.32rem; font-weight:600; color: var(--text); line-height:1.42; margin-bottom:.95rem; }
.expand-btn {
  width:24px; height:24px; border:none; background:transparent; color: var(--neon-blue); font-size:1.1rem; cursor:pointer;
}
.expand-btn.collapsed::after { content:"▼"; }
.expand-btn.expanded::after { content:"▲"; }
.title-row { display:flex; align-items:center; gap:.8rem; }
.keywords { display:flex; flex-wrap:wrap; gap:.5rem; margin-bottom:1rem; }
.keyword { font-size:.75rem; color: var(--text-muted); background: rgba(255,255,255,.05); padding:.2rem .6rem; border-radius:3px; }
.news-excerpt { font-size:.96rem; color: var(--text-muted); margin-bottom:1.35rem; line-height:1.55; }
.highlight { color: var(--accent); font-weight:500; }
.card-footer { display:flex; justify-content:space-between; align-items:center; font-size:.86rem; color: var(--text-muted); }
.source-meta { display:flex; align-items:center; gap:.8rem; flex-wrap:wrap; }
.time-divider { width:4px; height:4px; border-radius:50%; background: var(--text-muted); margin:0 .4rem; }
.ai-btn {
  width:28px; height:28px; border:none; background: rgba(255,255,255,.05); border-radius:4px;
  color: var(--text-muted); cursor:pointer;
}
.ai-btn:hover { background: rgba(0,243,255,.15); color: var(--neon-blue); }
.detail-panel {
  background: rgba(20,28,44,.95); border-top:1px solid var(--neon-blue); padding:1.5rem; margin-top:1rem;
  border-radius: 0 0 6px 6px; border-left:1px solid var(--border); border-right:1px solid var(--border); border-bottom:1px solid var(--border);
}
.detail-content { font-size:1rem; color: var(--text); line-height:1.7; }
.detail-meta { margin-top:1rem; font-size:.85rem; color: var(--text-muted); }
.ai-status {
  padding:1rem; background: rgba(0,0,0,.3); border-radius:4px; margin-top:1rem; font-size:.85rem; color: var(--text-muted);
}
.empty-state {
  background: var(--card-bg); border:1px solid var(--border); border-radius:6px; padding:2rem; text-align:center; color: var(--text-muted);
}
footer {
  text-align:center; padding-top:2.6rem; margin-top:3.2rem; border-top:1px solid var(--divider); color: var(--text-muted); font-size:.86rem;
}
.dynamiHatch { font-style:italic; color: var(--accent); margin-top:.3rem; display:block; }
@media (max-width: 768px) {
  .news-grid { grid-template-columns:1fr; }
  h1 { font-size:1.7rem; }
  .container { padding: 1.7rem 1rem; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="container">
  <header>
    <h1>MARKET INTELLIGENCE</h1>
    <p class="subtitle">Analisis Mendalam untuk Trader Modern</p>
    <p class="by-aerovulpis">Dirancang oleh Tim Aerovulpis</p>
  </header>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Pengaturan")
    kategori_terpilih = st.radio(
        "Pilih kategori",
        list(KATEGORI.keys()),
        format_func=lambda x: KATEGORI[x],
        index=0
    )
    st.caption("Limit 5 berita per kategori. Mode 'Semua' menggabungkan semua kategori hari ini.")
    refresh = st.button("Muat Ulang Berita")
    st.caption(f"Tanggal acuan: {datetime.now(timezone.utc).strftime('%d %b %Y')}")

marketaux_key = st.secrets["MARKETAUX_API_KEY"]
openrouter_key = st.secrets["OPENROUTER_API_KEY"]
tanggal_target = datetime.now(timezone.utc).date().isoformat()

@st.cache_data(ttl=1800)
def muat_data_kategori(kategori, tanggal_target):
    if kategori == "all":
        return ambil_semua_kategori(marketaux_key, tanggal_target=tanggal_target)
    return {kategori: ambil_berita_kategori(kategori, marketaux_key, tanggal_target=tanggal_target)}

if refresh:
    st.cache_data.clear()

data_kategori = muat_data_kategori(kategori_terpilih, tanggal_target)

st.markdown('<div class="categories">' + ''.join([
    f'<span class="category-btn {"active" if k == kategori_terpilih else ""}">{v}</span>'
    for k, v in KATEGORI.items()
]) + '</div>', unsafe_allow_html=True)

if kategori_terpilih == "all":
    items = []
    for k, arr in data_kategori.items():
        for x in arr:
            xx = dict(x)
            xx["kategori_asli"] = k
            items.append(xx)
    items = hapus_duplikat(items)
else:
    items = data_kategori.get(kategori_terpilih, [])

if not items:
    st.markdown('<div class="empty-state">Tidak ada berita tersedia untuk hari ini pada kategori ini.</div>', unsafe_allow_html=True)
else:
    cols = st.columns(2)
    for i, item in enumerate(items):
        berita_lower = (item.get("judul", "") + " " + item.get("deskripsi", "")).lower()
        warna = "neutral"
        if any(x in berita_lower for x in ["rise", "surge", "beats", "strong", "record", "bullish", "gain", "rebound", "higher", "increase", "jump", "rally", "growth"]):
            warna = "bullish"
        if any(x in berita_lower for x in ["fall", "drop", "miss", "weak", "bearish", "decline", "slump", "tumble", "lower", "reduce", "down", "slowdown"]):
            warna = "bearish"

        tag_label = item.get("kategori_label") or KATEGORI.get(item.get("kategori_asli", kategori_terpilih), KATEGORI.get(kategori_terpilih, "LAINNYA"))
        key_prefix = f"{kategori_terpilih}_{i}"

        with cols[i % 2]:
            st.markdown(f"""
            <div class="news-card">
              <div class="sentiment-indicator sentiment-{warna}"></div>
              <div class="card-body">
                <div class="category-tag">{tag_label}</div>
                <div class="title-row">
                  <h3 class="news-title">{item.get('judul', '')}</h3>
                </div>
                <div class="keywords"></div>
                <p class="news-excerpt">{item.get('deskripsi', '')}</p>
                <div class="card-footer">
                  <div class="source-meta">
                    <span class="source-name">{item.get('sumber', '')}</span>
                    <span class="time-divider"></span>
                    <span>{item.get('waktu_terbit', '')}</span>
                  </div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("Detail", key=f"detail_{key_prefix}"):
                    st.session_state[f"show_detail_{key_prefix}"] = not st.session_state.get(f"show_detail_{key_prefix}", False)
            with c2:
                if st.button("AI Analisis", key=f"ai_{key_prefix}"):
                    st.session_state[f"do_ai_{key_prefix}"] = True

            if st.session_state.get(f"show_detail_{key_prefix}", False):
                st.markdown(f"""
                <div class="detail-panel">
                  <div class="detail-content">{item.get('deskripsi', '')}</div>
                  <div class="detail-meta">Durasi Baca: 2 Menit</div>
                </div>
                """, unsafe_allow_html=True)

            if st.session_state.get(f"do_ai_{key_prefix}", False):
                with st.spinner("AI sedang menganalisis berita..."):
                    hasil = analisis_ai(openrouter_key, item, tag_label)
                st.markdown(f'<div class="ai-status">{hasil}</div>', unsafe_allow_html=True)
                st.session_state[f"do_ai_{key_prefix}"] = False

st.markdown("""
<div class="container">
  <footer>
    © 2026 Aerovulpis
    <span class="dynamiHatch">Dikembangkan oleh DynamiHatch • Teknologi Intelijensi Pasar Masa Depan</span>
  </footer>
</div>
""", unsafe_allow_html=True)