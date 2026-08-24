"""Kontrak 22 keluarga respons × 50 variasi yang stabil dan bebas jargon internal."""

from __future__ import annotations

from response_variations import RESPONSE_VARIANTS, response_variant_at, response_variant_count, select_response_variant


def run() -> None:
    assert len(RESPONSE_VARIANTS) == 22, len(RESPONSE_VARIANTS)
    prohibited = ("pipeline", "python data engine", "traceable context", "yfinance", "yahoo finance", "gc=f")
    audited = 0
    for family, variants in RESPONSE_VARIANTS.items():
        assert response_variant_count(family) == 50, (family, response_variant_count(family))
        assert len(set(variants)) == 50, family
        for index in range(50):
            copy = response_variant_at(family, index)
            assert copy == variants[index], (family, index)
            assert all(token not in copy.casefold() for token in prohibited), (family, copy)
            audited += 1
        key = f"{family}|uji stabil"
        assert select_response_variant(family, key) == select_response_variant(family, key), family
    print(f"response_variation_ok=families:{len(RESPONSE_VARIANTS)} variants:{audited}")


if __name__ == "__main__":
    run()
