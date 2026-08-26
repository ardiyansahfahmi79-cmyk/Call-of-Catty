"""AeroVulpis Kalkulator Risiko — perencanaan lokal tanpa koneksi broker.

Filosofi visual: satu tugas per bagian, istilah bahasa Indonesia sederhana,
hasil hanya muncul setelah pengguna menekan tombol, dan kurs selalu beratribusi.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import plotly.graph_objects as go
import streamlit as st

from currency_converter_core import (
    available_currency_codes,
    convert_from_usd_reference,
    currency_label,
    currency_pair_label,
)
from currency_trend_core import CURRENCY_TREND_DAYS, parse_historical_rates, trend_change_percent
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
    .trend-summary { color:var(--muted); font-size:.82rem; line-height:1.5; margin:.45rem 0 .3rem; }
    .pair-readout { font-family:'DM Mono',monospace; color:var(--blue); font-size:.9rem; padding:.72rem .82rem; border:1px solid rgba(70,201,255,.22); border-radius:10px; background:rgba(20,56,74,.22); margin:.2rem 0 .75rem; }
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


def format_exchange_rate(value: float) -> str:
    """Mempertahankan detail kurs kecil tanpa membebani hasil kurs bernilai besar."""
    decimals = 2 if value >= 100 else 4 if value >= 1 else 6
    return f"{value:,.{decimals}f}"


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
        rates = {str(code): float(rate) for code, rate in payload["rates"].items()}
        if payload.get("result") != "success" or not available_currency_codes(rates):
            raise ValueError("Respons kurs tidak valid")
        return {
            "ok": True,
            "rates": rates,
            "updated": str(payload.get("time_last_update_utc", "waktu pembaruan tidak tersedia")),
            "next_update": str(payload.get("time_next_update_utc", "jadwal pembaruan tidak tersedia")),
        }
    except (URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as error:
        return {"ok": False, "error": str(error)}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_currency_trend(base_code: str, quote_code: str) -> dict[str, object]:
    """Mengambil maksimum tiga puluh hari kalender kurs referensi historis tanpa API key."""
    if base_code == quote_code:
        return {"ok": False, "error": "Pilih dua mata uang yang berbeda untuk grafik tren."}
    if base_code not in available_currency_codes({base_code: 1.0}) or quote_code not in available_currency_codes({quote_code: 1.0}):
        return {"ok": False, "error": "Pasangan mata uang tidak tersedia untuk grafik."}

    end_date = datetime.now(UTC).date()
    start_date = end_date - timedelta(days=CURRENCY_TREND_DAYS)
    parameters = urlencode({"base": base_code, "symbols": quote_code})
    url = f"https://api.frankfurter.dev/v1/{start_date.isoformat()}..{end_date.isoformat()}?{parameters}"
    try:
        request = Request(url, headers={"User-Agent": "AeroVulpisRiskCalculator/1.0"})
        with urlopen(request, timeout=8) as response:  # nosec B310 - fixed HTTPS endpoint
            payload = json.loads(response.read().decode("utf-8"))
        points = parse_historical_rates(payload, quote_code)
        if not points:
            raise ValueError("Riwayat kurs tidak tersedia untuk pasangan ini")
        return {
            "ok": True,
            "points": points,
            "start": str(payload.get("start_date", start_date.isoformat())),
            "end": str(payload.get("end_date", end_date.isoformat())),
            "source": "Frankfurter — kurs referensi bank sentral",
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

st.markdown("<div class='mini' style='margin:1.7rem 0 .45rem'>KONVERTER MATA UANG</div>", unsafe_allow_html=True)
st.markdown("<div class='card'><div class='step'>Bandingkan kurs antar mata uang</div><div class='helper'>Pilih dua mata uang untuk melihat nilai <b>1 unit</b>. Daftar dibatasi pada 90 mata uang negara lintas kawasan.</div>", unsafe_allow_html=True)
refresh_rate = st.button("MUAT KURS & 90 MATA UANG", use_container_width=True)
if refresh_rate:
    st.session_state["usd_idr_rate"] = fetch_usd_idr_rate()

fx = st.session_state.get("usd_idr_rate")
if fx and fx.get("ok"):
    rates = fx["rates"]
    codes = available_currency_codes(rates)
    st.caption(f"Tersedia {len(codes)} pilihan mata uang negara dari sumber publik.")
    search_term = st.text_input(
        "Pencarian cepat mata uang",
        placeholder="Cari kode, misalnya IDR atau USD",
        key="currency_search_term",
    ).strip().upper()
    matching_codes = [code for code in codes if search_term in code or search_term in currency_label(code).upper()]
    if search_term and not matching_codes:
        st.info("Tidak ada kode mata uang yang cocok. Kosongkan pencarian untuk melihat seluruh daftar.")

    selected_from = st.session_state.get("currency_from_code", "IDR")
    selected_to = st.session_state.get("currency_to_code", "USD")
    from_choices = matching_codes if selected_from in matching_codes else [selected_from, *matching_codes]
    to_choices = matching_codes if selected_to in matching_codes else [selected_to, *matching_codes]
    from_index = from_choices.index(selected_from) if selected_from in from_choices else 0
    to_index = to_choices.index(selected_to) if selected_to in to_choices else 0
    from_col, to_col = st.columns(2, gap="medium")
    with from_col:
        from_code = st.selectbox("Mata uang asal", from_choices, index=from_index, format_func=currency_label, key="currency_from_code")
    with to_col:
        to_code = st.selectbox("Mata uang pembanding", to_choices, index=to_index, format_func=currency_label, key="currency_to_code")
    compared_rate = convert_from_usd_reference(1.0, from_code, to_code, rates)
    st.markdown(f"<div class='pair-readout'>{currency_pair_label(from_code, to_code)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='fx-value'>1 {from_code} = {format_exchange_rate(compared_rate)} {to_code}</div>", unsafe_allow_html=True)
    st.caption("Perbandingan kurs untuk satu unit mata uang asal.")
    st.caption(f"Kurs referensi dihitung dari basis USD · pembaruan sumber: {fx['updated']}")
    st.caption(f"Pembaruan berikutnya menurut sumber: {fx['next_update']}")
    st.markdown("Sumber: [Rates By Exchange Rate API](https://www.exchangerate-api.com)")

    trend_key = f"{from_code}_{to_code}"
    if st.button(f"TAMPILKAN GRAFIK TREN {CURRENCY_TREND_DAYS} HARI", use_container_width=True, key=f"trend_{trend_key}"):
        st.session_state["currency_trend"] = {
            "pair": trend_key,
            "data": fetch_currency_trend(from_code, to_code),
        }

    trend_state = st.session_state.get("currency_trend")
    if trend_state and trend_state.get("pair") == trend_key:
        trend = trend_state["data"]
        if trend.get("ok"):
            points = trend["points"]
            change = trend_change_percent(points)
            st.markdown(f"<div class='mini' style='margin:1rem 0 .2rem'>GRAFIK TREN KURS · {CURRENCY_TREND_DAYS} HARI KALENDER</div>", unsafe_allow_html=True)
            figure = go.Figure(
                go.Scatter(
                    x=[point["Tanggal"] for point in points],
                    y=[point["Kurs"] for point in points],
                    mode="lines+markers",
                    line={"color": "#46c9ff", "width": 3},
                    marker={"color": "#36e49a", "size": 5},
                    hoverinfo="skip",
                )
            )
            figure.update_layout(
                height=270,
                margin={"l": 10, "r": 10, "t": 10, "b": 10},
                paper_bgcolor="#0c1721",
                plot_bgcolor="#0c1721",
                font={"family": "Manrope, sans-serif", "color": "#c9d8e2", "size": 11},
                showlegend=False,
                dragmode=False,
            )
            figure.update_xaxes(title=None, fixedrange=True, showgrid=False, tickfont={"color": "#9fb0bf"})
            figure.update_yaxes(title=f"{to_code} per 1 {from_code}", fixedrange=True, gridcolor="#203347", zeroline=False, tickfont={"color": "#9fb0bf"})
            st.plotly_chart(
                figure,
                use_container_width=True,
                config={"displayModeBar": False, "scrollZoom": False, "staticPlot": True, "responsive": True},
            )
            change_text = "belum dapat dihitung" if change is None else f"{change:+.2f}%"
            st.markdown(
                f"<div class='trend-summary'>Data tersedia {len(points)} hari kurs pada rentang {trend['start']} sampai {trend['end']} · perubahan dari titik pertama ke terakhir: <b>{change_text}</b>.</div>",
                unsafe_allow_html=True,
            )
            st.caption("Grafik bersifat statis: tidak dapat di-zoom, digeser, disentuh, atau diunduh. Hari tanpa publikasi kurs tidak menghasilkan titik grafik.")
            st.markdown("Sumber tren: [Frankfurter](https://frankfurter.dev/) — kurs referensi historis dari bank sentral, bukan harga broker real-time.")
        else:
            st.warning(f"Grafik tren belum tersedia: {trend['error']}")
elif fx and not fx.get("ok"):
    st.warning("Kurs publik tidak dapat dimuat. Coba muat ulang; aplikasi tidak membuat kurs pengganti.")
else:
    st.markdown("<div class='empty-result'>Tekan <b>Muat Kurs & 90 Mata Uang</b> untuk memilih pasangan dan melihat perbandingan kurs satu unit.</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='footer-note'>AEROVULPIS KALKULATOR RISIKO · UNTUK EDUKASI DAN PERENCANAAN · BUKAN NASIHAT FINANSIAL PERSONAL ATAU SISTEM EKSEKUSI</div>", unsafe_allow_html=True)
