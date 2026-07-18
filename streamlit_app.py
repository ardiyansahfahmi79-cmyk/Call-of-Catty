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

st.set_page_config(
    page_title="Market Intelligence | Aerovulpis",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg:         #060b14;
  --surface:    #0d1523;
  --surface2:   #0a1020;
  --border:     #1a2840;
  --text:       #c8d8ea;
  --text-muted: #5a7490;
  --text-dim:   #324560;
  --accent:     #00c8f0;
  --accent2:    #0055cc;
  --purple:     #6020cc;
  --bullish:    #00d090;
  --bearish:    #ff3060;
  --neutral:    #3380ff;
  --neon:       #00ffcc;
}

*, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }

html, body, .stApp {
  background: var(--bg) !important;
  color: var(--text);
  font-family: 'Inter', sans-serif;
}

/* Hapus semua ornamen Streamlit */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton, [data-testid="stToolbar"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

.block-container {
  padding: 0 1.2rem 3rem !important;
  max-width: 1300px !important;
}

/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
   HEADER
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
.aero-header {
  text-align: center;
  padding: 2.2rem 1rem 1.6rem;
}

.aero-header h1 {
  font-size: clamp(2rem, 6vw, 3.2rem);
  font-weight: 800;
  letter-spacing: 4px;
  line-height: 1.1;
  margin-bottom: 0.5rem;
  background: linear-gradient(120deg, #ffffff 20%, #00c8f0 60%, #6020cc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.aero-header .sub {
  font-size: 0.88rem;
  color: var(--text-muted);
  letter-spacing: 2px;
  margin-bottom: 0.25rem;
}

.aero-header .credit {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: var(--text-dim);
  letter-spacing: 1px;
}

.aero-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, var(--accent) 40%, var(--purple) 60%, transparent 100%);
  opacity: 0.35;
  max-width: 480px;
  margin: 1.2rem auto 0;
}

/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
   KATEGORI â€” HORIZONTAL SCROLL
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
.cat-scroll-wrapper {
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  margin: 1.4rem 0 0.8rem;
  padding-bottom: 4px;
}

.cat-scroll-wrapper::-webkit-scrollbar { display: none; }

.cat-scroll-inner {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  gap: 0.45rem;
  padding: 0.2rem 0.1rem;
  width: max-content;
  min-width: 100%;
  justify-content: center;
}

.cat-btn {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 1.8px;
  text-transform: uppercase;
  background: var(--surface);
  color: var(--text-muted);
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 0.45rem 1.1rem;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.18s ease;
  flex-shrink: 0;
  -webkit-tap-highlight-color: transparent;
}

.cat-btn:hover {
  background: rgba(0,200,240,0.07);
  color: var(--accent);
  border-color: rgba(0,200,240,0.45);
  box-shadow: 0 0 12px rgba(0,200,240,0.1);
}

.cat-btn.active {
  background: rgba(0,200,240,0.12);
  color: var(--accent);
  border-color: var(--accent);
  box-shadow: 0 0 16px rgba(0,200,240,0.18);
}

/* Streamlit button override â€” tetap ada untuk fallback */
div[data-testid="stHorizontalBlock"] {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  overflow-x: auto !important;
  justify-content: flex-start !important;
  gap: 0.4rem !important;
  scrollbar-width: none !important;
  -webkit-overflow-scrolling: touch !important;
  padding-bottom: 4px !important;
}
div[data-testid="stHorizontalBlock"]::-webkit-scrollbar { display: none !important; }

div[data-testid="column"] {
  padding: 0 !important;
  flex: 0 0 auto !important;
  width: auto !important;
  min-width: 0 !important;
}

div[data-testid="stButton"] > button {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.68rem !important;
  font-weight: 600 !important;
  letter-spacing: 1.8px !important;
  text-transform: uppercase !important;
  background: var(--surface) !important;
  color: var(--text-muted) !important;
  border: 1px solid var(--border) !important;
  border-radius: 3px !important;
  padding: 0.42rem 1rem !important;
  white-space: nowrap !important;
  height: auto !important;
  width: auto !important;
  min-width: 0 !important;
  transition: all 0.18s !important;
}
div[data-testid="stButton"] > button:hover {
  background: rgba(0,200,240,0.08) !important;
  color: var(--accent) !important;
  border-color: rgba(0,200,240,0.5) !important;
  box-shadow: 0 0 12px rgba(0,200,240,0.12) !important;
}
div[data-testid="stButton"] > button:focus,
div[data-testid="stButton"] > button:active {
  background: rgba(0,200,240,0.12) !important;
  color: var(--accent) !important;
  border-color: var(--accent) !important;
  box-shadow: 0 0 18px rgba(0,200,240,0.2) !important;
}

/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
   SECTION LABEL
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
.section-label {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: var(--text-dim);
  letter-spacing: 2.5px;
  text-transform: uppercase;
  margin: 0.8rem 0 1rem;
}
.section-label::before { content:''; flex:1; height:1px; background:var(--border); }
.section-label .count { color: var(--accent); font-weight: 600; }

/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
   NEWS CARD
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
.news-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--neutral);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 1rem;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}
.news-card.bullish { border-left-color: var(--bullish); }
.news-card.bearish { border-left-color: var(--bearish); }
.news-card.neutral { border-left-color: var(--neutral); }

.news-card:hover {
  transform: translateY(-2px);
  border-color: rgba(0,200,240,0.3);
  border-left-color: var(--accent);
  box-shadow: 0 6px 24px rgba(0,200,240,0.06);
}

.card-body { padding: 1.1rem 1.2rem 0.9rem 1.3rem; }

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.7rem;
  gap: 0.5rem;
}

.cat-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--accent);
  background: rgba(0,200,240,0.07);
  border: 1px solid rgba(0,200,240,0.2);
  border-radius: 2px;
  padding: 0.1rem 0.5rem;
  flex-shrink: 0;
}

.sent-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.56rem;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  padding: 0.1rem 0.45rem;
  border-radius: 2px;
  flex-shrink: 0;
}
.sent-badge.bullish { color:var(--bullish); background:rgba(0,208,144,0.09); border:1px solid rgba(0,208,144,0.25); }
.sent-badge.bearish { color:var(--bearish); background:rgba(255,48,96,0.09); border:1px solid rgba(255,48,96,0.25); }
.sent-badge.neutral { color:var(--neutral); background:rgba(51,128,255,0.09); border:1px solid rgba(51,128,255,0.25); }

.news-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.45;
  margin-bottom: 0.6rem;
}

.news-desc {
  font-size: 0.82rem;
  color: var(--text-muted);
  line-height: 1.62;
  margin-bottom: 0.8rem;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  color: var(--text-dim);
  flex-wrap: wrap;
}
.meta-src { color: var(--text-muted); font-weight: 600; }
.meta-dot { width:3px; height:3px; border-radius:50%; background:var(--text-dim); flex-shrink:0; }

/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
   DETAIL PANEL
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
.detail-panel {
  border-top: 1px solid rgba(0,200,240,0.12);
  background: rgba(0,8,20,0.5);
  padding: 0.9rem 1.2rem 0.9rem 1.3rem;
}
.detail-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.56rem;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: 0.5rem;
}
.detail-text {
  font-size: 0.83rem;
  color: var(--text-muted);
  line-height: 1.7;
}
.detail-foot {
  margin-top: 0.5rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.57rem;
  color: var(--text-dim);
}

/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
   AI ANIMASI LOADING
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
.ai-loading-wrap {
  border-top: 1px solid rgba(0,200,240,0.15);
  background: linear-gradient(135deg, rgba(0,200,240,0.025), rgba(96,32,204,0.02));
  padding: 1rem 1.2rem 1rem 1.3rem;
}

.ai-load-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 2.5px;
  color: var(--accent);
  text-transform: uppercase;
  margin-bottom: 0.7rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.ai-spinner {
  width: 8px; height: 8px;
  border-radius: 50%;
  border: 1.5px solid rgba(0,200,240,0.2);
  border-top-color: var(--accent);
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

.ai-bar-wrap {
  height: 3px;
  background: rgba(255,255,255,0.05);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.8rem;
}
.ai-bar-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, var(--accent2), var(--accent), var(--neon));
  transition: width 0.45s ease;
}

.ai-steps-grid {
  display: flex;
  flex-direction: column;
  gap: 0.28rem;
}
.ai-step-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.63rem;
  color: var(--text-dim);
  transition: color 0.2s;
}
.ai-step-row.step-done   { color: var(--bullish); }
.ai-step-row.step-active { color: var(--accent); }
.ai-step-icon { font-size: 0.7rem; width: 14px; text-align: center; flex-shrink:0; }

/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
   AI RESULT PANEL
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
.ai-result-wrap {
  border-top: 1px solid rgba(0,200,240,0.15);
  background: linear-gradient(135deg, rgba(0,200,240,0.03), rgba(96,32,204,0.025));
  padding: 1rem 1.2rem 1.1rem 1.3rem;
}

.ai-result-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.8rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 600;
  letter-spacing: 2.5px;
  color: var(--accent);
  text-transform: uppercase;
}

.ai-pulse-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 8px var(--accent);
  animation: pulse-glow 2s ease-in-out infinite;
  flex-shrink: 0;
}
@keyframes pulse-glow {
  0%,100% { opacity:1; box-shadow: 0 0 6px var(--accent); }
  50%      { opacity:0.4; box-shadow: 0 0 16px var(--accent); }
}

.ai-result-text {
  font-size: 0.84rem;
  color: var(--text);
  line-height: 1.8;
  white-space: pre-wrap;
}

/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
   EMPTY STATE
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
.empty-wrap {
  text-align: center;
  padding: 3.5rem 2rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  margin: 1.5rem auto;
  max-width: 520px;
}
.empty-icon { font-size: 1.6rem; opacity:0.2; margin-bottom: 0.9rem; }
.empty-wrap h3 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}
.empty-wrap p { font-size: 0.82rem; color: var(--text-dim); line-height: 1.65; }

/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
   FOOTER
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
.aero-footer {
  margin-top: 2.5rem;
  padding: 1.2rem;
  border-top: 1px solid var(--border);
  text-align: center;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem;
  color: var(--text-dim);
  line-height: 1.9;
}
.aero-footer .brand { color: var(--accent); font-weight: 700; letter-spacing: 2px; }

/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
   RESPONSIVE
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */
@media (max-width: 768px) {
  .block-container { padding-left: 0.6rem !important; padding-right: 0.6rem !important; }
  .news-title { font-size: 0.9rem; }
  .aero-header h1 { letter-spacing: 2px; }
  .cat-scroll-inner { justify-content: flex-start; }
}
</style>
""", unsafe_allow_html=True)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HEADER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
st.markdown("""
<div class="aero-header">
  <h1>MARKET INTELLIGENCE</h1>
  <div class="sub">Analisis Mendalam untuk Trader Modern</div>
  <div class="credit">Dirancang oleh Tim Aerovulpis</div>
  <div class="aero-divider"></div>
</div>
""", unsafe_allow_html=True)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECRETS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
marketaux_key  = st.secrets["MARKETAUX_API_KEY"]
openrouter_key = st.secrets["OPENROUTER_API_KEY"]

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SESSION STATE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
if "kategori_terpilih" not in st.session_state:
    st.session_state.kategori_terpilih = "all"
if "show_detail" not in st.session_state:
    st.session_state.show_detail = {}
if "ai_result" not in st.session_state:
    st.session_state.ai_result = {}

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HELPERS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
@st.cache_data(ttl=3600, max_entries=200)
def terjemahkan(teks: str) -> str:
    if not teks:
        return ""
    try:
        return GoogleTranslator(source='en', target='id').translate(html.unescape(teks))
    except Exception:
        return teks

# api_key sebagai parameter agar cache benar
@st.cache_data(ttl=1800, show_spinner=False)
def muat_data(kategori: str, api_key: str):
    if kategori == "all":
        return ambil_semua_kategori(api_key)
    return {kategori: ambil_berita_kategori(kategori, api_key)}

def sentimen(text: str) -> str:
    t = (text or "").lower()
    if any(x in t for x in ["naik","lonjak","kuat","rekor","untung","pulih","tinggi","peningkatan","lompat","reli","pertumbuhan","bullish"]):
        return "bullish"
    if any(x in t for x in ["turun","jatuh","lemah","merosot","anjlok","tumbang","rendah","kurang","lambat","bearish"]):
        return "bearish"
    return "neutral"

SENT_LBL = {"bullish":"â–² BULLISH","bearish":"â–¼ BEARISH","neutral":"â— NETRAL"}

def sx(v) -> str:
    return escape("" if v is None else str(v))

def fmt_dt(s: str) -> str:
    try:
        dt = datetime.fromisoformat(s.replace("Z","+00:00"))
        return dt.strftime("%d %b %Y %H:%M")
    except Exception:
        return s or ""

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# KATEGORI â€” HORIZONTAL SCROLL (pakai st.columns + CSS override)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
kat_list = list(KATEGORI.items())
cols_btn = st.columns(len(kat_list))
for i, (k, v) in enumerate(kat_list):
    with cols_btn[i]:
        if st.button(v, key=f"cat_{k}", use_container_width=False):
            st.session_state.kategori_terpilih = k
            st.session_state.show_detail = {}
            st.session_state.ai_result = {}
            st.rerun()

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# LOAD DATA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with st.spinner("Memuat berita..."):
    data_kategori = muat_data(st.session_state.kategori_terpilih, marketaux_key)

if st.session_state.kategori_terpilih == "all":
    items = []
    for k, arr in data_kategori.items():
        for x in arr:
            xx = dict(x); xx["kategori_asli"] = k
            items.append(xx)
    items = hapus_duplikat(items)
else:
    items = data_kategori.get(st.session_state.kategori_terpilih, [])

# Filter 4 hari
batas = datetime.now(timezone.utc) - timedelta(days=4)
filtered = []
for item in items:
    try:
        wt = datetime.fromisoformat(item.get("waktu_terbit","").replace("Z","+00:00"))
        if wt >= batas:
            filtered.append(item)
    except Exception:
        filtered.append(item)
items = filtered

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# RENDER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
cat_lbl = KATEGORI.get(st.session_state.kategori_terpilih, "Semua")

if not items:
    st.markdown(f"""
    <div class="empty-wrap">
      <div class="empty-icon">â—ˆ</div>
      <h3>Tidak Ada Data</h3>
      <p>Tidak ada berita dalam 4 hari terakhir<br>
         untuk kategori <strong>{sx(cat_lbl)}</strong>.<br>
         Coba kategori lain atau tunggu update berikutnya.</p>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="section-label">
      <span>FEED BERITA</span>
      <span class="count">{len(items)} artikel</span>
    </div>""", unsafe_allow_html=True)

    cols_news = st.columns(2)
    for i, item in enumerate(items):
        judul_id = terjemahkan(item.get("judul",""))
        desc_id  = terjemahkan(item.get("deskripsi",""))
        warna    = sentimen(judul_id + " " + desc_id)
        sent_lbl = SENT_LBL.get(warna,"â— NETRAL")

        tag = item.get("kategori_label") or KATEGORI.get(
            item.get("kategori_asli", st.session_state.kategori_terpilih),
            KATEGORI.get(st.session_state.kategori_terpilih,"LAINNYA")
        )
        kid      = sx(f"{st.session_state.kategori_terpilih}_{i}")
        wkt      = fmt_dt(item.get("waktu_terbit",""))

        with cols_news[i % 2]:
            # â”€â”€ KARTU â”€â”€
            st.markdown(f"""
            <div class="news-card {warna}">
              <div class="card-body">
                <div class="card-top">
                  <span class="cat-badge">{sx(tag)}</span>
                  <span class="sent-badge {warna}">{sent_lbl}</span>
                </div>
                <div class="news-title">{sx(judul_id)}</div>
                <div class="news-desc">{sx(desc_id)}</div>
                <div class="card-meta">
                  <span class="meta-src">{sx(item.get('sumber',''))}</span>
                  <span class="meta-dot"></span>
                  <span>{sx(wkt)}</span>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            # â”€â”€ TOMBOL AKSI â”€â”€
            c1, c2 = st.columns(2)
            with c1:
                lbl_d = "â–² TUTUP" if st.session_state.show_detail.get(kid) else "â–¼ DETAIL"
                if st.button(lbl_d, key=f"d_{kid}", use_container_width=True):
                    st.session_state.show_detail[kid] = not st.session_state.show_detail.get(kid, False)
                    st.rerun()
            with c2:
                if st.button("â—ˆ AI ANALISIS", key=f"ai_{kid}", use_container_width=True):
                    AI_STEPS = [
                        "Membaca data berita...",
                        "Mengidentifikasi konteks pasar...",
                        "Memetakan dampak ke aset...",
                        "Menilai sentimen global...",
                        "Menyusun analisis akhir...",
                        "Memverifikasi kesimpulan...",
                        "Finalisasi laporan...",
                    ]
                    total = len(AI_STEPS)
                    ph = st.empty()

                    for idx, step in enumerate(AI_STEPS):
                        pct = int((idx + 1) / total * 85)
                        rows = ""
                        for j, s in enumerate(AI_STEPS):
                            if j < idx:
                                cls, icon = "step-done", "âœ“"
                            elif j == idx:
                                cls, icon = "step-active", "â–¶"
                            else:
                                cls, icon = "", "â—‹"
                            rows += f'<div class="ai-step-row {cls}"><span class="ai-step-icon">{icon}</span>{escape(s)}</div>'

                        ph.markdown(f"""
                        <div class="ai-loading-wrap">
                          <div class="ai-load-title">
                            <div class="ai-spinner"></div>
                            AI ENGINE â€” MEMPROSES
                          </div>
                          <div class="ai-bar-wrap">
                            <div class="ai-bar-fill" style="width:{pct}%"></div>
                          </div>
                          <div class="ai-steps-grid">{rows}</div>
                        </div>""", unsafe_allow_html=True)
                        time.sleep(10 / total)

                    # Progress 100%
                    ph.markdown("""
                    <div class="ai-loading-wrap">
                      <div class="ai-load-title">
                        <div class="ai-spinner"></div>
                        AI ENGINE â€” MENYELESAIKAN...
                      </div>
                      <div class="ai-bar-wrap">
                        <div class="ai-bar-fill" style="width:100%"></div>
                      </div>
                    </div>""", unsafe_allow_html=True)

                    # Panggil AI
                    item_trj = item.copy()
                    item_trj["judul"]     = judul_id
                    item_trj["deskripsi"] = desc_id
                    try:
                        hasil = analisis_ai(openrouter_key, item_trj, tag)
                    except Exception as e:
                        hasil = f"Gagal menganalisis: {str(e)}"

                    ph.empty()
                    st.session_state.ai_result[kid] = hasil
                    st.rerun()

            # â”€â”€ DETAIL PANEL â”€â”€
            if st.session_state.show_detail.get(kid, False):
                st.markdown(f"""
                <div class="detail-panel">
                  <div class="detail-label">Detail Berita</div>
                  <div class="detail-text">{sx(desc_id)}</div>
                  <div class="detail-foot">Sumber: {sx(item.get('sumber',''))} &nbsp;â€¢&nbsp; Est. baca ~2 menit</div>
                </div>""", unsafe_allow_html=True)

            # â”€â”€ AI RESULT PANEL â”€â”€
            if st.session_state.ai_result.get(kid):
                st.markdown(f"""
                <div class="ai-result-wrap">
                  <div class="ai-result-header">
                    <div class="ai-pulse-dot"></div>
                    AEROVULPIS AI â€” ANALISIS PASAR
                  </div>
                  <div class="ai-result-text">{sx(st.session_state.ai_result[kid])}</div>
                </div>""", unsafe_allow_html=True)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FOOTER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
st.markdown("""
<div class="aero-footer">
  <span class="brand">AEROVULPIS</span> &nbsp;â€¢&nbsp; Â© 2026 Market Intelligence Terminal<br>
  Dikembangkan oleh DynamiHatch &nbsp;â€¢&nbsp; Teknologi Intelijensi Pasar Masa Depan
</div>""", unsafe_allow_html=True)