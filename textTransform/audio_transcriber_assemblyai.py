import assemblyai as aai
import time

from assemblyai import WordBoost


class AudioTranscriber:
    def __init__(self, api_key=None, language="pl", speaker_labels=True, keywords=None):
        aai.settings.api_key = api_key
        self.config = aai.TranscriptionConfig(
            speech_model=aai.SpeechModel.best,
            language_code=language,
            speaker_labels=speaker_labels,
            word_boost=keywords,
            boost_param=WordBoost.high,
        )

        self.time = -1

    def transcribe(self, audio_file_path):
        print("Rozpoczynam transkrypcję z diaryzacją mówców...")
        start_time = time.time()

        transcript = aai.Transcriber(config=self.config).transcribe(audio_file_path)

        elapsed_time = time.time() - start_time
        self.time = elapsed_time

        if transcript.status == aai.TranscriptStatus.error:
            raise RuntimeError(f"Transkrypcja nie powiodła się: {transcript.error}")

        print(f"Czas transkrypcji: {elapsed_time:.2f}s")
        return transcript

    def save(self, transcript, output_file_path):
        output = ""
        with open(output_file_path, "w", encoding="utf-8") as f:
            for utterance in transcript.utterances:
                start = utterance.start / 1000
                end = utterance.end / 1000
                f.write(f"[{start:.2f}s - {end:.2f}s] {utterance.speaker}:\n")
                f.write(f"{utterance.text}\n\n")
                output += f"[{start:.2f}s - {end:.2f}s] {utterance.speaker}:\n" + f"{utterance.text}\n\n"
        print(f"✓ Zapisano: {output_file_path}")
        return output


