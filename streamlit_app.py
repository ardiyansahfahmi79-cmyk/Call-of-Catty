"""Aero AI — chatbot market formal berbasis data publik dan Python."""

from __future__ import annotations

from datetime import timezone
import html
import re
import time

import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from market_chat import build_reply, follow_up_prompts
from market_data import MarketSnapshot, detect_instruments, fetch_market_snapshot, normalized_comparison

MIN_ANALYSIS_SECONDS = 13

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Share+Tech+Mono&display=swap');
:root { --ink:#050609; --line:#262b35; --text:#f5f6f8; --cyan:#18d9f5; --green:#31d47a; --yellow:#f0c447; }
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background:var(--ink)!important; color:var(--text)!important; font-family:Manrope,sans-serif; }
.block-container { max-width:940px; padding:1.15rem 1rem 2rem; }
.brand-kicker { color:var(--cyan); font: .65rem 'Share Tech Mono',monospace; letter-spacing:1.6px; }
.title-row { display:flex; justify-content:space-between; align-items:flex-end; border-bottom:1px solid var(--line); padding:0 0 1rem; margin-bottom:1rem; }.title-row h1 { font-size:clamp(1.65rem,6vw,2.7rem); margin:.3rem 0 0; letter-spacing:-1.8px; }.engine { color:#aab2c0; font:.63rem 'Share Tech Mono',monospace; text-align:right; line-height:1.55; }.engine b { color:var(--green); }
.context-band { display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; background:linear-gradient(110deg,#0d1118,#090b10); border:1px solid var(--line); border-radius:12px; padding:12px 14px; margin-bottom:16px; }.context-band p { color:#aab2c0; font-size:.77rem; line-height:1.5; margin:0; }.market-chip { display:inline-flex; gap:8px; align-items:center; border:1px solid var(--line); border-radius:999px; padding:6px 10px; color:#c8ced8; font:.64rem 'Share Tech Mono',monospace; margin:3px 4px 0 0; }.market-chip .dot { width:7px; height:7px; background:var(--green); border-radius:50%; box-shadow:0 0 12px var(--green); }
.reply-card { background:linear-gradient(135deg,rgba(24,217,245,.11),rgba(13,16,22,.98) 38%); border:1px solid rgba(24,217,245,.48); border-radius:18px 18px 18px 4px; padding:17px 18px; margin:9px 0 18px; line-height:1.8; font-size:.94rem; }.chat-label { color:#9ba5b6; font:.61rem 'Share Tech Mono',monospace; letter-spacing:1.5px; margin:22px 0 5px; }.user-message { text-align:right; color:#edf1f7; padding:9px 0; font-size:.95rem; }
.data-proof { display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px; background:#0a0d12; border:1px solid var(--line); padding:11px 13px; border-radius:10px; color:#b5bdcb; font:.64rem 'Share Tech Mono',monospace; }.metric-box { border-left:2px solid var(--cyan); padding:8px 0 8px 11px; }.metric-box .name { color:#7e899a; font:.57rem 'Share Tech Mono',monospace; letter-spacing:1.2px; }.metric-box .val { font-weight:800; font-size:1rem; margin-top:4px; }.signal-buy { color:var(--green); }.signal-sell { color:#ff6672; }.signal-neutral { color:var(--yellow); }
.indicator-table { border:1px solid var(--line); border-radius:10px; overflow:hidden; margin-top:10px; }.indicator-row { display:grid; grid-template-columns:1fr 1fr; gap:10px; padding:9px 11px; border-bottom:1px solid #1e2430; font-size:.77rem; }.indicator-row:last-child { border-bottom:0; }.indicator-row.header { background:#11151d; color:var(--cyan); font:.59rem 'Share Tech Mono',monospace; letter-spacing:1px; }.indicator-row span:last-child { text-align:right; color:#e5eaf2; font-family:'Share Tech Mono',monospace; }
.chart-guide { display:flex; justify-content:space-between; flex-wrap:wrap; gap:7px; color:#9ba5b6; font:.62rem 'Share Tech Mono',monospace; padding:7px 2px 10px; }.scroll-cue { text-align:center; color:var(--cyan); font:.65rem 'Share Tech Mono',monospace; letter-spacing:1px; margin:15px 0 2px; }
div[data-testid="stChatInput"] { position:static; margin-top:1.25rem; padding:0; background:transparent; } div[data-testid="stChatInput"] textarea { background:#11141b!important; border:1px solid #3a414e!important; border-radius:17px!important; color:var(--text)!important; } div.stButton > button { background:#11141b; color:#e8edf5; border:1px solid #343b47; border-radius:10px; font-weight:700; min-height:38px; } div.stButton > button:hover { border-color:var(--cyan); color:var(--cyan); }
@media (max-width:640px) { .block-container { padding:1rem .85rem 1.5rem; }.title-row { display:block; }.engine { text-align:left; margin-top:8px; }.data-proof { font-size:.56rem; }.reply-card { font-size:.92rem; padding:15px; }.chart-guide { font-size:.56rem; } }
</style>
"""


def init_state() -> None:
    defaults = {
        "messages": [{"role": "assistant", "content": "Silakan sebutkan instrumen yang ingin dianalisis, misalnya **XAUUSD**, EURUSD, BTCUSD, WTI, atau dua instrumen untuk dibandingkan. Aero AI akan mendeteksinya langsung dari pertanyaan Anda."}],
        "latest_snapshots": [],
        "scroll_to_latest": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_message(role: str, content: str) -> None:
    if role == "user":
        st.markdown(f'<div class="chat-label">ANDA</div><div class="user-message">{html.escape(content)}</div>', unsafe_allow_html=True)
        return
    safe_content = html.escape(content).replace("\n\n", "<br><br>")
    safe_content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe_content)
    st.markdown(f'<div class="chat-label">AERO AI · MARKET RESEARCH ENGINE</div><div class="reply-card">{safe_content}</div>', unsafe_allow_html=True)


def render_candle_chart(snapshot: MarketSnapshot) -> None:
    candles = snapshot.candles.copy()
    candles["ma50"] = candles["close"].rolling(50).mean()
    candles["ma200"] = candles["close"].rolling(200).mean()
    candles = candles.tail(180)
    figure = go.Figure()
    figure.add_trace(go.Candlestick(x=candles.index, open=candles["open"], high=candles["high"], low=candles["low"], close=candles["close"], name=snapshot.instrument.code, increasing_line_color="#31d47a", decreasing_line_color="#e14c56"))
    figure.add_trace(go.Scatter(x=candles.index, y=candles["ma50"], name="MA 50", line={"color":"#18d9f5", "width":1.55}))
    figure.add_trace(go.Scatter(x=candles.index, y=candles["ma200"], name="MA 200", line={"color":"#f0c447", "width":1.35, "dash":"dot"}))
    figure.update_layout(template="plotly_dark", paper_bgcolor="#0a0d12", plot_bgcolor="#0a0d12", height=430, margin={"l":10, "r":12, "t":10, "b":8}, dragmode="pan", hovermode="x unified", xaxis={"rangeslider":{"visible":True, "thickness":.07}, "gridcolor":"#202632"}, yaxis={"side":"right", "gridcolor":"#202632"}, legend={"orientation":"h", "x":0, "y":1.02, "xanchor":"left", "yanchor":"bottom"}, font={"family":"Manrope", "color":"#eaf0f7"})
    st.markdown(f'<div class="brand-kicker">{snapshot.instrument.code} · CANDLESTICK 1H</div><div class="chart-guide"><span>Geser grafik untuk pan</span><span>Scroll/cubit untuk zoom</span><span>Double-click untuk reset</span></div>', unsafe_allow_html=True)
    st.plotly_chart(figure, use_container_width=True, config={"displaylogo":False, "scrollZoom":True, "responsive":True, "doubleClick":"reset+autosize", "modeBarButtonsToRemove":["select2d", "lasso2d"]})


def render_snapshot(snapshot: MarketSnapshot) -> None:
    data = snapshot.indicators
    bias = str(data["bias"])
    signal_class = {"BUY": "signal-buy", "SELL": "signal-sell"}.get(bias, "signal-neutral")
    last_candle = snapshot.last_candle_at.astimezone(timezone.utc).strftime("%d %b %H:%M UTC")
    basis = snapshot.instrument.note or f"{snapshot.instrument.asset_class} · quote publik referensi"
    st.markdown(f'<div class="data-proof"><span>SUMBER: {snapshot.source}</span><span>CANDLE TERAKHIR: {last_candle}</span><span>BASIS: {basis}</span><span>DIAMBIL: {snapshot.fetched_at.astimezone(timezone.utc).strftime("%H:%M:%S UTC")}</span></div>', unsafe_allow_html=True)
    metrics = [("HARGA", f"{float(data['price']):,.5f}" if float(data["price"]) < 20 else f"{float(data['price']):,.2f}"), ("20 CANDLE", f"{float(data['change_20']):+.2f}%"), ("RSI 14", f"{float(data['rsi14']):.1f}"), ("MACD", f"{float(data['macd']):+.4f}"), ("ATR 14", f"{float(data['atr14']):.4f}"), ("BIAS", bias)]
    cols = st.columns(3)
    for index, (name, value) in enumerate(metrics):
        cls = signal_class if name == "BIAS" else ""
        cols[index % 3].markdown(f'<div class="metric-box"><div class="name">{name}</div><div class="val {cls}">{value}</div></div>', unsafe_allow_html=True)
    with st.expander(f"Grafik interaktif dan bukti indikator · {snapshot.instrument.code}", expanded=True):
        render_candle_chart(snapshot)
        rows = [("MA 20", data["ma20"]), ("MA 50", data["ma50"]), ("MA 200", data["ma200"]), ("RSI 14", data["rsi14"]), ("MACD", data["macd"]), ("MACD signal", data["macd_signal"]), ("ATR 14", data["atr14"]), ("High 20", data["high20"]), ("Low 20", data["low20"]), ("Volatilitas 20", f"{float(data['volatility20']):.2f}%")]
        table_rows = ['<div class="indicator-row header"><span>INDIKATOR</span><span>NILAI</span></div>']
        for name, value in rows:
            formatted = f"{value:,.5f}" if isinstance(value, float) else str(value)
            table_rows.append(f'<div class="indicator-row"><span>{name}</span><span>{formatted}</span></div>')
        st.markdown(f'<div class="indicator-table">{"".join(table_rows)}</div>', unsafe_allow_html=True)
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
    figure.update_layout(template="plotly_dark", paper_bgcolor="#0a0d12", plot_bgcolor="#0a0d12", height=330, margin={"l":10,"r":10,"t":15,"b":8}, dragmode="pan", xaxis={"rangeslider":{"visible":True,"thickness":.08},"gridcolor":"#202632"}, yaxis={"gridcolor":"#202632"}, legend={"orientation":"h","y":1.02,"yanchor":"bottom"})
    with st.expander("Perbandingan performa relatif · basis 100", expanded=True):
        st.plotly_chart(figure, use_container_width=True, config={"displaylogo":False, "scrollZoom":True, "responsive":True, "doubleClick":"reset+autosize"})


def wait_until(started_at: float, seconds: float) -> None:
    remaining = seconds - (time.monotonic() - started_at)
    if remaining > 0:
        time.sleep(remaining)


def process_question(question: str) -> None:
    instruments = detect_instruments(question)
    st.session_state.messages.append({"role":"user", "content":question})
    if not instruments:
        st.session_state.messages.append({"role":"assistant", "content":"Instrumen belum terdeteksi. Sebutkan simbol eksplisit, misalnya **XAUUSD**, EURUSD, BTCUSD, WTI, DXY, atau gunakan format `bandingkan XAUUSD dan oil`."})
        st.session_state.scroll_to_latest = True
        return
    started_at = time.monotonic()
    snapshots: list[MarketSnapshot] = []
    with st.status("Aero AI sedang menelaah data market…", expanded=True) as status:
        status.write("01 / 05 · Mendeteksi instrumen dari pertanyaan Anda")
        wait_until(started_at, 1.5)
        status.write("02 / 05 · Mengambil OHLCV publik dan memeriksa candle terbaru")
        for instrument in instruments[:2]:
            try:
                snapshots.append(fetch_market_snapshot(instrument, interval="1h"))
            except RuntimeError as exc:
                st.warning(f"{instrument.code}: {exc}")
        wait_until(started_at, 6.0)
        status.write("03 / 05 · Memvalidasi sumber, basis instrumen, dan waktu candle")
        wait_until(started_at, 8.5)
        status.write("04 / 05 · Menghitung 10 indikator dengan Python")
        wait_until(started_at, 11.0)
        status.write("05 / 05 · Menyusun ringkasan formal dan area observasi")
        wait_until(started_at, MIN_ANALYSIS_SECONDS)
        status.update(label="Analisis Aero AI selesai", state="complete", expanded=False)
    if not snapshots:
        st.session_state.messages.append({"role":"assistant", "content":"Sumber publik belum mengembalikan data memadai. Aero AI tidak akan membuat angka pengganti. Silakan ulangi beberapa saat lagi atau coba instrumen lain."})
    else:
        st.session_state.messages.append({"role":"assistant", "content":build_reply(question, snapshots[0])})
        st.session_state.latest_snapshots = snapshots
    st.session_state.scroll_to_latest = True


def scroll_to_latest_response() -> None:
    if not st.session_state.get("scroll_to_latest"):
        return
    st.markdown('<div id="aero-latest-response"></div><div class="scroll-cue">↓ RESPONS TERBARU DAN GRAFIK BERADA DI BAWAH ↓</div>', unsafe_allow_html=True)
    components.html("""<script>setTimeout(() => { const host = window.parent.document.querySelector('[data-testid="stMain"]'); if (host) host.scrollTo({top: host.scrollHeight, behavior: 'smooth'}); }, 250);</script>""", height=0)
    st.session_state.scroll_to_latest = False


def main() -> None:
    st.set_page_config(page_title="Aero AI · Market Chat", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")
    st.markdown(APP_CSS, unsafe_allow_html=True)
    init_state()
    st.markdown('<div class="title-row"><div><div class="brand-kicker">AEROVULPIS / AERO AI / MARKET RESEARCH PROTOTYPE</div><h1>Aero AI.</h1></div><div class="engine"><b>●</b> PYTHON MARKET ENGINE<br>INDEPENDENT INSTRUMENT DETECTION</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="context-band"><p><b>Aero AI</b> menganalisis instrumen yang disebut langsung pada chat. Sumber dan waktu candle selalu ditampilkan agar basis data dapat diperiksa.</p><div><span class="market-chip"><span class="dot"></span>XAUUSD</span><span class="market-chip"><span class="dot"></span>EURUSD</span><span class="market-chip"><span class="dot"></span>BTCUSD</span><span class="market-chip"><span class="dot"></span>WTI</span></div></div>', unsafe_allow_html=True)
    for message in st.session_state.messages:
        render_message(message["role"], message["content"])
    if st.session_state.latest_snapshots:
        render_comparison(st.session_state.latest_snapshots)
        render_snapshot(st.session_state.latest_snapshots[0])
        st.markdown('<div class="brand-kicker" style="margin-top:20px">PERTANYAAN LANJUTAN</div>', unsafe_allow_html=True)
        for prompt in follow_up_prompts(st.session_state.latest_snapshots[0].instrument.code):
            if st.button(prompt, key=f"suggest_{prompt}", use_container_width=True):
                process_question(prompt)
                st.rerun()
    scroll_to_latest_response()
    question = st.chat_input("Tanyakan analisis market: XAUUSD, EURUSD, BTCUSD, oil…")
    if question:
        process_question(question)
        st.rerun()


if __name__ == "__main__":
    main()
