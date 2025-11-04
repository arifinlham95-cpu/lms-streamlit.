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
# HALAMAN KELAS
# ----------------------------------
def halaman_kelas():
    st.title("👥 Kelas dan Materi")
    role = st.session_state.role

    if role == "guru":
        st.subheader("📘 Buat Kelas Baru")
        nama_kelas = st.text_input("Nama Kelas")
        kode_kelas = st.text_input("Kode Kelas (unik)")
        if st.button("➕ Buat Kelas"):
            if not nama_kelas or not kode_kelas:
                st.warning("Isi semua kolom.")
            elif kode_kelas in st.session_state.kelas_data:
                st.error("Kode kelas sudah digunakan.")
            else:
                st.session_state.kelas_data[kode_kelas] = {
                    "nama": nama_kelas,
                    "guru": st.session_state.username,
                    "materi": [],
                    "anggota": []
                }
                st.success(f"Kelas '{nama_kelas}' berhasil dibuat!")

        st.divider()
        st.subheader("📚 Daftar Kelas Anda")

        kelas_guru = {k: v for k, v in st.session_state.kelas_data.items() if v["guru"] == st.session_state.username}
        if not kelas_guru:
            st.info("Belum ada kelas yang Anda buat.")
        else:
            for kode, data in kelas_guru.items():
                with st.expander(f"{data['nama']} ({kode})"):
                    st.markdown(f"👩‍🏫 Guru: **{data['guru']}**")
                    st.markdown(f"👨‍🎓 Jumlah siswa: **{len(data['anggota'])}**")

                    st.markdown("### ✏️ Tambah Materi")
                    with st.form(f"form_materi_{kode}"):
                        judul = st.text_input("Judul Materi", key=f"judul_{kode}")
                        isi = st.text_area("Isi Materi")
                        submit = st.form_submit_button("📥 Simpan Materi")

                        if submit:
                            if not judul.strip() or not isi.strip():
                                st.warning("Isi semua kolom.")
                            else:
                                st.session_state.kelas_data[kode]["materi"].append({"judul": judul, "isi": isi})
                                st.success("Materi berhasil disimpan!")
                                st.rerun()

                    if data["materi"]:
                        st.markdown("### 📄 Materi di Kelas Ini")
                        for i, m in enumerate(data["materi"]):
                            st.write(f"**{i+1}. {m['judul']}**")
                            st.info(m["isi"])
                            if st.button("🗑️ Hapus Materi", key=f"hapus_{kode}_{i}"):
                                st.session_state.kelas_data[kode]["materi"].pop(i)
                                st.success("Materi dihapus.")
                                st.rerun()
                    else:
                        st.info("Belum ada materi di kelas ini.")

    elif role == "siswa":
        st.subheader("📘 Bergabung ke Kelas")
        kode_gabung = st.text_input("Masukkan Kode Kelas")
        if st.button("Gabung"):
            if kode_gabung not in st.session_state.kelas_data:
                st.error("Kode kelas tidak ditemukan.")
            else:
                kelas = st.session_state.kelas_data[kode_gabung]
                if st.session_state.username in kelas["anggota"]:
                    st.info("Anda sudah tergabung di kelas ini.")
                else:
                    kelas["anggota"].append(st.session_state.username)
                    st.success(f"Berhasil bergabung ke kelas {kelas['nama']}!")

        st.divider()
        st.subheader("📚 Kelas Saya")
        kelas_saya = {k: v for k, v in st.session_state.kelas_data.items() if st.session_state.username in v["anggota"]}

        if not kelas_saya:
            st.info("Belum bergabung di kelas mana pun.")
        else:
            for kode, data in kelas_saya.items():
                with st.expander(f"{data['nama']} ({kode})"):
                    st.markdown(f"👩‍🏫 Guru: **{data['guru']}**")
                    if not data["materi"]:
                        st.warning("Belum ada materi di kelas ini.")
                    else:
                        for m in data["materi"]:
                            st.markdown(f"### 📄 {m['judul']}")
                            st.info(m["isi"])

# ----------------------------------
# HALAMAN ABSEN
# ----------------------------------
def halaman_absen():
    st.title("📅 Absen")
    role = st.session_state.role

    # ---------------------------
    # GURU
    # ---------------------------
    if role == "guru":
        st.subheader("🆕 Buat Absen Baru")
        judul = st.text_input("Judul Absen")
        kode_absen = st.text_input("Kode Absen (unik)")
        tanggal_mulai = st.date_input("Tanggal Mulai Absen", datetime.date.today())

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
                    "tanggal": tanggal_mulai,
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
                batas = data["tanggal"] + datetime.timedelta(days=1)
                with st.expander(f"{data['judul']} ({kode}) - {data['tanggal']}"):
                    st.markdown(f"🕒 Berlaku sampai: {batas}")
                    df = pd.DataFrame(
                        [{"Nama Siswa": s, "Status": data['status'].get(s, "❌ Tidak Hadir" if datetime.date.today() > batas else "Belum Absen")}
                         for s in data["peserta"]]
                    )
                    st.dataframe(df, use_container_width=True)

    # ---------------------------
    # SISWA
    # ---------------------------
    elif role == "siswa":
        st.subheader("📅 Absen yang Bisa Diisi")
        today = datetime.date.today()
        absen_aktif = {
            k: v for k, v in st.session_state.absen_data.items()
            if st.session_state.username in v["peserta"] and today <= v["tanggal"] + datetime.timedelta(days=1)
        }

        if not absen_aktif:
            st.info("Tidak ada absen aktif.")
        else:
            for kode, data in absen_aktif.items():
                batas = data["tanggal"] + datetime.timedelta(days=1)
                with st.expander(f"{data['judul']} ({kode}) - Berlaku sampai {batas}"):
                    if st.session_state.username in data["status"]:
                        st.success(f"Anda sudah absen: {data['status'][st.session_state.username]}")
                    elif today > batas:
                        st.error("Waktu absen sudah habis, status Anda: ❌ Tidak Hadir")
                    else:
                        status = st.radio("Pilih Kehadiran:", ["Hadir", "Sakit"], key=f"absen_{kode}")
                        if st.button("Kirim", key=f"kirim_{kode}"):
                            data["status"][st.session_state.username] = status
                            st.success("Absen berhasil dikirim!")
                            st.rerun()

# ----------------------------------
# HALAMAN LAIN (TUGAS, TEST, CHAT)
# ----------------------------------
# (kode halaman_tugas, halaman_test, dan halaman_chat tetap sama seperti versi kamu sebelumnya)

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
        st.title("COOK LMS")
        st.write("Selamat datang di COOK LMS! 👋")
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
