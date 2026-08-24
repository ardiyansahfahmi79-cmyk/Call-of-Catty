"""Kontrak ATR per timeframe untuk seluruh instrumen AMI: 58 instrumen × 4 timeframe."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from market_chat import build_reply
from market_data import INSTRUMENTS, MarketSnapshot, calculate_indicators


def _snapshot(instrument, interval: str) -> MarketSnapshot:
    index = pd.date_range("2026-08-01", periods=280, freq="h", tz="UTC")
    base = 100.0 if instrument.code not in {"XAUUSD", "XAGUSD"} else 4700.0
    close = [base + number * (0.08 if base == 100.0 else 0.65) for number in range(len(index))]
    candles = pd.DataFrame(
        {"open": [value - 0.2 for value in close], "high": [value + 0.7 for value in close], "low": [value - 0.6 for value in close], "close": close, "volume": [100.0] * len(index)},
        index=index,
    )
    indicators = calculate_indicators(candles)
    spot = 4647.0 if instrument.code == "XAUUSD" else None
    return MarketSnapshot(
        instrument, candles, indicators, datetime.now(timezone.utc), index[-1].to_pydatetime(), "fixture", "fixture", interval,
        spot, datetime.now(timezone.utc) if spot else None, spot - 0.25 if spot else None, spot + 0.25 if spot else None, datetime.now(timezone.utc) if spot else None,
    )


def run() -> None:
    intervals = (("15m", "M15"), ("30m", "M30"), ("1h", "H1"), ("1d", "D1"))
    count = 0
    for instrument in INSTRUMENTS:
        for interval, label in intervals:
            reply = build_reply(f"Tentukan entry {instrument.code} pada {label}", _snapshot(instrument, interval), [])
            assert "TP1, TP2, dan TP3" in reply, (instrument.code, interval, reply)
            assert f"ATR(14) {label}" in reply, (instrument.code, interval, reply)
            assert "Catatan risiko" in reply, (instrument.code, interval)
            count += 1
    assert count == len(INSTRUMENTS) * len(intervals) == 232
    print(f"cross_asset_atr_contract_ok=instruments:{len(INSTRUMENTS)} cases:{count}")


if __name__ == "__main__":
    run()
