"""AeroVulpis v3.0 — aplikasi Streamlit historis dengan SDK Gemini modern."""

from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from google import genai


st.set_page_config(
    layout="wide",
    page_title="AeroVulpis v3.0 - Trading Signal Edition",
    page_icon="A",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');
    :root { --green:#00ff88; --red:#ff2a6d; --blue:#00d4ff; --glass:rgba(255,255,255,.05); --line:rgba(255,255,255,.1); }
    .stApp { background:radial-gradient(circle at top right,#0a0e17,#020408); color:#e0e0e0; }
    .glass-card { background:var(--glass); backdrop-filter:blur(12px); border:1px solid var(--line); border-radius:15px; padding:20px; box-shadow:0 8px 32px rgba(0,0,0,.8); margin-bottom:20px; }
    .main-title { font-family:Orbitron,sans-serif; font-size:clamp(2.4rem,6vw,3.7rem); font-weight:700; background:linear-gradient(90deg,var(--green),var(--blue)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; text-align:center; margin-bottom:5px; }
    .digital-font { font-family:Orbitron,sans-serif; color:var(--green); text-shadow:0 0 10px var(--green); }.rajdhani-font { font-family:Rajdhani,sans-serif; }
    .stButton>button { background:linear-gradient(145deg,#00d4ff,#0055ff)!important; border:0!important; color:white!important; font-family:Orbitron,sans-serif!important; font-weight:700!important; border-radius:10px!important; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def gemini_client() -> genai.Client | None:
    """Membuat klien bila Google API key tersedia sebagai secret Streamlit."""
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    return genai.Client(api_key=api_key) if api_key else None


def gemini_response(question: str, context: str) -> str:
    client = gemini_client()
    if client is None:
        return "Chatbot belum dikonfigurasi. Tambahkan `GOOGLE_API_KEY` pada Secrets Streamlit, lalu reboot aplikasi."
    prompt = f"""Kamu adalah AeroVulpis v3.0, asisten riset pasar berbahasa Indonesia.
Jawab ringkas, jelas, dan jangan menjanjikan keuntungan. Selalu jelaskan bahwa ini edukasi,
bukan nasihat finansial personal.

Konteks data: {context}
Pertanyaan: {question}"""
    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text or "Gemini tidak mengembalikan teks jawaban."
    except Exception as error:
        return f"Chatbot Gemini tidak dapat merespons saat ini: {error}"


@st.cache_data(ttl=90, show_spinner=False)
def market_data(symbol: str) -> tuple[dict[str, float] | None, pd.DataFrame]:
    try:
        daily = yf.Ticker(symbol).history(period="5d", interval="1d", auto_adjust=False)
        hourly = yf.Ticker(symbol).history(period="1mo", interval="1h", auto_adjust=False)
        if daily.empty:
            return None, pd.DataFrame()
        item = daily.iloc[-1]
        snapshot = {"open": float(item["Open"]), "high": float(item["High"]), "low": float(item["Low"]), "close": float(item["Close"])}
        return snapshot, hourly.sort_index().dropna()
    except Exception:
        return None, pd.DataFrame()


def indicators(data: pd.DataFrame) -> pd.DataFrame:
    if len(data) < 30:
        return data
    data = data.copy()
    data["SMA20"] = data["Close"].rolling(20).mean()
    data["SMA50"] = data["Close"].rolling(50).mean()
    delta = data["Close"].diff()
    up = delta.clip(lower=0).rolling(14).mean()
    down = (-delta.clip(upper=0)).rolling(14).mean().replace(0, float("nan"))
    data["RSI"] = 100 - (100 / (1 + up / down))
    fast = data["Close"].ewm(span=12, adjust=False).mean()
    slow = data["Close"].ewm(span=26, adjust=False).mean()
    data["MACD"] = fast - slow
    data["Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()
    return data


INSTRUMENTS = {
    "Forex": {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "USDJPY=X", "AUD/USD": "AUDUSD=X", "USD/CHF": "USDCHF=X"},
    "Komoditas": {"Gold (XAUUSD)": "GC=F", "WTI Crude Oil": "CL=F", "Silver": "SI=F", "Brent Oil": "BZ=F"},
    "Saham AS": {"Apple (AAPL)": "AAPL", "Microsoft (MSFT)": "MSFT", "NVIDIA (NVDA)": "NVDA", "Amazon (AMZN)": "AMZN"},
    "Saham Indonesia": {"BBCA (BCA)": "BBCA.JK", "BBRI (BRI)": "BBRI.JK", "TLKM (Telkom)": "TLKM.JK", "BMRI (Mandiri)": "BMRI.JK"},
}


def technical_bias(data: pd.DataFrame) -> tuple[str, str, list[str]]:
    latest = data.iloc[-1]
    score, reasons = 0, []
    if latest.get("RSI", 50) < 30:
        score += 2; reasons.append("RSI rendah; konfirmasi momentum diperlukan.")
    elif latest.get("RSI", 50) > 70:
        score -= 2; reasons.append("RSI tinggi; risiko pullback perlu diperhatikan.")
    if latest.get("MACD", 0) > latest.get("Signal", 0):
        score += 1; reasons.append("MACD berada di atas garis sinyal.")
    else:
        score -= 1; reasons.append("MACD berada di bawah garis sinyal.")
    if latest["Close"] > latest.get("SMA20", latest["Close"]):
        score += 1; reasons.append("Harga berada di atas SMA20.")
    else:
        score -= 1; reasons.append("Harga berada di bawah SMA20.")
    score += 1 if latest.get("SMA20", 0) > latest.get("SMA50", 0) else -1
    if score >= 2:
        return "BUY", "#00ff88", reasons
    if score <= -2:
        return "SELL", "#ff2a6d", reasons
    return "NEUTRAL", "#00d4ff", reasons


st.markdown('<h1 class="main-title">AERO VULPIS v3.0</h1>', unsafe_allow_html=True)
st.caption("Trading Signal Edition · Data publik · Edukasi, bukan nasihat finansial personal")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Sistem AeroVulpis v3.0 aktif. Pilih instrumen dan ajukan pertanyaan market."}]

st.sidebar.markdown('<h2 class="digital-font" style="text-align:center">AeroVulpis</h2>', unsafe_allow_html=True)
category = st.sidebar.selectbox("Pilih Kategori", list(INSTRUMENTS))
name = st.sidebar.selectbox("Pilih Instrumen", list(INSTRUMENTS[category]))
symbol = INSTRUMENTS[category][name]
section = st.sidebar.radio("Navigasi Sistem", ["Live Dashboard", "Trading Signals", "Market History", "Chatbot AI Trading"])
snapshot, raw_data = market_data(symbol)
data = indicators(raw_data)

if section == "Live Dashboard":
    left, right = st.columns([2, 1])
    with left:
        if st.button("REFRESH HARGA", use_container_width=True):
            st.cache_data.clear(); st.rerun()
        if snapshot and not data.empty:
            price = snapshot["close"]
            previous = data["Close"].iloc[-2] if len(data) > 1 else price
            color = "#00ff88" if price >= previous else "#ff2a6d"
            st.markdown(f'<div class="glass-card" style="text-align:center"><p class="rajdhani-font">HARGA {name} TERAKHIR</p><h1 class="digital-font" style="font-size:42px;color:{color}">{price:,.4f}</h1></div>', unsafe_allow_html=True)
            chart = go.Figure(go.Scatter(x=data.index, y=data["Close"], mode="lines", line=dict(color=color, width=3), name="Harga"))
            chart.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=440, margin=dict(l=0, r=0, t=25, b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})
        else:
            st.warning("Data belum tersedia untuk instrumen ini. Coba refresh kembali.")
    with right:
        st.markdown('<p class="digital-font">TECHNICAL SUMMARY</p>', unsafe_allow_html=True)
        if not data.empty:
            latest = data.iloc[-1]
            st.markdown(f'<div class="glass-card"><p class="rajdhani-font">RSI (14): <b>{latest.get("RSI", 50):.2f}</b></p><p class="rajdhani-font">MACD: <b>{latest.get("MACD", 0):.4f}</b></p><p class="rajdhani-font">SMA 20: <b>{latest.get("SMA20", 0):,.2f}</b></p></div>', unsafe_allow_html=True)
        st.info("Gunakan analisis sebagai bahan riset. Selalu tentukan risiko sendiri.")

elif section == "Trading Signals":
    st.markdown('<h2 class="digital-font">Trading Signals</h2>', unsafe_allow_html=True)
    if len(data) >= 30:
        label, color, reasons = technical_bias(data)
        left, right = st.columns(2)
        with left:
            st.markdown(f'<div class="glass-card" style="text-align:center;border-top:5px solid {color}"><p class="rajdhani-font">BIAS TEKNIS</p><h1 class="digital-font" style="color:{color};font-size:50px">{label}</h1><p class="rajdhani-font">Berdasarkan RSI, MACD, SMA20, dan SMA50</p></div>', unsafe_allow_html=True)
        with right:
            st.markdown('<div class="glass-card"><p class="digital-font">KONTEKS ANALISIS</p>', unsafe_allow_html=True)
            for reason in reasons:
                st.markdown(f'<p class="rajdhani-font">• {reason}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.info("Bias teknis bersifat edukatif, bukan instruksi transaksi.")
    else:
        st.warning("Data belum cukup untuk menghitung indikator.")

elif section == "Market History":
    st.markdown('<h2 class="digital-font">Market History</h2>', unsafe_allow_html=True)
    if snapshot:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("OPEN", f'{snapshot["open"]:,.2f}'); c2.metric("HIGH", f'{snapshot["high"]:,.2f}'); c3.metric("LOW", f'{snapshot["low"]:,.2f}'); c4.metric("CLOSE", f'{snapshot["close"]:,.2f}')
    if not raw_data.empty:
        st.dataframe(raw_data[["Open", "High", "Low", "Close", "Volume"]].sort_index(ascending=False).head(30), use_container_width=True)

else:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Kirim pertanyaan market ke AeroVulpis..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Menganalisis konteks market..."):
                price = snapshot["close"] if snapshot else "tidak tersedia"
                context = f"Instrumen: {name}. Harga terakhir publik: {price}. Waktu: {datetime.now().strftime('%d %b %Y %H:%M')}."
                answer = gemini_response(prompt, context)
                st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('---')
st.markdown('<div style="text-align:center;padding:20px;opacity:.8"><p class="rajdhani-font" style="font-style:italic;font-size:18px;color:#ccc">"Disiplin adalah kunci, emosi adalah musuh. Tetap tenang dan percaya pada sistem."</p><p class="digital-font">— Fahmi (Pencipta AeroVulpis)</p><p style="font-size:10px;color:#444;letter-spacing:2px">DYNAMIHATCH IDENTITY • v3.0 TRADING SIGNAL</p></div>', unsafe_allow_html=True)
