from datetime import datetime, timezone

KATEGORI = {
    "all": "Semua",
    "stock": "Saham",
    "crypto": "Aset Digital",
    "geopolitics": "Geopolitik",
    "forex": "Valuta Asing",
    "indonesia": "Indonesia",
    "economy_us": "Ekonomi AS",
    "fed": "Federal Reserve",
}

QUERY_KATEGORI = {
    "stock": [
        "stocks", "equities", "earnings", "semiconductors", "big tech", "ai stocks"
    ],
    "crypto": [
        "bitcoin", "ethereum", "crypto", "ETF", "blockchain", "spot ETF"
    ],
    "geopolitics": [
        "war", "tariff", "sanctions", "geopolitics", "conflict", "trade war"
    ],
    "forex": [
        "USD", "EUR", "JPY", "currency", "forex", "dollar", "yen", "euro"
    ],
    "indonesia": [
        "Indonesia", "IHSG", "Bank Indonesia", "rupiah", "BPS", "emiten"
    ],
    "economy_us": [
        "CPI", "PPI", "NFP", "jobs report", "GDP", "inflation", "unemployment",
        "retail sales", "Treasury yield", "consumer confidence"
    ],
    "fed": [
        "Federal Reserve", "Powell", "FOMC", "rate cuts", "rates", "dot plot",
        "minutes", "hawkish", "dovish"
    ],
    "all": []
}

BATAS_BERITA_PER_KATEGORI = 5
MODEL_OPENROUTER = "nvidia/nemotron-3-super-120b-a12b:free"

PROMPT_SISTEM = """
Kamu adalah analis pasar profesional Aerovulpis.
Tugasmu:
1. Jelaskan inti berita secara ringkas.
2. Terangkan dampak ke pasar secara jelas.
3. Beri sentimen: bullish, bearish, atau netral.
4. Tulis dalam Bahasa Indonesia yang rapi dan mudah dipahami trader/investor.
5. Jangan menambah data yang tidak ada di input.
6. Jika berita bersifat makro AS, jelaskan pengaruhnya ke dolar, obligasi, emas, saham, dan crypto bila relevan.
"""

def hari_ini_utc():
    return datetime.now(timezone.utc).date()