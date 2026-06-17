import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# PAGE CONFIG
# ==============================================================================
st.set_page_config(
    page_title="Aerovulpis Pro Terminal",
    page_icon="🔷",
    layout="wide"
)

# ==============================================================================
# GLOBAL CSS
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

:root {
    --bg: #070C18;
    --panel: #0C1425;
    --card: #111D35;
    --cyan: #00EEFF;
    --purple: #8B5CF6;
    --green: #00FF9D;
    --red: #FF3D71;
    --text: #C8D8F0;
    --text-muted: #4B6A8A;
    --border: #162035;
}
.stApp {
    background: #070C18 !important;
    background-image: 
        radial-gradient(ellipse at 10% 70%, rgba(139,92,246,0.07) 0%, transparent 45%),
        radial-gradient(ellipse at 90% 15%, rgba(0,238,255,0.07) 0%, transparent 45%),
        linear-gradient(rgba(0,238,255,0.022) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,238,255,0.022) 1px, transparent 1px);
    background-size: auto, auto, 48px 48px, 48px 48px;
    color: #C8D8F0 !important;
}
.block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
    padding-left: 0.3rem !important;
    padding-right: 0.3rem !important;
    overflow-x: hidden;
}

/* --- FIX: 3 KOLOM UTAMA AGAR SCROLL HORIZONTAL KE KANAN --- */
[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 8px !important;
    padding: 5px 0 0 0 !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    align-items: stretch !important;
}

[data-testid="column"] {
    flex: 0 0 auto !important; /* Mencegah kolom menyusut */
    display: flex !important;
    flex-direction: column !important;
}

/* Mengatur Lebar Spesifik Agar TradingView Lebih Lebar */
[data-testid="column"]:nth-of-type(1) { width: 320px !important; min-width: 320px !important; }
[data-testid="column"]:nth-of-type(2) { width: 600px !important; min-width: 600px !important; flex: 1 0 auto !important; }
[data-testid="column"]:nth-of-type(3) { width: 340px !important; min-width: 340px !important; }

/* Scrollbar Kustom */
::-webkit-scrollbar { height: 6px; width: 6px; }
::-webkit-scrollbar-thumb { background: #00EEFF; border-radius: 3px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }

/* --- RESET BERSARANG UNTUK AI SIGNAL FEED (Kolom 3) --- */
[data-testid="column"] [data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    overflow: visible !important;
    padding: 0 !important;
    gap: 4px !important;
}

/* --- CYBER BUTTON --- */
div.stButton > button {
    background: linear-gradient(135deg, rgba(0,238,255,0.15), rgba(139,92,246,0.15)) !important;
    border: 1px solid #00EEFF !important;
    border-radius: 4px !important;
    color: #00EEFF !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 10px !important;
    padding: 6px !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    width: 100% !important;
    height: 38px !important;
}
div.stButton > button:hover {
    box-shadow: 0 0 15px rgba(0,238,255,0.25) !important;
    transform: scale(1.02) !important;
}

/* --- SELECTOR TRADINGVIEW --- */
div[data-testid="stSelectbox"] { padding: 0 !important; margin: 0 0 4px 0 !important; }
div[data-testid="stSelectbox"] label { display: none !important; }
div[data-testid="stSelectbox"] div[data-baseweb="select"] { min-height: 32px !important; }
div[data-testid="stSelectbox"] div[data-baseweb="select"] div {
    font-size: 11px !important;
    font-family: 'Share Tech Mono', monospace !important;
    color: #00EEFF !important;
    background: #0C1425 !important;
    border: 1px solid rgba(0,238,255,0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# HELPER CSS UNTUK IFRAME COMPONENTS
# (Digunakan khusus untuk disuntikkan ke dalam components.html)
# ==============================================================================
IFRAME_PANEL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
body { margin: 0; padding: 0; background: transparent; overflow: hidden; height: 100vh;}
.cyber-panel-native {
    background: #0C1425; border: 1px solid #162035; border-radius: 8px;
    display: flex; flex-direction: column; height: 100%; box-sizing: border-box;
}
.panel-header {
    background: rgba(0,0,0,0.28); border-bottom: 1px solid #162035;
    padding: 6px 10px; display: flex; justify-content: space-between; align-items: center;
}
.panel-title { font-family: 'Share Tech Mono', monospace; font-size: 11px; color: #00EEFF; letter-spacing: 2px; text-transform: uppercase; }
.panel-badge { font-family: monospace; font-size: 9px; color: #4B6A8A; letter-spacing: 1px; text-transform: uppercase; }
.panel-body { flex: 1; min-height: 0; overflow: hidden; }
</style>
"""

# ==============================================================================
# HEADER & SENTINEL TITLE
# ==============================================================================
st.markdown("""
<div style="height: 44px; display: flex; align-items: center; justify-content: space-between; padding: 0 10px; background: rgba(7,12,24,0.97); border-bottom: 1px solid #162035;">
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="width: 24px; height: 24px; background: linear-gradient(135deg, #00EEFF, #8B5CF6); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-family: 'Share Tech Mono', monospace; font-size: 9px; font-weight: 700; color: #fff;">AV</div>
        <div style="font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #00EEFF; letter-spacing: 1px;">AEROVULPIS PRO</div>
    </div>
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #00EEFF; background: rgba(0,238,255,0.10); border: 1px solid rgba(0,238,255,0.22); padding: 2px 6px; border-radius: 3px; letter-spacing: 1px;">LONDON/NY</div>
    </div>
</div>
<div style="text-align: center; padding: 6px 0; border-bottom: 1px solid rgba(0,238,255,0.15); margin-bottom: 4px;">
    <span style="font-family: 'Share Tech Mono', monospace; font-size: 14px; color: #00EEFF; letter-spacing: 4px; text-shadow: 0 0 20px rgba(0,238,255,0.3);">[ AEROVULPIS SENTINEL NEXUS ]</span>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# TICKER TAPE
# ==============================================================================
ticker_html = """
<div class="tradingview-widget-container" style="height: 44px; overflow: hidden;">
    <div class="tradingview-widget-container__widget"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
    {
    "symbols": [{"proName": "FOREXCOM:SPXUSD", "title": "S&P 500"}, {"proName": "FX_IDC:EURUSD", "title": "EUR/USD"}, {"proName": "BITSTAMP:BTCUSD", "title": "Bitcoin"}, {"proName": "OANDA:XAUUSD", "title": "XAUUSD"}],
    "colorTheme": "dark", "isTransparent": true, "locale": "id", "width": "100%", "height": 44
    }
    </script>
</div>
"""
components.html(ticker_html, height=44)

# ==============================================================================
# 3 KOLOM UTAMA (HORIZONTAL, SCROLL)
# ==============================================================================
col1, col2, col3 = st.columns(3)

# --- KOLOM 1: ECONOMIC CALENDAR ---
with col1:
    eco_html = IFRAME_PANEL_CSS + """
    <div class="cyber-panel-native">
        <div class="panel-header">
            <span class="panel-title">Economic Calendar</span>
            <span class="panel-badge">Tradays</span>
        </div>
        <div class="panel-body">
            <iframe src="https://www.tradays.com/en/economic-calendar/widget?mode=2&colorTheme=dark" style="width:100%; height:100%; border:none; background:#0C1425;" frameborder="0" scrolling="auto"></iframe>
        </div>
    </div>
    """
    components.html(eco_html, height=620)

# --- KOLOM 2: TRADINGVIEW CHART + RSI ---
with col2:
    pair_options = ["XAUUSD", "BTCUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USOIL"]
    selected_pair = st.selectbox("", pair_options, index=0, key="chart_pair", label_visibility="collapsed")
    
    symbol_map = {"XAUUSD": "OANDA:XAUUSD", "BTCUSD": "BITSTAMP:BTCUSD", "EURUSD": "FX_IDC:EURUSD", "GBPUSD": "FX_IDC:GBPUSD", "USDJPY": "FX_IDC:USDJPY", "AUDUSD": "FX_IDC:AUDUSD", "USOIL": "TVC:USOIL"}
    tv_symbol = symbol_map.get(selected_pair, "OANDA:XAUUSD")
    
    # Ketinggian Chart diturunkan sedikit (584) agar pas dengan total tinggi div kolom 1 & 3 karena adanya combobox Streamlit di atasnya.
    chart_html = IFRAME_PANEL_CSS + f"""
    <div class="cyber-panel-native">
        <div class="panel-header">
            <span class="panel-title">{selected_pair} Chart</span>
            <span class="panel-badge">Live</span>
        </div>
        <div class="panel-body" id="tv_chart_main"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
            "autosize": true, "symbol": "{tv_symbol}", "interval": "60", "timezone": "Asia/Jakarta",
            "theme": "dark", "style": "2", "locale": "id", "enable_publishing": false,
            "hide_top_toolbar": false, "hide_legend": false, "save_image": false,
            "container_id": "tv_chart_main", "studies": ["RSI@tv-basicstudies"],
            "backgroundColor": "rgba(12,20,37,1)", "gridColor": "rgba(0,238,255,0.05)"
        }});
        </script>
    </div>
    """
    components.html(chart_html, height=580)

# --- KOLOM 3: AI SIGNAL FEED + HEATMAP ---
with col3:
    # Header Native Panel menggunakan st.markdown
    st.markdown("""
    <div style="background: rgba(0,0,0,0.28); border: 1px solid #162035; border-radius: 8px 8px 0 0; padding: 8px 10px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <span style="font-family: 'Share Tech Mono', monospace; font-size: 11px; color: #00EEFF; letter-spacing: 2px; text-transform: uppercase;">AI Signal Feed</span>
        <span style="font-family: monospace; font-size: 9px; color: #4B6A8A; letter-spacing: 1px;">CORE ENGINE</span>
    </div>
    <div style="font-family:'Share Tech Mono',monospace; font-size:9px; color:#4B6A8A; background:rgba(0,238,255,0.05); border-left:2px solid #00EEFF; padding:6px; border-radius:3px; margin-bottom: 8px;">
        [INFO] Masukkan pair/berita untuk analisis AI (contoh: EURUSD)
    </div>
    """, unsafe_allow_html=True)

    col_input, col_btn = st.columns([3, 1])
    with col_input:
        user_input = st.text_input("", placeholder="Ketik di sini...", key="ai_input", label_visibility="collapsed")
    with col_btn:
        send_clicked = st.button("▶ SEND", key="ai_send", use_container_width=True)

    if send_clicked and user_input:
        st.info(f"Analisis untuk: {user_input}")

    # Heatmap dibungkus terpisah di dalam components.html (Ketinggiannya disesuaikan sisa ruang layar)
    heatmap_html = IFRAME_PANEL_CSS + """
    <div class="cyber-panel-native" style="margin-top: 4px; border-radius: 0 0 8px 8px;">
        <div class="panel-header">
            <span class="panel-title">Currency Heatmap</span>
            <span class="panel-badge">Live</span>
        </div>
        <div class="panel-body">
            <div class="tradingview-widget-container" style="height: 100%;">
                <div class="tradingview-widget-container__widget" style="height: calc(100% - 32px);"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-forex-heat-map.js" async>
                {
                "colorTheme": "dark", "isTransparent": true, "locale": "id",
                "currencies": ["EUR","USD","JPY","GBP","CHF","AUD","CAD","NZD"],
                "width": "100%", "height": "100%"
                }
                </script>
            </div>
        </div>
    </div>
    """
    components.html(heatmap_html, height=420)


# ==============================================================================
# BAGIAN BAWAH: MERGE HTML ACTIVE TRADES & SIGNAL MATRIX (Mencegah DOM Leak)
# ==============================================================================
setup_data = [
    {"pair": "EURUSD", "dir": "SELL", "dir_cls": "sell", "entry": "1.08420", "tp1": "1.0795", "tp1_st": "✓", "tp2": "1.0750", "tp2_st": "✗", "tp3": "1.0680", "tp3_st": "~", "sl": "1.0890", "gradient": "#FF3D71"},
    {"pair": "USDJPY", "dir": "BUY", "dir_cls": "buy", "entry": "149.820", "tp1": "150.50", "tp1_st": "✓", "tp2": "151.20", "tp2_st": "✓", "tp3": "152.00", "tp3_st": "~", "sl": "149.20", "gradient": "#00FF9D"}
]

# Bangun HTML secara menyeluruh sebelum di render oleh Streamlit
bottom_html = """
<style>
.cyber-tag { font-family: 'Share Tech Mono', monospace; font-size: 8px; letter-spacing: 1px; padding: 2px 6px; border-radius: 3px; display: inline-block; }
.cyber-tag.buy { background: rgba(0,255,157,0.12); color: #00FF9D; border: 1px solid rgba(0,255,157,0.25); }
.cyber-tag.sell { background: rgba(255,61,113,0.12); color: #FF3D71; border: 1px solid rgba(255,61,113,0.25); }
.grid-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 8px; padding: 8px; }
.setup-card { background: #111D35; border: 1px solid #162035; border-radius: 6px; padding: 8px; position: relative; }
</style>
<div style="background: #0C1425; border: 1px solid #162035; border-radius: 8px; margin-top: 10px;">
    <div style="background: rgba(0,0,0,0.28); border-bottom: 1px solid #162035; padding: 8px 12px; display: flex; justify-content: space-between;">
        <span style="font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #00EEFF; letter-spacing: 2px; text-transform: uppercase;">Active Trade Setups</span>
    </div>
    <div class="grid-container">
"""

for setup in setup_data:
    tp1_col = "#00FF9D" if setup['tp1_st'] == "✓" else "#FF3D71" if setup['tp1_st'] == "✗" else "#4B6A8A"
    tp2_col = "#00FF9D" if setup['tp2_st'] == "✓" else "#FF3D71" if setup['tp2_st'] == "✗" else "#4B6A8A"
    bottom_html += f"""
        <div class="setup-card">
            <div style="position:absolute; top:0; left:0; right:0; height:2px; background:{setup['gradient']}; border-radius: 6px 6px 0 0;"></div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <span style="font-family:'Share Tech Mono',monospace; font-size:12px; font-weight:bold; color:#C8D8F0;">{setup['pair']}</span>
                <span class="cyber-tag {setup['dir_cls']}">{setup['dir']}</span>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:4px; font-family:sans-serif; font-size:10px;">
                <div><span style="color:#4B6A8A;">Entry</span><br><span style="color:#C8D8F0; font-weight:bold;">{setup['entry']}</span></div>
                <div><span style="color:#4B6A8A;">TP1</span><br><span style="color:{tp1_col}; font-weight:bold;">{setup['tp1']}</span></div>
                <div><span style="color:#4B6A8A;">TP2</span><br><span style="color:{tp2_col}; font-weight:bold;">{setup['tp2']}</span></div>
            </div>
        </div>
    """
bottom_html += "</div></div>"
st.markdown(bottom_html, unsafe_allow_html=True)


# ==============================================================================
# TOP STORIES (Memperbaiki Iframe yang terlempar keluar dari panel)
# ==============================================================================
news_html = IFRAME_PANEL_CSS + """
<div class="cyber-panel-native">
    <div class="panel-header">
        <span class="panel-title">Top Stories</span>
        <span class="panel-badge">TradingView</span>
    </div>
    <div class="panel-body">
        <div class="tradingview-widget-container" style="width:100%; height:100%;">
            <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-timeline.js" async>
            {
            "feedMode": "all_symbols", "colorTheme": "dark", "isTransparent": true,
            "displayMode": "regular", "width": "100%", "height": "100%", "locale": "id"
            }
            </script>
        </div>
    </div>
</div>
"""
# Ketinggian ditambah agar berita bisa ter-load secara maksimal
components.html(news_html, height=550)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("""
<div style="text-align: center; padding: 15px; opacity: 0.4;">
    <p style="font-family: 'Share Tech Mono', monospace; font-size: 9px; color: #4B6A8A; margin: 0; letter-spacing: 1px;">
        [PROTOTYPE] AEROVULPIS V3.5 | DYNAMIHATCH SYSTEM INTEGRATION
    </p>
</div>
""", unsafe_allow_html=True)