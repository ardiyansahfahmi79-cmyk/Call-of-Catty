import streamlit as st
from config import KATEGORI
from news_fetcher import ambil_berita_kategori, ambil_semua_kategori
from ai_analyzer import analisis_ai
from utils import hapus_duplikat

st.set_page_config(page_title="Market Intelligence | Aerovulpis", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0a0f1a; color: #e6eef7; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .kartu {
        background: #151d2d;
        border: 1px solid #2a364a;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .judul { font-size: 1.2rem; font-weight: 700; color: #e6eef7; }
    .muted { color: #94a3b8; }
    .badge {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border: 1px solid #2a364a;
        border-radius: 999px;
        font-size: 0.75rem;
        margin-right: 0.35rem;
        color: #94a3b8;
        margin-bottom: 0.35rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# MARKET INTELLIGENCE")
st.markdown("Analisis Mendalam untuk Trader Modern — **Aerovulpis**")
st.caption("Semua antarmuka dan prompt AI menggunakan Bahasa Indonesia.")

with st.sidebar:
    st.header("Pengaturan")
    kategori_terpilih = st.radio(
        "Pilih kategori",
        list(KATEGORI.keys()),
        format_func=lambda x: KATEGORI[x],
        index=0,
    )
    st.caption("Batas berita: 5 item per kategori. Mode 'Semua' menggabungkan semua kategori.")
    refresh = st.button("Muat Ulang Berita")

marketaux_key = st.secrets["MARKETAUX_API_KEY"]
openrouter_key = st.secrets["OPENROUTER_API_KEY"]

@st.cache_data(ttl=1800)
def muat_data_kategori(kategori):
    if kategori == "all":
        return ambil_semua_kategori(marketaux_key)
    return {kategori: ambil_berita_kategori(kategori, marketaux_key)}

if refresh:
    st.cache_data.clear()

data_kategori = muat_data_kategori(kategori_terpilih)

if kategori_terpilih == "all":
    semua_item = []
    for k, items in data_kategori.items():
        for item in items:
            item["kategori_asli"] = k
            semua_item.append(item)

    semua_item = hapus_duplikat(semua_item)

    if not semua_item:
        st.info("Tidak ada berita tersedia.")
    else:
        kolom = st.columns(2)
        for i, item in enumerate(semua_item):
            with kolom[i % 2]:
                st.markdown('<div class="kartu">', unsafe_allow_html=True)
                st.markdown(f"<div class='judul'>{item['judul']}</div>", unsafe_allow_html=True)
                st.write(item["deskripsi"])
                st.markdown(f"<div class='muted'>{item['sumber']} • {item['waktu_terbit']}</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button("Analisis AI", key=f"ai_all_{i}"):
                        with st.spinner("AI sedang menganalisis berita..."):
                            hasil = analisis_ai(openrouter_key, item, KATEGORI.get(item.get("kategori_asli", ""), ""))
                        st.success(hasil)
                with c2:
                    if item["url"]:
                        st.link_button("Buka sumber", item["url"])
else:
    items = data_kategori.get(kategori_terpilih, [])

    if not items:
        st.info("Tidak ada berita yang tersedia untuk kategori ini.")
    else:
        kolom = st.columns(2)
        for i, item in enumerate(items):
            with kolom[i % 2]:
                st.markdown('<div class="kartu">', unsafe_allow_html=True)
                st.markdown(f"<div class='judul'>{item['judul']}</div>", unsafe_allow_html=True)
                st.write(item["deskripsi"])
                st.markdown(f"<div class='muted'>{item['sumber']} • {item['waktu_terbit']}</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button("Analisis AI", key=f"ai_{kategori_terpilih}_{i}"):
                        with st.spinner("AI sedang menganalisis berita..."):
                            hasil = analisis_ai(openrouter_key, item, KATEGORI[kategori_terpilih])
                        st.success(hasil)
                with c2:
                    if item["url"]:
                        st.link_button("Buka sumber", item["url"])