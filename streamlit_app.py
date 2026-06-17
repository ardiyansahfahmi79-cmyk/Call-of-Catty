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
# CSS CYBERTECH - CORE UI ARCHITECTURE
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
    --green: #00FF9D;
    --red: #FF3D71;
    --text: #C8D8F0;
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
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
}

/* Panel Frame Wrapper */
.cyber-panel-native {
    background: #0C1425;
    border: 1px solid #162035;
    border-radius: 10px;
    position: relative;
    overflow: hidden;
    padding: 10px;
    margin-bottom: 10px;
}
.panel-header-text {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #00EEFF;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. TOP TICKER WIDGET (TRADINGVIEW)
# ==============================================================================
ticker_html = """
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-tickers.js" async>
  {
  "symbols": [
    {"proName": "FOREXCOM:SPXUSD", "title": "S&P 500 Index"},
    {"proName": "FOREXCOM:NSXUSD", "title": "US 100 Cash CFD"},
    {"proName": "FX_IDC:EURUSD", "title": "EUR to USD"},
    {"proName": "BITSTAMP:BTCUSD", "title": "Bitcoin"},
    {"proName": "BITSTAMP:ETHUSD", "title": "Ethereum"},
    {"proName": "OANDA:XAUUSD", "title": "XAUUSD"},
    {"proName": "TVC:DXY", "title": "DXY "},
    {"proName": "IDX:COMPOSITE", "title": "IHSG"},
    {"proName": "OANDA:USDJPY", "title": "USD to JPY"}
  ],
  "colorTheme": "dark",
  "locale": "id",
  "largeChartUrl": "",
  "isTransparent": true,
  "showSymbolLogo": true
}
  </script>
</div>
"""
components.html(ticker_html, height=50)

# ==============================================================================
# TERMINAL HEADER BANNER
# ==============================================================================
st.markdown("""
<div style="height: 42px; display: flex; align-items: center; justify-content: space-between; padding: 0 10px; background: rgba(7,12,24,0.95); border-bottom: 1px solid #162035; margin-bottom: 10px;">
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="width: 24px; height: 24px; background: linear-gradient(135deg, #00EEFF, #8B5CF6); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-family: 'Share Tech Mono', monospace; font-size: 10px; font-weight: 700; color: #fff;">AV</div>
        <div style="font-family: 'Share Tech Mono', monospace; font-size: 13px; color: #00EEFF; letter-spacing: 1.5px;">AEROVULPIS PRO TERMINAL v3.5</div>
    </div>
    <div style="font-family: 'Share Tech Mono', monospace; font-size: 9px; color: #00FF9D; letter-spacing: 1px;">⚡ DYNAMIHATCH ENGINE LIVE</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# CORE INTERFACE - 3-COLUMN STRUCTURE
# ==============================================================================
col1, col2, col3 = st.columns([1, 1.3, 1])

# --- KOLOM 1: ECONOMIC CALENDAR ---
with col1:
    st.markdown('<div class="cyber-panel-native"><div class="panel-header-text"><span>Economic Calendar</span><span style="color:#4B6A8A;">Tradays</span></div>', unsafe_allow_html=True)
    calendar_html = """
    <iframe src="https://www.tradays.com/en/economic-calendar/widget?mode=2&colorTheme=dark" 
            style="width:100%; height:620px; border:none; background:#0C1425;" 
            frameborder="0" scrolling="auto">
    </iframe>
    """
    components.html(calendar_html, height=625)
    st.markdown('</div>', unsafe_allow_html=True)

# --- KOLOM 2: DXY + LIVE NEWS TIMELINE + GRAPH TRADINGVIEW WITH RSI ---
with col2:
    # Menggunakan Tabs agar layout di HP tetap rapih, terstruktur, dan hemat ruang
    tab_charts, tab_news = st.tabs(["📊 Market Analytics & Charts", "📰 Live TradingView News"])
    
    with tab_charts:
        # Panel Atas: DXY Symbol Overview (Sesuai Request)
        st.markdown('<div class="cyber-panel-native"><div class="panel-header-text"><span>DXY Overview</span><span style="color:#4B6A8A;">Index</span></div>', unsafe_allow_html=True)
        dxy_widget_html = """
        <div class="tradingview-widget-container" style="height:240px;">
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-symbol-overview.js" async>
          {
          "lineWidth": 2, "lineType": 0, "chartType": "area",
          "fontColor": "rgb(106, 109, 120)", "gridLineColor": "rgba(242, 242, 242, 0.06)",
          "backgroundColor": "#0C1425", "widgetFontColor": "#DBDBDB",
          "upColor": "#22ab94", "downColor": "#f7525f", "colorTheme": "dark",
          "isTransparent": true, "locale": "en", "symbols": [["INDEX:DXY|1D"]],
          "dateRanges": ["1d|1","1m|30","3m|60","12m|1D","all|1M"],
          "fontSize": "10", "headerFontSize": "medium", "autosize": true, "width": "100%", "height": "100%"
          }
          </script>
        </div>
        """
        components.html(dxy_widget_html, height=245)
        st.markdown('</div>', unsafe_allow_html=True)

        # Panel Bawah: Grafik TradingView Pengganti MT4 (Dengan Indikator RSI)
        st.markdown('<div class="cyber-panel-native"><div class="panel-header-text"><span>Grafik TradingView (RSI Included)</span><span style="color:#4B6A8A;">Interactive Chart</span></div>', unsafe_allow_html=True)
        chart_rsi_html = """
        <div id="tv-chart-rsi-container" style="height:310px;"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({
          "autosize": true,
          "symbol": "OANDA:XAUUSD",
          "interval": "60",
          "timezone": "Asia/Jakarta",
          "theme": "dark",
          "style": "1",
          "locale": "id",
          "enable_publishing": false,
          "hide_side_toolbar": false,
          "allow_symbol_change": true,
          "container_id": "tv-chart-rsi-container",
          "studies": ["RSI@tv-basicstudies"],
          "backgroundColor": "#0C1425",
          "gridColor": "rgba(0,238,255,0.02)"
        });
        </script>
        """
        components.html(chart_rsi_html, height=315)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_news:
        # Integrasi Komponen News Widget Timeline 
        st.markdown('<div class="cyber-panel-native"><div class="panel-header-text"><span>TradingView Live Timeline News</span></div>', unsafe_allow_html=True)
        news_html = """
        <div class="tradingview-widget-container">
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-timeline.js" async>
          {
          "displayMode": "regular",
          "feedMode": "all_symbols",
          "colorTheme": "dark",
          "isTransparent": true,
          "locale": "id",
          "width": "100%",
          "height": "590"
          }
          </script>
        </div>
        """
        components.html(news_html, height=600)
        st.markdown('</div>', unsafe_allow_html=True)

# --- KOLOM 3: AI INTERACTIVE SIGNAL FEED + FOREX HEATMAP ---
with col3:
    # Bagian Atas: Komponen Input AI Terbuka & Interaktif (Menghilangkan Bug HTML Mentah)
    st.markdown('<div class="cyber-panel-native"><div class="panel-header-text"><span>AI Intelligence Terminal</span><span style="color:#00FF9D;">Online</span></div>', unsafe_allow_html=True)
    
    st.info("💡 **Pemberitahuan:** Silakan masukkan nama *pair* mata uang atau data fundamental (*news*) di bawah ini untuk mendapatkan hasil kalkulasi analisis teknikal dan sentimen dari sistem AI.")
    
    # Form Input Native Streamlit (Dijamin Responsif)
    ai_query = st.text_input("Data Entry Parameter :", placeholder="Contoh: XAUUSD atau US CPI Data Release")
    btn_submit = st.button("🚀 Mulai Analisis AI", use_container_width=True)
    
    # Simulasi Tampilan Output AI saat Tombol Diklik
    if btn_submit and ai_query:
        st.success(f"Analisis Berhasil Diinisiasi untuk: **{ai_query}**")
        st.code(f"[SYSTEM INFERENCE]: Memproses matriks data orderblock & liquidity pool untuk {ai_query}...", language="bash")
    else:
        st.markdown("""
        <div style="background: rgba(0,238,255,0.03); border: 1px dashed #162035; padding: 10px; border-radius: 6px; text-align: center;">
            <span style="font-family: monospace; font-size: 10px; color: #4B6A8A;">Menunggu Perintah Analisis...</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Bagian Bawah: Peletakan Terbaik Forex Heatmap (Tepat di Bawah Feed AI)
    st.markdown('<div class="cyber-panel-native"><div class="panel-header-text"><span>Forex Cross Rates Heatmap</span><span style="color:#4B6A8A;">Live Matrix</span></div>', unsafe_allow_html=True)
    heatmap_html = """
    <div class="tradingview-widget-container" style="width:100%;">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-forex-heat-map.js" async>
      {
      "colorTheme": "dark",
      "isTransparent": true,
      "locale": "id",
      "currencies": ["EUR","USD","JPY","GBP","CHF","AUD","CAD","NZD","CNY"],
      "width": "100%",
      "height": "340"
      }
      </script>
    </div>
    """
    components.html(heatmap_html, height=345)
    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# LOWER SECTION: DYNAMIC SIGNAL MATRIX & CUSTOM WATCHLIST (SESUAI APP SMARTPHONE)
# ==============================================================================
st.markdown('<div class="cyber-panel-native">', unsafe_allow_html=True)
st.markdown('<div class="panel-header-text"><span>Market Watchlist Overview (Sesuai Komposisi Screenshot)</span><span style="color:#8B5CF6;">TradingView Core</span></div>', unsafe_allow_html=True)

# Membangun struktur tab persis seperti pengelompokan di bursa aplikasi TradingView Mobile Anda
watchlist_core_html = """
<div class="tradingview-widget-container">
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>
  {
  "colorTheme": "dark",
  "dateRange": "12M",
  "showChart": false,
  "locale": "id",
  "isTransparent": true,
  "showSymbolLogo": true,
  "width": "100%",
  "height": "320",
  "tabs": [
    {
      "title": "Indeks Utama & DXY",
      "symbols": [
        {"s": "IDX:COMPOSITE", "d": "COMPOSITE (IHSG)"},
        {"s": "IDX:IDX30", "d": "IDX30 Index"},
        {"s": "IDX:IDXBUMN20", "d": "IDX BUMN 20"},
        {"s": "FOREXCOM:SPXUSD", "d": "S&P 500 Index"},
        {"s": "TVC:DXY", "d": "Indeks Dolar (DXY)"}
      ]
    },
    {
      "title": "Saham (Stock)",
      "symbols": [
        {"s": "IDX:ANTM", "d": "PT ANTAM Tbk"},
        {"s": "IDX:BBRI", "d": "PT Bank Rakyat Indonesia"},
        {"s": "IDX:TLKM", "d": "PT Telkom Indonesia"}
      ]
    },
    {
      "title": "Forex",
      "symbols": [
        {"s": "FX:EURUSD", "d": "EURUSD"},
        {"s": "FX:GBPUSD", "d": "GBPUSD"}
      ]
    }
  ]
}
  </script>
</div>
"""
components.html(watchlist_core_html, height=330)
st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# FOOTER TERMINAL
# ==============================================================================
st.markdown("""
<div style="text-align: center; padding: 15px 0; opacity: 0.4;">
    <p style="font-family: 'Share Tech Mono', monospace; font-size: 9px; color: #4B6A8A; margin: 0;">
        [PRODUCTION RUN] AEROVULPIS V3.5 | INTEGRATED DYNAMIHATCH MATRIX SYSTEM
    </p>
</div>
""", unsafe_allow_html=True)
