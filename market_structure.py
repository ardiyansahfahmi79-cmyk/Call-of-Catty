"""Struktur harga kausal untuk respons AMI.

Filosofi berkas ini: struktur hanya memakai candle yang sudah tertutup. Sebuah
swing diberi label setelah jendela konfirmasi di kanan pivot tersedia; karena
itu modul tidak menjadikan puncak/lembah candle terakhir sebagai fakta yang
sudah diketahui. Semua output adalah konteks riset, bukan prediksi harga atau
instruksi transaksi.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from market_data import MarketSnapshot


Direction = Literal["bullish", "bearish"]


@dataclass(frozen=True)
class ConfirmedSwing:
    """Pivot yang baru sah sesudah sejumlah candle konfirmasi selesai."""

    kind: Literal["high", "low"]
    level: float
    pivot_at: object
    confirmed_at: object


@dataclass(frozen=True)
class FairValueGap:
    """Imbalance tiga candle yang diketahui setelah candle ketiga ditutup."""

    direction: Direction
    lower: float
    upper: float
    formed_at: object


@dataclass(frozen=True)
class FibonacciRange:
    """Level retracement dari dua swing terkonfirmasi, bukan target harga."""

    direction: Direction
    swing_start: float
    swing_end: float
    level_382: float
    level_500: float
    level_618: float
    level_786: float


@dataclass(frozen=True)
class PriceStructure:
    """Hasil pembacaan struktur yang seluruhnya dapat ditelusuri ke OHLC."""

    state: str
    swings: tuple[ConfirmedSwing, ...]
    latest_break: str | None
    latest_break_level: float | None
    latest_fvg: FairValueGap | None
    fibonacci: FibonacciRange | None
    notes: tuple[str, ...]


def _number(series: pd.Series, position: int) -> float:
    return float(series.iloc[position])


def confirmed_swings(candles: pd.DataFrame, window: int = 2) -> tuple[ConfirmedSwing, ...]:
    """Cari swing dengan pivot kiri dan kanan sehingga labelnya bersifat kausal.

    `window=2` berarti pivot pada posisi i baru diketahui pada penutupan candle
    i+2. Candle di akhir data yang belum punya sisi kanan tidak diberi label.
    """
    required = {"high", "low"}
    if candles.empty or not required.issubset(candles.columns) or window < 1:
        return ()
    highs, lows = candles["high"].astype(float), candles["low"].astype(float)
    swings: list[ConfirmedSwing] = []
    for position in range(window, len(candles) - window):
        left_high, right_high = highs.iloc[position - window:position], highs.iloc[position + 1:position + window + 1]
        left_low, right_low = lows.iloc[position - window:position], lows.iloc[position + 1:position + window + 1]
        value_high, value_low = _number(highs, position), _number(lows, position)
        pivot_at, confirmed_at = candles.index[position], candles.index[position + window]
        if value_high > float(left_high.max()) and value_high > float(right_high.max()):
            swings.append(ConfirmedSwing("high", value_high, pivot_at, confirmed_at))
        if value_low < float(left_low.min()) and value_low < float(right_low.min()):
            swings.append(ConfirmedSwing("low", value_low, pivot_at, confirmed_at))
    return tuple(swings)


def _structure_state(swings: tuple[ConfirmedSwing, ...]) -> str:
    highs = [swing.level for swing in swings if swing.kind == "high"]
    lows = [swing.level for swing in swings if swing.kind == "low"]
    if len(highs) < 2 or len(lows) < 2:
        return "STRUKTUR BELUM CUKUP"
    if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
        return "BULLISH"
    if highs[-1] < highs[-2] and lows[-1] < lows[-2]:
        return "BEARISH"
    return "NETRAL / TRANSISI"


def _latest_break(candles: pd.DataFrame, swings: tuple[ConfirmedSwing, ...], state: str) -> tuple[str | None, float | None]:
    if candles.empty or "close" not in candles.columns:
        return None, None
    close = float(candles["close"].iloc[-1])
    latest_high = next((swing for swing in reversed(swings) if swing.kind == "high"), None)
    latest_low = next((swing for swing in reversed(swings) if swing.kind == "low"), None)
    if latest_high and close > latest_high.level:
        label = "PERUBAHAN KARAKTER BULLISH" if state == "BEARISH" else "PENEMBUSAN STRUKTUR BULLISH"
        return label, latest_high.level
    if latest_low and close < latest_low.level:
        label = "PERUBAHAN KARAKTER BEARISH" if state == "BULLISH" else "PENEMBUSAN STRUKTUR BEARISH"
        return label, latest_low.level
    return None, None


def latest_fair_value_gap(candles: pd.DataFrame) -> FairValueGap | None:
    """Temukan FVG terakhir setelah candle ketiga pada pola telah ditutup."""
    required = {"high", "low"}
    if len(candles) < 3 or not required.issubset(candles.columns):
        return None
    highs, lows = candles["high"].astype(float), candles["low"].astype(float)
    latest: FairValueGap | None = None
    for position in range(2, len(candles)):
        if _number(lows, position) > _number(highs, position - 2):
            latest = FairValueGap("bullish", _number(highs, position - 2), _number(lows, position), candles.index[position])
        elif _number(highs, position) < _number(lows, position - 2):
            latest = FairValueGap("bearish", _number(highs, position), _number(lows, position - 2), candles.index[position])
    return latest


def _fibonacci_range(swings: tuple[ConfirmedSwing, ...], state: str) -> FibonacciRange | None:
    if state not in {"BULLISH", "BEARISH"}:
        return None
    ordered = list(swings)
    if state == "BULLISH":
        end = next((swing for swing in reversed(ordered) if swing.kind == "high"), None)
        if not end:
            return None
        start = next((swing for swing in reversed(ordered) if swing.kind == "low" and swing.pivot_at < end.pivot_at), None)
        if not start or end.level <= start.level:
            return None
        distance = end.level - start.level
        return FibonacciRange("bullish", start.level, end.level, end.level - distance * 0.382, end.level - distance * 0.5, end.level - distance * 0.618, end.level - distance * 0.786)
    end = next((swing for swing in reversed(ordered) if swing.kind == "low"), None)
    if not end:
        return None
    start = next((swing for swing in reversed(ordered) if swing.kind == "high" and swing.pivot_at < end.pivot_at), None)
    if not start or start.level <= end.level:
        return None
    distance = start.level - end.level
    return FibonacciRange("bearish", start.level, end.level, end.level + distance * 0.382, end.level + distance * 0.5, end.level + distance * 0.618, end.level + distance * 0.786)


def build_price_structure(candles: pd.DataFrame, window: int = 2) -> PriceStructure:
    """Bangun struktur yang dapat diuji dari OHLC tanpa memakai data masa depan."""
    if candles.empty or not {"open", "high", "low", "close"}.issubset(candles.columns):
        return PriceStructure("DATA OHLC BELUM MEMADAI", (), None, None, None, None, ("kolom OHLC belum lengkap",))
    swings = confirmed_swings(candles, window=window)
    state = _structure_state(swings)
    latest_break, latest_break_level = _latest_break(candles, swings, state)
    notes = [f"{len(swings)} swing telah terkonfirmasi setelah {window} candle"]
    if len(candles) < 2 * window + 3:
        notes.append("jumlah candle masih terbatas untuk struktur yang lebih dalam")
    if latest_break:
        notes.append("penembusan dinilai dari close candle terakhir, bukan wick")
    return PriceStructure(
        state=state,
        swings=swings,
        latest_break=latest_break,
        latest_break_level=latest_break_level,
        latest_fvg=latest_fair_value_gap(candles),
        fibonacci=_fibonacci_range(swings, state),
        notes=tuple(notes),
    )


def _fmt(value: float) -> str:
    return f"{value:,.5f}" if abs(value) < 20 else f"{value:,.2f}"


def price_structure_section(snapshot: MarketSnapshot) -> str:
    """Format struktur harga berorientasi Support/Resistance dan Supply/Demand.

    Tidak ada order-flow atau zona institusional yang dibuat-buat. Label Supply
    dan Demand hanya memakai swing yang sudah terkonfirmasi atau FVG yang
    terdeteksi dari candle selesai. Untuk XAUUSD, level candle ditampilkan pada
    basis spot secara proporsional agar tidak mencampur dua basis harga.
    """
    structure = build_price_structure(snapshot.candles)
    candle_price = float(snapshot.indicators.get("price", 0.0))
    scale = 1.0
    basis_note = ""
    if snapshot.instrument.code == "XAUUSD" and snapshot.reference_spot_price and candle_price > 0:
        scale = float(snapshot.reference_spot_price) / candle_price
        basis_note = " Level struktur diselaraskan secara proporsional ke referensi spot yang tersedia."

    def level(value: float) -> str:
        return _fmt(value * scale)

    title = f"**STRUKTUR HARGA · {snapshot.instrument.code} · {snapshot.interval.upper()}**"
    if structure.state in {"DATA OHLC BELUM MEMADAI", "STRUKTUR BELUM CUKUP"}:
        return (
            f"{title}\n\n"
            "Candle yang tersedia belum cukup untuk mengonfirmasi rangkaian swing high dan swing low. "
            "Aero AI tidak akan memaksakan arah struktur atau level Fibonacci ketika konfirmasi belum ada."
        )
    latest_support = next((swing for swing in reversed(structure.swings) if swing.kind == "low"), None)
    latest_resistance = next((swing for swing in reversed(structure.swings) if swing.kind == "high"), None)
    support_text = (
        f"**Support terkonfirmasi:** **{level(latest_support.level)}** · menjadi referensi Demand struktural, bukan kepastian pantulan."
        if latest_support else "**Support / Demand:** belum ada swing low yang cukup untuk dikonfirmasi."
    )
    resistance_text = (
        f"**Resistance terkonfirmasi:** **{level(latest_resistance.level)}** · menjadi referensi Supply struktural, bukan kepastian penolakan."
        if latest_resistance else "**Resistance / Supply:** belum ada swing high yang cukup untuk dikonfirmasi."
    )
    imbalance_text = "Tidak ada FVG terakhir yang dapat digunakan sebagai zona ketidakseimbangan tambahan."
    if structure.latest_fvg:
        fvg = structure.latest_fvg
        side = "Demand / imbalance bullish" if fvg.direction == "bullish" else "Supply / imbalance bearish"
        imbalance_text = f"**{side}:** **{level(fvg.lower)}–{level(fvg.upper)}**; zona ini perlu respons candle, bukan asumsi harga pasti kembali."

    confirmation = "Belum ada penembusan close candle terakhir terhadap swing terkonfirmasi yang lebih dekat."
    if structure.latest_break and structure.latest_break_level is not None:
        confirmation = f"Close candle terakhir membentuk **{structure.latest_break}** pada level **{level(structure.latest_break_level)}**."
    fib_text = "Fibonacci belum membentuk rentang swing yang cukup jelas."
    if structure.fibonacci:
        fib = structure.fibonacci
        fib_text = (
            f"Fibonacci swing: 38,2% **{level(fib.level_382)}** · 50,0% **{level(fib.level_500)}** · "
            f"61,8% **{level(fib.level_618)}** · 78,6% **{level(fib.level_786)}**."
        )
    return (
        f"{title}\n\n"
        f"**Kondisi swing:** **{structure.state}**. {confirmation}\n\n"
        f"**SUPPORT / DEMAND**\n\n{support_text}\n{imbalance_text}\n\n"
        f"**RESISTANCE / SUPPLY**\n\n{resistance_text}\n\n"
        f"**Konfluensi swing**\n\n{fib_text}{basis_note}\n\n"
        "Area struktur perlu dievaluasi kembali setelah candle baru ditutup dan bukan instruksi transaksi personal."
    )
