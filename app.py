# app.py — Final + Auto Backup Dataset Lama + Fix Login Siswa + Full Data Siswa
import streamlit as st
from views import dashboard, data_siswa, data_guru, rapor, statistik, prediksi
import pandas as pd
import sqlite3
import os
from datetime import datetime

from login import show as login_show, logout

DB_FILE = "database.db"
BACKUP_DIR = "backup"

# =========================
# Util dataset
# =========================
def normalize_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Samakan nama kolom supaya konsisten"""
    df.columns = [c.strip().title() for c in df.columns]

    if "Nis" in df.columns:
        df = df.rename(columns={"Nis": "NIS"})
    if "Nisn" in df.columns:
        df = df.rename(columns={"Nisn": "NISN"})
    if "Nama Siswa" in df.columns and "Nama" not in df.columns:
        df = df.rename(columns={"Nama Siswa": "Nama"})
    if "Mtk" in df.columns:
        df = df.rename(columns={"Mtk": "MTK"})
    if "B.Indonesia" in df.columns:
        df = df.rename(columns={"B.Indonesia": "Indo"})
    if "B.Inggris" in df.columns:
        df = df.rename(columns={"B.Inggris": "Inggris"})
    if "Ppkn" in df.columns:
        df = df.rename(columns={"Ppkn": "PPKN"})
    return df

def save_dataset_to_db(df: pd.DataFrame):
    conn = sqlite3.connect(DB_FILE)
    df.to_sql("siswa", conn, if_exists="replace", index=False)
    conn.close()

def load_dataset_from_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql("SELECT * FROM siswa", conn)
        conn.close()
        return df
    except Exception:
        return None

def backup_dataset():
    """Backup dataset lama sebelum diganti"""
    df_old = load_dataset_from_db()
    if df_old is not None:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"siswa_backup_{timestamp}.csv")
        df_old.to_csv(backup_file, index=False)
        st.info(f"📦 Dataset lama di-backup: {backup_file}")

# =========================
# Sidebar untuk Admin/Guru
# =========================
def sidebar_menu_admin():
    with st.sidebar:
        st.image("assets/img/logo.png", use_container_width=True)
        st.markdown("### 📂 Dataset")
        uploaded_file = st.file_uploader("Upload file CSV/XLSX", type=["csv","xls","xlsx"])

        # Hapus dataset lama saat tidak ada file
        if uploaded_file is None and "dataset" in st.session_state:
            del st.session_state["dataset"]

        # Proses upload file
        if uploaded_file is not None:
            try:
                raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
                df = normalize_dataset(raw)

                # Backup dataset lama
                backup_dataset()

                # Simpan dataset baru
                st.session_state["dataset"] = df.copy()
                save_dataset_to_db(df)
                st.success("✅ Dataset berhasil diunggah dan tersimpan ke DB")
            except Exception as e:
                st.error(f"❌ Gagal memproses file: {e}")
        else:
            # Load dataset dari DB jika session_state belum ada
            if "dataset" not in st.session_state:
                db_df = load_dataset_from_db()
                if db_df is not None:
                    st.session_state["dataset"] = db_df
            if "dataset" not in st.session_state:
                st.info("Belum ada file diunggah.")

        st.markdown("---")
        menu = [
            "🏠 Dashboard","👨‍🎓 Data Siswa","👨‍🏫 Data Guru",
            "📑 Rapor","📊 Statistik","🤖 Prediksi Kelulusan","🚪 Logout"
        ]
        return st.radio("Navigasi", menu, label_visibility="collapsed")

# =========================
# Sidebar untuk Siswa
# =========================
def sidebar_menu_siswa():
    with st.sidebar:
        st.image("assets/img/logo.png", use_container_width=True)
        menu = ["🤖 Prediksi Kelulusan","🚪 Logout"]
        return st.radio("Navigasi", menu, label_visibility="collapsed")

# =========================
# Main
# =========================
def main():
    st.set_page_config(page_title="Sistem Akademik", layout="wide")

    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login_show()
        return

    role = st.session_state.get("role", "")

    # ================= Siswa =================
    if role == "Siswa":
        choice = sidebar_menu_siswa()
        if choice == "🤖 Prediksi Kelulusan":
            df = load_dataset_from_db()
            if df is not None:
                st.session_state["dataset"] = df
                nama = st.session_state.get("nama", "").strip()
                nis = str(st.session_state.get("nis", "")).strip()

                # Pastikan Nama & NIS cocok (case-insensitive)
                df_siswa = df[
                    (df["Nama"].astype(str).str.strip().str.lower() == nama.lower()) &
                    (df["NIS"].astype(str).str.strip() == nis)
                ]

                if not df_siswa.empty:
                    st.subheader("📊 Nilai & Hasil Prediksi Anda")
                    st.dataframe(df_siswa, use_container_width=True)

                    # Tampilkan juga hasil prediksi model
                    try:
                        prediksi.show_siswa(df_siswa)
                    except:
                        st.warning("⚠️ Modul prediksi belum siap.")
                else:
                    st.error("❌ Nama / NIS tidak terdaftar!")
            else:
                st.warning("⚠️ Dataset belum tersedia, silakan hubungi Admin/Guru.")
        elif choice == "🚪 Logout":
            if "dataset" in st.session_state: del st.session_state["dataset"]
            logout()

    # ================= Admin / Guru =================
    else:
        choice = sidebar_menu_admin()
        if choice == "🏠 Dashboard":
            dashboard.show()
        elif choice == "👨‍🎓 Data Siswa":
            # 🔥 Panggil CRUD siswa
            data_siswa.show()
        elif choice == "👨‍🏫 Data Guru":
            data_guru.show()
        elif choice == "📑 Rapor":
            rapor.show()
        elif choice == "📊 Statistik":
            statistik.show()
        elif choice == "🤖 Prediksi Kelulusan":
            if "dataset" in st.session_state:
                prediksi.show()
            else:
                st.warning("⚠️ Dataset belum tersedia, silakan unggah terlebih dahulu.")
        elif choice == "🚪 Logout":
            if "dataset" in st.session_state: del st.session_state["dataset"]
            logout()

if __name__ == "__main__":
    main()
