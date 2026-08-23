"""Regresi variasi respons NFP tanpa mempublikasikan nilai uji sebagai data pasar."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

from economic_calendar import EconomicCalendarEvent
from market_chat import _agenda_release_summary, detect_economic_agenda


def _event(actual: str, forecast: str, previous: str = "") -> EconomicCalendarEvent:
    return EconomicCalendarEvent(
        title="Non-Farm Employment Change",
        currency="USD",
        release_at=datetime(2026, 9, 4, 12, 30, tzinfo=timezone.utc),
        impact="High",
        actual=actual,
        forecast=forecast,
        previous=previous,
        fetched_at=datetime(2026, 9, 4, 12, 31, tzinfo=timezone.utc),
        source_name="Kalender publik uji",
        source_url="https://example.invalid/calendar-test",
    )


def _reply(actual: str, forecast: str, previous: str = "") -> str:
    agenda = detect_economic_agenda("NFP")
    assert agenda is not None
    with patch("market_chat.find_calendar_events", return_value=[_event(actual, forecast, previous)]):
        return _agenda_release_summary(agenda, "Jelaskan NFP untuk DXY", "DXY")


def main() -> None:
    before_release = _reply("", "nilai_konsensus_sumber", "nilai_sebelumnya_sumber")
    assert "dijadwalkan" in before_release
    assert "Actual belum tersedia" in before_release

    simultaneous = _reply("nilai_actual_sumber", "nilai_konsensus_sumber", "nilai_sebelumnya_sumber")
    assert "actual **nilai_actual_sumber**, konsensus **nilai_konsensus_sumber**" in simultaneous
    assert "Previous: **nilai_sebelumnya_sumber**" in simultaneous
    assert "Untuk DXY" in simultaneous

    no_forecast = _reply("nilai_actual_sumber", "", "nilai_sebelumnya_sumber")
    assert "Konsensus belum tersedia" in no_forecast

    for reply in (before_release, simultaneous, no_forecast):
        assert "PIPELINE" not in reply.upper()
        assert "SHADOW MODE" not in reply.upper()
        assert "ledger" not in reply.casefold()
    print("nfp_release_variants_ok=before_release,actual_with_forecast,actual_without_forecast")


if __name__ == "__main__":
    main()
