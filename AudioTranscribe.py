import deepspeech
import librosa
import numpy as np


def read_audio(path):
    audio_data, sample_rate = librosa.load(path, sr=16000)
    duration = librosa.get_duration(y=audio_data, sr=sample_rate)
    return (audio_data * 32767).astype(np.int16), sample_rate, duration


class AudioTranscribe:
    def __init__(self, model_file, scorer_file):
        self.model = deepspeech.Model(model_file)
        self.model.enableExternalScorer(scorer_file)

    def transcribe(self, audio_file_path, callback):
        audio, sample_rate, audio_length = read_audio(audio_file_path)

        first_start_time = 0
        word = []
        words = []
        times = {}
        result = self.model.sttWithMetadata(audio)
        tokens = result.transcripts[0].tokens
        len_tokens = len(tokens)

        callback(0, len_tokens)
        for i, token in enumerate(tokens):
            char = token.text
            if len(word) == 0:
                first_start_time = token.start_time
            if char == " " or i == len_tokens - 1:
                if i == len_tokens - 1:
                    word.append(char)
                word_str = "".join(word)
                words.append(word_str)
                if word_str in times:
                    times[word_str].append({"start": first_start_time, "end": token.start_time})
                else:
                    times[word_str] = [{"start": first_start_time, "end": token.start_time}]
                word = []
            else:
                word.append(char)
            callback(i + 1, len_tokens)
        return words, times

