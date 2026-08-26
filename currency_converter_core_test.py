"""Kontrak deterministik untuk daftar dan perhitungan konverter mata uang."""

from currency_converter_core import (
    BLOCKED_CURRENCY_CODES,
    PREFERRED_CURRENCY_CODES,
    available_currency_codes,
    convert_from_usd_reference,
    currency_label,
    currency_pair_label,
)


RATES = {"USD": 1.0, "IDR": 16_000.0, "EUR": 0.9, "ILS": 3.0}


def run() -> None:
    choices = available_currency_codes(RATES)
    assert "ILS" not in choices
    assert BLOCKED_CURRENCY_CODES.isdisjoint(choices)
    assert len(choices) == 3
    assert len(PREFERRED_CURRENCY_CODES) == 90
    assert BLOCKED_CURRENCY_CODES.isdisjoint(PREFERRED_CURRENCY_CODES)
    assert len(available_currency_codes({code: 1.0 for code in PREFERRED_CURRENCY_CODES})) == 90
    assert currency_label("IDR") == "🇮🇩 IDR"
    assert currency_pair_label("IDR", "USD") == "🇮🇩 IDR → 🇺🇸 USD"
    assert convert_from_usd_reference(100.0, "USD", "IDR", RATES) == 1_600_000.0
    assert round(convert_from_usd_reference(1_600_000.0, "IDR", "USD", RATES), 2) == 100.0
    try:
        convert_from_usd_reference(1.0, "ILS", "USD", RATES)
    except ValueError:
        pass
    else:
        raise AssertionError("kode terblokir tidak boleh dapat dikonversi")
    print("Currency converter contract: PASS")


if __name__ == "__main__":
    run()
