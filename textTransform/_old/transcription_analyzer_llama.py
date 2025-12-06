from huggingface_hub import InferenceClient
import os
from datetime import datetime
from dotenv import load_dotenv
import time

load_dotenv()


class TranscriptionAnalyzer:
    """System analizy transkrypcji dla różnych typów spotkań"""

    def __init__(self, api_key):
        self.client = InferenceClient(
            provider="novita",
            api_key=api_key
        )
        self.model = "meta-llama/Llama-3.3-70B-Instruct"
        self.prompts_dir = "../assets/prompts"

    def load_transcription(self, filepath):
        """Wczytuje transkrypcję z pliku"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ Błąd: Nie znaleziono pliku {filepath}")
            return None

    def load_prompt(self, prompt_type):
        """Wczytuje prompt z pliku"""
        prompt_path = os.path.join(self.prompts_dir, f"{prompt_type}.txt")
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ Błąd: Nie znaleziono promptu {prompt_path}")
            return None

    def save_output(self, content, output_name):
        """Zapisuje wynik do pliku"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_name}_{timestamp}.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Zapisano: {filename}")
        return filename

    def analyze(self, transcription, prompt_type="universal"):
        prompt_template = self.load_prompt(prompt_type)

        if not prompt_template:
            print(f"⚠️ Nieznany typ: {prompt_type}. Używam 'universal'")
            prompt_template = self.load_prompt("universal")
            if not prompt_template:
                return None

        prompt = prompt_template.replace("{transcription}", transcription)
        print(f"🔄 Analizuję transkrypcję ({prompt_type})...")

        try:

            start_time = time.perf_counter()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )

            end_time = time.perf_counter()
            execution_time = end_time - start_time

            result = response.choices[0].message.content
            print("✅ Analiza zakończona")
            print(f"⏱ Czas wykonania: {execution_time:.2f} s")
            return result

        except Exception as e:
            print(f"❌ Błąd podczas analizy: {e}")
            return None


def main():
    """Przykłady użycia systemu"""
    API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    analyzer = TranscriptionAnalyzer(API_KEY)

    print("=" * 60)
    print("  SYSTEM ANALIZY TRANSKRYPCJI")
    print("=" * 60)

    print("\nDostępne tryby analizy:")
    print("1. Universal - uniwersalny (domyślny)")
    print("2. Organizational - spotkania organizacyjne")
    print("3. Lecture - wykłady i webinary")
    print("4. Panel - dyskusje panelowe")
    print("5. Difficult - trudne warunki (szumy, błędy)")
    print("6. WRSS - spotkanie WRSS")
    print("7. wykład rozwinięty")
    print("8. Spotkanie samorzadu - starosci")

    choice = input("\nWybierz tryb (1-8) lub Enter dla domyślnego: ").strip()

    mode_map = {
        "1": "universal",
        "2": "organizational",
        "3": "lecture",
        "4": "panel",
        "5": "difficult",
        "6": "wrss",
        "7": "lecture_better",
        "8": "starosci",
        "": "universal"
    }

    mode = mode_map.get(choice, "universal")

    filename = input("\nPodaj nazwę pliku (domyślnie: transcripts/transkrypcja_timeline.txt): ").strip()
    if not filename:
        filename = "OUTPUT/transcripts/transkrypcja_timeline.txt"

    transcription = analyzer.load_transcription(filename)
    output_name = ""
    if transcription:
        result = analyzer.analyze(transcription, prompt_type=mode)

        if result:

            output_name = f"konspekt_{mode}"
            analyzer.save_output(result, output_name)

    print(f"\n✅ Zakończono i zapisano jako {output_name}...")


if __name__ == "__main__":
    main()