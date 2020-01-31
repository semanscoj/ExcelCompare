from Tkinter import *
from collections import OrderedDict
from glob import glob
import os

class Free(Frame):
    def __init__(self, return_view=None, return_callback=None, master=None):
        Frame.__init__(self, master)
        self.parent = master
        self.old_content = return_view # view to restore when THIS frame is hidden
        self.callback = return_callback # data to pass value back on on submit
        self.content = None # view to show when THIS frame is visible
        self.entry = None # entry field to filter selections

    def rebuild(self):
        if self.content:
            self.content.destroy()
        if self.entry:
            self.entry.destroy()
        self.content = Frame(self.master) 
        self.content.pack(fill=BOTH, expand=1)
        self.sv = StringVar()
        Label(self.content, text='Please enter a name in the box below:').pack(fill=X)
        self.entry = Entry(self.content, textvariable=self.sv)
        self.entry.bind('<Return>', self.submit)
        self.entry.pack(fill=X, pady=20, padx=20)

    def set_default_text(self, text):
        self.entry.insert(0, text)

    def show(self):
        self.old_content.pack_forget()
        self.rebuild()

    def hide(self):
        self.content.pack_forget()
        self.old_content.pack(fill=X)

    def submit(self, event):
        try:
            if self.callback:
                self.callback(self.sv.get())
            else:
                print(context_str, context_index)
            self.hide()
        except IndexError as e:
            pass
