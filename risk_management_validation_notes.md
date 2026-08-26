# Validasi Kalkulator Risiko Sederhana

Tanggal validasi: 26 Agustus 2026.

| Area | Hasil |
|---|---|
| Kompilasi Python | Lulus untuk `risk_management_core.py`, `risk_management_prototype.py`, dan kontrak uji. |
| Kontrak kalkulasi normal | Lulus: saldo US$1.000, risiko 1%, SL 5, target 10, menghasilkan risiko US$10, R:R 1:2, dan estimasi 0,020 sesuai nilai input. |
| Guard batas rugi | Lulus: skenario yang melewati batas rugi harian diberi status `BATAS RUGI TERCAPAI`. |
| Guard stop loss | Lulus: saat stop loss sama dengan entry, estimasi lot menjadi 0 dan UI menampilkan peringatan tanpa crash. |
| Render Streamlit | Lulus pada desktop; halaman kini menampilkan saldo, risiko per transaksi, harga masuk, Stop Loss, Target Profit, pengaturan opsional, dan empat hasil inti. |
| Koneksi eksternal | Tidak ada: prototipe tidak menggunakan broker, akun, database, harga live, atau perintah transaksi. |

Catatan: nilai lot bergantung pada nilai pergerakan harga per lot yang diinput pengguna. Nilai tersebut harus diverifikasi terhadap spesifikasi kontrak broker sebelum digunakan sebagai dasar keputusan.

## Perbaikan tombol dan kurs — 26 Agustus 2026

| Area | Hasil |
|---|---|
| Keadaan awal | Lulus: hasil risiko tersembunyi dan hanya menampilkan pesan bahwa pengguna perlu menekan tombol perhitungan. |
| Tombol `Hitung Risiko Saya` | Lulus: empat hasil inti baru tampil setelah formulir disubmit. |
| Konverter USD–Rupiah | Lulus: nilai USD dan kurs publik hanya tampil setelah tombol `Perbarui Kurs` ditekan. |
| Transparansi kurs | Lulus: UI menampilkan nilai referensi, waktu pembaruan, jadwal pembaruan berikutnya, serta atribusi sumber. |
| Fallback | Diterapkan: jika kurs publik gagal dimuat, aplikasi tidak membuat nilai baru dan menawarkan input kurs manual opsional. |
