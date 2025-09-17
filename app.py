import streamlit as st
import sqlite3
import pandas as pd
import hashlib

# === Fungsi bantu ===
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hash(password, hashed):
    return make_hash(password) == hashed

# === Koneksi database ===
conn = sqlite3.connect("lms.db")
c = conn.cursor()

def create_tables():
    c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS classes(id INTEGER PRIMARY KEY, class_name TEXT, code TEXT, teacher_id INT)")
    c.execute("CREATE TABLE IF NOT EXISTS enrollments(id INTEGER PRIMARY KEY, user_id INT, class_id INT)")
    c.execute("CREATE TABLE IF NOT EXISTS materials(id INTEGER PRIMARY KEY, class_id INT, title TEXT, file_path TEXT, video_url TEXT)")
    conn.commit()

create_tables()

# === UI ===
st.title("📚 COOK ")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    st.subheader("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Teacher", "Student"])
    if st.button("Daftar"):
        c.execute("INSERT INTO users(username,password,role) VALUES (?,?,?)", (username, make_hash(password), role))
        conn.commit()
        st.success("Akun berhasil dibuat! Silakan login.")

elif choice == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Masuk"):
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        data = c.fetchone()
        if data and check_hash(password, data[2]):
            st.success(f"Selamat datang, {username} ({data[3]})")
            # TODO: Tambahkan dashboard guru/siswa
        else:
            st.error("Username/password salah")
 if data[3] == "Teacher":
    st.subheader("📘 Dashboard Guru")

    # Buat kelas baru
    with st.expander("Buat Kelas Baru"):
        class_name = st.text_input("Nama Kelas")
        class_code = st.text_input("Kode Kelas (unik)")
        if st.button("Buat Kelas"):
            c.execute("INSERT INTO classes(class_name, code, teacher_id) VALUES (?,?,?)",
                      (class_name, class_code, data[0]))
            conn.commit()
            st.success(f"Kelas '{class_name}' berhasil dibuat dengan kode: {class_code}")

    # Upload materi
    with st.expander("Upload Materi"):
        c.execute("SELECT * FROM classes WHERE teacher_id=?", (data[0],))
        classes = c.fetchall()
        class_opt = {cls[1]: cls[0] for cls in classes}
        class_choice = st.selectbox("Pilih Kelas", list(class_opt.keys()))
        title = st.text_input("Judul Materi")
        file = st.file_uploader("Upload File (opsional)")
        video_url = st.text_input("Link Video YouTube (opsional)")
        if st.button("Simpan Materi"):
            filepath = None
            if file:
                filepath = file.name
                with open(filepath, "wb") as f:
                    f.write(file.getbuffer())
            c.execute("INSERT INTO materials(class_id, title, file_path, video_url) VALUES (?,?,?,?)",
                      (class_opt[class_choice], title, filepath, video_url))
            conn.commit()
            st.success("Materi berhasil ditambahkan")

elif data[3] == "Student":
    st.subheader("🎓 Dashboard Siswa")

    # Join kelas pakai kode
    with st.expander("Gabung Kelas"):
        join_code = st.text_input("Masukkan Kode Kelas")
        if st.button("Gabung"):
            c.execute("SELECT * FROM classes WHERE code=?", (join_code,))
            class_data = c.fetchone()
            if class_data:
                c.execute("INSERT INTO enrollments(user_id, class_id) VALUES (?,?)", (data[0], class_data[0]))
                conn.commit()
                st.success(f"Berhasil gabung ke kelas {class_data[1]}")
            else:
                st.error("Kode kelas tidak ditemukan")

    # Lihat materi
    with st.expander("Materi Kelas Saya"):
        c.execute("""SELECT classes.class_name, materials.title, materials.file_path, materials.video_url
                     FROM enrollments 
                     JOIN classes ON enrollments.class_id = classes.id
                     JOIN materials ON classes.id = materials.class_id
                     WHERE enrollments.user_id=?""", (data[0],))
        materi = c.fetchall()
        if materi:
            for row in materi:
                st.markdown(f"### 📘 {row[0]} - {row[1]}")
                if row[2]:
                    st.download_button("📂 Download Materi", data=open(row[2], "rb"), file_name=row[2])
                if row[3]:
                    st.video(row[3])
        else:
            st.info("Belum ada materi di kelas Anda")

def create_tables():
    c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS classes(id INTEGER PRIMARY KEY, class_name TEXT, code TEXT, teacher_id INT)")
    c.execute("CREATE TABLE IF NOT EXISTS enrollments(id INTEGER PRIMARY KEY, user_id INT, class_id INT)")
    c.execute("CREATE TABLE IF NOT EXISTS materials(id INTEGER PRIMARY KEY, class_id INT, title TEXT, file_path TEXT, video_url TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS attendance(id INTEGER PRIMARY KEY, class_id INT, user_id INT, date TEXT)")
    conn.commit()

with st.expander("📋 Lihat Daftar Hadir"):
    c.execute("SELECT * FROM classes WHERE teacher_id=?", (data[0],))
    classes = c.fetchall()
    if classes:
        class_opt = {cls[1]: cls[0] for cls in classes}
        class_choice = st.selectbox("Pilih Kelas", list(class_opt.keys()))
        if st.button("Tampilkan Absensi"):
            c.execute("""SELECT users.username, attendance.date 
                         FROM attendance 
                         JOIN users ON attendance.user_id = users.id
                         WHERE attendance.class_id=?""", (class_opt[class_choice],))
            rows = c.fetchall()
            if rows:
                df = pd.DataFrame(rows, columns=["Nama Siswa", "Tanggal Hadir"])
                st.dataframe(df)
            else:
                st.info("Belum ada data absensi untuk kelas ini.")

with st.expander("📋 Daftar Hadir"):
    c.execute("""SELECT classes.id, classes.class_name 
                 FROM enrollments 
                 JOIN classes ON enrollments.class_id = classes.id
                 WHERE enrollments.user_id=?""", (data[0],))
    kelas_saya = c.fetchall()
    if kelas_saya:
        class_opt = {cls[1]: cls[0] for cls in kelas_saya}
        class_choice = st.selectbox("Pilih Kelas", list(class_opt.keys()))
        if st.button("Saya Hadir Hari Ini"):
            from datetime import date
            today = str(date.today())
            c.execute("INSERT INTO attendance(class_id, user_id, date) VALUES (?,?,?)",
                      (class_opt[class_choice], data[0], today))
            conn.commit()
            st.success(f"Kehadiran dicatat untuk {today}")
    else:
        st.info("Anda belum bergabung di kelas manapun.")

