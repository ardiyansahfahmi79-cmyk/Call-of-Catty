import streamlit as st
import streamlit.components.v1 as components

# 1. Pengaturan Halaman Lebar Penuh
st.set_page_config(page_title="Aerovulpis Pro Terminal", layout="wide")

# 2. TRICK CSS: Memaksa layout kolom tetap berjejer ke samping di HP (Tampilan Laptop)
st.markdown("""
    <style>
        /* Memaksa container kolom Streamlit tidak pecah ke bawah pada layar kecil */
        [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            overflow-x: auto !important; /* Biar bisa di-geser kanan kiri kalau layar terlalu sempit */
        }
        /* Mengatur lebar minimal per kolom agar tidak terlalu gepeng di HP */
        [data-testid="column"]:nth-of-type(1) { min-width: 300px; } /* Kiri: Kalender */
        [data-testid="column"]:nth-of-type(2) { min-width: 500px; } /* Tengah: Chart & MT5 */
        [data-testid="column"]:nth-of-type(3) { min-width: 250px; } /* Kanan: AI */
    </style>
""", unsafe_allow_html=True)

st.title("Aerovulpis Pro Dashboard ⚡")

# 3. Membuat Layout 3 Kolom (Kiri, Tengah, Kanan)
col_kiri, col_tengah, col_kanan = st.columns([1.2, 2, 1])

# === KOLOM KIRI: KALENDER EKONOMI MQL5 (TRADAYS) ===
with col_kiri:
    st.subheader("📅 Economic Calendar")
    # Menggunakan URL widget murni Tradays agar tidak error
    calendar_html = """
    <iframe src="https://tradays.com" 
            width="100%" height="700" frameborder="0" style="border: 1px solid #ccc; border-radius: 8px;"></iframe>
    """
    components.html(calendar_html, height=720)

# === KOLOM TENGAH: TRADINGVIEW (ATAS) & MT5 (BAWAH) ===
with col_tengah:
    st.subheader("📊 Market Execution")
    
    # Tengah Atas: TradingView Chart
    # (Ganti URL ini dengan widget embed chart TradingView milikmu sendiri)
    tv_html = """
    <iframe src="https://tradingview.com" 
            width="100%" height="350" frameborder="0" style="border-radius: 8px;"></iframe>
    """
    components.html(tv_html, height=360)
    
    # Tengah Bawah: MT5 Web Terminal untuk Entry
    mt5_html = """
    <iframe src="https://mql5.com" 
            width="100%" height="320" frameborder="0" style="border-radius: 8px; border: 1px solid #444;"></iframe>
    """
    components.html(mt5_html, height=330)

# === KOLOM KANAN: AI SENTIMENT FEED ===
with col_kanan:
    st.subheader("🤖 AI Signal & News")
    st.caption("Live AI sentiment analysis assistant")
    
    # Tempat menaruh hasil output dari API AI-mu nanti
    st.metric(label="USD Sentiment", value="BULLISH 🔥", delta="Strong")
    
    with st.expander("AI News Summary", expanded=True):
        st.write("**US CPI Data Release:**")
        st.write("AI Analysis: Inflasi AS naik lebih tinggi dari prediksi. Ini memicu penguatan USD secara instan. Disarankan fokus mencari peluang *Sell* pada EURUSD atau *Buy* pada USDJPY untuk 15 menit ke depan.")