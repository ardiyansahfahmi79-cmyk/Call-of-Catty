from datetime import datetime, timezone, timedelta
from html import escape

import streamlit as st

st.set_page_config(
    page_title="Market Intelligence | Aerovulpis",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg:       #04090f;
  --surf:     #080f1c;
  --surf2:    #060d18;
  --bdr:      #112030;
  --bdr2:     #1a3050;
  --text:     #bdd0e8;
  --muted:    #46647e;
  --dim:      #253850;
  --accent:   #00c8f0;
  --purple:   #6830d8;
  --bullish:  #00d888;
  --bearish:  #ff2050;
  --neutral:  #2070ff;
  --warn:     #e8b000;
  --star1:    #00ff88;
  --star2:    #ffe000;
  --star3:    #ff1840;
  --neon:     #00ffd0;
}

*,*::before,*::after { margin:0; padding:0; box-sizing:border-box; }
html,body,.stApp { background:var(--bg)!important; color:var(--text); font-family:'Inter',sans-serif; }
#MainMenu,footer,header { visibility:hidden!important; }
.stDeployButton,[data-testid="stToolbar"] { display:none!important; }
section[data-testid="stSidebar"] { display:none!important; }
.block-container { padding:0 .65rem 3rem!important; max-width:100%!important; }

/* ── HEADER ── */
.hdr { text-align:center; padding:1.5rem 1rem .9rem; }
.hdr h1 {
  font-size:clamp(1.6rem,5vw,2.7rem); font-weight:800; letter-spacing:4px; line-height:1.1; margin-bottom:.35rem;
  background:linear-gradient(120deg,#e8f4ff 12%,#00c8f0 50%,#6830d8 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.hdr .sub    { font-size:.79rem; color:var(--muted); letter-spacing:1.5px; margin-bottom:.12rem; }
.hdr .credit { font-family:'JetBrains Mono',monospace; font-size:.57rem; color:var(--dim); }
.hdr-line    { height:1px; background:linear-gradient(90deg,transparent,var(--accent) 38%,var(--purple) 62%,transparent); opacity:.28; max-width:380px; margin:.8rem auto 0; }

/* ── ADMIN TOGGLE BAR ── */
.atbar {
  display:flex; align-items:center; justify-content:space-between;
  padding:.42rem .85rem; background:var(--surf2);
  border:1px solid var(--bdr); border-radius:5px; margin:.55rem 0 .65rem;
}
.atbar-l { display:flex; align-items:center; gap:.48rem; }
.atdot   { width:7px; height:7px; border-radius:50%; background:var(--dim); flex-shrink:0; transition:all .3s; }
.atdot.on { background:var(--warn); box-shadow:0 0 10px var(--warn); }
.atlbl   { font-family:'JetBrains Mono',monospace; font-size:.57rem; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:var(--dim); }
.atlbl.on { color:var(--warn); }
.atbadge { font-family:'JetBrains Mono',monospace; font-size:.49rem; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; padding:.1rem .42rem; border-radius:2px; }
.atbadge.on  { background:rgba(232,176,0,.1); border:1px solid rgba(232,176,0,.25); color:var(--warn); }
.atbadge.off { background:rgba(255,255,255,.03); border:1px solid var(--bdr); color:var(--dim); }

/* ── KATEGORI — horizontal scroll ── */
div[data-testid="stHorizontalBlock"] {
  display:flex!important; flex-wrap:nowrap!important; overflow-x:auto!important;
  gap:.3rem!important; padding-bottom:3px!important; scrollbar-width:none!important;
  -webkit-overflow-scrolling:touch!important;
}
div[data-testid="stHorizontalBlock"]::-webkit-scrollbar { display:none!important; }
div[data-testid="column"] { padding:0!important; flex:0 0 auto!important; min-width:0!important; width:auto!important; }

/* ── SEMUA TOMBOL BASE ── */
div[data-testid="stButton"]>button {
  font-family:'JetBrains Mono',monospace!important;
  font-size:.61rem!important; font-weight:600!important;
  letter-spacing:1.5px!important; text-transform:uppercase!important;
  background:var(--surf)!important; color:var(--muted)!important;
  border:1px solid var(--bdr)!important; border-radius:3px!important;
  padding:.35rem .72rem!important; white-space:nowrap!important;
  height:auto!important; transition:all .18s!important;
}
div[data-testid="stButton"]>button:hover {
  background:rgba(0,200,240,.07)!important; color:var(--accent)!important;
  border-color:rgba(0,200,240,.38)!important;
}
div[data-testid="stButton"]>button:focus,
div[data-testid="stButton"]>button:active {
  background:rgba(0,200,240,.12)!important; color:var(--accent)!important;
  border-color:var(--accent)!important;
}

/* ── SECTION LABEL ── */
.sec-lbl {
  display:flex; align-items:center; gap:.6rem;
  font-family:'JetBrains Mono',monospace; font-size:.57rem; color:var(--dim);
  letter-spacing:2.5px; text-transform:uppercase; margin:.4rem 0 .7rem;
}
.sec-lbl::before { content:''; flex:1; height:1px; background:var(--bdr); }
.sec-lbl .n { color:var(--accent); font-weight:700; }

/* ══════════════════════════════════════
   NEWS CARD — redesign premium
══════════════════════════════════════ */
.card {
  background:linear-gradient(160deg, #0a1525 0%, #070f1c 100%);
  border:1px solid var(--bdr2); border-radius:8px;
  margin-bottom:.75rem; overflow:hidden; position:relative;
  transition:transform .22s, border-color .22s, box-shadow .22s;
}
/* Garis sentimen kiri */
.card::before {
  content:''; position:absolute; top:0; left:0;
  width:3px; height:100%; border-radius:3px 0 0 3px;
  background:var(--neutral);
}
.card.bullish::before { background:var(--bullish); box-shadow:0 0 12px rgba(0,216,136,.3); }
.card.bearish::before { background:var(--bearish); box-shadow:0 0 12px rgba(255,32,80,.3); }
.card.neutral::before { background:var(--neutral);  box-shadow:0 0 12px rgba(32,112,255,.2); }
.card:hover {
  transform:translateY(-2px);
  border-color:rgba(0,200,240,.3);
  box-shadow:0 6px 28px rgba(0,0,0,.4), 0 0 0 1px rgba(0,200,240,.06);
}

/* TOP ROW */
.ctop { display:flex; align-items:center; gap:.3rem; margin-bottom:.5rem; flex-wrap:wrap; padding:.85rem .95rem 0 1.15rem; }

.kat-b {
  font-family:'JetBrains Mono',monospace; font-size:.52rem; font-weight:700;
  letter-spacing:2px; text-transform:uppercase; color:var(--accent);
  background:rgba(0,200,240,.07); border:1px solid rgba(0,200,240,.2);
  border-radius:2px; padding:.07rem .38rem; flex-shrink:0;
}
.src-b {
  font-family:'JetBrains Mono',monospace; font-size:.48rem; color:var(--dim);
  background:rgba(255,255,255,.025); border:1px solid var(--bdr);
  border-radius:2px; padding:.05rem .3rem; flex-shrink:0;
}
.sent-b {
  font-family:'JetBrains Mono',monospace; font-size:.5rem; font-weight:700;
  letter-spacing:1px; text-transform:uppercase; padding:.07rem .35rem;
  border-radius:2px; flex-shrink:0; margin-left:auto;
}
.sent-b.bullish { color:var(--bullish); background:rgba(0,216,136,.08); border:1px solid rgba(0,216,136,.22); }
.sent-b.bearish { color:var(--bearish); background:rgba(255,32,80,.08);  border:1px solid rgba(255,32,80,.22); }
.sent-b.neutral { color:var(--neutral); background:rgba(32,112,255,.08); border:1px solid rgba(32,112,255,.22); }

/* DAMPAK */
.dampak {
  display:flex; align-items:center; gap:.4rem;
  padding:.3rem .95rem .3rem 1.15rem;
  border-bottom:1px solid rgba(255,255,255,.04);
  margin-bottom:.5rem;
}
.dstars { font-size:.78rem; letter-spacing:.08rem; line-height:1; }
.dlabel {
  font-family:'JetBrains Mono',monospace; font-size:.48rem;
  font-weight:600; letter-spacing:1.5px; text-transform:uppercase;
}
.d1 .dstars { color:var(--star1); text-shadow:0 0 10px rgba(0,255,136,.6); }
.d1 .dlabel { color:var(--star1); }
.d2 .dstars { color:var(--star2); text-shadow:0 0 10px rgba(255,224,0,.6); }
.d2 .dlabel { color:var(--star2); }
.d3 .dstars { color:var(--star3); text-shadow:0 0 12px rgba(255,24,64,.7); }
.d3 .dlabel { color:var(--star3); }

/* BODY */
.cbody { padding:.1rem .95rem .8rem 1.15rem; }

/* TAG ROWS */
.tag-row  { display:flex; flex-wrap:wrap; gap:.22rem; margin-bottom:.42rem; }
.etag {
  font-family:'JetBrains Mono',monospace; font-size:.48rem; font-weight:700;
  letter-spacing:1.5px; text-transform:uppercase;
  color:var(--accent); background:rgba(0,200,240,.06);
  border:1px solid rgba(0,200,240,.18); border-radius:2px; padding:.04rem .28rem;
}
.instr-row { display:flex; flex-wrap:wrap; gap:.22rem; margin-bottom:.42rem; }
.instr-tag {
  font-family:'JetBrains Mono',monospace; font-size:.46rem; font-weight:600;
  color:var(--purple); background:rgba(104,48,216,.08);
  border:1px solid rgba(104,48,216,.22); border-radius:2px; padding:.04rem .28rem;
}

/* JUDUL & DESKRIPSI */
.ntitle {
  font-size:.92rem; font-weight:700; color:#d8eaf8;
  line-height:1.48; margin-bottom:.45rem;
  letter-spacing:-.01em;
}
.ndesc {
  font-size:.79rem; color:var(--muted);
  line-height:1.68; margin-bottom:.55rem;
}

/* CATATAN EDITOR */
.enote {
  border-left:3px solid rgba(232,176,0,.5);
  background:rgba(232,176,0,.04);
  padding:.45rem .65rem .45rem .7rem;
  margin-bottom:.5rem; border-radius:0 4px 4px 0;
}
.enote-lbl {
  font-family:'JetBrains Mono',monospace; font-size:.48rem; font-weight:700;
  letter-spacing:2px; text-transform:uppercase; color:var(--warn);
  margin-bottom:.2rem; display:flex; align-items:center; gap:.3rem;
}
.enote-lbl::before { content:''; width:14px; height:1px; background:var(--warn); opacity:.5; }
.enote-text { font-size:.76rem; color:#a89040; line-height:1.65; font-style:italic; }

/* DISCLAIMER */
.disc {
  display:flex; align-items:flex-start; gap:.4rem;
  background:rgba(232,176,0,.04); border:1px solid rgba(232,176,0,.16);
  border-radius:4px; padding:.4rem .6rem; margin-bottom:.5rem;
}
.disc-ico { color:var(--warn); font-size:.7rem; flex-shrink:0; margin-top:.05rem; }
.disc-txt {
  font-family:'JetBrains Mono',monospace; font-size:.52rem;
  color:#907830; line-height:1.6; letter-spacing:.2px;
}

/* META */
.cmeta {
  display:flex; align-items:center; gap:.3rem; padding-top:.4rem;
  border-top:1px solid rgba(255,255,255,.04);
  font-family:'JetBrains Mono',monospace; font-size:.54rem; color:var(--dim); flex-wrap:wrap;
}
.msrc { color:var(--muted); font-weight:600; }
.mdot { width:3px; height:3px; border-radius:50%; background:var(--dim); flex-shrink:0; }

/* ── TOMBOL DETAIL DALAM KARTU ── */
.card-action {
  display: flex;
  align-items: center;
  gap: .55rem;
  padding: .6rem .95rem .65rem 1.15rem;
  border-top: 1px solid rgba(255,255,255,.04);
  cursor: pointer;
  transition: background .18s;
}
.card-action:hover { background: rgba(0,200,240,.03); }

.action-circle {
  width: 26px; height: 26px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  font-size: .65rem; font-weight: 700;
  transition: all .2s;
}
.circle-open {
  background: rgba(0,200,240,.12);
  border: 1.5px solid rgba(0,200,240,.5);
  color: #00c8f0;
  box-shadow: 0 0 10px rgba(0,200,240,.2);
}
.circle-open:hover {
  background: rgba(0,200,240,.22);
  box-shadow: 0 0 18px rgba(0,200,240,.35);
}
.circle-close {
  background: rgba(255,24,64,.12);
  border: 1.5px solid rgba(255,24,64,.5);
  color: #ff1840;
  box-shadow: 0 0 10px rgba(255,24,64,.22);
}
.circle-close:hover {
  background: rgba(255,24,64,.22);
  box-shadow: 0 0 18px rgba(255,24,64,.38);
}

.action-text-open {
  font-family: 'JetBrains Mono', monospace;
  font-size: .57rem; font-weight: 600;
  letter-spacing: 1.8px; text-transform: uppercase;
  color: var(--accent);
}
.action-text-close {
  font-family: 'JetBrains Mono', monospace;
  font-size: .57rem; font-weight: 600;
  letter-spacing: 1.8px; text-transform: uppercase;
  color: #ff1840;
}
.action-sub {
  font-family: 'JetBrains Mono', monospace;
  font-size: .46rem; color: var(--dim);
  letter-spacing: 1px; margin-top: .08rem;
}

/* DETAIL PANEL */
.det {
  border-top:1px solid rgba(0,200,240,.08);
  background:rgba(0,4,12,.6); padding:.65rem .95rem .65rem 1.15rem;
}
.det-lbl {
  font-family:'JetBrains Mono',monospace; font-size:.49rem; letter-spacing:2.5px;
  text-transform:uppercase; color:var(--dim); margin-bottom:.32rem;
}
.det-txt  { font-size:.78rem; color:var(--muted); line-height:1.7; }
.det-foot { margin-top:.3rem; font-family:'JetBrains Mono',monospace; font-size:.49rem; color:var(--dim); }

/* ADMIN PANEL */
.adm-box { background:var(--surf); border:1px solid var(--bdr2); border-radius:8px; overflow:hidden; margin-bottom:.8rem; }
.adm-head {
  background:linear-gradient(135deg,rgba(232,176,0,.07),rgba(104,48,216,.05));
  border-bottom:1px solid var(--bdr2); padding:.58rem .8rem;
  display:flex; align-items:center; gap:.4rem;
}
.adm-dot   { width:6px; height:6px; border-radius:50%; background:var(--warn); box-shadow:0 0 9px var(--warn); flex-shrink:0; }
.adm-title { font-family:'JetBrains Mono',monospace; font-size:.59rem; font-weight:700; letter-spacing:2.5px; text-transform:uppercase; color:var(--warn); }
.adm-body  { padding:.65rem .8rem .8rem; }
.flbl {
  font-family:'JetBrains Mono',monospace; font-size:.51rem; font-weight:600;
  letter-spacing:2px; text-transform:uppercase; color:var(--dim);
  margin-bottom:.2rem; margin-top:.48rem;
}
.flbl:first-child { margin-top:0; }
.fsep { height:1px; background:var(--bdr); margin:.5rem 0; }

/* Dampak selector */
.d-preview {
  text-align:center; padding:.38rem; border-radius:4px;
  font-family:'JetBrains Mono',monospace; margin:.28rem 0;
}

/* Publish button */
.pub-btn div[data-testid="stButton"]>button {
  width:100%!important;
  background:linear-gradient(135deg,rgba(0,200,240,.14),rgba(104,48,216,.1))!important;
  color:var(--accent)!important; border-color:rgba(0,200,240,.45)!important;
  box-shadow:0 0 16px rgba(0,200,240,.08)!important;
  font-size:.63rem!important; padding:.43rem 1rem!important;
}
.pub-btn div[data-testid="stButton"]>button:hover {
  box-shadow:0 0 24px rgba(0,200,240,.18)!important;
}

/* Saved list */
.saved-i { font-size:.71rem; color:var(--muted); padding:.23rem 0; border-bottom:1px solid var(--bdr); }

/* Widget overrides */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
  background:var(--surf2)!important; color:var(--text)!important;
  border:1px solid var(--bdr2)!important; border-radius:4px!important;
  font-family:'Inter',sans-serif!important; font-size:.81rem!important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus { border-color:rgba(0,200,240,.45)!important; }
div[data-baseweb="select"]>div { background:var(--surf2)!important; border-color:var(--bdr2)!important; border-radius:4px!important; }

/* EMPTY */
.empty { text-align:center; padding:2.5rem 1.5rem; border:1px solid var(--bdr); border-radius:8px; margin:.8rem 0; }
.empty h3 { font-family:'JetBrains Mono',monospace; font-size:.63rem; letter-spacing:2.5px; text-transform:uppercase; color:var(--muted); margin-bottom:.4rem; }
.empty p  { font-size:.77rem; color:var(--dim); line-height:1.65; }

/* FOOTER */
.ftr { margin-top:2rem; padding:.9rem; border-top:1px solid var(--bdr); text-align:center; font-family:'JetBrains Mono',monospace; font-size:.55rem; color:var(--dim); line-height:1.9; }
.ftr .brand { color:var(--accent); font-weight:700; letter-spacing:2px; }

@media(max-width:900px) {
  .ntitle { font-size:.87rem; }
  .block-container { padding-left:.35rem!important; padding-right:.35rem!important; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hdr">
  <h1>MARKET INTELLIGENCE</h1>
  <div class="sub">Analisis Mendalam untuk Trader Modern</div>
  <div class="credit">Dirancang oleh Tim Aerovulpis</div>
  <div class="hdr-line"></div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# KONSTANTA
# ══════════════════════════════════════════════════════════════════
KATEGORI = {
    "all":"Semua","stock":"Saham","crypto":"Aset Digital",
    "geopolitics":"Geopolitik","forex":"Valuta Asing",
    "indonesia":"Indonesia","economy_us":"Ekonomi AS","fed":"Federal Reserve",
}
KAT_LABEL = {
    "stock":"SAHAM","crypto":"ASET DIGITAL","geopolitics":"GEOPOLITIK",
    "forex":"VALUTA ASING","indonesia":"INDONESIA","economy_us":"EKONOMI AS","fed":"FEDERAL RESERVE",
}
INSTRUMEN = [
    "Tidak Ada / None",
    "XAUUSD","XAGUSD","EURUSD","GBPUSD","USDJPY","AUDUSD","USDCAD","USDCHF","NZDUSD",
    "DXY (Dolar Index)","US10Y Treasury","US30Y Treasury",
    "BTC/USD","ETH/USD","BNB/USD","SOL/USD","XRP/USD",
    "S&P 500","NASDAQ","Dow Jones","IHSG","Nikkei 225","Hang Seng",
    "Minyak WTI","Minyak Brent","Gas Alam",
]
# Tag dikelompokkan: Mata Uang | Komoditas | Aset | Event Makro AS | Event Global | Indonesia
TAGS = [
    # Mata uang
    "USD","EUR","IDR","JPY","GBP","CNY",
    # Komoditas & aset
    "Gold","Silver","Oil","Gas","Crypto","Saham",
    # Event makro AS
    "NFP","CPI","PPI","PCE","GDP","FOMC","Fed Minutes","Retail Sales",
    # Event bank sentral global
    "ECB","BOJ","BI Rate","PBOC",
    # Indikator makro
    "PMI","Unemployment","Trade Balance","Inflation",
    # Indonesia
    "IHSG","Rupiah","BI","BPS","APBN",
    # Geopolitik & sentimen
    "Tariff","Sanctions","War Risk","Risk On","Risk Off",
]
DAMPAK_CFG = {
    1:{"cls":"d1","stars":"★","rest":"☆☆","label":"DAMPAK RENDAH","color":"#00ff88","glow":"rgba(0,255,136,.22)"},
    2:{"cls":"d2","stars":"★★","rest":"☆","label":"DAMPAK SEDANG","color":"#ffe000","glow":"rgba(255,224,0,.22)"},
    3:{"cls":"d3","stars":"★★★","rest":"","label":"DAMPAK TINGGI","color":"#ff1840","glow":"rgba(255,24,64,.28)"},
}

# ══════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════
for k, v in [
    ("kat","all"), ("show_detail",{}),
    ("berita",[]), ("dampak_sel",2), ("admin_mode",False),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════
# HELPERS — PENTING: render_html tidak di-escape
# ══════════════════════════════════════════════════════════════════
def tx(v) -> str:
    """Escape teks plain untuk HTML — HANYA untuk konten teks, bukan HTML."""
    return escape(str(v)) if v else ""

def fmt_dt(s: str) -> str:
    try:
        dt = datetime.fromisoformat(s.replace("Z","+00:00"))
        return dt.strftime("%d %b %Y %H:%M")
    except:
        return str(s)

def build_card_html(item: dict, kid: str, show_detail: bool) -> str:
    """Bangun HTML kartu — semua bagian dirakit di Python, lalu dirender sekali."""
    warna     = item.get("sentimen","neutral")
    tag       = item.get("kategori_label","T.I.M NEWS")
    sent_map  = {"bullish":"+ BULLISH","bearish":"- BEARISH","neutral":"~ NETRAL"}
    sent_lbl  = sent_map.get(warna,"~ NETRAL")
    wkt       = item.get("waktu_terbit","")
    instrumen = [x for x in item.get("instrumen",[]) if x != "Tidak Ada / None"]
    tags_list = item.get("tags",[])
    dampak    = item.get("dampak",1)
    dcfg      = DAMPAK_CFG.get(dampak, DAMPAK_CFG[1])
    editor    = item.get("catatan_editor","").strip()
    disc      = item.get("pakai_disclaimer", False)
    judul     = item.get("judul","")
    deskripsi = item.get("deskripsi","")

    # Dampak row
    dampak_row = (
        f'<div class="dampak {dcfg["cls"]}">'
        f'<span class="dstars">{dcfg["stars"]}{dcfg["rest"]}</span>'
        f'<span class="dlabel">{dcfg["label"]}</span>'
        f'</div>'
    )

    # Tags ekonomi
    tags_row = ""
    if tags_list:
        tags_inner = "".join(f'<span class="etag">{tx(t)}</span>' for t in tags_list)
        tags_row = f'<div class="tag-row">{tags_inner}</div>'

    # Instrumen
    instr_row = ""
    if instrumen:
        instr_inner = "".join(f'<span class="instr-tag">{tx(ins)}</span>' for ins in instrumen)
        instr_row = f'<div class="instr-row">{instr_inner}</div>'

    # Catatan editor
    editor_block = ""
    if editor:
        editor_block = (
            f'<div class="enote">'
            f'<div class="enote-lbl">Catatan Editor</div>'
            f'<div class="enote-text">{tx(editor)}</div>'
            f'</div>'
        )

    # Disclaimer
    disc_block = ""
    if disc:
        disc_block = (
            f'<div class="disc">'
            f'<span class="disc-ico">&#9888;</span>'
            f'<span class="disc-txt">Ini merupakan perkiraan/prediksi Tim Analis T.I.M NEWS '
            f'dan bukan merupakan rekomendasi investasi.</span>'
            f'</div>'
        )

    # Action button dalam kartu
    if show_detail:
        action_html = (
            f'<div class="card-action">'
            f'  <div class="action-circle circle-close">&#10005;</div>'
            f'  <div>'
            f'    <div class="action-text-close">Sembunyikan Berita</div>'
            f'    <div class="action-sub">Tutup ringkasan berita ini</div>'
            f'  </div>'
            f'</div>'
        )
    else:
        action_html = (
            f'<div class="card-action">'
            f'  <div class="action-circle circle-open">&#9654;</div>'
            f'  <div>'
            f'    <div class="action-text-open">Baca Selengkapnya</div>'
            f'    <div class="action-sub">Buka ringkasan berita & analisis</div>'
            f'  </div>'
            f'</div>'
        )

    # Detail panel (muncul di dalam kartu jika show_detail True)
    detail_inner = ""
    if show_detail:
        instrumen_d = [x for x in item.get("instrumen",[]) if x != "Tidak Ada / None"]
        instr_str_d = ", ".join(instrumen_d) if instrumen_d else "Tidak ada"
        dcfg_d = DAMPAK_CFG.get(dampak, DAMPAK_CFG[1])
        detail_inner = (
            f'<div class="det">'
            f'  <div class="det-lbl">Ringkasan Berita</div>'
            f'  <div class="det-txt">{tx(deskripsi)}</div>'
            f'  <div class="det-foot">'
            f'    Instrumen: {tx(instr_str_d)} &nbsp;|&nbsp; '
            f'    Dampak: {dcfg_d["stars"]} {dcfg_d["label"]} &nbsp;|&nbsp; '
            f'    {tx(wkt)}'
            f'  </div>'
            f'</div>'
        )

    html = (
        f'<div class="card {warna}">'
        f'  <div class="ctop">'
        f'    <span class="kat-b">{tx(tag)}</span>'
        f'    <span class="src-b">T.I.M NEWS</span>'
        f'    <span class="sent-b {warna}">{sent_lbl}</span>'
        f'  </div>'
        f'  {dampak_row}'
        f'  <div class="cbody">'
        f'    {tags_row}'
        f'    {instr_row}'
        f'    <div class="ntitle">{tx(judul)}</div>'
        f'    <div class="ndesc">{tx(deskripsi)}</div>'
        f'    {editor_block}'
        f'    {disc_block}'
        f'    <div class="cmeta">'
        f'      <span class="msrc">T.I.M NEWS</span>'
        f'      <span class="mdot"></span>'
        f'      <span>{tx(wkt)}</span>'
        f'    </div>'
        f'  </div>'
        f'  {action_html}'
        f'  {detail_inner}'
        f'</div>'
    )
    return html

# ══════════════════════════════════════════════════════════════════
# ADMIN TOGGLE BAR
# ══════════════════════════════════════════════════════════════════
is_admin  = st.session_state.admin_mode
dot_cls   = "atdot on" if is_admin else "atdot"
lbl_cls   = "atlbl on" if is_admin else "atlbl"
badge_cls = "atbadge on" if is_admin else "atbadge off"
mode_txt  = "EDITOR AKTIF" if is_admin else "READER MODE"
btn_lbl   = "TUTUP ADMIN" if is_admin else "ADMIN"

col_tbar, col_tbtn = st.columns([5, 1])
with col_tbar:
    st.markdown(
        f'<div class="atbar">'
        f'<div class="atbar-l"><div class="{dot_cls}"></div>'
        f'<span class="{lbl_cls}">T.I.M NEWS</span></div>'
        f'<span class="{badge_cls}">{mode_txt}</span>'
        f'</div>',
        unsafe_allow_html=True
    )
with col_tbtn:
    if st.button(btn_lbl, key="tog_admin", use_container_width=True):
        st.session_state.admin_mode = not st.session_state.admin_mode
        st.rerun()

# ══════════════════════════════════════════════════════════════════
# KATEGORI BUTTONS — HANYA st.button, tidak ada markdown duplikat
# ══════════════════════════════════════════════════════════════════
kat_aktif = st.session_state.kat
kat_cols  = st.columns(len(KATEGORI))
for i, (k, v) in enumerate(KATEGORI.items()):
    with kat_cols[i]:
        # Gaya aktif via CSS inline pada wrapper
        aktif = k == kat_aktif
        style = (
            "background:rgba(0,200,240,.12)!important;"
            "color:#00c8f0!important;"
            "border-color:#00c8f0!important;"
            "box-shadow:0 0 12px rgba(0,200,240,.14)!important;"
        ) if aktif else ""
        if style:
            st.markdown(
                f'<style>div[data-testid="stButton"]:has(button[kind="secondary"]#cat_{k}) button'
                f'{{ {style} }}</style>',
                unsafe_allow_html=True
            )
        if st.button(v, key=f"cat_{k}", use_container_width=True):
            st.session_state.kat = k
            st.session_state.show_detail = {}
            st.rerun()

# ══════════════════════════════════════════════════════════════════
# FILTER BERITA
# ══════════════════════════════════════════════════════════════════
kat_aktif = st.session_state.kat
items = st.session_state.berita if kat_aktif == "all" else [
    b for b in st.session_state.berita if b.get("kategori_key") == kat_aktif
]
cat_lbl = KATEGORI.get(kat_aktif, "Semua")

# ══════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════
if st.session_state.admin_mode:
    col_feed, col_admin = st.columns([3, 1], gap="medium")
else:
    col_feed  = st.container()
    col_admin = None

# ══════════════════════════════════════════════════════════════════
# FEED
# ══════════════════════════════════════════════════════════════════
with col_feed:
    if not items:
        if kat_aktif == "all":
            empty_msg = (
                "Tim Aerovulpis & T.I.M NEWS sedang menyiapkan berita terkini untuk Anda. "
                "Mohon bersabar — update akan segera hadir."
            )
        else:
            empty_msg = (
                f"Belum ada update untuk kategori <strong>{tx(cat_lbl)}</strong> saat ini. "
                "Tim T.I.M NEWS sedang memantau perkembangan pasar dan akan segera hadir."
            )
        st.markdown(
            f'''<div class="empty">
              <div style="font-size:1.6rem;opacity:.18;margin-bottom:.8rem">&#9711;</div>
              <h3>Sedang Disiapkan</h3>
              <p>{empty_msg}</p>
              <div style="font-family:'JetBrains Mono',monospace;font-size:.5rem;
                          color:var(--dim);letter-spacing:2px;margin-top:.8rem">
                T.I.M NEWS | AEROVULPIS INTELLIGENCE
              </div>
            </div>''',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="sec-lbl"><span>FEED BERITA</span>'
            f'<span class="n">{len(items)} artikel</span></div>',
            unsafe_allow_html=True
        )
        for i, item in enumerate(items):
            kid = f"{kat_aktif}_{item.get('id','')}"

            # Render kartu — HTML dirakit di Python, tidak ada interpolasi double
            show_det = st.session_state.show_detail.get(kid, False)
            st.markdown(build_card_html(item, kid, show_det), unsafe_allow_html=True)

            # Tombol styled menyatu dengan kartu — override CSS per-key
            is_open = st.session_state.show_detail.get(kid, False)
            if is_open:
                btn_label = "✕  Sembunyikan Berita"
                btn_style = (
                    "background:rgba(255,24,64,.1)!important;"
                    "color:#ff1840!important;"
                    "border-color:rgba(255,24,64,.4)!important;"
                    "box-shadow:0 0 12px rgba(255,24,64,.18)!important;"
                    "border-radius:0 0 7px 7px!important;"
                    "border-top:1px solid rgba(255,24,64,.15)!important;"
                    "margin-top:-2px!important;"
                    "font-size:.58rem!important;"
                    "letter-spacing:2px!important;"
                    "padding:.4rem 1rem!important;"
                    "width:100%!important;"
                )
            else:
                btn_label = "▶  Baca Selengkapnya"
                btn_style = (
                    "background:rgba(0,200,240,.07)!important;"
                    "color:#00c8f0!important;"
                    "border-color:rgba(0,200,240,.3)!important;"
                    "box-shadow:0 0 10px rgba(0,200,240,.12)!important;"
                    "border-radius:0 0 7px 7px!important;"
                    "border-top:1px solid rgba(0,200,240,.1)!important;"
                    "margin-top:-2px!important;"
                    "font-size:.58rem!important;"
                    "letter-spacing:2px!important;"
                    "padding:.4rem 1rem!important;"
                    "width:100%!important;"
                )
            safe_kid = kid.replace('-','_').replace('.','_')
            st.markdown(
                f'<style>div[data-testid="stButton"]:has(>button[data-testid="baseButton-secondary"])#btn_{safe_kid},'
                f'button[kind="secondary"][aria-label="{btn_label}"] {{'
                f'{btn_style}}}</style>',
                unsafe_allow_html=True
            )
            if st.button(btn_label, key=f"d_{kid}", use_container_width=True):
                st.session_state.show_detail[kid] = not is_open
                st.rerun()

    st.markdown(
        '<div class="ftr"><span class="brand">AEROVULPIS</span> | '
        '2026 Market Intelligence Terminal<br>'
        'Dikembangkan oleh DynamiHatch | Teknologi Intelijensi Pasar Masa Depan</div>',
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════════════════════════════
# ADMIN PANEL
# ══════════════════════════════════════════════════════════════════
if st.session_state.admin_mode and col_admin is not None:
    with col_admin:
        st.markdown(
            '<div class="adm-box"><div class="adm-head">'
            '<div class="adm-dot"></div>'
            '<div class="adm-title">T.I.M NEWS</div>'
            '</div></div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="flbl">Judul Berita</div>', unsafe_allow_html=True)
        judul_in = st.text_input("j", label_visibility="collapsed",
            placeholder="Masukkan judul berita...", key="f_judul")

        st.markdown('<div class="flbl">Deskripsi / Isi</div>', unsafe_allow_html=True)
        desk_in = st.text_area("d", label_visibility="collapsed",
            placeholder="Tulis isi berita lengkap...", height=95, key="f_desk")

        st.markdown('<div class="fsep"></div>', unsafe_allow_html=True)

        st.markdown('<div class="flbl">Tanggal</div>', unsafe_allow_html=True)
        tgl_in = st.date_input("tgl", label_visibility="collapsed",
            value=datetime.now(timezone.utc).date(), key="f_tgl")

        st.markdown('<div class="flbl">Waktu (WIB)</div>', unsafe_allow_html=True)
        now_wib = datetime.now(timezone(timedelta(hours=7)))
        ch, cm  = st.columns(2)
        with ch:
            jam_in = st.selectbox("H", label_visibility="collapsed",
                options=[f"{h:02d}" for h in range(24)], index=now_wib.hour, key="f_jam")
        with cm:
            mnt_in = st.selectbox("M", label_visibility="collapsed",
                options=[f"{m:02d}" for m in range(0,60,5)],
                index=now_wib.minute//5, key="f_mnt")

        st.markdown('<div class="fsep"></div>', unsafe_allow_html=True)

        st.markdown('<div class="flbl">Kategori</div>', unsafe_allow_html=True)
        kat_in = st.selectbox("k", label_visibility="collapsed",
            options=list(KAT_LABEL.keys()),
            format_func=lambda x: KAT_LABEL[x].title(), key="f_kat")

        st.markdown('<div class="flbl">Sentimen</div>', unsafe_allow_html=True)
        sent_in = st.selectbox("s", label_visibility="collapsed",
            options=["bullish","bearish","neutral"],
            format_func=lambda x: {"bullish":"+ Bullish","bearish":"- Bearish","neutral":"~ Netral"}[x],
            key="f_sent")

        # Dampak bintang
        st.markdown('<div class="flbl">Tingkat Dampak</div>', unsafe_allow_html=True)
        dc1, dc2, dc3 = st.columns(3)
        with dc1:
            if st.button("★ LOW",  key="d1b", use_container_width=True):
                st.session_state.dampak_sel = 1; st.rerun()
        with dc2:
            if st.button("★★ MED", key="d2b", use_container_width=True):
                st.session_state.dampak_sel = 2; st.rerun()
        with dc3:
            if st.button("★★★ HI", key="d3b", use_container_width=True):
                st.session_state.dampak_sel = 3; st.rerun()

        d_aktif = st.session_state.dampak_sel
        dcfg    = DAMPAK_CFG[d_aktif]
        st.markdown(
            f'<div class="d-preview" style="border:1px solid {dcfg["color"]}30;'
            f'background:{dcfg["color"]}0d;box-shadow:0 0 14px {dcfg["glow"]};">'
            f'<span style="color:{dcfg["color"]};text-shadow:0 0 10px {dcfg["color"]};'
            f'font-size:.92rem;letter-spacing:.1rem">{dcfg["stars"]}</span>'
            f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:.48rem;'
            f'color:{dcfg["color"]};letter-spacing:1.5px;text-transform:uppercase;'
            f'display:block;margin-top:.12rem">{dcfg["label"]}</span></div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="flbl">Tag Ekonomi</div>', unsafe_allow_html=True)
        tags_in = st.multiselect("tg", label_visibility="collapsed",
            options=TAGS, placeholder="Pilih tag...", key="f_tags")

        st.markdown('<div class="flbl">Instrumen Terdampak</div>', unsafe_allow_html=True)
        instr_in = st.multiselect("i", label_visibility="collapsed",
            options=INSTRUMEN, placeholder="Pilih instrumen...", key="f_instr")

        st.markdown('<div class="flbl">Catatan Editor <span style="color:var(--dim);font-size:.42rem"> (OPSIONAL)</span></div>', unsafe_allow_html=True)
        editor_in = st.text_area("e", label_visibility="collapsed",
            placeholder="Konteks tambahan dari tim (opsional)...", height=58, key="f_editor")

        st.markdown('<div class="fsep"></div>', unsafe_allow_html=True)
        disc_in = st.checkbox("Tambahkan disclaimer prediksi", key="f_disc")

        st.markdown('<div class="fsep"></div>', unsafe_allow_html=True)
        st.markdown('<div class="pub-btn">', unsafe_allow_html=True)
        if st.button("PUBLISH BERITA", key="pub", use_container_width=True):
            if judul_in.strip() and desk_in.strip():
                instr_clean = [x for x in instr_in if x != "Tidak Ada / None"]
                wkt_str = f"{tgl_in.strftime('%d %b %Y')} {jam_in}:{mnt_in} WIB"
                berita_baru = {
                    "id":             str(len(st.session_state.berita)),
                    "judul":          judul_in.strip(),
                    "deskripsi":      desk_in.strip(),
                    "waktu_terbit":   wkt_str,
                    "sentimen":       sent_in,
                    "kategori_key":   kat_in,
                    "kategori_label": KAT_LABEL[kat_in],
                    "instrumen":      instr_clean,
                    "dampak":         d_aktif,
                    "tags":           tags_in,
                    "catatan_editor": editor_in.strip(),
                    "pakai_disclaimer": disc_in,
                }
                st.session_state.berita.insert(0, berita_baru)
                for k in ["f_judul","f_desk","f_instr","f_tags","f_editor","f_disc"]:
                    if k in st.session_state: del st.session_state[k]
                st.success("Berita dipublish!")
                st.rerun()
            else:
                st.error("Judul dan deskripsi wajib diisi.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Daftar tersimpan
        if st.session_state.berita:
            st.markdown('<div class="fsep"></div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="flbl">Tersimpan ({len(st.session_state.berita)})</div>',
                unsafe_allow_html=True
            )
            for idx, b in enumerate(st.session_state.berita):
                preview = b["judul"][:32] + "..." if len(b["judul"]) > 32 else b["judul"]
                dcfg_s  = DAMPAK_CFG.get(b.get("dampak",1), DAMPAK_CFG[1])
                c1, c2  = st.columns([5,1])
                with c1:
                    st.markdown(
                        f'<div class="saved-i">'
                        f'<span style="color:{dcfg_s["color"]};font-size:.6rem">{dcfg_s["stars"]}</span> '
                        f'{tx(preview)}</div>',
                        unsafe_allow_html=True
                    )
                with c2:
                    if st.button("X", key=f"del_{idx}", use_container_width=True):
                        st.session_state.berita.pop(idx)
                        st.rerun()