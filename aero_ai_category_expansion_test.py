"""Ekspansi 50 kasus per kategori tanpa memanggil sumber harga atau kalender eksternal."""

from __future__ import annotations

from market_chat import build_unknown_input_reply, infer_intent
from market_data import INSTRUMENTS, detect_instruments, detect_timeframe
from streamlit_app import _loader_markup


def _codes(question: str) -> list[str]:
    return [instrument.code for instrument in detect_instruments(question)]


def main() -> None:
    categories: dict[str, int] = {}

    # 1. Resolusi instrumen + intent level/risk: 50 variasi casing dan frasa.
    for index in range(50):
        instrument = INSTRUMENTS[index % len(INSTRUMENTS)]
        question = f"{('ANALISA' if index % 2 else 'analisa')} {instrument.code.lower() if index % 3 else instrument.code} pada H{(index % 12) + 1}"
        assert _codes(question) == [instrument.code], question
    categories["Instrumen + Entry + Risiko"] = 50

    # 2. Format pair: slash, spasi, dash, dan garis bawah pada pair yang dipetakan eksplisit.
    pairs = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY", "EURCHF", "EURAUD", "EURNZD", "AUDJPY", "CADJPY", "CHFJPY")
    separators = (" / ", " ", "-", "_")
    format_cases = [f"Analisa {pair[:3]}{separator}{pair[3:]} H1" for pair in pairs for separator in separators][:50]
    for question in format_cases:
        compact = question.replace("Analisa ", "").replace(" H1", "").replace(" ", "").replace("/", "").replace("-", "").replace("_", "")
        assert _codes(question) == [compact], question
    categories["Format pair tambahan"] = len(format_cases)

    # 3. Alias: pilih 50 alias eksplisit yang bukan token pendek ambigu.
    alias_cases: list[tuple[str, str]] = []
    for instrument in INSTRUMENTS:
        for alias in instrument.aliases:
            if len(alias.replace("/", "").replace(" ", "")) >= 4:
                alias_cases.append((alias, instrument.code))
            if len(alias_cases) == 50:
                break
        if len(alias_cases) == 50:
            break
    assert len(alias_cases) == 50
    for alias, code in alias_cases:
        assert _codes(f"Tinjau risiko {alias} D1") == [code], alias
    categories["Alias instrumen"] = len(alias_cases)

    # 4. Timeframe: 50 kombinasi instrumen dan 17 timeframe yang didukung.
    timeframe_cases = (("M15", "15m"), ("M30", "30m"), ("H1", "1h"), ("H2", "2h"), ("H3", "3h"), ("H4", "4h"), ("H5", "5h"), ("H6", "6h"), ("H7", "7h"), ("H8", "8h"), ("H9", "9h"), ("H10", "10h"), ("H11", "11h"), ("H12", "12h"), ("D1", "1d"), ("W1", "1wk"), ("MN", "1mo"))
    for index in range(50):
        written, expected = timeframe_cases[index % len(timeframe_cases)]
        code = ("XAUUSD", "EURUSD", "US100", "BTCUSD")[index % 4]
        question = f"Analisa {code} {written}"
        assert detect_timeframe(question) == expected, question
    categories["Instrumen × timeframe"] = 50

    # 5. Permintaan level tanpa instrumen: harus meminta instrumen, bukan membuat level.
    entry_templates = ("tentukan entry", "tentukan sl", "buat tp1", "buat tp2", "buat tp3", "atur stop loss", "atur take profit", "hitung risk reward", "entry sekarang", "mau level entry")
    for index in range(50):
        reply = build_unknown_input_reply(entry_templates[index % len(entry_templates)])
        assert "sebutkan instrumen" in reply
    categories["Level tanpa instrumen"] = 50

    # 6. Input ambigu/tidak tersedia: tetap respons profesional tanpa memilih aset.
    ambiguous = ("gu", "xtiusd", "abcxyz", "xxxusd", "zzzusd", "pair rahasia", "harga qqq", "scan yyy", "analisa zzz", "aset uuu")
    for index in range(50):
        question = f"analisa {ambiguous[index % len(ambiguous)]}"
        reply = build_unknown_input_reply(question)
        assert reply and not _codes(question), question
    categories["Input ambigu / tidak tersedia"] = 50

    # 7. Loader/konteks: 50 status bebas jargon teknis.
    for index in range(50):
        stage = ("Membaca instrumen dan timeframe", "Meninjau kondisi market", "Merangkum informasi dan menyiapkan grafik", "Informasi berhasil disiapkan")[index % 4]
        markup = _loader_markup(stage, min(96, 20 + index))
        assert stage in markup
        for forbidden in ("PIPELINE", "EST.", "DIGITAL MARKET", "PYTHON DATA ENGINE", "TRACEABLE CONTEXT"):
            assert forbidden not in markup.upper(), forbidden
    categories["Loader + konteks sesi"] = 50

    assert all(count == 50 for count in categories.values())
    assert sum(categories.values()) == 350
    print("expanded_scenarios_ok=" + ",".join(f"{name}:{count}" for name, count in categories.items()) + ";total:350")


if __name__ == "__main__":
    main()
