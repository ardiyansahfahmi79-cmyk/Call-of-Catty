"""Narasi formal Aero AI yang hanya memakai data terukur dari Python."""

from __future__ import annotations

from fundamental_data import FundamentalSnapshot
from market_data import MarketSnapshot


def _fmt(value: float) -> str:
    return f"{value:,.5f}" if abs(value) < 20 else f"{value:,.2f}"


def _trend_description(data: dict) -> str:
    price = float(data["price"])
    ma50 = float(data["ma50"])
    ma200 = float(data["ma200"])
    if price > ma50 > ma200:
        return "Harga berada di atas MA 50 dan MA 200; struktur tren menengah masih selaras ke atas."
    if price < ma50 < ma200:
        return "Harga berada di bawah MA 50 dan MA 200; struktur tren menengah masih selaras ke bawah."
    return "Harga dan rata-rata bergerak belum selaras penuh; struktur tren memerlukan konfirmasi lanjutan."


def _momentum_description(data: dict) -> str:
    rsi = float(data["rsi14"])
    macd = float(data["macd"])
    signal = float(data["macd_signal"])
    if rsi >= 70:
        rsi_text = "RSI berada pada area tinggi sehingga momentum kuat namun rentan normalisasi."
    elif rsi <= 30:
        rsi_text = "RSI berada pada area rendah sehingga tekanan masih dominan namun berpotensi normalisasi."
    else:
        rsi_text = "RSI berada di area menengah sehingga momentum belum berada pada kondisi ekstrem."
    macd_text = "MACD berada di atas signal line." if macd > signal else "MACD berada di bawah signal line."
    return f"{rsi_text} {macd_text}"


def _fundamental_section(items: list[FundamentalSnapshot]) -> str:
    if not items:
        return "Konteks fundamental belum tersedia dari sumber publik yang dikonfigurasi. Analisis teknikal tetap memakai data harga yang ditampilkan beserta waktunya."
    lines = []
    for item in items[:4]:
        observed = item.observed_at.strftime("%d %b %Y")
        lines.append(f"{item.title}: **{item.value} {item.unit}** (observasi {observed}; {item.source_name}).")
    return " ".join(lines)


def build_reply(question: str, snapshot: MarketSnapshot, fundamentals: list[FundamentalSnapshot] | None = None) -> str:
    data = snapshot.indicators
    instrument = snapshot.instrument.code
    price = _fmt(float(data["price"]))
    change_20 = float(data["change_20"])
    rsi = float(data["rsi14"])
    atr = _fmt(float(data["atr14"]))
    high20 = _fmt(float(data["high20"]))
    low20 = _fmt(float(data["low20"]))
    state = str(data["market_state"])
    alignment = int(data["confluence"])

    return (
        f"**STATUS PASAR · {instrument}**\n\n"
        f"Harga referensi terakhir adalah **{price}** dengan perubahan **{change_20:+.2f}%** dalam 20 candle. "
        f"Klasifikasi kondisi pada timeframe data saat ini adalah **{state}**. Keselarasan teknikal tercatat **{alignment}/100**; "
        f"ini adalah jumlah indikator yang searah, bukan probabilitas keberhasilan transaksi.\n\n"
        f"**STRUKTUR TREN**\n\n"
        f"{_trend_description(data)} Nilai MA 50 adalah **{_fmt(float(data['ma50']))}** dan MA 200 adalah "
        f"**{_fmt(float(data['ma200']))}**.\n\n"
        f"**MOMENTUM DAN VOLATILITAS**\n\n"
        f"{_momentum_description(data)} RSI(14) berada pada **{rsi:.1f}**, ATR(14) pada **{atr}**, dan volatilitas 20 candle "
        f"sebesar **{float(data['volatility20']):.2f}%**.\n\n"
        f"**AREA OBSERVASI DAN INVALIDASI**\n\n"
        f"Rentang 20 candle terakhir berada di antara **{low20}** dan **{high20}**. Bias kondisi perlu dievaluasi ulang bila harga "
        f"menembus rentang tersebut atau kembali melawan arah MA 50/MA 200. Area ini adalah konteks observasi, bukan instruksi entry.\n\n"
        f"**KONTEKS FUNDAMENTAL PUBLIK**\n\n"
        f"{_fundamental_section(fundamentals or [])}\n\n"
        f"**RISIKO DAN BATAS DATA**\n\n"
        f"{snapshot.warning} Gunakan waktu candle, basis instrumen, dan sumber yang ditampilkan pada kartu data sebelum menafsirkan perubahan. "
        f"Analisis ini bersifat riset dan edukatif, bukan nasihat finansial personal."
    )


def follow_up_prompts(instrument: str) -> list[str]:
    return [
        f"Bandingkan {instrument} dengan DXY",
        f"Jelaskan tren {instrument} berdasarkan MA 50 dan MA 200",
        f"Apa area observasi high dan low 20 candle {instrument}?",
    ]
