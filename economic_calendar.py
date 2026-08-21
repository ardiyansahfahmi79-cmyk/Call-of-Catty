"""Adapter kalender ekonomi publik untuk konteks Aero AI.

Forecast dan previous berasal dari feed kalender pihak ketiga bila tersedia. Adapter
tidak menghitung atau mengarang prediksi internal. Kolom actual hanya ditampilkan
jika disediakan feed pada saat pemindaian.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
import time
from typing import Iterable

import requests


CALENDAR_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
FALLBACK_CALENDAR_URL = "https://tradingeconomics.com/calendar"
REQUEST_TIMEOUT = 8
CACHE_TTL_SECONDS = 15 * 60
_CACHE: tuple[float, list["EconomicCalendarEvent"]] | None = None


@dataclass(frozen=True)
class EconomicCalendarEvent:
    title: str
    currency: str
    release_at: datetime | None
    impact: str
    actual: str
    forecast: str
    previous: str
    fetched_at: datetime
    source_name: str
    source_url: str


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def _fetch_weekly_json() -> list[EconomicCalendarEvent]:
    response = requests.get(
        CALENDAR_URL,
        timeout=REQUEST_TIMEOUT,
        headers={"Accept": "application/json", "User-Agent": "AeroAI-Research/1.0"},
    )
    response.raise_for_status()
    rows = response.json()
    fetched_at = _utc_now()
    events: list[EconomicCalendarEvent] = []
    for row in rows:
        title, currency, date = str(row.get("title", "")).strip(), str(row.get("country", "")).strip(), str(row.get("date", "")).strip()
        if not title or not currency or not date:
            continue
        events.append(EconomicCalendarEvent(
            title=title,
            currency=currency,
            release_at=_parse_timestamp(date),
            impact=str(row.get("impact", "Tidak diklasifikasikan")).strip() or "Tidak diklasifikasikan",
            actual=str(row.get("actual", "")).strip(),
            forecast=str(row.get("forecast", "")).strip(),
            previous=str(row.get("previous", "")).strip(),
            fetched_at=fetched_at,
            source_name="Forex Factory weekly public calendar",
            source_url=CALENDAR_URL,
        ))
    return events


def _fetch_public_html_fallback() -> list[EconomicCalendarEvent]:
    """Baca tabel kalender terbuka sebagai fallback jika ekspor JSON sedang dibatasi."""
    from bs4 import BeautifulSoup

    response = requests.get(
        FALLBACK_CALENDAR_URL,
        timeout=REQUEST_TIMEOUT,
        headers={"Accept": "text/html", "User-Agent": "AeroAI-Research/1.0"},
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    fetched_at = _utc_now()
    events: list[EconomicCalendarEvent] = []
    for link in soup.select("a.calendar-event"):
        row = link.find_parent("tr")
        currency_node = row.select_one(".calendar-iso") if row else None
        title, currency = link.get_text(" ", strip=True), currency_node.get_text(" ", strip=True) if currency_node else ""
        if not title or not currency:
            continue
        actual_node, forecast_node, previous_node = row.select_one("#actual"), row.select_one("#forecast"), row.select_one("#previous")
        events.append(EconomicCalendarEvent(
            title=title,
            currency=currency,
            release_at=None,
            impact="Tidak diklasifikasikan oleh fallback",
            actual=actual_node.get_text(" ", strip=True) if actual_node else "",
            forecast=forecast_node.get_text(" ", strip=True) if forecast_node else "",
            previous=previous_node.get_text(" ", strip=True) if previous_node else "",
            fetched_at=fetched_at,
            source_name="Trading Economics public calendar fallback",
            source_url=FALLBACK_CALENDAR_URL,
        ))
    return events


def fetch_public_calendar() -> list[EconomicCalendarEvent]:
    """Ambil kalender publik dengan cache dan fallback, tanpa mengubah nilai sumber."""
    global _CACHE
    now_monotonic = time.monotonic()
    if _CACHE and now_monotonic - _CACHE[0] < CACHE_TTL_SECONDS:
        return _CACHE[1]
    for loader in (_fetch_weekly_json, _fetch_public_html_fallback):
        try:
            events = loader()
            if events:
                _CACHE = (now_monotonic, events)
                return events
        except (requests.RequestException, ValueError, TypeError, KeyError, AttributeError):
            continue
    return _CACHE[1] if _CACHE else []


def find_calendar_events(keywords: Iterable[str], limit: int = 3) -> list[EconomicCalendarEvent]:
    """Pilih event kalender dengan kecocokan judul yang eksplisit terhadap alias agenda."""
    normalized_keywords = [_normalized(keyword) for keyword in keywords if len(_normalized(keyword)) >= 3]
    matches: list[tuple[int, EconomicCalendarEvent]] = []
    for event in fetch_public_calendar():
        title = _normalized(event.title)
        score = max((len(keyword) for keyword in normalized_keywords if keyword in title), default=0)
        if score:
            matches.append((score, event))
    far_future = datetime.max.replace(tzinfo=timezone.utc)
    matches.sort(key=lambda item: (-item[0], item[1].release_at or far_future))
    return [event for _, event in matches[:limit]]
