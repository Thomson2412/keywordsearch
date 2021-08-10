import math
import os
import tempfile
from io import BytesIO
import speech_recognition as sr
from pocketsphinx import get_model_path, Decoder
from pydub import AudioSegment


def transcribe(audio_file_path, callback):
    decoder = create_decoder()
    raw_data = convert_audio_to_raw(audio_file_path)
    stream = BytesIO(raw_data)

    chunk_size = 1024
    total_size = len(raw_data)
    steps = math.ceil(total_size / chunk_size)
    count = 0

    decoder.start_utt()
    while True:
        buf = stream.read(1024)
        if buf:
            decoder.process_raw(buf, False, False)
            count += 1
            callback(count, steps)
        else:
            break


    decoder.end_utt()

    return decoder


def keyword_search(audio_file_path, keyword_entries):
    decoder = create_decoder()
    raw_data = convert_audio_to_raw(audio_file_path)

    temp_file_descriptor, temp_file_path = tempfile.mkstemp()
    file = os.fdopen(temp_file_descriptor, "w")
    lines = ["{} /1e{}/\n".format(keyword.lower(), sensitivity) for keyword, sensitivity in keyword_entries]
    file.writelines(lines)
    file.flush()

    decoder.set_kws("keywords", temp_file_path)
    decoder.set_search("keywords")
    decoder.start_utt()
    decoder.process_raw(raw_data, False, True)
    decoder.end_utt()

    os.remove(temp_file_path)

    return decoder


def create_decoder():
    model_path = get_model_path()
    config = Decoder.default_config()
    config.set_string("-hmm", os.path.join(model_path, "en-us"))
    config.set_string("-lm", os.path.join(model_path, "en-us.lm.bin"))
    config.set_string("-dict", os.path.join(model_path, "cmudict-en-us.dict"))
    config.set_string("-logfn", os.devnull)
    return Decoder(config)


def convert_audio_to_raw(audio_file_path):
    if ".mp3" not in audio_file_path and ".wav" not in audio_file_path:
        raise Exception("File path must contain extension and can only be wav or mp3")

    if ".mp3" in audio_file_path:
        if os.path.exists("temp.wav"):
            raise Exception("Temp file already exist. Abort!")
        else:
            sound = AudioSegment.from_mp3(audio_file_path)
            sound.export("temp.wav", format="wav")
            audio_file = sr.AudioFile("temp.wav")
    else:
        audio_file = sr.AudioFile(audio_file_path)

    r = sr.Recognizer()
    with audio_file as source:
        r.adjust_for_ambient_noise(source)
        audio = r.record(source)

    if ".mp3" in audio_file_path and os.path.exists("temp.wav"):
        os.remove("temp.wav")

    return audio.get_raw_data(convert_rate=16000, convert_width=2)


def get_json_from_segments(segments):
    fps = 100
    result = {}
    for s in segments:
        start_time = s.start_frame / fps
        end_time = s.end_frame / fps
        if s.word in result:
            result[s.word].append({"start": start_time, "end": end_time})
        else:
            result[s.word] = [{"start": start_time, "end": end_time}]
    return result


def print_segments(segments):
    fps = 100  # Standard rate
    print("-" * 28)
    print("| %5s |  %3s  |   %4s   |" % ("start", "end", "word"))
    for s in segments:
        print("| %4ss | %4ss | %8s |" % (s.start_frame / fps, s.end_frame / fps, s.word))
    print("-" * 28)


class AudioTranscribe:
    pass
