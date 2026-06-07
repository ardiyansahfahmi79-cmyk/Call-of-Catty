
# widgets.py - AEROVULPIS V4.0 ULTIMATE (NO SOURCE DISPLAY)
# Economic Calendar & Smart Alert Widget

import streamlit as st
import requests
import os
from supabase import create_client, Client
from datetime import datetime, timedelta
import pytz
import yfinance as yf
import time

# ============================================================
# SUPABASE ADMIN CLIENT
# ============================================================
def get_supabase_admin():
    url = st.secrets["supabase_url"]
    service_role_key = st.secrets.get("supabase_service_role_key", st.secrets["supabase_key"])
    return create_client(url, service_role_key)

# ============================================================
# PRICE FORMATTER
# ============================================================
def format_price_display(price, instrument_name):
    name_upper = str(instrument_name).upper() if instrument_name else ""
    if "XAU" in name_upper or "GOLD" in name_upper:
        return f"{price:,.2f}"
    elif "XAG" in name_upper or "SILVER" in name_upper:
        return f"{price:,.2f}"
    elif "BTC" in name_upper or "BITCOIN" in name_upper:
        return f"{price:,.2f}"
    elif "ETH" in name_upper or "ETHEREUM" in name_upper:
        return f"{price:,.2f}"
    elif any(c in name_upper for c in ["SOL", "BNB", "XRP"]):
        return f"{price:,.2f}"
    elif any(fx in name_upper for fx in ["EUR", "GBP", "CHF", "JPY", "AUD", "NZD", "CAD"]):
        return f"{price:,.4f}"
    elif any(idx in name_upper for idx in ["NASDAQ", "S&P", "DOW", "DAX", "IHSG"]):
        return f"{price:,.2f}"
    elif any(cmd in name_upper for cmd in ["OIL", "WTI", "CRUDE", "GAS", "COPPER", "PALLADIUM", "PLATINUM"]):
        return f"{price:,.2f}"
    else:
        if price >= 1000:
            return f"{price:,.2f}"
        elif price >= 1:
            return f"{price:,.2f}"
        else:
            return f"{price:,.4f}".rstrip('0').rstrip('.')

# ============================================================
# MAPPING
# ============================================================
DISPLAY_TO_DB = {
    "XAUUSD": "GOLD (XAUUSD)",
    "XAGUSD": "SILVER (XAGUSD)",
    "BTCUSD": "BITCOIN",
    "ETHUSD": "ETHEREUM",
    "SOLUSD": "SOLANA",
    "EURUSD": "EUR/USD",
    "GBPUSD": "GBP/USD",
    "USDJPY": "USD/JPY",
    "AUDUSD": "AUD/USD",
    "USDCHF": "USD/CHF",
    "WTI": "CRUDE OIL (WTI)",
    "US100": "NASDAQ-100",
    "Palladium": "PALLADIUM",
    "Platinum": "PLATINUM",
    "GOOGL": "GOOGL",
    "AAPL": "APPLE",
    "BBCA.JK": "BBCA",
    "TLKM.JK": "TLKM"
}

DB_TO_YFINANCE_TICKER = {
    "GOLD (XAUUSD)": "GC=F",
    "SILVER (XAGUSD)": "SI=F",
    "BITCOIN": "BTC-USD",
    "ETHEREUM": "ETH-USD",
    "SOLANA": "SOL-USD",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CHF": "USDCHF=X",
    "CRUDE OIL (WTI)": "CL=F",
    "NASDAQ-100": "^IXIC",
    "PALLADIUM": "PA=F",
    "PLATINUM": "PL=F",
    "APPLE": "AAPL",
    "BBCA": "BBCA.JK",
    "TLKM": "TLKM.JK",
    "GOOGL": "GOOGL"
}

# ============================================================
# PRICE FETCHERS (INTERNAL, TIDAK DITAMPILKAN)
# ============================================================
def fetch_twelvedata_price(symbol):
    twelve_key = st.secrets.get("TWELVEDATA_KEY") or os.getenv("TWELVEDATA_KEY")
    if not twelve_key:
        return None
    name_upper = str(symbol).upper() if symbol else ""
    twelve_symbol = None
    if "XAU" in name_upper or "GOLD" in name_upper:
        twelve_symbol = "XAU/USD"
    elif "XAG" in name_upper or "SILVER" in name_upper:
        twelve_symbol = "XAG/USD"
    elif "EUR" in name_upper and "USD" in name_upper:
        twelve_symbol = "EUR/USD"
    elif "GBP" in name_upper and "USD" in name_upper:
        twelve_symbol = "GBP/USD"
    elif "USD" in name_upper and "JPY" in name_upper:
        twelve_symbol = "USD/JPY"
    elif "BTC" in name_upper:
        twelve_symbol = "BTC/USD"
    elif "ETH" in name_upper:
        twelve_symbol = "ETH/USD"
    if not twelve_symbol:
        return None
    try:
        url = f"https://api.twelvedata.com/price?symbol={twelve_symbol}&apikey={twelve_key}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("price"):
                return {"price": float(data["price"])}
    except Exception:
        pass
    return None

def fetch_finnhub_price_widget(symbol):
    finnhub_key = st.secrets.get("FINNHUB_KEY") or os.getenv("FINNHUB_KEY")
    if not finnhub_key:
        return None
    name_upper = str(symbol).upper() if symbol else ""
    finn_symbol = None
    if "XAU" in name_upper or "GOLD" in name_upper:
        finn_symbol = "OANDA:XAU_USD"
    elif "XAG" in name_upper or "SILVER" in name_upper:
        finn_symbol = "OANDA:XAG_USD"
    elif "EUR" in name_upper and "USD" in name_upper:
        finn_symbol = "OANDA:EUR_USD"
    elif "GBP" in name_upper and "USD" in name_upper:
        finn_symbol = "OANDA:GBP_USD"
    if not finn_symbol:
        return None
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={finn_symbol}&token={finnhub_key}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('c') and data.get('c') > 0:
                return {"price": float(data['c'])}
    except Exception:
        pass
    return None

def get_cached_price_from_supabase(db_name):
    try:
        supabase_admin = get_supabase_admin()
        res = supabase_admin.table("market_prices").select("*").eq("instrument", db_name).execute()
        if res and res.data:
            data = res.data[0]
            updated_at_str = data.get('updated_at', '')
            if not updated_at_str:
                return None
            try:
                updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
            except:
                return None
            if updated_at.tzinfo is None:
                updated_at = updated_at.replace(tzinfo=pytz.UTC)
            now_utc = datetime.now(pytz.UTC)
            if (now_utc - updated_at).total_seconds() < 5:
                price = data.get("price")
                if price and price > 0:
                    return {"price": price}
    except Exception:
        pass
    return None

@st.cache_data(ttl=60)
def fetch_price_yfinance(ticker):
    try:
        yt = yf.Ticker(ticker)
        hist = yt.history(period="1d")
        if not hist.empty:
            price = float(hist["Close"].iloc[-1])
            if price > 0:
                return {"price": price}
    except Exception:
        pass
    return {"price": 0.0}

def get_current_price(db_name):
    twelve_res = fetch_twelvedata_price(db_name)
    if twelve_res and twelve_res.get("price", 0) > 0:
        return twelve_res
    finnhub_res = fetch_finnhub_price_widget(db_name)
    if finnhub_res and finnhub_res.get("price", 0) > 0:
        return finnhub_res
    cached = get_cached_price_from_supabase(db_name)
    if cached and cached.get("price", 0) > 0:
        return cached
    ticker = DB_TO_YFINANCE_TICKER.get(db_name)
    if ticker:
        return fetch_price_yfinance(ticker)
    return {"price": 0.0}

# ============================================================
# ECONOMIC CALENDAR WIDGET
# ============================================================
def economic_calendar_widget():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&family=Share+Tech+Mono&display=swap');
        .radar-header-stack { display: flex; flex-direction: column; align-items: center; margin-bottom: 14px; width: 100%; gap: 6px; }
        .radar-title { font-family: 'Orbitron', sans-serif; font-size: 26px; font-weight: 700; color: #00d4ff; text-shadow: 0 0 12px rgba(0, 212, 255, 0.6); margin: 0; text-transform: uppercase; letter-spacing: 3px; text-align: center; }
        .radar-subtitle-row { display: flex; align-items: center; justify-content: center; gap: 8px; }
        .status-indicator { font-family: 'Share Tech Mono', monospace; font-size: 10px; color: #00ff88; letter-spacing: 1px; background: rgba(0, 255, 136, 0.05); padding: 2px 8px; border-radius: 3px; border: 1px solid rgba(0, 255, 136, 0.2); display: flex; align-items: center; }
        .status-dot { height: 5px; width: 5px; background: #00ff88; border-radius: 50%; display: inline-block; margin-right: 6px; box-shadow: 0 0 5px #00ff88; animation: pg 2s infinite; }
        @keyframes pg { 0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.6); } 70% { transform: scale(1); box-shadow: 0 0 0 4px rgba(0, 255, 136, 0); } 100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); } }
        .tradingview-widget-container iframe { border-radius: 6px !important; filter: brightness(0.9) contrast(1.05); }
        .impact-legend { display: flex; justify-content: center; gap: 18px; margin-top: 14px; font-family: 'Share Tech Mono', monospace; font-size: 10px; flex-wrap: wrap; }
        .legend-item { display: flex; align-items: center; gap: 6px; color: #8899bb; }
        .star-icon { font-size: 11px; }
        .high-impact { color: #ff2a6d; text-shadow: 0 0 4px rgba(255, 42, 109, 0.4); }
        .med-impact { color: #ffcc00; }
        .low-impact { color: #00ff88; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="radar-header-stack">
        <h2 class="radar-title">ECONOMIC RADAR</h2>
        <div class="radar-subtitle-row">
            <div class="status-indicator"><span class="status-dot"></span>LIVE CONNECTION</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tradingview_html = """
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
      {
        "colorTheme": "dark",
        "isTransparent": true,
        "width": "100%",
        "height": "450",
        "locale": "en",
        "importanceFilter": "-1,0,1",
        "currencyFilter": "USD,EUR,GBP,JPY,AUD,CAD,CHF,NZD"
      }
      </script>
    </div>
    """
    try:
        st.components.v1.html(tradingview_html, height=450)
    except Exception as e:
        st.error(f"ECONOMIC RADAR ERROR: {str(e)}")

    st.markdown("""
    <div class="impact-legend">
        <div class="legend-item"><span class="star-icon high-impact">★★★</span> High Impact</div>
        <div class="legend-item"><span class="star-icon med-impact">★★☆</span> Medium</div>
        <div class="legend-item"><span class="star-icon low-impact">★☆☆</span> Low</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# SMART ALERT WIDGET (TANPA SOURCE, INDIKATOR 5 MENIT)
# ============================================================
def smart_alert_widget(max_alerts=1):
    display_names = list(DISPLAY_TO_DB.keys())
    selected_display = st.selectbox("INSTRUMENT SELECTOR", display_names, key="alert_instrument_fix")
    db_name = DISPLAY_TO_DB.get(selected_display, selected_display)
    price_data = get_current_price(db_name)
    current_price = price_data["price"]
    price_display = format_price_display(current_price, db_name)

    if "active_alerts" not in st.session_state:
        st.session_state.active_alerts = []
    current_alerts_count = len(st.session_state.active_alerts)

    # CURRENT PRICE (tanpa source)
    st.markdown(f"""
    <div style="background:rgba(0,212,255,0.04);border:1px solid rgba(0,212,255,0.2);padding:14px;border-radius:4px;margin-bottom:16px;text-align:center;">
        <span style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#557799;letter-spacing:2px;">CURRENT PRICE</span><br>
        <span style="font-family:'Orbitron',sans-serif;font-size:22px;color:#00ff88;text-shadow:0 0 12px rgba(0,255,136,0.5);letter-spacing:2px;">{price_display}</span>
    </div>
    """, unsafe_allow_html=True)

    # INDIKATOR UPDATE 5 MENIT (dipasang tepat di bawah CURRENT PRICE)
    st.markdown("""
    <div style="text-align:center; margin-top:-10px; margin-bottom:12px;">
        <span style="font-family:'Share Tech Mono', monospace; font-size:8px; color:#00d4ff; letter-spacing:1px; background:rgba(0,212,255,0.08); padding:2px 6px; border-radius:2px;">
        [ PRICE UPDATED EVERY 5 MINUTES ]
        </span>
    </div>
    """, unsafe_allow_html=True)

    # SMART ALERT USAGE
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
        <span style="font-family: 'Orbitron', sans-serif; font-size: 10px; color: #8899bb; letter-spacing: 1px;">SMART ALERT USAGE</span>
        <span style="font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #00d4ff;">{current_alerts_count}/{max_alerts}</span>
    </div>
    """, unsafe_allow_html=True)

    # Tentukan desimal
    if db_name in ["GOLD (XAUUSD)", "SILVER (XAGUSD)"]:
        decimal_places = 2
    elif db_name in ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF"]:
        decimal_places = 4
    else:
        decimal_places = 2

    st.markdown('<p style="font-family:Orbitron;font-size:9px;color:#8899bb;letter-spacing:2px;text-transform:uppercase;margin:0 0 4px 0;">DIGITAL PRICE TARGET</p>', unsafe_allow_html=True)
    raw_target_input = st.text_input("TARGET", value="0", key="alert_target_fix_text", label_visibility="collapsed", placeholder="Masukkan harga target...")

    def parse_localized_number(input_str):
        if not input_str or not input_str.strip():
            return 0.0
        cleaned = input_str.strip()
        has_dot = "." in cleaned
        has_comma = "," in cleaned
        if has_comma and not has_dot:
            parts = cleaned.split(",")
            after_last_comma = parts[-1]
            if len(parts) == 2 and len(after_last_comma) <= 2:
                return float(cleaned.replace(",", "."))
        elif has_comma and has_dot:
            cleaned = cleaned.replace(",", "")
            return float(cleaned)
        else:
            return float(cleaned)

    try:
        price_target = parse_localized_number(raw_target_input)
    except ValueError:
        price_target = 0.0
        st.caption("Format tidak valid. Gunakan koma untuk ribuan (contoh: 2,650)")

    if price_target > 0:
        formatted_preview = f"{price_target:,.{decimal_places}f}"
        st.markdown(f"""
        <div style="background:rgba(0,255,136,0.03);border:1px solid rgba(0,255,136,0.15);padding:10px;border-radius:3px;margin-top:8px;text-align:center;">
            <span style="font-family:'Share Tech Mono',monospace;font-size:9px;color:#557799;letter-spacing:2px;">[ TARGET LOCKED ]</span><br>
            <span style="font-family:'Orbitron',sans-serif;font-size:16px;color:#00ff88;text-shadow:0 0 8px rgba(0,255,136,0.4);letter-spacing:2px;">{formatted_preview}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<p style="font-family:Orbitron;font-size:9px;color:#8899bb;letter-spacing:2px;text-transform:uppercase;margin:16px 0 4px 0;">TELEGRAM CHAT ID</p>', unsafe_allow_html=True)
    telegram_chat_id = st.text_input("CHAT ID", value="", placeholder="Enter Telegram Chat ID...", key="alert_chatid_fix", label_visibility="collapsed")

    st.markdown('<p style="font-family:Orbitron;font-size:9px;color:#8899bb;letter-spacing:2px;text-transform:uppercase;margin:16px 0 4px 0;">CONDITION TRIGGER</p>', unsafe_allow_html=True)
    condition_label = st.radio("CONDITION", ["BREAKOUT ABOVE [BULLISH]", "BREAKDOWN BELOW [BEARISH]"], key="alert_cond_fix", label_visibility="collapsed")
    condition_value = "bullish" if "ABOVE" in condition_label else "bearish"

    if st.button("LOCK TARGET & ACTIVATE SENSOR", key="alert_activate_fix", type="primary", use_container_width=True):
        if current_alerts_count >= max_alerts:
            st.error(f"[LIMIT] Smart Alert limit reached ({current_alerts_count}/{max_alerts}). Upgrade tier to add more.")
        elif price_target > 0 and telegram_chat_id:
            now_wib = datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%d/%m/%Y %H:%M:%S")
            formatted_target_display = f"{price_target:,.{decimal_places}f}"
            target_numeric = round(price_target, decimal_places)
            user_id = st.session_state.get("user_id", "unknown")
            initial_price = round(current_price, decimal_places) if current_price else 0.0

            alert_data = {
                "user_id": user_id,
                "instrument": db_name,
                "target": target_numeric,
                "initial_price": initial_price,
                "condition": condition_value,
                "chat_id": telegram_chat_id,
                "time_created": now_wib,
                "triggered": False
            }

            try:
                supabase_admin = get_supabase_admin()
                supabase_admin.table("active_alerts").insert(alert_data).execute()
                session_alert = alert_data.copy()
                session_alert["target_display"] = formatted_target_display
                if "active_alerts" not in st.session_state:
                    st.session_state.active_alerts = []
                st.session_state.active_alerts.append(session_alert)

                st.markdown(f"""
                <div style="background:rgba(0,212,255,0.06);border-left:3px solid #00d4ff;padding:16px;border-radius:3px;margin-top:18px;box-shadow:0 0 15px rgba(0,212,255,0.1);">
                    <p style="font-family:Orbitron;font-size:12px;color:#00d4ff;margin:0 0 8px;letter-spacing:2px;">/// SENSOR ACTIVATED ///</p>
                    <p style="font-family:Rajdhani;font-size:13px;color:#00d4ff;opacity:0.9;margin:2px 0;">INSTRUMENT: {selected_display}</p>
                    <p style="font-family:Rajdhani;font-size:13px;color:#00d4ff;opacity:0.9;margin:2px 0;">TARGET: {formatted_target_display}</p>
                    <p style="font-family:Rajdhani;font-size:13px;color:#00d4ff;opacity:0.9;margin:2px 0;">CHAT ID: {telegram_chat_id}</p>
                    <p style="font-family:Share Tech Mono;font-size:9px;color:#00ff88;margin:6px 0 0 0;letter-spacing:1px;">[STATUS]: MONITORING_24/7 | TELEGRAM_LINKED</p>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"DATABASE ERROR: {str(e)}")
        else:
            st.warning("ENTER VALID TARGET PRICE AND TELEGRAM CHAT ID")