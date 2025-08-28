# utils/helpers.py
import os
import io
import pandas as pd
import streamlit as st

PRIMARY = "#f5f5f5"     # teks putih
ACCENT = "#52b87d"      # hijau aksen
BG_DARK = "#2c2c2c"     # hitam background
BG_SIDEBAR = "#1f1f1f"  # sidebar lebih gelap

STYLE_CSS = f"""
<style>
/* GLOBAL */
.stApp {{ background: #f7faf7; }}
.block-container {{ padding-top: .8rem !important; }}
h1,h2,h3,h4,h5 {{ color: {BG_SIDEBAR} !important; }}

/* SIDEBAR */
section[data-testid="stSidebar"] {{
    background: {BG_SIDEBAR};
}}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, 
[data-testid="stSidebar"] span {{
    color: {PRIMARY} !important;
    font-weight: 500;
}}

/* FILE UPLOADER (outer) */
[data-testid="stFileUploader"] section {{
    background: {BG_DARK} !important;
    border-radius: 10px !important;
}}
/* FILE UPLOADER (inner drag&drop) */
[data-testid="stFileUploader"] section div:first-child {{
    background-color: {BG_DARK} !important;
    border: 2px dashed #444 !important;
    border-radius: 10px !important;
    padding: 1rem !important;
    color: {PRIMARY} !important;
}}
[data-testid="stFileUploader"] section div:first-child:hover {{
    border-color: {ACCENT} !important;
    background-color: #1a1a1a !important;
}}
[data-testid="stFileUploader"] section div:first-child * {{
    color: {PRIMARY} !important;
}}

/* CARD */
.kpi, .card {{
    border-radius: 14px;
    background: #fff;
    padding: 14px;
    border: 1px solid #eaeaea;
    box-shadow: 0 6px 18px rgba(0,0,0,.05);
    margin-bottom: 1rem;
}}
/* BUTTON */
.stButton>button {{
    background: {BG_SIDEBAR};
    color: #fff;
    border-radius: 10px;
    padding: .5rem 1rem;
    border: none;
}}
.stButton>button:hover {{ background: {ACCENT}; }}
</style>
"""

def show_logo(location="main", width=110):
    """
    Tampilkan logo aman tanpa error:
    - cek assets/smk.png
    - cek assets/img/smk.png
    - jika tidak ada: tampilkan judul teks
    """
    candidates = ["assets/smk.png", "assets/img/smk.png"]
    for path in candidates:
        if os.path.exists(path):
            if location == "sidebar":
                st.sidebar.image(path, width=width)
            else:
                st.image(path, width=width)
            return
    # fallback teks
    if location == "sidebar":
        st.sidebar.markdown("### 🏫 SMK Dashboard")
    else:
        st.markdown("### 🏫 SMK Dashboard")

# Kolom meta (bukan mapel)
META_COLS = {"NO","NAMA","NIS","NISN","KELAS","TOTAL","SAKIT","IZIN","ALPA","EKSTRA","B"}

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Bersihkan nama kolom + konversi numerik aman untuk kolom mapel."""
    out = df.copy()
    out.columns = [str(c).strip().upper() for c in out.columns]
    # Buang Unnamed
    out = out.loc[:, ~out.columns.astype(str).str.contains(r"^UNNAMED", na=False)]
    # Konversi numerik aman untuk kolom mapel
    for c in out.columns:
        if c not in META_COLS:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    # TOTAL juga numeric kalau ada
    if "TOTAL" in out.columns:
        out["TOTAL"] = pd.to_numeric(out["TOTAL"], errors="coerce")
    return out

def detect_mapel_columns(df: pd.DataFrame):
    """Deteksi kolom mapel dari dataset lebar (exclude kolom meta)."""
    return [c for c in df.columns if c not in META_COLS]

def try_read_any(file):
    """Baca CSV/XLS/XLSX dari UploadedFile atau path."""
    name = getattr(file, "name", str(file)).lower()
    if name.endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)

def df_download_button(df, filename="data.csv", label="💾 Download CSV"):
    """Tombol download DataFrame jadi CSV."""
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(label, data=csv, file_name=filename, mime="text/csv")
