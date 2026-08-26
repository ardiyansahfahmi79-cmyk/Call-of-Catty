# Sumber Kurs Konverter USD–Rupiah

Kalkulator menggunakan endpoint publik ExchangeRate-API `https://open.er-api.com/v6/latest/USD` untuk memperoleh kurs referensi dengan basis USD. Endpoint ini tidak memerlukan API key, mengembalikan waktu pembaruan terakhir serta jadwal pembaruan berikutnya, dan memperbarui data sekali per hari.

UI harus mencantumkan atribusi **Rates By Exchange Rate API** dengan tautan ke dokumentasi sumber. Kurs ditampilkan sebagai kurs referensi harian untuk perencanaan, bukan kurs eksekusi broker, harga transfer bank, atau jaminan nilai transaksi.

Dokumentasi sumber menyebut 165 mata uang yang umum beredar. Aplikasi membangun pilihan dari respons sumber yang terbaru dan mengecualikan satu kode mata uang secara eksplisit, sehingga jumlah pilihan aktual tampil pada UI dan dapat berubah jika cakupan sumber berubah.

Jika sumber tidak dapat diakses atau respons tidak valid, konverter tidak membuat nilai kurs baru. UI hanya menampilkan input kurs manual yang dapat diisi pengguna beserta status bahwa pembaruan publik tidak tersedia.

Referensi:

- https://www.exchangerate-api.com/docs/free
