"""Regresi deterministik untuk struktur harga AMI tanpa data jaringan atau harga fiktif live."""

from __future__ import annotations

import pandas as pd

from market_structure import build_price_structure, confirmed_swings


def _fixture() -> pd.DataFrame:
    index = pd.date_range("2025-01-02", periods=15, freq="h", tz="UTC")
    rows = [
        (10.0, 11.0, 9.5, 10.5), (10.5, 11.5, 10.0, 10.8), (10.8, 11.2, 9.0, 9.6),
        (9.6, 10.0, 9.3, 9.8), (9.8, 12.0, 9.7, 11.7), (11.7, 13.5, 11.0, 13.0),
        (13.0, 13.0, 11.5, 12.0), (12.0, 12.5, 10.7, 11.0), (11.0, 12.4, 10.2, 11.5),
        (11.5, 14.5, 11.2, 14.3), (14.3, 15.0, 13.0, 14.6), (14.6, 15.3, 14.0, 15.0),
        (15.0, 15.0, 14.3, 14.7), (14.7, 14.9, 14.1, 14.5), (14.5, 15.7, 14.4, 15.6),
    ]
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=index)


def run() -> None:
    candles = _fixture()
    early = confirmed_swings(candles.iloc[:7], window=2)
    full = confirmed_swings(candles, window=2)
    assert not any(swing.kind == "high" and swing.level == 13.5 for swing in early), "pivot tak boleh dikenali sebelum dua candle konfirmasi"
    assert any(swing.kind == "high" and swing.level == 13.5 for swing in full), "pivot harus tersedia setelah candle konfirmasi"
    structure = build_price_structure(candles, window=2)
    assert structure.state == "BULLISH", structure
    assert structure.latest_break == "PENEMBUSAN STRUKTUR BULLISH", structure
    assert structure.latest_fvg is not None and structure.latest_fvg.direction == "bullish", structure
    assert structure.fibonacci is not None and structure.fibonacci.direction == "bullish", structure
    assert structure.fibonacci.level_618 < structure.fibonacci.level_500 < structure.fibonacci.level_382, structure
    print(f"market_structure_ok=swings:{len(structure.swings)} state:{structure.state} break:{structure.latest_break}")


if __name__ == "__main__":
    run()
