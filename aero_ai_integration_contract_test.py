"""Kontrak integrasi respons dan grafik AMI; seluruh fixture bersifat lokal untuk regresi."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from market_chat import build_reply, build_unknown_input_reply
from market_data import MarketSnapshot, calculate_indicators, instrument_from_code


def _snapshot() -> MarketSnapshot:
    index = pd.date_range("2025-02-03", periods=280, freq="h", tz="UTC")
    close = [1.08 + point * 0.00008 + ((point % 7) - 3) * 0.00001 for point in range(len(index))]
    candles = pd.DataFrame({
        "open": [value - 0.00002 for value in close],
        "high": [value + 0.00008 for value in close],
        "low": [value - 0.00009 for value in close],
        "close": close,
        "volume": [0.0] * len(close),
    }, index=index)
    instrument = instrument_from_code("EURUSD")
    assert instrument is not None
    return MarketSnapshot(
        instrument=instrument,
        candles=candles,
        indicators=calculate_indicators(candles),
        fetched_at=datetime.now(timezone.utc),
        last_candle_at=index[-1].to_pydatetime(),
        source="fixture lokal untuk regresi",
        warning="fixture lokal",
        interval="1h",
    )


def run() -> None:
    reply = build_reply("Tentukan Entry, SL, TP1 TP2 TP3 dan Risk untuk EURUSD pada H1", _snapshot())
    for expected in ("SKENARIO LEVEL TEKNIKAL", "STRUKTUR HARGA", "KONTEKS VOLATILITAS & WAKTU"):
        assert expected in reply, expected
    for prohibited in ("pipeline", "python data engine", "traceable context", "yfinance", "yahoo finance", "gc=f"):
        assert prohibited not in reply.casefold(), prohibited
    clarification = build_unknown_input_reply("tentukan risk reward")
    assert "sebutkan instrumen" in clarification.casefold(), clarification
    app_source = Path("streamlit_app.py").read_text(encoding="utf-8")
    for expected in ('"staticPlot": True', '"displayModeBar": False', '"scrollZoom": False', "pointer-events:none"):
        assert expected in app_source, expected
    print(f"integration_contract_ok=reply_chars:{len(reply)} static_chart:yes")


if __name__ == "__main__":
    run()
