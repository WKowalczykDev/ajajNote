import assemblyai as aai
import time
from collections import defaultdict
from dotenv import load_dotenv
import os

load_dotenv()

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

audio_file = "./audio_files/starosci.mp3"

# Konfiguracja z językiem polskim i DIARYZACJĄ
config = aai.TranscriptionConfig(
    speech_model=aai.SpeechModel.best,
    language_code="pl",
    speaker_labels=True  # WŁĄCZENIE DIARYZACJI MÓWCÓW
)

# Rozpocznij pomiar czasu
start_time = time.time()

print("Rozpoczynam transkrypcję z diaryzacją mówców...")
transcript = aai.Transcriber(config=config).transcribe(audio_file)

# Zakończ pomiar czasu
end_time = time.time()

if transcript.status == aai.TranscriptStatus.error:
    raise RuntimeError(f"Transkrypcja nie powiodła się: {transcript.error}")

# Oblicz czas transkrypcji
elapsed_time = end_time - start_time

# ========== WYŚWIETLANIE WYNIKÓW ==========

print("\n" + "=" * 80)
print("PEŁNA TRANSKRYPCJA:")
print("=" * 80)
print(transcript.text)

print("\n" + "=" * 80)
print("TRANSKRYPCJA Z PODZIAŁEM NA MÓWCÓW (CHRONOLOGICZNIE):")
print("=" * 80)

# Wyświetl każdą wypowiedź z informacją o mówcy
for utterance in transcript.utterances:
    speaker = utterance.speaker
    text = utterance.text
    start = utterance.start / 1000  # konwersja z ms na sekundy
    end = utterance.end / 1000

    print(f"\n[{start:.2f}s - {end:.2f}s] {speaker}:")
    print(f"  {text}")

print("\n" + "=" * 80)
print("PODSUMOWANIE WEDŁUG MÓWCÓW:")
print("=" * 80)

# Grupuj teksty według mówców
speakers_text = defaultdict(list)
speakers_time = defaultdict(float)

for utterance in transcript.utterances:
    speakers_text[utterance.speaker].append(utterance.text)
    duration = (utterance.end - utterance.start) / 1000
    speakers_time[utterance.speaker] += duration

# Wyświetl podsumowanie dla każdego mówcy
for speaker in sorted(speakers_text.keys()):
    print(f"\n{speaker}:")
    print(f"  Czas mówienia: {speakers_time[speaker]:.2f} sekund ({speakers_time[speaker] / 60:.2f} minut)")
    print(f"  Liczba wypowiedzi: {len(speakers_text[speaker])}")
    print(f"  Pełny tekst:")
    full_text = " ".join(speakers_text[speaker])

print("\n" + "=" * 80)
print(f"Czas transkrypcji: {elapsed_time:.2f} sekund ({elapsed_time / 60:.2f} minut)")
print(f"Znaleziono {len(speakers_text)} mówców")
print("=" * 80)

# ========== OPCJONALNIE: ZAPIS DO PLIKÓW ==========

# Zapisz pełną transkrypcję z timestampami
with open("./transcripts/starosci.txt", "w", encoding="utf-8") as f:
    for utterance in transcript.utterances:
        start = utterance.start / 1000
        end = utterance.end / 1000
        f.write(f"[{start:.2f}s - {end:.2f}s] {utterance.speaker}:\n")
        f.write(f"{utterance.text}\n\n")

print("\n✓ Zapisano: ./transcripts/starosci.txt")

# # Zapisz osobne pliki dla każdego mówcy
# for speaker, texts in speakers_text.items():
#     filename = f"transkrypcja_{speaker}.txt"
#     with open(filename, "w", encoding="utf-8") as f:
#         f.write(f"=== {speaker} ===\n\n")
#         f.write(" ".join(texts))
#     print(f"✓ Zapisano: {filename}")