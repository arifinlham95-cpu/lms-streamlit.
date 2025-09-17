import streamlit as st
import sqlite3
import datetime

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

conn.commit()

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

# =========================
# STREAMLIT APP
# =========================
st.set_page_config(page_title="Mini LMS", page_icon="📚")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

st.title("📚 COOK")

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
                st.experimental_rerun()
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
        st.experimental_rerun()

    # =========================
    # Dashboard Guru
    # =========================
    if role == "Teacher":
        st.subheader("👨‍🏫 Dashboard Guru")

        tab1, tab2, tab3 = st.tabs(["📘 Buat Kelas", "📂 Upload Materi", "📋 Laporan Absensi"])

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
            st.write("Upload materi pembelajaran")
            class_code = st.text_input("Masukkan kode kelas untuk upload materi")
            kelas = get_class_by_code(class_code)
            if kelas:
                title = st.text_input("Judul Materi")
                content = st.text_area("Konten / Catatan Materi")
                video_url = st.text_input("URL Video (YouTube)")
                if st.button("Upload Materi"):
                    add_material(kelas[0], title, content, video_url)
                    st.success("Materi berhasil diupload!")
            else:
                st.info("Masukkan kode kelas valid")

        with tab3:
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

        tab1, tab2, tab3 = st.tabs(["🔑 Join Kelas", "📖 Materi", "✅ Absensi"])

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

