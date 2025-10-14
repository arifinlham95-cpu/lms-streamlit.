import streamlit as st
import sqlite3
import datetime
import os
import base64

# =========================
# DATABASE SETUP
# =========================
conn = sqlite3.connect('lms.db', check_same_thread=False)
c = conn.cursor()

# === Users ===
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)''')

# === Classes ===
c.execute('''CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name TEXT,
    class_code TEXT UNIQUE,
    teacher_id INTEGER
)''')

# === Materials ===
c.execute('''CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    title TEXT,
    content TEXT,
    video_url TEXT
)''')

# === Attendance ===
c.execute('''CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    student_id INTEGER,
    date TEXT
)''')

# === Assignments ===
c.execute('''CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    title TEXT,
    description TEXT,
    file_path TEXT
)''')

# === Submissions ===
c.execute('''CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER,
    student_id INTEGER,
    file_path TEXT,
    submitted_at TEXT
)''')

# === Pre-Test ===
c.execute('''CREATE TABLE IF NOT EXISTS pretest_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    question TEXT,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_option TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS pretest_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER,
    student_id INTEGER,
    selected_option TEXT,
    is_correct INTEGER
)''')

# === LKPD ===
c.execute('''CREATE TABLE IF NOT EXISTS lkpd (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER,
    title TEXT,
    flipbook_link TEXT,
    pdf_path TEXT
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

def add_assignment(class_id, title, description, file_path):
    c.execute("INSERT INTO assignments (class_id, title, description, file_path) VALUES (?, ?, ?, ?)", 
              (class_id, title, description, file_path))
    conn.commit()

def get_assignments(class_id):
    c.execute("SELECT * FROM assignments WHERE class_id=?", (class_id,))
    return c.fetchall()

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

# === Pre-test ===
def add_pretest_question(class_id, q, a, b, c_, d, correct):
    c.execute("INSERT INTO pretest_questions (class_id, question, option_a, option_b, option_c, option_d, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (class_id, q, a, b, c_, d, correct))
    conn.commit()

def get_pretest_questions(class_id):
    c.execute("SELECT * FROM pretest_questions WHERE class_id=?", (class_id,))
    return c.fetchall()

def save_pretest_answer(question_id, student_id, selected, is_correct):
    c.execute("INSERT INTO pretest_answers (question_id, student_id, selected_option, is_correct) VALUES (?, ?, ?, ?)",
              (question_id, student_id, selected, is_correct))
    conn.commit()

def get_student_score(class_id, student_id):
    c.execute("""SELECT COUNT(*) FROM pretest_answers pa
                 JOIN pretest_questions pq ON pa.question_id = pq.id
                 WHERE pq.class_id=? AND pa.student_id=? AND pa.is_correct=1""",
              (class_id, student_id))
    return c.fetchone()[0]

# === LKPD ===
def add_lkpd(class_id, title, flipbook_link, pdf_path):
    c.execute("INSERT INTO lkpd (class_id, title, flipbook_link, pdf_path) VALUES (?, ?, ?, ?)",
              (class_id, title, flipbook_link, pdf_path))
    conn.commit()

def get_lkpd(class_id):
    c.execute("SELECT * FROM lkpd WHERE class_id=?", (class_id,))
    return c.fetchall()

# =========================
# STREAMLIT APP
# =========================
st.set_page_config(page_title="COOK LMS", page_icon="📚")
st.title("📚 COOK LMS")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.current_class = None

# =========================
# LOGIN & REGISTER
# =========================
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

# =========================
# DASHBOARD
# =========================
else:
    user = st.session_state.user
    role = user[3]

    st.sidebar.write(f"👤 {user[1]} ({role})")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.current_class = None
        st.rerun()

    st.divider()
    st.header("🏫 Dashboard COOK LMS")

    if role == "Teacher":
        tabs = st.tabs(["📘 Kelas", "📂 Materi", "🧠 Pre-Test", "📑 Tugas", "📕 LKPD", "📋 Absensi"])

        # === LKPD ===
        with tabs[4]:
            code = st.text_input("Kode Kelas (LKPD)")
            kelas = get_class_by_code(code)
            if kelas:
                title = st.text_input("Judul LKPD")
                flip = st.text_input("Link Flipbook (opsional)")
                pdf = st.file_uploader("Upload PDF (opsional)", type=["pdf"])
                if st.button("Tambahkan LKPD"):
                    pdf_path = None
                    if pdf:
                        pdf_path = os.path.join(UPLOAD_DIR, pdf.name)
                        with open(pdf_path, "wb") as f: f.write(pdf.getbuffer())
                    add_lkpd(kelas[0], title, flip, pdf_path)
                    st.success("LKPD ditambahkan!")
                st.divider()
                for l in get_lkpd(kelas[0]):
                    st.markdown(f"### {l[1]}")
                    if l[2]:
                        st.markdown(f"[🌐 Buka Flipbook]({l[2]})")
                    if l[3]:
                        with open(l[3], "rb") as f:
                            st.download_button("📥 Download PDF", f, file_name=os.path.basename(l[3]))
                        # tampilkan seperti flipbook
                        base64_pdf = base64.b64encode(open(l[3], "rb").read()).decode("utf-8")
                        flip_view = f"""
                        <iframe 
                            src="data:application/pdf;base64,{base64_pdf}" 
                            width="100%" 
                            height="600" 
                            style="border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.15);">
                        </iframe>
                        """
                        st.markdown(flip_view, unsafe_allow_html=True)

    # === STUDENT ===
    else:
        tabs = st.tabs(["🔑 Join Kelas", "📖 Materi", "🧠 Pre-Test", "✅ Absensi", "📝 Tugas", "📕 LKPD"])

        # === LKPD ===
        with tabs[5]:
            if st.session_state.current_class:
                k = st.session_state.current_class
                for l in get_lkpd(k[0]):
                    st.markdown(f"### {l[1]}")
                    if l[2]:
                        st.markdown(f"[🌐 Buka Flipbook]({l[2]})")
                    if l[3]:
                        with open(l[3], "rb") as f:
                            st.download_button("📥 Download PDF", f, file_name=os.path.basename(l[3]))
                        base64_pdf = base64.b64encode(open(l[3], "rb").read()).decode("utf-8")
                        flip_view = f"""
                        <iframe 
                            src="data:application/pdf;base64,{base64_pdf}" 
                            width="100%" 
                            height="600" 
                            style="border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.15);">
                        </iframe>
                        """
                        st.markdown(flip_view, unsafe_allow_html=True)
            else:
                st.info("Silakan join kelas dulu.")
