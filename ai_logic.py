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
