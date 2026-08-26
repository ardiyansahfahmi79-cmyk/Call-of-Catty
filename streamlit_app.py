"""AeroVulpis Risk Framework — prototipe Streamlit local-first.

Filosofi visual file ini: cyber-finance yang tenang, panel terminal asimetris,
aksen cyan/emerald terukur, angka utama sangat jelas, dan tidak ada koneksi broker.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from risk_management_core import RiskSnapshot, calculate_risk_snapshot


st.set_page_config(
    page_title="AeroVulpis — Risk Framework",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
    /* Risk Framework visual system: restrained cyber-finance, not broker execution UI. */
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Rajdhani:wght@400;500;600;700&display=swap');
    :root { --ink:#060a12; --panel:#0b1120; --panel2:#101827; --line:rgba(109,231,255,.16); --cyan:#42d7ff; --mint:#39f4a6; --red:#ff5d85; --violet:#bd65ff; --text:#eef6ff; --muted:#93a4b8; }
    .stApp { background:radial-gradient(circle at 9% 9%,rgba(20,110,153,.18),transparent 26%),radial-gradient(circle at 92% 14%,rgba(50,204,162,.11),transparent 22%),var(--ink); color:var(--text); }
    .block-container { max-width:1180px; padding-top:2.25rem; padding-bottom:4rem; }
    #MainMenu, footer, header { visibility:hidden; }
    .brand-kicker,.eyebrow,.metric-label,.terminal-tag,.risk-note { font-family:'DM Mono',monospace; letter-spacing:.13em; }
    .brand-kicker { color:var(--cyan); font-size:.7rem; text-transform:uppercase; }
    .hero-title { font-family:'Rajdhani',sans-serif; font-size:clamp(2.6rem,7vw,5.7rem); line-height:.9; letter-spacing:.045em; font-weight:700; margin:.55rem 0 .35rem; color:var(--text); }
    .hero-title span { color:var(--mint); text-shadow:0 0 24px rgba(57,244,166,.28); }
    .hero-copy { max-width:680px; color:var(--muted); font-size:1rem; line-height:1.55; margin:0 0 1.1rem; }
    .status-shell { border:1px solid var(--line); background:linear-gradient(135deg,rgba(10,27,43,.85),rgba(9,14,25,.72)); padding:18px; border-radius:18px; min-height:154px; position:relative; overflow:hidden; }
    .status-shell:after { content:''; position:absolute; inset:auto -18px -28px auto; width:95px; height:95px; border:1px solid rgba(66,215,255,.18); border-radius:50%; box-shadow:0 0 0 18px rgba(66,215,255,.035),0 0 0 38px rgba(66,215,255,.025); }
    .status-value { font-family:'Rajdhani',sans-serif; font-weight:700; font-size:1.9rem; color:var(--mint); margin:.45rem 0; position:relative; z-index:1; }
    .status-sub { color:var(--muted); font-size:.82rem; max-width:230px; position:relative; z-index:1; }
    .warning-strip { border-left:3px solid var(--cyan); background:rgba(19,78,111,.17); border-radius:0 10px 10px 0; color:#c7deec; padding:.7rem .85rem; font-size:.86rem; margin:.4rem 0 1.2rem; }
    .section-head { display:flex; align-items:end; justify-content:space-between; gap:1rem; border-bottom:1px solid rgba(143,170,196,.14); padding:1.4rem 0 .8rem; margin:1rem 0 .75rem; }
    .section-title { font-family:'Rajdhani',sans-serif; letter-spacing:.04em; font-size:1.55rem; font-weight:600; margin:0; color:var(--text); }
    .section-index { color:var(--cyan); font-family:'DM Mono',monospace; font-size:.7rem; }
    .panel { background:linear-gradient(145deg,rgba(16,24,39,.95),rgba(8,13,23,.92)); border:1px solid rgba(144,177,204,.14); border-radius:16px; padding:1rem 1rem .35rem; min-height:100%; }
    .metric-card { background:linear-gradient(145deg,rgba(16,32,49,.9),rgba(10,15,27,.96)); border:1px solid rgba(72,215,255,.14); border-radius:15px; padding:1rem; min-height:126px; }
    .metric-label { font-size:.66rem; color:var(--muted); text-transform:uppercase; }
    .metric-value { font-family:'Rajdhani',sans-serif; font-size:2.1rem; font-weight:700; margin:.25rem 0 0; }
    .metric-caption { color:var(--muted); font-size:.76rem; }
    .green { color:var(--mint); } .cyan { color:var(--cyan); } .red { color:var(--red); } .violet { color:var(--violet); }
    div[data-testid='stNumberInput'] label, div[data-testid='stSlider'] label { font-family:'DM Mono',monospace!important; letter-spacing:.08em; font-size:.7rem!important; color:#a9bdcf!important; text-transform:uppercase; }
    div[data-testid='stNumberInput'] input { background:#090e19!important; border:1px solid rgba(111,194,227,.16)!important; color:var(--text)!important; border-radius:9px!important; font-family:'DM Mono',monospace!important; }
    div[data-testid='stNumberInput'] button { color:var(--cyan)!important; background:rgba(39,91,122,.16)!important; border-color:rgba(111,194,227,.16)!important; }
    .stButton>button { width:100%; min-height:48px; background:linear-gradient(90deg,rgba(19,100,144,.95),rgba(15,157,168,.92))!important; color:#efffff!important; border:1px solid rgba(87,230,255,.65)!important; border-radius:10px!important; font-family:'DM Mono',monospace!important; letter-spacing:.12em!important; font-size:.75rem!important; box-shadow:0 0 24px rgba(12,157,206,.14); }
    .stButton>button:active { transform:scale(.98); }
    .stProgress > div > div { background:linear-gradient(90deg,var(--cyan),var(--mint))!important; }
    .stDataFrame { border:1px solid rgba(109,231,255,.14); border-radius:12px; overflow:hidden; }
    .footer-note { margin-top:2rem; color:#71849a; font-size:.78rem; line-height:1.55; text-align:center; }
    @media (max-width:700px) { .block-container { padding:1.25rem 1rem 3rem; } .hero-title { font-size:3rem; } .hero-copy { font-size:.92rem; } .status-shell { margin-top:.6rem; } .metric-card { min-height:106px; padding:.8rem; } .metric-value { font-size:1.7rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def money(value: float) -> str:
    return f"${value:,.2f}"


def status_color(status: str) -> str:
    if status == "RISIKO TERKONTROL":
        return "green"
    if status == "TARGET HARIAN TERCAPAI":
        return "cyan"
    return "red"


def metric_card(label: str, value: str, caption: str, color: str) -> str:
    return f"""
    <div class='metric-card'>
      <div class='metric-label'>{label}</div>
      <div class='metric-value {color}'>{value}</div>
      <div class='metric-caption'>{caption}</div>
    </div>
    """


def scenario_table(snapshot: RiskSnapshot, wins: int, losses: int) -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("Saldo awal", money(snapshot.balance)),
            ("Risiko satu setup", money(snapshot.risk_amount)),
            ("Proyeksi kemenangan", money(wins * snapshot.risk_amount * snapshot.reward_risk)),
            ("Proyeksi kerugian", f"-{money(losses * snapshot.risk_amount)}"),
            ("Proyeksi bersih", money(snapshot.scenario_net)),
        ],
        columns=["Komponen simulasi", "Nilai"],
    )


st.markdown("<div class='brand-kicker'>AEROVULPIS / CONTROLLED EXPOSURE SYSTEM</div>", unsafe_allow_html=True)
top_left, top_right = st.columns([1.55, 0.75], gap="large")
with top_left:
    st.markdown("<div class='hero-title'>RISK <span>FRAMEWORK</span></div>", unsafe_allow_html=True)
    st.markdown("<p class='hero-copy'>Kalibrasikan batas risiko sebelum menyusun rencana trading. Prototipe ini menghitung simulasi lokal dari angka yang Anda masukkan—tanpa broker, database, harga live, atau perintah transaksi.</p>", unsafe_allow_html=True)
with top_right:
    st.markdown("<div class='status-shell'><div class='terminal-tag brand-kicker'>MODE AKTIF</div><div class='status-value'>SIMULASI LOKAL</div><div class='status-sub'>Tidak ada data yang dikirim atau disimpan ke akun broker.</div></div>", unsafe_allow_html=True)

st.markdown("<div class='warning-strip'>Gunakan hasil sebagai alat perencanaan edukatif. Nilai lot adalah estimasi berdasarkan <i>nilai per pergerakan harga per 1 lot</i> yang Anda masukkan; verifikasi spesifikasi kontrak langsung di broker sebelum mengambil keputusan.</div>", unsafe_allow_html=True)

st.markdown("<div class='section-head'><h2 class='section-title'>01 / KONFIGURASI AKUN</h2><span class='section-index'>LOCAL INPUTS</span></div>", unsafe_allow_html=True)
acc_1, acc_2, acc_3 = st.columns([1.1, 1, 1], gap="medium")
with acc_1:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    balance = st.number_input("Saldo akun (USD)", min_value=10.0, max_value=10_000_000.0, value=1000.0, step=50.0, format="%.2f")
    risk_percent = st.slider("Risiko per setup (%)", min_value=0.25, max_value=10.0, value=1.0, step=0.25)
    st.markdown("</div>", unsafe_allow_html=True)
with acc_2:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    daily_loss_percent = st.slider("Batas rugi harian (%)", min_value=0.5, max_value=20.0, value=5.0, step=0.5)
    daily_profit_percent = st.slider("Target profit harian (%)", min_value=0.5, max_value=30.0, value=10.0, step=0.5)
    st.markdown("</div>", unsafe_allow_html=True)
with acc_3:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    instrument = st.selectbox("Kelas instrumen", ["XAUUSD / Komoditas", "Forex mayor", "Indeks / CFD", "Kustom"], index=0)
    preset_value = 100.0 if instrument == "XAUUSD / Komoditas" else 10.0 if instrument == "Forex mayor" else 1.0
    price_move_value_per_lot = st.number_input("Nilai gerak harga / 1 lot (USD)", min_value=0.0001, value=preset_value, step=1.0, format="%.4f", help="Masukkan sesuai spesifikasi kontrak broker. Nilai preset hanyalah titik awal simulasi.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section-head'><h2 class='section-title'>02 / MATRIKS RISIKO–REWARD</h2><span class='section-index'>SETUP SIMULATION</span></div>", unsafe_allow_html=True)
setup_1, setup_2 = st.columns([1.1, 1], gap="medium")
with setup_1:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    direction = st.radio("Arah rencana", ["BUY", "SELL"], horizontal=True)
    p1, p2, p3 = st.columns(3)
    with p1:
        entry = st.number_input("Harga entry", min_value=0.0001, value=2350.0, step=0.1, format="%.4f")
    with p2:
        stop_loss = st.number_input("Stop loss", min_value=0.0001, value=2345.0, step=0.1, format="%.4f")
    with p3:
        take_profit = st.number_input("Take profit", min_value=0.0001, value=2360.0, step=0.1, format="%.4f")
    st.markdown("</div>", unsafe_allow_html=True)
with setup_2:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    w1, w2 = st.columns(2)
    with w1:
        wins = st.number_input("Skenario win", min_value=0, max_value=50, value=3, step=1)
    with w2:
        losses = st.number_input("Skenario loss", min_value=0, max_value=50, value=2, step=1)
    run_simulation = st.button("JALANKAN SIMULASI RISIKO", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

snapshot = calculate_risk_snapshot(
    balance=balance,
    risk_percent=risk_percent,
    daily_loss_percent=daily_loss_percent,
    daily_profit_percent=daily_profit_percent,
    entry=entry,
    stop_loss=stop_loss,
    take_profit=take_profit,
    price_move_value_per_lot=price_move_value_per_lot,
    wins=wins,
    losses=losses,
)

if run_simulation:
    st.session_state["risk_simulation_ran"] = True

st.markdown("<div class='section-head'><h2 class='section-title'>03 / PROYEKSI TERUKUR</h2><span class='section-index'>NO EXECUTION</span></div>", unsafe_allow_html=True)
metrics = st.columns(4, gap="medium")
with metrics[0]:
    st.markdown(metric_card("Risiko per setup", money(snapshot.risk_amount), f"{risk_percent:.2f}% dari saldo", "red"), unsafe_allow_html=True)
with metrics[1]:
    st.markdown(metric_card("Risk : Reward", f"1 : {snapshot.reward_risk:.2f}", f"BE rate {snapshot.break_even_rate * 100:.1f}%", "cyan"), unsafe_allow_html=True)
with metrics[2]:
    st.markdown(metric_card("Estimasi lot", f"{snapshot.estimated_lots:.3f}", "Verifikasi kontrak broker", "violet"), unsafe_allow_html=True)
with metrics[3]:
    st.markdown(metric_card("Status skenario", snapshot.scenario_status, "Berdasarkan input saat ini", status_color(snapshot.scenario_status)), unsafe_allow_html=True)

detail_left, detail_right = st.columns([1.16, 0.84], gap="medium")
with detail_left:
    st.markdown("<div class='panel'><div class='metric-label'>RINCIAN SIMULASI</div>", unsafe_allow_html=True)
    st.dataframe(scenario_table(snapshot, wins, losses), hide_index=True, use_container_width=True, height=214)
    st.markdown("</div>", unsafe_allow_html=True)
with detail_right:
    st.markdown("<div class='panel'><div class='metric-label'>PENJAGA BATAS HARIAN</div>", unsafe_allow_html=True)
    loss_load = min(snapshot.risk_amount * losses / snapshot.daily_loss_amount, 1.0) if snapshot.daily_loss_amount else 0.0
    profit_load = min(max(snapshot.scenario_net, 0.0) / snapshot.daily_profit_amount, 1.0) if snapshot.daily_profit_amount else 0.0
    st.caption(f"Batas rugi: {money(snapshot.daily_loss_amount)}")
    st.progress(loss_load, text=f"Eksposur loss simulasi: {loss_load * 100:.0f}%")
    st.caption(f"Target harian: {money(snapshot.daily_profit_amount)}")
    st.progress(profit_load, text=f"Progres target simulasi: {profit_load * 100:.0f}%")
    if snapshot.stop_distance <= 0:
        st.error("Stop loss harus berbeda dari harga entry agar risiko dapat dihitung.")
    elif snapshot.reward_risk < 1:
        st.warning("Risk-reward di bawah 1:1. Tinjau kembali jarak target dan stop loss.")
    elif snapshot.scenario_status == "BATAS RUGI TERCAPAI":
        st.error("Skenario melewati batas rugi harian yang Anda tentukan.")
    elif snapshot.scenario_status == "TARGET HARIAN TERCAPAI":
        st.success("Skenario menyentuh target harian; pertimbangkan kunci entry baru sesuai rencana disiplin Anda.")
    else:
        st.success("Simulasi berada di dalam batas yang Anda masukkan.")
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.get("risk_simulation_ran"):
    st.success("Simulasi diperbarui dari parameter lokal Anda. Tidak ada data atau order yang dikirim ke broker.")

st.markdown("<div class='footer-note'>AEROVULPIS RISK FRAMEWORK · LOCAL-ONLY PROTOTYPE · EDUKASI DAN PERENCANAAN, BUKAN NASIHAT FINANSIAL PERSONAL ATAU SISTEM EKSEKUSI.</div>", unsafe_allow_html=True)
