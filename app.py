import streamlit as st
from views import dashboard, data_siswa, data_guru, rapor, statistik, prediksi
import pandas as pd
import sqlite3

from login import show as login_show, logout

DB_FILE = "database.db"

# =========================
# Dataset Util
# =========================
def normalize_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().title() for c in df.columns]
    if "Nis" in df.columns: df = df.rename(columns={"Nis": "NIS"})
    if "Nama Siswa" in df.columns: df = df.rename(columns={"Nama Siswa": "Nama"})
    if "Mtk" in df.columns: df = df.rename(columns={"Mtk": "MTK"})
    if "B.Indonesia" in df.columns: df = df.rename(columns={"B.Indonesia": "Indo"})
    if "B.Inggris" in df.columns: df = df.rename(columns={"B.Inggris": "Inggris"})
    if "Ppkn" in df.columns: df = df.rename(columns={"Ppkn": "PPKN"})
    return df

def save_dataset_to_db(df: pd.DataFrame):
    conn = sqlite3.connect(DB_FILE)
    df.to_sql("siswa", conn, if_exists="replace", index=False)
    conn.close()

def load_dataset_from_db():
    if "dataset" in st.session_state:
        return st.session_state["dataset"]
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql("SELECT * FROM siswa", conn)
        conn.close()
        st.session_state["dataset"] = df
        return df
    except Exception:
        return None

# =========================
# Sidebar
# =========================
def sidebar_menu():
    with st.sidebar:
        st.markdown("### 📂 Dataset")

        uploaded_file = st.file_uploader("Upload file CSV/XLSX", type=["csv","xls","xlsx"])

        if uploaded_file is not None:
            try:
                raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
                df = normalize_dataset(raw)
                st.session_state["dataset"] = df.copy()
                save_dataset_to_db(df)
                st.success("✅ Dataset berhasil diunggah")
            except Exception as e:
                st.error(f"❌ Gagal memproses file: {e}")
        else:
            if "dataset" not in st.session_state:
                load_dataset_from_db()
            if "dataset" not in st.session_state:
                st.info("Belum ada file diunggah.")

        st.markdown("---")

        menu = [
            "🏠 Dashboard",
            "👨‍🎓 Data Siswa",
            "👨‍🏫 Data Guru",
            "📑 Rapor",
            "📊 Statistik",
            "🤖 Prediksi Kelulusan",
            "🚪 Logout",
        ]
        return st.radio("Navigasi", menu, label_visibility="collapsed")

# =========================
# Main
# =========================
def main():
    st.set_page_config(page_title="Sistem Akademik", layout="wide")

    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login_show()
        return

    choice = sidebar_menu()

    # Auto redirect ke Dashboard setelah login
    if st.session_state.get("redirect_dashboard", False):
        st.session_state["redirect_dashboard"] = False
        choice = "🏠 Dashboard"

    # Navigasi
    if choice == "🏠 Dashboard":
        dashboard.show()
    elif choice == "👨‍🎓 Data Siswa":
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
            st.warning("⚠️ Dataset belum tersedia.")
    elif choice == "🚪 Logout":
        if "dataset" in st.session_state:
            del st.session_state["dataset"]
        logout()

if __name__ == "__main__":
    main()
