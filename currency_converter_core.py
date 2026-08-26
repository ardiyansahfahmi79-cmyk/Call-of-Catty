"""Fungsi murni untuk pilihan dan perhitungan konverter kurs lokal."""

from __future__ import annotations

from typing import Mapping


BLOCKED_CURRENCY_CODES = frozenset({"ILS"})

DISPLAY_NAMES = {
    "AED": "Dirham Uni Emirat Arab",
    "AUD": "Dolar Australia",
    "BND": "Dolar Brunei",
    "BRL": "Real Brasil",
    "CAD": "Dolar Kanada",
    "CHF": "Franc Swiss",
    "CNY": "Yuan Tiongkok",
    "DKK": "Krone Denmark",
    "EGP": "Pound Mesir",
    "EUR": "Euro",
    "GBP": "Pound Inggris",
    "HKD": "Dolar Hong Kong",
    "IDR": "Rupiah Indonesia",
    "INR": "Rupee India",
    "JPY": "Yen Jepang",
    "KRW": "Won Korea Selatan",
    "KWD": "Dinar Kuwait",
    "MAD": "Dirham Maroko",
    "MYR": "Ringgit Malaysia",
    "MXN": "Peso Meksiko",
    "NGN": "Naira Nigeria",
    "NOK": "Krone Norwegia",
    "NZD": "Dolar Selandia Baru",
    "PHP": "Peso Filipina",
    "PKR": "Rupee Pakistan",
    "QAR": "Riyal Qatar",
    "RUB": "Ruble Rusia",
    "SAR": "Riyal Arab Saudi",
    "SEK": "Krona Swedia",
    "SGD": "Dolar Singapura",
    "THB": "Baht Thailand",
    "TRY": "Lira Turki",
    "TWD": "Dolar Taiwan",
    "UAH": "Hryvnia Ukraina",
    "USD": "Dolar Amerika Serikat",
    "VND": "Dong Vietnam",
    "ZAR": "Rand Afrika Selatan",
}


def available_currency_codes(rates: Mapping[str, float]) -> list[str]:
    """Mengembalikan kode dengan nilai positif, terurut, dan tanpa kode terblokir."""
    return sorted(
        code
        for code, rate in rates.items()
        if code not in BLOCKED_CURRENCY_CODES and isinstance(rate, (float, int)) and rate > 0
    )


def currency_label(code: str) -> str:
    """Membuat label Indonesia ringkas; kode tetap jelas untuk pilihan yang kurang umum."""
    return f"{code} — {DISPLAY_NAMES.get(code, 'Mata uang internasional')}"


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
