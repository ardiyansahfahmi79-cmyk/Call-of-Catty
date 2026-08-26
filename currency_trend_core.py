"""Normalisasi data historis kurs untuk grafik tujuh hari."""

from __future__ import annotations

from math import ceil, log10
from typing import Mapping


CURRENCY_TREND_DAYS = 30


def parse_historical_rates(payload: Mapping[str, object], quote_code: str) -> list[dict[str, object]]:
    """Membaca respons Frankfurter v1 dan mengembalikan titik valid menurut tanggal."""
    rate_days = payload.get("rates")
    if not isinstance(rate_days, Mapping):
        return []

    points: list[dict[str, object]] = []
    for day, values in sorted(rate_days.items()):
        if not isinstance(day, str) or not isinstance(values, Mapping):
            continue
        raw_rate = values.get(quote_code)
        if not isinstance(raw_rate, (float, int)) or raw_rate <= 0:
            continue
        points.append({"Tanggal": day, "Kurs": float(raw_rate)})
    return points


def trend_change_percent(points: list[dict[str, object]]) -> float | None:
    """Menghitung perubahan dari titik pertama ke terakhir, bila data cukup."""
    if len(points) < 2:
        return None
    first = float(points[0]["Kurs"])
    last = float(points[-1]["Kurs"])
    if first <= 0:
        return None
    return ((last - first) / first) * 100


def format_axis_value(value: float, decimals: int | None = None) -> str:
    """Menampilkan angka sumbu dengan desimal eksplisit, bukan notasi mikro."""
    magnitude = abs(value)
    if decimals is None:
        decimals = 2 if magnitude >= 1 else 4 if magnitude >= 0.01 else 6 if magnitude >= 0.000001 else 8
    return f"{value:.{decimals}f}"


def trend_axis_ticks(points: list[dict[str, object]], tick_count: int = 4) -> tuple[list[float], list[str], list[float]]:
    """Menyusun rentang dan label sumbu yang memberi ruang napas pada data asli."""
    values = [float(point["Kurs"]) for point in points]
    if not values:
        return [], [], []
    lower_value = min(values)
    upper_value = max(values)
    spread = upper_value - lower_value
    padding = max(spread * 0.18, abs(upper_value) * 0.003, 1e-10)
    lower_bound = max(0.0, lower_value - padding)
    upper_bound = upper_value + padding
    if tick_count < 2 or upper_bound == lower_bound:
        ticks = [lower_value]
        decimals = None
    else:
        step = (upper_bound - lower_bound) / (tick_count - 1)
        ticks = [lower_bound + step * index for index in range(tick_count)]
        decimals = min(8, max(2, ceil(-log10(step)) + 1))
    return ticks, [format_axis_value(value, decimals) for value in ticks], [lower_bound, upper_bound]
