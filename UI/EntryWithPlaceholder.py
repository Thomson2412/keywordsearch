import tkinter as tk


class EntryWithPlaceholder(tk.Entry):
    def __init__(self,
                 master=None,
                 width=None,
                 textvariable=None,
                 placeholder="",
                 color="grey",
                 ):
        super().__init__(master, width=width, textvariable=textvariable, fg="black", bg="white")

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.has_placeholder = True
        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color
        self.has_placeholder = True

    def remove_placeholder(self):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color
            self.has_placeholder = False

    def foc_in(self, *args):
        self.remove_placeholder()

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()
