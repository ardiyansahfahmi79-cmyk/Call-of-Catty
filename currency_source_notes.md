# Sumber Kurs Konverter USD–Rupiah

Kalkulator menggunakan endpoint publik ExchangeRate-API `https://open.er-api.com/v6/latest/USD` untuk memperoleh kurs referensi dengan basis USD. Endpoint ini tidak memerlukan API key, mengembalikan waktu pembaruan terakhir serta jadwal pembaruan berikutnya, dan memperbarui data sekali per hari.

UI harus mencantumkan atribusi **Rates By Exchange Rate API** dengan tautan ke dokumentasi sumber. Kurs ditampilkan sebagai kurs referensi harian untuk perencanaan, bukan kurs eksekusi broker, harga transfer bank, atau jaminan nilai transaksi.

Antarmuka dikurasi menjadi 90 mata uang negara dari Asia, Eropa, Afrika, Amerika, dan Oseania. Sebuah kode hanya muncul bila juga tersedia pada respons sumber publik; satu kode yang diblokir tidak masuk ke daftar atau perhitungan.

Jika sumber tidak dapat diakses atau respons tidak valid, konverter tidak membuat nilai kurs baru dan meminta pengguna mencoba memuat ulang.

## Grafik tren tujuh hari

Grafik menggunakan endpoint historis Frankfurter `https://api.frankfurter.dev/v1/` dengan mata uang asal dan tujuan yang dipilih pengguna. Dokumentasi Frankfurter menyatakan data historis tersedia tanpa API key dan bersumber dari bank sentral; jumlah titik dapat kurang dari tujuh karena kurs referensi umumnya tidak diterbitkan saat akhir pekan atau hari tanpa publikasi.

Grafik adalah referensi kurs harian, bukan harga broker, harga transfer bank, atau kuotasi eksekusi trading. Bila riwayat pasangan tidak tersedia, aplikasi menampilkan status gagal dan tidak membuat garis sintetis.

Referensi:

- https://www.exchangerate-api.com/docs/free
