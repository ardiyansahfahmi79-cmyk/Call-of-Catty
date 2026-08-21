"""Mesin data market publik dan indikator teknikal untuk prototipe Call-of-Catty.

Sumber default memakai yfinance/Yahoo Finance tanpa API key untuk riset dan edukasi.
Data dapat tertunda, tidak ber-SLA, dan bukan harga eksekusi broker.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class Instrument:
    code: str
    label: str
    yahoo_symbol: str
    asset_class: str
    aliases: tuple[str, ...]
    note: str = ""


INSTRUMENTS: tuple[Instrument, ...] = (
    Instrument("XAUUSD", "Gold / US Dollar", "GC=F", "Komoditas", ("xauusd", "xau/usd", "gold", "emas", "xau"), "Proxy COMEX Gold Futures (GC=F), bukan spot broker."),
    Instrument("XAGUSD", "Silver / US Dollar", "SI=F", "Komoditas", ("xagusd", "xag/usd", "silver", "perak", "xag"), "Proxy COMEX Silver Futures (SI=F)."),
    Instrument("EURUSD", "Euro / US Dollar", "EURUSD=X", "Forex", ("eurusd", "eur/usd", "euro dollar", "euro usd")),
    Instrument("GBPUSD", "Pound / US Dollar", "GBPUSD=X", "Forex", ("gbpusd", "gbp/usd", "pound dollar", "pound usd")),
    Instrument("USDJPY", "US Dollar / Yen", "JPY=X", "Forex", ("usdjpy", "usd/jpy", "dollar yen", "usd yen")),
    Instrument("AUDUSD", "Australian Dollar / US Dollar", "AUDUSD=X", "Forex", ("audusd", "aud/usd", "aussie")),
    Instrument("BTCUSD", "Bitcoin / US Dollar", "BTC-USD", "Kripto", ("btcusd", "btc/usd", "bitcoin", "btc")),
    Instrument("ETHUSD", "Ethereum / US Dollar", "ETH-USD", "Kripto", ("ethusd", "eth/usd", "ethereum", "eth")),
    Instrument("SOLUSD", "Solana / US Dollar", "SOL-USD", "Kripto", ("solusd", "sol/usd", "solana", "sol")),
    Instrument("WTI", "WTI Crude Oil", "CL=F", "Komoditas", ("wti", "crude oil", "minyak wti", "oil", "minyak"), "Proxy WTI futures (CL=F)."),
    Instrument("BRENT", "Brent Crude Oil", "BZ=F", "Komoditas", ("brent", "brent oil", "minyak brent"), "Proxy Brent futures (BZ=F)."),
    Instrument("DXY", "US Dollar Index", "DX-Y.NYB", "Indeks", ("dxy", "dollar index", "indeks dolar")),
    Instrument("SPX", "S&P 500", "^GSPC", "Indeks", ("spx", "sp500", "s&p 500", "s&p500", "snp500")),
    Instrument("NAS100", "Nasdaq Composite", "^IXIC", "Indeks", ("nas100", "nasdaq", "nasdaq 100")),
)

_BY_CODE = {instrument.code: instrument for instrument in INSTRUMENTS}


@dataclass
class MarketSnapshot:
    instrument: Instrument
    candles: pd.DataFrame
    indicators: dict[str, float | str]
    fetched_at: datetime
    last_candle_at: datetime
    source: str
    warning: str


def detect_instruments(question: str) -> list[Instrument]:
    """Temukan instrumen dari bahasa alami tanpa bergantung pada pilihan terminal lain."""
    normalized = re.sub(r"[^a-z0-9/=^&$\- ]", " ", question.casefold())
    matches: list[tuple[int, Instrument]] = []
    for instrument in INSTRUMENTS:
        for alias in instrument.aliases:
            position = normalized.find(alias.casefold())
            if position >= 0:
                matches.append((position, instrument))
                break
    matches.sort(key=lambda item: item[0])
    unique: list[Instrument] = []
    for _, instrument in matches:
        if instrument not in unique:
            unique.append(instrument)
    return unique


def instrument_from_code(code: str) -> Instrument | None:
    return _BY_CODE.get(code.upper())


def _period_for_interval(interval: str) -> str:
    return {"15m": "30d", "1h": "60d", "1d": "2y"}.get(interval, "60d")


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


def calculate_indicators(candles: pd.DataFrame) -> dict[str, float | str]:
    close = candles["close"]
    high = candles["high"]
    low = candles["low"]
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
    ret = close.pct_change()
    volatility = ret.rolling(20, min_periods=10).std() * (252**0.5) * 100
    change_1 = ((close.iloc[-1] / close.iloc[-2]) - 1) * 100 if len(close) > 1 else 0.0
    change_20 = ((close.iloc[-1] / close.iloc[-21]) - 1) * 100 if len(close) > 20 else 0.0
    last = float(close.iloc[-1])
    ma50_value = float(ma50.iloc[-1]) if pd.notna(ma50.iloc[-1]) else last
    ma200_value = float(ma200.iloc[-1]) if pd.notna(ma200.iloc[-1]) else last
    rsi_value = float(_rsi(close).iloc[-1])
    macd_value = float(macd.iloc[-1])
    signal_value = float(signal.iloc[-1])
    votes = [last > ma20.iloc[-1], last > ma50_value, last > ma200_value, rsi_value >= 52, macd_value > signal_value]
    bearish_votes = [last < ma20.iloc[-1], last < ma50_value, last < ma200_value, rsi_value <= 48, macd_value < signal_value]
    if sum(votes) >= 4:
        bias = "BUY"
    elif sum(bearish_votes) >= 4:
        bias = "SELL"
    else:
        bias = "NEUTRAL"
    confidence = round(max(sum(votes), sum(bearish_votes)) / 5 * 100)
    return {
        "price": last,
        "change_1": float(change_1),
        "change_20": float(change_20),
        "ma20": float(ma20.iloc[-1]) if pd.notna(ma20.iloc[-1]) else last,
        "ma50": ma50_value,
        "ma200": ma200_value,
        "rsi14": rsi_value,
        "macd": macd_value,
        "macd_signal": signal_value,
        "atr14": float(atr.iloc[-1]) if pd.notna(atr.iloc[-1]) else 0.0,
        "high20": float(high.tail(20).max()),
        "low20": float(low.tail(20).min()),
        "volatility20": float(volatility.iloc[-1]) if pd.notna(volatility.iloc[-1]) else 0.0,
        "bias": bias,
        "confluence": confidence,
    }


def fetch_market_snapshot(instrument: Instrument, interval: str = "1h") -> MarketSnapshot:
    """Ambil OHLCV aktual dari yfinance tanpa membangkitkan data sintetis jika sumber gagal."""
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError("Library yfinance belum terpasang. Jalankan pip install -r requirements.txt.") from exc
    try:
        frame = yf.download(
            instrument.yahoo_symbol,
            period=_period_for_interval(interval),
            interval=interval,
            auto_adjust=False,
            progress=False,
            threads=False,
        )
    except Exception as exc:
        raise RuntimeError(f"Gagal menghubungi sumber data: {exc}") from exc
    candles = _normalize_history(frame)
    if len(candles) < 55:
        raise RuntimeError("Sumber data belum mengembalikan cukup candle untuk analisis indikator.")
    warning = "Data publik untuk riset/edukasi; dapat tertunda dan bukan harga eksekusi broker."
    if instrument.note:
        warning = f"{instrument.note} {warning}"
    return MarketSnapshot(
        instrument=instrument,
        candles=candles,
        indicators=calculate_indicators(candles),
        fetched_at=datetime.now(timezone.utc),
        last_candle_at=candles.index[-1].to_pydatetime(),
        source=f"Yahoo Finance chart via yfinance · {instrument.yahoo_symbol}",
        warning=warning,
    )


def normalized_comparison(snapshots: Iterable[MarketSnapshot]) -> pd.DataFrame:
    frames: list[pd.Series] = []
    for snapshot in snapshots:
        series = snapshot.candles["close"].rename(snapshot.instrument.code).dropna()
        if not series.empty:
            frames.append((series / series.iloc[0] * 100).rename(snapshot.instrument.code))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, axis=1).dropna(how="all").ffill()
