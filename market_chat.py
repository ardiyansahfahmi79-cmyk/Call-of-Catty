"""Persona Neuro dan Aime untuk prototipe chatbot market Call-of-Catty.

Narasi sengaja memakai hasil perhitungan Python yang diberikan market_data,
bukan membuat angka harga atau prediksi profit secara fiktif.
"""

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


def build_reply(question: str, snapshot: MarketSnapshot, persona: str) -> str:
    data = snapshot.indicators
    instrument = snapshot.instrument.code
    bias = str(data["bias"])
    direction = {"BUY": "bias naik", "SELL": "bias turun", "NEUTRAL": "bias netral"}[bias]
    price = _fmt(float(data["price"]))
    change = float(data["change_20"])
    change_word = "naik" if change >= 0 else "turun"
    momentum = _momentum_name(data)
    levels = f"range 20 candle {_fmt(float(data['low20']))}–{_fmt(float(data['high20']))}"
    rsi = float(data["rsi14"])
    confluence = int(data["confluence"])

    if persona == "Neuro":
        return (
            f"Bro, **{instrument}** kebaca di **{price}**. Dalam 20 candle terakhir harganya {change_word} "
            f"**{abs(change):.2f}%**, jadi mesin Python nangkep {direction} dengan konfluensi **{confluence}/100**. "
            f"RSI(14) di **{rsi:.1f}** dan MACD lagi kasih sinyal bahwa {momentum}.\n\n"
            f"Yang wajib lo pantau sekarang itu {levels}. Harga di atas MA50/MA200 atau malah balik nembus levelnya "
            f"lebih penting daripada ngejar candle. Ini pembacaan kondisi, bukan lampu hijau buat masuk buta-buta. "
            f"Mau gue bedah support-resistance, bandingin sama instrumen lain, atau cek timeframe lain?"
        )
    return (
        f"Berdasarkan data **{instrument}**, harga terakhir tercatat di **{price}** dengan perubahan 20 candle sebesar "
        f"**{change:+.2f}%**. Kombinasi posisi harga terhadap moving average, RSI(14) **{rsi:.1f}**, dan MACD "
        f"menghasilkan klasifikasi **{bias}** dengan tingkat konfluensi indikator **{confluence}/100**.\n\n"
        f"Area observasi terdekat berada pada {levels}. Momentum saat ini menunjukkan {momentum}; karena itu, "
        f"konfirmasi struktur harga dan batas risiko tetap diperlukan sebelum mengambil keputusan. Analisis ini bersifat "
        f"edukatif dan tidak merupakan rekomendasi transaksi individual."
    )


def follow_up_prompts(instrument: str) -> list[str]:
    return [
        f"Bandingkan {instrument} dengan DXY",
        f"Tampilkan grafik {instrument} dan jelaskan MA 50/200",
        f"Apa level high dan low 20 candle {instrument}?",
    ]
