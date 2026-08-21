"""Narasi formal Aero AI berbasis indikator Python dan konteks fundamental."""

from __future__ import annotations

from fundamental_data import FundamentalSnapshot
from market_data import MarketSnapshot, timeframe_label, timeframe_was_explicit


ECONOMIC_AGENDAS: tuple[tuple[tuple[str, ...], str, str], ...] = (
    (("nfp", "non farm", "nonfarm", "laporan tenaga kerja as"), "NFP / tenaga kerja AS", "Data ketenagakerjaan AS dapat menggeser ekspektasi suku bunga The Fed dan kekuatan USD."),
    (("fomc", "federal reserve", "the fed", "fed meeting"), "FOMC / Federal Reserve", "Keputusan suku bunga, proyeksi, dan komunikasi The Fed dapat mengubah ekspektasi imbal hasil serta kekuatan USD."),
    (("bank of japan", "boj", "boj meeting"), "Bank of Japan", "Keputusan kebijakan Bank of Japan terutama relevan untuk JPY dan dinamika carry trade."),
    (("ecb", "european central bank"), "European Central Bank", "Keputusan kebijakan ECB terutama relevan untuk EUR dan selisih ekspektasi suku bunga EUR-USD."),
    (("cpi", "inflasi"), "CPI / inflasi", "Rilis inflasi dapat memengaruhi ekspektasi kebijakan moneter dan volatilitas lintas aset."),
    (("ppi",), "PPI", "Rilis harga produsen dapat menjadi konteks tambahan bagi tekanan inflasi dan ekspektasi kebijakan moneter."),
    (("gdp", "produk domestik bruto"), "GDP / pertumbuhan ekonomi", "Data pertumbuhan dapat mengubah penilaian pasar terhadap ketahanan ekonomi dan arah kebijakan."),
)


def _fmt(value: float) -> str:
    return f"{value:,.5f}" if abs(value) < 20 else f"{value:,.2f}"


def detect_economic_agenda(question: str) -> tuple[str, str] | None:
    """Temukan agenda ekonomi yang disebutkan pengguna, tanpa mengasumsikan jadwal atau hasil rilis."""
    text = question.casefold()
    for aliases, name, context in ECONOMIC_AGENDAS:
        if any(alias in text for alias in aliases):
            return name, context
    return None


def infer_intent(question: str) -> str:
    text = question.casefold()
    if detect_economic_agenda(question):
        return "economic_agenda"
    if any(word in text for word in ("bandingkan", "compare", "versus", " vs ")):
        return "comparison"
    if any(word in text for word in ("entry", "stop loss", "take profit", "tentukan level", "tp1", "tp2", "tp3")) or " sl " in f" {text} ":
        return "levels_entry"
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


def _agenda_market_channel(instrument: str | None = None) -> str:
    if instrument in {"XAUUSD", "XAGUSD"}:
        return "Untuk logam mulia, saluran yang lazim dipantau adalah perubahan USD dan imbal hasil riil; reaksi aktual dapat berbeda dari ekspektasi."
    if instrument in {"EURUSD", "GBPUSD", "AUDUSD", "USDJPY"}:
        return "Untuk pasangan FX, pasar biasanya menilai perubahan relatif ekspektasi kebijakan kedua mata uang, bukan hanya angka tajuk rilis."
    if instrument in {"SPX", "NAS100"}:
        return "Untuk indeks ekuitas AS, perhatian umumnya berada pada perubahan ekspektasi imbal hasil, pertumbuhan, dan valuasi; respons antar-sektor dapat berbeda."
    if instrument in {"BTCUSD", "ETHUSD", "SOLUSD"}:
        return "Untuk kripto, agenda makro dapat bertepatan dengan perubahan likuiditas dan sentimen risiko, tetapi hubungan tersebut tidak selalu stabil."
    if instrument in {"WTI", "BRENT"}:
        return "Untuk minyak, dampak agenda makro perlu dibaca bersama data permintaan, inventori, pasokan, dan faktor geopolitik."
    if instrument == "DXY":
        return "Untuk DXY, fokusnya adalah perubahan relatif ekspektasi suku bunga dan prospek ekonomi AS terhadap mitra dagangnya."
    return "Dampak potensial perlu dibaca bersama instrumen yang dianalisis, nilai aktual rilis, revisi data, dan ekspektasi pasar sebelum rilis."


def build_agenda_reply(question: str) -> str | None:
    """Buat jawaban edukasional jika agenda disebut tanpa instrumen market."""
    agenda = detect_economic_agenda(question)
    if not agenda:
        return None
    name, context = agenda
    return (
        f"**KONTEKS AGENDA EKONOMI · {name}**\n\n"
        f"{context} {_agenda_market_channel()}\n\n"
        "Aero AI tidak mengasumsikan bahwa agenda tersebut sedang berlangsung, sudah dirilis, atau akan menghasilkan arah harga tertentu. Untuk pemindaian berbasis harga, sertakan instrumen dan timeframe, misalnya **Analisa XAUUSD pada H1 setelah NFP**.\n\n"
        "**BATAS ANALISIS**\n\nIni adalah penjelasan konteks pasar untuk riset dan edukasi, bukan nasihat finansial personal atau instruksi transaksi."
    )


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
        "economic_agenda": "Fokus pertanyaan mencakup agenda ekonomi; narasi memisahkan mekanisme dampak potensial dari kondisi harga aktual pada snapshot ini.",
        "levels_entry": "Fokus pertanyaan adalah skenario level; semua area berikut dihitung dari harga, ATR, MA 50, dan rentang 20 candle pada snapshot ini, bukan sinyal eksekusi.",
        "risk": f"Fokus pertanyaan adalah risiko; ATR(14) sebesar {_fmt(float(data['atr14']))} dan volatilitas 20 candle {float(data['volatility20']):.2f}% perlu dipakai sebagai konteks rentang, bukan ukuran posisi otomatis.",
        "fundamental": "Fokus pertanyaan adalah fundamental; setiap observasi di bawah memiliki frekuensi rilis sendiri dan tidak boleh diperlakukan sebagai data intraday.",
        "levels": f"Fokus pertanyaan adalah level; rentang 20 candle adalah {_fmt(float(data['low20']))} sampai {_fmt(float(data['high20']))}, sedangkan zona Fibonacci 61.8% berada pada {_fmt(float(data['fib618']))}.",
        "trend": "Fokus pertanyaan adalah tren; pembacaan utama memakai hubungan harga dengan MA 50/MA 200 serta ADX untuk menilai kekuatan tren, bukan arah harga berikutnya.",
        "signals": "Fokus pertanyaan adalah sinyal; label BUY, NEUTRAL, atau SELL menjelaskan kondisi indikator pada snapshot ini dan bukan instruksi transaksi.",
        "overview": "Fokus pertanyaan adalah ringkasan kondisi; Aero AI menggabungkan struktur tren, momentum, volatilitas, dan konteks fundamental yang tersedia.",
    }
    return mapping[intent]


def _entry_scenario(data: dict) -> str:
    """Menghitung area observasi dari snapshot, tanpa menentukan ukuran posisi atau instruksi eksekusi."""
    price = float(data["price"])
    atr = float(data["atr14"])
    if atr <= 0:
        return "ATR(14) belum memadai untuk membentuk jarak observasi. Aero AI tidak akan membuat level pengganti."

    low20, high20, ma50 = float(data["low20"]), float(data["high20"]), float(data["ma50"])
    entry_low, entry_high = price - 0.25 * atr, price + 0.25 * atr
    bias = str(data["bias"])
    if bias == "BUY":
        invalidation = min(low20, ma50, entry_low - atr)
        risk_distance = abs(price - invalidation) / price * 100
        return (
            f"Bias indikator saat ini **BUY**. Area observasi entry teknikal berada pada **{_fmt(entry_low)}–{_fmt(entry_high)}**. "
            f"Invalidasi teknikal / SL observasi berada di **{_fmt(invalidation)}**. Target observasi bertahap TP1, TP2, dan TP3 berada di **{_fmt(price + atr)}**, **{_fmt(price + 2 * atr)}**, dan **{_fmt(price + 3 * atr)}**. "
            f"Jarak risiko harga menuju invalidasi adalah **{risk_distance:.2f}%** dari harga referensi; angka ini belum memasukkan ukuran posisi, spread, biaya, atau slippage."
        )
    if bias == "SELL":
        invalidation = max(high20, ma50, entry_high + atr)
        risk_distance = abs(invalidation - price) / price * 100
        return (
            f"Bias indikator saat ini **SELL**. Area observasi entry teknikal berada pada **{_fmt(entry_low)}–{_fmt(entry_high)}**. "
            f"Invalidasi teknikal / SL observasi berada di **{_fmt(invalidation)}**. Target observasi bertahap TP1, TP2, dan TP3 berada di **{_fmt(price - atr)}**, **{_fmt(price - 2 * atr)}**, dan **{_fmt(price - 3 * atr)}**. "
            f"Jarak risiko harga menuju invalidasi adalah **{risk_distance:.2f}%** dari harga referensi; angka ini belum memasukkan ukuran posisi, spread, biaya, atau slippage."
        )
    return (
        f"Bias indikator saat ini **NEUTRAL**, sehingga Aero AI tidak membentuk satu instruksi arah. Area observasi awal berada pada **{_fmt(entry_low)}–{_fmt(entry_high)}**. "
        f"Konfirmasi bullish perlu dievaluasi terhadap high 20 candle **{_fmt(high20)}**, sedangkan konfirmasi bearish terhadap low 20 candle **{_fmt(low20)}**. "
        "Tunggu konfirmasi struktur sesuai rencana risiko pribadi; tidak ada Entry, SL, atau TP satu arah yang dipaksakan ketika indikator belum selaras."
    )


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
    timeframe_note = (
        f"Timeframe **{timeframe_label(snapshot.interval)}** terdeteksi langsung dari pertanyaan Anda."
        if timeframe_was_explicit(question)
        else f"Timeframe tidak disebutkan; Aero AI menggunakan asumsi default **{timeframe_label(snapshot.interval)}**."
    )
    agenda = detect_economic_agenda(question)
    agenda_section = ""
    if agenda:
        name, context = agenda
        agenda_section = f"\n\n**KONTEKS AGENDA EKONOMI · {name}**\n\n{context} {_agenda_market_channel(snapshot.instrument.code)}"
    scenario_section = f"\n\n**SKENARIO LEVEL TEKNIKAL**\n\n{_entry_scenario(data)}" if intent == "levels_entry" else ""
    return (
        f"**STATUS PASAR · {snapshot.instrument.code}**\n\n"
        f"{timeframe_note} Harga referensi terakhir adalah **{price}** dengan perubahan **{change_20:+.2f}%** dalam 20 candle. Kondisi pada timeframe data saat ini adalah **{data['market_state']}** dengan keselarasan teknikal **{int(data['confluence'])}/100**. Nilai tersebut menunjukkan jumlah indikator yang searah, bukan probabilitas keberhasilan transaksi.\n\n"
        f"**FOKUS PEMINDAIAN**\n\n{_focus_line(intent, data)}\n\n"
        f"**STRUKTUR DAN MOMENTUM**\n\n{_trend_description(data)} RSI(14) berada pada **{rsi:.1f}**, ADX(14) pada **{adx:.1f}**, dan relative volume pada **{volume:.2f}x**. ADX mengukur kekuatan tren, bukan arahnya; volume relatif bernilai netral bila penyedia tidak menyediakan volume yang bermakna.\n\n"
        f"**AREA OBSERVASI DAN RISIKO**\n\n"
        f"Range 20 candle berada pada **{_fmt(float(data['low20']))}** sampai **{_fmt(float(data['high20']))}**. ATR(14) adalah **{_fmt(float(data['atr14']))}** dan volatilitas 20 candle **{float(data['volatility20']):.2f}%**. Bias harus dievaluasi ulang bila struktur harga bergerak melawan MA 50/MA 200 atau keluar dari range observasi.{agenda_section}{scenario_section}\n\n"
        f"**KONTEKS FUNDAMENTAL PUBLIK**\n\n{_fundamental_section(fundamentals or [])}\n\n"
        f"**BATAS DATA**\n\n{snapshot.warning} Analisis ini dibuat untuk riset dan edukasi, bukan nasihat finansial personal."
    )


def follow_up_prompts(instrument: str, interval: str | None = None) -> list[str]:
    timeframe_suffix = f" pada timeframe {timeframe_label(interval)}" if interval else ""
    return [
        f"Bandingkan {instrument} dengan DXY{timeframe_suffix}",
        f"Jelaskan tren {instrument} berdasarkan MA 50 dan MA 200{timeframe_suffix}",
        f"Tinjau risiko {instrument} dari ATR dan volatilitas{timeframe_suffix}",
        f"Jelaskan 10 indikator {instrument} saat ini{timeframe_suffix}",
        f"Tentukan area observasi high, low, dan Fibonacci {instrument}{timeframe_suffix}",
        f"Tentukan Entry, SL, TP1 TP2 TP3 dan Risk untuk {instrument}{timeframe_suffix}",
        f"Rangkum konteks fundamental publik untuk {instrument}{timeframe_suffix}",
    ]
