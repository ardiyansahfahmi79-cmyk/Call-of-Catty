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
# CSS CYBERTECH - STRIKTUR TERKUNCI HORIZONTAL (PC & HP TETAP SCROLL)
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
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
}

/* --- FORCE BARIS ATAS TETAP HORIZONTAL SCROLL DI MANAPUN (PC & HP) --- */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    gap: 8px !important;
    padding: 5px 0 !important;
    height: 70vh !important; /* Menjaga tinggi proporsional */
}

/* Menjaga lebar kolom agar tidak mengkeret/gepeng di HP */
[data-testid="column"] {
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    flex-shrink: 0 !important;
}
[data-testid="column"]:nth-of-type(1) { min-width: 290px !important; width: 290px !important; }
[data-testid="column"]:nth-of-type(2) { min-width: 410px !important; width: 410px !important; }
[data-testid="column"]:nth-of-type(3) { min-width: 280px !important; width: 280px !important; }

/* Kustomisasi Scrollbar Horizontal Baris Atas */
[data-testid="stHorizontalBlock"]::-webkit-scrollbar {
    height: 4px;
}
[data-testid="stHorizontalBlock"]::-webkit-scrollbar-thumb {
    background: #00EEFF;
    border-radius: 2px;
}

/* --- BAGIAN BAWAH --- */
.bottom-section {
    width: 100% !important;
    margin-top: 10px;
}

/* --- PANEL --- */
.cyber-panel {
    background: #0C1425;
    border: 1px solid #162035;
    border-radius: 10px;
    padding: 0;
    margin-bottom: 4px;
    position: relative;
    overflow: hidden;
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
}
.cyber-panel::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 11px;
    height: 11px;
    border: 2px solid rgba(0,238,255,0.45);
    border-width: 2px 0 0 2px;
    border-radius: 4px 0 0 0;
    pointer-events: none;
    z-index: 10;
}
.cyber-panel::after {
    content: '';
    position: absolute;
    bottom: 0;
    right: 0;
    width: 11px;
    height: 11px;
    border: 2px solid rgba(0,238,255,0.45);
    border-width: 0 2px 2px 0;
    border-radius: 0 0 4px 0;
    pointer-events: none;
    z-index: 10;
}
.cyber-header {
    background: rgba(0,0,0,0.28);
    border-bottom: 1px solid #162035;
    padding: 4px 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
}
.cyber-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #00EEFF;
    letter-spacing: 2.5px;
    text-transform: uppercase;
}
.cyber-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 7px;
    color: #4B6A8A;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.cyber-body {
    padding: 4px;
    flex: 1;
    min-height: 0;
    position: relative;
}
.cyber-body-iframe {
    padding: 0;
    flex: 1;
    min-height: 0;
    position: relative;
}
.scan-wrap {
    position: absolute;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
    border-radius: inherit;
    z-index: 6;
}
.scan-line {
    position: absolute;
    left: 0;
    right: 0;
    height: 55px;
    background: linear-gradient(to bottom, transparent, rgba(0,238,255,0.022), rgba(0,238,255,0.048), rgba(0,238,255,0.022), transparent);
    animation: scanDown 9s linear infinite;
}
@keyframes scanDown {
    from { transform: translateY(-60px); }
    to { transform: translateY(100%); }
}

/* --- DATA GRIDS (Bawah Tetap Responsif Menyesuaikan Lebar HP) --- */
.trade-grid, .signal-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 6px;
    padding: 4px;
}

.cyber-metric {
    background: #111D35;
    border: 1px solid #162035;
    border-radius: 6px;
    padding: 6px 8px;
    margin-bottom: 4px;
}
.cyber-metric-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 7px;
    color: #4B6A8A;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.cyber-metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 700;
}
.cyber-metric-value.bullish { color: #00FF9D; }
.cyber-metric-value.bearish { color: #FF3D71; }
.cyber-metric-value.neutral { color: #00EEFF; }
.cyber-metric-conf {
    font-family: 'JetBrains Mono', monospace;
    font-size: 8px;
    color: #4B6A8A;
}
.cyber-bar {
    margin-top: 4px;
    height: 2px;
    background: #162035;
    border-radius: 1px;
    overflow: hidden;
}
.cyber-bar-fill.bullish { background: linear-gradient(90deg, #00EEFF, #00FF9D); }
.cyber-bar-fill.bearish { background: linear-gradient(90deg, #8B5CF6, #FF3D71); }
.cyber-bar-fill.neutral { background: #00EEFF; }
.cyber-divider {
    height: 1px;
    background: #162035;
    margin: 4px 0;
}
.analysis-card {
    background: #111D35;
    border: 1px solid #162035;
    border-left: 2px solid #8B5CF6;
    border-radius: 6px;
    padding: 6px 8px;
    margin-bottom: 4px;
}
.analysis-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 8px;
    color: #8B5CF6;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 3px;
}
.analysis-text {
    font-size: 9px;
    line-height: 1.3;
    color: #C8D8F0;
}
.cyber-tag {
    font-family: 'Share Tech Mono', monospace;
    font-size: 6px;
    letter-spacing: 1px;
    padding: 1px 4px;
    border-radius: 3px;
    display: inline-block;
}
.cyber-tag.buy { background: rgba(0,255,157,0.12); color: #00FF9D; border: 1px solid rgba(0,255,157,0.25); }
.cyber-tag.sell { background: rgba(255,61,113,0.12); color: #FF3D71; border: 1px solid rgba(255,61,113,0.25); }
.cyber-tag.neutral { background: rgba(0,238,255,0.10); color: #00EEFF; border: 1px solid rgba(0,238,255,0.22); }
.cyber-tag.watch { background: rgba(139,92,246,0.10); color: #8B5CF6; border: 1px solid rgba(139,92,246,0.25); }

.mt5-fallback {
    position: absolute;
    bottom: 6px;
    right: 8px;
    z-index: 100;
    background: rgba(0,0,0,0.7);
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 7px;
    color: #4B6A8A;
}
.mt5-fallback a { color: #00EEFF; text-decoration: none; }

.signal-card {
    background: #111D35;
    border: 1px solid #162035;
    border-radius: 6px;
    padding: 6px;
    position: relative;
    overflow: hidden;
}
.signal-card .signal-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}
.signal-card .signal-symbol {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #00EEFF;
    letter-spacing: 1px;
}
.signal-card .signal-dir {
    font-family: 'Share Tech Mono', monospace;
    font-size: 7px;
    letter-spacing: 1px;
    padding: 1px 5px;
    border-radius: 3px;
}
.signal-dir.buy { background: rgba(0,255,157,0.12); color: #00FF9D; border: 1px solid rgba(0,255,157,0.25); }
.signal-dir.sell { background: rgba(255,61,113,0.12); color: #FF3D71; border: 1px solid rgba(255,61,113,0.25); }

.signal-values {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 2px;
}
.signal-values .sv-item {
    background: rgba(0,0,0,0.2);
    border-radius: 3px;
    padding: 2px 1px;
    text-align: center;
}
.sv-label { font-family: 'Share Tech Mono', monospace; font-size: 5px; color: #4B6A8A; text-transform: uppercase; }
.sv-value { font-family: 'JetBrains Mono', monospace; font-size: 8px; font-weight: 700; color: #C8D8F0; }
.sv-value.green { color: #00FF9D; }
.sv-value.red { color: #FF3D71; }
.sv-value.cyan { color: #00EEFF; }
.signal-tp-extra { margin-top: 3px; font-family: 'JetBrains Mono', monospace; font-size: 7px; color: #4B6A8A; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# HEADER
# ==============================================================================
st.markdown("""
<div style="
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 10px;
    background: rgba(7,12,24,0.97);
    border-bottom: 1px solid #162035;
    flex-shrink: 0;
">
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="
            width: 26px; height: 26px;
            background: linear-gradient(135deg, #00EEFF, #8B5CF6);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Share Tech Mono', monospace;
            font-size: 10px;
            font-weight: 700;
            color: #fff;
            box-shadow: 0 0 10px rgba(0,238,255,0.25);
        ">AV</div>
        <div>
            <div style="font-family: 'Share Tech Mono', monospace; font-size: 13px; color: #00EEFF; letter-spacing: 1.5px;">
                AEROVULPIS PRO TERMINAL
            </div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 8px;">
        <div style="display: flex; align-items: center; gap: 4px; font-family: 'Share Tech Mono', monospace; font-size: 8px; color: #00FF9D; letter-spacing: 1px;">
            <div style="width: 5px; height: 5px; background: #00FF9D; border-radius: 50%;"></div>
            LIVE FEED
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 3 KOLOM UTAMA (TERKUNCI HORIZONTAL SCROLL DI HP & PC)
# ==============================================================================
col1, col2, col3 = st.columns(3)

# --- KOLOM 1: ECONOMIC CALENDAR ---
with col1:
    st.markdown("""
    <div class="cyber-panel">
        <div class="cyber-header">
            <span class="cyber-title">Economic Calendar</span>
            <span class="cyber-badge">Tradays</span>
        </div>
        <div class="cyber-body-iframe">
            <iframe src="https://www.tradays.com/en/economic-calendar/widget?mode=2&colorTheme=dark" 
                    style="width:100%; height:100%; border:none; background:#0C1425;"
                    frameborder="0" scrolling="auto">
            </iframe>
        </div>
        <div class="scan-wrap"><div class="scan-line" style="animation-delay:0s;"></div></div>
    </div>
    """, unsafe_allow_html=True)

# --- KOLOM 2: DXY CHART + MT5 TERMINAL ---
with col2:
    # DXY Chart
    st.markdown("""
    <div class="cyber-panel" style="flex: 1;">
        <div class="cyber-header">
            <span class="cyber-title">DXY & RSI (TV)</span>
            <span class="cyber-badge">TradingView</span>
        </div>
        <div class="cyber-body-iframe">
            <div class="tradingview-widget-container" style="height:100%;width:100%;">
                <div id="tradingview_dxy" style="height:100%;width:100%;"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                <script type="text/javascript">
                new TradingView.widget({
                    "autosize": true,
                    "symbol": "TVC:DXY",
                    "interval": "60",
                    "timezone": "Asia/Jakarta",
                    "theme": "dark",
                    "style": "2",
                    "locale": "id",
                    "enable_publishing": false,
                    "hide_top_toolbar": true,
                    "hide_legend": false,
                    "save_image": false,
                    "container_id": "tradingview_dxy",
                    "studies": ["RSI@tv-basicstudies"],
                    "backgroundColor": "rgba(7,12,24,1)",
                    "gridColor": "rgba(0,238,255,0.04)"
                });
                </script>
            </div>
        </div>
    </div>
    <div class="cyber-panel" style="flex: 1; margin-top: 4px;">
        <div class="cyber-header">
            <span class="cyber-title">MT5 TERMINAL</span>
            <span class="cyber-badge">MetaTrader</span>
        </div>
        <div class="cyber-body-iframe">
            <iframe src="https://metatraderweb.app/trade" 
                    style="width:100%; height:100%; border:none; background:#0C1425;"
                    frameborder="0" allowfullscreen="true" scrolling="no">
            </iframe>
            <div class="mt5-fallback">
                [MT5] <a href="https://metatraderweb.app/trade" target="_blank">buka tab</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- KOLOM 3: AI SIGNAL FEED ---
with col3:
    st.markdown("""
    <div class="cyber-panel">
        <div class="cyber-header">
            <span class="cyber-title">AI SIGNAL FEED</span>
            <span class="cyber-badge">Core Engine</span>
        </div>
        <div class="cyber-body" style="overflow-y:auto;">
    """, unsafe_allow_html=True)

    sentiments = [
        {"label": "USD Sentiment", "val": "BULLISH", "cls": "bullish", "conf": 78},
        {"label": "EUR Sentiment", "val": "BEARISH", "cls": "bearish", "conf": 64}
    ]
    for item in sentiments:
        st.markdown(f"""
        <div class="cyber-metric">
            <div class="cyber-metric-label">{item['label']}</div>
            <div class="cyber-metric-value {item['cls']}">{item['val']}</div>
            <div class="cyber-metric-conf">Conf: {item['conf']}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="cyber-divider"></div>', unsafe_allow_html=True)

    analyses = [
        {"title": "US CPI Update", "text": "USD menguat akibat inflasi tinggi. RSI DXY kokoh.", "tags": [("SELL EURUSD", "sell")]},
        {"title": "XAUUSD Read", "text": "Tekanan jual teknikal dipicu yield obligasi AS.", "tags": [("BIAS SELL", "sell")]}
    ]
    for a in analyses:
        tags_html = ''.join([f'<span class="cyber-tag {cls}">{label}</span>' for label, cls in a['tags']])
        st.markdown(f"""
        <div class="analysis-card">
            <div class="analysis-title">{a['title']}</div>
            <div class="analysis-text">{a['text']}</div>
            <div style="margin-top:2px;">{tags_html}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# BAGIAN BAWAH (BARIS ACTIVE TRADES DAN SIGNAL MATRIX)
# ==============================================================================
st.markdown('<div class="bottom-section">', unsafe_allow_html=True)

# --- Active Trade Setups ---
st.markdown("""
<div class="cyber-panel">
    <div class="cyber-header"><span class="cyber-title">Active Trade Setups</span></div>
    <div class="cyber-body">
""", unsafe_allow_html=True)

setup_data = [
    {"pair": "EURUSD", "dir": "SELL", "dir_cls": "sell", "entry": "1.08420", "sl": "1.08900", "gradient": "#FF3D71"},
    {"pair": "USDJPY", "dir": "BUY", "dir_cls": "buy", "entry": "149.820", "sl": "149.200", "gradient": "#00FF9D"},
    {"pair": "XAUUSD", "dir": "SELL", "dir_cls": "sell", "entry": "2,014.50", "sl": "2,025.00", "gradient": "#FF3D71"},
    {"pair": "DXY", "dir": "LONG", "dir_cls": "buy", "entry": "105.840", "sl": "104.900", "gradient": "#00FF9D"}
]

st.markdown('<div class="trade-grid">', unsafe_allow_html=True)
for setup in setup_data:
    st.markdown(f"""
    <div style="background:#111D35; border:1px solid #162035; border-radius:6px; padding:6px; position:relative;">
        <div style="position:absolute; top:0; left:0; right:0; height:2px; background:{setup['gradient']};"></div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">
            <span style="font-family:'Share Tech Mono',monospace; font-size:10px; color:#C8D8F0;">{setup['pair']}</span>
            <span class="cyber-tag {setup['dir_cls']}">{setup['dir']}</span>
        </div>
        <div style="font-size:9px; color:#4B6A8A;">Entry: <span style="color:#C8D8F0; font-weight:700;">{setup['entry']}</span></div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div></div></div>', unsafe_allow_html=True)

# --- Signal Matrix & Watchlist ---
st.markdown("""
<div class="cyber-panel">
    <div class="cyber-header">
        <span class="cyber-title">SIGNAL MATRIX &amp; WATCHLIST (TradingView)</span>
    </div>
    <div class="cyber-body">
        <div style="font-family:'Share Tech Mono',monospace; font-size:9px; color:#00EEFF; padding: 2px 4px;">
            XAUUSD BUY | BTCUSD BUY | EURUSD SELL | GBPUSD SELL
        </div>
        <div style="font-family:'Share Tech Mono',monospace; font-size:7px; color:#4B6A8A; margin: 4px 0 2px 4px;">[WATCHLIST PRICES] - 3 tabs</div>
""", unsafe_allow_html=True)

watchlist_html = """
<div class="tradingview-widget-container" style="width:100%;">
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-symbols.js" async>
    {
    "colorTheme": "dark",
    "showChart": false,
    "locale": "id",
    "width": "100%",
    "height": "160",
    "tabs": [
        {"title": "Komoditas & DXY", "symbols": [{"s": "TVC:DXY"}] Gold, [{"s": "FX_IDC:XAUUSD"}]},
        {"title": "Forex", "symbols": [{"s": "FX:EURUSD"}, {"s": "FX:USDJPY"}]},
        {"title": "Crypto", "symbols": [{"s": "BINANCE:BTCUSDT"}]}
    ]
    }
    </script>
</div>
"""
components.html(watchlist_html, height=170)

st.markdown('</div></div></div>', unsafe_allow_html=True)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("""
<div style="text-align: center; padding: 4px; opacity: 0.5; width:100%;">
    <p style="font-family: 'Share Tech Mono', monospace; font-size: 8px; color: #4B6A8A; margin: 0;">
        AEROVULPIS | DYNAMIHATCH IDENTITY
    </p>
</div>
""", unsafe_allow_html=True)
