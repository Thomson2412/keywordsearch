import glob
import os
import re
import string
import tempfile
import speech_recognition as sr
from pocketsphinx import Decoder, get_model_path
from pydub import AudioSegment
import tkinter as tk
import tkinter.filedialog

window = tk.Tk()
selected_dir = "No dir selected"
lbl_selected_dir_var = tk.StringVar(value=selected_dir)
lb_files_content = ["No files"]
lb_files_content_var = tk.StringVar(value=lb_files_content)
ent_search_var = tk.StringVar()

abstract_text: tk.Text
file_text: tk.Text
lb_keywords: tk.Listbox

last_selected_file = ""


def main():
    layout_creator()


def layout_creator():
    global abstract_text, file_text, lb_keywords
    window.columnconfigure(0, weight=1, minsize=400)
    window.columnconfigure(1, weight=1, minsize=800)
    window.rowconfigure([0, 1], weight=1, minsize=400)

    frame_config = tk.Frame(window)
    frame_config.grid(row=0, column=0, sticky="nsew")
    lb_keywords = tk.Listbox(frame_config)
    lb_keywords.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    entry_keywords = tk.Entry(frame_config, width=40, bg="white", fg="black", textvariable=ent_search_var)
    entry_keywords.pack(side=tk.TOP, fill=tk.X, expand=False)
    btn_word_remove = tk.Button(frame_config, text="-", command=remove_keyword_selected)
    btn_word_remove.pack(side=tk.LEFT, fill=tk.X, expand=True)
    btn_word_add = tk.Button(frame_config, text="+", command=add_keyword_from_entry)
    btn_word_add.pack(side=tk.RIGHT, fill=tk.X, expand=True)



    frame_files = tk.Frame(window)
    frame_files.grid(row=1, column=0, sticky="nsew")
    btn_load_dir = tk.Button(frame_files, text="Load directory", command=select_dir)
    btn_load_dir.pack(side=tk.TOP, fill=tk.X, expand=False)
    lbl_selected_dir = tk.Label(frame_files, textvariable=lbl_selected_dir_var)
    lbl_selected_dir.pack(side=tk.TOP, fill=tk.X, expand=False)

    lb_files = tk.Listbox(frame_files, listvariable=lb_files_content_var)
    lb_files.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb_files = tk.Scrollbar(frame_files, orient="vertical")
    sb_files.config(command=lb_files.yview)
    sb_files.pack(side=tk.RIGHT, fill=tk.Y)
    lb_files.config(yscrollcommand=sb_files.set)
    lb_files.bind('<<ListboxSelect>>', file_selected)



    frame_abstract = tk.Frame(window)
    frame_abstract.grid(row=0, column=1, sticky="nsew")
    abstract_text = tk.Text(frame_abstract)
    abstract_text.config(state=tk.DISABLED)
    abstract_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb_abstract = tk.Scrollbar(frame_abstract, orient="vertical")
    sb_abstract.config(command=abstract_text.yview)
    sb_abstract.pack(side=tk.RIGHT, fill=tk.Y)
    abstract_text.config(yscrollcommand=sb_abstract.set)

    frame_text = tk.Frame(window)
    frame_text.grid(row=1, column=1, sticky="nsew")
    file_text = tk.Text(frame_text)
    file_text.config(state=tk.DISABLED)
    file_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb_text = tk.Scrollbar(frame_text, orient="vertical")
    sb_text.config(command=file_text.yview)
    sb_text.pack(side=tk.RIGHT, fill=tk.Y)
    file_text.config(yscrollcommand=sb_text.set)

    window.mainloop()
    # input_file_path = "recordings/english1.mp3"
    #
    # tr = transcribe(input_file_path)
    # print("Prediction: {}".format(tr.hyp().hypstr))
    # print("Accuracy: {}".format(calculate_accuracy(tr.hyp().hypstr)))
    #
    # kwr = keyword_search(input_file_path, [
    #     ("peas", 20),
    #     ("store", 20),
    #     ("thick", 10),
    # ])
    #
    # print_segments(reversed(list(kwr.seg())))


def populate_files():
    kw = lb_keywords.get(0)
    filepath_list = []
    for root, dirs, files in os.walk(selected_dir):
        for filename in files:
            if filename.endswith(".txt"):
                filepath = os.path.join(root, filename)
                with open(os.path.join(root, filename), "r") as f:
                    if re.search(r'\b' + kw + r'\b', f.read()):
                        filepath_list.append(filepath)
    lb_files_content_var.set(filepath_list)


def select_dir():
    global selected_dir
    selected_dir = tk.filedialog.askdirectory()
    lbl_selected_dir_var.set(selected_dir)


def add_keyword_from_entry():
    word = ent_search_var.get()
    if word is not string.whitespace and len(word) > 0:
        lb_keywords.insert(0, word)
        ent_search_var.set("")


def remove_keyword_selected():
    global lb_keywords
    selection = lb_keywords.curselection()
    if selection:
        index = selection[0]
        lb_keywords.delete(index)


def file_selected(event):
    global last_selected_file, file_text
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        data = event.widget.get(index)
        if last_selected_file != data:
            last_selected_file = data
            with open(data, "r") as file:
                file_text.config(state=tk.NORMAL)
                file_text.delete("1.0", tk.END)
                text = file.read()
                file_text.insert(tk.END, text)
                file_text.config(state=tk.DISABLED)


def create_abstract(input_str, kw):
    # words = input_str.lower().split(" ")
    # indices = [index for index, word in enumerate(words) if word == kw.lower()]
    indices = [m.start() for m in re.finditer(r'\b' + kw + r'\b', input_str)]
    abstract_text.config(state=tk.NORMAL)
    abstract_text.delete("1.0", tk.END)
    for c, index in enumerate(indices):
        abstract_text.insert(tk.END, f"Abstract {c}: \n")
        # abstract_text.insert(tk.END, f"{' '.join(words[max(index - 50, 0):index + 50])} \n")
        abstract_text.insert(tk.END, f"{input_str[max(index - 50, 0):index + 50]} \n")

    abstract_text.config(state=tk.DISABLED)







def accuracy_all():
    data_amount = 579
    cumm_acc = 0
    for i in range(data_amount):
        tr = transcribe("recordings/english{}.mp3".format(i + 1))
        acc = calculate_accuracy(tr.hyp().hypstr)
        print("Accuracy one: {}".format(acc))
        cumm_acc += acc
        print("Accuracy all: {}".format(cumm_acc / (i + 1)))
    print("Accuracy overall: {}".format(cumm_acc / data_amount))


def transcribe(audio_file_path):
    decoder = create_decoder()
    raw_data = convert_audio_to_raw(audio_file_path)

    decoder.start_utt()
    decoder.process_raw(raw_data, False, True)
    decoder.end_utt()

    return decoder


def keyword_search(audio_file_path, keyword_entries):
    decoder = create_decoder()
    raw_data = convert_audio_to_raw(audio_file_path)

    temp_file_descriptor, temp_file_path = tempfile.mkstemp()
    file = os.fdopen(temp_file_descriptor, "w")
    file.writelines("{} /1e{}/\n".format(keyword.lower(), sensitivity) for keyword, sensitivity in keyword_entries)
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


def print_segments(segments):
    fps = 100  # Standard rate
    print("-" * 28)
    print("| %5s |  %3s  |   %4s   |" % ("start", "end", "word"))
    for s in segments:
        print("| %4ss | %4ss | %8s |" % (s.start_frame / fps, s.end_frame / fps, s.word))
    print("-" * 28)


def calculate_accuracy(prediction):
    utterance = open("reading-passage.txt", "r").read().lower()
    utterance = utterance.replace(".", "").replace(",", "").replace(":", "").replace("  ", " ")
    word_list = utterance.split(" ")
    word_list = set(word_list)
    correct = len(word_list.intersection(prediction.split(" ")))

    return (correct / len(word_list)) * 100


if __name__ == "__main__":
    main()
