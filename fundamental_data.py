"""Adapter fundamental publik tanpa API key untuk Aero AI.

Setiap nilai membawa metadata sumber dan waktu observasi agar narasi tidak
menyajikan angka tanpa jejak. Adapter dirancang gagal secara aman: kegagalan
satu sumber tidak boleh menghentikan analisis teknikal utama.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
import time
from typing import Any

import requests

from market_data import Instrument


REQUEST_TIMEOUT = 8
_CACHE: dict[str, tuple[float, list["FundamentalSnapshot"]]] = {}


@dataclass(frozen=True)
class FundamentalSnapshot:
    category: str
    instrument_code: str
    title: str
    value: str
    unit: str
    observed_at: datetime
    released_at: datetime | None
    fetched_at: datetime
    source_name: str
    source_url: str
    freshness: str
    warning: str = ""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_datetime(value: str | None) -> datetime:
    if not value:
        return _utc_now()
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        try:
            return datetime(int(value), 1, 1, tzinfo=timezone.utc)
        except (TypeError, ValueError):
            return _utc_now()


def _get_json(url: str, params: dict[str, Any] | None = None) -> Any:
    response = requests.get(
        url,
        params=params,
        timeout=REQUEST_TIMEOUT,
        headers={"Accept": "application/json", "User-Agent": "AeroAI-Research/1.0"},
    )
    response.raise_for_status()
    return response.json()


def _get_text(url: str) -> str:
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
        headers={"Accept": "text/csv", "Accept-Encoding": "identity", "User-Agent": "AeroAI-Research/1.0"},
    )
    response.raise_for_status()
    return response.text


def _cached(key: str, ttl_seconds: int, loader) -> list[FundamentalSnapshot]:
    now = time.monotonic()
    cached = _CACHE.get(key)
    if cached and now - cached[0] < ttl_seconds:
        return cached[1]
    try:
        result = loader()
    except (requests.RequestException, ValueError, TypeError, KeyError):
        return cached[1] if cached else []
    _CACHE[key] = (now, result)
    return result


def _latest_us_unemployment(instrument_code: str) -> list[FundamentalSnapshot]:
    def load() -> list[FundamentalSnapshot]:
        source_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/LNS14000000?latest=true"
        payload = _get_json(source_url)
        point = payload["Results"]["series"][0]["data"][0]
        observed = _to_datetime(f"{point['year']}-{point['period'][1:]}-01")
        return [FundamentalSnapshot(
            category="Makro AS",
            instrument_code=instrument_code,
            title="Tingkat pengangguran AS",
            value=str(point["value"]),
            unit="%",
            observed_at=observed,
            released_at=None,
            fetched_at=_utc_now(),
            source_name="U.S. Bureau of Labor Statistics",
            source_url=source_url,
            freshness="Seri bulanan; bukan data intraday.",
            warning="Gunakan sebagai konteks makro USD, bukan penyebab tunggal pergerakan harga.",
        )]
    return _cached("bls_unemployment", 6 * 60 * 60, load)


def _latest_us_cpi(instrument_code: str) -> list[FundamentalSnapshot]:
    def load() -> list[FundamentalSnapshot]:
        source_url = "https://api.worldbank.org/v2/country/USA/indicator/FP.CPI.TOTL.ZG?format=json&per_page=8"
        payload = _get_json(source_url)
        rows = payload[1]
        point = next(row for row in rows if row.get("value") is not None)
        return [FundamentalSnapshot(
            category="Makro AS",
            instrument_code=instrument_code,
            title="Inflasi konsumen AS",
            value=f"{float(point['value']):.1f}",
            unit="% tahunan",
            observed_at=_to_datetime(point.get("date")),
            released_at=None,
            fetched_at=_utc_now(),
            source_name="World Bank Indicators",
            source_url=source_url,
            freshness="Seri tahunan; konteks struktural, bukan pembaruan market harian.",
            warning="Gunakan bersama data rilis yang lebih baru bila diperlukan.",
        )]
    return _cached("worldbank_us_cpi", 24 * 60 * 60, load)


def _latest_fred_macro(instrument_code: str) -> list[FundamentalSnapshot]:
    """Ambil seri harian publik FRED untuk konteks lintas aset, bukan prediksi market."""
    definitions = (
        ("DGS2", "Imbal hasil US Treasury 2Y", "%", "Board of Governors of the Federal Reserve System (US) via FRED"),
        ("DGS10", "Imbal hasil US Treasury 10Y", "%", "Board of Governors of the Federal Reserve System (US) via FRED"),
        ("VIXCLS", "VIX / volatilitas implisit ekuitas AS", "indeks", "Chicago Board Options Exchange via FRED"),
    )

    def load() -> list[FundamentalSnapshot]:
        snapshots: list[FundamentalSnapshot] = []
        fetched_at = _utc_now()
        for series_id, title, unit, source_name in definitions:
            csv_url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
            rows = list(csv.DictReader(StringIO(_get_text(csv_url))))
            point = next((row for row in reversed(rows) if row.get(series_id) not in (None, "", ".")), None)
            if not point:
                continue
            observed_at = datetime.strptime(point["observation_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            snapshots.append(FundamentalSnapshot(
                category="Kondisi pasar AS",
                instrument_code=instrument_code,
                title=title,
                value=point[series_id],
                unit=unit,
                observed_at=observed_at,
                released_at=None,
                fetched_at=fetched_at,
                source_name=source_name,
                source_url=f"https://fred.stlouisfed.org/series/{series_id}",
                freshness="Seri harian publik; bukan harga intraday atau sinyal arah harga.",
                warning="Gunakan hanya sebagai konteks kondisi pasar lintas aset, bukan dasar tunggal keputusan transaksi.",
            ))
        return snapshots

    return _cached("fred_market_context", 15 * 60, load)


def _crypto_structure(instrument_code: str) -> list[FundamentalSnapshot]:
    coin_ids = {"BTCUSD": "bitcoin", "ETHUSD": "ethereum", "SOLUSD": "solana"}
    coin_id = coin_ids.get(instrument_code)
    if not coin_id:
        return []

    def load() -> list[FundamentalSnapshot]:
        source_url = "https://api.coingecko.com/api/v3/simple/price"
        payload = _get_json(source_url, {
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_market_cap": "true",
            "include_24hr_change": "true",
        })
        point = payload[coin_id]
        now = _utc_now()
        market_cap = float(point["usd_market_cap"])
        daily_change = float(point["usd_24h_change"])
        return [
            FundamentalSnapshot(
                category="Struktur pasar kripto",
                instrument_code=instrument_code,
                title="Kapitalisasi pasar",
                value=f"US${market_cap:,.0f}",
                unit="USD",
                observed_at=now,
                released_at=None,
                fetched_at=now,
                source_name="CoinGecko Keyless API",
                source_url=source_url,
                freshness="Endpoint keyless dengan batas rate bersama; hanya untuk prototipe.",
            ),
            FundamentalSnapshot(
                category="Struktur pasar kripto",
                instrument_code=instrument_code,
                title="Perubahan pasar 24 jam",
                value=f"{daily_change:+.2f}",
                unit="%",
                observed_at=now,
                released_at=None,
                fetched_at=now,
                source_name="CoinGecko Keyless API",
                source_url=source_url,
                freshness="Endpoint keyless dengan batas rate bersama; bukan feed eksekusi.",
            ),
        ]
    return _cached(f"coingecko_{coin_id}", 90, load)


def fetch_fundamental_context(instrument: Instrument) -> list[FundamentalSnapshot]:
    """Ambil konteks fundamental yang relevan tanpa membuat angka pengganti."""
    snapshots: list[FundamentalSnapshot] = []
    snapshots.extend(_latest_fred_macro(instrument.code))
    snapshots.extend(_crypto_structure(instrument.code))
    # Makro USD relevan untuk FX, logam, energi, indeks, dan saham; kripto sudah memakai konteks pasar serta struktur asetnya.
    if instrument.code not in {"BTCUSD", "ETHUSD", "BNBUSD", "SOLUSD", "XRPUSD", "ADAUSD", "DOTUSD", "MATICUSD", "LINKUSD", "AVAXUSD"}:
        snapshots.extend(_latest_us_unemployment(instrument.code))
        snapshots.extend(_latest_us_cpi(instrument.code))
    return snapshots
