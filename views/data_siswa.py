# views/data_siswa.py
import streamlit as st
import pandas as pd
from io import BytesIO

def show():
    st.title("👨‍🎓 Data Siswa")

    if "dataset" not in st.session_state or st.session_state["dataset"] is None:
        st.warning("⚠️ Upload dataset dulu di sidebar.")
        return

    df = st.session_state["dataset"].copy()  # ambil dari upload, bukan DB

    # Tentukan kolom NIS/Nama
    nis_col = next((c for c in df.columns if c.lower() == "nis"), None)
    nama_col = next((c for c in df.columns if c.lower() == "nama"), None)
    if not nis_col or not nama_col:
        st.error("❌ Dataset harus memiliki kolom 'NIS' dan 'Nama'.")
        return

    # Editable table
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )

    # Update session state
    st.session_state["dataset"] = edited_df

    # Download Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        edited_df.to_excel(writer, index=False, sheet_name="DataSiswa")
    excel_data = output.getvalue()

    st.download_button(
        "📥 Download Excel",
        data=excel_data,
        file_name="data_siswa.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
