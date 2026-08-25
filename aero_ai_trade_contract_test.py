"""Kontrak deterministik untuk guardrail Aero AI Trade tanpa Streamlit atau broker nyata."""

from aero_ai_trade import (
    HEARTBEAT_TTL_SECONDS,
    _close_paper_position,
    _new_paper_position,
    _paper_entry_block_reason,
    _session_is_fresh,
)


def run() -> None:
    assert _session_is_fresh(100.0, 100.0 + HEARTBEAT_TTL_SECONDS)
    assert not _session_is_fresh(100.0, 100.0 + HEARTBEAT_TTL_SECONDS + 0.1)

    assert _paper_entry_block_reason(False, True, True, 0) == "Paper Trading belum aktif."
    assert _paper_entry_block_reason(True, True, False, 0) == "Heartbeat browser sudah kedaluwarsa; refresh sesi sebelum membuat simulasi baru."
    assert _paper_entry_block_reason(True, False, True, 0) == "Auto Trade simulasi sedang pause. Aktifkan mode simulasi terlebih dahulu."
    assert _paper_entry_block_reason(True, True, True, 1) == "Batas 1 posisi Paper Trading telah tercapai."
    assert _paper_entry_block_reason(True, True, True, 0) is None

    paper = _new_paper_position(1)
    assert paper["ID"] == "PAPER-001"
    assert paper["Status"] == "OPEN · PAPER"
    assert paper["Quote"] == "Tidak dikutip pada prototipe"
    assert "Harga" not in paper

    remaining, closed = _close_paper_position([paper], "PAPER-001")
    assert closed and remaining == []
    untouched, closed = _close_paper_position([paper], "PAPER-404")
    assert not closed and untouched == [paper]


if __name__ == "__main__":
    run()
    print("aero_ai_trade_contract_test_ok")
