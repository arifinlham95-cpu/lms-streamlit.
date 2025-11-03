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
if "kelas_data" not in st.session_state:
    # Menyimpan data kelas dan materi
    st.session_state.kelas_data = {}  # format: {kode_kelas: {"nama":..., "guru":..., "materi": [...], "anggota": [...] }}


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
                if pass_reg in st.session_state.users[role_reg.lower()]:
                    st.error("Kata sandi ini sudah digunakan.")
                else:
                    st.session_state.users[role_reg.lower()][pass_reg] = nama_reg
                    st.success(f"Akun {role_reg} berhasil dibuat! Silakan login.")
                    st.info(f"Gunakan kata sandi: **{pass_reg}** untuk login.")
                    st.rerun()


# ----------------------------------
# HALAMAN KELAS & MATERI (Gabung)
# ----------------------------------
def halaman_kelas():
    st.title("👥 Kelas dan Materi")
    role = st.session_state.role

    # ================== GURU ==================
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

                    # Tambah materi
                    with st.form(f"form_materi_{kode}"):
                        st.markdown("### ➕ Tambah Materi")
                        judul = st.text_input("Judul Materi", key=f"judul_{kode}")
                        deskripsi = st.text_area("Deskripsi", key=f"des_{kode}")
                        link_vidio = st.text_input("Link Video (opsional)", key=f"vid_{kode}")
                        foto = st.file_uploader("Upload Foto (opsional)", type=["jpg", "png"], key=f"foto_{kode}")
                        submitted = st.form_submit_button("Tambah Materi")

                        if submitted:
                            materi = {
                                "judul": judul,
                                "deskripsi": deskripsi,
                                "link_vidio": link_vidio,
                                "foto": foto.name if foto else None
                            }
                            st.session_state.kelas_data[kode]["materi"].append(materi)
                            st.success("Materi berhasil ditambahkan!")
                            st.rerun()

                    # Daftar materi
                    if data["materi"]:
                        st.markdown("### 📄 Materi di Kelas Ini")
                        for i, m in enumerate(data["materi"]):
                            st.markdown(f"**{i+1}. {m['judul']}**")
                            st.write(m["deskripsi"])
                            if m["link_vidio"]:
                                st.video(m["link_vidio"])
                            if m["foto"]:
                                st.image(m["foto"])
                            col1, col2 = st.columns(2)
                            if col1.button("✏️ Edit", key=f"edit_{kode}_{i}"):
                                st.session_state.edit_index = (kode, i)
                                st.rerun()
                            if col2.button("🗑️ Hapus", key=f"hapus_{kode}_{i}"):
                                st.session_state.kelas_data[kode]["materi"].pop(i)
                                st.success("Materi dihapus.")
                                st.rerun()
                    else:
                        st.info("Belum ada materi di kelas ini.")

        # Mode edit materi
        if "edit_index" in st.session_state:
            kode, idx = st.session_state.edit_index
            materi = st.session_state.kelas_data[kode]["materi"][idx]
            st.sidebar.subheader(f"✏️ Edit Materi ({materi['judul']})")
            judul_baru = st.sidebar.text_input("Judul Baru", materi["judul"])
            des_baru = st.sidebar.text_area("Deskripsi Baru", materi["deskripsi"])
            link_baru = st.sidebar.text_input("Link Video Baru", materi["link_vidio"])
            if st.sidebar.button("Simpan Perubahan"):
                materi["judul"], materi["deskripsi"], materi["link_vidio"] = judul_baru, des_baru, link_baru
                st.success("Materi diperbarui!")
                del st.session_state.edit_index
                st.rerun()

    # ================== SISWA ==================
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
                            st.write(m["deskripsi"])
                            if m["link_vidio"]:
                                st.video(m["link_vidio"])
                            if m["foto"]:
                                st.image(m["foto"])


# ----------------------------------
# HALAMAN UTAMA & MENU LAIN
# ----------------------------------
def main_app():
    st.sidebar.title("📚 Navigasi LMS")

    if st.session_state.role:
        st.sidebar.write(f"👋 Hai, **{st.session_state.username}** ({st.session_state.role.capitalize()})")

    menu = st.sidebar.radio("Pilih Halaman:", [
        "🏠 Dashboard",
        "👥 Kelas",
        "🧠 Pre-Test",
        "📝 Tugas",
        "📄 LKPD",
        "📅 Absensi",
        "🚪 Logout"
    ])

    if menu == "🏠 Dashboard":
        st.title("COOK LMS")
        st.write("Selamat datang di COOK LMS! 👋")

    elif menu == "👥 Kelas":
        halaman_kelas()

    elif menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.role = ""
        st.session_state.username = ""
        st.warning("Anda telah keluar.")
        st.rerun()

    st.markdown("---")
    st.caption("COOK LMS | © 2025 Universitas Sriwijaya")


# ----------------------------------
# MAIN FLOW
# ----------------------------------
if not st.session_state.logged_in:
    login()
else:
    main_app()
