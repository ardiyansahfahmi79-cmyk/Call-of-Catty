# Validasi Prototipe Risk Management

Tanggal validasi: 26 Agustus 2026.

| Area | Hasil |
|---|---|
| Kompilasi Python | Lulus untuk `risk_management_core.py`, `risk_management_prototype.py`, dan kontrak uji. |
| Kontrak kalkulasi normal | Lulus: saldo US$1.000, risiko 1%, SL 5, target 10, menghasilkan risiko US$10, R:R 1:2, dan estimasi 0,020 sesuai nilai input. |
| Guard batas rugi | Lulus: skenario yang melewati batas rugi harian diberi status `BATAS RUGI TERCAPAI`. |
| Guard stop loss | Lulus: saat stop loss sama dengan entry, estimasi lot menjadi 0 dan UI menampilkan peringatan tanpa crash. |
| Render Streamlit | Lulus pada desktop; hierarki hero, konfigurasi, matriks, metrik, tabel simulasi, dan penjaga batas tampil. |
| Koneksi eksternal | Tidak ada: prototipe tidak menggunakan broker, akun, database, harga live, atau perintah transaksi. |

Catatan: nilai lot bergantung pada nilai pergerakan harga per lot yang diinput pengguna. Nilai tersebut harus diverifikasi terhadap spesifikasi kontrak broker sebelum digunakan sebagai dasar keputusan.
