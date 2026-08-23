from __future__ import annotations

from market_chat import infer_intent
from market_intent_router import load_intent_registry, resolve_local_intent


def main() -> None:
    registry = load_intent_registry()
    assert registry
    assert all(item.get("name") and item.get("patterns") for item in registry)
    assert all("responses" not in item for item in registry)

    expected = {
        "Tentukan entry XAUUSD pada H1": "levels_entry",
        "Pasang stop loss untuk EURUSD": "levels_entry",
        "Berapa TP1 TP2 TP3 BTCUSD": "levels_entry",
        "Hitung risk reward untuk GBPJPY": "levels_entry",
        "Tinjau risiko AUDCAD pada H4": "risk",
        "Bandingkan EURUSD versus GBPUSD": "comparison",
        "Lihat tren MA 200 DXY": "trend",
        "Jelaskan sinyal market XAGUSD": "signals",
        "Konteks fundamental untuk USDJPY": "fundamental",
    }
    for question, name in expected.items():
        resolved = resolve_local_intent(question)
        assert resolved and resolved.name == name, question
        assert infer_intent(question) == name, question

    # Agenda ekonomi selalu didahulukan agar kata seperti risiko tidak mengubah fokus kalender.
    assert infer_intent("Bagaimana risiko CPI AS untuk DXY") == "economic_agenda"
    assert resolve_local_intent("sjey6wiwhsisj") is None
    print(f"local_intent_ok=patterns:{sum(len(item['patterns']) for item in registry)} cases:{len(expected) + 2}")


if __name__ == "__main__":
    main()
