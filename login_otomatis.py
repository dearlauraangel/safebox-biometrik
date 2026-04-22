import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os

# --- 1. KONFIGURASI HALAMAN & IKON ---
# Memuat logo.png sebagai ikon di tab browser
try:
    logo_img = Image.open("logo.png")
    st.set_page_config(page_title="SafeBox Biometrik", page_icon=logo_img, layout="centered")
except:
    st.set_page_config(page_title="SafeBox Biometrik", page_icon="🔐", layout="centered")

# --- 2. CSS CUSTOM UNTUK TAMPILAN MOBILE ---
st.markdown("""
    <style>
    .main {
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    /* Membuat tampilan input kamera lebih rapi di HP */
    .stCameraInput {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE SEDERHANA & FUNGSI ---
if not os.path.exists("wajah_terdaftar"):
    os.makedirs("wajah_terdaftar")

def ambil_daftar_sosmed():
    if not os.path.exists("sosmed.txt"):
        # Default jika file belum ada
        return [{"nama": "Instagram", "url": "https://www.instagram.com"}]
    daftar = []
    with open("sosmed.txt", "r") as f:
        for line in f:
            if "," in line:
                nama, url = line.strip().split(",", 1)
                daftar.append({"nama": nama, "url": url})
    return daftar

def simpan_sosmed_baru(nama, url):
    with open("sosmed.txt", "a") as f:
        f.write(f"{nama},{url}\n")

# --- 4. HEADER APLIKASI ---
# Menampilkan logo besar di tengah halaman
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image(Image.open("logo.png"), use_container_width=True)
    except:
        st.title("🔐")

st.markdown("<h2 style='text-align: center;'>SafeBox Biometrik</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Brankas Digital Berbasis Pengenalan Wajah</p>", unsafe_allow_html=True)
st.divider()

# --- 5. MENU NAVIGASI (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Pengaturan")
    menu = st.radio("Pilih Menu:", ["🔓 Buka Brankas", "👤 Daftar Wajah", "➕ Tambah Akun"])
    st.info("Pastikan pencahayaan cukup saat melakukan scan wajah.")

# --- 6. LOGIKA MENU ---

# MENU: DAFTAR WAJAH
if menu == "👤 Daftar Wajah":
    st.subheader("Registrasi Pemilik Baru")
    nama_user = st.text_input("Masukkan Nama Anda:")
    foto_regis = st.camera_input("Ambil Foto Profil")
    
    if foto_regis and nama_user:
        if st.button("Simpan Wajah ke Sistem"):
            img = Image.open(foto_regis).resize((300, 300))
            img.save(f"wajah_terdaftar/{nama_user}.jpg")
            st.success(f"Wajah {nama_user} berhasil didaftarkan!")

# MENU: TAMBAH AKUN
elif menu == "➕ Tambah Akun":
    st.subheader("Simpan Link Sosmed Baru")
    nama_link = st.text_input("Nama Aplikasi (Contoh: TikTok)")
    url_link = st.text_input("Alamat URL (Contoh: https://tiktok.com)")
    
    if st.button("Simpan Permanen"):
        if nama_link and url_link:
            simpan_sosmed_baru(nama_link, url_link)
            st.success("Akun berhasil disimpan ke brankas!")
        else:
            st.warning("Mohon isi semua data.")

# MENU: BUKA BRANKAS (LOGIN)
elif menu == "🔓 Buka Brankas":
    st.subheader("Verifikasi Biometrik")
    foto_login = st.camera_input("Scan Wajah untuk Masuk")
    
    if foto_login:
        # Proses gambar login
        img_login = Image.open(foto_login).resize((300, 300))
        img_login_cv = cv2.cvtColor(np.array(img_login), cv2.COLOR_RGB2BGR)
        
        # Ekstraksi fitur wajah sederhana (Histogram)
        hist_login = cv2.calcHist([img_login_cv], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        cv2.normalize(hist_login, hist_login)

        login_sukses = False
        nama_pemilik = ""

        # Cek ke database folder
        for file in os.listdir("wajah_terdaftar"):
            img_db = cv2.imread(f"wajah_terdaftar/{file}")
            if img_db is None: continue
            
            img_db = cv2.resize(img_db, (300, 300))
            hist_db = cv2.calcHist([img_db], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            cv2.normalize(hist_db, hist_db)
            
            # Bandingkan kemiripan (threshold 0.7)
            skor = cv2.compareHist(hist_login, hist_db, cv2.HISTCMP_CORREL)
            if skor > 0.7:
                login_sukses = True
                nama_pemilik = file.replace(".jpg", "")
                break

        if login_sukses:
            st.balloons()
            st.success(f"Selamat Datang, {nama_pemilik}!")
            st.write("### Isi Brankas Anda:")
            
            # Tampilkan tombol-tombol link sosmed
            daftar = ambil_daftar_sosmed()
            for item in daftar:
                st.link_button(f"🚀 Buka {item['nama']}", item['url'], use_container_width=True)
        else:
            st.error("Wajah tidak dikenali. Silakan daftar terlebih dahulu.")
