import streamlit as st
import pandas as pd
import os
from datetime import date

# Pastikan folder data ada
os.makedirs("data", exist_ok=True)
DATA_PATH = "data/rekap.xlsx"

# Load atau inisialisasi rekap
if os.path.exists(DATA_PATH):
    df_rekap = pd.read_excel(DATA_PATH)
else:
    df_rekap = pd.DataFrame(columns=["Tanggal","Pembeli","Barang","Banyaknya","Harga","Jumlah"])

st.title("🧾 Aplikasi Nota Penjualan")

# --- Form Input ---
st.sidebar.header("Input Penjualan Baru")
tanggal = st.sidebar.date_input("Tanggal", date.today())
pembeli = st.sidebar.text_input("Nama Pembeli / Toko")

# Isi tabel dinamis
st.sidebar.subheader("Item yang Dijual")
items = st.session_state.get("items", [])
if "items" not in st.session_state:
    st.session_state.items = []

def tambah_item():
    st.session_state.items.append({"barang":"", "banyaknya":0.0, "harga":0.0})

def hapus_item(idx):
    st.session_state.items.pop(idx)

st.sidebar.button("Tambah Baris Item", on_click=tambah_item)

# Render item dalam form
for idx, it in enumerate(st.session_state.items):
    col1,col2,col3,col4 = st.sidebar.columns([3,2,2,1])
    it["barang"] = col1.text_input("Barang", value=it["barang"], key=f"barang_{idx}")
    it["banyaknya"] = col2.number_input("Banyaknya", value=it["banyaknya"], format="%.2f", key=f"banyaknya_{idx}")
    it["harga"] = col3.number_input("Harga", value=it["harga"], format="%.2f", key=f"harga_{idx}")
    if col4.button("🗑️", key=f"hapus_{idx}"):
        hapus_item(idx)
        st.experimental_rerun()

# Proses nota
if st.sidebar.button("Simpan & Tampilkan Nota"):
    if not pembeli or len(st.session_state.items)==0:
        st.sidebar.error("Isi semua data dulu ya!")
    else:
        rows = []
        for it in st.session_state.items:
            jumlah = it["banyaknya"] * it["harga"]
            rows.append({
                "Tanggal": tanggal,
                "Pembeli": pembeli,
                "Barang": it["barang"],
                "Banyaknya": it["banyaknya"],
                "Harga": it["harga"],
                "Jumlah": jumlah
            })
        df_notes = pd.DataFrame(rows)
        # Append ke rekap & simpan
        df_rekap = pd.concat([df_rekap, df_notes], ignore_index=True)
        df_rekap.to_excel(DATA_PATH, index=False)
        st.session_state.items = []
        st.success("Nota tersimpan! Cek preview di bawah.")

# --- Tampilkan Nota Preview & Rekap ---
st.header("Preview Nota Terakhir")
if 'df_notes' in locals():
    st.table(df_notes.assign(Jumlah=lambda x: x["Jumlah"].map("Rp {:,.2f}".format)))

st.header("Rekap Penjualan")
if not df_rekap.empty:
    df_show = df_rekap.copy()
    df_show["Jumlah"] = df_show["Jumlah"].map("Rp {:,.2f}".format)
    st.dataframe(df_show)
else:
    st.write("Belum ada data rekap.")
