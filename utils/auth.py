import streamlit as st

USERS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "guru": {"password": "guru123", "role": "Guru"},
    "siswa": {"password": "siswa123", "role": "Siswa"},
}

def authenticate(username, password):
    user = USERS.get(username)
    if user and user["password"] == password:
        return True, user["role"]
    return False, None

def sidebar_auth_fallback():
    st.sidebar.header("🔐 Login Sistem")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Login")

    if login_btn:
        valid, role = authenticate(username, password)
        if valid:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.sidebar.success(f"✅ Login berhasil sebagai {role}")
            st.rerun()
        else:
            st.sidebar.error("❌ Username atau password salah.")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.success("✅ Anda sudah logout.")
