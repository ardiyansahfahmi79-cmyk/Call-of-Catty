"""Kontrak level profesional, parser struktur harga, dan chart opt-in Aero AI."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from market_chat import build_reply, build_unknown_input_reply, infer_intent
from market_data import INSTRUMENTS, MarketSnapshot, calculate_indicators, detect_instruments
from market_display_policy import chart_requested


def _instrument(code: str):
    return next(item for item in INSTRUMENTS if item.code == code)


def _snapshot(code: str = "XAUUSD") -> MarketSnapshot:
    instrument = _instrument(code)
    index = pd.date_range("2026-08-01", periods=280, freq="h", tz="UTC")
    base = 4700.0 if code == "XAUUSD" else 100.0
    wave = (0.0, 1.4, 2.2, 1.0, 0.1, -1.1, -1.8, -0.7, 0.6, 1.5)
    close = [base + number * (0.11 if code == "XAUUSD" else 0.02) + wave[number % len(wave)] for number in range(len(index))]
    candles = pd.DataFrame(
        {"open": [value - 0.2 for value in close], "high": [value + 0.7 for value in close], "low": [value - 0.6 for value in close], "close": close, "volume": [100.0] * len(index)},
        index=index,
    )
    indicators = calculate_indicators(candles)
    now = datetime.now(timezone.utc)
    spot = 4647.0 if code == "XAUUSD" else None
    return MarketSnapshot(instrument, candles, indicators, now, index[-1].to_pydatetime(), "fixture", "fixture", "1h", spot, now if spot else None)


def run() -> None:
    assert detect_instruments("Area resistance ada di harga berapa?") == []
    assert detect_instruments("Analisa ADAUSD pada H1")[0].code == "ADAUSD"
    assert infer_intent("Tentukan area buy XAUUSD pada H1") == "levels_entry"
    assert infer_intent("Di mana supply dan demand XAUUSD H1") == "levels"

    missing = build_unknown_input_reply("Area resistance ada di harga berapa?")
    assert "Support, Resistance, Supply, atau Demand" in missing
    assert "ADAUSD" not in missing

    reply = build_reply("Tentukan area buy XAUUSD pada H1", _snapshot(), [])
    for marker in ("SKENARIO LEVEL · XAUUSD · H1", "Zona Entry", "Invalidasi / SL observasi", "TP1", "TP2", "TP3", "ATR(14) H1", "SUPPORT / DEMAND", "RESISTANCE / SUPPLY"):
        assert marker in reply, marker
    structure_reply = build_reply("Area resistance dan supply XAUUSD pada H1", _snapshot(), [])
    for marker in ("STRUKTUR HARGA · XAUUSD · 1H", "SUPPORT / DEMAND", "RESISTANCE / SUPPLY"):
        assert marker in structure_reply, marker

    yes_chart = ("buat grafik XAUUSD H1", "tampilkan chart EURUSD", "bandingkan harga XAUUSD dan DXY pada H1")
    no_chart = ("analisa XAUUSD H1", "tentukan area entry XAUUSD H1", "area support XAUUSD H1", "bandingkan XAUUSD dengan DXY")
    assert all(chart_requested(question) for question in yes_chart)
    assert not any(chart_requested(question) for question in no_chart)
    app_source = Path("streamlit_app.py").read_text(encoding="utf-8")
    for marker in ("show_chart=chart_requested(question)", "if show_chart:\n        render_line_chart(snapshot)", "comparison_chart = len(snapshots) > 1 and show_chart"):
        assert marker in app_source, marker
    print("level_structure_display_ok=parser:4 level:9 chart_opt_in:7")


if __name__ == "__main__":
    run()
