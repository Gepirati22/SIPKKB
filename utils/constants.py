import os

# =====================================================================
# PATH FILE
# =====================================================================
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKL_PATH  = os.path.join(BASE_DIR, "model_decision_tree (1).pkl")
LOGO_PATH = os.path.join(BASE_DIR, "logo_sipkkb.png")

# =====================================================================
# KONFIGURASI MySQL
# =====================================================================
import pymysql
import streamlit as st

pymysql.install_as_MySQLdb()

MYSQL_CONFIG = {
    "host": st.secrets["MYSQLHOST"],
    "port": int(st.secrets["MYSQLPORT"]),
    "user": st.secrets["MYSQLUSER"],
    "password": st.secrets["MYSQLPASSWORD"],
    "database": st.secrets["MYSQLDATABASE"]
}

# =====================================================================
# KONSTANTA BULAN & FUNGSI
# =====================================================================
BULAN_INDO = {
    1:"Januari", 2:"Februari", 3:"Maret",    4:"April",
    5:"Mei",     6:"Juni",     7:"Juli",      8:"Agustus",
    9:"September",10:"Oktober",11:"November", 12:"Desember"
}

URUTAN_BULAN = [
    "Januari","Februari","Maret","April","Mei","Juni",
    "Juli","Agustus","September","Oktober","November","Desember"
]

BULAN_VALID = URUTAN_BULAN

DAFTAR_FUNGSI = [
    "Fungsi Keagamaan",
    "Fungsi Sosial Budaya",
    "Fungsi Cinta Kasih",
    "Fungsi Perlindungan",
    "Fungsi Reproduksi",
    "Fungsi Pendidikan",
    "Fungsi Ekonomi",
    "Fungsi Pembinaan Lingkungan",
]
