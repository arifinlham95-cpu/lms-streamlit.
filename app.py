import streamlit as st
import pandas as pd
import datetime

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
    st.session_state.users = {
        "guru": {"guru123": "Guru Default"},
        "siswa": {"siswa123": "Siswa Default"}
    }
if "kelas_data" not in st.session_state:
    st.session_state.kelas_data = {}
if "test_data" not in st.session_state:
    st.session_state.test_data = {}
if "tugas_data" not in st.session_state:
    st.session_state.tugas_data = {}
if "chat_data" not in st.session_state:
    st.session_state.chat_data = {}
if "absen_data" not in st.session_state:
    st.session_state.absen_data = {}

# ----------------------------------
# FUNGSI LOGIN / REGISTER
# ----------------------------------
def login():
    st.title("🔐 COOK LMS Login")

    tab1, tab2 = st.tabs(["🔑 Masuk", "🆕 Buat Akun"])

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
                if role.lower() in st.session_state.users and password in st.session_state.users[role.lower()]:
                    st.session_state.logged_in = True
                    st.session_state.role = role.lower()
                    st.session_state.username = st.session_state.users[role.lower()][password]
                    st.success(f"Selamat datang, {st.session_state.username} ({role})!")
                    st.rerun()
                else:
                    st.error("Username atau password salah.")

    with tab2:
        role_reg = st.selectbox("Daftar sebagai:", ["Guru", "Siswa"], key="reg_role")
        nama_reg = st.text_input("Nama Lengkap", key="reg_name")
        pass_reg = st.text_input("Buat Kata Sandi", type="password", key="reg_pass")

        if st.button("Daftar"):
            if nama_reg == "" or pass_reg == "":
                st.warning("Isi semua kolom terlebih dahulu.")
            else:
                if pass_reg in st.session_state.users[role_reg.lower()]:
                    st.error("Kata sandi ini sudah digunakan.")
                else:
                    st.session_state.users[role_reg.lower()][pass_reg] = nama_reg
                    st.success(f"Akun {role_reg} berhasil dibuat! Silakan login.")
                    st.info(f"Gunakan kata sandi: **{pass_reg}** untuk login.")
                    st.rerun()

# ----------------------------------
# HALAMAN DASHBOARD
# ----------------------------------
def halaman_dashboard():
    role = st.session_state.role
    st.title("🏠 Dashboard")

    if role == "guru":
        st.subheader("📊 Student Progress")

        if not st.session_state.kelas_data:
            st.info("Belum ada kelas yang dibuat.")
            return

        for kode, kelas in st.session_state.kelas_data.items():
            if kelas["guru"] != st.session_state.username:
                continue

            st.markdown(f"### 📘 {kelas['nama']} ({kode})")

            data_progress = []
            for siswa in kelas["anggota"]:
                # Ambil nilai tes
                nilai_total = []
                for test in st.session_state.test_data.values():
                    if test["guru"] == st.session_state.username and siswa in test["hasil"]:
                        nilai_total.append(test["hasil"][siswa])

                avg_nilai = round(sum(nilai_total) / len(nilai_total), 2) if nilai_total else 0

                # Ambil kehadiran
                hadir_count, total_absen = 0, 0
                for absen in st.session_state.absen_data.values():
                    if absen["guru"] == st.session_state.username and siswa in absen["status"]:
                        total_absen += 1
                        if absen["status"][siswa] == "Hadir":
                            hadir_count += 1
                hadir_rate = f"{(hadir_count / total_absen * 100):.1f}%" if total_absen else "0%"

                data_progress.append({
                    "Nama Siswa": siswa,
                    "Rata-rata Nilai": avg_nilai,
                    "Kehadiran": hadir_rate
                })

            if data_progress:
                df = pd.DataFrame(data_progress)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Belum ada data siswa atau hasil tes.")

    elif role == "siswa":
        st.subheader("🧠 Tes yang Belum Dikerjakan")
        belum_tes = []
        for kode, test in st.session_state.test_data.items():
            if st.session_state.username not in test["hasil"]:
                belum_tes.append(test["judul"])
        if belum_tes:
            st.write("Berikut daftar tes yang belum kamu kerjakan:")
            for t in belum_tes:
                st.write(f"• {t}")
        else:
            st.success("Tidak ada tes yang belum dikerjakan!")

        st.divider()
        st.subheader("📅 Absen yang Belum Diisi")
        belum_absen = []
        today = datetime.date.today()
        for kode, absen in st.session_state.absen_data.items():
            batas = absen["tanggal"] + datetime.timedelta(days=1)
            if today <= batas:
                if st.session_state.username in absen["peserta"] and st.session_state.username not in absen["status"]:
                    belum_absen.append(absen["judul"])
        if belum_absen:
            for a in belum_absen:
                st.write(f"• {a}")
        else:
            st.success("Semua absen sudah diisi!")

# ----------------------------------
# HALAMAN ABSEN
# ----------------------------------
def halaman_absen():
    st.title("📅 Absen")
    role = st.session_state.role

    if role == "guru":
        st.subheader("🆕 Buat Absen Baru")
        judul = st.text_input("Judul Absen")
        kode_absen = st.text_input("Kode Absen (unik)")
        tanggal = datetime.date.today()

        if st.button("📌 Buat Absen"):
            if not judul or not kode_absen:
                st.warning("Isi semua kolom.")
            elif kode_absen in st.session_state.absen_data:
                st.error("Kode absen sudah digunakan.")
            else:
                peserta = []
                for k, v in st.session_state.kelas_data.items():
                    if v["guru"] == st.session_state.username:
                        peserta += v["anggota"]

                st.session_state.absen_data[kode_absen] = {
                    "judul": judul,
                    "guru": st.session_state.username,
                    "tanggal": tanggal,
                    "peserta": list(set(peserta)),
                    "status": {}
                }
                st.success("Absen berhasil dibuat!")

        st.divider()
        st.subheader("📋 Daftar Absen")
        absen_guru = {k: v for k, v in st.session_state.absen_data.items() if v["guru"] == st.session_state.username}
        if not absen_guru:
            st.info("Belum ada absen.")
        else:
            for kode, data in absen_guru.items():
                with st.expander(f"{data['judul']} ({kode}) - {data['tanggal']}"):
                    batas = data["tanggal"] + datetime.timedelta(days=1)
                    st.markdown(f"🕒 Berlaku sampai: {batas}")
                    df = pd.DataFrame(
                        [{"Nama Siswa": s, "Status": data['status'].get(s, "❌ Belum Absen")} for s in data["peserta"]]
                    )
                    st.dataframe(df, use_container_width=True)

    elif role == "siswa":
        st.subheader("📅 Daftar Absen yang Bisa Diisi")
        today = datetime.date.today()
        absen_aktif = {
            k: v for k, v in st.session_state.absen_data.items()
            if st.session_state.username in v["peserta"] and today <= v["tanggal"] + datetime.timedelta(days=1)
        }

        if not absen_aktif:
            st.info("Tidak ada absen aktif.")
            return

        for kode, data in absen_aktif.items():
            with st.expander(f"{data['judul']} ({kode}) - {data['tanggal']}"):
                if st.session_state.username in data["status"]:
                    st.success(f"Anda sudah absen: {data['status'][st.session_state.username]}")
                else:
                    status = st.radio("Pilih Kehadiran:", ["Hadir", "Sakit"], key=f"absen_{kode}")
                    if st.button("Kirim", key=f"kirim_{kode}"):
                        data["status"][st.session_state.username] = status
                        st.success("Absen berhasil dikirim!")
                        st.rerun()

# ----------------------------------
# HALAMAN LAIN (Kelas, Tugas, Test, Chat)
# ----------------------------------
# fungsi halaman_kelas(), halaman_tugas(), halaman_test(), halaman_chat()
# (semua yang sudah kamu punya, tetap sama, tidak diubah)
# ----------------------------------

# MAIN CONTROL
def main_app():
    st.sidebar.title("📚 Navigasi LMS")
    st.sidebar.write(f"👋 Hai, **{st.session_state.username}** ({st.session_state.role.capitalize()})")

    menu = st.sidebar.radio("Pilih Halaman:", [
        "🏠 Dashboard",
        "👥 Kelas",
        "📝 Tugas",
        "🧠 Test",
        "📅 Absen",
        "💬 Room Chat",
        "🚪 Logout"
    ])

    if menu == "🏠 Dashboard":
        halaman_dashboard()
    elif menu == "👥 Kelas":
        halaman_kelas()
    elif menu == "📝 Tugas":
        halaman_tugas()
    elif menu == "🧠 Test":
        halaman_test()
    elif menu == "📅 Absen":
        halaman_absen()
    elif menu == "💬 Room Chat":
        halaman_chat()
    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.role = ""
        st.session_state.username = ""
        st.warning("Anda telah keluar.")
        st.rerun()

    st.markdown("---")
    st.caption("COOK LMS | © 2025 Universitas Sriwijaya")

# ----------------------------------
# MAIN PROGRAM
# ----------------------------------
if not st.session_state.logged_in:
    login()
else:
    main_app()


