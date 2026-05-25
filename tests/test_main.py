from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_root():
    # Kita suruh komputer mengetuk "pintu depan" bot kita
    response = client.get("/")

    
    assert response.status_code == 200

    # Kita pastikan balasan bot sesuai
    assert response.json() == {"status": "Bot EduAssist-AI Hidup!"}