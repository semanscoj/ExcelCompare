from Tkinter import *
from collections import OrderedDict
from glob import glob
import os

class Button_options(Frame):
    def __init__(self, setup=None, return_view=None, master=None):
        Frame.__init__(self, master)
        self.parent = master
        self.setup = setup
        self.old_content = return_view # view to restore when THIS frame is hidden
        self.content = None # view to show when THIS frame is visible

    def rebuild(self):
        if self.content:
            self.content.destroy()
        self.content = Frame(self.master) 
        self.content.pack(fill=BOTH, expand=1)
        prompt = self.setup['prompt'] if 'prompt' in self.setup else 'Choose an Option to proceed:'
        Label(self.content, text=prompt).pack(fill=X, pady=10)

        if self.setup and 'buttons' in self.setup:
            for button in self.setup['buttons']:
                text = button['text']
                cb = button['command']
                b = Button(self.content, text=text, command=lambda e=cb: self.submit(e))
                b.pack()

    def show(self):
        self.old_content.pack_forget()
        self.rebuild()

    def hide(self):
        self.content.pack_forget()
        self.old_content.pack(fill=X)

    def submit(self, cb):
        self.hide()
        cb()
 
