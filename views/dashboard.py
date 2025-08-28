# views/dashboard.py
import streamlit as st
import pandas as pd
import altair as alt
import sqlite3

DB_FILE = "database.db"

# =========================
# Helper Cards
# =========================
def _kpi_card(title: str, value: str, delta: str = ""):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg,#0f172a,#1e293b);
            color:white;padding:16px;border-radius:18px;
            box-shadow:0 10px 24px rgba(0,0,0,.18)">
            <div style="font-size:13px;opacity:.85">{title}</div>
            <div style="font-size:28px;font-weight:700;margin-top:4px">{value}</div>
            <div style="font-size:12px;opacity:.85;margin-top:2px">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def _profil_card(profil: dict):
    st.markdown(
        f"""
        <div style="
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 1rem;
        ">
            <b style="font-size:18px">{profil.get("nama","SMK Ma'arif NU 01 Karangkobar")}</b><br>
            {profil.get("alamat","Jl. K.H Hasyim Asyari, Leksana, Kec. Karangkobar, Kab. Banjarnegara")}<br>
             Telepon: {profil.get("Telepon","(0286) 5988 005")}<br>
             Email : {profil.get("Email","maarifnusmk@gmail.com")}<br>
            Tahun Berdiri: {profil.get("tahun","2009")}
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# Fetch Guru from DB
# =========================
def get_guru_count():
    conn = sqlite3.connect(DB_FILE)
    try:
        df = pd.read_sql("SELECT * FROM guru", conn)
        return len(df)
    except Exception:
        return 0
    finally:
        conn.close()

# =========================
# Show Dashboard
# =========================
def show():
    st.markdown("## 📊 Dashboard Prediksi Kelulusan Siswa")
    st.caption("Ringkasan cepat, profil sekolah, dan tren akademik.")

    # LOGO & Profil
    c1, c2 = st.columns([1,4])
    with c1:
        logo = st.session_state.get("logo_sekolah", None)
        if logo:
            st.image(logo, use_container_width=True)
        else:
            st.image("assets/img/logo.png", use_container_width=True)
    with c2:
        profil = st.session_state.get("profil_sekolah", {})
        _profil_card(profil)

    # =========================
    # Cek Dataset
    # =========================
    if "dataset" not in st.session_state or st.session_state["dataset"] is None:
        st.warning("⚠️ Belum ada dataset. Silakan upload file CSV/XLSX dulu.")
        return   # 🚪 keluar supaya grafik/KPI tidak dipanggil

    df = st.session_state["dataset"].copy()

    # Kolom nilai
    exclude_cols = ["no","nis","nisn","sakit","izin","alpa"]
    nilai_cols = [c for c in df.select_dtypes(include="number").columns if c.lower() not in exclude_cols]

    if nilai_cols and "Rata-rata" not in df.columns:
        df["Rata-rata"] = df[nilai_cols].mean(axis=1)

    jumlah_siswa = len(df)
    jumlah_guru = get_guru_count()
    rapor_terisi = df["Rata-rata"].count() if "Rata-rata" in df.columns else 0
    coverage = f"{round((rapor_terisi/len(df))*100,1)}%" if len(df)>0 else "0%"
    lulus = df[df["Rata-rata"]>=70].shape[0] if "Rata-rata" in df.columns else 0
    tingkat_lulus = f"{round((lulus/len(df))*100,1)}%" if len(df)>0 else "0%"

    # KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1: _kpi_card("👨‍🎓 Jumlah Siswa", str(jumlah_siswa))
    with c2: _kpi_card("👩‍🏫 Jumlah Guru", str(jumlah_guru))
    with c3: _kpi_card("📑 Rapor Terisi", str(rapor_terisi), coverage)
    with c4: _kpi_card("🎓 Tingkat Lulus", tingkat_lulus)

    st.markdown("---")

    # Distribusi rata-rata
    if "Rata-rata" in df.columns:
        st.markdown("#### 📈 Distribusi Rata-rata Nilai Siswa")
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("Rata-rata:Q", bin=alt.Bin(maxbins=20)),
            y="count()"
        ).properties(height=360)
        st.altair_chart(chart, use_container_width=True)

        # Top 10 rata-rata
        if "Nama" in df.columns:
            st.markdown("#### 🏆 10 Besar Rata-rata Nilai")
            top10 = df.sort_values("Rata-rata", ascending=False).head(10)
            rank_chart = alt.Chart(top10).mark_bar().encode(
                x="Rata-rata",
                y=alt.Y("Nama", sort="-x"),
                color="Jurusan" if "Jurusan" in df.columns else alt.value("steelblue"),
                tooltip=["Nama","Rata-rata"]
            )
            st.altair_chart(rank_chart, use_container_width=True)

    # Distribusi Jurusan
    if "Jurusan" in df.columns:
        st.markdown("#### 🏫 Distribusi Siswa per Jurusan")
        jurusan_chart = alt.Chart(df).mark_bar().encode(
            x="Jurusan",
            y="count()",
            color="Jurusan",
            tooltip=["Jurusan","count()"]
        )
        st.altair_chart(jurusan_chart, use_container_width=True)
