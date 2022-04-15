import deepspeech
import WavSplit
import numpy as np
import webrtcvad


def vad_segment_generator(path, aggressiveness):
    audio, sample_rate, audio_length = WavSplit.read_wave(path)
    assert sample_rate == 16000, "Only 16000Hz input WAV files are supported for now!"
    vad = webrtcvad.Vad(int(aggressiveness))
    frames = WavSplit.frame_generator(30, audio, sample_rate)
    frames = list(frames)
    segments = WavSplit.vad_collector(sample_rate, 30, 300, vad, frames)

    return segments, sample_rate, audio_length


class AudioTranscribe:
    def __init__(self, model_file, scorer_file):
        self.model = deepspeech.Model(model_file)
        self.model.enableExternalScorer(scorer_file)

    def transcribe(self, audio_file_path, callback):
        # audio, sample_rate, audio_length = WavSplit.read_wave(audio_file_path)
        segments, sample_rate, audio_length = vad_segment_generator(audio_file_path, 2)
        segments = list(segments)
        len_segments = len(segments)

        first_start_time = 0
        word = []
        words = []
        times = {}
        for i, segment in enumerate(segments):
            callback(i + 1, len_segments)
            audio = np.frombuffer(segment, dtype=np.int16)
            result = self.model.sttWithMetadata(audio)
            tokens = result.transcripts[0].tokens
            for token in tokens:
                char = token.text
                if len(word) == 0:
                    first_start_time = token.start_time
                if char == " ":
                    word_str = "".join(word)
                    words.append(word_str)
                    if word_str in times:
                        times[word_str].append({"start": first_start_time, "end": token.start_time})
                    else:
                        times[word_str] = [{"start": first_start_time, "end": token.start_time}]
                    word = []
                else:
                    word.append(char)
            callback(i + 1, len_segments)
        return " ".join(words), times
