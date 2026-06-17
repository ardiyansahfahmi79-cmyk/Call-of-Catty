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
# CSS - PASTIKAN 3 KOLOM HORIZONTAL, TIDAK BERTUMPUK
# ==============================================================================
st.markdown("""
<style>
:root {
    --bg: #070C18;
    --panel: #0C1425;
    --card: #111D35;
    --cyan: #00EEFF;
    --cyan-dim: rgba(0,238,255,0.10);
    --cyan-border: rgba(0,238,255,0.22);
    --purple: #8B5CF6;
    --purple-dim: rgba(139,92,246,0.10);
    --green: #00FF9D;
    --red: #FF3D71;
    --text: #C8D8F0;
    --text-muted: #4B6A8A;
    --text-dim: #243450;
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
html, body, .stApp {
    height: 100% !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
}
.block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
    padding-left: 0.3rem !important;
    padding-right: 0.3rem !important;
}

/* --- 3 KOLOM UTAMA - HORIZONTAL, TIDAK PECAH KE BAWAH --- */
.block-container > [data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 8px !important;
    padding: 5px 0 0 0 !important;
    min-height: 620px !important;
    align-items: stretch !important;
    overflow-x: auto !important;
    overflow-y: visible !important;
}

/* --- RESET KOLOM BERSARANG (nested) --- */
[data-testid="column"] [data-testid="stHorizontalBlock"] {
    min-height: unset !important;
    height: auto !important;
    gap: 4px !important;
    padding: 0 !important;
    margin-bottom: 4px !important;
    flex-wrap: nowrap !important;
}

[data-testid="column"] {
    height: auto !important;
    display: flex !important;
    flex-direction: column !important;
    flex-shrink: 0 !important;
}
[data-testid="column"]:nth-of-type(1) { min-width: 280px !important; width: 280px !important; }
[data-testid="column"]:nth-of-type(2) { min-width: 420px !important; width: 420px !important; }
[data-testid="column"]:nth-of-type(3) { min-width: 300px !important; width: 300px !important; }

[data-testid="stHorizontalBlock"]::-webkit-scrollbar { height: 4px; }
[data-testid="stHorizontalBlock"]::-webkit-scrollbar-thumb { background: #00EEFF; border-radius: 2px; }
[data-testid="stHorizontalBlock"]::-webkit-scrollbar-track { background: transparent; }

/* --- PANEL --- */
.cyber-panel-native {
    background: #0C1425;
    border: 1px solid #162035;
    border-radius: 10px;
    position: relative;
    overflow: hidden;
    padding: 4px;
    margin-bottom: 6px;
    flex: 1;
    display: flex;
    flex-direction: column;
}
.cyber-panel-native .panel-header {
    background: rgba(0,0,0,0.28);
    border-bottom: 1px solid #162035;
    padding: 4px 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
}
.cyber-panel-native .panel-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #00EEFF;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.cyber-panel-native .panel-badge {
    font-family: monospace;
    font-size: 7px;
    color: #4B6A8A;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.cyber-panel-native .panel-body {
    flex: 1;
    overflow-y: auto;
    padding: 4px;
}
.cyber-panel-native .panel-iframe {
    flex: 1;
    min-height: 0;
    padding: 0;
}

/* --- CYBER BUTTON --- */
div.stButton > button {
    background: linear-gradient(135deg, rgba(0,238,255,0.15), rgba(139,92,246,0.15)) !important;
    border: 1px solid #00EEFF !important;
    border-radius: 4px !important;
    color: #00EEFF !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 9px !important;
    padding: 6px 14px !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    width: 100% !important;
    height: 38px !important;
    box-shadow: 0 0 12px rgba(0,238,255,0.1) !important;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,238,255,0.3), rgba(139,92,246,0.3)) !important;
    box-shadow: 0 0 24px rgba(0,238,255,0.25) !important;
    transform: scale(1.02) !important;
}

/* --- GRIDS --- */
.trade-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 6px;
    padding: 4px;
}
.signal-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 6px;
    padding: 4px;
}

/* --- TAGS --- */
.cyber-tag {
    font-family: 'Share Tech Mono', monospace;
    font-size: 6px;
    letter-spacing: 1px;
    padding: 1px 4px;
    border-radius: 3px;
    display: inline-block;
}
.cyber-tag.buy {
    background: rgba(0,255,157,0.12);
    color: #00FF9D;
    border: 1px solid rgba(0,255,157,0.25);
}
.cyber-tag.sell {
    background: rgba(255,61,113,0.12);
    color: #FF3D71;
    border: 1px solid rgba(255,61,113,0.25);
}

/* --- SELECTOR --- */
div[data-testid="stSelectbox"] {
    padding: 0 !important;
    margin: 0 !important;
}
div[data-testid="stSelectbox"] label {
    display: none !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    min-height: 28px !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] div {
    font-size: 10px !important;
    font-family: 'Share Tech Mono', monospace !important;
    color: #00EEFF !important;
    background: rgba(0,0,0,0.3) !important;
    border: 1px solid rgba(0,238,255,0.2) !important;
    border-radius: 4px !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# HEADER
# ==============================================================================
st.markdown("""
<div style="height: 44px; display: flex; align-items: center; justify-content: space-between; padding: 0 10px; background: rgba(7,12,24,0.97); border-bottom: 1px solid #162035; flex-shrink: 0;">
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="width: 24px; height: 24px; background: linear-gradient(135deg, #00EEFF, #8B5CF6); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-family: 'Share Tech Mono', monospace; font-size: 9px; font-weight: 700; color: #fff; box-shadow: 0 0 10px rgba(0,238,255,0.25);">AV</div>
        <div style="font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #00EEFF; letter-spacing: 1px;">AEROVULPIS PRO</div>
    </div>
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="display: flex; align-items: center; gap: 3px; font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #00FF9D; letter-spacing: 1px;">
            <div style="width: 4px; height: 4px; background: #00FF9D; border-radius: 50%; animation: blink 2s infinite;"></div>LIVE
        </div>
        <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #00EEFF; background: rgba(0,238,255,0.10); border: 1px solid rgba(0,238,255,0.22); padding: 1px 6px; border-radius: 3px; letter-spacing: 1px;">LONDON/NY</div>
    </div>
</div>
<style>
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.2; } }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# JUDUL SENTINEL
# ==============================================================================
st.markdown("""
<div style="text-align: center; padding: 6px 0; border-bottom: 1px solid rgba(0,238,255,0.15); margin-bottom: 4px;">
    <span style="font-family: 'Share Tech Mono', monospace; font-size: 14px; color: #00EEFF; letter-spacing: 4px; text-shadow: 0 0 20px rgba(0,238,255,0.3);">
        [ AEROVULPIS SENTINEL NEXUS ]
    </span>
    <span style="font-family: 'Share Tech Mono', monospace; font-size: 8px; color: #4B6A8A; margin-left: 12px; letter-spacing: 2px;">
        QUANTUM INTELLIGENCE CORE
    </span>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# TICKER TAPE
# ==============================================================================
ticker_html = """
<div class="tradingview-widget-container" style="margin-bottom: 4px; height: 44px; overflow: hidden;">
    <div class="tradingview-widget-container__widget" style="height:100%;"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
    {
    "symbols": [
        {"proName": "FOREXCOM:SPXUSD", "title": "S&P 500"},
        {"proName": "FOREXCOM:NSXUSD", "title": "US 100"},
        {"proName": "FX_IDC:EURUSD", "title": "EUR/USD"},
        {"proName": "BITSTAMP:BTCUSD", "title": "Bitcoin"},
        {"proName": "BITSTAMP:ETHUSD", "title": "Ethereum"},
        {"proName": "OANDA:XAUUSD", "title": "XAUUSD"},
        {"proName": "TVC:DXY", "title": "DXY"},
        {"proName": "IDX:COMPOSITE", "title": "IHSG"},
        {"proName": "OANDA:USDJPY", "title": "USD/JPY"}
    ],
    "colorTheme": "dark",
    "isTransparent": true,
    "locale": "id",
    "width": "100%",
    "height": 44
    }
    </script>
</div>
"""
components.html(ticker_html, height=50)

# ==============================================================================
# 3 KOLOM UTAMA (HORIZONTAL, SCROLL)
# ==============================================================================
col1, col2, col3 = st.columns(3)

# --- KOLOM 1: ECONOMIC CALENDAR ---
with col1:
    st.markdown("""
    <div class="cyber-panel-native" style="height:620px;">
        <div class="panel-header">
            <span class="panel-title">Economic Calendar</span>
            <span class="panel-badge">Tradays</span>
        </div>
        <div class="panel-iframe" style="flex:1; min-height:0;">
            <iframe src="https://www.tradays.com/en/economic-calendar/widget?mode=2&colorTheme=dark" 
                    style="width:100%; height:100%; border:none; background:#0C1425;" 
                    frameborder="0" scrolling="auto">
            </iframe>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- KOLOM 2: TRADINGVIEW CHART + RSI (dengan pair selector) ---
with col2:
    # Pair selector
    pair_options = ["XAUUSD", "BTCUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USOIL"]
    selected_pair = st.selectbox("", pair_options, index=0, key="chart_pair", label_visibility="collapsed")
    
    # Mapping pair ke simbol TradingView
    symbol_map = {
        "XAUUSD": "OANDA:XAUUSD",
        "BTCUSD": "BITSTAMP:BTCUSD",
        "EURUSD": "FX_IDC:EURUSD",
        "GBPUSD": "FX_IDC:GBPUSD",
        "USDJPY": "FX_IDC:USDJPY",
        "AUDUSD": "FX_IDC:AUDUSD",
        "USOIL": "TVC:USOIL"
    }
    tv_symbol = symbol_map.get(selected_pair, "OANDA:XAUUSD")
    
    chart_html = f"""
    <div class="cyber-panel-native" style="height:620px;">
        <div class="panel-header">
            <span class="panel-title">{selected_pair} Chart & RSI</span>
            <span class="panel-badge">TradingView</span>
        </div>
        <div class="panel-iframe" style="flex:1; min-height:0;">
            <div id="tv_chart_main" style="height:100%;width:100%;"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({{
                "autosize": true,
                "symbol": "{tv_symbol}",
                "interval": "60",
                "timezone": "Asia/Jakarta",
                "theme": "dark",
                "style": "2",
                "locale": "id",
                "enable_publishing": false,
                "hide_top_toolbar": false,
                "hide_legend": false,
                "save_image": false,
                "container_id": "tv_chart_main",
                "studies": ["RSI@tv-basicstudies"],
                "backgroundColor": "rgba(7,12,24,1)",
                "gridColor": "rgba(0,238,255,0.04)"
            }});
            </script>
        </div>
    </div>
    """
    components.html(chart_html, height=620)

# --- KOLOM 3: AI SIGNAL FEED + HEATMAP ---
with col3:
    st.markdown("""
    <div class="cyber-panel-native" style="height:620px;">
        <div class="panel-header">
            <span class="panel-title">AI Signal Feed</span>
            <span class="panel-badge">Core Engine</span>
        </div>
        <div class="panel-body" style="display:flex; flex-direction:column; gap:4px;">
    """, unsafe_allow_html=True)

    # Pemberitahuan
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace; font-size:8px; color:#4B6A8A; background:rgba(0,238,255,0.05); border-left:2px solid #00EEFF; padding:4px 6px; border-radius:3px; flex-shrink:0;">
        [INFO] Masukkan pair atau berita untuk analisis AI (contoh: EURUSD, CPI, FOMC)
    </div>
    """, unsafe_allow_html=True)

    # Input & Tombol Kirim
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        user_input = st.text_input("", placeholder="EURUSD, CPI, FOMC...", key="ai_input", label_visibility="collapsed")
    with col_btn:
        send_clicked = st.button("▶ SEND", key="ai_send", use_container_width=True)

    # Hasil AI
    if send_clicked and user_input:
        st.info(f"Analisis untuk: {user_input} (contoh AI)")
    else:
        st.caption(" ")

    # HEATMAP
    heatmap_html = """
    <div class="tradingview-widget-container" style="width:100%; margin-top:4px; flex-shrink:0;">
        <div class="tradingview-widget-container__widget"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-forex-heat-map.js" async>
        {
        "colorTheme": "dark",
        "isTransparent": true,
        "locale": "id",
        "currencies": ["EUR","USD","JPY","GBP","CHF","AUD","CAD","NZD","CNY"],
        "width": "100%",
        "height": 300
        }
        </script>
    </div>
    """
    components.html(heatmap_html, height=310)

    st.markdown("</div></div>", unsafe_allow_html=True)

# ==============================================================================
# BAGIAN BAWAH
# ==============================================================================

# --- ACTIVE TRADE SETUPS (dengan TP1, TP2, TP3 status) ---
st.markdown("""
<div class="cyber-panel-native">
    <div class="panel-header">
        <span class="panel-title">Active Trade Setups</span>
        <span class="panel-badge">Prototype</span>
    </div>
    <div style="padding: 4px;">
""", unsafe_allow_html=True)

setup_data = [
    {"pair": "EURUSD", "dir": "SELL", "dir_cls": "sell", "entry": "1.08420", 
     "tp1": "1.07950", "tp1_st": "✓", "tp2": "1.07500", "tp2_st": "✗", "tp3": "1.06800", "tp3_st": "~", 
     "sl": "1.08900", "gradient": "#FF3D71"},
    {"pair": "USDJPY", "dir": "BUY", "dir_cls": "buy", "entry": "149.820", 
     "tp1": "150.500", "tp1_st": "✓", "tp2": "151.200", "tp2_st": "✓", "tp3": "152.000", "tp3_st": "~", 
     "sl": "149.200", "gradient": "#00FF9D"},
    {"pair": "XAUUSD", "dir": "SELL", "dir_cls": "sell", "entry": "2,014.50", 
     "tp1": "2,000.00", "tp1_st": "✗", "tp2": "1,990.00", "tp2_st": "~", "tp3": "1,975.00", "tp3_st": "~", 
     "sl": "2,025.00", "gradient": "#FF3D71"},
    {"pair": "DXY", "dir": "LONG BIAS", "dir_cls": "buy", "entry": "105.840", 
     "tp1": "106.500", "tp1_st": "~", "tp2": "107.200", "tp2_st": "~", "tp3": "108.000", "tp3_st": "~", 
     "sl": "104.900", "gradient": "#00FF9D"}
]

st.markdown('<div class="trade-grid">', unsafe_allow_html=True)
for setup in setup_data:
    tp1_color = "#00FF9D" if setup['tp1_st'] == "✓" else "#FF3D71" if setup['tp1_st'] == "✗" else "#4B6A8A"
    tp2_color = "#00FF9D" if setup['tp2_st'] == "✓" else "#FF3D71" if setup['tp2_st'] == "✗" else "#4B6A8A"
    tp3_color = "#00FF9D" if setup['tp3_st'] == "✓" else "#FF3D71" if setup['tp3_st'] == "✗" else "#4B6A8A"
    
    st.markdown(f"""
    <div style="background:#111D35; border:1px solid #162035; border-radius:6px; padding:6px; position:relative; padding-top:8px;">
        <div style="position:absolute; top:0; left:0; right:0; height:2px; background:{setup['gradient']};"></div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <span style="font-family:'Share Tech Mono',monospace; font-size:11px; font-weight:bold; color:#C8D8F0;">{setup['pair']}</span>
            <span class="cyber-tag {setup['dir_cls']}">{setup['dir']}</span>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:2px; font-size:9px;">
            <div><span style="color:#4B6A8A;">Entry</span> <br><span style="color:#C8D8F0;">{setup['entry']}</span></div>
            <div><span style="color:#4B6A8A;">TP1</span> <br><span style="color:{tp1_color};">{setup['tp1']} [{setup['tp1_st']}]</span></div>
            <div><span style="color:#4B6A8A;">TP2</span> <br><span style="color:{tp2_color};">{setup['tp2']} [{setup['tp2_st']}]</span></div>
            <div><span style="color:#4B6A8A;">TP3</span> <br><span style="color:{tp3_color};">{setup['tp3']} [{setup['tp3_st']}]</span></div>
        </div>
        <div style="margin-top:2px; font-size:8px; color:#4B6A8A;">
            SL: <span style="color:#FF3D71;">{setup['sl']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div></div></div>', unsafe_allow_html=True)

# --- SIGNAL MATRIX (dengan TP1, TP2, TP3 status) ---
st.markdown("""
<div class="cyber-panel-native">
    <div class="panel-header">
        <span class="panel-title">Signal Matrix</span>
        <span class="panel-badge">Live</span>
    </div>
    <div style="padding: 4px;">
""", unsafe_allow_html=True)

signal_data = [
    {"symbol": "XAUUSD", "dir": "BUY", "entry": "2,014.50", 
     "tp1": "2,025.00", "tp1_st": "✓", "tp2": "2,035.00", "tp2_st": "✗", "tp3": "2,050.00", "tp3_st": "~", 
     "conf": 78},
    {"symbol": "BTCUSD", "dir": "BUY", "entry": "65,790.00", 
     "tp1": "66,800.00", "tp1_st": "✓", "tp2": "67,500.00", "tp2_st": "~", "tp3": "68,900.00", "tp3_st": "~", 
     "conf": 72},
    {"symbol": "EURUSD", "dir": "SELL", "entry": "1.08420", 
     "tp1": "1.07950", "tp1_st": "✗", "tp2": "1.07500", "tp2_st": "~", "tp3": "1.06800", "tp3_st": "~", 
     "conf": 65},
    {"symbol": "GBPUSD", "dir": "SELL", "entry": "1.3430", 
     "tp1": "1.3370", "tp1_st": "~", "tp2": "1.3310", "tp2_st": "~", "tp3": "1.3220", "tp3_st": "~", 
     "conf": 60}
]

st.markdown('<div class="signal-grid">', unsafe_allow_html=True)
for sig in signal_data:
    cls = "buy" if sig['dir'] == "BUY" else "sell"
    color = "#00FF9D" if sig['dir'] == "BUY" else "#FF3D71"
    
    tp1_color = "#00FF9D" if sig['tp1_st'] == "✓" else "#FF3D71" if sig['tp1_st'] == "✗" else "#4B6A8A"
    tp2_color = "#00FF9D" if sig['tp2_st'] == "✓" else "#FF3D71" if sig['tp2_st'] == "✗" else "#4B6A8A"
    tp3_color = "#00FF9D" if sig['tp3_st'] == "✓" else "#FF3D71" if sig['tp3_st'] == "✗" else "#4B6A8A"
    
    st.markdown(f"""
    <div style="background:#111D35; border:1px solid #162035; border-radius:4px; padding:6px; position:relative; padding-top:8px;">
        <div style="position:absolute; top:0; left:0; right:0; height:2px; background:{color};"></div>
        <div style="display:flex; justify-content:space-between; font-family:'Share Tech Mono',monospace; font-size:10px; font-weight:bold; margin-bottom:4px;">
            <span style="color:#00EEFF;">{sig['symbol']}</span>
            <span class="cyber-tag {cls}">{sig['dir']}</span>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:2px; font-size:8px; color:#4B6A8A;">
            <div>Entry: <b style="color:#C8D8F0;">{sig['entry']}</b></div>
            <div>TP1: <b style="color:{tp1_color};">{sig['tp1']} [{sig['tp1_st']}]</b></div>
            <div>TP2: <b style="color:{tp2_color};">{sig['tp2']} [{sig['tp2_st']}]</b></div>
            <div>TP3: <b style="color:{tp3_color};">{sig['tp3']} [{sig['tp3_st']}]</b></div>
        </div>
        <div style="margin-top:2px; font-size:8px; color:#4B6A8A;">
            Conf: <b style="color:#00EEFF;">{sig['conf']}%</b>
        </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div></div></div>', unsafe_allow_html=True)

# ==============================================================================
# TOP STORIES
# ==============================================================================
st.markdown("""
<div class="cyber-panel-native">
    <div class="panel-header">
        <span class="panel-title">Top Stories</span>
        <span class="panel-badge">TradingView</span>
    </div>
    <div style="padding: 4px; height: 500px; overflow: hidden;">
""", unsafe_allow_html=True)

news_html = """
<div class="tradingview-widget-container" style="width:100%; height:100%;">
    <div class="tradingview-widget-container__widget" style="height:100%;"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-timeline.js" async>
    {
    "feedMode": "all_symbols",
    "colorTheme": "dark",
    "isTransparent": true,
    "displayMode": "regular",
    "width": "100%",
    "height": "100%",
    "locale": "id",
    "showHeader": true
    }
    </script>
</div>
"""
components.html(news_html, height=500)

st.markdown("""
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("""
<div style="text-align: center; padding: 4px; opacity: 0.4; width:100%;">
    <p style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #4B6A8A; margin: 0;">
        [PROTOTYPE] AEROVULPIS V3.5 | DYNAMIHATCH SYSTEM INTEGRATION
    </p>
</div>
""", unsafe_allow_html=True)