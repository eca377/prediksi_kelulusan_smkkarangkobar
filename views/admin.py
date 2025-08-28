import streamlit as st
import sqlite3

DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # buat tabel kalau belum ada
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()

    # cek apakah kolom role sudah ada
    c.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in c.fetchall()]
    if "role" not in cols:
        try:
            c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'Siswa'")
            conn.commit()
        except Exception as e:
            print("Kolom role sudah ada atau gagal:", e)

    conn.close()


def show(df=None):
    st.title("👨‍💻 Manajemen Pengguna")

    # init database
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    menu = ["Daftar User", "Tambah User"]
    choice = st.sidebar.radio("📌 Menu Admin", menu)

    # ------------------------------
    # Daftar User
    # ------------------------------
    if choice == "Daftar User":
        st.subheader("📋 Daftar User")
        users = c.execute("SELECT rowid, username, role FROM users").fetchall()
        if users:
            for u in users:
                col1, col2, col3, col4 = st.columns([2,2,2,1])
                with col1:
                    st.write(f"**{u[1]}**")
                with col2:
                    st.write(f"Role: {u[2]}")
                with col3:
                    new_role = st.selectbox(
                        "Ubah role", ["Admin","Guru","Siswa"],
                        index=["Admin","Guru","Siswa"].index(u[2] if u[2] else "Siswa"),
                        key=f"role_{u[0]}"
                    )
                with col4:
                    if st.button("❌ Hapus", key=f"del_{u[0]}"):
                        c.execute("DELETE FROM users WHERE rowid=?", (u[0],))
                        conn.commit()
                        st.success(f"User {u[1]} dihapus.")
                        st.rerun()
                # update role jika berubah
                if new_role != u[2]:
                    c.execute("UPDATE users SET role=? WHERE rowid=?", (new_role, u[0]))
                    conn.commit()
                    st.success(f"Role {u[1]} diubah ke {new_role}")
                    st.rerun()
        else:
            st.info("Belum ada user.")

    # ------------------------------
    # Tambah User
    # ------------------------------
    elif choice == "Tambah User":
        st.subheader("➕ Tambah User Baru")
        with st.form("form_tambah_user", clear_on_submit=True):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["Admin","Guru","Siswa"])
            submitted = st.form_submit_button("Simpan")

        if submitted:
            if username and password:
                try:
                    c.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
                              (username, password, role))
                    conn.commit()
                    st.success(f"User {username} berhasil dibuat sebagai {role}.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("⚠️ Username sudah ada, gunakan yang lain.")
            else:
                st.error("Username dan password wajib diisi.")

    conn.close()
