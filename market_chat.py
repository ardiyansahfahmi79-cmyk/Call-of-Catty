"""Narasi formal Aero AI berbasis indikator Python dan konteks fundamental."""

from __future__ import annotations

from fundamental_data import FundamentalSnapshot
from market_data import MarketSnapshot


def _fmt(value: float) -> str:
    return f"{value:,.5f}" if abs(value) < 20 else f"{value:,.2f}"


def infer_intent(question: str) -> str:
    text = question.casefold()
    if any(word in text for word in ("bandingkan", "compare", "versus", " vs ")):
        return "comparison"
    if any(word in text for word in ("risiko", "risk", "atr", "volatil")):
        return "risk"
    if any(word in text for word in ("fundamental", "makro", "cpi", "pengangguran")):
        return "fundamental"
    if any(word in text for word in ("level", "high", "low", "support", "resistance", "fib")):
        return "levels"
    if any(word in text for word in ("tren", "trend", "ma 50", "ma50", "ma 200", "ma200")):
        return "trend"
    if any(word in text for word in ("sinyal", "signal", "indikator", "buy", "sell")):
        return "signals"
    return "overview"


def _trend_description(data: dict) -> str:
    price, ma50, ma200 = float(data["price"]), float(data["ma50"]), float(data["ma200"])
    if price > ma50 > ma200:
        return "Harga berada di atas MA 50 dan MA 200; struktur tren menengah masih selaras ke atas."
    if price < ma50 < ma200:
        return "Harga berada di bawah MA 50 dan MA 200; struktur tren menengah masih selaras ke bawah."
    return "Harga dan rata-rata bergerak belum selaras penuh; struktur tren memerlukan konfirmasi lanjutan."


def _focus_line(intent: str, data: dict) -> str:
    mapping = {
        "comparison": "Fokus pertanyaan adalah perbandingan; gunakan grafik basis 100 untuk melihat pergerakan relatif, bukan nominal harga.",
        "risk": f"Fokus pertanyaan adalah risiko; ATR(14) sebesar {_fmt(float(data['atr14']))} dan volatilitas 20 candle {float(data['volatility20']):.2f}% perlu dipakai sebagai konteks rentang, bukan ukuran posisi otomatis.",
        "fundamental": "Fokus pertanyaan adalah fundamental; setiap observasi di bawah memiliki frekuensi rilis sendiri dan tidak boleh diperlakukan sebagai data intraday.",
        "levels": f"Fokus pertanyaan adalah level; rentang 20 candle adalah {_fmt(float(data['low20']))} sampai {_fmt(float(data['high20']))}, sedangkan zona Fibonacci 61.8% berada pada {_fmt(float(data['fib618']))}.",
        "trend": "Fokus pertanyaan adalah tren; pembacaan utama memakai hubungan harga dengan MA 50/MA 200 serta ADX untuk menilai kekuatan tren, bukan arah harga berikutnya.",
        "signals": "Fokus pertanyaan adalah sinyal; label BUY, NEUTRAL, atau SELL menjelaskan kondisi indikator pada snapshot ini dan bukan instruksi transaksi.",
        "overview": "Fokus pertanyaan adalah ringkasan kondisi; Aero AI menggabungkan struktur tren, momentum, volatilitas, dan konteks fundamental yang tersedia.",
    }
    return mapping[intent]


def _fundamental_section(items: list[FundamentalSnapshot]) -> str:
    if not items:
        return "Konteks fundamental belum tersedia dari sumber publik yang dikonfigurasi. Analisis teknikal tetap memakai data harga yang ditampilkan beserta waktunya."
    return " ".join(f"{item.title}: **{item.value} {item.unit}** (observasi {item.observed_at.strftime('%d %b %Y')}; {item.source_name})." for item in items[:4])


def build_reply(question: str, snapshot: MarketSnapshot, fundamentals: list[FundamentalSnapshot] | None = None) -> str:
    data = snapshot.indicators
    intent = infer_intent(question)
    price, change_20 = _fmt(float(data["price"])), float(data["change_20"])
    rsi, adx = float(data["rsi14"]), float(data["adx14"])
    volume = float(data["relative_volume"])
    return (
        f"**STATUS PASAR · {snapshot.instrument.code}**\n\n"
        f"Harga referensi terakhir adalah **{price}** dengan perubahan **{change_20:+.2f}%** dalam 20 candle. Kondisi pada timeframe data saat ini adalah **{data['market_state']}** dengan keselarasan teknikal **{int(data['confluence'])}/100**. Nilai tersebut menunjukkan jumlah indikator yang searah, bukan probabilitas keberhasilan transaksi.\n\n"
        f"**FOKUS PEMINDAIAN**\n\n{_focus_line(intent, data)}\n\n"
        f"**STRUKTUR DAN MOMENTUM**\n\n{_trend_description(data)} RSI(14) berada pada **{rsi:.1f}**, ADX(14) pada **{adx:.1f}**, dan relative volume pada **{volume:.2f}x**. ADX mengukur kekuatan tren, bukan arahnya; volume relatif bernilai netral bila penyedia tidak menyediakan volume yang bermakna.\n\n"
        f"**AREA OBSERVASI DAN RISIKO**\n\n"
        f"Range 20 candle berada pada **{_fmt(float(data['low20']))}** sampai **{_fmt(float(data['high20']))}**. ATR(14) adalah **{_fmt(float(data['atr14']))}** dan volatilitas 20 candle **{float(data['volatility20']):.2f}%**. Bias harus dievaluasi ulang bila struktur harga bergerak melawan MA 50/MA 200 atau keluar dari range observasi.\n\n"
        f"**KONTEKS FUNDAMENTAL PUBLIK**\n\n{_fundamental_section(fundamentals or [])}\n\n"
        f"**BATAS DATA**\n\n{snapshot.warning} Analisis ini dibuat untuk riset dan edukasi, bukan nasihat finansial personal."
    )


def follow_up_prompts(instrument: str) -> list[str]:
    return [
        f"Bandingkan {instrument} dengan DXY",
        f"Jelaskan tren {instrument} berdasarkan MA 50 dan MA 200",
        f"Tinjau risiko {instrument} dari ATR dan volatilitas",
        f"Jelaskan 10 indikator {instrument} saat ini",
        f"Tentukan area observasi high, low, dan Fibonacci {instrument}",
        f"Rangkum konteks fundamental publik untuk {instrument}",
    ]
