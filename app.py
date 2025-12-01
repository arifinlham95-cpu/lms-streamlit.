import streamlit as st
import pandas as pd
import datetime
import json
import os
import base64
from typing import Any

DATA_FILE = "lms_data.json"

# ----------------------------------
# Convert data before saving
# ----------------------------------
def safe_serialize(obj: Any):
    if isinstance(obj, bytes):
        return {"__bytes__": True, "data": base64.b64encode(obj).decode("utf-8")}

    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()

    elif isinstance(obj, dict):
        return {k: safe_serialize(v) for k, v in obj.items()}

    elif isinstance(obj, list):
        return [safe_serialize(v) for v in obj]

    return obj


# ----------------------------------
# Convert back to bytes when loading
# ----------------------------------
def safe_deserialize(obj: Any):
    if isinstance(obj, dict):
        if "__bytes__" in obj:
            return base64.b64decode(obj["data"])
        return {k: safe_deserialize(v) for k, v in obj.items()}

    elif isinstance(obj, list):
        return [safe_deserialize(v) for v in obj]

    return obj


def save_data():
    data = {
        "users": st.session_state.users,
        "kelas_data": st.session_state.kelas_data,
        "tugas_data": st.session_state.tugas_data,
        "test_data": st.session_state.test_data,
        "chat_data": st.session_state.chat_data,
        "absen_data": st.session_state.get("absen_data", {})
    }
    data = safe_serialize(data)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = safe_deserialize(json.load(f))
        except Exception:
            st.warning("⚠️ Data rusak, reset.")
            data = {}
    else:
        data = {}

    st.session_state.users = data.get("users", {"guru": {"guru123": "Guru Default"}, "siswa": {"siswa123": "Siswa Default"}})
    st.session_state.kelas_data = data.get("kelas_data", {})
    st.session_state.tugas_data = data.get("tugas_data", {})
    st.session_state.test_data = data.get("test_data", {})
    st.session_state.chat_data = data.get("chat_data", {})
    st.session_state.absen_data = data.get("absen_data", {})

    data = safe_serialize(data)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    raise ValueError("File kosong")
                data = json.loads(content)
        except (json.JSONDecodeError, ValueError):
            st.warning("⚠️ File data rusak atau kosong, membuat file baru.")
            data = {
                "users": {"guru": {"guru123": "Guru Default"}, "siswa": {"siswa123": "Siswa Default"}},
                "kelas_data": {},
                "tugas_data": {},
                "test_data": {},
                "chat_data": {},
                "absen_data": {}
            }
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=4)
        st.session_state.users = data.get("users", {})
        st.session_state.kelas_data = data.get("kelas_data", {})
        st.session_state.tugas_data = data.get("tugas_data", {})
        st.session_state.test_data = data.get("test_data", {})
        st.session_state.chat_data = data.get("chat_data", {})
        st.session_state.absen_data = data.get("absen_data", {})
    else:
        # Buat file baru kalau belum ada
        data = {
            "users": {"guru": {"guru123": "Guru Default"}, "siswa": {"siswa123": "Siswa Default"}},
            "kelas_data": {},
            "tugas_data": {},
            "test_data": {},
            "chat_data": {},
            "absen_data": {}
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        st.session_state.update(data)


# ----------------------------------
# KONFIGURASI DASAR
# ----------------------------------
st.set_page_config(page_title="COOK LMS", layout="wide")

# 1️⃣ Load data dari file saat aplikasi mulai
load_data()

# 2️⃣ Inisialisasi session state jika belum ada
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

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

# ----------------------------------
# FUNGSI LOGIN / REGISTER
# ----------------------------------
def login():
    st.title("🔐 COOK LMS Login")

    tab1, tab2 = st.tabs(["🔑 Masuk", "🆕 Buat Akun"])

    # ---------------- Tab Masuk ----------------
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

    # ---------------- Tab Daftar ----------------
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
                    save_data()  # simpan data baru
                    st.success(f"Akun {role_reg} berhasil dibuat! Silakan login.")
                    st.info(f"Gunakan kata sandi: **{pass_reg}** untuk login.")
                    st.rerun()


# ----------------------------------
# HALAMAN KELAS
# ----------------------------------
def halaman_kelas():
    st.title("👥 Kelas dan Materi")
    submit = False
    judul = ""
    teks_materi = ""
    gambar_files = []
    video_files = []
    youtube_link = ""
    dokumen_files = []
    urutan = []
    kode = ""
    data = {}
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
                save_data()  # simpan data setelah membuat kelas
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

                    st.markdown("### ✏️ Tambah Materi (Teks, Gambar, Video, Dokumen)")
                    
                    with st.form(f"form_materi_{kode}"):
                        judul = st.text_input("Judul Materi", key=f"judul_{kode}")
                        teks_materi = st.text_area("Tambahkan teks materi (opsional)", key=f"teks_{kode}")
                        gambar_files = st.file_uploader("Upload Gambar (opsional, bisa lebih dari 1)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key=f"gambar_{kode}")
                        video_files = st.file_uploader("Upload Video (opsional, bisa lebih dari 1)", type=["mp4", "mov"], accept_multiple_files=True, key=f"video_{kode}")
                        youtube_link = st.text_input("Tambahkan Link YouTube (opsional)", key=f"yt_{kode}")
                        dokumen_files = st.file_uploader("Upload Dokumen (opsional, bisa lebih dari 1)", type=["pdf", "docx", "pptx"], accept_multiple_files=True, key=f"dokumen_{kode}")

                        st.markdown("### 🧩 Urutan Konten")
                        urutan = st.multiselect(
                            "Pilih dan urutkan jenis konten yang ingin ditampilkan:",
                            ["Teks", "Gambar", "Video", "YouTube", "Dokumen"],
                            default=["Teks", "Gambar", "Video", "Dokumen"]
                        )
                        
                        submit = st.form_submit_button("📥 Simpan Materi")

    if submit:
        if not judul.strip():
            st.warning("Isi judul materi terlebih dahulu.")
        else:
            konten = []
            for tipe in urutan:
                if tipe == "Teks" and teks_materi.strip():
                    konten.append({"tipe": "text", "isi": teks_materi})
                
                elif tipe == "Gambar":
                    for g in gambar_files:
                        konten.append({"tipe": "image", "nama": g.name, "data": g.read()})
                
                elif tipe == "Video":
                    for v in video_files:
                        konten.append({"tipe": "video", "nama": v.name, "data": v.read()})
                
                elif tipe == "YouTube" and youtube_link.strip():
                    konten.append({"tipe": "youtube", "link": youtube_link.strip()})
                
                elif tipe == "Dokumen":
                    for d in dokumen_files:
                        konten.append({"tipe": "file", "nama": d.name, "data": d.read()})
                        
            if not konten:
                st.warning("Tambahkan minimal satu konten (teks, gambar, video, YouTube, atau dokumen).")
            else:
                st.session_state.kelas_data[kode]["materi"].append({
                    "judul": judul,
                    "konten": konten
                })
                save_data()
                st.success("Materi berhasil disimpan!")
                st.rerun()
                
            if data["materi"]:
                st.markdown("### 📄 Materi di Kelas Ini")
                for i, m in enumerate(data["materi"]):
                    st.write(f"**{i+1}. {m['judul']}**")
                    for item in m.get("konten", []):
                        if item["tipe"] == "text":
                            st.markdown(item["isi"])
                        elif item["tipe"] == "image":
                            st.image(item["data"], caption=item["nama"], use_container_width=True)
                        elif item["tipe"] == "video":
                            st.video(item["data"])
                        elif item["tipe"] == "youtube":
                            yt_link = item["link"].replace("watch?v=", "embed/").replace("youtu.be/", "youtube.com/embed/")
                            st.markdown(
                                f"""
                                <iframe width="100%" height="400" src="{yt_link}" 
                                frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowfullscreen></iframe>
                                """, unsafe_allow_html=True
                            )
                        elif item["tipe"] == "file":
                            st.download_button(
                                label=f"📄 Unduh {item['nama']}",
                                data=item["data"],
                                file_name=item["nama"],
                                mime="application/octet-stream",
                                key=f"unduh_{kode}_{i}_{item['nama']}"
                            )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✏️ Edit Materi", key=f"edit_{kode}_{i}"):
                            st.session_state.editing_materi = (kode, i)
                            st.rerun()
                    with col2:
                        if st.button("🗑️ Hapus Materi", key=f"hapus_{kode}_{i}"):
                            st.session_state.kelas_data[kode]["materi"].pop(i)
                            st.success("Materi dihapus.")
                            st.rerun()
                    
            else:
                st.info("Belum ada materi di kelas ini.")

            # --- Form Edit Materi ---
            if "editing_materi" in st.session_state:
                kode_edit, idx_edit = st.session_state.editing_materi
                materi_edit = st.session_state.kelas_data[kode_edit]["materi"][idx_edit]

                st.markdown("---")
                st.subheader(f"✏️ Edit Materi: {materi_edit['judul']}")

                with st.form("form_edit_materi"):
                    new_title = st.text_input("Judul Materi", value=materi_edit["judul"])
                    new_text = ""
                    for item in materi_edit["konten"]:
                        if item["tipe"] == "text":
                            new_text = item["isi"]
                            break
                    new_text = st.text_area("Teks Materi (opsional)", value=new_text)

                    new_yt = ""
                    for item in materi_edit["konten"]:
                        if item["tipe"] == "youtube":
                            new_yt = item["link"]
                            break
                    new_yt = st.text_input("Link YouTube (opsional)", value=new_yt)

                    st.markdown("Upload ulang file/gambar/video/dokumen (opsional)")
                    new_images = st.file_uploader("Gambar", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
                    new_videos = st.file_uploader("Video", type=["mp4", "mov"], accept_multiple_files=True)
                    new_docs = st.file_uploader("Dokumen", type=["pdf", "docx", "pptx"], accept_multiple_files=True)

                    submit_edit = st.form_submit_button("💾 Simpan Perubahan")
                    cancel_edit = st.form_submit_button("❌ Batal")

                    if submit_edit:
                        new_konten = []
                        if new_text.strip():
                            new_konten.append({"tipe": "text", "isi": new_text})
                        if new_images:
                            for g in new_images:
                                new_konten.append({"tipe": "image", "nama": g.name, "data": g.read()})
                        if new_videos:
                            for v in new_videos:
                                new_konten.append({"tipe": "video", "nama": v.name, "data": v.read()})
                        if new_yt.strip():
                            new_konten.append({"tipe": "youtube", "link": new_yt})
                        if new_docs:
                            for d in new_docs:
                                new_konten.append({"tipe": "file", "nama": d.name, "data": d.read()})

                        materi_edit["judul"] = new_title
                        if new_konten:
                            materi_edit["konten"] = new_konten

                        save_data()
                        st.success("Materi berhasil diperbarui!")
                        del st.session_state.editing_materi
                        st.rerun()

                    if cancel_edit:
                        del st.session_state.editing_materi
                        st.info("Edit materi dibatalkan.")
                        st.rerun()

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
        kelas_saya = {
            k: v
            for k, v in st.session_state.kelas_data.items()
            if st.session_state.username in v["anggota"]
        }

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
                            if "konten" in m:
                                for item in m["konten"]:
                                    if item["tipe"] == "text":
                                        st.markdown(item["isi"])
                                    elif item["tipe"] == "image":
                                        st.image(item["data"], caption=item["nama"], use_container_width=True)
                                    elif item["tipe"] == "video":
                                        st.video(item["data"])
                                    elif item["tipe"] == "youtube":
                                        yt_link = item["link"].replace("watch?v=", "embed/").replace("youtu.be/", "youtube.com/embed/")
                                        st.markdown(
                                            f"""
                                            <iframe width="100%" height="400" src="{yt_link}"
                                            frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                            allowfullscreen></iframe>
                                            """, unsafe_allow_html=True
                                        )
                                    elif item["tipe"] == "file":
                                        st.download_button(
                                            label=f"📄 Unduh {item['nama']}",
                                            data=item["data"],
                                            file_name=item["nama"],
                                            mime="application/octet-stream",
                                            key=f"unduh_{kode}_{m['judul']}_{item['nama']}"
                                        )
                            else:
                                st.info("Materi ini belum memiliki konten.")


# ----------------------------------
# HALAMAN TUGAS
# ----------------------------------
def halaman_tugas():
    st.title("📝 Tugas")
    role = st.session_state.role

    if role == "guru":
        st.subheader("📘 Buat Tugas untuk Kelas")
        kode_kelas = st.selectbox("Pilih Kelas", list(st.session_state.kelas_data.keys()))
        judul = st.text_input("Judul Tugas")
        deskripsi = st.text_area("Deskripsi Tugas")
        dokumen = st.file_uploader("Upload Dokumen (Opsional)", type=["pdf", "docx"])
        if st.button("📤 Simpan Tugas"):
            if not judul.strip() or not kode_kelas:
                st.warning("Isi semua kolom.")
            else:
                if kode_kelas not in st.session_state.tugas_data:
                    st.session_state.tugas_data[kode_kelas] = []
                st.session_state.tugas_data[kode_kelas].append({
                    "judul": judul,
                    "deskripsi": deskripsi,
                    "dokumen": dokumen.read() if dokumen else None,
                    "nama_dok": dokumen.name if dokumen else None,
                    "kumpul": {}
                })
                st.success("Tugas berhasil disimpan!")

        st.divider()
        st.subheader("📋 Daftar Tugas")
        for kode, daftar in st.session_state.tugas_data.items():
            st.markdown(f"### 📘 {st.session_state.kelas_data[kode]['nama']}")
            for i, t in enumerate(daftar):
                st.write(f"**{i+1}. {t['judul']}**")
                st.info(t["deskripsi"])
                if t["dokumen"]:
                    st.download_button("📄 Unduh Dokumen", t["dokumen"], file_name=t["nama_dok"])
                if t["kumpul"]:
                    df = pd.DataFrame([{"Nama Siswa": s, "Tanggal": d} for s, d in t["kumpul"].items()])
                    st.dataframe(df, use_container_width=True)

    elif role == "siswa":
        st.subheader("📘 Tugas dari Kelas Anda")
        kelas_saya = {k: v for k, v in st.session_state.kelas_data.items() if st.session_state.username in v["anggota"]}
        if not kelas_saya:
            st.info("Belum ada kelas yang diikuti.")
        else:
            for kode, data in kelas_saya.items():
                if kode not in st.session_state.tugas_data:
                    continue
                with st.expander(f"Tugas - {data['nama']}"):
                    for i, t in enumerate(st.session_state.tugas_data[kode]):
                        st.write(f"### {t['judul']}")
                        st.info(t["deskripsi"])
                        if t["dokumen"]:
                            st.download_button("📄 Unduh Dokumen", t["dokumen"], file_name=t["nama_dok"])
                        if st.session_state.username in t["kumpul"]:
                            st.success("✅ Anda sudah mengumpulkan tugas ini.")
                        else:
                            file_tugas = st.file_uploader(f"Upload Tugas Anda (satu kali saja) - {t['judul']}", type=["pdf", "docx"], key=f"upload_{kode}_{i}")
                            if st.button("Kumpulkan", key=f"kumpul_{kode}_{i}"):
                                if file_tugas:
                                    t["kumpul"][st.session_state.username] = str(datetime.datetime.now())
                                    st.success("Tugas berhasil dikumpulkan!")
                                    st.rerun()
                                else:
                                    st.warning("Pilih file terlebih dahulu.")

# ----------------------------------
# HALAMAN ROOM CHAT
# ----------------------------------
def halaman_chat():
    st.title("💬 Room Chat")
    role = st.session_state.role

    kelas_saya = (
        {k: v for k, v in st.session_state.kelas_data.items() if (v["guru"] == st.session_state.username or st.session_state.username in v["anggota"])}
    )

    if not kelas_saya:
        st.info("Belum ada kelas untuk chat.")
        return

    kode_kelas = st.selectbox("Pilih Kelas", list(kelas_saya.keys()))
    if kode_kelas not in st.session_state.chat_data:
        st.session_state.chat_data[kode_kelas] = []

    st.divider()
    st.subheader(f"💭 Chat Room - {kelas_saya[kode_kelas]['nama']}")

    for chat in st.session_state.chat_data[kode_kelas]:
        st.markdown(f"**{chat['user']}** ({chat['waktu']}): {chat['pesan']}")

    pesan = st.text_input("Ketik pesan...")
    if st.button("Kirim"):
        if pesan.strip():
            st.session_state.chat_data[kode_kelas].append({
                "user": st.session_state.username,
                "pesan": pesan,
                "waktu": datetime.datetime.now().strftime("%H:%M")
            })
            st.rerun()

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

                    if data["hasil"]:
                        st.markdown("### 📊 Hasil Siswa")
                        df = pd.DataFrame([{"Nama Siswa": s, "Nilai": n} for s, n in data["hasil"].items()])
                        st.dataframe(df, use_container_width=True)

    elif role == "siswa":
        st.subheader("📘 Kerjakan Test")
        kode_test = st.text_input("Masukkan Kode Test")

        if st.button("Mulai Test"):
            if kode_test not in st.session_state.test_data:
                st.error("Kode test tidak ditemukan.")
            elif st.session_state.username in st.session_state.test_data[kode_test]["hasil"]:
                st.warning("Anda sudah mengerjakan test ini.")
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
# HALAMAN ABSEN (FITUR BARU)
# ----------------------------------
def halaman_absen():
    st.title("📅 Absen")
    role = st.session_state.role

    # ----------------------------
    # AKUN GURU
    # ----------------------------
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
                # Ambil semua siswa di kelas guru
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
                st.success("✅ Absen berhasil dibuat!")

        st.divider()
        st.subheader("📋 Daftar Absen Anda")

        absen_guru = {k: v for k, v in st.session_state.absen_data.items() if v["guru"] == st.session_state.username}
        if not absen_guru:
            st.info("Belum ada absen yang Anda buat.")
        else:
            today = datetime.date.today()
            for kode, data in absen_guru.items():
                batas = data["tanggal"] + datetime.timedelta(days=1)
                if today > batas:
                    # Otomatis menandai siswa yang belum absen
                    for s in data["peserta"]:
                        if s not in data["status"]:
                            data["status"][s] = "Tidak Hadir"

                with st.expander(f"{data['judul']} ({kode}) - {data['tanggal']}"):
                    st.markdown(f"🕒 Berlaku sampai: {batas}")
                    df = pd.DataFrame(
                        [{"Nama Siswa": s, "Status": data['status'].get(s, '❌ Belum Absen')} for s in data["peserta"]]
                    )
                    st.dataframe(df, use_container_width=True)

    # ----------------------------
    # AKUN SISWA
    # ----------------------------
    elif role == "siswa":
        st.subheader("📅 Daftar Absen Aktif")
        today = datetime.date.today()

        absen_aktif = {
            k: v for k, v in st.session_state.absen_data.items()
            if st.session_state.username in v["peserta"]
        }

        if not absen_aktif:
            st.info("Belum ada absen aktif.")
        else:
            for kode, data in absen_aktif.items():
                batas = data["tanggal"] + datetime.timedelta(days=1)
                if today > batas and st.session_state.username not in data["status"]:
                    data["status"][st.session_state.username] = "Tidak Hadir"

                with st.expander(f"{data['judul']} ({kode}) - {data['tanggal']}"):
                    if today <= batas:
                        if st.session_state.username in data["status"]:
                            st.success(f"Anda sudah absen: {data['status'][st.session_state.username]}")
                        else:
                            status = st.radio("Pilih Kehadiran:", ["Hadir", "Sakit"], key=f"absen_{kode}")
                            if st.button("Kirim", key=f"kirim_{kode}"):
                                data["status"][st.session_state.username] = status
                                st.success("✅ Absen berhasil dikirim!")
                                st.rerun()
                    else:
                        st.warning("Waktu absen telah berakhir.")
                        st.info(f"Status Anda: {data['status'].get(st.session_state.username, 'Tidak Hadir')}")

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
        st.title("📊 Dashboard COOK LMS")
        role = st.session_state.role
        if role == "guru":
            # ... isi dashboard guru ...
            pass
        elif role == "siswa":
            # ... isi dashboard siswa ...
            pass
        else:
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
 


























