import streamlit as st
import google.generativeai as genai
import os
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ====================== KONFIGURASI ======================
st.set_page_config(layout="wide", page_title="AeroVulpis - AI Trading Assistant")

# API KEY Gemini
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# ====================== GEMINI FUNCTION ======================
def get_gemini_response(question: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(question)
        return response.text
    except Exception as e:
        return f"❌ Error Gemini: {str(e)}"

# ====================== DATA FUNCTION ======================
def get_current_xauusd_price():
    try:
        ticker = yf.Ticker("GC=F")
        fast_info = ticker.fast_info
        return fast_info.get("lastPrice") or fast_info.get("regularMarketPrice")
    except:
        return None

def get_xauusd_data(period="1y", interval="1d"):
    try:
        ticker = yf.Ticker("GC=F")
        return ticker.history(period=period, interval=interval)
    except:
        return pd.DataFrame()

# ====================== INDICATOR ======================
def add_technical_indicators(df: pd.DataFrame):
    if len(df) < 14:
        return df

    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df

# ====================== CHART ======================
def create_candlestick_chart(df):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="XAUUSD"
    ))

    if "SMA20" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["SMA20"],
            name="SMA 20",
            line=dict(width=2)
        ))

    if "SMA50" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["SMA50"],
            name="SMA 50",
            line=dict(width=2)
        ))

    if "Volume" in df.columns and not df["Volume"].isnull().all():
        fig.add_trace(go.Bar(
            x=df.index,
            y=df["Volume"],
            name="Volume",
            yaxis="y2"
        ))

    fig.update_layout(
        title="Grafik XAUUSD",
        xaxis_title="Waktu",
        yaxis_title="Harga",
        yaxis2=dict(overlaying="y", side="right"),
        xaxis_rangeslider_visible=False,
        height=650
    )

    return fig

# ====================== UI ======================
st.title("🦅 AeroVulpis - AI Trading Assistant")

menu = st.sidebar.radio("Navigasi", ["Dashboard XAUUSD", "Chatbot AI Trading"])

# ====================== DASHBOARD ======================
if menu == "Dashboard XAUUSD":
    st.header("Dashboard XAUUSD")

    if st.button("🔄 Refresh Data"):
        st.rerun()

    period_option = st.selectbox(
        "Periode",
        ["1 hari", "5 hari", "1 bulan", "3 bulan", "6 bulan", "1 tahun", "5 tahun", "Max"],
        index=5
    )

    interval_option = st.selectbox(
        "Interval",
        ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"],
        index=5
    )

    period_map = {
        "1 hari": "1d",
        "5 hari": "5d",
        "1 bulan": "1mo",
        "3 bulan": "3mo",
        "6 bulan": "6mo",
        "1 tahun": "1y",
        "5 tahun": "5y",
        "Max": "max"
    }

    data = get_xauusd_data(period_map[period_option], interval_option)

    if not data.empty:
        data = add_technical_indicators(data)

        current_price = get_current_xauusd_price()
        if current_price:
            st.success(f"Harga Real-Time: {current_price:.2f} USD")

        st.dataframe(data.tail(10))
        st.plotly_chart(create_candlestick_chart(data), use_container_width=True)

        latest = data["Close"].iloc[-1]
        prev = data["Close"].iloc[-2] if len(data) > 1 else latest
        change = latest - prev
        percent = (change / prev) * 100 if prev != 0 else 0

        st.write(f"Harga Terakhir: {latest:.2f}")
        st.write(f"Perubahan: {change:.2f} ({percent:.2f}%)")

        if st.button("🤖 Analisis AI"):
            summary = data.tail(15)[["Open", "High", "Low", "Close"]].to_string()

            prompt = f"""
Analisis XAUUSD:

Harga terakhir: {latest}
Perubahan: {change} ({percent}%)

Data:
{summary}

Berikan:
1. Trend
2. Support & Resistance
3. Rekomendasi Trading
"""

            result = get_gemini_response(prompt)
            st.write(result)

    else:
        st.error("Data gagal diambil")

# ====================== CHATBOT ======================
else:
    st.header("Chatbot AI Trading")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Tanya sesuatu..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        response = get_gemini_response(prompt)

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})