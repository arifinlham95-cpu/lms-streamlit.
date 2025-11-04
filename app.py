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
    st.title("🏠 Dashboard COOK LMS")

    role = st.session_state.role

    if role == "guru":
        st.subheader("📊 Student Progress")
        kelas_guru = {k: v for k, v in st.session_state.kelas_data.items() if v["guru"] == st.session_state.username}

        if not kelas_guru:
            st.info("Belum ada kelas yang Anda buat.")
        else:
            for kode, kelas in kelas_guru.items():
                st.markdown(f"### 🏫 {kelas['nama']} ({kode})")
                jumlah_siswa = len(kelas["anggota"])
                st.write(f"👨‍🎓 Jumlah siswa: {jumlah_siswa}")

                # Ambil test yang terkait dengan guru ini
                test_guru = {k: v for k, v in st.session_state.test_data.items() if v["guru"] == st.session_state.username}
                nilai_list = []
                for t in test_guru.values():
                    nilai_list.extend(list(t["hasil"].values()))

                if nilai_list:
                    rata2 = round(sum(nilai_list) / len(nilai_list), 2)
                    st.success(f"📈 Rata-rata nilai siswa: {rata2}")
                else:
                    st.warning("Belum ada data test yang dikerjakan siswa.")

    elif role == "siswa":
        st.subheader("📅 Aktivitas yang Belum Selesai")

        # Test yang belum dikerjakan
        belum_test = []
        for kode, data in st.session_state.test_data.items():
            if st.session_state.username not in data["hasil"]:
                belum_test.append(data["judul"])

        # Absen yang belum diisi
        belum_absen = []
        for kode, absen in st.session_state.absen_data.items():
            batas = absen["tanggal"] + datetime.timedelta(days=1)
            if datetime.datetime.now() < batas:
                if st.session_state.username not in absen["kehadiran"]:
                    belum_absen.append(absen["judul"])

        st.markdown("### 🧠 Test yang Belum Dikerjakan")
        if belum_test:
            for t in belum_test:
                st.warning(f"Belum dikerjakan: {t}")
        else:
            st.success("Semua test sudah dikerjakan!")

        st.markdown("### 📅 Absen yang Belum Diisi")
        if belum_absen:
            for a in belum_absen:
                st.warning(f"Belum diisi: {a}")
        else:
            st.success("Semua absen sudah diisi!")

# ----------------------------------
# HALAMAN ABSEN
# ----------------------------------
def halaman_absen():
    st.title("📅 Absen")
    role = st.session_state.role

    if role == "guru":
        st.subheader("🗓️ Buat Jadwal Absen")
        judul = st.text_input("Judul Absen (misal: Absen Pertemuan 1)")
        tanggal = st.date_input("Tanggal Absen", datetime.date.today())
        kelas_pilih = st.selectbox("Pilih Kelas", list(st.session_state.kelas_data.keys()))

        if st.button("Buat Absen"):
            if not judul.strip() or not kelas_pilih:
                st.warning("Isi semua kolom.")
            else:
                id_absen = f"{kelas_pilih}_{judul}"
                st.session_state.absen_data[id_absen] = {
                    "judul": judul,
                    "kelas": kelas_pilih,
                    "tanggal": datetime.datetime.combine(tanggal, datetime.datetime.min.time()),
                    "kehadiran": {}
                }
                st.success(f"Absen '{judul}' berhasil dibuat! Berlaku selama 1 hari.")

        st.divider()
        st.subheader("📋 Daftar Absen")
        for kode, absen in st.session_state.absen_data.items():
            if st.session_state.kelas_data[absen["kelas"]]["guru"] == st.session_state.username:
                batas = absen["tanggal"] + datetime.timedelta(days=1)
                st.markdown(f"### {absen['judul']} - {absen['kelas']}")
                st.caption(f"Tanggal: {absen['tanggal'].strftime('%d %B %Y')} | Berlaku hingga: {batas.strftime('%d %B %Y %H:%M')}")
                df = pd.DataFrame([{"Nama Siswa": s, "Status": st} for s, st in absen["kehadiran"].items()])
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Belum ada siswa yang mengisi absen.")

    elif role == "siswa":
        st.subheader("📝 Isi Absen")
        aktif = {}
        now = datetime.datetime.now()
        for kode, absen in st.session_state.absen_data.items():
            batas = absen["tanggal"] + datetime.timedelta(days=1)
            if now < batas and st.session_state.username in st.session_state.kelas_data[absen["kelas"]]["anggota"]:
                aktif[kode] = absen

        if not aktif:
            st.info("Tidak ada absen aktif saat ini.")
        else:
            for kode, absen in aktif.items():
                st.markdown(f"### {absen['judul']} - {absen['kelas']}")
                if st.session_state.username in absen["kehadiran"]:
                    st.success(f"Anda sudah mengisi absen: {absen['kehadiran'][st.session_state.username]}")
                else:
                    pilihan = st.radio("Pilih status:", ["Hadir", "Sakit"])
                    if st.button("Kirim Absen", key=f"kirim_{kode}"):
                        absen["kehadiran"][st.session_state.username] = pilihan
                        st.success("Absen berhasil dikirim!")
                        st.rerun()

        # Tandai siswa yang tidak hadir setelah waktu absen habis
        for kode, absen in st.session_state.absen_data.items():
            batas = absen["tanggal"] + datetime.timedelta(days=1)
            if now >= batas:
                for siswa in st.session_state.kelas_data[absen["kelas"]]["anggota"]:
                    if siswa not in absen["kehadiran"]:
                        absen["kehadiran"][siswa] = "Tidak Hadir"

# ----------------------------------
# (FITUR LAIN TIDAK DIUBAH)
# ----------------------------------
def halaman_kelas():
    # kode sama seperti sebelumnya
    pass  # gunakan kode kamu yang lama di sini

def halaman_tugas():
    pass  # gunakan kode kamu yang lama di sini

def halaman_chat():
    pass  # gunakan kode kamu yang lama di sini

def halaman_test():
    pass  # gunakan kode kamu yang lama di sini

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

