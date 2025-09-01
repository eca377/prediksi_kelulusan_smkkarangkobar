# views/prediksi.py
# ==========================================================
# Modul Prediksi Kelulusan Siswa
# Streamlit + Scikit-Learn + Altair + FPDF
# ==========================================================
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
        for _, row in eval_df.iterrows():
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
            page_width = pdf.w - 2 * pdf.l_margin
            col_widths = []
            for c in col_names:
                if c.lower() == "nis":
                    col_widths.append(20)
                elif c.lower() == "nama":
                    col_widths.append(60)
                elif c.lower() == "keterangan":
                    col_widths.append(60)
                else:
                    col_widths.append((page_width - 140) / (len(col_names) - 3))

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


# PDF pribadi siswa
def generate_pdf_siswa(nama, nis, rata2, bonus, status, threshold, alpa=None):
    pdf = FPDF("P", "mm", "A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Hasil Prediksi Kelulusan", ln=1, align="C")
    pdf.ln(8)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Nama : {nama}", ln=1)
    pdf.cell(0, 8, f"NIS  : {nis}", ln=1)
    pdf.cell(0, 8, f"Rata-rata + Bonus : {rata2:.2f}", ln=1)
    pdf.cell(0, 8, f"Bonus Ekstra : {bonus}", ln=1)
    pdf.cell(0, 8, f"Threshold    : {threshold}", ln=1)
    if alpa is not None:
        pdf.cell(0, 8, f"Alpa         : {alpa}", ln=1)
    pdf.ln(4)

    if status == 1:
        pdf.set_text_color(0, 128, 0)
        pdf.cell(0, 10, "🎉 Anda dinyatakan LULUS!", ln=1)
    else:
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 10, "❌ Anda dinyatakan TIDAK LULUS!", ln=1)
        if alpa is not None and alpa > 5:
            pdf.set_text_color(200, 0, 0)
            pdf.cell(0, 10, "⚠️ Catatan: Alpa > 5. Harap menemui Guru BK.", ln=1)
    pdf.set_text_color(0, 0, 0)

    pdf_bytes = bytes(pdf.output(dest="S"))
    return pdf_bytes


# ===================== SHOW FUNCTION =====================
def show(dataset=None, role="admin", nis=None, nama=None):
    st.title("🎯 Prediksi Kelulusan Siswa")

    # Dataset
    if dataset is None:
        if "dataset" not in st.session_state:
            st.error("❌ Dataset belum diupload.")
            return
        df = st.session_state["dataset"].copy()
    else:
        df = dataset.copy()

    # Filter untuk siswa
    if role == "siswa":
        if nis:
            df = df[df["NIS"].astype(str) == str(nis)]
        elif nama:
            df = df[df["Nama"].str.upper() == str(nama).upper()]

        if df.empty:
            st.error("❌ Nama / NIS tidak terdaftar!")
            return
        else:
            st.success(f"✅ Selamat datang, {df.iloc[0]['Nama']}")

    # ===================== Pilih kolom mapel =====================
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
        return 0

    df["Bonus_Ekstra"] = df.apply(bonus_ekstra, axis=1)
    df["Rata-rata_Final"] = df["Rata-rata"] + df["Bonus_Ekstra"]

    # Threshold slider (Admin bisa atur, siswa hanya lihat default)
    if role == "admin":
        threshold = st.slider("🎚️ Threshold Kelulusan", 0, 200, 75)
    else:
        threshold = 75
        st.info(f"🎚️ Threshold Kelulusan: {threshold}")

    df["Target"] = np.where(df["Rata-rata_Final"] >= threshold, 1, 0)
    df["Keterangan"] = ""

    # Override jika alpa > 5
    if "Alpa" in df.columns:
        df.loc[df["Alpa"] > 5, "Target"] = 0
        df.loc[df["Alpa"] > 5, "Keterangan"] = "⚠️ Harap menemui Guru BK"
        df_alpha_warn = df[df["Alpa"] > 5]
        if not df_alpha_warn.empty and "Nama" in df_alpha_warn.columns and role == "siswa":
            st.warning("⚠️ Anda memiliki Alpa > 5. Silahkan hubungi guru BK.")

    # ================= Model Random Forest =================
    X = df[nilai_cols]
    y = df["Target"]

    eval_df = pd.DataFrame()
    if len(y.unique()) > 1 and role == "admin":
        min_count = y.value_counts().min()
        if min_count >= 2:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
            model = RandomForestClassifier(random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            eval_df = pd.DataFrame({
                "Metrik": ["Accuracy", "Precision", "Recall", "F1-Score"],
                "Skor": [
                    accuracy_score(y_test, y_pred),
                    precision_score(y_test, y_pred, zero_division=0),
                    recall_score(y_test, y_pred, zero_division=0),
                    f1_score(y_test, y_pred, zero_division=0)
                ]
            })

            st.subheader("📊 Evaluasi Model (Random Forest)")
            st.dataframe(eval_df, use_container_width=True)
            chart_eval = alt.Chart(eval_df).mark_line(color="red", point=True).encode(
                alt.X("Metrik", title="Metrik"),
                alt.Y("Skor", title="Skor")
            ).properties(width=600, height=300, title="Evaluasi Model - Random Forest")
            st.altair_chart(chart_eval, use_container_width=True)

    # ================= Hasil Prediksi =================
    st.subheader("📋 Hasil Prediksi Kelulusan")
    selected_cols = ["NIS", "Nama", "Rata-rata_Final", "Bonus_Ekstra", "Keterangan"] if "Nama" in df.columns else ["Rata-rata_Final", "Bonus_Ekstra", "Keterangan"]

    lulus = df[df["Target"] == 1][selected_cols]
    tidak_lulus = df[df["Target"] == 0][selected_cols]

    if role == "admin":
        # Ringkasan jumlah
        summary_df = pd.DataFrame({
            "Status": ["Lulus", "Tidak Lulus"],
            "Jumlah": [len(lulus), len(tidak_lulus)]
        })

        # Grafik jumlah kelulusan
        chart_summary = alt.Chart(summary_df).mark_bar().encode(
            alt.X("Status", title="Status"),
            alt.Y("Jumlah", title="Jumlah"),
            color=alt.Color("Status", scale=alt.Scale(range=["green", "red"]))
        ).properties(width=400, height=300, title="Distribusi Kelulusan")
        st.altair_chart(chart_summary, use_container_width=True)

        # Grafik distribusi nilai
        chart_nilai = alt.Chart(df).mark_bar(color="blue").encode(
            alt.X("Rata-rata_Final", bin=alt.Bin(maxbins=20), title="Rata-rata Final"),
            alt.Y("count()", title="Jumlah")
        ).properties(width=600, height=300, title="Distribusi Nilai Rata-rata Final")
        st.altair_chart(chart_nilai, use_container_width=True)

    # Tabel hasil
    if role == "admin":
        st.success("✅ Daftar Siswa Lulus")
        st.dataframe(lulus, use_container_width=True)
        st.error("❌ Daftar Siswa Tidak Lulus")
        st.dataframe(tidak_lulus, use_container_width=True)
    else:
        row = df.iloc[0]
        status = row["Target"]
        if status == 1:
            st.success("🎉 Anda dinyatakan LULUS!")
        else:
            st.error("❌ Anda dinyatakan TIDAK LULUS!")
            if "Alpa" in row and row["Alpa"] > 5:
                st.warning("⚠️ Karena Alpa > 5, harap menemui Guru BK.")

        # Download PDF pribadi
        if st.button("📥 Download Hasil Prediksi Saya (PDF)"):
            pdf_bytes = generate_pdf_siswa(
                row["Nama"], row["NIS"], row["Rata-rata_Final"],
                row["Bonus_Ekstra"], row["Target"], threshold, row.get("Alpa", None)
            )
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=f"Prediksi_{row['Nama']}.pdf",
                mime="application/pdf"
            )

    # Download PDF kelas (Admin)
    if role == "admin":
        kelas_name = st.text_input("Nama Kelas / File", "Kelas")
        if st.button("📥 Download PDF Hasil Prediksi (Semua Siswa)"):
            pdf_bytes = generate_pdf(lulus, tidak_lulus, threshold, eval_df, kelas_name)
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=f"{kelas_name}_Prediksi.pdf",
                mime="application/pdf"
            )
