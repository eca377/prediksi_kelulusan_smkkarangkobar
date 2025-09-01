# views/data_guru.py
import streamlit as st
import pandas as pd
import sqlite3

DB_FILE = "database.db"

# =============================
# DATABASE FUNCTIONS
# =============================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS guru (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            mapel TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def tambah_guru(nama, mapel, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO guru (nama, mapel, status) VALUES (?, ?, ?)", (nama, mapel, status))
    conn.commit()
    conn.close()

def get_guru():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM guru", conn)
    conn.close()
    return df

def hapus_guru(guru_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM guru WHERE id=?", (guru_id,))
    conn.commit()
    conn.close()

def update_guru(guru_id, nama, mapel, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE guru SET nama=?, mapel=?, status=? WHERE id=?", (nama, mapel, status, guru_id))
    conn.commit()
    conn.close()

# =============================
# STREAMLIT UI
# =============================
def show():
    st.markdown("## 👩‍🏫 Manajemen Data Guru")
    init_db()

    # =============================
    # FORM TAMBAH GURU
    # =============================
    with st.expander("➕ Tambah Guru Baru", expanded=True):
        with st.form("form_tambah_guru", clear_on_submit=True):
            nama = st.text_input("Nama Guru")
            mapel = st.text_input("Mata Pelajaran")
            status = st.selectbox("Status", ["Produktif", "Honorer", "Tetap"])
            submit = st.form_submit_button("Simpan Guru")

            if submit:
                if nama and mapel:
                    tambah_guru(nama, mapel, status)
                    st.success(f"Guru **{nama}** berhasil ditambahkan.")
                    # set flag agar dashboard tahu ada perubahan
                    st.session_state["reload_guru"] = True
                else:
                    st.error("Nama dan Mapel wajib diisi!")

    st.markdown("---")

    # =============================
    # TABEL DAFTAR GURU
    # =============================
    st.subheader("📋 Daftar Guru")
    df = get_guru()

    if not df.empty:
        for i, row in df.iterrows():
            edit_key = f"edit_{row['id']}"
            delete_key = f"delete_{row['id']}"

            if "edit_id" in st.session_state and st.session_state["edit_id"] == row["id"]:
                # MODE EDIT
                with st.form(f"form_edit_{row['id']}"):
                    nama_edit = st.text_input("Nama Guru", value=row["nama"])
                    mapel_edit = st.text_input("Mata Pelajaran", value=row["mapel"])
                    status_edit = st.selectbox("Status", ["Produktif","Honorer","Tetap"],
                                               index=["Produktif","Honorer","Tetap"].index(row["status"]))
                    simpan_edit = st.form_submit_button("💾 Simpan Perubahan")
                    batal_edit = st.form_submit_button("❌ Batal")

                    if simpan_edit:
                        update_guru(row["id"], nama_edit, mapel_edit, status_edit)
                        st.success(f"Guru **{nama_edit}** berhasil diperbarui.")
                        del st.session_state["edit_id"]
                        st.session_state["reload_guru"] = True
                    if batal_edit:
                        del st.session_state["edit_id"]

            else:
                # MODE TAMPIL DATA
                c1, c2, c3, c4, c5 = st.columns([3,3,2,1,1])
                with c1: st.write(row["nama"])
                with c2: st.write(row["mapel"])
                with c3: st.write(row["status"])
                with c4:
                    if st.button("✏️", key=edit_key):
                        st.session_state["edit_id"] = row["id"]
                with c5:
                    if st.button("🗑️", key=delete_key):
                        hapus_guru(row["id"])
                        st.success(f"Guru **{row['nama']}** berhasil dihapus.")
                        st.session_state["reload_guru"] = True
    else:
        st.info("Belum ada data guru.")
