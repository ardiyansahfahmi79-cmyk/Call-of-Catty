import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import pytz

# ==============================================================================
# PAGE CONFIG
# ==============================================================================
st.set_page_config(
    page_title="Aerovulpis Pro Terminal",
    page_icon="🔷",
    layout="wide"
)

# ==============================================================================
# CSS STYLING (Cybertech Theme)
# ==============================================================================
st.markdown("""
<style>
/* --- DESIGN TOKENS --- */
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

/* --- BACKGROUND --- */
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

/* --- FORCE HORIZONTAL SCROLL ON MOBILE --- */
[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    gap: 10px !important;
    padding: 5px 0 !important;
}
[data-testid="column"] {
    min-width: 280px !important;
    flex-shrink: 0 !important;
}
[data-testid="column"]:nth-of-type(1) { min-width: 260px; }
[data-testid="column"]:nth-of-type(2) { min-width: 380px; }
[data-testid="column"]:nth-of-type(3) { min-width: 280px; }

/* --- PANEL STYLING --- */
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

/* --- SCAN LINE EFFECT --- */
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
    background: linear-gradient(
        to bottom,
        transparent,
        rgba(0,238,255,0.022),
        rgba(0,238,255,0.048),
        rgba(0,238,255,0.022),
        transparent
    );
    animation: scanDown 9s linear infinite;
}
@keyframes scanDown {
    from { transform: translateY(-60px); }
    to { transform: translateY(100%); }
}

/* --- METRIC STYLING --- */
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
.cyber-bar-fill {
    height: 100%;
    border-radius: 1px;
}
.cyber-bar-fill.bullish { background: linear-gradient(90deg, #00EEFF, #00FF9D); }
.cyber-bar-fill.bearish { background: linear-gradient(90deg, #8B5CF6, #FF3D71); }
.cyber-bar-fill.neutral { background: #00EEFF; }

.cyber-divider {
    height: 1px;
    background: #162035;
    margin: 8px 0;
}

/* --- ANALYSIS CARD --- */
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
# HEADER (Tanpa Emoji, Tanpa Jam)
# ==============================================================================
st.markdown("""
<div style="
    flex-shrink: 0;
    height: 58px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    background: rgba(7,12,24,0.97);
    border-bottom: 1px solid #162035;
    position: relative;
    z-index: 30;
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
# DATA DUMMY UNTUK CHART DXY
# ==============================================================================
def create_dxy_chart():
    # Generate dummy data untuk DXY
    dates = pd.date_range(end=datetime.now(pytz.UTC), periods=100, freq='H')
    # Simulasi harga DXY dengan trend + noise
    base = 105.5
    values = []
    for i in range(100):
        trend = i * 0.005
        noise = np.random.normal(0, 0.15)
        values.append(base + trend + noise)
    
    # Hitung RSI sederhana (dummy)
    rsi_values = [50 + (v - values[0]) * 2 for v in values]
    rsi_values = [max(20, min(80, v)) for v in rsi_values]
    
    fig = go.Figure()
    
    # DXY Line Chart
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines',
        name='DXY',
        line=dict(color='#00EEFF', width=2),
        fill='tozeroy',
        fillcolor='rgba(0,238,255,0.05)'
    ))
    
    # RSI Overlay (secondary y-axis)
    fig.add_trace(go.Scatter(
        x=dates,
        y=rsi_values,
        mode='lines',
        name='RSI',
        line=dict(color='#8B5CF6', width=1.5, dash='dot'),
        yaxis='y2'
    ))
    
    # Level 70 dan 30 untuk RSI
    fig.add_hline(y=70, line_dash="dash", line_color="#FF3D71", opacity=0.3, yref="y2")
    fig.add_hline(y=30, line_dash="dash", line_color="#00FF9D", opacity=0.3, yref="y2")
    fig.add_hline(y=50, line_dash="dot", line_color="#4B6A8A", opacity=0.2, yref="y2")
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=280,
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.03)',
            showticklabels=True,
            tickfont=dict(color='#4B6A8A', size=9)
        ),
        yaxis=dict(
            title='DXY',
            titlefont=dict(color='#00EEFF', size=9),
            showgrid=True,
            gridcolor='rgba(255,255,255,0.03)',
            tickfont=dict(color='#4B6A8A', size=9)
        ),
        yaxis2=dict(
            title='RSI',
            titlefont=dict(color='#8B5CF6', size=9),
            overlaying='y',
            side='right',
            range=[0, 100],
            showgrid=False,
            tickfont=dict(color='#4B6A8A', size=9)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='#4B6A8A', size=9)
        ),
        hovermode='x unified'
    )
    
    return fig

# ==============================================================================
# WATCHLIST DATA (DUMMY)
# ==============================================================================
watchlist_data = {
    "Forex": [
        {"pair": "EURUSD", "price": "1.1613", "change": "+0.04%", "direction": "bullish"},
        {"pair": "GBPUSD", "price": "1.3430", "change": "+0.03%", "direction": "bullish"},
        {"pair": "USDJPY", "price": "160.29", "change": "-0.05%", "direction": "bearish"},
    ],
    "Futures": [
        {"pair": "USOIL", "price": "75.13", "change": "-1.93%", "direction": "bearish"},
        {"pair": "UKOIL", "price": "78.66", "change": "-0.84%", "direction": "bearish"},
        {"pair": "GOLD", "price": "4,331.75", "change": "-0.03%", "direction": "bearish"},
    ],
    "Crypto": [
        {"pair": "BTCUSDT", "price": "65,790.00", "change": "+0.18%", "direction": "bullish"},
        {"pair": "ETHUSD", "price": "1,791.6", "change": "+0.02%", "direction": "bullish"},
    ]
}

# ==============================================================================
# LAYOUT: 3 KOLOM UTAMA
# ==============================================================================
col_kiri, col_tengah, col_kanan = st.columns([1.2, 2, 1])

# ==============================================================================
# KOLOM KIRI: KALENDER EKONOMI (TEKS STATIS)
# ==============================================================================
with col_kiri:
    st.markdown("""
    <div class="cyber-panel">
        <div class="cyber-header">
            <span class="cyber-title">Economic Calendar</span>
            <span class="cyber-badge">Real-Time</span>
        </div>
        <div class="cyber-body" style="padding: 12px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #C8D8F0; max-height: 600px; overflow-y: auto;">
    """, unsafe_allow_html=True)
    
    # Kalender teks statis
    st.markdown("""
    <div style="border-bottom: 1px solid #162035; padding: 8px 0;">
        <span style="color: #00FF9D;">[HIGH]</span>
        <span style="color: #4B6A8A;">15:30 WIB</span>
        <span style="color: #C8D8F0; font-weight: 600;">Fed Interest Rate Decision</span>
        <div style="color: #4B6A8A; font-size: 10px; margin-top: 2px;">Prev: 5.50% | Forecast: 5.50%</div>
    </div>
    <div style="border-bottom: 1px solid #162035; padding: 8px 0;">
        <span style="color: #00FF9D;">[HIGH]</span>
        <span style="color: #4B6A8A;">16:30 WIB</span>
        <span style="color: #C8D8F0; font-weight: 600;">ECB Press Conference</span>
        <div style="color: #4B6A8A; font-size: 10px; margin-top: 2px;">Prev: 4.50% | Forecast: 4.50%</div>
    </div>
    <div style="border-bottom: 1px solid #162035; padding: 8px 0;">
        <span style="color: #FF3D71;">[MEDIUM]</span>
        <span style="color: #4B6A8A;">10:00 WIB</span>
        <span style="color: #C8D8F0; font-weight: 600;">BOJ Policy Rate</span>
        <div style="color: #4B6A8A; font-size: 10px; margin-top: 2px;">Prev: -0.10% | Forecast: -0.10%</div>
    </div>
    <div style="border-bottom: 1px solid #162035; padding: 8px 0;">
        <span style="color: #FF3D71;">[MEDIUM]</span>
        <span style="color: #4B6A8A;">21:30 WIB</span>
        <span style="color: #C8D8F0; font-weight: 600;">US Crude Oil Inventories</span>
        <div style="color: #4B6A8A; font-size: 10px; margin-top: 2px;">Prev: +1.2M | Forecast: +0.8M</div>
    </div>
    <div style="padding: 8px 0;">
        <span style="color: #FF3D71;">[MEDIUM]</span>
        <span style="color: #4B6A8A;">13:00 WIB</span>
        <span style="color: #C8D8F0; font-weight: 600;">UK Retail Sales</span>
        <div style="color: #4B6A8A; font-size: 10px; margin-top: 2px;">Prev: +0.5% | Forecast: +0.3%</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid #162035;">
        <a href="https://www.fxstreet.com/economic-calendar" target="_blank" style="color: #00EEFF; font-family: 'Share Tech Mono', monospace; font-size: 9px; letter-spacing: 1px; text-decoration: none;">
            [OPEN FULL CALENDAR]
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
        <div class="scan-wrap"><div class="scan-line" style="animation-delay: 0s;"></div></div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# KOLOM TENGAH: CHART DXY + MT5
# ==============================================================================
with col_tengah:
    # --- DXY Chart dengan Plotly ---
    st.markdown("""
    <div class="cyber-panel">
        <div class="cyber-header">
            <span class="cyber-title">DXY & RSI Analysis</span>
            <span class="cyber-badge">Real-Time</span>
        </div>
        <div class="cyber-body" style="padding: 5px;">
    """, unsafe_allow_html=True)
    
    fig = create_dxy_chart()
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("""
        </div>
        <div class="scan-wrap"><div class="scan-line" style="animation-delay: 3s;"></div></div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- MT5 Web Terminal (iframe) ---
    st.markdown("""
    <div class="cyber-panel" style="margin-top: 10px;">
        <div class="cyber-header">
            <span class="cyber-title">MT5 Execution Terminal</span>
            <span class="cyber-badge">Prototype</span>
        </div>
        <div class="cyber-body" style="padding: 0; height: 320px; overflow: hidden;">
            <iframe src="https://metatraderweb.app/trade" 
                    style="width: 100%; height: 100%; border: none;" 
                    allow="fullscreen; autoplay">
            </iframe>
        </div>
        <div class="scan-wrap"><div class="scan-line" style="animation-delay: 3s;"></div></div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# KOLOM KANAN: AI SIGNAL FEED
# ==============================================================================
with col_kanan:
    st.markdown("""
    <div class="cyber-panel">
        <div class="cyber-header">
            <span class="cyber-title">AI Signal Feed</span>
            <span class="cyber-badge">Contoh AI</span>
        </div>
        <div class="cyber-body" style="max-height: 600px; overflow-y: auto; padding: 12px;">
    """, unsafe_allow_html=True)
    
    # USD Sentiment
    st.markdown("""
    <div class="cyber-metric">
        <div class="cyber-metric-label">USD Sentiment</div>
        <div class="cyber-metric-value bullish">BULLISH</div>
        <div class="cyber-metric-conf">Confidence: 78%</div>
        <div class="cyber-bar"><div class="cyber-bar-fill bullish" style="width:78%;"></div></div>
    </div>
    """, unsafe_allow_html=True)
    
    # EUR Sentiment
    st.markdown("""
    <div class="cyber-metric">
        <div class="cyber-metric-label">EUR Sentiment</div>
        <div class="cyber-metric-value bearish">BEARISH</div>
        <div class="cyber-metric-conf">Confidence: 64%</div>
        <div class="cyber-bar"><div class="cyber-bar-fill bearish" style="width:64%;"></div></div>
    </div>
    """, unsafe_allow_html=True)
    
    # XAU Sentiment
    st.markdown("""
    <div class="cyber-metric">
        <div class="cyber-metric-label">XAU Sentiment</div>
        <div class="cyber-metric-value neutral">NEUTRAL-BEAR</div>
        <div class="cyber-metric-conf">Confidence: 51%</div>
        <div class="cyber-bar"><div class="cyber-bar-fill neutral" style="width:51%;"></div></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="cyber-divider"></div>', unsafe_allow_html=True)
    
    # Analysis Cards
    st.markdown("""
    <div class="analysis-card">
        <div class="analysis-title">US CPI Data Release</div>
        <div class="analysis-text">Inflasi AS tercatat lebih tinggi dari konsensus. Penguatan USD terjadi secara instan. RSI DXY di zona 58, momentum bullish masih solid.</div>
        <div style="margin-top: 8px; display: flex; gap: 5px; flex-wrap: wrap;">
            <span class="cyber-tag sell">SELL EURUSD</span>
            <span class="cyber-tag buy">BUY USDJPY</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="analysis-card">
        <div class="analysis-title">XAUUSD Technical Read</div>
        <div class="analysis-text">Tekanan jual XAU dipicu penguatan yield obligasi AS. Level 1985-1990 zona support kritis. Pantau data ADP untuk konfirmasi arah selanjutnya.</div>
        <div style="margin-top: 8px; display: flex; gap: 5px; flex-wrap: wrap;">
            <span class="cyber-tag watch">WATCH 1985</span>
            <span class="cyber-tag sell">BIAS SELL</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="analysis-card">
        <div class="analysis-title">DXY Momentum Breakout</div>
        <div class="analysis-text">Breakout dari descending channel mingguan telah terkonfirmasi. Target resistance berikutnya di 107.20. RSI H4 belum overbought.</div>
        <div style="margin-top: 8px; display: flex; gap: 5px; flex-wrap: wrap;">
            <span class="cyber-tag buy">MOMENTUM BULL</span>
            <span class="cyber-tag watch">TARGET 107.20</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
        <div class="scan-wrap"><div class="scan-line" style="animation-delay: 6s;"></div></div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# BAGIAN BAWAH: TRADE SETUPS (4 kolom)
# ==============================================================================
st.markdown("""
<div class="cyber-panel" style="margin-top: 10px;">
    <div class="cyber-header">
        <span class="cyber-title">Active Trade Setups</span>
        <span class="cyber-badge">Contoh Data — Prototype</span>
    </div>
    <div class="cyber-body" style="padding: 12px;">
""", unsafe_allow_html=True)

# Buat 4 kolom untuk trade setups
col_s1, col_s2, col_s3, col_s4 = st.columns(4)

with col_s1:
    st.markdown("""
    <div style="background: #111D35; border: 1px solid #162035; border-radius: 8px; padding: 10px; position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #8B5CF6, #FF3D71);"></div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 9px;">
            <span style="font-family: 'Share Tech Mono', monospace; font-size: 13px; color: #C8D8F0; letter-spacing: 2px;">EURUSD</span>
            <span style="font-family: 'Share Tech Mono', monospace; font-size: 8px; letter-spacing: 1px; padding: 2px 7px; border-radius: 3px; background: rgba(255,61,113,0.12); color: #FF3D71; border: 1px solid rgba(255,61,113,0.25);">SELL</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px;">
            <div style="grid-column: 1 / -1; background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">Entry</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #C8D8F0;">1.08420</div>
            </div>
            <div style="background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">TP 1</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #00FF9D;">1.07950</div>
            </div>
            <div style="background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">TP 2</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #00FF9D;">1.07500</div>
            </div>
            <div style="grid-column: 1 / -1; background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">Stop Loss</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #FF3D71;">1.08900</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_s2:
    st.markdown("""
    <div style="background: #111D35; border: 1px solid #162035; border-radius: 8px; padding: 10px; position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #00EEFF, #00FF9D);"></div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 9px;">
            <span style="font-family: 'Share Tech Mono', monospace; font-size: 13px; color: #C8D8F0; letter-spacing: 2px;">USDJPY</span>
            <span style="font-family: 'Share Tech Mono', monospace; font-size: 8px; letter-spacing: 1px; padding: 2px 7px; border-radius: 3px; background: rgba(0,255,157,0.12); color: #00FF9D; border: 1px solid rgba(0,255,157,0.25);">BUY</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px;">
            <div style="grid-column: 1 / -1; background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">Entry</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #C8D8F0;">149.820</div>
            </div>
            <div style="background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">TP 1</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #00FF9D;">150.500</div>
            </div>
            <div style="background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">TP 2</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #00FF9D;">151.200</div>
            </div>
            <div style="grid-column: 1 / -1; background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">Stop Loss</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #FF3D71;">149.200</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_s3:
    st.markdown("""
    <div style="background: #111D35; border: 1px solid #162035; border-radius: 8px; padding: 10px; position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #8B5CF6, #FF3D71);"></div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 9px;">
            <span style="font-family: 'Share Tech Mono', monospace; font-size: 13px; color: #C8D8F0; letter-spacing: 2px;">XAUUSD</span>
            <span style="font-family: 'Share Tech Mono', monospace; font-size: 8px; letter-spacing: 1px; padding: 2px 7px; border-radius: 3px; background: rgba(255,61,113,0.12); color: #FF3D71; border: 1px solid rgba(255,61,113,0.25);">SELL</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px;">
            <div style="grid-column: 1 / -1; background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">Entry</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #C8D8F0;">2,014.50</div>
            </div>
            <div style="background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">TP 1</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #00FF9D;">2,000.00</div>
            </div>
            <div style="background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">TP 2</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #00FF9D;">1,990.00</div>
            </div>
            <div style="grid-column: 1 / -1; background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">Stop Loss</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #FF3D71;">2,025.00</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_s4:
    st.markdown("""
    <div style="background: #111D35; border: 1px solid #162035; border-radius: 8px; padding: 10px; position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #00EEFF, #00FF9D);"></div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 9px;">
            <span style="font-family: 'Share Tech Mono', monospace; font-size: 13px; color: #C8D8F0; letter-spacing: 2px;">DXY</span>
            <span style="font-family: 'Share Tech Mono', monospace; font-size: 8px; letter-spacing: 1px; padding: 2px 7px; border-radius: 3px; background: rgba(0,255,157,0.12); color: #00FF9D; border: 1px solid rgba(0,255,157,0.25);">LONG BIAS</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px;">
            <div style="grid-column: 1 / -1; background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">Watch Level</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #C8D8F0;">105.840</div>
            </div>
            <div style="background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">Target 1</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #00FF9D;">106.500</div>
            </div>
            <div style="background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">Target 2</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #00FF9D;">107.200</div>
            </div>
            <div style="grid-column: 1 / -1; background: rgba(0,0,0,0.2); border: 1px solid #162035; border-radius: 5px; padding: 5px 7px;">
                <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #243450; letter-spacing: 1px; text-transform: uppercase;">Invalidation</div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #FF3D71;">104.900</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
    </div>
    <div class="scan-wrap"><div class="scan-line" style="animation-delay: 6s;"></div></div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# BAGIAN BAWAH: WATCHLIST HARGA (dari iframe)
# ==============================================================================
st.markdown("""
<div class="cyber-panel" style="margin-top: 10px;">
    <div class="cyber-header">
        <span class="cyber-title">Watchlist Prices</span>
        <span class="cyber-badge">Live</span>
    </div>
    <div class="cyber-body" style="padding: 0; height: 320px; overflow: hidden;">
        <iframe src="https://metatraderweb.app/watchlist" 
                style="width: 100%; height: 100%; border: none;" 
                allow="fullscreen; autoplay">
        </iframe>
    </div>
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