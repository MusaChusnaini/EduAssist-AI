# Menggunakan sistem operasi Python yang ringan
FROM python:3.11-slim

# Menyiapkan folder kerja di dalam Docker
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode bot kalian
COPY . .

# Membuka port 8000 agar bot bisa diakses
EXPOSE 8000

# Perintah untuk menjalankan bot saat Docker dinyalakan
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
