import streamlit as st
import pandas as pd

# ----------------------------------
# KONFIGURASI DASAR
# ----------------------------------
st.set_page_config(page_title="COOK LMS", layout="wide")

# Inisialisasi session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = ""
if "username" not in st.session_state:
    st.session_state.username = ""
if "users" not in st.session_state:
    # Akun default
    st.session_state.users = {
        "guru": {"guru123": "Guru Default"},
        "siswa": {"siswa123": "Siswa Default"}
    }

# ----------------------------------
# FUNGSI LOGIN / REGISTER
# ----------------------------------
def login():
    st.title("🔐 COOK LMS Login")

    tab1, tab2 = st.tabs(["🔑 Masuk", "🆕 Buat Akun"])

    # ------------------ LOGIN ------------------
    with tab1:
        role = st.selectbox("Masuk sebagai:", ["Pilih akun", "Guru", "Siswa"])
        username = st.text_input("Nama pengguna")
        password = st.text_input("Kata sandi", type="password")

        if st.button("Masuk"):
            if role == "Pilih akun":
                st.warning("Pilih jenis akun terlebih dahulu.")
            elif username == "" or password == "":
                st.warning("Masukkan username dan password.")
            else:
                # Cek akun di session_state
                if role.lower() in st.session_state.users and password in st.session_state.users[role.lower()]:
                    st.session_state.logged_in = True
                    st.session_state.role = role.lower()
                    st.session_state.username = st.session_state.users[role.lower()][password]
                    st.success(f"Selamat datang, {st.session_state.username} ({role})!")
                    st.rerun()
                else:
                    st.error("Username atau password salah.")

    # ------------------ REGISTER ------------------
    with tab2:
        role_reg = st.selectbox("Daftar sebagai:", ["Guru", "Siswa"], key="reg_role")
        nama_reg = st.text_input("Nama Lengkap", key="reg_name")
        pass_reg = st.text_input("Buat Kata Sandi", type="password", key="reg_pass")

        if st.button("Daftar"):
            if nama_reg == "" or pass_reg == "":
                st.warning("Isi semua kolom terlebih dahulu.")
            else:
                # Simpan akun baru
                if pass_reg in st.session_state.users[role_reg.lower()]:
                    st.error("Kata sandi ini sudah digunakan, buat yang lain.")
                else:
                    st.session_state.users[role_reg.lower()][pass_reg] = nama_reg
                    st.success(f"Akun {role_reg} berhasil dibuat! Silakan login.")
                    st.info(f"Gunakan kata sandi: **{pass_reg}** untuk login.")
                    st.rerun()

# ----------------------------------
# HALAMAN UTAMA LMS
# ----------------------------------
def main_app():
    st.sidebar.title("📚 Navigasi LMS")

    if st.session_state.role:
        st.sidebar.write(f"👋 Hai, **{st.session_state.username}** ({st.session_state.role.capitalize()})")
    else:
        st.sidebar.write("👋 Hai, pengguna!")

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

    # -------------------------------------------------
    # DASHBOARD
    # -------------------------------------------------
    if menu == "🏠 Dashboard":
        st.title("COOK LMS")
        st.write("Selamat datang di COOK LMS! 👋")

        if st.session_state.role == "guru":
            st.subheader("👩‍🏫 Student Progress")
            data_progress = pd.DataFrame({
                "Nama Siswa": ["Andi", "Budi", "Citra", "Dina"],
                "Kelas": ["Fisika XII"] * 4,
                "Progress Materi (%)": [80, 60, 90, 70],
                "Tugas Selesai": [3, 2, 4, 3],
                "Absen (%)": [100, 80, 90, 85]
            })
            st.dataframe(data_progress, use_container_width=True)
            st.success("📊 Berikut perkembangan siswa di kelas Anda.")

        elif st.session_state.role == "siswa":
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

    # -------------------------------------------------
    # FITUR LAIN
    # -------------------------------------------------
    elif menu == "👥 Kelas":
        st.title("Kelas")
        st.info("Daftar kelas dan jadwal perkuliahan.")

    elif menu == "📖 Materi":
        st.title("Materi Pembelajaran")
        st.info("Materi kuliah yang dapat diakses mahasiswa.")

    elif menu == "🧠 Pre-Test":
        st.title("Pre-Test")
        st.info("Kerjakan pre-test untuk mengukur pemahaman awal.")

    elif menu == "📝 Tugas":
        st.title("Tugas")
        st.info("Kumpulkan tugas sesuai instruksi dosen.")

    elif menu == "📄 LKPD":
        st.title("LKPD (Lembar Kerja Peserta Didik)")
        st.info("Kerjakan LKPD untuk memperdalam pemahaman.")

    elif menu == "📅 Absensi":
        st.title("Absensi")
        st.info("Isi daftar hadir perkuliahan.")

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.role = ""
        st.session_state.username = ""
        st.warning("Anda telah keluar dari sistem.")
        st.rerun()

    st.markdown("---")
    st.caption("COOK LMS | © 2025 Universitas Sriwijaya")

# ----------------------------------
# MAIN CONTROL FLOW
# ----------------------------------
if not st.session_state.logged_in:
    login()
else:
    main_app()

