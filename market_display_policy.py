"""Kebijakan presentasi untuk elemen visual Aero AI.

Grafik bersifat opt-in: analisis teks, level, dan struktur harga tidak perlu
memuat chart kecuali pengguna secara eksplisit meminta grafik atau perbandingan
harga. Kebijakan ini tidak mengubah data maupun perhitungan pasar.
"""

from __future__ import annotations

import re


def chart_requested(question: str) -> bool:
    """Tentukan apakah pengguna benar-benar meminta chart statis.

    Perbandingan umum tetap dijawab sebagai teks. Hanya perbandingan yang secara
    eksplisit menyebut harga yang diperlakukan sebagai permintaan visual.
    """
    text = question.casefold()
    explicit_chart = re.search(r"\b(?:grafik|chart|candlestick|line\s*chart|plot|grafikkan|tampilkan\s+harga)\b", text)
    price_comparison = re.search(r"\b(?:bandingkan|compare|perbandingan)\b.*\b(?:harga|price)\b", text)
    return bool(explicit_chart or price_comparison)
