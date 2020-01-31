from Tkinter import *
from collections import OrderedDict
import os, subprocess
from data.packages.frames.util import Util as Util

class Ribbon(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.parent = master
        self.pack(fill=X, expand=1)
        self.content = None
        self.file_label = None
        self.setup()

    def setup(self):
        self.rebuild()
        self.info_bar()
        self.add_actions()

    def rebuild(self):
        if self.content:
            self.content.destroy()
        self.content = Frame(self)
        self.content.pack(fill=X, expand=1)

    def info_bar(self):
        info = Frame(self.content)
        info.pack(fill=X, expand=1)
        self.file_label = Label(info, text='No file Loaded: (click here to load)', pady=10, padx=10, bg='yellow')
        self.file_label.bind('<Button-1>', lambda e: self.parent.load_config())
        self.file_label.pack()

    def update_file_label(self, file_name):
        try:
            name = os.path.splitext(os.path.basename(file_name))[0]
        except:
            name = 'No file Loaded'
        self.file_label.config(text='Currently loaded file: %s' % name, bg='white')

    def open_input_folder(self):
        path = os.path.join(os.getcwd(), Util.INPUT_ROOT)
        subprocess.Popen(r'explorer "%s"' % path)

    def open_output_folder(self):
        path = os.path.join(os.getcwd(), Util.OUTPUT_ROOT)
        subprocess.Popen(r'explorer "%s"' % path)

    def add_actions(self):
        content = OrderedDict()
        content['Run']= self.parent.run
        content['Edit']= self.parent.edit
        content['Remove']= self.parent.remove
        
        content['Open Input']= self.open_input_folder
        content['Open Output']= self.open_output_folder
        bf = Frame(self.content)
        bf.pack(expand=1)
        for k, v in content.items():
            b = Button(bf, text=k, command=v)
            b.pack(side=LEFT, padx=10, pady=5)
