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
    # Akun default
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
# HALAMAN ABSEN
# ----------------------------------
def halaman_absen():
    st.title("📅 Absensi")
    role = st.session_state.role

    # Guru membuat absen
    if role == "guru":
        st.subheader("🗓️ Buat Jadwal Absen")
        kode_kelas = st.selectbox("Pilih Kelas", list(st.session_state.kelas_data.keys()))
        tanggal = st.date_input("Tanggal Absen", datetime.date.today())
        if st.button("📤 Buat Absen"):
            if not kode_kelas:
                st.warning("Pilih kelas terlebih dahulu.")
            else:
                batas = tanggal + datetime.timedelta(days=1)
                if kode_kelas not in st.session_state.absen_data:
                    st.session_state.absen_data[kode_kelas] = {}
                st.session_state.absen_data[kode_kelas][str(tanggal)] = {
                    "batas": batas,
                    "kehadiran": {}
                }
                st.success(f"Absen untuk {tanggal} berhasil dibuat, berlaku hingga {batas}.")
                st.rerun()

        st.divider()
        st.subheader("📋 Daftar Absen")
        for kode, absen_kelas in st.session_state.absen_data.items():
            st.markdown(f"### 📘 {st.session_state.kelas_data[kode]['nama']}")
            for tgl, data in absen_kelas.items():
                st.write(f"📅 **{tgl}** (Batas: {data['batas']})")
                if data["kehadiran"]:
                    df = pd.DataFrame([
                        {"Nama Siswa": s, "Status": v} for s, v in data["kehadiran"].items()
                    ])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Belum ada siswa yang mengisi absen.")

    # Siswa mengisi absen
    elif role == "siswa":
        st.subheader("🗓️ Absen Hari Ini")
        kelas_saya = {k: v for k, v in st.session_state.kelas_data.items() if st.session_state.username in v["anggota"]}
        if not kelas_saya:
            st.info("Belum tergabung di kelas mana pun.")
        else:
            today = datetime.date.today()
            for kode, data in kelas_saya.items():
                if kode in st.session_state.absen_data and str(today) in st.session_state.absen_data[kode]:
                    absen = st.session_state.absen_data[kode][str(today)]
                    batas = absen["batas"]
                    if datetime.datetime.now().date() <= batas:
                        st.markdown(f"### {data['nama']} - {today}")
                        if st.session_state.username in absen["kehadiran"]:
                            st.success(f"Anda sudah absen: {absen['kehadiran'][st.session_state.username]}")
                        else:
                            status = st.radio("Pilih status:", ["Hadir", "Sakit"])
                            if st.button("Kirim Absen", key=f"absen_{kode}"):
                                absen["kehadiran"][st.session_state.username] = status
                                st.success("Absen berhasil dikirim.")
                                st.rerun()
                    else:
                        if st.session_state.username not in absen["kehadiran"]:
                            absen["kehadiran"][st.session_state.username] = "Tidak Hadir"

# ----------------------------------
# HALAMAN KELAS
# ----------------------------------
def halaman_kelas():
    st.title("👥 Kelas dan Materi")
    role = st.session_state.role
    # (kode halaman kelas tetap sama seperti sebelumnya)
    # Potongan fungsi di sini tidak diubah dari kode asli kamu
    # .........................................................

# ----------------------------------
# HALAMAN TUGAS
# ----------------------------------
def halaman_tugas():
    st.title("📝 Tugas")
    role = st.session_state.role
    # (fungsi sama seperti di kode asli)
    # .........................................................

# ----------------------------------
# HALAMAN CHAT
# ----------------------------------
def halaman_chat():
    st.title("💬 Room Chat")
    role = st.session_state.role
    # (fungsi sama seperti di kode asli)
    # .........................................................

# ----------------------------------
# HALAMAN TEST
# ----------------------------------
def halaman_test():
    st.title("🧠 Test (Ujian)")
    role = st.session_state.role
    # (fungsi sama seperti di kode asli)
    # .........................................................

# ----------------------------------
# DASHBOARD
# ----------------------------------
def halaman_dashboard():
    role = st.session_state.role
    st.title("🏠 Dashboard")

    if role == "guru":
        st.subheader("📊 Progress Siswa per Kelas")
        for kode, data in st.session_state.kelas_data.items():
            if data["guru"] == st.session_state.username:
                st.markdown(f"### 📘 {data['nama']}")
                df_progress = []
                for siswa in data["anggota"]:
                    nilai_test = []
                    for t_kode, t_data in st.session_state.test_data.items():
                        if siswa in t_data.get("hasil", {}):
                            nilai_test.append(t_data["hasil"][siswa])
                    rata_test = sum(nilai_test)/len(nilai_test) if nilai_test else 0
                    df_progress.append({
                        "Nama Siswa": siswa,
                        "Jumlah Test": len(nilai_test),
                        "Rata-rata Nilai": round(rata_test, 2)
                    })
                if df_progress:
                    st.dataframe(pd.DataFrame(df_progress), use_container_width=True)
                else:
                    st.info("Belum ada data siswa atau nilai.")

    elif role == "siswa":
        st.subheader("🧠 Tes yang Belum Dikerjakan")
        belum_test = []
        for kode, data in st.session_state.test_data.items():
            if st.session_state.username not in data.get("hasil", {}):
                belum_test.append(data["judul"])
        if belum_test:
            for t in belum_test:
                st.write(f"📄 {t}")
        else:
            st.success("Semua tes sudah dikerjakan.")

        st.divider()
        st.subheader("📅 Absen yang Belum Diisi")
        today = datetime.date.today()
        for kode, data in st.session_state.kelas_data.items():
            if st.session_state.username in data["anggota"]:
                if kode in st.session_state.absen_data and str(today) in st.session_state.absen_data[kode]:
                    absen = st.session_state.absen_data[kode][str(today)]
                    if st.session_state.username not in absen["kehadiran"]:
                        st.warning(f"Belum absen di kelas {data['nama']}")
                else:
                    st.info(f"Tidak ada jadwal absen hari ini di kelas {data['nama']}.")

# ----------------------------------
# MAIN CONTROL
# ----------------------------------
def main_app():
    st.sidebar.title("📚 Navigasi LMS")
    st.sidebar.write(f"👋 Hai, **{st.session_state.username}** ({st.session_state.role.capitalize()})")

    menu = st.sidebar.radio("Pilih Halaman:", [
        "🏠 Dashboard",
        "👥 Kelas",
        "📝 Tugas",
        "🧠 Test",
        "📅 Absensi",
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
    elif menu == "📅 Absensi":
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
