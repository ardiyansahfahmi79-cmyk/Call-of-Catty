from __future__ import annotations

from datetime import datetime, timezone

from market_data import _fetch_public_pair_quote, reference_quote_freshness


def main() -> None:
    eurusd_bid, eurusd_ask, eurusd_at = _fetch_public_pair_quote("EURUSD")
    if eurusd_bid is not None and eurusd_ask is not None and eurusd_at is not None:
        assert eurusd_ask >= eurusd_bid > 0
        quote_age_seconds = (datetime.now(timezone.utc) - eurusd_at).total_seconds()
        assert 0 <= quote_age_seconds < 7 * 24 * 60 * 60
        eurusd_message = f"eurusd_mid:{(eurusd_bid + eurusd_ask) / 2:.6f} quote_age_seconds:{quote_age_seconds:.0f}"
    else:
        freshness, age = reference_quote_freshness(eurusd_at)
        assert (freshness, age) == ("TIDAK TERSEDIA", None)
        eurusd_message = "eurusd_quote_tidak_tersedia"

    xau_bid, xau_ask, xau_at = _fetch_public_pair_quote("XAUUSD")
    if xau_bid is not None and xau_ask is not None and xau_at is not None:
        assert xau_ask >= xau_bid > 0
        xau_message = f"xau_spot:{(xau_bid + xau_ask) / 2:.2f}"
    else:
        freshness, age = reference_quote_freshness(xau_at)
        assert (freshness, age) == ("TIDAK TERSEDIA", None)
        xau_message = "xau_quote_tidak_tersedia"
    print(
        "pair_quote_ok="
        f"{eurusd_message} {xau_message}"
    )


if __name__ == "__main__":
    main()
