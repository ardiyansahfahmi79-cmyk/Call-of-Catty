"""Audit kontrak UI AMI tanpa menjalankan browser atau memodifikasi sesi pengguna."""

from __future__ import annotations

from pathlib import Path

from streamlit_app import (
    MIN_ANALYSIS_SECONDS,
    _loader_markup,
    resolve_confirmation_context,
    resolve_thread_context,
    select_stable_prompt_chips,
    should_show_opening_suggestions,
)


def run() -> None:
    assert MIN_ANALYSIS_SECONDS == 13, MIN_ANALYSIS_SECONDS
    markup = _loader_markup("Merangkum informasi yang tersedia", 92)
    assert "Merangkum informasi yang tersedia" in markup
    for forbidden in ("PIPELINE", "EST.", "PYTHON DATA ENGINE", "TRACEABLE CONTEXT"):
        assert forbidden not in markup.upper(), forbidden
    prompts = [f"Prompt {position}" for position in range(8)]
    cache: dict = {}
    first = select_stable_prompt_chips(cache, "audit", prompts)
    second = select_stable_prompt_chips(cache, "audit", prompts)
    assert len(first) == 3 and first == second and all(item in prompts for item in first), (first, second)
    confirmation = resolve_confirmation_context("iya", {"instrument": "XAUUSD", "interval": "1h"})
    assert confirmation == "Analisa XAUUSD pada timeframe 1h", confirmation
    follow_up = resolve_thread_context("tentukan entry", {"instrument": "EURUSD", "interval": "4h"})
    assert follow_up == "Tentukan Entry, SL, TP1 TP2 TP3 dan Risk untuk EURUSD pada timeframe 4h", follow_up
    assert should_show_opening_suggestions([])
    assert not should_show_opening_suggestions([{"role": "user", "content": "Analisa EURUSD"}])
    source = Path("streamlit_app.py").read_text(encoding="utf-8")
    for expected in (
        '"staticPlot": True',
        '"displayModeBar": False',
        '"scrollZoom": False',
        "pointer-events:none",
        "queue_question(question)",
        "stable_prompt_chips.pop(scope, None)",
        "for message in st.session_state.messages:",
        "process_question(pending_question, loader_slot)",
    ):
        assert expected in source, expected
    print(f"ui_contract_ok=loader:{MIN_ANALYSIS_SECONDS}s chips:{len(first)} static_chart:yes")


if __name__ == "__main__":
    run()
