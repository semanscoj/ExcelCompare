from Tkinter import *
from collections import OrderedDict
from glob import glob
import os

class Picker(Frame):
    def __init__(self, get_options=None, return_view=None, return_callback=None, master=None, prompt=None):
        Frame.__init__(self, master)
        self.parent = master
        self.get_options = get_options
        self.old_content = return_view # view to restore when THIS frame is hidden
        self.callback = return_callback # data to pass value back on on submit
        self.prompt = prompt
        self.options = []
        self.content = None # view to show when THIS frame is visible
        self.listbox = None # list box to show selections
        self.entry = None # entry field to filter selections
        self.option_paths = None

    def rebuild(self):
        if self.content:
            self.content.destroy()
        if self.entry:
            self.entry.destroy()
        self.content = Frame(self.master) 
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
        if self.old_content:
            try:
                self.old_content.pack(fill=X)
            except TclError as e:
                print e

    def list_selection(self, event):
        try:
            listbox_index = str(event.widget.curselection()[0])
            context_str = self.listbox.get(listbox_index)
            if self.option_paths:
                context_str = os.path.join(self.option_paths['root'], context_str + self.option_paths['ext'])
            context_index = self.options.index(context_str)
        except IndexError as e:
            pass

    def clear_entry(self):
        if self.entry:
            self.entry.delete(0, END)
        if self.listbox:
            self.listbox.selection_clear(0, END)
            self.__write_list(self.options)

    def filter_listbox(self, event):
        filter_value = self.entry.get()
        a = [i for i in self.options if filter_value.lower() in i.lower()]
        self.__write_list(a)

    def __write_list(self, options):
        if len(options):
            write_options = []
            if '//' or '\\' in options[0]:
                for i in options:
                    root = os.path.dirname(i)
                    fl, ext = os.path.splitext(os.path.basename(i))
                    if not self.option_paths: 
                        self.option_paths = {'root':root, 'ext':ext}
                    write_options.append(fl)
            else:
                write_options = options

            self.listbox.delete(0, END)
            for i in write_options:
                self.listbox.insert(END, i)

    def submit(self):
        try:
            listbox_index = str(self.listbox.curselection()[0])
            context_str = self.listbox.get(listbox_index)
            if self.option_paths:
                context_str = os.path.join(self.option_paths['root'], context_str + self.option_paths['ext'])
            
            context_index = self.options.index(context_str)
            if self.callback:
                self.callback((context_index, self.options))
            else:
                print(context_str, context_index)
            self.hide()
        except IndexError as e:
            pass

    def __list_options(self):
        self.rebuild()
        scrollbar = Scrollbar(self.content)
        scrollbar.pack(side=RIGHT, fill=Y)

        if self.prompt:
            Label(self.content, text=self.prompt).pack(fill=X, pady=10, padx=10)
        
        self.listbox = Listbox(self.content)
        self.listbox.bind('<<ListboxSelect>>', self.list_selection)
        self.listbox.bind('<Double-Button-1>', lambda e:self.submit())
        self.listbox.pack(fill=BOTH, expand=1)

        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        self.__write_list(self.options)
        sv = StringVar()

        sv.trace("w", lambda name, index, mode, sv=sv:self.filter_listbox(sv))
        self.entry = Entry(self.content, textvariable=sv)
        self.entry.pack(fill=X)

        buttons = Frame(self.content)
        buttons.pack()
        back = Button(buttons, text='Back', command=self.hide)
        back.pack(fill=X, side=LEFT, padx=10, pady=10)
        clear = Button(buttons, text='Clear', command=self.clear_entry)
        clear.pack(fill=X, side=LEFT, padx=10, pady=10)
        submit = Button(buttons, text='Submit', command=lambda:self.submit())
        submit.pack(fill=X, side=LEFT, padx=10, pady=10)


