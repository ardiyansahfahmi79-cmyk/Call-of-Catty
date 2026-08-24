"""Regresi deterministik untuk volatilitas, pivot, dan sesi AMI tanpa sumber jaringan."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from market_context import bollinger_context, classic_pivot_from_completed_day, session_context


def _fixture() -> pd.DataFrame:
    index = pd.date_range("2025-01-06", periods=48, freq="h", tz="UTC")
    close = [100 + ((position % 9) - 4) * 0.4 + position * 0.08 for position in range(len(index))]
    return pd.DataFrame({
        "open": [value - 0.1 for value in close],
        "high": [value + 0.35 for value in close],
        "low": [value - 0.45 for value in close],
        "close": close,
    }, index=index)


def run() -> None:
    candles = _fixture()
    bands = bollinger_context(candles)
    assert bands is not None and bands.upper > bands.middle > bands.lower, bands
    pivot = classic_pivot_from_completed_day(candles)
    assert pivot is not None and pivot.resistance_1 > pivot.pivot > pivot.support_1, pivot
    london = session_context(datetime(2025, 1, 6, 12, 0, tzinfo=timezone.utc))
    assert "London" in london.active_windows, london
    weekend = session_context(datetime(2025, 1, 11, 12, 0, tzinfo=timezone.utc))
    assert not weekend.active_windows and weekend.notes, weekend
    print(f"market_context_ok=bb:{bands.width_state} pivot:{pivot.period_date} london:{'+'.join(london.active_windows)}")


if __name__ == "__main__":
    run()
