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

# === CRUD MATERIALS ===
def add_material(class_id, title, content, video_url):
    c.execute("INSERT INTO materials (class_id, title, content, video_url) VALUES (?, ?, ?, ?)", 
              (class_id, title, content, video_url))
    conn.commit()

def update_material(mid, title, content, video_url):
    c.execute("UPDATE materials SET title=?, content=?, video_url=? WHERE id=?", (title, content, video_url, mid))
    conn.commit()

def delete_material(mid):
    c.execute("DELETE FROM materials WHERE id=?", (mid,))
    conn.commit()

def get_materials(class_id):
    c.execute("SELECT * FROM materials WHERE class_id=?", (class_id,))
    return c.fetchall()

# === CRUD ASSIGNMENTS ===
def add_assignment(class_id, title, description, file_path):
    c.execute("INSERT INTO assignments (class_id, title, description, file_path) VALUES (?, ?, ?, ?)", 
              (class_id, title, description, file_path))
    conn.commit()

def update_assignment(aid, title, description):
    c.execute("UPDATE assignments SET title=?, description=? WHERE id=?", (title, description, aid))
    conn.commit()

def delete_assignment(aid):
    c.execute("DELETE FROM assignments WHERE id=?", (aid,))
    conn.commit()

def get_assignments(class_id):
    c.execute("SELECT * FROM assignments WHERE class_id=?", (class_id,))
    return c.fetchall()

# === CRUD PRETEST ===
def add_pretest_question(class_id, q, a, b, c_, d, correct):
    c.execute("INSERT INTO pretest_questions (class_id, question, option_a, option_b, option_c, option_d, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (class_id, q, a, b, c_, d, correct))
    conn.commit()

def update_pretest_question(qid, question, a, b, c_, d, correct):
    c.execute("UPDATE pretest_questions SET question=?, option_a=?, option_b=?, option_c=?, option_d=?, correct_option=? WHERE id=?", 
              (question, a, b, c_, d, correct, qid))
    conn.commit()

def delete_pretest_question(qid):
    c.execute("DELETE FROM pretest_questions WHERE id=?", (qid,))
    conn.commit()

def get_pretest_questions(class_id):
    c.execute("SELECT * FROM pretest_questions WHERE class_id=?", (class_id,))
    return c.fetchall()

# === CRUD LKPD ===
def add_lkpd(class_id, title, flipbook_link, pdf_path):
    c.execute("INSERT INTO lkpd (class_id, title, flipbook_link, pdf_path) VALUES (?, ?, ?, ?)",
              (class_id, title, flipbook_link, pdf_path))
    conn.commit()

def update_lkpd(lid, title, flip, pdf_path):
    c.execute("UPDATE lkpd SET title=?, flipbook_link=?, pdf_path=? WHERE id=?", (title, flip, pdf_path, lid))
    conn.commit()

def delete_lkpd(lid):
    c.execute("DELETE FROM lkpd WHERE id=?", (lid,))
    conn.commit()

def get_lkpd(class_id):
    c.execute("SELECT * FROM lkpd WHERE class_id=?", (class_id,))
    return c.fetchall()

# === Attendance ===
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
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✏️ Edit {m[0]}"):
                            new_title = st.text_input("Edit Judul", value=m[2], key=f"title{m[0]}")
                            new_content = st.text_area("Edit Isi", value=m[3], key=f"cont{m[0]}")
                            new_video = st.text_input("Edit Video", value=m[4], key=f"vid{m[0]}")
                            if st.button(f"Simpan Perubahan {m[0]}"):
                                update_material(m[0], new_title, new_content, new_video)
                                st.success("Materi diperbarui!")
                                st.rerun()
                    with col2:
                        if st.button(f"🗑️ Hapus {m[0]}"):
                            delete_material(m[0])
                            st.warning("Materi dihapus!")
                            st.rerun()

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
                    st.info(f"✅ Jawaban benar: {s[7]}")
                    if st.button(f"🗑️ Hapus Soal {s[0]}"):
                        delete_pretest_question(s[0])
                        st.warning("Soal dihapus!")
                        st.rerun()

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
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✏️ Edit {t[0]}"):
                            new_title = st.text_input("Edit Judul", value=t[1], key=f"t{t[0]}")
                            new_desc = st.text_area("Edit Deskripsi", value=t[2], key=f"d{t[0]}")
                            if st.button(f"Simpan Perubahan Tugas {t[0]}"):
                                update_assignment(t[0], new_title, new_desc)
                                st.success("Tugas diperbarui!")
                                st.rerun()
                    with col2:
                        if st.button(f"🗑️ Hapus {t[0]}"):
                            delete_assignment(t[0])
                            st.warning("Tugas dihapus!")
                            st.rerun()

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
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✏️ Edit LKPD {l[0]}"):
                            new_title = st.text_input("Edit Judul", value=l[1], key=f"lt{l[0]}")
                            new_flip = st.text_input("Edit Link", value=l[2], key=f"lf{l[0]}")
                            new_pdf = st.file_uploader("Upload Ulang PDF", type=["pdf"], key=f"lp{l[0]}")
                            pdf_path = l[3]
                            if new_pdf:
                                pdf_path = os.path.abspath(os.path.join(UPLOAD_DIR, new_pdf.name))
                                with open(pdf_path, "wb") as f:
                                    f.write(new_pdf.getbuffer())
                            if st.button(f"Simpan LKPD {l[0]}"):
                                update_lkpd(l[0], new_title, new_flip, pdf_path)
                                st.success("LKPD diperbarui!")
                                st.rerun()
                    with col2:
                        if st.button(f"🗑️ Hapus LKPD {l[0]}"):
                            delete_lkpd(l[0])
                            st.warning("LKPD dihapus!")
                            st.rerun()

