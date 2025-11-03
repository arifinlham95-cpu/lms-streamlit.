import streamlit as st

# Judul utama aplikasi
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

# Tampilan halaman
if menu == "🏠 Dashboard":
    st.title("COOK LMS")
    st.write("Selamat datang di COOK LMS!")

elif menu == "👥 Kelas":
    st.title("Kelas")
    st.info("Daftar kelas dan jadwal perkuliahan.")
    # --- Panggil kode lama fitur Kelas di sini ---
    # contoh:
    # tampilkan_kelas()

elif menu == "📖 Materi":
    st.title("Materi Pembelajaran")
    st.info("Materi kuliah yang dapat diakses mahasiswa.")
    # --- Panggil kode lama fitur Materi di sini ---
    # contoh:
    # tampilkan_materi()

elif menu == "🧠 Pre-Test":
    st.title("Pre-Test")
    st.info("Kerjakan pre-test untuk mengukur pemahaman awal.")
    # --- Panggil kode lama fitur Pre-Test di sini ---

elif menu == "📝 Tugas":
    st.title("Tugas")
    st.info("Kumpulkan tugas sesuai instruksi dosen.")
    # --- Panggil kode lama fitur Tugas di sini ---

elif menu == "📄 LKPD":
    st.title("LKPD (Lembar Kerja Peserta Didik)")
    st.info("Kerjakan LKPD untuk memperdalam pemahaman.")
    # --- Panggil kode lama fitur LKPD di sini ---

elif menu == "📅 Absensi":
    st.title("Absensi")
    st.info("Isi daftar hadir perkuliahan.")
    # --- Panggil kode lama fitur Absensi di sini ---

elif menu == "🚪 Logout":
    st.warning("Anda telah keluar dari sistem.")
    # --- Kode logout lama tetap dipakai di sini ---

# (opsional) footer
st.markdown("---")
st.caption("COOK | © 2025 Universitas Sriwijaya")

