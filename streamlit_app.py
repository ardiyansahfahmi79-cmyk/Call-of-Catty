import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import random
from datetime import datetime, timedelta
import time

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="DynamiHatch Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CUSTOM CSS - CYBERPUNK / DIGITALTECH THEME
# =============================================================================
st.markdown("""
<style>
    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');

    /* Root Variables */
    :root {
        --neon-cyan: #00f0ff;
        --neon-green: #00ff9d;
        --neon-pink: #ff00ff;
        --neon-orange: #ff9d00;
        --neon-red: #ff0040;
        --neon-blue: #0066ff;
        --neon-purple: #9d00ff;
        --dark-bg: #0a0a0f;
        --panel-bg: #0d1117;
        --panel-border: #1a1f2e;
        --grid-line: #1e2330;
        --text-primary: #e0e0e0;
        --text-secondary: #8899a6;
        --accent-glow: rgba(0, 240, 255, 0.15);
    }

    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0a0f 100%);
        font-family: 'Rajdhani', sans-serif;
    }

    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0a0f;
    }
    ::-webkit-scrollbar-thumb {
        background: #1a1f2e;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #00f0ff;
    }

    /* Terminal Header */
    .terminal-header {
        background: linear-gradient(90deg, #0a0a0f 0%, #0d1117 50%, #0a0a0f 100%);
        border-bottom: 2px solid var(--neon-cyan);
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.3);
        padding: 8px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 1000;
    }

    .terminal-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00f0ff, #00ff9d, #00f0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 240, 255, 0.5);
        letter-spacing: 3px;
    }

    .terminal-subtitle {
        font-family: 'Share Tech Mono', monospace;
        color: var(--neon-green);
        font-size: 0.75rem;
        letter-spacing: 2px;
    }

    /* Cyberpunk Panels */
    .cyber-panel {
        background: linear-gradient(145deg, #0d1117 0%, #111827 100%);
        border: 1px solid #1a1f2e;
        border-radius: 8px;
        padding: 15px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }

    .cyber-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--neon-cyan), transparent);
        opacity: 0.6;
    }

    .cyber-panel::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--neon-green), transparent);
        opacity: 0.3;
    }

    .cyber-panel-corner {
        position: absolute;
        width: 8px;
        height: 8px;
        border: 2px solid var(--neon-cyan);
    }
    .cyber-panel-corner.tl { top: 0; left: 0; border-right: none; border-bottom: none; }
    .cyber-panel-corner.tr { top: 0; right: 0; border-left: none; border-bottom: none; }
    .cyber-panel-corner.bl { bottom: 0; left: 0; border-right: none; border-top: none; }
    .cyber-panel-corner.br { bottom: 0; right: 0; border-left: none; border-top: none; }

    /* Panel Title */
    .panel-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.85rem;
        color: var(--neon-cyan);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .panel-title::before {
        content: '◆';
        color: var(--neon-green);
        font-size: 0.6rem;
    }

    /* Ticker Bar */
    .ticker-container {
        background: linear-gradient(90deg, #0a0a0f, #0d1117, #0a0a0f);
        border-top: 1px solid #1a1f2e;
        border-bottom: 1px solid #1a1f2e;
        padding: 8px 0;
        overflow: hidden;
        position: relative;
    }

    .ticker-container::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 100px;
        background: linear-gradient(90deg, #0a0a0f, transparent);
        z-index: 2;
    }

    .ticker-container::after {
        content: '';
        position: absolute;
        right: 0;
        top: 0;
        bottom: 0;
        width: 100px;
        background: linear-gradient(270deg, #0a0a0f, transparent);
        z-index: 2;
    }

    /* Ticker Items */
    .ticker-item {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 0 20px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.85rem;
        white-space: nowrap;
    }

    .ticker-symbol {
        color: var(--neon-cyan);
        font-weight: 700;
    }

    .ticker-price {
        color: var(--text-primary);
    }

    .ticker-change-up {
        color: var(--neon-green);
    }

    .ticker-change-down {
        color: var(--neon-red);
    }

    /* Data Grid */
    .data-grid {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.8rem;
    }

    .data-row {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid #1a1f2e;
    }

    .data-label {
        color: var(--text-secondary);
    }

    .data-value {
        color: var(--text-primary);
        font-weight: 600;
    }

    .data-value.positive {
        color: var(--neon-green);
    }

    .data-value.negative {
        color: var(--neon-red);
    }

    /* News Ticker */
    .news-ticker {
        background: linear-gradient(90deg, #0d1117, #111827, #0d1117);
        border: 1px solid #1a1f2e;
        border-radius: 4px;
        padding: 10px 15px;
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.85rem;
        color: var(--text-secondary);
    }

    .news-item {
        display: flex;
        gap: 15px;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px solid #1a1f2e;
    }

    .news-time {
        color: var(--neon-orange);
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.75rem;
        min-width: 60px;
    }

    .news-source {
        color: var(--neon-cyan);
        font-size: 0.75rem;
        min-width: 40px;
    }

    .news-text {
        color: var(--text-primary);
    }

    /* Status Bar */
    .status-bar {
        background: linear-gradient(90deg, #0a0a0f, #0d1117);
        border-top: 1px solid var(--neon-cyan);
        padding: 6px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.75rem;
        color: var(--text-secondary);
    }

    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--neon-green);
        box-shadow: 0 0 10px var(--neon-green);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }

    /* Scanline Effect */
    .scanline {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            to bottom,
            rgba(255,255,255,0),
            rgba(255,255,255,0) 50%,
            rgba(0,0,0,0.1) 50%,
            rgba(0,0,0,0.1)
        );
        background-size: 100% 4px;
        pointer-events: none;
        z-index: 9999;
        opacity: 0.3;
    }

    /* Blinking cursor */
    .cursor-blink {
        animation: blink 1s step-end infinite;
    }

    @keyframes blink {
        50% { opacity: 0; }
    }

    /* Tab buttons */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #0d1117;
        border-radius: 8px 8px 0 0;
        padding: 4px 4px 0 4px;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.75rem;
        color: var(--text-secondary);
        background: #111827;
        border-radius: 6px 6px 0 0;
        border: 1px solid #1a1f2e;
        border-bottom: none;
    }

    .stTabs [aria-selected="true"] {
        color: var(--neon-cyan) !important;
        background: linear-gradient(180deg, #1a1f2e, #0d1117) !important;
        border-color: var(--neon-cyan) !important;
        box-shadow: 0 -2px 10px rgba(0, 240, 255, 0.2);
    }

    /* Buttons */
    .stButton > button {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(145deg, #0d1117, #1a1f2e);
        color: var(--neon-cyan);
        border: 1px solid var(--neon-cyan);
        border-radius: 4px;
        padding: 8px 16px;
        font-size: 0.8rem;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(145deg, #1a1f2e, #0d1117);
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
        transform: translateY(-1px);
    }

    /* Select boxes */
    .stSelectbox > div > div {
        background: #0d1117;
        border: 1px solid #1a1f2e;
        color: var(--text-primary);
        font-family: 'Share Tech Mono', monospace;
    }

    /* Input boxes */
    .stTextInput > div > div > input {
        background: #0d1117;
        border: 1px solid #1a1f2e;
        color: var(--neon-cyan);
        font-family: 'Share Tech Mono', monospace;
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(145deg, #0d1117, #111827);
        border: 1px solid #1a1f2e;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--neon-cyan), var(--neon-green));
    }

    .metric-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--neon-cyan);
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
    }

    .metric-label {
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 4px;
    }

    /* Economic Calendar Styles */
    .eco-calendar-row {
        display: grid;
        grid-template-columns: 80px 100px 60px 1fr 80px;
        gap: 10px;
        padding: 8px 0;
        border-bottom: 1px solid #1a1f2e;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.8rem;
        align-items: center;
    }

    .eco-time { color: var(--neon-orange); }
    .eco-currency { color: var(--neon-cyan); font-weight: 700; }
    .eco-impact { 
        padding: 2px 8px; 
        border-radius: 3px; 
        font-size: 0.7rem;
        text-align: center;
    }
    .eco-impact.high { background: rgba(255, 0, 64, 0.2); color: var(--neon-red); border: 1px solid var(--neon-red); }
    .eco-impact.medium { background: rgba(255, 157, 0, 0.2); color: var(--neon-orange); border: 1px solid var(--neon-orange); }
    .eco-impact.low { background: rgba(0, 255, 157, 0.2); color: var(--neon-green); border: 1px solid var(--neon-green); }
    .eco-event { color: var(--text-primary); }
    .eco-forecast { color: var(--neon-green); text-align: right; }

    /* Heatmap Grid */
    .heatmap-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 4px;
    }

    .heatmap-cell {
        padding: 8px;
        text-align: center;
        border-radius: 4px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.75rem;
        transition: all 0.3s ease;
    }

    .heatmap-cell:hover {
        transform: scale(1.05);
        z-index: 10;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
    }

    /* Sector Performance */
    .sector-bar {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 6px 0;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.8rem;
    }

    .sector-name { min-width: 120px; color: var(--text-secondary); }
    .sector-bar-track {
        flex: 1;
        height: 8px;
        background: #1a1f2e;
        border-radius: 4px;
        overflow: hidden;
        position: relative;
    }
    .sector-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    .sector-value { min-width: 50px; text-align: right; }

    /* Terminal Log */
    .terminal-log {
        background: #050508;
        border: 1px solid #1a1f2e;
        border-radius: 4px;
        padding: 10px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.75rem;
        color: var(--neon-green);
        max-height: 200px;
        overflow-y: auto;
    }

    .log-entry {
        padding: 2px 0;
        border-bottom: 1px solid #0d1117;
    }

    .log-time { color: var(--neon-orange); }
    .log-info { color: var(--neon-cyan); }
    .log-success { color: var(--neon-green); }
    .log-warning { color: var(--neon-orange); }
    .log-error { color: var(--neon-red); }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SCANLINE OVERLAY
# =============================================================================
st.markdown('<div class="scanline"></div>', unsafe_allow_html=True)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = "AAPL"
if 'timeframe' not in st.session_state:
    st.session_state.timeframe = "1D"
if 'terminal_logs' not in st.session_state:
    st.session_state.terminal_logs = []

# =============================================================================
# MOCK DATA GENERATORS
# =============================================================================

def generate_ohlc_data(ticker, periods=100):
    """Generate realistic OHLC data for charts"""
    np.random.seed(hash(ticker) % 2**32)
    base_price = random.uniform(50, 500)

    dates = pd.date_range(end=datetime.now(), periods=periods, freq='1h')
    data = []

    for i in range(periods):
        if i == 0:
            open_p = base_price
        else:
            open_p = data[-1]['close']

        change = np.random.normal(0, base_price * 0.02)
        close_p = open_p + change
        high_p = max(open_p, close_p) + abs(np.random.normal(0, base_price * 0.01))
        low_p = min(open_p, close_p) - abs(np.random.normal(0, base_price * 0.01))
        volume = int(np.random.normal(1000000, 300000))

        data.append({
            'date': dates[i],
            'open': round(open_p, 2),
            'high': round(high_p, 2),
            'low': round(low_p, 2),
            'close': round(close_p, 2),
            'volume': max(volume, 100000)
        })

    return pd.DataFrame(data)

def generate_ticker_data():
    """Generate live ticker data"""
    tickers = [
        ("AAPL", 178.35, 1.24), ("MSFT", 412.56, 0.89), ("GOOGL", 142.78, -0.45),
        ("AMZN", 185.23, 2.15), ("TSLA", 245.67, -1.82), ("META", 498.12, 3.45),
        ("NVDA", 875.45, 4.23), ("JPM", 198.34, 0.56), ("V", 285.67, -0.23),
        ("WMT", 168.90, 0.78), ("JNJ", 156.23, -0.34), ("UNH", 512.45, 1.12),
        ("XOM", 112.34, -0.89), ("BAC", 37.89, 0.45), ("PG", 165.78, 0.23)
    ]

    result = []
    for symbol, base, change_pct in tickers:
        current = base * (1 + np.random.normal(0, 0.002))
        change = current - base
        change_pct_real = (change / base) * 100
        result.append({
            'symbol': symbol,
            'price': round(current, 2),
            'change': round(change, 2),
            'change_pct': round(change_pct_real, 2)
        })
    return result

def generate_economic_calendar():
    """Generate MQL5-style economic calendar data"""
    events = [
        ("08:30", "USD", "HIGH", "Non-Farm Payrolls", "185K"),
        ("08:30", "USD", "HIGH", "Unemployment Rate", "3.7%"),
        ("10:00", "USD", "MEDIUM", "ISM Manufacturing PMI", "49.5"),
        ("14:00", "USD", "HIGH", "FOMC Interest Rate Decision", "5.50%"),
        ("02:30", "AUD", "MEDIUM", "RBA Cash Rate", "4.35%"),
        ("07:00", "EUR", "HIGH", "ECB Main Refinancing Rate", "4.50%"),
        ("09:00", "GBP", "MEDIUM", "BoE Official Bank Rate", "5.25%"),
        ("12:30", "CAD", "HIGH", "BoC Overnight Rate", "5.00%"),
        ("19:50", "JPY", "MEDIUM", "Tokyo CPI y/y", "2.8%"),
        ("21:00", "NZD", "LOW", "NZIER Business Confidence", "-23"),
        ("01:30", "CNY", "HIGH", "Caixin Manufacturing PMI", "50.8"),
        ("03:30", "CHF", "MEDIUM", "SNB Policy Rate", "1.75%"),
    ]
    return events

def generate_news_feed():
    """Generate financial news feed"""
    news = [
        ("14:32", "RTRS", "Fed signals potential rate cuts in Q3 2026 amid cooling inflation"),
        ("14:28", "BLOOM", "Tech sector rally continues as AI demand surges globally"),
        ("14:15", "DJ", "Oil prices stabilize near $78/bbl on supply outlook"),
        ("14:05", "RTRS", "ECB maintains hawkish stance despite eurozone slowdown"),
        ("13:58", "BLOOM", "Tesla announces new Gigafactory location in Southeast Asia"),
        ("13:42", "DJ", "Bitcoin breaks $72,000 as institutional adoption accelerates"),
        ("13:30", "RTRS", "China reports stronger-than-expected manufacturing data"),
        ("13:15", "BLOOM", "JPMorgan exceeds Q2 earnings expectations by 12%"),
    ]
    return news

def generate_sector_data():
    """Generate sector performance data"""
    sectors = [
        ("Technology", 2.45), ("Healthcare", 0.89), ("Financials", -0.34),
        ("Energy", -1.23), ("Consumer Disc.", 1.56), ("Industrials", 0.67),
        ("Materials", -0.45), ("Utilities", 0.23), ("Real Estate", -0.78),
        ("Communication", 1.89), ("Consumer Staples", 0.12)
    ]
    return sectors

def generate_heatmap_data():
    """Generate market heatmap data"""
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", 
               "V", "WMT", "JNJ", "UNH", "XOM", "BAC", "PG", "DIS"]
    data = []
    for sym in symbols:
        change = np.random.normal(0, 2)
        data.append((sym, change))
    return data

def add_log(message, level="info"):
    """Add entry to terminal log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.terminal_logs.append((timestamp, level, message))
    if len(st.session_state.terminal_logs) > 50:
        st.session_state.terminal_logs.pop(0)

# =============================================================================
# HEADER SECTION
# =============================================================================
header_col1, header_col2, header_col3 = st.columns([3, 4, 2])

with header_col1:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 15px;">
        <div style="font-size: 2rem;">⚡</div>
        <div>
            <div class="terminal-title">DYNAMIHATCH</div>
            <div class="terminal-subtitle">TERMINAL v2.6.0 // SYSTEM ONLINE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    # Search bar
    search_col1, search_col2 = st.columns([4, 1])
    with search_col1:
        ticker_input = st.text_input("", value=st.session_state.selected_ticker, 
                                     placeholder="ENTER TICKER...", 
                                     label_visibility="collapsed")
    with search_col2:
        if st.button("EXECUTE", key="search_btn"):
            st.session_state.selected_ticker = ticker_input.upper()
            add_log(f"Ticker search executed: {ticker_input.upper()}", "success")

with header_col3:
    st.markdown(f"""
    <div style="text-align: right; font-family: 'Share Tech Mono', monospace;">
        <div style="color: #00f0ff; font-size: 1.2rem;">{datetime.now().strftime("%H:%M:%S")}</div>
        <div style="color: #8899a6; font-size: 0.75rem;">{datetime.now().strftime("%Y-%m-%d")}</div>
        <div style="color: #00ff9d; font-size: 0.7rem;">● LIVE DATA FEED</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# TICKER TAPE (SCROLLING)
# =============================================================================
st.markdown('<div style="height: 2px; background: linear-gradient(90deg, transparent, #00f0ff, transparent);"></div>', unsafe_allow_html=True)

ticker_data = generate_ticker_data()
ticker_html = '<div class="ticker-container"><div style="display: flex; animation: scroll 30s linear infinite;">'
for item in ticker_data:
    change_class = "ticker-change-up" if item['change'] >= 0 else "ticker-change-down"
    arrow = "▲" if item['change'] >= 0 else "▼"
    ticker_html += f'<div class="ticker-item"><span class="ticker-symbol">{item["symbol"]}</span><span class="ticker-price">{item["price"]:.2f}</span><span class="{change_class}">{arrow} {abs(item["change_pct"]):.2f}%</span></div>'
ticker_html += '</div></div>'

st.markdown(ticker_html + """
<style>
@keyframes scroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div style="height: 2px; background: linear-gradient(90deg, transparent, #00ff9d, transparent); margin-bottom: 15px;"></div>', unsafe_allow_html=True)

# =============================================================================
# MAIN DASHBOARD GRID
# =============================================================================

# Row 1: Main Chart + Side Panels
row1_col1, row1_col2 = st.columns([3, 1])

with row1_col1:
    # Main Chart Panel
    st.markdown("""
    <div class="cyber-panel" style="height: 500px;">
        <div class="cyber-panel-corner tl"></div>
        <div class="cyber-panel-corner tr"></div>
        <div class="cyber-panel-corner bl"></div>
        <div class="cyber-panel-corner br"></div>
        <div class="panel-title">MARKET ANALYSIS // {ticker}</div>
    """.format(ticker=st.session_state.selected_ticker), unsafe_allow_html=True)

    # Chart controls
    chart_ctrl_col1, chart_ctrl_col2, chart_ctrl_col3, chart_ctrl_col4 = st.columns([1, 1, 1, 1])
    with chart_ctrl_col1:
        timeframe = st.selectbox("", ["1M", "5M", "15M", "1H", "4H", "1D", "1W"], 
                                  index=5, label_visibility="collapsed", key="tf_select")
    with chart_ctrl_col2:
        chart_type = st.selectbox("", ["Candlestick", "Line", "Area", "Heikin-Ashi"], 
                                   index=0, label_visibility="collapsed", key="chart_type")
    with chart_ctrl_col3:
        indicators = st.multiselect("", ["SMA", "EMA", "Bollinger", "RSI", "MACD", "Volume"], 
                                     default=["SMA", "Volume"], label_visibility="collapsed", key="indicators")
    with chart_ctrl_col4:
        if st.button("REFRESH", key="refresh_chart"):
            add_log("Chart data refreshed", "info")

    # Generate and display chart
    ohlc_data = generate_ohlc_data(st.session_state.selected_ticker)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.02, 
                        row_heights=[0.6, 0.2, 0.2],
                        subplot_titles=("", "", ""))

    # Main candlestick chart
    fig.add_trace(go.Candlestick(
        x=ohlc_data['date'],
        open=ohlc_data['open'],
        high=ohlc_data['high'],
        low=ohlc_data['low'],
        close=ohlc_data['close'],
        name="OHLC",
        increasing_line_color='#00ff9d',
        increasing_fillcolor='rgba(0, 255, 157, 0.3)',
        decreasing_line_color='#ff0040',
        decreasing_fillcolor='rgba(255, 0, 64, 0.3)'
    ), row=1, col=1)

    # SMA
    if "SMA" in indicators:
        sma20 = ohlc_data['close'].rolling(20).mean()
        fig.add_trace(go.Scatter(x=ohlc_data['date'], y=sma20, 
                                  mode='lines', name='SMA 20',
                                  line=dict(color='#00f0ff', width=1)), row=1, col=1)

    # Bollinger Bands
    if "Bollinger" in indicators:
        sma20 = ohlc_data['close'].rolling(20).mean()
        std20 = ohlc_data['close'].rolling(20).std()
        upper = sma20 + 2 * std20
        lower = sma20 - 2 * std20
        fig.add_trace(go.Scatter(x=ohlc_data['date'], y=upper, 
                                  mode='lines', name='BB Upper',
                                  line=dict(color='rgba(157, 0, 255, 0.5)', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=ohlc_data['date'], y=lower, 
                                  mode='lines', name='BB Lower',
                                  line=dict(color='rgba(157, 0, 255, 0.5)', width=1),
                                  fill='tonexty', fillcolor='rgba(157, 0, 255, 0.05)'), row=1, col=1)

    # Volume
    if "Volume" in indicators:
        colors = ['#00ff9d' if ohlc_data['close'].iloc[i] >= ohlc_data['open'].iloc[i] 
                  else '#ff0040' for i in range(len(ohlc_data))]
        fig.add_trace(go.Bar(x=ohlc_data['date'], y=ohlc_data['volume'], 
                            marker_color=colors, name='Volume', opacity=0.6), row=2, col=1)

    # RSI
    if "RSI" in indicators:
        delta = ohlc_data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        fig.add_trace(go.Scatter(x=ohlc_data['date'], y=rsi, 
                                  mode='lines', name='RSI',
                                  line=dict(color='#ff9d00', width=1)), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="rgba(255, 0, 64, 0.5)", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="rgba(0, 255, 157, 0.5)", row=3, col=1)

    # Layout
    fig.update_layout(
        height=420,
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(13, 17, 23, 0.5)',
        font=dict(family="Share Tech Mono, monospace", color="#e0e0e0"),
        xaxis_rangeslider_visible=False,
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
        xaxis=dict(gridcolor='rgba(26, 31, 46, 0.5)', showgrid=True),
        yaxis=dict(gridcolor='rgba(26, 31, 46, 0.5)', showgrid=True),
        xaxis2=dict(gridcolor='rgba(26, 31, 46, 0.5)', showgrid=True),
        yaxis2=dict(gridcolor='rgba(26, 31, 46, 0.5)', showgrid=True),
        xaxis3=dict(gridcolor='rgba(26, 31, 46, 0.5)', showgrid=True),
        yaxis3=dict(gridcolor='rgba(26, 31, 46, 0.5)', showgrid=True),
    )

    st.plotly_chart(fig, use_container_width=True, key="main_chart")
    st.markdown('</div>', unsafe_allow_html=True)

with row1_col2:
    # Quote Panel
    st.markdown("""
    <div class="cyber-panel" style="height: 240px; margin-bottom: 15px;">
        <div class="cyber-panel-corner tl"></div>
        <div class="cyber-panel-corner tr"></div>
        <div class="cyber-panel-corner bl"></div>
        <div class="cyber-panel-corner br"></div>
        <div class="panel-title">QUOTE // {ticker}</div>
    """.format(ticker=st.session_state.selected_ticker), unsafe_allow_html=True)

    quote_data = generate_ohlc_data(st.session_state.selected_ticker, 2)
    last = quote_data.iloc[-1]
    prev = quote_data.iloc[-2]
    change = last['close'] - prev['close']
    change_pct = (change / prev['close']) * 100

    color = "#00ff9d" if change >= 0 else "#ff0040"
    arrow = "▲" if change >= 0 else "▼"

    st.markdown(f"""
    <div style="text-align: center; padding: 10px 0;">
        <div style="font-family: 'Orbitron'; font-size: 2rem; color: {color}; text-shadow: 0 0 20px {color};">
            {last['close']:.2f}
        </div>
        <div style="font-family: 'Share Tech Mono'; font-size: 1rem; color: {color};">
            {arrow} {abs(change):.2f} ({abs(change_pct):.2f}%)
        </div>
    </div>
    <div class="data-grid" style="margin-top: 10px;">
        <div class="data-row"><span class="data-label">OPEN</span><span class="data-value">{last['open']:.2f}</span></div>
        <div class="data-row"><span class="data-label">HIGH</span><span class="data-value">{last['high']:.2f}</span></div>
        <div class="data-row"><span class="data-label">LOW</span><span class="data-value">{last['low']:.2f}</span></div>
        <div class="data-row"><span class="data-label">VOL</span><span class="data-value">{last['volume']:,}</span></div>
        <div class="data-row"><span class="data-label">PREV CLOSE</span><span class="data-value">{prev['close']:.2f}</span></div>
        <div class="data-row"><span class="data-label">52W HIGH</span><span class="data-value">{last['close']*1.15:.2f}</span></div>
        <div class="data-row"><span class="data-label">52W LOW</span><span class="data-value">{last['close']*0.85:.2f}</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Quick Stats Panel
    st.markdown("""
    <div class="cyber-panel" style="height: 240px;">
        <div class="cyber-panel-corner tl"></div>
        <div class="cyber-panel-corner tr"></div>
        <div class="cyber-panel-corner bl"></div>
        <div class="cyber-panel-corner br"></div>
        <div class="panel-title">KEY METRICS</div>
    """, unsafe_allow_html=True)

    metrics = [
        ("MARKET CAP", f"${random.uniform(100, 3000):.1f}B"),
        ("P/E RATIO", f"{random.uniform(15, 45):.1f}"),
        ("EPS (TTM)", f"${random.uniform(2, 15):.2f}"),
        ("DIV YIELD", f"{random.uniform(0.5, 4.5):.2f}%"),
        ("BETA", f"{random.uniform(0.8, 1.8):.2f}"),
        ("AVG VOL", f"{random.uniform(10, 100):.1f}M"),
    ]

    for label, value in metrics:
        st.markdown(f"""
        <div class="data-row">
            <span class="data-label">{label}</span>
            <span class="data-value" style="color: #00f0ff;">{value}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# ROW 2: ECONOMIC CALENDAR + NEWS + MARKET HEATMAP + SECTORS
# =============================================================================
row2_col1, row2_col2, row2_col3 = st.columns([2, 1, 1])

with row2_col1:
    # Economic Calendar (MQL5 Style)
    st.markdown("""
    <div class="cyber-panel" style="height: 400px;">
        <div class="cyber-panel-corner tl"></div>
        <div class="cyber-panel-corner tr"></div>
        <div class="cyber-panel-corner bl"></div>
        <div class="cyber-panel-corner br"></div>
        <div class="panel-title">ECONOMIC CALENDAR // MQL5 FEED</div>
    """, unsafe_allow_html=True)

    # Calendar filters
    cal_filter_col1, cal_filter_col2, cal_filter_col3 = st.columns([1, 1, 1])
    with cal_filter_col1:
        st.selectbox("", ["All Currencies", "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF"], 
                     label_visibility="collapsed", key="cal_currency")
    with cal_filter_col2:
        st.selectbox("", ["All Impact", "High", "Medium", "Low"], 
                     label_visibility="collapsed", key="cal_impact")
    with cal_filter_col3:
        st.selectbox("", ["Today", "Tomorrow", "This Week"], 
                     label_visibility="collapsed", key="cal_period")

    # Calendar header
    st.markdown("""
    <div class="eco-calendar-row" style="border-bottom: 2px solid #00f0ff; font-weight: bold; color: #00f0ff;">
        <div>TIME</div>
        <div>CCY</div>
        <div>IMPACT</div>
        <div>EVENT</div>
        <div style="text-align: right;">FORECAST</div>
    </div>
    """, unsafe_allow_html=True)

    calendar_events = generate_economic_calendar()
    for time, currency, impact, event, forecast in calendar_events:
        impact_class = impact.lower()
        st.markdown(f"""
        <div class="eco-calendar-row">
            <div class="eco-time">{time}</div>
            <div class="eco-currency">{currency}</div>
            <div><span class="eco-impact {impact_class}">{impact}</span></div>
            <div class="eco-event">{event}</div>
            <div class="eco-forecast">{forecast}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with row2_col2:
    # Market Heatmap
    st.markdown("""
    <div class="cyber-panel" style="height: 190px; margin-bottom: 15px;">
        <div class="cyber-panel-corner tl"></div>
        <div class="cyber-panel-corner tr"></div>
        <div class="cyber-panel-corner bl"></div>
        <div class="cyber-panel-corner br"></div>
        <div class="panel-title">MARKET HEATMAP</div>
    """, unsafe_allow_html=True)

    heatmap_data = generate_heatmap_data()
    heatmap_html = '<div class="heatmap-grid">'
    for sym, change in heatmap_data:
        if change > 2:
            bg = f"rgba(0, 255, 157, {min(change/5, 0.8)})"
            color = "#00ff9d"
        elif change > 0:
            bg = f"rgba(0, 255, 157, {change/10})"
            color = "#00ff9d"
        elif change > -2:
            bg = f"rgba(255, 0, 64, {abs(change)/10})"
            color = "#ff0040"
        else:
            bg = f"rgba(255, 0, 64, {min(abs(change)/5, 0.8)})"
            color = "#ff0040"

        heatmap_html += f'<div class="heatmap-cell" style="background: {bg}; color: {color}; border: 1px solid #1a1f2e;"><div style="font-weight: bold;">{sym}</div><div style="font-size: 0.65rem;">{change:+.2f}%</div></div>'
    heatmap_html += '</div>'
    st.markdown(heatmap_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Sector Performance
    st.markdown("""
    <div class="cyber-panel" style="height: 190px;">
        <div class="cyber-panel-corner tl"></div>
        <div class="cyber-panel-corner tr"></div>
        <div class="cyber-panel-corner bl"></div>
        <div class="cyber-panel-corner br"></div>
        <div class="panel-title">SECTOR PERFORMANCE</div>
    """, unsafe_allow_html=True)

    sectors = generate_sector_data()
    for name, value in sectors:
        bar_color = "#00ff9d" if value >= 0 else "#ff0040"
        width = min(abs(value) * 20, 100)
        st.markdown(f"""
        <div class="sector-bar">
            <span class="sector-name">{name}</span>
            <div class="sector-bar-track">
                <div class="sector-bar-fill" style="width: {width}%; background: {bar_color};"></div>
            </div>
            <span class="sector-value" style="color: {bar_color};">{value:+.2f}%</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with row2_col3:
    # News Feed
    st.markdown("""
    <div class="cyber-panel" style="height: 400px;">
        <div class="cyber-panel-corner tl"></div>
        <div class="cyber-panel-corner tr"></div>
        <div class="cyber-panel-corner bl"></div>
        <div class="cyber-panel-corner br"></div>
        <div class="panel-title">NEWS FEED // LIVE</div>
    """, unsafe_allow_html=True)

    news = generate_news_feed()
    for time, source, text in news:
        st.markdown(f"""
        <div class="news-item">
            <span class="news-time">{time}</span>
            <span class="news-source">{source}</span>
            <span class="news-text">{text}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# ROW 3: BOTTOM PANELS - WATCHLIST + TERMINAL LOG + PORTFOLIO
# =============================================================================
row3_col1, row3_col2, row3_col3 = st.columns([1, 1, 1])

with row3_col1:
    # Watchlist
    st.markdown("""
    <div class="cyber-panel" style="height: 300px;">
        <div class="cyber-panel-corner tl"></div>
        <div class="cyber-panel-corner tr"></div>
        <div class="cyber-panel-corner bl"></div>
        <div class="cyber-panel-corner br"></div>
        <div class="panel-title">WATCHLIST // PORTFOLIO</div>
    """, unsafe_allow_html=True)

    watchlist = [
        ("AAPL", 178.35, 1.24), ("MSFT", 412.56, 0.89), ("GOOGL", 142.78, -0.45),
        ("AMZN", 185.23, 2.15), ("TSLA", 245.67, -1.82), ("META", 498.12, 3.45),
        ("NVDA", 875.45, 4.23), ("JPM", 198.34, 0.56)
    ]

    # Table header
    st.markdown("""
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; 
                padding: 8px 0; border-bottom: 2px solid #00f0ff; 
                font-family: 'Orbitron'; font-size: 0.7rem; color: #00f0ff;">
        <div>SYMBOL</div>
        <div style="text-align: right;">PRICE</div>
        <div style="text-align: right;">CHANGE</div>
        <div style="text-align: right;">%CHG</div>
    </div>
    """, unsafe_allow_html=True)

    for sym, base, change_pct in watchlist:
        current = base * (1 + np.random.normal(0, 0.002))
        change = current - base
        change_pct_real = (change / base) * 100
        color = "#00ff9d" if change >= 0 else "#ff0040"
        arrow = "▲" if change >= 0 else "▼"

        st.markdown(f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; 
                    padding: 6px 0; border-bottom: 1px solid #1a1f2e;
                    font-family: 'Share Tech Mono'; font-size: 0.8rem;">
            <div style="color: #00f0ff; font-weight: bold;">{sym}</div>
            <div style="text-align: right; color: #e0e0e0;">{current:.2f}</div>
            <div style="text-align: right; color: {color};">{arrow} {abs(change):.2f}</div>
            <div style="text-align: right; color: {color};">{abs(change_pct_real):.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with row3_col2:
    # Terminal Log
    st.markdown("""
    <div class="cyber-panel" style="height: 300px;">
        <div class="cyber-panel-corner tl"></div>
        <div class="cyber-panel-corner tr"></div>
        <div class="cyber-panel-corner bl"></div>
        <div class="cyber-panel-corner br"></div>
        <div class="panel-title">SYSTEM LOG // TERMINAL</div>
    """, unsafe_allow_html=True)

    if not st.session_state.terminal_logs:
        add_log("DynamiHatch Terminal v2.6.0 initialized", "info")
        add_log("Market data feed connected", "success")
        add_log("MQL5 Economic Calendar API loaded", "success")
        add_log("WebSocket connection established", "info")

    log_html = '<div class="terminal-log">'
    for time, level, msg in st.session_state.terminal_logs[-15:]:
        color_map = {"info": "#00f0ff", "success": "#00ff9d", "warning": "#ff9d00", "error": "#ff0040"}
        color = color_map.get(level, "#00f0ff")
        log_html += f'<div class="log-entry"><span class="log-time">[{time}]</span> <span style="color: {color};">[{level.upper()}]</span> {msg}</div>'
    log_html += '</div>'

    st.markdown(log_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with row3_col3:
    # Market Overview / Indices
    st.markdown("""
    <div class="cyber-panel" style="height: 300px;">
        <div class="cyber-panel-corner tl"></div>
        <div class="cyber-panel-corner tr"></div>
        <div class="cyber-panel-corner bl"></div>
        <div class="cyber-panel-corner br"></div>
        <div class="panel-title">GLOBAL INDICES</div>
    """, unsafe_allow_html=True)

    indices = [
        ("S&P 500", 5123.45, 0.89), ("NASDAQ", 16234.56, 1.45), ("DOW JONES", 38987.23, 0.34),
        ("FTSE 100", 7689.45, -0.23), ("DAX", 17890.12, 1.12), ("NIKKEI 225", 39876.54, 2.34),
        ("HSI", 16876.23, -0.67), ("SHANGHAI", 2987.45, 0.45)
    ]

    for name, base, change_pct in indices:
        current = base * (1 + np.random.normal(0, 0.001))
        change = current - base
        change_pct_real = (change / base) * 100
        color = "#00ff9d" if change >= 0 else "#ff0040"

        st.markdown(f"""
        <div class="data-row" style="font-family: 'Share Tech Mono'; font-size: 0.8rem;">
            <span class="data-label">{name}</span>
            <span style="color: {color};">{current:,.2f} ({change_pct_real:+.2f}%)</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# STATUS BAR
# =============================================================================
st.markdown(f"""
<div class="status-bar">
    <div style="display: flex; gap: 20px; align-items: center;">
        <span><span class="status-indicator"></span> SYSTEM ONLINE</span>
        <span>LATENCY: {random.randint(12, 45)}ms</span>
        <span>DATA: REAL-TIME</span>
    </div>
    <div style="display: flex; gap: 20px;">
        <span>CPU: {random.randint(15, 45)}%</span>
        <span>MEM: {random.randint(40, 70)}%</span>
        <span>CONN: 8/8</span>
    </div>
    <div>
        <span style="color: #00f0ff;">DYNAMIHATCH TERMINAL v2.6.0</span>
        <span style="color: #8899a6; margin-left: 10px;">© 2026</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Auto-refresh indicator
st.markdown("""
<style>
@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
</style>
<div style="position: fixed; bottom: 20px; right: 20px; z-index: 10000;">
    <div style="width: 40px; height: 40px; border: 2px solid #00f0ff; border-top-color: transparent; 
                border-radius: 50%; animation: spin 1s linear infinite; box-shadow: 0 0 15px rgba(0, 240, 255, 0.5);"></div>
</div>
""", unsafe_allow_html=True)
