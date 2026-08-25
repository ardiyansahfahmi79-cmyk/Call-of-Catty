"""Aero AI Trade — prototipe dashboard Headway MT5 berbasis sesi browser.

Desain: command-center cyber-finance yang tenang dan padat informasi.
Ruang lingkup sengaja dibatasi ke monitoring, guardrail, dan Paper Trading;
file ini tidak menyimpan kata sandi broker, tidak terhubung ke MT5, dan tidak
mengirim atau menutup order live.
"""

from __future__ import annotations

from datetime import datetime
import time
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st


WIB = ZoneInfo("Asia/Jakarta")
HEARTBEAT_TTL_SECONDS = 55
MAX_PAPER_POSITIONS = 1


TRADE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Share+Tech+Mono&display=swap');
:root { --at-ink:#05070b; --at-panel:#0d121b; --at-panel2:#121a27; --at-line:#273349; --at-text:#edf3f8; --at-muted:#93a0b2; --at-cyan:#18d9f5; --at-green:#35dc8b; --at-red:#ff6875; --at-yellow:#edc45f; }
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"] { background:var(--at-ink)!important; color:var(--at-text)!important; font-family:Manrope,sans-serif; }
.stApp { background-image:radial-gradient(circle at 85% 8%,rgba(24,217,245,.09),transparent 22%),linear-gradient(rgba(24,217,245,.018) 1px,transparent 1px),linear-gradient(90deg,rgba(24,217,245,.018) 1px,transparent 1px)!important; background-size:auto,42px 42px,42px 42px!important; }
.block-container { max-width:1180px; padding:1.2rem 1rem 2.5rem!important; }
.trade-shell { border-left:1px solid rgba(24,217,245,.3); border-right:1px solid rgba(24,217,245,.14); padding:0 1rem 1.4rem; }
.trade-kicker { color:var(--at-cyan); font:.64rem 'Share Tech Mono',monospace; letter-spacing:2px; }.trade-title { font-size:clamp(2.25rem,7vw,4rem); line-height:.95; letter-spacing:-3px; margin:.35rem 0 .65rem; color:#f4f8fb; }.trade-title b { color:var(--at-cyan); text-shadow:0 0 20px rgba(24,217,245,.45); }.trade-subtitle { color:var(--at-muted); max-width:720px; font-size:.86rem; line-height:1.65; }.trade-banner { border:1px solid rgba(237,196,95,.42); border-left:3px solid var(--at-yellow); border-radius:9px; padding:11px 13px; margin:1rem 0 1.15rem; background:rgba(237,196,95,.055); color:#e9d6a2; font-size:.78rem; line-height:1.55; }.trade-banner b{color:#fff3cc;}
.status-rail { display:flex; gap:8px; flex-wrap:wrap; margin:1rem 0; }.status-pill { display:inline-flex; align-items:center; gap:7px; border:1px solid var(--at-line); border-radius:999px; padding:6px 10px; font:.6rem 'Share Tech Mono',monospace; color:#bcc6d4; background:#0c111a; }.status-dot { width:7px; height:7px; border-radius:50%; background:var(--at-muted); }.status-dot.good { background:var(--at-green); box-shadow:0 0 10px rgba(53,220,139,.72); }.status-dot.warn { background:var(--at-yellow); box-shadow:0 0 10px rgba(237,196,95,.62); }.status-dot.off { background:var(--at-red); }
.panel-title { color:var(--at-cyan); font:.65rem 'Share Tech Mono',monospace; letter-spacing:1.5px; margin:1.35rem 0 .55rem; }.metric-card { min-height:104px; padding:13px; border:1px solid var(--at-line); background:linear-gradient(135deg,rgba(18,26,39,.94),rgba(10,14,21,.97)); border-radius:10px; }.metric-card .label { color:var(--at-muted); font:.58rem 'Share Tech Mono',monospace; letter-spacing:1.1px; }.metric-card .value { color:var(--at-text); margin-top:8px; font-size:1.16rem; font-weight:800; }.metric-card .meta { color:#78879a; margin-top:5px; font-size:.67rem; }.green { color:var(--at-green)!important; }.yellow { color:var(--at-yellow)!important; }.red { color:var(--at-red)!important; }
.guard-card { border:1px solid var(--at-line); border-top:2px solid rgba(24,217,245,.62); background:#0c121b; border-radius:12px; padding:15px; margin:.35rem 0 .8rem; }.guard-card p { color:var(--at-muted); font-size:.76rem; line-height:1.55; margin:0 0 .75rem; }.audit-line { padding:8px 0; border-bottom:1px solid #1e2938; display:flex; justify-content:space-between; gap:12px; color:#c5cfdb; font-size:.72rem; }.audit-line:last-child { border-bottom:0; }.audit-time { color:#758397; font-family:'Share Tech Mono',monospace; white-space:nowrap; }
.stButton>button { background:#111a27!important; color:#e9f4fa!important; border:1px solid #35465a!important; border-radius:8px!important; font-weight:700!important; min-height:40px!important; }.stButton>button:hover { border-color:var(--at-cyan)!important; color:var(--at-cyan)!important; }.stButton>button[kind="primary"] { background:linear-gradient(90deg,#049db7,#18d9f5)!important; border-color:#18d9f5!important; color:#021217!important; }.stTextInput input,.stNumberInput input { background:#101824!important; color:#edf3f8!important; border-color:#36495f!important; }.stSelectbox div[data-baseweb="select"] > div { background:#101824!important; color:#edf3f8!important; border-color:#36495f!important; }.stDataFrame { border:1px solid var(--at-line); border-radius:9px; overflow:hidden; }
@media(max-width:640px){.block-container{padding:.75rem .55rem 1.5rem!important}.trade-shell{padding:0 .55rem 1rem}.trade-title{letter-spacing:-2.1px}.metric-card{min-height:94px}.trade-subtitle{font-size:.8rem}}
</style>
"""


def _wib_now() -> str:
    return datetime.now(WIB).strftime("%d %b %Y · %H:%M:%S WIB")


def _init_state() -> None:
    defaults = {
        "trade_paper_mode": True,
        "trade_auto_enabled": False,
        "trade_last_heartbeat": time.time(),
        "trade_session_active": True,
        "trade_audit": [
            ("Sistem siap dalam mode Paper Trading; tidak ada koneksi broker.", _wib_now()),
            ("Risk guard aktif sebelum mode otomatis dapat disimulasikan.", _wib_now()),
        ],
        "trade_positions": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _session_is_fresh(last_heartbeat: float, now: float, ttl_seconds: int = HEARTBEAT_TTL_SECONDS) -> bool:
    """Mengembalikan True bila heartbeat sesi masih berada dalam toleransi waktu."""
    return (now - last_heartbeat) <= ttl_seconds


def _paper_entry_block_reason(
    paper_enabled: bool,
    auto_enabled: bool,
    session_active: bool,
    current_positions: int,
    max_positions: int = MAX_PAPER_POSITIONS,
) -> str | None:
    """Memusatkan aturan blokir entry agar test dan UI memakai kebijakan yang sama."""
    if not paper_enabled:
        return "Paper Trading belum aktif."
    if not session_active:
        return "Heartbeat browser sudah kedaluwarsa; refresh sesi sebelum membuat simulasi baru."
    if not auto_enabled:
        return "Auto Trade simulasi sedang pause. Aktifkan mode simulasi terlebih dahulu."
    if current_positions >= max_positions:
        return f"Batas {max_positions} posisi Paper Trading telah tercapai."
    return None


def _new_paper_position(sequence: int) -> dict[str, str]:
    """Membuat catatan posisi Paper Trading tanpa menyertakan harga atau hasil pasar fiktif."""
    return {
        "ID": f"PAPER-{sequence:03d}",
        "Simbol": "XAUUSD",
        "Arah": "BUY",
        "Lot": "0.01",
        "Status": "OPEN · PAPER",
        "Quote": "Tidak dikutip pada prototipe",
    }


def _close_paper_position(positions: list[dict[str, str]], position_id: str) -> tuple[list[dict[str, str]], bool]:
    """Menghapus satu catatan posisi simulasi; fungsi ini tidak dapat menutup posisi broker."""
    remaining = [position for position in positions if position["ID"] != position_id]
    return remaining, len(remaining) != len(positions)


def _log_event(message: str) -> None:
    st.session_state.trade_audit.insert(0, (message, _wib_now()))
    st.session_state.trade_audit = st.session_state.trade_audit[:8]


def _heartbeat() -> None:
    st.session_state.trade_last_heartbeat = time.time()
    st.session_state.trade_session_active = True


def _enforce_session_guard() -> bool:
    """Fail closed bila Streamlit menerima rerun setelah heartbeat telah kedaluwarsa."""
    fresh = _session_is_fresh(st.session_state.trade_last_heartbeat, time.time())
    if not fresh:
        st.session_state.trade_session_active = False
        if st.session_state.trade_auto_enabled:
            st.session_state.trade_auto_enabled = False
            _log_event("Heartbeat browser kedaluwarsa; Auto Trade simulasi dipause secara fail-closed.")
    return fresh


def _status_markup(dot_class: str, label: str, value: str) -> str:
    return f'<span class="status-pill"><span class="status-dot {dot_class}"></span>{label}: <b>{value}</b></span>'


def _metric(label: str, value: str, meta: str, accent: str = "") -> str:
    return f'<div class="metric-card"><div class="label">{label}</div><div class="value {accent}">{value}</div><div class="meta">{meta}</div></div>'


def render() -> None:
    """Render dashboard paper-trading; tidak mengirim order ke Headway atau MT5."""
    st.set_page_config(page_title="Aero AI Trade", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")
    st.markdown(TRADE_CSS, unsafe_allow_html=True)
    _init_state()
    session_active = _enforce_session_guard()

    st.markdown('<div class="trade-shell">', unsafe_allow_html=True)
    st.markdown('<div class="trade-kicker">AEROVULPIS / EXECUTION CONTROL PROTOTYPE</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="trade-title">Aero AI <b>Trade</b></h1>', unsafe_allow_html=True)
    st.markdown('<div class="trade-subtitle">Dashboard prototipe untuk memantau kesiapan koneksi Headway MT5, browser heartbeat, risk guard, dan Paper Trading. Tidak ada kredensial broker, koneksi MT5, atau order live pada versi ini.</div>', unsafe_allow_html=True)
    st.markdown('<div class="trade-banner"><b>MODE PROTOTIPE / PAPER TRADING</b><br>Kontrol di bawah hanya mensimulasikan alur dashboard. Browser yang aktif dianggap sebagai heartbeat sesi; bila sesi berakhir, mode otomatis simulasi dipause.</div>', unsafe_allow_html=True)

    auto_label = "PAPER AUTO MODE" if st.session_state.trade_auto_enabled else "PAPER AUTO MODE PAUSED"
    auto_dot = "good" if st.session_state.trade_auto_enabled else "warn"
    session_dot = "good" if session_active else "off"
    session_label = "AKTIF" if session_active else "KEDALUWARSA"
    st.markdown('<div class="status-rail">' + _status_markup("warn", "BROKER", "BELUM TERHUBUNG") + _status_markup(session_dot, "BROWSER SESSION", session_label) + _status_markup(auto_dot, "MODE", auto_label) + _status_markup("off", "LIVE EXECUTION", "DINONAKTIFKAN") + '</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-title">STATUS AKUN / HEADWAY MT5</div>', unsafe_allow_html=True)
    account_col, bridge_col = st.columns([1.1, 1])
    with account_col:
        with st.container(border=True):
            st.markdown("**Koneksi broker belum dikonfigurasi**")
            st.caption("Untuk integrasi nyata, pengguna login di terminal Headway MT5 miliknya. Dashboard tidak meminta atau menyimpan password broker.")
            left, right = st.columns(2)
            with left:
                st.text_input("MT5 Login ID", placeholder="Diisi oleh bridge lokal", disabled=True)
            with right:
                st.text_input("Server Headway", value="Headway MT5", disabled=True)
            st.button("Verifikasi koneksi MT5", disabled=True, help="Dinonaktifkan pada prototipe. Tidak ada koneksi broker yang dibuat.")
    with bridge_col:
        st.markdown('<div class="guard-card"><p><b>Aturan sesi browser</b><br>Heartbeat berlaku 55 detik. Ketika halaman mendapatkan rerun setelah TTL berakhir, mode otomatis dipause secara fail-closed dan entry simulasi diblokir. Streamlit tidak mendeteksi penutupan tab secara asynchronous; bridge produksi wajib menerapkan fail-closed sendiri.</p><p><b>Integrasi berikutnya</b><br>Headway MT5 desktop + bridge lokal + database audit. Tahap berikutnya dimulai dari akun demo, bukan akun live.</p></div>', unsafe_allow_html=True)
        if st.button("Refresh heartbeat sesi", use_container_width=True):
            _heartbeat()
            _log_event("Heartbeat browser disegarkan oleh interaksi pengguna.")
            st.rerun()

    st.markdown('<div class="panel-title">RISK GUARD / KEBIJAKAN SIMULASI</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_metric("MAX LOT / ORDER", "0.01", "parameter simulasi", "yellow"), unsafe_allow_html=True)
    with c2:
        st.markdown(_metric("MAX POSISI", "1", "satu simbol / satu arah", "yellow"), unsafe_allow_html=True)
    with c3:
        st.markdown(_metric("BATAS RISIKO", "0.50%", "per skenario simulasi", "yellow"), unsafe_allow_html=True)
    with c4:
        st.markdown(_metric("WHITELIST", "XAUUSD", "dapat dikonfigurasi nanti", "green"), unsafe_allow_html=True)

    st.markdown('<div class="panel-title">KONTROL PAPER TRADING</div>', unsafe_allow_html=True)
    control_left, control_mid, control_right = st.columns([1.1, 1, 1])
    with control_left:
        paper_mode = st.toggle("Paper Trading aktif", value=st.session_state.trade_paper_mode, key="trade-paper-toggle")
        st.session_state.trade_paper_mode = paper_mode
        st.caption("Tidak ada order dikirim. Status hanya digunakan untuk memvalidasi alur kontrol.")
    with control_mid:
        activate_disabled = not st.session_state.trade_paper_mode or not session_active
        if st.button("Aktifkan Auto Trade Simulasi", type="primary", disabled=activate_disabled, use_container_width=True):
            st.session_state.trade_auto_enabled = True
            _log_event("Auto Trade simulasi diaktifkan; bridge broker tetap tidak tersedia.")
            st.rerun()
    with control_right:
        if st.button("Emergency Stop", use_container_width=True):
            st.session_state.trade_auto_enabled = False
            _log_event("Emergency Stop diterapkan; seluruh order baru simulasi diblokir.")
            st.rerun()

    entry_reason = _paper_entry_block_reason(
        st.session_state.trade_paper_mode,
        st.session_state.trade_auto_enabled,
        session_active,
        len(st.session_state.trade_positions),
    )
    if st.session_state.trade_auto_enabled:
        st.success("Auto Trade simulasi aktif. Browser heartbeat tercatat, tetapi prototipe tidak membuka posisi atau mengirim order ke Headway.")
    else:
        st.info("Auto Trade simulasi sedang pause. Gunakan mode ini untuk menguji alur dashboard sebelum ada bridge Headway MT5.")

    if st.button("Buat posisi XAUUSD simulasi", disabled=entry_reason is not None, use_container_width=False, help=entry_reason or "Menambah catatan posisi Paper Trading tanpa quote atau order broker."):
        paper_position = _new_paper_position(len(st.session_state.trade_positions) + 1)
        st.session_state.trade_positions.append(paper_position)
        _heartbeat()
        _log_event(f"{paper_position['ID']} dibuat sebagai posisi Paper Trading; tidak ada quote atau order broker.")
        st.rerun()
    if entry_reason:
        st.caption(f"Guard entry: {entry_reason}")

    st.markdown('<div class="panel-title">POSISI & AUDIT TRAIL</div>', unsafe_allow_html=True)
    positions, audit = st.columns([1.05, 1])
    with positions:
        st.markdown("**Posisi simulasi**")
        if st.session_state.trade_positions:
            st.dataframe(pd.DataFrame(st.session_state.trade_positions), use_container_width=True, hide_index=True)
            for position in st.session_state.trade_positions:
                close_col, meta_col = st.columns([.8, 1.2])
                with close_col:
                    if st.button(f"Close {position['ID']} (Paper)", key=f"close-{position['ID']}", use_container_width=True):
                        remaining, closed = _close_paper_position(st.session_state.trade_positions, position["ID"])
                        if closed:
                            st.session_state.trade_positions = remaining
                            _heartbeat()
                            _log_event(f"{position['ID']} ditutup dalam catatan Paper Trading; tidak ada perintah broker.")
                            st.rerun()
                with meta_col:
                    st.caption(f"{position['ID']} hanya catatan simulasi, bukan posisi Headway MT5.")
        else:
            st.caption("Belum ada posisi simulasi. Koneksi broker dan eksekusi live sengaja tidak tersedia pada prototipe ini.")
            st.dataframe(pd.DataFrame(columns=["ID", "Simbol", "Arah", "Lot", "Status", "Quote"]), use_container_width=True, hide_index=True)
        st.button("Close semua posisi", disabled=True, help="Dinonaktifkan: prototipe tidak memiliki posisi atau akses broker.")
    with audit:
        st.markdown("**Audit trail sesi**")
        for event, timestamp in st.session_state.trade_audit:
            st.markdown(f'<div class="audit-line"><span>{event}</span><span class="audit-time">{timestamp}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-title">KONDISI SEBELUM INTEGRASI LIVE</div>', unsafe_allow_html=True)
    st.markdown('<div class="guard-card"><p>Versi live hanya boleh dipertimbangkan setelah bridge Headway MT5 berhasil diverifikasi pada akun demo, risk guard diuji, audit log tersimpan, dan tombol pengiriman order memiliki konfirmasi eksplisit. Tidak ada data login, password, token broker, atau instruksi order live yang dikumpulkan oleh halaman ini.</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    render()
