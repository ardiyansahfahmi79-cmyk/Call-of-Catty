# ==============================================================================
# AEROVULPIS V4.0 ULTIMATE - PART 1 (SEMUA FUNGSI & KONFIGURASI)
# ==============================================================================

from supabase import create_client, Client
import streamlit as st
from groq import Groq
from news_cache_manager import initialize_news_cache, should_update_news, get_cached_news, update_news_cache
from widgets import economic_calendar_widget, smart_alert_widget
import os
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, time as dt_time, timedelta
import pytz
import ta
import time
import requests
import json
import finnhub
import re
import hashlib
from io import BytesIO
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
import wbgapi as wb

# Import tambahan untuk backup LLM
try:
    import cohere
except ImportError:
    cohere = None
try:
    from cerebras.cloud.sdk import Cerebras
except ImportError:
    Cerebras = None

# ==============================================================================
# AUTO-REFRESH
# ==============================================================================
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    AUTOREFRESH_AVAILABLE = False

load_dotenv()

# ##############################################################################
# SUPABASE
# ##############################################################################
url = st.secrets["supabase_url"]
key = st.secrets["supabase_key"]
service_role_key = st.secrets.get("supabase_service_role_key", key)

def get_supabase_client():
    return create_client(url, key)

def get_supabase_admin():
    return create_client(url, service_role_key)

def rest_api_request(method, table, params=None, body=None, limit=None):
    supabase_url_str = st.secrets["supabase_url"]
    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    base_url = f"{supabase_url_str}/rest/v1/{table}"
    query_params = params or {}
    if limit:
        query_params["limit"] = str(limit)
    qs = "&".join([f"{k}={v}" for k, v in query_params.items()])
    url_with_qs = f"{base_url}?{qs}" if qs else base_url

    if method == "GET":
        resp = requests.get(url_with_qs, headers=headers, timeout=10)
    elif method == "PATCH":
        resp = requests.patch(url_with_qs, headers=headers, json=body, timeout=10)
    elif method == "POST":
        resp = requests.post(url_with_qs, headers=headers, json=body, timeout=10)
    else:
        return None
    return resp

# ##############################################################################
# LOGGING & MAINTENANCE
# ##############################################################################
def send_log(pesan):
    try:
        supabase_admin = get_supabase_admin()
        supabase_admin.table("logs_aktivitas").insert({"keterangan": pesan}).execute()
    except Exception:
        pass

def cleanup_logs():
    try:
        supabase_admin = get_supabase_admin()
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        supabase_admin.table("logs_aktivitas").delete().lt("created_at", cutoff).execute()
    except Exception:
        pass

def cleanup_ai_cache():
    try:
        supabase_admin = get_supabase_admin()
        supabase_admin.rpc("cleanup_ai_cache").execute()
    except Exception:
        try:
            cutoff = (datetime.now(pytz.UTC) - timedelta(hours=2, minutes=30)).isoformat()
            supabase_admin.table("ai_cache_sentinel").delete().lt("created_at", cutoff).execute()
            supabase_admin.table("ai_cache_deep").delete().lt("created_at", cutoff).execute()
        except Exception:
            pass

def cleanup_news_cache():
    try:
        supabase_admin = get_supabase_admin()
        cutoff = (datetime.now(pytz.UTC) - timedelta(hours=2)).isoformat()
        supabase_admin.table("news_cache").delete().lt("created_at", cutoff).execute()
    except Exception:
        pass

def safe_parse_timestamp(ts_value):
    if ts_value is None:
        return None
    if isinstance(ts_value, datetime):
        if ts_value.tzinfo is None:
            return ts_value.replace(tzinfo=pytz.UTC)
        return ts_value
    if isinstance(ts_value, str):
        try:
            cleaned = ts_value.replace('Z', '+00:00')
            dt = datetime.fromisoformat(cleaned)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=pytz.UTC)
            return dt
        except Exception:
            pass
        try:
            dt = datetime.strptime(ts_value[:19], "%Y-%m-%dT%H:%M:%S")
            return dt.replace(tzinfo=pytz.UTC)
        except Exception:
            pass
    return None

# ##############################################################################
# AI CACHE (2.5 JAM)
# ##############################################################################
def get_cached_ai_analysis(asset_name, analysis_type, timeframe_key):
    try:
        supabase_admin = get_supabase_admin()
        table = "ai_cache_sentinel" if analysis_type == "sentinel" else "ai_cache_deep"
        res = supabase_admin.table(table).select("*")\
            .eq("instrument", asset_name)\
            .eq("timeframe", timeframe_key)\
            .order("created_at", desc=True).limit(1).execute()
        if not res or not res.data:
            return None
        entry = res.data[0]
        created_at_val = entry.get("created_at")
        created_at = safe_parse_timestamp(created_at_val)
        if created_at is None:
            return None
        if (datetime.now(pytz.UTC) - created_at).total_seconds() < 9000:
            return entry.get("analysis")
    except Exception:
        pass
    return None

def cache_ai_analysis(asset_name, analysis, analysis_type, timeframe_key):
    try:
        supabase_admin = get_supabase_admin()
        table = "ai_cache_sentinel" if analysis_type == "sentinel" else "ai_cache_deep"
        data = {
            "instrument": asset_name,
            "timeframe": timeframe_key,
            "analysis": analysis,
            "created_at": datetime.now(pytz.UTC).isoformat()
        }
        supabase_admin.table(table).insert(data).execute()
    except Exception:
        pass

# ==============================================================================
# SIGNAL CACHE (UNTUK SIGNAL ANALYSIS - UPDATE JAM 7 PAGI)
# ==============================================================================
def get_cached_signal(instrument):
    try:
        supabase_admin = get_supabase_admin()
        res = supabase_admin.table("signal_cache").select("*")\
            .eq("instrument", instrument)\
            .gte("valid_until", datetime.now(pytz.UTC).isoformat())\
            .order("created_at", desc=True).limit(1).execute()
        if res and res.data:
            return res.data[0]
    except Exception:
        pass
    return None

def cache_signal(instrument, signal_data):
    try:
        supabase_admin = get_supabase_admin()
        supabase_admin.table("signal_cache").delete().eq("instrument", instrument).execute()
        data = {
            "instrument": instrument,
            "signal_type": signal_data["signal_type"],
            "entry_price": signal_data["entry_price"],
            "stop_loss": signal_data["stop_loss"],
            "take_profit_1": signal_data["take_profit_1"],
            "take_profit_2": signal_data["take_profit_2"],
            "take_profit_3": signal_data["take_profit_3"],
            "risk_reward_ratio": signal_data.get("risk_reward_ratio", 0),
            "created_at": datetime.now(pytz.UTC).isoformat(),
            "valid_until": (datetime.now(pytz.UTC) + timedelta(hours=24)).isoformat(),
            "updated_at": datetime.now(pytz.UTC).isoformat()
        }
        supabase_admin.table("signal_cache").insert(data).execute()
    except Exception as e:
        print(f"Error cache signal: {e}")

def generate_signal_for_instrument(instrument, current_price, df_indicators):
    if df_indicators.empty:
        return None
    latest = df_indicators.iloc[-1]
    rsi = latest.get("RSI", 50)
    macd = latest.get("MACD", 0)
    signal_line = latest.get("Signal_Line", 0)
    close = latest.get("Close", current_price)
    sma50 = latest.get("SMA50", close)
    sma200 = latest.get("SMA200", close)
    atr = latest.get("ATR", 0.001)
    
    if rsi < 40 and macd > signal_line:
        signal = "BUY"
        entry = close
        sl = entry - (atr * 1.5)
        tp1 = entry + (atr * 1.5)
        tp2 = entry + (atr * 3)
        tp3 = entry + (atr * 5)
    elif rsi > 60 and macd < signal_line:
        signal = "SELL"
        entry = close
        sl = entry + (atr * 1.5)
        tp1 = entry - (atr * 1.5)
        tp2 = entry - (atr * 3)
        tp3 = entry - (atr * 5)
    else:
        if sma50 > sma200 and close > sma50:
            signal = "BUY"
            entry = close
            sl = entry - (atr * 1.2)
            tp1 = entry + (atr * 1.5)
            tp2 = entry + (atr * 3)
            tp3 = entry + (atr * 5)
        elif sma50 < sma200 and close < sma50:
            signal = "SELL"
            entry = close
            sl = entry + (atr * 1.2)
            tp1 = entry - (atr * 1.5)
            tp2 = entry - (atr * 3)
            tp3 = entry - (atr * 5)
        else:
            return None
    
    rr = abs((tp1 - entry) / (entry - sl)) if signal == "BUY" else abs((entry - tp1) / (sl - entry))
    return {
        "signal_type": signal,
        "entry_price": entry,
        "stop_loss": sl,
        "take_profit_1": tp1,
        "take_profit_2": tp2,
        "take_profit_3": tp3,
        "risk_reward_ratio": round(rr, 2)
    }

def update_all_signals():
    target_instruments = ["GOLD (XAUUSD)", "BITCOIN", "EUR/USD", "GBP/USD"]
    instrument_to_ticker = {
        "GOLD (XAUUSD)": "GC=F",
        "BITCOIN": "BTC-USD",
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X"
    }
    for inst in target_instruments:
        ticker = instrument_to_ticker.get(inst)
        if not ticker:
            continue
        market = get_market_data(ticker)
        if not market:
            continue
        if inst == "GOLD (XAUUSD)":
            df = get_historical_data("GC=F", period="1mo", interval="1h")
        elif inst == "BITCOIN":
            df = get_historical_data("BTC-USD", period="1mo", interval="1h")
        else:
            df = get_historical_data(ticker, period="1mo", interval="1h")
        if df.empty:
            continue
        df = add_technical_indicators(df)
        signal_data = generate_signal_for_instrument(inst, market["price"], df)
        if signal_data:
            cache_signal(inst, signal_data)

# ##############################################################################
# NEWS CACHE SUPABASE
# ##############################################################################
def get_cached_news_supabase(category):
    try:
        supabase_admin = get_supabase_admin()
        res = supabase_admin.table("news_cache").select("*").eq("category", category).order("created_at", desc=True).limit(1).execute()
        if not res or not res.data:
            return None
        entry = res.data[0]
        created_at_val = entry.get("created_at")
        created_at = safe_parse_timestamp(created_at_val)
        if created_at is None:
            return None
        if (datetime.now(pytz.UTC) - created_at).total_seconds() < 3600:
            articles = entry.get("articles")
            if isinstance(articles, str):
                articles = json.loads(articles)
            return articles
    except Exception:
        pass
    return None

def cache_news_supabase(category, articles):
    try:
        supabase_admin = get_supabase_admin()
        data = {
            "category": category,
            "articles": json.dumps(articles, default=str),
            "created_at": datetime.now(pytz.UTC).isoformat()
        }
        supabase_admin.table("news_cache").insert(data).execute()
    except Exception:
        pass

# ##############################################################################
# MARKET PRICE CACHE
# ##############################################################################
def cache_market_price(symbol, price, change_pct=0.0):
    try:
        supabase_admin = get_supabase_admin()
        data = {
            "instrument": symbol,
            "price": price,
            "change_pct": change_pct,
            "updated_at": datetime.now(pytz.timezone('Asia/Jakarta')).isoformat()
        }
        supabase_admin.table("market_prices").upsert(data, on_conflict="instrument").execute()
    except Exception:
        pass

def get_cached_market_price(symbol):
    try:
        supabase_admin = get_supabase_admin()
        res = supabase_admin.table("market_prices").select("price").eq("instrument", symbol).execute()
        if res and res.data:
            return res.data[0]["price"]
    except Exception:
        pass
    return None

def get_cached_market_price_full(symbol):
    try:
        supabase_admin = get_supabase_admin()
        res = supabase_admin.table("market_prices").select("*").eq("instrument", symbol).execute()
        if res and res.data:
            data = res.data[0]
            updated_at_str = data.get('updated_at', '')
            updated_at = safe_parse_timestamp(updated_at_str)
            if updated_at is None:
                return None
            if (datetime.now(pytz.UTC) - updated_at).total_seconds() < 5:
                return {
                    "price": data.get("price", 0),
                    "change_pct": data.get("change_pct", 0),
                    "updated_at": updated_at_str
                }
    except Exception:
        pass
    return None

def cleanup_old_data():
    try:
        supabase_admin = get_supabase_admin()
        cutoff = (datetime.now(pytz.timezone('Asia/Jakarta')) - timedelta(hours=24)).isoformat()
        supabase_admin.table("market_prices").delete().lt("updated_at", cutoff).execute()
    except Exception:
        pass

# ==============================================================================
# TICKER DATA (MARQUEE)
# ==============================================================================
def get_ticker_data():
    supabase_admin = get_supabase_admin()
    instruments_ticker = [
        "GOLD (XAUUSD)", "SILVER (XAGUSD)", "BITCOIN", "ETHEREUM",
        "EUR/USD", "GBP/USD", "BBRI", "TLKM", "BBCA", "ASII", "BMRI", "IHSG"
    ]
    try:
        res = supabase_admin.table("market_prices").select("instrument, price, change_pct").in_("instrument", instruments_ticker).execute()
        data = {row["instrument"]: {"price": row["price"], "change_pct": row.get("change_pct", 0)} for row in res.data}
        return data
    except Exception:
        return {}

# ##############################################################################
# USER & LICENSE MANAGEMENT
# ##############################################################################
def get_user_tier(user_id):
    if not user_id:
        return "free", None
    try:
        res = rest_api_request("GET", "user_tiers",
                               params={"user_id": f"eq.{user_id}", "select": "tier, expired_at"},
                               limit=1)
        if res and res.status_code == 200 and res.json():
            data = res.json()[0]
            tier = data.get("tier", "free")
            expired_at = data.get("expired_at")
            if expired_at:
                try:
                    expired_date = datetime.fromisoformat(expired_at.replace('Z', '+00:00'))
                    if datetime.now(pytz.UTC) > expired_date:
                        rest_api_request("PATCH", "user_tiers",
                                         params={"user_id": f"eq.{user_id}"},
                                         body={"tier": "free"})
                        return "free", None
                except:
                    pass
            return tier, expired_at
    except:
        pass
    return "free", None

def activate_key(user_id, key_code):
    if not user_id or not key_code:
        return False, "IDENTITY VERIFICATION REQUIRED"
    try:
        res = rest_api_request("GET", "activation_keys",
                               params={"key_code": f"eq.{key_code.upper().strip()}",
                                       "is_used": "eq.false",
                                       "select": "*"},
                               limit=1)
        if res is None or res.status_code != 200 or not res.json():
            return False, "INVALID OR EXPIRED LICENSE KEY"
        key_data = res.json()[0]
        tier = key_data.get("tier", "monthly")
        duration_days = key_data.get("duration_days", 30)
        expired_at = (datetime.now(pytz.UTC) + timedelta(days=duration_days)).isoformat()

        sync_user_to_supabase(user_id, st.session_state.get("user_email", ""),
                              st.session_state.get("user_name", ""))

        tier_data = {
            "tier": tier,
            "expired_at": expired_at,
            "activated_at": datetime.now(pytz.UTC).isoformat()
        }
        check = rest_api_request("GET", "user_tiers",
                                 params={"user_id": f"eq.{user_id}", "select": "id"},
                                 limit=1)
        if check is not None and check.status_code == 200 and check.json():
            rest_api_request("PATCH", "user_tiers",
                             params={"user_id": f"eq.{user_id}"},
                             body=tier_data)
        else:
            tier_data["user_id"] = user_id
            rest_api_request("POST", "user_tiers", body=tier_data)

        update_data = {
            "is_used": True,
            "used_by": user_id,
            "used_at": datetime.now(pytz.UTC).isoformat()
        }
        rest_api_request("PATCH", "activation_keys",
                         params={"key_code": f"eq.{key_code.upper().strip()}"},
                         body=update_data)

        return True, f"ACCESS GRANTED | TIER: {tier.upper()} | VALID UNTIL: {expired_at[:10]}"
    except Exception as e:
        return False, f"SYSTEM ERROR: {str(e)}"

def sync_user_to_supabase(user_id, email, name, avatar=""):
    try:
        supabase_admin = get_supabase_admin()
        existing = supabase_admin.table("users").select("id").eq("id", user_id).execute()
        if existing and existing.data:
            supabase_admin.table("users").update({
                "email": email,
                "name": name,
                "avatar": avatar,
                "last_login": datetime.now(pytz.UTC).isoformat()
            }).eq("id", user_id).execute()
        else:
            supabase_admin.table("users").insert({
                "id": user_id,
                "email": email,
                "name": name,
                "avatar": avatar,
                "created_at": datetime.now(pytz.UTC).isoformat(),
                "last_login": datetime.now(pytz.UTC).isoformat()
            }).execute()
            try:
                supabase_admin.table("user_tiers").upsert({
                    "user_id": user_id,
                    "tier": "free",
                    "activated_at": datetime.now(pytz.UTC).isoformat()
                }).execute()
            except Exception:
                pass
    except Exception:
        pass

def delete_user_with_verification(email, password):
    try:
        supabase_auth = get_supabase_client()
        resp = supabase_auth.auth.sign_in_with_password({"email": email.strip(), "password": password})
        if not resp or not resp.user:
            return False, "Verifikasi gagal. Pastikan email dan password benar."
        user_id = resp.user.id
        supabase_admin = get_supabase_admin()
        supabase_admin.table("user_tiers").delete().eq("user_id", user_id).execute()
        supabase_admin.table("users").delete().eq("id", user_id).execute()
        supabase_admin.auth.admin.delete_user(user_id)
        return True, "Akun berhasil dihapus permanen."
    except Exception as e:
        error_msg = str(e).lower()
        if "invalid login credentials" in error_msg or "invalid_grant" in error_msg:
            return False, "Email atau password salah. Tidak dapat menghapus akun."
        return False, f"Gagal menghapus akun: {str(e)}"

# ##############################################################################
# PERSISTENSI LIMIT HARIAN
# ##############################################################################
def get_user_usage(user_id):
    if not user_id:
        return 0, 0, 0
    try:
        supabase_admin = get_supabase_admin()
        res = supabase_admin.table("users").select("analysis_count, chatbot_count, sentinel_count, last_reset_date").eq("id", user_id).execute()
        if res and res.data and len(res.data) > 0:
            data = res.data[0]
            db_date = data.get("last_reset_date")
            today_str = datetime.now(pytz.UTC).date().isoformat()
            if db_date == today_str:
                return data.get("analysis_count", 0), data.get("chatbot_count", 0), data.get("sentinel_count", 0)
            else:
                supabase_admin.table("users").update({
                    "analysis_count": 0,
                    "chatbot_count": 0,
                    "sentinel_count": 0,
                    "last_reset_date": today_str
                }).eq("id", user_id).execute()
                return 0, 0, 0
    except Exception:
        pass
    return 0, 0, 0

def increment_user_usage(user_id, usage_type):
    if not user_id:
        return
    try:
        supabase_admin = get_supabase_admin()
        column_map = {"analysis": "analysis_count", "chatbot": "chatbot_count", "sentinel": "sentinel_count"}
        column = column_map.get(usage_type, "analysis_count")
        res = supabase_admin.table("users").select(column).eq("id", user_id).execute()
        if res and res.data and len(res.data) > 0:
            current_val = res.data[0].get(column, 0) or 0
            supabase_admin.table("users").update({column: current_val + 1}).eq("id", user_id).execute()
    except Exception:
        pass

# ##############################################################################
# SMART ALERT – LOAD FROM DATABASE
# ##############################################################################
def load_active_alerts_from_db(user_id):
    if not user_id:
        return
    try:
        supabase_admin = get_supabase_admin()
        res = supabase_admin.table("active_alerts").select("*")\
            .eq("user_id", user_id)\
            .eq("triggered", False)\
            .execute()
        if res and res.data:
            st.session_state.active_alerts = []
            for item in res.data:
                st.session_state.active_alerts.append({
                    "id": item["id"],
                    "instrument": item["instrument"],
                    "target": item["target"],
                    "target_display": format_price_display(item["target"], item["instrument"]),
                    "condition": item["condition"],
                    "chat_id": item["chat_id"],
                    "triggered": item.get("triggered", False),
                    "initial_price": item.get("initial_price")
                })
    except Exception:
        try:
            supabase_admin = get_supabase_admin()
            res = supabase_admin.table("active_alerts").select("*").eq("triggered", False).execute()
            if res and res.data:
                st.session_state.active_alerts = []
                for item in res.data:
                    st.session_state.active_alerts.append({
                        "id": item["id"],
                        "instrument": item["instrument"],
                        "target": item["target"],
                        "target_display": format_price_display(item["target"], item["instrument"]),
                        "condition": item["condition"],
                        "chat_id": item["chat_id"],
                        "triggered": item.get("triggered", False),
                        "initial_price": item.get("initial_price")
                    })
        except Exception:
            pass

# ##############################################################################
# AUTH SESSION RESTORE
# ##############################################################################
def restore_session():
    supabase_auth = get_supabase_client()
    try:
        session = supabase_auth.auth.get_session()
        if session and session.user:
            user = session.user
            st.session_state.auth_session = session.access_token
            st.session_state.user_id = user.id
            st.session_state.user_name = user.user_metadata.get("full_name") or \
                (user.email.split("@")[0] if user.email else "USER")
            st.session_state.user_email = user.email or ""
            st.session_state.user_avatar = user.user_metadata.get("avatar_url", "")
            tier, exp = get_user_tier(user.id)
            st.session_state.user_tier = tier
            st.session_state.user_expired_at = exp[:10] if exp else None
            sync_user_to_supabase(user.id, user.email or "", st.session_state.user_name, st.session_state.user_avatar)
            a_count, c_count, s_count = get_user_usage(user.id)
            st.session_state.daily_analysis_count = a_count
            st.session_state.daily_chatbot_count = c_count
            st.session_state.daily_sentinel_count = s_count
            load_active_alerts_from_db(user.id)
            send_log(f"AUTH: {st.session_state.user_name} ({st.session_state.user_email}) - Session Restored")
            return True
    except Exception:
        pass

    if st.session_state.get("auth_session"):
        return True
    return False

# ##############################################################################
# PRICE FETCHER
# ##############################################################################
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
                return {"price": float(data["price"]), "source": "TWELVEDATA"}
    except Exception:
        pass
    return None

def fetch_finnhub_price(symbol):
    finnhub_key = st.secrets.get("FINNHUB_KEY") or os.getenv("FINNHUB_KEY")
    if not finnhub_key:
        return None

    finnhub_client = finnhub.Client(api_key=finnhub_key)
    name_upper = str(symbol).upper() if symbol else ""

    if "BTC" in name_upper or "BITCOIN" in name_upper:
        finn_symbol = "BINANCE:BTCUSDT"
    elif "ETH" in name_upper or "ETHEREUM" in name_upper:
        finn_symbol = "BINANCE:ETHUSDT"
    elif "SOL" in name_upper or "SOLANA" in name_upper:
        finn_symbol = "BINANCE:SOLUSDT"
    elif "XRP" in name_upper:
        finn_symbol = "BINANCE:XRPUSDT"
    elif "BNB" in name_upper:
        finn_symbol = "BINANCE:BNBUSDT"
    elif "XAU" in name_upper or "GOLD" in name_upper:
        finn_symbol = "OANDA:XAU_USD"
    elif "XAG" in name_upper or "SILVER" in name_upper:
        finn_symbol = "OANDA:XAG_USD"
    elif "EUR" in name_upper and "USD" in name_upper:
        finn_symbol = "OANDA:EUR_USD"
    elif "GBP" in name_upper and "USD" in name_upper:
        finn_symbol = "OANDA:GBP_USD"
    elif "USD" in name_upper and "JPY" in name_upper:
        finn_symbol = "OANDA:USD_JPY"
    elif "AUD" in name_upper and "USD" in name_upper:
        finn_symbol = "OANDA:AUD_USD"
    elif "USD" in name_upper and "CHF" in name_upper:
        finn_symbol = "OANDA:USD_CHF"
    elif "USD" in name_upper and "CAD" in name_upper:
        finn_symbol = "OANDA:USD_CAD"
    elif "NZD" in name_upper and "USD" in name_upper:
        finn_symbol = "OANDA:NZD_USD"
    else:
        return None

    try:
        res = finnhub_client.quote(finn_symbol)
        if res and res.get('c') and res.get('c') > 0:
            return {"price": float(res['c']), "source": "FINNHUB"}
    except Exception:
        pass
    return None

# ##############################################################################
# PRICE FORMATTER
# ##############################################################################
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
    elif any(idx in name_upper for idx in ["NASDAQ", "S&P", "DOW", "DAX", "IHSG", "SP500"]):
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

# ##############################################################################
# API Key Configuration
# ##############################################################################
groq_api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
marketaux_key = st.secrets.get("MARKETAUX_KEY") or os.getenv("MARKETAUX_KEY")
currents_api_key = st.secrets.get("CURRENTS_API_KEY") or os.getenv("CURRENTS_API_KEY")
cerebras_api_key = st.secrets.get("CEREBRAS_API_KEY") or os.getenv("CEREBRAS_API_KEY")
sambanova_api_key = st.secrets.get("SAMBANOVA_API_KEY") or os.getenv("SAMBANOVA_API_KEY")
cohere_api_key = st.secrets.get("COHERE_API_KEY") or os.getenv("COHERE_API_KEY")
nvidia_api_key = st.secrets.get("NVIDIA_API_KEY") or os.getenv("NVIDIA_API_KEY")
coinmarketcap_api_key = st.secrets.get("COINMARKETCAP_API_KEY") or os.getenv("COINMARKETCAP_API_KEY")
newsapi_key = st.secrets.get("NEWSAPI_KEY") or os.getenv("NEWSAPI_KEY")
tiingo_key = st.secrets.get("TIINGO_KEY") or os.getenv("TIINGO_KEY")
openrouter_api_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
puter_auth_token = st.secrets.get("PUTER_AUTH_TOKEN") or os.getenv("PUTER_AUTH_TOKEN")
alpha_vantage_key = st.secrets.get("ALPHA_VANTAGE_KEY") or os.getenv("ALPHA_VANTAGE_KEY")

client = None
if groq_api_key:
    try:
        client = Groq(api_key=groq_api_key)
    except Exception as e:
        st.sidebar.error(f"SYSTEM ERROR: {str(e)}")
else:
    st.sidebar.error("API CONFIGURATION REQUIRED")

# ==============================================================================
# FUNGSI AI BACKUP
# ==============================================================================
def call_puter_ai(system_prompt, user_prompt, model="claude-opus-4-5", max_tokens=2500, temperature=0.5, timeout=70):
    if not puter_auth_token:
        return None
    try:
        headers = {"Authorization": f"Bearer {puter_auth_token}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        resp = requests.post("https://api.puter.com/puterai/openai/v1/chat/completions", headers=headers, json=payload, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("choices") and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
    except Exception:
        pass
    return None

def call_openrouter(system_prompt, user_prompt, model='nousresearch/hermes-3-llama-3.1-405b', max_tokens=2000, temperature=0.6, timeout=60):
    if not openrouter_api_key: return None
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {openrouter_api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]},
            timeout=timeout
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
    except:
        pass
    return None

def call_cerebras(system_prompt, user_prompt, model="llama-3.3-70b", max_tokens=2000, temperature=0.6, timeout=45):
    if not cerebras_api_key or Cerebras is None: return None
    try:
        cerebras_client = Cerebras(api_key=cerebras_api_key)
        completion = cerebras_client.chat.completions.create(
            messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}],
            model=model, max_completion_tokens=max_tokens, temperature=temperature, stream=False
        )
        if completion and completion.choices:
            return completion.choices[0].message.content
    except:
        pass
    return None

def call_sambanova(system_prompt, user_prompt, model="MiniMax-M2.5", max_tokens=2000, temperature=0.6, timeout=45):
    if not sambanova_api_key: return None
    try:
        response = requests.post(
            url="https://api.sambanova.ai/v1/chat/completions",
            headers={"Authorization":f"Bearer {sambanova_api_key}","Content-Type":"application/json"},
            json={"model":model,"messages":[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}],"max_tokens":max_tokens,"temperature":temperature,"stream":False},
            timeout=timeout
        )
        if response.status_code==200:
            return response.json()['choices'][0]['message']['content']
    except:
        pass
    return None

def call_cohere(system_prompt, user_prompt, model="command-a-03-2025", max_tokens=2000, temperature=0.7, timeout=45):
    if not cohere_api_key or cohere is None: return None
    try:
        co = cohere.ClientV2(api_key=cohere_api_key)
        combined = f"{system_prompt}\n\n{user_prompt}"
        res = co.chat(model=model, messages=[{"role":"user","content":combined}], max_tokens=max_tokens, temperature=temperature)
        if res and hasattr(res,'message') and res.message:
            if hasattr(res.message,'content') and res.message.content:
                return res.message.content[0].text if isinstance(res.message.content,list) else str(res.message.content)
    except:
        pass
    return None

def call_nvidia_nim(system_prompt, user_prompt, model="meta/llama-3.3-70b-instruct", max_tokens=2000, temperature=0.7, timeout=45):
    if not nvidia_api_key: return None
    try:
        response = requests.post(
            url="https://integrate.api.nvidia.com/v1/chat/completions",
            headers={"Authorization":f"Bearer {nvidia_api_key}","Content-Type":"application/json"},
            json={"model":model,"messages":[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}],"max_tokens":max_tokens,"temperature":temperature},
            timeout=timeout
        )
        if response.status_code==200:
            return response.json()['choices'][0]['message']['content']
    except:
        pass
    return None

def fetch_coinmarketcap_news(max_articles=10):
    if not coinmarketcap_api_key: return []
    try:
        headers = {"X-CMC_PRO_API_KEY":coinmarketcap_api_key}
        resp = requests.get("https://pro-api.coinmarketcap.com/v1/content/posts/latest", headers=headers, params={"limit":max_articles}, timeout=10)
        if resp.status_code==200:
            articles = []
            for post in resp.json().get("data",[]):
                articles.append({"publishedAt":post.get("created_at",datetime.now().isoformat()),"title":post.get("title","NO TITLE"),"description":post.get("subtitle",post.get("title","")),"source":"COINMARKETCAP CRYPTO","url":post.get("url","#")})
            return articles
    except:
        pass
    return []

# ==============================================================================
# FUNGSI MAKROEKONOMI (WORLD BANK)
# ==============================================================================
@st.cache_data(ttl=86400)
def get_macro_data(country_name="Indonesia"):
    country_map = {
        "Indonesia": "IDN", "United States": "USA", "China": "CHN", "Japan": "JPN",
        "Germany": "DEU", "India": "IND", "United Kingdom": "GBR", "France": "FRA",
        "Brazil": "BRA", "Russia": "RUS", "Australia": "AUS", "Singapore": "SGP",
        "Malaysia": "MYS", "Thailand": "THA", "Vietnam": "VNM", "Philippines": "PHL"
    }
    country_code = country_map.get(country_name, "IDN")
    indicators = {
        "GDP": "NY.GDP.MKTP.CD",
        "Unemployment Rate": "SL.UEM.TOTL.ZS",
        "Gov. Debt to GDP": "GC.DOD.TOTL.GD.ZS",
        "Inflation Rate": "FP.CPI.TOTL.ZG",
    }
    macro_data = {}
    try:
        for name, code in indicators.items():
            try:
                data = wb.data.DataFrame(code, country_code, mrv=1)
                if not data.empty:
                    value = data.iloc[0, -1]
                    if pd.notna(value):
                        if name == "GDP":
                            macro_data[name] = f"{value / 1_000_000_000_000:.2f} Triliun USD"
                        else:
                            macro_data[name] = f"{value:.2f}%"
                    else:
                        macro_data[name] = "Tidak tersedia"
                else:
                    macro_data[name] = "Tidak tersedia"
            except Exception:
                macro_data[name] = "Tidak tersedia"
        macro_data["Interest Rate"] = "Data tidak tersedia"
    except Exception as e:
        for key in ["GDP", "Unemployment Rate", "Gov. Debt to GDP", "Inflation Rate", "Interest Rate"]:
            macro_data[key] = "Tidak tersedia"
    return macro_data

# ==============================================================================
# DATA HISTORIS IHSG & SAHAM IDX (ALPHA VANTAGE)
# ==============================================================================
def get_id_historical_data(symbol, period="1mo", interval="1d"):
    if not alpha_vantage_key:
        st.warning("⚠️ Konfigurasi kunci API untuk data pasar belum lengkap.")
        return pd.DataFrame()
    if symbol.upper() == "^JKSE":
        ticker = "JKSE"
    else:
        ticker = symbol.upper().replace(".JK", "")
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}.JK&apikey={alpha_vantage_key}"
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            quote = data.get("Global Quote", {})
            if quote:
                price = float(quote.get("05. price", 0))
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                dates = pd.date_range(start=start_date, end=end_date, freq='D')
                df = pd.DataFrame(index=dates)
                df["Open"] = price
                df["High"] = price
                df["Low"] = price
                df["Close"] = price
                df["Volume"] = 0
                df.index = pd.to_datetime(df.index)
                df.sort_index(inplace=True)
                return df[["Open", "High", "Low", "Close", "Volume"]]
            else:
                st.warning(f"⚠️ Data untuk {symbol} sedang dalam proses perbaikan.")
        else:
            st.warning(f"⚠️ Data untuk {symbol} sedang dalam proses perbaikan.")
    except Exception:
        st.warning(f"⚠️ Data untuk {symbol} sedang dalam proses perbaikan.")
    return pd.DataFrame()

def get_historical_data(ticker_symbol, period="1mo", interval="1h"):
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty: return pd.DataFrame()
        return df.sort_index().dropna()
    except: return pd.DataFrame()

def get_market_data(ticker_symbol):
    try:
        inst_name = ticker_symbol
        for cat in instruments.values():
            for name, tick in cat.items():
                if tick == ticker_symbol: inst_name = name; break
        twelve_result = fetch_twelvedata_price(inst_name)
        if twelve_result and twelve_result.get("price", 0) > 0:
            cache_market_price(inst_name, twelve_result["price"], 0)
            return {"price": twelve_result["price"], "change": 0, "change_pct": 0, "source": "TWELVEDATA", "spread": 0}
        finnhub_result = fetch_finnhub_price(inst_name)
        if finnhub_result and finnhub_result.get("price",0)>0:
            cache_market_price(inst_name, finnhub_result["price"],0)
            return {"price":finnhub_result["price"],"change":0,"change_pct":0,"source":finnhub_result.get("source","FINNHUB"),"spread":0}
        supabase_admin = get_supabase_admin()
        res = supabase_admin.table("market_prices").select("*").eq("instrument",inst_name).execute()
        if res and res.data:
            cached = res.data[0]
            updated_at_str = cached.get('updated_at','')
            if isinstance(updated_at_str,str) and updated_at_str:
                updated_at_str = updated_at_str.replace('Z','+00:00')
                try: updated_at = datetime.fromisoformat(updated_at_str)
                except: updated_at = datetime.now(pytz.UTC) - timedelta(seconds=10)
            else: updated_at = datetime.now(pytz.UTC) - timedelta(seconds=10)
            if updated_at.tzinfo is None: updated_at = updated_at.replace(tzinfo=pytz.UTC)
            if (datetime.now(pytz.UTC) - updated_at).total_seconds()<5:
                return {"price":cached.get('price',0),"change":cached.get('price',0)*(cached.get('change_pct',0)/100),"change_pct":cached.get('change_pct',0),"source":"CACHE"}
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="2d")
        if not hist.empty:
            price = float(hist["Close"].iloc[-1])
            prev_close = float(hist["Close"].iloc[-2]) if len(hist)>1 else float(hist["Open"].iloc[-1])
            change_pct = ((price-prev_close)/prev_close)*100 if prev_close>0 else 0
            cache_market_price(inst_name, price, change_pct)
            return {"price":price,"change":price-prev_close,"change_pct":change_pct,"source":"LIVE"}
        return None
    except: return None

def add_technical_indicators(df):
    if len(df)<50: return df
    df["SMA20"] = df["Close"].rolling(window=20).mean()
    df["SMA50"] = df["Close"].rolling(window=50).mean()
    df["SMA200"] = df["Close"].rolling(window=min(len(df),200)).mean()
    df["EMA9"] = df["Close"].ewm(span=9, adjust=False).mean()
    df["EMA21"] = df["Close"].ewm(span=21, adjust=False).mean()
    delta = df["Close"].diff()
    gain = delta.where(delta>0,0).rolling(window=14).mean()
    loss = -delta.where(delta<0,0).rolling(window=14).mean()
    rs = gain / loss.replace(0,0.001)
    df["RSI"] = 100 - (100/(1+rs))
    exp1 = df["Close"].ewm(span=12, adjust=False).mean()
    exp2 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = exp1 - exp2
    df["Signal_Line"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["BB_Mid"] = df["Close"].rolling(window=20).mean()
    df["BB_Std"] = df["Close"].rolling(window=20).std()
    df["BB_Upper"] = df["BB_Mid"] + (df["BB_Std"]*2)
    df["BB_Lower"] = df["BB_Mid"] - (df["BB_Std"]*2)
    low_14 = df["Low"].rolling(window=14).min()
    high_14 = df["High"].rolling(window=14).max()
    df["Stoch_K"] = 100 * ((df["Close"]-low_14)/(high_14-low_14).replace(0,0.001))
    df["Stoch_D"] = df["Stoch_K"].rolling(window=3).mean()
    high_low = df["High"] - df["Low"]
    high_cp = np.abs(df["High"] - df["Close"].shift())
    low_cp = np.abs(df["Low"] - df["Close"].shift())
    df["TR"] = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
    df["ATR"] = df["TR"].rolling(window=14).mean()
    df["UpMove"] = df["High"] - df["High"].shift()
    df["DownMove"] = df["Low"].shift() - df["Low"]
    df["+DM"] = np.where((df["UpMove"]>df["DownMove"])&(df["UpMove"]>0), df["UpMove"],0)
    df["-DM"] = np.where((df["DownMove"]>df["UpMove"])&(df["DownMove"]>0), df["DownMove"],0)
    df["+DI"] = 100 * (df["+DM"].rolling(14).mean() / df["ATR"].replace(0,0.001))
    df["-DI"] = 100 * (df["-DM"].rolling(14).mean() / df["ATR"].replace(0,0.001))
    df["DX"] = 100 * np.abs(df["+DI"]-df["-DI"]) / (df["+DI"]+df["-DI"]).replace(0,0.001)
    df["ADX"] = df["DX"].rolling(14).mean()
    df["CCI"] = ta.trend.cci(df["High"], df["Low"], df["Close"], window=20)
    df["WPR"] = ta.momentum.williams_r(df["High"], df["Low"], df["Close"], lbp=14)
    df["MFI"] = ta.volume.money_flow_index(df["High"], df["Low"], df["Close"], df["Volume"], window=14)
    df["TRIX"] = ta.trend.trix(df["Close"], window=15)
    df["ROC"] = ta.momentum.roc(df["Close"], window=12)
    df["AO"] = ta.momentum.awesome_oscillator(df["High"], df["Low"], window1=5, window2=34)
    df["KAMA"] = ta.momentum.kama(df["Close"], window=10, pow1=2, pow2=30)
    df["Ichimoku_A"] = ta.trend.ichimoku_a(df["High"], df["Low"], window1=9, window2=26)
    df["Ichimoku_B"] = ta.trend.ichimoku_b(df["High"], df["Low"], window2=26, window3=52)
    psar_up = ta.trend.psar_up(df["High"], df["Low"], df["Close"])
    psar_down = ta.trend.psar_down(df["High"], df["Low"], df["Close"])
    df["Parabolic_SAR"] = psar_up.fillna(psar_down)
    df["Vol_SMA"] = df["Volume"].rolling(window=20).mean()
    df["Base_Line"] = (df["High"].rolling(window=26).max() + df["Low"].rolling(window=26).min())/2
    return df

def get_weighted_signal(df):
    required_cols = ['RSI', 'MACD', 'Signal_Line', 'SMA50', 'SMA200', 'CCI', 'WPR', 'MFI', 'EMA9', 'EMA21', 'ADX', 'Stoch_K', 'ATR', 'ROC', 'TRIX', 'AO', 'KAMA', 'Ichimoku_A', 'Ichimoku_B', 'Parabolic_SAR', 'BB_Upper', 'BB_Lower']
    for col in required_cols:
        if col not in df.columns:
            return 0, "WAITING", ["INITIALIZING INDICATORS..."], 0, 0, 100

    latest = df.iloc[-1]
    atr_mean = df['ATR'].mean() if not df['ATR'].isna().all() else 0

    rules = []
    rsi = latest['RSI']
    rules.append(('RSI', 'bullish' if rsi < 30 else 'bearish' if rsi > 70 else 'neutral'))
    rules.append(('MACD', 'bullish' if latest['MACD'] > latest['Signal_Line'] else 'bearish'))
    rules.append(('SMA50', 'bullish' if latest['Close'] > latest['SMA50'] else 'bearish'))
    rules.append(('SMA200', 'bullish' if latest['Close'] > latest['SMA200'] else 'bearish'))
    cci = latest['CCI']
    rules.append(('CCI', 'bullish' if cci < -100 else 'bearish' if cci > 100 else 'neutral'))
    wpr = latest['WPR']
    rules.append(('Williams %R', 'bullish' if wpr < -80 else 'bearish' if wpr > -20 else 'neutral'))
    mfi = latest['MFI']
    rules.append(('MFI', 'bullish' if mfi < 20 else 'bearish' if mfi > 80 else 'neutral'))
    rules.append(('EMA Cross', 'bullish' if latest['EMA9'] > latest['EMA21'] else 'bearish'))
    adx = latest['ADX']
    rules.append(('ADX', 'bullish' if adx > 25 else 'bearish' if adx < 20 else 'neutral'))
    stoch = latest['Stoch_K']
    rules.append(('Stoch K', 'bullish' if stoch < 20 else 'bearish' if stoch > 80 else 'neutral'))
    atr_val = latest['ATR']
    rules.append(('ATR', 'bullish' if atr_val > atr_mean else 'bearish' if atr_val < atr_mean else 'neutral'))
    roc = latest['ROC']
    rules.append(('ROC', 'bullish' if roc > 0 else 'bearish'))
    trix = latest['TRIX']
    rules.append(('TRIX', 'bullish' if trix > 0 else 'bearish'))
    ao = latest['AO']
    rules.append(('AO', 'bullish' if ao > 0 else 'bearish'))
    kama = latest['KAMA']
    rules.append(('KAMA', 'bullish' if latest['Close'] > kama else 'bearish'))
    ichi_a = latest['Ichimoku_A']
    rules.append(('Ichimoku A', 'bullish' if latest['Close'] > ichi_a else 'bearish'))
    ichi_b = latest['Ichimoku_B']
    rules.append(('Ichimoku B', 'bullish' if latest['Close'] > ichi_b else 'bearish'))
    psar = latest['Parabolic_SAR']
    rules.append(('Parabolic SAR', 'bullish' if latest['Close'] > psar else 'bearish'))
    bb_upper = latest['BB_Upper']
    rules.append(('BB Upper', 'bearish' if latest['Close'] > bb_upper else 'neutral'))
    bb_lower = latest['BB_Lower']
    rules.append(('BB Lower', 'bullish' if latest['Close'] < bb_lower else 'neutral'))

    bullish = sum(1 for _, v in rules if v == 'bullish')
    bearish = sum(1 for _, v in rules if v == 'bearish')
    neutral = sum(1 for _, v in rules if v == 'neutral')
    total = bullish + bearish + neutral
    score = (bullish / total) * 100 if total > 0 else 50

    reasons = [f"{name}: {'BULL' if val=='bullish' else 'BEAR' if val=='bearish' else 'NEUT'}" for name, val in rules]

    if score > 70: signal = "STRONG BUY"
    elif score > 55: signal = "BUY"
    elif score < 30: signal = "STRONG SELL"
    elif score < 45: signal = "SELL"
    else: signal = "NEUTRAL"

    return score, signal, reasons, bullish, bearish, neutral

# ==============================================================================
# STYLING: UNTUK SENTINEL SAJA (DENGAN WARNA NEON)
# ==============================================================================
def style_sentinel_output(analysis):
    """Warnai angka desimal dan label Entry/SL/TP untuk Sentinel."""
    if '<span style=' in analysis: 
        return analysis
    
    # Warnai angka desimal
    analysis = re.sub(r"(\d+\.\d+)", r"<span style='color:#00ff88;font-weight:bold;text-shadow:0 0 3px #00ff88;'>\1</span>", analysis)
    # Warnai angka integer besar
    analysis = re.sub(r"(\d{3,})", r"<span style='color:#00ff88;font-weight:bold;'>\1</span>", analysis)
    
    # Warnai label
    patterns = [
        (r"(Zona Injeksi Ideal \(Entry\):)", r"<span style='color:#00ff88;font-weight:bold;text-shadow:0 0 3px #00ff88;'>\1</span>"),
        (r"(Zona Entry Presisi:)", r"<span style='color:#00ff88;font-weight:bold;text-shadow:0 0 3px #00ff88;'>\1</span>"),
        (r"(Entry Zone)", r"<span style='color:#00ff88;font-weight:bold;'>\1</span>"),
        (r"(Stop Loss:)", r"<span style='color:#ff2a6d;font-weight:bold;text-shadow:0 0 3px #ff2a6d;'>\1</span>"),
        (r"(Invalidasi \(Dynamic SL\):)", r"<span style='color:#ff2a6d;font-weight:bold;text-shadow:0 0 3px #ff2a6d;'>\1</span>"),
        (r"(SL \(2×ATR\))", r"<span style='color:#ff2a6d;font-weight:bold;'>\1</span>"),
        (r"(Take Profit \d:)", r"<span style='color:#00ff88;font-weight:bold;text-shadow:0 0 3px #00ff88;'>\1</span>"),
        (r"(Proyeksi Target \(TP\d*\):)", r"<span style='color:#00ff88;font-weight:bold;text-shadow:0 0 3px #00ff88;'>\1</span>"),
        (r"(TP\d)", r"<span style='color:#00ff88;font-weight:bold;'>\1</span>"),
    ]
    for pattern, replacement in patterns:
        analysis = re.sub(pattern, replacement, analysis, flags=re.IGNORECASE)
    
    return analysis

def style_deep_output(analysis):
    """Deep Analysis: tidak ada warna, hanya return asli."""
    return analysis

# ==============================================================================
# AI FUNCTIONS (GROQ, SENTINEL, DEEP)
# ==============================================================================
def get_groq_response(question, context=""):
    if not client: return "ERROR: SYSTEM CONFIGURATION REQUIRED"
    user_limits = LIMITS.get(st.session_state.user_tier, LIMITS["free"])
    if st.session_state.daily_chatbot_count >= user_limits["chatbot_per_day"]:
        return f"LIMIT REACHED [{st.session_state.daily_chatbot_count}/{user_limits['chatbot_per_day']}] | UPGRADE TIER"
    MODEL_NAME = 'llama-3.3-70b-versatile'
    system_prompt = f"Kamu adalah mentor trading berpengalaman yang ramah. Berikan jawaban singkat, padat, dan jelas dalam Bahasa Indonesia. Sampaikan seperti manusia biasa, bukan robot. Fokus pada inti pertanyaan, tanpa basa-basi. Konteks: {context}. Waktu sekarang: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB."
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role":"system","content":system_prompt},{"role":"user","content":question}],
            model=MODEL_NAME, temperature=0.8, max_tokens=1024,
        )
        st.session_state.daily_chatbot_count += 1
        increment_user_usage(st.session_state.user_id, "chatbot")
        return chat_completion.choices[0].message.content
    except Exception as e:
        result = call_cerebras(system_prompt, question, model="llama-3.3-70b", max_tokens=1024, temperature=0.8)
        if result:
            st.session_state.daily_chatbot_count += 1; increment_user_usage(st.session_state.user_id, "chatbot")
            return f"[VIA CEREBRAS BACKUP]\n\n{result}"
        result = call_sambanova(system_prompt, question, model="MiniMax-M2.5", max_tokens=1024, temperature=0.8)
        if result:
            st.session_state.daily_chatbot_count += 1; increment_user_usage(st.session_state.user_id, "chatbot")
            return f"[VIA SAMBANOVA BACKUP]\n\n{result}"
        return f"SYSTEM ERROR: {str(e)}"

def get_sentinel_analysis(asset_name, market_data, df, signal, reasons):
    user_limits = LIMITS.get(st.session_state.user_tier, LIMITS["free"])
    if user_limits["sentinel_per_day"] == 0:
        return "SENTINEL PRO ACCESS RESTRICTED | UPGRADE TIER"
    if st.session_state.daily_sentinel_count >= user_limits["sentinel_per_day"]:
        return f"LIMIT REACHED [{st.session_state.daily_sentinel_count}/{user_limits['sentinel_per_day']}] | UPGRADE TIER"

    timeframe_key = f"{st.session_state.current_period}_{st.session_state.current_interval}"
    cached = get_cached_ai_analysis(asset_name, "sentinel", timeframe_key)
    if cached:
        return f"""<div class="sentinel-cyber-report">{cached}</div>"""

    latest = df.iloc[-1]
    price = market_data['price']
    news_list, _ = get_news_data(asset_name, max_articles=5)
    news_context = "\n".join([f"> {n['title']}: {n.get('description','')[:120]}" for n in news_list]) if news_list else "NO NEWS DATA AVAILABLE"

    # PROMPT SENTINEL TANPA BORDER (seperti sebelumnya)
    sentinel_prompt = f"""AEROVULPIS QUANTUM CORE V4.0 [TERMINAL MODE]
ASSET: {asset_name} | TIME: {datetime.now().strftime('%d %b %Y')} | SIGNAL: {signal}
CAPITAL: $1000
...

[1] QUANTUM STRUCTURE & LIQUIDITY MAP
- Wyckoff Phase & Intent: [Analisis]
- GARCH Volatility (24h): [Nilai] | Implikasi: [Singkat]
- Entropy & ADX Regime: [Nilai] | ADX: [Nilai]
- Buy-Side Liquidity Pool: [Zona]
- Sell-Side Liquidity Pool: [Zona]
- Unmitigated FVG / Voids: [Zona]
- Multi-TF Alignment Score: 1H:[X] 4H:[X] D1:[X] | Confluence: [X/3]

[2] SMC & PREDICTIVE KEY LEVELS
• Institutional Supply (Resistance): [Zona1] | [Zona2] | [Zona3]
• Institutional Demand (Support): [Zona1] | [Zona2] | [Zona3]
• Volume PoC / VAH / VAL: [PoC] / [VAH] / [VAL]
• Fibonacci Liquidity Hunt Map:
  - 0.618 (Discount): [Zona]
  - 1.272 (Std Ext): [Zona]
  - 1.618 (Golden): [Zona]
  - 2.618 (Inst. Hunt): [Zona]

[3] MACROECONOMIC CATALYST & SENTIMENT
• News Impact Score: [X/10] | Bias: [Bullish/Bearish]
• Intermarket: [Sintesis DXY/Yields]
• Crowd vs Smart Money: [Retail vs COT]

[4] EXECUTION VECTORS (COMPARATIVE MATRIX)

🟢 LONG SCENARIO (Prob: X%)
- Zona Injeksi Ideal (Entry): [Rentang Presisi]
- Trigger Konfirmasi: [Syarat Teknikal]
- Invalidasi (Dynamic SL): [Level] = Entry - (2 × ATR)
- Proyeksi Target: TP1 [Level] | TP2 [Level] | TP3 [Level]
- Risk:Reward: [X:1]
- Kelly Criterion Sizing: [X%] risk = [X] lot

🔴 SHORT SCENARIO (Prob: Y%)
- Zona Injeksi Ideal (Entry): [Rentang Presisi]
- Trigger Konfirmasi: [Syarat Teknikal]
- Invalidasi (Dynamic SL): [Level] = Entry + (2 × ATR)
- Proyeksi Target: TP1 [Level] | TP2 [Level] | TP3 [Level]
- Risk:Reward: [Y:1]
- Kelly Criterion Sizing: [Y%] risk = [Y] lot

[5] MONTE CARLO RISK & TAIL EVENTS
• P5 / P50 / P95 (7d): [Nilai] / [Nilai] / [Nilai]
• Expected Value (EV): $[X] | Probability of Profit: [X%]
• Black Swan Vulnerability: [X/10] | Hedge: [Yes/No]

[FINAL ALGORITHMIC VERDICT]
- DECISION: [STRONG BUY / BUY / NEUTRAL / SELL / STRONG SELL]
- INSTRUCTION: [Eksekusi Market / Limit Order / Hindari]
- TRADE MANAGEMENT: [Aturan Trailing Stop & Partial Profit]
- KILL SWITCH: [Kondisi pembatalan setup]
- PROBABILITY EDGE: [X%]                                                   
"""
    system_msg = """You are AeroVulpis Quantum Core. Provide the analysis strictly following the format above. Use bullet points and simple formatting. No ASCII borders or tables. Replace [...] with actual calculated values. Keep each line concise (max 15 words). Use Indonesian language. Do NOT refuse to answer. Provide technical analysis directly. You MUST complete the analysis. Never say you cannot predict. Use the data given to make a forecast."""

    analysis = None
    analysis = call_puter_ai(system_msg, sentinel_prompt, model="claude-opus-4-5", max_tokens=2500, temperature=0.5)
    if not analysis:
        analysis = call_openrouter(system_msg, sentinel_prompt, model='nousresearch/hermes-3-llama-3.1-405b', max_tokens=2500, temperature=0.5)
    if not analysis:
        analysis = call_cohere(system_msg, sentinel_prompt, model="command-a-03-2025", max_tokens=2500, temperature=0.5)
    if not analysis:
        analysis = call_nvidia_nim(system_msg, sentinel_prompt, model="meta/llama-3.3-70b-instruct", max_tokens=2500, temperature=0.5)
    if not analysis:
        analysis = call_cerebras(system_msg, sentinel_prompt, model="llama-3.3-70b", max_tokens=2500, temperature=0.5)
    if not analysis:
        return "ALL NEURAL SYSTEMS AT CAPACITY | PLEASE RETRY"

    analysis = style_sentinel_output(analysis)

    st.session_state.daily_sentinel_count += 1
    increment_user_usage(st.session_state.user_id, "sentinel")
    analysis += "\n\n---\n*Ingat, analisis ini hanyalah pandangan objektif dari sistem AeroVulpis. Selalu padukan dengan analisis dan strategi Anda sendiri sebelum mengambil keputusan trading.*"
    analysis += "\n\n⚠️ *Simpan hasil analisis ini di catatan Anda. Halaman mungkin di-refresh otomatis.*"

    cache_ai_analysis(asset_name, analysis, "sentinel", timeframe_key)
    st.session_state.sentinel_analysis = f"""<div class="sentinel-cyber-report">{analysis}</div>"""
    return st.session_state.sentinel_analysis

def get_deep_analysis(asset_name, market_data, df, signal, reasons):
    if not client: return "ERROR: SYSTEM CONFIGURATION REQUIRED"

    timeframe_key = f"{st.session_state.current_period}_{st.session_state.current_interval}"
    cached = get_cached_ai_analysis(asset_name, "deep", timeframe_key)
    if cached:
        st.session_state.deep_analysis_result = cached
        return cached

    user_limits = LIMITS.get(st.session_state.user_tier, LIMITS["free"])
    if st.session_state.daily_analysis_count >= user_limits["analysis_per_day"]:
        return f"DAILY LIMIT REACHED | UPGRADE TIER"

    MODEL_NAME = 'llama-3.3-70b-versatile'
    latest = df.iloc[-1]
    price = market_data['price']
    
    technical_data = f"""INSTRUMENT: {asset_name} | SIGNAL: {signal}
RSI (14): {latest.get('RSI',0):.2f} | MACD: {latest.get('MACD',0):.4f} | Signal Line: {latest.get('Signal_Line',0):.4f}
SMA 50: {latest.get('SMA50',0):.4f} | SMA 200: {latest.get('SMA200',0):.4f} | ATR (14): {latest.get('ATR',0):.4f}
ADX (14): {latest.get('ADX',0):.2f} | BB: [{latest.get('BB_Lower',0):.4f} - {latest.get('BB_Upper',0):.4f}]
Stochastic K: {latest.get('Stoch_K',0):.2f} | CCI: {latest.get('CCI',0):.2f} | Volume: {df['Volume'].iloc[-1]:,.0f}
Williams %R: {latest.get('WPR',0):.2f} | MFI: {latest.get('MFI',0):.2f}
TECHNICAL REASONS: {', '.join(reasons)}"""

    system_prompt = """AEROVULPIS DEEP ANALYSIS ENGINE V4.0. Bertindaklah sebagai Senior Technical Analyst di proprietary trading firm. Gunakan Bahasa Indonesia yang LUGAS, PRESISI, dan BERORIENTASI EKSEKUSI. Hindari bahasa spekulatif. Gunakan kalimat imperatif dan probabilistik terukur. JANGAN gunakan kode HTML atau span warna. Berikan analisis dalam teks biasa. JANGAN tolak memberikan analisis. Gunakan data yang diberikan untuk membuat prediksi."""

    user_prompt = f"""DEEP ANALYSIS REQUEST — SHARP EDITION: {technical_data}
INSTRUMENT: {asset_name}
TIMEFRAME FOCUS: Multi-Timeframe (30m, 1H, 4H, Daily)

### WAJIB MASUKKAN:

**1. STRUKTUR PASAR & TREND ANALYSIS:**
- Identifikasi Market Structure: Higher High/Higher Low (uptrend) atau Lower High/Lower Low (downtrend) pada 3 timeframe.
- Klasifikasi fase tren: Akumulasi, Markup, Distribusi, atau Markdown (Wyckoff Framework).
- Skor kekuatan tren dari 1-10 berdasarkan ADX, slope SMA, dan konsistensi price action.

**2. INTERPRETASI INDIKATOR (Kontekstual, BUKAN sekadar angka):**
- RSI (14): Apakah ada divergence? Overbought/Oversold dalam konteks tren atau reversal?
- MACD: Histogram momentum, crossover, dan posisinya relatif terhadap zero line.
- Posisi harga vs SMA 50 & 200: Golden Cross/Death Cross? Harga sebagai support/resistance dinamis?

**3. ZONA KRITIS:**
- Minimal 3 Support krusial (dengan alasan struktural: swing low, demand zone, Fibonacci).
- Minimal 3 Resistance krusial (dengan alasan struktural: swing high, supply zone, Fibonacci).
- Volume Profile: Identifikasi Point of Control (PoC) dan Value Area.

**4. RENCANA EKSEKUSI (WAJIB 2 SETUP):**

**SETUP #1 — Skenario Bullish:**
- Zona Entry Presisi: [Rentang harga]
- Trigger Konfirmasi: [Candle pattern + indikator + volume]
- Stop Loss: [Level] = Entry - (1.5 × ATR). Jelaskan alasan struktural.
- Take Profit 1: [Level] | Rasio Risk:Reward [X:1]
- Take Profit 2: [Level] | Rasio Risk:Reward [X:1]
- Probabilitas Setup: [X%] dengan justifikasi.
- Position Sizing: Risiko 1% dari modal $1000 = $[X]. Hitung jumlah unit/lot.

**SETUP #2 — Skenario Bearish:**
- Zona Entry Presisi: [Rentang harga]
- Trigger Konfirmasi: [Candle pattern + indikator + volume]
- Stop Loss: [Level] = Entry + (1.5 × ATR). Jelaskan alasan struktural.
- Take Profit 1: [Level] | Rasio Risk:Reward [X:1]
- Take Profit 2: [Level] | Rasio Risk:Reward [X:1]
- Probabilitas Setup: [X%] dengan justifikasi.
- Position Sizing: Risiko 2% dari modal $1000 = $[X]. Hitung jumlah unit/lot.

**5. MANAJEMEN RISIKO & TRADE MANAGEMENT:**
- Aturan Trailing Stop: Kapan dan bagaimana menggeser SL ke BEP?
- Partial Profit Taking: Di level mana ambil 50% profit?
- Invalidation Condition: Kapan setup dianggap gagal total?

**6. KESIMPULAN AKHIR:**
- Bias Dominan Jangka Pendek: [BULLISH / BEARISH / NEUTRAL]
- Key Catalyst: [Satu faktor penentu yang akan menggerakkan harga minggu ini]
- Action Plan: [Entry sekarang / Tunggu konfirmasi / Hindari pasar]
- Confidence Level: [X/10]

### ATURAN OUTPUT:
- Minimal 600 kata.
- Gunakan bullet points, tabel, dan format numerik yang rapi.
- JANGAN memberikan nasihat investasi umum. Fokus pada eksekusi teknikal.
- JANGAN menggunakan kode HTML atau tag span. Teks biasa saja.
- JANGAN menolak untuk memberikan analisis. Gunakan data yang tersedia.
"""
    analysis = None
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}],
            model=MODEL_NAME, temperature=0.6, max_tokens=2500,
        )
        analysis = chat_completion.choices[0].message.content
    except:
        analysis = call_cerebras(system_prompt, user_prompt, model="llama-3.3-70b", max_tokens=2500, temperature=0.6)
        if analysis:
            analysis = f"[VIA CEREBRAS BACKUP]\n\n{analysis}"
        else:
            analysis = call_sambanova(system_prompt, user_prompt, model="MiniMax-M2.5", max_tokens=2500, temperature=0.6)
            if analysis:
                analysis = f"[VIA SAMBANOVA BACKUP]\n\n{analysis}"
            else:
                return "ALL AI SYSTEMS AT CAPACITY | PLEASE RETRY"

    st.session_state.daily_analysis_count += 1
    increment_user_usage(st.session_state.user_id, "analysis")
    analysis += "\n\n---\n*Ingat, analisis ini hanyalah pandangan objektif dari sistem AeroVulpis. Selalu padukan dengan analisis dan strategi Anda sendiri sebelum mengambil keputusan trading.*"
    analysis += "\n\n⚠️ *Simpan hasil analisis ini di catatan Anda. Halaman mungkin di-refresh otomatis.*"

    # Deep Analysis TANPA warna
    analysis = style_deep_output(analysis)

    cache_ai_analysis(asset_name, analysis, "deep", timeframe_key)
    st.session_state.deep_analysis_result = analysis
    return analysis

def market_session_status():
    tz = pytz.timezone('Asia/Jakarta')
    now = datetime.now(tz); current_time = now.time()
    sessions = [
        {"name":"ASIAN SESSION","market":"TOKYO","start":dt_time(6,0),"end":dt_time(15,0),"color":"#00ff88"},
        {"name":"EUROPEAN SESSION","market":"LONDON","start":dt_time(14,0),"end":dt_time(23,0),"color":"#00d4ff"},
        {"name":"AMERICAN SESSION","market":"NEW YORK","start":dt_time(19,0),"end":dt_time(4,0),"color":"#ff2a6d"}
    ]
    st.markdown('<div class="session-container">',unsafe_allow_html=True)
    st.markdown('<h2 style="font-family:Orbitron;color:#00d4ff;text-align:center;font-size:22px;margin-bottom:25px;letter-spacing:5px;">GLOBAL MARKET SESSIONS</h2>',unsafe_allow_html=True)
    for sess in sessions:
        is_active = (sess["start"]<=current_time<=sess["end"]) if sess["start"]<sess["end"] else (current_time>=sess["start"] or current_time<=sess["end"])
        status_html = f'<span style="padding:4px 14px;border-radius:2px;background:rgba(0,255,136,0.07);border:1px solid rgba(0,255,136,0.35);color:#00ff88;font-size:9px;">ACTIVE</span>' if is_active else f'<span style="padding:4px 14px;border-radius:2px;background:rgba(255,42,109,0.04);border:1px solid rgba(255,42,109,0.18);color:#556680;font-size:9px;opacity:0.6;">CLOSED</span>'
        progress=0
        if is_active:
            now_minutes = now.hour*60+now.minute
            start_minutes = sess["start"].hour*60+sess["start"].minute
            end_minutes = sess["end"].hour*60+sess["end"].minute
            if end_minutes<start_minutes: end_minutes+=24*60
            if now_minutes<start_minutes and sess["start"]>sess["end"]: now_minutes+=24*60
            total_duration = end_minutes-start_minutes
            elapsed = now_minutes-start_minutes
            progress = min(100,max(0,int((elapsed/total_duration)*100)))
        st.markdown(f"""<div style="background:rgba(0,18,36,0.5);border:1px solid rgba(0,212,255,0.08);border-radius:4px;padding:18px;margin-bottom:10px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;"><div><span style="font-family:Orbitron;font-weight:700;color:{sess['color']};font-size:14px;letter-spacing:2px;">{sess['name']}</span><span style="font-family:Share Tech Mono;font-size:10px;color:#557799;margin-left:8px;">{sess['market']}</span></div>{status_html}</div>
            <div style="font-family:Share Tech Mono;font-size:11px;color:#6688aa;margin-bottom:10px;">{sess['start'].strftime('%H:%M')} - {sess['end'].strftime('%H:%M')} WIB</div>
            <div style="background:rgba(255,255,255,0.03);height:4px;border-radius:2px;overflow:hidden;"><div style="background:{sess['color'] if is_active else '#333'};width:{progress if is_active else 0}%;height:100%;border-radius:2px;transition:width 0.5s ease;"></div></div>
            <div style="font-family:Share Tech Mono;font-size:9px;color:{sess['color'] if is_active else '#445566'};text-align:right;margin-top:4px;">{f'PROGRESS: {progress}%' if is_active else 'STANDBY'}</div>
        </div>""",unsafe_allow_html=True)
    is_golden = (dt_time(19,0)<=current_time<=dt_time(23,0))
    if is_golden:
        st.markdown("""<div style="text-align:center;padding:16px;background:rgba(0,212,255,0.04);border:1px solid rgba(0,212,255,0.28);border-radius:4px;margin-top:12px;"><p style="font-family:Orbitron;color:#00d4ff;text-shadow:0 0 12px rgba(0,212,255,0.5);margin:0;font-size:18px;letter-spacing:3px;">GOLDEN HOUR ACTIVE</p></div>""",unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

# ##############################################################################
# INSTRUMENTS DICTIONARY
# ##############################################################################
instruments = {
    "FOREX":{"EUR/USD":"EURUSD=X","GBP/USD":"GBPUSD=X","USD/JPY":"USDJPY=X","AUD/USD":"AUDUSD=X","USD/CHF":"USDCHF=X"},
    "CRYPTO":{"BITCOIN":"BTC-USD","ETHEREUM":"ETH-USD","SOLANA":"SOL-USD","BNB":"BNB-USD","XRP":"XRP-USD"},
    "INDICES":{"NASDAQ-100":"^IXIC","S&P 500":"^GSPC","DOW JONES":"^DJI","DAX 40":"^GDAXI","IHSG":"^JKSE"},
    "US STOCKS":{"NVIDIA":"NVDA","APPLE":"AAPL","TESLA":"TSLA","MICROSOFT":"MSFT","AMAZON":"AMZN"},
    "ID STOCKS":{"BBRI":"BBRI.JK","BBCA":"BBCA.JK","TLKM":"TLKM.JK","ASII":"ASII.JK","BMRI":"BMRI.JK"},
    "COMMODITIES":{"GOLD (XAUUSD)":"GC=F","SILVER (XAGUSD)":"SI=F","CRUDE OIL (WTI)":"CL=F","NATURAL GAS":"NG=F","COPPER":"HG=F","PALLADIUM":"PA=F","PLATINUM":"PL=F"}
}

def get_news_data(category="General", max_articles=10):
    cached = get_cached_news_supabase(category)
    if cached: return cached, None
    from news_cache_manager import initialize_news_cache, should_update_news, get_cached_news, update_news_cache
    initialize_news_cache()
    force_refresh = False
    if "last_news_fetch" not in st.session_state: st.session_state.last_news_fetch = {}
    last_fetch = st.session_state.last_news_fetch.get(category)
    if last_fetch is None or (datetime.now()-last_fetch).total_seconds()>3600:
        force_refresh = True; st.session_state.last_news_fetch[category] = datetime.now()
    if not force_refresh and not should_update_news(category):
        cached_news = get_cached_news(category)
        if cached_news: cache_news_supabase(category, cached_news); return cached_news, None
    berita_final = []; urls_terpakai = set()
    
    category_map = {
        "General": "finance, economy, market, breaking news",
        "Stock": "stocks, equities, earnings, wall street",
        "Geopolitics": "geopolitics, war, conflict, sanctions, central banks",
        "Gold & Silver": "gold, silver, precious metals, commodities",
        "Forex": "forex, currency, EURUSD, GBPUSD, central banks, interest rates",
        "Ekonomi Indonesia": "indonesia economy, bi, bank indonesia, rupiah",
        "Saham Indonesia": "idx, bursa efek indonesia, saham indonesia",
        "Indonesia Stock": "idx, bursa efek indonesia, saham indonesia",
        "Crypto": "cryptocurrency, bitcoin, ethereum, solana"
    }
    
    if newsapi_key and category in ["General", "Stock", "Crypto", "Ekonomi Indonesia", "Saham Indonesia", "Indonesia Stock"]:
        try:
            query_map = {"General":"finance OR economy OR market","Stock":"stocks OR equities OR earnings","Crypto":"cryptocurrency OR bitcoin OR ethereum","Ekonomi Indonesia":"indonesia economy OR bank indonesia","Saham Indonesia":"IDX OR saham OR bursa efek indonesia","Indonesia Stock":"IDX OR saham OR bursa efek indonesia"}
            keyword = query_map.get(category, "finance")
            url_n = f"https://newsapi.org/v2/everything?q={keyword}&language=en&sortBy=publishedAt&pageSize={max_articles}&apiKey={newsapi_key}"
            res_n = requests.get(url_n, timeout=10).json()
            if res_n.get("articles"):
                for item in res_n["articles"]:
                    if item.get('url') and item['url'] not in urls_terpakai:
                        berita_final.append({'publishedAt':item.get('publishedAt',datetime.now().isoformat()),'title':item.get('title','NO TITLE'),'description':item.get('description',''),'source':item.get('source',{}).get('name','NEWSAPI'),'url':item['url']})
                        urls_terpakai.add(item['url'])
        except: pass

    if marketaux_key:
        try:
            since_date = (datetime.now()-timedelta(hours=48)).strftime('%Y-%m-%dT%H:%M')
            api_query = category_map.get(category, "finance,economy,market")
            url_m = f"https://api.marketaux.com/v1/news/all?api_token={marketaux_key}&language=en&search={api_query}&limit=20&published_after={since_date}"
            res_m = requests.get(url_m, timeout=10).json()
            if res_m.get('data'):
                for item in res_m.get('data',[]):
                    if item.get('url') and item['url'] not in urls_terpakai:
                        berita_final.append({'publishedAt':item.get('published_at',datetime.now().isoformat()),'title':item.get('title','NO TITLE'),'description':item.get('description',''),'source':item.get('source','MARKETAUX'),'url':item['url']})
                        urls_terpakai.add(item['url'])
        except: pass

    if currents_api_key:
        try:
            currents_cat_map = {"General":"finance","Stock":"stocks","Geopolitics":"world","Gold & Silver":"commodities","Forex":"finance","Crypto":"crypto"}
            currents_cat = currents_cat_map.get(category,"finance")
            url_c = f"https://api.currentsapi.services/v1/latest-news?apiKey={currents_api_key}&language=en&category={currents_cat}&limit=15"
            res_c = requests.get(url_c, timeout=10).json()
            if res_c.get('news'):
                for item in res_c.get('news',[]):
                    if item.get('url') and item['url'] not in urls_terpakai:
                        berita_final.append({'publishedAt':item.get('published',datetime.now().isoformat()),'title':item.get('title','NO TITLE'),'description':item.get('description',''),'source':'CURRENTS','url':item['url']})
                        urls_terpakai.add(item['url'])
        except: pass

    if tiingo_key:
        try:
            start_date = (datetime.now()-timedelta(hours=48)).strftime('%Y-%m-%dT%H:%M:%S')
            url_t = f"https://api.tiingo.com/tiingo/news?token={tiingo_key}&limit=15&startDate={start_date}"
            if category in ["Stock","Saham Indonesia"]: url_t += "&tags=stocks"
            elif category == "Forex": url_t += "&tags=forex,currencies"
            elif category == "Gold & Silver": url_t += "&tags=commodities"
            elif category == "Crypto": url_t += "&tags=crypto"
            res_t = requests.get(url_t, timeout=10).json()
            if isinstance(res_t,list):
                for item in res_t:
                    if item.get('url') and item['url'] not in urls_terpakai:
                        berita_final.append({'publishedAt':item.get('publishedDate',datetime.now().isoformat()),'title':item.get('title','NO TITLE'),'description':item.get('description',item.get('title','')),'source':'TIINGO','url':item['url']})
                        urls_terpakai.add(item['url'])
        except: pass

    if coinmarketcap_api_key and category in ["Crypto","General"]:
        try:
            cmc_news = fetch_coinmarketcap_news(max_articles=10)
            for item in cmc_news:
                if item.get('url') and item['url'] not in urls_terpakai:
                    berita_final.append(item); urls_terpakai.add(item['url'])
        except: pass

    if not berita_final and category in ["Gold & Silver","Forex"] and marketaux_key:
        try:
            since_date = (datetime.now()-timedelta(hours=72)).strftime('%Y-%m-%dT%H:%M')
            fallback_q = "gold silver commodity forex currency central bank" if category in ["Gold & Silver","Forex"] else "finance economy"
            url_fb = f"https://api.marketaux.com/v1/news/all?api_token={marketaux_key}&language=en&search={fallback_q}&limit=15&published_after={since_date}"
            res_fb = requests.get(url_fb, timeout=10).json()
            if res_fb.get('data'):
                for item in res_fb['data']:
                    if item.get('url') and item['url'] not in urls_terpakai:
                        berita_final.append({'publishedAt':item.get('published_at',datetime.now().isoformat()),'title':item.get('title','NO TITLE'),'description':item.get('description',''),'source':item.get('source','MARKETAUX'),'url':item['url']})
                        urls_terpakai.add(item['url'])
        except: pass

    if not berita_final:
        cached_news = get_cached_news(category)
        if cached_news: cache_news_supabase(category, cached_news); return cached_news, "DISPLAYING CACHED DATA"
        return [], "NO NEWS AVAILABLE"
    
    try: berita_final = sorted(berita_final, key=lambda x: str(x.get('publishedAt','')), reverse=True)
    except: pass
    berita_final = berita_final[:max_articles]
    tz_wib = pytz.timezone('Asia/Jakarta')
    for b in berita_final:
        try:
            raw_date = b.get('publishedAt','')
            if raw_date:
                if isinstance(raw_date, datetime):
                    if raw_date.tzinfo is None: raw_date = pytz.UTC.localize(raw_date)
                    dt_wib = raw_date.astimezone(tz_wib)
                else:
                    raw_date = str(raw_date).replace('Z','+00:00')
                    try: dt_utc = datetime.fromisoformat(raw_date)
                    except:
                        try: dt_utc = datetime.strptime(str(raw_date)[:19],"%Y-%m-%dT%H:%M:%S")
                        except: dt_utc = datetime.now(pytz.UTC)
                    if dt_utc.tzinfo is None: dt_utc = dt_utc.replace(tzinfo=pytz.UTC)
                    dt_wib = dt_utc.astimezone(tz_wib)
                b['publishedAt'] = dt_wib.strftime("%d %b %Y, %H:%M WIB")
            else: b['publishedAt'] = 'N/A'
        except: b['publishedAt'] = 'N/A'
    update_news_cache(category, berita_final)
    cache_news_supabase(category, berita_final)
    return berita_final, None

# ##############################################################################
# CHECK SMART ALERTS
# ##############################################################################
def check_smart_alerts():
    if "active_alerts" not in st.session_state or not st.session_state.active_alerts:
        return
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN") or st.secrets.get("TELEGRAM_BOT_TOKEN")
    if not telegram_bot_token: return

    unique_instruments = list(set(a["instrument"] for a in st.session_state.active_alerts if not a.get("triggered", False)))
    if not unique_instruments: return

    instrument_to_ticker = {}
    for cat in instruments.values():
        for name, ticker in cat.items():
            instrument_to_ticker[name] = ticker

    current_prices = {}
    for inst in unique_instruments:
        cached_data = get_cached_market_price_full(inst)
        if cached_data and cached_data.get("price"):
            current_prices[inst] = cached_data["price"]
        else:
            ticker = instrument_to_ticker.get(inst)
            if ticker:
                m_data = get_market_data(ticker)
                if m_data:
                    current_prices[inst] = m_data.get("price")

    supabase_admin = get_supabase_admin()
    for alert in st.session_state.active_alerts:
        if alert.get("triggered", False): continue
        inst_name = alert["instrument"]
        current_price = current_prices.get(inst_name)
        if current_price is None: continue
        target_num = alert["target"] if isinstance(alert["target"], (int, float)) else float(alert["target"])
        condition = alert["condition"]
        triggered = False
        if condition == "bullish" and current_price >= target_num:
            triggered = True
        elif condition == "bearish" and current_price <= target_num:
            triggered = True
        if triggered:
            now_wib = datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%Y-%m-%d %H:%M:%S WIB")
            formatted_price = format_price_display(current_price, inst_name)
            formatted_target = format_price_display(target_num, inst_name)
            alert_message = f"🔔 *AEROVULPIS TARGET ACQUIRED*\n\nINSTR: *{inst_name}*\nPRICE: *{formatted_price}*\nTARGET: *{formatted_target}*\nTIME: *{now_wib}*\n\nStatus: *TRIGGERED*"
            url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
            payload = {'chat_id': alert["chat_id"], 'text': alert_message, 'parse_mode': 'Markdown'}
            try:
                requests.post(url, json=payload, timeout=10)
                st.toast(f"TARGET ACQUIRED: {inst_name} @ {formatted_target}")
            except: pass
            alert["triggered"] = True
            if "id" in alert:
                try:
                    supabase_admin.table("active_alerts").update({"triggered": True, "triggered_at": datetime.now(pytz.UTC).isoformat()}).eq("id", alert["id"]).execute()
                except: pass

# ========== PART 1 END ==========
# ========== PART 2 START ==========
# ##############################################################################
# APPLICATION CONFIGURATION (PAGE CONFIG HARUS PERTAMA)
# ##############################################################################

st.set_page_config(
    layout="wide",
    page_title="AEROVULPIS V4.0",
    page_icon="https://files.manuscdn.com/user_upload_by_module/session_file/310519663520709901/oOIKIIkSvIdagiSw.png",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# AUTO-REFRESH (5 MENIT) - HARUS DILETAKAN SETELAH SET_PAGE_CONFIG
# ==============================================================================
if AUTOREFRESH_AVAILABLE:
    st_autorefresh(interval=5 * 60 * 1000, key="data_autorefresh")
else:
    st.sidebar.info("ℹ️ Install streamlit-autorefresh untuk auto-refresh setiap 5 menit")

# ==============================================================================
# SPLASH SCREEN (FIXED - AKAN HILANG SETELAH 2.5 DETIK)
# ==============================================================================
if "splash_done" not in st.session_state:
    splash_placeholder = st.empty()
    with splash_placeholder.container():
        st.markdown("""
        <div id="splash-overlay" style="position:fixed; top:0; left:0; width:100%; height:100%; background:radial-gradient(ellipse at 50% 50%, #0a0f1e 0%, #020408 100%); z-index:9999; display:flex; flex-direction:column; justify-content:center; align-items:center;">
            <div style="position:relative; width:120px; height:120px; margin-bottom:30px;">
                <div style="position:absolute; top:50%; left:50%; width:50px; height:50px; margin-left:-25px; margin-top:-25px; border-radius:50%; border:3px solid transparent; border-top-color:#00d4ff; border-right-color:#bc13fe; animation: spinRing 1.8s infinite cubic-bezier(0.4,0,0.2,1);"></div>
                <div style="position:absolute; top:50%; left:50%; width:70px; height:70px; margin-left:-35px; margin-top:-35px; border-radius:50%; border:3px solid transparent; border-bottom-color:#00ff88; border-left-color:#ff2a6d; animation: spinRing 2.2s infinite cubic-bezier(0.4,0,0.2,1); animation-delay:0.2s;"></div>
                <div style="position:absolute; top:50%; left:50%; width:90px; height:90px; margin-left:-45px; margin-top:-45px; border-radius:50%; border:3px solid transparent; border-top-color:#ffcc00; border-right-color:#00d4ff; animation: spinRing 2.6s infinite cubic-bezier(0.4,0,0.2,1); animation-delay:0.4s;"></div>
            </div>
            <p style="font-family:'Orbitron', monospace; font-size:28px; color:#00d4ff; text-shadow:0 0 30px #00d4ff; letter-spacing:10px; margin:10px 0;">AEROVULPIS</p>
            <p style="font-family:'Share Tech Mono', monospace; font-size:12px; color:#00ff88; text-shadow:0 0 15px #00ff88; letter-spacing:3px;">INITIALIZING QUANTUM CORE</p>
            <div style="width:300px; height:2px; background:rgba(0,212,255,0.2); margin-top:20px; border-radius:2px; overflow:hidden;">
                <div id="splash-progress-bar" style="width:0%; height:100%; background:#00d4ff; box-shadow:0 0 20px #00d4ff; transition:width 0.05s linear;"></div>
            </div>
        </div>
        <style>
            @keyframes spinRing {
                0% { transform: rotateY(0deg) rotateX(0deg) rotate(0deg); opacity:0.9; }
                50% { opacity:0.4; }
                100% { transform: rotateY(360deg) rotateX(360deg) rotate(720deg); opacity:0.9; }
            }
        </style>
        <script>
            let width = 0;
            const interval = setInterval(() => {
                if (width >= 100) {
                    clearInterval(interval);
                } else {
                    width += Math.random() * 15 + 5;
                    if (width > 100) width = 100;
                    const bar = document.getElementById('splash-progress-bar');
                    if (bar) bar.style.width = width + '%';
                }
            }, 100);
        </script>
        """, unsafe_allow_html=True)
    time.sleep(2.5)
    st.session_state.splash_done = True
    splash_placeholder.empty()
    st.rerun()

# ==============================================================================
# INITIAL CLEANUP & SESSION STATE
# ==============================================================================

cleanup_logs()
cleanup_old_data()
cleanup_ai_cache()
cleanup_news_cache()
send_log("AEROVULPIS V4.0 SYSTEM ONLINE")

if "lang" not in st.session_state: st.session_state.lang = "ID"
if "cached_analysis" not in st.session_state: st.session_state.cached_analysis = {}
if "user_tier" not in st.session_state: st.session_state.user_tier = "free"
if "user_id" not in st.session_state: st.session_state.user_id = None
if "user_name" not in st.session_state: st.session_state.user_name = None
if "user_email" not in st.session_state: st.session_state.user_email = None
if "user_avatar" not in st.session_state: st.session_state.user_avatar = None
if "auth_session" not in st.session_state: st.session_state.auth_session = None
if "show_signup" not in st.session_state: st.session_state.show_signup = False
if "daily_analysis_count" not in st.session_state: st.session_state.daily_analysis_count = 0
if "daily_chatbot_count" not in st.session_state: st.session_state.daily_chatbot_count = 0
if "daily_sentinel_count" not in st.session_state: st.session_state.daily_sentinel_count = 0
if "last_reset_date" not in st.session_state: st.session_state.last_reset_date = datetime.now(pytz.UTC).date()
if "show_activation" not in st.session_state: st.session_state.show_activation = False
if "activation_result" not in st.session_state: st.session_state.activation_result = None
if "sentinel_analysis" not in st.session_state: st.session_state.sentinel_analysis = None
if "messages" not in st.session_state: st.session_state.messages = []
if "active_alerts" not in st.session_state: st.session_state.active_alerts = []
if "last_news_fetch" not in st.session_state: st.session_state.last_news_fetch = {}
if "show_payment_modal" not in st.session_state: st.session_state.show_payment_modal = False
if "selected_package" not in st.session_state: st.session_state.selected_package = None
if "selected_price" not in st.session_state: st.session_state.selected_price = ""
if "selected_duration" not in st.session_state: st.session_state.selected_duration = ""
if "payment_proof_uploaded" not in st.session_state: st.session_state.payment_proof_uploaded = False
if "show_forgot_password" not in st.session_state: st.session_state.show_forgot_password = False
if "user_expired_at" not in st.session_state: st.session_state.user_expired_at = None
if "menu_selection" not in st.session_state: st.session_state.menu_selection = "Live Dashboard"
if "awaiting_otp" not in st.session_state: st.session_state.awaiting_otp = False
if "temp_reg_email" not in st.session_state: st.session_state.temp_reg_email = ""
if "current_period" not in st.session_state: st.session_state.current_period = "1mo"
if "current_interval" not in st.session_state: st.session_state.current_interval = "1h"

if st.session_state.last_reset_date < datetime.now(pytz.UTC).date():
    st.session_state.daily_analysis_count = 0
    st.session_state.daily_chatbot_count = 0
    st.session_state.daily_sentinel_count = 0
    st.session_state.last_reset_date = datetime.now(pytz.UTC).date()

restore_session()

# ##############################################################################
# TIER LIMITS CONFIGURATION
# ##############################################################################
LIMITS = {
    "free":          {"analysis_per_day": 1,   "sentinel_per_day": 0,  "chatbot_per_day": 5,   "alert_per_day": 1},
    "trial":         {"analysis_per_day": 8,   "sentinel_per_day": 1,  "chatbot_per_day": 20,  "alert_per_day": 2},
    "weekly":        {"analysis_per_day": 15,  "sentinel_per_day": 2,  "chatbot_per_day": 40,  "alert_per_day": 8},
    "monthly":       {"analysis_per_day": 30,  "sentinel_per_day": 4,  "chatbot_per_day": 60,  "alert_per_day": 10},
    "six_months":    {"analysis_per_day": 60,  "sentinel_per_day": 8,  "chatbot_per_day": 200, "alert_per_day": 13},
    "yearly":        {"analysis_per_day": 80,  "sentinel_per_day": 28, "chatbot_per_day": 300, "alert_per_day": 20},
    "yearly_promo":  {"analysis_per_day": 80,  "sentinel_per_day": 28, "chatbot_per_day": 300, "alert_per_day": 20},
}

# ##############################################################################
# LANGUAGE DICTIONARY
# ##############################################################################
translations = {
    "ID": {
        "control_center": "CONTROL CENTER", "category": "KATEGORI ASET", "asset": "PILIH INSTRUMEN",
        "timeframe": "TIMEFRAME", "navigation": "NAVIGATION SYSTEM", "live_price": "LIVE PRICE",
        "signal": "SIGNAL", "rsi": "RSI", "atr": "ATR", "refresh": "REFRESH DATA",
        "ai_analysis": "AI ANALYSIS", "generate_ai": "GENERATE DEEP ANALYSIS",
        "market_sessions": "MARKET SESSIONS", "market_news": "MARKET NEWS",
        "risk_mgmt": "RISK MANAGEMENT", "settings": "SETTINGS", "clear_cache": "CLEAR SYSTEM CACHE",
        "lang_select": "LANGUAGE", "recommendation": "CURRENT RECOMMENDATION",
        "no_news": "TIDAK ADA BERITA", "limit_reached": "DAILY LIMIT REACHED",
        "daily_limit": "DAILY USAGE", "upgrade_premium": "UPGRADE TIER",
        "login_title": "AUTHENTICATION SYSTEM", "login_email": "EMAIL",
        "login_password": "PASSWORD", "login_btn": "LOGIN",
        "signup_btn": "REGISTER NEW IDENTITY", "logout": "TERMINATE SESSION",
        "activate_key": "ACTIVATE LICENSE KEY", "enter_key": "ENTER ACTIVATION KEY",
        "activate_btn": "VALIDATE & ACTIVATE", "welcome": "WELCOME", "tier_free": "FREE TIER",
        "processing": "PROCESSING AUTHENTICATION", "activation_success": "ACTIVATION SUCCESSFUL",
        "activation_failed": "ACTIVATION FAILED", "sign_in_prompt": "IDENTITY VERIFICATION REQUIRED",
        "sign_in_desc": "Enter credentials to access the terminal",
        "sentinel_btn": "INITIATE DEEP ANALYSIS PRO", "risk_simulate": "EXECUTE SIMULATION",
        "risk_weekly": "WEEKLY", "risk_monthly": "MONTHLY", "risk_yearly": "YEARLY",
        "risk_net": "NET P/L", "risk_return": "RETURN %", "risk_balance": "FINAL BALANCE",
        "risk_initial": "INITIAL", "risk_after": "AFTER", "risk_params": "RISK PARAMETERS",
        "risk_per_trade": "RISK PER TRADE", "risk_reward_trade": "REWARD PER TRADE",
        "risk_max_loss": "MAX DAILY LOSS", "risk_max_profit": "MAX DAILY PROFIT",
        "risk_summary": "BALANCE PROJECTION", "funding_details": "ACCOUNT CONFIGURATION",
        "account_balance": "ACCOUNT BALANCE", "rr_simulator": "RISK-REWARD MATRIX",
        "wins": "WINNING TRADES", "losses": "LOSING TRADES", "daily_risk": "DAILY RISK LIMITS",
        "help_support": "SYSTEM DOCUMENTATION", "sentinel_title": "SENTINEL PRO INTELLIGENCE",
        "sentinel_ai_status": "AEROVULPIS SENTINEL CORE ACTIVE", "market_status": "MARKET STATUS: ACTIVE",
        "sentinel_intel": "INTELLIGENCE REPORT",
        "sentinel_placeholder": "Initialize Deep Analysis Pro to generate intelligence report",
        "news_filter": "KATEGORI BERITA",
        "news_updated": "Live feed dari jaringan finansial global | Diperbarui setiap jam",
        "economic_title": "GLOBAL ECONOMIC SCANNER",
        "economic_subtitle": "Deteksi Peristiwa Berdampak Tinggi Real-Time Aktif",
        "alert_title": "SMART ALERT CENTER", "alert_subtitle": "AEROVULPIS TERMINAL V4.0",
        "alert_online": "SYSTEM ONLINE", "alert_sync": "MONITORING ACTIVE",
        "dashboard_title": "LIVE DASHBOARD", "signal_title": "TECHNICAL SIGNAL MATRIX",
        "chatbot_title": "NEURAL ASSISTANT", "risk_title": "RISK FRAMEWORK",
        "settings_title": "SYSTEM SETTINGS", "help_title": "SYSTEM DOCUMENTATION",
        "projection_title": "PROJECTED PERFORMANCE", "tier_label": "LICENSE TIER",
        "daily_usage_label": "DAILY USAGE MONITOR", "user_id_label": "USER ID",
        "user_email_label": "EMAIL", "license_activation": "LICENSE ACTIVATION",
        "enter_license_key": "ENTER LICENSE KEY", "license_placeholder": "XXXX-XXXX-XXXX-XXXX",
        "key_activate_button": "VALIDATE & ACTIVATE LICENSE",
        "upgrade_level": "UPGRADE LEVEL",
        "premium_lock": "PREMIUM ACCESS ONLY",
        "premium_msg": "Fitur ini tersedia untuk pengguna premium. Upgrade akses Anda untuk membuka.",
        "broker_title": "PARTNER BROKER",
        "broker_subtitle": "Pilih Broker Resmi untuk Trading Anda",
        "gauge_title": "TECHNICAL STRENGTH MATRIX"
    },
    "EN": {
        "control_center": "CONTROL CENTER", "category": "ASSET CATEGORY", "asset": "SELECT INSTRUMENT",
        "timeframe": "TIMEFRAME", "navigation": "NAVIGATION SYSTEM", "live_price": "LIVE PRICE",
        "signal": "SIGNAL", "rsi": "RSI", "atr": "ATR", "refresh": "REFRESH DATA",
        "ai_analysis": "AI ANALYSIS", "generate_ai": "GENERATE DEEP ANALYSIS",
        "market_sessions": "MARKET SESSIONS", "market_news": "MARKET NEWS",
        "risk_mgmt": "RISK MANAGEMENT", "settings": "SETTINGS", "clear_cache": "CLEAR SYSTEM CACHE",
        "lang_select": "LANGUAGE", "recommendation": "CURRENT RECOMMENDATION",
        "no_news": "NO NEWS AVAILABLE", "limit_reached": "DAILY LIMIT REACHED",
        "daily_limit": "DAILY USAGE", "upgrade_premium": "UPGRADE TIER",
        "login_title": "AUTHENTICATION SYSTEM", "login_email": "EMAIL",
        "login_password": "PASSWORD", "login_btn": "LOGIN",
        "signup_btn": "REGISTER NEW IDENTITY", "logout": "TERMINATE SESSION",
        "activate_key": "ACTIVATE LICENSE KEY", "enter_key": "ENTER ACTIVATION KEY",
        "activate_btn": "VALIDATE & ACTIVATE", "welcome": "WELCOME", "tier_free": "FREE TIER",
        "sentinel_btn": "INITIATE DEEP ANALYSIS PRO", "risk_simulate": "EXECUTE SIMULATION",
        "risk_weekly": "WEEKLY", "risk_monthly": "MONTHLY", "risk_yearly": "YEARLY",
        "risk_net": "NET P/L", "risk_return": "RETURN %", "risk_balance": "FINAL BALANCE",
        "risk_initial": "INITIAL", "risk_after": "AFTER", "risk_params": "RISK PARAMETERS",
        "risk_per_trade": "RISK PER TRADE", "risk_reward_trade": "REWARD PER TRADE",
        "risk_max_loss": "MAX DAILY LOSS", "risk_max_profit": "MAX DAILY PROFIT",
        "risk_summary": "BALANCE PROJECTION", "funding_details": "ACCOUNT CONFIGURATION",
        "account_balance": "ACCOUNT BALANCE", "rr_simulator": "RISK-REWARD MATRIX",
        "wins": "WINNING TRADES", "losses": "LOSING TRADES", "daily_risk": "DAILY RISK LIMITS",
        "help_support": "SYSTEM DOCUMENTATION", "sentinel_title": "SENTINEL PRO INTELLIGENCE",
        "sentinel_ai_status": "AEROVULPIS SENTINEL CORE ACTIVE", "market_status": "MARKET STATUS: ACTIVE",
        "sentinel_intel": "INTELLIGENCE REPORT",
        "sentinel_placeholder": "Initialize Deep Analysis Pro to generate intelligence report",
        "news_filter": "NEWS CATEGORY",
        "news_updated": "Live feed from global financial networks | Updated hourly",
        "economic_title": "GLOBAL ECONOMIC SCANNER",
        "economic_subtitle": "Real-Time High Impact Event Detection Active",
        "alert_title": "SMART ALERT CENTER", "alert_subtitle": "AEROVULPIS TERMINAL V4.0",
        "alert_online": "SYSTEM ONLINE", "alert_sync": "MONITORING ACTIVE",
        "dashboard_title": "LIVE DASHBOARD", "signal_title": "TECHNICAL SIGNAL MATRIX",
        "chatbot_title": "NEURAL ASSISTANT", "risk_title": "RISK FRAMEWORK",
        "settings_title": "SYSTEM SETTINGS", "help_title": "SYSTEM DOCUMENTATION",
        "projection_title": "PROJECTED PERFORMANCE", "tier_label": "LICENSE TIER",
        "daily_usage_label": "DAILY USAGE MONITOR", "user_id_label": "USER ID",
        "user_email_label": "EMAIL", "license_activation": "LICENSE ACTIVATION",
        "enter_license_key": "ENTER LICENSE KEY", "license_placeholder": "XXXX-XXXX-XXXX-XXXX",
        "key_activate_button": "VALIDATE & ACTIVATE LICENSE",
        "upgrade_level": "UPGRADE LEVEL",
        "premium_lock": "PREMIUM ACCESS ONLY",
        "premium_msg": "This feature is available for premium users. Upgrade your access to unlock.",
        "broker_title": "PARTNER BROKERS",
        "broker_subtitle": "Choose Official Broker for Your Trading",
        "gauge_title": "TECHNICAL STRENGTH MATRIX"
    }
}

t = translations[st.session_state.lang]

# ##############################################################################
# CSS (FIXED - LOGO TIDAK TERPOTONG + DIGITAL TIMER STYLE + CYBERTECH BUTTON)
# ##############################################################################
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');
:root {
    --neon-cyan: #00d4ff; --neon-green: #00ff88; --neon-red: #ff2a6d;
    --deep-blue: #0055ff; --dark-bg: #020408; --card-bg: rgba(10, 14, 23, 0.85);
    --glass-border: rgba(0, 212, 255, 0.12); --text-primary: #dce4f0;
    --text-secondary: #8899bb; --text-muted: #556680;
}
* { font-family: 'Rajdhani', sans-serif; box-sizing: border-box; margin:0; padding:0; }
html, body, .stApp, .stMain, .stMainBlockContainer, .block-container, [data-testid="stAppViewBlockContainer"] {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
}
*, *::before, *::after {
    border-style: none !important;
    outline: none !important;
}
.stApp {
    background: radial-gradient(ellipse at 15% 45%, #0a1a30 0%, #030810 35%, #010408 100%) !important;
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(6,10,18,0.99) 0%, rgba(2,5,10,0.99) 100%) !important;
    border-right: 1px solid rgba(0,212,255,0.2) !important;
    display: block !important;
    visibility: visible !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 0.5rem 0.5rem !important;
}
.main .block-container {
    padding-top: 3rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
}
.glass-card {
    background: var(--card-bg);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid var(--glass-border);
    border-radius: 6px;
    padding: 20px;
    box-shadow: 0 4px 32px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.02);
    margin-bottom: 6px;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
}
.glass-card:hover {
    border-color: rgba(0,212,255,0.25);
    box-shadow: 0 6px 36px rgba(0,0,0,0.7), 0 0 16px rgba(0,212,255,0.04);
}
.session-container {
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 6px;
    padding: 28px;
    background: rgba(0,18,36,0.55);
    box-shadow: 0 0 48px rgba(0,212,255,0.05);
    margin-bottom: 24px;
}
.news-card {
    background: rgba(0,212,255,0.015);
    border: 1px solid rgba(0,212,255,0.06);
    padding: 20px;
    border-radius: 4px;
    margin-bottom: 10px;
    transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
    position: relative;
    overflow: hidden;
}
.news-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 2px;
    height: 100%;
    background: linear-gradient(180deg, var(--neon-cyan) 0%, transparent 100%);
    opacity: 0.4;
}
.news-card:hover {
    background: rgba(0,212,255,0.03);
    border-color: rgba(0,212,255,0.2);
    box-shadow: 0 0 20px rgba(0,212,255,0.04);
    transform: translateX(2px);
}
.main-title-container {
    text-align: center;
    margin-top: 60px;
    padding-bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.main-logo-container {
    position: relative;
    display: inline-block;
    animation: floatLogo 5s infinite ease-in-out;
    padding: 5px 0;
    margin-bottom: 0px;
    background: transparent !important;
    perspective: 1200px;
    overflow: visible !important;
    height: auto;
}
.custom-logo {
    width: 55px;
    height: auto;
    object-fit: contain;
    filter: drop-shadow(0 0 22px rgba(0,212,255,0.45));
    background-color: transparent !important;
    animation: rotateLogo3D 15s infinite linear;
    transform-style: preserve-3d;
    position: relative;
    z-index: 2;
}
@keyframes floatLogo { 0%,100% { transform: translateY(0px); } 50% { transform: translateY(-5px); } }
@keyframes rotateLogo3D { 0% { transform: rotateY(0deg) rotateX(0deg); } 25% { transform: rotateY(90deg) rotateX(4deg); } 50% { transform: rotateY(180deg) rotateX(0deg); } 75% { transform: rotateY(270deg) rotateX(-4deg); } 100% { transform: rotateY(360deg) rotateX(0deg); } }
.main-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(135deg, #00d4ff 0%, #00ff88 30%, #00d4ff 60%, #0055ff 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: titleShimmer 6s ease infinite;
    margin: 0;
    padding: 0;
    letter-spacing: 6px;
    text-align: center;
}
@keyframes titleShimmer { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
.subtitle-text {
    text-align: center;
    color: #556680;
    font-family: 'Share Tech Mono', monospace;
    margin-top: -4px;
    padding: 0;
    font-size: 9px;
    letter-spacing: 3px;
}
/* --- STATISTIK DIGITAL (HANYA UNTUK BELUM LOGIN) --- */
.digital-stats {
    display: flex;
    justify-content: center;
    gap: 32px;
    margin: 24px auto 16px auto;
    flex-wrap: wrap;
    background: rgba(0, 20, 40, 0.4);
    backdrop-filter: blur(4px);
    border-radius: 8px;
    padding: 16px 24px;
    border: 1px solid rgba(0, 212, 255, 0.15);
    max-width: 800px;
}
.stat-item {
    text-align: center;
    font-family: 'Share Tech Mono', monospace;
}
.stat-number {
    font-family: 'Orbitron', monospace;
    font-size: 28px;
    font-weight: 700;
    color: #00d4ff;
    text-shadow: 0 0 10px rgba(0,212,255,0.5);
    letter-spacing: 2px;
}
.stat-label {
    font-size: 10px;
    color: #8899bb;
    letter-spacing: 1px;
    margin-top: 4px;
}
/* --- END STATISTIK --- */
/* --- DIGITAL BADGE UNTUK SIGNAL ANALYSIS --- */
.cyber-success {
    display: inline-block;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: #00ff88;
    text-shadow: 0 0 6px #00ff88;
    background: rgba(0,255,136,0.1);
    padding: 2px 8px;
    border-radius: 4px;
    border-left: 2px solid #00ff88;
    letter-spacing: 1px;
    margin-left: 6px;
}
.cyber-fail {
    display: inline-block;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: #ff2a6d;
    text-shadow: 0 0 6px #ff2a6d;
    background: rgba(255,42,109,0.1);
    padding: 2px 8px;
    border-radius: 4px;
    border-left: 2px solid #ff2a6d;
    letter-spacing: 1px;
    margin-left: 6px;
}
.digital-check-bull {
    display: inline-block;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    color: #00ff88;
    text-shadow: 0 0 6px #00ff88;
    background: rgba(0,255,136,0.08);
    padding: 2px 6px;
    border-radius: 3px;
}
.digital-check-bear {
    display: inline-block;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    color: #ff2a6d;
    text-shadow: 0 0 6px #ff2a6d;
    background: rgba(255,42,109,0.08);
    padding: 2px 6px;
    border-radius: 3px;
}
.signal-target-hit {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #00ff88;
    margin-left: 8px;
}
.signal-target-hit::before {
    content: "[⚡] ";
    color: #00d4ff;
}
/* --- SIGNAL ANALYSIS GRID RESPONSIVE --- */
.signal-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 16px;
}
@media (max-width: 768px) {
    .signal-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}
.signal-item {
    white-space: nowrap;
    overflow-x: auto;
    font-size: clamp(12px, 4vw, 16px);
}
.signal-number {
    font-family: 'Orbitron', monospace;
    font-size: clamp(16px, 5vw, 20px);
    color: #00ff88;
    word-break: normal;
}
.signal-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 9px;
    color: #557799;
}
.entry-number {
    font-family: 'Orbitron', monospace;
    font-size: clamp(16px, 5vw, 20px);
    color: #00ff88;
    white-space: nowrap;
}
.sl-number {
    font-family: 'Orbitron', monospace;
    font-size: clamp(14px, 4vw, 16px);
    color: #ff2a6d;
    white-space: nowrap;
}
.stButton > button {
    background: linear-gradient(160deg, #001a33, #002850) !important;
    border: 1px solid rgba(0,212,255,0.35) !important;
    color: #00d4ff !important;
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 600 !important;
    font-size: 11px !important;
    padding: 10px 20px !important;
    border-radius: 3px !important;
    letter-spacing: 2px !important;
    transition: all 0.3s ease !important;
    text-transform: uppercase;
}
.stButton > button:hover {
    background: linear-gradient(160deg, #002850, #003870) !important;
    border-color: #00d4ff !important;
    box-shadow: 0 0 28px rgba(0,212,255,0.25), 0 0 56px rgba(0,212,255,0.08) !important;
    color: #ffffff !important;
    transform: translateY(-1px);
}
.sentinel-container {
    border: 2px solid rgba(0,212,255,0.3);
    border-radius: 8px;
    padding: 28px;
    background: linear-gradient(160deg, rgba(0,10,24,0.95), rgba(0,3,12,0.98));
    box-shadow: 0 0 60px rgba(0,212,255,0.08), inset 0 1px 0 rgba(0,212,255,0.05);
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.sentinel-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent, #00d4ff, #bc13fe, transparent);
    animation: scanHorizontal 3s infinite;
}
@keyframes scanHorizontal { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
.sentinel-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 28px;
    font-weight: 800;
    color: #00d4ff;
    text-shadow: 0 0 25px rgba(0,212,255,0.4), 0 0 50px rgba(0,212,255,0.1);
    letter-spacing: 5px;
    margin: 0;
}
.intelligence-panel {
    background: rgba(0,6,18,0.8);
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 6px;
    padding: 22px;
    height: 100%;
    box-shadow: inset 0 0 30px rgba(0,0,0,0.4);
}
.intel-header {
    font-family: 'Orbitron', sans-serif;
    font-size: 14px;
    font-weight: 700;
    color: #00d4ff;
    margin-bottom: 14px;
    border-left: 3px solid #00d4ff;
    padding-left: 14px;
    letter-spacing: 4px;
    text-shadow: 0 0 10px rgba(0,212,255,0.3);
}
.sentinel-cyber-report {
    background: rgba(0,6,18,0.85);
    border-left: 3px solid #00d4ff;
    padding: 20px 22px;
    border-radius: 4px;
    margin: 14px 0;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #8899bb;
    line-height: 1.8;
    box-shadow: 0 0 25px rgba(0,212,255,0.08), inset 0 0 20px rgba(0,0,0,0.3);
    position: relative;
    overflow: hidden;
}
.indicator-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
    gap: 7px;
    margin-top: 14px;
}
.indicator-box {
    background: rgba(0,28,56,0.35);
    border: 1px solid rgba(0,212,255,0.08);
    border-radius: 3px;
    padding: 14px;
    text-align: center;
    transition: all 0.3s ease;
}
.digital-auth-container {
    background: rgba(0,15,30,0.7);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 6px;
    padding: 20px;
    margin: 8px 0;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 24px rgba(0,212,255,0.05);
}
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: #010408; }
::-webkit-scrollbar-thumb { background: #1a3350; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #00d4ff; }
.risk-cyber-container {
    border: 1px solid rgba(0,212,255,0.25);
    border-radius: 8px;
    padding: 24px 20px;
    background: linear-gradient(160deg, rgba(0,12,32,0.95), rgba(0,4,16,0.98));
    box-shadow: 0 0 60px rgba(0,212,255,0.06), inset 0 1px 0 rgba(0,212,255,0.04);
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.risk-cyber-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00d4ff, #00ff88, #bc13fe, transparent);
    animation: scanHorizontal 4s infinite;
}
.risk-hud-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: #00d4ff;
    text-align: center;
    letter-spacing: 6px;
    text-shadow: 0 0 35px rgba(0,212,255,0.5), 0 0 70px rgba(0,212,255,0.15);
    margin-bottom: 2px;
}
.risk-neon-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.2), transparent);
    margin: 16px 0;
}
.risk-input-card {
    background: rgba(0,22,55,0.6);
    border: 1px solid rgba(0,212,255,0.1);
    border-radius: 4px;
    padding: 12px;
    margin-bottom: 8px;
    backdrop-filter: blur(8px);
}
.risk-matrix-item {
    background: rgba(0,25,60,0.5);
    border: 1px solid rgba(0,212,255,0.08);
    border-radius: 4px;
    padding: 10px 6px;
    text-align: center;
}
.risk-simulate-btn button {
    background: linear-gradient(160deg, #002850, #004080) !important;
    border: 1px solid #00d4ff !important;
    color: #00d4ff !important;
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    letter-spacing: 4px !important;
    padding: 14px 24px !important;
    border-radius: 4px !important;
    width: 100% !important;
}
.upgrade-container { max-width: 1000px; margin: 0 auto; padding: 20px 10px; }
.upgrade-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 26px;
    font-weight: 800;
    text-align: center;
    color: #00d4ff;
    text-shadow: 0 0 35px rgba(0,212,255,0.55), 0 0 70px rgba(0,212,255,0.15);
    letter-spacing: 6px;
    margin-bottom: 5px;
}
.pricing-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 20px; }
@media (max-width: 900px) { .pricing-grid { grid-template-columns: repeat(2, 1fr); } }
.pricing-card {
    background: linear-gradient(160deg, rgba(0,15,38,0.9), rgba(0,4,12,0.97));
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 6px;
    padding: 22px 12px 30px 12px;
    text-align: center;
    transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
    height: auto;
    min-height: 480px;
}
.pricing-card:hover { border-color: #00d4ff; box-shadow: 0 0 35px rgba(0,212,255,0.25), 0 0 70px rgba(0,212,255,0.08); transform: translateY(-4px); }
.pricing-card.featured { border-color: rgba(0,255,136,0.35); box-shadow: 0 0 30px rgba(0,255,136,0.1); }
.pricing-badge {
    text-align: center;
    background: #ff2a6d;
    color: #fff;
    font-family: 'Orbitron', sans-serif;
    font-size: 7px;
    font-weight: 800;
    letter-spacing: 1px;
    padding: 4px 8px;
    border-radius: 3px;
    text-transform: uppercase;
    max-width: 120px;
    margin: 10px auto 0 auto;
}
.pricing-name {
    font-family: 'Orbitron', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #00d4ff;
    letter-spacing: 3px;
    margin-bottom: 4px;
}
.pricing-price {
    font-family: 'Share Tech Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    color: #ffffff;
    text-shadow: 0 0 20px rgba(0,212,255,0.3);
    margin-bottom: 14px;
}
.pricing-features {
    list-style: none;
    padding: 0;
    margin: 0 0 16px 0;
    text-align: left;
    font-family: 'Rajdhani', sans-serif;
    font-size: 10px;
    color: #8899bb;
}
.pricing-features li { padding: 3px 0; border-bottom: 1px solid rgba(255,255,255,0.02); }
.pricing-features li::before { content: "// "; color: #00d4ff; font-family: 'Share Tech Mono', monospace; font-size: 7px; }
.chat-avatar-robot { width: 40px; height: 40px; border-radius: 6px; background: linear-gradient(135deg, #00d4ff, #0055ff); display: flex; align-items: center; justify-content: center; font-family: 'Orbitron'; font-size: 20px; color: #000; box-shadow: 0 0 15px #00d4ff; margin-right: 10px; }
.chat-avatar-user { width: 40px; height: 40px; border-radius: 6px; background: linear-gradient(135deg, #ffcc00, #ff2a6d); display: flex; align-items: center; justify-content: center; font-family: 'Orbitron'; font-size: 20px; color: #000; box-shadow: 0 0 15px #ff2a6d; margin-left: 10px; }
.chat-bubble-robot { background: rgba(0, 212, 255, 0.08); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 6px; padding: 10px 14px; color: #dce4f0; font-family: 'Rajdhani'; box-shadow: 0 0 10px rgba(0, 212, 255, 0.1); }
.chat-bubble-user { background: rgba(255, 42, 109, 0.08); border: 1px solid rgba(255, 42, 109, 0.3); border-radius: 6px; padding: 10px 14px; color: #dce4f0; font-family: 'Rajdhani'; box-shadow: 0 0 10px rgba(255, 42, 109, 0.1); }
.status-badge { display: inline-block; padding: 5px 16px; border-radius: 2px; font-family: 'Share Tech Mono', monospace; font-size: 9px; letter-spacing: 2px; margin-right: 8px; }
.status-open { background: rgba(0,255,136,0.06); border: 1px solid rgba(0,255,136,0.4); color: #00ff88; }
.status-ai { background: rgba(188,19,254,0.06); border: 1px solid rgba(188,19,254,0.4); color: #bc13fe; animation: pulseAI 2s infinite; }
@keyframes pulseAI { 0%,100% { box-shadow: 0 0 8px rgba(188,19,254,0.2); } 50% { box-shadow: 0 0 20px rgba(188,19,254,0.5); } }
.nav-link { background: transparent !important; color: #8899bb !important; }
.nav-link:hover { background: rgba(0,212,255,0.08) !important; }
.nav-link-selected { background: linear-gradient(160deg, rgba(0,48,96,0.6), rgba(0,28,64,0.8)) !important; color: #00d4ff !important; }
.st-bk { background-color: transparent !important; }
.st-cb { background-color: transparent !important; }
.element-container { margin-bottom: 0 !important; }
.stMarkdown { margin: 0 !important; padding: 0 !important; }
hr { margin: 0.5rem 0 !important; }
header, footer, .st-emotion-cache-16txtl3, .st-emotion-cache-1lcbmhc, .st-emotion-cache-12fmjuu, .st-emotion-cache-1y4p8pa {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}

/* ========== CYBERTECH SIDEBAR TOGGLE BUTTON ========== */
button[kind="header"] {
    background: transparent !important;
    border: 1px solid rgba(0, 212, 255, 0.5) !important;
    border-radius: 4px !important;
    margin-left: 10px !important;
    margin-top: 5px !important;
    backdrop-filter: blur(8px) !important;
    transition: all 0.3s ease !important;
    position: relative;
    overflow: hidden;
}
button[kind="header"]::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.3), transparent);
    transition: left 0.5s ease;
}
button[kind="header"]:hover::before {
    left: 100%;
}
button[kind="header"] svg {
    fill: #00d4ff !important;
    stroke: #00d4ff !important;
    filter: drop-shadow(0 0 8px #00d4ff);
    transition: transform 0.2s ease;
}
button[kind="header"]:hover svg {
    transform: scale(1.1);
    fill: #00ff88 !important;
    stroke: #00ff88 !important;
}
/* Efek neon berkedip */
button[kind="header"] {
    animation: borderGlow 2s infinite;
}
@keyframes borderGlow {
    0% { border-color: rgba(0,212,255,0.5); box-shadow: 0 0 0px #00d4ff; }
    50% { border-color: #00d4ff; box-shadow: 0 0 8px #00d4ff; }
    100% { border-color: rgba(0,212,255,0.5); box-shadow: 0 0 0px #00d4ff; }
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# MAIN HEADER (Statistik digital hanya tampil jika BELUM login)
# ==============================================================================
st.markdown(f"""
<div class="main-title-container">
    <div class="main-logo-container">
        <img src="https://files.manuscdn.com/user_upload_by_module/session_file/310519663520709901/oOIKIIkSvIdagiSw.png" alt="AEROVULPIS" class="custom-logo">
    </div>
    <h1 class="main-title">AEROVULPIS</h1>
    <p class="subtitle-text">V4.0 ULTIMATE</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.get("auth_session"):
    st.markdown("""
    <div class="digital-stats">
        <div class="stat-item">
            <div class="stat-number">500+</div>
            <div class="stat-label">T R A D E R   A K T I F</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">85%</div>
            <div class="stat-label">A K U R A S I   S I N Y A L</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">130+</div>
            <div class="stat-label">T R A D I N G   P A I R</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">76%</div>
            <div class="stat-label">U P T I M E   S E R V E R</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# SIDEBAR CONTROL CENTER
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;margin-bottom:-10px;'>
        <img src='https://files.manuscdn.com/user_upload_by_module/session_file/310519663520709901/oOIKIIkSvIdagiSw.png' style='width:48px;filter:drop-shadow(0 0 12px rgba(0,212,255,0.5));'>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"<h2 style='font-family:Orbitron;text-align:center;font-size:16px;color:#00d4ff;letter-spacing:4px;margin-bottom:0;'>{t['control_center']}</h2>", unsafe_allow_html=True)

    tier_colors = {"free":"#556680","trial":"#00d4ff","weekly":"#00ff88","monthly":"#ffcc00","six_months":"#ff8800","yearly":"#ff2a6d","yearly_promo":"#bc13fe"}
    tier_names = {"free":"FREE","trial":"TRIAL","weekly":"WEEKLY","monthly":"MONTHLY","six_months":"6M PRO","yearly":"ULTIMATE","yearly_promo":"ULTIMATE PROMO"}

    if not st.session_state.get("auth_session"):
        st.markdown("""
        <div style="text-align:center;padding:20px 0;margin-bottom:10px;">
            <h3 style="font-family:'Orbitron',sans-serif;font-size:18px;color:#00d4ff;letter-spacing:3px;text-shadow:0 0 15px rgba(0,212,255,0.5);">
                ⬡ SELAMAT DATANG ⬡
            </h3>
            <p style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#557799;margin:0;">
                AEROVULPIS TERMINAL V4.0 · QUANTUM TRADING SYSTEM
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""<div style="text-align:center;padding:14px;margin:8px 0;background:rgba(0,15,30,0.5);border:1px solid rgba(0,212,255,0.1);border-radius:4px;"><p style="font-family:Orbitron;font-size:10px;color:#00d4ff;margin-bottom:0;letter-spacing:2px;">{t['sign_in_prompt']}</p><p style="font-family:Share Tech Mono;font-size:9px;color:#557799;margin:2px 0 0 0;">{t['sign_in_desc']}</p></div>""", unsafe_allow_html=True)
        st.markdown('<div class="digital-auth-container">', unsafe_allow_html=True)

        if st.session_state.awaiting_otp:
            st.markdown("### Verifikasi Kode OTP")
            st.info(f"Kode 8-digit telah dikirim ke **{st.session_state.temp_reg_email}**. Silakan periksa email Anda.")
            otp_input = st.text_input("Masukkan Kode OTP", max_chars=8, key="otp_input", placeholder="00000000")
            col_otp1, col_otp2 = st.columns(2)
            with col_otp1:
                if st.button("Verifikasi & Login", type="primary", use_container_width=True, key="verify_otp_btn"):
                    if not otp_input:
                        st.warning("Mohon masukkan kode OTP yang telah dikirim.")
                    elif len(otp_input) < 8:
                        st.warning("Kode OTP harus 8 digit.")
                    else:
                        try:
                            supabase_auth = get_supabase_client()
                            resp = supabase_auth.auth.verify_otp({
                                "email": st.session_state.temp_reg_email,
                                "token": otp_input.strip(),
                                "type": "signup"
                            })
                            if resp.user:
                                user = resp.user
                                st.session_state.auth_session = resp.session.access_token if resp.session else "active_session"
                                st.session_state.user_id = user.id
                                st.session_state.user_name = user.user_metadata.get("full_name") or (
                                    st.session_state.temp_reg_email.split("@")[0] if st.session_state.temp_reg_email else "USER")
                                st.session_state.user_email = user.email or st.session_state.temp_reg_email
                                st.session_state.user_avatar = ""
                                tier, exp = get_user_tier(user.id)
                                st.session_state.user_tier = tier
                                st.session_state.user_expired_at = exp[:10] if exp else None
                                sync_user_to_supabase(user.id, user.email or st.session_state.temp_reg_email, st.session_state.user_name, "")
                                st.session_state.daily_analysis_count = 0
                                st.session_state.daily_chatbot_count = 0
                                st.session_state.daily_sentinel_count = 0
                                st.session_state.awaiting_otp = False
                                st.session_state.temp_reg_email = ""
                                send_log(f"REGISTER (OTP): {st.session_state.user_name}")
                                st.success("Akun berhasil diverifikasi. Selamat datang di AeroVulpis!")
                                st.rerun()
                            else:
                                st.error("Kode OTP tidak valid atau telah kadaluarsa.")
                        except:
                            st.error("Kode OTP tidak valid atau telah kadaluarsa.")
            with col_otp2:
                if st.button("Batal", use_container_width=True, key="cancel_otp_btn"):
                    st.session_state.awaiting_otp = False
                    st.session_state.temp_reg_email = ""
                    st.rerun()
        else:
            with st.form("email_password_login_form"):
                st.markdown(f"""<p style="font-family:Orbitron;font-size:9px;color:#557799;letter-spacing:3px;margin:0 0 8px;">{t.get('login_title','AUTHENTICATION SYSTEM')}</p>""", unsafe_allow_html=True)
                email_input = st.text_input(t.get('login_email','EMAIL'), placeholder="ENTER EMAIL ADDRESS", key="login_email", label_visibility="collapsed")
                password_input = st.text_input(t.get('login_password','PASSWORD'), type="password", placeholder="ENTER PASSWORD", key="login_password", label_visibility="collapsed")
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    login_submitted = st.form_submit_button(t.get('login_btn','LOGIN'), width='stretch', type="primary")
                with col_btn2:
                    signup_submitted = st.form_submit_button(t.get('signup_btn','REGISTER'), width='stretch', type="primary")
                if login_submitted and email_input and password_input:
                    try:
                        supabase_auth = get_supabase_client()
                        resp = supabase_auth.auth.sign_in_with_password({"email":email_input.strip(),"password":password_input})
                        if resp and resp.user:
                            user = resp.user
                            st.session_state.auth_session = resp.session.access_token if resp.session else "active_session"
                            st.session_state.user_id = user.id
                            st.session_state.user_name = user.user_metadata.get("full_name") or (user.email.split("@")[0] if user.email else "USER")
                            st.session_state.user_email = user.email or ""
                            st.session_state.user_avatar = user.user_metadata.get("avatar_url","")
                            tier, exp = get_user_tier(user.id)
                            st.session_state.user_tier = tier
                            st.session_state.user_expired_at = exp[:10] if exp else None
                            sync_user_to_supabase(user.id, user.email or "", st.session_state.user_name, st.session_state.user_avatar)
                            a,c,s = get_user_usage(user.id)
                            st.session_state.daily_analysis_count = a
                            st.session_state.daily_chatbot_count = c
                            st.session_state.daily_sentinel_count = s
                            send_log(f"LOGIN: {st.session_state.user_name}")
                            st.rerun()
                    except Exception as e:
                        err = str(e).lower()
                        if "invalid" in err:
                            st.error("Email atau password salah.")
                        elif "not confirmed" in err:
                            st.error("Email belum dikonfirmasi.")
                        else:
                            st.error(f"Gagal login: {err}")
                if signup_submitted and email_input and password_input:
                    email_clean = email_input.strip()
                    if not email_clean:
                        st.error("Mohon masukkan alamat email.")
                    elif len(password_input) < 6:
                        st.error("Password harus minimal 6 karakter.")
                    else:
                        try:
                            supabase_auth = get_supabase_client()
                            resp = supabase_auth.auth.sign_up({"email": email_clean, "password": password_input})
                            if resp.user is not None:
                                st.session_state.awaiting_otp = True
                                st.session_state.temp_reg_email = email_clean
                                st.success("Kode OTP 8-digit telah dikirim ke email Anda.")
                                st.rerun()
                            else:
                                st.warning("Email sudah terdaftar. Silakan LOGIN.")
                        except Exception as e:
                            err = str(e).lower()
                            if "already registered" in err:
                                st.warning("Email sudah terdaftar.")
                            else:
                                st.error(f"Registrasi gagal: {err}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")
        with st.columns(2)[0]:
            if st.button("LUPA PASSWORD", key="forgot_password_btn", width='stretch'):
                st.session_state.show_forgot_password = True
        if st.session_state.get("show_forgot_password"):
            with st.container():
                reset_email = st.text_input("Email untuk reset password", key="reset_email")
                c1,c2=st.columns(2)
                with c1:
                    if st.button("Kirim Link Reset", key="send_reset_btn", width='stretch'):
                        if reset_email:
                            try:
                                get_supabase_client().auth.reset_password_email(reset_email.strip(), options={"redirect_to":"http://localhost:8501"})
                                st.success(f"Link reset password telah dikirim ke {reset_email}.")
                                st.session_state.show_forgot_password = False
                            except Exception as e:
                                st.error(f"Gagal: {str(e)}")
                        else:
                            st.warning("Masukkan email terlebih dahulu.")
                with c2:
                    if st.button("Batal", key="cancel_reset_btn", width='stretch'):
                        st.session_state.show_forgot_password = False
                        st.rerun()
        st.stop()
    # --- LOGGED IN ---
    tier_color = tier_colors.get(st.session_state.user_tier, "#556680")
    tier_name = tier_names.get(st.session_state.user_tier, "FREE")
    avatar_url = st.session_state.get('user_avatar','')
    expired_str = st.session_state.get('user_expired_at')
    expired_display = ""
    if expired_str and st.session_state.user_tier!="free":
        expired_display = f'<p style="font-family:Share Tech Mono;font-size:8px;color:#ff2a6d;margin:2px 0;">EXPIRED: {str(expired_str)[:10]}</p>'
    st.markdown(f"""<div style="background:rgba(0,15,30,0.7);border:1px solid {tier_color}40;border-radius:4px;padding:16px;margin:8px 0;text-align:center;">{f'<img src="{avatar_url}" style="width:40px;height:40px;border-radius:2px;margin-bottom:10px;border:1px solid {tier_color};">' if avatar_url else '<div style="width:40px;height:40px;border-radius:2px;margin:0 auto 10px;background:linear-gradient(160deg,#001a33,#003060);display:flex;align-items:center;justify-content:center;font-size:18px;">V</div>'}<p style="font-family:Rajdhani;font-size:10px;color:#6688aa;margin:0;letter-spacing:1px;">{t['welcome']}</p><p style="font-family:Orbitron;font-size:12px;color:#e0e6f0;margin:3px 0;letter-spacing:1px;">{st.session_state.user_name.upper()}</p><p style="font-family:Share Tech Mono;font-size:8px;color:#557799;margin:2px 0;">{t['user_id_label']}: {st.session_state.user_id[:16]}...</p><p style="font-family:Share Tech Mono;font-size:8px;color:#557799;margin:2px 0;">{t['tier_label']}: <span style="color:{tier_color};">{tier_name}</span></p>{expired_display}</div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t['logout'], width='stretch', key="logout_btn"):
            try:
                get_supabase_client().auth.sign_out()
            except:
                pass
            for key in ['auth_session','user_id','user_name','user_email','user_avatar']:
                if key in st.session_state:
                    del st.session_state[key]
            st.query_params.clear()
            st.session_state.user_tier = "free"
            st.session_state.show_activation = False
            st.rerun()
    with col2:
        if st.button(t['activate_key'], width='stretch', key="show_activation_btn"):
            st.session_state.show_activation = not st.session_state.show_activation

    if st.session_state.get("show_activation"):
        with st.sidebar.container():
            st.markdown("---")
            st.markdown("### AKTIVASI PREMIUM")
            key_input = st.text_input("Masukkan Kunci Lisensi:", key="premium_key_input", placeholder="XXXX-XXXX-XXXX-XXXX")
            ca1, ca2 = st.columns(2)
            with ca1:
                if st.button("VALIDASI", type="primary", use_container_width=True, key="validate_key_btn"):
                    if key_input and st.session_state.user_id:
                        loading_ph = st.empty()
                        with loading_ph.container():
                            st.markdown('<div style="text-align:center;padding:20px;"><div class="cyber-ring-loader"><div class="cyber-ring"></div><div class="cyber-ring"></div><div class="cyber-ring"></div></div></div>', unsafe_allow_html=True)
                        time.sleep(2.5)
                        success, message = activate_key(st.session_state.user_id, key_input.strip().upper())
                        loading_ph.empty()
                        if success:
                            st.session_state.user_tier, st.session_state.user_expired_at = get_user_tier(st.session_state.user_id)
                            st.success(t['activation_success'])
                            st.info(message)
                            st.balloons()
                            st.session_state.show_activation = False
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"{t['activation_failed']}: {message}")
                    else:
                        st.warning("ENTER VALID LICENSE KEY")
            with ca2:
                if st.button("BATAL", use_container_width=True, key="cancel_activation_btn"):
                    st.session_state.show_activation = False
                    st.rerun()

    st.markdown("<p style='font-family:Share Tech Mono;font-size:9px;color:#445566;text-align:center;margin:8px 0;'>AEROVULPIS V4.0 | DYNAMIHATCH</p>", unsafe_allow_html=True)
    st.caption("2026 | SYSTEM ACTIVE")

    category = st.selectbox(t['category'], list(instruments.keys()))
    asset_name = st.selectbox(t['asset'], list(instruments[category].keys()))
    ticker_input = instruments[category][asset_name]
    ticker_display = f"{asset_name} [{ticker_input}]"
    st.markdown("---")
    tf_options = {"30M":{"period":"5d","interval":"30m"},"1H":{"period":"1mo","interval":"1h"},"3H":{"period":"1mo","interval":"1h"},"4H":{"period":"1mo","interval":"1h"},"1D":{"period":"1y","interval":"1d"},"1W":{"period":"2y","interval":"1wk"}}
    selected_tf_display = st.selectbox(t['timeframe'], list(tf_options.keys()), index=0)
    period = tf_options[selected_tf_display]["period"]
    interval = tf_options[selected_tf_display]["interval"]

    st.session_state.current_period = period
    st.session_state.current_interval = interval

    user_is_premium = st.session_state.user_tier != "free"

    # ==========================================================================
    # MENU UTAMA (DITAMBAHKAN "Our Journey" setelah Help & Support)
    # ==========================================================================
    menu_options = ["Live Dashboard"]
    menu_icons = ["activity"]
    if user_is_premium:
        menu_options += ["AeroVulpis Sentinel","Signal Analysis","Market Sessions","Market News","Smart Alert Center","Risk Management"]
        menu_icons += ["shield-shaded","graph-up-arrow","globe","newspaper","bell-fill","shield-fill"]
    else:
        menu_options += ["AeroVulpis Sentinel (Premium)","Signal Analysis (Premium)","Market Sessions (Premium)","Market News (Premium)","Smart Alert Center (Premium)","Risk Management (Premium)"]
        menu_icons += ["lock-fill"]*6
    menu_options += ["Broker","Economic Radar","Chatbot AI","Tingkatkan Level","Settings","Help & Support", "Our Journey"]
    menu_icons += ["bank","calendar-event","chat-dots","rocket-takeoff","gear","question-circle","compass"]

    st.session_state.menu_selection = option_menu(
        menu_title=t['navigation'], options=menu_options, icons=menu_icons, menu_icon="cast", default_index=0,
        styles={
            "container":{"padding":"5!important","background-color":"transparent"},
            "icon":{"color":"#00d4ff","font-size":"13px"},
            "nav-link":{"font-size":"11px","text-align":"left","margin":"2px 0","padding":"10px 12px","border-radius":"3px","font-family":"Rajdhani","font-weight":"500","letter-spacing":"1px","background":"rgba(0,212,255,0.015)","border":"1px solid rgba(0,212,255,0.06)"},
            "nav-link-selected":{"background":"linear-gradient(160deg,rgba(0,48,96,0.4),rgba(0,28,64,0.6))","border":"1px solid #00d4ff","color":"#00d4ff","box-shadow":"0 0 18px rgba(0,212,255,0.12)","font-weight":"700"},
        }
    )
    if "(Premium)" in st.session_state.menu_selection and not user_is_premium:
        st.error(f"**{t['premium_lock']}**")
        st.info(t['premium_msg'])
        st.stop()

    user_limits = LIMITS.get(st.session_state.user_tier, LIMITS["free"])
    st.markdown("---")
    st.markdown(f"""<div style="background:rgba(0,15,30,0.5);border:1px solid rgba(0,212,255,0.1);border-radius:4px;padding:12px;margin-top:8px;"><p style="font-family:Orbitron;font-size:8px;color:#557799;margin:0 0 8px;letter-spacing:2px;">{t['daily_usage_label']}</p>
        <div style="margin-bottom:6px;"><p style="font-family:Share Tech Mono;font-size:10px;color:#00d4ff;margin:2px 0;display:flex;justify-content:space-between;"><span>AI DEEP ANALYSIS</span><span>{st.session_state.daily_analysis_count}/{user_limits['analysis_per_day']}</span></p><div style="background:rgba(255,255,255,0.05);height:3px;border-radius:1px;overflow:hidden;"><div style="background:#00d4ff;width:{min(100,(st.session_state.daily_analysis_count/user_limits['analysis_per_day'])*100) if user_limits['analysis_per_day']>0 else 0}%;height:100%;border-radius:1px;"></div></div></div>
        <div style="margin-bottom:6px;"><p style="font-family:Share Tech Mono;font-size:10px;color:#bc13fe;margin:2px 0;display:flex;justify-content:space-between;"><span>AI SENTINEL PRO</span><span>{st.session_state.daily_sentinel_count}/{user_limits['sentinel_per_day']}</span></p><div style="background:rgba(255,255,255,0.05);height:3px;border-radius:1px;overflow:hidden;"><div style="background:#bc13fe;width:{min(100,(st.session_state.daily_sentinel_count/user_limits['sentinel_per_day'])*100) if user_limits['sentinel_per_day']>0 else 0}%;height:100%;border-radius:1px;"></div></div></div>
        <div style="margin-bottom:6px;"><p style="font-family:Share Tech Mono;font-size:10px;color:#00ff88;margin:2px 0;display:flex;justify-content:space-between;"><span>CHATBOT</span><span>{st.session_state.daily_chatbot_count}/{user_limits['chatbot_per_day']}</span></p><div style="background:rgba(255,255,255,0.05);height:3px;border-radius:1px;overflow:hidden;"><div style="background:#00ff88;width:{min(100,(st.session_state.daily_chatbot_count/user_limits['chatbot_per_day'])*100)}%;height:100%;border-radius:1px;"></div></div></div></div>""", unsafe_allow_html=True)

check_smart_alerts()

# ==============================================================================
# 1. AEROVULPIS SENTINEL PRO
# ==============================================================================
if st.session_state.menu_selection == "AeroVulpis Sentinel" or st.session_state.menu_selection == "AeroVulpis Sentinel (Premium)":
    st.markdown(f"""
    <div class="sentinel-container">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
            <div>
                <h2 class="sentinel-title">{t['sentinel_title']}</h2>
                <div style="display:flex;gap:12px;margin-top:12px;">
                    <span class="status-badge status-open">{t['market_status']}</span>
                    <span class="status-badge status-ai">{t['sentinel_ai_status']}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_chart, col_intel = st.columns([2, 1])

    with col_chart:
        tv_symbol = ticker_input.replace("-USD", "USD").replace("=X", "").replace(".JK", "")
        if "GC=F" in ticker_input:
            tv_symbol = "COMEX:GC1!"
        elif "SI=F" in ticker_input:
            tv_symbol = "COMEX:SI1!"
        elif "CL=F" in ticker_input:
            tv_symbol = "NYMEX:CL1!"

        tv_html = f"""
        <div class="tradingview-widget-container" style="height:500px;width:100%;">
          <div id="tv_sentinel" style="height:500px;"></div>
          <script src="https://s3.tradingview.com/tv.js"></script>
          <script>
          new TradingView.widget({{"autosize":true,"symbol":"{tv_symbol}","interval":"D","timezone":"Asia/Jakarta","theme":"dark","style":"1","locale":"en","enable_publishing":false,"allow_symbol_change":true,"container_id":"tv_sentinel","studies":["RSI@tv-basicstudies","MACD@tv-basicstudies"]}});
          </script>
        </div>
        """
        st.components.v1.html(tv_html, height=500)

        st.markdown("<br>", unsafe_allow_html=True)
        loading_placeholder = st.empty()

        if st.button(t['sentinel_btn'], key="sentinel_pro_btn", use_container_width=True):
            market = get_market_data(ticker_input)
            if category in ["ID STOCKS"] or (asset_name == "IHSG" and category == "INDICES"):
                df = get_id_historical_data(ticker_input, period, interval)
            else:
                df = get_historical_data(ticker_input, period, interval)
            if market and not df.empty:
                df = add_technical_indicators(df)
                score, signal, reasons, bull, bear, neut = get_weighted_signal(df)

                loading_placeholder.markdown("""
                <style>
                @keyframes quantumSpin {
                    0% { transform: rotate(0deg); opacity: 0.9; }
                    50% { transform: rotate(180deg); opacity: 0.4; }
                    100% { transform: rotate(360deg); opacity: 0.9; }
                }
                @keyframes glitchText {
                    0% { text-shadow: -2px 0 #00d4ff, 2px 0 #00d4ff; opacity: 1; }
                    50% { text-shadow: 2px 0 #00d4ff, -2px 0 #00d4ff; opacity: 0.8; }
                    100% { text-shadow: 0 0 15px #00d4ff; opacity: 1; }
                }
                @keyframes scanline {
                    0% { transform: translateY(-100%); }
                    100% { transform: translateY(100%); }
                }
                @keyframes quantumPulse {
                    0% { box-shadow: 0 0 0 0 #00d4ff80; }
                    70% { box-shadow: 0 0 0 15px #00d4ff00; }
                    100% { box-shadow: 0 0 0 0 #00d4ff00; }
                }
                .quantum-ring-loader {
                    position: relative;
                    width: 100px;
                    height: 100px;
                    margin: 0 auto;
                }
                .quantum-ring {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    border-radius: 50%;
                    border: 2px solid transparent;
                    animation: quantumSpin 2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
                    box-shadow: 0 0 15px rgba(0, 212, 255, 0.8);
                }
                .quantum-ring:nth-child(1) {
                    width: 40px;
                    height: 40px;
                    margin-left: -20px;
                    margin-top: -20px;
                    border-top-color: #00d4ff;
                    border-right-color: #00d4ff;
                    animation-duration: 1.2s;
                }
                .quantum-ring:nth-child(2) {
                    width: 70px;
                    height: 70px;
                    margin-left: -35px;
                    margin-top: -35px;
                    border-bottom-color: #00d4ff;
                    border-left-color: #00d4ff;
                    animation-duration: 1.8s;
                    animation-delay: 0.2s;
                }
                .quantum-ring:nth-child(3) {
                    width: 100px;
                    height: 100px;
                    margin-left: -50px;
                    margin-top: -50px;
                    border-top-color: #00d4ff;
                    border-right-color: #00d4ff;
                    animation-duration: 2.4s;
                    animation-delay: 0.4s;
                }
                .quantum-loading-text {
                    font-family: 'Orbitron', monospace;
                    font-size: 16px;
                    font-weight: 700;
                    color: #00d4ff;
                    text-align: center;
                    letter-spacing: 4px;
                    animation: glitchText 0.8s infinite alternate;
                    margin-top: 20px;
                }
                .sentinel-loading-container {
                    position: relative;
                    text-align: center;
                    padding: 30px 20px;
                    background: rgba(0, 10, 25, 0.7);
                    border-radius: 8px;
                    border: 1px solid #00d4ff33;
                    overflow: hidden;
                    backdrop-filter: blur(4px);
                }
                .sentinel-loading-container::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(180deg, transparent, #00d4ff15, transparent);
                    animation: scanline 3s linear infinite;
                    pointer-events: none;
                }
                .quantum-pulse {
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    background: #00d4ff;
                    border-radius: 50%;
                    margin: 0 5px;
                    animation: quantumPulse 1.5s infinite;
                }
                .quantum-pulse:nth-child(2) { animation-delay: 0.3s; }
                .quantum-pulse:nth-child(3) { animation-delay: 0.6s; }
                </style>
                <div class="sentinel-loading-container">
                    <div class="quantum-ring-loader">
                        <div class="quantum-ring"></div>
                        <div class="quantum-ring"></div>
                        <div class="quantum-ring"></div>
                    </div>
                    <p class="quantum-loading-text"> QUANTUM SENTINEL PROCESSING </p>
                    <p style="font-family:'Share Tech Mono', monospace; font-size:10px; color:#00d4ff; margin-top:10px; letter-spacing:2px;">
                        >> INITIALIZING QUANTUM CORE <<
                    </p>
                    <div style="margin-top: 15px;">
                        <span class="quantum-pulse"></span>
                        <span class="quantum-pulse"></span>
                        <span class="quantum-pulse"></span>
                    </div>
                    <p style="font-family:'Share Tech Mono', monospace; font-size:9px; color:#00d4ffaa; margin-top:12px;">
                        EXECUTING PREDICTIVE ALGORITHMS...
                    </p>
                </div>
                """, unsafe_allow_html=True)

                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)

                analysis = get_sentinel_analysis(asset_name, market, df, signal, reasons)
                st.session_state.sentinel_analysis = analysis

                loading_placeholder.empty()
                progress_bar.empty()
            else:
                st.error("DATA ACQUISITION FAILED | CHECK CONNECTION")

    with col_intel:
        st.markdown(f"""<div class="intelligence-panel"><div class="intel-header">{t['sentinel_intel']}</div><div class="intel-content">""", unsafe_allow_html=True)
        if st.session_state.sentinel_analysis:
            st.markdown(st.session_state.sentinel_analysis, unsafe_allow_html=True)
        else:
            st.info(t['sentinel_placeholder'])
        st.markdown("</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# 2. LIVE DASHBOARD
# ==============================================================================
elif st.session_state.menu_selection == "Live Dashboard":
    market = get_market_data(ticker_input)
    if category in ["ID STOCKS"] or (asset_name == "IHSG" and category == "INDICES"):
        df = get_id_historical_data(ticker_input, period, interval)
    else:
        df = get_historical_data(ticker_input, period, interval)

    if market and not df.empty:
        if selected_tf_display in ["3H", "4H"]:
            rule = "3h" if selected_tf_display == "3H" else "4h"
            df = df.resample(rule).agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}).dropna()

        df = add_technical_indicators(df)
        if 'SMA50' not in df.columns:
            st.warning("⚠️ Data historis tidak lengkap untuk instrumen ini. Coba instrumen lain atau periksa koneksi.")
            st.stop()
        score, signal, reasons, bull, bear, neut = get_weighted_signal(df)

        c1, c2, c3, c4 = st.columns(4)

        if market['price'] < 10:
            price_str = f"{market['price']:,.4f}"
        else:
            price_str = f"{market['price']:,.2f}"

        now_wib = datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%H:%M")

        with c1:
            st.markdown(f'<div class="glass-card"><p style="color:#557799;margin:0;font-size:9px;letter-spacing:2px;">{t["live_price"]}</p><p style="font-family:Share Tech Mono;color:#00ff88;font-size:24px;margin:0;text-shadow:0 0 10px rgba(0,255,136,0.4);">{price_str}</p><p style="font-size:8px;color:#556680;margin-top:4px;">*Harga mungkin memiliki selisih kecil dengan platform trading akibat perbedaan sumber data dan spread broker.</p></div>', unsafe_allow_html=True)

            st.markdown("""
            <div style="text-align:center; margin-top:5px;">
                <span style="font-family:'Share Tech Mono', monospace; font-size:8px; color:#00d4ff; letter-spacing:1px; background:rgba(0,212,255,0.06); padding:2px 8px; border-radius:2px;">
                ↓ SCROLL KEBAWAH UNTUK MENDAPATKAN SINYAL TRADING DARI AI ↓
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.4); border:1px solid #00d4ff30; border-radius:4px; padding:6px 10px; margin-top:6px; text-align:center;">
                <span style="font-family:'Share Tech Mono', monospace; font-size:9px; color:#00d4ff; letter-spacing:2px;">LAST UPDATE (WIB)</span>
                <div style="font-family:'Orbitron', monospace; font-size:20px; font-weight:700; color:#00ff88; text-shadow:0 0 8px #00ff88; letter-spacing:2px; margin-top:2px;">{now_wib}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="text-align:center; margin-top:6px;">
                <span style="font-family:'Share Tech Mono', monospace; font-size:8px; color:#00d4ff; letter-spacing:1px; background:rgba(0,212,255,0.08); padding:2px 6px; border-radius:2px;">
                [ PRICE UPDATED EVERY 5 MINUTES ]
                </span>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            color = "#00ff88" if "BUY" in signal else "#ff2a6d" if "SELL" in signal else "#ffcc00"
            st.markdown(f'<div class="glass-card"><p style="color:#557799;margin:0;font-size:9px;letter-spacing:2px;">{t["signal"]}</p><p style="font-family:Orbitron;font-size:20px;margin:0;color:{color};text-shadow:0 0 15px {color};">{signal}</p></div>', unsafe_allow_html=True)

        with c3:
            rsi_val = df["RSI"].iloc[-1] if "RSI" in df.columns else 0.0
            st.markdown(f'<div class="glass-card"><p style="color:#557799;margin:0;font-size:9px;letter-spacing:2px;">{t["rsi"]}</p><p style="font-family:Share Tech Mono;color:#00d4ff;font-size:24px;margin:0;">{rsi_val:.1f}</p></div>', unsafe_allow_html=True)

        with c4:
            atr_val = df["ATR"].iloc[-1] if "ATR" in df.columns else 0.0
            st.markdown(f'<div class="glass-card"><p style="color:#557799;margin:0;font-size:9px;letter-spacing:2px;">{t["atr"]}</p><p style="font-family:Share Tech Mono;color:#8899bb;font-size:24px;margin:0;">{atr_val:.4f}</p></div>', unsafe_allow_html=True)

        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode='lines', name='PRICE', line=dict(color='#00ff88', width=1.5)))
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], line=dict(color='#00d4ff', width=1, dash='dot'), name='SMA50'))
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA200"], line=dict(color='#bc13fe', width=1, dash='dash'), name='SMA200'))
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=10, r=10, t=10, b=10), height=380,
                          legend=dict(orientation="h", y=-0.15, font=dict(size=10)),
                          xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)'),
                          yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)'))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        col_g, col_a = st.columns([1, 1])

        with col_g:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            gauge_color = color
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                number={"font": {"family": "Orbitron", "color": "#00d4ff", "size": 36}, "suffix": "%"},
                title={"text": "TECHNICAL STRENGTH", "font": {"family": "Orbitron", "color": "#00d4ff", "size": 14}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#00d4ff", "tickfont": {"color": "#8899bb", "size": 10}},
                    "bar": {"color": gauge_color, "thickness": 0.15},
                    "bgcolor": "rgba(0,0,0,0)",
                    "borderwidth": 1,
                    "bordercolor": "rgba(0,212,255,0.3)",
                    "steps": [
                        {"range": [0, 30], "color": "rgba(255,42,109,0.15)"},
                        {"range": [30, 45], "color": "rgba(255,42,109,0.08)"},
                        {"range": [45, 55], "color": "rgba(255,204,0,0.08)"},
                        {"range": [55, 70], "color": "rgba(0,255,136,0.08)"},
                        {"range": [70, 100], "color": "rgba(0,255,136,0.15)"}
                    ],
                    "threshold": {"line": {"color": "#ffffff", "width": 3}, "thickness": 0.85, "value": score}
                },
                delta={"reference": 50, "increasing": {"color": "#00ff88"}, "decreasing": {"color": "#ff2a6d"}, "font": {"size": 12}}
            ))
            fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=220, margin=dict(l=10, r=10, t=35, b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_a:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-family:Orbitron;font-size:13px;color:#00d4ff;letter-spacing:2px;margin-bottom:10px;'>{t['ai_analysis']}</p>", unsafe_allow_html=True)
            for r in reasons:
                st.markdown(f"<p style='font-family:Share Tech Mono;font-size:10px;color:#8899bb;margin:3px 0;'>[ {r} ]</p>", unsafe_allow_html=True)
            if st.button(t['generate_ai'], use_container_width=True):
                with st.spinner("AEROVULPIS ENGINE PROCESSING..."):
                    ai_anal = get_deep_analysis(asset_name, market, df, signal, reasons)
                    st.info(ai_anal)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Data tidak tersedia. Pilih instrumen lain atau cek koneksi.")


# ==============================================================================
# 3. SIGNAL ANALYSIS
# ==============================================================================
elif st.session_state.menu_selection == "Signal Analysis" or st.session_state.menu_selection == "Signal Analysis (Premium)":
    def should_update_signal():
        now_wib = datetime.now(pytz.timezone('Asia/Jakarta'))
        today_7am = now_wib.replace(hour=7, minute=0, second=0, microsecond=0)
        if now_wib >= today_7am:
            try:
                supabase_admin = get_supabase_admin()
                res = supabase_admin.table("signal_cache").select("created_at").order("created_at", desc=True).limit(1).execute()
                if res and res.data:
                    last_signal_time = safe_parse_timestamp(res.data[0]["created_at"])
                    if last_signal_time and last_signal_time.astimezone(pytz.timezone('Asia/Jakarta')).date() == now_wib.date():
                        return False
                return True
            except:
                return True
        return False

    if should_update_signal():
        update_all_signals()
        st.toast("🔄 Sinyal trading harian diperbarui (07:00 WIB)", icon="📡")

    st.markdown(f'<h2 style="font-family:Orbitron;font-size:22px;color:#00d4ff;letter-spacing:3px;margin-bottom:5px;">SIGNAL MATRIX v4.0</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Share Tech Mono;font-size:9px;color:#557799;margin-bottom:15px;">Live trading signal untuk XAUUSD, BTCUSD, EURUSD, GBPUSD | Update setiap 07:00 WIB | Data berlaku 24 jam</p>', unsafe_allow_html=True)

    signal_instruments = ["GOLD (XAUUSD)", "BITCOIN", "EUR/USD", "GBP/USD"]
    display_names = {
        "GOLD (XAUUSD)": "XAUUSD (Gold)",
        "BITCOIN": "BTCUSD (Bitcoin)",
        "EUR/USD": "EURUSD (Euro/Dollar)",
        "GBP/USD": "GBPUSD (Pound/Dollar)"
    }
    ticker_map = {"GOLD (XAUUSD)": "GC=F", "BITCOIN": "BTC-USD", "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X"}

    all_signals = []
    for inst in signal_instruments:
        signal_data = get_cached_signal(inst)
        if signal_data:
            all_signals.append(signal_data)

    if all_signals:
        latest_update = max([s["updated_at"] for s in all_signals])
        if latest_update:
            latest_update_wib = safe_parse_timestamp(latest_update).astimezone(pytz.timezone('Asia/Jakarta')).strftime("%H:%M WIB, %d %b %Y")
            st.markdown(f"""
            <div style="text-align:right; margin-bottom:16px;">
                <span style="font-family:'Share Tech Mono'; font-size:9px; color:#00d4ff;">⟳ LAST SIGNAL UPDATE: {latest_update_wib}</span>
            </div>
            """, unsafe_allow_html=True)

        current_prices = {}
        for inst in signal_instruments:
            ticker = ticker_map.get(inst)
            if ticker:
                m_data = get_market_data(ticker)
                if m_data:
                    current_prices[inst] = m_data["price"]

        for sig in all_signals:
            inst = sig["instrument"]
            signal_type = sig["signal_type"]
            entry = sig["entry_price"]
            sl = sig["stop_loss"]
            tp1 = sig["take_profit_1"]
            tp2 = sig["take_profit_2"]
            tp3 = sig["take_profit_3"]
            rr = sig.get("risk_reward_ratio", 0)

            curr_price = current_prices.get(inst)
            tp1_hit = False
            tp2_hit = False
            tp3_hit = False
            sl_hit = False
            if curr_price:
                if signal_type == "BUY":
                    if curr_price >= tp1: tp1_hit = True
                    if curr_price >= tp2: tp2_hit = True
                    if curr_price >= tp3: tp3_hit = True
                    if curr_price <= sl: sl_hit = True
                else:
                    if curr_price <= tp1: tp1_hit = True
                    if curr_price <= tp2: tp2_hit = True
                    if curr_price <= tp3: tp3_hit = True
                    if curr_price >= sl: sl_hit = True

            border_color = "#00ff88" if signal_type == "BUY" else "#ff2a6d"
            signal_color = "#00ff88" if signal_type == "BUY" else "#ff2a6d"
            signal_badge = "🟢 BULLISH" if signal_type == "BUY" else "🔴 BEARISH"

            tp1_badge = '<span class="cyber-success">[✓]</span>' if tp1_hit else '<span class="cyber-fail">[✗]</span>' if sl_hit else '<span class="cyber-success">[~]</span>'
            tp2_badge = '<span class="cyber-success">[✓]</span>' if tp2_hit else '<span class="cyber-fail">[✗]</span>' if sl_hit else '<span class="cyber-success">[~]</span>'
            tp3_badge = '<span class="cyber-success">[✓]</span>' if tp3_hit else '<span class="cyber-fail">[✗]</span>' if sl_hit else '<span class="cyber-success">[~]</span>'
            sl_badge = '<span class="cyber-fail">[✗]</span>' if sl_hit else '<span class="cyber-success">[ACTIVE]</span>'

            st.markdown(f"""
            <div style="background:rgba(0,15,30,0.7); border-left:4px solid {border_color}; border-radius:6px; padding:16px; margin-bottom:20px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap;">
                    <p style="font-family:Orbitron; font-size:16px; color:#00d4ff; margin:0;">{display_names.get(inst, inst)}</p>
                    <span style="font-family:Share Tech Mono; font-size:12px; font-weight:700; color:{signal_color}; background:rgba({255 if signal_type=='BUY' else 42}, {136 if signal_type=='BUY' else 42}, {136 if signal_type=='BUY' else 109}, 0.15); padding:4px 12px; border-radius:4px;">{signal_badge}</span>
                </div>
                <div class="signal-grid">
                    <div class="signal-item"><div class="signal-label">ENTRY</div><div class="entry-number">{format_price_display(entry, inst)}</div></div>
                    <div class="signal-item"><div class="signal-label">STOP LOSS</div><div class="sl-number">{format_price_display(sl, inst)} {sl_badge}</div></div>
                    <div class="signal-item"><div class="signal-label">RISK:REWARD</div><div class="signal-number">1:{rr:.1f}</div></div>
                    <div class="signal-item"><div class="signal-label">CONFIDENCE</div><div class="signal-number">{85 if signal_type=='BUY' else 72}%</div></div>
                </div>
                <div style="margin-top:8px;">
                    <div class="signal-label">TAKE PROFIT TARGETS</div>
                    <div style="display:flex; gap:16px; margin-top:6px; flex-wrap:wrap;">
                        <div><span class="digital-check-bull">TP 1</span> <span class="entry-number">{format_price_display(tp1, inst)}</span> {tp1_badge} <span class="signal-target-hit">R:R 1:{rr}</span></div>
                        <div><span class="digital-check-bull">TP 2</span> <span class="entry-number">{format_price_display(tp2, inst)}</span> {tp2_badge} <span class="signal-target-hit">R:R 1:{rr*2:.1f}</span></div>
                        <div><span class="digital-check-bull">TP 3</span> <span class="entry-number">{format_price_display(tp3, inst)}</span> {tp3_badge} <span class="signal-target-hit">R:R 1:{rr*3:.1f}</span></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-top:20px; padding:12px; background:rgba(0,212,255,0.03); border-radius:4px; text-align:center;">
            <p style="font-family:'Share Tech Mono'; font-size:9px; color:#557799;">⚡ Sinyal ini dihasilkan oleh sistem otomatis berdasarkan analisis teknikal. [✓] = TP Tercapai | [✗] = SL Tersentuh | [~] = Belum tercapai.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Belum ada sinyal yang tersedia. Sistem akan memperbarui otomatis setiap jam 07:00 WIB.")


# ==============================================================================
# 4. MARKET SESSIONS
# ==============================================================================
elif st.session_state.menu_selection == "Market Sessions" or st.session_state.menu_selection == "Market Sessions (Premium)":
    market_session_status()


# ==============================================================================
# 5. MARKET NEWS
# ==============================================================================
elif st.session_state.menu_selection == "Market News" or st.session_state.menu_selection == "Market News (Premium)":
    st.markdown(f'<h2 style="font-family:Orbitron;font-size:22px;color:#00d4ff;letter-spacing:3px;margin-bottom:5px;">{t["market_news"]}</h2>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-family:Share Tech Mono;font-size:9px;color:#557799;margin-bottom:15px;">{t["news_updated"]}</p>', unsafe_allow_html=True)

    news_categories = ["General", "Stock", "Geopolitics", "Gold & Silver", "Forex", "Ekonomi Indonesia", "Indonesian Stock", "Crypto"]
    selected_news_cat = st.segmented_control(t['news_filter'], news_categories, default="General")

    articles, error = get_news_data(selected_news_cat, 10)
    if error and not articles:
        st.error(error)
    elif articles:
        for a in articles:
            st.markdown(f"""
            <div class="news-card">
                <p style="font-family:Orbitron;font-size:13px;color:#00d4ff;margin:0 0 5px;letter-spacing:1px;">{a.get('title','NO TITLE')}</p>
                <p style="font-family:Share Tech Mono;font-size:9px;color:#557799;margin:0 0 8px;">{a.get('source','')} | {a.get('publishedAt','')}</p>
                <p style="font-family:Rajdhani;font-size:11px;color:#8899bb;line-height:1.5;">{a.get('description','')[:300]}{'...' if len(a.get('description',''))>300 else ''}</p>
                <a href="{a.get('url','#')}" target="_blank" style="font-family:Share Tech Mono;font-size:9px;color:#00ff88;text-decoration:none;letter-spacing:1px;">[ ACCESS SOURCE ]</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(t['no_news'])


# ==============================================================================
# 6. SMART ALERT CENTER
# ==============================================================================
elif st.session_state.menu_selection == "Smart Alert Center" or st.session_state.menu_selection == "Smart Alert Center (Premium)":
    max_alerts = LIMITS.get(st.session_state.user_tier, LIMITS["free"])["alert_per_day"]
    st.markdown(f"""
    <div style="border:1px solid rgba(0,212,255,0.25);border-radius:6px;padding:28px;background:rgba(0,15,30,0.5);box-shadow:0 0 30px rgba(0,212,255,0.06);margin-bottom:20px;">
        <div style="text-align:center;margin-bottom:22px;">
            <p class="cyber-glow-text" style="font-size:24px;margin:0;letter-spacing:4px;">{t['alert_title']}</p>
            <p class="cyber-glow-text" style="font-size:15px;margin:6px 0;letter-spacing:3px;">{t['alert_subtitle']}</p>
            <div style="display:flex;justify-content:center;gap:24px;margin-top:12px;">
                <span style="font-family:Share Tech Mono;font-size:10px;color:#00ff88;text-shadow:0 0 8px rgba(0,255,136,0.5);">{t['alert_online']}</span>
                <span style="font-family:Share Tech Mono;font-size:10px;color:#00d4ff;text-shadow:0 0 8px rgba(0,212,255,0.5);">{t['alert_sync']}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    smart_alert_widget(max_alerts=max_alerts)
    st.markdown("</div>", unsafe_allow_html=True)
    time.sleep(60)
    st.rerun()


# ==============================================================================
# 7. RISK MANAGEMENT
# ==============================================================================
elif st.session_state.menu_selection == "Risk Management" or st.session_state.menu_selection == "Risk Management (Premium)":
    st.markdown(f"""
    <div class="risk-cyber-container">
        <h2 class="risk-hud-title">RISK FRAMEWORK V4.0</h2>
        <p class="risk-hud-subtitle">QUANTUM POSITION SIZING &middot; HOLOGRAPHIC PROJECTION &middot; NEURAL RISK ENGINE</p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:4px;margin:12px 0;">
        <div style="background:rgba(0,20,50,0.5);border:1px solid rgba(0,212,255,0.12);border-radius:3px;padding:10px 4px;text-align:center;">
            <div style="font-size:14px;color:#00d4ff;margin-bottom:3px;">&#9650;</div>
            <p style="font-family:Orbitron;font-size:5px;font-weight:700;color:#00d4ff;letter-spacing:1px;margin:0 0 1px;">TRADING RULES</p>
            <p style="font-family:Share Tech Mono;font-size:4px;color:#557799;margin:0;">SL DEFINITION MATRIX</p>
        </div>
        <div style="background:rgba(0,20,50,0.5);border:1px solid rgba(0,255,136,0.12);border-radius:3px;padding:10px 4px;text-align:center;">
            <div style="font-size:14px;color:#00ff88;margin-bottom:3px;">&#9632;</div>
            <p style="font-family:Orbitron;font-size:5px;font-weight:700;color:#00ff88;letter-spacing:1px;margin:0 0 1px;">POSITION SIZE</p>
            <p style="font-family:Share Tech Mono;font-size:4px;color:#557799;margin:0;">QUANTUM SCALE LOGIC</p>
        </div>
        <div style="background:rgba(0,20,50,0.5);border:1px solid rgba(188,19,254,0.12);border-radius:3px;padding:10px 4px;text-align:center;">
            <div style="font-size:14px;color:#bc13fe;margin-bottom:3px;">&#9670;</div>
            <p style="font-family:Orbitron;font-size:5px;font-weight:700;color:#bc13fe;letter-spacing:1px;margin:0 0 1px;">CONFIDENCE</p>
            <p style="font-family:Share Tech Mono;font-size:4px;color:#557799;margin:0;">NEURAL REAL-TIME</p>
        </div>
        <div style="background:rgba(0,20,50,0.5);border:1px solid rgba(255,42,109,0.12);border-radius:3px;padding:10px 4px;text-align:center;">
            <div style="font-size:14px;color:#ff2a6d;margin-bottom:3px;">&#9881;</div>
            <p style="font-family:Orbitron;font-size:5px;font-weight:700;color:#ff2a6d;letter-spacing:1px;margin:0 0 1px;">RISK MGMT</p>
            <p style="font-family:Share Tech Mono;font-size:4px;color:#557799;margin:0;">TACTICAL PROTOCOL</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="risk-neon-divider"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown(f'<p class="section-title" style="margin-top:0;font-size:10px;">{t["funding_details"]}</p>', unsafe_allow_html=True)
        st.markdown('<div class="risk-input-card" style="padding:10px;">', unsafe_allow_html=True)
        balance = st.number_input("bal", value=1000.0, step=100.0, min_value=100.0, key="sim_balance", label_visibility="collapsed")
        st.markdown(f'<p style="font-family:Share Tech Mono;font-size:18px;color:#00ff88;text-shadow:0 0 10px rgba(0,255,136,0.4);margin:0;text-align:center;">${balance:,.2f}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<p class="section-title" style="margin-top:0;font-size:10px;">{t["rr_simulator"]}</p>', unsafe_allow_html=True)
        st.markdown('<div class="risk-input-card" style="padding:10px;">', unsafe_allow_html=True)
        rr_ratios = {"1:2": 2.0, "1:3": 3.0, "1:4": 4.0, "2:3": 1.5, "2:4": 2.0}
        selected_rr = st.selectbox("rr", list(rr_ratios.keys()), key="rr_radio", label_visibility="collapsed")
        st.markdown(f'<p style="font-family:Share Tech Mono;font-size:18px;color:#00d4ff;text-align:center;margin:0;">{selected_rr}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<p class="section-title" style="margin-top:0;font-size:10px;">WINS / LOSSES</p>', unsafe_allow_html=True)
        st.markdown('<div class="risk-input-card" style="padding:6px;">', unsafe_allow_html=True)
        w1, w2 = st.columns(2)
        with w1:
            st.markdown('<p style="font-family:Orbitron;font-size:6px;color:#00ff88;text-align:center;margin:0;">WINS</p>', unsafe_allow_html=True)
            wins = st.number_input("w", min_value=0, value=3, step=1, key="wins", label_visibility="collapsed")
        with w2:
            st.markdown('<p style="font-family:Orbitron;font-size:6px;color:#ff2a6d;text-align:center;margin:0;">LOSS</p>', unsafe_allow_html=True)
            losses = st.number_input("l", min_value=0, value=2, step=1, key="losses", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<p class="section-title" style="font-size:10px;">{t["daily_risk"]}</p>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns([1, 1, 2])
    with d1:
        st.markdown('<div class="risk-input-card" style="padding:8px;border-color:rgba(255,42,109,0.3);">', unsafe_allow_html=True)
        st.markdown('<p style="font-family:Orbitron;font-size:6px;color:#ff2a6d;text-align:center;margin:0 0 3px;">MAX LOSS %</p>', unsafe_allow_html=True)
        max_loss = st.number_input("ml", 1.0, 100.0, 5.0, 1.0, key="maxl", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    with d2:
        st.markdown('<div class="risk-input-card" style="padding:8px;border-color:rgba(0,255,136,0.3);">', unsafe_allow_html=True)
        st.markdown('<p style="font-family:Orbitron;font-size:6px;color:#00ff88;text-align:center;margin:0 0 3px;">MAX PROFIT %</p>', unsafe_allow_html=True)
        max_profit = st.number_input("mp", 1.0, 200.0, 10.0, 1.0, key="maxp", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    with d3:
        st.markdown('<div class="risk-simulate-btn" style="margin-top:12px;">', unsafe_allow_html=True)
        simulate_clicked = st.button(t['risk_simulate'], use_container_width=True, type="primary", key="risk_sim_btn")
        st.markdown('</div>', unsafe_allow_html=True)

    risk_pct = 1.0

    if simulate_clicked:
        ra = balance * (risk_pct / 100)
        rw = ra * rr_ratios[selected_rr]
        wn = (wins * rw) - (losses * ra)
        wr = (wn / balance) * 100 if balance > 0 else 0
        mr = wr * 4
        yr = wr * 52
        fbw = balance + wn
        fbm = balance + (wn * 4)
        fby = balance + (wn * 52)
        mla = balance * (max_loss / 100)
        mpa = balance * (max_profit / 100)

        st.markdown('<div class="risk-neon-divider"></div>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-family:Orbitron;font-size:12px;color:#00d4ff;text-align:center;letter-spacing:3px;margin:0 0 10px;">{t["projection_title"]}</p>', unsafe_allow_html=True)

        periods = [(t['risk_weekly'], wn, wr, fbw), (t['risk_monthly'], wn * 4, mr, fbm), (t['risk_yearly'], wn * 52, yr, fby)]
        cols = st.columns(3)
        for i, (pn, net, ret, fbal) in enumerate(periods):
            with cols[i]:
                nc = "#00ff88" if net >= 0 else "#ff2a6d"
                rc = "#00ff88" if ret >= 0 else "#ff2a6d"
                st.markdown(f"""
                <div class="risk-projection-card" style="padding:12px;">
                    <p style="font-family:Orbitron;font-size:9px;color:#00d4ff;text-align:center;letter-spacing:2px;margin:0 0 8px;">{pn}</p>
                    <p style="font-family:Share Tech Mono;font-size:11px;color:{nc};text-align:center;margin:2px 0;">{t['risk_net']}: {net:+,.2f}</p>
                    <p style="font-family:Share Tech Mono;font-size:11px;color:{rc};text-align:center;margin:2px 0;">{t['risk_return']}: {ret:+.1f}%</p>
                    <p style="font-family:Share Tech Mono;font-size:11px;color:#00d4ff;text-align:center;margin:2px 0;">{t['risk_balance']}: {fbal:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f'<p style="font-family:Orbitron;font-size:10px;color:#ff2a6d;text-align:center;letter-spacing:2px;margin:10px 0 5px;">{t["risk_params"]}</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:4px;margin:6px 0;">
            <div class="risk-matrix-item"><div class="risk-matrix-label">{t['risk_per_trade']}</div><div class="risk-matrix-value" style="color:#ff2a6d;font-size:11px;">{ra:,.2f}</div></div>
            <div class="risk-matrix-item"><div class="risk-matrix-label">{t['risk_reward_trade']}</div><div class="risk-matrix-value" style="color:#00ff88;font-size:11px;">{rw:,.2f}</div></div>
            <div class="risk-matrix-item"><div class="risk-matrix-label">{t['risk_max_loss']}</div><div class="risk-matrix-value" style="color:#ff2a6d;font-size:11px;">-{mla:,.2f}</div></div>
            <div class="risk-matrix-item"><div class="risk-matrix-label">{t['risk_max_profit']}</div><div class="risk-matrix-value" style="color:#00ff88;font-size:11px;">+{mpa:,.2f}</div></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f'<p style="font-family:Orbitron;font-size:10px;color:#00d4ff;text-align:center;letter-spacing:2px;margin:10px 0 5px;">{t["risk_summary"]}</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:4px;margin:6px 0;">
            <div class="risk-matrix-item"><div class="risk-matrix-label">{t['risk_initial']}</div><div class="risk-matrix-value" style="font-size:11px;">{balance:,.2f}</div></div>
            <div class="risk-matrix-item"><div class="risk-matrix-label">{t['risk_after']} 1W</div><div class="risk-matrix-value" style="font-size:11px;color:{'#00ff88' if fbw>=balance else '#ff2a6d'};">{fbw:,.2f}</div></div>
            <div class="risk-matrix-item"><div class="risk-matrix-label">{t['risk_after']} 1M</div><div class="risk-matrix-value" style="font-size:11px;color:{'#00ff88' if fbm>=balance else '#ff2a6d'};">{fbm:,.2f}</div></div>
            <div class="risk-matrix-item"><div class="risk-matrix-label">{t['risk_after']} 1Y</div><div class="risk-matrix-value" style="font-size:11px;color:{'#00ff88' if fby>=balance else '#ff2a6d'};">{fby:,.2f}</div></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# 8. BROKER
# ==============================================================================
elif st.session_state.menu_selection == "Broker":
    fbs_logo = st.secrets.get("FBS_LOGO_URL", "")
    headway_logo = st.secrets.get("HEADWAY_LOGO_URL", "")

    st.markdown(f"""
    <div class="glass-card" style="text-align:center;">
        <h2 style="font-family:Orbitron;color:#00d4ff;letter-spacing:3px;">{t.get('broker_title','PARTNER BROKER')}</h2>
        <p style="font-family:Share Tech Mono;color:#557799;">{t.get('broker_subtitle','Pilih Broker Resmi untuk Trading Anda')}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background:rgba(0,15,30,0.8);border:1px solid rgba(0,212,255,0.3);border-radius:6px;padding:20px;text-align:center;min-height:500px;">
            {"<img src='"+fbs_logo+"' style='max-width:180px;margin-bottom:15px;filter:drop-shadow(0 0 10px rgba(0,212,255,0.5));'>" if fbs_logo else ""}
            <h3 style="font-family:Orbitron;color:#ffffff;letter-spacing:2px;">FBS</h3>
            <p style="font-family:Share Tech Mono;color:#00d4ff;margin:0;">Global Broker · Regulasi Ketat</p>
            <hr style="border-color:rgba(0,212,255,0.2);margin:15px 0;">
            <div style="text-align:left;color:#8899bb;font-size:12px;">
                <p><b style="color:#00ff88;">◈ Tidak ada akun Cent</b></p>
                <p><b style="color:#00ff88;">◈ Minimal Deposit: $1</b></p>
                <p><b style="color:#00ff88;">◈ Penarikan Minimum: $1</b></p>
                <p><b style="color:#00ff88;">◈ Spread Rendah</b></p>
                <p><b style="color:#00ff88;">◈ Leverage hingga 1:3000</b></p>
                <p><b style="color:#00ff88;">◈ Platform: MT4, MT5, Aplikasi Mobile</b></p>
                <p><b style="color:#00ff88;">◈ Bonus Deposit & Program Loyalitas</b></p>
            </div>
            <a href="https://fbs.partners?ibl=967003&ibp=34030661" target="_blank" style="text-decoration:none;">
                <div style="background:linear-gradient(160deg,#001a33,#002850);border:1px solid #00d4ff;border-radius:4px;padding:12px 20px;margin-top:15px;display:inline-block;">
                    <span style="font-family:Orbitron;color:#00d4ff;letter-spacing:2px;">DAFTAR SEKARANG</span>
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background:rgba(0,15,30,0.8);border:1px solid rgba(0,212,255,0.3);border-radius:6px;padding:20px;text-align:center;min-height:500px;">
            {"<img src='"+headway_logo+"' style='max-width:180px;margin-bottom:15px;filter:drop-shadow(0 0 10px rgba(0,212,255,0.5));'>" if headway_logo else ""}
            <h3 style="font-family:Orbitron;color:#ffffff;letter-spacing:2px;">HEADWAY</h3>
            <p style="font-family:Share Tech Mono;color:#00d4ff;margin:0;">Ecosystem Broker Modern</p>
            <hr style="border-color:rgba(0,212,255,0.2);margin:15px 0;">
            <div style="text-align:left;color:#8899bb;font-size:12px;">
                <p><b style="color:#00ff88;">◈ Memiliki Akun Cent</b></p>
                <p><b style="color:#00ff88;">◈ Minimal Deposit: $1 (Cent $1)</b></p>
                <p><b style="color:#00ff88;">◈ Penarikan Minimum: $1</b></p>
                <p><b style="color:#00ff88;">◈ Copy Trading & Social Trading</b></p>
                <p><b style="color:#00ff88;">◈ Leverage Fleksibel hingga 1:1000</b></p>
                <p><b style="color:#00ff88;">◈ Platform: MT4, MT5, WebTrader</b></p>
                <p><b style="color:#00ff88;">◈ Bonus Tanpa Deposit</b></p>
            </div>
            <a href="https://headway.partners/user/signup?hwp=520e6c" target="_blank" style="text-decoration:none;">
                <div style="background:linear-gradient(160deg,#001a33,#002850);border:1px solid #00d4ff;border-radius:4px;padding:12px 20px;margin-top:15px;display:inline-block;">
                    <span style="font-family:Orbitron;color:#00d4ff;letter-spacing:2px;">DAFTAR SEKARANG</span>
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-top:20px;color:#556680;font-size:10px;font-family:Share Tech Mono;">
        Broker di atas adalah partner resmi. AeroVulpis tidak bertanggung jawab atas aktivitas trading Anda.
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 9. ECONOMIC RADAR
# ==============================================================================
elif st.session_state.menu_selection == "Economic Radar":
    st.markdown(f"""
    <div style="text-align:center;padding:12px;margin-bottom:8px;background:rgba(0,20,40,0.5);border:1px solid rgba(0,212,255,0.15);border-radius:4px;">
        <p class="cyber-glow-text" style="font-size:13px;margin:0;letter-spacing:3px;">PETA EKONOMI & INDIKATOR MAKRO</p>
        <p style="font-family:Share Tech Mono;font-size:9px;color:#557799;margin:4px 0 0;">Pemetaan data sekilas secara global.</p>
    </div>
    """, unsafe_allow_html=True)

    map_image_url = st.secrets.get("MAP_IMAGE_URL")
    if map_image_url:
        st.markdown("""
        <div style="margin:15px 0;">
            <p style="font-family:'Orbitron'; font-size:14px; color:#00d4ff; letter-spacing:2px; margin-bottom:8px;">▸ PETA EKONOMI DUNIA</p>
            <p style="font-family:'Share Tech Mono'; font-size:10px; color:#557799; margin-bottom:12px;">Gambaran visual produk domestik bruto (GDP) tiap negara.</p>
        </div>
        """, unsafe_allow_html=True)
        st.image(map_image_url, use_container_width=True, caption="Sumber: World Bank / TradingView")
    else:
        st.warning("⚠️ URL gambar peta ekonomi belum dikonfigurasi. Tambahkan MAP_IMAGE_URL di Secrets.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin:15px 0 10px 0;">
        <p style="font-family:'Orbitron'; font-size:14px; color:#00ff88; letter-spacing:2px;">▸ INDIKATOR MAKRO & INDUSTRI</p>
        <p style="font-family:'Share Tech Mono'; font-size:10px; color:#557799;">Pilih negara untuk melihat data ekonomi utamanya (PDB, Pengangguran, Utang, Suku Bunga, Inflasi).</p>
    </div>
    """, unsafe_allow_html=True)
    
    country_options = [
        "Indonesia", "United States", "China", "Japan", "Germany", "India", "United Kingdom",
        "France", "Brazil", "Russia", "Australia", "Singapore", "Malaysia", "Thailand", "Vietnam", "Philippines"
    ]
    selected_country = st.selectbox("Pilih Negara", country_options, index=0)
    
    macro_data = get_macro_data(selected_country)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; padding:12px 6px;">
            <p style="font-family:Orbitron; font-size:10px; color:#00d4ff;">GDP (PDB)</p>
            <p style="font-family:Share Tech Mono; font-size:18px; font-weight:700; color:#00ff88;">{macro_data.get('GDP', 'Tidak tersedia')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; padding:12px 6px;">
            <p style="font-family:Orbitron; font-size:10px; color:#00d4ff;">PENGANGGURAN</p>
            <p style="font-family:Share Tech Mono; font-size:18px; font-weight:700; color:#00ff88;">{macro_data.get('Unemployment Rate', 'Tidak tersedia')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; padding:12px 6px;">
            <p style="font-family:Orbitron; font-size:10px; color:#00d4ff;">UTANG PEMERINTAH</p>
            <p style="font-family:Share Tech Mono; font-size:18px; font-weight:700; color:#00ff88;">{macro_data.get('Gov. Debt to GDP', 'Tidak tersedia')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; padding:12px 6px;">
            <p style="font-family:Orbitron; font-size:10px; color:#00d4ff;">SUKU BUNGA</p>
            <p style="font-family:Share Tech Mono; font-size:18px; font-weight:700; color:#00ff88;">{macro_data.get('Interest Rate', 'Tidak tersedia')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; padding:12px 6px;">
            <p style="font-family:Orbitron; font-size:10px; color:#00d4ff;">INFLASI</p>
            <p style="font-family:Share Tech Mono; font-size:18px; font-weight:700; color:#00ff88;">{macro_data.get('Inflation Rate', 'Tidak tersedia')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background:rgba(0,255,136,0.05); border-left:3px solid #00ff88; padding:12px; margin:15px 0; border-radius:4px;">
        <p style="font-family:'Share Tech Mono'; font-size:10px; color:#8899bb; margin:0;">
        ▸ <b>Penjelasan Indikator</b><br>
        • <b>GDP (PDB)</b>: Total nilai barang dan jasa yang dihasilkan suatu negara - mengukur ukuran ekonomi.<br>
        • <b>Tingkat Pengangguran</b>: Persentase angkatan kerja yang tidak bekerja - indikator kesehatan pasar tenaga kerja.<br>
        • <b>Utang Pemerintah terhadap PDB</b>: Rasio utang pemerintah terhadap PDB - mengukur keberlanjutan fiskal.<br>
        • <b>Suku Bunga</b>: Suku bunga acuan bank sentral - mempengaruhi biaya pinjaman dan nilai tukar.<br>
        • <b>Tingkat Inflasi</b>: Kenaikan harga barang dan jasa secara tahunan - menggerus daya beli.<br>
        <span style="color:#557799;">Sumber data: World Bank Open Data</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin:15px 0 10px 0;">
        <p style="font-family:'Orbitron'; font-size:14px; color:#00d4ff; letter-spacing:2px;">▸ KALENDER EKONOMI</p>
        <p style="font-family:'Share Tech Mono'; font-size:10px; color:#557799;">Jadwal rilis data ekonomi global dari TradingView.</p>
    </div>
    """, unsafe_allow_html=True)
    
    tv_calendar_html = """
    <div class="tradingview-widget-container" style="height:400px;">
        <div class="tradingview-widget-container__widget" style="height:400px;"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
        {
        "width": "100%",
        "height": "400",
        "language": "id"
        }
        </script>
    </div>
    """
    st.components.v1.html(tv_calendar_html, height=420)


# ==============================================================================
# 10. CHATBOT AI
# ==============================================================================
elif st.session_state.menu_selection == "Chatbot AI":
    st.markdown(f'<h2 style="font-family:Orbitron;font-size:20px;color:#00d4ff;letter-spacing:3px;">{t["chatbot_title"]}</h2>', unsafe_allow_html=True)
    st.caption(f"AEROVULPIS ENGINE | {tier_names.get(st.session_state.user_tier,'FREE')} | {st.session_state.daily_chatbot_count}/{user_limits['chatbot_per_day']}")

    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div style="display:flex; align-items:flex-start; justify-content:flex-end; margin-bottom:10px;">
                <div class="chat-bubble-user">{message["content"]}</div>
                <div class="chat-avatar-user">⬡</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display:flex; align-items:flex-start; margin-bottom:10px;">
                <div class="chat-avatar-robot">◈</div>
                <div class="chat-bubble-robot">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

    if prompt := st.chat_input("INPUT QUERY..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f"""
        <div style="display:flex; align-items:flex-start; justify-content:flex-end; margin-bottom:10px;">
            <div class="chat-bubble-user">{prompt}</div>
            <div class="chat-avatar-user">⬡</div>
        </div>
        """, unsafe_allow_html=True)
        with st.chat_message("assistant"):
            m_data = get_market_data(ticker_input)
            context_str = f"INSTR: {ticker_display} | PRICE: {format_price_display(m_data['price'], asset_name) if m_data else 'N/A'}"
            if st.session_state.get("active_alerts"):
                context_str += f" | ALERTS: {len(st.session_state.active_alerts)}"
            response = get_groq_response(prompt, context_str)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


# ==============================================================================
# 11. TINGKATKAN LEVEL
# ==============================================================================
elif st.session_state.menu_selection == "Tingkatkan Level":
    if "show_payment_modal" not in st.session_state:
        st.session_state.show_payment_modal = False
    if "selected_package" not in st.session_state:
        st.session_state.selected_package = None
    if "selected_price" not in st.session_state:
        st.session_state.selected_price = ""
    if "selected_duration" not in st.session_state:
        st.session_state.selected_duration = ""

    has_used_trial = False
    if st.session_state.user_id:
        try:
            supabase_admin = get_supabase_admin()
            trial_ever = supabase_admin.table("activation_keys").select("id").eq("used_by", st.session_state.user_id).eq("tier", "trial").execute()
            if trial_ever.data:
                has_used_trial = True
        except:
            pass

    yp_stok = 0
    try:
        supabase_admin = get_supabase_admin()
        yp_check = supabase_admin.table("activation_keys").select("id", count="exact").eq("tier", "yearly_promo").eq("is_used", False).execute()
        yp_stok = yp_check.count if yp_check.count else 0
    except:
        pass

    if st.session_state.show_payment_modal:
        user_id = st.session_state.get('user_id','GUEST')
        user_name = st.session_state.get('user_name','USER')
        pkg_name = st.session_state.selected_package
        pkg_price = st.session_state.selected_price
        qr_image_url = st.secrets.get("QRIS_IMAGE_URL","")
        qr_img_html = f'<img src="{qr_image_url}" style="width:200px; border-radius:10px;">' if qr_image_url else '<p>QR Code belum dikonfigurasi</p>'
        telegram_text = f"Halo Admin, saya ingin membeli paket:\n\n· Paket: {pkg_name}\n· Harga: {pkg_price}\n· ID User: {user_id}\n· Nama: {user_name}\n\nMohon diproses. Berikut bukti pembayaran (lampirkan gambar)."
        st.markdown(
'''<div style="background: linear-gradient(160deg, rgba(0,15,38,0.98), rgba(0,5,18,0.99)); border: 2px solid #00d4ff; border-radius: 10px; padding: 20px; max-width: 400px; margin: 0 auto; text-align: center; box-shadow: 0 0 50px rgba(0,212,255,0.15);">
<p style="font-family:'Orbitron'; font-size:18px; color:#00d4ff; letter-spacing:3px;">PAYMENT GATEWAY</p>
<p style="font-family:'Share Tech Mono'; font-size:10px; color:#557799; margin-bottom:15px;">Secure QRIS Transaction · Encrypted<br><span style="color:#ffcc00;">Admin Aktif 12.00 – 23.00 WIB</span></p>
''' + f'''
<div style="background:#fff; padding:10px; border-radius:8px; display:inline-block; margin-bottom:15px;">{qr_img_html}</div>
<div style="text-align:left; font-size:12px; color:#e0e6f0; margin-bottom:15px; border-top:1px solid rgba(0,212,255,0.2); padding-top:15px;">
<p><b>Paket:</b> <span style="color:#00ff88;">{pkg_name}</span></p>
<p><b>Harga:</b> <span style="color:#00ff88;">{pkg_price}</span></p>
<p><b>Status:</b> <span style="color:#ffcc00;">AWAITING PAYMENT</span></p>
</div>
<p style="font-size:12px; color:#8899bb; text-align:left;"><b>FORMAT PESAN TELEGRAM:</b></p>
</div>''', unsafe_allow_html=True)
        st.code(telegram_text, language="text")
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("BAYAR VIA TELEGRAM", "https://t.me/WartaPrime", type="primary", use_container_width=True)
        with col2:
            if st.button("BATAL & KEMBALI", use_container_width=True):
                st.session_state.show_payment_modal = False
                st.rerun()
    else:
        st.markdown("""
        <div class="upgrade-container">
            <h2 class="upgrade-title">UPGRADE ACCESS</h2>
            <p class="upgrade-subtitle">Select Your Plan · Unlock Full Potential · Professional Trading Terminal</p>
        """, unsafe_allow_html=True)

        packages = []
        if not has_used_trial:
            packages.append({
                "name":"TRIAL","duration":"1 DAY","price_usd":0.06,"price_idr":990,
                "price_label":"$0.06","strikethrough":"$0.12",
                "discount_badge":"Diskon 50% · Pengguna Baru",
                "features":["Full Access 24 Jam","8 AI Deep Analysis/hari","1 AI Sentinel Pro/hari","20 Chatbot/hari","2 Smart Alert/hari"],
                "featured":False,"id":"trial"
            })
        packages.append({
            "name":"WEEKLY","duration":"7 DAYS","price_usd":0.42,"price_idr":6990,
            "price_label":"$0.42","strikethrough":"$0.55",
            "discount_badge":"Hemat 24%",
            "features":["Full Access 7 Hari","15 AI Deep Analysis/hari","2 AI Sentinel Pro/hari","40 Chatbot/hari","8 Smart Alert/hari"],
            "featured":False,"id":"weekly"
        })
        packages.append({
            "name":"MONTHLY","duration":"30 DAYS","price_usd":1.65,"price_idr":27999,
            "price_label":"$1.65","strikethrough":"$2.24",
            "discount_badge":"Hemat 26% · Rp933/hari",
            "features":["Full Access 30 Hari","30 AI Deep Analysis/hari","4 AI Sentinel Pro/hari","60 Chatbot/hari","10 Smart Alert/hari"],
            "featured":True,"id":"monthly"
        })
        packages.append({
            "name":"6 MONTHS","duration":"180 DAYS","price_usd":5.65,"price_idr":96000,
            "price_label":"$5.65","strikethrough":"$6.88",
            "discount_badge":"Hemat 18% · $0.94/bulan",
            "features":["Full Access 180 Hari","60 AI Deep Analysis/hari","8 AI Sentinel Pro/hari","200 Chatbot/hari","13 Smart Alert/hari"],
            "featured":False,"id":"six_months"
        })
        packages.append({
            "name":"YEARLY","duration":"365 DAYS","price_usd":8.06,"price_idr":137000,
            "price_label":"$8.06","strikethrough":"$8.82",
            "discount_badge":"Hemat 9% · $0.02/hari",
            "features":["Full Access 365 Hari","80 AI Deep Analysis/hari","28 AI Sentinel Pro/hari","300 Chatbot/hari","20 Smart Alert/hari"],
            "featured":True,"id":"yearly"
        })
        if yp_stok > 0:
            packages.append({
                "name":"YEARLY PROMO","duration":"365 DAYS","price_usd":5.12,"price_idr":87000,
                "price_label":"$5.12","strikethrough":"$8.82",
                "discount_badge":f"Hemat 42% · $0.01/hari · ⚡ {yp_stok} slot tersisa!",
                "features":["Full Access 365 Hari","80 AI Deep Analysis/hari","28 AI Sentinel Pro/hari","300 Chatbot/hari","20 Smart Alert/hari"],
                "featured":True,"id":"yearly_promo_pkg"
            })

        cards_html = '<div class="pricing-grid">'
        for pkg in packages:
            featured_class = "featured" if pkg["featured"] else ""
            badge_html = pkg.get("discount_badge") and f'<div class="pricing-badge">{pkg["discount_badge"]}</div>' or ""
            strikethrough_html = pkg.get("strikethrough") and f'<p style="text-decoration:line-through;color:#557799;font-size:11px;margin:0 0 6px;">{pkg["strikethrough"]}</p>' or ""
            features_html = "".join([f"<li>{f}</li>" for f in pkg["features"]])
            price_html = f'<p class="pricing-price">${pkg["price_usd"]:,.2f}</p><p style="font-size:10px;color:#557799;margin-top:-10px;margin-bottom:10px;">(Rp{pkg["price_idr"]:,})</p>'
            cards_html += f"""
<div class="pricing-card {featured_class}">
<p class="pricing-name">{pkg['name']}</p>
<p class="pricing-duration">{pkg['duration']}</p>
{strikethrough_html}
{price_html}
<ul class="pricing-features">{features_html}</ul>
{badge_html}
</div>"""
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        for pkg in packages:
            if st.button(f"SELECT {pkg['name']} PACKAGE", key=f"btn_{pkg['id']}", use_container_width=True):
                st.session_state.show_payment_modal = True
                st.session_state.selected_package = pkg['name']
                st.session_state.selected_price = f"${pkg['price_usd']:,.2f} (Rp{pkg['price_idr']:,})"
                st.session_state.selected_duration = pkg['duration']
                st.session_state.selected_tier_for_payment = pkg['id'] if pkg['id'] != 'yearly_promo_pkg' else 'yearly_promo'
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# 12. SETTINGS
# ==============================================================================
elif st.session_state.menu_selection == "Settings":
    st.markdown(f'<h2 style="font-family:Orbitron;font-size:20px;color:#00d4ff;letter-spacing:3px;">{t["settings_title"]}</h2>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    new_lang = st.selectbox(t['lang_select'], ["ID", "EN"], index=0 if st.session_state.lang == "ID" else 1)
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()
    if st.button(t['clear_cache'], use_container_width=True):
        st.cache_data.clear()
        st.session_state.cached_analysis = {}
        st.session_state.last_news_fetch = {}
        st.success("SYSTEM CACHE CLEARED")
        time.sleep(1)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# 13. HELP & SUPPORT
# ==============================================================================
elif st.session_state.menu_selection == "Help & Support":
    st.markdown(f'<h2 style="font-family:Orbitron;text-align:center;font-size:24px;color:#00d4ff;letter-spacing:4px;margin-bottom:24px;">{t["help_title"]}</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="help-center-container">
        <div style="background:rgba(0,212,255,0.04);border:1px solid rgba(0,212,255,0.2);border-radius:6px;padding:18px;text-align:center;">
            <p style="font-family:Orbitron;font-size:12px;color:#00d4ff;margin:0 0 8px;letter-spacing:2px;">BANTUAN & SUPPORT</p>
            <p style="font-family:Share Tech Mono;font-size:11px;color:#8899bb;margin:0 0 12px;">Kendala pembayaran atau lisensi</p>
            <a href="https://t.me/WartaPrime" target="_blank" style="text-decoration:none;">
                <div style="background:linear-gradient(160deg,#001a33,#002850);border:1px solid rgba(0,212,255,0.35);border-radius:3px;padding:10px 16px;display:inline-block;"><span style="font-family:Orbitron;font-size:11px;color:#00d4ff;letter-spacing:2px;">@WartaPrime</span></div>
            </a>
        </div>
        <div style="background:rgba(0,255,136,0.03);border:1px solid rgba(0,255,136,0.15);border-radius:6px;padding:18px;text-align:center;">
            <p style="font-family:Orbitron;font-size:12px;color:#00ff88;margin:0 0 8px;letter-spacing:2px;">KOMUNITAS RESMI</p>
            <p style="font-family:Share Tech Mono;font-size:11px;color:#8899bb;margin:0 0 12px;">Diskusi, sinyal, dan update</p>
            <a href="https://t.me/+BARDIaUrXydkZDVl" target="_blank" style="text-decoration:none;">
                <div style="background:linear-gradient(160deg,#001a33,#002850);border:1px solid rgba(0,255,136,0.3);border-radius:3px;padding:10px 16px;display:inline-block;"><span style="font-family:Orbitron;font-size:11px;color:#00ff88;letter-spacing:2px;">AeroVulpis Group</span></div>
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("SENTINEL PRO INTELLIGENCE", expanded=True):
        st.markdown("""
        **Sentinel Pro** adalah dashboard analisis profesional yang didukung oleh sistem kecerdasan buatan AeroVulpis.
        **Kemampuan Utama:**
        - Grafik real-time dengan berbagai pilihan jangka waktu.
        - Laporan analisis mendalam mencakup level Support/Resistance, wawasan fundamental, serta skenario bullish dan bearish.
        - Analisis struktur pasar untuk penentuan waktu entry dan exit yang presisi.
        **Sumber Data:** Data harga diperoleh dari penyedia data independen untuk akurasi tinggi pada berbagai instrumen.
        **Cara Penggunaan:** Pilih instrumen dan jangka waktu dari sidebar, buka halaman Sentinel, lalu klik "INITIATE DEEP ANALYSIS PRO".
        """)

    with st.expander("LIVE DASHBOARD"):
        st.markdown("""
        **Live Dashboard** menyediakan pemantauan pasar real-time.
        **Fitur:**
        - Harga live dengan format desimal yang sesuai (4 desimal untuk Forex, 2 desimal untuk lainnya).
        - Cyber Gauge yang menunjukkan kekuatan teknikal (diperbarui dengan desain profesional).
        - Grafik harga interaktif dengan indikator moving average.
        - Analisis cepat dalam satu klik.
        **Catatan:** Harga yang ditampilkan mungkin memiliki selisih kecil dengan platform trading akibat perbedaan sumber data dan spread broker.
        """)

    with st.expander("SIGNAL ANALYSIS"):
        st.markdown("""
        **Signal Analysis Matrix** menampilkan 20 indikator teknikal dalam format grid.
        **Kategori Indikator:**
        - **Trend:** SMA 50, SMA 200, EMA 9/21, Ichimoku, Parabolic SAR
        - **Momentum:** RSI, MACD, Stochastic, CCI, Williams %R, MFI, ROC, TRIX, Awesome Oscillator
        - **Volatilitas:** ATR, Bollinger Bands
        - **Volume:** Volume SMA, Base Line
        **Warna Sinyal:** Hijau = Bullish | Merah = Bearish | Kuning = Netral
        """)

    with st.expander("MARKET SESSIONS & BERITA"):
        st.markdown("""
        **Monitor Sesi Pasar Global:**
        - Tracking real-time sesi Asia (Tokyo), Eropa (London), dan Amerika (New York)
        - Progress bar menunjukkan persentase sesi berjalan
        - Deteksi Golden Hour (tumpang tindih London-New York)
        **Agregator Berita:**
        - Berita dari berbagai jaringan finansial global.
        - Filter kategori: General, Stock, Geopolitics, Gold & Silver, Forex, Ekonomi Indonesia, Saham Indonesia, Crypto
        - Tautan langsung ke sumber berita.
        """)

    with st.expander("SMART ALERT CENTER"):
        st.markdown("""
        **Sistem Pemantauan Harga Otomatis** dengan notifikasi Telegram.
        **Cara Setup:**
        1. Pilih instrumen dari dropdown.
        2. Tentukan harga target.
        3. Masukkan Chat ID Telegram (dapatkan dari @userinfobot).
        4. Pilih kondisi: Bullish (harga naik) atau Bearish (harga turun).
        5. Aktifkan sensor untuk pemantauan 24/7.
        """)

    with st.expander("CHATBOT AI"):
        st.markdown("""
        **Asisten Cerdas** yang memahami konteks instrumen yang dipilih dan harga live.
        **Kemampuan:**
        - Analisis teknikal dan interpretasi indikator.
        - Rekomendasi level Entry, Stop Loss, dan Take Profit.
        - Diskusi strategi trading.
        """)

    with st.expander("ECONOMIC RADAR"):
        st.markdown("""
        **Pemindai Ekonomi Global** memantau peristiwa ekonomi berdampak tinggi.
        **Fitur:**
        - Peta ekonomi dunia (gambar statis dari Supabase Storage).
        - Indikator makroekonomi utama (GDP, pengangguran, utang pemerintah, suku bunga, inflasi) dengan filter negara.
        - Kalender ekonomi real-time dari TradingView.
        """)

    with st.expander("RISK MANAGEMENT"):
        st.markdown("""
        **Sistem Manajemen Risiko** untuk menghitung eksposur dan proyeksi:
        1. **Aturan Trading** - Tentukan stop loss dan parameter entry.
        2. **Ukuran Posisi** - Hitung ukuran posisi optimal.
        3. **Skor Keyakinan** - Penilaian kondisi teknikal.
        4. **Strategi Risiko** - Batas kerugian harian dan target profit.
        """)

    with st.expander("TINGKATKAN LEVEL"):
        st.markdown("""
        **Upgrade Akses Anda:**
        - Pilih paket yang sesuai dengan kebutuhan trading Anda.
        - Pembayaran mudah via Telegram, cukup kirim pesan format yang disediakan.
        - Aktivasi instan setelah verifikasi pembayaran.
        **Paket Tersedia:**
        - **TRIAL** (1 Hari): Rp990 (untuk pengguna baru, hanya sekali)
        - **WEEKLY** (7 Hari): Rp6.990
        - **MONTHLY** (30 Hari): Rp27.999
        - **6 MONTHS** (180 Hari): Rp96.000
        - **YEARLY** (365 Hari): Rp137.000
        - **YEARLY PROMO** (365 Hari): Rp87.000 (terbatas)
        """)

    with st.expander("AKTIVASI LISENSI & LIMIT"):
        st.markdown("""
        **Sistem Manajemen Lisensi**
        **Cara Masuk:** Masukkan email dan password di sidebar.
        **Aktivasi Lisensi:**
        1. Setelah masuk, klik "ACTIVATE LICENSE KEY".
        2. Masukkan kunci lisensi yang valid.
        3. Klik "VALIDATE & ACTIVATE".
        **Batas Harian per Level (Deep Analysis / Sentinel / Chatbot):**
        - **GRATIS:** 1 / 0 / 5
        - **TRIAL:** 8 / 1 / 20
        - **MINGGUAN:** 15 / 2 / 40
        - **BULANAN:** 30 / 4 / 60
        - **6 BULAN:** 60 / 8 / 200
        - **TAHUNAN/PROMO:** 80 / 28 / 300
        """)

    st.markdown("""
    <div style="margin-top:30px; padding:15px; background:rgba(0,212,255,0.03); border-left:3px solid #00d4ff;">
        <p style="font-family:'Share Tech Mono'; font-size:12px; color:#8899bb;">
            ⚡ <strong>Catatan Tampilan:</strong> Jika Anda melihat garis-garis putih tipis di sekitar halaman, itu hanyalah efek visual dari tema neon dan bukan merupakan masalah teknis. 
            Desain ini sengaja dibuat untuk memberikan kesan futuristik.
        </p>
        <p style="font-family:'Orbitron'; font-size:12px; color:#00ff88; margin-top:10px;">
            🚀 <strong>Dukung Pengembangan Terminal:</strong> Tingkatkan level Anda di menu <strong>"Tingkatkan Level"</strong> untuk membuka fitur premium, 
            membantu pengembangan sistem agar lebih profesional, real-time, dan berkelanjutan. Setiap upgrade Anda berkontribusi pada peningkatan kualitas platform.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.info("Gunakan halaman Settings untuk mengganti bahasa atau membersihkan cache.")


# ==============================================================================
# 14. OUR JOURNEY (MENU BARU)
# ==============================================================================
elif st.session_state.menu_selection == "Our Journey":
    st.markdown("""
    <div style="text-align:center; padding:20px;">
        <h2 style="font-family:'Orbitron'; color:#00d4ff; letter-spacing:4px;">OUR JOURNEY</h2>
        <div style="margin:30px auto; max-width:800px;">
    """, unsafe_allow_html=True)
    dh_logo_url = st.secrets.get("DH_IMAGE_URL", "")
    if dh_logo_url:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:24px;">
            <img src="{dh_logo_url}" style="width:100px; filter:drop-shadow(0 0 12px #00d4ff);">
        </div>
        """, unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(0,212,255,0.03); border:1px solid rgba(0,212,255,0.2); border-radius:8px; padding:28px; text-align:left;">
        <p style="font-family:'Share Tech Mono'; font-size:14px; color:#dce4f0; line-height:1.8;">
        Sebuah inovasi besar tidak lahir dalam semalam. AeroVulpis saat ini masih terus berbenah dan membutuhkan dukungan penuh dari komunitas trader domestik demi mencapai performa terbaiknya. 
        Melalui kemitraan strategis dengan DynamiHatch, kami ingin berjalan beriringan dengan Anda. 
        Mari bersama-sama memberikan dukungan, memperbaiki kekurangan yang ada, dan berkembang bersama DynamiHatch dan AeroVulpis untuk menciptakan standar trading yang lebih sehat di Indonesia.
        </p>
        <p style="font-family:'Share Tech Mono'; font-size:12px; color:#8899bb; margin-top:20px; text-align:right;">
        — Tim AeroVulpis & DynamiHatch
        </p>
    </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center;padding:25px;opacity:0.55;">
    <p style="font-family:Share Tech Mono;font-size:14px;color:#556680;margin:0;letter-spacing:2px;">
        "DISCIPLINE IS THE KEY | EMOTION IS THE ENEMY | TRUST THE SYSTEM"
    </p>
    <p style="font-family:Orbitron;font-size:11px;color:#00ff88;margin:8px 0;letter-spacing:3px;">
        FAHMI — AEROVULPIS ARCHITECT
    </p>
    <p style="font-family:Share Tech Mono;font-size:8px;color:#334455;letter-spacing:2px;margin-top:6px;">
        DYNAMIHATCH IDENTITY | V4.0 ULTIMATE
    </p>
</div>
""", unsafe_allow_html=True)

# ========== PART 2 END ==========
