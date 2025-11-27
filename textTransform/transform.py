from textTransform.audio_transcriber_assemblyai import AudioTranscriber
from textTransform.summary_gemini import TranscriptionAnalyzer
from textTransform import config


def transform(filename):
    # INICJALIZACJA
    print("🔧 Inicjalizacja...\n")
    config.ensure_directories()

    if not config.validate_config():
        print("\n❌ Konfiguracja zawiera błędy. Popraw je i spróbuj ponownie.")
        return

    config.print_config_summary()

    # TRANSKRYPCJA
    print("📝 ETAP 1: TRANSKRYPCJA")
    transcriber = AudioTranscriber(
        api_key=config.ASSEMBLYAI_API_KEY,
        language=config.ASSEMBLYAI_LANGUAGE,
        speaker_labels=config.ASSEMBLYAI_SPEAKER_LABELS
    )
    transcript_out  = ''
    try:
        print(filename)
        transcript = transcriber.transcribe(str(config.AUDIO_FILES_DIR / filename ) + ".mp3")
        transcript_out = transcriber.save(transcript, str(config.TRANSCRIPTS_DIR / filename ) + "_transcript.txt")
        print(f"✅ Transkrypcja zakończona w {transcriber.time:.2f}s\n")
    except Exception as e:
        print(f"❌ Błąd podczas transkrypcji: {e}")
        return

    # ANALIZA
    print("📊 ETAP 2: ANALIZA AI")
    analyzer = TranscriptionAnalyzer(
        api_key=config.GOOGLE_API_KEY,
        model=config.GEMINI_MODEL,
        prompt_path=str(config.ACTIVE_PROMPT_PATH),
        temperature=config.GEMINI_TEMPERATURE,
        top_p=config.GEMINI_TOP_P,
        top_k=config.GEMINI_TOP_K
    )

    try:
        analysis = analyzer.analyze(transcript_out)
        if analysis:
            analyzer.save(analysis, str(config.OUTPUT_DIR / filename ) + "_analysis.md")
            print(f"✅ Analiza zakończona\n")
        else:
            print("❌ Analiza nie powiodła się")
            return
    except Exception as e:
        print(f"❌ Błąd podczas analizy: {e}")
        return

    # PODSUMOWANIE
    print(f"📝 Transkrypcja: {str(config.TRANSCRIPTS_DIR / filename ) + "_transcript.txt"}")
    print(f"📊 Analiza: {str(config.OUTPUT_DIR / filename ) + "_analysis.md"}")
