# Validasi Aero AI Trade — 25 Agustus 2026

Halaman `aero_ai_trade.py` dirender melalui Streamlit lokal pada port 8519. Tampilan menampilkan dashboard profesional dengan pemberitahuan **MODE PROTOTIPE / PAPER TRADING**, status broker **BELUM TERHUBUNG**, status browser session aktif, dan status **LIVE EXECUTION DINONAKTIFKAN**.

Kontrol **Aktifkan Auto Trade Simulasi** diuji. Hasilnya hanya mengubah status mode Paper Auto menjadi aktif serta menambahkan entri audit yang secara eksplisit menyatakan bridge broker tidak tersedia. Tidak ada input kredensial aktif dan tidak ada koneksi broker yang dimulai.

Kontrol **Emergency Stop** kemudian diuji. Hasilnya mengembalikan mode Paper Auto ke pause dan menambah audit trail bahwa order baru simulasi diblokir. Tidak ada tindakan terhadap broker, posisi, atau akun eksternal.

Guardrail heartbeat juga diuji setelah versi baru dimuat ulang. Ketika timestamp sebelumnya telah melewati TTL 55 detik, status browser berubah menjadi **KEDALUWARSA**, Paper Auto tetap pause, dan tombol pembuatan posisi simulasi diblokir dengan alasan yang tampil di layar. Ini membuktikan perilaku fail-closed pada rerun Streamlit; tidak ada panggilan Headway MT5 maupun akses broker selama pengujian.

Sesudah tombol **Refresh heartbeat sesi** dipilih, status browser kembali aktif, tetapi pembuatan posisi masih diblokir sampai **Aktifkan Auto Trade Simulasi** dipilih. Urutan ini teruji: Paper mode aktif + heartbeat valid + Paper Auto aktif adalah syarat bersama sebelum catatan posisi simulasi dapat dibuat.

Satu posisi uji `PAPER-001` kemudian dibuat dan menampilkan `XAUUSD`, `BUY`, lot `0.01`, status `OPEN · PAPER`, serta kolom quote yang secara eksplisit menyatakan **Tidak dikutip pada prototipe**. Sesudah itu, guard membatasi entry baru pada satu posisi. Tombol **Close PAPER-001 (Paper)** diuji dan menghapus catatan tersebut, lalu audit mencatat bahwa proses penutupan tidak mengirim perintah broker.
