"""
DH LAB — Trading Simulation untuk AeroVulpis
============================================
Aplikasi Streamlit mandiri untuk simulasi trading pair sintetis DHAV.

Jalankan:
    pip install streamlit pandas numpy plotly
    streamlit run dh_lab.py

Catatan: DHAV adalah data simulasi edukasi, bukan data pasar riil.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import uuid

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# KONFIGURASI SIMULASI
# ============================================================
PAIR = "DHAV"
PAIR_NAME = "DynamiHatch AeroVulpis Index"
INITIAL_BALANCE = 100.0
CONTRACT_SIZE = 100
START_PRICE = 1_000.0
HISTORY_CANDLES = 140
MAX_RENDER_CANDLES = 180
CANDLE_MINUTES = 5
LIVE_INTERVAL_SECONDS = 0.75

# Warna dark terminal bergaya TradingView / MT5.
BG = "#0b0f14"
PANEL = "#111821"
CARD = "#18212c"
BORDER = "#283442"
TEXT = "#d9e1ea"
MUTED = "#8190a0"
GREEN = "#26a69a"
RED = "#ef5350"
BLUE = "#4f8cff"
YELLOW = "#f5b942"


# ============================================================
# CSS
# ============================================================
CSS = f"""
<style>
html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"] {{
    background: {BG} !important;
    color: {TEXT} !important;
}}
[data-testid="stSidebar"] {{ background: {PANEL} !important; }}
.block-container {{ max-width: 1500px; padding-top: 1rem; }}

.dh-header {{
    display: flex; align-items: center; gap: 12px;
    border-bottom: 1px solid {BORDER}; padding-bottom: 12px; margin-bottom: 16px;
}}
.dh-logo {{ color: {BLUE}; font-size: 25px; font-weight: 800; letter-spacing: 1px; }}
.dh-title {{ color: {TEXT}; font-size: 17px; font-weight: 700; }}
.dh-subtitle {{ color: {MUTED}; font-size: 12px; margin-top: 2px; }}

[data-testid="stMetric"] {{
    background: {CARD}; border: 1px solid {BORDER}; border-radius: 9px;
    padding: 12px 15px;
}}
[data-testid="stMetricLabel"] p {{ color: {MUTED} !important; font-size: 11px !important; }}
[data-testid="stMetricValue"] {{ color: {TEXT} !important; font-size: 21px !important; }}

.order-card {{
    background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px;
    padding: 15px;
}}
.price {{ color: {YELLOW}; font-size: 26px; font-weight: 800; }}
.caption {{ color: {MUTED}; font-size: 11px; text-transform: uppercase; letter-spacing: .6px; }}

div.stButton > button {{
    min-height: 40px; border-radius: 7px; border: 1px solid {BORDER};
    background: {CARD}; color: {TEXT}; font-weight: 650;
}}
div.stButton > button:hover {{ border-color: {BLUE}; color: {BLUE}; }}
.buy button {{ background: {GREEN} !important; border: 0 !important; color: white !important; font-size: 16px !important; }}
.sell button {{ background: {RED} !important; border: 0 !important; color: white !important; font-size: 16px !important; }}

.position-head, .position-row {{
    display: grid; grid-template-columns: 1.0fr .9fr 1.2fr 1.2fr 1.2fr .9fr;
    gap: 8px; align-items: center;
}}
.position-head {{
    color: {MUTED}; background: {CARD}; border: 1px solid {BORDER};
    border-radius: 7px 7px 0 0; padding: 8px 10px; font-size: 10px;
    text-transform: uppercase; letter-spacing: .4px;
}}
.position-row {{
    background: {PANEL}; border: 1px solid {BORDER}; border-top: 0;
    padding: 8px 10px; font-size: 12px;
}}
.buy-text {{ color: {GREEN}; font-weight: 700; }}
.sell-text {{ color: {RED}; font-weight: 700; }}
.pos-text {{ color: {GREEN}; font-weight: 700; }}
.neg-text {{ color: {RED}; font-weight: 700; }}
.notice {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 6px; padding: 7px 9px; margin-bottom: 5px; font-size: 11px; }}
hr {{ border-color: {BORDER} !important; }}
</style>
"""


# ============================================================
# SESSION STATE DAN DATA SIMULASI
# ============================================================
def _make_candle(open_price: float, close_price: float, timestamp: datetime) -> dict:
    wick_up = abs(float(np.random.normal(0, 0.42)))
    wick_down = abs(float(np.random.normal(0, 0.42)))
    return {
        "time": timestamp,
        "open": round(open_price, 4),
        "high": round(max(open_price, close_price) + wick_up, 4),
        "low": round(max(0.5, min(open_price, close_price) - wick_down), 4),
        "close": round(close_price, 4),
    }


def _generate_history(count: int = HISTORY_CANDLES) -> tuple[pd.DataFrame, float, float]:
    rows: list[dict] = []
    price = START_PRICE
    drift = 0.0
    timestamp = datetime.now().replace(second=0, microsecond=0) - timedelta(
        minutes=CANDLE_MINUTES * count
    )

    for _ in range(count):
        drift = float(np.clip(drift + np.random.normal(0, 0.010), -0.09, 0.09))
        shock = float(np.random.normal(drift, 0.48))
        close_price = max(1.0, price + shock)
        rows.append(_make_candle(price, close_price, timestamp))
        price = close_price
        timestamp += timedelta(minutes=CANDLE_MINUTES)

    return pd.DataFrame(rows), price, drift


def _next_tick(df: pd.DataFrame, price: float, drift: float) -> tuple[pd.DataFrame, float, float]:
    drift = float(np.clip(drift + np.random.normal(0, 0.010), -0.09, 0.09))
    shock = float(np.random.normal(drift, 0.48))
    close_price = max(1.0, price + shock)
    timestamp = df.iloc[-1]["time"] + timedelta(minutes=CANDLE_MINUTES)
    candle = _make_candle(price, close_price, timestamp)

    rows = df.tail(MAX_RENDER_CANDLES - 1).to_dict("records")
    rows.append(candle)
    return pd.DataFrame.from_records(rows), close_price, drift

def _init_state() -> None:
    defaults = {
        "balance": INITIAL_BALANCE,
        "positions": [],
        "notifications": [],
        "live": False,
        "price": START_PRICE,
        "drift": 0.0,
        "history": None,
        "last_tick": datetime.now(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if st.session_state.history is None:
        history, price, drift = _generate_history()
        st.session_state.history = history
        st.session_state.price = price
        st.session_state.drift = drift


def _reset_state() -> None:
    for key in [
        "balance", "positions", "notifications", "live", "price",
        "drift", "history", "last_tick", "lot", "sl", "tp",
    ]:
        st.session_state.pop(key, None)
    st.rerun()


# ============================================================
# ORDER MANAGEMENT
# ============================================================
def _calculate_pnl(position: dict, current_price: float) -> float:
    quantity = position["lot"] * CONTRACT_SIZE
    if position["side"] == "BUY":
        return (current_price - position["entry"]) * quantity
    return (position["entry"] - current_price) * quantity


def _open_position(side: str, lot: float, stop_loss: float, take_profit: float) -> None:
    entry = float(st.session_state.price)
    position = {
        "id": uuid.uuid4().hex[:7].upper(),
        "pair": PAIR,
        "side": side,
        "entry": entry,
        "lot": float(lot),
        "sl": float(stop_loss),
        "tp": float(take_profit),
        "opened_at": datetime.now().strftime("%H:%M:%S"),
    }
    st.session_state.positions.append(position)
    st.session_state.notifications.insert(
        0, f"{side} {PAIR} dibuka @ ${entry:,.2f} · {lot:.2f} lot"
    )
    st.session_state.notifications = st.session_state.notifications[:6]


def _close_position(position_id: str, reason: str = "Manual") -> None:
    for position in list(st.session_state.positions):
        if position["id"] == position_id:
            pnl = _calculate_pnl(position, st.session_state.price)
            st.session_state.balance += pnl
            st.session_state.positions.remove(position)
            st.session_state.notifications.insert(
                0,
                f"{reason}: {position['side']} {PAIR} ditutup @ "
                f"${st.session_state.price:,.2f} · PnL ${pnl:+,.2f}",
            )
            st.session_state.notifications = st.session_state.notifications[:6]
            break


def _check_sl_tp() -> None:
    current = float(st.session_state.price)
    for position in list(st.session_state.positions):
        sl_hit = position["sl"] > 0 and (
            (position["side"] == "BUY" and current <= position["sl"])
            or (position["side"] == "SELL" and current >= position["sl"])
        )
        tp_hit = position["tp"] > 0 and (
            (position["side"] == "BUY" and current >= position["tp"])
            or (position["side"] == "SELL" and current <= position["tp"])
        )
        if sl_hit:
            _close_position(position["id"], "SL Hit")
        elif tp_hit:
            _close_position(position["id"], "TP Hit")


def _advance_market() -> None:
    history, price, drift = _next_tick(
        st.session_state.history,
        st.session_state.price,
        st.session_state.drift,
    )
    st.session_state.history = history
    st.session_state.price = price
    st.session_state.drift = drift
    st.session_state.last_tick = datetime.now()
    _check_sl_tp()


# ============================================================
# CHART DAN UI
# ============================================================
def _build_chart() -> go.Figure:
    df = st.session_state.history.tail(MAX_RENDER_CANDLES)
    figure = go.Figure(
        go.Candlestick(
            x=df["time"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name=PAIR,
            increasing={"line": {"color": GREEN}, "fillcolor": GREEN},
            decreasing={"line": {"color": RED}, "fillcolor": RED},
            hovertemplate=(
                "Waktu: %{x|%d %b %H:%M}<br>"
                "Open: %{open:,.2f}<br>High: %{high:,.2f}<br>"
                "Low: %{low:,.2f}<br>Close: %{close:,.2f}<extra></extra>"
            ),
        )
    )

    for position in st.session_state.positions:
        color = GREEN if position["side"] == "BUY" else RED
        figure.add_hline(
            y=position["entry"], line_dash="dot", line_color=color,
            opacity=0.85, annotation_text=f"{position['side']} #{position['id']}",
            annotation_font_color=color,
        )
        if position["sl"] > 0:
            figure.add_hline(y=position["sl"], line_dash="dash", line_color=RED, opacity=0.5)
        if position["tp"] > 0:
            figure.add_hline(y=position["tp"], line_dash="dash", line_color=GREEN, opacity=0.5)

    figure.update_layout(
        template="plotly_dark",
        height=510,
        margin={"l": 8, "r": 8, "t": 48, "b": 8},
        paper_bgcolor=PANEL,
        plot_bgcolor=BG,
        font={"color": TEXT, "size": 11},
        title={"text": f"<b>{PAIR}</b> · {PAIR_NAME} · 5M · SIMULATION", "x": 0.02},
        xaxis={"gridcolor": BORDER, "rangeslider": {"visible": False}, "showspikes": True},
        yaxis={"gridcolor": BORDER, "showspikes": True, "side": "right"},
        hovermode="x unified",
        uirevision="dhav-terminal",
        transition={"duration": 0},
    )
    return figure

def _render_metrics() -> None:
    open_pnl = sum(
        _calculate_pnl(p, st.session_state.price)
        for p in st.session_state.positions
    )
    equity = st.session_state.balance + open_pnl

    m1, m2, m3 = st.columns(3)
    m1.metric("Saldo Saat Ini", f"${st.session_state.balance:,.2f}")
    m2.metric(
        "Open PnL",
        f"${open_pnl:+,.2f}",
        delta=f"${open_pnl:+,.2f}",
    )
    m3.metric("Total Equity", f"${equity:,.2f}")


def _render_order_panel() -> None:
    price = float(st.session_state.price)

    st.markdown('<div class="order-card">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="price">${price:,.2f}</div>'
        '<div class="caption">Harga DHAV saat ini</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    lot = st.number_input(
        "Lot / Size",
        min_value=0.01,
        max_value=10.0,
        value=0.10,
        step=0.01,
        key="lot",
    )
    sl = st.number_input(
        "Stop Loss",
        min_value=0.0,
        value=round(price * 0.985, 2),
        step=0.50,
        key="sl",
    )
    tp = st.number_input(
        "Take Profit",
        min_value=0.0,
        value=round(price * 1.015, 2),
        step=0.50,
        key="tp",
    )

    left, right = st.columns(2)

    with left:
        st.markdown('<div class="buy">', unsafe_allow_html=True)
        if st.button("▲ BUY", use_container_width=True, key="buy"):
            _open_position("BUY", lot, sl, tp)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="sell">', unsafe_allow_html=True)
        if st.button("▼ SELL", use_container_width=True, key="sell"):
            _open_position("SELL", lot, sl, tp)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    st.toggle(
        "Live Simulation",
        key="live",
        help="Update harga simulasi secara otomatis.",
    )

    if st.button("⏭ Tick Manual", use_container_width=True, key="manual_tick"):
        _advance_market()
        st.rerun()

    if st.button("Reset Simulasi", use_container_width=True, key="reset"):
        _reset_state()

    st.markdown('</div>', unsafe_allow_html=True)


def _render_positions() -> None:
    st.subheader("Posisi Terbuka")
    positions = st.session_state.positions

    if not positions:
        st.caption("Belum ada posisi. Atur lot, SL, TP, lalu tekan BUY atau SELL.")
        return

    st.markdown(
        '<div class="position-head">'
        '<span>Pair</span><span>Tipe</span><span>Entry</span>'
        '<span>Current</span><span>PnL</span><span>Aksi</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    for position in positions:
        pnl = _calculate_pnl(position, st.session_state.price)
        side_class = "buy-text" if position["side"] == "BUY" else "sell-text"
        pnl_class = "pos-text" if pnl >= 0 else "neg-text"

        cols = st.columns([1.0, 0.9, 1.2, 1.2, 1.2, 0.9])
        cols[0].write(position["pair"])
        cols[1].markdown(
            f'<span class="{side_class}">{position["side"]}</span>',
            unsafe_allow_html=True,
        )
        cols[2].write(f"${position['entry']:,.2f}")
        cols[3].write(f"${st.session_state.price:,.2f}")
        cols[4].markdown(
            f'<span class="{pnl_class}">${pnl:+,.2f}</span>',
            unsafe_allow_html=True,
        )

        if cols[5].button("Close", key=f"close_{position['id']}"):
            _close_position(position["id"])
            st.rerun()


def _render_activity() -> None:
    st.subheader("Aktivitas")

    if not st.session_state.notifications:
        st.caption("Belum ada aktivitas.")
        return

    for message in st.session_state.notifications:
        st.markdown(
            f'<div class="notice">{message}</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# LIVE FRAGMENT
# ============================================================
def _fragment_fallback(func):
    """Fallback agar file tetap bisa dibuka pada Streamlit lama."""
    return func


fragment = getattr(st, "fragment", _fragment_fallback)


@fragment(run_every=LIVE_INTERVAL_SECONDS)
def _render_terminal() -> None:
    if st.session_state.live:
        _advance_market()

    _render_metrics()
    st.divider()

    chart_col, order_col = st.columns([3.6, 1.15], gap="medium")

    with chart_col:
        st.plotly_chart(
            _build_chart(),
            use_container_width=True,
            config={
                "displaylogo": False,
                "scrollZoom": True,
                "doubleClick": "reset",
                "modeBarButtonsToRemove": ["lasso2d", "select2d"],
            },
        )

    with order_col:
        _render_order_panel()

    st.divider()

    pos_col, activity_col = st.columns([2.6, 1.0], gap="medium")

    with pos_col:
        _render_positions()

    with activity_col:
        _render_activity()

# ============================================================
# ENTRY POINT
# ============================================================
def main() -> None:
    st.set_page_config(
        page_title="DH LAB · AeroVulpis",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.markdown(CSS, unsafe_allow_html=True)
    _init_state()

    st.markdown(
        f"""
        <div class="dh-header">
            <div class="dh-logo">DH LAB</div>
            <div style="color:{MUTED}; font-size:20px;">|</div>
            <div>
                <div class="dh-title">AeroVulpis Trading Simulation</div>
                <div class="dh-subtitle">
                    {PAIR} · {PAIR_NAME} · Prototipe edukasi dengan saldo virtual $100
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _render_terminal()


if __name__ == "__main__":
    main()
