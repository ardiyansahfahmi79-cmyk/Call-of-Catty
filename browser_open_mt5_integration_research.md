# Riset Integrasi Browser-Terbuka Headway MT5

Tanggal riset: 25 Agustus 2026.

## Temuan resmi

MetaTrader 5 Web Platform memungkinkan pengguna melakukan trading manual dari browser, termasuk akun demo/real, order market/pending, quote real-time, dan one-click trading. Dokumentasi Headway hanya menyatakan ketersediaan MT5 WebTerminal untuk akun demo/real serta aplikasi terminal untuk Windows/macOS. Tidak ditemukan dokumentasi resmi publik Headway yang menawarkan API order retail untuk menghubungkan aplikasi Streamlit ke akun pengguna.

Halaman API MetaTrader 5 yang ditemukan ditujukan untuk broker: Server API, Manager API, Gateway API, dan Web API adalah komponen integrasi sistem broker/perusahaan, bukan endpoint retail yang dapat diakses pengguna biasa dengan login/password MT5. Karena itu, browser Streamlit tidak dapat secara aman atau resmi mengontrol tombol WebTerminal, membaca kredensialnya, atau mengirim order ke akun Headway hanya melalui ID/password.

## Audit repository GitHub (pasif, tidak ada kode dijalankan)

| Repository | Temuan | Kelayakan untuk Aero AI Trade |
| --- | --- | --- |
| `dceoy/streamlit-metatrader5-metrics` | Aplikasi Streamlit untuk metrik MT5 **di Windows**; membutuhkan Python/MT5 lokal. Lisensi AGPL-3.0. | Tidak diintegrasikan: tetap membutuhkan terminal Windows dan lisensi copyleft perlu evaluasi. |
| `devcartel/pymt5` | Mengharuskan DevCartel MT5 gateway dipasang di platform; README memperlihatkan alur login/password dalam data gateway. Lisensi MIT. | Ditolak untuk kebutuhan ini: menambah gateway pihak ketiga dan pola kredensial tidak sesuai kebijakan dashboard. |
| `ryu878/MT5-python-bot` | Contoh sederhana open/close dengan Python MetaTrader5; README meminta pengguna mengubah akun dan parameter langsung di file. Lisensi yang dilaporkan halaman GitHub: Apache-2.0, namun README menyebut MIT (konflik metadata). Membutuhkan MT5 terpasang. | Tidak diintegrasikan: konfigurasi akun dalam source dan tetap memerlukan terminal MT5. Hanya menjadi referensi pola tingkat tinggi. |
| `Maxiviper117/PyTrader-python-mt4-mt5` | Connector Python–EA berbasis WebSocket. Repo memuat binary EA `.ex5`; fungsi demo dibatasi beberapa instrumen dan versi penuh ditautkan ke Marketplace. | Tidak diintegrasikan: membungkus EA pihak ketiga/binary dan tidak menjamin dukungan XAUUSD Headway demo. |

## Kesimpulan teknis

1. Menjaga browser Streamlit terbuka dapat menjadi sinyal heartbeat UI, tetapi tidak menggantikan terminal MT5 atau API broker.
2. Dashboard tidak boleh menerima ID/password MT5; kredensial seharusnya hanya dimasukkan pengguna ke WebTerminal Headway untuk trading manual atau terminal desktop yang didukung.
3. Komponen Aero AI Trade yang sudah ada tetap benar: browser dashboard → bridge privat → terminal MT5 yang sudah login. Untuk browser-only tanpa komputer, tidak ada jalur API retail resmi Headway yang dapat diverifikasi.
4. Integrasi GitHub yang paling aman adalah mengadopsi **ide arsitektur** seperti audit, keepalive, magic number, order validation, dan position filtering secara orisinal; bukan mengimpor kode/binary pihak ketiga.

## Referensi

1. MetaTrader 5, *Web platform* — https://www.metatrader5.com/en/trading-platform/web-trading
2. MetaTrader 5, *For Brokers / APIs* — https://www.metatrader5.com/en/brokers
3. Headway, *MT5 & MT4 platforms* — https://hw.online/platforms/
4. dceoy/streamlit-metatrader5-metrics — https://github.com/dceoy/streamlit-metatrader5-metrics
5. devcartel/pymt5 — https://github.com/devcartel/pymt5
6. ryu878/MT5-python-bot — https://github.com/ryu878/MT5-python-bot
7. Maxiviper117/PyTrader-python-mt4-mt5 — https://github.com/Maxiviper117/PyTrader-python-mt4-mt5
