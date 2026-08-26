"""Fungsi murni untuk pilihan dan perhitungan konverter kurs lokal."""

from __future__ import annotations

from typing import Mapping


BLOCKED_CURRENCY_CODES = frozenset({"ILS"})

# Kurasi sengaja dibatasi: 30 Asia, 20 Eropa, 15 Afrika, 20 Amerika, dan 5 Oseania.
# Setiap kode hanya muncul jika juga tersedia di respons kurs publik.
CURRENCY_FLAGS = {
    # Asia
    "AED": "🇦🇪", "BHD": "🇧🇭", "BND": "🇧🇳", "CNY": "🇨🇳", "HKD": "🇭🇰",
    "IDR": "🇮🇩", "INR": "🇮🇳", "IQD": "🇮🇶", "JPY": "🇯🇵", "KRW": "🇰🇷",
    "KWD": "🇰🇼", "KZT": "🇰🇿", "MYR": "🇲🇾", "OMR": "🇴🇲", "PHP": "🇵🇭",
    "PKR": "🇵🇰", "QAR": "🇶🇦", "SAR": "🇸🇦", "SGD": "🇸🇬", "THB": "🇹🇭",
    "TWD": "🇹🇼", "VND": "🇻🇳", "BDT": "🇧🇩", "NPR": "🇳🇵", "LKR": "🇱🇰",
    "KHR": "🇰🇭", "LAK": "🇱🇦", "MNT": "🇲🇳", "UZS": "🇺🇿", "GEL": "🇬🇪",
    # Eropa
    "ALL": "🇦🇱", "BGN": "🇧🇬", "BAM": "🇧🇦", "CHF": "🇨🇭", "CZK": "🇨🇿",
    "DKK": "🇩🇰", "EUR": "🇪🇺", "GBP": "🇬🇧", "HUF": "🇭🇺", "ISK": "🇮🇸",
    "MDL": "🇲🇩", "NOK": "🇳🇴", "PLN": "🇵🇱", "RON": "🇷🇴", "RSD": "🇷🇸",
    "RUB": "🇷🇺", "SEK": "🇸🇪", "TRY": "🇹🇷", "UAH": "🇺🇦", "MKD": "🇲🇰",
    # Afrika
    "AOA": "🇦🇴", "BWP": "🇧🇼", "DZD": "🇩🇿", "EGP": "🇪🇬", "ETB": "🇪🇹",
    "GHS": "🇬🇭", "KES": "🇰🇪", "MAD": "🇲🇦", "MUR": "🇲🇺", "NGN": "🇳🇬",
    "TND": "🇹🇳", "UGX": "🇺🇬", "ZAR": "🇿🇦", "ZMW": "🇿🇲", "XOF": "🇸🇳",
    # Amerika
    "ARS": "🇦🇷", "BBD": "🇧🇧", "BOB": "🇧🇴", "BRL": "🇧🇷", "CAD": "🇨🇦",
    "CLP": "🇨🇱", "COP": "🇨🇴", "CRC": "🇨🇷", "DOP": "🇩🇴", "GTQ": "🇬🇹",
    "GYD": "🇬🇾", "JMD": "🇯🇲", "MXN": "🇲🇽", "PAB": "🇵🇦", "PEN": "🇵🇪",
    "PYG": "🇵🇾", "TTD": "🇹🇹", "USD": "🇺🇸", "UYU": "🇺🇾", "XCD": "🇦🇬",
    # Oseania
    "AUD": "🇦🇺", "NZD": "🇳🇿", "FJD": "🇫🇯", "PGK": "🇵🇬", "SBD": "🇸🇧",
}

PREFERRED_CURRENCY_CODES = tuple(CURRENCY_FLAGS)


def available_currency_codes(rates: Mapping[str, float]) -> list[str]:
    """Mengembalikan maksimal 90 kode kurasi yang tersedia pada sumber publik."""
    return [
        code
        for code in PREFERRED_CURRENCY_CODES
        if code not in BLOCKED_CURRENCY_CODES
        and isinstance(rates.get(code), (float, int))
        and float(rates[code]) > 0
    ]


def currency_label(code: str) -> str:
    """Membuat pilihan sangat ringkas agar mudah dipindai pada ponsel."""
    return f"{CURRENCY_FLAGS.get(code, '🏳️')} {code}"


def currency_pair_label(from_code: str, to_code: str) -> str:
    """Menampilkan pasangan pilihan seperti format konverter mata uang umum."""
    return f"{currency_label(from_code)} → {currency_label(to_code)}"


def convert_from_usd_reference(
    amount: float,
    from_code: str,
    to_code: str,
    usd_rates: Mapping[str, float],
) -> float:
    """Mengonversi antar-kode menggunakan kurs referensi dengan basis USD."""
    if amount < 0:
        raise ValueError("Jumlah tidak boleh negatif")
    if from_code in BLOCKED_CURRENCY_CODES or to_code in BLOCKED_CURRENCY_CODES:
        raise ValueError("Mata uang tidak tersedia")
    from_rate = 1.0 if from_code == "USD" else float(usd_rates[from_code])
    to_rate = 1.0 if to_code == "USD" else float(usd_rates[to_code])
    if from_rate <= 0 or to_rate <= 0:
        raise ValueError("Kurs harus lebih besar dari nol")
    return amount / from_rate * to_rate
