"""Mesin data harga publik dan indikator Python berlapis untuk Aero AI.

Sumber default memakai yfinance/Yahoo Finance tanpa API key untuk riset dan
edukasi. Data dapat tertunda, tidak ber-SLA, dan bukan harga eksekusi broker.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Iterable

import pandas as pd
import requests


@dataclass(frozen=True)
class Instrument:
    code: str
    label: str
    yahoo_symbol: str
    asset_class: str
    aliases: tuple[str, ...]
    note: str = ""


INSTRUMENTS: tuple[Instrument, ...] = (
    Instrument("XAUUSD", "Gold / US Dollar", "GC=F", "Komoditas", ("xauusd", "xau/usd", "gold", "emas", "emas dunia", "harga emas", "gold price", "xau"), "Proxy COMEX Gold Futures (GC=F), bukan spot broker."),
    Instrument("XAGUSD", "Silver / US Dollar", "SI=F", "Komoditas", ("xagusd", "xag/usd", "silver", "perak", "xag"), "Proxy COMEX Silver Futures (SI=F)."),
    Instrument("XAUEUR", "Gold / Euro", "XAUEUR=X", "Komoditas", ("xaueur", "xau/eur", "gold eur", "emas euro"), "Quote publik XAUEUR; ketersediaan bergantung pada Yahoo Finance."),
    Instrument("XAGEUR", "Silver / Euro", "XAGEUR=X", "Komoditas", ("xageur", "xag/eur", "silver eur", "perak euro"), "Quote publik XAGEUR; ketersediaan bergantung pada Yahoo Finance."),
    Instrument("XBRUSD", "Brent Crude Oil / US Dollar", "BZ=F", "Komoditas", ("xbrusd", "xbr/usd"), "Proxy Brent futures (BZ=F)."),
    Instrument("XNGUSD", "Natural Gas / US Dollar", "NG=F", "Komoditas", ("xngusd", "xng/usd", "natural gas", "gas alam"), "Proxy Henry Hub Natural Gas futures (NG=F)."),
    Instrument("XPDUSD", "Palladium / US Dollar", "PA=F", "Komoditas", ("xpdusd", "xpd/usd", "palladium", "paladium"), "Proxy Palladium futures (PA=F)."),
    Instrument("EURUSD", "Euro / US Dollar", "EURUSD=X", "Forex", ("eurusd", "eur/usd", "euro dollar", "euro usd")),
    Instrument("GBPUSD", "Pound / US Dollar", "GBPUSD=X", "Forex", ("gbpusd", "gbp/usd", "pound dollar", "pound usd")),
    Instrument("USDJPY", "US Dollar / Yen", "JPY=X", "Forex", ("usdjpy", "usd/jpy", "dollar yen", "usd yen")),
    Instrument("AUDUSD", "Australian Dollar / US Dollar", "AUDUSD=X", "Forex", ("audusd", "aud/usd", "aussie")),
    Instrument("USDCAD", "US Dollar / Canadian Dollar", "CAD=X", "Forex", ("usdcad", "usd/cad", "dollar cad")),
    Instrument("USDCHF", "US Dollar / Swiss Franc", "CHF=X", "Forex", ("usdchf", "usd/chf", "dollar franc")),
    Instrument("NZDUSD", "New Zealand Dollar / US Dollar", "NZDUSD=X", "Forex", ("nzdusd", "nzd/usd", "kiwi dollar")),
    Instrument("EURGBP", "Euro / Pound", "EURGBP=X", "Forex", ("eurgbp", "eur/gbp", "euro pound")),
    Instrument("EURJPY", "Euro / Yen", "EURJPY=X", "Forex", ("eurjpy", "eur/jpy", "euro yen")),
    Instrument("GBPJPY", "Pound / Yen", "GBPJPY=X", "Forex", ("gbpjpy", "gbp/jpy", "pound yen")),
    Instrument("BTCUSD", "Bitcoin / US Dollar", "BTC-USD", "Kripto", ("btcusd", "btc/usd", "bitcoin", "btc")),
    Instrument("ETHUSD", "Ethereum / US Dollar", "ETH-USD", "Kripto", ("ethusd", "eth/usd", "ethereum", "eth")),
    Instrument("BNBUSD", "BNB / US Dollar", "BNB-USD", "Kripto", ("bnbusd", "bnb/usd", "bnb")),
    Instrument("SOLUSD", "Solana / US Dollar", "SOL-USD", "Kripto", ("solusd", "sol/usd", "solana", "sol")),
    Instrument("XRPUSD", "XRP / US Dollar", "XRP-USD", "Kripto", ("xrpusd", "xrp/usd", "xrp", "ripple")),
    Instrument("ADAUSD", "Cardano / US Dollar", "ADA-USD", "Kripto", ("adausd", "ada/usd", "cardano", "ada")),
    Instrument("DOTUSD", "Polkadot / US Dollar", "DOT-USD", "Kripto", ("dotusd", "dot/usd", "polkadot", "dot")),
    Instrument("MATICUSD", "Polygon / US Dollar", "MATIC-USD", "Kripto", ("maticusd", "matic/usd", "polygon", "matic")),
    Instrument("LINKUSD", "Chainlink / US Dollar", "LINK-USD", "Kripto", ("linkusd", "link/usd", "chainlink", "link")),
    Instrument("AVAXUSD", "Avalanche / US Dollar", "AVAX-USD", "Kripto", ("avaxusd", "avax/usd", "avalanche", "avax")),
    Instrument("WTI", "WTI Crude Oil", "CL=F", "Komoditas", ("wti", "crude oil", "minyak wti", "oil", "minyak"), "Proxy WTI futures (CL=F)."),
    Instrument("BRENT", "Brent Crude Oil", "BZ=F", "Komoditas", ("brent", "brent oil", "minyak brent"), "Proxy Brent futures (BZ=F)."),
    Instrument("DXY", "US Dollar Index", "DX-Y.NYB", "Indeks", ("dxy", "dollar index", "indeks dolar")),
    Instrument("SPX", "S&P 500", "^GSPC", "Indeks", ("spx", "sp500", "s&p 500", "s&p500", "snp500")),
    Instrument("NAS100", "Nasdaq Composite", "^IXIC", "Indeks", ("nas100", "nasdaq", "nasdaq 100")),
    Instrument("IHSG", "Indeks Harga Saham Gabungan", "^JKSE", "Indeks", ("ihsg", "jakarta composite", "idx composite")),
    Instrument("BBCA", "Bank Central Asia", "BBCA.JK", "Saham IDX", ("bbca", "bank bca")),
    Instrument("BBRI", "Bank Rakyat Indonesia", "BBRI.JK", "Saham IDX", ("bbri", "bank bri")),
    Instrument("TLKM", "Telkom Indonesia", "TLKM.JK", "Saham IDX", ("tlkm", "telkom")),
    Instrument("ASII", "Astra International", "ASII.JK", "Saham IDX", ("asii", "astra")),
    Instrument("BMRI", "Bank Mandiri", "BMRI.JK", "Saham IDX", ("bmri", "bank mandiri")),
    Instrument("UNVR", "Unilever Indonesia", "UNVR.JK", "Saham IDX", ("unvr", "unilever")),
    Instrument("GGRM", "Gudang Garam", "GGRM.JK", "Saham IDX", ("ggrm", "gudang garam")),
    Instrument("HMSP", "HM Sampoerna", "HMSP.JK", "Saham IDX", ("hmsp", "sampoerna")),
    Instrument("ANTM", "Aneka Tambang", "ANTM.JK", "Saham IDX", ("antm", "antam", "aneka tambang")),
)

# Pemetaan ini hanya menyatakan sisi mata uang/ekonomi yang dapat dipakai sebagai
# filter agenda. Pemetaan tidak menyimpulkan arah harga ataupun dampak rilis.
_INSTRUMENT_ECONOMIC_CURRENCIES: dict[str, tuple[str, ...]] = {
    "XAUUSD": ("USD",), "XAGUSD": ("USD",), "XAUEUR": ("EUR",), "XAGEUR": ("EUR",),
    "XBRUSD": ("USD",), "XNGUSD": ("USD",), "XPDUSD": ("USD",),
    "EURUSD": ("EUR", "USD"), "GBPUSD": ("GBP", "USD"), "USDJPY": ("USD", "JPY"),
    "AUDUSD": ("AUD", "USD"), "USDCAD": ("USD", "CAD"), "USDCHF": ("USD", "CHF"),
    "NZDUSD": ("NZD", "USD"), "EURGBP": ("EUR", "GBP"), "EURJPY": ("EUR", "JPY"),
    "GBPJPY": ("GBP", "JPY"),
    "BTCUSD": ("USD",), "ETHUSD": ("USD",), "BNBUSD": ("USD",), "SOLUSD": ("USD",),
    "XRPUSD": ("USD",), "ADAUSD": ("USD",), "DOTUSD": ("USD",), "MATICUSD": ("USD",),
    "LINKUSD": ("USD",), "AVAXUSD": ("USD",),
    "WTI": ("USD",), "BRENT": ("USD",), "DXY": ("USD",), "SPX": ("USD",), "NAS100": ("USD",),
    "IHSG": ("IDR",), "BBCA": ("IDR",), "BBRI": ("IDR",), "TLKM": ("IDR",), "ASII": ("IDR",),
    "BMRI": ("IDR",), "UNVR": ("IDR",), "GGRM": ("IDR",), "HMSP": ("IDR",), "ANTM": ("IDR",),
}


def instrument_economic_currencies(instrument_code: str) -> tuple[str, ...]:
    """Kembalikan mata uang ekonomi terkait tanpa menebak negara atau sentimen."""
    return _INSTRUMENT_ECONOMIC_CURRENCIES.get(instrument_code.upper(), ())


_BY_CODE = {instrument.code: instrument for instrument in INSTRUMENTS}
_CRYPTO_COIN_IDS = {
    "BTCUSD": "bitcoin", "ETHUSD": "ethereum", "BNBUSD": "binancecoin", "SOLUSD": "solana",
    "XRPUSD": "ripple", "ADAUSD": "cardano", "DOTUSD": "polkadot", "MATICUSD": "matic-network",
    "LINKUSD": "chainlink", "AVAXUSD": "avalanche-2",
}
_TIMEFRAME_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("15m", (r"\b(?:m15|15m|15\s*(?:menit|minute|minutes|min))\b",)),
    ("30m", (r"\b(?:m30|30m|30\s*(?:menit|minute|minutes|min))\b",)),
    ("1h", (r"\b(?:h1|1h|1\s*(?:jam|hour|hours))\b",)),
    ("2h", (r"\b(?:h2|2h|2\s*(?:jam|hour|hours))\b",)),
    ("3h", (r"\b(?:h3|3h|3\s*(?:jam|hour|hours))\b",)),
    ("4h", (r"\b(?:h4|4h|4\s*(?:jam|hour|hours))\b",)),
    ("5h", (r"\b(?:h5|5h|5\s*(?:jam|hour|hours))\b",)),
    ("6h", (r"\b(?:h6|6h|6\s*(?:jam|hour|hours))\b",)),
    ("7h", (r"\b(?:h7|7h|7\s*(?:jam|hour|hours))\b",)),
    ("8h", (r"\b(?:h8|8h|8\s*(?:jam|hour|hours))\b",)),
    ("9h", (r"\b(?:h9|9h|9\s*(?:jam|hour|hours))\b",)),
    ("10h", (r"\b(?:h10|10h|10\s*(?:jam|hour|hours))\b",)),
    ("11h", (r"\b(?:h11|11h|11\s*(?:jam|hour|hours))\b",)),
    ("12h", (r"\b(?:h12|12h|12\s*(?:jam|hour|hours))\b",)),
    ("1d", (r"\b(?:d1|1d|daily|harian|1\s*(?:hari|day|days))\b",)),
    ("1wk", (r"\b(?:w1|1w|1wk|weekly|mingguan|1\s*(?:minggu|week|weeks))\b",)),
    ("1mo", (r"\b(?:mn|month|monthly|bulan|bulanan|1\s*(?:bulan|month|months))\b",)),
)
_TIMEFRAME_LABELS = {
    "15m": "M15", "30m": "M30", "1h": "H1", "2h": "H2", "3h": "H3", "4h": "H4",
    "5h": "H5", "6h": "H6", "7h": "H7", "8h": "H8", "9h": "H9", "10h": "H10",
    "11h": "H11", "12h": "H12", "1d": "D1", "1wk": "W1", "1mo": "MN",
}


@dataclass
class MarketSnapshot:
    instrument: Instrument
    candles: pd.DataFrame
    indicators: dict[str, float | str | dict[str, str]]
    fetched_at: datetime
    last_candle_at: datetime
    source: str
    warning: str
    interval: str = "1h"


def detect_instruments(question: str) -> list[Instrument]:
    """Temukan instrumen dari bahasa alami tanpa bergantung pada terminal lain."""
    normalized = re.sub(r"[^a-z0-9/=^&$\- ]", " ", question.casefold())
    # Menyatukan hanya pasangan kode yang memang terdaftar, sehingga `xau usd`,
    # `EUR / USD`, dan kapitalisasi apa pun terbaca tanpa menggabungkan kata umum.
    for instrument in INSTRUMENTS:
        if len(instrument.code) != 6 or not instrument.code.isalnum():
            continue
        left, right = instrument.code[:3].casefold(), instrument.code[3:].casefold()
        pattern = rf"(?<![a-z0-9]){left}\s*[/_\- ]?\s*{right}(?![a-z0-9])"
        normalized = re.sub(pattern, instrument.code.casefold(), normalized)
    matches: list[tuple[int, int, Instrument]] = []
    for instrument in INSTRUMENTS:
        alias_matches = [
            (matched.start(), -len(alias))
            for alias in instrument.aliases
            if (matched := re.search(rf"(?<![a-z0-9]){re.escape(alias.casefold())}(?![a-z0-9])", normalized))
        ]
        if alias_matches:
            # Pilih alias terawal; bila posisi sama, ambil frase terpanjang.
            # Ini menjaga `gold eur` dan `minyak brent` lebih spesifik daripada
            # alias umum `gold` atau `minyak`.
            start, specificity = min(alias_matches)
            matches.append((start, specificity, instrument))
    matches.sort(key=lambda item: (item[0], item[1]))
    unique: list[Instrument] = []
    for _, _, instrument in matches:
        if instrument not in unique:
            unique.append(instrument)
    return unique


def detect_unknown_instrument_candidates(question: str) -> list[str]:
    """Temukan kode pair yang tampak eksplisit tetapi belum tersedia di daftar instrumen."""
    ignored = {"ANALISA", "ANALYZE", "TIMEFRAME", "INSTRUMEN", "FORECAST", "ACTUAL", "PREVIOUS", "RETAIL", "SALES", "PREDIKSI"}
    candidates: list[str] = []
    for raw in re.findall(r"\b[A-Za-z]{5,8}\b", question):
        code = raw.upper()
        looks_like_pair = code.startswith("X") or code.endswith(("USD", "EUR", "JPY", "GBP", "CAD", "CHF", "NZD"))
        if looks_like_pair and code not in _BY_CODE and code not in ignored and code not in candidates:
            candidates.append(code)
    return candidates


def _matched_timeframe(question: str) -> str | None:
    normalized = question.casefold().replace("-", " ")
    for interval, patterns in _TIMEFRAME_RULES:
        if any(re.search(pattern, normalized) for pattern in patterns):
            return interval
    return None


def detect_timeframe(question: str) -> str:
    """Baca timeframe dari pesan pengguna tanpa menampilkan pemilih timeframe."""
    return _matched_timeframe(question) or "1h"


def timeframe_was_explicit(question: str) -> bool:
    """Tandai apakah timeframe tertulis eksplisit agar asumsi H1 dapat dijelaskan."""
    return _matched_timeframe(question) is not None


def timeframe_label(interval: str) -> str:
    return _TIMEFRAME_LABELS.get(interval, interval.upper())


def instrument_from_code(code: str) -> Instrument | None:
    return _BY_CODE.get(code.upper())


def _period_for_interval(interval: str) -> str:
    if interval in {"15m", "30m"}:
        return "30d" if interval == "15m" else "60d"
    if interval.endswith("h"):
        return "60d"
    return {"1d": "2y", "1wk": "10y", "1mo": "max"}.get(interval, "60d")


def _resample_to_hours(candles: pd.DataFrame, hours: int) -> pd.DataFrame:
    """Bangun candle H2–H12 dari candle H1 publik, tanpa membuat harga sintetis."""
    if candles.empty:
        return candles
    aggregated = candles.resample(f"{hours}h").agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    return aggregated.dropna(subset=["open", "high", "low", "close"])


def _normalize_history(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)
    frame.columns = [str(column).lower() for column in frame.columns]
    needed = ["open", "high", "low", "close"]
    if any(column not in frame.columns for column in needed):
        return pd.DataFrame()
    if "volume" not in frame.columns:
        frame["volume"] = 0.0
    frame = frame[needed + ["volume"]].apply(pd.to_numeric, errors="coerce").dropna(subset=needed)
    frame.index = pd.to_datetime(frame.index, utc=True)
    return frame[~frame.index.duplicated(keep="last")].sort_index()


def _rsi(close: pd.Series, length: int = 14) -> pd.Series:
    diff = close.diff()
    gain = diff.clip(lower=0).ewm(alpha=1 / length, adjust=False).mean()
    loss = (-diff.clip(upper=0)).ewm(alpha=1 / length, adjust=False).mean()
    ratio = gain / loss.replace(0, pd.NA)
    return (100 - (100 / (1 + ratio))).fillna(50.0)


def _adx(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(0.0, index=high.index).where(~((up_move > down_move) & (up_move > 0)), up_move)
    minus_dm = pd.Series(0.0, index=high.index).where(~((down_move > up_move) & (down_move > 0)), down_move)
    previous_close = close.shift(1)
    true_range = pd.concat([high - low, (high - previous_close).abs(), (low - previous_close).abs()], axis=1).max(axis=1)
    atr = true_range.ewm(alpha=1 / length, adjust=False).mean().replace(0, pd.NA)
    plus_di = 100 * plus_dm.ewm(alpha=1 / length, adjust=False).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1 / length, adjust=False).mean() / atr
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, pd.NA)).fillna(0.0)
    return dx.ewm(alpha=1 / length, adjust=False).mean().fillna(0.0)


def _state(value: bool, opposite: bool) -> str:
    if value:
        return "BUY"
    if opposite:
        return "SELL"
    return "NEUTRAL"


def _market_state(bullish_votes: int, bearish_votes: int) -> str:
    if bullish_votes >= 6:
        return "STRONG BULLISH"
    if bullish_votes >= 4:
        return "BULLISH"
    if bearish_votes >= 6:
        return "STRONG BEARISH"
    if bearish_votes >= 4:
        return "BEARISH"
    return "NEUTRAL"


def calculate_indicators(candles: pd.DataFrame) -> dict[str, float | str | dict[str, str]]:
    """Hitung indikator tanpa mengubahnya menjadi klaim prediksi."""
    close, high, low, volume = candles["close"], candles["high"], candles["low"], candles["volume"]
    ma20 = close.rolling(20, min_periods=10).mean()
    ma50 = close.rolling(50, min_periods=20).mean()
    ma200 = close.rolling(200, min_periods=50).mean()
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    previous_close = close.shift(1)
    true_range = pd.concat([high - low, (high - previous_close).abs(), (low - previous_close).abs()], axis=1).max(axis=1)
    atr = true_range.rolling(14, min_periods=7).mean()
    volatility = close.pct_change().rolling(20, min_periods=10).std() * (252**0.5) * 100
    adx = _adx(high, low, close)
    volume_average = volume.rolling(20, min_periods=10).mean()
    relative_volume = float(volume.iloc[-1] / volume_average.iloc[-1]) if pd.notna(volume_average.iloc[-1]) and volume_average.iloc[-1] > 0 else 0.0
    swing_low, swing_high = float(low.tail(60).min()), float(high.tail(60).max())
    fib_618 = swing_low + (swing_high - swing_low) * 0.618
    change_1 = ((close.iloc[-1] / close.iloc[-2]) - 1) * 100 if len(close) > 1 else 0.0
    change_20 = ((close.iloc[-1] / close.iloc[-21]) - 1) * 100 if len(close) > 20 else 0.0
    last = float(close.iloc[-1])
    ma20_value = float(ma20.iloc[-1]) if pd.notna(ma20.iloc[-1]) else last
    ma50_value = float(ma50.iloc[-1]) if pd.notna(ma50.iloc[-1]) else last
    ma200_value = float(ma200.iloc[-1]) if pd.notna(ma200.iloc[-1]) else last
    rsi_value, macd_value, signal_value = float(_rsi(close).iloc[-1]), float(macd.iloc[-1]), float(signal.iloc[-1])
    adx_value = float(adx.iloc[-1]) if pd.notna(adx.iloc[-1]) else 0.0
    high20, low20 = float(high.tail(20).max()), float(low.tail(20).min())
    bullish = [last > ma20_value, last > ma50_value, last > ma200_value, rsi_value >= 52, macd_value > signal_value, last >= fib_618, last >= (high20 + low20) / 2]
    bearish = [last < ma20_value, last < ma50_value, last < ma200_value, rsi_value <= 48, macd_value < signal_value, last < fib_618, last < (high20 + low20) / 2]
    bullish_votes, bearish_votes = sum(bullish), sum(bearish)
    bias = "BUY" if bullish_votes >= 5 else "SELL" if bearish_votes >= 5 else "NEUTRAL"
    states = {
        "Harga vs MA 20": _state(last > ma20_value, last < ma20_value),
        "Harga vs MA 50": _state(last > ma50_value, last < ma50_value),
        "Harga vs MA 200": _state(last > ma200_value, last < ma200_value),
        "RSI 14": "BUY" if rsi_value >= 52 else "SELL" if rsi_value <= 48 else "NEUTRAL",
        "MACD": _state(macd_value > signal_value, macd_value < signal_value),
        "ADX 14": "BUY" if adx_value >= 25 and last > ma50_value else "SELL" if adx_value >= 25 and last < ma50_value else "NEUTRAL",
        "Volume relatif": "BUY" if relative_volume >= 1.2 and change_1 > 0 else "SELL" if relative_volume >= 1.2 and change_1 < 0 else "NEUTRAL",
        "Fibonacci 61.8%": _state(last >= fib_618, last < fib_618),
        "High 20": "BUY" if last >= high20 else "NEUTRAL",
        "Low 20": "SELL" if last <= low20 else "NEUTRAL",
    }
    return {
        "price": last, "change_1": float(change_1), "change_20": float(change_20),
        "ma20": ma20_value, "ma50": ma50_value, "ma200": ma200_value,
        "rsi14": rsi_value, "macd": macd_value, "macd_signal": signal_value,
        "atr14": float(atr.iloc[-1]) if pd.notna(atr.iloc[-1]) else 0.0,
        "adx14": adx_value, "relative_volume": relative_volume, "fib618": fib_618,
        "high20": high20, "low20": low20,
        "volatility20": float(volatility.iloc[-1]) if pd.notna(volatility.iloc[-1]) else 0.0,
        "bias": bias, "market_state": _market_state(bullish_votes, bearish_votes),
        "confluence": round(max(bullish_votes, bearish_votes) / 7 * 100), "indicator_states": states,
    }


def _fetch_coingecko_ohlc(instrument: Instrument, interval: str) -> pd.DataFrame:
    """Fallback OHLC publik untuk kripto tanpa membangkitkan candle sintetis."""
    coin_id = _CRYPTO_COIN_IDS.get(instrument.code)
    if not coin_id:
        return pd.DataFrame()
    try:
        days = "30" if interval in {"15m", "30m"} or interval.endswith("h") else "365"
        response = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc",
            params={"vs_currency": "usd", "days": days},
            timeout=8,
            headers={"Accept": "application/json", "User-Agent": "AeroAI-Research/1.0"},
        )
        response.raise_for_status()
        rows = response.json()
        frame = pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close"])
        if frame.empty:
            return pd.DataFrame()
        frame["volume"] = 0.0
        frame.index = pd.to_datetime(frame.pop("timestamp"), unit="ms", utc=True)
        return frame[["open", "high", "low", "close", "volume"]].apply(pd.to_numeric, errors="coerce").dropna()
    except (ImportError, ValueError, TypeError, KeyError, requests.RequestException):
        return pd.DataFrame()


def fetch_market_snapshot(instrument: Instrument, interval: str = "1h") -> MarketSnapshot:
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError("Library yfinance belum terpasang. Jalankan pip install -r requirements.txt.") from exc
    requested_interval = interval if interval in _TIMEFRAME_LABELS else "1h"
    hour_match = re.fullmatch(r"(\d+)h", requested_interval)
    resample_hours = int(hour_match.group(1)) if hour_match and requested_interval != "1h" else 0
    yahoo_interval = "1h" if resample_hours else requested_interval
    try:
        frame = yf.download(instrument.yahoo_symbol, period=_period_for_interval(requested_interval), interval=yahoo_interval, auto_adjust=False, progress=False, threads=False)
    except Exception as exc:
        raise RuntimeError(f"Gagal menghubungi sumber data: {exc}") from exc
    candles = _normalize_history(frame)
    if resample_hours:
        candles = _resample_to_hours(candles, resample_hours)
    source = f"Yahoo Finance chart via yfinance · {instrument.yahoo_symbol}"
    if resample_hours:
        source = f"{source} · candle {timeframe_label(requested_interval)} diagregasi dari H1 publik"
    if len(candles) < 55:
        fallback = _fetch_coingecko_ohlc(instrument, requested_interval)
        if len(fallback) >= 55:
            candles = fallback
            source = f"CoinGecko OHLC keyless · {_CRYPTO_COIN_IDS[instrument.code]}"
    if len(candles) < 55:
        raise RuntimeError("Sumber data belum mengembalikan cukup candle untuk analisis indikator.")
    warning = "Data publik untuk riset/edukasi; dapat tertunda dan bukan harga eksekusi broker."
    if resample_hours:
        warning = f"Timeframe {timeframe_label(requested_interval)} diagregasi dari candle H1 publik. {warning}"
    if source.startswith("CoinGecko"):
        warning = "CoinGecko keyless memiliki batas rate bersama dan candle historis; bukan feed eksekusi broker."
    if instrument.note:
        warning = f"{instrument.note} {warning}"
    return MarketSnapshot(instrument, candles, calculate_indicators(candles), datetime.now(timezone.utc), candles.index[-1].to_pydatetime(), source, warning, requested_interval)


def normalized_comparison(snapshots: Iterable[MarketSnapshot]) -> pd.DataFrame:
    frames: list[pd.Series] = []
    for snapshot in snapshots:
        series = snapshot.candles["close"].rename(snapshot.instrument.code).dropna()
        if not series.empty:
            frames.append((series / series.iloc[0] * 100).rename(snapshot.instrument.code))
    return pd.concat(frames, axis=1).dropna(how="all").ffill() if frames else pd.DataFrame()
