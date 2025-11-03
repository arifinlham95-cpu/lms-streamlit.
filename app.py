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
    st.session_state.kelas_data = {}  # {kode_kelas: {"nama":..., "guru":..., "materi": [...], "anggota": [...] }}
if "test_data" not in st.session_state:
    st.session_state.test_data = {}  # {kode_test: {"judul":..., "guru":..., "soal": [...], "hasil": {siswa: skor}}}


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
# HALAMAN TEST (BARU)
# ----------------------------------
def halaman_test():
    st.title("🧠 Test (Ujian)")
    role = st.session_state.role

    # ----------------- GURU -----------------
    if role == "guru":
        st.subheader("📘 Buat Test Baru")
        judul_test = st.text_input("Judul Test")
        kode_test = st.text_input("Kode Test (unik)")
        if st.button("➕ Buat Test"):
            if not judul_test or not kode_test:
                st.warning("Isi semua kolom.")
            elif kode_test in st.session_state.test_data:
                st.error("Kode test sudah digunakan.")
            else:
                st.session_state.test_data[kode_test] = {
                    "judul": judul_test,
                    "guru": st.session_state.username,
                    "soal": [],
                    "hasil": {}
                }
                st.success(f"Test '{judul_test}' berhasil dibuat!")

        st.divider()
        st.subheader("📋 Daftar Test Anda")
        test_guru = {k: v for k, v in st.session_state.test_data.items() if v["guru"] == st.session_state.username}
        if not test_guru:
            st.info("Belum ada test yang Anda buat.")
        else:
            for kode, data in test_guru.items():
                with st.expander(f"{data['judul']} ({kode})"):
                    st.markdown("### ➕ Tambah Soal")
                    with st.form(f"form_soal_{kode}"):
                        pertanyaan = st.text_area("Soal", key=f"q_{kode}")
                        opsi_a = st.text_input("Pilihan A", key=f"a_{kode}")
                        opsi_b = st.text_input("Pilihan B", key=f"b_{kode}")
                        opsi_c = st.text_input("Pilihan C", key=f"c_{kode}")
                        opsi_d = st.text_input("Pilihan D", key=f"d_{kode}")
                        jawaban_benar = st.selectbox("Jawaban Benar", ["A", "B", "C", "D"], key=f"ans_{kode}")
                        submit_q = st.form_submit_button("Tambah Soal")

                        if submit_q:
                            st.session_state.test_data[kode]["soal"].append({
                                "pertanyaan": pertanyaan,
                                "opsi": {"A": opsi_a, "B": opsi_b, "C": opsi_c, "D": opsi_d},
                                "benar": jawaban_benar
                            })
                            st.success("Soal ditambahkan!")
                            st.rerun()

                    # Tampilkan soal
                    if data["soal"]:
                        st.markdown("### 🧾 Daftar Soal")
                        for i, q in enumerate(data["soal"]):
                            st.write(f"**{i+1}. {q['pertanyaan']}**")
                            for huruf, teks in q["opsi"].items():
                                st.write(f"{huruf}. {teks}")
                            st.caption(f"✅ Jawaban Benar: {q['benar']}")
                    else:
                        st.info("Belum ada soal di test ini.")

                    # Hasil siswa
                    if data["hasil"]:
                        st.markdown("### 📊 Hasil Siswa")
                        df = pd.DataFrame([
                            {"Nama Siswa": s, "Nilai": n}
                            for s, n in data["hasil"].items()
                        ])
                        st.dataframe(df, use_container_width=True)

    # ----------------- SISWA -----------------
    elif role == "siswa":
        st.subheader("📘 Kerjakan Test")
        kode_test = st.text_input("Masukkan Kode Test")

        if st.button("Mulai Test"):
            if kode_test not in st.session_state.test_data:
                st.error("Kode test tidak ditemukan.")
            else:
                st.session_state.current_test = kode_test
                st.rerun()

        if "current_test" in st.session_state:
            kode = st.session_state.current_test
            data = st.session_state.test_data[kode]
            st.markdown(f"## {data['judul']}")
            jawaban_siswa = {}
            skor = 0

            with st.form("form_test_siswa"):
                for i, q in enumerate(data["soal"]):
                    st.markdown(f"**{i+1}. {q['pertanyaan']}**")
                    jawaban = st.radio(
                        "Pilih jawaban:",
                        ["A", "B", "C", "D"],
                        key=f"ans_{i}",
                        format_func=lambda x: f"{x}. {q['opsi'][x]}"
                    )
                    jawaban_siswa[i] = jawaban
                submit_test = st.form_submit_button("Kirim Jawaban")

                if submit_test:


