import os
import sqlite3
import base64
import streamlit as st
import pandas as pd
import views.prediksi as prediksi

DB_PATH = "data.db"
DATASET_PATH = os.path.join("data", "dataset.xlsx")

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
    # Tambahkan admin default
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                  ("admin", "admin123", "Admin"))
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
                """, unsafe_allow_html=True
            )
    except Exception as e:
        st.warning(f"⚠️ Background tidak dimuat: {e}")

# =========================
# Halaman Login (Admin only)
# =========================
def login_page():
    init_db()
    set_bg()
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "img", "logo.png")

    # Load dataset sekali saja
    if "dataset" not in st.session_state:
        try:
            if os.path.exists(DATASET_PATH):
                df = pd.read_excel(DATASET_PATH)
                df.columns = df.columns.str.strip()
                st.session_state["dataset"] = df
            else:
                st.error(f"❌ File {DATASET_PATH} tidak ditemukan!")
        except Exception as e:
            st.error(f"❌ Gagal membaca dataset.xlsx: {e}")

    # Custom style
    st.markdown("""
    <style>
    .login-box {background: rgba(255,255,255,0.9); border-radius: 16px; padding: 30px; width: 330px; margin: auto; box-shadow: 0 8px 24px rgba(0,0,0,0.35);}
    .login-title {font-size: 22px; font-weight: bold; margin-bottom: 15px; text-align: center;}
    .stButton>button {width: 100% !important; border-radius: 8px; padding: 10px; background: linear-gradient(135deg,#1f1f1f,#3a3a3a); color: white; border: none;}
    .stButton>button:hover {background: linear-gradient(135deg,#52b87d,#3bb371);}
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])
    with col1:
        if os.path.exists(logo_path):
            st.image(logo_path, width=160)
        st.markdown("<h3 style='color:white'>Sistem Prediksi Kelulusan Siswa</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:white'>SMK Ma'arif NU 01 Karangkobar</p>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='login-title'>🔑 Login Admin</div>", unsafe_allow_html=True)
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

    # Jika sudah login admin → tampilkan prediksi admin
    if st.session_state.get("logged_in") and st.session_state.role == "Admin":
        prediksi.show()

# =========================
# Ekspor fungsi
# =========================
def show():
    login_page()

def logout():
    for key in ["logged_in", "username", "role"]:
        if key in st.session_state:
            del st.session_state[key]
    st.success("✅ Logout berhasil")
    st.rerun()
