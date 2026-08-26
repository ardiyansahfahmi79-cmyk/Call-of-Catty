"""Kontrak deterministik normalisasi data grafik tren kurs."""

from currency_trend_core import CURRENCY_TREND_DAYS, format_axis_value, parse_historical_rates, trend_axis_ticks, trend_change_percent


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
    small_points = [{"Tanggal": "2026-08-19", "Kurs": 0.000055}, {"Tanggal": "2026-08-20", "Kurs": 0.000057}]
    tick_values, tick_labels, chart_range = trend_axis_ticks(small_points)
    assert len(tick_values) == 4
    assert all("µ" not in label for label in tick_labels)
    assert tick_labels[0].startswith("0.000")
    assert len(set(tick_labels)) == len(tick_labels)
    assert chart_range[0] < 0.000055 < chart_range[1]
    assert format_axis_value(0.000056) == "0.000056"
    print("Currency trend contract: PASS")


if __name__ == "__main__":
    run()
