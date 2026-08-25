"""Aero AI Trade — prototipe dashboard Headway MT5 berbasis sesi browser.

Desain: command-center cyber-finance yang tenang dan padat informasi.
Ruang lingkup sengaja dibatasi ke monitoring, guardrail, dan Paper Trading;
file ini tidak menyimpan kata sandi broker, tidak terhubung ke MT5, dan tidak
mengirim atau menutup order live.
"""

from __future__ import annotations

from datetime import datetime
import os
import time
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from trade_demo_client import DemoBridgeClient, DemoBridgeError


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


def _configured_bridge_client() -> DemoBridgeClient | None:
    """Membaca endpoint/token dari environment, bukan dari UI atau repository."""
    url, token = os.environ.get("AERO_TRADE_BRIDGE_URL", ""), os.environ.get("AERO_TRADE_BRIDGE_TOKEN", "")
    if not url and not token:
        return None
    if not url or not token:
        raise DemoBridgeError("Konfigurasi bridge belum lengkap di environment lokal.")
    return DemoBridgeClient(url, token)


def _bridge_status() -> tuple[DemoBridgeClient | None, dict | None, str | None]:
    """Heartbeat bridge hanya berjalan bila konfigurasi lokal sudah tersedia."""
    try:
        client = _configured_bridge_client()
        if client is None:
            return None, None, None
        client.heartbeat()
        return client, client.health(), None
    except DemoBridgeError as error:
        return None, None, str(error)


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
    bridge_client, bridge_state, bridge_error = _bridge_status()

    st.markdown('<div class="trade-shell">', unsafe_allow_html=True)
    st.markdown('<div class="trade-kicker">AEROVULPIS / EXECUTION CONTROL PROTOTYPE</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="trade-title">Aero AI <b>Trade</b></h1>', unsafe_allow_html=True)
    st.markdown('<div class="trade-subtitle">Dashboard untuk Paper Trading dan monitoring Headway MT5 akun demo melalui bridge lokal. Kredensial tidak ditulis pada UI, repository, ataupun log dashboard.</div>', unsafe_allow_html=True)
    st.markdown('<div class="trade-banner"><b>DEMO ONLY · FAIL-CLOSED</b><br>Jika bridge demo belum terpasang, dashboard tetap menjadi Paper Trading. Scan scalping hanya membaca kondisi M1; scan tidak mengirim order broker.</div>', unsafe_allow_html=True)

    auto_label = "PAPER AUTO MODE" if st.session_state.trade_auto_enabled else "PAPER AUTO MODE PAUSED"
    auto_dot = "good" if st.session_state.trade_auto_enabled else "warn"
    session_dot = "good" if session_active else "off"
    session_label = "AKTIF" if session_active else "KEDALUWARSA"
    bridge_ok = bool(bridge_state and bridge_state.get("ok") and bridge_state.get("mode") == "demo")
    broker_dot = "good" if bridge_ok else "warn"
    broker_label = "DEMO MT5 TERHUBUNG" if bridge_ok else "BRIDGE DEMO BELUM SIAP"
    bridge_kill = bool(bridge_state and bridge_state.get("kill_switch"))
    bridge_execution_enabled = bool(bridge_state and bridge_state.get("execution_enabled"))
    bridge_mode = "KILL SWITCH AKTIF" if bridge_kill else "BRIDGE DEMO"
    bridge_dot = "off" if bridge_kill else ("good" if bridge_ok else "warn")
    st.markdown('<div class="status-rail">' + _status_markup(broker_dot, "BROKER", broker_label) + _status_markup(session_dot, "BROWSER SESSION", session_label) + _status_markup(auto_dot, "PAPER", auto_label) + _status_markup(bridge_dot, "SCALPING", bridge_mode) + _status_markup("off", "LIVE ACCOUNT", "DITOLAK") + '</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-title">STATUS AKUN / HEADWAY MT5</div>', unsafe_allow_html=True)
    account_col, bridge_col = st.columns([1.1, 1])
    with account_col:
        with st.container(border=True):
            if bridge_ok:
                account = bridge_client.account() if bridge_client else {}
                st.markdown("**Headway MT5 demo terverifikasi**")
                left, right = st.columns(2)
                with left:
                    st.metric("Login demo", account.get("login_masked", "—"))
                    st.caption("Identitas akun ditampilkan sebagian untuk audit, bukan sebagai kredensial.")
                with right:
                    st.metric("Server", account.get("server", "—"))
                    st.caption(f"Saldo: {account.get('balance', '—')} {account.get('currency', '')}")
            else:
                st.markdown("**Koneksi demo belum dikonfigurasi**")
                st.caption("Login dilakukan manual di terminal Headway MT5 Windows. Setel URL dan token bridge sebagai environment lokal; dashboard tidak meminta password broker.")
                if bridge_error:
                    st.error(f"Status bridge: {bridge_error}")
                st.code('AERO_TRADE_BRIDGE_URL=http://127.0.0.1:8765\nAERO_TRADE_BRIDGE_TOKEN=<secret-lokal>', language="text")
    with bridge_col:
        st.markdown('<div class="guard-card"><p><b>Aturan sesi browser</b><br>Heartbeat berlaku 55 detik. Ketika panel/bridge mendeteksi TTL terlewati, mode otomatis dipause secara fail-closed dan proposal baru diblokir. Streamlit tidak mendeteksi penutupan tab secara asynchronous; bridge lokal menjadi pengawas utama.</p><p><b>Lingkup konektor saat ini</b><br>Bridge hanya menerima akun demo, membaca akun/posisi/history, menjalankan scan scalping M1, dan menjalankan kill switch. Tidak ada order dikirim oleh tombol scan.</p></div>', unsafe_allow_html=True)
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

    st.markdown('<div class="panel-title">SCALPING DEMO / M1 FILTER</div>', unsafe_allow_html=True)
    scan_col, result_col, kill_col = st.columns([1, 1.5, .9])
    with scan_col:
        scan_disabled = not bridge_ok or bridge_kill
        if st.button("Scan kondisi M1", type="primary", disabled=scan_disabled, use_container_width=True, help="Membaca candle dan tick dari terminal demo; tidak mengirim order."):
            try:
                st.session_state.trade_scalping_scan = bridge_client.scan_scalping() if bridge_client else None
                _log_event("Scan scalping M1 dilakukan melalui bridge demo tanpa order.")
            except DemoBridgeError as error:
                st.error(f"Scan gagal: {error}")
    with result_col:
        scan = st.session_state.get("trade_scalping_scan")
        if scan:
            decision_class = "green" if scan.get("decision") in {"BUY", "SELL"} else "yellow"
            st.markdown(_metric("KONDISI M1", scan.get("decision", "NO_TRADE"), scan.get("reason", "—"), decision_class), unsafe_allow_html=True)
            if scan.get("bid") is not None and scan.get("ask") is not None:
                st.caption(f"Quote demo broker · Bid {scan['bid']} · Ask {scan['ask']} · Spread {scan.get('spread_points', '—')} points")
            if scan.get("entry_block"):
                st.caption(f"Proposal diblokir: {scan['entry_block']}")
            else:
                st.caption("Kondisi teknis dapat ditinjau. Proposal order demo belum disiapkan pada dashboard ini.")
        else:
            st.caption("Scan menunggu bridge demo terverifikasi. Kondisi ambigu selalu dibaca sebagai NO_TRADE.")
    with kill_col:
        if st.button("Aktifkan kill switch", disabled=not bridge_ok, use_container_width=True):
            try:
                bridge_client.set_kill_switch() if bridge_client else None
                _log_event("Kill switch bridge demo diaktifkan dari dashboard.")
                st.rerun()
            except DemoBridgeError as error:
                st.error(f"Kill switch gagal: {error}")

    if bridge_ok:
        st.markdown('<div class="panel-title">PROPOSAL ORDER DEMO</div>', unsafe_allow_html=True)
        proposal_col, approval_col, execution_col = st.columns([1.15, 1.15, .9])
        with proposal_col:
            if st.button("Buat proposal dari scan", disabled=bridge_kill, use_container_width=True, help="Bridge menjalankan filter risiko dan order_check; tindakan ini belum mengirim order."):
                try:
                    st.session_state.trade_demo_proposal = bridge_client.create_scalping_proposal() if bridge_client else None
                    _log_event("Proposal order demo dibuat; belum ada order broker yang dikirim.")
                except DemoBridgeError as error:
                    st.error(f"Proposal tidak tersedia: {error}")
            proposal = st.session_state.get("trade_demo_proposal")
            if proposal:
                st.markdown(_metric("PROPOSAL", proposal["direction"], f"{proposal['symbol']} · {proposal['volume']:.2f} lot · berlaku {proposal['expires_in_seconds']} detik", "yellow"), unsafe_allow_html=True)
                st.caption(f"Entry {proposal['price']} · SL {proposal['sl']} · TP {proposal['tp']}")
        with approval_col:
            proposal = st.session_state.get("trade_demo_proposal")
            if proposal:
                demo_phrase = st.text_input("Frasa konfirmasi demo", placeholder="salin frasa dari proposal", key="trade-demo-confirmation")
                deliberate = st.checkbox("Saya meninjau detail order akun demo ini", key="trade-demo-deliberate")
                if not bridge_execution_enabled:
                    st.warning("Bridge demo masih mode aman. Set opt-in eksekusi pada Windows lokal hanya setelah meninjau proposal.")
            else:
                demo_phrase, deliberate = "", False
                st.caption("Frasa konfirmasi muncul hanya untuk proposal aktif dan tidak disimpan setelah sesi berakhir.")
        with execution_col:
            proposal = st.session_state.get("trade_demo_proposal")
            ready_to_execute = bool(proposal and bridge_execution_enabled and deliberate and demo_phrase == proposal["confirmation_phrase"])
            if st.button("Kirim order demo", type="primary", disabled=not ready_to_execute, use_container_width=True, help="Hanya aktif untuk proposal valid dengan frasa konfirmasi yang tepat."):
                try:
                    result = bridge_client.execute_proposal(proposal["proposal_id"], demo_phrase) if bridge_client else None
                    st.session_state.trade_demo_proposal = None
                    _log_event(f"Order demo dikonfirmasi broker: ticket {result.get('order', '—')}.")
                    st.success("Order demo diterima broker. Periksa tab posisi dan history MT5.")
                except DemoBridgeError as error:
                    st.error(f"Order demo tidak dikirim: {error}")

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
        if bridge_ok:
            st.markdown("**Posisi Headway MT5 demo milik Aero AI Trade**")
            try:
                broker_positions = (bridge_client.positions() if bridge_client else {}).get("items", [])
                if broker_positions:
                    st.dataframe(pd.DataFrame(broker_positions), use_container_width=True, hide_index=True)
                    for position in broker_positions:
                        ticket = int(position["ticket"])
                        close_phrase = st.text_input(f"Konfirmasi close {ticket}", placeholder=f"CLOSE-{ticket}", key=f"broker-close-phrase-{ticket}")
                        if st.button(f"Close demo {ticket}", disabled=not (bridge_execution_enabled and close_phrase == f"CLOSE-{ticket}"), key=f"broker-close-{ticket}"):
                            try:
                                result = bridge_client.close_position(ticket, close_phrase) if bridge_client else None
                                _log_event(f"Close demo dikonfirmasi broker: posisi {result.get('closed_ticket', ticket)}.")
                                st.success(f"Posisi demo {ticket} dikirim untuk ditutup.")
                            except DemoBridgeError as error:
                                st.error(f"Close demo tidak dikirim: {error}")
                else:
                    st.caption("Tidak ada posisi Aero AI Trade terbuka pada akun demo.")
            except DemoBridgeError as error:
                st.error(f"Posisi demo tidak dapat dibaca: {error}")
            st.markdown("**Riwayat deal Aero AI Trade · 7 hari**")
            try:
                broker_history = (bridge_client.history() if bridge_client else {}).get("items", [])
                if broker_history:
                    st.dataframe(pd.DataFrame(broker_history), use_container_width=True, hide_index=True)
                else:
                    st.caption("Belum ada deal Aero AI Trade pada riwayat akun demo.")
            except DemoBridgeError as error:
                st.error(f"Riwayat demo tidak dapat dibaca: {error}")
    with audit:
        st.markdown("**Audit trail sesi**")
        for event, timestamp in st.session_state.trade_audit:
            st.markdown(f'<div class="audit-line"><span>{event}</span><span class="audit-time">{timestamp}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-title">JALUR EKSEKUSI DEMO</div>', unsafe_allow_html=True)
    st.markdown('<div class="guard-card"><p>Urutan aman adalah: terminal Headway MT5 login ke akun demo → bridge memverifikasi mode demo → panel mengirim heartbeat → scan M1 menghasilkan kondisi teknis → order demo diringkas sebagai proposal yang berumur singkat → pengguna meninjau detail dan memberi konfirmasi eksplisit → bridge menjalankan pemeriksaan margin lalu mengirim order demo. Saat ini dashboard berhenti pada tahap scan dan proposal; tidak ada order yang dikirim otomatis.</p><p>Untuk akun live, mode ini tetap ditolak. Eksekusi live hanya dapat dipertimbangkan setelah periode uji demo, audit log stabil, dan konfirmasi terpisah untuk setiap tindakan broker.</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    render()
