"""Uji respons Aero AI pada riwayat volatilitas ekstrem dan agenda inflasi publik."""

from __future__ import annotations

from datetime import datetime, timezone

import yfinance as yf

from fundamental_data import fetch_fundamental_context
from market_chat import build_reply
from market_data import MarketSnapshot, _normalize_history, calculate_indicators, instrument_from_code


FORBIDDEN_INTERNAL_TERMS = (
    "PIPELINE", "SHADOW MODE", "GLOBAL MACRO ROUTER", "EVIDENCE & DATA TRUST SCORE",
    "MARKET REGIME ENGINE", "DATA PROVENANCE LEDGER", "SOURCE HEALTH CONSOLE",
    "LOCAL DATASET & EVALUATION STUDIO",
)


def _historical_daily_snapshot(code: str, start: str, end: str) -> MarketSnapshot:
    instrument = instrument_from_code(code)
    assert instrument is not None
    history = yf.download(
        instrument.yahoo_symbol,
        start=start,
        end=end,
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    candles = _normalize_history(history)
    assert len(candles) >= 200, f"Riwayat publik tidak cukup: {len(candles)} candle"
    return MarketSnapshot(
        instrument=instrument,
        candles=candles,
        indicators=calculate_indicators(candles),
        fetched_at=datetime.now(timezone.utc),
        last_candle_at=candles.index[-1].to_pydatetime(),
        source=f"Yahoo Finance chart via yfinance · {instrument.yahoo_symbol}",
        warning="Riwayat harga publik untuk uji respons; bukan harga eksekusi broker.",
        interval="1d",
    )


def _assert_user_facing(reply: str) -> None:
    assert "Hal yang paling relevan" in reply
    assert "Risiko dan batas data" in reply
    assert "Konteks pendukung" in reply
    assert "bukan nasihat finansial personal" in reply
    assert not any(term in reply.upper() for term in FORBIDDEN_INTERNAL_TERMS), reply
    assert len(reply) < 4000, len(reply)


def main() -> None:
    # Cutoff sesudah penurunan tajam indeks AS pada Maret 2020; semua candle berasal dari Yahoo Finance.
    flash_crash_snapshot = _historical_daily_snapshot("SPX", "2019-01-01", "2020-03-18")
    flash_reply = build_reply("Analisa SPX saat volatilitas ekstrem pada D1", flash_crash_snapshot, [])
    _assert_user_facing(flash_reply)
    assert flash_reply.startswith("**RINGKASAN SPX · D1**")
    assert "Riwayat harga publik untuk uji respons" in flash_reply

    # Agenda CPI diproses hanya dari kalender publik yang tersedia; tidak ada nilai rilis yang dibuat-buat.
    dxy_snapshot = _historical_daily_snapshot("DXY", "2025-01-01", "2026-08-22")
    cpi_reply = build_reply("Jelaskan dampak lonjakan CPI AS untuk DXY pada D1", dxy_snapshot, fetch_fundamental_context(dxy_snapshot.instrument))
    _assert_user_facing(cpi_reply)
    assert "CPI / Consumer Price Index untuk DXY" in cpi_reply
    assert "Status rilis" in cpi_reply
    assert any(
        marker in cpi_reply
        for marker in (
            "Actual:",
            "tidak akan menggantinya",
            "tidak akan membuat nilai forecast",
            "tidak tersedia pada pemindaian ini",
            "belum memuat event yang cocok",
        )
    )

    print(
        "extreme_market_ok="
        f"spx_date:{flash_crash_snapshot.last_candle_at.date()} "
        f"spx_chars:{len(flash_reply)} cpi_chars:{len(cpi_reply)}"
    )


if __name__ == "__main__":
    main()
