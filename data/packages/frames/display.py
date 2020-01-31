from Tkinter import *
import tkMessageBox
from collections import OrderedDict
import os
from data.packages.frames.picker import Picker
from data.packages.frames.util import Util as Util
from data.packages.frames.job import Job
from data.packages.frames.free import Free
from data.packages.frames.split import Split
from data.packages.frames.filter import Filter
from data.packages.frames.selection import Selection

class Display(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.parent = master
        self.content = None
        self.wizard = None
        self.job = None
        self.default()
        self.showing = None

    def rebuild(self):
        if self.content:
            self.content.destroy()
        self.content = Frame(self)
        self.content.pack(fill=BOTH, expand=1)

    def get_name(self, caller):
        if self.job:
            self.job.caller = caller
            f = Free(return_callback=self.job.validate, return_view=self.content, master=self)
            f.show()
            
            try:
                count = len(self.parent.config['work'][self.job.action])
                choice = Util.get_output_name(self.job, count + 1)
            except:
                choice = None

            f.set_default_text(choice if choice else Util.DEFAULT_PROMPT)
            f.entry.focus()
            f.entry.select_range(0, END)

    def get_sheet(self, caller, key):
        if self.job:
            self.job.caller = caller
            Picker(get_options=lambda: Util.get_sheet_name(self.job, key), return_callback=lambda e=caller: self.job.validate(e), return_view=self.content, master=self).show()

    def get_column(self, caller, key):
        if self.job:
            self.job.caller = caller
            Picker(get_options=lambda: Util.get_column_names(self.job, key), return_callback=self.job.validate, return_view=self.content, master=self).show()

    def get_columns(self, caller, key):
        if self.job:
            self.job.caller = caller
            Split(key, get_options=lambda: Util.get_column_names(self.job, key), return_callback=self.job.validate, return_view=self.content, master=self).show()

    def get_filter(self, caller, key):
        if self.job:
            self.job.caller = caller
            f = Filter(job=self.job, return_view=self.content, master=self)
            f.show()

    def fill_cols(self, caller, key):
        if self.job:
            self.job.caller = caller
            Split(key, get_options=lambda: Util.get_column_names(self.job, key), return_callback=self.__fill_cols, return_view=self.content, master=self).show()


    def __fill_cols(self, *stuff):
        _, selections = stuff
        self.job.set_value('add_col', selections)
    
        if self.job:
            self.job.validate()

    def get_file(self, path, ext, callback):
        if self.showing == None:
            prompt = "Select a master file to load."          
            picker = Picker(get_options= lambda: Util.get_file_list(path, ext), return_callback=lambda e: self.__get_file(e, callback), return_view=self.content, master=self, prompt=prompt)
            self.showing = picker
            picker.show()

    def __get_file(self, values, callback):
        self.showing.hide()
        self.showing = None
        callback(values)

    def new_job(self, action):
        if self.job:
            tkMessageBox.showinfo("Warning", "Please submit or cancel the current task before starting a new one.")
        else:
            self.job = Job(self, action)

            if self.content:
                self.content.destroy()
            if self.wizard:
                self.wizard.destroy()

            self.content = Frame(self)
            self.content.pack(fill=BOTH, expand=1)

            Label(self.content, text='Starting %s' % action.title()).pack()

            self.wizard = Frame(self.content)
            self.wizard.pack(fill=BOTH)

            controls = Frame(self.content)
            controls.pack()
            Button(controls, text='Cancel', command=self.cancel_job).pack(fill=X, side=LEFT, padx=10, pady=10)
            done = Button(controls, text='Submit', command=self.complete_job, state=DISABLED)
            self.job.done = done
            done.pack(fill=X, side=LEFT, padx=10, pady=10)

            self.job.next()

    def edit_job(self, action, index):
        if self.job:
            tkMessageBox.showinfo("Warning", "Please submit or cancel the current task before starting a new one.")
        else:
            self.new_job(action)
            self.job.edit(index, self.parent.config)

    def complete_job(self):
        self.job.complete_job()
        self.default()
        self.parent.save_config()
        self.job = None

    def cancel_job(self):
        self.job = None
        self.default()

    def default(self):
        self.rebuild()
        default_text = """
            Welcome

            To load a file, select file and load.
            Optionally, you cause double click the file name in the ribbon.

            After a file is loaded, you can add a new action by clicking the button in the left pane.
            You can edit or remove and action by selecting it and clicking the edit/remove button in the ribbon.

            To run the actions configured on the master file, click the run button in the ribbon.
        """
        Label(self.content, text=default_text).pack(fill=BOTH, padx=10, pady=10)

