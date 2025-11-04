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
    st.title("📅 Absen")
    role = st.session_state.role

    # Guru
    if role == "guru":
        st.subheader("🧾 Buat Jadwal Absen")
        kode_kelas = st.selectbox("Pilih Kelas", list(st.session_state.kelas_data.keys()))
        tanggal_absen = st.date_input("Tanggal Absen", datetime.date.today())
        if st.button("Buat Absen"):
            if kode_kelas not in st.session_state.absen_data:
                st.session_state.absen_data[kode_kelas] = {}
            if str(tanggal_absen) in st.session_state.absen_data[kode_kelas]:
                st.warning("Absen untuk tanggal ini sudah ada.")
            else:
                batas = datetime.datetime.now() + datetime.timedelta(days=1)
                st.session_state.absen_data[kode_kelas][str(tanggal_absen)] = {
                    "batas": batas,
                    "data": {}
                }
                st.success(f"Absen tanggal {tanggal_absen} berhasil dibuat! Berlaku hingga {batas.strftime('%H:%M %d-%m-%Y')}")

        st.divider()
        st.subheader("📋 Rekap Absen")
        for kode, daftar in st.session_state.absen_data.items():
            st.markdown(f"### 📘 {st.session_state.kelas_data[kode]['nama']}")
            for tanggal, data in daftar.items():
                st.write(f"📅 **{tanggal}** (batas: {data['batas'].strftime('%d-%m-%Y %H:%M')})")
                if data["data"]:
                    df = pd.DataFrame([{"Nama": s, "Status": stt} for s, stt in data["data"].items()])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Belum ada siswa yang mengisi absen.")

    # Siswa
    elif role == "siswa":
        st.subheader("📘 Daftar Absen yang Tersedia")
        kelas_saya = {k: v for k, v in st.session_state.kelas_data.items() if st.session_state.username in v["anggota"]}

        if not kelas_saya:
            st.info("Belum tergabung di kelas mana pun.")
        else:
            for kode, data in kelas_saya.items():
                if kode not in st.session_state.absen_data:
                    continue
                with st.expander(f"Absen - {data['nama']}"):
                    for tanggal, absen in st.session_state.absen_data[kode].items():
                        now = datetime.datetime.now()
                        if now > absen["batas"]:
                            if st.session_state.username not in absen["data"]:
                                absen["data"][st.session_state.username] = "Tidak Hadir"
                        status = absen["data"].get(st.session_state.username, "Belum Absen")
                        st.write(f"📅 {tanggal} - Status: **{status}**")
                        if status == "Belum Absen":
                            opsi = st.radio("Pilih kehadiran:", ["Hadir", "Sakit"], key=f"opsi_{kode}_{tanggal}")
                            if st.button("Kirim Absen", key=f"kirim_{kode}_{tanggal}"):
                                absen["data"][st.session_state.username] = opsi
                                st.success("Absen berhasil disimpan!")
                                st.rerun()

# ----------------------------------
# HALAMAN DASHBOARD
# ----------------------------------
def halaman_dashboard():
    st.title("🏠 Dashboard COOK LMS")
    role = st.session_state.role

    if role == "guru":
        st.subheader("📊 Student Progress per Kelas")
        if not st.session_state.kelas_data:
            st.info("Belum ada kelas yang dibuat.")
        else:
            for kode, data in st.session_state.kelas_data.items():
                if data["guru"] != st.session_state.username:
                    continue
                with st.expander(f"{data['nama']} ({kode})"):
                    siswa = data["anggota"]
                    if not siswa:
                        st.warning("Belum ada siswa di kelas ini.")
                    else:
                        df_list = []
                        for s in siswa:
                            nilai_test = []
                            for test_kode, tdata in st.session_state.test_data.items():
                                if s in tdata.get("hasil", {}):
                                    nilai_test.append(tdata["hasil"][s])
                            rata = round(sum(nilai_test)/len(nilai_test), 2) if nilai_test else 0
                            df_list.append({"Nama Siswa": s, "Rata-rata Nilai Test": rata})
                        df = pd.DataFrame(df_list)
                        st.dataframe(df, use_container_width=True)

    elif role == "siswa":
        st.subheader("🧠 Tes dan Absen yang Belum Dikerjakan")
        pending_test = []
        for kode, t in st.session_state.test_data.items():
            if st.session_state.username not in t.get("hasil", {}):
                pending_test.append(t["judul"])
        if pending_test:
            st.markdown("### 📋 Test yang Belum Dikerjakan")
            for t in pending_test:
                st.write(f"🔸 {t}")
        else:
            st.success("Tidak ada test tertunda 🎉")

        st.divider()
        pending_absen = []
        for kode, daftar in st.session_state.absen_data.items():
            for tanggal, data in daftar.items():
                batas = data["batas"]
                if datetime.datetime.now() <= batas and st.session_state.username not in data["data"]:
                    pending_absen.append(f"{st.session_state.kelas_data[kode]['nama']} - {tanggal}")
        if pending_absen:
            st.markdown("### 📅 Absen yang Belum Diisi")
            for a in pending_absen:
                st.write(f"🔸 {a}")
        else:
            st.success("Semua absen sudah terisi 🎉")

# ----------------------------------
# HALAMAN LAIN (kelas, tugas, test, chat)
# ----------------------------------
def halaman_kelas():
    # isi sama seperti sebelumnya
    # (gunakan kode halaman_kelas dari versi terakhir kamu)
    st.info("Fitur kelas tetap seperti sebelumnya.")

def halaman_tugas():
    st.info("Fitur tugas tetap seperti sebelumnya.")

def halaman_test():
    st.info("Fitur test tetap seperti sebelumnya.")

def halaman_chat():
    st.info("Fitur chat tetap seperti sebelumnya.")

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
        "💬 Room Chat",
        "📅 Absen",
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
    elif menu == "💬 Room Chat":
        halaman_chat()
    elif menu == "📅 Absen":
        halaman_absen()
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
