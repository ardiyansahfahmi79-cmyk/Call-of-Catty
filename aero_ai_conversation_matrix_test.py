"""Regresi percakapan data-driven Aero AI tanpa mengambil data jaringan per kasus.

Matriks ini menguji ratusan variasi input pada lapisan resolusi intent. Uji
snapshot dan AppTest tetap dijalankan terpisah karena hanya keduanya memakai
sumber publik atau runtime Streamlit.
"""

from __future__ import annotations

from market_chat import build_unknown_input_reply, detect_economic_agenda
from market_data import INSTRUMENTS, detect_instruments, detect_timeframe
from market_intelligence import normalize_market_language


def _assert_instrument(question: str, expected: str) -> None:
    normalized = normalize_market_language(question).normalized_question
    found = detect_instruments(normalized)
    assert found and found[0].code == expected, (question, normalized, [item.code for item in found], expected)


def test_instrument_alias_matrix() -> int:
    tested = 0
    wrappers = (
        "Analisa {alias} pada H1",
        "ANALISA {alias} H4",
        "tolong scan {alias} di m15",
        "bagaimana tren {alias} sekarang",
    )
    for instrument in INSTRUMENTS:
        aliases = dict.fromkeys((instrument.code, instrument.code.casefold(), *instrument.aliases))
        for alias in aliases:
            for wrapper in wrappers:
                _assert_instrument(wrapper.format(alias=alias), instrument.code)
                tested += 1
    return tested


def test_pair_format_matrix() -> int:
    tested = 0
    for instrument in INSTRUMENTS:
        if len(instrument.code) != 6 or not instrument.code.isalnum():
            continue
        left, right = instrument.code[:3], instrument.code[3:]
        for written in (instrument.code.lower(), f"{left} {right}", f"{left} / {right}", f"{left}-{right}", f"{left}_{right}"):
            _assert_instrument(f"analisa {written} pada H1", instrument.code)
            tested += 1
    return tested


def test_timeframe_and_conversation_matrix() -> int:
    tested = 0
    for written, expected in (
        ("m15", "15m"), ("M30", "30m"), ("h1", "1h"), ("H2", "2h"), ("h3", "3h"),
        ("H4", "4h"), ("h5", "5h"), ("H6", "6h"), ("h7", "7h"), ("H8", "8h"),
        ("h9", "9h"), ("H10", "10h"), ("h11", "11h"), ("H12", "12h"), ("d1", "1d"),
        ("W1", "1wk"), ("mn", "1mo"),
    ):
        assert detect_timeframe(f"analisa xauusd pada {written}") == expected
        tested += 1

    for greeting in ("halo Aero", "Halo Aero AI", "HALO AERO AI", "hai aero ai", "selamat pagi Aero"):
        reply = build_unknown_input_reply(greeting)
        assert "Aero AI" in reply and "analisa" in reply.casefold(), (greeting, reply)
        tested += 1

    for creator_question in ("siapa yang menciptakanmu", "siapa pembuatmu", "siapa yang membuat Aero AI", "who created you"):
        assert "DynamiHatch" in build_unknown_input_reply(creator_question)
        tested += 1

    ambiguous = build_unknown_input_reply("analisa gu pada h1")
    assert "singkatan **gu**" in ambiguous and "XAUUSD" in ambiguous
    assert detect_instruments("analisa gu pada h1") == []
    tested += 1

    for agenda_question, expected_name in (
        ("Jelaskan CPI AS", "CPI / Consumer Price Index"),
        ("retail sales mom usa", "Retail Sales"),
        ("FOMC untuk XAUUSD", "FOMC / Federal Reserve"),
        ("boJ untuk usdjpy", "Bank of Japan"),
        ("ECB untuk EUR / USD", "European Central Bank"),
    ):
        agenda = detect_economic_agenda(agenda_question)
        assert agenda and agenda[1] == expected_name, (agenda_question, agenda)
        tested += 1
    return tested


def main() -> None:
    instrument_cases = test_instrument_alias_matrix()
    pair_cases = test_pair_format_matrix()
    conversation_cases = test_timeframe_and_conversation_matrix()
    total = instrument_cases + pair_cases + conversation_cases
    assert total >= 300, total
    print(
        "conversation_matrix_ok="
        f"{total} alias={instrument_cases} pair_format={pair_cases} semantic={conversation_cases}"
    )


if __name__ == "__main__":
    main()
