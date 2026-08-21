"""Narasi formal Aero AI yang hanya memakai hasil hitungan market_data."""

from __future__ import annotations

from market_data import MarketSnapshot


def _fmt(value: float) -> str:
    return f"{value:,.5f}" if abs(value) < 20 else f"{value:,.2f}"


def _momentum_name(indicators: dict) -> str:
    rsi = float(indicators["rsi14"])
    macd_ok = float(indicators["macd"]) > float(indicators["macd_signal"])
    if rsi >= 65 and macd_ok:
        return "momentum naik cukup panas"
    if rsi <= 35 and not macd_ok:
        return "momentum turun cukup tertekan"
    return "momentum masih campuran"


def build_reply(question: str, snapshot: MarketSnapshot) -> str:
    data = snapshot.indicators
    instrument = snapshot.instrument.code
    bias = str(data["bias"])
    price = _fmt(float(data["price"]))
    change = float(data["change_20"])
    momentum = _momentum_name(data)
    levels = f"range 20 candle {_fmt(float(data['low20']))}–{_fmt(float(data['high20']))}"
    rsi = float(data["rsi14"])
    confluence = int(data["confluence"])

    return (
        f"**RINGKASAN KONDISI**\n\n"
        f"Berdasarkan data **{instrument}**, harga terakhir tercatat pada **{price}** dengan perubahan 20 candle sebesar "
        f"**{change:+.2f}%**. Posisi harga terhadap moving average, RSI(14) **{rsi:.1f}**, dan MACD menghasilkan "
        f"klasifikasi teknikal **{bias}**. Keselarasan indikator saat ini adalah **{confluence}/100**; angka ini menunjukkan "
        f"jumlah kondisi indikator yang searah, bukan probabilitas keberhasilan transaksi.\n\n"
        f"**BUKTI DAN AREA OBSERVASI**\n\n"
        f"Area high-low 20 candle berada pada {levels}. Momentum saat ini menunjukkan {momentum}. Konfirmasi struktur harga, "
        f"likuiditas, dan batas risiko tetap diperlukan sebelum mengambil keputusan. Data ini bersifat riset dan edukatif, "
        f"bukan rekomendasi transaksi individual."
    )


def follow_up_prompts(instrument: str) -> list[str]:
    return [
        f"Bandingkan {instrument} dengan DXY",
        f"Tampilkan grafik {instrument} dan jelaskan MA 50/200",
        f"Apa level high dan low 20 candle {instrument}?",
    ]
