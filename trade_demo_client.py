"""Klien HTTP minimal untuk dashboard Aero AI Trade menuju bridge demo lokal."""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class DemoBridgeError(RuntimeError):
    """Kesalahan koneksi atau respons bridge demo."""


def validate_bridge_url(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise DemoBridgeError("URL bridge harus memakai http:// atau https:// yang lengkap.")
    if parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise DemoBridgeError("Bridge HTTP hanya boleh memakai localhost; endpoint jarak jauh wajib HTTPS.")
    return value.rstrip("/")


@dataclass(frozen=True)
class DemoBridgeClient:
    base_url: str
    token: str
    timeout_seconds: int = 5

    def __post_init__(self) -> None:
        object.__setattr__(self, "base_url", validate_bridge_url(self.base_url))
        if not self.token.strip():
            raise DemoBridgeError("Token bridge demo belum tersedia di environment.")

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            try:
                detail = json.loads(error.read().decode("utf-8")).get("detail", error.reason)
            except (UnicodeDecodeError, json.JSONDecodeError):
                detail = error.reason
            raise DemoBridgeError(f"Bridge menolak permintaan: {detail}") from error
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise DemoBridgeError("Bridge demo tidak dapat dihubungi.") from error

    def heartbeat(self) -> dict:
        return self._request("POST", "/v1/heartbeat", {"source": "streamlit-panel"})

    def health(self) -> dict:
        return self._request("GET", "/v1/health")

    def account(self) -> dict:
        return self._request("GET", "/v1/account")

    def positions(self) -> dict:
        return self._request("GET", "/v1/positions")

    def history(self) -> dict:
        return self._request("GET", "/v1/history")

    def scan_scalping(self) -> dict:
        return self._request("POST", "/v1/scalping/scan", {})

    def create_scalping_proposal(self) -> dict:
        return self._request("POST", "/v1/scalping/proposal", {})

    def execute_proposal(self, proposal_id: str, confirmation_phrase: str) -> dict:
        return self._request("POST", f"/v1/proposals/{proposal_id}/execute", {"confirmation_phrase": confirmation_phrase})

    def close_position(self, ticket: int, confirmation_phrase: str) -> dict:
        return self._request("POST", f"/v1/positions/{ticket}/close", {"confirmation_phrase": confirmation_phrase})

    def set_kill_switch(self) -> dict:
        return self._request("POST", "/v1/kill-switch", {"active": True})
