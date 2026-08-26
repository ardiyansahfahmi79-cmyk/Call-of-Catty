"""AeroVulpis Kalkulator Risiko — perencanaan lokal tanpa koneksi broker.

Filosofi visual: satu tugas per bagian, istilah bahasa Indonesia sederhana,
hasil hanya muncul setelah pengguna menekan tombol, dan kurs selalu beratribusi.
"""

from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen

import streamlit as st

from risk_management_core import calculate_risk_snapshot


st.set_page_config(
    page_title="AeroVulpis — Kalkulator Risiko",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
    /* Simple Risk visual system: calm dark surface, one task, readable mobile controls. */
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root { --bg:#081018; --card:#101a26; --line:#203347; --blue:#46c9ff; --green:#36e49a; --red:#ff6c8e; --text:#eef5fa; --muted:#9fb0bf; }
    .stApp { background:radial-gradient(circle at 85% 2%,rgba(41,126,174,.16),transparent 27%),var(--bg); color:var(--text); }
    .block-container { max-width:780px; padding-top:2.2rem; padding-bottom:3rem; }
    header, footer, #MainMenu { visibility:hidden; }
    .mini { font-family:'DM Mono',monospace; font-size:.69rem; color:var(--blue); letter-spacing:.1em; text-transform:uppercase; }
    .title { font-family:'Manrope',sans-serif; font-size:clamp(2rem,8vw,3.25rem); font-weight:800; letter-spacing:-.06em; line-height:1; margin:.45rem 0 .7rem; color:var(--text); }
    .title span { color:var(--green); }
    .intro { color:var(--muted); font-family:'Manrope',sans-serif; line-height:1.6; font-size:.98rem; max-width:650px; margin-bottom:1.35rem; }
    .card { background:linear-gradient(145deg,rgba(20,31,45,.96),rgba(13,21,31,.96)); border:1px solid var(--line); border-radius:16px; padding:1rem; margin:.5rem 0 1rem; }
    .step { font-family:'Manrope',sans-serif; font-size:1.02rem; font-weight:700; margin:0 0 .9rem; color:var(--text); }
    .helper { color:var(--muted); font-size:.82rem; line-height:1.45; margin-top:-.25rem; margin-bottom:.75rem; }
    .result-card { background:linear-gradient(145deg,rgba(18,42,56,.92),rgba(13,24,34,.98)); border:1px solid rgba(70,201,255,.18); border-radius:14px; padding:1rem; min-height:122px; }
    .result-label { font-family:'Manrope',sans-serif; color:var(--muted); font-size:.78rem; font-weight:600; }
    .result-value { font-family:'Manrope',sans-serif; color:var(--text); font-size:1.7rem; font-weight:800; letter-spacing:-.04em; margin:.4rem 0 .22rem; }
    .result-copy { font-size:.75rem; color:var(--muted); line-height:1.35; }
    .fx-value { font-family:'Manrope',sans-serif; font-size:2rem; color:var(--green); font-weight:800; letter-spacing:-.04em; margin:.35rem 0; }
    .green { color:var(--green); } .blue { color:var(--blue); } .red { color:var(--red); }
    div[data-testid='stNumberInput'] label, div[data-testid='stSlider'] label { font-family:'Manrope',sans-serif!important; font-size:.84rem!important; font-weight:700!important; color:#dfeaf2!important; }
    div[data-testid='stNumberInput'] input { background:#09121c!important; color:var(--text)!important; border:1px solid #2a4055!important; border-radius:10px!important; font-family:'DM Mono',monospace!important; }
    div[data-testid='stNumberInput'] button { background:#122333!important; color:var(--blue)!important; border-color:#2a4055!important; }
    .stButton>button { background:var(--green)!important; color:#062116!important; border:0!important; border-radius:10px!important; min-height:48px!important; font-family:'Manrope',sans-serif!important; font-weight:800!important; }
    .stButton>button:active { transform:scale(.98); }
    div[data-testid='stExpander'] { background:rgba(10,17,25,.72); border:1px solid var(--line); border-radius:12px; }
    .notice { background:rgba(31,100,130,.12); border-left:3px solid var(--blue); color:#bfdae8; padding:.8rem .9rem; border-radius:0 9px 9px 0; font-size:.83rem; line-height:1.45; }
    .empty-result { border:1px dashed #2d465c; background:rgba(15,27,39,.5); border-radius:14px; padding:1rem; color:var(--muted); font-size:.88rem; }
    .footer-note { margin-top:1.7rem; color:#718697; font-size:.73rem; text-align:center; line-height:1.55; }
    @media (max-width:700px) { .block-container { padding:1.25rem 1rem 2.4rem; } .title { font-size:2.45rem; } .result-card { min-height:104px; padding:.85rem; } .result-value { font-size:1.38rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def money(value: float) -> str:
    return f"${value:,.2f}"


def rupiah(value: float) -> str:
    return "Rp " + f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def result_card(label: str, value: str, description: str, color: str) -> str:
    return f"""
    <div class='result-card'>
      <div class='result-label'>{label}</div>
      <div class='result-value {color}'>{value}</div>
      <div class='result-copy'>{description}</div>
    </div>
    """


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_usd_idr_rate() -> dict[str, object]:
    """Mengambil kurs referensi harian tanpa API key dan tanpa fallback fiktif."""
    try:
        request = Request(
            "https://open.er-api.com/v6/latest/USD",
            headers={"User-Agent": "AeroVulpisRiskCalculator/1.0"},
        )
        with urlopen(request, timeout=8) as response:  # nosec B310 - fixed HTTPS endpoint
            payload = json.loads(response.read().decode("utf-8"))
        rate = float(payload["rates"]["IDR"])
        if payload.get("result") != "success" or rate <= 0:
            raise ValueError("Respons kurs tidak valid")
        return {
            "ok": True,
            "rate": rate,
            "updated": str(payload.get("time_last_update_utc", "waktu pembaruan tidak tersedia")),
            "next_update": str(payload.get("time_next_update_utc", "jadwal pembaruan tidak tersedia")),
        }
    except (URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as error:
        return {"ok": False, "error": str(error)}


st.markdown("<div class='mini'>AEROVULPIS / SIMULASI LOKAL</div>", unsafe_allow_html=True)
st.markdown("<div class='title'>Kalkulator <span>Risiko</span></div>", unsafe_allow_html=True)
st.markdown("<p class='intro'>Isi angka di bawah, lalu tekan tombol hitung. Hasil tidak akan ditampilkan sebelum Anda menjalankan perhitungan. Tidak terhubung ke akun broker.</p>", unsafe_allow_html=True)

with st.form("risk_calculator_form", clear_on_submit=False):
    st.markdown("<div class='card'><div class='step'>1. Tentukan saldo dan risiko</div>", unsafe_allow_html=True)
    left, right = st.columns(2, gap="medium")
    with left:
        balance = st.number_input("Saldo akun (USD)", min_value=10.0, max_value=10_000_000.0, value=1000.0, step=50.0, format="%.2f")
    with right:
        risk_percent = st.slider("Risiko per transaksi (%)", min_value=0.25, max_value=10.0, value=1.0, step=0.25)
    st.markdown("<div class='helper'>Contoh sederhana: saldo $1.000 dengan risiko 1% berarti risiko maksimal $10 untuk satu rencana transaksi.</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='card'><div class='step'>2. Masukkan rencana harga</div>", unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3, gap="small")
    with p1:
        entry = st.number_input("Harga masuk", min_value=0.0001, value=2350.0, step=0.1, format="%.4f")
    with p2:
        stop_loss = st.number_input("Stop Loss", min_value=0.0001, value=2345.0, step=0.1, format="%.4f")
    with p3:
        take_profit = st.number_input("Target Profit", min_value=0.0001, value=2360.0, step=0.1, format="%.4f")
    st.markdown("<div class='helper'>Harga masuk adalah rencana entry. Stop Loss membatasi kerugian. Target Profit adalah target rencana Anda.</div></div>", unsafe_allow_html=True)

    with st.expander("Pengaturan tambahan (opsional)"):
        instrument = st.selectbox("Instrumen", ["XAUUSD / Emas", "Forex mayor", "Indeks / CFD", "Lainnya"], index=0)
        default_value = 100.0 if instrument == "XAUUSD / Emas" else 10.0 if instrument == "Forex mayor" else 1.0
        price_move_value_per_lot = st.number_input(
            "Nilai pergerakan harga untuk 1 lot (USD)",
            min_value=0.0001,
            value=default_value,
            step=1.0,
            format="%.4f",
            help="Nilai ini berbeda pada setiap broker/instrumen. Cek spesifikasi kontrak broker untuk hasil lot yang lebih akurat.",
        )
        daily_loss_percent = st.slider("Batas rugi harian (%)", min_value=0.5, max_value=20.0, value=5.0, step=0.5)

    calculate_pressed = st.form_submit_button("HITUNG RISIKO SAYA", use_container_width=True)

if calculate_pressed:
    snapshot = calculate_risk_snapshot(
        balance=balance,
        risk_percent=risk_percent,
        daily_loss_percent=daily_loss_percent,
        daily_profit_percent=100.0,
        entry=entry,
        stop_loss=stop_loss,
        take_profit=take_profit,
        price_move_value_per_lot=price_move_value_per_lot,
        wins=0,
        losses=0,
    )
    st.session_state["risk_result"] = {
        "snapshot": snapshot,
        "risk_percent": risk_percent,
    }

st.markdown("<div class='mini' style='margin:1.6rem 0 .45rem'>HASIL PERHITUNGAN</div>", unsafe_allow_html=True)
result = st.session_state.get("risk_result")
if not result:
    st.markdown("<div class='empty-result'>Hasil akan muncul di sini setelah Anda menekan <b>Hitung Risiko Saya</b>.</div>", unsafe_allow_html=True)
else:
    snapshot = result["snapshot"]
    calculated_risk_percent = float(result["risk_percent"])
    cards = st.columns(2, gap="medium")
    with cards[0]:
        st.markdown(result_card("Jika Stop Loss terkena", money(snapshot.risk_amount), f"{calculated_risk_percent:.2f}% dari saldo Anda", "red"), unsafe_allow_html=True)
    with cards[1]:
        potential = snapshot.risk_amount * snapshot.reward_risk
        st.markdown(result_card("Jika target tercapai", money(potential), "Potensi berdasarkan jarak target", "green"), unsafe_allow_html=True)
    with cards[0]:
        st.markdown(result_card("Perbandingan risiko : target", f"1 : {snapshot.reward_risk:.2f}", "Semakin besar angka kanan, semakin besar target dibanding risiko", "blue"), unsafe_allow_html=True)
    with cards[1]:
        st.markdown(result_card("Perkiraan ukuran lot", f"{snapshot.estimated_lots:.3f}", "Selalu cocokkan dengan spesifikasi broker", "blue"), unsafe_allow_html=True)

    if snapshot.stop_distance <= 0:
        st.error("Stop Loss harus berbeda dari Harga Masuk agar risiko dapat dihitung.")
    elif snapshot.reward_risk < 1:
        st.warning("Target Anda lebih kecil daripada risiko. Periksa kembali Stop Loss atau Target Profit sebelum membuat keputusan.")
    else:
        st.markdown("<div class='notice'>Ringkasan: rencana Anda memiliki Stop Loss yang terisi dan target lebih besar atau sama dengan risiko. Ini bukan rekomendasi untuk entry; gunakan sebagai bahan mengecek rencana sendiri.</div>", unsafe_allow_html=True)

st.markdown("<div class='mini' style='margin:1.7rem 0 .45rem'>KONVERTER USD → RUPIAH</div>", unsafe_allow_html=True)
st.markdown("<div class='card'><div class='step'>Konversi USD ke Rupiah</div>", unsafe_allow_html=True)
amount_col, update_col = st.columns([1.2, 1], gap="medium")
with amount_col:
    usd_amount = st.number_input("Jumlah USD", min_value=0.0, value=100.0, step=10.0, format="%.2f")
with update_col:
    refresh_rate = st.button("PERBARUI KURS", use_container_width=True)
if refresh_rate:
    st.session_state["usd_idr_rate"] = fetch_usd_idr_rate()

fx = st.session_state.get("usd_idr_rate")
if fx and fx.get("ok"):
    idr_value = usd_amount * float(fx["rate"])
    st.markdown(f"<div class='fx-value'>{money(usd_amount)} = {rupiah(idr_value)}</div>", unsafe_allow_html=True)
    st.caption(f"Kurs referensi: 1 USD = {rupiah(float(fx['rate']))} · pembaruan sumber: {fx['updated']}")
    st.caption(f"Pembaruan berikutnya menurut sumber: {fx['next_update']}")
    st.markdown("Sumber: [Rates By Exchange Rate API](https://www.exchangerate-api.com)")
elif fx and not fx.get("ok"):
    st.warning("Kurs publik tidak dapat dimuat. Tidak ada kurs pengganti yang dibuat oleh aplikasi.")
    manual_rate = st.number_input("Masukkan kurs USD–IDR manual (opsional)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
    if manual_rate > 0:
        st.markdown(f"<div class='fx-value'>{money(usd_amount)} = {rupiah(usd_amount * manual_rate)}</div>", unsafe_allow_html=True)
        st.caption("Menggunakan kurs manual yang Anda masukkan, bukan kurs dari sumber publik.")
else:
    st.markdown("<div class='empty-result'>Tekan <b>Perbarui Kurs</b> untuk mengambil kurs referensi USD–Rupiah beserta waktu pembaruannya.</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='footer-note'>AEROVULPIS KALKULATOR RISIKO · UNTUK EDUKASI DAN PERENCANAAN · BUKAN NASIHAT FINANSIAL PERSONAL ATAU SISTEM EKSEKUSI</div>", unsafe_allow_html=True)
