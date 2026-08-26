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

## Konverter multi-mata uang — 26 Agustus 2026

| Area | Hasil |
|---|---|
| Cakupan awal sumber | Endpoint sumber mengembalikan 166 kode kurs, termasuk basis USD. |
| Pilihan aplikasi | Lulus: UI menampilkan 165 pilihan mata uang setelah satu kode dikecualikan. |
| Hasil default | Lulus: 100 USD dikonversi ke IDR sesudah tombol pemuatan kurs ditekan. |
| Pengecualian kode | Diterapkan pada mesin daftar dan fungsi konversi, sehingga kode terblokir tidak muncul dan tidak dapat dikonversi. |

## Pilihan mode konverter — 26 Agustus 2026

| Area | Hasil |
|---|---|
| Mode awal | Lulus: `Konversi nilai` menjadi pilihan awal dan menampilkan input jumlah yang jelas. |
| Mode kedua | Tersedia: `Bandingkan kurs` untuk membandingkan nilai satu unit mata uang asal dan tujuan. |
| Keadaan sebelum kurs dimuat | Lulus: pilihan mata uang serta hasil tetap tersembunyi sampai pengguna menekan `Muat Mata Uang & Kurs`. |
| Bandingkan Kurs setelah dimuat | Lulus: hasil menampilkan `1 USD = 17.714,5656 IDR` dengan pilihan mata uang asal dan tujuan yang jelas. |

## Grafik tren kurs tujuh hari — 26 Agustus 2026

| Area | Hasil |
|---|---|
| Pengambilan riwayat | Lulus: endpoint historis Frankfurter mengembalikan lima hari kurs USD–IDR dalam jendela tujuh hari kalender; akhir pekan tidak memiliki publikasi kurs. |
| Tombol grafik | Lulus: tombol `Tampilkan Grafik Tren 7 Hari` baru muncul sesudah kurs dan pilihan mata uang tersedia. |
| Render grafik | Lulus pada desktop: grafik garis menampilkan lima titik USD–IDR, sumbu tanggal, sumbu kurs, tooltip, dan perubahan dari titik pertama ke terakhir. |
| Transparansi | Lulus: UI menyebut rentang tanggal, jumlah hari kurs yang tersedia, perubahan persentase, tautan Frankfurter, serta batas bahwa ini bukan harga broker real-time. |
| Fallback | Diterapkan: bila riwayat pasangan tidak tersedia, aplikasi memberi peringatan dan tidak membuat garis sintetis. |
| Tampilan ponsel | Lulus pada viewport 375 px: alur memuat kurs lalu grafik dapat dijalankan, dan lebar dokumen tetap 375 px tanpa overflow horizontal. |

## Penyederhanaan Bandingkan Kurs — 26 Agustus 2026

| Area | Hasil |
|---|---|
| Mode tunggal | Lulus: pilihan radio Konversi Nilai/Bandingkan Kurs dan kolom jumlah telah dihapus. |
| Daftar pilihan | Lulus: sumber publik menyediakan 90 mata uang negara hasil kurasi pada antarmuka. |
| Label ponsel | Lulus: dropdown memakai bendera dan kode, dengan pasangan hasil seperti `🇮🇩 IDR → 🇺🇸 USD`. |
| Hasil awal | Lulus: nilai standar membandingkan satu IDR terhadap USD tanpa meminta pengguna memasukkan nominal. |
| Grafik pasangan awal | Lulus: grafik tren IDR–USD tujuh hari tetap muncul beserta titik data, perubahan persentase, dan atribusi sumber. |

## Pencarian dan tren 30 hari — 26 Agustus 2026

| Area | Hasil |
|---|---|
| Pencarian cepat | Lulus: kata kunci `USD` menyaring daftar pembanding menjadi satu opsi, yaitu `🇺🇸 USD`. |
| Nilai awal | Lulus: sesi baru dimulai dengan pasangan `🇮🇩 IDR → 🇺🇸 USD`. |
| Riwayat 30 hari | Lulus: pasangan IDR–USD menampilkan 22 hari kurs yang tersedia pada rentang 27 Juli–25 Agustus 2026; hari tanpa publikasi tidak ditambahkan. |
| Grafik Plotly statis | Lulus: konfigurasi render menunjukkan `staticPlot=true`, `scrollZoom=false`, `displayModeBar=false`, `dragmode=false`, serta sumbu X/Y `fixedrange=true`. |
| Tampilan ponsel | Lulus pada viewport 375 px: alur memuat kurs, pencarian, dan grafik tiga puluh hari berjalan tanpa overflow horizontal. |

## Transparansi nilai referensi — 26 Agustus 2026

| Area | Hasil |
|---|---|
| Posisi pemberitahuan | Lulus: catatan tampil tepat setelah sumber dan waktu pembaruan kurs, sebelum tombol grafik tren. |
| Isi pemberitahuan | Lulus: menjelaskan perbedaan nilai akibat waktu pembaruan, spread, biaya, dan metode penetapan kurs, tanpa menjanjikan kesetaraan dengan nilai transaksi atau harga eksekusi. |

## Input nominal dan angka rencana — 26 Agustus 2026

| Area | Hasil |
|---|---|
| Nominal kurs | Lulus: pasangan `🇺🇸 USD → 🇮🇩 IDR` dengan nominal `1` menampilkan `1 USD = 17,714.57 IDR` dari kurs referensi yang dimuat. |
| Pencarian mata uang | Lulus: kolom pencarian cepat tidak lagi ditampilkan. |
| Harga Masuk | Lulus: nilai `158.293` tetap tampil persis sama setelah tombol Hitung Risiko Saya ditekan; aplikasi tidak menambah nol atau memformat ulang teks. |
