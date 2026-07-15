import streamlit as st
from datetime import datetime

from pages.sidebar import cek_login_atau_stop, render_sidebar
from utils.database import (load_semua_kegiatan, simpan_kegiatan_db,
                             update_kegiatan_db, hapus_kegiatan_db)
from utils.constants import BULAN_INDO, DAFTAR_FUNGSI

st.set_page_config(page_title="Input Data — SIPKKB", page_icon="📥", layout="centered")

cek_login_atau_stop()
render_sidebar()

# =====================================================================
# KONTEN HALAMAN
# =====================================================================
st.title("📥 Manajemen Data Kegiatan")
st.caption("Admin dapat input, edit, dan hapus data dari semua fungsi.")

# Pastikan session state edit_id tersedia
if 'edit_id' not in st.session_state:
    st.session_state['edit_id'] = None

with st.expander("✏️ Formulir Tambah / Edit Data", expanded=True):
    if st.session_state['edit_id'] is not None:
        st.markdown("##### 📝 Edit Data Kegiatan")
        df_curr  = load_semua_kegiatan()
        row_edit = df_curr[df_curr['No'] == st.session_state['edit_id']].iloc[0]
        def_fungsi    = row_edit['Nama Fungsi']
        def_kegiatan  = row_edit['Nama Kegiatan']
        try:
            def_tanggal = datetime.strptime(str(row_edit['Tanggal Kegiatan'])[:10], '%Y-%m-%d')
        except:
            def_tanggal = datetime.now()
        def_target_keg = int(row_edit['Target Kegiatan/Bulan'])
        def_target_pes = int(row_edit['Target Peserta'])
        def_hadir      = int(row_edit['Jumlah Peserta Hadir'])
        btn_label = "💾 Update Perubahan Data"
    else:
        st.markdown("INPUT MANUAL KEGIATAN")
        def_fungsi     = DAFTAR_FUNGSI[0]
        def_kegiatan   = ""
        def_tanggal    = datetime.now()
        def_target_keg = 4
        def_target_pes = 30
        def_hadir      = 0
        btn_label      = "💾 Simpan Data Kegiatan"

    with st.form("form_input_admin"):
        idx_f = DAFTAR_FUNGSI.index(def_fungsi) if def_fungsi in DAFTAR_FUNGSI else 0
        nama_fungsi   = st.selectbox("Nama Fungsi Keluarga", DAFTAR_FUNGSI, index=idx_f)
        nama_kegiatan = st.text_input("Nama Kegiatan", value=def_kegiatan,
                                      placeholder="Contoh: Sosialisasi Poktan BKB")
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
                    'Nama Fungsi':           nama_fungsi,
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

st.markdown("### 📋 Seluruh Data Kegiatan")
df_db = load_semua_kegiatan()
if len(df_db) > 0:
    # Urutkan dari data terlama -> terbaru dulu untuk hitung nomor urut rapi
    df_db_tampil = df_db.sort_values('No', ascending=True).reset_index(drop=True)
    df_db_tampil.insert(0, 'No Urut', range(1, len(df_db_tampil) + 1))

    # Baru dibalik supaya data terbaru tampil di paling atas
    df_db_tampil = df_db_tampil.sort_values('No Urut', ascending=False)

    # Sembunyikan kolom 'No' asli dari tampilan (tetap dipakai di belakang layar)
    kolom_tampil = ['No Urut'] + [c for c in df_db_tampil.columns if c not in ('No', 'No Urut')]
    st.dataframe(df_db_tampil[kolom_tampil], use_container_width=True, height=400)

    # Buat mapping: No Urut (tampilan) -> No asli (database)
    peta_no = dict(zip(df_db_tampil['No Urut'], df_db_tampil['No']))

    cs1, cs2, cs3 = st.columns([2, 1, 1])
    with cs1:
        no_urut_pilihan = st.selectbox(
            "Pilih No Urut Data untuk dikelola:",
            list(peta_no.keys())
        )
        pilihan_id = peta_no[no_urut_pilihan]
    with cs2:
        if st.button("✏️ Edit Baris", use_container_width=True):
            st.session_state['edit_id'] = pilihan_id; st.rerun()
    with cs3:
        if st.button("🗑️ Hapus Baris", use_container_width=True):
            if hapus_kegiatan_db(pilihan_id):
                st.success(f"Data No {pilihan_id} dihapus!")
                if st.session_state['edit_id'] == pilihan_id:
                    st.session_state['edit_id'] = None
                st.rerun()
else:
    st.info("Belum ada data di database.")