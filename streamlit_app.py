"""Aero AI — chatbot market formal, data-sourced, dan mobile-first."""

from __future__ import annotations

from datetime import timezone
import html
import re
import time
from uuid import uuid4

import plotly.graph_objects as go
import streamlit as st

from fundamental_data import FundamentalSnapshot, fetch_fundamental_context
from market_chat import build_reply, follow_up_prompts
from market_data import MarketSnapshot, detect_instruments, fetch_market_snapshot, normalized_comparison


MIN_ANALYSIS_SECONDS = 13

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Share+Tech+Mono&display=swap');
:root { --ink:#06080d; --surface:#0d1119; --surface-2:#111722; --line:#28303d; --text:#f3f6fb; --muted:#9aa5b5; --cyan:#18d9f5; --green:#36d987; --yellow:#e7bd52; --red:#ff6975; }
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"] { background:var(--ink)!important; color:var(--text)!important; font-family:Manrope,sans-serif; }
.stApp { background-image:linear-gradient(rgba(24,217,245,.018) 1px,transparent 1px),linear-gradient(90deg,rgba(24,217,245,.018) 1px,transparent 1px)!important; background-size:40px 40px!important; }
.block-container { max-width:900px; padding:1.25rem 1rem 2.2rem; }
.app-shell { border-left:1px solid rgba(24,217,245,.25); border-right:1px solid rgba(24,217,245,.12); padding:0 1rem 1.25rem; }
.brand-kicker { color:var(--cyan); font:.65rem 'Share Tech Mono',monospace; letter-spacing:1.8px; }
.title-row { display:flex; align-items:end; justify-content:space-between; gap:18px; border-bottom:1px solid var(--line); padding:0 0 1.1rem; margin-bottom:1rem; }.title-row h1 { margin:.3rem 0 0; font-size:clamp(1.9rem,6vw,3rem); letter-spacing:-2px; }.engine { color:var(--muted); font:.61rem 'Share Tech Mono',monospace; line-height:1.65; text-align:right; }.engine b { color:var(--green); }
.context-band { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; border:1px solid var(--line); background:linear-gradient(110deg,rgba(17,23,34,.95),rgba(9,12,18,.95)); border-radius:12px; padding:12px 14px; margin-bottom:1.2rem; }.context-band p { margin:0; color:#c0c8d5; font-size:.79rem; line-height:1.55; }.market-chip { display:inline-flex; align-items:center; gap:7px; border:1px solid #2d3745; padding:5px 9px; border-radius:999px; color:#c4cedb; font:.6rem 'Share Tech Mono',monospace; margin:2px; }.market-chip .dot { width:6px; height:6px; border-radius:50%; background:var(--green); box-shadow:0 0 10px var(--green); }
.chat-label { color:#8794a8; font:.6rem 'Share Tech Mono',monospace; letter-spacing:1.5px; margin:22px 0 6px; }.user-message { margin-left:14%; padding:11px 13px; border:1px solid #303947; background:#111620; border-radius:13px 13px 4px 13px; color:#edf2f8; line-height:1.6; text-align:right; }.reply-card { border:1px solid rgba(24,217,245,.48); border-left:3px solid var(--cyan); background:linear-gradient(125deg,rgba(16,37,45,.72),rgba(12,16,24,.98) 42%); border-radius:5px 16px 16px 16px; padding:17px 18px; color:#eaf0f7; line-height:1.82; font-size:.94rem; }
.analysis-shell { border:1px solid var(--line); border-top:2px solid rgba(24,217,245,.68); background:rgba(9,12,18,.76); padding:14px; border-radius:13px; margin:14px 0 4px; }.data-proof { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:7px 12px; color:#aeb8c7; font:.59rem 'Share Tech Mono',monospace; margin-bottom:13px; }.data-proof span { overflow-wrap:anywhere; }.metric-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:9px; }.metric-box { border-left:2px solid var(--cyan); padding:8px 0 8px 10px; background:rgba(17,23,34,.54); }.metric-box .name { color:#8793a5; font:.55rem 'Share Tech Mono',monospace; letter-spacing:1.1px; }.metric-box .val { margin-top:4px; font-size:.95rem; font-weight:800; }.signal-buy { color:var(--green); }.signal-sell { color:var(--red); }.signal-neutral { color:var(--yellow); }
.chart-guide { display:flex; justify-content:space-between; gap:8px; flex-wrap:wrap; padding:2px 0 9px; color:#aeb8c7; font:.6rem 'Share Tech Mono',monospace; }.indicator-table { margin-top:12px; overflow:hidden; border:1px solid var(--line); border-radius:9px; }.indicator-row { display:grid; grid-template-columns:1.1fr 1fr .7fr; gap:8px; padding:9px 10px; border-bottom:1px solid #202734; font-size:.73rem; }.indicator-row:last-child { border-bottom:0; }.indicator-row.header { background:#111722; color:var(--cyan); font:.56rem 'Share Tech Mono',monospace; letter-spacing:1px; }.indicator-row span:nth-child(2),.indicator-row span:nth-child(3) { text-align:right; font-family:'Share Tech Mono',monospace; }.indicator-buy { color:var(--green); }.indicator-sell { color:var(--red); }.indicator-neutral { color:var(--yellow); }
.fundamental-title { color:var(--cyan); font:.61rem 'Share Tech Mono',monospace; letter-spacing:1.5px; margin:18px 0 8px; }.fundamental-card { border:1px solid #2c3542; background:#10151e; border-radius:9px; padding:10px 11px; margin:7px 0; }.fundamental-card b { color:#eef3f8; }.fundamental-meta { color:#8f9bac; font:.57rem 'Share Tech Mono',monospace; margin-top:5px; overflow-wrap:anywhere; }
.scroll-cue { text-align:center; color:var(--cyan); font:.6rem 'Share Tech Mono',monospace; letter-spacing:1.4px; margin:18px 0 3px; }.input-panel { margin-top:1.25rem; padding:13px; border:1px solid #2d3948; background:rgba(12,16,24,.94); border-radius:14px; }.input-panel p { color:var(--muted); margin:0 0 9px; font-size:.74rem; }.stTextArea textarea { background:#111620!important; color:var(--text)!important; border:1px solid #384557!important; border-radius:10px!important; }.stButton>button { background:#121923!important; color:#eaf0f7!important; border:1px solid #364355!important; border-radius:9px!important; font-weight:700!important; min-height:38px!important; }.stButton>button:hover { color:var(--cyan)!important; border-color:var(--cyan)!important; }
div[data-testid="stPlotlyChart"],div[data-testid="stPlotlyChart"] .plot-container,div[data-testid="stPlotlyChart"] .svg-container { touch-action:pan-y!important; pointer-events:none!important; -webkit-user-select:none; user-select:none; }
@media(max-width:640px){ .block-container { padding:.8rem .62rem 1.5rem; }.app-shell { padding:0 .6rem 1rem; }.title-row { display:block; }.engine { text-align:left; margin-top:8px; }.user-message { margin-left:8%; }.reply-card { padding:15px; font-size:.91rem; }.metric-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }.data-proof { grid-template-columns:1fr; }.indicator-row { grid-template-columns:1fr .9fr .65fr; font-size:.68rem; }.context-band { padding:11px; } }
</style>
"""

STATIC_CHART_CONFIG = {"displaylogo": False, "displayModeBar": False, "scrollZoom": False, "responsive": True, "staticPlot": True}


def _message(role: str, content: str, **extra) -> dict:
    return {"id": str(uuid4()), "role": role, "content": content, "created_at": time.time(), **extra}


def init_state() -> None:
    defaults = {
        "messages": [_message("assistant", "Silakan sebutkan instrumen yang ingin dianalisis, misalnya **XAUUSD**, EURUSD, BTCUSD, WTI, atau dua instrumen untuk dibandingkan. Aero AI mendeteksi instrumen langsung dari pertanyaan Anda.")],
        "latest_response_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_message(message: dict) -> None:
    role, content = message["role"], message["content"]
    if role == "user":
        st.markdown(f'<div class="chat-label">ANDA</div><div class="user-message">{html.escape(content)}</div>', unsafe_allow_html=True)
        return
    safe_content = html.escape(content).replace("\n\n", "<br><br>")
    safe_content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe_content)
    st.markdown(f'<div class="chat-label">AERO AI · PYTHON MARKET RESEARCH</div><div class="reply-card">{safe_content}</div>', unsafe_allow_html=True)


def render_line_chart(snapshot: MarketSnapshot) -> None:
    candles = snapshot.candles.copy()
    candles["ma50"] = candles["close"].rolling(50).mean()
    candles["ma200"] = candles["close"].rolling(200).mean()
    candles = candles.tail(180)
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=candles.index, y=candles["close"], name=snapshot.instrument.code, mode="lines", line={"color":"#edf3fa", "width":2.2}))
    figure.add_trace(go.Scatter(x=candles.index, y=candles["ma50"], name="MA 50", mode="lines", line={"color":"#18d9f5", "width":1.55}))
    figure.add_trace(go.Scatter(x=candles.index, y=candles["ma200"], name="MA 200", mode="lines", line={"color":"#e7bd52", "width":1.35, "dash":"dot"}))
    figure.update_layout(template="plotly_dark", paper_bgcolor="#0a0d12", plot_bgcolor="#0a0d12", height=365, margin={"l":8,"r":10,"t":10,"b":8}, hovermode=False, xaxis={"rangeslider":{"visible":False},"gridcolor":"#202734","fixedrange":True}, yaxis={"side":"right","gridcolor":"#202734","fixedrange":True}, legend={"orientation":"h","x":0,"y":1.02,"xanchor":"left","yanchor":"bottom"}, font={"family":"Manrope","color":"#eaf0f7"})
    st.markdown(f'<div class="brand-kicker">{snapshot.instrument.code} · STATIC LINE MARKET CHART · {snapshot.interval.upper()}</div><div class="chart-guide"><span>Line chart statis · interaksi dinonaktifkan</span><span>Harga penutupan, MA 50, MA 200</span></div>', unsafe_allow_html=True)
    st.plotly_chart(figure, use_container_width=True, config=STATIC_CHART_CONFIG)


def _format_number(value) -> str:
    numeric = float(value)
    return f"{numeric:,.5f}" if abs(numeric) < 20 else f"{numeric:,.2f}"


def render_fundamentals(items: list[FundamentalSnapshot]) -> None:
    st.markdown('<div class="fundamental-title">KONTEKS FUNDAMENTAL · SUMBER PUBLIK</div>', unsafe_allow_html=True)
    if not items:
        st.caption("Konteks fundamental belum tersedia dari sumber publik yang dikonfigurasi. Data teknikal tetap ditampilkan dengan metadata sumbernya.")
        return
    for item in items[:5]:
        observed = item.observed_at.strftime("%d %b %Y")
        detail = f"{html.escape(item.category)} · observasi {observed} · {html.escape(item.freshness)}"
        st.markdown(f'<div class="fundamental-card"><b>{html.escape(item.title)}: {html.escape(item.value)} {html.escape(item.unit)}</b><div class="fundamental-meta">{detail}<br>SUMBER: {html.escape(item.source_name)} · {html.escape(item.source_url)}</div></div>', unsafe_allow_html=True)


def render_snapshot(snapshot: MarketSnapshot, fundamentals: list[FundamentalSnapshot]) -> None:
    data = snapshot.indicators
    bias = str(data["bias"])
    signal_class = {"BUY":"signal-buy", "SELL":"signal-sell"}.get(bias, "signal-neutral")
    last_candle = snapshot.last_candle_at.astimezone(timezone.utc).strftime("%d %b %H:%M UTC")
    basis = snapshot.instrument.note or f"{snapshot.instrument.asset_class} · quote publik referensi"
    st.markdown('<div class="analysis-shell">', unsafe_allow_html=True)
    st.markdown(f'<div class="data-proof"><span>SUMBER: {html.escape(snapshot.source)}</span><span>CANDLE TERAKHIR: {last_candle}</span><span>BASIS: {html.escape(basis)}</span><span>DIAMBIL: {snapshot.fetched_at.astimezone(timezone.utc).strftime("%H:%M:%S UTC")}</span></div>', unsafe_allow_html=True)
    metrics = [("HARGA", _format_number(data["price"])), ("20 CANDLE", f"{float(data['change_20']):+.2f}%"), ("RSI 14", f"{float(data['rsi14']):.1f}"), ("ATR 14", _format_number(data["atr14"])), ("KONDISI", str(data["market_state"])), ("BIAS", bias)]
    metric_markup = []
    for name, value in metrics:
        cls = signal_class if name in {"KONDISI", "BIAS"} else ""
        metric_markup.append(f'<div class="metric-box"><div class="name">{name}</div><div class="val {cls}">{html.escape(value)}</div></div>')
    st.markdown(f'<div class="metric-grid">{"".join(metric_markup)}</div>', unsafe_allow_html=True)
    render_line_chart(snapshot)
    states = data["indicator_states"]
    rows = [("Harga vs MA 20", data["ma20"]), ("Harga vs MA 50", data["ma50"]), ("Harga vs MA 200", data["ma200"]), ("RSI 14", data["rsi14"]), ("MACD", data["macd"]), ("MACD signal", data["macd_signal"]), ("ATR 14", data["atr14"]), ("High 20", data["high20"]), ("Low 20", data["low20"]), ("Volatilitas 20", f"{float(data['volatility20']):.2f}%")]
    table = ['<div class="indicator-table"><div class="indicator-row header"><span>INDIKATOR</span><span>NILAI</span><span>KONDISI</span></div>']
    for name, value in rows:
        state = str(states.get(name, "NEUTRAL"))
        css = {"BUY":"indicator-buy", "SELL":"indicator-sell"}.get(state, "indicator-neutral")
        formatted = _format_number(value) if not isinstance(value, str) else value
        table.append(f'<div class="indicator-row"><span>{name}</span><span>{formatted}</span><span class="{css}">{state}</span></div>')
    table.append('</div>')
    st.markdown("".join(table), unsafe_allow_html=True)
    render_fundamentals(fundamentals)
    st.caption(snapshot.warning)
    st.markdown('</div>', unsafe_allow_html=True)


def render_comparison(snapshots: list[MarketSnapshot]) -> None:
    if len(snapshots) < 2:
        return
    frame = normalized_comparison(snapshots)
    if frame.empty:
        return
    figure = go.Figure()
    for column in frame.columns:
        figure.add_trace(go.Scatter(x=frame.index, y=frame[column], name=column, mode="lines"))
    figure.update_layout(template="plotly_dark", paper_bgcolor="#0a0d12", plot_bgcolor="#0a0d12", height=310, margin={"l":8,"r":8,"t":15,"b":8}, hovermode=False, xaxis={"rangeslider":{"visible":False},"gridcolor":"#202734","fixedrange":True}, yaxis={"gridcolor":"#202734","fixedrange":True}, legend={"orientation":"h","y":1.02,"yanchor":"bottom"})
    st.markdown('<div class="brand-kicker">PERBANDINGAN RELATIF · BASIS 100</div>', unsafe_allow_html=True)
    st.plotly_chart(figure, use_container_width=True, config=STATIC_CHART_CONFIG)


def wait_until(started_at: float, seconds: float) -> None:
    remaining = seconds - (time.monotonic() - started_at)
    if remaining > 0:
        time.sleep(remaining)


def process_question(question: str) -> None:
    instruments = detect_instruments(question)
    st.session_state.messages.append(_message("user", question))
    if not instruments:
        st.session_state.messages.append(_message("assistant", "Instrumen belum terdeteksi. Sebutkan simbol eksplisit seperti **XAUUSD**, EURUSD, BTCUSD, WTI, atau DXY. Aero AI tidak akan memilih instrumen secara acak."))
        return
    started_at = time.monotonic()
    snapshots: list[MarketSnapshot] = []
    fundamentals: dict[str, list[FundamentalSnapshot]] = {}
    with st.status("Aero AI sedang menelaah data market…", expanded=True) as status:
        status.write("01 / 05 · Mendeteksi instrumen dari pertanyaan Anda")
        wait_until(started_at, 1.5)
        status.write("02 / 05 · Mengambil OHLCV publik dan memeriksa candle terbaru")
        for instrument in instruments[:2]:
            try:
                snapshot = fetch_market_snapshot(instrument, interval="1h")
                snapshots.append(snapshot)
            except RuntimeError as exc:
                st.warning(f"{instrument.code}: {exc}")
        wait_until(started_at, 6.0)
        status.write("03 / 05 · Memeriksa konteks fundamental publik beserta waktu observasi")
        for snapshot in snapshots:
            fundamentals[snapshot.instrument.code] = fetch_fundamental_context(snapshot.instrument)
        wait_until(started_at, 8.5)
        status.write("04 / 05 · Menghitung indikator Python dan validasi kondisi market")
        wait_until(started_at, 11.0)
        status.write("05 / 05 · Menyusun analisis formal, area observasi, dan batas data")
        wait_until(started_at, MIN_ANALYSIS_SECONDS)
        status.update(label="Analisis Aero AI selesai", state="complete", expanded=False)
    if not snapshots:
        st.session_state.messages.append(_message("assistant", "Sumber publik belum mengembalikan data memadai. Aero AI tidak akan membuat angka pengganti. Silakan ulangi beberapa saat lagi atau coba instrumen lain."))
        return
    response = _message("assistant", build_reply(question, snapshots[0], fundamentals.get(snapshots[0].instrument.code, [])), snapshots=snapshots, fundamentals=fundamentals)
    st.session_state.messages.append(response)
    st.session_state.latest_response_id = response["id"]


def render_analysis_message(message: dict) -> None:
    render_message(message)
    snapshots: list[MarketSnapshot] = message.get("snapshots", [])
    fundamentals: dict[str, list[FundamentalSnapshot]] = message.get("fundamentals", {})
    if not snapshots:
        return
    if len(snapshots) > 1:
        render_comparison(snapshots)
    for snapshot in snapshots:
        render_snapshot(snapshot, fundamentals.get(snapshot.instrument.code, []))
    st.markdown('<div class="brand-kicker" style="margin-top:18px">PERTANYAAN LANJUTAN</div>', unsafe_allow_html=True)
    for prompt in follow_up_prompts(snapshots[0].instrument.code):
        if st.button(prompt, key=f"prompt_{message['id']}_{prompt}", use_container_width=True):
            process_question(prompt)
            st.rerun()
    if message["id"] == st.session_state.get("latest_response_id"):
        st.markdown('<div class="scroll-cue">↓ RESPONS TERBARU, DATA, DAN GRAFIK BERLANJUT DI BAWAH PESAN ANDA ↓</div>', unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="Aero AI · Market Chat", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")
    st.markdown(APP_CSS, unsafe_allow_html=True)
    init_state()
    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    st.markdown('<div class="title-row"><div><div class="brand-kicker">AEROVULPIS / AERO AI / TRACEABLE MARKET RESEARCH</div><h1>Aero AI.</h1></div><div class="engine"><b>●</b> PYTHON RESEARCH ENGINE<br>INSTRUMENT DETECTION · DATA TRACEABILITY</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="context-band"><p><b>Aero AI</b> mendeteksi instrumen langsung dari pertanyaan dan menampilkan sumber, basis, waktu candle, indikator Python, serta konteks fundamental yang tersedia.</p><div><span class="market-chip"><span class="dot"></span>XAUUSD</span><span class="market-chip"><span class="dot"></span>EURUSD</span><span class="market-chip"><span class="dot"></span>BTCUSD</span><span class="market-chip"><span class="dot"></span>WTI</span></div></div>', unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            render_analysis_message(message)
        else:
            render_message(message)
    st.markdown('<div class="input-panel"><p>Respons baru ditambahkan di bawah pertanyaan Anda. Sebutkan satu atau dua instrumen untuk analisis atau perbandingan.</p>', unsafe_allow_html=True)
    with st.form("aero_question_form", clear_on_submit=True):
        question = st.text_area("Tanyakan analisis market", placeholder="Contoh: Analisa XAUUSD sekarang atau bandingkan EURUSD dan DXY", height=68, label_visibility="collapsed")
        submitted = st.form_submit_button("Analisis dengan Aero AI", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
    if submitted and question.strip():
        process_question(question.strip())
        st.rerun()


if __name__ == "__main__":
    main()
