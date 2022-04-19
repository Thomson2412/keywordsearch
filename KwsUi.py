import json
import os
import re
import string
import time
import tkinter as tk
import tkinter.filedialog
import tkinter.ttk
from AudioTranscribe import AudioTranscribe


def time_word_selected(event):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        data = event.widget.get(index)
        print(data)


class KwsUi:
    def __init__(self) -> None:
        super().__init__()
        self.window = tk.Tk()
        self.window.title("ViFrU - keyword search")
        self.window.configure(bg="#e0e0e0")
        self.selected_dir = "No dir selected"
        self.file_content = {}
        self.lbl_selected_dir_var = tk.StringVar(value=self.selected_dir)

        self.lbl_abstract_header_var = tk.StringVar()
        self.lbl_text_header_var = tk.StringVar()

        self.ent_search_var = tk.StringVar()
        self.lb_keywords_content_var = tk.Variable(value=[])
        self.lb_files_content_var = tk.Variable(value=[])

        self.lb_time_words_content_var = tk.Variable(value=[])

        self.last_selected_file = ""

        self.window.columnconfigure(0, weight=1, minsize=400)
        self.window.columnconfigure(1, weight=1, minsize=800)
        self.window.columnconfigure(2, weight=1, minsize=400)
        self.window.rowconfigure([0, 1], weight=1, minsize=400)

        frame_config = tk.Frame(self.window)
        frame_config.grid(row=0, column=0, sticky="nsew")
        lbl_keywords = tk.Label(frame_config, text="Keywords")
        lbl_keywords.pack(side=tk.TOP, fill=tk.X, expand=False)
        self.lb_keywords = tk.Listbox(frame_config, selectmode=tk.MULTIPLE, listvariable=self.lb_keywords_content_var)
        self.lb_keywords.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # lb_keywords.bind('<<ListboxSelect>>', keyword_selected)

        entry_keywords = tk.Entry(frame_config, width=40, bg="white", fg="black", textvariable=self.ent_search_var)
        entry_keywords.pack(side=tk.TOP, fill=tk.X, expand=False)
        btn_word_remove = tk.Button(frame_config, text="-", command=self.remove_keyword_selected)
        btn_word_remove.pack(side=tk.LEFT, fill=tk.X, expand=True)
        btn_word_add = tk.Button(frame_config, text="+", command=self.add_keyword_from_entry)
        btn_word_add.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        frame_files = tk.Frame(self.window)
        frame_files.grid(row=1, column=0, sticky="nsew")
        btn_load_dir = tk.Button(frame_files, text="Load directory", command=self.select_dir)
        btn_load_dir.pack(side=tk.TOP, fill=tk.X, expand=False)
        lbl_selected_dir = tk.Label(frame_files, textvariable=self.lbl_selected_dir_var)
        lbl_selected_dir.pack(side=tk.TOP, fill=tk.X, expand=False)

        lb_files = tk.Listbox(frame_files, listvariable=self.lb_files_content_var)
        lb_files.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_files = tk.Scrollbar(frame_files, orient="vertical")
        sb_files.config(command=lb_files.yview)
        sb_files.pack(side=tk.RIGHT, fill=tk.Y)
        lb_files.config(yscrollcommand=sb_files.set)
        lb_files.bind('<<ListboxSelect>>', self.file_selected)

        frame_abstract = tk.Frame(self.window)
        frame_abstract.grid(row=0, column=1, sticky="nsew")
        lbl_abstract_header = tk.Label(frame_abstract, textvariable=self.lbl_abstract_header_var)
        lbl_abstract_header.pack(side=tk.TOP, fill=tk.X, expand=False)
        self.abstract_text = tk.Text(frame_abstract)
        self.abstract_text.config(state=tk.DISABLED)
        self.abstract_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_abstract = tk.Scrollbar(frame_abstract, orient="vertical")
        sb_abstract.config(command=self.abstract_text.yview)
        sb_abstract.pack(side=tk.RIGHT, fill=tk.Y)
        self.abstract_text.config(yscrollcommand=sb_abstract.set)

        frame_text = tk.Frame(self.window)
        frame_text.grid(row=1, column=1, sticky="nsew")
        lbl_text_header = tk.Label(frame_text, textvariable=self.lbl_text_header_var)
        lbl_text_header.pack(side=tk.TOP, fill=tk.X, expand=False)
        self.file_text = tk.Text(frame_text)
        self.file_text.config(state=tk.DISABLED)
        self.file_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_text = tk.Scrollbar(frame_text, orient="vertical")
        sb_text.config(command=self.file_text.yview)
        sb_text.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_text.config(yscrollcommand=sb_text.set)

        frame_audio_controls = tk.Frame(self.window)
        frame_audio_controls.grid(row=0, column=2, sticky="nsew")
        lbl_audio_header = tk.Label(frame_audio_controls, text="Transcribe/Search options")
        lbl_audio_header.pack(side=tk.TOP, fill=tk.X, expand=False)
        btn_word_transcribe = tk.Button(frame_audio_controls, text="Transcribe all", command=self.transcribe_audio_all)
        btn_word_transcribe.pack(side=tk.TOP, fill=tk.X, expand=False)
        btn_word_transcribe = tk.Button(frame_audio_controls, text="Transcribe selected",
                                        command=self.transcribe_audio_single_btn)
        btn_word_transcribe.pack(side=tk.TOP, fill=tk.X, expand=False)

        frame_time_words = tk.Frame(self.window)
        frame_time_words.grid(row=1, column=2, sticky="nsew")
        lbl_time_header = tk.Label(frame_time_words, text="Timestamps")
        lbl_time_header.pack(side=tk.TOP, fill=tk.X, expand=False)
        lb_time_words = tk.Listbox(frame_time_words, listvariable=self.lb_time_words_content_var)
        lb_time_words.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_time_words = tk.Scrollbar(frame_time_words, orient="vertical")
        sb_time_words.config(command=lb_time_words.yview)
        sb_time_words.pack(side=tk.RIGHT, fill=tk.Y)
        lb_time_words.config(yscrollcommand=sb_time_words.set)
        lb_time_words.bind('<<ListboxSelect>>', time_word_selected)

        frame_progress = tk.Frame(self.window)
        frame_progress.grid(row=2, column=0, columnspan=3, sticky="nsew")
        self.progress_bar = tk.ttk.Progressbar(frame_progress, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_label = tk.Label(frame_progress, text="Ready")
        self.progress_label.pack(side=tk.RIGHT)

        self.audio_transcriber = AudioTranscribe("data/models/deepspeech-0.9.3-models.pbmm",
                                                 "data/models/deepspeech-0.9.3-models.scorer")

        self.window.mainloop()

    def populate_files(self, keywords):
        if len(self.file_content) > 0:
            filepath_list = []
            if len(keywords) > 0:
                self.update_progress_bar(0, len(self.file_content))
                for i, (file, content) in enumerate(self.file_content.items()):
                    all_match = True
                    for kw in keywords:
                        if not re.search(r'\b' + kw + r'\b', content["text"]):
                            all_match = False
                            break
                    if all_match:
                        filepath_list.append(file)
                    self.update_progress_bar(i + 1, len(self.file_content))
            else:
                filepath_list = list(self.file_content.keys())
            if len(filepath_list) == 0:
                self.last_selected_file = ""
            if self.last_selected_file not in filepath_list:
                self.last_selected_file = ""
                self.clear_abstract()
                self.clear_file_text()
                self.lb_time_words_content_var.set([])
            filepath_list.sort()
            self.lb_files_content_var.set(filepath_list)

    def select_dir(self):
        self.selected_dir = tk.filedialog.askdirectory()
        self.lbl_selected_dir_var.set(self.selected_dir)
        self.file_content = {}
        for root, dirs, files in os.walk(self.selected_dir):
            files_amount = len(files)
            for i, filename in enumerate(files):
                if i == 0:
                    self.update_progress_bar(i, files_amount)
                if filename.endswith(".wav") or filename.endswith(".mp3"):
                    filepath = os.path.splitext(filename)[0]
                    filepath_audio = os.path.join(root, filename)
                    filepath_txt = os.path.join(root, f"{filepath}.txt")
                    filepath_time = os.path.join(root, f"{filepath}.json")

                    text = ""
                    has_transcription = False
                    if os.path.exists(filepath_txt):
                        with open(filepath_txt, "r") as f:
                            text = f.read()
                            has_transcription = True
                    has_time_file = False
                    time_content = {}
                    if os.path.exists(filepath_time):
                        with open(filepath_time, "r") as f:
                            time_content = json.load(f)
                            has_time_file = True
                    self.file_content[filepath] = {
                        "text": text,
                        "time_content": time_content,
                        "filepath_audio": filepath_audio,
                        "filepath_txt": filepath_txt,
                        "has_transcription": has_transcription,
                        "filepath_time": filepath_time,
                        "has_time_file": has_time_file

                    }
                self.update_progress_bar(i + 1, files_amount)
        keywords = list(self.lb_keywords_content_var.get())
        self.populate_files(keywords)

    def add_keyword_from_entry(self):
        word = self.ent_search_var.get()
        if word is not string.whitespace and len(word) > 0:
            keywords = list(self.lb_keywords_content_var.get())
            if word not in keywords:
                keywords.append(word)
                self.lb_keywords_content_var.set(keywords)
                self.populate_files(keywords)
                if self.last_selected_file != "":
                    self.create_file_text(self.last_selected_file)
                    self.create_abstract(self.last_selected_file, keywords)
                    self.search_keyword_timestamps_in_time_file(self.last_selected_file, keywords)
            self.ent_search_var.set("")

    def remove_keyword_selected(self):
        selection = self.lb_keywords.curselection()
        if len(selection) > 0:
            for index in reversed(selection):
                self.lb_keywords.delete(index)
            keywords = list(self.lb_keywords_content_var.get())
            self.populate_files(keywords)
            if self.last_selected_file != "" and len(keywords) > 0:
                self.create_file_text(self.last_selected_file)
                self.create_abstract(self.last_selected_file, keywords)
                self.search_keyword_timestamps_in_time_file(self.last_selected_file, keywords)

    def file_selected(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            data = event.widget.get(index)
            # if self.last_selected_file != data:
            self.last_selected_file = data
            self.create_file_text(self.last_selected_file)
            keywords = list(self.lb_keywords_content_var.get())
            if len(keywords) > 0:
                self.create_abstract(self.last_selected_file, keywords)
                self.search_keyword_timestamps_in_time_file(self.last_selected_file, keywords)
            else:
                self.clear_abstract()
                self.lb_time_words_content_var.set([])

    def clear_file_text(self):
        self.lbl_text_header_var.set("")
        self.file_text.config(state=tk.NORMAL)
        self.file_text.delete("1.0", tk.END)
        self.file_text.config(state=tk.DISABLED)

    def create_file_text(self, file):
        if file != "":
            self.clear_file_text()
            if self.file_content[file]["has_transcription"]:
                text = self.file_content[file]["text"]
            else:
                text = "No transcription found"
            self.lbl_text_header_var.set(file)
            self.file_text.config(state=tk.NORMAL)
            self.file_text.insert(tk.END, text)
            self.file_text.config(state=tk.DISABLED)

    # def keyword_selected(event):
    #     global last_selected_keywords
    #     selection = event.widget.curselection()
    #     if len(selection) > 0:
    #         data = []
    #         for index in selection:
    #             data.append(event.widget.get(index))
    #         if set(last_selected_keywords) != set(data):
    #             last_selected_keywords = data
    #             if self.last_selected_file is not string.whitespace and len(self.last_selected_file) > 0:
    #                 with open(self.last_selected_file, "r") as file:
    #                     create_abstract(file.read(), last_selected_keywords)

    def clear_abstract(self):
        self.lbl_abstract_header_var.set("")
        self.abstract_text.config(state=tk.NORMAL)
        self.abstract_text.delete("1.0", tk.END)
        self.abstract_text.config(state=tk.DISABLED)

    def create_abstract(self, file, keywords):
        if file != "" and len(keywords) > 0:
            self.clear_abstract()
            text = self.file_content[file]["text"]
            self.lbl_abstract_header_var.set(", ".join(keywords))
            self.abstract_text.config(state=tk.NORMAL)
            for kw in keywords:
                indices = [m.start() for m in re.finditer(r'\b' + kw + r'\b', text)]
                for c, index in enumerate(indices):
                    self.abstract_text.insert(tk.END, f"Abstract for {kw}, instance {c}: \n")
                    self.abstract_text.insert(tk.END, f"{text[max(index - 50, 0):index + 50]} \n\n")
            self.abstract_text.config(state=tk.DISABLED)

    def transcribe_audio_single_btn(self):
        if self.last_selected_file != "":
            self.transcribe_audio_single(self.last_selected_file)
            self.create_file_text(self.last_selected_file)
            self.create_abstract(self.last_selected_file, list(self.lb_keywords_content_var.get()))
            self.search_keyword_timestamps_in_time_file(self.last_selected_file,
                                                        list(self.lb_keywords_content_var.get()))

    def transcribe_audio_single(self, filename):
        if filename in self.file_content.keys() and (not self.file_content[filename]["has_transcription"]
                                                     or not self.file_content[filename]["has_time_file"]):
            content = self.file_content[filename]
            result = self.audio_transcriber.transcribe(content["filepath_audio"], self.update_progress_bar)
            if not content["has_transcription"]:
                result_txt = " ".join(result[0])
                with open(content["filepath_txt"], "x") as f:
                    f.write(result_txt)
                    content["text"] = result_txt
                    content["has_transcription"] = True
            if not content["has_time_file"]:
                result_time = result[1]
                with open(content["filepath_time"], "x") as f:
                    json.dump(result_time, f, indent=4)
                    content["time_content"] = result_time
                    content["has_time_file"] = True

    def transcribe_audio_all(self):
        files_amount = len(self.file_content)
        self.update_progress_bar(0, files_amount)
        for i, filename in enumerate(self.file_content.keys()):
            self.transcribe_audio_single(filename)
            self.update_progress_bar(i + 1, files_amount)

    def search_keyword_timestamps_in_time_file(self, filename, keywords):
        self.lb_time_words_content_var.set([])
        if filename in self.file_content.keys():
            content = self.file_content[filename]
            if content["has_time_file"]:
                if len(keywords) > 0:
                    to_show_times = []
                    for kw in keywords:
                        if kw in content["time_content"]:
                            timestamps = content["time_content"][kw]
                            for timestamp in timestamps:
                                start = time.strftime('%H:%M:%S', time.gmtime(timestamp["start"]))
                                end = time.strftime('%H:%M:%S', time.gmtime(timestamp["end"]))
                                to_show_times.append(f"{kw}: {start} - {end}")
                                print(timestamp)
                    self.lb_time_words_content_var.set(to_show_times)

    def update_progress_bar(self, current, total):
        percentage = (current / total) * 100
        if 0 <= percentage < 100:
            self.progress_bar["value"] = percentage
            self.progress_label["text"] = f"({current} / {total})"
        if percentage == 100:
            self.progress_bar["value"] = 0
            self.progress_label["text"] = "Ready"
        self.window.update_idletasks()
