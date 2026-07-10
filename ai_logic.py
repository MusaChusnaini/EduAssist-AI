import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.file import PyMuPDFReader

# Variabel global untuk menyimpan "Database Vektor" dan "Sesi Obrolan User"
rag_index = None
user_chat_engines = {}

def setup_llama_index():
    """Wajib dipanggil di main.py saat bot pertama kali menyala"""
    global rag_index

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("[ERROR CRITICAL] GEMINI_API_KEY tidak ditemukan di file .env!")
        return

    os.environ["GOOGLE_API_KEY"] = api_key

    # 1. Konfigurasi LLM dan Embedding
    instruksi_sistem = (
        "Kamu adalah EduAssist AI, asisten akademik yang tegas dan cerdas. "
        "Tugasmu HANYA menjawab berdasarkan dokumen referensi."
    )
    Settings.llm = Gemini(model="models/gemini-3.1-flash-lite", api_key=api_key, system_prompt=instruksi_sistem)
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # 2. Pengaturan Chunking (Diperlebar agar data tidak terputus)
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 200

    # 3. Membaca folder statis saat startup menggunakan PyMuPDF
    folder_sumber = "data_pdf"

    if os.path.exists(folder_sumber) and os.listdir(folder_sumber):
        print(f"[SISTEM] Menemukan dokumen di folder '{folder_sumber}'. Membangun Vector Database awal...")

        pembaca_kustom = {".pdf": PyMuPDFReader()}
        dokumen_awal = SimpleDirectoryReader(
            folder_sumber,
            file_extractor=pembaca_kustom
        ).load_data()

        # --- BLOK DEBUGGING DETAIL ---
        print(f"\n[DEBUG] Total halaman terekstrak dengan PyMuPDF: {len(dokumen_awal)}")
        for doc in dokumen_awal:
            nama_file = doc.metadata.get('file_name', 'Tidak diketahui')
            nomor_hal = doc.metadata.get('page_label', 'Tidak diketahui')
            cuplikan_teks = doc.text[:50].replace('\n', ' ')
            print(f" -> File: {nama_file} | Hal: {nomor_hal} | Cuplikan: {cuplikan_teks}...")
        print("------------------------------------------\n")

        rag_index = VectorStoreIndex.from_documents(dokumen_awal)
        print("[SISTEM] Database referensi berhasil dimuat ke RAM!")
    else:
        print(f"[SISTEM] Folder '{folder_sumber}' kosong. Bot menunggu file via chat.")

def analyze_pdf(file_path: str, prompt: str, user_id: str) -> str:
    """Mengolah PDF baru menggunakan CPU lokal, lalu merespon via Gemini"""
    global rag_index, user_chat_engines

    try:
        print(f"[SISTEM] Membaca dan mengekstrak dokumen: {file_path}")
        dokumen_baru = SimpleDirectoryReader(input_files=[file_path]).load_data()

        # Proses di bawah ini sekarang menggunakan CPU laptopmu, bukan API Google!
        if rag_index is None:
            print("[SISTEM] Membangun Vector Database di RAM...")
            rag_index = VectorStoreIndex.from_documents(dokumen_baru)
        else:
            print("[SISTEM] Menambahkan dokumen baru ke database...")
            for hal in dokumen_baru:
                rag_index.insert(hal)

        # Reset ingatan bot untuk user ini agar fokus ke PDF yang baru masuk
        if user_id in user_chat_engines:
            del user_chat_engines[user_id]

        return generate_answer(prompt, user_id)

    except Exception as e:
        return f"Maaf, terjadi kesalahan saat memproses RAG PDF: {e}"

def generate_answer(prompt: str, user_id: str) -> str:
    """Merespon chat teks dengan menjaring konteks secara luas (Top-K)"""
    global rag_index, user_chat_engines

    if rag_index is None:
        return "Sistem belum memiliki dokumen referensi. Silakan upload file PDF terlebih dahulu."

    if user_id not in user_chat_engines:
        print(f"[SISTEM] Membuat sesi memori RAG baru untuk user: {user_id}")
        # Memori obrolan dinaikkan agar AI tidak mudah lupa konteks awal
        memori = ChatMemoryBuffer.from_defaults(token_limit=2048)

        # KUNCI PERUBAHAN: Paksa AI membaca secara detail dan perluas jaring pencarian
        instruksi_detail = (
            "Kamu adalah EduAssist AI. Jawablah pertanyaan secara LENGKAP dan DETAIL "
            "berdasarkan dokumen referensi. Sebutkan semua poin-poin yang ada, jangan ada informasi yang dihilangkan atau dipotong."
        )

        user_chat_engines[user_id] = rag_index.as_chat_engine(
            chat_mode="condense_plus_context",
            memory=memori,
            similarity_top_k=6, # Menarik 6 bongkahan data, bukan cuma 2
            system_prompt=instruksi_detail
        )

    mesin_chat = user_chat_engines[user_id]

    try:
        jawaban = mesin_chat.chat(prompt)
        return str(jawaban)
    except Exception as e:
        return f"Maaf, AI mengalami kendala saat merespon: {e}"