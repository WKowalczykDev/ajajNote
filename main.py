from audio_transcriber_assemblyai import AudioTranscriber



INPUT_MP3 = "zamarzanie_wody.mp3" #TUTAJ NAZWA PLIKU MP3
OUTPUT_TRANSCRIPTION = "XD.txt" #TUTAJ NAZWA, GDZIE CHCEMY ZAPISAĆ TRANSKRYPCJE

transcriber = AudioTranscriber()
transcript = transcriber.transcribe(f"./INPUT/audio_files/{INPUT_MP3}")
transcriber.save(transcript, f"./OUTPUT/transcripts/{OUTPUT_TRANSCRIPTION}")