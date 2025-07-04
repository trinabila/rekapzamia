import streamlit as st
import pandas as pd
import os
from datetime import date

# Buat folder data kalau belum ada
os.makedirs("data", exist_ok=True)
DATA_PATH = "data/rekap.xlsx"

# Load atau inisialisasi rekap
if os.path.exists(DATA_PATH):
    df_rekap = pd.read_excel(DATA_PATH)
else:
    df_rekap = pd.DataFrame(columns=["Tanggal","Pembeli","Barang","Banyaknya","Harga","Jumlah"])

st.set_page_config(page_title="Nota Penjualan", layout="wide")
st.title("🧾 Aplikasi Nota Penjualan")

# --- Sidebar Form Input ---
st.sidebar.header("Input Penjualan Baru")
tanggal = st.sidebar.date_input("Tanggal", date.today())
pembeli = st.sidebar.text_input("Nama Pembeli / Toko")

st.sidebar.subheader("Item yang Dijual")

# Inisialisasi session_state
if "items" not in st.session_state:
    st.session_state["items"] = []

# Tombol tambah item
if st.sidebar.button("Tambah Baris Item"):
    st.session_state["items"].append({"barang": "", "banyaknya": 0.0, "harga": 0.0})

# Render form per item
for idx, it in enumerate(st.session_state["items"]):
    col1, col2, col3, col4 = st.sidebar.columns([3, 2, 2, 1])
    it["barang"] = col1.text_input("Barang", value=it["barang"], key=f"barang_{idx}")
    it["banyaknya"] = col2.number_input("Banyaknya", value=it["banyaknya"], key=f"banyak_{idx}", format="%.2f")
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
            jumlah = it["banyaknya"] * it["harga"]
            rows.append({
                "Tanggal": tanggal,
                "Pembeli": pembeli,
                "Barang": it["barang"],
                "Banyaknya": it["banyaknya"],
                "Harga": it["harga"],
                "Jumlah": jumlah
            })
        df_nota = pd.DataFrame(rows)
        df_rekap = pd.concat([df_rekap, df_nota], ignore_index=True)
        df_rekap.to_excel(DATA_PATH, index=False)
        st.session_state["items"] = []
        st.success("Nota berhasil disimpan!")

# --- Preview Nota Terakhir ---
if 'df_nota' in locals():
    st.subheader("📋 Preview Nota Terakhir")
    st.table(df_nota.assign(Jumlah=lambda x: x["Jumlah"].map("Rp {:,.2f}".format)))

# --- Tampilkan Rekap ---
st.subheader("📈 Rekap Penjualan")
if not df_rekap.empty:
    df_tampil = df_rekap.copy()
    df_tampil["Jumlah"] = df_tampil["Jumlah"].map
