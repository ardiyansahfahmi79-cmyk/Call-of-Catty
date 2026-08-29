"""
AERO AI TRADE v2.1
Streamlit + TradingView (chart real-time) + MetaApi.cloud (auto-trade)
Scoring system: EMA + RSI + ATR — porting dari EA MQL5
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# ================================================================
# PAGE CONFIG
# ================================================================
st.set_page_config(page_title="Aero AI Trade", page_icon="✈", layout="wide", initial_sidebar_state="collapsed")

# ================================================================
# DARK THEME OVERRIDE
# ================================================================
st.markdown("""<style>
[data-testid="stHeader"]{visibility:hidden}
[data-testid="stToolbar"]{visibility:hidden}
.stApp{background:#060610;color:#e2e2f0}
.block-container{padding-top:1rem;max-width:100%}
.stTabs [data-baseweb="tab-list"]{gap:2px;background:#0b0b1a;border-radius:6px;padding:3px}
.stTabs [data-baseweb="tab"]{border-radius:4px;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.7px;color:#3e3e60;padding:6px 14px}
.stTabs [aria-selected="true"]{background:#101028;color:#00d4aa}
.stTabs [data-baseweb="tab-highlight"]{background-color:#00d4aa;height:2px}
.stDataFrame{background:#0b0b1a;border:1px solid #1c1c40;border-radius:6px}
.stDataFrame td{font-size:11px;padding:4px 8px}
.stDataFrame th{font-size:9px;text-transform:uppercase;letter-spacing:.5px;color:#3e3e60;background:#0b0b1a}
div[data-testid="stTextInput"] label{font-size:10px;color:#6a6a90;text-transform:uppercase;letter-spacing:.5px}
div[data-testid="stTextInput"] input{background:#151535;border:1px solid #1c1c40;color:#e2e2f0;font-size:12px}
div[data-testid="stSelectbox"] label{font-size:10px;color:#6a6a90;text-transform:uppercase;letter-spacing:.5px}
div[data-testid="stSelectbox"] div[data-baseweb="select"]{background:#151535;border:1px solid #1c1c40}
div[data-testid="stSelectbox"] span{color:#e2e2f0;font-size:12px}
.stButton>button{font-size:11px;font-weight:600;border-radius:5px;padding:6px 16px}
.stAlert{font-size:11px;padding:8px 12px;border-radius:6px}
div[data-testid="stMetric"]{background:#0b0b1a;border:1px solid #1c1c40;border-radius:6px;padding:8px 12px}
div[data-testid="stMetricLabel"]{font-size:9px;text-transform:uppercase;letter-spacing:.8px;color:#3e3e60}
div[data-testid="stMetricValue"]{font-size:13px;font-weight:700}
.sig-card{background:#101028;border:1px solid #1c1c40;border-radius:8px;padding:12px 14px;text-align:center}
.sig-card .sig-label{font-size:9px;color:#3e3e60;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;font-weight:600}
.sig-card .sig-val{font-size:18px;font-weight:700;font-family:monospace}
.sig-card .sig-sub{font-size:10px;color:#6a6a90;margin-top:2px}
</style>""", unsafe_allow_html=True)

# ================================================================
# KONSTANTA
# ================================================================
PAIRS = {
    'EURUSD': {'name':'EUR/USD','tv':'FX:EURUSD','digits':5,'pip':10},
    'GBPUSD': {'name':'GBP/USD','tv':'FX:GBPUSD','digits':5,'pip':10},
    'USDJPY': {'name':'USD/JPY','tv':'FX:USDJPY','digits':3,'pip':6.67},
    'AUDUSD': {'name':'AUD/USD','tv':'FX:AUDUSD','digits':5,'pip':10},
    'USDCAD': {'name':'USD/CAD','tv':'FX:USDCAD','digits':5,'pip':7.33},
    'NZDUSD': {'name':'NZD/USD','tv':'FX:NZDUSD','digits':5,'pip':10},
    'XAUUSD': {'name':'XAU/USD','tv':'OANDA:XAUUSD','digits':2,'pip':1},
    'BTCUSD': {'name':'BTC/USD','tv':'BITSTAMP:BTCUSD','digits':2,'pip':1},
}
TF_TV = {'M1':'1','M5':'5','M15':'15','M30':'30','H1':'60','H4':'240','D1':'D','W1':'W'}
TF_API = {'M1':'1m','M5':'5m','M15':'15m','M30':'30m','H1':'1h','H4':'4h','D1':'1d','W1':'1w'}

# ================================================================
# SESSION STATE
# ================================================================
defaults = {
    'bot_active': False, 'connected': False, 'metaapi_ready': False,
    'journal': [], 'score': 0, 'last_signal': 'WAIT',
    'ema_status': '—', 'rsi_val': 50.0, 'atr_val': 0.0,
    'sl_calc': 0.0, 'tp_calc': 0.0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def add_log(tp, msg):
    st.session_state.journal.insert(0, {'time': datetime.now().strftime('%H:%M:%S'), 'type': tp, 'msg': msg})
    if len(st.session_state.journal) > 200:
        st.session_state.journal = st.session_state.journal[:200]

# ================================================================
# META API BRIDGE (REST API — tanpa SDK async, murni requests)
# ================================================================
class MetaApiBridge:
    """Komunikasi dengan MetaApi.cloud via REST API — 100% synchronous, aman untuk Streamlit"""
    BASE = 'https://metaapi.cloud/api/v2'

    def __init__(self, token):
        self.token = token
        self.h = {'auth-token': token, 'Accept': 'application/json', 'Content-Type': 'application/json'}

    def get_accounts(self):
        try:
            r = requests.get(f'{self.BASE}/users/current/accounts', headers=self.h, timeout=10)
            return r.json()
        except Exception as e:
            return {'error': str(e)}

    def ensure_rpc(self, account_id):
        """Pastikan RPC connection aktif (terminal MT5 berjalan di cloud MetaApi)"""
        try:
            # Cek state
            r = requests.get(f'{self.BASE}/users/current/accounts/{account_id}', headers=self.h, timeout=10)
            acc = r.json()
            if acc.get('state') != 'DEPLOYED':
                requests.post(f'{self.BASE}/users/current/accounts/{account_id}/deploy', headers=self.h, timeout=30)
                return False  # Perlu tunggu deploy
            # Connect RPC
            requests.post(f'{self.BASE}/users/current/accounts/{account_id}/rpc/connect', headers=self.h, timeout=15)
            return True
        except Exception as e:
            add_log('error', f'MetaApi connect error: {e}')
            return False

    def get_candles(self, account_id, symbol, timeframe, limit=100):
        """Ambil data candle dari MT5 via MetaApi"""
        try:
            tf = TF_API.get(timeframe, '1h')
            r = requests.get(
                f'{self.BASE}/users/current/accounts/{account_id}/history/candles',
                headers=self.h, timeout=15,
                params={'symbol': symbol, 'timeframe': tf, 'limit': limit}
            )
            data = r.json()
            if 'history' in data:
                return data['history']
            return []
        except Exception as e:
            add_log('error', f'Get candles error: {e}')
            return []

    def get_price(self, account_id, symbol):
        """Ambil harga terkini"""
        try:
            r = requests.get(
                f'{self.BASE}/users/current/accounts/{account_id}/symbols/{symbol}/price',
                headers=self.h, timeout=10
            )
            return r.json()
        except Exception as e:
            return {}

    def open_trade(self, account_id, symbol, trade_type, volume, sl=None, tp=None, magic=123456):
        """Buka order BUY atau SELL"""
        try:
            body = {'symbol': symbol, 'volume': volume, 'type': trade_type, 'magic': magic}
            if sl: body['stopLoss'] = sl
            if tp: body['takeProfit'] = tp
            r = requests.post(
                f'{self.BASE}/users/current/accounts/{account_id}/trade',
                headers=self.h, timeout=15, json=body
            )
            return r.json()
        except Exception as e:
            return {'error': str(e)}

    def get_positions(self, account_id):
        """Ambil posisi terbuka"""
        try:
            r = requests.get(
                f'{self.BASE}/users/current/accounts/{account_id}/positions',
                headers=self.h, timeout=10
            )
            return r.json()
        except Exception as e:
            return []

    def close_position(self, account_id, position_id):
        """Tutup posisi"""
        try:
            r = requests.post(
                f'{self.BASE}/users/current/accounts/{account_id}/trade',
                headers=self.h, timeout=15,
                json={'positionId': position_id}
            )
            return r.json()
        except Exception as e:
            return {'error': str(e)}


@st.cache_resource
def get_metaapi():
    """Inisialisasi MetaApi bridge — di-cache supaya tidak buat ulang setiap rerun"""
    token = st.secrets.get('META_API_TOKEN', '')
    acc_id = st.secrets.get('META_API_ACCOUNT_ID', '')
    if not token or not acc_id:
        return None
    api = MetaApiBridge(token)
    # Test koneksi
    accs = api.get_accounts()
    if 'error' in accs:
        return None
    return {'api': api, 'account_id': acc_id}

# ================================================================
# INDIKATOR (sama persis logika dengan MQL5 EA)
# ================================================================
def calc_ema(close_series, period):
    """EMA calculation — identik dengan iMA() di MQL5"""
    if len(close_series) < period:
        return close_series
    k = 2.0 / (period + 1)
    ema = [close_series[0]]
    for i in range(1, len(close_series)):
        ema.append(close_series[i] * k + ema[-1] * (1 - k))
    return ema

def calc_rsi(close_series, period=14):
    """RSI calculation — identik dengan iRSI() di MQL5"""
    if len(close_series) < period + 1:
        return [50.0] * len(close_series)
    rsi = [50.0] * (period)
    gains, losses = [], []
    for i in range(1, period + 1):
        d = close_series[i] - close_series[i-1]
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    rsi.append(100 if avg_loss == 0 else 100 - 100 / (1 + avg_gain / avg_loss))
    for i in range(period + 1, len(close_series)):
        d = close_series[i] - close_series[i-1]
        avg_gain = (avg_gain * (period - 1) + max(d, 0)) / period
        avg_loss = (avg_loss * (period - 1) + max(-d, 0)) / period
        rsi.append(100 if avg_loss == 0 else 100 - 100 / (1 + avg_gain / avg_loss))
    return rsi

def calc_atr(high, low, close, period=14):
    """ATR calculation — identik dengan iATR() di MQL5"""
    if len(high) < period + 1:
        return [0.0] * len(high)
    tr_list = []
    for i in range(1, len(high)):
        tr = max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1]))
        tr_list.append(tr)
    atr = [0.0] * period
    atr.append(sum(tr_list[:period]) / period)
    for i in range(period, len(tr_list)):
        atr.append((atr[-1] * (period - 1) + tr_list[i]) / period)
    return atr

# ================================================================
# SCORING SYSTEM — porting 1:1 dari MQL5 EA
# ================================================================
def calc_score(ema_fast, ema_slow, rsi_vals, ema_fast_period=9, rsi_ob=70, rsi_os=30):
    """
    Scoring identik dengan EA MQL5:
    - EMA crossover/trend: ±1
    - RSI zone/momentum: ±1
    - Total skor -2 s/d +2
    """
    n = len(ema_fast)
    if n < 3:
        return 0
    score = 0

    # 1. EMA Trend (sama persis MQL5)
    if ema_fast[n-1] > ema_slow[n-1] and ema_fast[n-2] <= ema_slow[n-2]:
        score += 1   # Bullish crossover
    elif ema_fast[n-1] < ema_slow[n-1] and ema_fast[n-2] >= ema_slow[n-2]:
        score -= 1   # Bearish crossover
    elif ema_fast[n-1] > ema_slow[n-1]:
        score += 1   # Masih tren naik
    elif ema_fast[n-1] < ema_slow[n-1]:
        score -= 1   # Masih tren turun

    # 2. RSI Momentum (sama persis MQL5)
    r = rsi_vals[n-1] if n-1 < len(rsi_vals) else 50
    if r < rsi_os:
        score += 1   # Oversold → buy
    elif r > rsi_ob:
        score -= 1   # Overbought → sell
    elif r > 50:
        score += 1   # Momentum naik
    elif r < 50:
        score -= 1   # Momentum turun

    return score

# ================================================================
# TRADINGVIEW WIDGET — chart real-time 100%
# ================================================================
def render_tv_chart(symbol_tv, interval_tv, height=480):
    """Embed TradingView Advanced Chart — harga REAL dari market"""
    widget_id = f"tv_{symbol_tv.replace(':','_')}_{interval_tv}"
    html = f"""
    <div style="width:100%;height:{height}px;border-radius:8px;overflow:hidden;border:1px solid #1c1c40">
        <div id="{widget_id}" style="height:100%;width:100%"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
            "autosize": true,
            "symbol": "{symbol_tv}",
            "interval": "{interval_tv}",
            "timezone": "Asia/Jakarta",
            "theme": "dark",
            "style": "1",
            "locale": "id_ID",
            "backgroundColor": "#080812",
            "gridColor": "#1c1c40",
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "save_image": false,
            "container_id": "{widget_id}",
            "hide_volume": false,
            "studies": [
                "MAExp@tv-basicstudies",
                "RSI@tv-basicstudies",
                "ATR@tv-basicstudies"
            ],
            "study_overrides": {{
                "MAExp.length": 9,
                "RSI.length": 14
            }}
        }});
        </script>
    </div>"""
    components.html(html, height=height + 4)

# ================================================================
# MAIN APP
# ================================================================
def main():
    # --- MetaApi init ---
    ma = get_metaapi()
    if ma and not st.session_state.metaapi_ready:
        ma['api'].ensure_rpc(ma['account_id'])
        st.session_state.metaapi_ready = True
        add_log('system', 'MetaApi.cloud terhubung — auto-entry siap')

    metaapi_connected = ma is not None and st.session_state.metaapi_ready

    # ============================================================
    # HEADER
    # ============================================================
    col_logo, col_spacer, col_metrics = st.columns([0.15, 0.55, 0.3])
    with col_logo:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px">
            <div style="width:30px;height:30px;border-radius:7px;background:linear-gradient(135deg,#00d4aa,#006b55);
                        display:flex;align-items:center;justify-content:center;box-shadow:0 0 16px rgba(0,212,170,.12)">
                <span style="font-size:13px">✈</span>
            </div>
            <div style="font-weight:700;font-size:14px;letter-spacing:1.5px"><span style="color:#00d4aa">AERO</span> AI TRADE</div>
        </div>""", unsafe_allow_html=True)
    with col_metrics:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Balance", "$10,000.00")
        m2.metric("Equity", "$10,000.00")
        m3.metric("Margin", "$0.00")
        m4.metric("Free Margin", "$10,000.00")

    st.divider()

    # ============================================================
    # KONTROL BAR (horizontal, bukan sidebar)
    # ============================================================
    c1, c2, c3, c4, c5, c6, c7 = st.columns([1.5, 0.8, 0.6, 0.8, 1.2, 0.4, 0.7])
    with c1:
        pair = st.selectbox('Pair', list(PAIRS.keys()), format_func=lambda x: PAIRS[x]['name'])
    with c2:
        tf = st.selectbox('TF', ['M1','M5','M15','M30','H1','H4','D1','W1'])
    with c3:
        mode = st.selectbox('Mode', ['scoring', 'limit'])
    with c4:
        if mode == 'limit':
            limit_entry = st.text_input('Limit Entry', placeholder='0.00000')
        else:
            limit_entry = ''
    with c5:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            btn_bot = st.button(
                '⏹ Deactivate' if st.session_state.bot_active else '▶ Activate Bot',
                use_container_width=True,
                type='primary' if not st.session_state.bot_active else 'secondary'
            )
        with col_btn2:
            score_color = '🟢' if st.session_state.score > 0 else ('🔴' if st.session_state.score < 0 else '⚪')
            st.markdown(f"""
            <div style="text-align:center;margin-top:4px">
                <div style="font-size:9px;color:#3e3e60;text-transform:uppercase;letter-spacing:.5px">Score</div>
                <div style="font-size:20px;font-weight:700;font-family:monospace;color:{'#10b981' if st.session_state.score > 0 else '#f43f5e' if st.session_state.score < 0 else '#3e3e60'}">
                    {score_color} {st.session_state.score:+d}
                </div>
            </div>""", unsafe_allow_html=True)
    with c6:
        st.markdown(f"""<div style="margin-top:8px;font-size:11px;font-weight:600;color:{'#10b981' if st.session_state.bot_active else '#3e3e60'}">
            {'● ACTIVE' if st.session_state.bot_active else '○ IDLE'}
        </div>""", unsafe_allow_html=True)
    with c7:
        if metaapi_connected:
            st.markdown("""<div style="margin-top:8px;font-size:10px;color:#10b981"><i>● MetaApi Live</i></div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div style="margin-top:8px;font-size:10px;color:#eab308"><i>○ Demo Mode</i></div>""", unsafe_allow_html=True)

    # Handle bot toggle
    if btn_bot:
        st.session_state.bot_active = not st.session_state.bot_active
        if st.session_state.bot_active:
            add_log('bot', f'Bot AKTIF — {mode} | {PAIRS[pair]["name"]} {tf}')
        else:
            add_log('bot', 'Bot DIMATIKAN')
        st.rerun()

    # ============================================================
    # TRADINGVIEW CHART — REAL-TIME 100%
    # ============================================================
    tv_symbol = PAIRS[pair]['tv']
    tv_interval = TF_TV.get(tf, '60')
    render_tv_chart(tv_symbol, tv_interval, height=440)

    # ============================================================
    # SIGNAL CARDS
    # ============================================================
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        ema_color = '#10b981' if 'BULL' in st.session_state.ema_status else '#f43f5e'
        st.markdown(f"""<div class="sig-card">
            <div class="sig-label">EMA Trend</div>
            <div class="sig-val" style="color:{ema_color}">{st.session_state.ema_status}</div>
            <div class="sig-sub">Fast({st.secrets.get('EMA_FAST',9)}/Slow({st.secrets.get('EMA_SLOW',21)}))</div>
        </div>""", unsafe_allow_html=True)
    with sc2:
        rsi_color = '#f43f5e' if st.session_state.rsi_val > 70 else ('#10b981' if st.session_state.rsi_val < 30 else '#e2e2f0')
        st.markdown(f"""<div class="sig-card">
            <div class="sig-label">RSI Momentum</div>
            <div class="sig-val" style="color:{rsi_color}">{st.session_state.rsi_val:.1f}</div>
            <div class="sig-sub">{'Overbought' if st.session_state.rsi_val>70 else 'Oversold' if st.session_state.rsi_val<30 else 'Neutral zone'}</div>
        </div>""", unsafe_allow_html=True)
    with sc3:
        st.markdown(f"""<div class="sig-card">
            <div class="sig-label">ATR Volatility</div>
            <div class="sig-val">{st.session_state.atr_val:.5f}</div>
            <div class="sig-sub">SL: {st.session_state.sl_calc:.5f} | TP: {st.session_state.tp_calc:.5f}</div>
        </div>""", unsafe_allow_html=True)
    with sc4:
        dec_color = '#10b981' if st.session_state.last_signal == 'BUY' else ('#f43f5e' if st.session_state.last_signal == 'SELL' else '#3e3e60')
        min_s = int(st.secrets.get('MIN_SCORE', 2))
        st.markdown(f"""<div class="sig-card">
            <div class="sig-label">Decision (min ±{min_s})</div>
            <div class="sig-val" style="color:{dec_color}">{st.session_state.last_signal}</div>
            <div class="sig-sub">{'Auto-execute via MetaApi' if metaapi_connected else 'Demo — butuh MetaApi'}</div>
        </div>""", unsafe_allow_html=True)

    # ============================================================
    # BOTTOM TABS
    # ============================================================
    tab_sig, tab_pos, tab_log, tab_set = st.tabs(['Signals', 'Positions', 'Journal', 'Settings'])

    with tab_pos:
        if metaapi_connected and ma:
            positions = ma['api'].get_positions(ma['account_id'])
            if isinstance(positions, list) and positions:
                rows = []
                for p in positions:
                    rows.append({
                        'Ticket': p.get('id', '—'),
                        'Pair': p.get('symbol', '—'),
                        'Type': p.get('type', '—'),
                        'Lot': p.get('volume', 0),
                        'Open': p.get('openPrice', 0),
                        'S/L': p.get('stopLoss', '—'),
                        'T/P': p.get('takeProfit', '—'),
                        'Profit': p.get('profit', 0),
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.info('Tidak ada posisi terbuka')
        else:
            st.info('Tidak ada posisi terbuka (Demo Mode)')

    with tab_log:
        if st.session_state.journal:
            log_rows = []
            for j in st.session_state.journal[:50]:
                tp_color = {'system':'🟢','trade':'🟡','error':'🔴','bot':'🔵','signal':'🟣'}.get(j['type'], '⚪')
                log_rows.append({'⏰': j['time'], '': tp_color, 'Type': j['type'], 'Message': j['msg']})
            st.dataframe(pd.DataFrame(log_rows), use_container_width=True, hide_index=True)
        else:
            st.info('Journal kosong')

    with tab_set:
        st.markdown('### MetaApi.cloud Configuration')
        st.markdown("""
        Untuk mengaktifkan **auto-entry real** (bot mengeksekusi order ke MT5 secara otomatis):

        1. Daftar gratis di [metaapi.cloud](https://metaapi.cloud)
        2. Tambahkan akun MT5 Anda di dashboard MetaApi
        3. Copy **API Token** dan **Account ID**
        4. Isi di file `.streamlit/secrets.toml`:

        ```
        META_API_TOKEN = "token_anda_di_sini"
        META_API_ACCOUNT_ID = "account_id_anda_di_sini"
        ```
        """)
        st.markdown('### EA Parameters')
        st.markdown('Edit di `.streamlit/secrets.toml`:')
        st.code("""
EMA_FAST = 9
EMA_SLOW = 21
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
ATR_PERIOD = 14
ATR_SL_MULT = 1.5
ATR_TP_MULT = 2.5
MIN_SCORE = 2
LOT_SIZE = 0.01
MAGIC_NUMBER = 123456
        """, language='toml')

    # ============================================================
    # BOT TICK — dijalankan setiap rerun
    # ============================================================
    if st.session_state.bot_active:
        if metaapi_connected and ma:
            # === MODE LIVE: Data dari MetaApi, eksekusi real ===
            candles = ma['api'].get_candles(ma['account_id'], pair, tf, limit=100)
            if candles and len(candles) >= 25:
                closes = [c['close'] for c in candles]
                highs = [c['high'] for c in candles]
                lows = [c['low'] for c in candles]
                ema_f = int(st.secrets.get('EMA_FAST', 9))
                ema_s = int(st.secrets.get('EMA_SLOW', 21))
                rsi_p = int(st.secrets.get('RSI_PERIOD', 14))
                atr_p = int(st.secrets.get('ATR_PERIOD', 14))
                sl_m = float(st.secrets.get('ATR_SL_MULT', 1.5))
                tp_m = float(st.secrets.get('ATR_TP_MULT', 2.5))
                min_s = int(st.secrets.get('MIN_SCORE', 2))

                ef = calc_ema(closes, ema_f)
                es = calc_ema(closes, ema_s)
                rsi = calc_rsi(closes, rsi_p)
                atr = calc_atr(highs, lows, closes, atr_p)

                score = calc_score(ef, es, rsi)
                st.session_state.score = score
                st.session_state.rsi_val = rsi[-1]
                st.session_state.atr_val = atr[-1]
                st.session_state.sl_calc = closes[-1] - atr[-1] * sl_m
                st.session_state.tp_calc = closes[-1] + atr[-1] * tp_m
                st.session_state.ema_status = 'BULLISH' if ef[-1] > es[-1] else 'BEARISH'

                # Cek posisi terbuka
                positions = ma['api'].get_positions(ma['account_id'])
                has_pos = isinstance(positions, list) and len(positions) > 0

                if mode == 'scoring' and not has_pos:
                    if score >= min_s:
                        st.session_state.last_signal = 'BUY'
                        result = ma['api'].open_trade(
                            ma['account_id'], pair, 'BUY',
                            float(st.secrets.get('LOT_SIZE', 0.01)),
                            sl=round(st.session_state.sl_calc, PAIRS[pair]['digits']),
                            tp=round(st.session_state.tp_calc, PAIRS[pair]['digits']),
                            magic=int(st.secrets.get('MAGIC_NUMBER', 123456))
                        )
                        add_log('signal', f'SCORE {score:+d} → AUTO BUY {PAIRS[pair]["name"]} @ {closes[-1]:.5f} via MetaApi')
                        if 'error' in result:
                            add_log('error', f'Order error: {result["error"]}')
                    elif score <= -min_s:
                        st.session_state.last_signal = 'SELL'
                        result = ma['api'].open_trade(
                            ma['account_id'], pair, 'SELL',
                            float(st.secrets.get('LOT_SIZE', 0.01)),
                            sl=round(closes[-1] + atr[-1] * sl_m, PAIRS[pair]['digits']),
                            tp=round(closes[-1] - atr[-1] * tp_m, PAIRS[pair]['digits']),
                            magic=int(st.secrets.get('MAGIC_NUMBER', 123456))
                        )
                        add_log('signal', f'SCORE {score:+d} → AUTO SELL {PAIRS[pair]["name"]} @ {closes[-1]:.5f} via MetaApi')
                        if 'error' in result:
                            add_log('error', f'Order error: {result["error"]}')
                    else:
                        st.session_state.last_signal = 'WAIT'

                elif mode == 'limit' and not has_pos and limit_entry:
                    try:
                        le = float(limit_entry)
                        price = ma['api'].get_price(ma['account_id'], pair)
                        bid = price.get('bid', 0)
                        cfg = PAIRS[pair]
                        if abs(bid - le) < cfg['pip'] * 2:  # Toleransi 2 pip
                            result = ma['api'].open_trade(
                                ma['account_id'], pair, 'BUY',
                                float(st.secrets.get('LOT_SIZE', 0.01)),
                                magic=int(st.secrets.get('MAGIC_NUMBER', 123456))
                            )
                            add_log('signal', f'Limit {le} tersentuh @ {bid} → AUTO BUY via MetaApi')
                            st.session_state.bot_active = False
                            st.rerun()
                        else:
                            add_log('bot', f'Limit {le} — bid {bid:.5f}, menunggu...')
                    except ValueError:
                        pass

        else:
            # === MODE DEMO: Tampilkan info tanpa eksekusi ===
            st.session_state.last_signal = 'DEMO'
            st.session_state.ema_status = 'DEMO'
            st.session_state.rsi_val = 50.0
            st.session_state.atr_val = 0.0
            add_log('bot', f'[DEMO] Monitoring {PAIRS[pair]["name"]} {tf} — isi MetaApi Token di Settings untuk eksekusi real')

    # ============================================================
    # AUTO-REFRESH — trigger rerun setiap 5 detik saat bot aktif
    # ============================================================
    if st.session_state.bot_active:
        import time
        time.sleep(5)
        st.rerun()

# ================================================================
# RUN
# ================================================================
if __name__ == '__main__':
    main()