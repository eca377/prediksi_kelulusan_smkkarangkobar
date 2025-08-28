import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import os

# ===========================
# Fungsi generate PDF
# ===========================
def generate_pdf(dataframe, filename="rapor_siswa.pdf"):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 14)

    # Judul ambil dari nama file
    kelas = os.path.splitext(os.path.basename(filename))[0]
    pdf.cell(0, 10, f"RAPOR SISWA - {kelas}", 0, 1, "C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 9)

    headers = list(dataframe.columns)
    n_cols = len(headers)

    # Total lebar halaman A4 landscape = 297mm, margin kiri-kanan 15mm → 267mm untuk tabel
    total_width = 267

    # Hitung lebar kolom proporsional sesuai panjang teks
    text_lengths = [max([len(str(x)) for x in dataframe[h]] + [len(h)]) for h in headers]
    sum_len = sum(text_lengths)
    col_widths = [max(20, min(total_width * l / sum_len, 50)) for l in text_lengths]

    # Header tabel
    pdf.set_font("Arial", "B", 9)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 8, str(h), 1, 0, "C")
    pdf.ln()

    # Isi tabel
    pdf.set_font("Arial", "", 8)
    for _, row in dataframe.iterrows():
        max_lines = 1
        cell_texts = []
        for i, h in enumerate(headers):
            text = str(row[h])
            # hitung baris multi-cell jika teks panjang
            lines = pdf.multi_cell(col_widths[i], 6, text, border=0, split_only=True)
            max_lines = max(max_lines, len(lines))
            cell_texts.append(text)

        # tulis row
        for line_idx in range(max_lines):
            for i, text in enumerate(cell_texts):
                pdf.multi_cell(
                    col_widths[i],
                    6,
                    text if line_idx == 0 else "",
                    border=1,
                    align="C",
                    ln=3 if i == n_cols - 1 else 0
                )
            pdf.ln()

    # Output PDF ke BytesIO
    pdf_bytes = pdf.output(dest="S")
    pdf_output = BytesIO(pdf_bytes)
    return pdf_output

# ===========================
# Main view
# ===========================
def show():
    st.title("📑 Rapor Siswa")

    if "dataset" not in st.session_state or st.session_state["dataset"] is None:
        st.warning("⚠️ Upload dataset dulu di sidebar untuk menampilkan rapor.")
        return

    df = st.session_state["dataset"].copy()

    # Hapus duplikat kolom
    df = df.loc[:, ~df.columns.duplicated()]

    # Tentukan kolom nilai mapel
    exclude_cols = ["no", "nisn", "sakit", "izin", "alpa"]
    nilai_cols = [c for c in df.select_dtypes(include="number").columns if c.lower() not in exclude_cols]

    # Tambah rata-rata
    if "Rata-rata" not in df.columns and nilai_cols:
        df["Rata-rata"] = df[nilai_cols].mean(axis=1)

    # Kolom ditampilkan
    display_cols = []
    if "NIS" in df.columns:
        display_cols.append("NIS")
    if "Nama" in df.columns:
        display_cols.append("Nama")
    display_cols += nilai_cols
    if "Rata-rata" in df.columns:
        display_cols.append("Rata-rata")

    if not display_cols:
        st.warning("⚠️ Tidak ada kolom yang bisa ditampilkan.")
        return

    # Buat DataFrame baru & hapus kolom duplikat biar rapi
    display_df = df.loc[:, display_cols].copy()
    display_df = display_df.loc[:, ~display_df.columns.duplicated()]

    # Tampilkan tabel editable
    st.subheader("📋 Tabel Rapor Siswa")
    edited_df = st.data_editor(display_df, num_rows="dynamic", use_container_width=True)

    # Tombol simpan perubahan
    if st.button("💾 Simpan Perubahan"):
        st.session_state["dataset"][display_df.columns] = edited_df
        st.success("✅ Perubahan disimpan.")

    st.markdown("---")
    st.subheader("⬇️ Download PDF Rapor")

    # Nama file sesuai kelas
    filename = st.session_state.get("dataset_filename", "rapor_siswa.csv")
    pdf_data = generate_pdf(edited_df, filename)

    st.download_button(
        label="📥 Download PDF",
        data=pdf_data,
        file_name=f"Rapor_{os.path.splitext(os.path.basename(filename))[0]}.pdf",
        mime="application/pdf"
    )
