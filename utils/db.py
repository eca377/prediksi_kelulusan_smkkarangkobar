import sqlite3
import pandas as pd

DB_NAME = "akademik.db"

def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

# =========================
# INIT DATABASE
# =========================
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Tabel Guru
    cur.execute("""
    CREATE TABLE IF NOT EXISTS guru (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Nama TEXT NOT NULL,
        NIP TEXT NOT NULL,
        Mapel TEXT NOT NULL
    )
    """)

    # Tabel Users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        linked_id INTEGER
    )
    """)

    # Seed admin default
    cur.execute("SELECT * FROM users WHERE role='Admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                    ("admin","admin123","Admin"))
    
    conn.commit()
    conn.close()

# =========================
# CRUD GURU
# =========================
def get_guru():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM guru", conn)
    conn.close()
    return df

def add_guru(nama, nip, mapel):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO guru (Nama, NIP, Mapel) VALUES (?, ?, ?)", (nama, nip, mapel))
    conn.commit()
    conn.close()

def update_guru(id_guru, nama, nip, mapel):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE guru SET Nama=?, NIP=?, Mapel=? WHERE id=?", (nama, nip, mapel, id_guru))
    conn.commit()
    conn.close()

def delete_guru(id_guru):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM guru WHERE id=?", (id_guru,))
    conn.commit()
    conn.close()

# =========================
# CRUD USERS
# =========================
def get_users():
    conn = get_conn()
    df = pd.read_sql("SELECT id,username,role FROM users", conn)
    conn.close()
    return df

def add_user(username, password, role, linked_id=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username,password,role,linked_id) VALUES (?,?,?,?)",
                (username,password,role,linked_id))
    conn.commit()
    conn.close()

def update_user(user_id, username, password, role):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET username=?, password=?, role=? WHERE id=?",
                (username,password,role,user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

# Init DB sekali jalan
init_db()
