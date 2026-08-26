"""Mesin kalkulasi deterministik untuk prototipe AeroVulpis Risk Management.

Tidak ada koneksi broker, harga pasar, atau perintah transaksi pada modul ini.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskSnapshot:
    """Hasil kalkulasi yang hanya berlaku sebagai simulasi edukasi."""

    balance: float
    risk_amount: float
    daily_loss_amount: float
    daily_profit_amount: float
    stop_distance: float
    target_distance: float
    reward_risk: float
    estimated_lots: float
    break_even_rate: float
    scenario_net: float
    scenario_status: str


def clamp(value: float, lower: float, upper: float) -> float:
    """Menjaga nilai berada pada rentang yang diizinkan."""
    return max(lower, min(value, upper))


def calculate_risk_snapshot(
    *,
    balance: float,
    risk_percent: float,
    daily_loss_percent: float,
    daily_profit_percent: float,
    entry: float,
    stop_loss: float,
    take_profit: float,
    price_move_value_per_lot: float,
    wins: int,
    losses: int,
) -> RiskSnapshot:
    """Menghitung risk-reward dan batas simulasi tanpa asumsi broker atau lot spesifik."""
    safe_balance = max(float(balance), 0.0)
    safe_risk_percent = clamp(float(risk_percent), 0.0, 100.0)
    safe_daily_loss = clamp(float(daily_loss_percent), 0.0, 100.0)
    safe_daily_profit = clamp(float(daily_profit_percent), 0.0, 100.0)
    safe_value = max(float(price_move_value_per_lot), 0.000001)
    safe_wins = max(int(wins), 0)
    safe_losses = max(int(losses), 0)

    stop_distance = abs(float(entry) - float(stop_loss))
    target_distance = abs(float(take_profit) - float(entry))
    risk_amount = safe_balance * safe_risk_percent / 100.0
    daily_loss_amount = safe_balance * safe_daily_loss / 100.0
    daily_profit_amount = safe_balance * safe_daily_profit / 100.0

    if stop_distance <= 0:
        reward_risk = 0.0
        estimated_lots = 0.0
        break_even_rate = 0.0
    else:
        reward_risk = target_distance / stop_distance
        estimated_lots = risk_amount / (stop_distance * safe_value)
        break_even_rate = 1 / (1 + reward_risk) if reward_risk > 0 else 0.0

    scenario_net = (safe_wins * risk_amount * reward_risk) - (safe_losses * risk_amount)
    if daily_loss_amount and scenario_net <= -daily_loss_amount:
        scenario_status = "BATAS RUGI TERCAPAI"
    elif daily_profit_amount and scenario_net >= daily_profit_amount:
        scenario_status = "TARGET HARIAN TERCAPAI"
    elif reward_risk < 1.0 or stop_distance <= 0:
        scenario_status = "PERLU PENINJAUAN"
    else:
        scenario_status = "RISIKO TERKONTROL"

    return RiskSnapshot(
        balance=safe_balance,
        risk_amount=risk_amount,
        daily_loss_amount=daily_loss_amount,
        daily_profit_amount=daily_profit_amount,
        stop_distance=stop_distance,
        target_distance=target_distance,
        reward_risk=reward_risk,
        estimated_lots=estimated_lots,
        break_even_rate=break_even_rate,
        scenario_net=scenario_net,
        scenario_status=scenario_status,
    )
