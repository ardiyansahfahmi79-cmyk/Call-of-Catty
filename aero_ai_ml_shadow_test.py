"""Audit shadow mode ML AMI; menilai kontrak klasifikasi regime, bukan harga masa depan."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from market_data import MarketSnapshot, fetch_market_snapshot, instrument_from_code
from market_regime_ml import classify_ml_regime


def _weak_snapshot() -> MarketSnapshot:
    instrument = instrument_from_code("EURUSD")
    assert instrument is not None
    index = pd.date_range("2026-01-01", periods=12, freq="h", tz="UTC")
    candles = pd.DataFrame({"open": [1.0] * 12, "high": [1.1] * 12, "low": [0.9] * 12, "close": [1.0] * 12, "volume": [0.0] * 12}, index=index)
    return MarketSnapshot(instrument, candles, {}, datetime.now(timezone.utc), index[-1].to_pydatetime(), "fixture", "fixture", "1h")


def run() -> None:
    weak = classify_ml_regime(_weak_snapshot(), "RANGE / TREN LEMAH", 0)
    assert weak.state == "ABSTAIN" and weak.confidence is None and weak.balanced_accuracy is None, weak
    instrument = instrument_from_code("EURUSD")
    assert instrument is not None
    snapshot = fetch_market_snapshot(instrument, "1h")
    assessment = classify_ml_regime(snapshot, "TRANSISI / KONFLUENSI TERBATAS", 100)
    assert assessment.state in {"TERSEDIA", "DATA BELUM CUKUP"}, assessment
    assert assessment.censor_gap_candles == 24, assessment
    if assessment.state == "TERSEDIA":
        assert assessment.training_end_at is not None and assessment.training_end_at < snapshot.candles.index[-1], assessment
        assert assessment.balanced_accuracy is not None and 0 <= assessment.balanced_accuracy <= 1, assessment
        assert assessment.confidence is not None and 0 <= assessment.confidence <= 1, assessment
    print(f"ml_shadow_ok=weak:{weak.state} live:{assessment.state} gap:{assessment.censor_gap_candles} test_rows:{assessment.test_rows}")


if __name__ == "__main__":
    run()
