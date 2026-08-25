# Dasar Integrasi Headway MT5 Demo

Tanggal riset: 25 Agustus 2026.

## Fakta terverifikasi

Headway mendokumentasikan pembuatan akun demo MT5 pada komputer dan menyatakan bahwa MT5 membuat login serta password demo setelah registrasi. Akun demo dimaksudkan untuk mencoba strategi tanpa modal nyata. Headway juga menyediakan MT5 untuk Windows serta WebTerminal untuk akun demo.

Dokumentasi MQL5 menyatakan modul Python `MetaTrader5` berkomunikasi langsung dengan terminal MT5 melalui interprocess communication. Antarmuka tersebut menyediakan pembacaan status terminal dan akun, tick/bar, posisi, order aktif, serta riwayat. Operasi trading termasuk `order_check` dan `order_send`; dua operasi ini harus dipisahkan secara ketat dari mode monitoring dan Paper Trading.

Dokumentasi `order_check` menegaskan pemeriksaan hanya memeriksa kecukupan dana dan request valid tidak menjamin eksekusi berhasil. Dokumentasi `order_send` mewajibkan request memuat tindakan, simbol, volume, harga, deviasi, dan ticket posisi pada penutupan. `positions_get` dapat mengambil posisi berdasarkan ticket, sehingga close per posisi harus dibatasi pada posisi dengan magic number bridge.

## Implikasi rancangan

1. Streamlit tidak boleh menjadi eksekutor broker langsung; ia hanya panel kontrol dan visualisasi.
2. Untuk integrasi akun demo, MT5 harus berjalan pada mesin Windows yang memiliki terminal Headway MT5 dan telah login ke server demo.
3. Bridge lokal wajib hanya mengizinkan mode `demo`, memeriksa account/terminal state, menggunakan `order_check` sebelum setiap order, serta membatalkan tindakan saat heartbeat kontrol hilang.
4. Kredensial demo tetap berada pada terminal/secret store lokal; tidak dimasukkan ke repository, UI Streamlit, atau log audit.
5. Kode eksekusi broker tidak akan dipanggil hingga pengguna meninjau detail order demo dan memberikan konfirmasi eksplisit untuk order pertama; penutupan hanya dapat merujuk posisi dengan magic number bridge.

## Referensi primer

1. Headway, *MetaTrader 5: A Step-by-Step Guide to Creating a Demo Account on PC* — https://hw.online/faq/metatrader-5-a-step-by-step-guide-to-creating-a-demo-account-on-pc/
2. Headway, *MetaTrader 5 & 4 trading platforms* — https://hw.online/platforms/
3. MQL5, *MetaTrader module for integration with Python* — https://www.mql5.com/en/docs/python_metatrader5
4. MetaTrader 5, *Working with Python* — https://www.metatrader5.com/en/metaeditor/help/development/python
5. MQL5, *order_check — Python Integration* — https://www.mql5.com/en/docs/python_metatrader5/mt5ordercheck_py
6. MQL5, *order_send — Python Integration* — https://www.mql5.com/en/docs/python_metatrader5/mt5ordersend_py
7. MQL5, *positions_get — Python Integration* — https://www.mql5.com/en/docs/python_metatrader5/mt5positionsget_py
