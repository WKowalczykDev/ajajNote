import os

from textTransform.audio_transcriber_assemblyai import AudioTranscriber
from textTransform.summary_gemini import TranscriptionAnalyzer
from textTransform import config


def transform(input, transcript_dir, note, filename):
    # INICJALIZACJA
    name, extension = os.path.splitext(filename)
    print("🔧 Inicjalizacja...\n")

    if not config.validate_config():
        msg = "Configuration error"
        return msg, 400

    config.print_config_summary()

    # TRANSKRYPCJA
    transcriber = AudioTranscriber(
        api_key=config.ASSEMBLYAI_API_KEY,
        language=config.ASSEMBLYAI_LANGUAGE,
        speaker_labels=config.ASSEMBLYAI_SPEAKER_LABELS
    )
    transcript_out = ''

    file_path = os.path.join(input, name + extension)
    print("Transcribing file:", file_path)

    if not os.path.exists(file_path):
        msg = f"File not found: {file_path}"
        return msg, 400

    try:
        transcript = transcriber.transcribe(file_path)
        transcript_out = transcriber.save(transcript, os.path.join(transcript_dir, name + ".txt"))
    except Exception as e:
        print("❌ Transcription Exception:", e)
        msg = f"Transcription error: {e}"
        return msg, 400

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
            analyzer.save(analysis, os.path.join(note, name + ".md"))
            msg = "Success"
            return msg, 200
        else:
            msg = f"Analysis Error: {analysis} is null"
            return msg, -1
    except Exception as e:
        msg = f"Analysis Error: {str(e)}"
        return msg, 400
