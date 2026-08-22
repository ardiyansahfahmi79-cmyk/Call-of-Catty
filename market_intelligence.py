"""Komponen market-intelligence lokal Aero AI.

Modul ini bukan model bahasa atau mesin prediksi. Semua klasifikasi memakai
aturan terukur atas snapshot harga publik, metadata sumber, dan observasi
historis yang tersedia. Tidak ada angka pasar yang dibangkitkan ketika data
publik gagal atau sampel historis tidak memadai.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import get_close_matches
import re

import pandas as pd

from fundamental_data import FundamentalSnapshot
from market_data import MarketSnapshot, instrument_economic_currencies


CURRENCY_DISPLAY_NAMES = {
    "USD": "AS", "EUR": "Euro Area", "CAD": "Kanada", "GBP": "Inggris",
    "JPY": "Jepang", "AUD": "Australia", "CHF": "Swiss", "NZD": "Selandia Baru",
    "IDR": "Indonesia",
}

_CURRENCY_ROUTING_NOTES = {
    "USD": "data AS, ekspektasi imbal hasil, dan kondisi likuiditas USD",
    "EUR": "data Euro Area, komunikasi ECB, dan kondisi EUR",
    "CAD": "data Kanada, Bank of Canada, serta kondisi energi bila relevan",
    "GBP": "data Inggris, Bank of England, dan kondisi GBP",
    "JPY": "data Jepang, Bank of Japan, serta kondisi JPY",
    "AUD": "data Australia, Reserve Bank of Australia, serta siklus komoditas bila relevan",
    "CHF": "data Swiss, Swiss National Bank, dan kondisi CHF",
    "NZD": "data Selandia Baru, Reserve Bank of New Zealand, dan kondisi NZD",
    "IDR": "data Indonesia, Bank Indonesia, dan kondisi rupiah",
}

_PHRASE_REPLACEMENTS = {
    "retal sales": "retail sales",
    "retail salse": "retail sales",
    "retail sale": "retail sales",
    "penjualan ritel": "retail sales",
    "non farm payroll": "nfp",
    "nonfarm payroll": "nfp",
    "federal reserve meeting": "fomc",
    "time frame": "timeframe",
    "resiko": "risiko",
}

_FUZZY_TERMS = (
    "retail", "sales", "consumer", "price", "index", "inflasi", "analisa",
    "analisis", "timeframe", "fundamental", "indikator", "volatilitas", "risiko",
    "fomc", "nonfarm", "payroll", "jolts", "pengangguran",
)


@dataclass(frozen=True)
class NormalizationResult:
    normalized_question: str
    notes: tuple[str, ...]


@dataclass(frozen=True)
class MacroRoute:
    instrument_code: str
    currencies: tuple[str, ...]
    focus: tuple[str, ...]


@dataclass(frozen=True)
class EvidenceScore:
    score: int
    label: str
    source_count: int
    candle_age_minutes: int
    notes: tuple[str, ...]


@dataclass(frozen=True)
class MarketRegime:
    label: str
    volatility_label: str
    rationale: str


@dataclass(frozen=True)
class HistoricalEvaluation:
    sample_count: int
    positive_count: int
    negative_count: int
    median_change_pct: float
    mean_change_pct: float
    horizon_candles: int
    censor_gap_days: int
    regime_label: str


def normalize_market_language(question: str) -> NormalizationResult:
    """Normalisasi typo ringan dan format pair tanpa menebak instrumen yang ambigu."""
    normalized = re.sub(r"\s+", " ", question.strip().casefold())
    notes: list[str] = []

    for original, replacement in _PHRASE_REPLACEMENTS.items():
        if original in normalized:
            normalized = normalized.replace(original, replacement)
            notes.append(f"{original} → {replacement}")

    for code in (
        "XAUUSD", "XAGUSD", "XAUEUR", "XAGEUR", "XBRUSD", "XNGUSD", "XPDUSD",
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
        "EURGBP", "EURJPY", "GBPJPY", "BTCUSD", "ETHUSD", "BNBUSD", "SOLUSD",
        "XRPUSD", "ADAUSD", "DOTUSD", "MATICUSD", "LINKUSD", "AVAXUSD",
    ):
        left, right = code[:3].casefold(), code[3:].casefold()
        pattern = rf"(?<![a-z0-9]){left}\s*[/\-_]?\s*{right}(?![a-z0-9])"
        updated, count = re.subn(pattern, code.casefold(), normalized)
        if count and updated != normalized:
            notes.append(f"format pair → {code}")
        normalized = updated

    tokens = re.findall(r"\b[a-z]{5,}\b", normalized)
    for token in tokens:
        if token in _FUZZY_TERMS:
            continue
        matched = get_close_matches(token, _FUZZY_TERMS, n=2, cutoff=0.9)
        if len(matched) == 1:
            replacement = matched[0]
            normalized = re.sub(rf"\b{re.escape(token)}\b", replacement, normalized)
            notes.append(f"{token} → {replacement}")

    return NormalizationResult(normalized, tuple(dict.fromkeys(notes)))


def normalization_section(result: NormalizationResult) -> str:
    if not result.notes:
        return ""
    changes = "; ".join(f"**{note}**" for note in result.notes[:3])
    return (
        "**NORMALISASI INPUT**\n\n"
        f"Aero AI membaca variasi istilah berikut sebagai konteks market yang sama: {changes}. "
        "Normalisasi hanya diterapkan saat kecocokan cukup jelas; kode atau maksud yang ambigu tetap akan diminta klarifikasi."
    )


def build_macro_route(instrument_code: str) -> MacroRoute:
    currencies = instrument_economic_currencies(instrument_code)
    focus = tuple(_CURRENCY_ROUTING_NOTES.get(currency, currency) for currency in currencies)
    return MacroRoute(instrument_code.upper(), currencies, focus)


def macro_router_section(instrument_code: str) -> str:
    route = build_macro_route(instrument_code)
    if not route.currencies:
        return ""
    labels = " dan ".join(f"**{CURRENCY_DISPLAY_NAMES.get(currency, currency)} ({currency})**" for currency in route.currencies)
    focus = "; ".join(route.focus)
    return (
        "**GLOBAL MACRO ROUTER**\n\n"
        f"Sisi ekonomi yang dipetakan untuk **{route.instrument_code}** adalah {labels}. "
        f"Router memprioritaskan {focus}. Pemetaan ini hanya memilih konteks yang relevan; "
        "pemetaan tidak menyimpulkan arah harga atau dampak rilis secara pasti."
    )


def classify_market_regime(snapshot: MarketSnapshot) -> MarketRegime:
    """Klasifikasikan kondisi snapshot, bukan arah harga masa depan."""
    data = snapshot.indicators
    price, ma50, ma200 = float(data["price"]), float(data["ma50"]), float(data["ma200"])
    adx, volatility = float(data["adx14"]), float(data["volatility20"])
    atr_pct = abs(float(data["atr14"])) / price * 100 if price else 0.0
    if price > ma50 > ma200 and adx >= 20:
        label = "TREND BULLISH TERKONFIRMASI"
        rationale = "harga berada di atas MA 50 dan MA 200, sementara ADX menunjukkan kekuatan tren yang memadai"
    elif price < ma50 < ma200 and adx >= 20:
        label = "TREND BEARISH TERKONFIRMASI"
        rationale = "harga berada di bawah MA 50 dan MA 200, sementara ADX menunjukkan kekuatan tren yang memadai"
    elif adx < 18:
        label = "RANGE / TREN LEMAH"
        rationale = "ADX masih rendah sehingga struktur tren belum cukup kuat untuk dibaca sebagai tren terkonfirmasi"
    else:
        label = "TRANSISI / KONFLUENSI TERBATAS"
        rationale = "hubungan harga dan rata-rata bergerak belum sepenuhnya selaras atau kekuatan tren masih berubah"
    if volatility >= 45 or atr_pct >= 2.5:
        volatility_label = "TINGGI"
    elif volatility >= 20 or atr_pct >= 1.0:
        volatility_label = "MENENGAH"
    else:
        volatility_label = "RENDAH"
    return MarketRegime(label, volatility_label, rationale)


def evidence_score(snapshot: MarketSnapshot, fundamentals: list[FundamentalSnapshot], calendar_state: str) -> EvidenceScore:
    """Nilai kelengkapan dan keterbaruan bukti; bukan probabilitas sinyal atau akurasi prediksi."""
    now = datetime.now(timezone.utc)
    candle_age_minutes = max(0, int((now - snapshot.last_candle_at.astimezone(timezone.utc)).total_seconds() // 60))
    sources = {snapshot.source, *(item.source_name for item in fundamentals)}
    score = 45
    notes = ["snapshot harga membawa sumber dan waktu candle"]
    if candle_age_minutes <= 180:
        score += 20
        notes.append("candle berada dalam jendela keterbaruan pendek")
    elif candle_age_minutes <= 24 * 60:
        score += 12
        notes.append("candle tersedia tetapi bukan pembaruan intraday terbaru")
    else:
        score += 4
        notes.append("candle memiliki jeda waktu yang perlu diperhatikan")
    if fundamentals:
        score += min(18, 6 + 3 * len(sources - {snapshot.source}))
        notes.append(f"{len(fundamentals)} observasi fundamental membawa metadata sumber")
    if calendar_state == "live":
        score += 10
        notes.append("kalender publik diperbarui pada sesi ini")
    elif calendar_state == "cache_aktif":
        score += 6
        notes.append("kalender memakai cache sesi yang masih aktif")
    elif calendar_state == "cache_kedaluwarsa":
        score -= 8
        notes.append("kalender memakai cache kedaluwarsa")
    score = max(0, min(100, score))
    label = "BUKTI KUAT" if score >= 80 else "BUKTI CUKUP" if score >= 60 else "BUKTI TERBATAS"
    return EvidenceScore(score, label, len(sources), candle_age_minutes, tuple(notes))


def evidence_section(snapshot: MarketSnapshot, fundamentals: list[FundamentalSnapshot], calendar_state: str) -> str:
    evidence = evidence_score(snapshot, fundamentals, calendar_state)
    notes = "; ".join(evidence.notes[:3])
    return (
        "**EVIDENCE & DATA TRUST SCORE**\n\n"
        f"Status **{evidence.label} · {evidence.score}/100** berdasarkan jejak sumber, keterbaruan candle, metadata fundamental, dan status kalender yang tersedia. "
        f"Sumber unik: **{evidence.source_count}**; usia candle: **{evidence.candle_age_minutes} menit**. {notes}. "
        "Skor ini mengukur kelengkapan bukti pada pemindaian, bukan akurasi prediksi atau peluang profit."
    )


def regime_section(snapshot: MarketSnapshot) -> str:
    regime = classify_market_regime(snapshot)
    return (
        "**MARKET REGIME ENGINE**\n\n"
        f"Regime saat ini: **{regime.label}** dengan volatilitas **{regime.volatility_label}**. "
        f"Dasar pembacaan: {regime.rationale}. Label ini menggambarkan kondisi snapshot dan harus dievaluasi ulang ketika candle baru masuk."
    )


def _rsi_series(close: pd.Series, length: int = 14) -> pd.Series:
    diff = close.diff()
    gain = diff.clip(lower=0).ewm(alpha=1 / length, adjust=False).mean()
    loss = (-diff.clip(upper=0)).ewm(alpha=1 / length, adjust=False).mean()
    ratio = gain / loss.replace(0, pd.NA)
    return (100 - (100 / (1 + ratio))).fillna(50.0)


def historical_regime_evaluation(snapshot: MarketSnapshot, horizon_candles: int = 3) -> HistoricalEvaluation | None:
    """Nilai observasi historis ber-regime sama dengan gap sensor minimal satu hari.

    Seluruh kandidat berhenti setidaknya satu hari sebelum candle terbaru. Dengan
    demikian perubahan berikutnya untuk kandidat historis tidak memakai candle
    terakhir sebagai informasi yang "sudah diketahui" pada titik kandidat.
    """
    candles = snapshot.candles.copy()
    if candles.empty or len(candles) < 230 or horizon_candles < 1:
        return None
    close = candles["close"].astype(float)
    ma50 = close.rolling(50, min_periods=50).mean()
    ma200 = close.rolling(200, min_periods=200).mean()
    rsi = _rsi_series(close)
    current = classify_market_regime(snapshot).label
    if current == "TREND BULLISH TERKONFIRMASI":
        mask = (close > ma50) & (ma50 > ma200) & (rsi >= 52)
    elif current == "TREND BEARISH TERKONFIRMASI":
        mask = (close < ma50) & (ma50 < ma200) & (rsi <= 48)
    elif current == "RANGE / TREN LEMAH":
        mask = ((close - ma50).abs() / ma50.replace(0, pd.NA) < 0.012) & rsi.between(44, 56)
    else:
        mask = (close.notna() & ma50.notna() & ma200.notna())
    censor_boundary = candles.index[-1] - pd.Timedelta(days=1)
    returns: list[float] = []
    for position in range(200, len(candles) - horizon_candles):
        if candles.index[position + horizon_candles] > censor_boundary or not bool(mask.iloc[position]):
            continue
        start, end = float(close.iloc[position]), float(close.iloc[position + horizon_candles])
        if start:
            returns.append((end / start - 1) * 100)
    if len(returns) < 5:
        return None
    series = pd.Series(returns[-80:], dtype="float64")
    return HistoricalEvaluation(
        sample_count=int(series.count()),
        positive_count=int((series > 0).sum()),
        negative_count=int((series < 0).sum()),
        median_change_pct=float(series.median()),
        mean_change_pct=float(series.mean()),
        horizon_candles=horizon_candles,
        censor_gap_days=1,
        regime_label=current,
    )


def historical_section(snapshot: MarketSnapshot) -> str:
    evaluation = historical_regime_evaluation(snapshot)
    if not evaluation:
        return (
            "**HISTORICAL SCENARIO LAB & LOCAL EVALUATION**\n\n"
            "Candle historis yang memenuhi regime saat ini belum cukup untuk evaluasi yang layak. "
            "Aero AI tidak akan menampilkan statistik sampel yang terlalu kecil atau membuat estimasi pengganti."
        )
    return (
        "**HISTORICAL SCENARIO LAB & LOCAL EVALUATION**\n\n"
        f"Pada **{evaluation.sample_count}** observasi historis dengan regime **{evaluation.regime_label}** di candle yang tersedia, "
        f"perubahan sampai **{evaluation.horizon_candles} candle** berikutnya memiliki median **{evaluation.median_change_pct:+.2f}%** dan rerata **{evaluation.mean_change_pct:+.2f}%**; "
        f"{evaluation.positive_count} observasi positif dan {evaluation.negative_count} observasi negatif. "
        f"Sampel berhenti minimal **{evaluation.censor_gap_days} hari** sebelum candle terakhir untuk mengurangi kebocoran informasi. "
        "Ini adalah evaluasi deskriptif atas jendela historis, bukan forecast atau instruksi transaksi berikutnya."
    )
