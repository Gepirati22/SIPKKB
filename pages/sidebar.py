import streamlit as st
import os
from utils.constants import LOGO_PATH, PKL_PATH


def cek_login_atau_stop():
    """Hentikan halaman jika belum login."""
    if not st.session_state.get('logged_in'):
        st.warning("⚠️ Silakan login terlebih dahulu.")
        if st.button("🔐 Ke Halaman Login"):
            st.switch_page("app.py")
        st.stop()


def render_sidebar():
    role   = (st.session_state.get('user_info') or {}).get('role', 'user')
    fungsi = (st.session_state.get('user_info') or {}).get('fungsi')

    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=180)
        st.markdown("## 🌺 SIPKKB")
        st.markdown("**Kampung KB Bougenville**")
        st.markdown("Desa Sundawenang, Sukabumi")
        st.markdown("---")

        if role == 'admin':
            if os.path.exists(PKL_PATH):
                st.success("✅ Model PKL terdeteksi")
            else:
                st.warning("⚠️ Model PKL belum ada")

        st.markdown("---")
        if role == 'admin':
            st.markdown("👤 Login sebagai: **Admin**")
        else:
            st.markdown(f"👤 Login sebagai:\n\n**{fungsi}**")
            st.caption("_(Pengurus Fungsi)_")

        if st.button("🚪 Logout", key="btn_logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("app.py")

        st.markdown("---")
        st.markdown("**📌 Menu:**")

        if role == 'admin':
            st.page_link("pages/1_Dashboard_Admin.py",  label="🏠 Dashboard")
            st.page_link("pages/2_Input_Data_Admin.py", label="📥 Input Data Kegiatan")
            st.page_link("pages/3_Import_Excel.py",     label="📤 Import dari Excel")
            st.page_link("pages/4_Klasifikasi_C45.py",  label="⚙️ Proses Klasifikasi C4.5")
            st.page_link("pages/4b_Visualisasi.py",     label="📊 Visualisasi & Evaluasi")
            st.page_link("pages/4c_Manajemen_Akun.py",  label="👥 Manajemen Akun")
        else:
            st.page_link("pages/5_Dashboard_Fungsi.py", label="🏠 Dashboard Fungsi Saya")
            st.page_link("pages/6_Input_Data_User.py",  label="📥 Input Data Kegiatan")
