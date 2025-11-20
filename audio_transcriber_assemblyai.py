import assemblyai as aai
import time
from dotenv import load_dotenv
import os

load_dotenv()

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

audio_file = "./audio_files/zamarzanie_wody.mp3"

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

# CZAS TRANSKRYPCJI
elapsed_time = end_time - start_time


# ZAPIS DO PLIKÓW
with open("./transcripts/zamarzanie_wody.txt", "w", encoding="utf-8") as f:
    for utterance in transcript.utterances:
        start = utterance.start / 1000
        end = utterance.end / 1000
        f.write(f"[{start:.2f}s - {end:.2f}s] {utterance.speaker}:\n")
        f.write(f"{utterance.text}\n\n")

print("\n✓ Zapisano: ./transcripts/assembleai-wrss-17_11.txt")