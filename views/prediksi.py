# views/prediksi.py
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import altair as alt
from fpdf import FPDF

# ===================== PDF GENERATOR =====================
def generate_pdf(lulus, tidak_lulus, threshold, eval_df, kelas_name="Rapor"):
    pdf = FPDF("P", "mm", "A4")
    pdf.add_page()
    pdf.set_font("Arial", "", 12)

    # Header
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, f"Prediksi Kelulusan - {kelas_name}", ln=1, align="C")
    pdf.ln(4)
    pdf.set_font("Arial", "", 12)

    # Threshold
    pdf.cell(0, 8, f"Threshold Kelulusan: {threshold}", ln=1, align="L")
    pdf.ln(4)

    # Evaluasi Model
    if not eval_df.empty:
        pdf.cell(0, 8, "Evaluasi Model", ln=1, align="L")
        for idx, row in eval_df.iterrows():
            pdf.cell(0, 6, f"{row['Metrik']}: {row['Skor']:.2f}", ln=1, align="L")
        pdf.ln(4)

    # Fungsi cetak tabel
    def print_table(df_table, title):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, title, ln=1, align="C")
        pdf.ln(2)
        pdf.set_font("Arial", "", 12)

        if not df_table.empty:
            col_names = df_table.columns.tolist()
            page_width = pdf.w - 2*pdf.l_margin
            col_widths = []
            for c in col_names:
                if c.lower() == "nis":
                    col_widths.append(20)
                elif c.lower() == "nama":
                    col_widths.append(80)
                else:
                    col_widths.append((page_width - 100) / (len(col_names)-2))
            # Header kolom
            for i, h in enumerate(col_names):
                pdf.cell(col_widths[i], 8, str(h), 1, 0, "C")
            pdf.ln()
            # Rows
            for _, r in df_table.iterrows():
                for i, c in enumerate(col_names):
                    pdf.cell(col_widths[i], 8, str(r[c]), 1, 0, "L")
                pdf.ln()
        else:
            pdf.cell(0, 8, "Tidak ada data", ln=1, align="L")
        pdf.ln(4)

    print_table(lulus, "Daftar Siswa Lulus")
    print_table(tidak_lulus, "Daftar Siswa Tidak Lulus")

    pdf_bytes = bytes(pdf.output(dest="S"))
    return pdf_bytes

# ===================== SHOW FUNCTION =====================
def show(dataset=None):
    st.title("🎯 Prediksi Kelulusan Siswa")

    if dataset is None:
        if "dataset" not in st.session_state:
            st.error("❌ Dataset belum diupload.")
            return
        df = st.session_state["dataset"].copy()
    else:
        df = dataset.copy()

    # ===================== Pilih kolom mapel =====================
    # Sesuaikan nama kolom mapel sesuai dataset kamu
    mapel_cols = ["MTK", "BINDO", "BINGGRIS", "IPA", "IPS"]
    nilai_cols = [c for c in mapel_cols if c in df.columns]

    if not nilai_cols:
        st.error("❌ Dataset tidak memiliki kolom mapel yang valid.")
        return

    # Hitung rata-rata hanya dari kolom mapel
    df["Rata-rata"] = df[nilai_cols].mean(axis=1)

    # Bonus ekstra
    def bonus_ekstra(row):
        if "EKSTRA" not in row:
            return 0
        if str(row["EKSTRA"]).upper() == "B":
            return 65
        elif str(row["EKSTRA"]).upper() == "SB":
            return 70
        else:
            return 0
    df["Bonus_Ekstra"] = df.apply(bonus_ekstra, axis=1)
    df["Rata-rata_Final"] = df["Rata-rata"] + df["Bonus_Ekstra"]

    threshold = st.slider("🎚️ Threshold Kelulusan", 0, 200, 75)
    df["Target"] = np.where(df["Rata-rata_Final"] >= threshold, 1, 0)

    # Override jika alpa > 7
    if "Alpa" in df.columns:
        df.loc[df["Alpa"] > 7, "Target"] = 0
        df_alpha_warn = df[df["Alpa"] > 7]
        if not df_alpha_warn.empty and "Nama" in df_alpha_warn.columns:
            for nama in df_alpha_warn["Nama"]:
                st.warning(f"⚠️ {nama} memiliki alpha > 7. Silahkan hubungi guru BK.")

    # ================= Model Random Forest =================
    X = df[nilai_cols]
    y = df["Target"]

    eval_df = pd.DataFrame()
    if len(y.unique()) > 1:
        min_count = y.value_counts().min()
        if min_count < 2:
            st.warning("⚠️ Tidak cukup data untuk evaluasi model (kelas terlalu sedikit). Hanya menampilkan prediksi tanpa evaluasi.")
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
            model = RandomForestClassifier(random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, zero_division=0)
            rec = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)

            eval_df = pd.DataFrame({
                "Metrik": ["Accuracy","Precision","Recall","F1-Score"],
                "Skor": [acc, prec, rec, f1]
            })

            st.subheader("📊 Evaluasi Model (Random Forest)")
            st.dataframe(eval_df, use_container_width=True)
            chart_eval = alt.Chart(eval_df).mark_line(color="red", point=True).encode(
                x="Metrik",
                y="Skor"
            ).properties(width=600, height=300, title="Evaluasi Model - Random Forest")
            st.altair_chart(chart_eval, use_container_width=True)

    # ================= Hasil Prediksi =================
    st.subheader("📋 Hasil Prediksi Kelulusan")
    lulus = df[df["Target"] == 1][["NIS","Nama","Rata-rata_Final","Bonus_Ekstra"]] if "Nama" in df.columns else df[df["Target"] == 1][["Rata-rata_Final","Bonus_Ekstra"]]
    tidak_lulus = df[df["Target"] == 0][["NIS","Nama","Rata-rata_Final","Bonus_Ekstra"]] if "Nama" in df.columns else df[df["Target"] == 0][["Rata-rata_Final","Bonus_Ekstra"]]

    # Ringkasan jumlah
    summary_df = pd.DataFrame({
        "Status": ["Lulus", "Tidak Lulus"],
        "Jumlah": [len(lulus), len(tidak_lulus)]
    })

    # Grafik jumlah kelulusan
    chart_summary = alt.Chart(summary_df).mark_bar().encode(
        x="Status",
        y="Jumlah",
        color=alt.Color("Status", scale=alt.Scale(range=["green","red"]))
    ).properties(width=400, height=300, title="Distribusi Kelulusan")
    st.altair_chart(chart_summary, use_container_width=True)

    # Grafik distribusi nilai
    chart_nilai = alt.Chart(df).mark_bar(color="blue").encode(
        alt.X("Rata-rata_Final", bin=alt.Bin(maxbins=20), title="Rata-rata Final"),
        y='count()'
    ).properties(width=600, height=300, title="Distribusi Nilai Rata-rata Final")
    st.altair_chart(chart_nilai, use_container_width=True)

    # Tabel hasil
    st.success("✅ Daftar Siswa Lulus")
    st.dataframe(lulus, use_container_width=True)
    st.error("❌ Daftar Siswa Tidak Lulus")
    st.dataframe(tidak_lulus, use_container_width=True)

    kelas_name = st.text_input("Nama Kelas / File", "Kelas")
    if st.button("📥 Download PDF Hasil Prediksi"):
        pdf_bytes = generate_pdf(lulus, tidak_lulus, threshold, eval_df, kelas_name)
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=f"{kelas_name}_Prediksi.pdf",
            mime="application/pdf"
        )
