# Aero AI Trade

Dashboard Streamlit untuk monitoring **Headway MT5 akun demo**, Paper Trading, dan evaluasi proposal scalping secara fail-closed. Dashboard tidak meminta password broker dan tidak memasukkan kredensial ke repository.

## Menjalankan dashboard

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Tanpa bridge lokal, dashboard tetap berjalan sebagai Paper Trading dan menampilkan status broker belum terhubung.

## Mode browser-only tanpa komputer

Dashboard menyediakan tautan aman ke [Headway MT5 Demo WebTerminal](https://hw.online/webterminal/mt5-demo/). Login ID, password, dan server dimasukkan **hanya** pada halaman broker tersebut. Aero AI Trade tidak menerima atau memvalidasi kredensial WebTerminal, tidak dapat membaca posisi/history WebTerminal, dan tidak dapat menekan tombol Buy, Sell, atau Close di tab broker. Mode ini dipakai untuk menjaga Paper Trading dan risk guard dashboard terbuka sambil Anda melakukan trading demo secara manual pada WebTerminal.

## Menghubungkan Headway MT5 akun demo secara lokal

Jalankan bridge hanya pada **Windows** yang memiliki terminal Headway MT5, telah login manual ke akun **demo**, serta dibuka pada mesin yang sama dengan dashboard. Jangan masukkan password MT5 ke Streamlit, `.env` yang di-commit, atau GitHub.

```powershell
pip install -r requirements-demo-bridge.txt
$env:AERO_TRADE_BRIDGE_TOKEN = "buat-secret-acak-minimal-24-karakter"
python headway_mt5_demo_bridge.py
```

Pada jendela PowerShell yang menjalankan Streamlit, setel environment berikut sebelum menjalankan dashboard:

```powershell
$env:AERO_TRADE_BRIDGE_URL = "http://127.0.0.1:8765"
$env:AERO_TRADE_BRIDGE_TOKEN = "secret-yang-sama"
streamlit run streamlit_app.py
```

Bridge ini memverifikasi bahwa terminal MT5 tersambung dan akun memiliki mode **demo**. Ia menolak akun non-demo, menolak URL HTTP jarak jauh, membutuhkan heartbeat panel yang masih hidup, dan menyimpan audit chain lokal. Endpoint scan scalping hanya membaca data MT5 serta tidak mengirim order.

Jalur proposal dan close sudah tersedia di bridge, tetapi eksekusi demo tetap **nonaktif secara default**. Ia memerlukan proposal berumur 30 detik, `order_check` broker, frasa konfirmasi per tindakan, dan environment `AERO_TRADE_DEMO_EXECUTION_ENABLED=YES` yang disetel secara lokal. Posisi hanya dapat ditutup jika membawa magic number Aero AI Trade; posisi manual atau EA lain tidak disentuh.

## Kebijakan scalping demo awal

Mode scalping awal dibatasi ke `XAUUSD`, lot maksimal `0.01`, satu posisi terbuka, batas spread `50` points, serta batas kerugian harian `0.50%`. Sinyal hanya dapat muncul dari struktur M1 EMA 9/21 dengan filter ATR. Kondisi yang tidak memenuhi syarat menghasilkan `NO_TRADE`; sistem tidak mengubah kondisi ambigu menjadi sinyal.

> Ini adalah perangkat riset dan uji akun demo, bukan nasihat finansial personal atau jaminan hasil. Trading berleverage memiliki risiko.

## Struktur

| File | Fungsi |
| --- | --- |
| `aero_ai_trade.py` | Dashboard Streamlit dan Paper Trading. |
| `headway_mt5_demo_bridge.py` | Bridge Windows lokal untuk pembacaan MT5 demo, heartbeat, kill switch, posisi, dan history. |
| `scalping_rules.py` | Aturan sinyal dan risk guard yang deterministik. |
| `trade_demo_client.py` | Klien aman dashboard ke bridge lokal/HTTPS. |
| `requirements-demo-bridge.txt` | Dependency khusus Windows bridge. |
| `headway_mt5_research_notes.md` | Catatan sumber resmi dan batas integrasi. |

## Catatan pembersihan Aero AI lama

Modul chat Aero AI lama di root telah dipindahkan/pensiunkan dari repository ini; implementasi produksinya berada pada repository utama. Berkas `aero_ai_*_test.py` sengaja dipertahankan sebagai harness historis dan tidak dijalankan oleh alur Aero AI Trade. Harness tersebut memerlukan modul chat lama atau paket produksi utama bila ingin digunakan kembali.
