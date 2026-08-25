"""Aturan deterministik untuk proposal scalping akun demo.

Strategi ini hanya menghasilkan kondisi teknis atau alasan abstain. Ia tidak
mengirim order, tidak menjanjikan hasil, dan harus melewati guard bridge demo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class ScalpingPolicy:
    allowed_symbols: tuple[str, ...] = ("XAUUSD",)
    max_volume: float = 0.01
    max_positions: int = 1
    max_spread_points: float = 50.0
    max_daily_loss_percent: float = 0.50
    heartbeat_ttl_seconds: int = 55
    proposal_ttl_seconds: int = 30
    cooldown_seconds: int = 60


@dataclass(frozen=True)
class ScalpingSignal:
    decision: str
    reason: str
    atr: float | None = None


def ema(values: Iterable[float], period: int) -> float:
    series = [float(value) for value in values]
    if len(series) < period:
        raise ValueError("Data candle belum cukup untuk EMA.")
    multiplier = 2 / (period + 1)
    current = sum(series[:period]) / period
    for value in series[period:]:
        current = (value - current) * multiplier + current
    return current


def atr(bars: Iterable[Mapping[str, float]], period: int = 14) -> float:
    rows = list(bars)
    if len(rows) < period + 1:
        raise ValueError("Data candle belum cukup untuk ATR.")
    ranges: list[float] = []
    for index in range(1, len(rows)):
        high, low = float(rows[index]["high"]), float(rows[index]["low"])
        previous_close = float(rows[index - 1]["close"])
        ranges.append(max(high - low, abs(high - previous_close), abs(low - previous_close)))
    return sum(ranges[-period:]) / period


def evaluate_m1_scalping_signal(bars: Iterable[Mapping[str, float]]) -> ScalpingSignal:
    """Memberi sinyal teknis M1 sederhana atau abstain bila struktur belum sehat.

    Syarat: EMA 9/21 searah, candle terakhir menutup melampaui EMA cepat, dan
    jarak EMA lebih besar dari 10% ATR. Ini filter, bukan prediksi harga.
    """
    rows = list(bars)
    if len(rows) < 30:
        return ScalpingSignal("NO_TRADE", "Candle M1 belum cukup untuk validasi struktur.")
    closes = [float(row["close"]) for row in rows]
    try:
        fast, slow, current_atr = ema(closes, 9), ema(closes, 21), atr(rows)
    except (KeyError, TypeError, ValueError):
        return ScalpingSignal("NO_TRADE", "Data candle tidak lengkap untuk indikator scalping.")
    last_close = closes[-1]
    if current_atr <= 0:
        return ScalpingSignal("NO_TRADE", "ATR tidak valid; tidak membuat proposal.")
    separation = abs(fast - slow)
    if separation < current_atr * 0.10:
        return ScalpingSignal("NO_TRADE", "EMA terlalu rapat dibanding ATR; kondisi ranging.", current_atr)
    if fast > slow and last_close > fast:
        return ScalpingSignal("BUY", "EMA 9 di atas EMA 21 dan penutupan terakhir berada di atas EMA cepat.", current_atr)
    if fast < slow and last_close < fast:
        return ScalpingSignal("SELL", "EMA 9 di bawah EMA 21 dan penutupan terakhir berada di bawah EMA cepat.", current_atr)
    return ScalpingSignal("NO_TRADE", "Struktur EMA dan penutupan candle belum searah.", current_atr)


def entry_block_reason(
    *,
    demo_verified: bool,
    heartbeat_fresh: bool,
    kill_switch_active: bool,
    symbol: str,
    volume: float,
    open_positions: int,
    spread_points: float,
    daily_loss_percent: float,
    policy: ScalpingPolicy,
) -> str | None:
    """Mengembalikan alasan blokir pertama; fail-closed jika data tidak layak."""
    if not demo_verified:
        return "Bridge hanya menerima akun demo MT5 yang terverifikasi."
    if not heartbeat_fresh:
        return "Heartbeat panel telah kedaluwarsa."
    if kill_switch_active:
        return "Kill switch aktif; proposal order diblokir."
    if symbol not in policy.allowed_symbols:
        return f"{symbol} tidak ada di whitelist scalping demo."
    if volume <= 0 or volume > policy.max_volume:
        return f"Lot harus lebih dari 0 dan tidak melebihi {policy.max_volume:.2f}."
    if open_positions >= policy.max_positions:
        return f"Batas {policy.max_positions} posisi terbuka telah tercapai."
    if spread_points < 0 or spread_points > policy.max_spread_points:
        return "Spread melewati batas keamanan atau data spread tidak valid."
    if daily_loss_percent < 0 or daily_loss_percent >= policy.max_daily_loss_percent:
        return "Batas kerugian harian scalping telah tercapai."
    return None
