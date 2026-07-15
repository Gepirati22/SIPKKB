import streamlit as st
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pages.sidebar import cek_login_atau_stop, render_sidebar
from utils.database import load_semua_kegiatan

st.set_page_config(page_title="Dashboard — SIPKKB", page_icon="🏠", layout="centered")

cek_login_atau_stop()
render_sidebar()

# =====================================================================
# KONTEN HALAMAN
# =====================================================================
st.title("Dashboard SIPKKB")
st.markdown("**Sistem Informasi Program Kampung Keluarga Berkualitas** — Evaluasi berbasis Decision Tree C4.5")
st.markdown("---")

df_all = load_semua_kegiatan()

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Total Data Kegiatan", len(df_all))
with col2: st.metric("Fungsi Aktif", f"{df_all['Nama Fungsi'].nunique() if len(df_all)>0 else 0}/8")
with col3: st.metric("Bulan Tercatat", df_all['Bulan'].nunique() if len(df_all)>0 else 0)
with col4: st.metric("Status Database", "✅ MySQL" if st.session_state.get('db_ok') else "❌ Offline")

if len(df_all) > 0:
    st.markdown("### Distribusi Kegiatan per Fungsi")
    dist = df_all['Nama Fungsi'].value_counts()
    fig, ax = plt.subplots(figsize=(6.5, 3))
    dist.plot(kind='bar', ax=ax, color='#1D9E75', edgecolor='white')
    ax.set_ylabel("Jumlah Kegiatan", fontsize=8)
    plt.xticks(rotation=20, ha='right', fontsize=7)
    plt.yticks(fontsize=7)
    plt.tight_layout()
    st.pyplot(fig); plt.close()

    st.markdown("### Rekap Data per Fungsi")
    rekap = df_all.groupby('Nama Fungsi').agg(
        Jumlah_Kegiatan=('No', 'count'),
        Total_Peserta_Hadir=('Jumlah Peserta Hadir', 'sum')
    ).reset_index()
    st.dataframe(rekap, use_container_width=True, hide_index=True)
else:
    st.info("Belum ada data. Silakan isi lewat Input Data Kegiatan atau Import dari Excel.")
