# app.py
import streamlit as st
from views import dashboard, data_siswa, data_guru, rapor, statistik, prediksi
import pandas as pd
import sqlite3

# login.py sejajar dengan app.py
from login import show as login_show, logout

DB_FILE = "database.db"

# =========================
# Util dataset
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
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql("SELECT * FROM siswa", conn)
        conn.close()
        return df
    except Exception:
        return None

# =========================
# Sidebar
# =========================
def sidebar_menu():
    with st.sidebar:
        st.markdown("### 📂 Dataset")

        # Upload dataset
        uploaded_file = st.file_uploader("Upload file CSV/XLSX", type=["csv","xls","xlsx"])

        # Reset dataset otomatis saat tidak ada file diupload
        if uploaded_file is None and "dataset" in st.session_state:
            del st.session_state["dataset"]

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
            # jika ada dataset di db, load otomatis
            if "dataset" not in st.session_state:
                db_df = load_dataset_from_db()
                if db_df is not None:
                    st.session_state["dataset"] = db_df
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

    # cek login
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login_show()
        return

    # sidebar menu
    choice = sidebar_menu()

    # navigasi
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
            prediksi.show()   # ✅ pakai session_state["dataset"]
        else:
            st.warning("⚠️ Dataset belum tersedia, silakan unggah terlebih dahulu.")
    elif choice == "🚪 Logout":
        # ✅ Kosongkan dataset dari session_state
        if "dataset" in st.session_state:
            del st.session_state["dataset"]

        # ✅ Hapus dataset dari database
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS siswa")
        conn.commit()
        conn.close()

        logout()

if __name__ == "__main__":
    main()
