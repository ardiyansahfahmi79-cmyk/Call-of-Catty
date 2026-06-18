# ==============================================================================
# sentinel_page.py - Halaman AeroVulpis Sentinel (terpisah)
# ==============================================================================
# HANYA LOGIKA TAMPILAN 3 KOLOM ATAS YANG DIUBAH AGAR BISA SCROLL HORIZONTAL.
# LOGIKA AI FEED, PROMPT, DAN ACTIVE SETUPS TETAP ASLI.
# ==============================================================================

import streamlit as st
import streamlit.components.v1 as components
# ==============================================================================
# PAGE CONFIG (hanya untuk keperluan jika dibuka langsung)
# ==============================================================================
if __name__ == "__main__":
    st.set_page_config(
        page_title="Aerovulpis Pro Terminal",
        page_icon="🔷",
        layout="wide"
    )

def show():
    """
    Fungsi utama untuk menampilkan halaman Sentinel.
    Semua fungsi pendukung diharapkan sudah tersedia di namespace global (dari streamlit_app.py).
    """

    # --- INISIALISASI SESSION STATE UNTUK SENTINEL ---
    if "sentinel_ai_output" not in st.session_state:
        st.session_state.sentinel_ai_output = None
    if "sentinel_chart_pair" not in st.session_state:
        st.session_state.sentinel_chart_pair = "XAUUSD"
    if "sentinel_analysis_mode" not in st.session_state:
        st.session_state.sentinel_analysis_mode = "pair"

    # ==========================================================================
    # TAMPILAN & HEADER
    # ==========================================================================
    st.markdown("""
    <div style="height: 44px; display: flex; align-items: center; justify-content: space-between; padding: 0 10px; background: rgba(7,12,24,0.97); border-bottom: 1px solid #162035;">
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="width: 24px; height: 24px; background: linear-gradient(135deg, #00EEFF, #8B5CF6); border-radius: 4px; display: flex; align-items: center; justify-content: center; font-family: 'Share Tech Mono', monospace; font-size: 9px; font-weight: 700; color: #fff;">AV</div>
            <div style="font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #00EEFF; letter-spacing: 1px;">AEROVULPIS PRO</div>
        </div>
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="font-family: 'Share Tech Mono', monospace; font-size: 7px; color: #00EEFF; background: rgba(0,238,255,0.10); border: 1px solid rgba(0,238,255,0.22); padding: 2px 6px; border-radius: 3px; letter-spacing: 1px;">LONDON/NY</div>
        </div>
    </div>
    <div style="text-align: center; padding: 6px 0; border-bottom: 1px solid rgba(0,238,255,0.15); margin-bottom: 4px;">
        <span style="font-family: 'Share Tech Mono', monospace; font-size: 14px; color: #00EEFF; letter-spacing: 4px; text-shadow: 0 0 20px rgba(0,238,255,0.3);">[ AEROVULPIS SENTINEL NEXUS ]</span>
    </div>
    """, unsafe_allow_html=True)

    # --- TICKER TAPE ---
    ticker_html = """
    <div class="tradingview-widget-container" style="height: 55px; overflow: hidden;">
        <div class="tradingview-widget-container__widget"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
        {
        "symbols": [{"proName": "FOREXCOM:SPXUSD", "title": "S&P 500"}, {"proName": "FX_IDC:EURUSD", "title": "EUR/USD"}, {"proName": "BITSTAMP:BTCUSD", "title": "Bitcoin"}, {"proName": "OANDA:XAUUSD", "title": "XAUUSD"}],
        "colorTheme": "dark", "isTransparent": true, "locale": "id", "width": "100%", "height": 55
        }
        </script>
    </div>
    """
    st.components.v1.html(ticker_html, height=55)

    # ==========================================================================
    # CUSTOM CSS AGAR 3 KOLOM UTAMA BISA DI-SCROLL KANAN KIRI
    # ==========================================================================
    st.markdown("""
    <style>
    /* Target blok kolom yang berisi kalender ekonomi Tradays */
    div[data-testid="stHorizontalBlock"]:has(iframe[src*="tradays.com"]) {
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        gap: 16px !important;
        padding-bottom: 15px;
    }
    /* Set ukuran minimum per kolom agar tidak gepeng saat di-scroll */
    div[data-testid="stHorizontalBlock"]:has(iframe[src*="tradays.com"]) > div[data-testid="column"] {
        min-width: 440px !important;
        flex: 1 0 440px !important;
    }
    /* Style Scrollbar agar senada dengan tema cyberpunk dark */
    div[data-testid="stHorizontalBlock"]:has(iframe[src*="tradays.com"])::-webkit-scrollbar {
        height: 7px;
    }
    div[data-testid="stHorizontalBlock"]:has(iframe[src*="tradays.com"])::-webkit-scrollbar-track {
        background: #0C1425;
        border-radius: 4px;
    }
    div[data-testid="stHorizontalBlock"]:has(iframe[src*="tradays.com"])::-webkit-scrollbar-thumb {
        background: #162035;
        border-radius: 4px;
        border: 1px solid rgba(0,238,255,0.1);
    }
    div[data-testid="stHorizontalBlock"]:has(iframe[src*="tradays.com"])::-webkit-scrollbar-thumb:hover {
        background: #00EEFF;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 3 KOLOM UTAMA (KIRI: CALENDAR, TENGAH: CHART, KANAN: HEATMAP) ---
    col1, col2, col3 = st.columns(3)

    # KOLOM 1: ECONOMIC CALENDAR (DI KIRI)
    with col1:
        eco_html = """
        <style>
        .cyber-panel-native {
            background: #0C1425; border: 1px solid #162035; border-radius: 8px;
            display: flex; flex-direction: column; height: 100%; box-sizing: border-box;
        }
        .panel-header {
            background: rgba(0,0,0,0.28); border-bottom: 1px solid #162035;
            padding: 6px 10px; display: flex; justify-content: space-between; align-items: center;
        }
        .panel-title { font-family: 'Share Tech Mono', monospace; font-size: 11px; color: #00EEFF; letter-spacing: 2px; text-transform: uppercase; }
        .panel-badge { font-family: monospace; font-size: 9px; color: #4B6A8A; letter-spacing: 1px; text-transform: uppercase; }
        .panel-body { flex: 1; min-height: 0; overflow: hidden; }
        </style>
        <div class="cyber-panel-native">
            <div class="panel-header">
                <span class="panel-title">Economic Calendar</span>
                <span class="panel-badge">Tradays</span>
            </div>
            <div class="panel-body">
                <iframe src="https://www.tradays.com/en/economic-calendar/widget?mode=2&colorTheme=dark" style="width:100%; height:100%; border:none; background:#0C1425;" frameborder="0" scrolling="auto"></iframe>
            </div>
        </div>
        """
        st.components.v1.html(eco_html, height=620)

    # KOLOM 2: TRADINGVIEW CHART (DI TENGAH)
    with col2:
        pair_options = ["XAUUSD", "BTCUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USOIL"]
        selected_pair = st.selectbox("", pair_options, index=pair_options.index(st.session_state.sentinel_chart_pair) if st.session_state.sentinel_chart_pair in pair_options else 0, key="sentinel_chart_pair_select", label_visibility="collapsed")
        if selected_pair != st.session_state.sentinel_chart_pair:
            st.session_state.sentinel_chart_pair = selected_pair

        symbol_map = {"XAUUSD": "OANDA:XAUUSD", "BTCUSD": "BITSTAMP:BTCUSD", "EURUSD": "FX_IDC:EURUSD", "GBPUSD": "FX_IDC:GBPUSD", "USDJPY": "FX_IDC:USDJPY", "AUDUSD": "FX_IDC:AUDUSD", "USOIL": "TVC:USOIL"}
        tv_symbol = symbol_map.get(selected_pair, "OANDA:XAUUSD")

        chart_html = f"""
        <style>
        .cyber-panel-native {
            background: #0C1425; border: 1px solid #162035; border-radius: 8px;
            display: flex; flex-direction: column; height: 100%; box-sizing: border-box;
        }
        .panel-header {
            background: rgba(0,0,0,0.28); border-bottom: 1px solid #162035;
            padding: 6px 10px; display: flex; justify-content: space-between; align-items: center;
        }
        .panel-title { font-family: 'Share Tech Mono', monospace; font-size: 11px; color: #00EEFF; letter-spacing: 2px; text-transform: uppercase; }
        .panel-badge { font-family: monospace; font-size: 9px; color: #4B6A8A; letter-spacing: 1px; text-transform: uppercase; }
        .panel-body { flex: 1; min-height: 0; overflow: hidden; }
        </style>
        <div class="cyber-panel-native">
            <div class="panel-header">
                <span class="panel-title">{selected_pair} Premium Chart</span>
                <span class="panel-badge">Live</span>
            </div>
            <div class="panel-body" id="tv_chart_main"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({{
                "autosize": true, "symbol": "{tv_symbol}", "interval": "60", "timezone": "Asia/Jakarta",
                "theme": "dark", "style": "2", "locale": "id", "enable_publishing": false,
                "hide_top_toolbar": false, "hide_legend": false, "save_image": false,
                "container_id": "tv_chart_main", "studies": ["RSI@tv-basicstudies"],
                "backgroundColor": "rgba(12,20,37,1)", "gridColor": "rgba(0,238,255,0.05)"
            }});
            </script>
        </div>
        """
        st.components.v1.html(chart_html, height=584)

    # KOLOM 3: CURRENCY HEATMAP (DI KANAN)
    with col3:
        heatmap_html = """
        <style>
        .cyber-panel-native {
            background: #0C1425; border: 1px solid #162035; border-radius: 8px;
            display: flex; flex-direction: column; height: 100%; box-sizing: border-box;
        }
        .panel-header {
            background: rgba(0,0,0,0.28); border-bottom: 1px solid #162035;
            padding: 6px 10px; display: flex; justify-content: space-between; align-items: center;
        }
        .panel-title { font-family: 'Share Tech Mono', monospace; font-size: 11px; color: #00EEFF; letter-spacing: 2px; text-transform: uppercase; }
        .panel-badge { font-family: monospace; font-size: 9px; color: #4B6A8A; letter-spacing: 1px; text-transform: uppercase; }
        .panel-body { flex: 1; min-height: 0; overflow: hidden; }
        </style>
        <div class="cyber-panel-native">
            <div class="panel-header">
                <span class="panel-title">Currency Heatmap</span>
                <span class="panel-badge">Live</span>
            </div>
            <div class="panel-body">
                <div class="tradingview-widget-container" style="height: 100%;">
                    <div class="tradingview-widget-container__widget" style="height: 100%;"></div>
                    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-forex-heat-map.js" async>
                    {
                    "colorTheme": "dark", "isTransparent": true, "locale": "id",
                    "currencies": ["EUR","USD","JPY","GBP","CHF","AUD","CAD","NZD"],
                    "width": "100%", "height": "100%"
                    }
                    </script>
                </div>
            </div>
        </div>
        """
        st.components.v1.html(heatmap_html, height=620)

    # ==========================================================================
    # AI SIGNAL FEED & ANALYSIS TERMINAL (LOGIKA & PROMPT TIDAK DIUBAH)
    # ==========================================================================
    st.markdown("""
    <div style="background: #0C1425; border: 1px solid #162035; border-radius: 8px; margin-top: 20px; padding: 0 0 10px 0;">
        <div style="background: rgba(0,0,0,0.28); border-bottom: 1px solid #162035; padding: 8px 12px; display: flex; justify-content: space-between; align-items: center; border-radius: 8px 8px 0 0;">
            <span style="font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #00EEFF; letter-spacing: 2px; text-transform: uppercase;">AI Signal Feed & Analysis Terminal</span>
            <span style="font-family: monospace; font-size: 9px; color: #4B6A8A; letter-spacing: 1px;">CORE ENGINE V3.5</span>
        </div>
        <div style="padding: 12px 12px 2px 12px;">
            <div style="font-family:'Share Tech Mono',monospace; font-size:10px; color:#4B6A8A; background:rgba(0,238,255,0.05); border-left:2px solid #00EEFF; padding:8px; border-radius:3px; margin-bottom:10px;">
                [SYSTEM GENUINE] Pilih mode analisis, lalu ketik market pair atau topik fundamental untuk mengekstrak data.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Radio Pilihan Tipe Analisis
    analysis_type = st.radio(
        "Pilih Mode AI:",
        ["Analisis Pair (Teknikal/SMC)", "Analisis News (Fundamental)"],
        horizontal=True,
        label_visibility="collapsed",
        key="sentinel_analysis_type"
    )
    st.session_state.sentinel_analysis_mode = "pair" if "Pair" in analysis_type else "news"

    # Input dan tombol
    st.markdown('<div class="ai-input-container">', unsafe_allow_html=True)
    col_input, col_btn = st.columns([5, 1], gap="small")
    with col_input:
        user_input = st.text_input("", placeholder="Ketik di sini (contoh: XAUUSD atau Berita NFP)...", key="sentinel_ai_input", label_visibility="collapsed")
    with col_btn:
        send_clicked = st.button("▶ RUN ANALYSIS", key="sentinel_ai_send", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if send_clicked and user_input:
        user_limits = LIMITS.get(st.session_state.user_tier, LIMITS["free"])
        if user_limits["sentinel_per_day"] == 0:
            st.error("SENTINEL PRO ACCESS RESTRICTED | UPGRADE TIER")
        elif st.session_state.daily_sentinel_count >= user_limits["sentinel_per_day"]:
            st.error(f"LIMIT REACHED [{st.session_state.daily_sentinel_count}/{user_limits['sentinel_per_day']}] | UPGRADE TIER")
        else:
            pair_for_analysis = st.session_state.sentinel_chart_pair
            if st.session_state.sentinel_analysis_mode == "pair":
                ticker_map = {"XAUUSD": "GC=F", "BTCUSD": "BTC-USD", "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "USDJPY=X", "AUDUSD": "AUDUSD=X", "USOIL": "CL=F"}
                ticker = ticker_map.get(pair_for_analysis, "GC=F")
                market = get_market_data_with_cache(ticker, force_refresh=False)
                if market:
                    df = get_historical_data(ticker, period="1mo", interval="1h")
                    if not df.empty:
                        df = add_technical_indicators(df)
                        score, signal, reasons, bull, bear, neut = get_weighted_signal(df)
                        analysis = get_sentinel_analysis(pair_for_analysis, market, df, signal, reasons)
                        st.session_state.sentinel_ai_output = analysis
                    else:
                        st.error("Data historis tidak tersedia untuk pair ini.")
                else:
                    st.error("Gagal mengambil harga untuk pair ini.")
            else:
                analysis = get_news_analysis(pair_for_analysis, user_input)
                st.session_state.sentinel_ai_output = analysis

    if st.session_state.get("sentinel_ai_output"):
        st.markdown("---")
        st.markdown("### [OUTPUT ANALYSIS]")
        st.markdown(st.session_state.sentinel_ai_output, unsafe_allow_html=True)

    # ==========================================================================
    # ACTIVE TRADE SETUPS (LOGIKA TIDAK DIUBAH)
    # ==========================================================================
    from streamlit_app import get_active_trade_setups   
    setups = get_active_trade_setups()

    if setups:
        bottom_html = """<style>
        .cyber-tag { font-family: 'Share Tech Mono', monospace; font-size: 8px; letter-spacing: 1px; padding: 2px 6px; border-radius: 3px; display: inline-block; }
        .cyber-tag.buy { background: rgba(0,255,157,0.12); color: #00FF9D; border: 1px solid rgba(0,255,157,0.25); }
        .cyber-tag.sell { background: rgba(255,61,113,0.12); color: #FF3D71; border: 1px solid rgba(255,61,113,0.25); }
        .grid-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 10px; padding: 10px; }
        .setup-card { background: #111D35; border: 1px solid #162035; border-radius: 6px; padding: 12px; position: relative; }
        .tp-status { font-size: 10px; margin-left: 4px; }
        .tp-hit { color: #00FF9D; }
        .tp-miss { color: #FF3D71; }
        .tp-pending { color: #FFD700; }
        </style>
        <div style="background: #0C1425; border: 1px solid #162035; border-radius: 8px; margin-top: 15px;">
        <div style="background: rgba(0,0,0,0.28); border-bottom: 1px solid #162035; padding: 8px 12px;">
        <span style="font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #00EEFF; letter-spacing: 2px; text-transform: uppercase;">Active Trade Setups</span>
        </div>
        <div class="grid-container">"""

        for s in setups:
            dir_cls = "buy" if s["dir"] == "BUY" else "sell"
            gradient = "#00FF9D" if s["dir"] == "BUY" else "#FF3D71"
            tp1_status = "✓" if s["tp1_hit"] else "✗" if s["sl_hit"] else "~"
            tp2_status = "✓" if s["tp2_hit"] else "✗" if s["sl_hit"] else "~"
            tp3_status = "✓" if s["tp3_hit"] else "✗" if s["sl_hit"] else "~"
            tp1_class = "tp-hit" if s["tp1_hit"] else "tp-miss" if s["sl_hit"] else "tp-pending"
            tp2_class = "tp-hit" if s["tp2_hit"] else "tp-miss" if s["sl_hit"] else "tp-pending"
            tp3_class = "tp-hit" if s["tp3_hit"] else "tp-miss" if s["sl_hit"] else "tp-pending"

            bottom_html += f"""
            <div class="setup-card">
                <div style="position:absolute; top:0; left:0; right:0; height:2px; background:{gradient}; border-radius: 6px 6px 0 0;"></div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <span style="font-family:'Share Tech Mono',monospace; font-size:14px; font-weight:bold; color:#C8D8F0;">{s['pair']}</span>
                    <span class="cyber-tag {dir_cls}">{s['dir']}</span>
                </div>
                <div style="display:grid; grid-template-columns: repeat(5, 1fr); gap:6px; font-family:sans-serif; font-size:10px; text-align: left;">
                    <div><span style="color:#4B6A8A; font-size:9px;">SL</span><br><span style="color:#FF3D71; font-weight:bold;">{format_price_display(s['sl'], s['pair'])}</span></div>
                    <div><span style="color:#4B6A8A; font-size:9px;">ENTRY</span><br><span style="color:#00FF9D; font-weight:bold;">{format_price_display(s['entry'], s['pair'])}</span></div>
                    <div><span style="color:#4B6A8A; font-size:9px;">TP1</span><br><span style="color:#00FF9D; font-weight:bold;">{format_price_display(s['tp1'], s['pair'])}</span> <span class="tp-status {tp1_class}">{tp1_status}</span></div>
                    <div><span style="color:#4B6A8A; font-size:9px;">TP2</span><br><span style="color:#00FF9D; font-weight:bold;">{format_price_display(s['tp2'], s['pair'])}</span> <span class="tp-status {tp2_class}">{tp2_status}</span></div>
                    <div><span style="color:#4B6A8A; font-size:9px;">TP3</span><br><span style="color:#00FF9D; font-weight:bold;">{format_price_display(s['tp3'], s['pair'])}</span> <span class="tp-status {tp3_class}">{tp3_status}</span></div>
                </div>
            </div>"""

        bottom_html += "</div></div>"
        st.markdown(bottom_html, unsafe_allow_html=True)
    else:
        st.info("Belum ada sinyal aktif. Tunggu update berikutnya.")

    # ==========================================================================
    # TOP STORIES FROM TRADINGVIEW (DIPALING BAWAH)
    # ==========================================================================
    news_html = """
    <style>
    .cyber-panel-native {
        background: #0C1425; border: 1px solid #162035; border-radius: 8px;
        display: flex; flex-direction: column; height: 100%; box-sizing: border-box;
    }
    .panel-header {
        background: rgba(0,0,0,0.28); border-bottom: 1px solid #162035;
        padding: 6px 10px; display: flex; justify-content: space-between; align-items: center;
    }
    .panel-title { font-family: 'Share Tech Mono', monospace; font-size: 11px; color: #00EEFF; letter-spacing: 2px; text-transform: uppercase; }
    .panel-badge { font-family: monospace; font-size: 9px; color: #4B6A8A; letter-spacing: 1px; text-transform: uppercase; }
    .panel-body { flex: 1; min-height: 0; overflow: hidden; }
    </style>
    <div class="cyber-panel-native" style="margin-top: 15px;">
        <div class="panel-header">
            <span class="panel-title">Top Stories</span>
            <span class="panel-badge">TradingView</span>
        </div>
        <div class="panel-body">
            <div class="tradingview-widget-container" style="width:100%; height:100%;">
                <div class="tradingview-widget-container__widget" style="height:100%;"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-timeline.js" async>
                {
                "feedMode": "all_symbols", "colorTheme": "dark", "isTransparent": true,
                "displayMode": "regular", "width": "100%", "height": "100%", "locale": "id"
                }
                </script>
            </div>
        </div>
    </div>
    """
    st.components.v1.html(news_html, height=500)

if __name__ == "__main__":
    st.warning("File ini dirancang untuk di-import dari streamlit_app.py. Fungsi-fungsi pendukung belum tersedia saat dijalankan langsung.")
    show()
