import streamlit as st
import pandas as pd
import pymysql
import pymysql.cursors
from datetime import datetime
from utils.constants import MYSQL_CONFIG, BULAN_INDO, BULAN_VALID, URUTAN_BULAN

# =====================================================================
# KONEKSI DATABASE
# =====================================================================
def get_connection():
    try:
        conn = pymysql.connect(
            host=MYSQL_CONFIG["host"],
            port=MYSQL_CONFIG["port"],
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            database=MYSQL_CONFIG["database"],
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=10,
        )
        return conn
    except Exception as e:
        st.error(f"Gagal koneksi ke MySQL: {e}")
        return None


def init_database():
    conn = get_connection()
    if conn is None:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_kegiatan (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nama_fungsi VARCHAR(100),
                    nama_kegiatan VARCHAR(200),
                    tanggal_kegiatan VARCHAR(20),
                    bulan VARCHAR(20),
                    tahun INT,
                    target_kegiatan_bulan INT,
                    target_peserta INT,
                    jumlah_peserta_hadir INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role ENUM('admin','user') NOT NULL,
                    nama_fungsi VARCHAR(100)
                )
            """)
            cursor.execute("SELECT COUNT(*) as cnt FROM users")
            jumlah = cursor.fetchone()["cnt"]
            if jumlah == 0:
                seed_data = [
                    ("admin@gmail.com",            "admin123",     "admin", None),
                    ("Fungsi Keagamaan",            "kag2024",      "user",  "Fungsi Keagamaan"),
                    ("Fungsi Sosial Budaya",        "sosbud2024",   "user",  "Fungsi Sosial Budaya"),
                    ("Fungsi Cinta Kasih",          "cinta2024",    "user",  "Fungsi Cinta Kasih"),
                    ("Fungsi Perlindungan",         "lindung2024",  "user",  "Fungsi Perlindungan"),
                    ("Fungsi Reproduksi",           "repro2024",    "user",  "Fungsi Reproduksi"),
                    ("Fungsi Pendidikan",           "didik2024",    "user",  "Fungsi Pendidikan"),
                    ("Fungsi Ekonomi",              "ekon2024",     "user",  "Fungsi Ekonomi"),
                    ("Fungsi Pembinaan Lingkungan", "lingkung2024", "user",  "Fungsi Pembinaan Lingkungan"),
                ]
                cursor.executemany(
                    "INSERT IGNORE INTO users (username, password, role, nama_fungsi) VALUES (%s,%s,%s,%s)",
                    seed_data
                )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error inisialisasi database: {e}")
        return False


# =====================================================================
# LOGIN
# =====================================================================
def cek_login(username: str, password: str):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (username.strip(), password)
            )
            row = cursor.fetchone()
        conn.close()
        if row:
            return {"role": row["role"], "fungsi": row["nama_fungsi"]}
        return None
    except Exception as e:
        st.error(f"Error login: {e}")
        return None


# =====================================================================
# CRUD DATA KEGIATAN
# =====================================================================
def simpan_kegiatan_db(data):
    conn = get_connection()
    if not conn: return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO data_kegiatan
                (nama_fungsi,nama_kegiatan,tanggal_kegiatan,bulan,tahun,
                 target_kegiatan_bulan,target_peserta,jumlah_peserta_hadir)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (data['Nama Fungsi'], data['Nama Kegiatan'], data['Tanggal Kegiatan'],
                  data['Bulan'], data['Tahun'], data['Target Kegiatan/Bulan'],
                  data['Target Peserta'], data['Jumlah Peserta Hadir']))
        conn.commit(); conn.close(); return True
    except Exception as e:
        st.error(f"Gagal simpan: {e}"); return False


def update_kegiatan_db(id_data, data):
    conn = get_connection()
    if not conn: return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE data_kegiatan SET
                nama_fungsi=%s,nama_kegiatan=%s,tanggal_kegiatan=%s,bulan=%s,tahun=%s,
                target_kegiatan_bulan=%s,target_peserta=%s,jumlah_peserta_hadir=%s
                WHERE id=%s
            """, (data['Nama Fungsi'], data['Nama Kegiatan'], data['Tanggal Kegiatan'],
                  data['Bulan'], data['Tahun'], data['Target Kegiatan/Bulan'],
                  data['Target Peserta'], data['Jumlah Peserta Hadir'], id_data))
        conn.commit(); conn.close(); return True
    except Exception as e:
        st.error(f"Gagal update: {e}"); return False


def hapus_kegiatan_db(id_data):
    conn = get_connection()
    if not conn: return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM data_kegiatan WHERE id=%s", (id_data,))
        conn.commit(); conn.close(); return True
    except Exception as e:
        st.error(f"Gagal hapus: {e}"); return False


def load_semua_kegiatan(filter_fungsi=None):
    conn = get_connection()
    if not conn: return pd.DataFrame()
    try:
        with conn.cursor() as cursor:
            if filter_fungsi:
                cursor.execute("""
                    SELECT id AS `No`, nama_fungsi AS `Nama Fungsi`,
                           nama_kegiatan AS `Nama Kegiatan`, bulan AS `Bulan`,
                           tahun AS `Tahun`, tanggal_kegiatan AS `Tanggal Kegiatan`,
                           target_peserta AS `Target Peserta`,
                           jumlah_peserta_hadir AS `Jumlah Peserta Hadir`,
                           target_kegiatan_bulan AS `Target Kegiatan/Bulan`
                    FROM data_kegiatan WHERE nama_fungsi = %s ORDER BY id ASC
                """, (filter_fungsi,))
            else:
                cursor.execute("""
                    SELECT id AS `No`, nama_fungsi AS `Nama Fungsi`,
                           nama_kegiatan AS `Nama Kegiatan`, bulan AS `Bulan`,
                           tahun AS `Tahun`, tanggal_kegiatan AS `Tanggal Kegiatan`,
                           target_peserta AS `Target Peserta`,
                           jumlah_peserta_hadir AS `Jumlah Peserta Hadir`,
                           target_kegiatan_bulan AS `Target Kegiatan/Bulan`
                    FROM data_kegiatan ORDER BY id ASC
                """)
            rows = cursor.fetchall()
        conn.close()
        if rows:
            return pd.DataFrame(rows)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Gagal load data: {e}"); return pd.DataFrame()

# =====================================================================
# MANAJEMEN AKUN
# =====================================================================
def load_semua_users():
    conn = get_connection()
    if not conn: return pd.DataFrame()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, username, role, nama_fungsi FROM users ORDER BY id ASC")
            rows = cursor.fetchall()
        conn.close()
        if rows:
            return pd.DataFrame(rows)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Gagal load users: {e}"); return pd.DataFrame()

def ganti_password_user(user_id, password_baru):
    conn = get_connection()
    if not conn: return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET password=%s WHERE id=%s", (password_baru, user_id))
        conn.commit(); conn.close(); return True
    except Exception as e:
        st.error(f"Gagal ganti password: {e}"); return False


# =====================================================================
# IMPORT EXCEL
# =====================================================================
def normalisasi_bulan(nilai):
    try:
        angka = int(float(str(nilai)))
        if 1 <= angka <= 12:
            return BULAN_INDO[angka]
    except (ValueError, TypeError):
        pass
    return str(nilai).strip().title()


def import_dari_excel(df_excel):
    conn = get_connection()
    if not conn: return 0
    kolom_unnamed = [c for c in df_excel.columns if "Unnamed" in str(c)]
    if kolom_unnamed:
        df_excel = df_excel.drop(columns=kolom_unnamed)
    if "Bulan" in df_excel.columns:
        if pd.api.types.is_numeric_dtype(df_excel["Bulan"]):
            df_excel["Bulan"] = df_excel["Bulan"].map(BULAN_INDO).fillna(df_excel["Bulan"])
        df_excel["Bulan"] = df_excel["Bulan"].astype(str).str.strip().str.title()
        invalid = df_excel[~df_excel["Bulan"].isin(BULAN_VALID)]["Bulan"].unique()
        if len(invalid) > 0:
            st.warning(f"Nama bulan tidak dikenali: {', '.join(str(x) for x in invalid)}")
        else:
            st.success("Semua nama bulan konsisten dan telah dinormalisasi.")
    if "Tanggal Kegiatan" in df_excel.columns:
        df_excel["Tanggal Kegiatan"] = pd.to_datetime(
            df_excel["Tanggal Kegiatan"], errors="coerce"
        ).dt.strftime("%d-%m-%Y")
    try:
        count = 0
        with conn.cursor() as cursor:
            for _, row in df_excel.iterrows():
                try:
                    f_nama    = str(row.get("Nama Fungsi", ""))
                    f_keg     = str(row.get("Nama Kegiatan", ""))
                    f_bln     = normalisasi_bulan(row.get("Bulan", ""))
                    f_thn     = int(row.get("Tahun", datetime.now().year))
                    f_tgl     = row.get("Tanggal Kegiatan", row.get("Tanggal Dilaksanakan", ""))
                    if pd.isna(f_tgl) or str(f_tgl) in ("", "NaT", "nan"):
                        f_tgl = datetime.now().strftime("%d-%m-%Y")
                    else:
                        f_tgl = str(f_tgl)
                    if f_bln not in BULAN_VALID:
                        for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%m/%d/%Y"):
                            try:
                                f_bln = BULAN_INDO[datetime.strptime(f_tgl, fmt).month]; break
                            except: pass
                    f_tar_pes = int(row.get("Target Peserta", 0))
                    f_hadir   = int(row.get("Jumlah Peserta Hadir", row.get("Peserta Hadir", 0)))
                    f_tar_keg = int(row.get("Target Kegiatan/Bulan", 4))
                    cursor.execute("""
                        INSERT INTO data_kegiatan
                        (nama_fungsi,nama_kegiatan,tanggal_kegiatan,bulan,tahun,
                         target_kegiatan_bulan,target_peserta,jumlah_peserta_hadir)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (f_nama, f_keg, f_tgl, f_bln, f_thn, f_tar_keg, f_tar_pes, f_hadir))
                    count += 1
                except: continue
        conn.commit(); conn.close(); return count
    except Exception as e:
        st.error(f"Error import: {e}"); return 0