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
# CSS CYBERTECH (tanpa emoji)
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
body { overflow: hidden; }
.block-container { padding-top: 0 !important; padding-bottom: 0 !important; }

/* --- 3 KOLOM SCROLL HORIZONTAL --- */
.main-row-scroll {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    gap: 10px !important;
    padding: 5px 0 !important;
    height: calc(100vh - 58px - 10px) !important;
    scrollbar-width: thin;
    scrollbar-color: #162035 transparent;
}
.main-row-scroll::-webkit-scrollbar {
    height: 4px;
}
.main-row-scroll::-webkit-scrollbar-track {
    background: transparent;
}
.main-row-scroll::-webkit-scrollbar-thumb {
    background: #162035;
    border-radius: 2px;
}
.main-row-scroll .scroll-col {
    min-width: 280px !important;
    flex-shrink: 0 !important;
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}
.main-row-scroll .scroll-col:nth-of-type(1) { min-width: 280px; }
.main-row-scroll .scroll-col:nth-of-type(2) { min-width: 420px; }
.main-row-scroll .scroll-col:nth-of-type(3) { min-width: 280px; }

/* --- PANEL --- */
.cyber-panel {
    background: #0C1425;
    border: 1px solid #162035;
    border-radius: 10px;
    padding: 0;
    margin-bottom: 10px;
    position: relative;
    overflow: hidden;
    flex-shrink: 0;
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
    padding: 6px 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
}
.cyber-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #00EEFF;
    letter-spacing: 2.5px;
    text-transform: uppercase;
}
.cyber-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 8px;
    color: #243450;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.cyber-body {
    padding: 6px;
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
.cyber-metric {
    background: #111D35;
    border: 1px solid #162035;
    border-radius: 7px;
    padding: 8px 10px;
    margin-bottom: 6px;
}
.cyber-metric-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 8px;
    color: #4B6A8A;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.cyber-metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 16px;
    font-weight: 700;
}
.cyber-metric-value.bullish { color: #00FF9D; }
.cyber-metric-value.bearish { color: #FF3D71; }
.cyber-metric-value.neutral { color: #00EEFF; }
.cyber-metric-conf {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #4B6A8A;
}
.cyber-bar {
    margin-top: 5px;
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
    margin: 6px 0;
}
.analysis-card {
    background: #111D35;
    border: 1px solid #162035;
    border-left: 2px solid #8B5CF6;
    border-radius: 7px;
    padding: 8px 10px;
    margin-bottom: 6px;
}
.analysis-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #8B5CF6;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.analysis-text {
    font-size: 11px;
    line-height: 1.5;
    color: #C8D8F0;
}
.cyber-tag {
    font-family: 'Share Tech Mono', monospace;
    font-size: 8px;
    letter-spacing: 1px;
    padding: 2px 7px;
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
.cyber-tag.neutral {
    background: rgba(0,238,255,0.10);
    color: #00EEFF;
    border: 1px solid rgba(0,238,255,0.22);
}
.cyber-tag.watch {
    background: rgba(139,92,246,0.10);
    color: #8B5CF6;
    border: 1px solid rgba(139,92,246,0.25);
}
.mt5-fallback {
    position: absolute;
    bottom: 10px;
    right: 10px;
    z-index: 100;
    background: rgba(0,0,0,0.7);
    padding: 4px 10px;
    border-radius: 4px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 8px;
    color: #4B6A8A;
}
.mt5-fallback a {
    color: #00EEFF;
    text-decoration: none;
}
.mt5-fallback a:hover {
    text-decoration: underline;
}
.trade-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 10px;
    padding: 6px;
}
.signal-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 10px;
    padding: 6px;
}
.signal-card {
    background: #111D35;
    border: 1px solid #162035;
    border-radius: 8px;
    padding: 10px;
    position: relative;
    overflow: hidden;
}
.signal-card .signal-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}
.signal-card .signal-symbol {
    font-family: 'Share Tech Mono', monospace;
    font-size: 14px;
    color: #00EEFF;
    letter-spacing: 2px;
}
.signal-card .signal-dir {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    letter-spacing: 1px;
    padding: 2px 10px;
    border-radius: 3px;
}
.signal-dir.buy {
    background: rgba(0,255,157,0.12);
    color: #00FF9D;
    border: 1px solid rgba(0,255,157,0.25);
}
.signal-dir.sell {
    background: rgba(255,61,113,0.12);
    color: #FF3D71;
    border: 1px solid rgba(255,61,113,0.25);
}
.signal-values {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 4px;
}
.signal-values .sv-item {
    background: rgba(0,0,0,0.2);
    border-radius: 4px;
    padding: 4px;
    text-align: center;
}
.sv-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 6px;
    color: #4B6A8A;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.sv-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: #C8D8F0;
}
.sv-value.green { color: #00FF9D; }
.sv-value.red { color: #FF3D71; }
.sv-value.cyan { color: #00EEFF; }
.signal-tp-extra {
    margin-top: 4px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #4B6A8A;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# HEADER
# ==============================================================================
st.markdown("""
<div style="
    height: 58px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    background: rgba(7,12,24,0.97);
    border-bottom: 1px solid #162035;
    flex-shrink: 0;
">
    <div style="display: flex; align-items: center; gap: 12px;">
        <div style="
            width: 36px; height: 36px;
            background: linear-gradient(135deg, #00EEFF, #8B5CF6);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Share Tech Mono', monospace;
            font-size: 13px;
            font-weight: 700;
            color: #fff;
            letter-spacing: 0.5px;
            box-shadow: 0 0 18px rgba(0,238,255,0.25);
        ">AV</div>
        <div>
            <div style="font-family: 'Share Tech Mono', monospace; font-size: 17px; color: #00EEFF; letter-spacing: 3px; text-shadow: 0 0 20px rgba(0,238,255,0.4);">
                AEROVULPIS PRO
            </div>
            <div style="font-size: 9px; color: #4B6A8A; letter-spacing: 2.5px; text-transform: uppercase; margin-top: 2px;">
                Intelligent Trading Terminal | Prototype v0.1
            </div>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 16px;">
        <div style="display: flex; align-items: center; gap: 7px; font-family: 'Share Tech Mono', monospace; font-size: 10px; color: #00FF9D; letter-spacing: 2px;">
            <div style="width: 7px; height: 7px; background: #00FF9D; border-radius: 50%; box-shadow: 0 0 8px #00FF9D; animation: blink 2s ease-in-out infinite;"></div>
            LIVE FEED
        </div>
        <div style="font-family: 'Share Tech Mono', monospace; font-size: 10px; color: #00EEFF; background: rgba(0,238,255,0.10); border: 1px solid rgba(0,238,255,0.22); padding: 3px 11px; border-radius: 4px; letter-spacing: 2px;">
            LONDON / NY OVERLAP
        </div>
    </div>
</div>
<style>
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.25; }
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3 KOLOM UTAMA (SCROLL HORIZONTAL)
# ==============================================================================
st.markdown('<div class="main-row-scroll">', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# KOLOM 1: ECONOMIC CALENDAR (Tradays)
# ------------------------------------------------------------------------------
st.markdown("""
<div class="scroll-col">
    <div class="cyber-panel" style="flex:1; display:flex; flex-direction:column;">
        <div class="cyber-header">
            <span class="cyber-title">Economic Calendar</span>
            <span class="cyber-badge">Tradays</span>
        </div>
        <div class="cyber-body" style="flex:1; padding:0; min-height:0;">
            <iframe src="https://tradays.com" 
                    style="width:100%; height:100%; border:none; background:#0C1425;"
                    frameborder="0" scrolling="yes">
            </iframe>
        </div>
        <div class="scan-wrap"><div class="scan-line" style="animation-delay:0s;"></div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# KOLOM 2: DXY CHART + MT5 TERMINAL
# ------------------------------------------------------------------------------
st.markdown("""
<div class="scroll-col">
    <!-- DXY Chart -->
    <div class="cyber-panel" style="flex:1; display:flex; flex-direction:column; min-height:300px;">
        <div class="cyber-header">
            <span class="cyber-title">DXY & RSI Analysis</span>
            <span class="cyber-badge">TradingView</span>
        </div>
        <div class="cyber-body" style="flex:1; padding:0; min-height:0;">
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
                    "hide_top_toolbar": false,
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
        <div class="scan-wrap"><div class="scan-line" style="animation-delay:3s;"></div></div>
    </div>
    
    <!-- MT5 Terminal -->
    <div class="cyber-panel" style="flex:1.5; display:flex; flex-direction:column; min-height:350px; margin-top:8px;">
        <div class="cyber-header">
            <span class="cyber-title">MT5 Execution Terminal</span>
            <span class="cyber-badge">Web Terminal</span>
        </div>
        <div class="cyber-body" style="flex:1; padding:0; min-height:0; position:relative;">
            <iframe src="https://metatraderweb.app/trade" 
                    style="width:100%; height:100%; border:none; background:#0C1425;"
                    frameborder="0" allowfullscreen="true" scrolling="no">
            </iframe>
            <div class="mt5-fallback">
                [MT5 Web Terminal] Jika tidak muncul, <a href="https://metatraderweb.app/trade" target="_blank">buka di tab baru</a>
            </div>
        </div>
        <div class="scan-wrap"><div class="scan-line" style="animation-delay:3s;"></div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# KOLOM 3: AI SIGNAL FEED
# ------------------------------------------------------------------------------
st.markdown("""
<div class="scroll-col">
    <div class="cyber-panel" style="flex:1; display:flex; flex-direction:column;">
        <div class="cyber-header">
            <span class="cyber-title">AI Signal Feed</span>
            <span class="cyber-badge">Contoh AI</span>
        </div>
        <div class="cyber-body" style="flex:1; overflow-y:auto; padding:8px;">
""", unsafe_allow_html=True)

# Sentimen
sentiments = [
    {"label": "USD Sentiment", "val": "BULLISH", "cls": "bullish", "conf": 78},
    {"label": "EUR Sentiment", "val": "BEARISH", "cls": "bearish", "conf": 64},
    {"label": "XAU Sentiment", "val": "NEUTRAL-BEAR", "cls": "neutral", "conf": 51}
]
for item in sentiments:
    st.markdown(f"""
    <div class="cyber-metric">
        <div class="cyber-metric-label">{item['label']}</div>
        <div class="cyber-metric-value {item['cls']}">{item['val']}</div>
        <div class="cyber-metric-conf">Confidence: {item['conf']}%</div>
        <div class="cyber-bar"><div class="cyber-bar-fill {item['cls']}" style="width:{item['conf']}%;"></div></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="cyber-divider"></div>', unsafe_allow_html=True)

# Analisis berita
analyses = [
    {"title": "US CPI Data Release", "text": "Inflasi AS tercatat lebih tinggi dari konsensus. Penguatan USD terjadi secara instan. RSI DXY di zona 58, momentum bullish masih solid.", "tags": [("SELL EURUSD", "sell"), ("BUY USDJPY", "buy")]},
    {"title": "XAUUSD Technical Read", "text": "Tekanan jual XAU dipicu penguatan yield obligasi AS. Level 1985-1990 zona support kritis. Pantau data ADP untuk konfirmasi arah selanjutnya.", "tags": [("WATCH 1985", "watch"), ("BIAS SELL", "sell")]},
    {"title": "DXY Momentum Breakout", "text": "Breakout dari descending channel mingguan telah terkonfirmasi. Target resistance berikutnya di 107.20. RSI H4 belum overbought.", "tags": [("MOMENTUM BULL", "buy"), ("TARGET 107.20", "watch")]}
]
for a in analyses:
    tags_html = ''.join([f'<span class="cyber-tag {cls}">{label}</span>' for label, cls in a['tags']])
    st.markdown(f"""
    <div class="analysis-card">
        <div class="analysis-title">{a['title']}</div>
        <div class="analysis-text">{a['text']}</div>
        <div style="margin-top: 6px; display: flex; gap: 4px; flex-wrap: wrap;">
            {tags_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
        </div>
        <div class="scan-wrap"><div class="scan-line" style="animation-delay:6s;"></div></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Tutup main-row-scroll

# ==============================================================================
# BAGIAN BAWAH (TIDAK IKUT SCROLL)
# ==============================================================================

# ------------------------------------------------------------------------------
# Trade Setups
# ------------------------------------------------------------------------------
st.markdown("""
<div class="cyber-panel" style="margin-top: 6px;">
    <div class="cyber-header">
        <span class="cyber-title">Active Trade Setups</span>
        <span class="cyber-badge">Contoh Data — Prototype</span>
    </div>
    <div class="cyber-body" style="padding:6px;">
""", unsafe_allow_html=True)

setup_data = [
    {"pair": "EURUSD", "dir": "SELL", "dir_cls": "sell", "entry": "1.08420", "tp1": "1.07950", "tp2": "1.07500", "tp3": "1.06800", "sl": "1.08900", "gradient": "linear-gradient(90deg, #8B5CF6, #FF3D71)"},
    {"pair": "USDJPY", "dir": "BUY", "dir_cls": "buy", "entry": "149.820", "tp1": "150.500", "tp2": "151.200", "tp3": "152.000", "sl": "149.200", "gradient": "linear-gradient(90deg, #00EEFF, #00FF9D)"},
    {"pair": "XAUUSD", "dir": "SELL", "dir_cls": "sell", "entry": "2,014.50", "tp1": "2,000.00", "tp2": "1,990.00", "tp3": "1,975.00", "sl": "2,025.00", "gradient": "linear-gradient(90deg, #8B5CF6, #FF3D71)"},
    {"pair": "DXY", "dir": "LONG BIAS", "dir_cls": "buy", "entry": "105.840", "tp1": "106.500", "tp2": "107.200", "tp3": "108.000", "sl": "104.900", "gradient": "linear-gradient(90deg, #00EEFF, #00FF9D)"}
]

st.markdown('<div class="trade-grid">', unsafe_allow_html=True)
for setup in setup_data:
    st.markdown(f"""
    <div style="background:#111D35; border:1px solid #162035; border-radius:8px; padding:8px; position:relative; overflow:hidden;">
        <div style="position:absolute; top:0; left:0; right:0; height:2px; background:{setup['gradient']};"></div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="font-family:'Share Tech Mono',monospace; font-size:12px; color:#C8D8F0; letter-spacing:1px;">{setup['pair']}</span>
            <span style="font-family:'Share Tech Mono',monospace; font-size:8px; letter-spacing:1px; padding:2px 7px; border-radius:3px; background:rgba({'0,255,157' if setup['dir_cls']=='buy' else '255,61,113'},0.12); color:{'#00FF9D' if setup['dir_cls']=='buy' else '#FF3D71'}; border:1px solid rgba({'0,255,157' if setup['dir_cls']=='buy' else '255,61,113'},0.25);">{setup['dir']}</span>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:4px; font-size:10px;">
            <div style="grid-column:1/-1; background:rgba(0,0,0,0.2); border-radius:4px; padding:3px 5px; display:flex; justify-content:space-between;">
                <span style="color:#4B6A8A;">Entry</span>
                <span style="color:#C8D8F0; font-weight:700;">{setup['entry']}</span>
            </div>
            <div style="background:rgba(0,0,0,0.2); border-radius:4px; padding:3px 5px; display:flex; justify-content:space-between;">
                <span style="color:#4B6A8A;">TP1</span>
                <span style="color:#00FF9D; font-weight:700;">{setup['tp1']}</span>
            </div>
            <div style="background:rgba(0,0,0,0.2); border-radius:4px; padding:3px 5px; display:flex; justify-content:space-between;">
                <span style="color:#4B6A8A;">TP2</span>
                <span style="color:#00FF9D; font-weight:700;">{setup['tp2']}</span>
            </div>
            <div style="grid-column:1/-1; background:rgba(0,0,0,0.2); border-radius:4px; padding:3px 5px; display:flex; justify-content:space-between;">
                <span style="color:#4B6A8A;">TP3</span>
                <span style="color:#00FF9D; font-weight:700;">{setup['tp3']}</span>
            </div>
            <div style="grid-column:1/-1; background:rgba(0,0,0,0.2); border-radius:4px; padding:3px 5px; display:flex; justify-content:space-between;">
                <span style="color:#4B6A8A;">Stop Loss</span>
                <span style="color:#FF3D71; font-weight:700;">{setup['sl']}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
    </div>
    <div class="scan-wrap"><div class="scan-line" style="animation-delay:6s;"></div></div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# Signal Matrix + Watchlist
# ------------------------------------------------------------------------------
st.markdown("""
<div class="cyber-panel" style="margin-top:6px;">
    <div class="cyber-header">
        <span class="cyber-title">Signal Matrix &amp; Watchlist</span>
        <span class="cyber-badge">Live</span>
    </div>
    <div class="cyber-body" style="padding:6px;">
""", unsafe_allow_html=True)

# Signal Matrix
signal_data = [
    {"symbol": "XAUUSD", "direction": "BUY", "entry": "2,014.50", "sl": "2,000.00", "tp1": "2,025.00", "tp2": "2,035.00", "tp3": "2,050.00", "conf": 78},
    {"symbol": "BTCUSD", "direction": "BUY", "entry": "65,790.00", "sl": "64,500.00", "tp1": "66,800.00", "tp2": "67,500.00", "tp3": "68,900.00", "conf": 72},
    {"symbol": "EURUSD", "direction": "SELL", "entry": "1.08420", "sl": "1.08900", "tp1": "1.07950", "tp2": "1.07500", "tp3": "1.06800", "conf": 65},
    {"symbol": "GBPUSD", "direction": "SELL", "entry": "1.3430", "sl": "1.3490", "tp1": "1.3370", "tp2": "1.3310", "tp3": "1.3220", "conf": 60}
]

st.markdown('<div class="signal-grid">', unsafe_allow_html=True)
for sig in signal_data:
    dir_class = "buy" if sig['direction'] == "BUY" else "sell"
    dir_color = "#00FF9D" if sig['direction'] == "BUY" else "#FF3D71"
    st.markdown(f"""
    <div class="signal-card">
        <div style="position:absolute; top:0; left:0; right:0; height:2px; background:{dir_color};"></div>
        <div class="signal-top">
            <span class="signal-symbol">{sig['symbol']}</span>
            <span class="signal-dir {dir_class}">{sig['direction']}</span>
        </div>
        <div class="signal-values">
            <div class="sv-item"><div class="sv-label">Entry</div><div class="sv-value">{sig['entry']}</div></div>
            <div class="sv-item"><div class="sv-label">SL</div><div class="sv-value red">{sig['sl']}</div></div>
            <div class="sv-item"><div class="sv-label">TP1</div><div class="sv-value green">{sig['tp1']}</div></div>
            <div class="sv-item"><div class="sv-label">Conf</div><div class="sv-value cyan">{sig['conf']}%</div></div>
        </div>
        <div class="signal-tp-extra">
            <span>TP2: <span style="color:#00FF9D;">{sig['tp2']}</span></span>
            <span>| TP3: <span style="color:#00FF9D;">{sig['tp3']}</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Watchlist (TradingView)
st.markdown("""
<div style="margin-top:10px; border-top:1px solid #162035; padding-top:10px;">
    <div style="font-family:'Share Tech Mono',monospace; font-size:9px; color:#4B6A8A; letter-spacing:1px; text-transform:uppercase; margin-bottom:6px;">
        [WATCHLIST PRICES]
    </div>
""", unsafe_allow_html=True)

watchlist_html = """
<div class="tradingview-widget-container" style="width:100%;">
    <div class="tradingview-widget-container__widget" style="width:100%;"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-symbols.js" async>
    {
    "colorTheme": "dark",
    "dateRange": "12M",
    "showChart": false,
    "locale": "id",
    "width": "100%",
    "height": "250",
    "tabs": [
        {
            "title": "Komoditas & DXY",
            "symbols": [
                {"s": "TVC:DXY", "d": "Indeks Dolar"},
                {"s": "FX_IDC:XAUUSD", "d": "Emas (XAUUSD)"},
                {"s": "FX_IDC:XAGUSD", "d": "Perak (XAGUSD)"}
            ]
        },
        {
            "title": "Forex",
            "symbols": [
                {"s": "FX:EURUSD", "d": "EUR/USD"},
                {"s": "FX:GBPUSD", "d": "GBP/USD"},
                {"s": "FX:USDJPY", "d": "USD/JPY"},
                {"s": "FX:AUDUSD", "d": "AUD/USD"}
            ]
        },
        {
            "title": "Crypto",
            "symbols": [
                {"s": "BINANCE:BTCUSDT", "d": "Bitcoin (BTC)"},
                {"s": "BINANCE:ETHUSDT", "d": "Ethereum (ETH)"},
                {"s": "BINANCE:SOLUSDT", "d": "Solana (SOL)"}
            ]
        }
    ]
    }
    </script>
</div>
"""
components.html(watchlist_html, height=280)

st.markdown("""
</div>
""", unsafe_allow_html=True)

st.markdown("""
    </div>
    <div class="scan-wrap"><div class="scan-line" style="animation-delay:9s;"></div></div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("""
<div style="text-align: center; padding: 12px; margin-top: 6px; border-top: 1px solid #162035; opacity: 0.55; flex-shrink:0;">
    <p style="font-family: 'Share Tech Mono', monospace; font-size: 11px; color: #4B6A8A; margin: 0; letter-spacing: 2px;">
        [PROTOTYPE] Aerovulpis Pro Terminal v0.1
    </p>
    <p style="font-family: 'Share Tech Mono', monospace; font-size: 8px; color: #243450; letter-spacing: 2px; margin-top: 4px;">
        AEROVULPIS | DYNAMIHATCH IDENTITY
    </p>
</div>
""", unsafe_allow_html=True)