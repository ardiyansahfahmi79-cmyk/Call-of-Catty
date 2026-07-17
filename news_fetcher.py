import requests
from config import QUERY_KATEGORI, BATAS_BERITA_PER_KATEGORI
from utils import normalisasi_artikel, hapus_duplikat, cocok_keyword

def ambil_marketaux(api_key, query="", limit=50):
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
    data = r.json().get("data", [])
    return [normalisasi_artikel(x) for x in data]

def beri_kategori_otomatis(artikel):
    t = f"{artikel['judul']} {artikel['deskripsi']}".lower()

    kategori = set()

    if cocok_keyword(t, QUERY_KATEGORI["economy_us"]):
        kategori.add("economy_us")
    if cocok_keyword(t, QUERY_KATEGORI["fed"]):
        kategori.add("fed")
    if cocok_keyword(t, QUERY_KATEGORI["stock"]):
        kategori.add("stock")
    if cocok_keyword(t, QUERY_KATEGORI["crypto"]):
        kategori.add("crypto")
    if cocok_keyword(t, QUERY_KATEGORI["geopolitics"]):
        kategori.add("geopolitics")
    if cocok_keyword(t, QUERY_KATEGORI["forex"]):
        kategori.add("forex")
    if cocok_keyword(t, QUERY_KATEGORI["indonesia"]):
        kategori.add("indonesia")

    if not kategori:
        kategori.add("stock")

    return list(kategori)

def ambil_semua_kategori(marketaux_key):
    hasil = {k: [] for k in QUERY_KATEGORI.keys() if k != "all"}

    for kategori, daftar_keyword in QUERY_KATEGORI.items():
        if kategori == "all":
            continue

        query = " OR ".join(daftar_keyword[:4]) if daftar_keyword else ""
        data = ambil_marketaux(marketaux_key, query=query, limit=50)
        data = hapus_duplikat(data)

        # filter tambahan dan batasi 5 per kategori
        filtered = []
        for item in data:
            gabungan = f"{item['judul']} {item['deskripsi']}"
            if cocok_keyword(gabungan, daftar_keyword):
                filtered.append(item)

        hasil[kategori] = filtered[:BATAS_BERITA_PER_KATEGORI]

    return hasil

def ambil_berita_kategori(kategori, marketaux_key):
    daftar_keyword = QUERY_KATEGORI.get(kategori, [])
    query = " OR ".join(daftar_keyword[:4]) if daftar_keyword else ""

    data = ambil_marketaux(marketaux_key, query=query, limit=50)
    data = hapus_duplikat(data)

    filtered = []
    for item in data:
        gabungan = f"{item['judul']} {item['deskripsi']}"
        if cocok_keyword(gabungan, daftar_keyword):
            filtered.append(item)

    return filtered[:BATAS_BERITA_PER_KATEGORI]