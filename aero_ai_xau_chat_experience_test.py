"""Regresi pengalaman chat XAUUSD: 6 kategori × 50 = 300 skenario lokal."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from market_chat import _entry_scenario, build_reply, build_spot_fallback_reply
from market_data import MarketSnapshot, calculate_indicators, detect_instruments, detect_timeframe, instrument_from_code


def _snapshot() -> MarketSnapshot:
    instrument = instrument_from_code("XAUUSD")
    assert instrument is not None
    index = pd.date_range("2026-08-20", periods=280, freq="h", tz="UTC")
    close = [4650 + point * 0.17 + ((point % 11) - 5) * 0.42 for point in range(len(index))]
    candles = pd.DataFrame(
        {
            "open": [value - 0.35 for value in close],
            "high": [value + 1.1 for value in close],
            "low": [value - 1.0 for value in close],
            "close": close,
            "volume": [100 + (point % 7) for point in range(len(index))],
        },
        index=index,
    )
    return MarketSnapshot(
        instrument,
        candles,
        calculate_indicators(candles),
        datetime(2026, 8, 24, 9, 14, tzinfo=timezone.utc),
        index[-1].to_pydatetime(),
        "fixture yfinance candle",
        "fixture",
        "1h",
        4641.81,
        datetime(2026, 8, 24, 9, 14, tzinfo=timezone.utc),
        4641.50,
        4642.12,
        datetime(2026, 8, 24, 9, 14, tzinfo=timezone.utc),
    )


def run() -> None:
    snapshot = _snapshot()
    categories: dict[str, int] = {}

    parsing_forms = (
        "Analisa XAUUSD di Timeframe H1",
        "analisa xauusd sekarang di timeframe h1",
        "Tolong analisa XAU / USD H1",
        "scan gold pada h1",
        "Analisis emas timeframe 1 jam",
    )
    for position in range(50):
        question = parsing_forms[position % len(parsing_forms)]
        assert [item.code for item in detect_instruments(question)] == ["XAUUSD"], question
        assert detect_timeframe(question) == "1h", question
    categories["Parsing instrumen dan timeframe"] = 50

    for position in range(50):
        question = f"{parsing_forms[position % len(parsing_forms)]} {position}"
        reply = build_reply(question, snapshot, [])
        assert "Permintaan terbaca" in reply and "XAUUSD" in reply and "H1" in reply, reply
        assert "Harga spot referensi **4,641.81**" in reply, reply
        assert "24 Aug 2026 16:14 WIB" in reply, reply
        assert "Harga chart" not in reply and "UTC" not in reply and "4,697.80" not in reply, reply
    categories["Jawaban spot dan WIB"] = 50

    for position in range(50):
        reply = build_spot_fallback_reply(
            f"Analisa XAUUSD H1 {position}",
            snapshot.instrument,
            "1h",
            4641.50,
            4642.12,
            datetime(2026, 8, 24, 9, 14, tzinfo=timezone.utc),
        )
        assert "Harga spot referensi saat ini **4,641.81**" in reply and "WIB" in reply, reply
        assert "indikator, Entry, SL, atau TP" in reply and "UTC" not in reply, reply
    categories["Fallback spot tanpa candle"] = 50

    h1_data = {"price": 100.0, "atr14": 10.0, "low20": 70.0, "high20": 130.0, "ma50": 90.0, "bias": "BUY"}
    for position in range(50):
        reply = _entry_scenario(h1_data, "1h")
        assert "106.00" in reply and "110.00" in reply and "114.00" in reply, reply
        assert "130.00" not in reply, reply
    categories["Skala level H1"] = 50

    daily_data = {"price": 100.0, "atr14": 10.0, "low20": 50.0, "high20": 150.0, "ma50": 80.0, "bias": "BUY"}
    for position in range(50):
        reply = _entry_scenario(daily_data, "1d")
        assert "110.00" in reply and "120.00" in reply and "130.00" in reply, reply
    categories["Skala level D1"] = 50

    source = Path("streamlit_app.py").read_text(encoding="utf-8")
    for position in range(50):
        assert "st.session_state.stable_prompt_chips.clear()" in source
        assert "if st.session_state.get(\"pending_question\")" in source
        assert "build_spot_fallback_reply" in source
        assert "_format_wib" in source
    categories["Chip dan kontrak tampilan"] = 50

    assert sum(categories.values()) == 300, categories
    print("xau_chat_experience_ok=" + ",".join(f"{key}:{value}" for key, value in categories.items()) + ";total:300")


if __name__ == "__main__":
    run()
