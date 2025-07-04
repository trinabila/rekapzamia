import streamlit as st
import pandas as pd
import os
import re
from datetime import date, datetime
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

# ---------- INFO TOKO ---------- #
NAMA_TOKO = 'Tenun Tradisional "ZAMIA"'
ALAMAT_TOKO = 'Jalan Jaya Bhakti III/131 Medono - Pekalongan'
KONTAK_TOKO = '085870156300'
PENUTUP = 'Hasanudin - Ibah'

# Kamus bulan manual
bulan_indo = {
    'January': 'Januari', 'February': 'Februari', 'March': 'Maret',
    'April': 'April', 'May': 'Mei', 'June': 'Juni',
    'July': 'Juli', 'August': 'Agustus', 'September': 'September',
    'October': 'Oktober', 'November': 'November', 'December': 'Desember'
}

# ---------- SETUP ---------- #
os.makedirs("data", exist_ok=True)
DATA_PATH = "data/rekap.xlsx"

# ---------- Load data lama ---------- #
if os.path.exists(DATA_PATH):
    df_rekap = pd.read_excel(DATA_PATH)
else:
    df_rekap = pd.DataFrame(columns=["Tanggal", "Pembeli", "Barang", "Rincian", "Banyaknya", "Harga", "Jumlah"])

st.set_page_config(page_title="Nota Penjualan", layout="wide")
st.title("🧾 Aplikasi Nota Penjualan")

# ---------- INPUT ---------- #
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

# ---------- SIMPAN NOTA ---------- #
if st.sidebar.button("Simpan & Tampilkan Nota"):
    if not pembeli or len(st.session_state["items"]) == 0:
        st.sidebar.error("Isi nama pembeli dan minimal 1 item ya!")
    else:
        rows = []
        for it in st.session_state["items"]:
            angka_str = re.findall(r"\((\d+(?:[.,]\d+)?)\)", it.get("rol", ""))
            try:
                panjang_list = [float(x.replace(",", ".")) for x in angka_str]
                banyaknya = sum(panjang_list)
            except:
                panjang_list = []
                banyaknya = 0
            rincian_kurung = " ".join(f"({x})" for x in angka_str) if panjang_list else ""
            barang_ditampilkan = it['barang']
            jumlah = banyaknya * it["harga"]
            rows.append({
                "Tanggal": tanggal,
                "Pembeli": pembeli,
                "Barang": barang_ditampilkan,
                "Rincian": rincian_kurung,
                "Banyaknya": banyaknya,
                "Harga": it["harga"],
                "Jumlah": jumlah
            })

        df_nota = pd.DataFrame(rows)
        df_rekap = pd.concat([df_rekap, df_nota], ignore_index=True)
        df_rekap.to_excel(DATA_PATH, index=False)
        st.session_state["items"] = []
        st.success("Nota berhasil disimpan!")

        # ---------- GENERATE GAMBAR NOTA ---------- #
        width, height = 800, 600 + len(df_nota) * 60
        img = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 16)
            bold_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
        except:
            font = ImageFont.load_default()
            bold_font = font

        y = 20
        line_height = 24

        draw.text((width//2 - 150, y), NAMA_TOKO, font=bold_font, fill="black")
        y += line_height
        draw.text((width//2 - 150, y), ALAMAT_TOKO, font=font, fill="black")
        y += line_height
        draw.text((width//2 - 150, y), f"HP/WA: {KONTAK_TOKO}", font=font, fill="black")
        y += 2 * line_height

        # Format tanggal manual dengan kamus
        tanggal_str = tanggal.strftime('%d %B %Y')
        for eng, indo in bulan_indo.items():
            tanggal_str = tanggal_str.replace(eng, indo)

        draw.text((50, y), f"Tanggal: {tanggal_str}", font=font, fill="black")
        y += line_height
        draw.text((50, y), f"Pembeli: {pembeli}", font=font, fill="black")
        y += 2 * line_height

        draw.text((50, y), "No", font=bold_font, fill="black")
        draw.text((100, y), "Nama Barang", font=bold_font, fill="black")
        draw.text((400, y), "Banyaknya", font=bold_font, fill="black")
        draw.text((500, y), "Harga", font=bold_font, fill="black")
        draw.text((620, y), "Jumlah", font=bold_font, fill="black")
        y += line_height

        total = 0
        for i, row in df_nota.iterrows():
            draw.text((50, y), str(i+1), font=font, fill="black")
            draw.text((100, y), row["Barang"], font=font, fill="black")
            y += line_height
            if row["Rincian"]:
                draw.text((100, y), row["Rincian"], font=font, fill="black")
            draw.text((400, y - line_height), f"{row['Banyaknya']:.2f}".replace(".", ","), font=font, fill="black")
            draw.text((500, y - line_height), f"Rp {int(row['Harga']):,}".replace(",", "."), font=font, fill="black")
            draw.text((620, y - line_height), f"Rp {int(row['Jumlah']):,}".replace(",", "."), font=font, fill="black")
            total += row["Jumlah"]
            y += line_height

        y += line_height
        draw.text((500, y), "Total:", font=bold_font, fill="black")
        draw.text((620, y), f"Rp {int(total):,}".replace(",", "."), font=bold_font, fill="black")
        y += 3 * line_height
        draw.text((width - 250, y), "Hormat Kami", font=font, fill="black")
        y += 2 * line_height
        draw.text((width - 300, y), PENUTUP, font=bold_font, fill="black")

        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        st.image(img_bytes, caption="Nota PNG")
        st.download_button("📥 Download Nota sebagai PNG", data=img_bytes, file_name="nota_zamia.png", mime="image/png")

# ---------- PREVIEW NOTA ---------- #
if 'df_nota' in locals():
    st.subheader("📋 Preview Nota Terakhir")
    df_preview = df_nota.copy()
    df_preview["Banyaknya"] = df_preview["Banyaknya"].map(lambda x: f"{x:.2f}".replace(".", ",") if pd.notnull(x) else "")
    df_preview["Harga"] = df_preview["Harga"] = df_preview["Harga"].map(lambda x: f"Rp {int(x):,}".replace(",", ".") if pd.notnull(x) else "")
    df_preview["Jumlah"] = df_preview["Jumlah"].map(lambda x: f"Rp {int(x):,}".replace(",", ".") if pd.notnull(x) else "")
    st.dataframe(df_preview)

# ---------- REKAP ---------- #
st.subheader("📈 Rekap Penjualan")
if not df_rekap.empty:
    df_tampil = df_rekap.copy()
    df_tampil["Banyaknya"] = pd.to_numeric(df_tampil["Banyaknya"], errors="coerce")
    df_tampil["Harga"] = pd.to_numeric(df_tampil["Harga"], errors="coerce")
    df_tampil["Jumlah"] = pd.to_numeric(df_tampil["Jumlah"], errors="coerce")

    df_tampil["Banyaknya"] = df_tampil["Banyaknya"].map(lambda x: f"{x:.2f}".replace(".", ",") if pd.notnull(x) else "")
    df_tampil["Harga"] = df_tampil["Harga"].map(lambda x: f"Rp {int(x):,}".replace(",", ".") if pd.notnull(x) else "")
    df_tampil["Jumlah"] = df_tampil["Jumlah"].map(lambda x: f"Rp {int(x):,}".replace(",", ".") if pd.notnull(x) else "")

    st.dataframe(df_tampil)
else:
    st.write("Belum ada data rekap.")
