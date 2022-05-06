import os
import argparse
import json
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
from AudioTranscribe import AudioTranscribe
import warnings

warnings.filterwarnings('ignore')

parser = argparse.ArgumentParser(description="Transcribe an audio file and export timestamps")
parser.add_argument("files", action="extend", nargs="+", type=str,
                    help="Path or paths to one or multiple audio files")
parser.add_argument("-o", "--output", metavar="path", dest="output", type=str,
                    help="Define the output path for the transcriptions and timestamp files")

audio_transcriber = AudioTranscribe("data/models/deepspeech-0.9.3-models.pbmm",
                                    "data/models/deepspeech-0.9.3-models.scorer")
args = parser.parse_args()
input_files = args.files
output_path = args.output

if len(input_files) == 0:
    raise IOError("No files detected")
if output_path is not None and not os.path.isdir(output_path):
    raise IOError("Output directory does not exist")

for file_path in input_files:
    if file_path.endswith(".wav") or file_path.endswith(".mp3"):
        file_path_head, file_path_tail = os.path.split(file_path)
        if output_path is None:
            output_path = file_path_head
        filename_split = os.path.splitext(file_path_tail)

        print(f"Started transcribing: {file_path_tail}")
        result = audio_transcriber.transcribe(file_path)
        result_txt = " ".join(result[0])
        result_time = result[1]
        print(f"Finished transcribing: {file_path_tail}")

        print(f"Started writing files for: {file_path_tail}")
        with open(os.path.join(output_path, f"{filename_split[0]}.txt"), "w") as f:
            f.write(result_txt)

        with open(os.path.join(output_path, f"{filename_split[0]}.json"), "w") as f:
            json.dump(result_time, f, indent=4)
        print(f"Finished writing files for: {file_path_tail}")

    else:
        print("Filetype not supported")
