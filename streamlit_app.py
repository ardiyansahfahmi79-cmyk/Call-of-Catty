"""
STREAMLIT APP — Aerovulpis v4.1 (Our Journey Standalone)
Ditaruh langsung sebagai streamlit_app.py di GitHub
"""

import streamlit as st

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Share+Tech+Mono&family=Inter:wght@300;400;500;600&display=swap');

/* ── SCANLINE overlay ── */
.oj-wrap::before {
    content:'';
    position:fixed; inset:0; pointer-events:none; z-index:0;
    background:repeating-linear-gradient(
        0deg,
        rgba(0,212,255,0.012) 0px,
        rgba(0,212,255,0.012) 1px,
        transparent 1px,
        transparent 3px
    );
}

/* ── HERO ── */
.oj-hero {
    text-align:center;
    padding: 2.5rem 1rem 1.5rem;
    position:relative;
}
.oj-hero-label {
    font-family:'Share Tech Mono',monospace;
    font-size:.65rem; letter-spacing:5px; text-transform:uppercase;
    color:rgba(0,212,255,.45); margin-bottom:.6rem;
}
.oj-hero h1 {
    font-family:'Orbitron',sans-serif;
    font-size:clamp(2rem,7vw,3.4rem);
    font-weight:900; letter-spacing:6px;
    background:linear-gradient(120deg,#ffffff 15%,#00d4ff 50%,#00ff88 85%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text; line-height:1.1; margin-bottom:.5rem;
}
.oj-hero-sub {
    font-family:'Share Tech Mono',monospace;
    font-size:.78rem; color:rgba(136,153,187,.7); letter-spacing:2px;
}
.oj-hero-line {
    height:1px; max-width:500px; margin:1.2rem auto 0;
    background:linear-gradient(90deg,transparent,#00d4ff 40%,#00ff88 60%,transparent);
    opacity:.35;
}

/* ── SECTION TITLE ── */
.oj-sec-title {
    font-family:'Orbitron',sans-serif;
    font-size:.8rem; font-weight:700; letter-spacing:4px;
    text-transform:uppercase; color:#00d4ff;
    display:flex; align-items:center; gap:.7rem;
    margin-bottom:1.2rem;
}
.oj-sec-title::before {
    content:''; width:30px; height:1px; background:#00d4ff; opacity:.5;
}
.oj-sec-title::after {
    content:''; flex:1; height:1px; background:rgba(0,212,255,.15);
}

/* ── STATUS BADGE ── */
.oj-status-bar {
    display:flex; align-items:center; justify-content:center;
    gap:1.5rem; flex-wrap:wrap;
    padding:.6rem 1rem;
    background:rgba(0,212,255,.03);
    border:1px solid rgba(0,212,255,.1);
    border-radius:5px; margin:1rem 0 2rem;
    font-family:'Share Tech Mono',monospace;
    font-size:.62rem; letter-spacing:2px; text-transform:uppercase;
}
.oj-live-dot {
    width:7px; height:7px; border-radius:50%;
    background:#00ff88; box-shadow:0 0 10px #00ff88;
    animation:oj-pulse 2s ease-in-out infinite;
    flex-shrink:0;
}
@keyframes oj-pulse {
    0%,100%{opacity:1;box-shadow:0 0 8px #00ff88;}
    50%{opacity:.4;box-shadow:0 0 18px #00ff88;}
}
.oj-stat-item { color:rgba(136,153,187,.7); }
.oj-stat-item span { color:#00d4ff; font-weight:600; }

/* ── FOUNDER CARD ── */
.oj-founder-card {
    background:linear-gradient(160deg, #080f1c 0%, #050b16 100%);
    border:1px solid rgba(0,212,255,.2);
    border-radius:10px; padding:2rem 1.8rem;
    position:relative; overflow:hidden;
    margin-bottom:1.5rem;
}
.oj-founder-card::before {
    content:'';
    position:absolute; top:0; left:0;
    width:4px; height:100%;
    background:linear-gradient(180deg,#00d4ff,#00ff88);
    border-radius:10px 0 0 10px;
}
.oj-founder-card::after {
    content:'FOUNDER';
    position:absolute; top:1.2rem; right:1.4rem;
    font-family:'Orbitron',sans-serif; font-size:.52rem;
    letter-spacing:3px; color:rgba(0,212,255,.25);
    font-weight:700;
}
.oj-founder-top {
    display:flex; align-items:flex-start; gap:1.2rem;
    margin-bottom:1.2rem;
}
.oj-avatar {
    width:56px; height:56px; border-radius:50%; flex-shrink:0;
    background:linear-gradient(135deg,#00d4ff22,#00ff8822);
    border:1.5px solid rgba(0,212,255,.4);
    display:flex; align-items:center; justify-content:center;
    font-family:'Orbitron',sans-serif; font-size:1.3rem;
    color:#00d4ff; box-shadow:0 0 16px rgba(0,212,255,.2);
}
.oj-founder-name {
    font-family:'Orbitron',sans-serif;
    font-size:1.15rem; font-weight:700;
    color:#e8f4ff; letter-spacing:2px; margin-bottom:.2rem;
}
.oj-founder-role {
    font-family:'Share Tech Mono',monospace;
    font-size:.7rem; color:#00d4ff; letter-spacing:1.5px;
    margin-bottom:.15rem;
}
.oj-founder-org {
    font-family:'Share Tech Mono',monospace;
    font-size:.62rem; color:rgba(136,153,187,.6); letter-spacing:1px;
}
.oj-founder-bio {
    font-family:'Inter',sans-serif;
    font-size:.86rem; color:rgba(180,200,220,.8);
    line-height:1.78; margin-bottom:1.1rem;
}
.oj-founder-bio strong { color:#00d4ff; font-weight:600; }

/* ── MISI BOX ── */
.oj-mission-box {
    background:rgba(0,255,136,.04);
    border:1px solid rgba(0,255,136,.15);
    border-radius:6px; padding:1.1rem 1.3rem;
    margin-top:.9rem;
}
.oj-mission-label {
    font-family:'Orbitron',sans-serif; font-size:.58rem;
    letter-spacing:3px; text-transform:uppercase;
    color:#00ff88; margin-bottom:.5rem; font-weight:700;
}
.oj-mission-text {
    font-family:'Inter',sans-serif; font-size:.83rem;
    color:rgba(160,220,180,.8); line-height:1.7; font-style:italic;
}

/* ── DEVELOPMENT STATUS ── */
.oj-dev-card {
    background:linear-gradient(160deg,#06101f,#040c18);
    border:1px solid rgba(255,170,0,.18);
    border-radius:10px; padding:1.6rem 1.8rem;
    margin-bottom:1.5rem; position:relative; overflow:hidden;
}
.oj-dev-card::before {
    content:'';
    position:absolute; top:0; left:0;
    width:4px; height:100%; background:var(--warn,#e8b000);
}
.oj-dev-badge {
    display:inline-flex; align-items:center; gap:.4rem;
    background:rgba(255,170,0,.08); border:1px solid rgba(255,170,0,.25);
    border-radius:3px; padding:.2rem .6rem;
    font-family:'Share Tech Mono',monospace; font-size:.58rem;
    letter-spacing:2px; color:#e8b000; margin-bottom:.9rem;
}
.oj-dev-badge-dot {
    width:5px; height:5px; border-radius:50%;
    background:#e8b000; box-shadow:0 0 8px #e8b000;
    animation:oj-pulse-warn 2s infinite;
}
@keyframes oj-pulse-warn {
    0%,100%{opacity:1;} 50%{opacity:.35;}
}
.oj-dev-text {
    font-family:'Inter',sans-serif; font-size:.85rem;
    color:rgba(180,195,215,.8); line-height:1.76;
}
.oj-dev-text strong { color:#e8b000; }
.oj-progress-wrap {
    margin-top:1.1rem;
}
.oj-progress-row {
    display:flex; align-items:center; gap:.8rem;
    margin-bottom:.5rem;
}
.oj-progress-label {
    font-family:'Share Tech Mono',monospace; font-size:.6rem;
    letter-spacing:1.5px; color:rgba(136,153,187,.6);
    width:130px; flex-shrink:0;
}
.oj-progress-bar {
    flex:1; height:4px; background:rgba(255,255,255,.05);
    border-radius:4px; overflow:hidden;
}
.oj-progress-fill {
    height:100%; border-radius:4px;
    background:linear-gradient(90deg,#00d4ff,#00ff88);
}
.oj-progress-pct {
    font-family:'Share Tech Mono',monospace; font-size:.58rem;
    color:#00d4ff; width:32px; text-align:right; flex-shrink:0;
}

/* ── SOCMED CARD ── */
.oj-socmed-grid {
    display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:1.5rem;
}
.oj-socmed-card {
    flex:1; min-width:220px;
    background:linear-gradient(160deg,#070e1c,#040a14);
    border-radius:8px; padding:1.3rem 1.4rem;
    position:relative; overflow:hidden;
    text-decoration:none; display:block;
    transition:transform .2s, box-shadow .2s, border-color .2s;
}
.oj-socmed-card.timnews {
    border:1px solid rgba(0,212,255,.2);
}
.oj-socmed-card.dynamihatch {
    border:1px solid rgba(0,255,136,.2);
}
.oj-socmed-card:hover {
    transform:translateY(-3px);
}
.oj-socmed-card.timnews:hover {
    border-color:rgba(0,212,255,.5);
    box-shadow:0 8px 28px rgba(0,212,255,.1);
}
.oj-socmed-card.dynamihatch:hover {
    border-color:rgba(0,255,136,.5);
    box-shadow:0 8px 28px rgba(0,255,136,.1);
}
.oj-socmed-platform {
    font-family:'Orbitron',sans-serif; font-size:.52rem;
    letter-spacing:3px; text-transform:uppercase;
    margin-bottom:.5rem; font-weight:700;
}
.timnews .oj-socmed-platform { color:rgba(0,212,255,.5); }
.dynamihatch .oj-socmed-platform { color:rgba(0,255,136,.5); }
.oj-socmed-name {
    font-family:'Orbitron',sans-serif; font-size:.9rem;
    font-weight:700; letter-spacing:1.5px; margin-bottom:.25rem;
}
.timnews .oj-socmed-name { color:#00d4ff; }
.dynamihatch .oj-socmed-name { color:#00ff88; }
.oj-socmed-desc {
    font-family:'Share Tech Mono',monospace; font-size:.62rem;
    letter-spacing:1px; margin-bottom:.9rem;
}
.timnews .oj-socmed-desc { color:rgba(0,212,255,.5); }
.dynamihatch .oj-socmed-desc { color:rgba(0,255,136,.5); }
.oj-socmed-btn {
    display:inline-flex; align-items:center; gap:.4rem;
    font-family:'Share Tech Mono',monospace; font-size:.62rem;
    letter-spacing:2px; text-transform:uppercase;
    padding:.3rem .75rem; border-radius:3px;
    text-decoration:none; font-weight:600;
    transition:all .18s;
}
.timnews .oj-socmed-btn {
    background:rgba(0,212,255,.1); color:#00d4ff;
    border:1px solid rgba(0,212,255,.3);
}
.timnews .oj-socmed-btn:hover {
    background:rgba(0,212,255,.2);
}
.dynamihatch .oj-socmed-btn {
    background:rgba(0,255,136,.08); color:#00ff88;
    border:1px solid rgba(0,255,136,.25);
}
.dynamihatch .oj-socmed-btn:hover {
    background:rgba(0,255,136,.16);
}
.oj-tiktok-icon {
    font-size:.75rem;
}

/* ── QUOTE BOX ── */
.oj-quote {
    background:linear-gradient(135deg,rgba(0,212,255,.04),rgba(0,255,136,.03));
    border:1px solid rgba(0,212,255,.12);
    border-left:4px solid #00d4ff;
    border-radius:0 8px 8px 0;
    padding:1.4rem 1.6rem; margin:1.5rem 0;
}
.oj-quote-text {
    font-family:'Share Tech Mono',monospace;
    font-size:.85rem; color:rgba(180,205,230,.85); line-height:1.8;
    margin-bottom:.7rem;
}
.oj-quote-sig {
    font-family:'Orbitron',sans-serif; font-size:.6rem;
    letter-spacing:2px; color:rgba(0,212,255,.5); text-align:right;
}

/* ── FOOTER ── */
.oj-footer {
    text-align:center; padding:1.5rem 1rem 1rem;
    border-top:1px solid rgba(0,212,255,.08);
    margin-top:2rem;
}
.oj-footer-brand {
    font-family:'Orbitron',sans-serif; font-size:.75rem;
    letter-spacing:3px; color:#00d4ff; font-weight:700;
    margin-bottom:.3rem;
}
.oj-footer-sub {
    font-family:'Share Tech Mono',monospace; font-size:.58rem;
    color:rgba(136,153,187,.35); letter-spacing:1.5px;
}
</style>
""", unsafe_allow_html=True)

# ── HERO ──
st.markdown("""
<div class="oj-wrap">
  <div class="oj-hero">
    <div class="oj-hero-label">// Aerovulpis · DynamiHatch · 2026</div>
    <h1>OUR JOURNEY</h1>
    <div class="oj-hero-sub">Membangun Terminal Intelijen Pasar untuk Indonesia</div>
    <div class="oj-hero-line"></div>
  </div>

  <div class="oj-status-bar">
    <div class="oj-live-dot"></div>
    <div class="oj-stat-item">STATUS: <span>AKTIF DIKEMBANGKAN</span></div>
    <div class="oj-stat-item">|</div>
    <div class="oj-stat-item">VERSI: <span>v4.1 ULTIMATE</span></div>
    <div class="oj-stat-item">|</div>
    <div class="oj-stat-item">PLATFORM: <span>AEROVULPIS.MY.ID</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── FOUNDER ──
st.markdown('<div class="oj-sec-title">Founder & Visioner</div>',
            unsafe_allow_html=True)

st.markdown("""
<div class="oj-founder-card">
  <div class="oj-founder-top">
    <div class="oj-avatar">F</div>
    <div>
      <div class="oj-founder-name">FAHMI</div>
      <div class="oj-founder-role">CEO &amp; Founder</div>
      <div class="oj-founder-org">DynamiHatch Technology &nbsp;·&nbsp; Aerovulpis</div>
    </div>
  </div>

  <div class="oj-founder-bio">
    <strong>Fahmi</strong> adalah inisiator di balik lahirnya Aerovulpis — sebuah terminal
    intelijen pasar yang dirancang khusus untuk trader Indonesia. Berangkat dari keyakinan
    bahwa <strong>setiap trader Indonesia berhak mendapatkan akses ke analisis berkualitas
    institusional</strong>, ia membangun ekosistem ini dari nol bersama tim DynamiHatch.
    <br><br>
    Melalui <strong>DynamiHatch Technology</strong>, visi ini diwujudkan dalam bentuk
    platform yang terus berkembang — menggabungkan kecerdasan buatan, data pasar real-time,
    dan edukasi trading dalam satu ekosistem yang terintegrasi. Setiap fitur yang hadir
    adalah cerminan dari komitmen untuk menciptakan standar trading yang lebih sehat,
    lebih cerdas, dan lebih independen di Indonesia.
  </div>

  <div class="oj-mission-box">
    <div class="oj-mission-label">Misi Utama</div>
    <div class="oj-mission-text">
      "Mendemokratisasi akses ke intelijen pasar kelas dunia — agar setiap trader Indonesia,
      dari pemula hingga profesional, dapat mengambil keputusan yang lebih terinformasi,
      lebih terukur, dan lebih percaya diri."
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── STATUS PENGEMBANGAN ──
st.markdown('<div class="oj-sec-title">Status Pengembangan</div>',
            unsafe_allow_html=True)

st.markdown("""
<div class="oj-dev-card">
  <div class="oj-dev-badge">
    <div class="oj-dev-badge-dot"></div>
    PLATFORM AKTIF DIKEMBANGKAN
  </div>
  <div class="oj-dev-text">
    Aerovulpis saat ini berada dalam fase pengembangan aktif. Website berjalan di
    <strong>aerovulpis.my.id</strong> dan terus diperbarui secara berkala.
    Setiap pembaruan membawa fitur baru, peningkatan performa, dan penyempurnaan
    pengalaman pengguna berdasarkan masukan komunitas trader Indonesia.
    <br><br>
    Kami percaya bahwa <strong>transparansi adalah fondasi kepercayaan</strong>.
    Oleh karena itu, perjalanan pengembangan ini kami jalani bersama komunitas —
    terbuka, iteratif, dan berorientasi pada kebutuhan nyata trader di lapangan.
  </div>

  <div class="oj-progress-wrap">
    <div class="oj-progress-row">
      <div class="oj-progress-label">AI Trade Analysis</div>
      <div class="oj-progress-bar">
        <div class="oj-progress-fill" style="width:85%"></div>
      </div>
      <div class="oj-progress-pct">85%</div>
    </div>
    <div class="oj-progress-row">
      <div class="oj-progress-label">Market Intelligence</div>
      <div class="oj-progress-bar">
        <div class="oj-progress-fill" style="width:78%"></div>
      </div>
      <div class="oj-progress-pct">78%</div>
    </div>
    <div class="oj-progress-row">
      <div class="oj-progress-label">Economic Radar</div>
      <div class="oj-progress-bar">
        <div class="oj-progress-fill" style="width:70%"></div>
      </div>
      <div class="oj-progress-pct">70%</div>
    </div>
    <div class="oj-progress-row">
      <div class="oj-progress-label">Aero Academy</div>
      <div class="oj-progress-bar">
        <div class="oj-progress-fill" style="width:60%"></div>
      </div>
      <div class="oj-progress-pct">60%</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── QUOTE ──
st.markdown("""
<div class="oj-quote">
  <div class="oj-quote-text">
    "Sebuah inovasi besar tidak lahir dalam semalam. AeroVulpis masih terus berbenah
    dan membutuhkan dukungan penuh dari komunitas trader domestik demi mencapai performa
    terbaiknya. Mari bersama-sama memberikan dukungan, memperbaiki kekurangan yang ada,
    dan berkembang bersama untuk menciptakan standar trading yang lebih sehat di Indonesia."
  </div>
  <div class="oj-quote-sig">&mdash; Fahmi · Founder, Aerovulpis &amp; DynamiHatch</div>
</div>
""", unsafe_allow_html=True)

# ── IKUTI KAMI ──
st.markdown('<div class="oj-sec-title">Ikuti Perjalanan Kami</div>',
            unsafe_allow_html=True)

st.markdown("""
<div class="oj-socmed-grid">

  <a class="oj-socmed-card timnews"
     href="https://vm.tiktok.com/ZS9hRjU5FKjcM-Gh63T/"
     target="_blank" rel="noopener noreferrer">
    <div class="oj-socmed-platform">TikTok</div>
    <div class="oj-socmed-name">T.I.M NEWS</div>
    <div class="oj-socmed-desc">Terminal Intelijen Pasar · Berita &amp; Analisis</div>
    <a class="oj-socmed-btn" href="https://vm.tiktok.com/ZS9hRjU5FKjcM-Gh63T/"
       target="_blank" rel="noopener noreferrer">
      <span class="oj-tiktok-icon">&#9654;</span> Buka TikTok
    </a>
  </a>

  <a class="oj-socmed-card dynamihatch"
     href="https://vm.tiktok.com/ZS9hRjbGvmAtc-keGWq/"
     target="_blank" rel="noopener noreferrer">
    <div class="oj-socmed-platform">TikTok</div>
    <div class="oj-socmed-name">DynamiHatch</div>
    <div class="oj-socmed-desc">Technology · Inovasi Digital Indonesia</div>
    <a class="oj-socmed-btn" href="https://vm.tiktok.com/ZS9hRjbGvmAtc-keGWq/"
       target="_blank" rel="noopener noreferrer">
      <span class="oj-tiktok-icon">&#9654;</span> Buka TikTok
    </a>
  </a>

</div>
""", unsafe_allow_html=True)

# ── CLOSING ──
st.markdown("""
<div class="oj-footer">
  <div class="oj-footer-brand">AEROVULPIS</div>
  <div class="oj-footer-sub">
    Dikembangkan oleh DynamiHatch Technology &nbsp;·&nbsp;
    aerovulpis.my.id &nbsp;·&nbsp; 2026
  </div>
</div>
""", unsafe_allow_html=True)
