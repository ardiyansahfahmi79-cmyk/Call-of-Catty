from datetime import datetime, timezone, timedelta
from html import escape

import streamlit as st

st.set_page_config(
    page_title="Market Intelligence | Aerovulpis",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg:        #04090f;
  --surf:      #0a1420;
  --surf2:     #071018;
  --bdr:       #162235;
  --bdr2:      #1e3050;
  --text:      #c5d8ec;
  --muted:     #4e6a88;
  --dim:       #273e58;
  --accent:    #00c8f0;
  --purple:    #7040e0;
  --bullish:   #00e090;
  --bearish:   #ff2855;
  --neutral:   #2e7fff;
  --warn:      #f0b800;
  --star-lo:   #00ff90;   /* 1★ hijau neon */
  --star-mid:  #ffe000;   /* 2★ kuning neon */
  --star-hi:   #ff2040;   /* 3★ merah neon */
  --neon:      #00ffd0;
}

*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html,body,.stApp{background:var(--bg)!important;color:var(--text);font-family:'Inter',sans-serif}
#MainMenu,footer,header{visibility:hidden!important}
.stDeployButton,[data-testid="stToolbar"]{display:none!important}
section[data-testid="stSidebar"]{display:none!important}
.block-container{padding:0 .7rem 3rem!important;max-width:100%!important}

/* ── HEADER ── */
.hdr{text-align:center;padding:1.6rem 1rem 1rem}
.hdr h1{
  font-size:clamp(1.6rem,5vw,2.7rem);font-weight:800;letter-spacing:4px;line-height:1.1;margin-bottom:.35rem;
  background:linear-gradient(120deg,#fff 15%,#00c8f0 52%,#7040e0 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.hdr .sub  {font-size:.8rem;color:var(--muted);letter-spacing:1.5px;margin-bottom:.15rem}
.hdr .credit{font-family:'JetBrains Mono',monospace;font-size:.58rem;color:var(--dim)}
.hdr-line{height:1px;background:linear-gradient(90deg,transparent,var(--accent) 38%,var(--purple) 62%,transparent);opacity:.3;max-width:400px;margin:.85rem auto 0}

/* ── KATEGORI ── */
div[data-testid="stHorizontalBlock"]{
  display:flex!important;flex-wrap:nowrap!important;overflow-x:auto!important;
  gap:.3rem!important;padding-bottom:4px!important;scrollbar-width:none!important;
  -webkit-overflow-scrolling:touch!important;justify-content:flex-start!important
}
div[data-testid="stHorizontalBlock"]::-webkit-scrollbar{display:none!important}
div[data-testid="column"]{padding:0!important;flex:0 0 auto!important;min-width:0!important;width:auto!important}

/* Semua tombol */
div[data-testid="stButton"]>button{
  font-family:'JetBrains Mono',monospace!important;
  font-size:.62rem!important;font-weight:600!important;
  letter-spacing:1.5px!important;text-transform:uppercase!important;
  background:var(--surf)!important;color:var(--muted)!important;
  border:1px solid var(--bdr)!important;border-radius:3px!important;
  padding:.36rem .75rem!important;white-space:nowrap!important;
  height:auto!important;transition:all .18s!important
}
div[data-testid="stButton"]>button:hover{
  background:rgba(0,200,240,.08)!important;color:var(--accent)!important;
  border-color:rgba(0,200,240,.4)!important
}
div[data-testid="stButton"]>button:focus,
div[data-testid="stButton"]>button:active{
  background:rgba(0,200,240,.13)!important;color:var(--accent)!important;
  border-color:var(--accent)!important
}

/* ── SECTION LABEL ── */
.sec-lbl{
  display:flex;align-items:center;gap:.6rem;
  font-family:'JetBrains Mono',monospace;font-size:.58rem;color:var(--dim);
  letter-spacing:2.5px;text-transform:uppercase;margin:.45rem 0 .75rem
}
.sec-lbl::before{content:'';flex:1;height:1px;background:var(--bdr)}
.sec-lbl .n{color:var(--accent);font-weight:700}

/* ── NEWS CARD ── */
.card{
  background:var(--surf);border:1px solid var(--bdr);
  border-left:3px solid var(--neutral);border-radius:6px;
  margin-bottom:.65rem;overflow:hidden;
  transition:transform .2s,border-color .2s,box-shadow .2s
}
.card.bullish{border-left-color:var(--bullish)}
.card.bearish{border-left-color:var(--bearish)}
.card.neutral{border-left-color:var(--neutral)}
.card:hover{transform:translateY(-2px);border-color:rgba(0,200,240,.3);box-shadow:0 4px 18px rgba(0,200,240,.05)}

.cbody{padding:.85rem .95rem .75rem 1.1rem}
.ctop{display:flex;align-items:center;justify-content:space-between;margin-bottom:.45rem;gap:.3rem;flex-wrap:wrap}

.kat-badge{font-family:'JetBrains Mono',monospace;font-size:.52rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--accent);background:rgba(0,200,240,.07);border:1px solid rgba(0,200,240,.2);border-radius:2px;padding:.07rem .38rem;flex-shrink:0}
.src-chip{font-family:'JetBrains Mono',monospace;font-size:.48rem;color:var(--dim);background:rgba(255,255,255,.03);border:1px solid var(--bdr);border-radius:2px;padding:.05rem .3rem;flex-shrink:0}
.sent-b{font-family:'JetBrains Mono',monospace;font-size:.5rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;padding:.07rem .36rem;border-radius:2px;flex-shrink:0}
.sent-b.bullish{color:var(--bullish);background:rgba(0,224,144,.09);border:1px solid rgba(0,224,144,.25)}
.sent-b.bearish{color:var(--bearish);background:rgba(255,40,85,.09);border:1px solid rgba(255,40,85,.25)}
.sent-b.neutral{color:var(--neutral);background:rgba(46,127,255,.09);border:1px solid rgba(46,127,255,.25)}

/* ── DAMPAK BINTANG ── */
.dampak-row{display:flex;align-items:center;gap:.45rem;margin-bottom:.45rem}
.dampak-stars{font-size:.85rem;letter-spacing:.1rem;line-height:1}
.dampak-label{font-family:'JetBrains Mono',monospace;font-size:.5rem;font-weight:600;letter-spacing:1.5px;text-transform:uppercase}
.d1 .dampak-stars{color:var(--star-lo);text-shadow:0 0 8px var(--star-lo)}
.d1 .dampak-label{color:var(--star-lo)}
.d2 .dampak-stars{color:var(--star-mid);text-shadow:0 0 10px var(--star-mid)}
.d2 .dampak-label{color:var(--star-mid)}
.d3 .dampak-stars{color:var(--star-hi);text-shadow:0 0 12px var(--star-hi)}
.d3 .dampak-label{color:var(--star-hi)}

/* ── INSTRUMEN TAGS ── */
.instr-row{display:flex;flex-wrap:wrap;gap:.25rem;margin-bottom:.45rem}
.instr-tag{font-family:'JetBrains Mono',monospace;font-size:.49rem;font-weight:600;color:var(--purple);background:rgba(112,64,224,.1);border:1px solid rgba(112,64,224,.25);border-radius:2px;padding:.04rem .3rem}

.news-title{font-size:.88rem;font-weight:700;color:var(--text);line-height:1.45;margin-bottom:.42rem}
.news-desc {font-size:.78rem;color:var(--muted);line-height:1.65;margin-bottom:.58rem}
.cmeta{display:flex;align-items:center;gap:.32rem;font-family:'JetBrains Mono',monospace;font-size:.55rem;color:var(--dim);flex-wrap:wrap}
.msrc{color:var(--muted);font-weight:600}
.mdot{width:3px;height:3px;border-radius:50%;background:var(--dim);flex-shrink:0}

/* ── DETAIL PANEL ── */
.det-panel{border-top:1px solid rgba(0,200,240,.1);background:rgba(0,6,16,.55);padding:.7rem .95rem .7rem 1.1rem}
.det-lbl{font-family:'JetBrains Mono',monospace;font-size:.5rem;letter-spacing:2.5px;text-transform:uppercase;color:var(--dim);margin-bottom:.35rem}
.det-text{font-size:.79rem;color:var(--muted);line-height:1.7}
.det-foot{margin-top:.35rem;font-family:'JetBrains Mono',monospace;font-size:.5rem;color:var(--dim)}

/* ── ADMIN PANEL ── */
.adm-box{background:var(--surf);border:1px solid var(--bdr2);border-radius:8px;overflow:hidden;margin-bottom:1rem}
.adm-head{
  background:linear-gradient(135deg,rgba(240,184,0,.07),rgba(112,64,224,.05));
  border-bottom:1px solid var(--bdr2);padding:.6rem .85rem;
  display:flex;align-items:center;gap:.4rem
}
.adm-dot{width:6px;height:6px;border-radius:50%;background:var(--warn);box-shadow:0 0 9px var(--warn);flex-shrink:0}
.adm-title{font-family:'JetBrains Mono',monospace;font-size:.6rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:var(--warn)}
.adm-body{padding:.7rem .85rem .85rem}
.flbl{font-family:'JetBrains Mono',monospace;font-size:.52rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--dim);margin-bottom:.22rem;margin-top:.5rem}
.flbl:first-child{margin-top:0}
.fsep{height:1px;background:var(--bdr);margin:.55rem 0}

/* Dampak selector visual */
.dampak-sel{display:flex;gap:.5rem;margin-bottom:.3rem}
.d-opt{
  flex:1;text-align:center;padding:.4rem .3rem;border-radius:4px;cursor:pointer;
  font-family:'JetBrains Mono',monospace;font-size:.55rem;font-weight:700;
  letter-spacing:1px;text-transform:uppercase;border:1px solid;transition:all .18s
}
.d-opt.lo{color:var(--star-lo);border-color:rgba(0,255,144,.25);background:rgba(0,255,144,.06)}
.d-opt.lo:hover,.d-opt.lo.sel{background:rgba(0,255,144,.15);box-shadow:0 0 12px rgba(0,255,144,.2)}
.d-opt.mid{color:var(--star-mid);border-color:rgba(255,224,0,.25);background:rgba(255,224,0,.06)}
.d-opt.mid:hover,.d-opt.mid.sel{background:rgba(255,224,0,.15);box-shadow:0 0 12px rgba(255,224,0,.2)}
.d-opt.hi{color:var(--star-hi);border-color:rgba(255,32,64,.25);background:rgba(255,32,64,.06)}
.d-opt.hi:hover,.d-opt.hi.sel{background:rgba(255,32,64,.15);box-shadow:0 0 12px rgba(255,32,64,.2)}

/* Saved list */
.saved-item{font-size:.72rem;color:var(--muted);padding:.25rem 0;border-bottom:1px solid var(--bdr);font-family:'Inter',sans-serif}

/* EMPTY */
.empty{text-align:center;padding:2.5rem 1.5rem;border:1px solid var(--bdr);border-radius:6px;margin:.8rem 0}
.empty h3{font-family:'JetBrains Mono',monospace;font-size:.65rem;letter-spacing:2.5px;text-transform:uppercase;color:var(--muted);margin-bottom:.4rem}
.empty p{font-size:.77rem;color:var(--dim);line-height:1.65}

/* PUBLISH BTN khusus */
.pub-btn div[data-testid="stButton"]>button{
  width:100%!important;
  background:linear-gradient(135deg,rgba(0,200,240,.15),rgba(112,64,224,.12))!important;
  color:var(--accent)!important;border-color:rgba(0,200,240,.48)!important;
  box-shadow:0 0 16px rgba(0,200,240,.1)!important;
  font-size:.65rem!important;padding:.45rem 1rem!important
}
.pub-btn div[data-testid="stButton"]>button:hover{box-shadow:0 0 26px rgba(0,200,240,.22)!important}

/* FOOTER */
.ftr{margin-top:2rem;padding:1rem;border-top:1px solid var(--bdr);text-align:center;font-family:'JetBrains Mono',monospace;font-size:.56rem;color:var(--dim);line-height:1.9}
.ftr .brand{color:var(--accent);font-weight:700;letter-spacing:2px}

@media(max-width:900px){
  .news-title{font-size:.84rem}
  .block-container{padding-left:.35rem!important;padding-right:.35rem!important}
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════
st.markdown("""
<div class="hdr">
  <h1>MARKET INTELLIGENCE</h1>
  <div class="sub">Analisis Mendalam untuk Trader Modern</div>
  <div class="credit">Dirancang oleh Tim Aerovulpis</div>
  <div class="hdr-line"></div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# KONSTAN
# ═══════════════════════════════════════════════
KATEGORI = {
    "all":        "Semua",
    "stock":      "Saham",
    "crypto":     "Aset Digital",
    "geopolitics":"Geopolitik",
    "forex":      "Valuta Asing",
    "indonesia":  "Indonesia",
    "economy_us": "Ekonomi AS",
    "fed":        "Federal Reserve",
}

KATEGORI_LABEL = {
    "stock":"SAHAM","crypto":"ASET DIGITAL","geopolitics":"GEOPOLITIK",
    "forex":"VALUTA ASING","indonesia":"INDONESIA","economy_us":"EKONOMI AS","fed":"FEDERAL RESERVE",
}

INSTRUMEN_OPTIONS = [
    "XAUUSD","XAGUSD","EURUSD","GBPUSD","USDJPY","AUDUSD","USDCAD","USDCHF","NZDUSD",
    "DXY (Dolar Index)","US10Y Treasury","US30Y Treasury",
    "BTC/USD","ETH/USD","BNB/USD","SOL/USD","XRP/USD",
    "S&P 500","NASDAQ","Dow Jones","IHSG","Nikkei 225","Hang Seng",
    "Minyak WTI","Minyak Brent","Gas Alam",
]

DAMPAK_CFG = {
    1: {"cls":"d1","stars":"★","empty":"☆☆","label":"DAMPAK RENDAH"},
    2: {"cls":"d2","stars":"★★","empty":"☆","label":"DAMPAK SEDANG"},
    3: {"cls":"d3","stars":"★★★","empty":"","label":"DAMPAK TINGGI"},
}

# ═══════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════
for k, v in [
    ("kat","all"),
    ("show_detail",{}),
    ("berita",[]),          # list berita manual
    ("dampak_sel",2),       # default pilihan dampak di form
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════
def c(v: str) -> str:
    """Escape teks untuk HTML."""
    return escape(str(v)) if v else ""

def fmt_dt(s: str) -> str:
    try:
        dt = datetime.fromisoformat(s.replace("Z","+00:00"))
        return dt.strftime("%d %b %Y %H:%M")
    except:
        return s or ""

def dampak_html(level: int) -> str:
    cfg = DAMPAK_CFG.get(level, DAMPAK_CFG[1])
    return f'''<div class="dampak-row {cfg["cls"]}">
      <span class="dampak-stars">{cfg["stars"]}{cfg["empty"]}</span>
      <span class="dampak-label">{cfg["label"]}</span>
    </div>'''

# ═══════════════════════════════════════════════
# KATEGORI BUTTONS
# ═══════════════════════════════════════════════
kat_aktif = st.session_state.kat
kat_list  = list(KATEGORI.items())
cat_cols  = st.columns(len(kat_list))
for i, (k, v) in enumerate(kat_list):
    with cat_cols[i]:
        if k == kat_aktif:
            st.markdown(
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:.6rem;'
                f'font-weight:700;letter-spacing:1.5px;text-transform:uppercase;'
                f'color:#00c8f0;background:rgba(0,200,240,.12);border:1px solid #00c8f0;'
                f'border-radius:3px;padding:.34rem .4rem;text-align:center;'
                f'box-shadow:0 0 12px rgba(0,200,240,.14);margin-bottom:.2rem">{escape(v)}</div>',
                unsafe_allow_html=True
            )
        if st.button(v, key=f"cat_{k}", use_container_width=True):
            st.session_state.kat = k
            st.session_state.show_detail = {}
            st.rerun()

# ═══════════════════════════════════════════════
# FILTER BERITA
# ═══════════════════════════════════════════════
kat_aktif = st.session_state.kat
if kat_aktif == "all":
    items = st.session_state.berita
else:
    items = [b for b in st.session_state.berita if b.get("kategori_key") == kat_aktif]

cat_lbl = KATEGORI.get(kat_aktif, "Semua")

# ═══════════════════════════════════════════════
# LAYOUT: FEED (kiri) + ADMIN (kanan)
# ═══════════════════════════════════════════════
col_feed, col_admin = st.columns([3, 1], gap="medium")

# ══════════════
# KOLOM FEED
# ══════════════
with col_feed:
    if not items:
        st.markdown(f"""
        <div class="empty">
          <h3>Belum Ada Berita</h3>
          <p>Tambahkan berita pertama untuk kategori<br>
             <strong>{c(cat_lbl)}</strong> melalui panel T.I.M NEWS.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="sec-lbl">
          <span>FEED BERITA</span>
          <span class="n">{len(items)} artikel</span>
        </div>""", unsafe_allow_html=True)

        for i, item in enumerate(items):
            kid      = f"{kat_aktif}_{item.get('id','')}"
            warna    = item.get("sentimen","neutral")
            tag      = item.get("kategori_label","T.I.M NEWS")
            sent_lbl = {"bullish":"+ BULLISH","bearish":"- BEARISH","neutral":"~ NETRAL"}.get(warna,"~ NETRAL")
            wkt      = item.get("waktu_terbit","")
            instrumen= item.get("instrumen",[])
            dampak   = item.get("dampak", 1)

            # Instrumen tags
            instr_html = ""
            if instrumen:
                instr_html = '<div class="instr-row">' + "".join(
                    f'<span class="instr-tag">{escape(ins)}</span>' for ins in instrumen
                ) + '</div>'

            st.markdown(f"""
            <div class="card {warna}">
              <div class="cbody">
                <div class="ctop">
                  <span class="kat-badge">{c(tag)}</span>
                  <span class="src-chip">T.I.M NEWS</span>
                  <span class="sent-b {warna}">{c(sent_lbl)}</span>
                </div>
                {dampak_html(dampak)}
                {instr_html}
                <div class="news-title">{c(item.get('judul',''))}</div>
                <div class="news-desc">{c(item.get('deskripsi',''))}</div>
                <div class="cmeta">
                  <span class="msrc">T.I.M NEWS</span>
                  <span class="mdot"></span>
                  <span>{c(wkt)}</span>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            # Tombol Detail
            lbl_d = "TUTUP DETAIL" if st.session_state.show_detail.get(kid) else "LIHAT DETAIL"
            if st.button(lbl_d, key=f"d_{kid}", use_container_width=True):
                st.session_state.show_detail[kid] = not st.session_state.show_detail.get(kid, False)
                st.rerun()

            if st.session_state.show_detail.get(kid, False):
                instr_str = ", ".join(instrumen) if instrumen else "-"
                d_cfg = DAMPAK_CFG.get(dampak, DAMPAK_CFG[1])
                st.markdown(f"""
                <div class="det-panel">
                  <div class="det-lbl">Detail Berita</div>
                  <div class="det-text">{c(item.get('deskripsi',''))}</div>
                  <div class="det-foot">
                    Instrumen: {escape(instr_str)} &nbsp;|&nbsp;
                    Dampak: {d_cfg['stars']} {d_cfg['label']} &nbsp;|&nbsp;
                    {c(wkt)}
                  </div>
                </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="ftr">
      <span class="brand">AEROVULPIS</span> | 2026 Market Intelligence Terminal<br>
      Dikembangkan oleh DynamiHatch | Teknologi Intelijensi Pasar Masa Depan
    </div>""", unsafe_allow_html=True)

# ══════════════
# KOLOM ADMIN
# ══════════════
with col_admin:
    st.markdown("""
    <div class="adm-box">
      <div class="adm-head">
        <div class="adm-dot"></div>
        <div class="adm-title">T.I.M NEWS</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="flbl">Judul Berita</div>', unsafe_allow_html=True)
    judul_in = st.text_input("j", label_visibility="collapsed",
        placeholder="Masukkan judul berita...", key="f_judul")

    st.markdown('<div class="flbl">Deskripsi / Isi</div>', unsafe_allow_html=True)
    desk_in = st.text_area("d", label_visibility="collapsed",
        placeholder="Tulis isi berita lengkap di sini...", height=100, key="f_desk")

    st.markdown('<div class="fsep"></div>', unsafe_allow_html=True)

    # Tanggal
    st.markdown('<div class="flbl">Tanggal</div>', unsafe_allow_html=True)
    tgl_in = st.date_input("tgl", label_visibility="collapsed",
        value=datetime.now(timezone.utc).date(), key="f_tgl")

    # Jam & Menit — selectbox hindari React error
    st.markdown('<div class="flbl">Waktu (WIB)</div>', unsafe_allow_html=True)
    now_wib = datetime.now(timezone(timedelta(hours=7)))
    ch, cm = st.columns(2)
    with ch:
        jam_in = st.selectbox("H", label_visibility="collapsed",
            options=[f"{h:02d}" for h in range(24)], index=now_wib.hour, key="f_jam")
    with cm:
        mnt_in = st.selectbox("M", label_visibility="collapsed",
            options=[f"{m:02d}" for m in range(0,60,5)],
            index=now_wib.minute // 5, key="f_mnt")

    st.markdown('<div class="fsep"></div>', unsafe_allow_html=True)

    # Kategori
    st.markdown('<div class="flbl">Kategori</div>', unsafe_allow_html=True)
    kat_in = st.selectbox("k", label_visibility="collapsed",
        options=list(KATEGORI_LABEL.keys()),
        format_func=lambda x: KATEGORI_LABEL[x].title(), key="f_kat")

    # Sentimen
    st.markdown('<div class="flbl">Sentimen</div>', unsafe_allow_html=True)
    sent_in = st.selectbox("s", label_visibility="collapsed",
        options=["bullish","bearish","neutral"],
        format_func=lambda x: {"bullish":"+ Bullish","bearish":"- Bearish","neutral":"~ Netral"}[x],
        key="f_sent")

    # DAMPAK BINTANG — 3 tombol visual
    st.markdown('<div class="flbl">Tingkat Dampak</div>', unsafe_allow_html=True)
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        if st.button("★ RENDAH", key="d1_btn", use_container_width=True):
            st.session_state.dampak_sel = 1
            st.rerun()
    with dc2:
        if st.button("★★ SEDANG", key="d2_btn", use_container_width=True):
            st.session_state.dampak_sel = 2
            st.rerun()
    with dc3:
        if st.button("★★★ TINGGI", key="d3_btn", use_container_width=True):
            st.session_state.dampak_sel = 3
            st.rerun()

    # Tampilkan pilihan dampak aktif
    d_aktif = st.session_state.dampak_sel
    d_cfg   = DAMPAK_CFG[d_aktif]
    warna_map = {1:"#00ff90",2:"#ffe000",3:"#ff2040"}
    glow_map  = {1:"rgba(0,255,144,.25)",2:"rgba(255,224,0,.25)",3:"rgba(255,32,64,.25)"}
    wc = warna_map[d_aktif]
    gc = glow_map[d_aktif]
    st.markdown(
        f'<div style="text-align:center;padding:.4rem;border:1px solid {wc}40;'
        f'border-radius:4px;background:{wc}10;margin:.3rem 0;'
        f'box-shadow:0 0 12px {gc};">'
        f'<span style="color:{wc};text-shadow:0 0 10px {wc};font-size:.95rem;letter-spacing:.1rem">'
        f'{d_cfg["stars"]}</span>'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:.5rem;'
        f'color:{wc};letter-spacing:1.5px;text-transform:uppercase;display:block;margin-top:.15rem">'
        f'{d_cfg["label"]}</span></div>',
        unsafe_allow_html=True
    )

    # Instrumen
    st.markdown('<div class="flbl">Instrumen Terdampak</div>', unsafe_allow_html=True)
    instr_in = st.multiselect("i", label_visibility="collapsed",
        options=INSTRUMEN_OPTIONS, placeholder="Pilih instrumen...", key="f_instr")

    st.markdown('<div class="fsep"></div>', unsafe_allow_html=True)

    # PUBLISH
    st.markdown('<div class="pub-btn">', unsafe_allow_html=True)
    if st.button("PUBLISH BERITA", key="pub", use_container_width=True):
        if judul_in.strip() and desk_in.strip():
            wkt_str = f"{tgl_in.strftime('%d %b %Y')} {jam_in}:{mnt_in} WIB"
            berita_baru = {
                "id":            str(len(st.session_state.berita)),
                "judul":         judul_in.strip(),
                "deskripsi":     desk_in.strip(),
                "sumber":        "T.I.M NEWS",
                "waktu_terbit":  wkt_str,
                "sentimen":      sent_in,
                "kategori_key":  kat_in,
                "kategori_label":KATEGORI_LABEL[kat_in],
                "instrumen":     instr_in,
                "dampak":        d_aktif,
            }
            st.session_state.berita.insert(0, berita_baru)
            for k in ["f_judul","f_desk","f_instr"]:
                if k in st.session_state: del st.session_state[k]
            st.success("Berita dipublish!")
            st.rerun()
        else:
            st.error("Judul dan deskripsi wajib diisi.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Daftar tersimpan
    if st.session_state.berita:
        st.markdown('<div class="fsep"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="flbl">Tersimpan ({len(st.session_state.berita)})</div>',
            unsafe_allow_html=True)
        for idx, b in enumerate(st.session_state.berita):
            preview = b["judul"][:33] + "..." if len(b["judul"]) > 33 else b["judul"]
            d_cfg_s = DAMPAK_CFG.get(b.get("dampak",1), DAMPAK_CFG[1])
            wc_s    = warna_map.get(b.get("dampak",1),"#00ff90")
            c1, c2  = st.columns([5,1])
            with c1:
                st.markdown(
                    f'<div class="saved-item">'
                    f'<span style="color:{wc_s};font-size:.62rem">{d_cfg_s["stars"]}</span> '
                    f'{escape(preview)}</div>',
                    unsafe_allow_html=True
                )
            with c2:
                if st.button("X", key=f"del_{idx}", use_container_width=True):
                    st.session_state.berita.pop(idx)
                    st.rerun()