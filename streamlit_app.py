# ==============================================================================
# dynamihatch_mct.py - Market Core Thermometer (MCT) Prototype
# ==============================================================================

import streamlit as st
import streamlit.components.v1 as components
import random

# Pastikan layout 'wide' agar bisa memanjang penuh dari kiri ke kanan
st.set_page_config(page_title="Market Core Thermometer", layout="wide")

# 1. SIMULASI ALGORITMA PYTHON (Menggabungkan Indikator)
def calculate_dominance_score():
    rsi_value = random.uniform(20, 80)
    macd_signal = random.uniform(-5, 5)
    volume_trend = random.uniform(0.5, 1.5)
    
    rsi_normalized = (rsi_value - 50) * 2 
    macd_score = macd_signal * 10
    
    raw_score = (rsi_normalized * 0.6) + (macd_score * 0.4)
    final_score = raw_score * volume_trend
    
    return max(min(final_score, 100), -100)

# Gunakan session state agar slider interaktif untuk prototipe
if 'market_score' not in st.session_state:
    st.session_state.market_score = 0.0

st.markdown("<h2 style='color: #C8D8F0; font-family: monospace; text-align: center;'>⚡ MARKET CORE THERMOMETER (MCT)</h2>", unsafe_allow_html=True)

# Slider untuk mengetes animasi UI (menggantikan data live untuk sementara)
st.session_state.market_score = st.slider(
    "Test Suhu Pasar (Kiri: Sellers/Merah, Kanan: Buyers/Biru):", 
    min_value=-100.0, max_value=100.0, value=st.session_state.market_score, step=1.0
)

score = st.session_state.market_score

# 2. LOGIKA VISUAL (Warna & Intensitas Neon)
glow_intensity = abs(score) / 1.5  # Efek neon diperbesar sedikit agar lebih dramatis
width_percent = abs(score)

if score > 0:
    # Buyers Dominant (Blue)
    blue_width = width_percent
    red_width = 0
    blue_glow = glow_intensity
    red_glow = 0
    status_text = f"BUYERS IN CONTROL (+{score:.1f}%)"
    text_color = "#00E1FF"
elif score < 0:
    # Sellers Dominant (Red)
    blue_width = 0
    red_width = width_percent
    blue_glow = 0
    red_glow = glow_intensity
    status_text = f"SELLERS IN CONTROL ({score:.1f}%)"
    text_color = "#FF3D71"
else:
    # Neutral
    blue_width = 0
    red_width = 0
    blue_glow = 0
    red_glow = 0
    status_text = "MARKET NEUTRAL (0.0%)"
    text_color = "#8B9BB4"

# 3. RENDER HTML & CSS (Tampilan Thermometer Neon Memanjang)
html_thermostat = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    .mct-wrapper {{
        background-color: #070B14;
        padding: 40px;
        border-radius: 12px;
        border: 1px solid #1A2642;
        font-family: 'Share Tech Mono', monospace;
        width: 100%; /* Memaksa elemen memanjang penuh ke kanan */
        box-sizing: border-box;
    }}
    .status-text {{
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 30px;
        letter-spacing: 2px;
        color: {text_color};
        text-shadow: 0 0 {max(blue_glow, red_glow)}px {text_color};
        transition: all 0.3s ease;
    }}
    .thermostat-container {{
        width: 100%;
        height: 60px; /* Dibuat lebih tebal agar terlihat jelas saat memanjang */
        background: #0D1424;
        position: relative;
        border-radius: 6px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.9);
        overflow: hidden;
    }}
    .center-line {{
        width: 6px;
        height: 100%;
        background: #FFFFFF;
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        z-index: 10;
        box-shadow: 0 0 15px #FFF;
    }}
    .bar {{
        height: 100%;
        position: absolute;
        top: 0;
        transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1); /* Animasi lebih smooth */
    }}
    .bar-blue {{
        left: 50%;
        background: linear-gradient(90deg, #0D1424, #00E1FF);
        width: {blue_width / 2}%;
        box-shadow: inset 0 0 15px rgba(0,225,255,0.5), 0 0 {blue_glow * 1.5}px #00E1FF;
    }}
    .bar-red {{
        right: 50%;
        background: linear-gradient(270deg, #0D1424, #FF3D71);
        width: {red_width / 2}%;
        box-shadow: inset 0 0 15px rgba(255,61,113,0.5), 0 0 {red_glow * 1.5}px #FF3D71;
    }}
    .scale-markers {{
        display: flex;
        justify-content: space-between;
        margin-top: 15px;
        color: #8B9BB4;
        font-size: 14px;
        font-weight: bold;
    }}
</style>

<div class="mct-wrapper">
    <div class="status-text">{status_text}</div>
    
    <div class="thermostat-container">
        <div class="center-line"></div>
        <div class="bar bar-blue"></div>
        <div class="bar bar-red"></div>
    </div>
    
    <div class="scale-markers">
        <span>-100 (BEARISH)</span>
        <span>0 (NEUTRAL)</span>
        <span>+100 (BULLISH)</span>
    </div>
</div>
"""

# Render dengan tinggi yang disesuaikan agar tidak terpotong
components.html(html_thermostat, height=350)
