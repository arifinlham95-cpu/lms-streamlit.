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
st.title("📚 LMS Sederhana")

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
