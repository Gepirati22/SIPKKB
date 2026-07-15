import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sklearn.tree import plot_tree, DecisionTreeClassifier
from sklearn.model_selection import KFold, cross_val_score
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report

from pages.sidebar import cek_login_atau_stop, render_sidebar
from utils.model import latih_model_c45
from utils.constants import URUTAN_BULAN

st.set_page_config(page_title="Visualisasi — SIPKKB", page_icon="📊", layout="centered")

cek_login_atau_stop()
render_sidebar()

# =====================================================================
# KONTEN HALAMAN
# =====================================================================
st.title("📊 Hasil Evaluasi & Grafik Pohon Keputusan C4.5")

if 'df_kegiatan' not in st.session_state:
    st.info("Silakan jalankan menu **⚙️ Proses Klasifikasi C4.5** terlebih dahulu.")
    st.stop()

df    = st.session_state['df_kegiatan']
hasil = latih_model_c45(df)

if hasil[0] is None:
    st.warning("Data terlalu sedikit untuk melatih model (minimal 5 sampel).")
    st.stop()

(model, le_fungsi, le_label,
 X_train, X_test, y_train, y_test, y_pred,
 cols_fitur, X_all, y_all) = hasil

akurasi_train = accuracy_score(y_train, model.predict(X_train)) * 100
akurasi_test  = accuracy_score(y_test, y_pred) * 100

# ── Metrik Akurasi ───────────────────────────────────────────────────
st.markdown("### 📈 Metrik Akurasi (Rasio Split 70:30)")
m1, m2, m3, m4 = st.columns(4)
with m1: st.metric("Akurasi Testing",      f"{akurasi_test:.2f}%")
with m2: st.metric("Akurasi Training",     f"{akurasi_train:.2f}%")
with m3: st.metric("Data Training (70%)",  len(X_train))
with m4: st.metric("Data Testing (30%)",   len(X_test))

gap = abs(akurasi_train - akurasi_test)
if gap < 5:
    st.success(f"Gap Training vs Testing: **{gap:.2f}%** — Model tidak overfitting.")
else:
    st.warning(f"Gap Training vs Testing: **{gap:.2f}%** — Perlu dicek potensi overfitting.")

# ── K-Fold CV ────────────────────────────────────────────────────────
st.markdown("### 🔁 5-Fold Cross Validation")
model_cv = DecisionTreeClassifier(
    criterion='entropy', max_depth=6,
    min_samples_split=5, min_samples_leaf=2, random_state=42
)
kf      = KFold(n_splits=5, shuffle=True, random_state=42)
skor_cv = cross_val_score(model_cv, X_all, y_all, cv=kf, scoring='accuracy')
cv_df   = pd.DataFrame({
    'Fold':        [f"Fold {i+1}" for i in range(5)],
    'Akurasi (%)': [f"{s*100:.2f}%" for s in skor_cv]
})
st.dataframe(cv_df, use_container_width=True, hide_index=True)
st.metric("Rata-rata K-Fold CV", f"{np.mean(skor_cv)*100:.2f}%",
          delta=f"± {np.std(skor_cv)*100:.2f}% std")

# ── Classification Report ────────────────────────────────────────────
st.markdown("### 📋 Classification Report")
report = classification_report(y_test, y_pred,
                                target_names=le_label.classes_,
                                output_dict=True)
st.dataframe(pd.DataFrame(report).transpose().round(4), use_container_width=True)

# ── Confusion Matrix & Pohon ─────────────────────────────────────────
ca, cb = st.columns(2)
with ca:
    st.markdown("Confusion Matrix")
    cm = confusion_matrix(y_test, y_pred)
    fig_cm, ax_cm = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=le_label.classes_,
                yticklabels=le_label.classes_, ax=ax_cm)
    ax_cm.set_ylabel('Aktual (Kondisi Nyata)')
    ax_cm.set_xlabel('Prediksi (Output Pohon)')
    plt.tight_layout()
    st.pyplot(fig_cm); plt.close()

with cb:
    st.markdown("Pohon Keputusan C4.5")
    try:
        fig_tree, ax_tree = plt.subplots(figsize=(8, 6))
        plot_tree(model,
                  feature_names=cols_fitur,
                  class_names=[str(c) for c in le_label.classes_],
                  filled=True, rounded=True, ax=ax_tree, fontsize=7)
        plt.tight_layout()
        st.pyplot(fig_tree); plt.close()
    except Exception as ex:
        st.warning(f"Gagal merender pohon keputusan: {ex}")

# ── Feature Importance ───────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 Feature Importance")
importances = pd.Series(model.feature_importances_,
                        index=cols_fitur).sort_values(ascending=False)
fig_fi, ax_fi = plt.subplots(figsize=(8, 4))
importances.plot(kind='barh', color='#4c72b0', ax=ax_fi)
ax_fi.set_title('Feature Importance — Decision Tree C4.5', fontsize=12, fontweight='bold')
ax_fi.set_xlabel('Tingkat Kepentingan')
ax_fi.invert_yaxis()
plt.tight_layout()
st.pyplot(fig_fi); plt.close()

# ── Tren Kegiatan & Kehadiran Semua Fungsi ───────────────────────────
st.markdown("---")
st.markdown("### 📈 Tren Kegiatan & Kehadiran Bulanan Per Fungsi (Semua Fungsi)")

df_tren_all = df.groupby(['Nama Fungsi', 'Bulan']).size().reset_index(name='Jumlah Kegiatan')
df_tren_all['Bulan'] = pd.Categorical(df_tren_all['Bulan'], categories=URUTAN_BULAN, ordered=True)
df_tren_all = df_tren_all.sort_values(['Nama Fungsi', 'Bulan'])

df_kehadiran_all = df.groupby(['Nama Fungsi', 'Bulan'])['Tingkat Kehadiran (%)'].mean().reset_index()
df_kehadiran_all['Bulan'] = pd.Categorical(df_kehadiran_all['Bulan'], categories=URUTAN_BULAN, ordered=True)

daftar_fungsi_all = sorted(df['Nama Fungsi'].unique())
warna_palet  = plt.cm.tab10.colors
marker_list  = ['o', 's', '^', 'D', 'v', 'P', '*', 'X']

# ── Hitung ringkasan label per fungsi ────────────────────────────────
ringkasan_fungsi = (
    df.groupby(['Nama Fungsi', 'Label'])
    .size().unstack(fill_value=0)
    .reindex(columns=['Aktif', 'Cukup Aktif', 'Kurang Aktif'], fill_value=0)
    .reset_index()
)
ringkasan_fungsi['Total'] = ringkasan_fungsi[['Aktif', 'Cukup Aktif', 'Kurang Aktif']].sum(axis=1)

grand_aktif  = int(ringkasan_fungsi['Aktif'].sum())
grand_cukup  = int(ringkasan_fungsi['Cukup Aktif'].sum())
grand_kurang = int(ringkasan_fungsi['Kurang Aktif'].sum())
grand_total  = grand_aktif + grand_cukup + grand_kurang

ringkasan_teks = (
    f"RINGKASAN KESELURUHAN KEAKTIFAN  |  "
    f"🟢  Aktif : {grand_aktif} kegiatan  ({grand_aktif/grand_total*100:.1f}%)     "
    f"🟠  Cukup Aktif : {grand_cukup} kegiatan  ({grand_cukup/grand_total*100:.1f}%)     "
    f"🔴  Kurang Aktif : {grand_kurang} kegiatan  ({grand_kurang/grand_total*100:.1f}%)     "
    f"📊  Total : {grand_total} kegiatan"
)

tabel_baris = []
for _, row in ringkasan_fungsi.iterrows():
    tabel_baris.append([
        row['Nama Fungsi'],
        f"{int(row['Aktif'])}  ({row['Aktif']/row['Total']*100:.0f}%)",
        f"{int(row['Cukup Aktif'])}  ({row['Cukup Aktif']/row['Total']*100:.0f}%)",
        f"{int(row['Kurang Aktif'])}  ({row['Kurang Aktif']/row['Total']*100:.0f}%)",
        f"{int(row['Total'])}"
    ])

def render_tabel(ax_sum):
    """Render ringkasan teks + tabel ke dalam axes ringkasan."""
    ax_sum.axis('off')
    ax_sum.text(0.5, 0.6, ringkasan_teks,
                transform=ax_sum.transAxes,
                fontsize=10.5, ha='center', va='center', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.6', facecolor='#F0F0F0',
                          edgecolor='#AAAAAA', alpha=0.95))
    tbl = ax_sum.table(
        cellText=tabel_baris,
        colLabels=['Fungsi Keluarga', '🟢 Aktif', '🟠 Cukup Aktif', '🔴 Kurang Aktif', 'Total'],
        loc='bottom', cellLoc='center', bbox=[0, -5.5, 1, 4.8]
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.5)
    for (r, c), cell in tbl.get_celld().items():
        if r == 0:
            cell.set_facecolor('#D6EAF8')
            cell.set_text_props(fontweight='bold')
        elif c == 1:
            cell.set_facecolor('#E8F8E8')
        elif c == 2:
            cell.set_facecolor('#FFF3E0')
        elif c == 3:
            cell.set_facecolor('#FFEBEE')
        cell.set_edgecolor('#CCCCCC')

# ── CHART 1: Tren Jumlah Kegiatan ────────────────────────────────────
st.markdown("#### 📊 Grafik 1 — Tren Jumlah Kegiatan Per Bulan")

semua_nilai = df_tren_all['Jumlah Kegiatan']
batas_bawah = int(semua_nilai.quantile(0.33))
batas_atas  = int(semua_nilai.quantile(0.66))
y_max_plot  = int(semua_nilai.max() * 1.18)

fig_keg, axes_keg = plt.subplots(
    2, 1, figsize=(18, 11),
    gridspec_kw={'height_ratios': [7, 1], 'hspace': 0.08}
)
ax_keg     = axes_keg[0]
ax_keg_sum = axes_keg[1]

# Zona warna
ax_keg.axhspan(0,           batas_bawah, alpha=0.10, color='#FF4C4C', zorder=0)
ax_keg.axhspan(batas_bawah, batas_atas,  alpha=0.10, color='#FFA500', zorder=0)
ax_keg.axhspan(batas_atas,  y_max_plot,  alpha=0.10, color='#4CAF50', zorder=0)
ax_keg.axhline(y=batas_bawah, color='#CC0000', linestyle='--', linewidth=1.3, alpha=0.7, zorder=1)
ax_keg.axhline(y=batas_atas,  color='#2E7D32', linestyle='--', linewidth=1.3, alpha=0.7, zorder=1)

ax_keg.text(-0.5, batas_bawah / 2,
            f'KURANG AKTIF\n(< {batas_bawah} kegiatan)',
            fontsize=9, color='#CC0000', ha='left', va='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='white', edgecolor='#CC0000', alpha=0.85))
ax_keg.text(-0.5, (batas_bawah + batas_atas) / 2,
            f'CUKUP AKTIF\n({batas_bawah}–{batas_atas} kegiatan)',
            fontsize=9, color='#E65C00', ha='left', va='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='white', edgecolor='#FFA500', alpha=0.85))
ax_keg.text(-0.5, (batas_atas + y_max_plot) / 2,
            f'AKTIF\n(≥ {batas_atas} kegiatan)',
            fontsize=9, color='#1B5E20', ha='left', va='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='white', edgecolor='#4CAF50', alpha=0.85))

for i, fn in enumerate(daftar_fungsi_all):
    data_f = df_tren_all[df_tren_all['Nama Fungsi'] == fn].sort_values('Bulan')
    ax_keg.plot(data_f['Bulan'].astype(str), data_f['Jumlah Kegiatan'],
                marker=marker_list[i % len(marker_list)],
                color=warna_palet[i % len(warna_palet)],
                linewidth=2, markersize=8, label=fn, zorder=3)

ax_keg.set_title('Tren Jumlah Kegiatan Per Fungsi Keluarga\n(Semua Fungsi Dalam Satu Diagram)',
                  fontsize=14, fontweight='bold', pad=15)
ax_keg.set_xlabel('Bulan', fontsize=11)
ax_keg.set_ylabel('Jumlah Kegiatan Terlaksana', fontsize=11)
ax_keg.set_ylim(0, y_max_plot)
ax_keg.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax_keg.grid(axis='y', linestyle='--', alpha=0.4)
ax_keg.grid(axis='x', linestyle=':', alpha=0.3)
ax_keg.tick_params(axis='x', rotation=30, labelsize=9)
ax_keg.legend(title='Fungsi Keluarga', title_fontsize=10, fontsize=9,
               loc='upper left', bbox_to_anchor=(1.01, 1), borderaxespad=0, framealpha=0.9)

render_tabel(ax_keg_sum)
plt.tight_layout()
st.pyplot(fig_keg); plt.close()

# ── CHART 2: Tren Tingkat Kehadiran ──────────────────────────────────
st.markdown("#### 📊 Grafik 2 — Tren Rata-rata Tingkat Kehadiran Per Bulan")

fig_had, axes_had = plt.subplots(
    2, 1, figsize=(18, 11),
    gridspec_kw={'height_ratios': [7, 1], 'hspace': 0.08}
)
ax_had     = axes_had[0]
ax_had_sum = axes_had[1]

# Zona warna
ax_had.axhspan(0,   50,  alpha=0.10, color='#FF4C4C', zorder=0)
ax_had.axhspan(50,  80,  alpha=0.10, color='#FFA500', zorder=0)
ax_had.axhspan(80, 115,  alpha=0.10, color='#4CAF50', zorder=0)
ax_had.axhline(y=50, color='#CC0000', linestyle='--', linewidth=1.5, alpha=0.8, zorder=1)
ax_had.axhline(y=80, color='#2E7D32', linestyle='--', linewidth=1.5, alpha=0.8, zorder=1)

ax_had.text(-0.5, 25,
            'KURANG AKTIF\nKehadiran Rendah (< 50%)',
            fontsize=9, color='#CC0000', ha='left', va='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='white', edgecolor='#CC0000', alpha=0.85))
ax_had.text(-0.5, 65,
            'CUKUP AKTIF\nKehadiran Sedang (50–80%)',
            fontsize=9, color='#E65C00', ha='left', va='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='white', edgecolor='#FFA500', alpha=0.85))
ax_had.text(-0.5, 97,
            'AKTIF\nKehadiran Tinggi (≥ 80%)',
            fontsize=9, color='#1B5E20', ha='left', va='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='white', edgecolor='#4CAF50', alpha=0.85))

for i, fn in enumerate(daftar_fungsi_all):
    data_f2 = df_kehadiran_all[df_kehadiran_all['Nama Fungsi'] == fn].sort_values('Bulan')
    ax_had.plot(data_f2['Bulan'].astype(str), data_f2['Tingkat Kehadiran (%)'],
                marker=marker_list[i % len(marker_list)],
                color=warna_palet[i % len(warna_palet)],
                linewidth=2, markersize=8, label=fn, zorder=3)

ax_had.set_title('Tren Rata-rata Tingkat Kehadiran Per Fungsi Keluarga\n(Semua Fungsi Dalam Satu Diagram)',
                  fontsize=14, fontweight='bold', pad=15)
ax_had.set_xlabel('Bulan', fontsize=11)
ax_had.set_ylabel('Rata-rata Tingkat Kehadiran (%)', fontsize=11)
ax_had.set_ylim(0, 115)
ax_had.grid(axis='y', linestyle='--', alpha=0.4)
ax_had.grid(axis='x', linestyle=':', alpha=0.3)
ax_had.tick_params(axis='x', rotation=30, labelsize=9)
ax_had.legend(title='Fungsi Keluarga', title_fontsize=10, fontsize=9,
               loc='upper left', bbox_to_anchor=(1.01, 1), borderaxespad=0, framealpha=0.9)

render_tabel(ax_had_sum)
plt.tight_layout()
st.pyplot(fig_had); plt.close()