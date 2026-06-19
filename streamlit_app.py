# ==============================================================================
# bloomberg_prototype.py - Eksperimen UI AeroVulpis ala Bloomberg Terminal
# ==============================================================================

import streamlit as st
import streamlit.components.v1 as components

# 1. PAGE CONFIG
st.set_page_config(page_title="AeroVulpis BBG Theme", page_icon="📈", layout="wide")

# 2. INJEKSI CSS KUSTOM (Tema Pure Black & Monospace)
st.markdown("""
<style>
    /* Import font mirip terminal */
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:ital,wght@0,400;0,700;1,400;1,700&display=swap');

    /* Reset Streamlit default padding & background */
    .stApp {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-family: 'Courier Prime', monospace !important;
    }
    
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100% !important;
    }

    /* Warna khas Bloomberg */
    .bbg-amber { color: #FFB000; }
    .bbg-blue { color: #00A1FF; }
    .bbg-green { color: #00FF00; }
    .bbg-red { color: #FF0000; }
    .bbg-bg-green { background-color: #00FF00; color: #000000; font-weight: bold; }
    .bbg-bg-amber { background-color: #FFB000; color: #000000; font-weight: bold; }
    .bbg-bg-red { background-color: #AA0000; color: #FFFFFF; font-weight: bold; }

    /* Top Command Menu */
    .cmd-menu {
        display: flex; gap: 2px; padding: 2px 0; border-bottom: 1px solid #333; margin-bottom: 4px;
    }
    .cmd-btn {
        background-color: #00FF00; color: #000000; padding: 1px 6px; font-size: 11px; font-weight: bold; text-transform: uppercase; cursor: pointer;
    }

    /* Ticker Header */
    .ticker-header {
        display: flex; align-items: center; gap: 15px; font-size: 14px; margin-bottom: 4px; border-bottom: 1px solid #333; padding-bottom: 4px;
    }
    .ticker-name { background-color: #FFB000; color: #000000; padding: 2px 8px; font-weight: bold; }
    
    /* Panel Data Kiri */
    .data-panel {
        font-size: 12px; line-height: 1.2;
    }
    .data-row {
        display: flex; justify-content: space-between; border-bottom: 1px dotted #333; padding: 2px 0;
    }
    .data-label { color: #FFFFFF; }
    .data-value-highlight { background-color: #FFB000; color: #000000; padding: 0 4px; min-width: 80px; text-align: right; }

    /* News Feed Bawah */
    .news-feed {
        background-color: #000044; color: #FFB000; padding: 4px; font-size: 12px; margin-top: 10px; border-top: 2px solid #00A1FF; height: 100px; overflow-y: hidden;
    }
</style>
""", unsafe_allow_html=True)

# 3. TOP COMMAND MENU (Meniru deretan tombol hijau di atas)
st.markdown("""
<div class="cmd-menu">
    <div class="cmd-btn" style="background-color: #FF00FF; color: white;">CANC</div>
    <div class="cmd-btn">HELP</div>
    <div class="cmd-btn">SEARC</div>
    <div class="cmd-btn">NEWS</div>
    <div class="cmd-btn">QUOTE</div>
    <div class="cmd-btn">MSG</div>
    <div class="cmd-btn">MENU</div>
    <div class="cmd-btn">PRINT</div>
</div>
""", unsafe_allow_html=True)

# 4. TICKER HEADER
st.markdown("""
<div class="ticker-header">
    <div class="ticker-name">TSLA US Equity</div>
    <div>$ <span class="bbg-amber" style="font-size: 18px;">315.13</span></div>
    <div class="bbg-green">+3.89</div>
    <div><span class="bbg-amber">Vol</span> 3,468,458</div>
    <div><span class="bbg-amber">O</span> 314.60K</div>
    <div><span class="bbg-amber">H</span> 316.98Q</div>
    <div><span class="bbg-amber">L</span> 311.26K</div>
    <div class="bbg-bg-red" style="padding: 2px 8px; margin-left: auto;">Bloomberg Default Risk</div>
</div>
""", unsafe_allow_html=True)

# 5. MAIN LAYOUT (Kiri: Data, Kanan: Chart)
col_left, col_right = st.columns([1, 2.2])

with col_left:
    # Panel Data Fundamental (Hardcoded HTML untuk prototipe visual)
    st.markdown("""
    <div class="data-panel">
        <div style="color: #FFB000; margin-bottom: 5px;">1-Yr Default Risk</div>
        <div style="font-size: 24px; margin-bottom: 10px;">IG9 <span style="font-size: 14px; float: right;">0.2796%</span></div>
        
        <div style="color: #00A1FF; margin-top: 15px; margin-bottom: 5px;">Model Inputs (USD) <input type="checkbox" checked> Override 2026:Q2</div>
        
        <div class="data-row"><span class="data-label">6) Share Price</span><span class="data-value-highlight">315.13</span></div>
        <div class="data-row"><span class="data-label">7) Market Cap</span><span class="data-value-highlight">52,963.08 MM</span></div>
        <div class="data-row"><span class="data-label">8) Price Vol (1-Yr)</span><span class="data-value-highlight">35.65 %</span></div>
        <div class="data-row"><span class="data-label">9) Short-Term Debt</span><span class="data-value-highlight">324.22 MM</span></div>
        <div class="data-row"><span class="data-label">10) Long-Term Debt</span><span class="data-value-highlight">10,719.38 MM</span></div>
        <div class="data-row"><span class="data-label">11) Total Debt</span><span style="background-color: #888; color: black; padding: 0 4px;">11,043.6 MM</span></div>
        <div class="data-row"><span class="data-label">12) Interest Expn (T12M)</span><span class="data-value-highlight">430.9 MM</span></div>
        <div class="data-row"><span class="data-label">13) Adj CFO (T12M)</span><span class="data-value-highlight">-459.96 MM</span></div>
        
        <div class="bbg-bg-amber" style="margin-top: 15px; padding: 2px;">20) Sector Comparison | AUTO &raquo;</div>
        <div style="background-color: #FFB000; color: #000; padding: 2px; font-size: 10px;">United States of America - Consumer Discretionary: Automobiles</div>
        
        <div class="data-row" style="border:none; margin-top: 5px;">
            <span class="data-label">Debt/Equity (%)</span>
            <span class="bbg-amber">115.9</span>
            <span class="data-label" style="font-size: 8px;">138.7 [---|---] 448.1</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    # Menggunakan Advanced Chart TradingView dengan tema sangat gelap
    chart_html = """
    <div class="tradingview-widget-container" style="height: 400px; width: 100%;">
      <div id="tv_chart_bbg" style="height: 100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {
      "autosize": true,
      "symbol": "NASDAQ:TSLA",
      "interval": "D",
      "timezone": "Asia/Jakarta",
      "theme": "dark",
      "style": "2", /* Style 2 adalah Line Chart, mirip gambar BBG */
      "locale": "id",
      "enable_publishing": false,
      "backgroundColor": "#000000", /* Pure Black */
      "gridColor": "#111111",
      "hide_top_toolbar": true,
      "hide_legend": false,
      "save_image": false,
      "container_id": "tv_chart_bbg",
      "studies": [
        "Volume@tv-basicstudies"
      ]
    }
      );
      </script>
    </div>
    """
    components.html(chart_html, height=400)

# 6. NEWS FEED BOTTOM PANEL
st.markdown("""
<div class="news-feed">
    <div>469 AGN 21:00 NSW prevents pregnant women being sacked</div>
    <div>468 BFW 21:00 Singapore Completes S$1.1B Bus Upgrade Program: Straits Times</div>
    <div>467 TWT 21:00 Nikkei Asian Review: Future of electric cars is at the bottom of a...</div>
    <div>466 WPT 21:00 Chip on Baker Mayfield's Shoulder Led Him to Oklahoma, And Now He is...</div>
    <div style="color: #00FF00; margin-top: 5px; font-weight: bold; background-color: #003300; padding: 2px;">Hard-to-explain topics, explained simply. Bloomberg QuickTake</div>
</div>
""", unsafe_allow_html=True)
