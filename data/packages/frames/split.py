from Tkinter import *

from collections import OrderedDict
from glob import glob
from util import Util
import os

class Split(Frame):
    def __init__(self, key, column=None, get_options=None, return_view=None, return_callback=None, master=None, prompt=None):
        Frame.__init__(self, master)
        self.parent = master
        self.key = key
        self.column=column
        self.get_options = get_options
        self.old_content = return_view # view to restore when THIS frame is hidden
        self.callback = return_callback # data to pass value back on on submit
        self.prompt = prompt
        self.options = []
        self.selections = []
        self.content = None # view to show when THIS frame is visible
        self.options_listbox = None # view to show when THIS frame is visible
        self.selected_listbox = None # view to show when THIS frame is visible
        self.entry = None # entry field to filter selections

    def rebuild(self):
        if self.content:
            self.content.destroy()
        if self.entry:
            self.entry.destroy()
        self.content = Frame(self.parent, bg='red') 
        self.content.pack(fill=BOTH, expand=1)

    def show(self):
        self.old_content.pack_forget()
        if type(self.get_options) == list:
            self.options = self.get_options
        else:
            self.options = self.get_options()
        self.__list_options()

    def hide(self):
        self.parent.showing = None
        self.content.pack_forget()
        self.old_content.pack(fill=BOTH)

    def list_selection(self, event):
        try:
            listbox_index = str(event.widget.curselection()[0])
            context_str = self.options_listbox.get(listbox_index)
            context_index = self.options.index(context_str)
        except IndexError as e:
            pass

    def clear_entry(self):
        if self.entry:
            self.entry.delete(0, END)
        if self.options_listbox or self.selection_listbox:
            self.options_listbox.selection_clear(0, END)
            self.selection_listbox.selection_clear(0, END)
            self.__write_list(self.options, self.options_listbox)
            self.__write_list(self.selections, self.selection_listbox)

    def filter_listbox(self, event):
        filter_value = self.entry.get()
        a = [i for i in self.options if filter_value.lower() in i.lower()]
        self.__write_list(a, self.options_listbox)

    def __write_list(self, options, lb):
        lb.delete(0, END)
        for i in sorted(options):
            lb.insert(END, i)

    def switch(self, event):
        try:
            w = event.widget
            index = w.curselection()[0]
            print(index)
            value = w.get(index)
            if w == self.options_listbox:
                self.selections.append(value)
                self.options.remove(value)
            else:
                self.options.append(value)
                self.selections.remove(value)
            self.clear_entry()
        except IndexError:
            pass
        except ValueError:
            pass

    def load_values(self):
        try:
            job = self.master.job
        except Exception as e:
            print(e)
            job = None
            pass

        if job:
            values = []
            for v in values:
                try:
                    self.options.remove(v)
                except ValueError:
                    pass
            #if values != Util.DEFAULT_PROMPT:
             #   self.selections = values

    def submit(self):
        self.hide()
        if self.callback:
            self.callback(self.column, self.selections)

    def __list_options(self):
        self.rebuild()

        top_pane = Frame(self.content)

        if self.prompt:
            Label(top_pane, text=self.prompt).pack(fill=X, pady=10, padx=10)

        left_pane = Frame(self.content)
        left_scollbar = Scrollbar(left_pane)
        left_scollbar.pack(side=RIGHT, fill=Y)
        
        self.options_listbox = Listbox(left_pane)
        self.options_listbox.bind('<<ListboxSelect>>', self.list_selection)
        self.options_listbox.bind('<Double-Button-1>', lambda e:self.switch(e))
        self.options_listbox.pack(fill=BOTH, expand=1)

        self.options_listbox.config(yscrollcommand=left_scollbar.set)
        left_scollbar.config(command=self.options_listbox.yview)


        right_pane = Frame(self.content)
        right_scollbar = Scrollbar(right_pane)
        right_scollbar.pack(side=RIGHT, fill=Y)
        
        self.selection_listbox = Listbox(right_pane)
        self.selection_listbox.bind('<<ListboxSelect>>', self.list_selection)
        self.selection_listbox.bind('<Double-Button-1>', lambda e:self.switch(e))
        self.selection_listbox.pack(fill=BOTH, expand=1)

        self.selection_listbox.config(yscrollcommand=right_scollbar.set)
        right_scollbar.config(command=self.selection_listbox.yview)


        bottom_pane = Frame(self.content)

        self.load_values()
        self.__write_list(self.options, self.options_listbox)
        self.__write_list(self.selections, self.selection_listbox)
        sv = StringVar()

        sv.trace("w", lambda name, index, mode, sv=sv:self.filter_listbox(sv))
        self.entry = Entry(bottom_pane, textvariable=sv)
        self.entry.pack(fill=X)

        buttons = Frame(bottom_pane)
        buttons.pack()
        back = Button(buttons, text='Back', command=self.hide)
        back.pack(fill=X, side=LEFT, padx=10, pady=10)
        clear = Button(buttons, text='Clear', command=self.clear_entry)
        clear.pack(fill=X, side=LEFT, padx=10, pady=10)
        submit = Button(buttons, text='Submit', command=lambda:self.submit())
        submit.pack(fill=X, side=LEFT, padx=10, pady=10)

        top_pane.grid(row=0, columnspan=2, sticky="nsew")
        left_pane.grid(row=1, column=0, sticky="nsew")
        right_pane.grid(row=1, column=1, sticky="nsew")
        bottom_pane.grid(row=2, columnspan=2, sticky="nsew")

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(1, weight=1)
