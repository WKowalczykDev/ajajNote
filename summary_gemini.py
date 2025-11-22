from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()


class TranscriptionAnalyzer:
    """Analyzer transkrypcji używający Gemini"""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.model = "models/gemini-2.5-pro"
        self.prompt_path = "assets/prompts/universal.txt"
        self.last_output = None

    def load_prompt(self):
        """Wczytuje uniwersalny prompt z pliku"""
        try:
            with open(self.prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ Błąd: Nie znaleziono promptu {self.prompt_path}")
            return None

    def analyze(self, transcription):
        """Analizuje transkrypcję i zwraca wynik"""
        prompt_template = self.load_prompt()

        if not prompt_template:
            return None

        prompt = prompt_template.replace("{transcription}", transcription)
        print("🔄 Analizuję transkrypcję...")

        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            ]

            config = types.GenerateContentConfig(
                temperature=0.2,
                top_p=0.8,
                top_k=40
            )

            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config
            )

            self.last_output = response

            """jeżeli odpowiedź jest zbyt długa to gemini rozbija ja na kawałki"""
            result = ""
            for part in response.candidates[0].content.parts:
                result += part.text

            print("✅ Analiza zakończona")
            return result

        except Exception as e:
            print(f"❌ Błąd podczas analizy: {e}")
            return None

    def save(self, content, filepath):
        """Zapisuje wynik do pliku"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Zapisano: {filepath}")
        return filepath