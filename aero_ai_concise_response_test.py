"""Verifikasi respons ringkas Aero AI pada agenda market dengan data publik aktual."""

from __future__ import annotations

from fundamental_data import fetch_fundamental_context
from market_chat import build_reply
from market_data import detect_instruments, fetch_market_snapshot


def main() -> None:
    instrument = detect_instruments("Jelaskan dampak NFP untuk DXY")[0]
    snapshot = fetch_market_snapshot(instrument, interval="1h")
    reply = build_reply("Jelaskan dampak NFP untuk DXY", snapshot, fetch_fundamental_context(instrument))
    forbidden = (
        "GLOBAL MACRO ROUTER", "EVIDENCE & DATA TRUST SCORE", "MARKET REGIME ENGINE",
        "MARKET STRUCTURE QUALITY GATE", "CROSS-ASSET CONTEXT MATRIX", "DATA PROVENANCE LEDGER",
        "SOURCE HEALTH CONSOLE", "SCENARIO INVALIDATION MAP", "COMPARATIVE REGIME REPLAY",
        "LOCAL DATASET & EVALUATION STUDIO", "SHADOW MODE",
    )
    assert reply.startswith("**DXY · H1 ·"), reply[:120]
    assert "NFP / Non-Farm Payrolls untuk DXY" in reply, reply
    assert "Inti pembacaan" in reply
    assert "KONTEKS AGENDA" in reply
    assert "Catatan risiko" in reply
    assert len(reply) < 4000, len(reply)
    assert not any(term in reply for term in forbidden), reply
    print(f"concise_dxy_nfp_ok=chars:{len(reply)} candle:{snapshot.last_candle_at.isoformat()}")


if __name__ == "__main__":
    main()
