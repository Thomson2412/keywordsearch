import threading
from pydub import AudioSegment
import pyaudio


def cut_audio(file_path, begin_time, end_time, padding=0):
    soundfile = None
    if file_path.endswith(".wav"):
        soundfile = AudioSegment.from_wav(file_path)
    if file_path.endswith(".mp3"):
        soundfile = AudioSegment.from_mp3(file_path)
    if soundfile:
        begin_time = begin_time - padding
        if begin_time < 0:
            begin_time = 0
        end_time = end_time + padding
        if end_time * 1000 > len(soundfile):
            end_time = len(soundfile) / 1000
        cut = soundfile[(begin_time * 1000):(end_time * 1000)]
        return cut
    return None


class RawAudioPlayer:
    def __init__(self, end_callback, progress_callback=None) -> None:
        super().__init__()
        self.playing_thread = None
        self.is_playing = False
        self.end_callback = end_callback
        self.progress_callback = progress_callback

    def play(self, file_path):
        soundfile = None
        if file_path.endswith(".wav"):
            soundfile = AudioSegment.from_wav(file_path)
        if file_path.endswith(".mp3"):
            soundfile = AudioSegment.from_mp3(file_path)
        if soundfile:
            self.playing_thread = threading.Thread(target=self.play_audio_segment, args=(soundfile,))
            self.playing_thread.start()

    def stop(self):
        self.is_playing = False

    def play_snippet(self, file_path, begin_time, end_time, padding=0):
        cut = cut_audio(file_path, begin_time, end_time, padding)
        if cut:
            self.playing_thread = threading.Thread(target=self.play_audio_segment, args=(cut,))
            self.playing_thread.start()

    def play_audio_segment(self, audio_segment):
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pa.get_format_from_width(audio_segment.sample_width),
                         channels=audio_segment.channels,
                         rate=audio_segment.frame_rate,
                         output=True)

        self.is_playing = True

        total_length = len(audio_segment.raw_data) - 1
        if self.progress_callback:
            self.progress_callback(0, total_length)
        chunk = 1024
        index = 0
        end = False
        while index < total_length and self.is_playing and not end:
            if index + chunk > total_length:
                chunk = total_length - index
            data = audio_segment.raw_data[index:index + chunk]
            index = index + chunk
            if self.progress_callback:
                self.progress_callback(index, total_length)
            stream.write(data)
        stream.close()
        pa.terminate()
        self.is_playing = False
        self.end_callback()
