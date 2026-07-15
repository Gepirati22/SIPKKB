import streamlit as st

from pages.sidebar import cek_login_atau_stop, render_sidebar
from utils.database import load_semua_kegiatan
from utils.model import proses_data_per_kegiatan, siapkan_fitur_model

st.set_page_config(page_title="Klasifikasi C4.5 — SIPKKB", page_icon="⚙️", layout="centered")

cek_login_atau_stop()
render_sidebar()

# =====================================================================
# KONTEN HALAMAN
# =====================================================================
st.title("Proses Klasifikasi C4.5 — Per Kegiatan")
st.markdown(
    "Klasifikasi dilakukan **per kegiatan individual** menggunakan fitur mentah: "
    "`Nama Fungsi`, `Bulan`, `Target Peserta`, dan `Jumlah Peserta Hadir`."
)

df_mentah = load_semua_kegiatan()

if len(df_mentah) < 5:
    st.warning("Data log belum mencukupi (minimal 5 baris).")
else:
    df_kegiatan = proses_data_per_kegiatan(df_mentah)

    st.markdown("### 📋 Tabel Data Per Kegiatan + Label")
    tampil = ['Nama Fungsi', 'Bulan', 'Nama Kegiatan',
              'Target Peserta', 'Jumlah Peserta Hadir',
              'Tingkat Kehadiran (%)', 'Terlaksana',
              'Kat_Kehadiran', 'Kat_Capaian', 'Label']
    tampil_ada = [c for c in tampil if c in df_kegiatan.columns]

    # Tampilkan SEMUA data, urut dari yang terbaru di paling atas,
    # dengan tinggi tabel dibatasi agar bisa di-scroll.
    df_tampil = df_kegiatan[tampil_ada].sort_index(ascending=False)
    st.dataframe(df_tampil, use_container_width=True, height=500)

    st.markdown("Distribusi Label Per Kegiatan (Semua Fungsi)")
    dist = df_kegiatan['Label'].value_counts()
    c1, c2, c3 = st.columns(3)
    for idx, label in enumerate(['Aktif', 'Cukup Aktif', 'Kurang Aktif']):
        ikon = ['🟢', '🟡', '🔴'][idx]
        with [c1, c2, c3][idx]:
            st.metric(f"{ikon} {label}", dist.get(label, 0))

    st.markdown("### 🔢 Encoding Fitur (Sinkron Cell 6 Notebook)")
    _, _, le_fungsi, _ = siapkan_fitur_model(df_kegiatan)
    mapping_fungsi = dict(zip(
        le_fungsi.classes_,
        le_fungsi.transform(le_fungsi.classes_).tolist()
    ))
    st.json(mapping_fungsi)

    # Simpan ke session state agar bisa dipakai halaman Visualisasi
    st.session_state['df_kegiatan'] = df_kegiatan
    st.success("✅ Data berhasil diproses! Lanjut ke halaman **Visualisasi & Evaluasi Model**.")