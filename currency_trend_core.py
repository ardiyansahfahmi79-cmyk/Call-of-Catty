"""Normalisasi data historis kurs untuk grafik tujuh hari."""

from __future__ import annotations

from typing import Mapping


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
