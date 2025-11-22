from audio_transcriber_assemblyai import AudioTranscriber
from summary_gemini import TranscriptionAnalyzer
import config

def main():
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
        transcript = transcriber.transcribe(str(config.INPUT_AUDIO_PATH))
        transcript_out = transcriber.save(transcript, str(config.OUTPUT_TRANSCRIPT_PATH))
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
            analyzer.save(analysis, str(config.OUTPUT_ANALYSIS_PATH))
            print(f"✅ Analiza zakończona\n")
        else:
            print("❌ Analiza nie powiodła się")
            return
    except Exception as e:
        print(f"❌ Błąd podczas analizy: {e}")
        return

    # PODSUMOWANIE
    print(f"📝 Transkrypcja: {config.OUTPUT_TRANSCRIPT_PATH}")
    print(f"📊 Analiza: {config.OUTPUT_ANALYSIS_PATH}")


if __name__ == "__main__":
    main()