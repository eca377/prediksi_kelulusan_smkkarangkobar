# views/data_siswa.py — CRUD + Auto Sync dari Dataset
import streamlit as st
import sqlite3
import pandas as pd

DB_FILE = "database.db"

# =========================
# DB Setup
# =========================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS siswa_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nis TEXT UNIQUE,
            nama TEXT,
            kelas TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_all_siswa():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM siswa_master ORDER BY kelas, nama", conn)
    conn.close()
    return df

def sync_from_dataset():
    """Sinkronkan data siswa dari tabel 'siswa' (dataset nilai)"""
    conn = sqlite3.connect(DB_FILE)
    try:
        df_dataset = pd.read_sql_query("SELECT * FROM siswa", conn)
    except Exception:
        conn.close()
        return

    if df_dataset.empty:
        conn.close()
        return

    # Ambil kolom utama
    nis_col = next((c for c in df_dataset.columns if c.lower() == "nis"), None)
    nama_col = next((c for c in df_dataset.columns if c.lower() == "nama"), None)
    kelas_col = next((c for c in df_dataset.columns if "kelas" in c.lower()), None)

    if not nis_col or not nama_col:
        conn.close()
        return

    # Buat dataframe master
    df_master = df_dataset[[nis_col, nama_col] + ([kelas_col] if kelas_col else [])].copy()
    df_master.columns = ["nis", "nama"] + (["kelas"] if kelas_col else [])

    # Insert unik ke siswa_master
    cur = conn.cursor()
    for _, row in df_master.iterrows():
        nis = str(row["nis"]).strip()
        nama = str(row["nama"]).strip()
        kelas = str(row["kelas"]).strip() if "kelas" in df_master.columns else "-"
        try:
            cur.execute(
                "INSERT OR IGNORE INTO siswa_master (nis, nama, kelas) VALUES (?,?,?)",
                (nis, nama, kelas)
            )
        except Exception:
            pass
    conn.commit()
    conn.close()

def add_siswa(nis, nama, kelas):
    if not nis or not nama:
        st.error("❌ NIS dan Nama wajib diisi!")
        return
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO siswa_master (nis, nama, kelas) VALUES (?,?,?)", (nis, nama, kelas))
        conn.commit()
        st.success(f"✅ Siswa {nama} ({nis}) berhasil ditambahkan")
    except sqlite3.IntegrityError:
        st.error("❌ NIS sudah ada!")
    conn.close()

def update_siswa(id, nis, nama, kelas):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE siswa_master SET nis=?, nama=?, kelas=? WHERE id=?", (nis, nama, kelas, id))
    conn.commit()
    conn.close()
    st.success("✅ Data siswa berhasil diperbarui")

def delete_siswa(id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM siswa_master WHERE id=?", (id,))
    conn.commit()
    conn.close()
    st.success("✅ Data siswa berhasil dihapus")

# =========================
# Halaman
# =========================
def show():
    st.title("📚 Manajemen Data Siswa")
    init_db()

    # Sinkron otomatis dari dataset kalau tabel masih kosong
    df_master = get_all_siswa()
    if df_master.empty:
        sync_from_dataset()
        df_master = get_all_siswa()

    menu = st.radio("Menu", ["📋 Semua Data", "➕ Tambah / Edit / Hapus"], horizontal=True)

    if menu == "📋 Semua Data":
        df = get_all_siswa()
        if df.empty:
            st.info("Belum ada data siswa")
        else:
            st.subheader("📋 Semua Riwayat Data Siswa")
            st.dataframe(df, use_container_width=True)

    elif menu == "➕ Tambah / Edit / Hapus":
        df = get_all_siswa()
        if not df.empty:
            st.subheader("📋 Data Saat Ini")
            st.dataframe(df, use_container_width=True)

        with st.form("add_siswa_form", clear_on_submit=True):
            nis = st.text_input("🆔 NIS")
            nama = st.text_input("👤 Nama Siswa")
            kelas = st.text_input("🏫 Kelas")
            submitted = st.form_submit_button("Tambah")
            if submitted:
                add_siswa(nis, nama, kelas)
                st.experimental_rerun()

        if not df.empty:
            siswa_id = st.selectbox("Pilih ID Siswa untuk Edit/Hapus", df["id"])
            siswa_row = df[df["id"] == siswa_id].iloc[0]

            with st.form("edit_siswa_form"):
                nis = st.text_input("🆔 NIS", siswa_row["nis"])
                nama = st.text_input("👤 Nama", siswa_row["nama"])
                kelas = st.text_input("🏫 Kelas", siswa_row["kelas"])
                col1, col2 = st.columns(2)
                with col1:
                    update_btn = st.form_submit_button("💾 Update")
                with col2:
                    delete_btn = st.form_submit_button("🗑️ Hapus")

                if update_btn:
                    update_siswa(siswa_id, nis, nama, kelas)
                    st.experimental_rerun()
                if delete_btn:
                    delete_siswa(siswa_id)
                    st.experimental_rerun()
