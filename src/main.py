from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
import google.generativeai as genai

app = FastAPI()

# Mengambil API Key dari Environment Variable (agar aman)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "API_KEY_DEFAULT")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.post("/tanya-gemini")
def tanya_ai(data: PesanMasuk):
    # Prompting agar AI bertindak sebagai Aslab
    prompt = f"Kamu adalah asisten lab EduAssist-AI. Jawab dengan singkat dan jelas. Pertanyaan mahasiswa bernama {data.nama}: {data.pesan}"
    
    try:
        response = model.generate_content(prompt)
        jawaban_ai = response.text
    except Exception as e:
        jawaban_ai = "Maaf, otak AI sedang gangguan. Silakan hubungi Aslab manusia."

    return {"jawaban": jawaban_ai}

# URL rahasia dari Google Apps Script (Langkah 7)
GAS_URL = "https://script.google.com/macros/s/AKfycbxJ5ksnHpDxLwgR5-6MTEfEByQqC3wAAd4-DdPpAU09xXeXPm0YTkbCpd_e_FfyuMBcGw/exec"

# Format data yang diterima bot
class PesanMasuk(BaseModel):
    nama: str
    pesan: str

@app.post("/webhook")
def proses_pesan(data: PesanMasuk):
    # 1. Menyiapkan data untuk dikirim ke Google Sheets
    payload = {
        "nama": data.nama,
        "pesan": data.pesan
    }
    
    # 2. Mengirim data ke Google Apps Script
    try:
        response = requests.post(GAS_URL, json=payload)
        status_sheets = "Berhasil disimpan ke Sheets" if response.status_code == 200 else "Gagal menyimpan"
    except Exception:
        status_sheets = "Error koneksi ke Sheets"

    return {
        "status_bot": "Pesan diterima",
        "status_database": status_sheets,
        "jawaban_sementara": f"Halo {data.nama}, pertanyaanmu '{data.pesan}' sedang diproses!"
    }