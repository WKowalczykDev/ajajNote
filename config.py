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
BASE_DIR = Path(__file__).parent
FILE_NAME = "spotkanie_wrss_01_12"
# Katalogi INPUT
INPUT_DIR = BASE_DIR / "INPUT"
AUDIO_FILES_DIR = INPUT_DIR / "audio_files"

# Katalogi OUTPUT
OUTPUT_DIR = BASE_DIR / "OUTPUT"
TRANSCRIPTS_DIR = OUTPUT_DIR / "transcripts"
ANALYSIS_DIR = OUTPUT_DIR / "md"
PDF_DIR = OUTPUT_DIR / "pdf"

# Katalog z promptami
PROMPTS_DIR = BASE_DIR / "assets" / "prompts"

# ==================== PLIKI WEJŚCIOWE ====================
# Główny plik audio do przetworzenia
INPUT_AUDIO_FILE = f"{FILE_NAME}.mp3"
INPUT_AUDIO_PATH = AUDIO_FILES_DIR / INPUT_AUDIO_FILE

# ==================== PLIKI WYJŚCIOWE ====================
# Nazwa pliku z transkrypcją
OUTPUT_TRANSCRIPT_FILE = f"{FILE_NAME}.txt"
OUTPUT_TRANSCRIPT_PATH = TRANSCRIPTS_DIR / OUTPUT_TRANSCRIPT_FILE

# Nazwa pliku z analizą
OUTPUT_ANALYSIS_FILE = f"{FILE_NAME}.md"
OUTPUT_ANALYSIS_PATH = ANALYSIS_DIR / OUTPUT_ANALYSIS_FILE

OUTPUT_PDF_FILE = f"{FILE_NAME}.pdf"
OUTPUT_PDF_PATH = PDF_DIR / OUTPUT_PDF_FILE

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


# ==================== FUNKCJE POMOCNICZE ====================
def ensure_directories():
    """Tworzy wszystkie wymagane katalogi, jeśli nie istnieją"""
    directories = [
        INPUT_DIR,
        AUDIO_FILES_DIR,
        OUTPUT_DIR,
        TRANSCRIPTS_DIR,
        ANALYSIS_DIR,
        PDF_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    print("✓ Wszystkie katalogi gotowe")


def validate_config():
    """Waliduje konfigurację i wyświetla ostrzeżenia"""
    issues = []

    # Sprawdzenie kluczy API
    if not ASSEMBLYAI_API_KEY:
        issues.append("⚠️  Brak klucza ASSEMBLYAI_API_KEY w pliku .env")

    if not GOOGLE_API_KEY:
        issues.append("⚠️  Brak klucza GOOGLE_API_KEY w pliku .env")

    # Sprawdzenie pliku wejściowego
    if not INPUT_AUDIO_PATH.exists():
        issues.append(f"⚠️  Plik audio nie istnieje: {INPUT_AUDIO_PATH}")

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
    print(f"🎤 Plik audio: {INPUT_AUDIO_FILE}")
    print(f"📝 Transkrypcja: {OUTPUT_TRANSCRIPT_FILE}")
    print(f"📊 Analiza: {OUTPUT_ANALYSIS_FILE}")
    print(f"PDF: {OUTPUT_PDF_FILE}")
    print(f"🤖 Model Gemini: {GEMINI_MODEL}")
    print(f"💬 Typ promptu: {ACTIVE_PROMPT_TYPE}")
    print(f"🔊 Diaryzacja: {'TAK' if ASSEMBLYAI_SPEAKER_LABELS else 'NIE'}")


# ==================== INICJALIZACJA ====================
if __name__ == "__main__":
    print("🔧 Testowanie konfiguracji...\n")
    ensure_directories()
    validate_config()
    print_config_summary()