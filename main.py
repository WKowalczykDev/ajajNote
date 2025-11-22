from audio_transcriber_assemblyai import AudioTranscriber
from summary_gemini import TranscriptionAnalyzer


INPUT_MP3 = "zamarzanie_wody.mp3" #TUTAJ NAZWA PLIKU MP3
OUTPUT_TRANSCRIPTION = "XD.txt" #TUTAJ NAZWA, GDZIE CHCEMY ZAPISAĆ TRANSKRYPCJE
OUTPUT_ANALYSIS = "zamarzanie_wody_analiza.md"

# Transkrypcja
transcriber = AudioTranscriber()
transcript = transcriber.transcribe(f"./INPUT/audio_files/{INPUT_MP3}")
transcriber.save(transcript, f"./OUTPUT/transcripts/{OUTPUT_TRANSCRIPTION}")

# with open(f"./OUTPUT/transcripts/{OUTPUT_TRANSCRIPTION}", "r", encoding="utf-8") as f:
#     transcript = f.read()

# Analiza
analyzer = TranscriptionAnalyzer()
analysis = analyzer.analyze(transcript)
if analysis:
    analyzer.save(analysis, f"./OUTPUT/md/{OUTPUT_ANALYSIS}")

print(analyzer.last_output)