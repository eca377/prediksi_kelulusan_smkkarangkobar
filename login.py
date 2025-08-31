# login.py
import os
import sqlite3
import base64
import streamlit as st
import views.prediksi as prediksi   # 🔑 langsung import prediksi.py

DB_PATH = "data.db"

# =========================
# DB Setup
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Table users (Admin)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT CHECK(role IN ('Admin'))
        )
    """)

    # Table siswa (untuk login siswa)
    c.execute("""
        CREATE TABLE IF NOT EXISTS siswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            nis TEXT,
            kelas TEXT
        )
    """)

    # Table hasil prediksi
    c.execute("""
        CREATE TABLE IF NOT EXISTS hasil_prediksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            nis TEXT,
            kelas TEXT,
            status TEXT
        )
    """)

    # Seed admin default
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (username,password,role) VALUES (?,?,?)",
            ("admin", "admin123", "Admin")
        )
    conn.commit()
    conn.close()

# =========================
# Auth Check
# =========================
def check_login_admin(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    if result and result[0] == "Admin":
        return {"role": "Admin", "username": username}
    return None

def check_login_siswa(nama, nis):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM siswa WHERE nama=? AND nis=?", (nama, nis))
    siswa = c.fetchone()
    conn.close()
    if siswa:
        return {"role": "Siswa", "username": nama, "nis": nis, "kelas": siswa[3]}
    return None

# =========================
# Background
# =========================
def set_bg(image_file="assets/img/bg8.jpg"):
    try:
        BASE_DIR = os.path.dirname(__file__)
        image_file = os.path.join(BASE_DIR, image_file)
        if os.path.exists(image_file):
            with open(image_file, "rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode()
            ext = os.path.splitext(image_file)[1][1:]
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background: url("data:image/{ext};base64,{b64}") no-repeat center center fixed;
                    background-size: cover;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
    except Exception as e:
        st.warning(f"⚠️ Background tidak dimuat: {e}")

# =========================
# Halaman Login
# =========================
def login_page():
    init_db()
    set_bg()
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "img", "logo.png")

    # Custom style
    st.markdown("""
    <style>
    .login-box {
        background: rgba(255,255,255,0.9);
        border-radius: 16px;
        padding: 30px;
        width: 330px;
        margin: auto;
        box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    }
    .login-title {
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 15px;
        text-align: center;
    }
    .stButton>button {
        width: 100% !important;
        border-radius: 8px;
        padding: 10px;
        background: linear-gradient(135deg,#1f1f1f,#3a3a3a);
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg,#52b87d,#3bb371);
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])
    with col1:
        if os.path.exists(logo_path):
            st.image(logo_path, width=160)
        else:
            st.warning("⚠️ Logo tidak ditemukan")
        st.markdown("<h3 style='color:white'>Sistem Prediksi Kelulusan Siswa</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:white'>SMK Ma'arif NU 01 Karangkobar</p>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='login-title'>🔑 Pilih Login</div>", unsafe_allow_html=True)

        role_tabs = st.tabs(["👨‍💼 Admin", "🎓 Siswa"])

        # === Login Admin ===
        with role_tabs[0]:
            st.info("Masuk sebagai **Admin** dengan Username & Password.")
            with st.form("admin_login_form", clear_on_submit=False):
                username = st.text_input("👤 Username")
                password = st.text_input("🔒 Password", type="password")
                submitted = st.form_submit_button("Masuk sebagai Admin")

                if submitted:
                    user = check_login_admin(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.role = user["role"]
                        st.session_state.username = user["username"]
                        st.success("✅ Login Admin berhasil!")
                        st.rerun()
                    else:
                        st.error("❌ Username / Password salah!")

        # === Login Siswa ===
        with role_tabs[1]:
            st.info("Masuk sebagai **Siswa** menggunakan Nama & NIS.")
            with st.form("siswa_login_form", clear_on_submit=False):
                nama = st.text_input("👤 Nama Lengkap")
                nis = st.text_input("🆔 NIS")
                submitted = st.form_submit_button("Masuk sebagai Siswa")

                if submitted:
                    user = check_login_siswa(nama, nis)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.role = user["role"]
                        st.session_state.username = user["username"]
                        st.session_state.nis = user["nis"]
                        st.session_state.kelas = user["kelas"]
                        st.success("✅ Login Siswa berhasil! Menampilkan hasil prediksi...")
                        st.session_state.show_prediksi = True
                        st.rerun()
                    else:
                        st.error("❌ Nama / NIS tidak ditemukan!")

        st.markdown("</div>", unsafe_allow_html=True)

    # Jika siswa login → langsung tampilkan prediksi
    if st.session_state.get("show_prediksi") and st.session_state.role == "Siswa":
        prediksi.show()

# =========================
# Ekspor fungsi
# =========================
def show():
    login_page()

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    if "nis" in st.session_state:
        del st.session_state["nis"]
    if "kelas" in st.session_state:
        del st.session_state["kelas"]
    if "show_prediksi" in st.session_state:
        del st.session_state["show_prediksi"]
    st.success("✅ Logout berhasil")
    st.rerun()
