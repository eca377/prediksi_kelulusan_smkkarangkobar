# views/statistik.py
import streamlit as st
import pandas as pd
import altair as alt

def show():
    st.sidebar.title("📂 Statistik")

    if "dataset" not in st.session_state or st.session_state["dataset"] is None:
        st.warning("⚠️ Upload dataset dulu.")
        return

    df = st.session_state["dataset"].copy()
    exclude_cols = ["no","nis","nisn","sakit","izin","alpa","Nama","Kelas","Jurusan"]
    nilai_cols = [c for c in df.select_dtypes(include="number").columns if c.lower() not in exclude_cols]

    if not nilai_cols:
        st.info("Tidak ada kolom nilai numerik.")
        return

    st.markdown("## 📊 Distribusi Nilai")
    st.markdown("---")

    # Dropdown mata pelajaran
    mapel = st.selectbox("Pilih Mata Pelajaran", nilai_cols)

    nilai_mapel = df[[mapel]].rename(columns={mapel: "Nilai"})

    # Histogram
    hist = alt.Chart(nilai_mapel).mark_bar(color="crimson", opacity=0.6).encode(
        x=alt.X("Nilai:Q", bin=alt.Bin(maxbins=30), title="Nilai"),
        y=alt.Y("count()", title="Frekuensi"),
    )

    # Density line
    density = alt.Chart(nilai_mapel).transform_density(
        "Nilai", as_=["Nilai", "density"]
    ).mark_line(color="black").encode(
        x="Nilai:Q",
        y="density:Q",
    )

    # Tambahkan nama mata pelajaran pada judul
    chart = (hist + density).properties(
        title=f"Distribusi Nilai – {mapel}",
        height=350
    )
    st.altair_chart(chart, use_container_width=True)
