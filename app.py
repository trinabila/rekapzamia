import streamlit as st
import pandas as pd
import os
import re
from datetime import date

# Setup file & folder
os.makedirs("data", exist_ok=True)
DATA_PATH = "data/rekap.xlsx"

# Load rekap data
if os.path.exists(DATA_PATH):
    df_rekap = pd.read_excel(DATA_PATH)
else:
    df_rekap = pd.DataFrame(columns=["Tanggal", "Pembeli", "Barang", "Banyaknya", "Harga", "Jumlah"])

st.set_page_config(page_title="Nota Penjualan", layout="wide")
st.title("🧾 Aplikasi Nota Penjualan")

# Sidebar: Form Input
st.sidebar.header("Input Penjualan Baru")
tanggal = st.sidebar.date_input("Tanggal", date.today())
pembeli = st.sidebar.text_input("Nama Pembeli / Toko")

st.sidebar.subheader("Item yang Dijual")

# Inisialisasi item di session_state
if "items" not in st.session_state:
    st.session_state["items"] = []

# Tombol tambah item
if st.sidebar.button("Tambah Baris Item"):
    st.session_state["items"].append({"barang": "", "rol": "", "harga": 0.0})

# Input form untuk setiap item
for idx, it in enumerate(st.session_state["items"]):
    col1, col2, col3, col4 = st.sidebar.columns([3, 3, 2, 1])

    it["barang"] = col1.text_input("Nama Barang", value=it["barang"], key=f"barang_{idx}")
    it["rol"] = col2.text_input("Rincian Rol (misal: (73) (58,8))", value=it["rol"], key=f"rol_{idx}")
    it["harga"] = col3.number_input("Harga", value=it["harga"], key=f"harga_{idx}", format="%.0f")

    if col4.button("❌", key=f"hapus_{idx}"):
        st.session_state["items"].pop(idx)
        st.experimental_rerun()

# Tombol simpan
if st.sidebar.button("Simpan & Tampilkan Nota"):
    if not pembeli or len(st.session_state["items"]) == 0:
        st.sidebar.error("Isi nama pembeli dan minimal 1 item ya!")
    else:
        rows = []
        for it in st.session_state["items"]:
            angka_str = re.findall(r"\((.*?)\)", it.get("rol", ""))
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

# Tampilkan preview nota
if 'df_nota' in locals():
    st.subheader("📋 Preview Nota Terakhir")
    st.table(df_nota.assign(Jumlah=lambda x: x["Jumlah"].map("Rp {:,.2f}".format)))

# Tampilkan rekap penjualan
st.subheader("📈 Rekap Penjualan")
if not df_rekap.empty:
    df_tampil = df_rekap.copy()
    df_tampil["Jumlah"] = df_tampil["Jumlah"].map("Rp {:,.2f}".format)
    st.dataframe(df_tampil)
else:
    st.write("Belum ada data rekap.")
