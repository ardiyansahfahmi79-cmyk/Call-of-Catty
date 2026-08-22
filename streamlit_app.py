"""Aero AI — market-scanning cybertech dengan data Python yang dapat ditelusuri."""

from __future__ import annotations

from datetime import timezone
import html
import random
import re
import time
from uuid import uuid4

import plotly.graph_objects as go
import streamlit as st

from fundamental_data import FundamentalSnapshot, fetch_fundamental_context
from market_chat import agenda_clarification_prompts, build_agenda_reply, build_instrument_confirmation, build_multi_instrument_clarification, build_reply, build_source_unavailable_reply, build_unknown_input_reply, detect_economic_agenda, follow_up_prompts, multi_instrument_clarification_prompts
from market_data import MarketSnapshot, detect_instruments, detect_timeframe, detect_unknown_instrument_candidates, fetch_market_snapshot, normalized_comparison


MIN_ANALYSIS_SECONDS = 13
TYPEWRITER_CHUNK = 40
CONFIRMATION_WORDS = {"ya", "iya", "yes", "y", "ok", "oke", "analisa", "analisis", "lanjut", "lanjutkan", "boleh", "silakan", "tolong", "saya", "mau", "ingin", "dong", "lah", "aja"}
CONFIRMATION_MARKERS = {"ya", "iya", "yes", "y", "ok", "oke", "analisa", "analisis", "lanjut", "lanjutkan", "boleh", "silakan"}

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Share+Tech+Mono&display=swap');
:root { --ink:#05070b; --surface:#0d1119; --surface-2:#111722; --line:#28303d; --text:#f3f6fb; --muted:#9aa5b5; --cyan:#18d9f5; --green:#36d987; --yellow:#e7bd52; --red:#ff6975; }
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"] { background:var(--ink)!important; color:var(--text)!important; font-family:Manrope,sans-serif; }
.stApp { background-image:linear-gradient(rgba(24,217,245,.016) 1px,transparent 1px),linear-gradient(90deg,rgba(24,217,245,.016) 1px,transparent 1px)!important; background-size:40px 40px!important; }
.block-container { max-width:900px; padding:1.25rem 1rem 2.2rem; }.app-shell { border-left:1px solid rgba(24,217,245,.25); border-right:1px solid rgba(24,217,245,.12); padding:0 1rem 1.25rem; }
.brand-kicker { color:var(--cyan); font:.65rem 'Share Tech Mono',monospace; letter-spacing:1.8px; }.title-row { display:flex; align-items:end; justify-content:space-between; gap:18px; border-bottom:1px solid var(--line); padding:0 0 1.1rem; margin-bottom:1rem; }.aero-title { margin:.3rem 0 0; font-size:clamp(2.1rem,7vw,3.35rem); letter-spacing:-2.7px; line-height:1; }.aero-white { color:#f5f7fb; }.ai-neon { color:var(--cyan); text-shadow:0 0 18px rgba(24,217,245,.45); }.engine { color:var(--muted); font:.61rem 'Share Tech Mono',monospace; line-height:1.65; text-align:right; }.engine b { color:var(--green); }
.market-only { border-left:2px solid var(--cyan); margin:0 0 1rem; padding:9px 12px; color:#cbd4df; font-size:.76rem; line-height:1.6; background:rgba(24,217,245,.045); }.market-only b { color:#f4f8fc; }.context-band { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; border:1px solid var(--line); background:linear-gradient(110deg,rgba(17,23,34,.95),rgba(9,12,18,.95)); border-radius:12px; padding:12px 14px; margin-bottom:1.2rem; }.context-band p { margin:0; color:#c0c8d5; font-size:.79rem; line-height:1.55; }.market-chip { display:inline-flex; align-items:center; gap:7px; border:1px solid #2d3745; padding:5px 9px; border-radius:999px; color:#c4cedb; font:.6rem 'Share Tech Mono',monospace; margin:2px; }.market-chip .dot { width:6px; height:6px; border-radius:50%; background:var(--green); box-shadow:0 0 10px var(--green); }
.loader-hud { border:1px solid rgba(24,217,245,.48); background:linear-gradient(105deg,rgba(8,29,38,.96),rgba(9,13,21,.98)); border-radius:12px; padding:13px 15px; margin:0 0 15px; overflow:hidden; position:relative; }.loader-hud:before { content:""; position:absolute; inset:0; background:linear-gradient(90deg,transparent,rgba(24,217,245,.08),transparent); transform:translateX(-100%); animation:scan 1.3s linear infinite; }.loader-top { position:relative; display:flex; justify-content:space-between; gap:12px; font:.62rem 'Share Tech Mono',monospace; color:#b8c9d8; }.loader-stage { position:relative; color:var(--cyan); letter-spacing:1px; margin-top:8px; }.loader-track { position:relative; height:4px; border-radius:9px; background:#172432; margin-top:11px; overflow:hidden; }.loader-fill { width:var(--progress); height:100%; background:linear-gradient(90deg,var(--cyan),#4d7cff); box-shadow:0 0 13px var(--cyan); transition:width .45s ease; }.loader-orbit { position:absolute; right:14px; bottom:8px; width:28px; height:28px; border:2px solid rgba(24,217,245,.22); border-top-color:var(--cyan); border-radius:50%; animation:spin .85s linear infinite; }.loader-dots span { animation:blink 1.2s infinite; }.loader-dots span:nth-child(2){animation-delay:.16s}.loader-dots span:nth-child(3){animation-delay:.32s}@keyframes scan{to{transform:translateX(100%)}}@keyframes spin{to{transform:rotate(360deg)}}@keyframes blink{50%{opacity:.2}}
.chat-label { color:#8794a8; font:.6rem 'Share Tech Mono',monospace; letter-spacing:1.5px; margin:22px 0 6px; }.user-message { margin-left:14%; padding:11px 13px; border:1px solid #303947; background:#111620; border-radius:13px 13px 4px 13px; color:#edf2f8; line-height:1.6; text-align:right; }.reply-card { border:1px solid rgba(24,217,245,.48); border-left:3px solid var(--cyan); background:linear-gradient(125deg,rgba(16,37,45,.72),rgba(12,16,24,.98) 42%); border-radius:5px 16px 16px 16px; padding:17px 18px; color:#eaf0f7; line-height:1.82; font-size:.94rem; }.reply-card.typing { min-height:92px; }.typing-cursor { display:inline-block; width:7px; height:1.05em; vertical-align:-.15em; background:var(--cyan); margin-left:3px; animation:blink .7s infinite; }
.analysis-shell { border:1px solid var(--line); border-top:2px solid rgba(24,217,245,.68); background:rgba(9,12,18,.76); padding:14px; border-radius:13px; margin:14px 0 4px; }.data-proof { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:7px 12px; color:#aeb8c7; font:.59rem 'Share Tech Mono',monospace; margin-bottom:13px; }.data-proof span { overflow-wrap:anywhere; }.metric-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:9px; }.metric-box { border-left:2px solid var(--cyan); padding:8px 0 8px 10px; background:rgba(17,23,34,.54); }.metric-box .name { color:#8793a5; font:.55rem 'Share Tech Mono',monospace; letter-spacing:1.1px; }.metric-box .val { margin-top:4px; font-size:.95rem; font-weight:800; }.signal-buy { color:var(--green); }.signal-sell { color:var(--red); }.signal-neutral { color:var(--yellow); }
.chart-guide { display:flex; justify-content:space-between; gap:8px; flex-wrap:wrap; padding:2px 0 9px; color:#aeb8c7; font:.6rem 'Share Tech Mono',monospace; }.indicator-table { margin-top:12px; overflow:hidden; border:1px solid var(--line); border-radius:9px; }.indicator-row { display:grid; grid-template-columns:1.1fr 1fr .7fr; gap:8px; padding:9px 10px; border-bottom:1px solid #202734; font-size:.73rem; }.indicator-row:last-child { border-bottom:0; }.indicator-row.header { background:#111722; color:var(--cyan); font:.56rem 'Share Tech Mono',monospace; letter-spacing:1px; }.indicator-row span:nth-child(2),.indicator-row span:nth-child(3) { text-align:right; font-family:'Share Tech Mono',monospace; }.indicator-buy { color:var(--green); }.indicator-sell { color:var(--red); }.indicator-neutral { color:var(--yellow); }
.fundamental-title { color:var(--cyan); font:.61rem 'Share Tech Mono',monospace; letter-spacing:1.5px; margin:18px 0 8px; }.fundamental-card { border:1px solid #2c3542; background:#10151e; border-radius:9px; padding:10px 11px; margin:7px 0; }.fundamental-card b { color:#eef3f8; }.fundamental-meta { color:#8f9bac; font:.57rem 'Share Tech Mono',monospace; margin-top:5px; overflow-wrap:anywhere; }.fundamental-meta a{color:var(--cyan);text-decoration:none;}.fundamental-meta a:hover{text-decoration:underline;}
	.scroll-cue { text-align:center; color:var(--cyan); font:.6rem 'Share Tech Mono',monospace; letter-spacing:1.4px; margin:18px 0 3px; }.input-panel { margin-top:1.25rem; padding:13px; border:1px solid #2d3948; background:rgba(12,16,24,.94); border-radius:14px; }.suggestion-kicker { color:#8794a8; font:.58rem 'Share Tech Mono',monospace; letter-spacing:1.35px; margin:0 0 7px; }[class*="st-key-chip-carousel-"] { overflow-x:auto!important; padding:1px 0 8px!important; scrollbar-width:thin; scrollbar-color:#34465a transparent; }[class*="st-key-chip-carousel-"] [data-testid="stButton"] { flex:0 0 min(78vw,310px)!important; min-width:min(78vw,310px)!important; }[class*="st-key-chip-carousel-"] .stButton>button { min-height:58px!important; white-space:normal!important; text-align:left!important; line-height:1.45!important; padding:10px 13px!important; }.stTextArea textarea { background:#111620!important; color:var(--text)!important; border:1px solid #384557!important; border-radius:10px!important; }.stButton>button { background:#121923!important; color:#eaf0f7!important; border:1px solid #364355!important; border-radius:9px!important; font-weight:700!important; min-height:38px!important; }.stButton>button:hover { color:var(--cyan)!important; border-color:var(--cyan)!important; }
div[data-testid="stPlotlyChart"],div[data-testid="stPlotlyChart"] .plot-container,div[data-testid="stPlotlyChart"] .svg-container { touch-action:pan-y!important; pointer-events:none!important; -webkit-user-select:none; user-select:none; }
@media(max-width:640px){ .block-container { padding:.8rem .62rem 1.5rem; }.app-shell { padding:0 .6rem 1rem; }.title-row { display:block; }.engine { text-align:left; margin-top:8px; }.user-message { margin-left:8%; }.reply-card { padding:15px; font-size:.91rem; }.metric-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }.data-proof { grid-template-columns:1fr; }.indicator-row { grid-template-columns:1fr .9fr .65fr; font-size:.68rem; }.context-band { padding:11px; } }
</style>
"""

STATIC_CHART_CONFIG = {"displaylogo": False, "displayModeBar": False, "scrollZoom": False, "responsive": True, "staticPlot": True}


def _message(role: str, content: str, **extra) -> dict:
    return {"id": str(uuid4()), "role": role, "content": content, "created_at": time.time(), **extra}


def init_state() -> None:
    defaults = {
        "messages": [_message("assistant", "Aero AI adalah sistem pemindaian market. Sebutkan instrumen seperti **XAUUSD**, EURUSD, BTCUSD, WTI, atau DXY untuk memulai analisis berbasis data." )],
        "latest_response_id": None,
        "typed_message_ids": set(),
        "pending_question": None,
        "pending_loader_ready": False,
        "opening_suggestions": None,
        "stable_prompt_chips": {},
        "pending_instrument_confirmation": None,
        "context_thread": {"instrument": None, "interval": None, "agenda": None},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _reply_markup(content: str, typing: bool = False) -> str:
    safe = html.escape(content).replace("\n\n", "<br><br>")
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    suffix = '<span class="typing-cursor"></span>' if typing else ""
    css = "reply-card typing" if typing else "reply-card"
    return f'<div class="chat-label">AERO AI · MARKET SCANNING SYSTEM</div><div class="{css}">{safe}{suffix}</div>'


def render_message(message: dict) -> None:
    if message["role"] == "user":
        st.markdown(f'<div class="chat-label">ANDA</div><div class="user-message">{html.escape(message["content"])}</div>', unsafe_allow_html=True)
        return
    should_type = bool(message.get("animate")) and message["id"] not in st.session_state.typed_message_ids
    if not should_type:
        st.markdown(_reply_markup(message["content"]), unsafe_allow_html=True)
        return
    slot = st.empty()
    content = message["content"]
    for end in range(TYPEWRITER_CHUNK, len(content) + TYPEWRITER_CHUNK, TYPEWRITER_CHUNK):
        slot.markdown(_reply_markup(content[:end], typing=True), unsafe_allow_html=True)
        time.sleep(0.018)
    slot.markdown(_reply_markup(content), unsafe_allow_html=True)
    st.session_state.typed_message_ids.add(message["id"])


def render_line_chart(snapshot: MarketSnapshot) -> None:
    candles = snapshot.candles.copy()
    candles["ma50"], candles["ma200"] = candles["close"].rolling(50).mean(), candles["close"].rolling(200).mean()
    candles = candles.tail(180)
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=candles.index, y=candles["close"], name=snapshot.instrument.code, mode="lines", line={"color":"#edf3fa", "width":2.2}))
    figure.add_trace(go.Scatter(x=candles.index, y=candles["ma50"], name="MA 50", mode="lines", line={"color":"#18d9f5", "width":1.55}))
    figure.add_trace(go.Scatter(x=candles.index, y=candles["ma200"], name="MA 200", mode="lines", line={"color":"#e7bd52", "width":1.35, "dash":"dot"}))
    figure.update_layout(template="plotly_dark", paper_bgcolor="#0a0d12", plot_bgcolor="#0a0d12", height=365, margin={"l":8,"r":10,"t":10,"b":8}, hovermode=False, xaxis={"rangeslider":{"visible":False},"gridcolor":"#202734","fixedrange":True}, yaxis={"side":"right","gridcolor":"#202734","fixedrange":True}, legend={"orientation":"h","x":0,"y":1.02,"xanchor":"left","yanchor":"bottom"}, font={"family":"Manrope","color":"#eaf0f7"})
    st.markdown(f'<div class="brand-kicker">{snapshot.instrument.code} · STATIC LINE MARKET CHART · {snapshot.interval.upper()}</div><div class="chart-guide"><span>Line chart statis · interaksi dinonaktifkan</span><span>Harga penutupan, MA 50, MA 200</span></div>', unsafe_allow_html=True)
    chart_key = f"market-chart-{snapshot.instrument.code}-{snapshot.interval}-{int(snapshot.fetched_at.timestamp() * 1_000_000)}"
    st.plotly_chart(figure, width="stretch", config=STATIC_CHART_CONFIG, key=chart_key)


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
        source = html.escape(item.source_name)
        url = html.escape(item.source_url, quote=True)
        st.markdown(f'<div class="fundamental-card"><b>{html.escape(item.title)}: {html.escape(item.value)} {html.escape(item.unit)}</b><div class="fundamental-meta">{html.escape(item.category)} · observasi {observed} · {html.escape(item.freshness)}<br><a href="{url}" target="_blank" rel="noopener">SUMBER RESMI: {source} ↗</a></div></div>', unsafe_allow_html=True)


def render_snapshot(snapshot: MarketSnapshot, fundamentals: list[FundamentalSnapshot]) -> None:
    data, bias = snapshot.indicators, str(snapshot.indicators["bias"])
    signal_class = {"BUY":"signal-buy", "SELL":"signal-sell"}.get(bias, "signal-neutral")
    last_candle = snapshot.last_candle_at.astimezone(timezone.utc).strftime("%d %b %H:%M UTC")
    basis = snapshot.instrument.note or f"{snapshot.instrument.asset_class} · quote publik referensi"
    st.markdown('<div class="analysis-shell">', unsafe_allow_html=True)
    st.markdown(f'<div class="data-proof"><span>SUMBER: {html.escape(snapshot.source)}</span><span>CANDLE TERAKHIR: {last_candle}</span><span>BASIS: {html.escape(basis)}</span><span>DIAMBIL: {snapshot.fetched_at.astimezone(timezone.utc).strftime("%H:%M:%S UTC")}</span></div>', unsafe_allow_html=True)
    metrics = [("HARGA", _format_number(data["price"])), ("20 CANDLE", f"{float(data['change_20']):+.2f}%"), ("RSI 14", f"{float(data['rsi14']):.1f}"), ("ADX 14", f"{float(data['adx14']):.1f}"), ("KONDISI", str(data["market_state"])), ("BIAS", bias)]
    markup = ''.join(f'<div class="metric-box"><div class="name">{name}</div><div class="val {signal_class if name in {"KONDISI", "BIAS"} else ""}">{html.escape(value)}</div></div>' for name, value in metrics)
    st.markdown(f'<div class="metric-grid">{markup}</div>', unsafe_allow_html=True)
    render_line_chart(snapshot)
    states = data["indicator_states"]
    rows = [("Harga vs MA 20", data["ma20"]), ("Harga vs MA 50", data["ma50"]), ("Harga vs MA 200", data["ma200"]), ("RSI 14", data["rsi14"]), ("MACD", data["macd"]), ("ADX 14", data["adx14"]), ("Volume relatif", f"{float(data['relative_volume']):.2f}x"), ("Fibonacci 61.8%", data["fib618"]), ("High 20", data["high20"]), ("Low 20", data["low20"])]
    table = ['<div class="indicator-table"><div class="indicator-row header"><span>INDIKATOR</span><span>NILAI</span><span>KONDISI</span></div>']
    for name, value in rows:
        state = str(states.get(name, "NEUTRAL"))
        css = {"BUY":"indicator-buy", "SELL":"indicator-sell"}.get(state, "indicator-neutral")
        formatted = _format_number(value) if not isinstance(value, str) else value
        table.append(f'<div class="indicator-row"><span>{name}</span><span>{formatted}</span><span class="{css}">{state}</span></div>')
    st.markdown("".join(table) + '</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="brand-kicker">PERBANDINGAN RELATIF · BASIS 100 · LINE CHART STATIS</div>', unsafe_allow_html=True)
    comparison_key = "comparison-chart-" + "-".join(f"{snapshot.instrument.code}-{int(snapshot.fetched_at.timestamp() * 1_000_000)}" for snapshot in snapshots)
    st.plotly_chart(figure, width="stretch", config=STATIC_CHART_CONFIG, key=comparison_key)


def _loader_markup(stage: str, estimate: int, progress: int) -> str:
    return f'<div class="loader-hud"><div class="loader-orbit"></div><div class="loader-top"><span>◈ AERO AI / DIGITAL MARKET PIPELINE</span><span>EST. {estimate:02d}S</span></div><div class="loader-stage">{html.escape(stage)}<span class="loader-dots"><span>.</span><span>.</span><span>.</span></span></div><div class="loader-track"><div class="loader-fill" style="--progress:{progress}%"></div></div></div>'


def _wait_until(started_at: float, seconds: float) -> None:
    remaining = seconds - (time.monotonic() - started_at)
    if remaining > 0:
        time.sleep(remaining)


def _run_context_loader(loader_slot, started_at: float, response_builder):
    """Tampilkan pipeline untuk agenda, klarifikasi, dan input yang tidak memerlukan snapshot harga."""
    stages = [
        ("01 / 04 · MEMVALIDASI INTENT, AGENDA, DAN KONTEKS PESAN", 28, 12, 1.1),
        ("02 / 04 · MEMETAKAN NEGARA, MATA UANG, DAN RELEVANSI", 22, 38, 4.0),
        ("03 / 04 · MEMERIKSA SUMBER KALENDER PUBLIK DAN BATAS DATA", 17, 69, 8.0),
        ("04 / 04 · MENYUSUN RESPONS MARKET YANG DAPAT DITELUSURI", 9, 92, MIN_ANALYSIS_SECONDS),
    ]
    response = None
    for index, (stage, estimate, progress, target_seconds) in enumerate(stages):
        loader_slot.markdown(_loader_markup(stage, estimate, progress), unsafe_allow_html=True)
        if index == 2:
            response = response_builder()
        _wait_until(started_at, target_seconds)
    loader_slot.markdown(_loader_markup("PIPELINE SELESAI · MENYIAPKAN RESPONS TERBARU", 0, 100), unsafe_allow_html=True)
    time.sleep(.35)
    loader_slot.empty()
    return response if response is not None else response_builder()


def queue_question(question: str) -> None:
    """Antrekan satu pesan agar rerun berikutnya selalu memindainya tepat di bawah chat."""
    normalized = question.strip()
    if not normalized or st.session_state.get("pending_question"):
        return
    st.session_state.messages.append(_message("user", normalized))
    st.session_state.pending_question = normalized
    st.session_state.pending_loader_ready = False


def queue_chip_question(question: str, scope: str) -> None:
    """Callback atomik untuk chip: simpan prompt sebelum rerun Streamlit merender ulang tombol.

    Callback widget dipanggil sebelum body skrip dijalankan kembali. Dengan demikian,
    pending_question sudah tersedia ketika main() sampai pada pipeline pemindaian dan
    pilihan chip lama tidak pernah digantikan secara acak sebelum klik diproses.
    """
    queue_question(question)
    if st.session_state.get("pending_question") != question.strip():
        return
    st.session_state.stable_prompt_chips.pop(scope, None)
    if scope == "opening":
        st.session_state.opening_suggestions = None


def resolve_confirmation_context(question: str, pending: dict | None) -> str | None:
    """Teruskan pair yang baru dikonfirmasi ketika pengguna memberi jawaban singkat."""
    if not pending:
        return None
    words = re.findall(r"[a-z]+", question.casefold())
    is_short_confirmation = bool(words) and len(words) <= 6 and all(word in CONFIRMATION_WORDS for word in words) and any(word in CONFIRMATION_MARKERS for word in words)
    if not is_short_confirmation:
        return None
    return f"Analisa {pending['instrument']} pada timeframe {pending['interval']}"


def resolve_thread_context(question: str, thread: dict | None) -> str | None:
    """Lanjutkan pertanyaan market singkat menggunakan tiga nilai kecil dari sesi aktif.

    Tidak ada riwayat tambahan atau penyimpanan database. Resolver hanya bekerja
    ketika instrumen baru tidak disebutkan dan selalu mempertahankan timeframe
    terakhir yang tersimpan pada sesi browser yang sama.
    """
    if not thread or not thread.get("instrument") or detect_instruments(question):
        return None
    instrument, interval = str(thread["instrument"]), str(thread.get("interval") or "1h")
    text = question.casefold()
    suffix = f"untuk {instrument} pada timeframe {interval}"
    if any(token in text for token in ("fomc", "federal reserve", "the fed", "fed meeting")):
        return f"Jelaskan konteks FOMC {suffix}"
    if any(token in text for token in ("retail sales", "penjualan ritel")):
        return f"Jelaskan {question.strip()} {suffix}"
    if any(token in text for token in ("nfp", "non farm", "nonfarm")):
        return f"Jelaskan dampak NFP {suffix}"
    if any(token in text for token in ("cpi", "inflasi", "ppi", "pce")):
        return f"Jelaskan {question.strip()} {suffix}"
    if any(token in text for token in ("risiko", "risk", "atr", "volatil")):
        return f"Tinjau risiko {suffix}"
    if any(token in text for token in ("tren", "trend", "momentum", "indikator", "sinyal")):
        return f"Jelaskan {question.strip()} {suffix}"
    return None


def update_context_thread(instrument: str, interval: str, question: str) -> None:
    """Simpan hanya konteks terakhir untuk sesi aktif, bukan percakapan atau data market."""
    agenda = detect_economic_agenda(question)
    st.session_state.context_thread = {
        "instrument": instrument,
        "interval": interval,
        "agenda": agenda[1] if agenda else None,
    }


def process_question(question: str, loader_slot) -> None:
    started_at = time.monotonic()
    resolved_question = resolve_confirmation_context(question, st.session_state.get("pending_instrument_confirmation"))
    if resolved_question:
        question = resolved_question
        st.session_state.pending_instrument_confirmation = None
    elif detect_instruments(question):
        st.session_state.pending_instrument_confirmation = None
    else:
        resolved_thread_question = resolve_thread_context(question, st.session_state.get("context_thread"))
        if resolved_thread_question:
            question = resolved_thread_question
    instruments = detect_instruments(question)
    interval = detect_timeframe(question)
    if not instruments:
        def build_context_reply() -> tuple[str, list[str]]:
            agenda_reply = build_agenda_reply(question)
            unknown_candidates = detect_unknown_instrument_candidates(question)
            return agenda_reply or build_unknown_input_reply(question, unknown_candidates), agenda_clarification_prompts(question) if agenda_reply else []

        reply, prompt_chips = _run_context_loader(loader_slot, started_at, build_context_reply)
        st.session_state.messages.append(_message("assistant", reply, prompt_chips=prompt_chips))
        return
    if len(instruments) > 2:
        codes = [instrument.code for instrument in instruments]
        reply, prompt_chips = _run_context_loader(
            loader_slot,
            started_at,
            lambda: (build_multi_instrument_clarification(codes), multi_instrument_clarification_prompts(codes)),
        )
        st.session_state.messages.append(_message(
            "assistant",
            reply,
            prompt_chips=prompt_chips,
        ))
        return
    action_words = ("analisa", "analyze", "scan", "bandingkan", "compare", "tren", "trend", "risiko", "risk", "indikator", "sinyal", "signal", "entry", "level", "fundamental", "forecast", "prediksi")
    if len(instruments) == 1 and not detect_economic_agenda(question) and not any(word in question.casefold() for word in action_words) and not re.search(r"\b(?:m15|m30|h\d{1,2}|d1|w1|mn)\b", question.casefold()):
        st.session_state.pending_instrument_confirmation = {"instrument": instruments[0].code, "interval": interval}
        st.session_state.messages.append(_message("assistant", build_instrument_confirmation(instruments[0].code)))
        return
    snapshots, fundamentals, unavailable_codes = [], {}, []
    stages = [("01 / 05 · MENDETEKSI INSTRUMEN, TIMEFRAME, DAN KONTEKS", 50, 9, 1.2), ("02 / 05 · MENARIK OHLCV PUBLIK DAN MEMVALIDASI CANDLE", 46, 27, 5.0), ("03 / 05 · MEMINDAI FUNDAMENTAL DAN KALENDER EKONOMI PUBLIK", 42, 49, 8.0), ("04 / 05 · MENGHITUNG 10 INDIKATOR PYTHON DAN REGIME PASAR", 38, 72, 10.5), ("05 / 05 · MENYUSUN NARASI DAN MEMBANGUN LINE CHART", 34, 92, MIN_ANALYSIS_SECONDS)]
    for index, (stage, estimate, progress, target_seconds) in enumerate(stages):
        loader_slot.markdown(_loader_markup(stage, estimate, progress), unsafe_allow_html=True)
        if index == 1:
            for instrument in instruments[:2]:
                try:
                    snapshots.append(fetch_market_snapshot(instrument, interval=interval))
                except RuntimeError:
                    unavailable_codes.append(instrument.code)
        elif index == 2:
            for snapshot in snapshots:
                fundamentals[snapshot.instrument.code] = fetch_fundamental_context(snapshot.instrument)
        _wait_until(started_at, target_seconds)
    loader_slot.markdown(_loader_markup("PIPELINE SELESAI · MENYIAPKAN RESPONS TERBARU", 0, 100), unsafe_allow_html=True)
    time.sleep(.35)
    loader_slot.empty()
    if not snapshots:
        st.session_state.messages.append(_message("assistant", build_source_unavailable_reply(unavailable_codes or [instrument.code for instrument in instruments])))
        return
    response = _message(
        "assistant",
        build_reply(question, snapshots[0], fundamentals.get(snapshots[0].instrument.code, [])),
        snapshots=snapshots,
        fundamentals=fundamentals,
        prompt_chips=agenda_clarification_prompts(question, snapshots[0].instrument.code),
        animate=True,
    )
    st.session_state.messages.append(response)
    st.session_state.latest_response_id = response["id"]
    update_context_thread(snapshots[0].instrument.code, snapshots[0].interval, question)


def render_analysis_message(message: dict) -> None:
    render_message(message)
    snapshots: list[MarketSnapshot] = message.get("snapshots", [])
    fundamentals: dict[str, list[FundamentalSnapshot]] = message.get("fundamentals", {})
    if not snapshots:
        prompts = message.get("prompt_chips") or []
        if prompts:
            st.markdown('<div class="brand-kicker" style="margin-top:18px">KLARIFIKASI FOKUS · GESER DAN PILIH</div>', unsafe_allow_html=True)
            render_prompt_carousel(prompts, scope=f"followup_{message['id']}")
        return
    if len(snapshots) > 1:
        render_comparison(snapshots)
    for snapshot in snapshots:
        render_snapshot(snapshot, fundamentals.get(snapshot.instrument.code, []))
    prompts = message.get("prompt_chips") or follow_up_prompts(snapshots[0].instrument.code, snapshots[0].interval)
    label = "KLARIFIKASI FOKUS · GESER DAN PILIH" if message.get("prompt_chips") else "PERTANYAAN LANJUTAN · GESER DAN PILIH FOKUS"
    st.markdown(f'<div class="brand-kicker" style="margin-top:18px">{label}</div>', unsafe_allow_html=True)
    render_prompt_carousel(
        prompts,
        scope=f"followup_{message['id']}",
    )
    if message["id"] == st.session_state.get("latest_response_id"):
        st.markdown('<div class="scroll-cue">↓ RESPONS TERBARU, DATA, DAN GRAFIK BERLANJUT DI BAWAH PESAN ANDA ↓</div>', unsafe_allow_html=True)


def contextual_suggestions() -> list[str]:
    """Ambil maksimal tiga saran yang relevan tanpa menyediakan menu pair atau timeframe."""
    instrument = None
    for message in reversed(st.session_state.messages):
        snapshots = message.get("snapshots", [])
        if snapshots:
            instrument = snapshots[0].instrument.code
            break
    if instrument:
        pool = [
            f"Analisa {instrument} pada timeframe M15",
            f"Analisa {instrument} pada timeframe H2",
            f"Analisa {instrument} pada timeframe H6",
            f"Analisa {instrument} pada timeframe H4",
            f"Analisa {instrument} pada timeframe W1",
            f"Analisa {instrument} pada timeframe MN",
            f"Tentukan Entry, SL, TP1 TP2 TP3 dan Risk untuk {instrument}",
            f"Jelaskan dampak NFP pada {instrument}",
            f"Jelaskan data Retail Sales untuk {instrument}",
            f"Jelaskan data CPI untuk {instrument}",
            f"Jelaskan data PPI untuk {instrument}",
            f"Jelaskan konteks FOMC untuk {instrument}",
            f"Bandingkan {instrument} dengan DXY pada H4",
            f"Tinjau tren {instrument} pada timeframe D1",
            f"Apakah Anda ingin saya menganalisa {instrument} lebih lanjut?",
        ]
    else:
        pool = [
            "Analisa XAUUSD pada timeframe H1",
            "Analisa EURUSD di M15",
            "Jelaskan dampak NFP untuk DXY",
            "Analisa BTCUSD pada timeframe H4",
            "Jelaskan konteks FOMC untuk XAUUSD",
            "Analisa IHSG pada timeframe D1",
            "Jelaskan data Retail Sales",
            "Jelaskan data CPI AS",
            "Analisa BBCA pada timeframe W1",
        ]
    return random.sample(pool, k=min(3, len(pool)))


def select_prompt_chips(prompts: list[str]) -> list[str]:
    """Pilih maksimal tiga chip tanpa mengubah pool prompt yang tersedia."""
    return random.sample(prompts, k=min(3, len(prompts)))


def select_stable_prompt_chips(cache: dict, scope: str, prompts: list[str]) -> list[str]:
    """Pertahankan urutan tiga chip sampai pool prompt untuk scope tersebut berubah."""
    prompt_pool = tuple(prompts)
    cached = cache.get(scope)
    if cached and cached.get("pool") == prompt_pool:
        return list(cached["selected"])
    selected = select_prompt_chips(prompts)
    cache[scope] = {"pool": prompt_pool, "selected": tuple(selected)}
    return selected


def should_show_opening_suggestions(messages: list[dict]) -> bool:
    return not any(message["role"] == "user" for message in messages)


def render_prompt_carousel(prompts: list[str], scope: str) -> None:
    """Render maksimal tiga prompt sebagai chip horizontal yang dapat digeser dan diklik."""
    selected = select_stable_prompt_chips(st.session_state.stable_prompt_chips, scope, prompts)
    carousel = st.container(horizontal=True, wrap=False, horizontal_alignment="left", gap="small", key=f"chip-carousel-{scope}")
    for index, prompt in enumerate(selected):
        carousel.button(
            prompt,
            key=f"{scope}_{index}_{prompt}",
            width="content",
            on_click=queue_chip_question,
            args=(prompt, scope),
        )


def render_input_panel() -> None:
    st.markdown('<div class="input-panel">', unsafe_allow_html=True)
    if should_show_opening_suggestions(st.session_state.messages):
        if st.session_state.opening_suggestions is None:
            st.session_state.opening_suggestions = contextual_suggestions()
        st.markdown('<div class="suggestion-kicker">SARAN PEMBUKA · GESER DAN PILIH UNTUK MEMINDAI</div>', unsafe_allow_html=True)
        render_prompt_carousel(st.session_state.opening_suggestions, scope="opening")
    with st.form("aero_question_form", clear_on_submit=True):
        question = st.text_area("Tanyakan analisis market", placeholder="Contoh: Analisa XAGUSD di M15, jelaskan NFP, atau cek Retail Sales untuk DXY", height=68, label_visibility="collapsed")
        submitted = st.form_submit_button("Mulai pemindaian Aero AI", width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)
    if submitted and question.strip():
        queue_question(question.strip())
        st.rerun()


def main() -> None:
    st.set_page_config(page_title="Aero AI · Market Scanner", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")
    st.markdown(APP_CSS, unsafe_allow_html=True)
    init_state()
    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    st.markdown('<div class="title-row"><div><div class="brand-kicker">AEROVULPIS / MARKET SCANNING SYSTEM</div><h1 class="aero-title"><span class="aero-white">Aero</span> <span class="ai-neon">AI</span></h1></div><div class="engine"><b>●</b> PYTHON DATA ENGINE<br>MARKET SIGNALS · TRACEABLE CONTEXT</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="market-only"><b>Aero AI adalah sistem pemindaian market berbasis data.</b> Sistem ini dikhususkan untuk instrumen, struktur harga, indikator, risiko, dan konteks fundamental market; bukan chatbot umum untuk topik di luar market.</div>', unsafe_allow_html=True)
    st.markdown('<div class="context-band"><p>Aero AI mendeteksi instrumen langsung dari pertanyaan dan menampilkan sumber, basis harga, waktu candle, indikator Python, serta konteks fundamental yang tersedia.</p><div><span class="market-chip"><span class="dot"></span>XAUUSD</span><span class="market-chip"><span class="dot"></span>EURUSD</span><span class="market-chip"><span class="dot"></span>BTCUSD</span><span class="market-chip"><span class="dot"></span>WTI</span></div></div>', unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            render_analysis_message(message)
        else:
            render_message(message)
    pending_question = st.session_state.get("pending_question")
    if pending_question:
        if not st.session_state.get("pending_loader_ready"):
            st.session_state.pending_loader_ready = True
            st.rerun()
        loader_slot = st.empty()
        process_question(pending_question, loader_slot)
        st.session_state.pending_question = None
        st.session_state.pending_loader_ready = False
        st.rerun()
    render_input_panel()
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
