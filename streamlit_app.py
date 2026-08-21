"""Call-of-Catty — prototipe chatbot market mandiri untuk Aerovulpis.

Chat mendeteksi instrumen dari pertanyaan pengguna. Data diproses Python
melalui market_data.py; persona hanya mengubah gaya penjelasan, bukan angkanya.
"""

from __future__ import annotations

from datetime import timezone
import html
import re
import time

import plotly.graph_objects as go
import streamlit as st

from market_chat import build_reply, follow_up_prompts
from market_data import MarketSnapshot, detect_instruments, fetch_market_snapshot, normalized_comparison


APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Share+Tech+Mono&display=swap');
:root { --ink:#050609; --panel:#0d1016; --line:#262b35; --soft:#9098a8; --text:#f5f6f8; --cyan:#18d9f5; --green:#31d47a; --red:#a62127; --yellow:#f0c447; }
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background:var(--ink) !important; color:var(--text) !important; font-family:Manrope,sans-serif; }
.block-container { max-width:1000px; padding:1.4rem 1rem 7rem; }
[data-testid="stSidebar"] { background:#080a0f; border-right:1px solid var(--line); }
.brand-kicker,.mono { font-family:'Share Tech Mono',monospace; letter-spacing:1.8px; }
.brand-kicker { color:var(--cyan); font-size:.66rem; }
.title-row { display:flex; justify-content:space-between; align-items:flex-end; border-bottom:1px solid var(--line); padding:0 0 1rem; margin-bottom:1.1rem; }
.title-row h1 { font-size:clamp(1.55rem,6vw,2.65rem); margin:.35rem 0 0; letter-spacing:-1.5px; }
.engine { color:#aab2c0; font: .64rem 'Share Tech Mono',monospace; text-align:right; }
.engine b { color:var(--green); }
.persona-card { border:1px solid var(--line); background:linear-gradient(140deg,#11141b,#090b10); padding:15px; border-radius:14px; min-height:124px; }
.persona-card.active { border-color:var(--cyan); box-shadow:0 0 0 1px rgba(24,217,245,.16), 0 0 28px rgba(24,217,245,.08); }
.persona-card h3 { font-size:1rem; margin:0 0 8px; }.persona-card p { color:#9da6b7; font-size:.78rem; line-height:1.55; margin:0; }
.market-chip { display:inline-flex; gap:8px; align-items:center; border:1px solid var(--line); border-radius:999px; padding:6px 10px; color:#c8ced8; font:.65rem 'Share Tech Mono',monospace; margin:3px 4px 0 0; }
.market-chip .dot { width:7px; height:7px; background:var(--green); border-radius:50%; box-shadow:0 0 12px var(--green); }
.reply-card { background:linear-gradient(135deg,rgba(166,33,39,.22),rgba(13,16,22,.98) 35%); border:1px solid rgba(166,33,39,.6); border-radius:20px 20px 20px 4px; padding:17px 18px; margin:10px 0 12px; line-height:1.75; }
.reply-card.formal { background:linear-gradient(135deg,rgba(24,217,245,.12),rgba(13,16,22,.98) 38%); border-color:rgba(24,217,245,.55); }
.chat-label { color:#9ba5b6; font:.62rem 'Share Tech Mono',monospace; letter-spacing:1.5px; margin:18px 0 4px; }
.data-proof { display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px; background:#0a0d12; border:1px solid var(--line); padding:11px 13px; border-radius:10px; color:#b5bdcb; font:.66rem 'Share Tech Mono',monospace; }
.metric-box { border-left:2px solid var(--cyan); padding:8px 0 8px 11px; }.metric-box .name { color:#7e899a; font:.58rem 'Share Tech Mono',monospace; letter-spacing:1.2px; }.metric-box .val { font-weight:800; font-size:1rem; margin-top:4px; }
.signal-buy { color:var(--green); }.signal-sell { color:#ff6672; }.signal-neutral { color:var(--yellow); }
div[data-testid="stChatInput"] { position:fixed; bottom:0; left:0; right:0; z-index:100; background:linear-gradient(transparent,#050609 18%); padding:1rem max(1rem,calc((100vw - 1000px)/2)) 1.1rem; }
div[data-testid="stChatInput"] textarea { background:#11141b !important; border:1px solid #3a414e !important; border-radius:18px !important; color:var(--text) !important; }
div.stButton > button { background:#11141b; color:#e8edf5; border:1px solid #343b47; border-radius:10px; font-weight:700; min-height:38px; }
div.stButton > button:hover { border-color:var(--cyan); color:var(--cyan); }
@media (max-width:640px) { .block-container { padding-top:1rem; }.engine { text-align:left; margin-top:8px; }.title-row { display:block; }.persona-card { min-height:108px; }.data-proof { font-size:.58rem; } }
</style>
"""


def init_state() -> None:
    defaults = {
        "persona": "Neuro",
        "messages": [{"role": "assistant", "persona": "Neuro", "content": "Sebut instrumen apa saja—misal **XAUUSD**, EURUSD, BTCUSD, WTI, atau dua instrumen sekaligus buat dibandingin. Gue/aku bakal deteksi dari pesanmu, bukan dari pair yang dipilih di terminal."}],
        "latest_snapshots": [],
        "latest_question": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    for message in st.session_state.messages:
        if message.get("role") == "assistant" and "persona" not in message:
            message["persona"] = "Neuro"


def indicator_class(bias: str) -> str:
    return {"BUY": "signal-buy", "SELL": "signal-sell"}.get(bias, "signal-neutral")


def render_persona_switcher() -> None:
    left, right = st.columns(2)
    for column, name, copy in (
        (left, "Neuro", "Gaya gaul, ringkas, dan to the point. Tetap pakai angka serta peringatan risiko."),
        (right, "Aime", "Gaya formal seperti catatan analis. Struktur lebih rapi untuk membaca kondisi pasar."),
    ):
        active = "active" if st.session_state.persona == name else ""
        with column:
            st.markdown(f'<div class="persona-card {active}"><h3>{name}</h3><p>{copy}</p></div>', unsafe_allow_html=True)
            if st.button(f"Pilih {name}", key=f"persona_{name}", use_container_width=True):
                st.session_state.persona = name
                st.rerun()


def render_candle_chart(snapshot: MarketSnapshot) -> None:
    candles = snapshot.candles.copy()
    candles["ma50"] = candles["close"].rolling(50).mean()
    candles["ma200"] = candles["close"].rolling(200).mean()
    candles = candles.tail(150)
    figure = go.Figure()
    figure.add_trace(go.Candlestick(x=candles.index, open=candles["open"], high=candles["high"], low=candles["low"], close=candles["close"], name=snapshot.instrument.code, increasing_line_color="#31d47a", decreasing_line_color="#e14c56"))
    figure.add_trace(go.Scatter(x=candles.index, y=candles["ma50"], name="MA 50", line={"color":"#18d9f5","width":1.4}))
    figure.add_trace(go.Scatter(x=candles.index, y=candles["ma200"], name="MA 200", line={"color":"#f0c447","width":1.3,"dash":"dot"}))
    figure.update_layout(template="plotly_dark", paper_bgcolor="#0a0d12", plot_bgcolor="#0a0d12", height=360, margin={"l":8,"r":8,"t":35,"b":8}, title=f"{snapshot.instrument.code} · data {snapshot.source}", xaxis={"rangeslider":{"visible":False},"gridcolor":"#202632"}, yaxis={"side":"right","gridcolor":"#202632"}, legend={"orientation":"h","y":1.1}, font={"family":"Manrope","color":"#eaf0f7"})
    st.plotly_chart(figure, use_container_width=True, config={"displaylogo":False,"scrollZoom":True})


def render_snapshot(snapshot: MarketSnapshot) -> None:
    data = snapshot.indicators
    bias = str(data["bias"])
    label_class = indicator_class(bias)
    st.markdown(f'<div class="data-proof"><span>SUMBER: {snapshot.source}</span><span>UPDATED: {snapshot.fetched_at.astimezone(timezone.utc).strftime("%H:%M:%S UTC")}</span><span>STATUS: <b style="color:#31d47a">DATA TERBACA</b></span></div>', unsafe_allow_html=True)
    metrics = [
        ("HARGA", f"{float(data['price']):,.5f}" if float(data["price"]) < 20 else f"{float(data['price']):,.2f}"),
        ("20 BAR", f"{float(data['change_20']):+.2f}%"),
        ("RSI 14", f"{float(data['rsi14']):.1f}"),
        ("MACD", f"{float(data['macd']):+.4f}"),
        ("ATR 14", f"{float(data['atr14']):.4f}"),
        ("BIAS", bias),
    ]
    cols = st.columns(3)
    for index, (name, value) in enumerate(metrics):
        class_name = label_class if name == "BIAS" else ""
        cols[index % 3].markdown(f'<div class="metric-box"><div class="name">{name}</div><div class="val {class_name}">{value}</div></div>', unsafe_allow_html=True)
    with st.expander(f"Grafik dan bukti indikator · {snapshot.instrument.code}", expanded=True):
        render_candle_chart(snapshot)
        rows = [
            ("MA 20", data["ma20"]), ("MA 50", data["ma50"]), ("MA 200", data["ma200"]), ("RSI 14", data["rsi14"]),
            ("MACD", data["macd"]), ("MACD signal", data["macd_signal"]), ("ATR 14", data["atr14"]), ("High 20", data["high20"]),
            ("Low 20", data["low20"]), ("Volatilitas 20", f"{float(data['volatility20']):.2f}%"),
        ]
        table = {"Indikator": [name for name, _ in rows], "Nilai": [f"{value:,.5f}" if isinstance(value, float) else value for _, value in rows]}
        st.dataframe(table, use_container_width=True, hide_index=True)
        st.caption(snapshot.warning)


def render_comparison(snapshots: list[MarketSnapshot]) -> None:
    if len(snapshots) < 2:
        return
    frame = normalized_comparison(snapshots)
    if frame.empty:
        return
    figure = go.Figure()
    for column in frame.columns:
        figure.add_trace(go.Scatter(x=frame.index, y=frame[column], name=column, mode="lines"))
    figure.update_layout(template="plotly_dark", paper_bgcolor="#0a0d12", plot_bgcolor="#0a0d12", height=300, margin={"l":8,"r":8,"t":32,"b":8}, title="Perbandingan performa relatif · basis 100", yaxis_title="Indeks", xaxis={"gridcolor":"#202632"}, yaxis={"gridcolor":"#202632"})
    with st.expander("Perbandingan multi-instrumen", expanded=True):
        st.plotly_chart(figure, use_container_width=True, config={"displaylogo":False})


def render_message(role: str, content: str) -> None:
    if role == "user":
        st.markdown(f'<div class="chat-label">KAMU</div><div style="text-align:right;color:#e7eaf0;padding:8px 0">{content}</div>', unsafe_allow_html=True)
    else:
        persona = st.session_state.get("rendered_persona", st.session_state.persona)
        formal = "formal" if persona == "Aime" else ""
        safe_content = html.escape(content).replace("\n\n", "<br><br>")
        safe_content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe_content)
        st.markdown(f'<div class="chat-label">{persona.upper()} · PYTHON MARKET ENGINE</div><div class="reply-card {formal}">{safe_content}</div>', unsafe_allow_html=True)


def process_question(question: str) -> None:
    instruments = detect_instruments(question)
    st.session_state.messages.append({"role":"user", "content":question})
    if not instruments:
        st.session_state.messages.append({"role":"assistant", "persona": st.session_state.persona, "content":"Gue/aku belum menangkap instrumennya. Coba sebut eksplisit: **XAUUSD**, EURUSD, BTCUSD, WTI, DXY, atau misalnya `bandingkan XAUUSD dan oil`."})
        return
    snapshots: list[MarketSnapshot] = []
    with st.status("Memproses pertanyaan market…", expanded=True) as status:
        status.write("01 · Mendeteksi instrumen langsung dari pertanyaan")
        time.sleep(0.15)
        status.write("02 · Mengambil OHLCV publik dan memverifikasi jumlah candle")
        for instrument in instruments[:2]:
            try:
                snapshots.append(fetch_market_snapshot(instrument, interval="1h"))
            except RuntimeError as exc:
                st.warning(f"{instrument.code}: {exc}")
        status.write("03 · Menghitung 10 indikator dengan Python")
        time.sleep(0.15)
        status.write("04 · Menyusun respons sesuai persona")
        status.update(label="Proses analisis selesai", state="complete", expanded=False)
    if not snapshots:
        st.session_state.messages.append({"role":"assistant", "persona": st.session_state.persona, "content":"Data instrumen belum dapat diambil dari sumber publik saat ini, jadi analisis tidak saya buat-buat. Coba ulangi beberapa saat lagi atau pilih instrumen lain."})
        return
    response = build_reply(question, snapshots[0], st.session_state.persona)
    st.session_state.messages.append({"role":"assistant", "persona": st.session_state.persona, "content":response})
    st.session_state.latest_snapshots = snapshots
    st.session_state.latest_question = question


def main() -> None:
    st.set_page_config(page_title="Call of Catty · Market Chat", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")
    st.markdown(APP_CSS, unsafe_allow_html=True)
    init_state()

    st.markdown('<div class="title-row"><div><div class="brand-kicker">AEROVULPIS / CALL OF CATTY / PROTOTYPE 01</div><h1>Neural Market Assistant.</h1></div><div class="engine"><b>●</b> PYTHON MARKET ENGINE<br>INDEPENDENT SYMBOL DETECTION</div></div>', unsafe_allow_html=True)
    render_persona_switcher()
    st.markdown('<div class="brand-kicker" style="margin-top:22px">CONTOH CEPAT</div><div><span class="market-chip"><span class="dot"></span>Analisa XAUUSD sekarang</span><span class="market-chip"><span class="dot"></span>Bandingkan XAUUSD dan oil</span><span class="market-chip"><span class="dot"></span>Kenapa EURUSD bergerak?</span></div>', unsafe_allow_html=True)

    for message in st.session_state.messages:
        st.session_state.rendered_persona = message.get("persona", st.session_state.persona)
        render_message(message["role"], message["content"])
    st.session_state.pop("rendered_persona", None)

    if st.session_state.latest_snapshots:
        render_comparison(st.session_state.latest_snapshots)
        render_snapshot(st.session_state.latest_snapshots[0])
        st.markdown('<div class="brand-kicker" style="margin-top:20px">PERTANYAAN LANJUTAN</div>', unsafe_allow_html=True)
        for prompt in follow_up_prompts(st.session_state.latest_snapshots[0].instrument.code):
            if st.button(prompt, key=f"suggest_{prompt}", use_container_width=True):
                process_question(prompt)
                st.rerun()

    question = st.chat_input("Tanyakan market apa saja: XAUUSD, EURUSD, BTCUSD, oil…")
    if question:
        process_question(question)
        st.rerun()


if __name__ == "__main__":
    main()
