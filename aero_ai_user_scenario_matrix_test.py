"""Regresi percakapan lokal untuk input market tanpa melakukan request sumber eksternal."""

from market_chat import build_unknown_input_reply, infer_intent
from market_data import INSTRUMENTS, detect_instruments, detect_timeframe
from streamlit_app import _loader_markup, resolve_thread_context


def _codes(question: str) -> list[str]:
    return [instrument.code for instrument in detect_instruments(question)]


def main() -> None:
    scenario_count = 0

    for instrument in INSTRUMENTS:
        code = instrument.code
        assert _codes(f"Analisa {code} pada H1") == [code], code
        scenario_count += 1

        assert _codes(f"Tentukan Entry, SL, TP1 TP2 TP3 untuk {code} pada H4") == [code], code
        assert infer_intent(f"Tentukan Entry, SL, TP1 TP2 TP3 untuk {code} pada H4") == "levels_entry"
        scenario_count += 1

        assert _codes(f"Tinjau risiko {code} pada D1") == [code], code
        assert infer_intent(f"Tinjau risiko {code} pada D1") == "risk"
        scenario_count += 1

    additional_pairs = (
        "EURCHF", "EURAUD", "EURNZD", "AUDJPY", "CADJPY", "CHFJPY", "GBPAUD", "GBPCAD",
        "GBPCHF", "AUDCAD", "AUDCHF", "NZDJPY", "NZDCAD", "NZDCHF", "CADCHF",
    )
    for pair in additional_pairs:
        left, right = pair[:3], pair[3:]
        assert _codes(f"Analisa {left} / {right} H1") == [pair], pair
        assert _codes(f"Analisa {left} {right} H1") == [pair], pair
        scenario_count += 2

    alias_cases = (
        ("emas", "XAUUSD"), ("harga emas", "XAUUSD"), ("gold", "XAUUSD"),
        ("gold eur", "XAUEUR"), ("minyak brent", "BRENT"), ("minyak wti", "WTI"),
        ("perak", "XAGUSD"), ("bitcoin", "BTCUSD"), ("ethereum", "ETHUSD"),
        ("jakarta composite", "IHSG"), ("bank mandiri", "BMRI"), ("antam", "ANTM"),
    )
    for alias, code in alias_cases:
        for question in (f"Analisa {alias} H1", f"Tentukan Entry untuk {alias} H4", f"Tinjau risiko {alias} D1", f"Jelaskan tren {alias} W1", f"Analisa {alias} MN"):
            assert _codes(question) == [code], (question, code)
            scenario_count += 1

    timeframe_cases = (
        ("M15", "15m"), ("M30", "30m"), ("H1", "1h"), ("H2", "2h"), ("H3", "3h"),
        ("H4", "4h"), ("H5", "5h"), ("H6", "6h"), ("H7", "7h"), ("H8", "8h"),
        ("H9", "9h"), ("H10", "10h"), ("H11", "11h"), ("H12", "12h"), ("D1", "1d"),
        ("W1", "1wk"), ("MN", "1mo"),
    )
    for code in ("XAUUSD", "EURUSD", "BTCUSD"):
        for written, expected in timeframe_cases:
            assert _codes(f"Analisa {code} {written}") == [code]
            assert detect_timeframe(f"Analisa {code} {written}") == expected
            scenario_count += 1

    for question in ("tentukan entry", "buat tp1 tp2 tp3", "tentukan sl", "entry sekarang", "take profit"):
        reply = build_unknown_input_reply(question)
        assert "sebutkan instrumen" in reply
        assert "Entry, SL, TP1, TP2, dan TP3" in reply
        scenario_count += 1

    for question in ("analisa gu", "scan gu h1", "harga gu", "pair gu", "analisa xtiusd", "analisa abcxyz", "analisa eur usd gbp jpy", "saya mau entry"):
        reply = build_unknown_input_reply(question)
        assert reply
        scenario_count += 1

    for stage in ("Membaca instrumen dan timeframe", "Merangkum informasi dan menyiapkan grafik", "Informasi berhasil disiapkan"):
        markup = _loader_markup(stage, 72)
        for forbidden in ("PIPELINE", "EST.", "DIGITAL MARKET", "PYTHON DATA ENGINE", "TRACEABLE CONTEXT"):
            assert forbidden not in markup.upper(), forbidden
        scenario_count += 1

    assert resolve_thread_context("tentukan entry", {"instrument": "XAUUSD", "interval": "1h", "agenda": None}) == "Tentukan Entry, SL, TP1 TP2 TP3 dan Risk untuk XAUUSD pada timeframe 1h"
    scenario_count += 1

    assert 200 <= scenario_count <= 400, scenario_count
    print(f"Aero AI user scenario matrix passed: {scenario_count} skenario lokal")


if __name__ == "__main__":
    main()
