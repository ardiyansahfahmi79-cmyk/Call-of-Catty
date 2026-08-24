"""Konteks volatilitas, level periode selesai, dan sesi berbasis timestamp candle.

Filosofi berkas ini: semua metrik berasal dari candle yang tersedia. Pivot hanya
menggunakan hari yang telah selesai, sedangkan sesi memakai zona waktu IANA agar
pergeseran daylight-saving tidak di-hardcode. Output menjelaskan konteks dan
tidak mengubahnya menjadi sinyal transaksi atau prediksi harga.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

from market_data import MarketSnapshot


@dataclass(frozen=True)
class BollingerContext:
    middle: float
    upper: float
    lower: float
    width_pct: float
    width_state: str
    price_position: str


@dataclass(frozen=True)
class ClassicPivot:
    period_date: object
    pivot: float
    resistance_1: float
    support_1: float


@dataclass(frozen=True)
class SessionContext:
    observed_at: datetime
    active_windows: tuple[str, ...]
    notes: tuple[str, ...]


def bollinger_context(candles: pd.DataFrame, length: int = 20, deviations: float = 2.0) -> BollingerContext | None:
    """Hitung Bollinger dari close; status lebar band dibanding median historis pendek."""
    if candles.empty or "close" not in candles.columns or len(candles) < length + 5:
        return None
    close = candles["close"].astype(float)
    middle = close.rolling(length, min_periods=length).mean()
    std = close.rolling(length, min_periods=length).std(ddof=0)
    upper, lower = middle + deviations * std, middle - deviations * std
    width = (upper - lower).div(middle.replace(0, pd.NA)) * 100
    current_middle, current_upper, current_lower = float(middle.iloc[-1]), float(upper.iloc[-1]), float(lower.iloc[-1])
    if pd.isna(current_middle) or pd.isna(current_upper) or pd.isna(current_lower):
        return None
    current_width = float(width.iloc[-1])
    reference_width = float(width.dropna().tail(length).median())
    if reference_width and current_width < reference_width * 0.75:
        width_state = "RENTANG MENYEMPIT"
    elif reference_width and current_width > reference_width * 1.25:
        width_state = "RENTANG MELEBAR"
    else:
        width_state = "RENTANG RELATIF STABIL"
    price = float(close.iloc[-1])
    if price > current_upper:
        position = "close berada di atas band atas"
    elif price < current_lower:
        position = "close berada di bawah band bawah"
    elif price >= current_middle:
        position = "close berada di antara garis tengah dan band atas"
    else:
        position = "close berada di antara band bawah dan garis tengah"
    return BollingerContext(current_middle, current_upper, current_lower, current_width, width_state, position)


def classic_pivot_from_completed_day(candles: pd.DataFrame) -> ClassicPivot | None:
    """Hitung pivot Classic dari hari kalender sebelum hari candle terakhir."""
    required = {"high", "low", "close"}
    if candles.empty or not required.issubset(candles.columns) or not isinstance(candles.index, pd.DatetimeIndex):
        return None
    normalized = candles.copy()
    if normalized.index.tz is None:
        normalized.index = normalized.index.tz_localize("UTC")
    dates = pd.Index(normalized.index.date).unique()
    if len(dates) < 2:
        return None
    prior_date = dates[-2]
    period = normalized[pd.Index(normalized.index.date) == prior_date]
    if period.empty:
        return None
    high, low, close = float(period["high"].max()), float(period["low"].min()), float(period["close"].iloc[-1])
    pivot = (high + low + close) / 3
    return ClassicPivot(prior_date, pivot, 2 * pivot - low, 2 * pivot - high)


def session_context(observed_at: datetime) -> SessionContext:
    """Tandai jendela kota berdasarkan timestamp candle dan zona waktu IANA."""
    observed = observed_at.astimezone(ZoneInfo("UTC"))
    if observed.weekday() >= 5:
        return SessionContext(observed, (), ("timestamp berada pada akhir pekan; jadwal instrumen dapat berbeda dari pasar FX utama",))
    windows = (
        ("Tokyo", ZoneInfo("Asia/Tokyo"), 9, 18),
        ("London", ZoneInfo("Europe/London"), 8, 17),
        ("New York", ZoneInfo("America/New_York"), 8, 17),
    )
    active: list[str] = []
    for label, zone, start_hour, end_hour in windows:
        local = observed.astimezone(zone)
        if start_hour <= local.hour < end_hour:
            active.append(label)
    notes = (
        "jendela dihitung dari waktu candle, bukan jam perangkat pengguna",
        "zona London dan New York menyesuaikan daylight-saving melalui timezone IANA",
    )
    return SessionContext(observed, tuple(active), notes)


def _fmt(value: float) -> str:
    return f"{value:,.5f}" if abs(value) < 20 else f"{value:,.2f}"


def market_context_section(snapshot: MarketSnapshot) -> str:
    """Format konteks pelengkap yang tetap ringkas dan tidak memberi instruksi personal."""
    bands = bollinger_context(snapshot.candles)
    pivot = classic_pivot_from_completed_day(snapshot.candles)
    session = session_context(snapshot.last_candle_at)
    rows: list[str] = []
    if bands:
        rows.append(
            f"Bollinger(20,2): **{bands.width_state}** dengan lebar **{bands.width_pct:.2f}%**; {bands.price_position}. "
            f"Band bawah/tengah/atas: **{_fmt(bands.lower)} / {_fmt(bands.middle)} / {_fmt(bands.upper)}**."
        )
    else:
        rows.append("Bollinger belum dihitung karena jumlah close candle belum memadai.")
    if pivot:
        rows.append(
            f"Pivot Classic dari periode selesai **{pivot.period_date}**: PP **{_fmt(pivot.pivot)}**, R1 **{_fmt(pivot.resistance_1)}**, S1 **{_fmt(pivot.support_1)}**."
        )
    else:
        rows.append("Pivot periode selesai belum tersedia pada jendela candle ini.")
    if session.active_windows:
        rows.append(f"Timestamp candle berada pada jendela kota: **{' + '.join(session.active_windows)}**.")
    else:
        rows.append("Timestamp candle tidak berada pada jendela Tokyo, London, atau New York yang dipetakan.")
    rows.append("Konteks ini tidak menentukan peluang entry dan perlu dibaca bersama struktur harga, spread, serta kalender agenda.")
    return "**KONTEKS VOLATILITAS & WAKTU**\n\n" + " ".join(rows)
