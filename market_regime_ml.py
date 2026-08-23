"""Klasifikasi regime pasar lokal Aero AI berbasis scikit-learn.

Modul ini mengklasifikasikan keadaan candle historis yang telah tersedia;
bukan memprediksi harga berikutnya, memberi instruksi transaksi, atau memuat
model dari sumber eksternal. Setiap inferensi melatih baseline lokal kecil dari
candle snapshot yang sama dan menyimpan provenance evaluasinya di memori.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, sqrt

import pandas as pd

from market_data import MarketSnapshot


MODEL_VERSION = "regime-rf-v1"
FEATURE_COLUMNS = (
    "return_1",
    "return_5",
    "distance_ma20",
    "distance_ma50",
    "distance_ma200",
    "ma50_slope_5",
    "adx14",
    "atr_pct",
    "volatility20",
    "range_position20",
    "relative_volume20",
)


@dataclass(frozen=True)
class MLRegimeAssessment:
    """Hasil model klasifikasi keadaan yang selalu menyertakan batas evaluasi."""

    state: str
    regime_label: str | None
    confidence: float | None
    agreement: str
    model_version: str
    dataset_id: str | None
    train_rows: int
    test_rows: int
    balanced_accuracy: float | None
    censor_gap_candles: int
    training_end_at: object | None
    notes: tuple[str, ...]


def _adx_series(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
    """Hitung ADX causal dari candle yang tersedia hingga setiap titik waktu."""
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(0.0, index=high.index).where(~((up_move > down_move) & (up_move > 0)), up_move)
    minus_dm = pd.Series(0.0, index=high.index).where(~((down_move > up_move) & (down_move > 0)), down_move)
    previous_close = close.shift(1)
    true_range = pd.concat([high - low, (high - previous_close).abs(), (low - previous_close).abs()], axis=1).max(axis=1)
    atr = true_range.ewm(alpha=1 / length, adjust=False).mean().replace(0, pd.NA)
    plus_di = 100 * plus_dm.ewm(alpha=1 / length, adjust=False).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1 / length, adjust=False).mean() / atr
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, pd.NA)).fillna(0.0)
    return dx.ewm(alpha=1 / length, adjust=False).mean().fillna(0.0)


def _censor_gap_candles(interval: str) -> int:
    """Menjaga sedikitnya satu hari observasi terakhir di luar data pengembangan."""
    if interval == "15m":
        return 96
    if interval == "30m":
        return 48
    if interval.endswith("h"):
        try:
            return max(1, ceil(24 / int(interval[:-1])))
        except ValueError:
            return 24
    return 1


def _feature_dataset(snapshot: MarketSnapshot) -> pd.DataFrame:
    """Membentuk fitur dan label regime causal, tanpa harga atau candle masa depan."""
    candles = snapshot.candles.copy()
    close = pd.to_numeric(candles["close"], errors="coerce")
    high = pd.to_numeric(candles["high"], errors="coerce")
    low = pd.to_numeric(candles["low"], errors="coerce")
    volume = pd.to_numeric(candles.get("volume", pd.Series(0.0, index=candles.index)), errors="coerce").fillna(0.0)

    ma20 = close.rolling(20, min_periods=20).mean()
    ma50 = close.rolling(50, min_periods=50).mean()
    ma200 = close.rolling(200, min_periods=200).mean()
    previous_close = close.shift(1)
    true_range = pd.concat([high - low, (high - previous_close).abs(), (low - previous_close).abs()], axis=1).max(axis=1)
    atr14 = true_range.rolling(14, min_periods=14).mean()
    volatility20 = close.pct_change().rolling(20, min_periods=20).std() * sqrt(252) * 100
    adx14 = _adx_series(high, low, close)
    high20 = high.rolling(20, min_periods=20).max()
    low20 = low.rolling(20, min_periods=20).min()
    volume_mean20 = volume.rolling(20, min_periods=20).mean().replace(0, pd.NA)
    relative_volume20 = (volume / volume_mean20).fillna(0.0)
    atr_pct = (atr14 / close.replace(0, pd.NA) * 100).abs()

    features = pd.DataFrame(
        {
            "return_1": close.pct_change(1) * 100,
            "return_5": close.pct_change(5) * 100,
            "distance_ma20": (close / ma20.replace(0, pd.NA) - 1) * 100,
            "distance_ma50": (close / ma50.replace(0, pd.NA) - 1) * 100,
            "distance_ma200": (close / ma200.replace(0, pd.NA) - 1) * 100,
            "ma50_slope_5": ma50.pct_change(5) * 100,
            "adx14": adx14,
            "atr_pct": atr_pct,
            "volatility20": volatility20,
            "range_position20": (close - low20) / (high20 - low20).replace(0, pd.NA),
            "relative_volume20": relative_volume20,
        },
        index=candles.index,
    )

    volatility_reference = volatility20.rolling(120, min_periods=80).median()
    atr_reference = atr_pct.rolling(120, min_periods=80).median()
    high_volatility = (volatility20 >= volatility_reference * 1.5) | (atr_pct >= atr_reference * 1.5)
    trend_bullish = (close > ma50) & (ma50 > ma200) & (adx14 >= 20)
    trend_bearish = (close < ma50) & (ma50 < ma200) & (adx14 >= 20)
    range_market = adx14 < 18
    target = pd.Series("TRANSISI", index=candles.index, dtype="object")
    target = target.mask(range_market, "RANGE")
    target = target.mask(trend_bearish, "TREND_BEARISH")
    target = target.mask(trend_bullish, "TREND_BULLISH")
    target = target.mask(high_volatility, "HIGH_VOLATILITY")
    features["target"] = target
    return features.dropna(subset=FEATURE_COLUMNS)


def _baseline_bucket(label: str) -> str:
    if "BULLISH" in label:
        return "TREND_BULLISH"
    if "BEARISH" in label:
        return "TREND_BEARISH"
    if "RANGE" in label:
        return "RANGE"
    return "TRANSISI"


def classify_ml_regime(snapshot: MarketSnapshot, baseline_label: str, structure_score: int) -> MLRegimeAssessment:
    """Latih baseline lokal dengan walk-forward CV lalu klasifikasikan candle terakhir.

    Model hanya melihat candle sampai batas sensor untuk pembelajaran. Candle
    terakhir dipakai sebagai observasi inferensi, bukan target price masa depan.
    """
    if structure_score < 75:
        return MLRegimeAssessment(
            state="ABSTAIN",
            regime_label=None,
            confidence=None,
            agreement="TIDAK DINILAI",
            model_version=MODEL_VERSION,
            dataset_id=None,
            train_rows=0,
            test_rows=0,
            balanced_accuracy=None,
            censor_gap_candles=_censor_gap_candles(snapshot.interval),
            training_end_at=None,
            notes=("Market Structure Quality Gate belum memenuhi ambang untuk klasifikasi ML.",),
        )

    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import TimeSeriesSplit
        from sklearn.pipeline import Pipeline
    except ImportError:
        return MLRegimeAssessment(
            state="TIDAK TERSEDIA",
            regime_label=None,
            confidence=None,
            agreement="TIDAK DINILAI",
            model_version=MODEL_VERSION,
            dataset_id=None,
            train_rows=0,
            test_rows=0,
            balanced_accuracy=None,
            censor_gap_candles=_censor_gap_candles(snapshot.interval),
            training_end_at=None,
            notes=("scikit-learn belum tersedia pada environment aplikasi.",),
        )

    dataset = _feature_dataset(snapshot)
    gap = _censor_gap_candles(snapshot.interval)
    if len(dataset) <= gap + 240:
        return MLRegimeAssessment(
            state="DATA BELUM CUKUP",
            regime_label=None,
            confidence=None,
            agreement="TIDAK DINILAI",
            model_version=MODEL_VERSION,
            dataset_id=None,
            train_rows=max(0, len(dataset) - gap),
            test_rows=0,
            balanced_accuracy=None,
            censor_gap_candles=gap,
            training_end_at=None,
            notes=("Candle historis setelah feature warm-up dan censor gap belum cukup untuk validasi temporal.",),
        )

    development = dataset.iloc[:-gap] if gap else dataset
    inference = dataset.iloc[[-1]]
    if len(development) < 240 or development["target"].nunique() < 2:
        return MLRegimeAssessment(
            state="DATA BELUM CUKUP",
            regime_label=None,
            confidence=None,
            agreement="TIDAK DINILAI",
            model_version=MODEL_VERSION,
            dataset_id=None,
            train_rows=len(development),
            test_rows=0,
            balanced_accuracy=None,
            censor_gap_candles=gap,
            training_end_at=development.index[-1] if not development.empty else None,
            notes=("Dataset regime tidak memiliki jumlah observasi atau variasi kelas yang memadai untuk baseline ML.",),
        )

    test_size = max(24, len(development) // 10)
    required_rows = 3 * test_size + gap + 60
    if len(development) < required_rows:
        return MLRegimeAssessment(
            state="DATA BELUM CUKUP",
            regime_label=None,
            confidence=None,
            agreement="TIDAK DINILAI",
            model_version=MODEL_VERSION,
            dataset_id=None,
            train_rows=len(development),
            test_rows=0,
            balanced_accuracy=None,
            censor_gap_candles=gap,
            training_end_at=development.index[-1],
            notes=("Dataset belum cukup untuk tiga fold validasi temporal dengan censor gap.",),
        )

    def make_pipeline() -> Pipeline:
        return Pipeline(
            [
                (
                    "classifier",
                    RandomForestClassifier(
                        n_estimators=80,
                        max_depth=8,
                        min_samples_leaf=4,
                        class_weight="balanced_subsample",
                        random_state=42,
                        n_jobs=1,
                    ),
                )
            ]
        )

    features, target = development.loc[:, FEATURE_COLUMNS], development["target"]
    splitter = TimeSeriesSplit(n_splits=3, test_size=test_size, gap=gap)
    scores: list[float] = []
    tested_rows = 0
    for train_index, test_index in splitter.split(features):
        train_x, train_y = features.iloc[train_index], target.iloc[train_index]
        test_x, test_y = features.iloc[test_index], target.iloc[test_index]
        if train_y.nunique() < 2 or test_y.empty:
            continue
        fold_model = make_pipeline()
        fold_model.fit(train_x, train_y)
        predicted_fold = pd.Series(fold_model.predict(test_x), index=test_y.index)
        recalls = [
            float((predicted_fold.loc[test_y == label] == label).mean())
            for label in sorted(test_y.unique())
        ]
        scores.append(sum(recalls) / len(recalls))
        tested_rows += len(test_index)
    if not scores:
        return MLRegimeAssessment(
            state="DATA BELUM CUKUP",
            regime_label=None,
            confidence=None,
            agreement="TIDAK DINILAI",
            model_version=MODEL_VERSION,
            dataset_id=None,
            train_rows=len(development),
            test_rows=tested_rows,
            balanced_accuracy=None,
            censor_gap_candles=gap,
            training_end_at=development.index[-1],
            notes=("Tidak ada fold temporal yang memiliki variasi kelas cukup untuk validasi model.",),
        )

    model = make_pipeline()
    model.fit(features, target)
    predicted = str(model.predict(inference.loc[:, FEATURE_COLUMNS])[0])
    classifier = model.named_steps["classifier"]
    probabilities = model.predict_proba(inference.loc[:, FEATURE_COLUMNS])[0]
    confidence = float(max(probabilities))
    baseline = _baseline_bucket(baseline_label)
    agreement = "SEPAKAT" if predicted == baseline else "BERBEDA"
    dataset_id = (
        f"{snapshot.instrument.code}-{snapshot.interval}-{MODEL_VERSION}-"
        f"{development.index[0].strftime('%Y%m%d')}-{development.index[-1].strftime('%Y%m%d')}"
    )
    notes = (
        "Kelas dibentuk dari fitur candle yang tersedia pada setiap waktu, bukan return atau harga masa depan.",
        "Balanced accuracy adalah rata-rata tiga fold TimeSeriesSplit dan mengukur kecocokan terhadap label regime kausal, bukan akurasi prediksi harga.",
        "Confidence adalah proporsi suara classifier untuk kelas regime; bukan probabilitas harga bergerak atau peluang profit.",
        "Model read-only ini dilatih ulang dari snapshot lokal dan tidak menyimpan atau menerima data akun pengguna.",
    )
    return MLRegimeAssessment(
        state="TERSEDIA",
        regime_label=predicted,
        confidence=confidence,
        agreement=agreement,
        model_version=MODEL_VERSION,
        dataset_id=dataset_id,
        train_rows=len(development),
        test_rows=tested_rows,
        balanced_accuracy=sum(scores) / len(scores),
        censor_gap_candles=gap,
        training_end_at=development.index[-1],
        notes=notes,
    )
