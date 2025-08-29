# views/data_siswa.py — CRUD Data Siswa
import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "data.db"

# =========================
# DB Setup
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS siswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nis TEXT UNIQUE,
            nama TEXT,
            kelas TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_all_siswa():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM siswa", conn)
    conn.close()
    return df

def add_siswa(nis, nama, kelas):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO siswa (nis, nama, kelas) VALUES (?,?,?)", (nis, nama, kelas))
        conn.commit()
        st.success(f"✅ Siswa {nama} ({nis}) berhasil ditambahkan")
    except sqlite3.IntegrityError:
        st.error("❌ NIS sudah ada!")
    conn.close()

def update_siswa(id, nis, nama, kelas):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE siswa SET nis=?, nama=?, kelas=? WHERE id=?", (nis, nama, kelas, id))
    conn.commit()
    conn.close()
    st.success("✅ Data siswa berhasil diperbarui")

def delete_siswa(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM siswa WHERE id=?", (id,))
    conn.commit()
    conn.close()
    st.success("✅ Data siswa berhasil dihapus")

# =========================
# Halaman
# =========================
def show():
    st.title("📚 Manajemen Data Siswa")
    init_db()

    menu = st.radio("Menu", ["➕ Tambah", "📋 Lihat / Edit / Hapus"], horizontal=True)

    if menu == "➕ Tambah":
        with st.form("add_siswa_form", clear_on_submit=True):
            nis = st.text_input("NIS")
            nama = st.text_input("Nama Siswa")
            kelas = st.text_input("Kelas")
            submitted = st.form_submit_button("Tambah")
            if submitted and nis and nama:
                add_siswa(nis, nama, kelas)

        # 🔥 langsung tampilkan data setelah input
        df = get_all_siswa()
        if not df.empty:
            st.subheader("📋 Data Siswa Saat Ini")
            st.dataframe(df, use_container_width=True)

    elif menu == "📋 Lihat / Edit / Hapus":
        df = get_all_siswa()
        if df.empty:
            st.info("Belum ada data siswa")
        else:
            st.dataframe(df, use_container_width=True)

            # Pilih siswa untuk edit / hapus
            siswa_id = st.selectbox("Pilih ID Siswa", df["id"])
            siswa_row = df[df["id"] == siswa_id].iloc[0]

            with st.form("edit_siswa_form"):
                nis = st.text_input("NIS", siswa_row["nis"])
                nama = st.text_input("Nama", siswa_row["nama"])
                kelas = st.text_input("Kelas", siswa_row["kelas"])
                col1, col2 = st.columns(2)
                with col1:
                    update_btn = st.form_submit_button("💾 Update")
                with col2:
                    delete_btn = st.form_submit_button("🗑️ Hapus")

                if update_btn:
                    update_siswa(siswa_id, nis, nama, kelas)
                if delete_btn:
                    delete_siswa(siswa_id)
