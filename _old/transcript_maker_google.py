import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

INPUT_FILE = "../INPUT/audio_files/spotkanie_wursu_17_11.mp3"
OUTPUT_FILE = "../OUTPUT/transcripts/tr-wrss-17_11_25.txt"

load_dotenv()

def transcribe_with_diarization():
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    with open(INPUT_FILE, "rb") as f:
        audio_data = f.read()

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=
                    "Przetranskrybuj ten plik dźwiękowy po polsku i oznacz mówców (Speaker 1, Speaker 2...)."
                ),
                types.Part.from_bytes(mime_type="audio/mpeg", data=audio_data),
            ],
        )
    ]

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=contents
    )

    transcript = ""
    for part in response.candidates[0].content.parts:
        transcript += part.text

    return transcript

def save_to_file(text, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[OK] Zapisano wynik do: {filename}")


def list_available_models():
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    models = client.models.list()

    print("Wszystkie dostępne modele:")
    for model in models:
        print(f"\nNazwa: {model.name}")
        print(f"  Display name: {getattr(model, 'display_name', 'N/A')}")
        print(f"  Metody: {getattr(model, 'supported_generation_methods', 'N/A')}")
        print(f"  Wszystkie atrybuty: {dir(model)}")
if __name__ == "__main__":
    # list_available_models()
    result = transcribe_with_diarization()
    save_to_file(result, OUTPUT_FILE)