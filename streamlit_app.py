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
/* --- SCROLL HORIZONTAL HANYA UNTUK 3 KOLOM UTAMA --- */
.main-row-scroll {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    gap: 10px !important;
    padding: 5px 0 !important;
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
}
.main-row-scroll .scroll-col:nth-of-type(1) { min-width: 260px; }
.main-row-scroll .scroll-col:nth-of-type(2) { min-width: 380px; }
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
    padding: 8px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
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
    padding: 12px;
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
    padding: 10px 12px;
    margin-bottom: 8px;
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
    margin-top: 7px;
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
    margin: 8px 0;
}
.analysis-card {
    background: #111D35;
    border: 1px solid #162035;
    border-left: 2px solid #8B5CF6;
    border-radius: 7px;
    padding: 10px 12px;
    margin-bottom: 8px;
}
.analysis-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #8B5CF6;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 7px;
}
.analysis-text {
    font-size: 11px;
    line-height: 1.78;
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
    margin-bottom: 10px;
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
# 3 KOLOM UTAMA (BISA DIGESER KANAN-KIRI)
# ==============================================================================
st.markdown('<div class="main-row-scroll">', unsafe_allow_html=True)

# --- KOLOM 1: ECONOMIC CALENDAR (Tradays) ---
with st.container():
    st.markdown('<div class="scroll-col">', unsafe_allow_html=True)
    st.markdown("""
    <div class="cyber-panel">
        <div class="cyber-header">
            <span class="cyber-title">Economic Calendar</span>
            <span class="cyber-badge">Tradays</span>
        </div>
        <div class="cyber-body" style="padding: 0; height: 700px; overflow: hidden; border-radius: 0 0 10px 10px;">
    """, unsafe_allow_html=True)
    
    # Kalender Tradays (resmi dari MetaQuotes)
    calendar_html = """
    <iframe src="https://tradays.com" 
            width="100%" 
            height="100%" 
            frameborder="0" 
            scrolling="yes"
            style="border: none; background: #0C1425;">
    </iframe>
    """
    components.html(calendar_html, height=700)
    
    st.markdown("""
        </div>
        <div class="scan-wrap"><div class="scan-line" style="animation-delay: 0s;"></div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- KOLOM 2: DXY CHART + MT5 TERMINAL ---
with st.container():
    st.markdown('<div class="scroll-col">', unsafe_allow_html=True)
    
    # DXY Chart (TradingView)
    st.markdown("""
    <div class="cyber-panel">
        <div class="cyber-header">
            <span class="cyber-title">DXY & RSI Analysis</span>
            <span class="cyber-badge">TradingView</span>
        </div>
        <div class="cyber-body" style="padding: 0; height: 400px; overflow: hidden; border-radius: 0 0 10px 10px;">
    """, unsafe_allow_html=True)
    
    dxy_html = """
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
    """
    components.html(dxy_html, height=400)
    
    st.markdown("""
        </div>
        <div class="scan-wrap"><div class="scan-line" style="animation-delay: 3s;"></div></div>
    </div>
    """, unsafe_allow_html=True)
    
    # MT5 Web Terminal
    st.markdown("""
    <div class="cyber-panel" style="margin-top: 10px;">
        <div class="cyber-header">
            <span class="cyber-title">MT5 Execution Terminal</span>
            <span class="cyber-badge">Web Terminal</span>
        </div>
        <div class="cyber-body" style="padding: 0; height: 650px; overflow: hidden; border-radius: 0 0 10px 10px;">
    """, unsafe_allow_html=True)
    
    mt5_html = """
    <iframe src="https://metatraderweb.app/trade" 
            width="100%" 
            height="100%" 
            frameborder="0" 
            allowfullscreen="true" 
            scrolling="no"
            style="border: none; background: #0C1425;">
    </iframe>
    """
    components.html(mt5_html, height=650)
    
    st.markdown("""
        </div>
        <div class="scan-wrap"><div class="scan-line" style="animation-delay: 3s;"></div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- KOLOM 3: AI SIGNAL FEED ---
with st.container():
    st.markdown('<div class="scroll-col">', unsafe_allow_html=True)
    st.markdown("""
    <div class="cyber-panel">
        <div class="cyber-header">
            <span class="cyber-title">AI Signal Feed</span>
            <span class="cyber-badge">Contoh AI</span>
        </div>
        <div class="cyber-body" style="max-height: 700px; overflow-y: auto; padding: 12px;">
    """, unsafe_allow_html=True)
    
    # Sentimen
    for item in [
        {"label": "USD Sentiment", "val": "BULLISH", "cls": "bullish", "conf": 78},
        {"label": "EUR Sentiment", "val": "BEARISH", "cls": "bearish", "conf": 64},
        {"label": "XAU Sentiment", "val": "NEUTRAL-BEAR", "cls": "neutral", "conf": 51}
    ]:
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
        st.markdown(f"""
        <div class="analysis-card">
            <div class="analysis-title">{a['title']}</div>
            <div class="analysis-text">{a['text']}</div>
            <div style="margin-top: 8px; display: flex; gap: 5px; flex-wrap: wrap;">
                {''.join([f'<span class="cyber-tag {cls}">{label}</span>' for label, cls in a['tags']])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
        <div class="scan-wrap"><div class="scan-line" style="animation-delay: 6s;"></div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Tutup main-row-scroll

# ==============================================================================
# BAGIAN BAWAH (TIDAK IKUT SCROLL)
# ==============================================================================

# --- Trade Setups (4 kolom) ---
st.markdown("""
<div class="cyber-panel" style="margin-top: 10px;">
    <div class="cyber-header">
        <span class="cyber-title">Active Trade Setups</span>
        <span class="cyber-badge">Contoh Data — Prototype</span>
    </div>
    <div class="cyber-body" style="padding: 12px;">
""", unsafe_allow_html=True)

col_s1, col_s2, col_s3, col_s4 = st.columns(4)

setup_data = [
    {"pair": "EURUSD", "dir": "SELL", "dir_cls": "sell", "entry": "1.08420", "tp1": "1.07950", "tp2": "1.07500", "tp3": "1.06800", "sl": "1.08900", "gradient": "linear-gradient(90deg, #8B5CF6, #FF3D71)"},
    {"pair": "USDJPY", "dir": "BUY", "dir_cls": "buy", "entry": "149.820", "tp1": "150.500", "tp2": "151.200", "tp3": "152.000", "sl": "149.200", "gradient": "linear-gradient(90deg, #00EEFF, #00FF9D)"},
    {"pair": "XAUUSD", "dir": "SELL", "dir_cls": "sell", "entry": "2,014.50", "tp1": "2,000.00", "tp2": "1,990.00", "tp3": "1,975.00", "sl": "2,025.00", "gradient": "linear-gradient(90deg, #8B5CF6, #FF3D71)"},
    {"pair": "DXY", "dir": "LONG BIAS", "dir_cls": "buy", "entry": "105.840", "tp1": "106.500", "tp2": "107.200", "tp3": "108.000", "sl": "104.900", "gradient": "linear-gradient(90deg, #00EEFF, #00FF9D)"}
]

for idx, setup in enumerate(setup_data):
    with [col_s1, col_s2, col_s3, col_s4][idx]:
        st.markdown(f"""
        <div style="background: #111D35; border: 1px solid #162035; border-radius: 8px; padding: 10px; position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; background: {setup['gradient']};"></div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 9px;">
                <span style="font-family: 'Share Tech Mono', monospace; font-size: 13px; color: #C8D8F0; letter-spacing: 2px;">{setup['pair']}</span>
                <span style="font-family: 'Share Tech Mono', monospace; font-size: 8px; letter-spacing: 1px; padding: 2px 7px; border-radius: 3px; background: rgba({'0,255,157' if setup['dir_cls']=='buy' else '255,61,113'},0.12); color: {'#00FF9D' if setup['dir_cls']=='buy' else '#FF3D71'}; border: 1px solid rgba({'0,255,157' if setup['dir_cls']=='buy' else '255,61,113'},0.25);">{setup['dir']}</span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px;">
                <div style="grid-column: 1 / -1; background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                    <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">Entry</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #C8D8F0;">{setup['entry']}</div>
                </div>
                <div style="background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                    <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">TP 1</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #00FF9D;">{setup['tp1']}</div>
                </div>
                <div style="background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                    <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">TP 2</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #00FF9D;">{setup['tp2']}</div>
                </div>
                <div style="grid-column: 1 / -1; background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                    <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">Stop Loss</div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #FF3D71;">{setup['sl']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
    </div>
    <div class="scan-wrap"><div class="scan-line" style="animation-delay: 6s;"></div></div>
</div>
""", unsafe_allow_html=True)

# --- Signal Matrix + Watchlist (TradingView) ---
st.markdown("""
<div class="cyber-panel" style="margin-top: 10px;">
    <div class="cyber-header">
        <span class="cyber-title">Signal Matrix & Watchlist</span>
        <span class="cyber-badge">Live</span>
    </div>
    <div class="cyber-body" style="padding: 12px;">
""", unsafe_allow_html=True)

# Signal Matrix (4 kartu sinyal)
signal_data = [
    {"symbol": "XAUUSD", "direction": "BUY", "entry": "2,014.50", "sl": "2,000.00", "tp1": "2,025.00", "tp2": "2,035.00", "tp3": "2,050.00", "conf": 78},
    {"symbol": "BTCUSD", "direction": "BUY", "entry": "65,790.00", "sl": "64,500.00", "tp1": "66,800.00", "tp2": "67,500.00", "tp3": "68,900.00", "conf": 72},
    {"symbol": "EURUSD", "direction": "SELL", "entry": "1.08420", "sl": "1.08900", "tp1": "1.07950", "tp2": "1.07500", "tp3": "1.06800", "conf": 65},
    {"symbol": "GBPUSD", "direction": "SELL", "entry": "1.3430", "sl": "1.3490", "tp1": "1.3370", "tp2": "1.3310", "tp3": "1.3220", "conf": 60}
]

st.markdown("""
<div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; margin-bottom: 15px;">
""", unsafe_allow_html=True)

for sig in signal_data:
    dir_color = "#00FF9D" if sig['direction'] == "BUY" else "#FF3D71"
    dir_bg = "rgba(0,255,157,0.12)" if sig['direction'] == "BUY" else "rgba(255,61,113,0.12)"
    dir_border = "rgba(0,255,157,0.25)" if sig['direction'] == "BUY" else "rgba(255,61,113,0.25)"
    st.markdown(f"""
    <div style="background: #111D35; border: 1px solid #162035; border-radius: 8px; padding: 12px; position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; background: {dir_color};"></div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-family: 'Share Tech Mono', monospace; font-size: 14px; color: #00EEFF; letter-spacing: 2px;">{sig['symbol']}</span>
            <span style="font-family: 'Share Tech Mono', monospace; font-size: 9px; letter-spacing: 1px; padding: 2px 10px; border-radius: 3px; background: {dir_bg}; color: {dir_color}; border: 1px solid {dir_border};">{sig['direction']}</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 4px;">
            <div style="background: rgba(0,0,0,0.2); border-radius: 4px; padding: 4px; text-align: center;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 6px; color: #4B6A8A; letter-spacing: 1px; text-transform: uppercase;">Entry</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #C8D8F0;">{sig['entry']}</div>
            </div>
            <div style="background: rgba(0,0,0,0.2); border-radius: 4px; padding: 4px; text-align: center;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 6px; color: #4B6A8A; letter-spacing: 1px; text-transform: uppercase;">SL</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #FF3D71;">{sig['sl']}</div>
            </div>
            <div style="background: rgba(0,0,0,0.2); border-radius: 4px; padding: 4px; text-align: center;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 6px; color: #4B6A8A; letter-spacing: 1px; text-transform: uppercase;">TP1</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #00FF9D;">{sig['tp1']}</div>
            </div>
            <div style="background: rgba(0,0,0,0.2); border-radius: 4px; padding: 4px; text-align: center;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 6px; color: #4B6A8A; letter-spacing: 1px; text-transform: uppercase;">Conf</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #00EEFF;">{sig['conf']}%</div>
            </div>
        </div>
        <div style="margin-top: 6px; display: flex; gap: 3px; flex-wrap: wrap;">
            <span style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #4B6A8A;">TP2: {sig['tp2']}</span>
            <span style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #4B6A8A;">| TP3: {sig['tp3']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# --- Watchlist (TradingView Widget dengan Tab) ---
st.markdown("""
<div style="margin-top: 12px; border-top: 1px solid #162035; padding-top: 12px;">
    <div style="font-family: 'Share Tech Mono', monospace; font-size: 9px; color: #4B6A8A; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px;">
        [WATCHLIST PRICES]
    </div>
""", unsafe_allow_html=True)

watchlist_html = """
<!-- TradingView Widget BEGIN -->
<div class="tradingview-widget-container" style="width:100%;">
    <div class="tradingview-widget-container__widget" style="width:100%;"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-symbols.js" async>
    {
    "colorTheme": "dark",
    "dateRange": "12M",
    "showChart": false,
    "locale": "id",
    "width": "100%",
    "height": "350",
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
<!-- TradingView Widget END -->
"""
components.html(watchlist_html, height=380)

st.markdown("""
</div>
""", unsafe_allow_html=True)

st.markdown("""
    </div>
    <div class="scan-wrap"><div class="scan-line" style="animation-delay: 9s;"></div></div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("""
<div style="text-align: center; padding: 20px; margin-top: 10px; border-top: 1px solid #162035; opacity: 0.55;">
    <p style="font-family: 'Share Tech Mono', monospace; font-size: 11px; color: #4B6A8A; margin: 0; letter-spacing: 2px;">
        [PROTOTYPE] Aerovulpis Pro Terminal v0.1
    </p>
    <p style="font-family: 'Share Tech Mono', monospace; font-size: 8px; color: #243450; letter-spacing: 2px; margin-top: 4px;">
        AEROVULPIS | DYNAMIHATCH IDENTITY
    </p>
</div>
""", unsafe_allow_html=True)