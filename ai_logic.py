import os
import google.generativeai as genai
from dotenv import load_dotenv

# Variabel global untuk menyimpan sesi obrolan per user
user_chats = {}
ai_model = None

def setup_ai():
    """Wajib dipanggil sekali di main.py saat bot menyala"""
    global ai_model
    
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("[ERROR] GEMINI_API_KEY tidak ditemukan!")
        return
        
    genai.configure(api_key=api_key)
    
    # Beri instruksi dasar agar dia ingat perannya
    instruksi_sistem = (
        "Kamu adalah EduAssist AI, asisten akademik yang sangat cerdas. "
        "Tugasmu membantu mahasiswa menjawab pertanyaan dan memahami materi. "
        "Bicaralah dengan bahasa yang natural, informatif, dan nyambung dengan obrolan sebelumnya."
    )
    
    # Gunakan model Flash yang cepat dan hemat kuota
    ai_model = genai.GenerativeModel(
        model_name="models/gemini-3.1-flash-lite",
        system_instruction=instruksi_sistem
    )
    print("[SISTEM] AI Native dengan Memori siap digunakan!")

def generate_answer(prompt: str, user_id: str) -> str:
    """Merespon chat biasa (teks saja) dengan mengingat obrolan sebelumnya"""
    global ai_model, user_chats
    
    if ai_model is None:
        return "Sistem AI belum siap."
        
    # Jika user baru pertama kali chat, buatkan 'ruangan' obrolan baru
    if user_id not in user_chats:
        print(f"[SISTEM] Membuat ruang obrolan baru untuk user: {user_id}")
        user_chats[user_id] = ai_model.start_chat(history=[])
        
    chat_session = user_chats[user_id]
    
    try:
        # Kirim pesan ke ruang obrolan tersebut
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        return f"Maaf, AI mengalami kendala: {e}"

def analyze_pdf(file_path: str, prompt: str, user_id: str) -> str:
    """Merespon jika user mengirim PDF, dan tetap mengingat konteksnya"""
    global ai_model, user_chats
    
    if ai_model is None:
        return "Sistem AI belum siap."
        
    try:
        print(f"[SISTEM] Mengunggah file ke memori sementara Google: {file_path}")
        # Upload utuh ke server Gemini (tidak memakan kuota embedding)
        uploaded_pdf = genai.upload_file(path=file_path)
        
        if user_id not in user_chats:
            user_chats[user_id] = ai_model.start_chat(history=[])
            
        chat_session = user_chats[user_id]
        
        # Kirim file PDF beserta teks pertanyaannya ke dalam ruang obrolan
        response = chat_session.send_message([uploaded_pdf, prompt])
        return response.text
        
    except Exception as e:
        return f"Maaf, gagal memproses PDF: {e}"