import streamlit as st
import google.generativeai as genai
import os
import time # Untuk simulasi delay balasan

# ==============================================================================
# PENGATURAN API KEY DAN MODEL (PENTING! UBAH SESUAI KEBUTUHAN ANDA)
# ==============================================================================

# GANTI INI DENGAN API KEY GEMINI ANDA!
# Catatan: Di Streamlit, disarankan menggunakan st.secrets atau environment variable.
# Untuk demo cepat, kita gunakan variabel langsung.
# JANGAN BAGIKAN KODE INI DENGAN API KEY DI DALAMNYA KE PUBLIK.
# HARAP GANTI "AIzaSyB3URVyEAiCVeUa-9yc_F-SiUsu0yEy_kE" DENGAN API KEY ASLI ANDA!
API_KEY = "AIzaSyB3URVyEAiCVeUa-9yc_F-SiUsu0yEy_kE" 

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT (INI BAGIAN YANG BISA SISWA MODIFIKASI!)
# ==============================================================================

# Definisikan peran chatbot Anda di sini.
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Kamu adalah ahli PPKN. Beri KAN MACAM MACAM SILA PANCASILA. Jawaban singkat dan JELAS . Tolak pertanyaan non-PPKN."]
    },
    {
        "role": "model",
        "parts": ["Baik! Berikan MACAM MACAM SILA PANCASILA untuk saya ceritakan sejarahnya."]
    }
]

# ==============================================================================
# FUNGSI UTAMA STREAMLIT
# ==============================================================================

st.set_page_config(page_title="🤖 Chatbot PPKN Gemini", layout="wide")
st.title("🤖 Chatbot Ahli PPKN (Gemini & Streamlit)")
st.caption(f"Powered by Google Gemini ({MODEL_NAME})")

# Cek apakah API Key sudah diatur
if API_KEY == "AIzaSyB3URVyEAiCVeUa-9yc_F-SiUsu0yEy_kE" or not API_KEY:
    st.error("⚠️ **Peringatan**: API Key belum diatur. Harap ganti `AIzaSyB3URVyEAiCVeUa-9yc_F-SiUsu0yEy_kE` dengan API Key Gemini Anda yang valid.")
    st.stop()

# --- Fungsi Inisialisasi Model dan Chat ---
def initialize_gemini():
    """Mengkonfigurasi Gemini API dan menginisialisasi sesi chat."""
    if "chat" not in st.session_state:
        try:
            # 1. Konfigurasi API
            genai.configure(api_key=API_KEY)
            
            # 2. Inisialisasi Model
            model = genai.GenerativeModel(
                MODEL_NAME,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4, 
                    max_output_tokens=500 
                )
            )
            
            # 3. Memulai Sesi Chat
            # Gunakan st.session_state.history untuk menyimpan riwayat chat yang tampil di UI
            if "history" not in st.session_state:
                st.session_state.history = INITIAL_CHATBOT_CONTEXT.copy()

            # Memulai chat dengan riwayat awal (konteks)
            st.session_state.chat = model.start_chat(history=st.session_state.history)
            
            # Hapus pesan pertama dari role "user" di riwayat yang ditampilkan
            # agar tidak mengganggu tampilan (hanya untuk instruksi sistem)
            # Jika Anda ingin menampilkan pesan user pertama, hapus blok ini.
            if st.session_state.history[0]["role"] == "user":
                del st.session_state.history[0]
                
        except Exception as e:
            st.error(f"❌ **Kesalahan Inisialisasi Gemini**: {e}")
            st.stop()
            
# Panggil inisialisasi
initialize_gemini()

# --- Tampilkan Riwayat Chat ---
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["parts"][0])
        
# --- Input Pengguna ---
if prompt := st.chat_input("Tanyakan sesuatu tentang PPKN..."):
    # 1. Tambahkan input pengguna ke riwayat dan tampilkan
    st.session_state.history.append({"role": "user", "parts": [prompt]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Kirim pesan ke Gemini dan tampilkan balasan
    with st.chat_message("model"):
        with st.spinner("Chatbot: (Sedang membalas...)"):
            try:
                # Kirim input pengguna ke model.
                # Kita kirim prompt, karena riwayat sudah dikelola di st.session_state.chat
                # Meskipun di demo ini, st.session_state.chat diinisialisasi sekali,
                # metode .send_message() tetap yang benar untuk interaksi chat berkelanjutan.
                response = st.session_state.chat.send_message(prompt, request_options={"timeout": 60})
                
                # Tambahkan balasan model ke riwayat
                if response and response.text:
                    st.session_state.history.append({"role": "model", "parts": [response.text]})
                    st.markdown(response.text)
                else:
                    error_msg = "Maaf, saya tidak bisa memberikan balasan (respons kosong)."
                    st.session_state.history.append({"role": "model", "parts": [error_msg]})
                    st.markdown(error_msg)

            except Exception as e:
                error_msg = f"❌ **Kesalahan Komunikasi**: Terjadi kesalahan saat berkomunikasi dengan Gemini: {e}. Coba lagi."
                st.session_state.history.append({"role": "model", "parts": [error_msg]})
                st.markdown(error_msg)
