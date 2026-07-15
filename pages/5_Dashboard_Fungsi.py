import streamlit as st
import pandas as pd

from pages.sidebar import cek_login_atau_stop, render_sidebar
from utils.database import load_semua_kegiatan
from utils.model import proses_data_per_kegiatan
from utils.constants import URUTAN_BULAN

st.set_page_config(page_title="Dashboard Fungsi — SIPKKB", page_icon="🏠", layout="centered")

cek_login_atau_stop()
render_sidebar()

fungsi = (st.session_state.get('user_info') or {}).get('fungsi')

# =====================================================================
# KONTEN HALAMAN
# =====================================================================
st.title(f"Dashboard — {fungsi}")
st.markdown(f"Menampilkan ringkasan data kegiatan **{fungsi}** yang telah diinput.")
st.markdown("---")

df_fungsi = load_semua_kegiatan(filter_fungsi=fungsi)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Kegiatan Diinput", len(df_fungsi))
with col2:
    st.metric("Bulan Tercatat", df_fungsi['Bulan'].nunique() if len(df_fungsi) > 0 else 0)
with col3:
    if len(df_fungsi) > 0:
        total_hadir  = df_fungsi['Jumlah Peserta Hadir'].sum()
        total_target = df_fungsi['Target Peserta'].sum()
        pct = round(total_hadir / total_target * 100, 1) if total_target > 0 else 0
        st.metric("Rata-rata Kehadiran", f"{pct}%")
    else:
        st.metric("Rata-rata Kehadiran", "0%")

if len(df_fungsi) > 0:
    st.markdown("### 📋 Rekap Kegiatan per Bulan")
    df_fungsi['Bulan'] = pd.Categorical(df_fungsi['Bulan'], categories=URUTAN_BULAN, ordered=True)
    rekap_bln = df_fungsi.groupby('Bulan', observed=True).agg(
        Jumlah_Kegiatan=('No', 'count'),
        Total_Peserta_Target=('Target Peserta', 'sum'),
        Total_Peserta_Hadir=('Jumlah Peserta Hadir', 'sum'),
    ).reset_index()
    rekap_bln['Kehadiran (%)'] = (
        rekap_bln['Total_Peserta_Hadir'] / rekap_bln['Total_Peserta_Target'] * 100
    ).fillna(0).round(1)
    st.dataframe(rekap_bln, use_container_width=True, hide_index=True)

    st.markdown("Status Keaktifan Kegiatan")
    df_label = proses_data_per_kegiatan(df_fungsi)
    dist = df_label['Label'].value_counts()
    c1, c2, c3 = st.columns(3)
    for idx, label in enumerate(['Aktif', 'Cukup Aktif', 'Kurang Aktif']):
        ikon = ['🟢', '🟡', '🔴'][idx]
        with [c1, c2, c3][idx]:
            st.metric(f"{ikon} {label}", dist.get(label, 0))
    st.caption("Status keaktifan dihitung berdasarkan tingkat kehadiran dan capaian kegiatan.")
else:
    st.info(f"Belum ada data untuk **{fungsi}**. Silakan input melalui menu Input Data Kegiatan.")
