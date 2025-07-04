import streamlit as st
import pandas as pd
import os
import re
from datetime import date, datetime
from PIL import Image, ImageDraw, ImageFont
import io
---------- INFO TOKO ----------
NAMA_TOKO = 'Tenun Tradisional "ZAMIA"'
ALAMAT_TOKO = 'Jalan Jaya Bhakti III/131 Medono - Pekalongan'
KONTAK_TOKO = '085870156300'
PENUTUP = 'Hormat Kami: Hasanudin - Ibah'
---------- SETUP ----------
os.makedirs("data", exist_ok=True)
DATA_PATH = "data/rekap.xlsx"
---------- Load data lama ----------
if os.path.exists(DATA_PATH):
df_rekap = pd.read_excel(DATA_PATH)
else:
df_rekap = pd.DataFrame(columns=["Tanggal", "Pembeli", "Barang", "Banyaknya", "Harga", "Jumlah"])
st.set_page_config(page_title="Nota Penjualan", layout="wide")
st.title("🧾 Aplikasi Nota Penjualan")
---------- INPUT ----------
st.sidebar.header("Input Penjualan Baru")
tanggal = st.sidebar.date_input("Tanggal", date.today())
pembeli = st.sidebar.text_input("Nama Pembeli / Toko")
st.sidebar.subheader("Item yang Dijual")
if "items" not in st.session_state:
st.session_state["items"] = []
if st.sidebar.button("Tambah Baris Item"):
st.session_state["items"].append({"barang": "", "rol": "", "harga": 0.0})
for idx, it in enumerate(st.session_state["items"]):
col1, col2, col3, col4 = st.sidebar.columns([3, 3, 2, 1])
it["barang"] = col1.text_input("Nama Barang", value=it["barang"], key=f"barang_{idx}")
it["rol"] = col2.text_input("Rincian Rol (misal: (73) (58,8))", value=it["rol"], key=f"rol_{idx}")
it["harga"] = col3.number_input("Harga", value=it["harga"], key=f"harga_{idx}", format="%.0f")
if col4.button("❌", key=f"hapus_{idx}"):
st.session_state["items"].pop(idx)
st.experimental_rerun()
---------- SIMPAN NOTA ----------
if st.sidebar.button("Simpan & Tampilkan Nota"):
if not pembeli or len(st.session_state["items"]) == 0:
st.sidebar.error("Isi nama pembeli dan minimal 1 item ya!")
else:
rows = []
for it in st.session_state["items"]:
angka_str = re.findall(r"", it.get("rol", ""))
try:
panjang_list = [float(x.replace(",", ".").strip()) for x in angka_str]
except:
panjang_list = []
banyaknya = sum(panjang_list)
rincian_kurung = " ".join(f"({x})" for x in angka_str)
barang_ditampilkan = f"{it['barang']} {rincian_kurung}"
rows.append({
"Tanggal": tanggal,
"Pembeli": pembeli,
"Barang": barang_ditampilkan,
"Banyaknya": banyaknya,
"Harga": it["harga"],
"Jumlah": banyaknya * it["harga"]
})
    df_nota = pd.DataFrame(rows)
    df_rekap = pd.concat([df_rekap, df_nota], ignore_index=True)
    df_rekap.to_excel(DATA_PATH, index=False)
    st.session_state["items"] = []
    st.success("Nota berhasil disimpan!")

    # ---------- GENERATE GAMBAR NOTA ---------- #
    width, height = 800, 600 + len(df_nota) * 40
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    y = 20
    line_height = 20

    draw.text((width//2 - 150, y), NAMA_TOKO, font=font, fill="black")
    y += line_height
    draw.text((width//2 - 150, y), ALAMAT_TOKO, font=font, fill="black")
    y += line_height
    draw.text((width//2 - 150, y), f"HP/WA: {KONTAK_TOKO}", font=font, fill="black")
    y += 2 * line_height
    draw.text((50, y), f"Tanggal : {tanggal.strftime('%d %B %Y')}", font=font, fill="black")
    y += line_height
    draw.text((50, y), f"Pembeli : {pembeli}", font=font, fill="black")
    y += 2 * line_height

    draw.text((50, y), "No", font=font, fill="black")
    draw.text((100, y), "Nama Barang", font=font, fill="black")
    draw.text((400, y), "Banyaknya", font=font, fill="black")
    draw.text((500, y), "Harga", font=font, fill="black")
    draw.text((620, y), "Jumlah", font=font, fill="black")
    y += line_height

    total = 0
    for i, row in df_nota.iterrows():
        draw.text((50, y), str(i+1), font=font, fill="black")
        draw.text((100, y), row["Barang"], font=font, fill="black")
        draw.text((400, y), f"{row['Banyaknya']:.2f}".replace(".", ","), font=font, fill="black")
        draw.text((500, y), f"Rp {int(row['Harga']):,}".replace(",", "."), font=font, fill="black")
        draw.text((620, y), f"Rp {int(row['Jumlah']):,}".replace(",", "."), font=font, fill="black")
        total += row["Jumlah"]
        y += line_height

    y += line_height
    draw.text((500, y), "Total:", font=font, fill="black")
    draw.text((620, y), f"Rp {int(total):,}".replace(",", "."), font=font, fill="black")
    y += 3 * line_height
    draw.text((width - 300, y), PENUTUP, font=font, fill="black")

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    st.image(img_bytes, caption="Nota PNG", use_column_width=True)
    st.download_button("📥 Download Nota sebagai PNG", data=img_bytes, file_name="nota_zamia.png", mime="image/png")

---------- PREVIEW NOTA ----------
if 'df_nota' in locals():
st.subheader("📋 Preview Nota Terakhir")
df_preview = df_nota.copy()
df_preview["Banyaknya"] = df_preview["Banyaknya"].map(lambda x: f"{x:.2f}".replace(".", ","))
df_preview["Harga"] = df_preview["Harga"].map(lambda x: f"Rp {int(x):,}".replace(",", "."))
df_preview["Jumlah"] = df_preview["Jumlah"].map(lambda x: f"Rp {int(x):,}".replace(",", "."))
st.dataframe(df_preview)
---------- REKAP ----------
st.subheader("📈 Rekap Penjualan")
if not df_rekap.empty:
df_tampil = df_rekap.copy()
df_tampil["Banyaknya"] = df_tampil["Banyaknya"].map(lambda x: f"{x:.2f}".replace(".", ","))
df_tampil["Harga"] = df_tampil["Harga"].map(lambda x: f"Rp {int(x):,}".replace(",", "."))
df_tampil["Jumlah"] = df_tampil["Jumlah"].map(lambda x: f"Rp {int(x):,}".replace(",", "."))
st.dataframe(df_tampil)
else:
st.write("Belum ada data rekap.")
