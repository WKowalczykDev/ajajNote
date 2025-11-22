from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY)

def list_models():
    try:
        models = client.models.list()
        print("Dostępne modele Gemini:\n")
        for m in models:
            print("-", m.name)
    except Exception as e:
        print("Błąd pobierania listy modeli:", e)

if __name__ == "__main__":
    list_models()
