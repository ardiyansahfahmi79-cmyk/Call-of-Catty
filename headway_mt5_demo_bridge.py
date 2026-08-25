"""Bridge lokal Windows untuk monitoring dan proposal order Headway MT5 akun demo.

Kredensial tidak pernah diminta di sini: terminal MT5 harus sudah login secara
manual. Bridge ini menolak akun non-demo, tidak mengeksekusi dari endpoint scan,
dan membutuhkan proposal berumur pendek + frasa konfirmasi untuk order demo.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from scalping_rules import ScalpingPolicy, entry_block_reason, evaluate_m1_scalping_signal


AUDIT_DIR = Path.home() / ".aero_ai_trade"
AUDIT_FILE = AUDIT_DIR / "demo_audit.jsonl"
MAGIC_NUMBER = 733710


class BridgeError(RuntimeError):
    """Kesalahan yang aman untuk ditampilkan kepada panel lokal."""


@dataclass
class PendingProposal:
    proposal_id: str
    request: dict[str, Any]
    phrase: str
    expires_at: float


class AuditChain:
    def __init__(self, audit_file: Path = AUDIT_FILE) -> None:
        self.audit_file = audit_file
        self.previous_hash = self._last_hash()

    def _last_hash(self) -> str:
        if not self.audit_file.exists():
            return "GENESIS"
        last_line = self.audit_file.read_text(encoding="utf-8").strip().splitlines()
        if not last_line:
            return "GENESIS"
        return json.loads(last_line[-1]).get("hash", "GENESIS")

    def append(self, event: str, payload: dict[str, Any]) -> None:
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)
        record = {"at": datetime.now(timezone.utc).isoformat(), "event": event, "payload": payload, "previous_hash": self.previous_hash}
        encoded = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
        record["hash"] = hashlib.sha256(encoded).hexdigest()
        with self.audit_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        self.previous_hash = record["hash"]


class HeadwayDemoBridge:
    def __init__(self, token: str, policy: ScalpingPolicy | None = None) -> None:
        if len(token) < 24:
            raise BridgeError("AERO_TRADE_BRIDGE_TOKEN harus berupa secret kuat minimal 24 karakter.")
        self.token = token
        self.policy = policy or ScalpingPolicy()
        self.last_heartbeat = 0.0
        self.kill_switch = True
        self.proposals: dict[str, PendingProposal] = {}
        self.audit = AuditChain()

    @property
    def execution_enabled(self) -> bool:
        """Eksekusi demo memerlukan opt-in environment eksplisit pada Windows lokal."""
        return os.environ.get("AERO_TRADE_DEMO_EXECUTION_ENABLED", "").strip().upper() == "YES"

    def authenticate(self, authorization: str | None) -> None:
        supplied = (authorization or "").removeprefix("Bearer ").strip()
        if not secrets.compare_digest(supplied, self.token):
            raise BridgeError("Token bridge tidak valid.")

    @staticmethod
    def _mt5():
        try:
            import MetaTrader5 as mt5
        except ImportError as error:
            raise BridgeError("MetaTrader5 belum terpasang. Jalankan bridge ini pada Windows dengan requirements-demo-bridge.txt.") from error
        if not mt5.initialize():
            raise BridgeError(f"Terminal MT5 tidak siap: {mt5.last_error()}")
        return mt5

    def _account(self) -> tuple[Any, Any]:
        mt5 = self._mt5()
        account = mt5.account_info()
        terminal = mt5.terminal_info()
        if account is None or terminal is None:
            raise BridgeError("Tidak dapat membaca akun atau terminal MT5.")
        if account.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
            raise BridgeError("Bridge menolak akun non-demo.")
        if not terminal.connected or not terminal.trade_allowed or terminal.tradeapi_disabled:
            raise BridgeError("Terminal MT5 belum siap untuk operasi demo.")
        return mt5, account

    def _heartbeat_is_fresh(self) -> bool:
        return (time.time() - self.last_heartbeat) <= self.policy.heartbeat_ttl_seconds

    def heartbeat(self, source: str) -> dict[str, Any]:
        self.last_heartbeat = time.time()
        self.audit.append("heartbeat", {"source": source})
        return {"ok": True, "heartbeat_ttl_seconds": self.policy.heartbeat_ttl_seconds, "kill_switch": self.kill_switch}

    def health(self) -> dict[str, Any]:
        try:
            mt5, account = self._account()
            return {
                "ok": True,
                "mode": "demo",
                "server": account.server,
                "login_masked": f"***{str(account.login)[-4:]}",
                "heartbeat_fresh": self._heartbeat_is_fresh(),
                "kill_switch": self.kill_switch,
                "execution_enabled": self.execution_enabled,
                "mt5_version": mt5.version(),
            }
        except BridgeError as error:
            return {"ok": False, "mode": "demo", "error": str(error), "kill_switch": self.kill_switch, "execution_enabled": self.execution_enabled}

    def account(self) -> dict[str, Any]:
        _, account = self._account()
        return {"login_masked": f"***{str(account.login)[-4:]}", "server": account.server, "balance": account.balance, "equity": account.equity, "margin_free": account.margin_free, "currency": account.currency, "mode": "demo"}

    def positions(self) -> dict[str, Any]:
        mt5, _ = self._account()
        positions = mt5.positions_get() or []
        return {"items": [{"ticket": item.ticket, "symbol": item.symbol, "type": item.type, "volume": item.volume, "price_open": item.price_open, "profit": item.profit, "magic": item.magic} for item in positions if item.magic == MAGIC_NUMBER]}

    def history(self) -> dict[str, Any]:
        mt5, _ = self._account()
        end, start = datetime.now(), datetime.now() - timedelta(days=7)
        deals = mt5.history_deals_get(start, end) or []
        return {"items": [{"ticket": item.ticket, "position_id": item.position_id, "symbol": item.symbol, "volume": item.volume, "price": item.price, "profit": item.profit, "time": item.time} for item in deals if item.magic == MAGIC_NUMBER]}

    def set_kill_switch(self, active: bool) -> dict[str, Any]:
        self.kill_switch = bool(active)
        self.audit.append("kill_switch", {"active": self.kill_switch})
        return {"kill_switch": self.kill_switch}

    def _trade_request(self, mt5: Any, symbol: str, direction: str, volume: float, current_atr: float) -> dict[str, Any]:
        info, tick = mt5.symbol_info(symbol), mt5.symbol_info_tick(symbol)
        if info is None or tick is None or not info.point:
            raise BridgeError("Informasi simbol atau tick tidak tersedia.")
        side = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL
        price = tick.ask if direction == "BUY" else tick.bid
        minimum_stop = max(float(info.trade_stops_level) * float(info.point), float(info.point))
        stop_distance = max(float(current_atr) * 1.20, minimum_stop)
        target_distance = max(float(current_atr) * 1.50, minimum_stop)
        sl = price - stop_distance if direction == "BUY" else price + stop_distance
        tp = price + target_distance if direction == "BUY" else price - target_distance
        digits = int(info.digits)
        return {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": side,
            "price": round(price, digits),
            "sl": round(sl, digits),
            "tp": round(tp, digits),
            "deviation": 20,
            "magic": MAGIC_NUMBER,
            "comment": "aero-demo-scalping",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

    def _check_request(self, mt5: Any, request: dict[str, Any]) -> None:
        checked = mt5.order_check(request)
        if checked is None or getattr(checked, "retcode", None) != 0:
            detail = getattr(checked, "comment", mt5.last_error()) if checked is not None else mt5.last_error()
            raise BridgeError(f"Order demo tidak lolos pemeriksaan broker: {detail}")

    def _risk_state(self, mt5: Any, account: Any, symbol: str, volume: float, current_atr: float) -> tuple[dict[str, Any], str | None]:
        info, tick = mt5.symbol_info(symbol), mt5.symbol_info_tick(symbol)
        if info is None or tick is None or not info.point:
            return {}, "Informasi spread broker tidak tersedia."
        spread_points = (tick.ask - tick.bid) / info.point
        daily_loss = max(0.0, (account.balance - account.equity) / account.balance * 100) if account.balance else 100.0
        positions = mt5.positions_get() or []
        block = entry_block_reason(
            demo_verified=True,
            heartbeat_fresh=self._heartbeat_is_fresh(),
            kill_switch_active=self.kill_switch,
            symbol=symbol,
            volume=volume,
            open_positions=len(positions),
            spread_points=spread_points,
            daily_loss_percent=daily_loss,
            policy=self.policy,
        )
        return {"spread_points": spread_points, "daily_loss_percent": daily_loss, "open_positions": len(positions), "atr": current_atr}, block

    def scan_scalping(self) -> dict[str, Any]:
        mt5, account = self._account()
        symbol = self.policy.allowed_symbols[0]
        if not mt5.symbol_select(symbol, True):
            raise BridgeError(f"{symbol} tidak tersedia pada Market Watch broker demo.")
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 40)
        if rates is None:
            raise BridgeError("Candle M1 demo belum tersedia.")
        bars = [{"high": float(row["high"]), "low": float(row["low"]), "close": float(row["close"])} for row in rates]
        signal = evaluate_m1_scalping_signal(bars)
        if signal.atr is None:
            result = {"symbol": symbol, "decision": signal.decision, "reason": signal.reason, "atr": None, "entry_block": "ATR belum tersedia.", "mode": "demo", "execution": "never from scan"}
            self.audit.append("scalping_scan", result)
            return result
        risk, block = self._risk_state(mt5, account, symbol, self.policy.max_volume, signal.atr)
        tick = mt5.symbol_info_tick(symbol)
        result = {"symbol": symbol, "decision": signal.decision, "reason": signal.reason, "atr": signal.atr, **risk, "bid": tick.bid if tick else None, "ask": tick.ask if tick else None, "tick_time": tick.time if tick else None, "entry_block": block, "mode": "demo", "execution": "never from scan"}
        self.audit.append("scalping_scan", result)
        return result

    def create_proposal(self) -> dict[str, Any]:
        """Membuat proposal yang belum berstatus order dan otomatis kedaluwarsa."""
        scan = self.scan_scalping()
        if scan["decision"] not in {"BUY", "SELL"}:
            raise BridgeError("Tidak ada kondisi entry; sistem mempertahankan NO_TRADE.")
        if scan["entry_block"]:
            raise BridgeError(f"Proposal diblokir: {scan['entry_block']}")
        mt5, _ = self._account()
        request = self._trade_request(mt5, scan["symbol"], scan["decision"], self.policy.max_volume, float(scan["atr"]))
        self._check_request(mt5, request)
        proposal_id = secrets.token_urlsafe(10)
        phrase = f"DEMO-{proposal_id[-6:].upper()}"
        proposal = PendingProposal(proposal_id, request, phrase, time.time() + self.policy.proposal_ttl_seconds)
        self.proposals[proposal_id] = proposal
        safe = {"proposal_id": proposal_id, "symbol": request["symbol"], "direction": scan["decision"], "volume": request["volume"], "price": request["price"], "sl": request["sl"], "tp": request["tp"], "expires_in_seconds": self.policy.proposal_ttl_seconds, "confirmation_phrase": phrase, "mode": "demo"}
        self.audit.append("proposal_created", safe)
        return safe

    def execute_proposal(self, proposal_id: str, phrase: str) -> dict[str, Any]:
        """Satu-satunya jalur entry demo; tidak tersedia kecuali opt-in lokal aktif."""
        if not self.execution_enabled:
            raise BridgeError("Eksekusi demo dinonaktifkan. Set AERO_TRADE_DEMO_EXECUTION_ENABLED=YES pada Windows lokal setelah meninjau proposal.")
        proposal = self.proposals.pop(proposal_id, None)
        if proposal is None or time.time() > proposal.expires_at:
            raise BridgeError("Proposal tidak ditemukan atau sudah kedaluwarsa.")
        if not secrets.compare_digest(phrase.strip(), proposal.phrase):
            raise BridgeError("Frasa konfirmasi proposal tidak sesuai.")
        mt5, account = self._account()
        atr_proxy = abs(float(proposal.request["price"]) - float(proposal.request["sl"])) / 1.20
        risk, block = self._risk_state(mt5, account, proposal.request["symbol"], float(proposal.request["volume"]), atr_proxy)
        if block:
            raise BridgeError(f"Order demo dibatalkan oleh guard terakhir: {block}")
        refreshed = self._trade_request(mt5, proposal.request["symbol"], "BUY" if proposal.request["type"] == mt5.ORDER_TYPE_BUY else "SELL", float(proposal.request["volume"]), atr_proxy)
        self._check_request(mt5, refreshed)
        result = mt5.order_send(refreshed)
        if result is None or getattr(result, "retcode", None) != mt5.TRADE_RETCODE_DONE:
            detail = getattr(result, "comment", mt5.last_error()) if result is not None else mt5.last_error()
            self.audit.append("order_rejected", {"proposal_id": proposal_id, "detail": str(detail)})
            raise BridgeError(f"Order demo ditolak broker: {detail}")
        response = {"ok": True, "proposal_id": proposal_id, "deal": result.deal, "order": result.order, "volume": result.volume, "price": result.price, "mode": "demo", **risk}
        self.audit.append("order_sent_demo", response)
        return response

    def close_position(self, ticket: int, phrase: str) -> dict[str, Any]:
        """Menutup satu posisi demo milik bridge; penutupan tidak tergantung kill switch."""
        if not self.execution_enabled:
            raise BridgeError("Eksekusi demo dinonaktifkan pada bridge lokal.")
        if not secrets.compare_digest(phrase.strip(), f"CLOSE-{ticket}"):
            raise BridgeError("Frasa konfirmasi close tidak sesuai.")
        mt5, _ = self._account()
        found = mt5.positions_get(ticket=ticket) or []
        if len(found) != 1 or found[0].magic != MAGIC_NUMBER:
            raise BridgeError("Posisi tidak ditemukan atau bukan posisi Aero AI Trade.")
        position = found[0]
        tick = mt5.symbol_info_tick(position.symbol)
        if tick is None:
            raise BridgeError("Tick penutupan tidak tersedia.")
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": position.ticket,
            "price": tick.bid if position.type == mt5.POSITION_TYPE_BUY else tick.ask,
            "deviation": 20,
            "magic": MAGIC_NUMBER,
            "comment": "aero-demo-close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        self._check_request(mt5, request)
        result = mt5.order_send(request)
        if result is None or getattr(result, "retcode", None) != mt5.TRADE_RETCODE_DONE:
            detail = getattr(result, "comment", mt5.last_error()) if result is not None else mt5.last_error()
            raise BridgeError(f"Close demo ditolak broker: {detail}")
        response = {"ok": True, "closed_ticket": ticket, "deal": result.deal, "order": result.order, "price": result.price, "mode": "demo"}
        self.audit.append("position_closed_demo", response)
        return response


def create_app():
    try:
        from fastapi import Depends, FastAPI, Header, HTTPException
    except ImportError as error:
        raise RuntimeError("FastAPI belum terpasang. Gunakan requirements-demo-bridge.txt pada Windows.") from error

    bridge = HeadwayDemoBridge(os.environ.get("AERO_TRADE_BRIDGE_TOKEN", ""))
    app = FastAPI(title="Aero AI Trade — Headway MT5 Demo Bridge", version="0.1.0")

    def authorize(authorization: str | None = Header(default=None)) -> None:
        try:
            bridge.authenticate(authorization)
        except BridgeError as error:
            raise HTTPException(status_code=401, detail=str(error)) from error

    @app.get("/v1/health", dependencies=[Depends(authorize)])
    def health() -> dict[str, Any]:
        return bridge.health()

    @app.post("/v1/heartbeat", dependencies=[Depends(authorize)])
    def heartbeat(payload: dict[str, str]) -> dict[str, Any]:
        return bridge.heartbeat(payload.get("source", "unknown"))

    @app.get("/v1/account", dependencies=[Depends(authorize)])
    def account() -> dict[str, Any]:
        try:
            return bridge.account()
        except BridgeError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error

    @app.get("/v1/positions", dependencies=[Depends(authorize)])
    def positions() -> dict[str, Any]:
        try:
            return bridge.positions()
        except BridgeError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error

    @app.get("/v1/history", dependencies=[Depends(authorize)])
    def history() -> dict[str, Any]:
        try:
            return bridge.history()
        except BridgeError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error

    @app.post("/v1/kill-switch", dependencies=[Depends(authorize)])
    def kill_switch(payload: dict[str, bool]) -> dict[str, Any]:
        return bridge.set_kill_switch(payload.get("active", True))

    @app.post("/v1/scalping/scan", dependencies=[Depends(authorize)])
    def scan_scalping() -> dict[str, Any]:
        try:
            return bridge.scan_scalping()
        except BridgeError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error

    @app.post("/v1/scalping/proposal", dependencies=[Depends(authorize)])
    def create_proposal() -> dict[str, Any]:
        try:
            return bridge.create_proposal()
        except BridgeError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

    @app.post("/v1/proposals/{proposal_id}/execute", dependencies=[Depends(authorize)])
    def execute_proposal(proposal_id: str, payload: dict[str, str]) -> dict[str, Any]:
        try:
            return bridge.execute_proposal(proposal_id, payload.get("confirmation_phrase", ""))
        except BridgeError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

    @app.post("/v1/positions/{ticket}/close", dependencies=[Depends(authorize)])
    def close_position(ticket: int, payload: dict[str, str]) -> dict[str, Any]:
        try:
            return bridge.close_position(ticket, payload.get("confirmation_phrase", ""))
        except BridgeError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(create_app(), host="127.0.0.1", port=8765, log_level="info")
