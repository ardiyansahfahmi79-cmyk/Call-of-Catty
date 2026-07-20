import requests
from config import QUERY_KATEGORI, BATAS_BERITA_PER_KATEGORI
from utils import normalisasi_artikel, hapus_duplikat, cocok_keyword

MAPPING_LABEL = {
    "stock":      "SAHAM",
    "crypto":     "ASET DIGITAL",
    "geopolitics":"GEOPOLITIK",
    "forex":      "VALUTA ASING",
    "indonesia":  "INDONESIA",
    "economy_us": "EKONOMI AS",
    "fed":        "FEDERAL RESERVE",
}

# ─────────────────────────────────────────────
# MARKETAUX
# ─────────────────────────────────────────────
def ambil_marketaux(api_key: str, query: str = "", limit: int = 50) -> list:
    if not api_key:
        return []
    try:
        url = "https://api.marketaux.com/v1/news/all"
        params = {
            "api_token": api_key,
            "language": "en",
            "limit": limit,
            "sort": "published_desc",
            "group_similar": "true",
        }
        if query:
            params["search"] = query
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        return [normalisasi_artikel(x) for x in r.json().get("data", [])]
    except Exception:
        return []

# ─────────────────────────────────────────────
# NEWSAPI.ORG
# ─────────────────────────────────────────────
def ambil_newsapi(api_key: str, query: str = "", limit: int = 20) -> list:
    """
    NewsAPI.org — free tier: 100 req/hari, delay 24 jam, hanya localhost di free.
    Gunakan hanya jika kamu punya key berbayar atau testing lokal.
    Endpoint: https://newsapi.org/v2/everything
    """
    if not api_key:
        return []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "apiKey": api_key,
            "q": query or "finance market economy",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": min(limit, 100),
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        articles = r.json().get("articles", [])
        hasil = []
        for x in articles:
            hasil.append({
                "judul":       x.get("title", ""),
                "deskripsi":   x.get("description", "") or x.get("content", ""),
                "url":         x.get("url", ""),
                "sumber":      x.get("source", {}).get("name", "NewsAPI"),
                "waktu_terbit":x.get("publishedAt", ""),
                "raw":         x,
            })
        return hasil
    except Exception:
        return []

# ─────────────────────────────────────────────
# FMP — Financial Modeling Prep
# ─────────────────────────────────────────────
def ambil_fmp(api_key: str, limit: int = 20) -> list:
    """
    FMP free tier: 250 req/hari, berita pasar & press release.
    Endpoint: https://financialmodelingprep.com/api/v3/stock_news
    """
    if not api_key:
        return []
    try:
        url = "https://financialmodelingprep.com/api/v3/stock_news"
        params = {
            "apikey": api_key,
            "limit": min(limit, 50),
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list):
            return []
        hasil = []
        for x in data:
            hasil.append({
                "judul":       x.get("title", ""),
                "deskripsi":   x.get("text", ""),
                "url":         x.get("url", ""),
                "sumber":      x.get("site", "FMP"),
                "waktu_terbit":x.get("publishedDate", ""),
                "raw":         x,
            })
        return hasil
    except Exception:
        return []

# ─────────────────────────────────────────────
# KATEGORISASI
# ─────────────────────────────────────────────
def tentukan_kategori_teks(artikel: dict) -> list:
    t = f"{artikel.get('judul','')} {artikel.get('deskripsi','')}"
    kategori = set()
    for k, keywords in QUERY_KATEGORI.items():
        if k == "all":
            continue
        if cocok_keyword(t, keywords):
            kategori.add(k)
    return list(kategori) if kategori else ["stock"]

def beri_kategori_label(artikel: dict, kategori_key: str) -> dict:
    item = dict(artikel)
    item["kategori_key"]   = kategori_key
    item["kategori_label"] = MAPPING_LABEL.get(kategori_key, kategori_key.upper())
    return item

# ─────────────────────────────────────────────
# FUNGSI UTAMA — MULTI-SOURCE
# ─────────────────────────────────────────────
def ambil_semua_kategori(
    marketaux_key: str,
    newsapi_key: str = "",
    fmp_key: str = "",
    tanggal_target=None,
) -> dict:
    hasil = {k: [] for k in QUERY_KATEGORI if k != "all"}

    # Kumpulkan dari semua sumber
    master = []

    if marketaux_key:
        master += ambil_marketaux(
            marketaux_key,
            query=" OR ".join(["stocks", "bitcoin", "CPI", "Federal Reserve", "IHSG", "tariff", "USD"]),
            limit=100,
        )

    if newsapi_key:
        master += ambil_newsapi(
            newsapi_key,
            query="stocks OR bitcoin OR inflation OR Federal Reserve OR forex OR economy",
            limit=30,
        )

    if fmp_key:
        master += ambil_fmp(fmp_key, limit=30)

    master = hapus_duplikat(master)

    for item in master:
        for k in tentukan_kategori_teks(item):
            if len(hasil.get(k, [])) < BATAS_BERITA_PER_KATEGORI:
                if k not in hasil:
                    hasil[k] = []
                hasil[k].append(beri_kategori_label(item, k))

    return hasil


def ambil_berita_kategori(
    kategori: str,
    marketaux_key: str,
    newsapi_key: str = "",
    fmp_key: str = "",
    tanggal_target=None,
) -> list:
    daftar_keyword = QUERY_KATEGORI.get(kategori, [])
    query = " OR ".join(daftar_keyword[:5]) if daftar_keyword else "finance"

    master = []

    if marketaux_key:
        master += ambil_marketaux(marketaux_key, query=query, limit=50)

    if newsapi_key:
        master += ambil_newsapi(newsapi_key, query=query, limit=20)

    if fmp_key and kategori in ("stock", "economy_us", "fed"):
        master += ambil_fmp(fmp_key, limit=20)

    master = hapus_duplikat(master)

    filtered = [
        beri_kategori_label(item, kategori)
        for item in master
        if cocok_keyword(f"{item.get('judul','')} {item.get('deskripsi','')}", daftar_keyword)
    ]

    return filtered[:BATAS_BERITA_PER_KATEGORI]