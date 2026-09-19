import os
from datetime import datetime
import json
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


# ---------------------------------------------------
# PENYIMPANAN PESANAN (Google Sheets)
# ---------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
NAMA_SPREADSHEET = "PesananDariKuki"  # samakan dengan nama spreadsheet kamu
KOLOM_PESANAN = ["waktu", "nama_pemesan", "nama_kue", "jumlah", "no_hp", "catatan", "total"]

creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client_gsheet = gspread.authorize(creds)
sheet = client_gsheet.open(NAMA_SPREADSHEET).sheet1

# kalau sheet masih kosong, tulis baris header dulu
if not sheet.get_all_values():
    sheet.append_row(KOLOM_PESANAN)


def simpan_pesanan(data_pesanan: dict):
    """Tambahkan satu baris pesanan baru ke Google Sheet"""
    baris = [data_pesanan[kolom] for kolom in KOLOM_PESANAN]
    sheet.append_row(baris)


def baca_pesanan() -> pd.DataFrame:
    """Baca semua pesanan dari Google Sheet sebagai DataFrame"""
    data = sheet.get_all_records()
    if not data:
        return pd.DataFrame(columns=KOLOM_PESANAN)
    return pd.DataFrame(data)

# bagian koneksi credentials
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.environ.get("RENDER"):
    CREDENTIALS_PATH = "/etc/secrets/credentials.json"
else:
    CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")

creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
# ---------------------------------------------------
# DATA MENU KUE
# Ganti / tambah item di sini sesuai kue yang kamu jual
# ---------------------------------------------------
menu_kue = [
    {
        "id": 1,
        "nama": "Classic Cookie",
        "harga": 25000,
        "deskripsi": "Brownies coklat lembut dengan taburan kacang almond.",
        "gambar": "Classic Cookie.png",
    },
    {
        "id": 2,
        "nama": "Kue Cubit",
        "harga": 15000,
        "deskripsi": "Kue cubit mini dengan topping keju dan meses.",
        "gambar": "Classic Cookie.png",
    },
    {
        "id": 3,
        "nama": "Red Velvet Cake",
        "harga": 45000,
        "deskripsi": "Cake merah lembut dengan lapisan cream cheese.",
        "gambar": "Classic Cookie.png",
    },
    {
        "id": 4,
        "nama": "Nastar",
        "harga": 60000,
        "deskripsi": "Kue nastar isi selai nanas, dijual per toples (isi 20 pcs).",
        "gambar": "Classic Cookie.png",
    },
        {
        "id": 5,
        "nama": "Classic Cookie",
        "harga": 25000,
        "deskripsi": "Brownies coklat lembut dengan taburan kacang almond.",
        "gambar": "Classic Cookie.png",
    },
    {
        "id": 6,
        "nama": "Kue Cubit",
        "harga": 15000,
        "deskripsi": "Kue cubit mini dengan topping keju dan meses.",
        "gambar": "Classic Cookie.png",
    },
    {
        "id": 7,
        "nama": "Red Velvet Cake",
        "harga": 45000,
        "deskripsi": "Cake merah lembut dengan lapisan cream cheese.",
        "gambar": "Classic Cookie.png",
    },
    {
        "id": 8,
        "nama": "Nastar",
        "harga": 60000,
        "deskripsi": "Kue nastar isi selai nanas, dijual per toples (isi 20 pcs).",
        "gambar": "Classic Cookie.png",
    }
]


def format_rupiah(angka):
    """Ubah angka jadi format Rp 35.000"""
    return f"Rp {angka:,.0f}".replace(",", ".")


# daftarkan filter supaya bisa dipakai di template (format_rupiah)
app.jinja_env.filters["rupiah"] = format_rupiah


@app.route("/")
def halaman_menu():
    """Halaman utama: menampilkan semua menu kue"""
    return render_template("index.html", menu=menu_kue, active_page="menu")


@app.route("/pesan/<int:item_id>", methods=["GET", "POST"])
def halaman_pesan(item_id):
    """Halaman kedua: form pemesanan untuk 1 item kue"""
    item = next((k for k in menu_kue if k["id"] == item_id), None)
    if item is None:
        return redirect(url_for("halaman_menu"))

    if request.method == "POST":
        nama_pemesan = request.form.get("nama_pemesan")
        jumlah = request.form.get("jumlah")
        no_hp = request.form.get("no_hp")
        catatan = request.form.get("catatan")

        # Di sini kamu bisa simpan pesanan ke database, kirim email,
        # atau kirim notifikasi WhatsApp. Untuk contoh ini kita hanya
        # tampilkan halaman konfirmasi sederhana.
        jumlah = int(jumlah)
        total = item["harga"] * jumlah

        # simpan pesanan supaya muncul di dashboard penjualan
        simpan_pesanan(
            {
                "waktu": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "nama_pemesan": nama_pemesan,
                "nama_kue": item["nama"],
                "jumlah": jumlah,
                "no_hp": no_hp,
                "catatan": catatan,
                "total": total,
            }
        )

        return render_template(
            "konfirmasi.html",
            item=item,
            nama_pemesan=nama_pemesan,
            jumlah=jumlah,
            no_hp=no_hp,
            catatan=catatan,
            total=total,
            active_page="menu",
        )

    return render_template("pesan.html", item=item, active_page="menu")


@app.route("/dashboard")
def halaman_dashboard():
    df = baca_pesanan()

    if not df.empty:
        df["waktu"] = pd.to_datetime(df["waktu"])

    tanggal_dari = request.args.get("dari", "")
    tanggal_sampai = request.args.get("sampai", "")

    if not df.empty and tanggal_dari:
        df = df[df["waktu"] >= pd.to_datetime(tanggal_dari)]
    if not df.empty and tanggal_sampai:
        batas_akhir = pd.to_datetime(tanggal_sampai) + pd.Timedelta(days=1)
        df = df[df["waktu"] < batas_akhir]

    total_pendapatan = int(df["total"].sum()) if not df.empty else 0
    total_pesanan = len(df)
    total_kue_terjual = int(df["jumlah"].sum()) if not df.empty else 0
    terlaris = (
        df.groupby("nama_kue")["jumlah"].sum().idxmax() if not df.empty else "-"
    )

    # data untuk grafik: total penjualan per hari
    if not df.empty:
        df["tanggal"] = df["waktu"].dt.strftime("%Y-%m-%d")
        grafik_df = df.groupby("tanggal")["total"].sum().reset_index().sort_values("tanggal")
        grafik_labels = grafik_df["tanggal"].tolist()
        grafik_data = grafik_df["total"].tolist()
    else:
        grafik_labels = []
        grafik_data = []

    pesanan = df.sort_values("waktu", ascending=False).to_dict("records") if not df.empty else []
    for p in pesanan:
        p["waktu"] = p["waktu"].strftime("%Y-%m-%d %H:%M")

    return render_template(
        "dashboard.html",
        pesanan=pesanan,
        total_pendapatan=total_pendapatan,
        total_pesanan=total_pesanan,
        total_kue_terjual=total_kue_terjual,
        terlaris=terlaris,
        active_page="dashboard",
        tanggal_dari=tanggal_dari,
        tanggal_sampai=tanggal_sampai,
        grafik_labels=json.dumps(grafik_labels),
        grafik_data=json.dumps(grafik_data),
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
