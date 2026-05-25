# Menggunakan sistem operasi Python yang ringan
FROM python:3.11-slim

# Menyiapkan folder kerja di dalam Docker
WORKDIR /app

# Menyalin daftar library dan menginstalnya
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode bot kalian ke dalam Docker
COPY . .

# Membuka port 8000 agar bot bisa diakses
EXPOSE 8000

# Perintah untuk menjalankan bot saat Docker dinyalakan
<<<<<<< HEAD:DockerFile
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
=======
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
>>>>>>> 5830a2493843a58fd974367697539c69c8aaa5ad:Dockerfile
