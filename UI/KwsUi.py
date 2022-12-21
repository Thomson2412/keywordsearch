import json
import os
import re
import string
import time
import tkinter as tk
import tkinter.filedialog
import tkinter.ttk
from AudioTranscribe import AudioTranscribe
import RawAudioPlayer
from UI.EntryWithPlaceholder import EntryWithPlaceholder


class KwsUi:
    def __init__(self) -> None:
        super().__init__()
        self.window = tk.Tk()
        self.window.title("ViFrU - keyword search")
        self.window.configure(bg="#e0e0e0")
        self.selected_dir = "No dir selected"
        self.file_info = {}
        self.lbl_selected_dir_var = tk.StringVar(value=self.selected_dir)

        self.lbl_abstract_header_var = tk.StringVar()
        self.lbl_text_header_var = tk.StringVar()

        self.ent_search_var = tk.StringVar()
        self.lb_keywords_content_var = tk.Variable(value=[])
        self.lb_files_content_var = tk.Variable(value=[])

        self.lb_time_words_content_var = tk.Variable(value=[])

        self.ent_snippet_padding_var = tk.StringVar()

        self.last_selected_file = ""
        self.last_selected_snippet = -1

        self.window.columnconfigure(0, weight=1, minsize=100)
        self.window.columnconfigure(1, weight=1, minsize=200)
        self.window.columnconfigure(2, weight=1, minsize=100)
        self.window.rowconfigure([0, 1], weight=1, minsize=100)

        frame_config = tk.Frame(self.window)
        frame_config.grid(row=0, column=0, sticky="nsew")
        lbl_keywords = tk.Label(frame_config, text="Keywords")
        lbl_keywords.pack(side=tk.TOP, fill=tk.X, expand=False)
        self.lb_keywords = tk.Listbox(frame_config, selectmode=tk.MULTIPLE, listvariable=self.lb_keywords_content_var)
        self.lb_keywords.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # lb_keywords.bind('<<ListboxSelect>>', keyword_selected)

        self.ent_keywords = EntryWithPlaceholder(frame_config, width=40, textvariable=self.ent_search_var,
                                                 placeholder="Enter keyword")
        self.ent_keywords.pack(side=tk.TOP, fill=tk.X, expand=False)
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

        frame_transcribe_controls = tk.Frame(self.window)
        frame_transcribe_controls.grid(row=0, column=2, sticky="nsew")
        lbl_audio_header = tk.Label(frame_transcribe_controls, text="Transcribe options")
        lbl_audio_header.pack(side=tk.TOP, fill=tk.X, expand=False)
        btn_all_transcribe = tk.Button(frame_transcribe_controls, text="Transcribe all",
                                       command=self.transcribe_audio_all)
        btn_all_transcribe.pack(side=tk.TOP, fill=tk.X, expand=False)
        btn_one_transcribe = tk.Button(frame_transcribe_controls, text="Transcribe selected",
                                       command=self.transcribe_audio_single_btn)
        btn_one_transcribe.pack(side=tk.TOP, fill=tk.X, expand=False)
        btn_save_text = tk.Button(frame_transcribe_controls, text="Save transcription text",
                                  command=self.save_transcription_btn)
        btn_save_text.pack(side=tk.TOP, fill=tk.X, expand=False)
        # btn_copy_all_text = tk.Button(frame_transcribe_controls, text="Copy all transcriptions text",
        #                               command=self.copy_all_transcription_btn)
        # btn_copy_all_text.pack(side=tk.TOP, fill=tk.X, expand=False)
        btn_save_abstract = tk.Button(frame_transcribe_controls, text="Save abstract text",
                                      command=self.save_abstract_btn)
        btn_save_abstract.pack(side=tk.TOP, fill=tk.X, expand=False)

        frame_time_words = tk.Frame(self.window)
        frame_time_words.grid(row=1, column=2, sticky="nsew")
        lbl_time_header = tk.Label(frame_time_words, text="Timestamps and snippets")
        lbl_time_header.pack(side=tk.TOP, fill=tk.X, expand=False)
        self.btn_play_snippet = tk.Button(frame_time_words, text="Play snippet",
                                          command=self.play_stop_snippet_btn)
        self.btn_play_snippet.pack(side=tk.TOP, fill=tk.X, expand=False)
        btn_save_snippet = tk.Button(frame_time_words, text="Save snippet",
                                     command=self.save_snippet_btn)
        btn_save_snippet.pack(side=tk.TOP, fill=tk.X, expand=False)
        ent_snippet_padding = EntryWithPlaceholder(frame_time_words, width=40,
                                                   textvariable=self.ent_snippet_padding_var,
                                                   placeholder="Snippet padding (Seconds)")
        ent_snippet_padding.pack(side=tk.TOP, fill=tk.X, expand=False)
        lb_time_words = tk.Listbox(frame_time_words, listvariable=self.lb_time_words_content_var)
        lb_time_words.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_time_words = tk.Scrollbar(frame_time_words, orient="vertical")
        sb_time_words.config(command=lb_time_words.yview)
        sb_time_words.pack(side=tk.RIGHT, fill=tk.Y)
        lb_time_words.config(yscrollcommand=sb_time_words.set)
        lb_time_words.bind('<<ListboxSelect>>', self.time_word_selected)

        frame_progress = tk.Frame(self.window)
        frame_progress.grid(row=2, column=0, columnspan=3, sticky="nsew")
        self.progress_bar = tk.ttk.Progressbar(frame_progress, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_label = tk.Label(frame_progress, text="Ready")
        self.progress_label.pack(side=tk.RIGHT)

        self.audio_transcriber = AudioTranscribe("base.en")

        self.audio_player = RawAudioPlayer.RawAudioPlayer(self.play_end, self.update_progress_bar)

        self.window.mainloop()

    def populate_files(self, keywords):
        if len(self.file_info) > 0:
            filepath_list = []
            if len(keywords) > 0:
                self.update_progress_bar(0, len(self.file_info))
                for i, (file, content) in enumerate(self.file_info.items()):
                    if self.file_info[file]["has_transcription"]:
                        all_match = True
                        for kw in keywords:
                            if not re.search(r'\b' + kw + r'\b', self.create_text_from_filepath(file)):
                                all_match = False
                                break
                        if all_match:
                            filepath_list.append(file)
                        self.update_progress_bar(i + 1, len(self.file_info))
            else:
                filepath_list = list(self.file_info.keys())
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
        new_dir = tk.filedialog.askdirectory()
        if new_dir == "" or len(new_dir) == 0:
            return
        else:
            self.selected_dir = new_dir
        self.lbl_selected_dir_var.set(self.selected_dir)
        self.file_info = {}
        for root, dirs, files in os.walk(self.selected_dir):
            files_amount = len(files)
            for i, filename in enumerate(files):
                if i == 0:
                    self.update_progress_bar(i, files_amount)
                if filename.endswith(".wav") or filename.endswith(".mp3"):
                    filepath = os.path.splitext(filename)[0]
                    filepath_audio = os.path.join(root, filename)
                    filepath_json = os.path.join(root, f"{filepath}.json")

                    has_transcription = False
                    if os.path.exists(filepath_json):
                        has_transcription = True
                    self.file_info[filepath] = {
                        "filepath_audio": filepath_audio,
                        "filepath_json": filepath_json,
                        "has_transcription": has_transcription
                    }
                self.update_progress_bar(i + 1, files_amount)
        keywords = list(self.lb_keywords_content_var.get())
        self.populate_files(keywords)

    def add_keyword_from_entry(self):
        word = self.ent_search_var.get()
        if word is not string.whitespace and len(word) > 0 and not self.ent_keywords.has_placeholder:
            keywords = list(self.lb_keywords_content_var.get())
            if word not in keywords:
                keywords.append(word)
                self.lb_keywords_content_var.set(keywords)
                self.populate_files(keywords)
                if self.last_selected_file != "":
                    self.create_file_text(self.last_selected_file)
                    self.display_abstract(self.last_selected_file, keywords)
                    self.search_keyword_timestamps_in_time_file(self.last_selected_file, keywords)
            self.ent_search_var.set("")

    def remove_keyword_selected(self):
        selection = self.lb_keywords.curselection()
        if len(selection) > 0:
            for index in reversed(selection):
                self.lb_keywords.delete(index)
            keywords = list(self.lb_keywords_content_var.get())
            self.populate_files(keywords)
            if self.last_selected_file != "":
                self.create_file_text(self.last_selected_file)
                self.display_abstract(self.last_selected_file, keywords)
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
                self.display_abstract(self.last_selected_file, keywords)
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
            if self.file_info[file]["has_transcription"]:
                text = self.create_text_from_filepath(file)
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
            content = self.file_info[file]
            lines = []
            with open(content["filepath_json"], "r") as f:
                content_json = json.load(f)
                for kw in keywords:
                    count = 0
                    for key, line_info in content_json.items():
                        line = line_info["line"]
                        if kw in line:
                            count += 1
                            lines.append(f"Abstract for {kw}, instance {count}: \n")
                            int_key = int(key)
                            if int_key > 0:
                                lines.append(content_json[str(int_key - 1)]["line"])
                            if int_key < len(content_json):
                                lines.append(content_json[str(int_key + 1)]["line"])
                            lines.append(line)
                            lines.append("\n\n")
                    lines.append("\n")
                return lines
        return []

    def display_abstract(self, file, keywords):
        self.clear_abstract()
        lines = self.create_abstract(file, keywords)
        if len(lines) > 0:
            self.lbl_abstract_header_var.set(", ".join(keywords))
            self.abstract_text.config(state=tk.NORMAL)
            for line in lines:
                self.abstract_text.insert(tk.END, line)
            self.abstract_text.config(state=tk.DISABLED)

    def transcribe_audio_single_btn(self):
        if self.last_selected_file != "":
            self.transcribe_audio_single(self.last_selected_file)
            self.create_file_text(self.last_selected_file)
            self.display_abstract(self.last_selected_file, list(self.lb_keywords_content_var.get()))
            self.search_keyword_timestamps_in_time_file(self.last_selected_file,
                                                        list(self.lb_keywords_content_var.get()))

    def transcribe_audio_single(self, filename):
        if filename in self.file_info.keys():
            content = self.file_info[filename]
            self.update_progress_bar(0, 1)
            result = self.audio_transcriber.transcribe(content["filepath_audio"], self.update_progress_bar)

            with open(content["filepath_json"], "w") as f:
                json.dump(result, f, indent=4)
                content["has_transcription"] = True

            # with open(content["filepath_txt"], "w") as f:
            #     f.write(" ".join([r["line"] for r in result.values()]))
            #     content["has_transcription"] = True

            self.update_progress_bar(1, 1)

    def transcribe_audio_all(self):
        files_amount = len(self.file_info)
        self.update_progress_bar(0, files_amount)
        for i, filename in enumerate(self.file_info.keys()):
            self.transcribe_audio_single(filename)
            self.update_progress_bar(i + 1, files_amount)

    def get_timestamps_for_keywords(self, filename, keywords):
        result = []
        if filename in self.file_info.keys():
            content = self.file_info[filename]
            if len(keywords) > 0 and content["has_transcription"]:
                with open(content["filepath_json"], "r") as f:
                    content_json = json.load(f)
                    for kw in keywords:
                        for line_info in content_json.values():
                            if kw in line_info["line"]:
                                result.append([kw, line_info["start"], line_info["end"]])
        return result

    def search_keyword_timestamps_in_time_file(self, filename, keywords):
        self.lb_time_words_content_var.set([])
        self.last_selected_snippet = - 1
        timestamps = self.get_timestamps_for_keywords(filename, keywords)
        to_show_times = []
        for timestamp in timestamps:
            start = time.strftime('%H:%M:%S', time.gmtime(timestamp[1]))
            end = time.strftime('%H:%M:%S', time.gmtime(timestamp[2]))
            to_show_times.append(f"{timestamp[0]}: {start} - {end}")
        self.lb_time_words_content_var.set(to_show_times)

    def time_word_selected(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.last_selected_snippet = index

    def play_stop_snippet_btn(self):
        if self.audio_player.is_playing:
            self.audio_player.stop()
            self.btn_play_snippet["text"] = "Play snippet"
        else:
            if self.last_selected_file != "" and self.last_selected_snippet >= 0:
                keywords = list(self.lb_keywords_content_var.get())
                if len(keywords) > 0:
                    timestamps = self.get_timestamps_for_keywords(self.last_selected_file, keywords)
                    timestamp = timestamps[self.last_selected_snippet]
                    padding_txt = self.ent_snippet_padding_var.get()
                    padding = 0
                    if padding_txt.isnumeric():
                        padding = int(padding_txt)
                    self.audio_player.play_snippet(
                        self.file_info[self.last_selected_file]["filepath_audio"],
                        timestamp[1],
                        timestamp[2],
                        padding
                    )
                    self.btn_play_snippet["text"] = "Stop snippet"

    def play_end(self):
        self.update_progress_bar(1, 1)
        self.btn_play_snippet["text"] = "Play snippet"

    def save_snippet_btn(self):
        if self.last_selected_file != "" and self.last_selected_snippet >= 0:
            keywords = list(self.lb_keywords_content_var.get())
            if len(keywords) > 0:
                timestamps = self.get_timestamps_for_keywords(self.last_selected_file, keywords)
                timestamp = timestamps[self.last_selected_snippet]
                padding_txt = self.ent_snippet_padding_var.get()
                padding = 0
                if padding_txt.isnumeric():
                    padding = int(padding_txt)
                cut_audio_segment = RawAudioPlayer.cut_audio(
                    self.file_info[self.last_selected_file]["filepath_audio"],
                    timestamp[1],
                    timestamp[2],
                    padding
                )
                output_file_path = tk.filedialog.asksaveasfilename(defaultextension=".wav")
                cut_audio_segment.export(output_file_path, format="wav")

    def save_transcription_btn(self):
        if self.last_selected_file != "" and self.file_info[self.last_selected_file]["has_transcription"]:
            selected_txt = self.create_text_from_filepath(self.last_selected_file)
            output_file_path = tk.filedialog.asksaveasfilename(defaultextension=".txt")
            with open(output_file_path, "w") as f:
                f.write(selected_txt)

    def copy_all_transcription_btn(self):
        if self.last_selected_file != "":
            keywords = list(self.lb_keywords_content_var.get())
            if len(keywords) > 0:
                timestamps = self.get_timestamps_for_keywords(self.last_selected_file, keywords)
                timestamp = timestamps[self.last_selected_snippet]
                padding_txt = self.ent_snippet_padding_var.get()
                padding = 0
                if padding_txt.isnumeric():
                    padding = int(padding_txt)
                cut_audio_segment = RawAudioPlayer.cut_audio(
                    self.file_info[self.last_selected_file]["filepath_audio"],
                    timestamp[1],
                    timestamp[2],
                    padding
                )
                output_file_path = tk.filedialog.asksaveasfilename(defaultextension=".wav")
                cut_audio_segment.export(output_file_path, format="wav")

    def save_abstract_btn(self):
        if self.last_selected_file != "" and self.file_info[self.last_selected_file]["has_transcription"]:
            keywords = list(self.lb_keywords_content_var.get())
            if len(keywords) > 0:
                selected_abstract = self.create_abstract(self.last_selected_file, keywords)
                output_file_path = tk.filedialog.asksaveasfilename(defaultextension=".txt")
                with open(output_file_path, "w") as f:
                    f.write("".join(selected_abstract))

    def create_text_from_filepath(self, filepath):
        if filepath in self.file_info.keys():
            content = self.file_info[filepath]
            with open(content["filepath_json"], "r") as f:
                content_json = json.load(f)
                text = " ".join([r["line"] for r in content_json.values()])
                return text

    def update_progress_bar(self, current, total):
        percentage = (current / total) * 100
        if 0 <= percentage < 100:
            self.progress_bar["value"] = percentage
            self.progress_label["text"] = f"({current} / {total})"
        if percentage == 100:
            self.progress_bar["value"] = 0
            self.progress_label["text"] = "Ready"
        self.window.update_idletasks()
