"""
DH LAB — Trading Simulation (Standalone)
=========================================
Prototipe simulasi trading mandiri oleh DynamiHatch Identity.
Pair simulasi: DHAV (DynamiHatch AeroVulpis Index)

Jalankan langsung:
    streamlit run dh_lab.py

Dependencies:
    pip install streamlit pandas numpy plotly
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import uuid

# ─────────────────────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────────────────────
SALDO_AWAL        = 100.0
KONTRAK_PER_LOT   = 100      # 1 lot = 100 unit DHAV
HARGA_AWAL        = 1000.0
CANDLE_AWAL       = 120
INTERVAL_MENIT    = 5
LIVE_INTERVAL_SEC = 1.5      # detik antar auto-tick

# Palet warna TradingView / MT5 dark
C_BG     = "#0e1117"
C_PANEL  = "#131722"
C_CARD   = "#1c2030"
C_BORDER = "#2a2e39"
C_TEXT   = "#d1d4dc"
C_MUTED  = "#787b86"
C_GREEN  = "#26a69a"
C_RED    = "#ef5350"
C_BLUE   = "#3b82f6"
C_YELLOW = "#f59e0b"


# ─────────────────────────────────────────────────────────
# CSS — DARK THEME
# ─────────────────────────────────────────────────────────
CSS = f"""
<style>
/* ── Latar belakang utama ── */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
    background-color: {C_BG} !important;
    color: {C_TEXT};
}}
[data-testid="stSidebar"] {{
    background-color: {C_PANEL} !important;
}}
/* ── Header ── */
.dh-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0 4px 0;
    border-bottom: 1px solid {C_BORDER};
    margin-bottom: 12px;
}}
.dh-logo {{
    font-size: 22px;
    font-weight: 800;
    letter-spacing: 1px;
    color: {C_BLUE};
}}
.dh-sub {{
    font-size: 12px;
    color: {C_MUTED};
}}
/* ── Metric cards ── */
[data-testid="stMetric"] {{
    background-color: {C_CARD} !important;
    border: 1px solid {C_BORDER} !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
}}
[data-testid="stMetricLabel"] p {{
    color: {C_MUTED} !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
[data-testid="stMetricValue"] {{
    font-size: 22px !important;
    font-weight: 700 !important;
    color: {C_TEXT} !important;
}}
/* ── Panel kanan ── */
.order-panel {{
    background-color: {C_CARD};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
    padding: 18px 16px;
}}
.price-display {{
    font-size: 26px;
    font-weight: 800;
    color: {C_YELLOW};
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}}
.panel-label {{
    font-size: 11px;
    color: {C_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 2px;
}}
/* ── Tombol BUY / SELL ── */
.btn-buy button {{
    background-color: {C_GREEN} !important;
    color: #ffffff !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    height: 48px !important;
    border: none !important;
    width: 100%;
}}
.btn-sell button {{
    background-color: {C_RED} !important;
    color: #ffffff !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    height: 48px !important;
    border: none !important;
    width: 100%;
}}
div.stButton > button {{
    border-radius: 7px;
    font-weight: 600;
    border: 1px solid {C_BORDER};
    background-color: {C_CARD};
    color: {C_TEXT};
    height: 40px;
}}
div.stButton > button:hover {{
    border-color: {C_BLUE};
    color: {C_BLUE};
}}
/* ── Input fields ── */
[data-testid="stNumberInputContainer"], [data-testid="stTextInput"] {{
    background-color: {C_CARD} !important;
    border-radius: 6px !important;
}}
/* ── Tabel posisi ── */
.pos-header {{
    display: grid;
    grid-template-columns: 80px 70px 110px 110px 110px 80px;
    gap: 4px;
    padding: 6px 10px;
    background-color: {C_CARD};
    border: 1px solid {C_BORDER};
    border-radius: 8px 8px 0 0;
    font-size: 11px;
    color: {C_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.4px;
}}
.pos-row {{
    display: grid;
    grid-template-columns: 80px 70px 110px 110px 110px 80px;
    gap: 4px;
    padding: 8px 10px;
    background-color: {C_PANEL};
    border: 1px solid {C_BORDER};
    border-top: none;
    font-size: 13px;
    align-items: center;
}}
.pos-row:last-child {{ border-radius: 0 0 8px 8px; }}
.tag-buy  {{ color: {C_GREEN}; font-weight: 700; }}
.tag-sell {{ color: {C_RED};   font-weight: 700; }}
.pnl-pos  {{ color: {C_GREEN}; font-weight: 600; }}
.pnl-neg  {{ color: {C_RED};   font-weight: 600; }}
/* ── Divider ── */
hr {{ border-color: {C_BORDER} !important; margin: 12px 0; }}
/* ── Scrollbar tipis ── */
::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: {C_BG}; }}
::-webkit-scrollbar-thumb {{ background: {C_BORDER}; border-radius: 4px; }}
</style>
"""


# ─────────────────────────────────────────────────────────
# GENERATOR HARGA — Random Walk + Macro Drift
# ─────────────────────────────────────────────────────────
def _bentuk_candle(open_: float, close_: float, ts: datetime) -> dict:
    wick_hi = abs(np.random.normal(0, 0.40))
    wick_lo = abs(np.random.normal(0, 0.40))
    return {
        "time":  ts,
        "open":  open_,
        "high":  max(open_, close_) + wick_hi,
        "low":   max(min(open_, close_) - wick_lo, 0.5),
        "close": close_,
    }


def _generate_histori(n: int = CANDLE_AWAL):
    rows, harga, drift = [], HARGA_AWAL, 0.0
    ts = datetime.now() - timedelta(minutes=INTERVAL_MENIT * n)
    for _ in range(n):
        drift  = float(np.clip(drift + np.random.normal(0, 0.012), -0.10, 0.10))
        shock  = float(np.random.normal(drift, 0.50))
        close_ = max(harga + shock, 1.0)
        rows.append(_bentuk_candle(harga, close_, ts))
        harga  = close_
        ts    += timedelta(minutes=INTERVAL_MENIT)
    return pd.DataFrame(rows), harga, drift


def _tick(df: pd.DataFrame, harga: float, drift: float):
    drift  = float(np.clip(drift + np.random.normal(0, 0.012), -0.10, 0.10))
    shock  = float(np.random.normal(drift, 0.50))
    close_ = max(harga + shock, 1.0)
    ts_baru = df.iloc[-1]["time"] + timedelta(minutes=INTERVAL_MENIT)
    candle  = _bentuk_candle(harga, close_, ts_baru)
    df_baru = pd.concat([df, pd.DataFrame([candle])], ignore_index=True).tail(300).reset_index(drop=True)
    return df_baru, close_, drift


# ─────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────
def _init():
    if "saldo" not in st.session_state:
        st.session_state.saldo = SALDO_AWAL
    if "positions" not in st.session_state:
        st.session_state.positions = []
    if "df" not in st.session_state:
        df, harga, drift = _generate_histori()
        st.session_state.df    = df
        st.session_state.harga = harga
        st.session_state.drift = drift
    if "live" not in st.session_state:
        st.session_state.live = False
    if "notif" not in st.session_state:
        st.session_state.notif = []   # list pesan notifikasi (SL/TP hit)


def _tambah_tick():
    df, harga, drift = _tick(
        st.session_state.df,
        st.session_state.harga,
        st.session_state.drift,
    )
    st.session_state.df    = df
    st.session_state.harga = harga
    st.session_state.drift = drift
    _cek_sl_tp(harga)


# ─────────────────────────────────────────────────────────
# LOGIKA TRADING
# ─────────────────────────────────────────────────────────
def _pnl(pos: dict, harga_now: float) -> float:
    qty = pos["lot"] * KONTRAK_PER_LOT
    return (harga_now - pos["entry"]) * qty if pos["tipe"] == "BUY" else (pos["entry"] - harga_now) * qty


def _buka(tipe: str, lot: float, sl: float, tp: float):
    st.session_state.positions.append({
        "id":    str(uuid.uuid4())[:8],
        "pair":  "DHAV",
        "tipe":  tipe,
        "entry": st.session_state.harga,
        "lot":   lot,
        "sl":    sl,
        "tp":    tp,
        "waktu": datetime.now(),
    })


def _tutup(pos_id: str, alasan: str = "Manual"):
    for pos in st.session_state.positions:
        if pos["id"] == pos_id:
            nilai_pnl = _pnl(pos, st.session_state.harga)
            st.session_state.saldo += nilai_pnl
            st.session_state.positions.remove(pos)
            label = f"{'🟢' if nilai_pnl >= 0 else '🔴'} [{alasan}] {pos['tipe']} DHAV ditutup @ ${st.session_state.harga:,.2f} — PnL: ${nilai_pnl:+,.2f}"
            st.session_state.notif.insert(0, label)
            st.session_state.notif = st.session_state.notif[:5]
            break


def _cek_sl_tp(harga_now: float):
    for pos in list(st.session_state.positions):
        sl, tp = pos["sl"], pos["tp"]
        kena_sl = sl > 0 and (
            (pos["tipe"] == "BUY"  and harga_now <= sl) or
            (pos["tipe"] == "SELL" and harga_now >= sl)
        )
        kena_tp = tp > 0 and (
            (pos["tipe"] == "BUY"  and harga_now >= tp) or
            (pos["tipe"] == "SELL" and harga_now <= tp)
        )
        if kena_sl: _tutup(pos["id"], "SL Hit")
        elif kena_tp: _tutup(pos["id"], "TP Hit")


# ─────────────────────────────────────────────────────────
# CHART
# ─────────────────────────────────────────────────────────
def _chart() -> go.Figure:
    df  = st.session_state.df
    fig = go.Figure()

    # Candlestick utama
    fig.add_trace(go.Candlestick(
        x=df["time"],
        open=df["open"], high=df["high"],
        low=df["low"],   close=df["close"],
        increasing=dict(line=dict(color=C_GREEN, width=1), fillcolor=C_GREEN),
        decreasing=dict(line=dict(color=C_RED,   width=1), fillcolor=C_RED),
        name="DHAV",
        hovertext=[
            f"O: {r.open:.2f}  H: {r.high:.2f}  L: {r.low:.2f}  C: {r.close:.2f}"
            for r in df.itertuples()
        ],
        hoverinfo="x+text",
    ))

    # Garis entry setiap posisi terbuka
    for pos in st.session_state.positions:
        warna = C_GREEN if pos["tipe"] == "BUY" else C_RED
        fig.add_hline(
            y=pos["entry"], line_dash="dot",
            line_color=warna, line_width=1, opacity=0.75,
            annotation_text=f"{pos['tipe']} #{pos['id']}",
            annotation_font_color=warna,
            annotation_font_size=10,
        )
        if pos["sl"] > 0:
            fig.add_hline(y=pos["sl"], line_dash="dash", line_color=C_RED,   line_width=1, opacity=0.45)
        if pos["tp"] > 0:
            fig.add_hline(y=pos["tp"], line_dash="dash", line_color=C_GREEN, line_width=1, opacity=0.45)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=C_PANEL,
        plot_bgcolor=C_BG,
        font=dict(color=C_TEXT, size=12),
        height=500,
        margin=dict(l=0, r=0, t=36, b=0),
        xaxis_rangeslider_visible=False,
        title=dict(
            text="<b>DHAV</b>  DynamiHatch AeroVulpis Index  •  5M  •  Simulasi",
            font=dict(size=13, color=C_TEXT),
            x=0.01,
        ),
        yaxis=dict(title="", gridcolor=C_BORDER, tickfont=dict(size=11)),
        xaxis=dict(gridcolor=C_BORDER, tickfont=dict(size=10)),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )
    return fig


# ─────────────────────────────────────────────────────────
# PANEL ORDER (KANAN)
# ─────────────────────────────────────────────────────────
def _panel_order():
    harga_now = st.session_state.harga

    st.markdown(f"""
<div class="price-display">${harga_now:,.2f}</div>
<div class="panel-label">Harga DHAV Saat Ini</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="panel-label">Lot / Size</div>', unsafe_allow_html=True)
    lot = st.number_input("lot_input", label_visibility="collapsed",
                          min_value=0.01, max_value=10.0,
                          value=0.10, step=0.01, key="k_lot")

    col_sl, col_tp = st.columns(2)
    with col_sl:
        st.markdown('<div class="panel-label">Stop Loss</div>', unsafe_allow_html=True)
        sl = st.number_input("sl_input", label_visibility="collapsed",
                             min_value=0.0, value=round(harga_now * 0.985, 2),
                             step=1.0, key="k_sl")
    with col_tp:
        st.markdown('<div class="panel-label">Take Profit</div>', unsafe_allow_html=True)
        tp = st.number_input("tp_input", label_visibility="collapsed",
                             min_value=0.0, value=round(harga_now * 1.015, 2),
                             step=1.0, key="k_tp")

    st.markdown("<br>", unsafe_allow_html=True)
    col_b, col_s = st.columns(2)
    with col_b:
        st.markdown('<div class="btn-buy">', unsafe_allow_html=True)
        if st.button("▲ BUY", use_container_width=True, key="k_buy"):
            _buka("BUY", lot, sl, tp)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_s:
        st.markdown('<div class="btn-sell">', unsafe_allow_html=True)
        if st.button("▼ SELL", use_container_width=True, key="k_sell"):
            _buka("SELL", lot, sl, tp)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Live toggle
    live_val = st.toggle("▶ Live Simulation", value=st.session_state.live, key="k_live")
    st.session_state.live = live_val

    if st.button("⏭ Tick Manual", use_container_width=True, key="k_tick"):
        _tambah_tick()
        st.rerun()

    if st.button("🔄 Reset Simulasi", use_container_width=True, key="k_reset"):
        for k in ["saldo","positions","df","harga","drift","live","notif"]:
            st.session_state.pop(k, None)
        st.rerun()


# ─────────────────────────────────────────────────────────
# TABEL POSISI TERBUKA
# ─────────────────────────────────────────────────────────
def _tabel_posisi():
    posisi    = st.session_state.positions
    harga_now = st.session_state.harga

    st.markdown("#### 📋 Posisi Terbuka")

    if not posisi:
        st.markdown(
            f'<div style="color:{C_MUTED}; font-size:13px; padding:10px 0;">Belum ada posisi — tekan BUY / SELL untuk memulai.</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        '<div class="pos-header">'
        '<span>Pair</span><span>Tipe</span>'
        '<span>Entry ($)</span><span>Now ($)</span>'
        '<span>PnL ($)</span><span>Aksi</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    for pos in posisi:
        pnl       = _pnl(pos, harga_now)
        tag_cls   = "tag-buy"  if pos["tipe"] == "BUY"  else "tag-sell"
        pnl_cls   = "pnl-pos"  if pnl >= 0              else "pnl-neg"
        pnl_sign  = f"+{pnl:,.2f}" if pnl >= 0 else f"{pnl:,.2f}"

        st.markdown(f"""
<div class="pos-row">
  <span>{pos["pair"]}</span>
  <span class="{tag_cls}">{pos["tipe"]}</span>
  <span>{pos["entry"]:,.2f}</span>
  <span>{harga_now:,.2f}</span>
  <span class="{pnl_cls}">{pnl_sign}</span>
  <span></span>
</div>
""", unsafe_allow_html=True)

        # Tombol close sejajar dengan baris (dirender via st.columns di bawah HTML)
        if st.button(f"Close #{pos['id']}", key=f"cls_{pos['id']}"):
            _tutup(pos["id"], "Manual")
            st.rerun()


# ─────────────────────────────────────────────────────────
# NOTIFIKASI SL / TP
# ─────────────────────────────────────────────────────────
def _notif_bar():
    if not st.session_state.notif:
        return
    for msg in st.session_state.notif:
        st.markdown(
            f'<div style="background:{C_CARD}; border:1px solid {C_BORDER}; '
            f'border-radius:6px; padding:6px 12px; margin-bottom:4px; font-size:12px;">'
            f'{msg}</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="DH LAB — DHAV Simulation",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CSS, unsafe_allow_html=True)
    _init()

    # Auto-tick dulu sebelum render, supaya harga selalu fresh saat live
    if st.session_state.live:
        _tambah_tick()

    # ── Header ──────────────────────────────────────────
    st.markdown(f"""
<div class="dh-header">
  <span class="dh-logo">🧪 DH LAB</span>
  <span style="color:{C_MUTED}; font-size:18px;">|</span>
  <div>
    <div style="font-size:15px; font-weight:600;">Trading Simulation</div>
    <div class="dh-sub">DynamiHatch Identity · Pair: DHAV · Prototipe edukasi, bukan data riil</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Metrics saldo ────────────────────────────────────
    open_pnl = sum(_pnl(p, st.session_state.harga) for p in st.session_state.positions)
    equity   = st.session_state.saldo + open_pnl

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Saldo",       f"${st.session_state.saldo:,.2f}")
    m2.metric("📈 Open PnL",    f"${open_pnl:,.2f}", delta=f"{open_pnl:,.2f}")
    m3.metric("⚖️ Total Equity", f"${equity:,.2f}")
    m4.metric("📊 Open Posisi", len(st.session_state.positions))

    st.markdown("---")

    # ── Layout: Chart (kiri) + Panel Order (kanan) ───────
    col_chart, col_panel = st.columns([3.5, 1], gap="medium")

    with col_chart:
        st.plotly_chart(_chart(), use_container_width=True)

    with col_panel:
        _panel_order()

    st.markdown("---")

    # ── Posisi & notifikasi ──────────────────────────────
    col_pos, col_log = st.columns([2.5, 1], gap="medium")
    with col_pos:
        _tabel_posisi()
    with col_log:
        st.markdown("#### 🔔 Aktivitas")
        _notif_bar()
        if not st.session_state.notif:
            st.markdown(
                f'<div style="color:{C_MUTED}; font-size:12px;">Belum ada aktivitas.</div>',
                unsafe_allow_html=True,
            )

    # ── Auto-refresh live mode ───────────────────────────
    if st.session_state.live:
        time.sleep(LIVE_INTERVAL_SEC)
        st.rerun()


if __name__ == "__main__":
    main()