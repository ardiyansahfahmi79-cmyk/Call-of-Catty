"""Router intent market lokal yang dapat diaudit dan tidak menghasilkan analisis pasar sendiri."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
import re


INTENT_FILE = Path(__file__).with_name("market_intents.json")


@dataclass(frozen=True)
class IntentResolution:
    name: str
    score: int
    matched_patterns: tuple[str, ...]


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


@lru_cache(maxsize=1)
def load_intent_registry() -> tuple[dict, ...]:
    """Muat registry statis sekali per proses; kegagalan file tidak mengubah fallback Aero AI."""
    try:
        payload = json.loads(INTENT_FILE.read_text(encoding="utf-8"))
        intents = payload.get("intents", [])
        if not isinstance(intents, list):
            return ()
        return tuple(item for item in intents if isinstance(item, dict) and item.get("name") and item.get("patterns"))
    except (OSError, ValueError, TypeError):
        return ()


def resolve_local_intent(question: str) -> IntentResolution | None:
    """Pilih intent dari frasa eksplisit; frasa panjang diberi bobot lebih tinggi daripada token tunggal."""
    text = _normalized(question)
    if not text:
        return None
    candidates: list[tuple[int, int, str, tuple[str, ...]]] = []
    for item in load_intent_registry():
        matches: list[str] = []
        score = 0
        for raw_pattern in item["patterns"]:
            pattern = _normalized(str(raw_pattern))
            if not pattern:
                continue
            bounded = rf"(?<![a-z0-9]){re.escape(pattern)}(?![a-z0-9])"
            if re.search(bounded, text):
                matches.append(pattern)
                score += 3 if " " in pattern else 1
        if score:
            candidates.append((score, int(item.get("priority", 0)), str(item["name"]), tuple(matches)))
    if not candidates:
        return None
    candidates.sort(key=lambda row: (-row[0], -row[1], row[2]))
    score, _, name, matches = candidates[0]
    return IntentResolution(name=name, score=score, matched_patterns=matches)
