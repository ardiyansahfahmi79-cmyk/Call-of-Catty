"""Jalankan evaluasi historis deskriptif pada candle publik yang tersedia.

Runner ini tidak digunakan oleh UI atau chat. Hasilnya hanya memeriksa apakah
data publik cukup untuk split temporal kausal; tidak mencetak atau menyatakan
akurasi, prediksi harga, maupun instruksi transaksi.
"""

from __future__ import annotations

from historical_evaluation import evaluate_ma_structure_screen, evaluation_report
from market_data import fetch_market_snapshot, instrument_from_code


def run() -> None:
    outcomes: list[str] = []
    for code in ("EURUSD", "XAUUSD", "BTCUSD", "US100"):
        instrument = instrument_from_code(code)
        if instrument is None:
            outcomes.append(f"{code}:KONFIGURASI_TIDAK_TERSEDIA")
            continue
        try:
            snapshot = fetch_market_snapshot(instrument, "1h")
            evaluation = evaluate_ma_structure_screen(snapshot.candles)
        except RuntimeError:
            outcomes.append(f"{code}:DATA_TIDAK_TERSEDIA")
            continue
        if not evaluation:
            outcomes.append(f"{code}:SPLIT_BELUM_MEMADAI")
            continue
        report = evaluation_report(evaluation)
        assert "bukan prediksi harga" in report
        outcomes.append(
            f"{code}:LAYAK_RISET train={evaluation.train.count} validation={evaluation.validation.count} test={evaluation.test.count}"
        )
    print("historical_research_run=" + ";".join(outcomes))


if __name__ == "__main__":
    run()
