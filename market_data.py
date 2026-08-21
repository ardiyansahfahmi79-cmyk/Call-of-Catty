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
    Instrument("XAUUSD", "Gold / US Dollar", "GC=F", "Komoditas", ("xauusd", "xau/usd", "gold", "emas", "xau"), "Proxy COMEX Gold Futures (GC=F), bukan spot broker."),
    Instrument("XAGUSD", "Silver / US Dollar", "SI=F", "Komoditas", ("xagusd", "xag/usd", "silver", "perak", "xag"), "Proxy COMEX Silver Futures (SI=F)."),
    Instrument("EURUSD", "Euro / US Dollar", "EURUSD=X", "Forex", ("eurusd", "eur/usd", "euro dollar", "euro usd")),
    Instrument("GBPUSD", "Pound / US Dollar", "GBPUSD=X", "Forex", ("gbpusd", "gbp/usd", "pound dollar", "pound usd")),
    Instrument("USDJPY", "US Dollar / Yen", "JPY=X", ("Forex"), ("usdjpy", "usd/jpy", "dollar yen", "usd yen")),
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
_CRYPTO_COIN_IDS = {"BTCUSD": "bitcoin", "ETHUSD": "ethereum", "SOLUSD": "solana"}


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
        days = "30" if interval in {"15m", "1h"} else "365"
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
    try:
        frame = yf.download(instrument.yahoo_symbol, period=_period_for_interval(interval), interval=interval, auto_adjust=False, progress=False, threads=False)
    except Exception as exc:
        raise RuntimeError(f"Gagal menghubungi sumber data: {exc}") from exc
    candles = _normalize_history(frame)
    source = f"Yahoo Finance chart via yfinance · {instrument.yahoo_symbol}"
    if len(candles) < 55:
        fallback = _fetch_coingecko_ohlc(instrument, interval)
        if len(fallback) >= 55:
            candles = fallback
            source = f"CoinGecko OHLC keyless · {_CRYPTO_COIN_IDS[instrument.code]}"
    if len(candles) < 55:
        raise RuntimeError("Sumber data belum mengembalikan cukup candle untuk analisis indikator.")
    warning = "Data publik untuk riset/edukasi; dapat tertunda dan bukan harga eksekusi broker."
    if source.startswith("CoinGecko"):
        warning = "CoinGecko keyless memiliki batas rate bersama dan candle historis; bukan feed eksekusi broker."
    if instrument.note:
        warning = f"{instrument.note} {warning}"
    return MarketSnapshot(instrument, candles, calculate_indicators(candles), datetime.now(timezone.utc), candles.index[-1].to_pydatetime(), source, warning, interval)


def normalized_comparison(snapshots: Iterable[MarketSnapshot]) -> pd.DataFrame:
    frames: list[pd.Series] = []
    for snapshot in snapshots:
        series = snapshot.candles["close"].rename(snapshot.instrument.code).dropna()
        if not series.empty:
            frames.append((series / series.iloc[0] * 100).rename(snapshot.instrument.code))
    return pd.concat(frames, axis=1).dropna(how="all").ffill() if frames else pd.DataFrame()
