from __future__ import annotations

from market_chat import build_reply
from market_data import fetch_market_snapshot, instrument_from_code


def main() -> None:
    instrument = instrument_from_code("XAUUSD")
    assert instrument is not None
    snapshot = fetch_market_snapshot(instrument, interval="1h")
    assert snapshot.reference_spot_price is not None
    assert snapshot.reference_spot_at is not None
    reply = build_reply("Tentukan Entry, SL, TP1 TP2 TP3 dan Risk untuk XAUUSD pada H1", snapshot, [])
    assert "SKENARIO LEVEL" in reply
    assert "TP1, TP2, dan TP3" in reply
    assert "ATR(14) H1" in reply
    assert "Harga spot referensi" in reply
    assert "WIB" in reply
    assert "Harga chart" not in reply
    assert "Yahoo Finance" not in reply
    assert "yfinance" not in reply.casefold()
    print(
        "xau_entry_ok="
        f"spot:{snapshot.reference_spot_price:.2f} "
        f"spot_at:{snapshot.reference_spot_at.isoformat()} "
        f"reply_chars:{len(reply)}"
    )


if __name__ == "__main__":
    main()
