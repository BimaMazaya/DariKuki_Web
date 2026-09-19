# Menu Kue (Flask)

Project sederhana: halaman utama menampilkan menu kue, halaman kedua untuk pemesanan.

## Cara menjalankan di VSCode

1. Buka folder ini di VSCode (`File > Open Folder...`).
2. Buka terminal di VSCode (`Terminal > New Terminal`).
3. Buat virtual environment:
   ```
   python -m venv venv
   ```
4. Aktifkan virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
5. Install dependency:
   ```
   pip install -r requirements.txt
   ```
6. Jalankan aplikasi:
   ```
   python app.py
   ```
7. Buka browser ke: http://127.0.0.1:5000

## Struktur folder

```
menu-kue/
├── app.py                  <- data menu & route Flask
├── requirements.txt
├── templates/
│   ├── index.html          <- halaman menu (utama)
│   ├── pesan.html          <- halaman form pemesanan
│   └── konfirmasi.html     <- halaman setelah pesan dikirim
└── static/
    ├── style.css
    └── images/              <- taruh foto kue di sini
```

## Cara menambah/mengubah menu

Edit list `menu_kue` di `app.py` — tambahkan dictionary baru dengan format:
```python
{
    "id": 5,
    "nama": "Nama Kue",
    "harga": 20000,
    "deskripsi": "Deskripsi singkat",
    "gambar": "nama_file.jpg",
}
```
Lalu taruh foto dengan nama yang sama di `static/images/`.

## Catatan

- Ini contoh dasar: pesanan belum disimpan ke database, hanya ditampilkan
  di halaman konfirmasi setelah form dikirim. Kalau nanti mau pesanan
  benar-benar tersimpan (atau dikirim ke WhatsApp/email), itu bisa
  ditambahkan di fungsi `halaman_pesan()` pada `app.py`.
