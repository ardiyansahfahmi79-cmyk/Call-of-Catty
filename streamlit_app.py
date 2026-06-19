# ==============================================================================
# dynamihatch_terminal.py - DynamiHatch Pro Terminal (Hybrid BBG x cTrader)
# ==============================================================================

import streamlit as st
import streamlit.components.v1 as components
import datetime

# ==============================================================================
# 1. PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="DynamiHatch Terminal",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 2. INJEKSI CSS KUSTOM (GLOBAL STYLING)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@400;600;800&display=swap');

    /* Reset & Dark Theme Base */
    .stApp {
        background-color: #070B14 !important; /* Super Dark Navy/Black */
        color: #C8D8F0 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hilangkan padding default Streamlit agar layar penuh */
    .block-container {
        padding: 0.5rem 0.5rem !important;
        max-width: 100% !important;
    }

    /* Font Khusus Angka & Terminal */
    .mono { font-family: 'Share Tech Mono', monospace; }

    /* Warna Kustom DynamiHatch */
    .dh-amber { color: #FFB000; }
    .dh-green { color: #00FF9D; }
    .dh-red { color: #FF3D71; }
    .dh-blue { color: #00E1FF; }

    /* Panel Box Base */
    .cyber-panel {
        background-color: #0D1424;
        border: 1px solid #1A2642;
        border-radius: 6px;
        padding: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* Header Top Bar */
    .top-header {
        display: flex; justify-content: space-between; align-items: center;
        background: linear-gradient(90deg, #0A101D 0%, #111A2F 100%);
        border-bottom: 2px solid #00E1FF;
        padding: 8px 15px; border-radius: 6px; margin-bottom: 10px;
    }
    .brand-title { font-size: 20px; font-weight: 800; letter-spacing: 2px; color: #FFFFFF; }
    .brand-title span { color: #00E1FF; }

    /* cTrader Style Execution Buttons */
    .ctrader-btn {
        width: 48%; padding: 12px 0; font-size: 16px; font-weight: bold; border: none; border-radius: 4px; cursor: pointer; color: white; text-align: center;
    }
    .btn-sell { background: linear-gradient(180deg, #FF3D71 0%, #BA103B 100%); }
    .btn-buy { background: linear-gradient(180deg, #00FF9D 0%, #00995E 100%); }

    /* Bloomberg Style Data Table */
    .bbg-row { display: flex; justify-content: space-between; border-bottom: 1px dotted #2A3B5C; padding: 4px 0; font-size: 12px; }
    .bbg-label { color: #8B9BB4; }
    .bbg-val { color: #FFB000; font-weight: bold; }
    
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. TOP HEADER (Branding, Market Time, Suhu/Weather)
# ==============================================================================
# Mendapatkan waktu saat ini untuk indikator sederhana
now = datetime.datetime.now().strftime("%H:%M:%S | %d %b %Y")

header_html = f"""
<div class="top-header mono">
    <div class="brand-title">DYNAMIHATCH <span>TERMINAL</span></div>
    
    <div style="display: flex; gap: 20px; align-items: center; font-size: 12px;">
        <div style="background: #1A2642; padding: 4px 10px; border-radius: 4px; color: #00E1FF;">
            📡 SYS: ONLINE
        </div>
        <div style="background: #1A2642; padding: 4px 10px; border-radius: 4px;">
            🌡️ SUHU GLOBAL: <span class="dh-amber">24°C (London)</span> | <span class="dh-amber">28°C (NY)</span>
        </div>
        <div style="background: #1A2642; padding: 4px 10px; border-radius: 4px; border-left: 2px solid #00FF9D;">
            ⏱️ WAKTU: {now} WIB
        </div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# ==============================================================================
# 4. TICKER TAPE (Global Markets)
# ==============================================================================
ticker_html = """
<div class="tradingview-widget-container" style="margin-bottom: 10px;">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
  {
  "symbols": [
    {"proName": "FOREXCOM:SPXUSD", "title": "S&P 500"},
    {"proName": "OANDA:XAUUSD", "title": "Gold"},
    {"proName": "FX_IDC:EURUSD", "title": "EUR/USD"},
    {"proName": "BITSTAMP:BTCUSD", "title": "Bitcoin"},
    {"proName": "OANDA:GBPUSD", "title": "GBP/USD"}
  ],
  "showSymbolLogo": true, "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive", "locale": "id"
}
  </script>
</div>
"""
components.html(ticker_html, height=45)

# ==============================================================================
# 5. MAIN GRID LAYOUT (3 KOLOM)
# ==============================================================================
# Komposisi: 25% (Kiri: Eksekusi & Data), 50% (Tengah: Chart Utama), 25% (Kanan: Kalender & Setups)
col_left, col_mid, col_right = st.columns([1.2, 2.5, 1.2])

# ------------------------------------------------------------------------------
# KOLOM KIRI: cTrader Order Panel + Bloomberg Data
# ------------------------------------------------------------------------------
with col_left:
    st.markdown("""
    <div class="cyber-panel">
        <div style="font-size: 14px; font-weight: bold; border-bottom: 1px solid #1A2642; padding-bottom: 8px; margin-bottom: 10px; color: #00E1FF;" class="mono">
            ⚡ QUICK EXECUTION (cTrader Style)
        </div>
        
        <div style="text-align: center; font-size: 22px; font-weight: 800; margin-bottom: 5px;">XAUUSD</div>
        <div style="text-align: center; font-size: 12px; color: #8B9BB4; margin-bottom: 15px;">Volume: 1.00 Lot</div>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
            <div class="ctrader-btn btn-sell mono">
                SELL<br><span style="font-size: 20px;">2341.15</span>
            </div>
            <div class="ctrader-btn btn-buy mono">
                BUY<br><span style="font-size: 20px;">2341.25</span>
            </div>
        </div>

        <div style="font-size: 10px; color: #8B9BB4; text-align: center; margin-bottom: 5px;">MARKET DEPTH</div>
        <div style="display: flex; font-size: 11px; font-family: monospace;">
            <div style="width: 50%; padding-right: 2px;">
                <div style="background: rgba(255,61,113,0.2); text-align: right; padding: 2px 5px; margin-bottom: 2px; color: #FF3D71;">2341.15 | 2.5m</div>
                <div style="background: rgba(255,61,113,0.3); text-align: right; padding: 2px 5px; margin-bottom: 2px; color: #FF3D71;">2341.14 | 5.1m</div>
                <div style="background: rgba(255,61,113,0.5); text-align: right; padding: 2px 5px; color: #FF3D71;">2341.12 | 8.0m</div>
            </div>
            <div style="width: 50%; padding-left: 2px;">
                <div style="background: rgba(0,255,157,0.2); text-align: left; padding: 2px 5px; margin-bottom: 2px; color: #00FF9D;">2341.25 | 1.1m</div>
                <div style="background: rgba(0,255,157,0.4); text-align: left; padding: 2px 5px; margin-bottom: 2px; color: #00FF9D;">2341.27 | 3.4m</div>
                <div style="background: rgba(0,255,157,0.6); text-align: left; padding: 2px 5px; color: #00FF9D;">2341.30 | 7.2m</div>
            </div>
        </div>
    </div>
    
    <div class="cyber-panel mono">
        <div style="background-color: #FFB000; color: #000; padding: 4px 8px; font-weight: bold; font-size: 11px; margin-bottom: 10px;">
            20) FUNDAMENTAL METRICS (BBG IG9)
        </div>
        <div class="bbg-row"><span class="bbg-label">1-Yr Default Prob</span><span class="dh-green">0.2796%</span></div>
        <div class="bbg-row"><span class="bbg-label">Market Cap (USD)</span><span class="bbg-val">N/A (Forex)</span></div>
        <div class="bbg-row"><span class="bbg-label">Daily Volatility</span><span class="bbg-val">1.24 %</span></div>
        <div class="bbg-row"><span class="bbg-label">RSI (14) Daily</span><span class="dh-red">68.5</span></div>
        <div class="bbg-row"><span class="bbg-label">MACD Line</span><span class="dh-green">12.45</span></div>
        <div class="bbg-row"><span class="bbg-label">Retail Sentiment</span><span class="dh-red">72% SHORT</span></div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# KOLOM TENGAH: Chart Utama TradingView
# ------------------------------------------------------------------------------
with col_mid:
    chart_html = """
    <div class="cyber-panel" style="height: 640px; padding: 5px;">
        <div class="tradingview-widget-container" style="height: 100%; width: 100%;">
          <div id="tv_chart_main" style="height: 100%;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget(
          {
          "autosize": true,
          "symbol": "OANDA:XAUUSD",
          "interval": "60",
          "timezone": "Asia/Jakarta",
          "theme": "dark",
          "style": "1", /* 1 = Candlestick */
          "locale": "id",
          "enable_publishing": false,
          "backgroundColor": "#0D1424",
          "gridColor": "#1A2642",
          "hide_top_toolbar": false,
          "hide_legend": false,
          "save_image": false,
          "container_id": "tv_chart_main",
          "studies": [
            "Volume@tv-basicstudies",
            "MACD@tv-basicstudies"
          ]
        }
          );
          </script>
        </div>
    </div>
    """
    components.html(chart_html, height=650)

# ------------------------------------------------------------------------------
# KOLOM KANAN: MQL5 Calendar & Setups
# ------------------------------------------------------------------------------
with col_right:
    # MQL5 Economic Calendar Iframe
    mql5_html = """
    <div class="cyber-panel" style="height: 380px; padding: 0; overflow: hidden;">
        <div style="background: rgba(0,0,0,0.4); padding: 8px; border-bottom: 1px solid #1A2642; font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #00E1FF;">
            📅 MQL5 ECONOMIC CALENDAR
        </div>
        <iframe src="https://www.mql5.com/en/economic-calendar/widget?mode=2&utm_source=www.mql5.com" 
                width="100%" height="340" frameborder="0" scrolling="auto" 
                style="background-color: #0D1424;"></iframe>
    </div>
    """
    components.html(mql5_html, height=380)

    # Active Trade Setups List (Ringkas)
    st.markdown("""
    <div class="cyber-panel mono">
        <div style="font-size: 12px; color: #00E1FF; border-bottom: 1px solid #1A2642; padding-bottom: 5px; margin-bottom: 10px;">
            🎯 ACTIVE AI SETUPS
        </div>
        
        <div style="background: rgba(0,255,157,0.05); border-left: 3px solid #00FF9D; padding: 8px; margin-bottom: 8px; border-radius: 0 4px 4px 0;">
            <div style="display: flex; justify-content: space-between; font-weight: bold;">
                <span>USDJPY</span> <span class="dh-green">BUY</span>
            </div>
            <div style="font-size: 10px; color: #8B9BB4; margin-top: 4px;">
                ENTRY: 149.820 | TP1: <span class="dh-green">150.50</span>
            </div>
        </div>

        <div style="background: rgba(255,61,113,0.05); border-left: 3px solid #FF3D71; padding: 8px; border-radius: 0 4px 4px 0;">
            <div style="display: flex; justify-content: space-between; font-weight: bold;">
                <span>EURUSD</span> <span class="dh-red">SELL</span>
            </div>
            <div style="font-size: 10px; color: #8B9BB4; margin-top: 4px;">
                ENTRY: 1.08420 | TP1: <span class="dh-red">1.0795</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
