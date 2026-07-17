import requests
from config import QUERY_KATEGORI, BATAS_BERITA_PER_KATEGORI
from utils import normalisasi_artikel, hapus_duplikat, cocok_keyword, tanggal_hari_ini

MAPPING_LABEL = {
    "stock": "SAHAM",
    "crypto": "ASET DIGITAL",
    "geopolitics": "GEOPOLITIK",
    "forex": "VALUTA ASING",
    "indonesia": "INDONESIA",
    "economy_us": "EKONOMI AS",
    "fed": "FEDERAL RESERVE",
}

def ambil_marketaux(api_key, query="", limit=100):
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

def tentukan_kategori_teks(artikel):
    t = f"{artikel['judul']} {artikel['deskripsi']}"
    kategori = set()
    for kategori_key, daftar_keyword in QUERY_KATEGORI.items():
        if kategori_key == "all":
            continue
        if cocok_keyword(t, daftar_keyword):
            kategori.add(kategori_key)
    if not kategori:
        kategori.add("stock")
    return list(kategori)

def beri_kategori_label(artikel, kategori_key):
    item = dict(artikel)
    item["kategori_key"] = kategori_key
    item["kategori_label"] = MAPPING_LABEL.get(kategori_key, kategori_key.upper())
    return item

def ambil_semua_kategori(marketaux_key, tanggal_target=None):
    hasil = {k: [] for k in QUERY_KATEGORI.keys() if k != "all"}
    master = ambil_marketaux(
        marketaux_key,
        query=" OR ".join(["stocks", "bitcoin", "CPI", "Federal Reserve", "IHSG", "tariff", "USD"]),
        limit=100
    )
    master = hapus_duplikat(master)

    for item in master:
        if tanggal_target and tanggal_hari_ini(item.get("waktu_terbit")) != tanggal_target:
            continue

        kategori_list = tentukan_kategori_teks(item)
        for k in kategori_list:
            if len(hasil[k]) < BATAS_BERITA_PER_KATEGORI:
                hasil[k].append(beri_kategori_label(item, k))

    return hasil

def ambil_berita_kategori(kategori, marketaux_key, tanggal_target=None):
    daftar_keyword = QUERY_KATEGORI.get(kategori, [])
    query = " OR ".join(daftar_keyword[:5]) if daftar_keyword else ""

    data = ambil_marketaux(marketaux_key, query=query, limit=100)
    data = hapus_duplikat(data)

    filtered = []
    for item in data:
        if tanggal_target and tanggal_hari_ini(item.get("waktu_terbit")) != tanggal_target:
            continue

        gabungan = f"{item['judul']} {item['deskripsi']}"
        if cocok_keyword(gabungan, daftar_keyword):
            filtered.append(beri_kategori_label(item, kategori))

    return filtered[:BATAS_BERITA_PER_KATEGORI]