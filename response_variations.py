"""Variasi copy Aero AI yang stabil, ringkas, dan tidak mengubah fakta pasar.

Filosofi berkas ini: variasi hanya mengubah cara Aero AI mengantar informasi.
Harga, indikator, agenda, waktu, status sumber, dan formula level selalu tetap
dibentuk oleh modul data/analisis yang telah ada.
"""

from __future__ import annotations

from hashlib import sha256


# Sepuluh pembuka dan lima penegas membentuk 50 variasi berbeda untuk setiap
# keluarga respons. Selector memakai hash stabil; tidak ada random state yang
# dapat membuat jawaban berubah ketika Streamlit melakukan rerun.
_LEADS: tuple[str, ...] = (
    "Ringkasnya,",
    "Fokus pembacaan:",
    "Sebagai titik awal,",
    "Untuk menjawab pertanyaan ini,",
    "Pada snapshot yang tersedia,",
    "Hal utama yang perlu diperhatikan:",
    "Pembacaan saat ini:",
    "Untuk menjaga analisis tetap terarah,",
    "Dengan batas data yang berlaku,",
    "Berikut konteks yang paling relevan:",
)

_ENDINGS: tuple[str, ...] = (
    "Bagian berikut mempertahankan pemisahan antara fakta, kondisi, dan batas data.",
    "Kesimpulan tetap bersyarat pada konfirmasi data berikutnya.",
    "Angka yang tidak tersedia tidak akan diisi dengan perkiraan.",
    "Risiko dan keterbatasan sumber tetap perlu dibaca sebelum menilai skenario.",
    "Pembacaan ini disusun untuk riset dan edukasi, bukan keputusan finansial personal.",
)


_FAMILY_FOCUS: dict[str, str] = {
    "analysis_overview": "ringkasan ini menempatkan kondisi market yang terlihat saat ini sebagai dasar pembacaan",
    "analysis_trend": "arah tren dibaca dari hubungan harga, rata-rata bergerak, dan kekuatan pergerakan yang tersedia",
    "analysis_signals": "label indikator diperlakukan sebagai pembacaan kondisi, bukan instruksi untuk masuk pasar",
    "analysis_risk": "rentang volatilitas dan batas risiko didahulukan sebelum kesimpulan arah",
    "analysis_levels": "area harga dibaca sebagai zona observasi yang perlu dikonfirmasi, bukan harga eksekusi",
    "analysis_levels_entry": "Entry, invalidasi, dan target dijelaskan sebagai skenario bersyarat berbasis data saat ini",
    "analysis_fundamental": "fakta fundamental dipisahkan dari kondisi harga agar frekuensi datanya tidak tercampur",
    "analysis_comparison": "perbandingan menekankan arah relatif dan basis data yang setara, bukan perbandingan nominal semata",
    "analysis_agenda": "status agenda dipisahkan dari reaksi harga agar satu rilis tidak dianggap sebagai kepastian arah",
    "analysis_xau_spot": "harga spot XAUUSD dipisahkan dari basis candle indikator dan hanya diselaraskan secara bersyarat",
    "agenda_direct": "ringkasan agenda menjelaskan status rilis dari data publik yang benar-benar tersedia",
    "agenda_clarification": "fokus negara atau sisi ekonomi perlu diperjelas sebelum kalender ditafsirkan",
    "unknown_unsupported": "kode yang belum didukung tidak akan dipetakan secara spekulatif ke instrumen lain",
    "unknown_greeting": "Aero AI dibatasi untuk pemindaian market, agenda ekonomi, indikator, dan konteks risiko",
    "unknown_identity": "identitas Aero AI dijelaskan secara singkat sebelum kembali ke fokus riset market",
    "unknown_ambiguous": "singkatan yang ambigu perlu diperjelas agar data instrumen tidak tertukar",
    "unknown_levels_missing": "instrumen dan timeframe diperlukan sebelum area risiko dapat dihitung secara bertanggung jawab",
    "unknown_off_topic": "pesan perlu dikaitkan dengan instrumen, timeframe, atau agenda market yang didukung",
    "instrument_confirmation": "instrumen sudah terbaca dan menunggu fokus analisis yang lebih spesifik",
    "multi_instrument_clarification": "fokus analisis perlu dibatasi agar tidak ada instrumen yang diabaikan",
    "source_unavailable": "sumber publik belum cukup untuk membentuk analisis sehingga sistem tidak membuat data pengganti",
    "spot_fallback": "harga spot tersedia, tetapi indikator ditahan sampai candle teknikal yang memadai tersedia",
}


def _build_variants(focus: str) -> tuple[str, ...]:
    """Bentuk tepat 50 copy berbeda dengan struktur yang tetap profesional."""
    return tuple(f"{lead} {focus}. {ending}" for lead in _LEADS for ending in _ENDINGS)


RESPONSE_VARIANTS: dict[str, tuple[str, ...]] = {
    family: _build_variants(focus) for family, focus in _FAMILY_FOCUS.items()
}


def response_variant_count(family: str) -> int:
    """Kembalikan jumlah variasi terdaftar untuk satu keluarga respons."""
    return len(RESPONSE_VARIANTS[family])


def response_variant_at(family: str, index: int) -> str:
    """Ambil variasi berdasarkan indeks untuk pengujian dan audit deterministik."""
    variants = RESPONSE_VARIANTS[family]
    return variants[index % len(variants)]


def select_response_variant(family: str, context_key: str) -> str:
    """Pilih copy stabil berdasarkan konteks, tanpa menyentuh fakta pada respons."""
    variants = RESPONSE_VARIANTS[family]
    digest = sha256(f"{family}|{context_key.casefold().strip()}".encode("utf-8")).digest()
    index = int.from_bytes(digest[:8], byteorder="big") % len(variants)
    return variants[index]


def analysis_response_family(intent: str, has_xau_spot: bool = False) -> str:
    """Petakan intent analisis ke keluarga copy yang sesuai."""
    if has_xau_spot:
        return "analysis_xau_spot"
    return {
        "overview": "analysis_overview",
        "trend": "analysis_trend",
        "signals": "analysis_signals",
        "risk": "analysis_risk",
        "levels": "analysis_levels",
        "levels_entry": "analysis_levels_entry",
        "fundamental": "analysis_fundamental",
        "comparison": "analysis_comparison",
        "economic_agenda": "analysis_agenda",
    }.get(intent, "analysis_overview")
