
import streamlit as st
import os
from utils.database import cek_login, init_database
from utils.constants import LOGO_PATH

st.set_page_config(
    page_title="SIPKKB - Kampung KB Bougenville",
    page_icon="🌺",
    layout="centered"
)

# Inisialisasi session state
for k, v in [('logged_in', False), ('db_ok', False),
              ('edit_id', None), ('user_info', None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# =====================================================================
# SUDAH LOGIN — tampilkan info + navigasi lewat sidebar
# =====================================================================
if st.session_state['logged_in']:
    role   = (st.session_state['user_info'] or {}).get('role', 'user')
    fungsi = (st.session_state['user_info'] or {}).get('fungsi', '')

    # Sidebar untuk navigasi setelah login
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=180)
        st.markdown("## 🌺 SIPKKB")
        st.markdown("---")
        if role == 'admin':
            st.markdown("👤 Login sebagai: **Admin**")
        else:
            st.markdown(f"👤 Login sebagai:\n\n**{fungsi}**")

        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("---")
        st.markdown("**📌 Pilih Menu:**")
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

    # Konten utama setelah login
    label = "Admin" if role == 'admin' else fungsi
    st.markdown(f"## 👋 Selamat datang, **{label}**!")
    st.success("Login berhasil! Silakan pilih menu di **sidebar kiri** untuk memulai.")
    st.stop()

# =====================================================================
# HALAMAN LOGIN (belum login)
# =====================================================================
col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=400)
    else:
        st.markdown("<h2 style='text-align:center;'>🌺</h2>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>SIPKKB</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:#4B5563;'>"
    "Sistem Informasi Program Kampung Keluarga Berkualitas<br>"
    "<small>Kampung KB Bougenville — Desa Sundawenang, Kec. Parungkuda, Kab. Sukabumi</small>"
    "</p>", unsafe_allow_html=True
)

col_a, col_b, col_c = st.columns([1, 1.5, 1])
with col_b:
    st.markdown("#####  Masuk ke Sistem")
    username = st.text_input("Username", placeholder="Masukkan username Anda")
    password = st.text_input("Password", type="password",
                              placeholder="Masukkan password Anda")

    if st.button("Masuk", use_container_width=True, type="primary"):
        if not username.strip() or not password.strip():
            st.warning("Username dan password wajib diisi!")
        else:
            with st.spinner("Memeriksa..."):
                info = cek_login(username.strip(), password.strip())
            if info:
                st.session_state['logged_in'] = True
                st.session_state['user_info'] = info
                st.session_state['db_ok'] = True  # skip init_database dulu
                st.rerun()
            else:
                st.error("Username atau password salah!")

    st.caption("Hubungi Admin untuk mendapatkan username dan password Anda.")
