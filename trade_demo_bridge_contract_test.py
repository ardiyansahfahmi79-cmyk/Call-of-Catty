"""Kontrak offline bridge demo; tidak memerlukan terminal MT5 atau data harga."""

from scalping_rules import ScalpingPolicy, entry_block_reason, evaluate_m1_scalping_signal
from trade_demo_client import DemoBridgeError, validate_bridge_url


def run() -> None:
    policy = ScalpingPolicy()
    assert validate_bridge_url("http://127.0.0.1:8765") == "http://127.0.0.1:8765"
    assert validate_bridge_url("https://bridge.example.test") == "https://bridge.example.test"
    try:
        validate_bridge_url("http://bridge.example.test")
        raise AssertionError("HTTP remote wajib ditolak.")
    except DemoBridgeError:
        pass

    base = dict(demo_verified=True, heartbeat_fresh=True, kill_switch_active=False, symbol="XAUUSD", volume=0.01, open_positions=0, spread_points=10.0, daily_loss_percent=0.0, policy=policy)
    assert entry_block_reason(**base) is None
    assert entry_block_reason(**(base | {"demo_verified": False})) == "Bridge hanya menerima akun demo MT5 yang terverifikasi."
    assert entry_block_reason(**(base | {"heartbeat_fresh": False})) == "Heartbeat panel telah kedaluwarsa."
    assert entry_block_reason(**(base | {"kill_switch_active": True})) == "Kill switch aktif; proposal order diblokir."
    assert entry_block_reason(**(base | {"symbol": "EURUSD"})) == "EURUSD tidak ada di whitelist scalping demo."
    assert entry_block_reason(**(base | {"volume": 0.02})) == "Lot harus lebih dari 0 dan tidak melebihi 0.01."
    assert entry_block_reason(**(base | {"open_positions": 1})) == "Batas 1 posisi terbuka telah tercapai."
    assert entry_block_reason(**(base | {"spread_points": 51.0})) == "Spread melewati batas keamanan atau data spread tidak valid."
    assert entry_block_reason(**(base | {"daily_loss_percent": 0.50})) == "Batas kerugian harian scalping telah tercapai."

    bullish = [{"high": 100.0 + index, "low": 99.5 + index, "close": 99.8 + index} for index in range(30)]
    bearish = [{"high": 130.0 - index, "low": 129.5 - index, "close": 129.8 - index} for index in range(30)]
    assert evaluate_m1_scalping_signal(bullish).decision == "BUY"
    assert evaluate_m1_scalping_signal(bearish).decision == "SELL"
    assert evaluate_m1_scalping_signal(bullish[:10]).decision == "NO_TRADE"


if __name__ == "__main__":
    run()
    print("trade_demo_bridge_contract_test_ok")
