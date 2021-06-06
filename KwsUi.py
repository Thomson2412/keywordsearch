import os
import re
import string
import tkinter as tk
import tkinter.filedialog

import AudioTranscribe


class KwsUi:
    def __init__(self) -> None:
        super().__init__()
        self.window = tk.Tk()
        self.window.configure(bg="#e0e0e0")
        self.selected_dir = "No dir selected"
        self.file_content = {}
        self.lbl_selected_dir_var = tk.StringVar(value=self.selected_dir)

        self.lbl_abstract_header_var = tk.StringVar()
        self.lbl_text_header_var = tk.StringVar()

        self.ent_search_var = tk.StringVar()
        self.lb_keywords_content_var = tk.Variable(value=[])
        self.lb_files_content_var = tk.Variable(value=[])

        # self.abstract_text: tk.Text
        # self.file_text: tk.Text
        # self.lb_keywords: tk.Listbox

        self.last_selected_file = ""

        self.window.columnconfigure(0, weight=1, minsize=400)
        self.window.columnconfigure(1, weight=1, minsize=800)
        self.window.columnconfigure(2, weight=1, minsize=400)
        self.window.rowconfigure([0, 1], weight=1, minsize=400)

        frame_config = tk.Frame(self.window)
        frame_config.grid(row=0, column=0, sticky="nsew")
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

        frame_audio = tk.Frame(self.window)
        frame_audio.grid(row=0, column=2, sticky="nsew")
        btn_word_transcribe = tk.Button(frame_audio, text="Transcribe all", command=self.transcribe_audio_all)
        btn_word_transcribe.pack(side=tk.TOP, fill=tk.X, expand=True)
        btn_word_transcribe = tk.Button(frame_audio, text="Transcribe selected", command=self.transcribe_audio_single)
        btn_word_transcribe.pack(side=tk.TOP, fill=tk.X, expand=True)
        btn_word_search = tk.Button(frame_audio, text="Search", command=self.search_keywords_in_audio)
        btn_word_search.pack(side=tk.TOP, fill=tk.X, expand=True)

        self.window.mainloop()

    def populate_files(self, keywords):
        if len(self.file_content) > 0:
            filepath_list = []
            if len(keywords) > 0:
                for file, content in self.file_content.items():
                    all_match = True
                    for kw in keywords:
                        if not re.search(r'\b' + kw + r'\b', content["text"]):
                            all_match = False
                            break
                    if all_match:
                        filepath_list.append(file)
            else:
                filepath_list = list(self.file_content.keys())
            self.lb_files_content_var.set(filepath_list)

    def select_dir(self):
        self.selected_dir = tk.filedialog.askdirectory()
        self.lbl_selected_dir_var.set(self.selected_dir)
        for root, dirs, files in os.walk(self.selected_dir):
            for filename in files:
                if filename.endswith(".wav") or filename.endswith(".mp3"):
                    filepath = os.path.splitext(filename)[0]
                    filepath_audio = os.path.join(root, filename)
                    filepath_txt = os.path.join(root, f"{filepath}.txt")

                    text = ""
                    has_transcription = False
                    if os.path.exists(filepath_txt):
                        with open(filepath_txt, "r") as f:
                            text = f.read()
                            has_transcription = True
                    self.file_content[filepath] = {
                        "text": text,
                        "filepath_audio": filepath_audio,
                        "filepath_txt": filepath_txt,
                        "has_transcription": has_transcription
                    }
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
            self.ent_search_var.set("")

    def remove_keyword_selected(self):
        selection = self.lb_keywords.curselection()
        if len(selection) > 0:
            for index in reversed(selection):
                self.lb_keywords.delete(index)
            keywords = list(self.lb_keywords_content_var.get())
            self.populate_files(keywords)
            self.clear_abstract()
            self.clear_file_text()

    def file_selected(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            data = event.widget.get(index)
            if self.last_selected_file != data:
                self.last_selected_file = data
                self.create_file_text(self.last_selected_file)
                keywords = list(self.lb_keywords_content_var.get())
                if len(keywords) > 0:
                    self.create_abstract(self.last_selected_file, keywords)

    def clear_file_text(self):
        self.lbl_text_header_var.set("")
        self.file_text.config(state=tk.NORMAL)
        self.file_text.delete("1.0", tk.END)
        self.file_text.config(state=tk.DISABLED)

    def create_file_text(self, file):
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

    def transcribe_audio_single(self):
        selected_file_content = self.file_content[self.last_selected_file]
        if not selected_file_content["has_transcription"]:
            result = AudioTranscribe.transcribe(selected_file_content["filepath_audio"])
            with open(selected_file_content["filepath_txt"], "x") as f:
                f.write(result)
            selected_file_content["text"] = result
            selected_file_content["has_transcription"] = True
            self.create_file_text(self.last_selected_file)

    def transcribe_audio_all(self):
        for content in self.file_content.values():
            if not content["has_transcription"]:
                result = AudioTranscribe.transcribe(content["filepath_audio"])
                with open(content["filepath_txt"], "x") as f:
                    f.write(result)
                content["text"] = result
                content["has_transcription"] = True

    def search_keywords_in_audio(self):
        selected_file_content = self.file_content[self.last_selected_file]
        if selected_file_content["has_transcription"]:
            search_list = []
            keywords = list(self.lb_keywords_content_var.get())
            for kw in keywords:
                search_list.append((kw, 20))
            file_to_search = f"{self.last_selected_file}{selected_file_content['audio_extension']}"
            result = AudioTranscribe.keyword_search(file_to_search, search_list)
            print(result)
