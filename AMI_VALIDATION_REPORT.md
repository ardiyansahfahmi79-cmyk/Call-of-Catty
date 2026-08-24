# Laporan Validasi Peningkatan AMI

**Tanggal validasi:** 24 Agustus 2026 (GMT+7)  
**Ruang lingkup:** Prototipe Aero AI saja. Website utama, repository utama yang private, database, domain, Cloudflare, dan integrasi broker tidak diubah.

> **Status keseluruhan: LULUS.** Seluruh kompilasi dan suite regresi yang dijalankan selesai dengan exit code `0`. Hasil ini membuktikan kontrak implementasi dan perilaku yang diuji pada snapshot/data publik saat pengujian, bukan akurasi prediksi harga atau jaminan hasil trading.

## 1. Fitur yang selesai diterapkan

| Komponen | Implementasi | Status |
|---|---|---|
| Struktur harga kausal | Swing terkonfirmasi setelah dua candle, HH/HL/LL/LH, penembusan struktur berbasis close, FVG tiga candle, dan Fibonacci dari swing terkonfirmasi. | **LULUS** |
| Proteksi look-ahead | Pivot tidak tersedia sebelum candle konfirmasi di sisi kanan selesai; penembusan memakai close, bukan wick. | **LULUS** |
| Konteks volatilitas | Bollinger Bands (20,2), lebar band dibanding jendela historis pendek, dan posisi close pada band. | **LULUS** |
| Level periode selesai | Pivot Classic PP/R1/S1 dihitung dari hari sebelum hari candle terakhir. | **LULUS** |
| Konteks sesi | Jendela Tokyo, London, dan New York dihitung dari timestamp candle dengan zona waktu IANA; London/New York mengikuti daylight-saving. | **LULUS** |
| Respons level dan risiko | Permintaan level menampilkan struktur harga, konteks volatilitas/waktu, serta skenario Entry/SL/TP yang tetap bersyarat. | **LULUS** |
| Batas respons | Jargon implementasi, sumber teknis internal, dan instruksi transaksi personal tidak muncul pada kontrak respons yang diuji. | **LULUS** |
| Grafik | Konfigurasi line chart tetap `staticPlot`, tanpa modebar, zoom, atau scroll zoom; CSS tetap mematikan interaksi pointer pada grafik. | **LULUS** |
| Evaluasi historis | Harness penelitian terpisah dengan MA50/MA200/RSI kausal, split train/validation/test, dan censor gap 24 jam. | **LULUS** |

## 2. Hasil pengujian

| Pengujian | Hasil aktual | Status |
|---|---|---|
| Kompilasi semua modul Python | `python3 -m py_compile *.py` | **LULUS** |
| Struktur harga | `market_structure_ok=swings:4 state:BULLISH break:PENEMBUSAN STRUKTUR BULLISH` | **LULUS** |
| Konteks volatilitas/sesi | `market_context_ok=bb:RENTANG RELATIF STABIL pivot:2025-01-06 london:London` | **LULUS** |
| Evaluasi historis kausal | `historical_evaluation_ok=train:151 validation:51 test:51` | **LULUS** |
| Kontrak integrasi respons/grafik | `integration_contract_ok=reply_chars:2079 static_chart:yes` | **LULUS** |
| Ekspansi kategori | 7 kategori × 50 kasus = `total:350` | **LULUS** |
| Matriks percakapan utama | `336 skenario lokal` | **LULUS** |
| Matriks format/alias/semantik | `conversation_matrix_ok=1236 alias=1004 pair_format=200 semantic=32` | **LULUS** |
| Intent lokal | `local_intent_ok=patterns:38 cases:11` | **LULUS** |
| Respons ringkas agenda | `concise_dxy_nfp_ok` | **LULUS** |
| Skenario ekstrem | `extreme_market_ok=spx_date:2020-03-17` | **LULUS** |
| Variasi status NFP | `before_release, actual_with_forecast, actual_without_forecast` | **LULUS** |
| Quote publik | `pair_quote_ok` dengan EURUSD bid/ask dan XAUUSD reference spot tersedia saat uji | **LULUS** |
| XAUUSD Entry/SL/TP bersyarat | `xau_entry_ok` | **LULUS** |
| Uji fitur sumber publik | XAGUSD M15 menghasilkan 2.222 candle dan 462 event kalender saat uji | **LULUS** |

## 3. Pemeriksaan data historis publik

Runner penelitian memeriksa **kelayakan data untuk split temporal**, bukan kualitas atau akurasi arah harga. Hasil berikut tidak boleh dibaca sebagai hit rate, forecast, atau rekomendasi.

| Instrumen | Train | Validation | Test | Status |
|---|---:|---:|---:|---|
| EURUSD H1 | 319 | 106 | 107 | **LAYAK RISET** |
| XAUUSD H1 | 245 | 82 | 82 | **LAYAK RISET** |
| BTCUSD H1 | 331 | 111 | 111 | **LAYAK RISET** |
| US100 H1 | 62 | 21 | 21 | **LAYAK RISET** |

`LAYAK RISET` hanya berarti data yang tersedia melewati ambang minimum internal untuk split temporal dan censor gap. Angka performa tidak ditampilkan sampai hipotesis, biaya/spread, slippage, jendela evaluasi, dan hasil out-of-sample dirancang serta diaudit secara terpisah.

## 4. Komponen yang sengaja tidak diaktifkan

| Komponen | Status | Alasan |
|---|---|---|
| Quote atau eksekusi broker | **DITUNDA** | Memerlukan broker pilihan pengguna, kredensial server-side, mapping simbol, bid/ask/timestamp/spread, dan mode read-only lebih dulu. |
| Berita generik / sentimen model | **DITUNDA** | Membutuhkan sumber teks berlisensi, evaluasi, resource, dan guardrail tambahan; tidak diperlukan untuk struktur harga fase ini. |
| Volume profile/order flow forex | **DITUNDA** | Volume forex publik tidak terpusat; AMI tidak boleh mengubah proxy volume menjadi klaim order flow institusional. |
| Multi-agent atau model prediksi harga | **DITUNDA** | Tidak menambahkannya sebelum data, definisi target, dan validasi kausal membuktikan kegunaannya. |
| Klaim “94%” atau “100%” | **TIDAK DITERAPKAN** | Tidak ada bukti evaluasi out-of-sample lengkap yang mendukung klaim tersebut. |

## 5. Berkas prototipe yang ditambahkan

| Berkas | Fungsi |
|---|---|
| `market_structure.py` | Kalkulasi struktur harga kausal. |
| `market_context.py` | Bollinger, pivot periode selesai, dan konteks sesi berbasis timestamp. |
| `historical_evaluation.py` | Harness evaluasi penelitian terpisah dari chat. |
| `aero_ai_market_structure_test.py` | Regresi struktur dan proteksi look-ahead. |
| `aero_ai_market_context_test.py` | Regresi volatilitas, pivot, dan sesi. |
| `aero_ai_historical_evaluation_test.py` | Regresi split temporal dan censor gap. |
| `aero_ai_historical_research_run.py` | Runner kelayakan data historis publik. |
| `aero_ai_integration_contract_test.py` | Kontrak respons level, jargon, klarifikasi risiko, dan grafik statis. |

## 6. Basis, waktu, asumsi, dan batas

**Basis:** perhitungan struktur memakai OHLC publik; indikator risiko memakai candle yang tersedia; referensi bid/ask publik dipisahkan dari candle.  
**Waktu:** hasil ini berlaku pada pelaksanaan validasi 24 Agustus 2026 GMT+7; quote dan kalender publik dapat berubah atau gagal di waktu lain.  
**Asumsi:** evaluasi historis memakai screen kausal MA50/MA200/RSI, horizon tiga candle, serta censor gap 24 jam; belum memasukkan biaya broker aktual.  
**Sumber dan keyakinan:** candle/quote/kalender memakai adapter publik aktif AMI; data publik dapat tertunda dan bukan harga eksekusi broker. Hasil regresi lokal sangat tinggi untuk kontrak perilaku yang diuji, tetapi tidak sama dengan akurasi market.  
**Kepatuhan:** seluruh fitur disajikan untuk riset dan edukasi, bukan nasihat finansial personal atau instruksi transaksi.
