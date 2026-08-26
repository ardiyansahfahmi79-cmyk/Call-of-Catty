# Sumber Kurs Konverter USD–Rupiah

Kalkulator menggunakan endpoint publik ExchangeRate-API `https://open.er-api.com/v6/latest/USD` untuk memperoleh nilai USD ke IDR. Endpoint ini tidak memerlukan API key, mengembalikan waktu pembaruan terakhir serta jadwal pembaruan berikutnya, dan memperbarui data sekali per hari.

UI harus mencantumkan atribusi **Rates By Exchange Rate API** dengan tautan ke dokumentasi sumber. Kurs ditampilkan sebagai kurs referensi harian untuk perencanaan, bukan kurs eksekusi broker, harga transfer bank, atau jaminan nilai transaksi.

Jika sumber tidak dapat diakses atau respons tidak valid, konverter tidak membuat nilai kurs baru. UI hanya menampilkan input kurs manual yang dapat diisi pengguna beserta status bahwa pembaruan publik tidak tersedia.

Referensi:

- https://www.exchangerate-api.com/docs/free
