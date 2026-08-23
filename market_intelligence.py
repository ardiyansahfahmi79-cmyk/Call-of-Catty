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


@dataclass(frozen=True)
class SourceHealth:
    price_state: str
    calendar_state: str
    fundamental_source_count: int
    oldest_observation_days: int


@dataclass(frozen=True)
class MarketStructureQuality:
    score: int
    label: str
    notes: tuple[str, ...]


@dataclass(frozen=True)
class LocalEvaluationStudio:
    dataset_id: str
    regime_label: str
    horizon_candles: int
    censor_gap_days: int
    train_count: int
    validation_count: int
    test_count: int
    test_positive_count: int
    test_negative_count: int
    test_median_change_pct: float


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
        "**AUDIT NORMALISASI INPUT**\n\n"
        f"Aero AI membaca variasi istilah berikut sebagai konteks market yang sama: {changes}. "
        "Normalisasi hanya diterapkan saat kecocokan cukup jelas; kode atau maksud yang ambigu tetap akan diminta klarifikasi. "
        "Pesan asli tetap menjadi rujukan di riwayat chat sehingga pembacaan ini dapat diperiksa pengguna."
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


def source_health(snapshot: MarketSnapshot, fundamentals: list[FundamentalSnapshot], calendar_state: str) -> SourceHealth:
    """Ringkas kesehatan sumber yang benar-benar tersedia, tanpa mengarang status endpoint lain."""
    now = datetime.now(timezone.utc)
    observation_ages = [max(0, (now - item.observed_at.astimezone(timezone.utc)).days) for item in fundamentals]
    candle_age_minutes = max(0, int((now - snapshot.last_candle_at.astimezone(timezone.utc)).total_seconds() // 60))
    price_state = "candle tersedia" if candle_age_minutes <= 24 * 60 else "candle tersedia dengan jeda waktu"
    return SourceHealth(
        price_state=price_state,
        calendar_state=calendar_state,
        fundamental_source_count=len({item.source_name for item in fundamentals}),
        oldest_observation_days=max(observation_ages, default=0),
    )


def source_health_section(snapshot: MarketSnapshot, fundamentals: list[FundamentalSnapshot], calendar_state: str) -> str:
    health = source_health(snapshot, fundamentals, calendar_state)
    calendar_label = {
        "live": "diperbarui pada sesi ini",
        "cache_aktif": "memakai cache sesi aktif",
        "cache_kedaluwarsa": "memakai cache kedaluwarsa",
        "tidak_tersedia": "belum tersedia",
        "belum_dipindai": "belum diminta",
    }.get(health.calendar_state, health.calendar_state)
    fundamental_label = (
        f"{health.fundamental_source_count} sumber fundamental tersedia; observasi tertua sekitar {health.oldest_observation_days} hari"
        if health.fundamental_source_count else "belum ada sumber fundamental tambahan yang tersedia"
    )
    return (
        "**SOURCE HEALTH CONSOLE**\n\n"
        f"Harga: **{health.price_state}**. Kalender: **{calendar_label}**. Fundamental: **{fundamental_label}**. "
        "Console ini melaporkan status bukti yang tersedia pada pemindaian ini; ia tidak mengklaim semua endpoint eksternal sedang online."
    )


def provenance_section(snapshot: MarketSnapshot, fundamentals: list[FundamentalSnapshot], calendar_state: str) -> str:
    """Buat jejak sumber ringkas dari metadata nyata tanpa database tambahan."""
    price_line = (
        f"Harga: **{snapshot.source}**; candle **{snapshot.last_candle_at.astimezone(timezone.utc).strftime('%d %b %Y %H:%M UTC')}**; "
        f"diambil **{snapshot.fetched_at.astimezone(timezone.utc).strftime('%H:%M:%S UTC')}**."
    )
    calendar_line = f"Kalender: status **{calendar_state}** pada sesi pemindaian ini."
    fundamentals_line = "Fundamental: belum ada observasi tambahan yang dapat ditelusuri."
    if fundamentals:
        items = []
        for item in fundamentals[:4]:
            items.append(
                f"{item.title} — {item.source_name}, observasi {item.observed_at.astimezone(timezone.utc).strftime('%d %b %Y')}"
            )
        fundamentals_line = "Fundamental: " + "; ".join(items) + "."
    return (
        "**DATA PROVENANCE LEDGER**\n\n"
        f"{price_line} {calendar_line} {fundamentals_line} "
        "Gunakan tautan sumber pada kartu data untuk memeriksa nilai dan frekuensinya."
    )


def _calendar_numeric(value: str) -> tuple[float, str] | None:
    """Ambil angka kalender apa adanya, hanya bila satu nilai numerik jelas tersedia."""
    compact = str(value or "").strip().replace(",", "")
    match = re.fullmatch(r"([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*(%|[kmb])?", compact.casefold())
    if not match:
        return None
    return float(match.group(1)), match.group(2) or ""


def release_surprise_section(events: list[object]) -> str:
    """Bandingkan actual dan forecast sumber kalender tanpa menamai dampak harga."""
    for event in events:
        actual = _calendar_numeric(getattr(event, "actual", ""))
        forecast = _calendar_numeric(getattr(event, "forecast", ""))
        if not actual or not forecast or actual[1] != forecast[1]:
            continue
        difference = actual[0] - forecast[0]
        relation = "di atas" if difference > 0 else "di bawah" if difference < 0 else "sama dengan"
        unit = actual[1]
        delta = f"{difference:+.2f}{unit}" if difference else f"0.00{unit}"
        title = getattr(event, "title", "Agenda")
        currency = getattr(event, "currency", "")
        return (
            "**RELEASE SURPRISE MAP**\n\n"
            f"Untuk **{title} · {currency}**, actual sumber kalender **{actual[0]:g}{unit}** {relation} forecast **{forecast[0]:g}{unit}**; "
            f"selisih actual − forecast adalah **{delta}**. Peta ini hanya membandingkan dua nilai yang diterbitkan sumber; "
            "ia tidak menetapkan reaksi harga bullish atau bearish secara otomatis."
        )
    return (
        "**RELEASE SURPRISE MAP**\n\n"
        "Actual dan forecast dengan unit yang dapat dibandingkan belum tersedia pada agenda yang cocok. "
        "Aero AI tidak menghitung kejutan rilis dari jadwal, previous, atau nilai berformat ambigu."
    )


def market_structure_quality(snapshot: MarketSnapshot) -> MarketStructureQuality:
    """Nilai apakah candle dan indikator cukup memadai untuk dibaca sebagai struktur pasar."""
    data = snapshot.indicators
    now = datetime.now(timezone.utc)
    age_minutes = max(0, int((now - snapshot.last_candle_at.astimezone(timezone.utc)).total_seconds() // 60))
    price = abs(float(data.get("price", 0.0)))
    atr = abs(float(data.get("atr14", 0.0)))
    adx = float(data.get("adx14", 0.0))
    volume = float(data.get("relative_volume", 0.0))
    ma50, ma200 = float(data.get("ma50", 0.0)), float(data.get("ma200", 0.0))
    score, notes = 0, []
    if len(snapshot.candles) >= 200:
        score += 30
        notes.append("minimal 200 candle tersedia untuk MA 200")
    elif len(snapshot.candles) >= 50:
        score += 15
        notes.append("candle cukup untuk MA 50 tetapi belum ideal untuk struktur panjang")
    else:
        notes.append("jumlah candle terbatas")
    if age_minutes <= 24 * 60:
        score += 20
        notes.append("candle berada dalam jendela waktu satu hari")
    else:
        notes.append("candle memiliki jeda waktu di atas satu hari")
    if price and atr / price > 0:
        score += 15
        notes.append("ATR tersedia sebagai ukuran rentang")
    if adx >= 10:
        score += 15
        notes.append("ADX tersedia untuk menilai kekuatan tren")
    if volume > 0:
        score += 10
        notes.append("volume relatif tersedia")
    if ma50 and ma200:
        score += 10
        notes.append("MA 50 dan MA 200 tersedia")
    score = max(0, min(100, score))
    label = "STRUKTUR LAYAK DIBACA" if score >= 75 else "STRUKTUR TERBATAS" if score >= 50 else "STRUKTUR BELUM MEMADAI"
    return MarketStructureQuality(score, label, tuple(notes))


def market_structure_quality_section(snapshot: MarketSnapshot) -> str:
    quality = market_structure_quality(snapshot)
    return (
        "**MARKET STRUCTURE QUALITY GATE**\n\n"
        f"Status **{quality.label} · {quality.score}/100**. Dasar: {'; '.join(quality.notes[:4])}. "
        "Gate ini menilai kelayakan data dan struktur untuk dibaca, bukan kekuatan sinyal atau probabilitas profit."
    )


def cross_asset_context_section(snapshot: MarketSnapshot, fundamentals: list[FundamentalSnapshot]) -> str:
    """Matriks ringkas dari komponen lintas aset yang benar-benar tersedia pada pemindaian saat ini."""
    rows = [f"Instrumen fokus: **{snapshot.instrument.code}** ({snapshot.instrument.asset_class})"]
    for item in fundamentals:
        title = item.title.casefold()
        if any(marker in title for marker in ("vix", "treasury", "sofr", "effr", "policy rate", "bank rate", "tankan")):
            rows.append(f"{item.title}: **{item.value} {item.unit}** ({item.source_name})")
    if len(rows) == 1:
        rows.append("Komponen lintas aset tambahan belum tersedia dari sumber publik pada pemindaian ini")
    return (
        "**CROSS-ASSET CONTEXT MATRIX**\n\n"
        f"{' ; '.join(rows[:5])}. Matriks ini merangkum proxy risiko, imbal hasil, atau kebijakan yang tersedia; "
        "keterkaitan antar aset bersifat deskriptif dan bukan bukti sebab-akibat."
    )


def scenario_invalidation_section(snapshot: MarketSnapshot) -> str:
    """Tentukan kondisi pembatalan pembacaan struktur, bukan stop-loss atau instruksi posisi."""
    data = snapshot.indicators
    price, ma50, ma200 = float(data["price"]), float(data["ma50"]), float(data["ma200"])
    low20, high20 = float(data["low20"]), float(data["high20"])
    regime = classify_market_regime(snapshot).label
    if regime == "TREND BULLISH TERKONFIRMASI":
        condition = (
            f"pembacaan tren bullish perlu ditinjau ulang bila candle menutup kembali di bawah MA 50 **{ma50:.5f}** "
            f"dan struktur gagal mempertahankan low 20 candle **{low20:.5f}**"
        )
    elif regime == "TREND BEARISH TERKONFIRMASI":
        condition = (
            f"pembacaan tren bearish perlu ditinjau ulang bila candle menutup kembali di atas MA 50 **{ma50:.5f}** "
            f"dan struktur menembus high 20 candle **{high20:.5f}**"
        )
    else:
        condition = (
            f"struktur belum memiliki arah dominan; konfirmasi perlu ditinjau bila harga keluar dan bertahan di luar range 20 candle "
            f"**{low20:.5f}–{high20:.5f}** sambil MA 50/MA 200 mulai selaras"
        )
    return (
        "**SCENARIO INVALIDATION MAP**\n\n"
        f"Pada harga referensi **{price:.5f}**, {condition}. Perubahan regime atau rilis agenda berdampak tinggi juga dapat membatasi relevansi pembacaan sebelumnya. "
        "Peta ini adalah kondisi evaluasi ulang analisis, bukan stop-loss personal atau instruksi transaksi."
    )


def comparative_regime_replay_section(snapshot: MarketSnapshot) -> str:
    """Bandingkan distribusi regime sama untuk horizon 1, 3, dan 6 candle bila sampel memadai."""
    results = [historical_regime_evaluation(snapshot, horizon) for horizon in (1, 3, 6)]
    valid = [item for item in results if item]
    if not valid:
        return (
            "**COMPARATIVE REGIME REPLAY**\n\n"
            "Candle historis ber-regime sama belum cukup untuk membandingkan horizon 1, 3, dan 6 candle. "
            "Aero AI tidak akan memperluas sampel secara paksa atau menyajikan forecast pengganti."
        )
    rows = []
    for item in valid:
        rows.append(
            f"{item.horizon_candles} candle: n={item.sample_count}, median **{item.median_change_pct:+.2f}%**, "
            f"positif/negatif {item.positive_count}/{item.negative_count}"
        )
    return (
        "**COMPARATIVE REGIME REPLAY**\n\n"
        f"Distribusi historis pada regime **{valid[0].regime_label}** — {'; '.join(rows)}. "
        "Setiap horizon memakai censor gap satu hari dan bersifat replay deskriptif, bukan proyeksi candle berikutnya."
    )


def local_evaluation_studio(snapshot: MarketSnapshot, horizon_candles: int = 3) -> LocalEvaluationStudio | None:
    """Siapkan evaluasi temporal terpisah tanpa melatih classifier atau memakai candle terbaru sebagai target."""
    candles = snapshot.candles.copy()
    if candles.empty or len(candles) < 260 or horizon_candles < 1:
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
        mask = close.notna() & ma50.notna() & ma200.notna()
    censor_boundary = candles.index[-1] - pd.Timedelta(days=1)
    observations: list[tuple[object, float]] = []
    for position in range(200, len(candles) - horizon_candles):
        if candles.index[position + horizon_candles] > censor_boundary or not bool(mask.iloc[position]):
            continue
        start, end = float(close.iloc[position]), float(close.iloc[position + horizon_candles])
        if start:
            observations.append((candles.index[position], (end / start - 1) * 100))
    if len(observations) < 15:
        return None
    train_end = int(len(observations) * 0.6)
    validation_end = int(len(observations) * 0.8)
    train, validation, test = observations[:train_end], observations[train_end:validation_end], observations[validation_end:]
    if min(len(train), len(validation), len(test)) < 3:
        return None
    test_series = pd.Series([value for _, value in test], dtype="float64")
    dataset_id = (
        f"{snapshot.instrument.code}-{snapshot.interval}-"
        f"{candles.index[0].strftime('%Y%m%d')}-{censor_boundary.strftime('%Y%m%d')}"
    )
    return LocalEvaluationStudio(
        dataset_id=dataset_id,
        regime_label=current,
        horizon_candles=horizon_candles,
        censor_gap_days=1,
        train_count=len(train),
        validation_count=len(validation),
        test_count=len(test),
        test_positive_count=int((test_series > 0).sum()),
        test_negative_count=int((test_series < 0).sum()),
        test_median_change_pct=float(test_series.median()),
    )


def local_evaluation_section(snapshot: MarketSnapshot) -> str:
    evaluation = local_evaluation_studio(snapshot)
    if not evaluation:
        return (
            "**LOCAL DATASET & EVALUATION STUDIO**\n\n"
            "Belum ada cukup episode historis untuk membentuk split temporal train/validation/test yang layak. "
            "Aero AI tidak menjalankan pelatihan model atau mengisi metrik evaluasi ketika sampel belum memadai."
        )
    return (
        "**LOCAL DATASET & EVALUATION STUDIO**\n\n"
        f"Versi dataset lokal **{evaluation.dataset_id}** memakai regime **{evaluation.regime_label}** dengan horizon {evaluation.horizon_candles} candle. "
        f"Split temporal: train **{evaluation.train_count}**, validation **{evaluation.validation_count}**, test **{evaluation.test_count}**. "
        f"Pada test set, observasi positif/negatif adalah **{evaluation.test_positive_count}/{evaluation.test_negative_count}** dengan median **{evaluation.test_median_change_pct:+.2f}%**. "
        f"Candle target berhenti minimal {evaluation.censor_gap_days} hari sebelum data terakhir. Ini adalah kontrol evaluasi dataset; belum ada classifier atau model prediksi yang dilatih."
    )


def policy_divergence_section(snapshot: MarketSnapshot, fundamentals: list[FundamentalSnapshot]) -> str:
    """Tampilkan observasi kebijakan per sisi mata uang tanpa menghitung spread dari seri yang tidak sebanding."""
    route = build_macro_route(snapshot.instrument.code)
    if len(route.currencies) < 2:
        return ""
    indicators_by_currency: dict[str, list[str]] = {currency: [] for currency in route.currencies}
    for item in fundamentals:
        title = item.title.casefold()
        if not any(marker in title for marker in ("policy rate", "bank rate", "bi-rate", "effr", "sofr", "tankan")):
            continue
        if "sofr" in title or "effr" in title:
            currency = "USD"
        elif "tankan" in title:
            currency = "JPY"
        elif "bi-rate" in title:
            currency = "IDR"
        elif "snb" in title:
            currency = "CHF"
        elif "bank rate" in title:
            currency = "GBP"
        else:
            continue
        if currency in indicators_by_currency:
            indicators_by_currency[currency].append(f"{item.title} **{item.value} {item.unit}** ({item.observed_at.strftime('%d %b %Y')})")
    rows = []
    for currency in route.currencies:
        label = CURRENCY_DISPLAY_NAMES.get(currency, currency)
        observations = indicators_by_currency[currency]
        rows.append(f"{label}: " + ("; ".join(observations[:2]) if observations else "belum ada observasi kebijakan yang sebanding pada pemindaian ini"))
    return (
        "**POLICY DIVERGENCE BOARD**\n\n"
        f"{' | '.join(rows)}. Board ini membandingkan konteks kebijakan yang tersedia per sisi pair. "
        "Aero AI tidak menghitung spread atau memprediksi keputusan rapat bila seri kedua tidak sebanding atau belum tersedia."
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
