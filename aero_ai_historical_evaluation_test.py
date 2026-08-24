"""Regresi harness evaluasi historis AMI menggunakan fixture deterministik, bukan data live."""

from __future__ import annotations

import math

import pandas as pd

from historical_evaluation import evaluate_ma_structure_screen, evaluation_report


def _fixture() -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=480, freq="h", tz="UTC")
    close = [100 + point * 0.03 + math.sin(point / 7) * 0.15 for point in range(len(index))]
    return pd.DataFrame({"close": close}, index=index)


def run() -> None:
    evaluation = evaluate_ma_structure_screen(_fixture(), horizon_candles=3, censor_gap_hours=24)
    assert evaluation is not None, "fixture harus menghasilkan observasi temporal yang cukup"
    assert evaluation.train.count > 0 and evaluation.validation.count > 0 and evaluation.test.count > 0, evaluation
    assert all(target <= evaluation.cutoff_at for target in evaluation.observations["target_at"]), "target melewati censor gap"
    report = evaluation_report(evaluation)
    assert "bukan prediksi harga" in report and "akurasi" not in report.casefold(), report
    print(f"historical_evaluation_ok=train:{evaluation.train.count} validation:{evaluation.validation.count} test:{evaluation.test.count}")


if __name__ == "__main__":
    run()
