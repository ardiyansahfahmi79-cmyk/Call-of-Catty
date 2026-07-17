from datetime import datetime

def teks_aman(value, default=""):
    return value if value is not None else default

def parse_waktu(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None

def tanggal_hari_ini(value):
    dt = parse_waktu(value)
    if not dt:
        return None
    return dt.date().isoformat()

def hapus_duplikat(items):
    seen = set()
    hasil = []
    for item in items:
        key = item.get("url") or item.get("judul")
        if key in seen:
            continue
        seen.add(key)
        hasil.append(item)
    return hasil

def normalisasi_artikel(item):
    return {
        "judul": teks_aman(item.get("title")),
        "deskripsi": teks_aman(item.get("description") or item.get("snippet")),
        "url": teks_aman(item.get("url")),
        "sumber": teks_aman(item.get("source") or item.get("source_name")),
        "waktu_terbit": teks_aman(item.get("published_at") or item.get("publishedAt")),
        "raw": item,
    }

def cocok_keyword(teks, daftar_keyword):
    t = (teks or "").lower()
    return any(k.lower() in t for k in daftar_keyword)