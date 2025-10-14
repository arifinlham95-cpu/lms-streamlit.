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

def update_class(class_id, new_name, new_code):
    try:
        c.execute("UPDATE classes SET class_name=?, class_code=? WHERE id=?", (new_name, new_code, class_id))
        conn.commit()
        return True
    except:
        return False

def delete_class(class_id):
    # optional: delete related rows (materials, assignments, lkpd, pretest, attendance, submissions)
    # delete files from disk for assignments, submissions, lkpd
    c.execute("SELECT file_path FROM assignments WHERE class_id=?", (class_id,))
    for row in c.fetchall():
        if row and row[0] and os.path.exists(row[0]):
            try: os.remove(row[0])
            except: pass
    c.execute("SELECT file_path FROM submissions WHERE assignment_id IN (SELECT id FROM assignments WHERE class_id=?)", (class_id,))
    for row in c.fetchall():
        if row and row[0] and os.path.exists(row[0]):
            try: os.remove(row[0])
            except: pass
    c.execute("SELECT pdf_path FROM lkpd WHERE class_id=?", (class_id,))
    for row in c.fetchall():
        if row and row[0] and os.path.exists(row[0]):
            try: os.remove(row[0])
            except: pass

    c.execute("DELETE FROM materials WHERE class_id=?", (class_id,))
    c.execute("DELETE FROM assignments WHERE class_id=?", (class_id,))
    c.execute("DELETE FROM submissions WHERE assignment_id IN (SELECT id FROM assignments WHERE class_id=?)", (class_id,))
    c.execute("DELETE FROM pretest_questions WHERE class_id=?", (class_id,))
    c.execute("DELETE FROM pretest_answers WHERE question_id NOT IN (SELECT id FROM pretest_questions)")
    c.execute("DELETE FROM lkpd WHERE class_id=?", (class_id,))
    c.execute("DELETE FROM attendance WHERE class_id=?", (class_id,))
    c.execute("DELETE FROM classes WHERE id=?", (class_id,))
    conn.commit()

def get_class_by_code(class_code):
    c.execute("SELECT * FROM classes WHERE class_code=?", (class_code,))
    return c.fetchone()

def add_material(class_id, title, content, video_url):
    c.execute("INSERT INTO materials (class_id, title, content, video_url) VALUES (?, ?, ?, ?)", 
              (class_id, title, content, video_url))
    conn.commit()

def update_material(material_id, title, content, video_url):
    c.execute("UPDATE materials SET title=?, content=?, video_url=? WHERE id=?", (title, content, video_url, material_id))
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

def add_assignment(class_id, title, description, file_path):
    c.execute("INSERT INTO assignments (class_id, title, description, file_path) VALUES (?, ?, ?, ?)", 
              (class_id, title, description, file_path))
    conn.commit()

def update_assignment(assignment_id, title, description):
    c.execute("UPDATE assignments SET title=?, description=? WHERE id=?", (title, description, assignment_id))
    conn.commit()

def delete_assignment(assignment_id):
    # remove file if exists
    c.execute("SELECT file_path FROM assignments WHERE id=?", (assignment_id,))
    row = c.fetchone()
    if row and row[0] and os.path.exists(row[0]):
        try: os.remove(row[0])
        except: pass
    # remove submissions files
    c.execute("SELECT file_path FROM submissions WHERE assignment_id=?", (assignment_id,))
    for r in c.fetchall():
        if r and r[0] and os.path.exists(r[0]):
            try: os.remove(r[0])
            except: pass
    c.execute("DELETE FROM submissions WHERE assignment_id=?", (assignment_id,))
    c.execute("DELETE FROM assignments WHERE id=?", (assignment_id,))
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
    c.execute("""SELECT s.id, u.username, s.file_path, s.submitted_at, s.student_id 
                 FROM submissions s 
                 JOIN users u ON s.student_id = u.id 
                 WHERE s.assignment_id=?""", (assignment_id,))
    return c.fetchall()

def delete_submission(submission_id):
    c.execute("SELECT file_path FROM submissions WHERE id=?", (submission_id,))
    row = c.fetchone()
    if row and row[0] and os.path.exists(row[0]):
        try: os.remove(row[0])
        except: pass
    c.execute("DELETE FROM submissions WHERE id=?", (submission_id,))
    conn.commit()

# === Pre-test ===
def add_pretest_question(class_id, q, a, b, c_, d, correct):
    c.execute("INSERT INTO pretest_questions (class_id, question, option_a, option_b, option_c, option_d, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (class_id, q, a, b, c_, d, correct))
    conn.commit()

def update_pretest_question(qid, q, a, b, c_, d, correct):
    c.execute("UPDATE pretest_questions SET question=?, option_a=?, option_b=?, option_c=?, option_d=?, correct_option=? WHERE id=?",
              (q, a, b, c_, d, correct, qid))
    conn.commit()

def delete_pretest_question(qid):
    c.execute("DELETE FROM pretest_answers WHERE question_id=?", (qid,))
    c.execute("DELETE FROM pretest_questions WHERE id=?", (qid,))
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

def update_lkpd(lid, title, flipbook_link):
    c.execute("UPDATE lkpd SET title=?, flipbook_link=? WHERE id=?", (title, flipbook_link, lid))
    conn.commit()

def delete_lkpd(lid):
    c.execute("SELECT pdf_path FROM lkpd WHERE id=?", (lid,))
    row = c.fetchone()
    if row and row[0] and os.path.exists(row[0]):
        try: os.remove(row[0])
        except: pass
    c.execute("DELETE FROM lkpd WHERE id=?", (lid,))
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
            st.divider()
            # List kelas milik guru
            c.execute("SELECT * FROM classes WHERE teacher_id=?", (user[0],))
            my_classes = c.fetchall()
            for cls in my_classes:
                st.markdown(f"### {cls[1]}  —  `{cls[2]}`")
                with st.expander("Edit / Hapus Kelas"):
                    new_name = st.text_input("Nama Kelas", value=cls[1], key=f"class_name_{cls[0]}")
                    new_code = st.text_input("Kode Kelas", value=cls[2], key=f"class_code_{cls[0]}")
                    col1, col2 = st.columns(2)
                    if col1.button("Simpan Perubahan", key=f"save_class_{cls[0]}"):
                        if update_class(cls[0], new_name, new_code):
                            st.success("Kelas diperbarui!")
                            st.experimental_rerun()
                        else:
                            st.error("Gagal memperbarui (mungkin kode duplikat).")
                    if col2.button("Hapus Kelas", key=f"del_class_{cls[0]}"):
                        delete_class(cls[0])
                        st.success("Kelas dan data terkait dihapus.")
                        st.experimental_rerun()

        # === Materi ===
        with tabs[1]:
            code = st.text_input("Masukkan kode kelas (materi)", key="materi_code_in")
            kelas = get_class_by_code(code)
            if kelas:
                st.subheader(f"Materi untuk {kelas[1]}")
                title = st.text_input("Judul Materi", key="materi_title_in")
                content = st.text_area("Isi Materi", key="materi_content_in")
                video = st.text_input("Link Video (opsional)", key="materi_video_in")
                if st.button("Tambah Materi"):
                    add_material(kelas[0], title, content, video)
                    st.success("Materi ditambahkan!")
                    st.experimental_rerun()
                st.divider()
                for m in get_materials(kelas[0]):
                    st.markdown(f"### {m[2]}")
                    st.write(m[3])
                    if m[4]: st.video(m[4])
                    with st.expander("Edit / Hapus Materi"):
                        new_title = st.text_input("Judul", value=m[2], key=f"mat_title_{m[0]}")
                        new_content = st.text_area("Konten", value=m[3], key=f"mat_content_{m[0]}")
                        new_video = st.text_input("Video URL", value=m[4] or "", key=f"mat_video_{m[0]}")
                        c1, c2 = st.columns(2)
                        if c1.button("Simpan Materi", key=f"save_mat_{m[0]}"):
                            update_material(m[0], new_title, new_content, new_video)
                            st.success("Materi diperbarui.")
                            st.experimental_rerun()
                        if c2.button("Hapus Materi", key=f"del_mat_{m[0]}"):
                            delete_material(m[0])
                            st.success("Materi dihapus.")
                            st.experimental_rerun()

        # === Pre-Test ===
        with tabs[2]:
            code = st.text_input("Masukkan kode kelas (Pre-Test)", key="pretest_code_in")
            kelas = get_class_by_code(code)
            if kelas:
                st.subheader(f"Soal Pre-Test {kelas[1]}")
                q = st.text_input("Pertanyaan", key="pre_q_in")
                a = st.text_input("Opsi A", key="pre_a_in")
                b = st.text_input("Opsi B", key="pre_b_in")
                c_ = st.text_input("Opsi C", key="pre_c_in")
                d = st.text_input("Opsi D", key="pre_d_in")
                correct = st.selectbox("Jawaban Benar", ["A", "B", "C", "D"], key="pre_correct_in")
                if st.button("Tambah Soal"):
                    add_pretest_question(kelas[0], q, a, b, c_, d, correct)
                    st.success("Soal berhasil ditambahkan!")
                    st.experimental_rerun()
                st.divider()
                for s in get_pretest_questions(kelas[0]):
                    st.markdown(f"**{s[2]}**")
                    st.write(f"A. {s[3]}  |  B. {s[4]}  |  C. {s[5]}  |  D. {s[6]}")
                    st.info(f"✅ Jawaban benar: {s[7]}")
                    with st.expander("Edit / Hapus Soal"):
                        new_q = st.text_input("Pertanyaan", value=s[2], key=f"pre_q_{s[0]}")
                        new_a = st.text_input("A", value=s[3], key=f"pre_a_{s[0]}")
                        new_b = st.text_input("B", value=s[4], key=f"pre_b_{s[0]}")
                        new_c = st.text_input("C", value=s[5], key=f"pre_c_{s[0]}")
                        new_d = st.text_input("D", value=s[6], key=f"pre_d_{s[0]}")
                        new_correct = st.selectbox("Jawaban Benar", ["A","B","C","D"], index=["A","B","C","D"].index(s[7]), key=f"pre_correct_{s[0]}")
                        col1, col2 = st.columns(2)
                        if col1.button("Simpan Soal", key=f"save_pre_{s[0]}"):
                            update_pretest_question(s[0], new_q, new_a, new_b, new_c, new_d, new_correct)
                            st.success("Soal diperbarui.")
                            st.experimental_rerun()
                        if col2.button("Hapus Soal", key=f"del_pre_{s[0]}"):
                            delete_pretest_question(s[0])
                            st.success("Soal dihapus.")
                            st.experimental_rerun()

        # === Tugas ===
        with tabs[3]:
            code = st.text_input("Kode Kelas (Tugas)", key="task_code_in")
            kelas = get_class_by_code(code)
            if kelas:
                title = st.text_input("Judul Tugas", key="task_title_in")
                desc = st.text_area("Deskripsi", key="task_desc_in")
                file = st.file_uploader("Upload File (opsional)", type=["pdf", "docx", "txt"], key="task_file_in")
                if st.button("Upload Tugas"):
                    path = None
                    if file:
                        path = os.path.abspath(os.path.join(UPLOAD_DIR, file.name))
                        with open(path, "wb") as f:
                            f.write(file.getbuffer())
                    add_assignment(kelas[0], title, desc, path)
                    st.success("Tugas berhasil diupload!")
                    st.experimental_rerun()
                st.divider()
                for t in get_assignments(kelas[0]):
                    st.markdown(f"**{t[1]}** - {t[2]}")
                    if t[4]:
                        if os.path.exists(t[4]):
                            with open(t[4], "rb") as f:
                                st.download_button("📥 Download", f, file_name=os.path.basename(t[4]), key=f"dl_assign_{t[0]}")
                        else:
                            st.warning(f"⚠️ File tugas tidak ditemukan di path: {t[4]}")
                    with st.expander("Edit / Hapus Tugas & Lihat Submissions"):
                        new_title = st.text_input("Judul", value=t[1], key=f"assign_title_{t[0]}")
                        new_desc = st.text_area("Deskripsi", value=t[2], key=f"assign_desc_{t[0]}")
                        c1, c2 = st.columns(2)
                        if c1.button("Simpan Tugas", key=f"save_assign_{t[0]}"):
                            update_assignment(t[0], new_title, new_desc)
                            st.success("Tugas diperbarui.")
                            st.experimental_rerun()
                        if c2.button("Hapus Tugas", key=f"del_assign_{t[0]}"):
                            delete_assignment(t[0])
                            st.success("Tugas dan submissions terkait dihapus.")
                            st.experimental_rerun()
                        st.markdown("**Submissions:**")
                        subs = get_submissions(t[0])
                        if subs:
                            for sub in subs:
                                st.write(f"{sub[1]} — {sub[3]}")
                                if sub[2]:
                                    if os.path.exists(sub[2]):
                                        with open(sub[2], "rb") as sf:
                                            st.download_button("📥 Download Submission", sf, file_name=os.path.basename(sub[2]), key=f"dl_sub_{sub[0]}")
                                    else:
                                        st.warning(f"File submission tidak ditemukan: {sub[2]}")
                                if st.button("Hapus Submission", key=f"del_sub_{sub[0]}"):
                                    delete_submission(sub[0])
                                    st.success("Submission dihapus.")
                                    st.experimental_rerun()
                        else:
                            st.info("Belum ada submission.")

        # === LKPD ===
        with tabs[4]:
            code = st.text_input("Kode Kelas (LKPD)", key="lkpd_code_in")
            kelas = get_class_by_code(code)
            if kelas:
                title = st.text_input("Judul LKPD", key="lkpd_title_in")
                flip = st.text_input("Link Flipbook (opsional)", key="lkpd_flip_in")
                pdf = st.file_uploader("Upload PDF (opsional)", type=["pdf"], key="lkpd_pdf_in")
                if st.button("Tambahkan LKPD"):
                    pdf_path = None
                    if pdf:
                        pdf_path = os.path.abspath(os.path.join(UPLOAD_DIR, pdf.name))
                        with open(pdf_path, "wb") as f:
                            f.write(pdf.getbuffer())
                    add_lkpd(kelas[0], title, flip, pdf_path)
                    st.success("LKPD ditambahkan!")
                    st.experimental_rerun()
                st.divider()
                for l in get_lkpd(kelas[0]):
                    st.markdown(f"### {l[1]}")
                    if l[2]:
                        st.markdown(f"[🌐 Lihat Flipbook]({l[2]})")
                    if l[3]:
                        if os.path.exists(l[3]):
                            with open(l[3], "rb") as pdf_file:
                                st.download_button("📥 Download PDF", pdf_file, file_name=os.path.basename(l[3]), key=f"dl_lkpd_{l[0]}")
                        else:
                            st.warning(f"⚠️ File PDF tidak ditemukan di path: {l[3]}")
                    with st.expander("Edit / Hapus LKPD"):
                        new_title = st.text_input("Judul", value=l[1], key=f"lkpd_title_{l[0]}")
                        new_flip = st.text_input("Flipbook Link", value=l[2] or "", key=f"lkpd_flip_{l[0]}")
                        c1, c2 = st.columns(2)
                        if c1.button("Simpan LKPD", key=f"save_lkpd_{l[0]}"):
                            update_lkpd(l[0], new_title, new_flip)
                            st.success("LKPD diperbarui.")
                            st.experimental_rerun()
                        if c2.button("Hapus LKPD", key=f"del_lkpd_{l[0]}"):
                            delete_lkpd(l[0])
                            st.success("LKPD dihapus.")
                            st.experimental_rerun()

        # === Absensi ===
        with tabs[5]:
            code = st.text_input("Kode Kelas (Absensi)", key="att_code_in")
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
            code = st.text_input("Masukkan kode kelas", key="student_join_code")
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
                    opt = st.radio("Pilih jawaban", ["A", "B", "C", "D"], key=f"stu_q_{q[0]}")
                    if st.button(f"Kirim Jawaban {q[0]}", key=f"send_q_{q[0]}"):
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
                st.divider()
                # show student's attendance history in class
                c.execute("SELECT date FROM attendance WHERE class_id=? AND student_id=?", (k[0], user[0]))
                rows = c.fetchall()
                if rows:
                    for r in rows:
                        st.write(f"📅 {r[0]}")
                else:
                    st.info("Belum ada absensi Anda.")
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
                                st.download_button("📥 Download", f, file_name=os.path.basename(a[4]), key=f"stu_dl_assign_{a[0]}")
                        else:
                            st.warning(f"⚠️ File tugas tidak ditemukan di path: {a[4]}")
                    up = st.file_uploader("Upload Jawaban", key=f"ans{a[0]}")
                    if st.button(f"Kumpulkan {a[0]}", key=f"kumpul_{a[0]}"):
                        if up:
                            path = os.path.abspath(os.path.join(UPLOAD_DIR, f"{user[1]}_{up.name}"))
                            with open(path, "wb") as f:
                                f.write(up.getbuffer())
                            submit_assignment(a[0], user[0], path)
                            st.success("Jawaban dikumpulkan!")
                            st.experimental_rerun()
                    # show student's own submissions with delete option
                    subs = get_submissions(a[0])
                    for sub in subs:
                        if sub[4] == user[0]:
                            st.write(f"Anda mengumpulkan: {sub[3]}")
                            if sub[2] and os.path.exists(sub[2]):
                                with open(sub[2], "rb") as sf:
                                    st.download_button("📥 Download Jawaban Saya", sf, file_name=os.path.basename(sub[2]), key=f"stu_dl_sub_{sub[0]}")
                            if st.button("Hapus Jawaban Saya", key=f"stu_del_sub_{sub[0]}"):
                                delete_submission(sub[0])
                                st.success("Jawaban Anda dihapus.")
                                st.experimental_rerun()
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
                                st.download_button("📥 Download PDF", pdf_file, file_name=os.path.basename(l[3]), key=f"stu_dl_lkpd_{l[0]}")
                        else:
                            st.warning(f"⚠️ File PDF tidak ditemukan di path: {l[3]}")
                    # students cannot edit/delete LKPD (teacher-only)
            else:
                st.info("Silakan join kelas dulu.")

