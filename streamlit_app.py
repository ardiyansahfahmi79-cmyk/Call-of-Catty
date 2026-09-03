"""
partner_broker_page.py — Aerovulpis · Partner Broker (Standalone Prototype)
Run : streamlit run partner_broker_page.py
Deps: streamlit
"""

import streamlit as st

st.set_page_config(
    page_title="Partner Broker · Aerovulpis",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
#  BROKER DATA
# ══════════════════════════════════════════════════════════════════════════════

BROKERS = [
    {
        "id":          "fbs",
        "name":        "FBS",
        "tagline":     "Global Broker Terpercaya Sejak 2009",
        "rating":      4.5,
        "reg":         "CySEC · FSC · ASIC",
        "est":         "2009",
        "color":       "#4FC3F7",
        "logo_url":    "https://fbs.com/img/favicon/favicon-32x32.png",
        "logo_full":   "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/FBS_broker_logo.svg/200px-FBS_broker_logo.svg.png",
        "reg_link":    "#",
        "ib_link":     "#",  # Ganti dengan link IB kamu
        "badge":       "REGULATED",
        "badge_color": "#00FFC8",
        "highlight":   "17 JUTA+ TRADER",
        "accounts": [
            {
                "type":    "CENT",
                "color":   "#4FC3F7",
                "deposit": "$1",
                "spread":  "1.0 pips",
                "lev":     "1:1000",
                "comm":    "Tanpa Komisi",
                "swap":    "Swap-Free Tersedia",
                "best":    "Pemula",
            },
            {
                "type":    "STANDARD",
                "color":   "#00FFC8",
                "deposit": "$5",
                "spread":  "0.7 pips",
                "lev":     "1:3000",
                "comm":    "Tanpa Komisi",
                "swap":    "Swap-Free Tersedia",
                "best":    "Semua Trader",
            },
        ],
        "features": [
            ("Regulasi",             "CySEC (EU), FSC, ASIC — teregulasi multi-jurisdiksi"),
            ("Min. Deposit",         "$1 (Cent) · $5 (Standard)"),
            ("Min. Penarikan",       "$5"),
            ("Leverage Maks",        "Hingga 1:3000"),
            ("Spread Mulai",         "0.7 pips — kompetitif untuk forex major"),
            ("Instrumen",            "550+ Forex, Saham, Indeks, Komoditas, Crypto"),
            ("Platform",             "MT4, MT5, Aplikasi Mobile FBS"),
            ("Eksekusi",             "Ab initio 0.01 detik, tanpa requote"),
            ("Bonus",                "Bonus Deposit + Program Loyalitas"),
            ("Dukungan",             "24/7 Live Chat, Email, Telepon"),
        ],
        "pros": [
            "Regulasi ketat multi-negara (CySEC, ASIC)",
            "Leverage tinggi hingga 1:3000",
            "Akun Cent — modal sangat kecil",
            "17 juta+ trader global",
            "Proses withdrawal cepat 15–20 menit",
            "Platform MT4 & MT5 lengkap",
        ],
        "cons": [
            "Spread Standard lebih tinggi dari ECN",
            "Beberapa fitur terbatas per region",
        ],
        "verdict": "FBS adalah pilihan solid untuk trader Indonesia yang menginginkan broker terregulasi ketat dengan fleksibilitas tinggi. Akun Cent ideal untuk pemula yang ingin latihan dengan modal nyata.",
    },
    {
        "id":          "headway",
        "name":        "HEADWAY",
        "tagline":     "Ecosystem Broker Modern · Copy Trading",
        "rating":      4.2,
        "reg":         "FSCA (South Africa)",
        "est":         "2022",
        "color":       "#FFD93D",
        "logo_url":    "https://hw.site/favicon.ico",
        "logo_full":   "https://hw.site/favicon.ico",
        "reg_link":    "#",
        "ib_link":     "#",  # Ganti dengan link IB kamu
        "badge":       "COPY TRADING",
        "badge_color": "#FFD93D",
        "highlight":   "LEVERAGE UNLIMITED",
        "accounts": [
            {
                "type":    "CENT",
                "color":   "#FFD93D",
                "deposit": "$1",
                "spread":  "0.3 pips",
                "lev":     "1:Unlimited*",
                "comm":    "Tanpa Komisi",
                "swap":    "Swap-Free Tersedia",
                "best":    "Pemula",
            },
            {
                "type":    "STANDARD",
                "color":   "#FF9F43",
                "deposit": "$1",
                "spread":  "0.3 pips",
                "lev":     "1:Unlimited*",
                "comm":    "Tanpa Komisi",
                "swap":    "Swap-Free Tersedia",
                "best":    "Umum",
            },
            {
                "type":    "PRO",
                "color":   "#C77DFF",
                "deposit": "$100",
                "spread":  "0.0 pips",
                "lev":     "1:Unlimited*",
                "comm":    "$1.5/lot",
                "swap":    "Swap-Free Tersedia",
                "best":    "Profesional",
            },
        ],
        "features": [
            ("Regulasi",         "FSCA South Africa (Lic. 52108)"),
            ("Min. Deposit",     "$1 (Cent & Standard) · $100 (Pro)"),
            ("Min. Penarikan",   "$1"),
            ("Leverage",         "1:1 hingga Unlimited (setelah 5 lot)"),
            ("Spread Mulai",     "0.0 pips (Pro) · 0.3 pips (Standard)"),
            ("Instrumen",        "500+ Forex, Crypto, Saham, Indeks, Energi"),
            ("Platform",         "MT4, MT5, Headway Trading App"),
            ("Copy Trading",     "Social Trading & Copy Trading built-in"),
            ("Bonus",            "$150 No-Deposit Bonus · Bonus Deposit 75%"),
            ("Dukungan",         "24/7 Live Chat, WhatsApp, Telegram"),
        ],
        "pros": [
            "Akun Cent tersedia — ideal pemula",
            "Copy Trading & Social Trading terintegrasi",
            "Leverage unlimited (post 5 lot)",
            "Bonus tanpa deposit $150",
            "Spread 0.0 pips untuk akun Pro",
            "500+ instrumen trading",
        ],
        "cons": [
            "Regulasi FSCA — bukan tier-1 (CySEC/FCA)",
            "Broker relatif baru (2022)",
            "Leverage unlimited = risiko tinggi bagi pemula",
        ],
        "verdict": "Headway cocok untuk trader yang ingin eksplorasi copy trading dengan modal minimal. Fitur leverage fleksibel dan bonus tanpa deposit menarik, namun perhatikan regulasi FSCA yang bukan tier-1.",
    },
]

STAR_FULL  = "&#9733;"
STAR_EMPTY = "&#9734;"

def stars_html(rating: float, color: str) -> str:
    full  = int(rating)
    half  = 1 if (rating - full) >= 0.5 else 0
    empty = 5 - full - half
    s  = f'<span style="color:{color};font-size:.85rem;">' + STAR_FULL * full
    if half:
        s += "&#189;"
    s += STAR_EMPTY * empty + "</span>"
    return s

def rating_num(rating: float, color: str) -> str:
    return f'<span style="font-family:\'Share Tech Mono\',monospace;font-size:.7rem;color:{color};font-weight:700;">{rating:.1f}/5.0</span>'

# ══════════════════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════════════════

def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

html,body,.stApp{background:#080B12!important;}
.block-container{padding:.8rem 1.2rem 3rem!important;max-width:100%!important;}
*{box-sizing:border-box;}

/* ─ PAGE HEADER ─ */
.pg-build{font-family:'Share Tech Mono',monospace;font-size:.52rem;letter-spacing:.22em;color:#0E2A1E;margin-bottom:.25rem;}
.pg-title{font-family:'Share Tech Mono',monospace;font-size:1.5rem;color:#00FFC8;letter-spacing:.06em;line-height:1.1;}
.pg-sub{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:#1A2E20;letter-spacing:.1em;margin-top:.2rem;}
.hr{border:none;border-top:1px solid #0D1724;margin:.7rem 0;}

/* ─ SECTION ─ */
.sec-title{font-family:'Share Tech Mono',monospace;color:#00FFC8;font-size:.72rem;
    letter-spacing:.2em;border-left:2px solid #00FFC8;padding-left:.65rem;
    margin:1.2rem 0 .2rem;text-transform:uppercase;}
.sec-sub{font-family:'Share Tech Mono',monospace;color:#1C3828;font-size:.54rem;
    letter-spacing:.1em;margin-bottom:.7rem;padding-left:.8rem;}

/* ─ NOTICE BOX ─ */
.notice{background:#090F18;border:1px solid #1A2D1A;border-left:2px solid #FFD93D;
    border-radius:0 2px 2px 0;padding:.65rem .85rem;margin:.5rem 0 1rem;}
.notice-t{font-family:'Share Tech Mono',monospace;font-size:.52rem;color:#FFD93D;
    letter-spacing:.13em;margin-bottom:.3rem;}
.notice-b{font-size:.7rem;color:#3A5040;line-height:1.65;}

/* ─ BROKER CARD ─ */
.bk-card{background:linear-gradient(150deg,#09101A 0%,#0B1420 100%);
    border:1px solid #141E2D;border-radius:3px;
    padding:1.1rem 1.2rem;margin-bottom:1.2rem;
    position:relative;overflow:hidden;}
.bk-top-bar{position:absolute;top:0;left:0;right:0;height:2px;background:var(--bc);}
.bk-left-bar{position:absolute;left:0;top:0;bottom:0;width:2px;background:var(--bc);}

/* ─ BROKER HEADER ─ */
.bk-header{display:flex;align-items:flex-start;gap:.9rem;flex-wrap:wrap;margin-bottom:.8rem;}
.bk-logo-wrap{width:52px;height:52px;background:#0E1520;border:1px solid #1A2D3A;
    border-radius:3px;display:flex;align-items:center;justify-content:center;
    overflow:hidden;flex-shrink:0;}
.bk-logo-wrap img{width:38px;height:38px;object-fit:contain;}
.bk-logo-fallback{font-family:'Share Tech Mono',monospace;font-size:.65rem;
    font-weight:700;color:var(--bc);text-align:center;line-height:1.2;}
.bk-meta{flex:1;}
.bk-name{font-family:'Share Tech Mono',monospace;font-size:1.2rem;font-weight:700;
    color:var(--bc);letter-spacing:.1em;line-height:1;}
.bk-tagline{font-family:'Share Tech Mono',monospace;font-size:.55rem;color:#1A3040;
    letter-spacing:.1em;margin-top:.15rem;}
.bk-reg{font-family:'Share Tech Mono',monospace;font-size:.52rem;color:#2A4050;
    margin-top:.25rem;}
.bk-badges{display:flex;gap:.35rem;flex-wrap:wrap;margin-top:.3rem;align-items:center;}

/* ─ BADGES ─ */
.bk-badge{font-family:'Share Tech Mono',monospace;font-size:.48rem;padding:1px 6px;
    border-radius:1px;font-weight:700;border:1px solid;}
.bk-hl{font-family:'Share Tech Mono',monospace;font-size:.5rem;padding:1px 7px;
    border-radius:1px;font-weight:700;letter-spacing:.05em;}

/* ─ ACCOUNT TYPE CARDS ─ */
.acc-grid{display:flex;gap:.5rem;flex-wrap:wrap;margin:.6rem 0;}
.acc-card{background:#070C14;border:1px solid #0D1724;border-radius:2px;
    padding:.6rem .75rem;flex:1;min-width:130px;position:relative;overflow:hidden;}
.acc-card-bar{position:absolute;top:0;left:0;right:0;height:1px;background:var(--ac);}
.acc-type{font-family:'Share Tech Mono',monospace;font-size:.62rem;font-weight:700;
    color:var(--ac);letter-spacing:.12em;margin-bottom:.35rem;}
.acc-best{font-family:'Share Tech Mono',monospace;font-size:.46rem;padding:1px 5px;
    border-radius:1px;background:rgba(255,255,255,.04);color:#1A3040;
    border:1px solid #0D1724;margin-left:.3rem;}
.acc-row{display:flex;justify-content:space-between;align-items:center;
    padding:.18rem 0;border-bottom:1px solid #0A1018;}
.acc-row:last-child{border-bottom:none;}
.acc-lbl{font-family:'Share Tech Mono',monospace;font-size:.48rem;color:#192838;letter-spacing:.08em;}
.acc-val{font-family:'Share Tech Mono',monospace;font-size:.58rem;color:var(--ac);font-weight:700;}

/* ─ FEATURE LIST ─ */
.feat-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:.3rem;margin:.5rem 0;}
.feat-row{display:flex;gap:.4rem;align-items:flex-start;background:#070C14;
    border:1px solid #0D1724;border-radius:2px;padding:.35rem .5rem;}
.feat-lbl{font-family:'Share Tech Mono',monospace;font-size:.5rem;color:#1A3040;
    min-width:95px;letter-spacing:.06em;padding-top:.05rem;}
.feat-val{font-size:.66rem;color:#3A5060;flex:1;line-height:1.45;}

/* ─ PROS / CONS ─ */
.pc-grid{display:grid;grid-template-columns:1fr 1fr;gap:.5rem;margin:.5rem 0;}
.pc-block{background:#070C14;border:1px solid #0D1724;border-radius:2px;padding:.5rem .65rem;}
.pc-title{font-family:'Share Tech Mono',monospace;font-size:.52rem;letter-spacing:.12em;margin-bottom:.3rem;}
.pc-item{display:flex;align-items:flex-start;gap:.3rem;margin:.18rem 0;
    font-size:.65rem;color:#3A5060;line-height:1.5;}
.pc-dot-ok{color:#00FFC8;font-size:.6rem;margin-top:.05rem;flex-shrink:0;}
.pc-dot-no{color:#FF6B6B;font-size:.6rem;margin-top:.05rem;flex-shrink:0;}

/* ─ VERDICT ─ */
.verdict-box{background:#090F18;border:1px solid #141E2D;border-left:2px solid var(--bc);
    border-radius:0 2px 2px 0;padding:.6rem .85rem;margin:.5rem 0;}
.verdict-lbl{font-family:'Share Tech Mono',monospace;font-size:.5rem;color:var(--bc);
    letter-spacing:.14em;margin-bottom:.28rem;}
.verdict-txt{font-size:.7rem;color:#4A6070;line-height:1.65;}

/* ─ CTA BUTTON ─ */
.cta-wrap{margin-top:.9rem;text-align:center;}
.cta-btn{display:inline-block;font-family:'Share Tech Mono',monospace;
    font-size:.7rem;font-weight:700;letter-spacing:.15em;
    padding:.7rem 2.5rem;border-radius:2px;text-decoration:none;
    background:transparent;border:1px solid var(--bc);color:var(--bc);
    transition:background .2s,color .2s;}
.cta-btn:hover{background:var(--bc);color:#080B12;}
.cta-sub{font-family:'Share Tech Mono',monospace;font-size:.48rem;
    color:#192838;margin-top:.35rem;letter-spacing:.1em;}

/* ─ COMPARISON TABLE ─ */
.cmp-table{width:100%;border-collapse:separate;border-spacing:0 2px;}
.cmp-th{font-family:'Share Tech Mono',monospace;font-size:.5rem;color:#1A3040;
    letter-spacing:.1em;padding:.3rem .5rem;text-align:left;background:#070C14;}
.cmp-th-r{text-align:center;}
.cmp-td{font-family:'Share Tech Mono',monospace;font-size:.6rem;color:#3A5060;
    background:#090F18;border:1px solid #0D1724;padding:.3rem .5rem;}
.cmp-td-lbl{color:#2A4050;font-size:.58rem;}
.cmp-td-fbs{color:#4FC3F7;font-weight:700;text-align:center;}
.cmp-td-hw{color:#FFD93D;font-weight:700;text-align:center;}
.cmp-win-fbs{background:rgba(79,195,247,.06)!important;color:#4FC3F7!important;}
.cmp-win-hw{background:rgba(255,217,61,.06)!important;color:#FFD93D!important;}

/* ─ SCORE BAR ─ */
.score-row{display:flex;align-items:center;gap:.5rem;margin:.2rem 0;}
.score-lbl{font-family:'Share Tech Mono',monospace;font-size:.52rem;color:#2A4050;min-width:100px;}
.score-bg{flex:1;height:4px;background:#0D1724;border-radius:2px;}
.score-fg{height:4px;border-radius:2px;}
.score-val{font-family:'Share Tech Mono',monospace;font-size:.52rem;min-width:28px;text-align:right;}

/* ─ DISCLAIMER ─ */
.disclaimer{font-family:'Share Tech Mono',monospace;font-size:.48rem;
    color:#0E2020;letter-spacing:.08em;line-height:1.7;margin-top:1.2rem;
    padding-top:.5rem;border-top:1px solid #0D1724;}

/* ─ STREAMLIT OVERRIDES ─ */
div[data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid #0D1724!important;}
div[data-baseweb="tab"]{font-family:'Share Tech Mono',monospace!important;font-size:.6rem!important;
    letter-spacing:.1em!important;color:#1C3020!important;}
div[data-baseweb="tab"][aria-selected="true"]{color:#00FFC8!important;border-bottom:2px solid #00FFC8!important;}

@media(max-width:768px){
    .block-container{padding:.5rem .5rem 3rem!important;}
    .pg-title{font-size:1.2rem;}
    .acc-grid{flex-direction:column;}
    .pc-grid{grid-template-columns:1fr;}
    .feat-grid{grid-template-columns:1fr;}
    .bk-header{gap:.6rem;}
    .cmp-table{font-size:.55rem;}
}
</style>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  RENDER HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def render_broker_card(b: dict):
    c = b["color"]

    # ── HEADER ──────────────────────────────────────────────────────────────
    # Logo: coba load dari URL, fallback ke teks
    logo_html = f"""
<div class="bk-logo-wrap" style="border-color:{c}30;">
<img src="{b['logo_url']}"
     onerror="this.style.display='none';this.nextElementSibling.style.display='block';"
     style="width:36px;height:36px;object-fit:contain;">
<div class="bk-logo-fallback" style="display:none;color:{c};">{b['name'][:3]}</div>
</div>"""

    stars  = stars_html(b["rating"], c)
    rating = rating_num(b["rating"], c)
    badge_html = f'<span class="bk-badge" style="color:{b["badge_color"]};border-color:{b["badge_color"]}40;background:rgba(0,0,0,.2);">{b["badge"]}</span>'
    hl_html    = f'<span class="bk-hl" style="background:{c}15;color:{c};border:none;">{b["highlight"]}</span>'
    est_badge  = f'<span class="bk-badge" style="color:#1A3040;border-color:#1A3040;">EST. {b["est"]}</span>'

    st.markdown(f"""
<div class="bk-card" style="--bc:{c};">
<div class="bk-top-bar"></div>
<div class="bk-left-bar"></div>
<div class="bk-header">
{logo_html}
<div class="bk-meta">
<div class="bk-name">{b['name']}</div>
<div class="bk-tagline">{b['tagline']}</div>
<div class="bk-reg">{b['reg']}</div>
<div class="bk-badges">
{stars} {rating} &nbsp; {badge_html} {hl_html} {est_badge}
</div>
</div>
</div>""", unsafe_allow_html=True)

    # ── ACCOUNT TYPES ────────────────────────────────────────────────────────
    st.markdown(f'<div class="sec-title" style="font-size:.62rem;margin-top:.2rem;">TIPE AKUN</div>', unsafe_allow_html=True)
    acc_html = '<div class="acc-grid">'
    for acc in b["accounts"]:
        ac = acc["color"]
        acc_html += f"""
<div class="acc-card" style="--ac:{ac};">
<div class="acc-card-bar"></div>
<div class="acc-type">{acc['type']}<span class="acc-best">{acc['best']}</span></div>
<div class="acc-row"><span class="acc-lbl">MIN. DEPOSIT</span><span class="acc-val">{acc['deposit']}</span></div>
<div class="acc-row"><span class="acc-lbl">SPREAD</span><span class="acc-val">{acc['spread']}</span></div>
<div class="acc-row"><span class="acc-lbl">LEVERAGE</span><span class="acc-val">{acc['lev']}</span></div>
<div class="acc-row"><span class="acc-lbl">KOMISI</span><span class="acc-val">{acc['comm']}</span></div>
<div class="acc-row"><span class="acc-lbl">SWAP</span><span class="acc-val">{acc['swap']}</span></div>
</div>"""
    acc_html += '</div>'
    st.markdown(acc_html, unsafe_allow_html=True)

    # ── FEATURES ─────────────────────────────────────────────────────────────
    st.markdown(f'<div class="sec-title" style="font-size:.62rem;margin-top:.5rem;">FITUR UTAMA</div>', unsafe_allow_html=True)
    feat_html = '<div class="feat-grid">'
    for lbl, val in b["features"]:
        feat_html += f'<div class="feat-row"><span class="feat-lbl">{lbl.upper()}</span><span class="feat-val">{val}</span></div>'
    feat_html += '</div>'
    st.markdown(feat_html, unsafe_allow_html=True)

    # ── PROS / CONS ───────────────────────────────────────────────────────────
    pros_items = "".join(f'<div class="pc-item"><span class="pc-dot-ok">+</span>{p}</div>' for p in b["pros"])
    cons_items = "".join(f'<div class="pc-item"><span class="pc-dot-no">-</span>{p}</div>' for p in b["cons"])
    st.markdown(f"""
<div class="pc-grid">
<div class="pc-block">
<div class="pc-title" style="color:#00FFC8;">KELEBIHAN</div>
{pros_items}
</div>
<div class="pc-block">
<div class="pc-title" style="color:#FF6B6B;">KEKURANGAN</div>
{cons_items}
</div>
</div>""", unsafe_allow_html=True)

    # ── VERDICT ───────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="verdict-box" style="--bc:{c};">
<div class="verdict-lbl">VERDICT AEROVULPIS</div>
<div class="verdict-txt">{b['verdict']}</div>
</div>""", unsafe_allow_html=True)

    # ── CTA ───────────────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="cta-wrap">
<a href="{b['ib_link']}" target="_blank" class="cta-btn" style="--bc:{c};">
DAFTAR SEKARANG — {b['name']}
</a>
<div class="cta-sub">* Link afiliasi resmi Aerovulpis · Partner IB terdaftar</div>
</div>

</div>""", unsafe_allow_html=True)  # tutup bk-card

def render_comparison():
    rows = [
        ("Regulasi",      "CySEC · FSC · ASIC", True,  "FSCA South Africa", False),
        ("Berdiri",       "2009 (15+ tahun)",   True,  "2022 (3 tahun)",    False),
        ("Min. Deposit",  "$1 (Cent)",           True,  "$1 (Cent)",         True),
        ("Min. Penarikan","$5",                  False, "$1",                True),
        ("Leverage Maks", "1:3000",              False, "Unlimited",         True),
        ("Spread Min",    "0.7 pips",            False, "0.0 pips (Pro)",    True),
        ("Copy Trading",  "Tidak",               False, "Ya — Built-in",     True),
        ("Akun Cent",     "Ya",                  True,  "Ya",                True),
        ("Bonus NDB",     "Tidak",               False, "$150 NDB",          True),
        ("Instrumen",     "550+",                True,  "500+",              False),
        ("Platform",      "MT4, MT5, App",       True,  "MT4, MT5, App",     True),
        ("Rating",        "4.5 / 5.0",           True,  "4.2 / 5.0",         False),
    ]

    html = """
<table class="cmp-table">
<thead>
<tr>
<th class="cmp-th">KRITERIA</th>
<th class="cmp-th cmp-th-r" style="color:#4FC3F7;">FBS</th>
<th class="cmp-th cmp-th-r" style="color:#FFD93D;">HEADWAY</th>
</tr>
</thead>
<tbody>"""

    for label, fbs_v, fbs_w, hw_v, hw_w in rows:
        fbs_cls = "cmp-td cmp-td-fbs" + (" cmp-win-fbs" if fbs_w and not hw_w else "")
        hw_cls  = "cmp-td cmp-td-hw"  + (" cmp-win-hw"  if hw_w and not fbs_w else "")
        html += f"""
<tr>
<td class="cmp-td cmp-td-lbl">{label}</td>
<td class="{fbs_cls}">{fbs_v} {'&#9670;' if fbs_w and not hw_w else ''}</td>
<td class="{hw_cls}">{hw_v} {'&#9670;' if hw_w and not fbs_w else ''}</td>
</tr>"""

    html += "</tbody></table>"
    html += '<div style="font-family:\'Share Tech Mono\',monospace;font-size:.46rem;color:#1A2D3A;margin-top:.3rem;">&#9670; = Unggul di kategori ini</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_scores():
    score_data = {
        "FBS": {
            "color": "#4FC3F7",
            "items": [
                ("Regulasi",     95),
                ("Biaya Trading",70),
                ("Platform",     85),
                ("Kemudahan",    88),
                ("Support",      82),
                ("Kepercayaan",  92),
            ]
        },
        "HEADWAY": {
            "color": "#FFD93D",
            "items": [
                ("Regulasi",     60),
                ("Biaya Trading",85),
                ("Platform",     80),
                ("Kemudahan",    88),
                ("Support",      75),
                ("Kepercayaan",  70),
            ]
        },
    }
    cols = st.columns(2)
    for col, (name, data) in zip(cols, score_data.items()):
        with col:
            c = data["color"]
            html = f'<div style="background:#090F18;border:1px solid #141E2D;border-radius:2px;padding:.7rem .85rem;">'
            html += f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:.62rem;font-weight:700;color:{c};letter-spacing:.1em;margin-bottom:.5rem;">{name}</div>'
            for lbl, val in data["items"]:
                html += f"""
<div class="score-row">
<span class="score-lbl">{lbl}</span>
<div class="score-bg"><div class="score-fg" style="width:{val}%;background:{c};"></div></div>
<span class="score-val" style="color:{c};">{val}</span>
</div>"""
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)

def render_guide():
    guides = [
        {
            "title": "PILIH FBS JIKA...",
            "color": "#4FC3F7",
            "items": [
                "Kamu prioritaskan regulasi ketat (CySEC, ASIC, FSC)",
                "Trading forex major dengan broker berpengalaman 15+ tahun",
                "Butuh akses ke 550+ instrumen dengan MT4/MT5 penuh",
                "Ingin mulai dengan akun Cent ($1) tapi broker tier-1",
                "Leverage tinggi 1:3000 dengan perlindungan saldo negatif",
            ],
        },
        {
            "title": "PILIH HEADWAY JIKA...",
            "color": "#FFD93D",
            "items": [
                "Kamu tertarik dengan Copy Trading & Social Trading",
                "Ingin leverage unlimited untuk strategi tertentu",
                "Butuh spread ketat 0.0 pips di akun Pro",
                "Mau manfaatkan bonus $150 tanpa deposit",
                "Trading crypto, saham, dan indeks dengan spread kompetitif",
            ],
        },
    ]
    cols = st.columns(2)
    for col, g in zip(cols, guides):
        with col:
            items = "".join(
                f'<div style="display:flex;gap:.4rem;margin:.2rem 0;font-size:.67rem;color:#3A5060;line-height:1.5;">'
                f'<span style="color:{g["color"]};flex-shrink:0;">&#9658;</span>{item}</div>'
                for item in g["items"]
            )
            st.markdown(f"""
<div style="background:#090F18;border:1px solid #141E2D;
    border-top:1px solid {g['color']}40;border-radius:2px;padding:.7rem .85rem;">
<div style="font-family:'Share Tech Mono',monospace;font-size:.6rem;font-weight:700;
    color:{g['color']};letter-spacing:.1em;margin-bottom:.4rem;">{g['title']}</div>
{items}
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    inject_css()

    # ── PAGE HEADER ──────────────────────────────────────────────────────────
    st.markdown("""
<div style="padding:.3rem 0 .5rem;">
<div class="pg-build">AEROVULPIS · PROTOTYPE · PARTNER BROKER MODULE · BUILD STABLE 02 SEP 2026</div>
<div class="pg-title">PARTNER BROKER</div>
<div class="pg-sub">PILIH BROKER RESMI UNTUK TRADING ANDA · TERVERIFIKASI AEROVULPIS</div>
</div>
<hr class="hr">""", unsafe_allow_html=True)

    # ── NOTICE ───────────────────────────────────────────────────────────────
    st.markdown("""
<div class="notice">
<div class="notice-t">&#9670; CATATAN PENTING — PEMILIHAN JENIS ASET</div>
<div class="notice-b">
Aerovulpis merekomendasikan broker di bawah sebagai partner IB resmi.
Kami mengimbau seluruh pengguna untuk <b style="color:#FFD93D;">menghindari produk Synthetic Indices</b>
— pergerakan harga buatan sistem komputer internal broker, bukan pasar riil.
Bertransaksilah hanya pada aset konvensional: <b style="color:#00FFC8;">Forex (mata uang dunia)</b>
dan <b style="color:#00FFC8;">Komoditas (XAU/USD)</b> dengan fitur <b style="color:#00FFC8;">Swap-Free</b> aktif.
</div>
</div>""", unsafe_allow_html=True)

    # ── TABS ────────────────────────────────────────────────────────────────
    tabs = st.tabs(["SEMUA BROKER", "PERBANDINGAN", "PANDUAN PILIH"])

    # TAB 1: SEMUA BROKER ────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown('<div class="sec-title">BROKER PARTNER RESMI</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">2 BROKER TERVERIFIKASI · LINK IB RESMI AEROVULPIS</div>', unsafe_allow_html=True)

        for b in BROKERS:
            render_broker_card(b)

    # TAB 2: PERBANDINGAN ────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown('<div class="sec-title">PERBANDINGAN LANGSUNG</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">FBS VS HEADWAY — SEMUA KATEGORI</div>', unsafe_allow_html=True)
        render_comparison()

        st.markdown('<hr class="hr">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">SKOR PER KATEGORI</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">PENILAIAN OBJEKTIF AEROVULPIS (0–100)</div>', unsafe_allow_html=True)
        render_scores()

    # TAB 3: PANDUAN PILIH ───────────────────────────────────────────────────
    with tabs[2]:
        st.markdown('<div class="sec-title">PANDUAN MEMILIH BROKER</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">REKOMENDASI BERDASARKAN PROFIL TRADER</div>', unsafe_allow_html=True)
        render_guide()

        st.markdown('<hr class="hr">', unsafe_allow_html=True)
        st.markdown("""
<div style="background:#090F18;border:1px solid #141E2D;border-left:2px solid #C77DFF;
    border-radius:0 2px 2px 0;padding:.65rem .85rem;">
<div style="font-family:'Share Tech Mono',monospace;font-size:.52rem;color:#C77DFF;
    letter-spacing:.13em;margin-bottom:.3rem;">TIPS KEAMANAN AKUN</div>
<div style="font-size:.7rem;color:#3A5060;line-height:1.7;">
<b style="color:#00FFC8;">1. Verifikasi KYC</b> — Lengkapi verifikasi identitas segera setelah daftar. Akun terverifikasi lebih aman dan proses withdrawal lebih cepat.<br>
<b style="color:#00FFC8;">2. Aktifkan 2FA</b> — Gunakan Google Authenticator atau SMS OTP untuk keamanan login.<br>
<b style="color:#00FFC8;">3. Metode Withdrawal Sama</b> — Gunakan metode pembayaran yang sama antara deposit dan withdrawal.<br>
<b style="color:#FFD93D;">4. Jangan Percaya Sinyal Berbayar</b> — Aerovulpis tidak menjual sinyal. Waspada akun palsu yang mengatasnamakan kami.<br>
<b style="color:#FF6B6B;">5. Manajemen Risiko</b> — Jangan pernah trading dengan uang yang tidak bisa Anda relakan kehilangannya.
</div>
</div>""", unsafe_allow_html=True)

    # ── DISCLAIMER ──────────────────────────────────────────────────────────
    st.markdown("""
<div class="disclaimer">
Broker di atas adalah partner resmi Aerovulpis. Penggunaan link di atas berarti Anda mendaftar melalui afiliasi IB Aerovulpis.
Trading forex dan CFD melibatkan risiko kerugian yang signifikan dan tidak cocok untuk semua investor.
Pastikan Anda memahami risiko yang terlibat sebelum trading. Kinerja masa lalu tidak menjamin hasil di masa depan.
Aerovulpis tidak bertanggung jawab atas keputusan trading yang Anda ambil.
</div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()