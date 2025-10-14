import streamlit as st
import sqlite3
import datetime
import os

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

        # === Buat Kelas ===
        with tabs[0]:
            st.subheader("📘 Buat Kelas")
            cname = st.text_input("Nama Kelas")
            ccode = st.text_input("Kode Kelas Unik")
            if st.button("Buat Kelas"):
                if create_class(cname, ccode, user[0]):
                    st.success("Kelas berhasil dibuat!")
                else:
                    st.error("Kode kelas sudah digunakan!")

        # === Materi ===
        with tabs[1]:
            code = st.text_input("Masukkan kode kelas (materi)")
            kelas = get_class_by_code(code)
            if kelas:
                st.subheader(f"Materi untuk {kelas[1]}")
                title = st.text_input("Judul Materi")
                content = st.text_area("Isi Materi")
                video = st.text_input("Link Video (opsional)")
                if st.button("Tambah Materi"):
                    add_material(kelas[0], title, content, video)
                    st.success("Materi ditambahkan!")
                st.divider()
                for m in get_materials(kelas[0]):
                    st.markdown(f"### {m[2]}")
                    st.write(m[3])
                    if m[4]: st.video(m[4])

        # === Pre-Test ===
        with tabs[2]:
            code = st.text_input("Masukkan kode kelas (Pre-Test)")
            kelas = get_class_by_code(code)
            if kelas:
                st.subheader(f"Soal Pre-Test {kelas[1]}")
                q = st.text_input("Pertanyaan")
                a = st.text_input("Opsi A")
                b = st.text_input("Opsi B")
                c_ = st.text_input("Opsi C")
                d = st.text_input("Opsi D")
                correct = st.selectbox("Jawaban Benar", ["A", "B", "C", "D"])
                if st.button("Tambah Soal"):
                    add_pretest_question(kelas[0], q, a, b, c_, d, correct)
                    st.success("Soal berhasil ditambahkan!")
                st.divider()
                for s in get_pretest_questions(kelas[0]):
                    st.markdown(f"**{s[1]}. {s[2]}**")
                    st.write(f"A. {s[3]}  |  B. {s[4]}  |  C. {s[5]}  |  D. {s[6]}")
                    st.info(f"✅ Jawaban benar: {s[7]}")

        # === Tugas ===
        with tabs[3]:
            code = st.text_input("Kode Kelas (Tugas)")
            kelas = get_class_by_code(code)
            if kelas:
                title = st.text_input("Judul Tugas")
                desc = st.text_area("Deskripsi")
                file = st.file_uploader("Upload File (opsional)", type=["pdf", "docx", "txt"])
                if st.button("Upload Tugas"):
                    path = None
                    if file:
                        path = os.path.abspath(os.path.join(UPLOAD_DIR, file.name))
                        with open(path, "wb") as f:
                            f.write(file.getbuffer())
                    add_assignment(kelas[0], title, desc, path)
                    st.success("Tugas berhasil diupload!")
                st.divider()
                for t in get_assignments(kelas[0]):
                    st.markdown(f"**{t[1]}** - {t[2]}")

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
                        pdf_path = os.path.abspath(os.path.join(UPLOAD_DIR, pdf.name))
                        with open(pdf_path, "wb") as f:
                            f.write(pdf.getbuffer())
                    add_lkpd(kelas[0], title, flip, pdf_path)
                    st.success("LKPD ditambahkan!")
                st.divider()
                for l in get_lkpd(kelas[0]):
                    st.markdown(f"### {l[1]}")
                    if l[2]:
                        st.markdown(f"[🌐 Lihat Flipbook]({l[2]})")
                    if l[3]:
                        if os.path.exists(l[3]):
                            with open(l[3], "rb") as pdf_file:
                                st.download_button("📥 Download PDF", pdf_file, file_name=os.path.basename(l[3]))
                        else:
                            st.warning(f"⚠️ File PDF tidak ditemukan di path: {l[3]}")

        # === Absensi ===
        with tabs[5]:
            code = st.text_input("Kode Kelas (Absensi)")
            kelas = get_class_by_code(code)
            if kelas:
                data = get_attendance_report(kelas[0])
                if data:
                    for row in data:
                        st.write(f"👩‍🎓 {row[0]} - 📅 {row[1]}")
                else:
                    st.info("Belum ada absensi")

    # =========================
    # STUDENT
    # =========================
    else:
        tabs = st.tabs(["🔑 Join Kelas", "📖 Materi", "🧠 Pre-Test", "✅ Absensi", "📝 Tugas", "📕 LKPD"])

        # === Join ===
        with tabs[0]:
            code = st.text_input("Masukkan kode kelas")
            if st.button("Join"):
                kelas = get_class_by_code(code)
                if kelas:
                    st.session_state.current_class = kelas
                    st.success(f"Berhasil join kelas {kelas[1]}")
                else:
                    st.error("Kode kelas salah!")

        # === Materi ===
        with tabs[1]:
            if st.session_state.current_class:
                k = st.session_state.current_class
                for m in get_materials(k[0]):
                    st.markdown(f"### {m[2]}")
                    st.write(m[3])
                    if m[4]: st.video(m[4])
            else:
                st.info("Silakan join kelas dulu.")

        # === Pre-Test ===
        with tabs[2]:
            if st.session_state.current_class:
                k = st.session_state.current_class
                qs = get_pretest_questions(k[0])
                score = 0
                for q in qs:
                    st.write(f"**{q[2]}**")
                    opt = st.radio("Pilih jawaban", ["A", "B", "C", "D"], key=q[0])
                    if st.button(f"Kirim Jawaban {q[0]}"):
                        is_correct = 1 if opt == q[7] else 0
                        save_pretest_answer(q[0], user[0], opt, is_correct)
                        st.success("Jawaban disimpan!")
                        st.rerun()
                score = get_student_score(k[0], user[0])
                st.info(f"Skor saat ini: {score}/{len(qs)}")
            else:
                st.info("Silakan join kelas dulu.")

        # === Absensi ===
        with tabs[3]:
            if st.session_state.current_class:
                k = st.session_state.current_class
                if st.button("Isi Absensi"):
                    if mark_attendance(k[0], user[0]):
                        st.success("Absensi berhasil!")
                    else:
                        st.warning("Anda sudah absen hari ini")
            else:
                st.info("Join kelas dulu.")

        # === Tugas ===
        with tabs[4]:
            if st.session_state.current_class:
                k = st.session_state.current_class
                for a in get_assignments(k[0]):
                    st.markdown(f"### {a[1]}")
                    st.write(a[2])
                    if a[4]:
                        if os.path.exists(a[4]):
                            with open(a[4], "rb") as f:
                                st.download_button("📥 Download", f, file_name=os.path.basename(a[4]))
                        else:
                            st.warning(f"⚠️ File tugas tidak ditemukan di path: {a[4]}")
                    up = st.file_uploader("Upload Jawaban", key=f"ans{a[0]}")
                    if st.button(f"Kumpulkan {a[0]}"):
                        if up:
                            path = os.path.abspath(os.path.join(UPLOAD_DIR, f"{user[1]}_{up.name}"))
                            with open(path, "wb") as f:
                                f.write(up.getbuffer())
                            submit_assignment(a[0], user[0], path)
                            st.success("Jawaban dikumpulkan!")
            else:
                st.info("Join kelas dulu.")

        # === LKPD ===
        with tabs[5]:
            if st.session_state.current_class:
                k = st.session_state.current_class
                for l in get_lkpd(k[0]):
                    st.markdown(f"### {l[1]}")
                    if l[2]:
                        st.markdown(f"[🌐 Buka Flipbook]({l[2]})")
                    if l[3]:
                        if os.path.exists(l[3]):
                            with open(l[3], "rb") as pdf_file:
                                st.download_button("📥 Download PDF", pdf_file, file_name=os.path.basename(l[3]))
                        else:
                            st.warning(f"⚠️ File PDF tidak ditemukan di path: {l[3]}")
            else:
                st.info("Silakan join kelas dulu.")

