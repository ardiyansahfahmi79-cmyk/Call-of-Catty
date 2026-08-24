"""Harness penelitian historis AMI yang terpisah dari respons chat.

Filosofi berkas ini: evaluasi hanya memakai informasi yang tersedia pada titik
observasi, target berhenti sebelum censor gap, dan tidak menghasilkan signal
eksekusi. Hasilnya adalah statistik penelitian untuk screen yang didefinisikan
secara eksplisit, bukan angka akurasi pasar atau janji kinerja masa depan.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class EvaluationSplit:
    name: str
    count: int
    favorable_count: int
    unfavorable_count: int
    median_return_pct: float
    mean_return_pct: float


@dataclass(frozen=True)
class CausalScreenEvaluation:
    screen_name: str
    horizon_candles: int
    censor_gap_hours: int
    cutoff_at: object
    observations: pd.DataFrame
    train: EvaluationSplit
    validation: EvaluationSplit
    test: EvaluationSplit


def _rsi(close: pd.Series, length: int = 14) -> pd.Series:
    changes = close.diff()
    gains = changes.clip(lower=0).ewm(alpha=1 / length, adjust=False).mean()
    losses = (-changes.clip(upper=0)).ewm(alpha=1 / length, adjust=False).mean()
    ratio = gains / losses.mask(losses == 0)
    rsi = 100 - (100 / (1 + ratio))
    rsi = rsi.mask((losses == 0) & (gains > 0), 100.0)
    rsi = rsi.mask((gains == 0) & (losses > 0), 0.0)
    return rsi.fillna(50.0)


def _split(name: str, values: pd.DataFrame) -> EvaluationSplit:
    returns = values["favorable_return_pct"].astype(float) if not values.empty else pd.Series(dtype="float64")
    return EvaluationSplit(
        name=name,
        count=int(returns.count()),
        favorable_count=int((returns > 0).sum()),
        unfavorable_count=int((returns < 0).sum()),
        median_return_pct=float(returns.median()) if not returns.empty else 0.0,
        mean_return_pct=float(returns.mean()) if not returns.empty else 0.0,
    )


def evaluate_ma_structure_screen(
    candles: pd.DataFrame,
    horizon_candles: int = 3,
    censor_gap_hours: int = 24,
) -> CausalScreenEvaluation | None:
    """Evaluasi deskriptif screen MA 50/200 + RSI dengan urutan waktu ketat.

    Pada titik t, screen memakai close dan indikator hingga t saja. Return target
    dihitung t→t+horizon dan hanya diterima jika selesai sebelum cutoff. Tidak ada
    optimasi parameter, fitting model, atau pemilihan screen berdasar hasil test.
    """
    required = {"close"}
    if candles.empty or not required.issubset(candles.columns) or len(candles) < 320 or horizon_candles < 1:
        return None
    if not isinstance(candles.index, pd.DatetimeIndex):
        return None
    data = candles[["close"]].copy()
    if data.index.tz is None:
        data.index = data.index.tz_localize("UTC")
    close = data["close"].astype(float)
    ma50 = close.rolling(50, min_periods=50).mean()
    ma200 = close.rolling(200, min_periods=200).mean()
    rsi = _rsi(close)
    cutoff_at = data.index[-1] - pd.Timedelta(hours=censor_gap_hours)
    observations: list[dict[str, object]] = []
    for position in range(200, len(data) - horizon_candles):
        target_at = data.index[position + horizon_candles]
        if target_at > cutoff_at:
            continue
        price, fast, slow, momentum = float(close.iloc[position]), float(ma50.iloc[position]), float(ma200.iloc[position]), float(rsi.iloc[position])
        if not price or pd.isna(fast) or pd.isna(slow):
            continue
        direction: str | None = None
        if price > fast > slow and momentum >= 52:
            direction = "bullish"
        elif price < fast < slow and momentum <= 48:
            direction = "bearish"
        if direction is None:
            continue
        raw_return = (float(close.iloc[position + horizon_candles]) / price - 1) * 100
        favorable_return = raw_return if direction == "bullish" else -raw_return
        observations.append({
            "observed_at": data.index[position],
            "target_at": target_at,
            "direction": direction,
            "raw_return_pct": raw_return,
            "favorable_return_pct": favorable_return,
        })
    frame = pd.DataFrame(observations)
    if len(frame) < 30:
        return None
    train_end = int(len(frame) * 0.6)
    validation_end = int(len(frame) * 0.8)
    train, validation, test = frame.iloc[:train_end], frame.iloc[train_end:validation_end], frame.iloc[validation_end:]
    if min(len(train), len(validation), len(test)) < 5:
        return None
    return CausalScreenEvaluation(
        screen_name="MA50_MA200_RSI_CAUSAL",
        horizon_candles=horizon_candles,
        censor_gap_hours=censor_gap_hours,
        cutoff_at=cutoff_at,
        observations=frame,
        train=_split("train", train),
        validation=_split("validation", validation),
        test=_split("test", test),
    )


def evaluation_report(evaluation: CausalScreenEvaluation | None) -> str:
    """Buat laporan riset yang melarang pembacaan sebagai akurasi atau rekomendasi."""
    if not evaluation:
        return (
            "EVALUASI BELUM MEMADAI: candle atau observasi screen belum cukup untuk split temporal yang layak. "
            "AMI tidak akan menghitung hit rate atau akurasi dari sampel yang terlalu kecil."
        )
    rows = []
    for split in (evaluation.train, evaluation.validation, evaluation.test):
        rows.append(
            f"{split.name}: n={split.count}; favorable/tidak favorable={split.favorable_count}/{split.unfavorable_count}; "
            f"median={split.median_return_pct:+.4f}%; rerata={split.mean_return_pct:+.4f}%"
        )
    return (
        f"EVALUASI RISET {evaluation.screen_name}: horizon {evaluation.horizon_candles} candle; "
        f"cutoff {evaluation.cutoff_at}; censor gap {evaluation.censor_gap_hours} jam. "
        + " | ".join(rows)
        + ". Statistik ini mendeskripsikan screen pada data historis dan bukan prediksi harga, sinyal eksekusi, atau jaminan hasil."
    )
