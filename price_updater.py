#!/usr/bin/env python3
# price_updater.py - AEROVULPIS V4.0
# Background job untuk memperbarui harga semua instrumen dari Twelve Data ke Supabase.
# Jalankan setiap 5 menit via cron atau GitHub Actions.

import os
import sys
import requests
from datetime import datetime
import pytz
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# KONFIGURASI
# ============================================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
TWELVE_DATA_API_KEY = os.getenv("TWELVEDATA_KEY")

# Daftar instrumen (twelve_symbol → db_name)
INSTRUMENTS = [
    {"twelve_symbol": "XAU/USD", "db_name": "GOLD (XAUUSD)"},
    {"twelve_symbol": "XAG/USD", "db_name": "SILVER (XAGUSD)"},
    {"twelve_symbol": "BTC/USD", "db_name": "BITCOIN"},
    {"twelve_symbol": "ETH/USD", "db_name": "ETHEREUM"},
    {"twelve_symbol": "SOL/USD", "db_name": "SOLANA"},
    {"twelve_symbol": "XRP/USD", "db_name": "XRP"},
    {"twelve_symbol": "BNB/USD", "db_name": "BNB"},
    {"twelve_symbol": "EUR/USD", "db_name": "EUR/USD"},
    {"twelve_symbol": "GBP/USD", "db_name": "GBP/USD"},
    {"twelve_symbol": "USD/JPY", "db_name": "USD/JPY"},
    {"twelve_symbol": "AUD/USD", "db_name": "AUD/USD"},
    {"twelve_symbol": "USD/CHF", "db_name": "USD/CHF"},
    {"twelve_symbol": "WTI", "db_name": "CRUDE OIL (WTI)"},
    {"twelve_symbol": "US100", "db_name": "NASDAQ-100"},
    {"twelve_symbol": "SPX", "db_name": "S&P 500"},
    {"twelve_symbol": "DJI", "db_name": "DOW JONES"},
    {"twelve_symbol": "DAX", "db_name": "DAX 40"},
    {"twelve_symbol": "JKSE", "db_name": "IHSG"},
    {"twelve_symbol": "NVDA", "db_name": "NVIDIA"},
    {"twelve_symbol": "AAPL", "db_name": "APPLE"},
    {"twelve_symbol": "TSLA", "db_name": "TESLA"},
    {"twelve_symbol": "MSFT", "db_name": "MICROSOFT"},
    {"twelve_symbol": "AMZN", "db_name": "AMAZON"},
    {"twelve_symbol": "BBRI.JK", "db_name": "BBRI"},
    {"twelve_symbol": "BBCA.JK", "db_name": "BBCA"},
    {"twelve_symbol": "TLKM.JK", "db_name": "TLKM"},
    {"twelve_symbol": "ASII.JK", "db_name": "ASII"},
    {"twelve_symbol": "BMRI.JK", "db_name": "BMRI"},
    {"twelve_symbol": "PA", "db_name": "PALLADIUM"},
    {"twelve_symbol": "PL", "db_name": "PLATINUM"},
    {"twelve_symbol": "NG", "db_name": "NATURAL GAS"},
    {"twelve_symbol": "HG", "db_name": "COPPER"},
]

# ============================================================
# FUNGSI
# ============================================================
def get_supabase_admin() -> Client:
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise Exception("Supabase credentials missing")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def fetch_all_prices():
    """Mengambil harga dalam batch (maksimal 8 simbol per request)"""
    symbols = [inst["twelve_symbol"] for inst in INSTRUMENTS]
    all_prices = {}
    chunk_size = 8  # Batasan free tier Twelve Data

    for i in range(0, len(symbols), chunk_size):
        chunk = symbols[i:i+chunk_size]
        symbols_str = ",".join(chunk)
        url = f"https://api.twelvedata.com/price?symbol={symbols_str}&apikey={TWELVE_DATA_API_KEY}"
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                all_prices.update(data)
            else:
                print(f"[ERROR] Chunk {chunk} failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"[ERROR] Chunk {chunk} exception: {e}")
    
    return all_prices if all_prices else None

def update_database(prices_dict):
    supabase = get_supabase_admin()
    now_iso = datetime.now(pytz.UTC).isoformat()
    updated = 0
    failed = []

    for inst in INSTRUMENTS:
        sym = inst["twelve_symbol"]
        db_name = inst["db_name"]
        price_info = prices_dict.get(sym)
        if not price_info or not isinstance(price_info, dict):
            failed.append(sym)
            continue
        price_str = price_info.get("price")
        if price_str is None:
            failed.append(sym)
            continue
        try:
            price = float(price_str)
        except (ValueError, TypeError):
            failed.append(sym)
            continue

        data = {
            "instrument": db_name,
            "price": price,
            "updated_at": now_iso
        }
        try:
            supabase.table("market_prices").upsert(data, on_conflict="instrument").execute()
            updated += 1
        except Exception as e:
            print(f"[ERROR] Update {db_name}: {e}")
            failed.append(sym)

    return updated, failed

def main():
    if not TWELVE_DATA_API_KEY:
        print("[ERROR] TWELVEDATA_KEY missing")
        sys.exit(1)
    
    print(f"[INFO] Update started at {datetime.now(pytz.timezone('Asia/Jakarta')).isoformat()}")
    prices = fetch_all_prices()
    if not prices:
        print("[ERROR] No prices retrieved")
        sys.exit(1)
    
    updated, failed = update_database(prices)
    print(f"[INFO] Updated: {updated} instruments, Failed: {len(failed)}")
    if failed:
        print(f"[WARN] Failed symbols: {failed}")

if __name__ == "__main__":
    main()