"""
Centralna konfiguracja aplikacji do transkrypcji i analizy audio
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()

# ==================== API KEYS ====================
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ==================== ŚCIEŻKI KATALOGÓW ====================
# Katalog główny projektu

# Katalogi OUTPUT
OUTPUT_DIR = Path("outputs")
TRANSCRIPTS_DIR = OUTPUT_DIR / "transcripts"
ANALYSIS_DIR = OUTPUT_DIR / "md"

# Katalog z promptami
PROMPTS_DIR = Path("textTransform/assets/prompts")

# ==================== KONFIGURACJA MODELI ====================
# Model Gemini do analizy
GEMINI_MODEL = "models/gemini-2.5-pro"

# Konfiguracja generowania Gemini
GEMINI_TEMPERATURE = 0.2
GEMINI_TOP_P = 0.8
GEMINI_TOP_K = 40

# Model AssemblyAI
ASSEMBLYAI_LANGUAGE = "pl"
ASSEMBLYAI_SPEAKER_LABELS = True  # diaryzacja mówców

# ==================== PROMPTY ====================
# Dostępne typy promptów
PROMPT_TYPES = {
    "universal": "universal.txt",
    "lecture": "lecture.txt",
}

# Aktywny typ promptu (zmień tutaj, aby użyć innego promptu)
ACTIVE_PROMPT_TYPE = "universal"
ACTIVE_PROMPT_PATH = PROMPTS_DIR / PROMPT_TYPES[ACTIVE_PROMPT_TYPE]



def validate_config():
    """Waliduje konfigurację i wyświetla ostrzeżenia"""
    issues = []

    # Sprawdzenie kluczy API
    if not ASSEMBLYAI_API_KEY:
        issues.append("⚠️  Brak klucza ASSEMBLYAI_API_KEY w pliku .env")

    if not GOOGLE_API_KEY:
        issues.append("⚠️  Brak klucza GOOGLE_API_KEY w pliku .env")

    # Sprawdzenie pliku wejściowego

    # Sprawdzenie promptu
    if not ACTIVE_PROMPT_PATH.exists():
        issues.append(f"⚠️  Plik promptu nie istnieje: {ACTIVE_PROMPT_PATH}")

    if issues:
        print("\n".join(issues))
        return False

    print("✓ Konfiguracja poprawna")
    return True


def print_config_summary():
    """Wyświetla podsumowanie aktualnej konfiguracji"""
    print("📋 AKTUALNA KONFIGURACJA")
    print(f"🤖 Model Gemini: {GEMINI_MODEL}")
    print(f"💬 Typ promptu: {ACTIVE_PROMPT_TYPE}")
    print(f"🔊 Diaryzacja: {'TAK' if ASSEMBLYAI_SPEAKER_LABELS else 'NIE'}")


# ==================== INICJALIZACJA ====================
if __name__ == "__main__":
    print("🔧 Testowanie konfiguracji...\n")
    validate_config()
    print_config_summary()