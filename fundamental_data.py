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
import re
import time
from typing import Any

import requests

from market_data import Instrument


REQUEST_TIMEOUT = 8
_CACHE: dict[str, tuple[float, list["FundamentalSnapshot"]]] = {}
NY_FED_SOFR_URL = "https://markets.newyorkfed.org/api/rates/secured/sofr/last/1.json"
NY_FED_EFFR_URL = "https://markets.newyorkfed.org/api/rates/unsecured/effr/last/1.json"
EIA_PETROLEUM_TABLE_URL = "https://ir.eia.gov/wpsr/table1.csv"
EIA_NATURAL_GAS_URL = "https://ir.eia.gov/ngs/wngsr.txt"
CFTC_DISAGGREGATED_URL = "https://www.cftc.gov/dea/newcot/f_disagg.txt"
CFTC_CONTRACTS = {
    "XAUUSD": "GOLD - COMMODITY EXCHANGE INC.",
    "XAGUSD": "SILVER - COMMODITY EXCHANGE INC.",
    "WTI": "WTI FINANCIAL CRUDE OIL - NEW YORK MERCANTILE EXCHANGE",
}


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


def _latest_new_york_fed_rates(instrument_code: str) -> list[FundamentalSnapshot]:
    """Ambil reference rates resmi AS untuk Macro Pulse tanpa membuat proyeksi kebijakan."""
    definitions = (
        ("SOFR", "SOFR / Secured Overnight Financing Rate", NY_FED_SOFR_URL, "Kondisi pendanaan beragunan AS"),
        ("EFFR", "EFFR / Effective Federal Funds Rate", NY_FED_EFFR_URL, "Suku bunga efektif overnight AS"),
    )

    def load() -> list[FundamentalSnapshot]:
        snapshots: list[FundamentalSnapshot] = []
        fetched_at = _utc_now()
        for expected_type, title, source_url, category in definitions:
            payload = _get_json(source_url)
            point = next((row for row in payload.get("refRates", []) if str(row.get("type", "")).upper() == expected_type), None)
            if not point or point.get("percentRate") is None or not point.get("effectiveDate"):
                continue
            snapshots.append(FundamentalSnapshot(
                category="Macro Pulse AS",
                instrument_code=instrument_code,
                title=title,
                value=str(point["percentRate"]),
                unit="%",
                observed_at=_to_datetime(str(point["effectiveDate"])),
                released_at=None,
                fetched_at=fetched_at,
                source_name="Federal Reserve Bank of New York Markets API",
                source_url=source_url,
                freshness="Reference rate harian resmi; bukan proyeksi kebijakan berikutnya.",
                warning=category + ". Gunakan sebagai konteks, bukan sinyal arah harga tunggal.",
            ))
        return snapshots

    return _cached("new_york_fed_reference_rates", 15 * 60, load)


def _parse_us_short_date(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%m/%d/%y").replace(tzinfo=timezone.utc)


def _eia_petroleum_inventory(instrument_code: str) -> list[FundamentalSnapshot]:
    if instrument_code not in {"WTI", "BRENT", "XBRUSD"}:
        return []

    def load() -> list[FundamentalSnapshot]:
        rows = list(csv.DictReader(StringIO(_get_text(EIA_PETROLEUM_TABLE_URL))))
        if not rows or not rows[0]:
            return []
        fields = list(rows[0].keys())
        if len(fields) < 4:
            return []
        current_date = fields[1]
        commercial = next((row for row in rows if str(row.get(fields[0], "")).strip() == "Commercial (Excluding SPR)"), None)
        if not commercial or not commercial.get(current_date):
            return []
        weekly_change = str(commercial.get("Difference", "")).strip()
        warning = "Perubahan mingguan tidak tersedia dari tabel sumber." if not weekly_change else f"Perubahan mingguan sumber: {weekly_change} juta barel. Inventori mingguan bukan proyeksi harga minyak."
        return [FundamentalSnapshot(
            category="Inventori energi AS",
            instrument_code=instrument_code,
            title="Inventori minyak mentah komersial AS (ex-SPR)",
            value=str(commercial[current_date]).strip(),
            unit="juta barel",
            observed_at=_parse_us_short_date(current_date),
            released_at=None,
            fetched_at=_utc_now(),
            source_name="U.S. Energy Information Administration · WPSR Table 1",
            source_url=EIA_PETROLEUM_TABLE_URL,
            freshness="Laporan mingguan EIA; bukan data intraday.",
            warning=warning,
        )]

    return _cached("eia_petroleum_inventory", 60 * 60, load)


def _eia_natural_gas_storage(instrument_code: str) -> list[FundamentalSnapshot]:
    if instrument_code != "XNGUSD":
        return []

    def load() -> list[FundamentalSnapshot]:
        text = _get_text(EIA_NATURAL_GAS_URL)
        total_match = re.search(r"Total \((\d{2}/\d{2}/\d{2})\):\s*([\d,]+)\s*Bcf", text)
        change_match = re.search(r"Net change:\s*([+-]?[\d,]+)\s*Bcf", text)
        if not total_match:
            return []
        storage_date, total = total_match.groups()
        change = change_match.group(1) if change_match else "tidak tersedia"
        return [FundamentalSnapshot(
            category="Inventori energi AS",
            instrument_code=instrument_code,
            title="Gas kerja dalam penyimpanan Lower 48",
            value=total,
            unit="Bcf",
            observed_at=_parse_us_short_date(storage_date),
            released_at=None,
            fetched_at=_utc_now(),
            source_name="U.S. Energy Information Administration · WNGSR",
            source_url=EIA_NATURAL_GAS_URL,
            freshness="Laporan mingguan EIA; bukan data intraday.",
            warning=f"Perubahan mingguan sumber: {change} Bcf. Data storage bukan proyeksi harga gas.",
        )]

    return _cached("eia_natural_gas_storage", 60 * 60, load)


def _cftc_managed_money_positioning(instrument_code: str) -> list[FundamentalSnapshot]:
    """Ambil positioning mingguan CFTC untuk kontrak yang punya pemetaan eksplisit.

    Kolom 13 dan 14 file Disaggregated Futures-only adalah posisi long dan short
    Managed Money menurut susunan laporan CFTC. Nilai net dihitung dari dua angka
    sumber ini, lalu selalu diberi tanggal as-of agar tidak disalahartikan real-time.
    """
    contract_name = CFTC_CONTRACTS.get(instrument_code)
    if not contract_name:
        return []

    def load() -> list[FundamentalSnapshot]:
        rows = csv.reader(StringIO(_get_text(CFTC_DISAGGREGATED_URL)))
        row = next((item for item in rows if item and item[0].strip() == contract_name), None)
        if not row or len(row) <= 14:
            return []
        managed_money_long = int(row[13].strip())
        managed_money_short = int(row[14].strip())
        net_position = managed_money_long - managed_money_short
        observed_at = _to_datetime(row[2].strip())
        return [FundamentalSnapshot(
            category="Positioning futures mingguan",
            instrument_code=instrument_code,
            title="CFTC Managed Money net positioning",
            value=f"{net_position:+,}",
            unit="kontrak",
            observed_at=observed_at,
            released_at=None,
            fetched_at=_utc_now(),
            source_name="U.S. Commodity Futures Trading Commission · Disaggregated COT",
            source_url=CFTC_DISAGGREGATED_URL,
            freshness="Laporan mingguan CFTC; bukan positioning real-time dan dapat memiliki jeda publikasi.",
            warning=(
                f"Managed Money long: {managed_money_long:,}; short: {managed_money_short:,}. "
                "Net positioning bukan rekomendasi transaksi dan tidak menjelaskan semua pelaku pasar."
            ),
        )]

    return _cached(f"cftc_disaggregated_{instrument_code}", 6 * 60 * 60, load)


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
    snapshots.extend(_eia_petroleum_inventory(instrument.code))
    snapshots.extend(_eia_natural_gas_storage(instrument.code))
    snapshots.extend(_cftc_managed_money_positioning(instrument.code))
    snapshots.extend(_latest_fred_macro(instrument.code))
    snapshots.extend(_latest_new_york_fed_rates(instrument.code))
    snapshots.extend(_crypto_structure(instrument.code))
    # Makro USD relevan untuk FX, logam, energi, indeks, dan saham; kripto sudah memakai konteks pasar serta struktur asetnya.
    if instrument.code not in {"BTCUSD", "ETHUSD", "BNBUSD", "SOLUSD", "XRPUSD", "ADAUSD", "DOTUSD", "MATICUSD", "LINKUSD", "AVAXUSD"}:
        snapshots.extend(_latest_us_unemployment(instrument.code))
        snapshots.extend(_latest_us_cpi(instrument.code))
    return snapshots
