import streamlit as st
import pandas as pd

from pages.sidebar import cek_login_atau_stop, render_sidebar
from utils.database import import_dari_excel

st.set_page_config(page_title="Import Excel — SIPKKB", page_icon="📤", layout="centered")

cek_login_atau_stop()
render_sidebar()

# =====================================================================
# KONTEN HALAMAN
# =====================================================================
st.title("📤 Import Massal via File Excel")
st.info("Fitur ini hanya tersedia untuk Admin. Data dari semua fungsi dapat di-import sekaligus.")

file = st.file_uploader("Pilih file Excel dataset", type=['xlsx', 'xls'])
if file is not None:
    try:
        df_up = pd.read_excel(file)
        st.write(f"**Pratinjau** ({len(df_up)} baris):")
        st.dataframe(df_up.head(5), use_container_width=True)
        if st.button("Jalankan Proses Batch Import", type="primary", use_container_width=True):
            with st.spinner("Memproses..."):
                jumlah = import_dari_excel(df_up)
            if jumlah > 0:
                st.success(f"Berhasil import **{jumlah}** data!"); st.rerun()
            else:
                st.error("Gagal import. Pastikan nama kolom Excel sesuai template.")
    except Exception as e:
        st.error(f"Gagal memproses Excel: {e}")
