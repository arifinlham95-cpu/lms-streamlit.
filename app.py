import streamlit as st
import sqlite3
import datetime
import os

# =========================
# DATABASE
# =========================
conn = sqlite3.connect('lms.db', check_same_thread=False)
c = conn.cursor()

# Buat tabel jika belum ada
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name TEXT,
    class_code TEXT UNIQUE,
    teacher_id INTEGER
)''')

c.execute('''CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    title TEXT,
    content TEXT,
    video_url TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    student_id INTEGER,
    date TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    title TEXT,
    description TEXT,
    file_path TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER,
    student_id INTEGER,
    file_path TEXT,
    submitted_at TEXT
)''')

conn.commit()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# =========================
# HELPER FUNCTIONS
# =========================
def register_user(username, password, role):
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                  (username, password, role))
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()

def create_class(class_name, class_code, teacher_id):
    try:
        c.execute("INSERT INTO classes (class_name, class_code, teacher_id) VALUES (?, ?, ?)", 
                  (class_name, class_code, teacher_id))
        conn.commit()
        return True
    except:
        return False

def get_class_by_code(class_code):
    c.execute("SELECT * FROM classes WHERE class_code=?", (class_code,))
    return c.fetchone()

def add_material(class_id, title, content, video_url):
    c.execute("INSERT INTO materials (class_id, title, content, video_url) VALUES (?, ?, ?, ?)", 
              (class_id, title, content, video_url))
    conn.commit()

def update_material(material_id, title, content, video_url):
    c.execute("UPDATE materials SET title=?, content=?, video_url=? WHERE id=?", 
              (title, content, video_url, material_id))
    conn.commit()

def delete_material(material_id):
    c.execute("DELETE FROM materials WHERE id=?", (material_id,))
    conn.commit()

def get_materials(class_id):
    c.execute("SELECT * FROM materials WHERE class_id=?", (class_id,))
    return c.fetchall()

def mark_attendance(class_id, student_id):
    today = str(datetime.date.today())
    c.execute("SELECT * FROM attendance WHERE class_id=? AND student_id=? AND date=?", 
              (class_id, student_id, today))
    if not c.fetchone():
        c.execute("INSERT INTO attendance (class_id, student_id, date) VALUES (?, ?, ?)", 
                  (class_id, student_id, today))
        conn.commit()
        return True
    return False

def get_attendance_report(class_id):
    c.execute("""SELECT u.username, a.date 
                 FROM attendance a 
                 JOIN users u ON a.student_id = u.id 
                 WHERE class_id=?""", (class_id,))
    return c.fetchall()

# --------------------------
# ASSIGNMENTS (TUGAS)
# --------------------------
def add_assignment(class_id, title, description, file_path):
    c.execute("INSERT INTO assignments (class_id, title, description, file_path) VALUES (?, ?, ?, ?)", 
              (class_id, title, description, file_path))
    conn.commit()

def get_assignments(class_id):
    c.execute("SELECT * FROM assignments WHERE class_id=?", (class_id,))
    return c.fetchall()

def update_assignment(assignment_id, title, description, file_path):
    c.execute("UPDATE assignments SET title=?, description=?, file_path=? WHERE id=?", 
              (title, description, file_path, assignment_id))
    conn.commit()

def delete_assignment(assignment_id):
    c.execute("DELETE FROM assignments WHERE id=?", (assignment_id,))
    conn.commit()

def submit_assignment(assignment_id, student_id, file_path):
    submitted_at = str(datetime.datetime.now())
    c.execute("INSERT INTO submissions (assignment_id, student_id, file_path, submitted_at) VALUES (?, ?, ?, ?)", 
              (assignment_id, student_id, file_path, submitted_at))
    conn.commit()

def get_submissions(assignment_id):
    c.execute("""SELECT u.username, s.file_path, s.submitted_at 
                 FROM submissions s 
                 JOIN users u ON s.student_id = u.id 
                 WHERE s.assignment_id=?""", (assignment_id,))
    return c.fetchall()

# =========================
# STREAMLIT APP
# =========================
st.set_page_config(page_title="Mini LMS", page_icon="📚")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

st.title("📚 COOK LMS")

# Login & Register
if not st.session_state.logged_in:
    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

    if menu == "Login":
        st.subheader("🔑 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success(f"Selamat datang {user[1]} ({user[3]})")
                st.rerun()
            else:
                st.error("Username atau password salah")

    elif menu == "Register":
        st.subheader("📝 Register")
        username = st.text_input("Buat Username")
        password = st.text_input("Buat Password", type="password")
        role = st.selectbox("Daftar sebagai", ["Teacher", "Student"])
        if st.button("Daftar"):
            if register_user(username, password, role):
                st.success("Registrasi berhasil! Silakan login.")
            else:
                st.error("Username sudah digunakan!")

else:
    user = st.session_state.user
    role = user[3]

    st.sidebar.write(f"👤 {user[1]} ({role})")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    # =========================
    # Dashboard Guru
    # =========================
    if role == "Teacher":
        st.subheader("👨‍🏫 Dashboard Guru")

        tab1, tab2, tab3, tab4 = st.tabs(["📘 Buat Kelas", "📂 Materi", "📑 Tugas", "📋 Laporan Absensi"])

        with tab1:
            st.write("Buat kelas baru dengan kode unik.")
            class_name = st.text_input("Nama Kelas")
            class_code = st.text_input("Kode Kelas")
            if st.button("Buat Kelas"):
                if create_class(class_name, class_code, user[0]):
                    st.success(f"Kelas '{class_name}' berhasil dibuat dengan kode {class_code}")
                else:
                    st.error("Kode kelas sudah digunakan!")

        with tab2:
            st.write("Kelola Materi")
            class_code = st.text_input("Masukkan kode kelas")
            kelas = get_class_by_code(class_code)
            if kelas:
                title = st.text_input("Judul Materi")
                content = st.text_area("Konten Materi")
                video_url = st.text_input("URL Video (YouTube)")
                if st.button("Upload Materi"):
                    add_material(kelas[0], title, content, video_url)
                    st.success("Materi berhasil diupload!")

                st.write("### 📂 Daftar Materi")
                for m in get_materials(kelas[0]):
                    st.markdown(f"**{m[2]}**")
                    st.write(m[3])
                    if m[4]:
                        st.video(m[4])

                    if st.button(f"✏️ Edit Materi {m[0]}"):
                        new_title = st.text_input("Edit Judul", m[2], key=f"title{m[0]}")
                        new_content = st.text_area("Edit Konten", m[3], key=f"content{m[0]}")
                        new_video = st.text_input("Edit Video URL", m[4], key=f"video{m[0]}")
                        if st.button("Simpan Perubahan", key=f"save{m[0]}"):
                            update_material(m[0], new_title, new_content, new_video)
                            st.success("Materi diperbarui!")
                            st.rerun()

                    if st.button(f"🗑️ Hapus Materi {m[0]}"):
                        delete_material(m[0])
                        st.warning("Materi dihapus!")
                        st.rerun()

        with tab3:
            st.write("Kelola Tugas")
            class_code = st.text_input("Masukkan kode kelas (Tugas)")
            kelas = get_class_by_code(class_code)
            if kelas:
                title = st.text_input("Judul Tugas")
                description = st.text_area("Deskripsi Tugas")
                file = st.file_uploader("Upload File Tugas", type=["pdf", "docx", "txt"])
                if st.button("Upload Tugas"):
                    file_path = None
                    if file:
                        file_path = os.path.join(UPLOAD_DIR, file.name)
                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())
                    add_assignment(kelas[0], title, description, file_path)
                    st.success("Tugas berhasil diupload!")

                st.write("### 📂 Daftar Tugas")
                for a in get_assignments(kelas[0]):
                    st.markdown(f"**{a[1]}** - {a[2]}")
                    if a[3]:
                        st.download_button("📥 Download Tugas", open(a[4], "rb"), file_name=os.path.basename(a[4]))

                    if st.button(f"✏️ Edit Tugas {a[0]}"):
                        new_title = st.text_input("Edit Judul", a[1], key=f"atitle{a[0]}")
                        new_desc = st.text_area("Edit Deskripsi", a[2], key=f"adesc{a[0]}")
                        new_file = st.file_uploader("Upload File Baru", type=["pdf", "docx", "txt"], key=f"afile{a[0]}")
                        new_file_path = a[4]
                        if new_file:
                            new_file_path = os.path.join(UPLOAD_DIR, new_file.name)
                            with open(new_file_path, "wb") as f:
                                f.write(new_file.getbuffer())
                        if st.button("Simpan Perubahan", key=f"asave{a[0]}"):
                            update_assignment(a[0], new_title, new_desc, new_file_path)
                            st.success("Tugas diperbarui!")
                            st.rerun()

                    if st.button(f"🗑️ Hapus Tugas {a[0]}"):
                        delete_assignment(a[0])
                        st.warning("Tugas dihapus!")
                        st.rerun()

                    st.write("### 📥 Jawaban Siswa")
                    subs = get_submissions(a[0])
                    if subs:
                        for s in subs:
                            st.write(f"👩‍🎓 {s[0]} - {s[2]}")
                            st.download_button("Download Jawaban", open(s[1], "rb"), file_name=os.path.basename(s[1]), key=f"dl{s[1]}")
                    else:
                        st.info("Belum ada jawaban")

        with tab4:
            st.write("Laporan Absensi Siswa")
            class_code = st.text_input("Masukkan kode kelas untuk melihat absensi")
            kelas = get_class_by_code(class_code)
            if kelas:
                data = get_attendance_report(kelas[0])
                if data:
                    for row in data:
                        st.write(f"👩‍🎓 {row[0]} - 📅 {row[1]}")
                else:
                    st.info("Belum ada absensi")

    # =========================
    # Dashboard Siswa
    # =========================
    else:
        st.subheader("👩‍🎓 Dashboard Siswa")

        tab1, tab2, tab3, tab4 = st.tabs(["🔑 Join Kelas", "📖 Materi", "✅ Absensi", "📝 Tugas"])

        with tab1:
            st.write("Masukkan kode kelas untuk bergabung")
            class_code = st.text_input("Kode Kelas")
            if st.button("Join"):
                kelas = get_class_by_code(class_code)
                if kelas:
                    st.session_state.current_class = kelas
                    st.success(f"Berhasil join kelas {kelas[1]}")
                else:
                    st.error("Kode kelas tidak ditemukan")

        with tab2:
            if "current_class" in st.session_state:
                kelas = st.session_state.current_class
                st.write(f"Materi untuk kelas: {kelas[1]}")
                materials = get_materials(kelas[0])
                for m in materials:
                    st.markdown(f"### 📘 {m[2]}")
                    st.write(m[3])
                    if m[4]:
                        st.video(m[4])
            else:
                st.info("Silakan join kelas dulu")

        with tab3:
            if "current_class" in st.session_state:
                kelas = st.session_state.current_class
                if st.button("Isi Daftar Hadir"):
                    if mark_attendance(kelas[0], user[0]):
                        st.success("Absensi berhasil disimpan")
                    else:
                        st.warning("Anda sudah absen hari ini")
            else:
                st.info("Silakan join kelas dulu")

        with tab4:
            if "current_class" in st.session_state:
                kelas = st.session_state.current_class
                st.write(f"Tugas untuk kelas: {kelas[1]}")
                for a in get_assignments(kelas[0]):
                    st.markdown(f"### 📑 {a[1]}")
                    st.write(a[2])
                    if a[4]:
                        st.download_button("📥 Download Tugas", open(a[4], "rb"), file_name=os.path.basename(a[4]), key=f"dlstu{a[0]}")

                    uploaded = st.file_uploader("Upload Jawaban", type=["pdf", "docx", "txt"], key=f"jawaban{a[0]}")
                    if uploaded and st.button(f"Kumpulkan Jawaban {a[0]}"):
                        file_path = os.path.join(UPLOAD_DIR, f"{user[1]}_{uploaded.name}")
                        with open(file_path, "wb") as f:
                            f.write(uploaded.getbuffer())
                        submit_assignment(a[0], user[0], file_path)
                        st.success("Jawaban berhasil dikumpulkan!")
            else:
                st.info("Silakan join kelas dulu")
