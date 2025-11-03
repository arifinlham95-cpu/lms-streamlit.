import streamlit as st
import pandas as pd

# ---- Konfigurasi dasar ----
st.set_page_config(page_title="COOK LMS", layout="wide")

st.sidebar.title("📚 Navigasi LMS")
menu = st.sidebar.radio("Pilih Halaman:", [
    "🏠 Dashboard",
    "👥 Kelas",
    "📖 Materi",
    "🧠 Pre-Test",
    "📝 Tugas",
    "📄 LKPD",
    "📅 Absensi",
    "🚪 Logout"
])

# ---- Simulasi role login ----
# (Nanti bisa diganti dengan data login sebenarnya)
role = st.session_state.get("role", "guru")  # "guru" atau "siswa"

# ---- Tampilan halaman ----
if menu == "🏠 Dashboard":
    st.title("COOK LMS")
    st.write("Selamat datang di COOK LMS! 👋")

    # ----------------------------------------
    # DASHBOARD GURU
    # ----------------------------------------
    if role == "guru":
        st.subheader("👩‍🏫 Student Progress")

        # Contoh data progress (bisa diganti dengan data asli dari database)
        data_progress = pd.DataFrame({
            "Nama Siswa": ["Andi", "Citra"],
            "Kelas": ["Fisika XII"]*4,
            "Progress Materi (%)": [80, 60],
            "Tugas Selesai": [3, 2],
            "Absen (%)": [100, 80]
        })

        st.dataframe(data_progress, use_container_width=True)
        st.success("📊 Berikut perkembangan siswa di kelas Anda.")

    # ----------------------------------------
    # DASHBOARD SISWA
    # ----------------------------------------
    elif role == "siswa":
        st.subheader("📋 Tugas dan Absensi yang Belum Dikerjakan")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📝 Tugas Belum Dikerjakan")
            tugas_belum = pd.DataFrame({
                "Judul Tugas": ["Tugas 1 - Gelombang", "Tugas 2 - Interferensi"],
                "Deadline": ["10 Nov 2025", "15 Nov 2025"]
            })
            st.table(tugas_belum)
            st.info("Segera kerjakan tugas di menu *Tugas*!")

        with col2:
            st.markdown("### 📅 Absensi Belum Diisi")
            absen_belum = pd.DataFrame({
                "Tanggal": ["01 Nov 2025", "03 Nov 2025"],
                "Kelas": ["Fisika 1", "Fisika 1"]
            })
            st.table(absen_belum)
            st.warning("Jangan lupa isi absensi di menu *Absensi*!")

# ---- Halaman lainnya tetap sama ----
elif menu == "👥 Kelas":
    st.title("Kelas")
    st.info("Daftar kelas dan jadwal perkuliahan.")
    # tampilkan_kelas()

elif menu == "📖 Materi":
    st.title("Materi Pembelajaran")
    st.info("Materi kuliah yang dapat diakses mahasiswa.")
    # tampilkan_materi()

elif menu == "🧠 Pre-Test":
    st.title("Pre-Test")
    st.info("Kerjakan pre-test untuk mengukur pemahaman awal.")
    # tampilkan_pretest()

elif menu == "📝 Tugas":
    st.title("Tugas")
    st.info("Kumpulkan tugas sesuai instruksi dosen.")
    # tampilkan_tugas()

elif menu == "📄 LKPD":
    st.title("LKPD (Lembar Kerja Peserta Didik)")
    st.info("Kerjakan LKPD untuk memperdalam pemahaman.")
    # tampilkan_lkpd()

elif menu == "📅 Absensi":
    st.title("Absensi")
    st.info("Isi daftar hadir perkuliahan.")
    # tampilkan_absensi()

elif menu == "🚪 Logout":
    st.warning("Anda telah keluar dari sistem.")
    # logout_function()

# ---- Footer ----
st.markdown("---")
st.caption("COOK LMS | © 2025 Universitas Sriwijaya")



