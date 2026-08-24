"""Regresi cache metadata fundamental tanpa panggilan jaringan."""

from __future__ import annotations

from unittest.mock import patch

import fundamental_data as fundamental


FRED_CSV = "observation_date,DGS2\n2026-08-20,4.19\n"
BLS_PAYLOAD = {
    "Results": {"series": [{"data": [{"year": "2026", "period": "M07", "value": "4.2"}]}]},
}


def run() -> None:
    fundamental._CACHE.clear()
    with patch.object(fundamental, "_get_text", return_value=FRED_CSV):
        eur = fundamental._latest_fred_macro("EURUSD")
        cad = fundamental._latest_fred_macro("USDCAD")
    assert eur and cad
    assert {item.instrument_code for item in eur} == {"EURUSD"}, eur
    assert {item.instrument_code for item in cad} == {"USDCAD"}, cad
    with patch.object(fundamental, "_get_json", return_value=BLS_PAYLOAD):
        eur_bls = fundamental._latest_us_unemployment("EURUSD")
        cad_bls = fundamental._latest_us_unemployment("USDCAD")
    assert {item.instrument_code for item in eur_bls} == {"EURUSD"}, eur_bls
    assert {item.instrument_code for item in cad_bls} == {"USDCAD"}, cad_bls
    print("fundamental_cache_ok=fred:EURUSD,USDCAD bls:EURUSD,USDCAD")


if __name__ == "__main__":
    run()
