"""Kontrak deterministik normalisasi data grafik tren kurs."""

from currency_trend_core import CURRENCY_TREND_DAYS, parse_historical_rates, trend_change_percent


PAYLOAD = {
    "rates": {
        "2026-08-19": {"IDR": 17_800.0},
        "2026-08-20": {"IDR": 17_900.0},
        "2026-08-21": {"IDR": 17_600.0},
    }
}


def run() -> None:
    assert CURRENCY_TREND_DAYS == 30
    points = parse_historical_rates(PAYLOAD, "IDR")
    assert [point["Tanggal"] for point in points] == ["2026-08-19", "2026-08-20", "2026-08-21"]
    assert round(trend_change_percent(points) or 0, 2) == -1.12
    assert parse_historical_rates({"rates": {"2026-08-19": {"IDR": 0}}}, "IDR") == []
    assert trend_change_percent(points[:1]) is None
    print("Currency trend contract: PASS")


if __name__ == "__main__":
    run()
