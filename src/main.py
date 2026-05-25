from fastapi import FastAPI

app = FastAPI()

# Pintu depan untuk mengecek apakah bot hidup
@app.get("/")
def read_root():
    return {"status": "Bot EduAssist-AI Hidup!"}

# Pintu belakang untuk menerima pesan dari Telegram/Discord
@app.post("/webhook")
def terima_pesan():
    return {"pesan": "Pesan diterima, tapi saya belum pintar."}