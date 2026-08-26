"""Kontrak ringkas untuk kalkulator Risk Management tanpa Streamlit atau broker."""

from risk_management_core import calculate_risk_snapshot


def run() -> None:
    controlled = calculate_risk_snapshot(
        balance=1000, risk_percent=1, daily_loss_percent=5, daily_profit_percent=10,
        entry=2350, stop_loss=2345, take_profit=2360, price_move_value_per_lot=100,
        wins=3, losses=2,
    )
    assert controlled.risk_amount == 10
    assert controlled.reward_risk == 2
    assert controlled.estimated_lots == 0.02
    assert round(controlled.break_even_rate, 4) == 0.3333
    assert controlled.scenario_status == "RISIKO TERKONTROL"

    blocked = calculate_risk_snapshot(
        balance=1000, risk_percent=2, daily_loss_percent=3, daily_profit_percent=20,
        entry=10, stop_loss=9, take_profit=12, price_move_value_per_lot=1,
        wins=0, losses=2,
    )
    assert blocked.scenario_status == "BATAS RUGI TERCAPAI"

    invalid = calculate_risk_snapshot(
        balance=1000, risk_percent=1, daily_loss_percent=5, daily_profit_percent=10,
        entry=10, stop_loss=10, take_profit=12, price_move_value_per_lot=1,
        wins=1, losses=0,
    )
    assert invalid.estimated_lots == 0
    assert invalid.scenario_status == "PERLU PENINJAUAN"

    print("Risk Management core contract: PASS")


if __name__ == "__main__":
    run()
