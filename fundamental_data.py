"""Adapter fundamental publik tanpa API key untuk Aero AI.

Setiap nilai membawa metadata sumber dan waktu observasi agar narasi tidak
menyajikan angka tanpa jejak. Adapter dirancang gagal secara aman: kegagalan
satu sumber tidak boleh menghentikan analisis teknikal utama.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from io import StringIO
import re
import time
from typing import Any

import requests

from market_data import Instrument, instrument_economic_currencies


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
WORLD_BANK_COUNTRY_BY_CURRENCY = {
    "USD": ("USA", "AS"), "EUR": ("EMU", "Euro Area"), "CAD": ("CAN", "Kanada"),
    "GBP": ("GBR", "Inggris"), "JPY": ("JPN", "Jepang"), "AUD": ("AUS", "Australia"),
    "CHF": ("CHE", "Swiss"), "NZD": ("NZL", "Selandia Baru"), "IDR": ("IDN", "Indonesia"),
}
ECB_EURUSD_URL = "https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?format=csvdata&lastNObservations=1"
BOC_USDCAD_URL = "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?recent=1"
RBA_AUDUSD_URL = "https://www.rba.gov.au/statistics/tables/csv/f11.1-data.csv"
BOJ_TANKAN_ENDPOINT = "https://www.stat-search.boj.or.jp/api/v1/getDataCode"
BOJ_TANKAN_SERIES_CODE = "TK99F1000601GCQ01000"
BI_HOME_URL = "https://www.bi.go.id/en/default.aspx"
BOE_BANK_RATE_ENDPOINT = "https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp"
SNB_POLICY_RATE_ENDPOINT = "https://data.snb.ch/api/cube/snbgwdzid/data/json/en"


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


def _get_html(url: str) -> str:
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
        headers={"Accept": "text/html", "User-Agent": "AeroAI-Research/1.0"},
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


def _for_instrument(items: list[FundamentalSnapshot], instrument_code: str) -> list[FundamentalSnapshot]:
    """Salin observasi sumber bersama dengan metadata instrumen pemanggil yang benar."""
    return [replace(item, instrument_code=instrument_code) for item in items]


def _latest_us_unemployment(instrument_code: str) -> list[FundamentalSnapshot]:
    def load() -> list[FundamentalSnapshot]:
        source_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/LNS14000000?latest=true"
        payload = _get_json(source_url)
        point = payload["Results"]["series"][0]["data"][0]
        observed = _to_datetime(f"{point['year']}-{point['period'][1:]}-01")
        return [FundamentalSnapshot(
            category="Makro AS",
            instrument_code="_SOURCE_",
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
    return _for_instrument(_cached("bls_unemployment", 6 * 60 * 60, load), instrument_code)


def _latest_worldbank_inflation(instrument: Instrument) -> list[FundamentalSnapshot]:
    """Ambil CPI tahunan lintas mata uang sebagai konteks struktural yang dapat ditelusuri."""
    snapshots: list[FundamentalSnapshot] = []
    for currency in dict.fromkeys(instrument_economic_currencies(instrument.code)):
        mapping = WORLD_BANK_COUNTRY_BY_CURRENCY.get(currency)
        if not mapping:
            continue
        country_code, country_name = mapping

        def load() -> list[FundamentalSnapshot]:
            source_url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/FP.CPI.TOTL.ZG?format=json&per_page=8"
            payload = _get_json(source_url)
            rows = payload[1]
            point = next(row for row in rows if row.get("value") is not None)
            return [FundamentalSnapshot(
                category=f"Makro {country_name}",
                instrument_code="_SOURCE_",
                title=f"Inflasi konsumen {country_name}",
                value=f"{float(point['value']):.1f}",
                unit="% tahunan",
                observed_at=_to_datetime(point.get("date")),
                released_at=None,
                fetched_at=_utc_now(),
                source_name="World Bank Indicators",
                source_url=source_url,
                freshness="Seri tahunan lintas negara; konteks struktural, bukan pembaruan market harian.",
                warning="Gunakan bersama kalender rilis yang lebih baru. Nilai ini tidak menggantikan actual, forecast, atau previous dari event berjalan.",
            )]

        snapshots.extend(_for_instrument(_cached(f"worldbank_cpi_{country_code}", 24 * 60 * 60, load), instrument.code))
    return snapshots


def _latest_ecb_eurusd_reference(instrument_code: str) -> list[FundamentalSnapshot]:
    if instrument_code != "EURUSD":
        return []

    def load() -> list[FundamentalSnapshot]:
        rows = list(csv.DictReader(StringIO(_get_text(ECB_EURUSD_URL))))
        point = next((row for row in reversed(rows) if row.get("OBS_VALUE") and row.get("TIME_PERIOD")), None)
        if not point:
            return []
        return [FundamentalSnapshot(
            category="Referensi bank sentral",
            instrument_code=instrument_code,
            title="ECB reference exchange rate USD/EUR",
            value=str(point["OBS_VALUE"]),
            unit="USD per EUR",
            observed_at=_to_datetime(point["TIME_PERIOD"]),
            released_at=None,
            fetched_at=_utc_now(),
            source_name="European Central Bank Data Portal",
            source_url=ECB_EURUSD_URL,
            freshness="Referensi harian ECB; bukan harga eksekusi atau tick intraday.",
            warning="Kurs referensi ECB tidak harus sama dengan harga Yahoo Finance pada saat pemindaian.",
        )]
    return _cached("ecb_eurusd_reference", 6 * 60 * 60, load)


def _latest_boc_usdcad_reference(instrument_code: str) -> list[FundamentalSnapshot]:
    if instrument_code != "USDCAD":
        return []

    def load() -> list[FundamentalSnapshot]:
        payload = _get_json(BOC_USDCAD_URL)
        observations = payload.get("observations", [])
        point = next((row for row in reversed(observations) if row.get("FXUSDCAD", {}).get("v") and row.get("d")), None)
        if not point:
            return []
        return [FundamentalSnapshot(
            category="Referensi bank sentral",
            instrument_code=instrument_code,
            title="Bank of Canada daily average USD/CAD",
            value=str(point["FXUSDCAD"]["v"]),
            unit="CAD per USD",
            observed_at=_to_datetime(point["d"]),
            released_at=None,
            fetched_at=_utc_now(),
            source_name="Bank of Canada Valet API",
            source_url=BOC_USDCAD_URL,
            freshness="Rata-rata harian Bank of Canada; bukan harga eksekusi atau tick intraday.",
            warning="Referensi harian dapat berbeda dari harga Yahoo Finance pada saat pemindaian.",
        )]
    return _cached("boc_usdcad_reference", 6 * 60 * 60, load)


def _latest_rba_audusd_reference(instrument_code: str) -> list[FundamentalSnapshot]:
    if instrument_code != "AUDUSD":
        return []

    def load() -> list[FundamentalSnapshot]:
        rows = list(csv.reader(StringIO(_get_text(RBA_AUDUSD_URL))))
        point = next((row for row in reversed(rows) if len(row) >= 2 and re.fullmatch(r"\d{2}-[A-Za-z]{3}-\d{4}", row[0].strip()) and row[1].strip()), None)
        if not point:
            return []
        observed_at = datetime.strptime(point[0].strip(), "%d-%b-%Y").replace(tzinfo=timezone.utc)
        return [FundamentalSnapshot(
            category="Referensi bank sentral",
            instrument_code=instrument_code,
            title="RBA indicative AUD/USD reference",
            value=point[1].strip(),
            unit="USD per AUD",
            observed_at=observed_at,
            released_at=None,
            fetched_at=_utc_now(),
            source_name="Reserve Bank of Australia statistical table F11.1",
            source_url=RBA_AUDUSD_URL,
            freshness="Referensi harian RBA; bukan harga eksekusi atau tick intraday.",
            warning="Nilai indikatif RBA dapat berbeda dari harga Yahoo Finance pada saat pemindaian.",
        )]
    return _cached("rba_audusd_reference", 6 * 60 * 60, load)


def _latest_boj_tankan(instrument: Instrument) -> list[FundamentalSnapshot]:
    """Ambil satu seri Tankan resmi yang eksplisit sebagai konteks kuartalan JPY."""
    if "JPY" not in instrument_economic_currencies(instrument.code):
        return []

    def load() -> list[FundamentalSnapshot]:
        now = _utc_now()
        current_quarter = max(1, min(4, (now.month - 1) // 3 + 1))
        end_period = f"{now.year}{current_quarter:02d}"
        params = {
            "format": "json", "lang": "en", "db": "CO", "startDate": "202401",
            "endDate": end_period, "code": BOJ_TANKAN_SERIES_CODE,
        }
        payload = _get_json(BOJ_TANKAN_ENDPOINT, params)
        if int(payload.get("STATUS", 0)) != 200 or not payload.get("RESULTSET"):
            return []
        series = payload["RESULTSET"][0]
        dates = series.get("VALUES", {}).get("SURVEY_DATES", [])
        values = series.get("VALUES", {}).get("VALUES", [])
        point = next(((period, value) for period, value in zip(reversed(dates), reversed(values)) if value is not None), None)
        if not point:
            return []
        period, value = point
        year, quarter = int(str(period)[:4]), int(str(period)[4:])
        if quarter not in {1, 2, 3, 4}:
            return []
        observed_at = datetime(year, quarter * 3, 1, tzinfo=timezone.utc)
        source_url = (
            f"{BOJ_TANKAN_ENDPOINT}?format=json&lang=en&db=CO&startDate=202401&"
            f"endDate={end_period}&code={BOJ_TANKAN_SERIES_CODE}"
        )
        return [FundamentalSnapshot(
            category="Makro Jepang",
            instrument_code=instrument.code,
            title="BOJ Tankan · kondisi bisnis manufaktur perusahaan besar",
            value=str(value),
            unit=str(series.get("UNIT", "% points")),
            observed_at=observed_at,
            released_at=None,
            fetched_at=now,
            source_name="Bank of Japan Time-Series Data Search API",
            source_url=source_url,
            freshness="Seri kuartalan resmi Bank of Japan; bukan indikator harga intraday.",
            warning="Tankan menggambarkan survei kondisi bisnis. Nilainya tidak menyimpulkan arah JPY atau harga instrumen secara pasti.",
        )]
    return _cached(f"boj_tankan_manufacturing_{instrument.code}", 12 * 60 * 60, load)


def _latest_bi_policy_rate(instrument: Instrument) -> list[FundamentalSnapshot]:
    """Baca BI-Rate dari kartu indikator resmi, dengan parser defensif atas halaman publik."""
    if "IDR" not in instrument_economic_currencies(instrument.code):
        return []

    def load() -> list[FundamentalSnapshot]:
        page = _get_html(BI_HOME_URL)
        pattern = (
            r"BI-Rate\s*</p>\s*<h2>\s*([0-9]+(?:[.,][0-9]+)?)%\s*</h2>\s*"
            r"<p>\s*([0-9]{2}-[A-Za-z]{3}-[0-9]{4})\s*</p>"
        )
        match = re.search(pattern, page, flags=re.IGNORECASE)
        if not match:
            return []
        raw_value, raw_date = match.groups()
        observed_at = datetime.strptime(raw_date, "%d-%b-%Y").replace(tzinfo=timezone.utc)
        return [FundamentalSnapshot(
            category="Makro Indonesia",
            instrument_code=instrument.code,
            title="BI-Rate",
            value=raw_value.replace(",", "."),
            unit="%",
            observed_at=observed_at,
            released_at=None,
            fetched_at=_utc_now(),
            source_name="Bank Indonesia",
            source_url=BI_HOME_URL,
            freshness="Kartu indikator publik Bank Indonesia; kebijakan dapat berubah pada rapat berikutnya.",
            warning="BI-Rate adalah konteks kebijakan moneter IDR, bukan sinyal arah tunggal IHSG atau saham IDX.",
        )]
    return _cached(f"bank_indonesia_policy_rate_{instrument.code}", 6 * 60 * 60, load)


def _latest_boe_policy_rate(instrument: Instrument) -> list[FundamentalSnapshot]:
    """Ambil Bank Rate resmi Inggris dari ekspor CSV database Bank of England."""
    if "GBP" not in instrument_economic_currencies(instrument.code):
        return []

    def load() -> list[FundamentalSnapshot]:
        now = _utc_now()
        date_from = f"01/Jan/{now.year - 2}"
        date_to = now.strftime("%d/%b/%Y")
        source_url = (
            f"{BOE_BANK_RATE_ENDPOINT}?csv.x=yes&Datefrom={date_from}&Dateto={date_to}&"
            "SeriesCodes=IUDBEDR&CSVF=TN&UsingCodes=Y&VPD=Y&VFD=N"
        )
        rows = list(csv.DictReader(StringIO(_get_text(source_url))))
        point = next((row for row in reversed(rows) if row.get("DATE") and row.get("IUDBEDR")), None)
        if not point:
            return []
        observed_at = datetime.strptime(point["DATE"], "%d %b %Y").replace(tzinfo=timezone.utc)
        return [FundamentalSnapshot(
            category="Makro Inggris",
            instrument_code=instrument.code,
            title="Bank Rate",
            value=point["IUDBEDR"],
            unit="%",
            observed_at=observed_at,
            released_at=None,
            fetched_at=now,
            source_name="Bank of England Database",
            source_url=source_url,
            freshness="Seri kebijakan resmi Inggris; bukan proyeksi keputusan Bank of England berikutnya.",
            warning="Bank Rate adalah konteks GBP, bukan instruksi transaksi atau prediksi arah harga.",
        )]
    return _cached(f"bank_of_england_bank_rate_{instrument.code}", 6 * 60 * 60, load)


def _latest_snb_policy_rate(instrument: Instrument) -> list[FundamentalSnapshot]:
    """Ambil SNB policy rate dari seri JSON eksplisit untuk konteks CHF."""
    if "CHF" not in instrument_economic_currencies(instrument.code):
        return []

    def load() -> list[FundamentalSnapshot]:
        now = _utc_now()
        start_date = (now.replace(day=1)).strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")
        params = {"dimSel": "D0(LZ)", "fromDate": start_date, "toDate": end_date}
        payload = _get_json(SNB_POLICY_RATE_ENDPOINT, params)
        series_list = payload.get("timeseries", [])
        if not series_list:
            return []
        series = series_list[0]
        point = next((value for value in reversed(series.get("values", [])) if value.get("value") is not None and value.get("date")), None)
        if not point:
            return []
        metadata = series.get("metadata", {})
        source_url = f"{SNB_POLICY_RATE_ENDPOINT}?dimSel=D0(LZ)&fromDate={start_date}&toDate={end_date}"
        return [FundamentalSnapshot(
            category="Makro Swiss",
            instrument_code=instrument.code,
            title="SNB policy rate",
            value=str(point["value"]),
            unit=str(metadata.get("unit", "%")),
            observed_at=_to_datetime(str(point["date"])),
            released_at=None,
            fetched_at=now,
            source_name="Swiss National Bank Data Portal",
            source_url=source_url,
            freshness="Seri kebijakan resmi Swiss; dipanggil dengan jendela tanggal terbatas dan cache, bukan polling berlebih.",
            warning="SNB policy rate adalah konteks CHF dan tidak menyimpulkan arah harga USDCHF secara pasti.",
        )]
    return _cached(f"swiss_national_bank_policy_rate_{instrument.code}", 6 * 60 * 60, load)


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
                instrument_code="_SOURCE_",
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

    return _for_instrument(_cached("fred_market_context", 15 * 60, load), instrument_code)


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
                instrument_code="_SOURCE_",
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

    return _for_instrument(_cached("new_york_fed_reference_rates", 15 * 60, load), instrument_code)


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

    return _cached(f"eia_petroleum_inventory_{instrument_code}", 60 * 60, load)


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

    return _cached(f"eia_natural_gas_storage_{instrument_code}", 60 * 60, load)


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
    snapshots.extend(_latest_worldbank_inflation(instrument))
    snapshots.extend(_latest_ecb_eurusd_reference(instrument.code))
    snapshots.extend(_latest_boc_usdcad_reference(instrument.code))
    snapshots.extend(_latest_rba_audusd_reference(instrument.code))
    snapshots.extend(_latest_boj_tankan(instrument))
    snapshots.extend(_latest_bi_policy_rate(instrument))
    snapshots.extend(_latest_boe_policy_rate(instrument))
    snapshots.extend(_latest_snb_policy_rate(instrument))
    # Pengangguran BLS tetap dibatasi pada aset yang berdenominasi/berkaitan USD.
    if instrument.code not in {"BTCUSD", "ETHUSD", "BNBUSD", "SOLUSD", "XRPUSD", "ADAUSD", "DOTUSD", "MATICUSD", "LINKUSD", "AVAXUSD"}:
        snapshots.extend(_latest_us_unemployment(instrument.code))
    return snapshots
