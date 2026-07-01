import os
from dotenv import load_dotenv
from google import genai


client = None
ai_model = "gemini-3.1-flash-lite"

def initialize_client():
    load_dotenv()

    global client
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

def generate_answer(prompt:str):
    global client
    response = client.models.generate_content(
        model=ai_model,
        contents=prompt
    )
    return response.text

def call_me():
    print("Hello from ai-logic!")

def analyze_pdf(file_path: str, prompt: str):
    global client
    
    # Cek inisialisasi client seperti biasa
    if client is None:
        initialize_client()
        
    try:
        # 1. Upload file PDF ke server Gemini
        uploaded_pdf = client.files.upload(file=file_path)
        
        # 2. Minta AI merespon dengan memberikan objek PDF dan prompt
        response = client.models.generate_content(
            model=ai_model,
            contents=[
                uploaded_pdf,
                prompt
            ]
        )
        return response.text
    except Exception as e:
        return f"Maaf, terjadi kesalahan saat membaca PDF: {e}"
