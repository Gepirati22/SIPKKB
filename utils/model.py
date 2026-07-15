import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import streamlit as st
from utils.constants import URUTAN_BULAN, PKL_PATH

# =====================================================================
# PREPROCESSING — LABELING
# =====================================================================
def kat_kehadiran(x):
    if x >= 80:    return 'Tinggi'
    elif x >= 50:  return 'Sedang'
    else:           return 'Rendah'


def kat_capaian_per_kegiatan(row):
    if row['Terlaksana'] == 'Ya' and row['Tingkat Kehadiran (%)'] >= 80:
        return 'Tinggi'
    elif row['Terlaksana'] == 'Ya' and row['Tingkat Kehadiran (%)'] >= 50:
        return 'Sedang'
    else:
        return 'Rendah'


def buat_label_kegiatan(row):
    if row['Kat_Capaian'] == 'Tinggi' and row['Kat_Kehadiran'] == 'Tinggi':
        return 'Aktif'
    elif row['Kat_Capaian'] == 'Rendah' or row['Kat_Kehadiran'] == 'Rendah':
        return 'Kurang Aktif'
    else:
        return 'Cukup Aktif'


def proses_data_per_kegiatan(df_mentah):
    df_kegiatan = df_mentah.copy()
    df_kegiatan['Tingkat Kehadiran (%)'] = (
        df_kegiatan['Jumlah Peserta Hadir'] / df_kegiatan['Target Peserta']
    ) * 100
    df_kegiatan['Tingkat Kehadiran (%)'] = df_kegiatan['Tingkat Kehadiran (%)'].fillna(0)
    df_kegiatan['Terlaksana']    = df_kegiatan['Jumlah Peserta Hadir'].apply(
        lambda x: 'Ya' if x > 0 else 'Tidak'
    )
    df_kegiatan['Kat_Kehadiran'] = df_kegiatan['Tingkat Kehadiran (%)'].apply(kat_kehadiran)
    df_kegiatan['Kat_Capaian']   = df_kegiatan.apply(kat_capaian_per_kegiatan, axis=1)
    df_kegiatan['Label']         = df_kegiatan.apply(buat_label_kegiatan, axis=1)
    return df_kegiatan


# =====================================================================
# FITUR & MODEL
# =====================================================================
def siapkan_fitur_model(df_kegiatan):
    df_kegiatan = df_kegiatan.copy()
    df_kegiatan['Bulan_Urutan'] = df_kegiatan['Bulan'].apply(
        lambda b: URUTAN_BULAN.index(b) + 1 if b in URUTAN_BULAN else 0
    )
    le_fungsi = LabelEncoder()
    le_label  = LabelEncoder()
    X = pd.DataFrame()
    X['Nama_Fungsi_Encoded']  = le_fungsi.fit_transform(df_kegiatan['Nama Fungsi'])
    X['Bulan_Encoded']        = df_kegiatan['Bulan_Urutan']
    X['Target_Peserta']       = df_kegiatan['Target Peserta']
    X['Jumlah_Peserta_Hadir'] = df_kegiatan['Jumlah Peserta Hadir']
    y_encoded = le_label.fit_transform(df_kegiatan['Label'])
    return X, y_encoded, le_fungsi, le_label


def load_model_pkl():
    import os
    if os.path.exists(PKL_PATH):
        try:
            return joblib.load(PKL_PATH)
        except Exception as e:
            st.warning(f"Gagal load model .pkl: {e}")
    return None


def latih_model_c45(df_kegiatan):
    X, y_encoded, le_fungsi, le_label = siapkan_fitur_model(df_kegiatan)
    if len(X) < 5:
        return (None,) * 11
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.3, random_state=42
    )
    model_pkl = load_model_pkl()
    if model_pkl is not None:
        model = model_pkl
    else:
        model = DecisionTreeClassifier(
            criterion='entropy', max_depth=6,
            min_samples_split=5, min_samples_leaf=2, random_state=42
        )
        model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    return (model, le_fungsi, le_label,
            X_train, X_test, y_train, y_test, y_pred,
            list(X.columns), X, y_encoded)
