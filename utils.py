import re
import html as _html
from datetime import datetime

def teks_aman(value, default=""):
    return value if value is not None else default

def strip_html_utils(teks: str) -> str:
    """Bersihkan HTML tag dari teks API."""
    if not teks: return ""
    teks = _html.unescape(teks)
    teks = re.sub(r'<[^>]+>', ' ', teks)
    teks = re.sub(r'\s+', ' ', teks).strip()
    return teks

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
    """
    Normalisasi artikel dari API.
    Prioritaskan field terpanjang untuk deskripsi agar
    konten tidak terpotong.
    """
    judul = strip_html_utils(teks_aman(item.get("title")))

    # Ambil deskripsi dari field terpanjang yang tersedia
    candidates = [
        item.get("description",""),
        item.get("snippet",""),
        item.get("content",""),
        item.get("text",""),        # FMP
        item.get("body",""),
    ]
    deskripsi = ""
    for c in candidates:
        cleaned = strip_html_utils(teks_aman(c))
        if len(cleaned) > len(deskripsi):
            deskripsi = cleaned

    # Potong di 600 karakter agar tidak terlalu panjang tapi tetap informatif
    if len(deskripsi) > 600:
        deskripsi = deskripsi[:597] + "..."

    return {
        "judul":       judul,
        "deskripsi":   deskripsi,
        "url":         teks_aman(item.get("url")),
        "sumber":      teks_aman(item.get("source") or item.get("source_name") or item.get("site")),
        "waktu_terbit":teks_aman(item.get("published_at") or item.get("publishedAt") or item.get("publishedDate")),
        "raw":         item,
    }

def cocok_keyword(teks, daftar_keyword):
    t = (teks or "").lower()
    return any(k.lower() in t for k in daftar_keyword)