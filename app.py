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
    st.session_state.kelas_data = {}
if "test_data" not in st.session_state:
    st.session_state.test_data = {}

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

                    st.markdown("### ✏️ Tambah Materi (Urutan Bebas, Banyak Item)")
                    with st.form(f"form_materi_{kode}"):
                        judul = st.text_input("Judul Materi", key=f"judul_{kode}")
                        st.caption("Tambahkan isi materi sesuai urutan yang Anda inginkan:")

                        jumlah_item = st.number_input("Jumlah bagian materi", min_value=1, max_value=20, value=1, key=f"jumlah_{kode}")
                        materi_isi = []

                        for i in range(int(jumlah_item)):
                            st.markdown(f"#### Bagian {i+1}")
                            tipe = st.selectbox(
                                f"Pilih jenis isi ke-{i+1}:",
                                ["Teks", "Video", "Gambar", "Dokumen"],
                                key=f"tipe_{kode}_{i}"
                            )

                            if tipe == "Teks":
                                teks = st.text_area("Isi teks:", key=f"teks_{kode}_{i}")
                                if teks.strip():
                                    materi_isi.append({"tipe": "teks", "konten": teks})

                            elif tipe == "Video":
                                vidio = st.text_input("Link video (YouTube):", key=f"vid_{kode}_{i}")
                                if vidio.strip():
                                    materi_isi.append({"tipe": "video", "konten": vidio})

                            elif tipe == "Gambar":
                                foto = st.file_uploader("Upload gambar:", type=["jpg", "png"], key=f"foto_{kode}_{i}")
                                if foto:
                                    materi_isi.append({"tipe": "gambar", "konten": foto.read(), "nama": foto.name})

                            elif tipe == "Dokumen":
                                dok = st.file_uploader("Upload dokumen:", type=["pdf", "docx", "pptx"], key=f"dok_{kode}_{i}")
                                if dok:
                                    materi_isi.append({"tipe": "dokumen", "konten": dok.read(), "nama": dok.name})

                        submitted = st.form_submit_button("📥 Simpan Materi")

                        if submitted:
                            if not judul.strip():
                                st.warning("Judul materi harus diisi.")
                            elif not materi_isi:
                                st.warning("Tambahkan minimal satu bagian isi materi.")
                            else:
                                st.session_state.kelas_data[kode]["materi"].append({
                                    "judul": judul,
                                    "isi": materi_isi
                                })
                                st.success("Materi berhasil disimpan dengan urutan bebas dan banyak item!")
                                st.rerun()

                    if data["materi"]:
                        st.markdown("### 📄 Materi di Kelas Ini")
                        for i, m in enumerate(data["materi"]):
                            st.markdown(f"**{i+1}. {m['judul']}**")
                            for bagian in m["isi"]:
                                if bagian["tipe"] == "teks":
                                    st.write(bagian["konten"])
                                elif bagian["tipe"] == "video":
                                    st.video(bagian["konten"])
                                elif bagian["tipe"] == "gambar":
                                    st.image(bagian["konten"], caption=bagian.get("nama", "Gambar"))
                                elif bagian["tipe"] == "dokumen":
                                    st.download_button(
                                        label=f"📄 Unduh {bagian['nama']}",
                                        data=bagian["konten"],
                                        file_name=bagian["nama"]
                                    )
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
                            for bagian in m["isi"]:
                                if bagian["tipe"] == "teks":
                                    st.write(bagian["konten"])
                                elif bagian["tipe"] == "video":
                                    st.video(bagian["konten"])
                                elif bagian["tipe"] == "gambar":
                                    st.image(bagian["konten"], caption=bagian.get("nama", "Gambar"))
                                elif bagian["tipe"] == "dokumen":
                                    st.download_button(
                                        label=f"📄 Unduh {bagian['nama']}",
                                        data=bagian["konten"],
                                        file_name=bagian["nama"]
                                    )

# ----------------------------------
# HALAMAN TEST
# ----------------------------------
def halaman_test():
    st.title("🧠 Test (Ujian)")
    role = st.session_state.role

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

                    if data["soal"]:
                        st.markdown("### 🧾 Daftar Soal")
                        for i, q in enumerate(data["soal"]):
                            st.write(f"**{i+1}. {q['pertanyaan']}**")
                            for huruf, teks in q["opsi"].items():
                                st.write(f"{huruf}. {teks}")
                            st.caption(f"✅ Jawaban Benar: {q['benar']}")
                    else:
                        st.info("Belum ada soal di test ini.")

                    if data["hasil"]:
                        st.markdown("### 📊 Hasil Siswa")
                        df = pd.DataFrame([
                            {"Nama Siswa": s, "Nilai": n}
                            for s, n in data["hasil"].items()
                        ])
                        st.dataframe(df, use_container_width=True)

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
                    skor = sum(1 for i, q in enumerate(data["soal"]) if jawaban_siswa[i] == q["benar"])
                    nilai = round((skor / len(data["soal"])) * 100, 2)
                    st.success(f"🎉 Tes selesai! Nilai Anda: {nilai}")
                    st.session_state.test_data[kode]["hasil"][st.session_state.username] = nilai
                    del st.session_state.current_test
                    st.rerun()

# ----------------------------------
# MAIN CONTROL
# ----------------------------------
def main_app():
    st.sidebar.title("📚 Navigasi LMS")
    if st.session_state.role:
        st.sidebar.write(f"👋 Hai, **{st.session_state.username}** ({st.session_state.role.capitalize()})")

    menu = st.sidebar.radio("Pilih Halaman:", [
        "🏠 Dashboard",
        "👥 Kelas",
        "🧠 Test",
        "🚪 Logout"
    ])

    if menu == "🏠 Dashboard":
        st.title("COOK LMS")
        st.write("Selamat datang di COOK LMS! 👋")

    elif menu == "👥 Kelas":
        halaman_kelas()

    elif menu == "🧠 Test":
        halaman_test()

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


