import torch
import whisper


class AudioTranscribe:
    def __init__(self, model_name):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(model_name)
        if device == "cuda":
            self.model = whisper.load_model(model_name).cuda()
        self.language = "en" if model_name.endswith(".en") else None

    def transcribe(self, audio_file_path, callback=None):
        transcription = self.model.transcribe(audio_file_path, language=self.language)
        segments = transcription['segments']
        len_segments = len(segments)

        lines = {}

        for i, segment in enumerate(segments):
            start_time = segment['start']
            end_time = segment['end']
            line = segment['text'].strip()
            lines[int(segment['id'])] = {
                "line": line,
                "start": start_time,
                "end": end_time
            }
            if callback:
                callback(i + 1, len_segments)

        return lines
