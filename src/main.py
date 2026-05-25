from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

# Menggunakan library Gemini generasi terbaru
from google import genai 

app = FastAPI()

# URL rahasia dari Google Apps Script (Langkah 7)
GAS_URL = "https://script.google.com/macros/s/AKfycbxJ5ksnHpDxLwgR5-6MTEfEByQqC3wAAd4-DdPpAU09xXeXPm0YTkbCpd_e_FfyuMBcGw/exec"

# Inisialisasi API Key dari Environment Variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "API_KEY_DEFAULT")

# Menyiapkan "Otak" AI
try:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
except Exception:
    ai_client = None

# Format data pesan
class PesanMasuk(BaseModel):
    nama: str
    pesan: str

# FIX 1: Mengembalikan "Pintu Depan" agar test_main.py lolos 100%
@app.get("/")
def read_root():
    return {"status": "Bot EduAssist-AI Hidup!"}

# Pintu untuk integrasi ke Google Sheets
@app.post("/webhook")
def proses_pesan(data: PesanMasuk):
    payload = {
        "nama": data.nama,
        "pesan": data.pesan
    }
    try:
        response = requests.post(GAS_URL, json=payload)
        status_sheets = "Berhasil disimpan" if response.status_code == 200 else "Gagal menyimpan"
    except Exception:
        status_sheets = "Error koneksi ke Sheets"

    return {
        "status_bot": "Pesan diterima",
        "status_database": status_sheets,
        "jawaban_sementara": f"Halo {data.nama}, pertanyaanmu '{data.pesan}' sedang diproses!"
    }

# FIX 2: Menggunakan struktur kode library Gemini API yang baru
@app.post("/tanya-gemini")
def tanya_ai(data: PesanMasuk):
    prompt = f"Kamu adalah asisten lab EduAssist-AI. Jawab dengan singkat dan jelas. Pertanyaan dari {data.nama}: {data.pesan}"
    
    try:
        if ai_client:
            # Menggunakan model flash terbaru untuk kecepatan tinggi
            response = ai_client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=prompt
            )
            jawaban_ai = response.text
        else:
            jawaban_ai = "Sistem AI belum siap. API Key tidak terdeteksi."
    except Exception as e:
        jawaban_ai = f"Maaf, AI sedang gangguan: {str(e)}"

    return {"jawaban": jawaban_ai}