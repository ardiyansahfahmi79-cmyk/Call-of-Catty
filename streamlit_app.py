# ==============================================================================
# dynamihatch_mct_master.py - MARKET CORE THERMOMETER (MCT)
# Arsitektur Komposit: Deepseek (Math) + Kimi (Smoothing) + Qwen (UI) + Twelve Data
# ==============================================================================

import streamlit as st
import pandas as pd
import pandas_ta as ta
import numpy as np
import requests
from scipy.signal import savgol_filter
import plotly.graph_objects as go

st.set_page_config(page_title="MCT Indicator", layout="wide")

# ==============================================================================
# 1. DATA ENGINEER (Twelve Data dengan Streamlit Secrets)
# ==============================================================================
@st.cache_data(ttl=60, show_spinner="Menarik data XAU/USD dari Twelve Data...")
def fetch_twelvedata_ohlcv(symbol="XAU/USD", interval="15min", outputsize=500):
    """Menarik data OHLCV menggunakan Twelve Data API dengan API Key dari st.secrets"""
    
    # 1. Memanggil API Key dengan aman
    try:
        api_key = st.secrets["TWELVE_DATA_API_KEY"]
    except KeyError:
        st.error("🚨 API Key tidak ditemukan! Pastikan sudah menambahkan TWELVE_DATA_API_KEY di file .streamlit/secrets.toml atau di pengaturan rahasia Streamlit Cloud.")
        return pd.DataFrame()

    # 2. Menyuntikkan API Key ke URL
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Cek apakah limit API tercapai atau ada error dari sisi Twelve Data
        if 'status' in data and data['status'] == 'error':
            st.error(f"Error Twelve Data: {data.get('message', 'Unknown error')}")
            return pd.DataFrame()
            
        if 'values' not in data:
            st.error("Gagal menarik data dari Twelve Data. Struktur respons tidak sesuai.")
            return pd.DataFrame()
            
        df = pd.DataFrame(data['values'])
        # Konversi tipe data
        df['datetime'] = pd.to_datetime(df['datetime'])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            # Fallback jika volume tidak ada di spot forex
            df[col] = df[col].astype(float) if col in df.columns else 0.0
            
        df = df.sort_values('datetime').reset_index(drop=True)
        df.set_index('datetime', inplace=True)
        return df
        
    except Exception as e:
        st.error(f"Error koneksi ke Twelve Data: {str(e)}")
        return pd.DataFrame()

# ==============================================================================
# 2. QUANTITATIVE ANALYST (Deepseek - Logika Komposit MCT)
# ==============================================================================
def calculate_mct_raw(df: pd.DataFrame) -> pd.Series:
    """Menghitung osilator komposit MCT dari Momentum, Volatility, Trend, Volume."""
    lookback = 63
    
    def to_oscillator(raw: pd.Series, lookback: int) -> pd.Series:
        roll_mean = raw.rolling(lookback, min_periods=10).mean()
        roll_std = raw.rolling(lookback, min_periods=10).std()
        z = (raw - roll_mean) / roll_std.replace(0, np.nan)
        return z.clip(-3, 3) / 3.0

    # 1. Momentum (RSI + MACD)
    rsi = ta.rsi(df['close'], length=14) - 50.0
    macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
    macd_hist = macd['MACDh_12_26_9']
    
    mom_signal = (to_oscillator(rsi, lookback) + to_oscillator(macd_hist, lookback)) / 2.0

    # 2. Volatilitas (ATR)
    atr = ta.atr(df['high'], df['low'], df['close'], length=14) / df['close']
    vol_signal = to_oscillator(atr, lookback)

    # 3. Trend (EMA Crossover)
    trend_raw = (ta.ema(df['close'], length=20) - ta.ema(df['close'], length=50)) / df['close']
    trend_signal = to_oscillator(trend_raw, lookback)

    # 4. Agregasi dengan Bobot (Volume diskip sementara jika Twelve Data Spot tidak punya volume valid)
    mct_raw = (0.4 * mom_signal) + (0.2 * vol_signal) + (0.4 * trend_signal)
    
    # Skala -100 ke 100
    return (mct_raw * 100).clip(-100, 100).fillna(0)

# ==============================================================================
# 3. DATA SCIENTIST (Kimi - Savitzky-Golay Smoothing)
# ==============================================================================
def smooth_mct_savgol(data_series: pd.Series, window_length=25, polyorder=3):
    """Menghaluskan data agar melengkung seperti gelombang air tanpa lag."""
    data_array = data_series.to_numpy()
    wl = min(window_length, len(data_array))
    if wl % 2 == 0: wl -= 1
    wl = max(wl, polyorder + 2)
    
    if len(data_array) < wl:
        return data_array # Bypass jika data kurang
        
    smoothed = savgol_filter(data_array, window_length=wl, polyorder=polyorder, mode='interp')
    return np.clip(smoothed, -100, 100)

# ==============================================================================
# 4. FRONTEND DEVELOPER (Qwen - Optimasi UI & Kondisional Trace Plotly)
# ==============================================================================
def render_mct_chart(dates, values):
    """Merender chart dengan warna Biru (>0) dan Merah (<0)."""
    fig = go.Figure()
    
    # Memisahkan array untuk pewarnaan presisi (Teknik Master Architect)
    y_upper = np.where(values >= 0, values, np.nan)
    y_lower = np.where(values <= 0, values, np.nan)

    # Trace Biru (Bullish)
    fig.add_trace(go.Scatter(
        x=dates, y=y_upper, mode='lines',
        line=dict(color="#00E1FF", width=3, shape='spline'),
        fill='tozeroy', fillcolor='rgba(0, 225, 255, 0.1)',
        hoverinfo='y', showlegend=False
    ))

    # Trace Merah (Bearish)
    fig.add_trace(go.Scatter(
        x=dates, y=y_lower, mode='lines',
        line=dict(color="#FF3D71", width=3, shape='spline'),
        fill='tozeroy', fillcolor='rgba(255, 61, 113, 0.1)',
        hoverinfo='y', showlegend=False
    ))

    # Garis Tengah (Zero Line)
    fig.add_hline(y=0, line_dash="solid", line_color="#FFFFFF", line_width=1.5, opacity=0.8)

    # Layout Minimalis Transparan ala Terminal Kuantitatif
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=250,
        margin=dict(l=10, r=40, t=10, b=10), # Margin tipis
        xaxis=dict(visible=False, showgrid=False),
        yaxis=dict(
            range=[-100, 100],
            showgrid=False,
            zeroline=False,
            tickfont=dict(color="#8B9BB4", size=12, family="monospace"),
            tickvals=[-80, -30, 0, 30, 80], # Titik ekstrem sesuai sketsa
            side='right'
        )
    )
    return fig

# ==============================================================================
# EKSEKUSI APLIKASI
# ==============================================================================
st.markdown("<h2 style='color: #C8D8F0; font-family: monospace;'>⚡ MARKET CORE THERMOMETER (MCT) - XAUUSD</h2>", unsafe_allow_html=True)

# 1. Ambil Data
df = fetch_twelvedata_ohlcv(symbol="XAU/USD", interval="15min", outputsize=300)

if not df.empty:
    # 2. Hitung Algoritma Mentah
    mct_raw = calculate_mct_raw(df)
    
    # 3. Haluskan Data
    mct_smooth = smooth_mct_savgol(mct_raw)
    
    # Ambil nilai terakhir untuk display suhu
    current_temp = mct_smooth[-1]
    temp_color = "#00E1FF" if current_temp >= 0 else "#FF3D71"
    
    st.markdown(f"<h3 style='color: {temp_color}; font-family: monospace; text-align: right;'>Suhu Saat Ini: {current_temp:.1f}%</h3>", unsafe_allow_html=True)
    
    # 4. Render Visual
    chart = render_mct_chart(df.index, mct_smooth)
    st.plotly_chart(chart, use_container_width=True, config={'displayModeBar': False})
    
else:
    st.warning("Data belum tersedia. Silakan cek koneksi atau limit API.")
