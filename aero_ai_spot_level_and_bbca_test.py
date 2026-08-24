"""Regresi level XAUUSD spot per timeframe, fallback BBCA W1, dan notice DynamiHatch."""

from __future__ import annotations

from pathlib import Path

from market_chat import _spot_entry_scenario, build_reply
from market_data import fetch_market_snapshot, instrument_from_code


def run() -> None:
    data = {"price": 4700.0, "atr14": 10.0, "bias": "BUY"}
    expected = {
        "15m": (4603.91, 4606.85, 4609.79),
        "30m": (4603.91, 4606.85, 4609.79),
        "1h": (4605.87, 4609.79, 4613.70),
        "1d": (4609.79, 4619.57, 4629.36),
    }
    for interval, targets in expected.items():
        reply = _spot_entry_scenario(data, 4600.0, interval)
        assert f"ATR(14) {interval.upper().replace('15M', 'M15').replace('30M', 'M30').replace('1H', 'H1').replace('1D', 'D1')}" in reply, reply
        for target in targets:
            assert f"{target:,.2f}" in reply, reply

    xau = instrument_from_code("XAUUSD")
    assert xau is not None
    for interval in ("15m", "30m"):
        snapshot = fetch_market_snapshot(xau, interval)
        assert snapshot.reference_spot_price is not None
        reply = build_reply(f"Tentukan entry XAUUSD pada {interval}", snapshot, [])
        label = "M15" if interval == "15m" else "M30"
        assert "SKENARIO LEVEL" in reply and all(marker in reply for marker in ("Zona Entry", "Invalidasi / SL observasi", "TP1", "TP2", "TP3")) and f"ATR(14) {label}" in reply, reply

    bbca = instrument_from_code("BBCA")
    assert bbca is not None
    bbca_snapshot = fetch_market_snapshot(bbca, "1wk")
    assert len(bbca_snapshot.candles) >= 55
    assert bbca_snapshot.interval == "1wk"

    app_source = Path("streamlit_app.py").read_text(encoding="utf-8")
    assert "DynamiHatch" in app_source
    assert "masih dalam tahap pengembangan" in app_source
    print(f"spot_level_bbca_ok=bbca_candles:{len(bbca_snapshot.candles)} xau_intervals:M15,M30 dynami:yes")


if __name__ == "__main__":
    run()
