# login.py — Modul Login dengan SQLite (Khusus Admin)
import streamlit as st
import sqlite3
import base64

DB_PATH = "data.db"

# =========================
# DB Setup
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT CHECK(role IN ('Admin'))
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

def check_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT role FROM users WHERE username=? AND password=?",
        (username, password)
    )
    result = c.fetchone()
    conn.close()
    if result and result[0] == "Admin":
        return True
    return False

# =========================
# Background
# =========================
def set_bg(image_file="assets/img/bg8.jpg"):
    try:
        with open(image_file, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: url("data:image/png;base64,{b64}") no-repeat center center fixed;
                background-size: cover;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except FileNotFoundError:
        pass

# =========================
# Halaman Login
# =========================
def login_page():
    init_db()
    set_bg()
    logo_path = "assets/img/logo.png"

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
        st.image(logo_path, width=160)
        st.markdown("<h3 style='color:white'>Sistem Prediksi Kelulusan Siswa</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:white'>SMK Ma'arif NU 01 Karangkobar</p>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='login-title'>🔑 Login Sistem</div>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 Username")
            password = st.text_input("🔒 Password", type="password")
            submitted = st.form_submit_button("Masuk")

            if submitted:
                if check_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = "Admin"
                    st.success("✅ Login berhasil sebagai Admin!")
                    st.rerun()
                else:
                    st.error("❌ Username / password salah!")

        st.markdown("</div>", unsafe_allow_html=True)

# =========================
# Ekspor fungsi
# =========================
def show():
    login_page()

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.success("✅ Logout berhasil")
    st.rerun()
