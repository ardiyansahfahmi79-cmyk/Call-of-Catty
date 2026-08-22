"""Narasi formal Aero AI berbasis snapshot harga dan kalender ekonomi publik."""

from __future__ import annotations

from datetime import datetime, timezone
import re

from economic_calendar import calendar_fetch_status, find_calendar_events
from fundamental_data import FundamentalSnapshot
from market_intelligence import evidence_section, historical_section, macro_router_section, regime_section
from market_data import MarketSnapshot, instrument_economic_currencies, timeframe_label, timeframe_was_explicit


AgendaDefinition = tuple[tuple[str, ...], str, str, tuple[str, ...]]

# Batas sengaja dipertahankan pada 50 kategori agar intent tetap terukur dan dapat diuji.
ECONOMIC_AGENDAS: tuple[AgendaDefinition, ...] = (
    (("nfp", "non farm", "nonfarm", "non-farm payroll", "laporan tenaga kerja as"), "NFP / Non-Farm Payrolls", "Data ketenagakerjaan AS dapat menggeser ekspektasi kebijakan The Fed dan kekuatan USD.", ("non farm", "nonfarm payroll")),
    (("adp", "adp employment"), "ADP Employment Change", "Estimasi tenaga kerja sektor swasta AS dapat menjadi konteks sebelum rilis tenaga kerja resmi.", ("adp employment",)),
    (("jobless claims", "initial claims", "klaim pengangguran"), "Initial Jobless Claims", "Klaim pengangguran mingguan memberi konteks frekuensi tinggi untuk pasar tenaga kerja AS.", ("unemployment claims", "jobless claims")),
    (("unemployment rate", "tingkat pengangguran"), "Unemployment Rate", "Tingkat pengangguran merupakan salah satu indikator kondisi pasar tenaga kerja dan mandat kebijakan moneter.", ("unemployment rate",)),
    (("average hourly earnings", "upah rata rata", "wage growth"), "Average Hourly Earnings", "Pertumbuhan upah sering dipantau sebagai salah satu komponen tekanan inflasi jasa.", ("average hourly earnings", "average earnings")),
    (("jolts", "job openings"), "JOLTS Job Openings", "Data lowongan kerja memberi konteks permintaan tenaga kerja AS.", ("jolts", "job openings")),
    (("employment cost index", "eci"), "Employment Cost Index", "Indeks biaya tenaga kerja memberi konteks upah dan kompensasi pada frekuensi kuartalan.", ("employment cost",)),
    (("core cpi", "cpi inti", "inflasi inti"), "Core CPI", "Inflasi inti sering diamati untuk memahami tekanan harga di luar komponen volatil tertentu.", ("core cpi",)),
    (("cpi", "consumer price index", "inflasi"), "CPI / Consumer Price Index", "Rilis inflasi dapat memengaruhi ekspektasi kebijakan moneter dan volatilitas lintas aset.", ("cpi", "consumer price")),
    (("core ppi", "ppi inti"), "Core PPI", "Harga produsen inti memberi konteks tekanan biaya di tingkat produsen.", ("core ppi",)),
    (("ppi", "producer price index"), "PPI / Producer Price Index", "Rilis harga produsen dapat menjadi konteks tambahan bagi tekanan inflasi.", ("ppi", "producer price")),
    (("core pce", "pce inti"), "Core PCE Price Index", "Core PCE merupakan salah satu ukuran inflasi yang dipantau Federal Reserve.", ("core pce",)),
    (("pce", "personal consumption expenditures"), "PCE Price Index", "PCE memberi konteks inflasi berbasis konsumsi pribadi AS.", ("pce", "personal consumption")),
    (("core retail sales", "retail sales ex", "retail inti"), "Core Retail Sales", "Penjualan ritel inti dapat memberi konteks konsumsi rumah tangga di luar komponen tertentu.", ("core retail", "retail sales ex")),
    (("retail sales", "penjualan ritel"), "Retail Sales", "Penjualan ritel digunakan sebagai konteks konsumsi dan aktivitas ekonomi.", ("retail sales",)),
    (("gdp price index", "deflator gdp"), "GDP Price Index", "Indeks harga GDP memberi konteks tekanan harga pada output ekonomi.", ("gdp price",)),
    (("gdp", "produk domestik bruto", "pertumbuhan ekonomi"), "GDP / Pertumbuhan Ekonomi", "Data pertumbuhan dapat mengubah penilaian pasar terhadap ketahanan ekonomi dan arah kebijakan.", ("gdp growth", "gdp")),
    (("durable goods", "barang tahan lama"), "Durable Goods Orders", "Pesanan barang tahan lama memberi konteks investasi dan permintaan manufaktur.", ("durable goods",)),
    (("factory orders", "pesanan pabrik"), "Factory Orders", "Pesanan pabrik memberi konteks permintaan sektor manufaktur.", ("factory orders",)),
    (("industrial production", "produksi industri"), "Industrial Production", "Produksi industri memberi konteks aktivitas manufaktur, pertambangan, dan utilitas.", ("industrial production",)),
    (("capacity utilization", "utilisasi kapasitas"), "Capacity Utilization", "Utilisasi kapasitas memberi konteks seberapa intens kapasitas industri digunakan.", ("capacity utilization",)),
    (("ism manufacturing", "ism manufaktur"), "ISM Manufacturing PMI", "Survei manufaktur memberi konteks aktivitas sektor industri dan pesanan baru.", ("ism manufacturing",)),
    (("ism services", "ism jasa"), "ISM Services PMI", "Survei jasa memberi konteks aktivitas sektor jasa yang dominan dalam ekonomi AS.", ("ism services",)),
    (("flash manufacturing pmi", "pmi manufaktur"), "Manufacturing PMI", "PMI manufaktur memberi pembacaan awal aktivitas pabrik dan pesanan.", ("manufacturing pmi",)),
    (("flash services pmi", "pmi jasa"), "Services PMI", "PMI jasa memberi pembacaan awal aktivitas sektor jasa.", ("services pmi",)),
    (("cb consumer confidence", "consumer confidence", "kepercayaan konsumen"), "Consumer Confidence", "Kepercayaan konsumen memberi konteks sentimen rumah tangga dan konsumsi.", ("consumer confidence",)),
    (("u michigan", "university of michigan", "umich"), "University of Michigan Sentiment", "Sentimen konsumen Michigan memberi konteks keyakinan konsumen dan ekspektasi inflasi.", ("michigan", "consumer sentiment")),
    (("housing starts", "perumahan baru"), "Housing Starts", "Housing starts memberi konteks aktivitas konstruksi perumahan.", ("housing starts",)),
    (("building permits", "izin bangunan"), "Building Permits", "Izin bangunan memberi konteks pipeline konstruksi perumahan.", ("building permits",)),
    (("existing home sales", "penjualan rumah existing"), "Existing Home Sales", "Penjualan rumah existing memberi konteks aktivitas pasar perumahan.", ("existing home sales",)),
    (("new home sales", "penjualan rumah baru"), "New Home Sales", "Penjualan rumah baru memberi konteks permintaan perumahan baru.", ("new home sales",)),
    (("pending home sales", "pending home"), "Pending Home Sales", "Penjualan rumah tertunda memberi konteks kontrak perumahan sebelum penyelesaian.", ("pending home sales",)),
    (("trade balance", "neraca perdagangan"), "Trade Balance", "Neraca perdagangan memberi konteks ekspor, impor, dan arus eksternal.", ("trade balance",)),
    (("current account", "neraca berjalan"), "Current Account", "Neraca berjalan memberi konteks transaksi eksternal yang lebih luas.", ("current account",)),
    (("wholesale inventories", "inventori grosir"), "Wholesale Inventories", "Inventori grosir memberi konteks stok dan aktivitas distribusi.", ("wholesale inventories",)),
    (("business inventories", "inventori bisnis"), "Business Inventories", "Inventori bisnis memberi konteks stok perusahaan dan siklus produksi.", ("business inventories",)),
    (("eia crude", "crude oil inventories", "stok minyak eia"), "EIA Crude Oil Inventories", "Data inventori minyak EIA dapat relevan untuk WTI dan Brent bersama faktor pasokan serta permintaan lain.", ("crude oil inventories", "eia crude")),
    (("natural gas storage", "eia natural gas", "stok gas"), "EIA Natural Gas Storage", "Data penyimpanan gas alam dapat relevan untuk instrumen energi terkait.", ("natural gas storage",)),
    (("baker hughes", "rig count", "jumlah rig"), "Baker Hughes Rig Count", "Jumlah rig memberi konteks aktivitas pengeboran energi, bukan arah harga tunggal.", ("rig count",)),
    (("fomc", "federal reserve", "the fed", "fed meeting"), "FOMC / Federal Reserve", "Keputusan suku bunga, proyeksi, dan komunikasi The Fed dapat mengubah ekspektasi imbal hasil serta kekuatan USD.", ("fomc", "federal reserve")),
    (("fed speech", "fed speaks", "pidato fed", "fed member"), "Federal Reserve Speech", "Pernyataan pejabat Fed dapat memengaruhi pembacaan pasar atas arah kebijakan, tetapi perlu dibaca dalam konteks lengkap.", ("fed", "fomc member")),
    (("interest rate decision", "keputusan suku bunga as", "rate decision us"), "US Interest Rate Decision", "Keputusan suku bunga AS memengaruhi ekspektasi imbal hasil dan USD, tanpa menjamin reaksi harga yang seragam.", ("interest rate decision",)),
    (("dot plot", "proyeksi fed"), "Federal Reserve Dot Plot", "Proyeksi suku bunga Fed memberi konteks distribusi pandangan pembuat kebijakan.", ("dot plot",)),
    (("bank of japan", "boj", "boj meeting"), "Bank of Japan", "Keputusan Bank of Japan terutama relevan untuk JPY dan dinamika carry trade.", ("boj", "bank of japan")),
    (("ecb", "european central bank"), "European Central Bank", "Keputusan ECB terutama relevan untuk EUR dan selisih ekspektasi suku bunga EUR-USD.", ("ecb", "european central bank")),
    (("rba", "reserve bank of australia"), "Reserve Bank of Australia", "Keputusan RBA terutama relevan untuk AUD dan ekspektasi suku bunga Australia.", ("rba", "australia")),
    (("boe", "bank of england"), "Bank of England", "Keputusan Bank of England terutama relevan untuk GBP dan ekspektasi suku bunga Inggris.", ("boe", "bank of england")),
    (("boc", "bank of canada"), "Bank of Canada", "Keputusan Bank of Canada terutama relevan untuk CAD dan kondisi ekonomi Kanada.", ("boc", "bank of canada")),
    (("snb", "swiss national bank"), "Swiss National Bank", "Keputusan Swiss National Bank terutama relevan untuk CHF dan kebijakan moneter Swiss.", ("snb", "swiss national bank")),
    (("rbnz", "reserve bank of new zealand"), "Reserve Bank of New Zealand", "Keputusan RBNZ terutama relevan untuk NZD dan ekspektasi suku bunga Selandia Baru.", ("rbnz", "new zealand")),
)

_CURRENCY_COUNTRY_ALIASES: dict[str, tuple[str, ...]] = {
    "USD": ("usd", "as", "us", "usa", "u s", "u s a", "amerika", "amerika serikat", "america", "american", "united states", "united states of america"),
    "EUR": ("eur", "eu", "e u", "euro", "euro area", "eurozone", "zona euro", "uni eropa", "european union", "eropa", "europe"),
    "CAD": ("cad", "kanada", "canada", "canadian"),
    "GBP": ("gbp", "uk", "u k", "inggris", "england", "britania", "british", "united kingdom"),
    "JPY": ("jpy", "jepang", "japan", "japanese", "yen"),
    "AUD": ("aud", "australia", "australian", "aussie"),
    "CHF": ("chf", "swiss", "switzerland", "swis", "franc"),
    "NZD": ("nzd", "nz", "n z", "selandia baru", "new zealand", "kiwi"),
    "IDR": ("idr", "rupiah", "indonesia", "indonesian"),
}
_CURRENCY_DISPLAY_NAMES = {
    "USD": "AS", "EUR": "Euro Area", "CAD": "Kanada", "GBP": "Inggris", "JPY": "Jepang",
    "AUD": "Australia", "CHF": "Swiss", "NZD": "Selandia Baru", "IDR": "Indonesia",
}
_FIXED_AGENDA_CURRENCIES = {
    "NFP / Non-Farm Payrolls": ("USD",), "ADP Employment Change": ("USD",),
    "Initial Jobless Claims": ("USD",), "JOLTS Job Openings": ("USD",),
    "Employment Cost Index": ("USD",), "Core PCE Price Index": ("USD",), "PCE Price Index": ("USD",),
    "EIA Crude Oil Inventories": ("USD",), "EIA Natural Gas Storage": ("USD",), "Baker Hughes Rig Count": ("USD",),
    "FOMC / Federal Reserve": ("USD",), "Federal Reserve Speech": ("USD",),
    "US Interest Rate Decision": ("USD",), "Federal Reserve Dot Plot": ("USD",),
    "Bank of Japan": ("JPY",), "European Central Bank": ("EUR",), "Reserve Bank of Australia": ("AUD",),
    "Bank of England": ("GBP",), "Bank of Canada": ("CAD",), "Swiss National Bank": ("CHF",),
    "Reserve Bank of New Zealand": ("NZD",),
}


def _fmt(value: float) -> str:
    return f"{value:,.5f}" if abs(value) < 20 else f"{value:,.2f}"


def detect_economic_agenda(question: str) -> AgendaDefinition | None:
    """Temukan satu agenda paling spesifik tanpa mengasumsikan jadwal atau hasil rilis."""
    text = question.casefold()
    matches = [agenda for agenda in ECONOMIC_AGENDAS if any(alias in text for alias in agenda[0])]
    return max(matches, key=lambda agenda: max(len(alias) for alias in agenda[0]), default=None)


def _retail_sales_period(question: str) -> str | None:
    """Klasifikasikan basis Retail Sales yang ditulis pengguna tanpa mengubah nilai kalender."""
    text = question.casefold()
    if re.search(r"\b(?:yoy|y\s*[/.-]\s*y|year\s+over\s+year|tahunan)\b", text):
        return "YoY"
    if re.search(r"\b(?:mom|m\s*[/.-]\s*m|month\s+over\s+month|monthly|bulanan)\b", text):
        return "MoM"
    return None


def agenda_display_name(agenda: AgendaDefinition, question: str) -> str:
    """Tampilkan variasi periode yang benar-benar disebut, terutama Retail Sales."""
    name = agenda[1]
    period = _retail_sales_period(question)
    if period and name in {"Retail Sales", "Core Retail Sales"}:
        return f"{name} ({period})"
    return name


def _phrase_in_text(text: str, phrase: str) -> bool:
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", text))


def _currencies_mentioned(question: str) -> tuple[str, ...]:
    text = re.sub(r"[^a-z0-9 ]+", " ", question.casefold())
    matched: list[str] = []
    for currency, aliases in _CURRENCY_COUNTRY_ALIASES.items():
        if any(_phrase_in_text(text, alias) for alias in aliases):
            matched.append(currency)
    return tuple(matched)


def _agenda_calendar_currencies(
    agenda: AgendaDefinition,
    question: str,
    instrument_code: str | None = None,
) -> tuple[str, ...]:
    """Tentukan filter hanya dari negara eksplisit, pair tunggal, atau agenda institusional."""
    explicit = _currencies_mentioned(question)
    if explicit:
        return explicit
    if instrument_code:
        related = instrument_economic_currencies(instrument_code)
        if len(related) == 1:
            return related
    return _FIXED_AGENDA_CURRENCIES.get(agenda[1], ())


def _needs_currency_clarification(agenda: AgendaDefinition, question: str, instrument_code: str | None = None) -> bool:
    if _agenda_calendar_currencies(agenda, question, instrument_code):
        return False
    if instrument_code and len(instrument_economic_currencies(instrument_code)) >= 2:
        return True
    return agenda[1] not in _FIXED_AGENDA_CURRENCIES


def agenda_clarification_prompts(question: str, instrument_code: str | None = None) -> list[str]:
    """Sediakan maksimal tiga prompt fokus tanpa mengirim data kalender negara lain."""
    agenda = detect_economic_agenda(question)
    if not agenda or not _needs_currency_clarification(agenda, question, instrument_code):
        return []
    name = agenda_display_name(agenda, question)
    related = instrument_economic_currencies(instrument_code or "")
    if instrument_code and len(related) >= 2:
        left, right = related[:2]
        left_name = _CURRENCY_DISPLAY_NAMES.get(left, left)
        right_name = _CURRENCY_DISPLAY_NAMES.get(right, right)
        return [
            f"Jelaskan {name} {left_name} untuk {instrument_code}",
            f"Jelaskan {name} {right_name} untuk {instrument_code}",
            f"Bandingkan {name} {left_name} dan {right_name} untuk {instrument_code}",
        ]
    return [f"Jelaskan {name} AS", f"Jelaskan {name} Euro Area", f"Jelaskan {name} Kanada"]


def _agenda_clarification_section(agenda: AgendaDefinition, question: str, instrument_code: str | None = None) -> str:
    name = agenda_display_name(agenda, question)
    prompts = agenda_clarification_prompts(question, instrument_code)
    if instrument_code and len(instrument_economic_currencies(instrument_code)) >= 2:
        sides = " dan ".join(_CURRENCY_DISPLAY_NAMES.get(currency, currency) for currency in instrument_economic_currencies(instrument_code)[:2])
        context = (
            f"**{instrument_code}** memiliki dua sisi ekonomi, yaitu **{sides}**. "
            "Aero AI tidak akan memilih salah satunya atau menampilkan kalender negara lain tanpa fokus yang jelas."
        )
    else:
        context = (
            "Agenda ini tersedia untuk beberapa negara. Aero AI memerlukan fokus negara atau instrumen agar kalender yang ditampilkan tidak salah relevansi."
        )
    choices = "; ".join(f"**{prompt.replace('Jelaskan ', '')}**" for prompt in prompts[:3])
    return f"**KLARIFIKASI AGENDA EKONOMI · {name}**\n\n{context}\n\nPilih salah satu fokus berikut: {choices}."


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
    if any(word in text for word in ("fundamental", "makro")):
        return "fundamental"
    if any(word in text for word in ("level", "high", "low", "support", "resistance", "fib")):
        return "levels"
    if any(word in text for word in ("tren", "trend", "ma 50", "ma50", "ma 200", "ma200")):
        return "trend"
    if any(word in text for word in ("sinyal", "signal", "indikator", "buy", "sell")):
        return "signals"
    return "overview"


def _agenda_market_channel(instrument: str | None = None) -> str:
    if instrument in {"XAUUSD", "XAGUSD", "XAUEUR", "XAGEUR", "XPDUSD"}:
        return "Untuk logam, saluran yang lazim dipantau adalah USD, imbal hasil, dan ekspektasi kebijakan moneter; reaksi aktual dapat berbeda dari ekspektasi."
    if instrument in {"EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCAD", "USDCHF", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"}:
        return "Untuk FX, pasar biasanya menilai perubahan relatif ekspektasi kebijakan mata uang yang bersangkutan, bukan hanya angka tajuk rilis."
    if instrument in {"SPX", "NAS100", "IHSG", "BBCA", "BBRI", "TLKM", "ASII", "BMRI", "UNVR", "GGRM", "HMSP", "ANTM"}:
        return "Untuk indeks dan saham, perhatian umumnya berada pada ekspektasi imbal hasil, pertumbuhan, serta dampak lintas sektor; respons tiap aset dapat berbeda."
    if instrument in {"BTCUSD", "ETHUSD", "BNBUSD", "SOLUSD", "XRPUSD", "ADAUSD", "DOTUSD", "MATICUSD", "LINKUSD", "AVAXUSD"}:
        return "Untuk kripto, agenda makro dapat bertepatan dengan perubahan likuiditas dan sentimen risiko, tetapi hubungannya tidak selalu stabil."
    if instrument in {"WTI", "BRENT", "XBRUSD", "XNGUSD"}:
        return "Untuk energi, dampak agenda makro perlu dibaca bersama data permintaan, inventori, pasokan, dan faktor geopolitik."
    if instrument == "DXY":
        return "Untuk DXY, fokusnya adalah perubahan relatif ekspektasi suku bunga dan prospek ekonomi AS terhadap mitra dagangnya."
    return "Dampak potensial perlu dibaca bersama instrumen, nilai aktual rilis, revisi data, dan ekspektasi pasar sebelum rilis."


def _calendar_section(agenda: AgendaDefinition, question: str = "", currency_filter: tuple[str, ...] = ()) -> str:
    events = find_calendar_events(agenda[3], currency_filter=currency_filter)
    status = calendar_fetch_status()
    if not events:
        focus = ", ".join(_CURRENCY_DISPLAY_NAMES.get(currency, currency) for currency in currency_filter)
        if status.state == "tidak_tersedia":
            return (
                "Sumber kalender publik dan fallback belum mengembalikan data pada pemindaian ini. "
                "Aero AI tidak akan membuat nilai forecast, previous, atau actual pengganti."
            )
        if focus:
            return (
                f"Tidak ada data kalender yang cocok untuk **{agenda_display_name(agenda, question)}** pada fokus **{focus}** di feed publik saat ini. "
                "Aero AI tidak akan menggantinya dengan rilis negara lain atau angka pengganti."
            )
        return (
            "Kalender publik mingguan belum memuat event yang cocok atau tidak menyediakan konsensus pada saat pemindaian. "
            "Aero AI tidak akan membuat nilai forecast, previous, atau actual pengganti."
        )
    requested_period = _retail_sales_period(question)
    if requested_period and agenda[1] in {"Retail Sales", "Core Retail Sales"}:
        marker = "m/m" if requested_period == "MoM" else "y/y"
        matching_period = [event for event in events if marker in event.title.casefold()]
        if matching_period:
            events = matching_period
    rows: list[str] = []
    for event in events:
        released = event.release_at.strftime("%d %b %Y %H:%M UTC") if event.release_at else "waktu rilis tidak tersedia dari fallback"
        actual = event.actual or "belum tersedia dari feed publik"
        forecast = event.forecast or "tidak tersedia"
        previous = event.previous or "tidak tersedia"
        rows.append(
            f"**{event.title} · {event.currency}** — jadwal **{released}**; dampak **{event.impact}**. "
            f"Actual: **{actual}**; forecast/konsensus sumber kalender: **{forecast}**; previous: **{previous}**. "
            f"Sumber: [{event.source_name}]({event.source_url})."
        )
    if requested_period and agenda[1] in {"Retail Sales", "Core Retail Sales"} and not any(
        ("m/m" if requested_period == "MoM" else "y/y") in event.title.casefold() for event in events
    ):
        rows.insert(
            0,
            f"Anda meminta **Retail Sales {requested_period}**. Feed kalender tidak menuliskan basis periode secara eksplisit pada judul event yang ditemukan; "
            "Aero AI menampilkan data sumber apa adanya dan tidak mengasumsikan MoM atau YoY dari nilai tersebut.",
        )
    if status.state == "cache_kedaluwarsa":
        rows.append(
            "**STATUS SUMBER KALENDER** — sumber publik sedang tidak merespons; data di atas berasal dari cache sesi terakhir yang tersedia dan tidak boleh dibaca sebagai pembaruan langsung."
        )
    return "\n\n".join(rows)


def _age_label(moment: datetime) -> str:
    seconds = max(0, int((datetime.now(timezone.utc) - moment.astimezone(timezone.utc)).total_seconds()))
    if seconds < 60:
        return "kurang dari satu menit"
    if seconds < 3600:
        return f"{seconds // 60} menit"
    if seconds < 86_400:
        return f"{seconds // 3600} jam"
    return f"{seconds // 86_400} hari"


def _freshness_section(snapshot: MarketSnapshot, fundamentals: list[FundamentalSnapshot]) -> str:
    candle_at = snapshot.last_candle_at.astimezone(timezone.utc)
    source_at = snapshot.fetched_at.astimezone(timezone.utc)
    fundamental_note = "Tidak ada konteks fundamental tambahan dari sumber publik pada pemindaian ini."
    if fundamentals:
        unique_sources = list(dict.fromkeys(item.source_name for item in fundamentals))
        fundamental_note = f"{len(fundamentals)} observasi tambahan dari {len(unique_sources)} sumber publik; frekuensi tiap seri ditampilkan pada kartu sumber."
    return (
        f"Candle terakhir: **{candle_at.strftime('%d %b %Y %H:%M UTC')}** ({_age_label(candle_at)} lalu). "
        f"Snapshot harga diambil: **{source_at.strftime('%H:%M:%S UTC')}**. {fundamental_note}"
    )


def _release_reaction_section(question: str, agenda: AgendaDefinition | None, snapshot: MarketSnapshot) -> str:
    """Ukur perubahan close di sekitar rilis hanya bila timestamp event dan candle beririsan."""
    text = question.casefold()
    if not agenda or not any(token in text for token in ("reaksi", "reaction", "setelah rilis", "pasca rilis")):
        return ""
    currency_filter = _agenda_calendar_currencies(agenda, question, snapshot.instrument.code)
    if _needs_currency_clarification(agenda, question, snapshot.instrument.code):
        return ""
    event = next((item for item in find_calendar_events(agenda[3], currency_filter=currency_filter) if item.release_at and item.actual), None)
    if not event or not event.release_at:
        return (
            "**RELEASE REACTION LENS**\n\n"
            "Tidak ada event yang memiliki timestamp dan nilai actual dari feed publik pada saat pemindaian. Aero AI tidak akan membentuk reaksi rilis dari jadwal atau forecast saja."
        )
    candles = snapshot.candles
    if candles.empty or "close" not in candles:
        return ""
    event_at = event.release_at
    candle_index = candles.index
    if getattr(candle_index, "tz", None) is None:
        event_at = event_at.replace(tzinfo=None)
    position = int(candle_index.searchsorted(event_at, side="left"))
    if position == 0 or position >= len(candles):
        return (
            "**RELEASE REACTION LENS**\n\n"
            "Timestamp agenda berada di luar jendela candle yang tersedia pada snapshot ini, sehingga reaksi historis tidak dihitung."
        )
    before_close = float(candles["close"].iloc[position - 1])
    first_close = float(candles["close"].iloc[position])
    horizon_position = min(position + 3, len(candles) - 1)
    horizon_close = float(candles["close"].iloc[horizon_position])
    first_change = (first_close / before_close - 1) * 100 if before_close else 0.0
    horizon_change = (horizon_close / before_close - 1) * 100 if before_close else 0.0
    return (
        "**RELEASE REACTION LENS**\n\n"
        f"Event **{event.title}** ({event.actual}) dijadwalkan pada **{event.release_at.strftime('%d %b %Y %H:%M UTC')}**. "
        f"Close candle pertama pada/ setelah jadwal berubah **{first_change:+.2f}%** dari close candle sebelumnya; perubahan sampai tiga candle setelahnya adalah **{horizon_change:+.2f}%**. "
        "Ini adalah observasi candle pada jendela data yang tersedia, bukan bukti sebab-akibat atau prediksi reaksi rilis berikutnya."
    )


def build_agenda_reply(question: str) -> str | None:
    """Buat jawaban agenda jika pengguna belum menyebut instrumen market."""
    agenda = detect_economic_agenda(question)
    if not agenda:
        return None
    _, _, context, _ = agenda
    name = agenda_display_name(agenda, question)
    if _needs_currency_clarification(agenda, question):
        return (
            f"{_agenda_clarification_section(agenda, question)}\n\n"
            "**BATAS ANALISIS**\n\nIni adalah konteks riset dan edukasi, bukan nasihat finansial personal atau instruksi transaksi."
        )
    currency_filter = _agenda_calendar_currencies(agenda, question)
    return (
        f"**KONTEKS AGENDA EKONOMI · {name}**\n\n"
        f"{context} {_agenda_market_channel()}\n\n"
        f"**DATA KALENDER PUBLIK**\n\n{_calendar_section(agenda, question, currency_filter)}\n\n"
        "Forecast atau consensus di atas adalah nilai yang tersedia dari sumber kalender, bukan prediksi yang dibuat Aero AI. "
        f"Apakah Anda ingin Aero AI menganalisa respons harga terhadap **{name}**? Sebutkan instrumen dan timeframe, misalnya **Analisa XAUUSD pada H1 setelah {name}**.\n\n"
        "**BATAS ANALISIS**\n\nIni adalah konteks riset dan edukasi, bukan nasihat finansial personal atau instruksi transaksi."
    )


def build_unknown_input_reply(question: str, unknown_candidates: list[str] | None = None) -> str:
    """Beri arahan eksplisit untuk typo pair, kode belum didukung, atau teks acak."""
    candidates = unknown_candidates or []
    if candidates:
        shown = ", ".join(f"**{candidate}**" for candidate in candidates[:3])
        return (
            f"Aero AI mendeteksi kode {shown}, tetapi instrumen atau pair tersebut **belum tersedia** pada daftar data publik yang dikonfigurasi. "
            "Silakan periksa ejaan atau gunakan kode yang tersedia, misalnya **XAUUSD**, EURUSD, BTCUSD, WTI, IHSG, atau BBCA. "
            "Jika Anda bermaksud menulis instrumen lain, sebutkan kode yang benar agar sistem tidak mengambil data yang salah."
        )
    compact = re.sub(r"\s+", "", question)
    if len(compact) >= 6 and not re.search(r"(?:analisa|market|agenda|indikator|risiko|trend|fundamental)", question.casefold()):
        return (
            "Pesan ini belum dapat dipahami sebagai pertanyaan market yang didukung. Aero AI masih berada dalam tahap pengembangan sebagai sistem pemindaian market berbasis data dan tidak dirancang untuk percakapan umum di luar konteks market. "
            "Mohon tulis instrumen atau agenda secara jelas, misalnya **Analisa XAUUSD pada H1**, **Jelaskan Retail Sales**, atau **NFP untuk DXY**."
        )
    return (
        "Pesan ini belum dapat dipetakan ke instrumen, timeframe, atau agenda ekonomi yang didukung. Aero AI masih berada dalam tahap pengembangan sebagai sistem pemindaian market berbasis data dan tidak dirancang untuk percakapan umum di luar konteks market. "
        "Silakan sebutkan instrumen, timeframe, atau agenda yang jelas. Contoh: **Analisa XAGUSD di M15**, **Bandingkan EURUSD dengan DXY pada H4**, **Jelaskan FOMC**, atau **Jelaskan Retail Sales MoM**."
    )


def build_source_unavailable_reply(instruments: list[str]) -> str:
    """Tampilkan kegagalan sumber publik tanpa mengungkap detail teknis atau membuat angka."""
    shown = ", ".join(f"**{instrument}**" for instrument in instruments[:2]) or "instrumen yang diminta"
    return (
        f"Sumber harga publik belum mengembalikan candle yang memadai untuk {shown} pada pemindaian ini. "
        "Aero AI tidak akan membuat harga, indikator, forecast, atau level pengganti ketika sumber eksternal terlambat atau tidak tersedia. "
        "Silakan coba kembali beberapa saat lagi, gunakan timeframe lain, atau pilih instrumen lain. Analisis Aero AI tetap ditujukan untuk riset dan edukasi, bukan nasihat finansial personal."
    )


def build_instrument_confirmation(instrument: str) -> str:
    return (
        f"Anda menyebut **{instrument}**. Apakah Anda ingin saya menganalisa instrumen tersebut? "
        f"Tambahkan timeframe agar pemindaian lebih spesifik, misalnya **Analisa {instrument} di M15**, **H4**, **D1**, **W1**, atau **MN**."
    )


def multi_instrument_clarification_prompts(instruments: list[str]) -> list[str]:
    """Buat tiga opsi fokus dari urutan instrumen yang memang ditulis pengguna."""
    codes = instruments[:3]
    if len(codes) < 3:
        return []
    return [
        f"Bandingkan {codes[0]} dengan {codes[1]} pada H1",
        f"Analisa {codes[0]} pada H1",
        f"Analisa {codes[2]} pada H1",
    ]


def build_multi_instrument_clarification(instruments: list[str]) -> str:
    """Hentikan pemindaian sebelum sistem mengabaikan instrumen ketiga atau berikutnya."""
    shown = ", ".join(f"**{code}**" for code in instruments[:5])
    extra = "" if len(instruments) <= 5 else f" serta {len(instruments) - 5} instrumen lainnya"
    return (
        f"Aero AI mendeteksi lebih dari dua instrumen: {shown}{extra}. "
        "Agar perbandingan tetap terbaca dan tidak ada instrumen yang diabaikan, pilih maksimal dua instrumen utama atau minta analisis satu per satu. "
        "Sistem belum akan menarik data sampai fokus tersebut jelas."
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
        "economic_agenda": "Fokus pertanyaan mencakup agenda ekonomi; narasi memisahkan data kalender publik dari kondisi harga aktual pada snapshot ini.",
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
    rsi, adx, volume = float(data["rsi14"]), float(data["adx14"]), float(data["relative_volume"])
    timeframe_note = (
        f"Timeframe **{timeframe_label(snapshot.interval)}** terdeteksi langsung dari pertanyaan Anda."
        if timeframe_was_explicit(question)
        else f"Timeframe tidak disebutkan; Aero AI menggunakan asumsi default **{timeframe_label(snapshot.interval)}**."
    )
    agenda = detect_economic_agenda(question)
    fundamentals = fundamentals or []
    agenda_section = ""
    if agenda:
        _, _, context, _ = agenda
        name = agenda_display_name(agenda, question)
        if _needs_currency_clarification(agenda, question, snapshot.instrument.code):
            agenda_section = f"\n\n{_agenda_clarification_section(agenda, question, snapshot.instrument.code)}"
        else:
            currency_filter = _agenda_calendar_currencies(agenda, question, snapshot.instrument.code)
            agenda_section = (
                f"\n\n**KONTEKS AGENDA EKONOMI · {name}**\n\n{context} {_agenda_market_channel(snapshot.instrument.code)}\n\n"
                f"**DATA KALENDER PUBLIK**\n\n{_calendar_section(agenda, question, currency_filter)}"
            )
    scenario_section = f"\n\n**SKENARIO LEVEL TEKNIKAL**\n\n{_entry_scenario(data)}" if intent == "levels_entry" else ""
    freshness_section = _freshness_section(snapshot, fundamentals)
    reaction_section = _release_reaction_section(question, agenda, snapshot)
    macro_section = macro_router_section(snapshot.instrument.code)
    trust_section = evidence_section(snapshot, fundamentals, calendar_fetch_status().state)
    regime_summary = regime_section(snapshot)
    history_summary = historical_section(snapshot)
    return (
        f"**STATUS PASAR · {snapshot.instrument.code}**\n\n"
        f"{timeframe_note} Harga referensi terakhir adalah **{price}** dengan perubahan **{change_20:+.2f}%** dalam 20 candle. Kondisi pada timeframe data saat ini adalah **{data['market_state']}** dengan keselarasan teknikal **{int(data['confluence'])}/100**. Nilai tersebut menunjukkan jumlah indikator yang searah, bukan probabilitas keberhasilan transaksi.\n\n"
        f"**FOKUS PEMINDAIAN**\n\n{_focus_line(intent, data)}\n\n"
        f"**STRUKTUR DAN MOMENTUM**\n\n{_trend_description(data)} RSI(14) berada pada **{rsi:.1f}**, ADX(14) pada **{adx:.1f}**, dan relative volume pada **{volume:.2f}x**. ADX mengukur kekuatan tren, bukan arahnya; volume relatif bernilai netral bila penyedia tidak menyediakan volume yang bermakna.\n\n"
        f"{regime_summary}\n\n"
        f"{macro_section}\n\n"
        f"{trust_section}\n\n"
        f"{history_summary}\n\n"
        f"**AREA OBSERVASI DAN RISIKO**\n\nRange 20 candle berada pada **{_fmt(float(data['low20']))}** sampai **{_fmt(float(data['high20']))}**. ATR(14) adalah **{_fmt(float(data['atr14']))}** dan volatilitas 20 candle **{float(data['volatility20']):.2f}%**. Bias harus dievaluasi ulang bila struktur harga bergerak melawan MA 50/MA 200 atau keluar dari range observasi.{agenda_section}{scenario_section}\n\n"
        f"**STATUS KETERBARUAN DATA**\n\n{freshness_section}\n\n"
        f"**KONTEKS FUNDAMENTAL PUBLIK**\n\n{_fundamental_section(fundamentals)}"
        f"{f'\n\n{reaction_section}' if reaction_section else ''}\n\n"
        f"**BATAS DATA**\n\n{snapshot.warning} Analisis ini dibuat untuk riset dan edukasi, bukan nasihat finansial personal."
    )


def follow_up_prompts(instrument: str, interval: str | None = None) -> list[str]:
    suffix = f" pada timeframe {timeframe_label(interval)}" if interval else ""
    return [
        f"Apakah Anda ingin saya menganalisa {instrument}{suffix}?",
        f"Bandingkan {instrument} dengan DXY{suffix}",
        f"Jelaskan tren {instrument} berdasarkan MA 50 dan MA 200{suffix}",
        f"Tinjau risiko {instrument} dari ATR dan volatilitas{suffix}",
        f"Jelaskan 10 indikator {instrument}{suffix}",
        f"Tentukan area observasi high, low, dan Fibonacci {instrument}{suffix}",
        f"Tentukan Entry, SL, TP1 TP2 TP3 dan Risk untuk {instrument}{suffix}",
        f"Jelaskan dampak NFP untuk {instrument}{suffix}",
        f"Jelaskan dampak CPI untuk {instrument}{suffix}",
        f"Jelaskan dampak Retail Sales untuk {instrument}{suffix}",
        f"Jelaskan Retail Sales MoM untuk {instrument}{suffix}",
        f"Jelaskan Retail Sales YoY untuk {instrument}{suffix}",
        f"Jelaskan konteks FOMC untuk {instrument}{suffix}",
        f"Nilai momentum dan konfluensi indikator {instrument}{suffix}",
        f"Rangkum konteks fundamental publik untuk {instrument}{suffix}",
    ]
