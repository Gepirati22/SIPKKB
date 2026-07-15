import streamlit as st

from pages.sidebar import cek_login_atau_stop, render_sidebar
from utils.database import load_semua_users, ganti_password_user

st.set_page_config(page_title="Manajemen Akun — SIPKKB", page_icon="👥", layout="centered")

cek_login_atau_stop()

# Hanya admin yang boleh akses
role = (st.session_state.get('user_info') or {}).get('role', 'user')
if role != 'admin':
    st.error("⛔ Halaman ini hanya untuk Admin.")
    st.stop()

render_sidebar()

# =====================================================================
# KONTEN HALAMAN
# =====================================================================
st.title("👥 Manajemen Akun Pengguna")
st.info("Hanya Admin yang dapat mengakses halaman ini. Password tidak ditampilkan demi keamanan.")

df_users = load_semua_users()

if len(df_users) > 0:
    st.markdown("### Daftar Akun Terdaftar")
    st.dataframe(
        df_users[['id', 'username', 'role', 'nama_fungsi']],
        use_container_width=True, hide_index=True
    )

    st.markdown("---")
    st.markdown("### 🔑 Ganti Password Akun")
    with st.form("form_ganti_password"):
        pilih_id = st.selectbox(
            "Pilih Akun:",
            df_users['id'].tolist(),
            format_func=lambda x: df_users[df_users['id'] == x]['username'].values[0]
        )
        pw_baru    = st.text_input("Password Baru", type="password",
                                    placeholder="Minimal 6 karakter")
        pw_konfirm = st.text_input("Konfirmasi Password Baru", type="password")
        simpan_pw  = st.form_submit_button("🔒 Simpan Password Baru",
                                            type="primary", use_container_width=True)
        if simpan_pw:
            if len(pw_baru) < 6:
                st.warning("Password minimal 6 karakter!")
            elif pw_baru != pw_konfirm:
                st.error("Konfirmasi password tidak cocok!")
            else:
                if ganti_password_user(pilih_id, pw_baru):
                    nama_akun = df_users[df_users['id'] == pilih_id]['username'].values[0]
                    st.success(f"Password akun **{nama_akun}** berhasil diperbarui!")
else:
    st.warning("Tidak ada data akun ditemukan.")
