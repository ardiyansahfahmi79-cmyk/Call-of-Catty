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
# CSS CYBERTECH
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

/* --- 3 KOLOM UTAMA --- */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    gap: 8px !important;
    padding: 5px 0 0 0 !important;
    height: auto !important;
    min-height: 600px !important;
    align-items: stretch !important;
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

/* --- Panel --- */
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
.cyber-panel-native .panel-body {
    flex: 1;
    overflow-y: auto;
    padding: 4px;
}
.cyber-panel-native .panel-header {
    background: rgba(0,0,0,0.28);
    border-bottom: 1px solid #162035;
    padding: 4px 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
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

/* --- Components --- */
.cyber-metric {
    background: #111D35;
    border: 1px solid #162035;
    border-radius: 6px;
    padding: 4px 6px;
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
.cyber-divider { height: 1px; background: #162035; margin: 4px 0; }

.analysis-card {
    background: #111D35;
    border: 1px solid #162035;
    border-left: 2px solid #8B5CF6;
    border-radius: 6px;
    padding: 4px 6px;
    margin-bottom: 4px;
}
.analysis-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 8px;
    color: #8B5CF6;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 2px;
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

/* --- Grids --- */
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
# TICKER
# ==============================================================================
ticker_html = """
<div class="tradingview-widget-container" style="margin-bottom: 4px;">
    <div class="tradingview-widget-container__widget"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-tickers.js" async>
    {
    "symbols": [
        {"proName": "FOREXCOM:SPXUSD", "title": "S&P 500"},
        {"proName": "FOREXCOM:NSXUSD", "title": "US 100 Cash CFD"},
        {"proName": "FX_IDC:EURUSD", "title": "EUR/USD"},
        {"proName": "BITSTAMP:BTCUSD", "title": "Bitcoin"},
        {"proName": "BITSTAMP:ETHUSD", "title": "Ethereum"},
        {"proName": "OANDA:XAUUSD", "title": "XAUUSD"},
        {"proName": "TVC:DXY", "title": "DXY"},
        {"proName": "IDX:COMPOSITE", "title": "IHSG"},
        {"proName": "OANDA:USDJPY", "title": "USD/JPY"}
    ],
    "colorTheme": "dark",
    "locale": "id",
    "isTransparent": true,
    "showSymbolLogo": true
    }
    </script>
</div>
"""
components.html(ticker_html, height=40)

# ==============================================================================
# 3 KOLOM UTAMA
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
        <div style="flex:1; min-height:0;">
            <iframe src="https://www.tradays.com/en/economic-calendar/widget?mode=2&colorTheme=dark" 
                    style="width:100%; height:100%; border:none; background:#0C1425;" 
                    frameborder="0" scrolling="auto">
            </iframe>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- KOLOM 2: DXY + CHART RSI ---
with col2:
    # DXY Symbol Overview
    dxy_html = """
    <div class="tradingview-widget-container" style="height:180px;">
        <div class="tradingview-widget-container__widget" style="height:100%;"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-symbol-overview.js" async>
        {
        "lineWidth": 2,
        "lineType": 0,
        "chartType": "area",
        "fontColor": "rgb(106, 109, 120)",
        "gridLineColor": "rgba(242, 242, 242, 0.06)",
        "volumeUpColor": "rgba(34, 171, 148, 0.5)",
        "volumeDownColor": "rgba(247, 82, 95, 0.5)",
        "backgroundColor": "#0F0F0F",
        "widgetFontColor": "#DBDBDB",
        "upColor": "#22ab94",
        "downColor": "#f7525f",
        "borderUpColor": "#22ab94",
        "borderDownColor": "#f7525f",
        "wickUpColor": "#22ab94",
        "wickDownColor": "#f7525f",
        "colorTheme": "dark",
        "isTransparent": false,
        "locale": "en",
        "chartOnly": false,
        "scalePosition": "right",
        "scaleMode": "Normal",
        "valuesTracking": "1",
        "changeMode": "price-and-percent",
        "symbols": [["INDEX:DXY|1D"]],
        "dateRanges": ["1d|1","1m|30","3m|60","12m|1D","60m|1W","all|1M"],
        "fontSize": "10",
        "headerFontSize": "medium",
        "autosize": true,
        "width": "100%",
        "height": "100%",
        "noTimeScale": false,
        "hideDateRanges": false,
        "hideMarketStatus": false,
        "hideSymbolLogo": false
        }
        </script>
    </div>
    """
    # Chart with RSI
    chart_rsi_html = """
    <div class="tradingview-widget-container" style="height:430px; margin-top:4px;">
        <div id="tv_chart_rsi" style="height:100%;width:100%;"></div>
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
            "container_id": "tv_chart_rsi",
            "studies": ["RSI@tv-basicstudies"],
            "backgroundColor": "rgba(7,12,24,1)",
            "gridColor": "rgba(0,238,255,0.04)"
        });
        </script>
    </div>
    """
    col2_content = f"""
    <div class="cyber-panel-native" style="height:620px;">
        <div class="panel-header">
            <span class="panel-title">DXY</span>
            <span class="panel-badge">TradingView</span>
        </div>
        <div style="flex:1; display:flex; flex-direction:column; min-height:0;">
            <div style="flex:0 0 180px;">{dxy_html}</div>
            <div style="flex:1; min-height:0;">{chart_rsi_html}</div>
        </div>
    </div>
    """
    components.html(col2_content, height=620)

# --- KOLOM 3: AI SIGNAL FEED + INPUT + HEATMAP ---
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
    <div style="font-family:'Share Tech Mono',monospace; font-size:8px; color:#4B6A8A; background:rgba(0,238,255,0.05); border-left:2px solid #00EEFF; padding:4px 6px; border-radius:3px;">
        [INFO] Masukkan pair atau berita untuk analisis AI (contoh: EURUSD, CPI, FOMC)
    </div>
    """, unsafe_allow_html=True)

    # Input & Tombol Kirim
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        user_input = st.text_input("", placeholder="EURUSD, CPI, FOMC...", key="ai_input", label_visibility="collapsed")
    with col_btn:
        send_clicked = st.button("Kirim", key="ai_send", use_container_width=True)

    # Hasil AI (contoh statis)
    if send_clicked and user_input:
        st.info(f"Analisis untuk: {user_input} (contoh AI)")
    else:
        st.caption("Contoh hasil AI:")

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
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="cyber-divider"></div>', unsafe_allow_html=True)

    # Analisis berita
    analyses = [
        {"title": "US CPI Data Release", "text": "Inflasi AS lebih tinggi dari konsensus. USD menguat. RSI DXY di zona 58, momentum bullish.", "tags": [("SELL EURUSD", "sell"), ("BUY USDJPY", "buy")]},
        {"title": "XAUUSD Technical Read", "text": "Tekanan jual XAU dipicu yield AS. Level 1985-1990 zona support kritis. Pantau data ADP.", "tags": [("WATCH 1985", "watch"), ("BIAS SELL", "sell")]},
        {"title": "DXY Momentum Breakout", "text": "Breakout dari descending channel terkonfirmasi. Target resistance berikutnya di 107.20.", "tags": [("MOMENTUM BULL", "buy"), ("TARGET 107.20", "watch")]}
    ]
    for a in analyses:
        tags_html = ''.join([f'<span class="cyber-tag {cls}">{label}</span>' for label, cls in a['tags']])
        st.markdown(f"""
        <div class="analysis-card">
            <div class="analysis-title">{a['title']}</div>
            <div class="analysis-text">{a['text']}</div>
            <div style="margin-top:2px; display:flex; gap:3px; flex-wrap:wrap;">{tags_html}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="cyber-divider"></div>', unsafe_allow_html=True)

    # HEATMAP
    heatmap_html = """
    <div class="tradingview-widget-container" style="width:100%;">
        <div class="tradingview-widget-container__widget"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-forex-heat-map.js" async>
        {
        "colorTheme": "dark",
        "isTransparent": true,
        "locale": "id",
        "currencies": ["EUR","USD","JPY","GBP","CHF","AUD","CAD","NZD","CNY"],
        "width": "100%",
        "height": 250
        }
        </script>
    </div>
    """
    components.html(heatmap_html, height=260)

    st.markdown("</div></div>", unsafe_allow_html=True)

# ==============================================================================
# BAGIAN BAWAH (TIDAK IKUT SCROLL)
# ==============================================================================

# --- ACTIVE TRADE SETUPS (4 KARTU) ---
st.markdown("""
<div class="cyber-panel-native">
    <div class="panel-header">
        <span class="panel-title">Active Trade Setups</span>
        <span class="panel-badge">Prototype</span>
    </div>
    <div style="padding: 4px;">
""", unsafe_allow_html=True)

setup_data = [
    {"pair": "EURUSD", "dir": "SELL", "dir_cls": "sell", "entry": "1.08420", "tp1": "1.07950", "tp2": "1.07500", "tp3": "1.06800", "sl": "1.08900", "gradient": "#FF3D71"},
    {"pair": "USDJPY", "dir": "BUY", "dir_cls": "buy", "entry": "149.820", "tp1": "150.500", "tp2": "151.200", "tp3": "152.000", "sl": "149.200", "gradient": "#00FF9D"},
    {"pair": "XAUUSD", "dir": "SELL", "dir_cls": "sell", "entry": "2,014.50", "tp1": "2,000.00", "tp2": "1,990.00", "tp3": "1,975.00", "sl": "2,025.00", "gradient": "#FF3D71"},
    {"pair": "DXY", "dir": "LONG BIAS", "dir_cls": "buy", "entry": "105.840", "tp1": "106.500", "tp2": "107.200", "tp3": "108.000", "sl": "104.900", "gradient": "#00FF9D"}
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
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:2px; font-size:8px;">
            <div><span style="color:#4B6A8A;">Entry</span> <span style="color:#C8D8F0;">{setup['entry']}</span></div>
            <div><span style="color:#4B6A8A;">TP1</span> <span style="color:#00FF9D;">{setup['tp1']}</span></div>
            <div><span style="color:#4B6A8A;">SL</span> <span style="color:#FF3D71;">{setup['sl']}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div></div></div>', unsafe_allow_html=True)

# --- SIGNAL MATRIX (4 KARTU SINYAL) ---
st.markdown("""
<div class="cyber-panel-native">
    <div class="panel-header">
        <span class="panel-title">Signal Matrix</span>
        <span class="panel-badge">Live</span>
    </div>
    <div style="padding: 4px;">
""", unsafe_allow_html=True)

signal_data = [
    {"symbol": "XAUUSD", "dir": "BUY", "entry": "2,014.50", "tp1": "2,025.00", "conf": 78},
    {"symbol": "BTCUSD", "dir": "BUY", "entry": "65,790.00", "tp1": "66,800.00", "conf": 72},
    {"symbol": "EURUSD", "dir": "SELL", "entry": "1.08420", "tp1": "1.07950", "conf": 65},
    {"symbol": "GBPUSD", "dir": "SELL", "entry": "1.3430", "tp1": "1.3370", "conf": 60}
]

st.markdown('<div class="signal-grid">', unsafe_allow_html=True)
for sig in signal_data:
    cls = "buy" if sig['dir'] == "BUY" else "sell"
    color = "#00FF9D" if sig['dir'] == "BUY" else "#FF3D71"
    st.markdown(f"""
    <div style="background:#111D35; border:1px solid #162035; border-radius:4px; padding:4px; position:relative; overflow:hidden;">
        <div style="position:absolute; top:0; left:0; right:0; height:2px; background:{color};"></div>
        <div style="display:flex; justify-content:space-between; font-family:'Share Tech Mono',monospace; font-size:9px;">
            <span style="color:#00EEFF;">{sig['symbol']}</span>
            <span class="cyber-tag {cls}">{sig['dir']}</span>
        </div>
        <div style="display:flex; gap:6px; font-size:8px; color:#4B6A8A; margin-top:2px;">
            <span>Entry <span style="color:#C8D8F0;">{sig['entry']}</span></span>
            <span>TP1 <span style="color:#00FF9D;">{sig['tp1']}</span></span>
            <span>Conf <span style="color:#00EEFF;">{sig['conf']}%</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div></div></div>', unsafe_allow_html=True)

# --- WATCHLIST (TradingView) ---
st.markdown("""
<div class="cyber-panel-native">
    <div class="panel-header">
        <span class="panel-title">Watchlist</span>
        <span class="panel-badge">TradingView</span>
    </div>
    <div style="padding: 4px;">
""", unsafe_allow_html=True)

watchlist_html = """
<div class="tradingview-widget-container" style="width:100%;">
    <div class="tradingview-widget-container__widget"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-symbols.js" async>
    {
    "colorTheme": "dark",
    "showChart": false,
    "locale": "id",
    "width": "100%",
    "height": "160",
    "tabs": [
        {"title": "Komoditas", "symbols": [{"s": "TVC:DXY"}, {"s": "FX_IDC:XAUUSD"}]},
        {"title": "Forex", "symbols": [{"s": "FX:EURUSD"}, {"s": "FX:USDJPY"}]},
        {"title": "Crypto", "symbols": [{"s": "BINANCE:BTCUSDT"}]}
    ]
    }
    </script>
</div>
"""
components.html(watchlist_html, height=170)

st.markdown("</div></div>", unsafe_allow_html=True)

# --- MARKET NEWS (TradingView Timeline) ---
st.markdown("""
<div class="cyber-panel-native">
    <div class="panel-header">
        <span class="panel-title">Market News</span>
        <span class="panel-badge">TradingView</span>
    </div>
    <div style="padding: 4px; height: 380px; overflow: hidden;">
""", unsafe_allow_html=True)

news_html = """
<div class="tradingview-widget-container" style="width:100%; height:100%;">
    <div class="tradingview-widget-container__widget" style="height:100%;"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-timeline.js" async>
    {
    "displayMode": "regular",
    "feedMode": "all_symbols",
    "colorTheme": "dark",
    "isTransparent": true,
    "locale": "id",
    "width": "100%",
    "height": "100%"
    }
    </script>
</div>
"""
components.html(news_html, height=380)

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