import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os

# --- PENGATURAN TAMPILAN ---
st.set_page_config(page_title="SafeBox Biometrik", page_icon="🔐")
st.title("🔐 SafeBox Biometrik")
st.write("Sistem keamanan berbasis wajah untuk melindungi akses akun media sosial Anda.")

# --- FUNGSI PENYIMPANAN DATA SOSMED ---
def simpan_sosmed(nama, url):
    with open("sosmed.txt", "a") as f:
        f.write(f"{nama},{url}\n")

def ambil_sosmed():
    # Jika file belum ada, berikan contoh default
    if not os.path.exists("sosmed.txt"):
        return [{"nama": "Instagram", "url": "https://www.instagram.com"}]
    
    daftar = []
    with open("sosmed.txt", "r") as f:
        for line in f:
            if "," in line:
                nama, url = line.strip().split(",", 1)
                daftar.append({"nama": nama, "url": url})
    return daftar

# --- DATABASE WAJAH ---
if not os.path.exists("wajah_terdaftar"):
    os.makedirs("wajah_terdaftar")

# --- MENU NAVIGASI ---
menu = ["Daftar Wajah Baru", "Buka Brankas Akun", "Kelola Link Akun"]
pilihan = st.sidebar.selectbox("Menu Utama", menu)

# 1. FITUR PENDAFTARAN
if pilihan == "Daftar Wajah Baru":
    st.subheader("📝 Registrasi Pemilik Akses")
    nama = st.text_input("Nama Lengkap Pengguna")
    foto = st.camera_input("Ambil Foto Profil untuk Database")
    if foto and nama:
        img = Image.open(foto).resize((300, 300))
        img.save(f"wajah_terdaftar/{nama}.jpg")
        st.success(f"Akses untuk {nama} berhasil didaftarkan!")

# 2. FITUR TAMBAH LINK
elif pilihan == "Kelola Link Akun":
    st.subheader("➕ Tambah Link Media Sosial")
    st.write("Tambahkan link baru yang ingin Anda sembunyikan di dalam brankas.")
    
    nama_baru = st.text_input("Nama Layanan (Contoh: YouTube, Pinterest)")
    url_baru = st.text_input("URL Tujuan (Contoh: https://...)")
    
    if st.button("Simpan ke Brankas"):
        if nama_baru and url_baru:
            simpan_sosmed(nama_baru, url_baru)
            st.success(f"Link {nama_baru} berhasil ditambahkan!")
        else:
            st.error("Mohon isi semua data link!")

# 3. FITUR LOGIN / BUKA BRANKAS
elif pilihan == "Buka Brankas Akun":
    st.subheader("🔍 Verifikasi Identitas")
    foto_login = st.camera_input("Scanner Wajah Aktif")
    
    if foto_login:
        # Analisis foto yang diambil
        img_login = Image.open(foto_login).resize((300, 300))
        img_login_cv = cv2.cvtColor(np.array(img_login), cv2.COLOR_RGB2BGR)
        hist_login = cv2.calcHist([img_login_cv], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        cv2.normalize(hist_login, hist_login)

        ditemukan = False
        nama_user = ""
        
        # Bandingkan dengan folder database
        files = os.listdir("wajah_terdaftar")
        if len(files) == 0:
            st.warning("Belum ada wajah terdaftar. Silakan daftar terlebih dahulu.")
        else:
            for file in files:
                img_db_path = f"wajah_terdaftar/{file}"
                img_db = cv2.imread(img_db_path)
                if img_db is None: continue
                
                img_db = cv2.resize(img_db, (300, 300))
                hist_db = cv2.calcHist([img_db], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                cv2.normalize(hist_db, hist_db)
                
                # Skor kemiripan
                if cv2.compareHist(hist_login, hist_db, cv2.HISTCMP_CORREL) > 0.7:
                    ditemukan = True
                    nama_user = os.path.splitext(file)[0]
                    break

            if ditemukan:
                st.success(f"Verifikasi Berhasil! Selamat Datang, {nama_user}.")
                st.balloons()
                
                st.divider()
                st.subheader("📱 Akun Terproteksi Anda")
                
                # Menampilkan link dari file
                daftar_sosmed = ambil_sosmed()
                for item in daftar_sosmed:
                    st.link_button(f"🔗 Buka {item['nama']}", item['url'])
            else:
                st.error("Wajah tidak dikenali! Akses ditolak.")