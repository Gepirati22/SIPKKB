import streamlit as st
from datetime import datetime

from pages.sidebar import cek_login_atau_stop, render_sidebar
from utils.database import (load_semua_kegiatan, simpan_kegiatan_db,
                             update_kegiatan_db)
from utils.constants import BULAN_INDO

st.set_page_config(page_title="Input Data Kegiatan — SIPKKB", page_icon="📥", layout="centered")

cek_login_atau_stop()
render_sidebar()

fungsi = (st.session_state.get('user_info') or {}).get('fungsi')

# Pastikan session state edit_id tersedia
if 'edit_id' not in st.session_state:
    st.session_state['edit_id'] = None

# =====================================================================
# KONTEN HALAMAN
# =====================================================================
st.title(f"Input Data Kegiatan — {fungsi}")
st.info(f"Anda hanya dapat menginput dan mengedit data untuk **{fungsi}**.")

with st.expander("✏️ Formulir Tambah / Edit Data", expanded=True):
    if st.session_state['edit_id'] is not None:
        st.markdown("##### 📝 Edit Data Kegiatan")
        df_curr  = load_semua_kegiatan(filter_fungsi=fungsi)
        baris    = df_curr[df_curr['No'] == st.session_state['edit_id']]
        if baris.empty:
            st.error("Data tidak ditemukan atau bukan milik fungsi Anda.")
            st.session_state['edit_id'] = None; st.rerun()
        row_edit = baris.iloc[0]
        def_kegiatan   = row_edit['Nama Kegiatan']
        try:
            def_tanggal = datetime.strptime(str(row_edit['Tanggal Kegiatan'])[:10], '%Y-%m-%d')
        except:
            def_tanggal = datetime.now()
        def_target_keg = int(row_edit['Target Kegiatan/Bulan'])
        def_target_pes = int(row_edit['Target Peserta'])
        def_hadir      = int(row_edit['Jumlah Peserta Hadir'])
        btn_label      = "💾 Update Perubahan Data"
    else:
        st.markdown("INPUT MANUAL KEGIATAN")
        def_kegiatan   = ""
        def_tanggal    = datetime.now()
        def_target_keg = 4
        def_target_pes = 30
        def_hadir      = 0
        btn_label      = "💾 Simpan Data Kegiatan"

    with st.form("form_input_user"):
        st.markdown(f"**Nama Fungsi:** {fungsi}")
        nama_kegiatan = st.text_input("Nama Kegiatan", value=def_kegiatan,
                                      placeholder="Contoh: Pertemuan Rutin BKB")
        tanggal = st.date_input("Tanggal Kegiatan", value=def_tanggal)
        c1, c2  = st.columns(2)
        with c1:
            target_keg     = st.number_input("Target Kegiatan/Bulan", min_value=1, step=1, value=def_target_keg)
            target_peserta = st.number_input("Target Peserta",         min_value=1, step=1, value=def_target_pes)
        with c2:
            peserta_hadir = st.number_input("Jumlah Peserta Hadir", min_value=0, step=1, value=def_hadir)

        if st.session_state['edit_id'] is not None:
            cb1, cb2 = st.columns([4, 1])
            with cb1:
                proses_submit = st.form_submit_button(btn_label, use_container_width=True, type="primary")
            with cb2:
                if st.form_submit_button("Batal", use_container_width=True):
                    st.session_state['edit_id'] = None; st.rerun()
        else:
            proses_submit = st.form_submit_button(btn_label, use_container_width=True, type="primary")

        if proses_submit:
            if not nama_kegiatan.strip():
                st.warning("Nama kegiatan wajib diisi!")
            else:
                data_form = {
                    'Nama Fungsi':           fungsi,
                    'Nama Kegiatan':         nama_kegiatan,
                    'Tanggal Kegiatan':      tanggal.strftime('%Y-%m-%d'),
                    'Bulan':                 BULAN_INDO[tanggal.month],
                    'Tahun':                 tanggal.year,
                    'Target Kegiatan/Bulan': target_keg,
                    'Target Peserta':        target_peserta,
                    'Jumlah Peserta Hadir':  peserta_hadir,
                }
                if st.session_state['edit_id'] is not None:
                    if update_kegiatan_db(st.session_state['edit_id'], data_form):
                        st.success("Data berhasil diperbarui!")
                        st.session_state['edit_id'] = None; st.rerun()
                else:
                    if simpan_kegiatan_db(data_form):
                        st.success(f"Data '{nama_kegiatan}' disimpan!"); st.rerun()

st.markdown(f"### 📋 Riwayat Data Kegiatan — {fungsi}")
df_db = load_semua_kegiatan(filter_fungsi=fungsi)
if len(df_db) > 0:
    # Urutkan dari data terlama -> terbaru dulu untuk hitung nomor urut rapi
    df_db_tampil = df_db.sort_values('No', ascending=True).reset_index(drop=True)
    df_db_tampil.insert(0, 'No Urut', range(1, len(df_db_tampil) + 1))

    # Baru dibalik supaya data terbaru tampil di paling atas
    df_db_tampil = df_db_tampil.sort_values('No Urut', ascending=False)

    # Sembunyikan kolom 'No' asli dari tampilan (tetap dipakai di belakang layar)
    kolom_tampil = ['No Urut'] + [c for c in df_db_tampil.columns if c not in ('No', 'No Urut')]
    st.dataframe(df_db_tampil[kolom_tampil], use_container_width=True, height=400)

    cs1, cs2 = st.columns([3, 1])
    with cs1:
        pilihan_id = st.selectbox("Pilih No Data untuk diedit:", df_db['No'].tolist())
    with cs2:
        if st.button("✏️ Edit Baris", use_container_width=True):
            st.session_state['edit_id'] = pilihan_id; st.rerun()
    st.caption("Pengurus fungsi hanya dapat mengedit data. Hubungi Admin jika perlu penghapusan data.")
else:
    st.info(f"Belum ada data untuk **{fungsi}**.")