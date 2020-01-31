from Tkinter import *
from collections import OrderedDict
from glob import glob
import os
from data.packages.frames.picker import Picker
from data.packages.frames.util import Util as Util
from data.packages.frames.button_options import Button_options
from data.packages.frames.split import Split
from itertools import groupby

class Selection(Frame):
    def __init__(self, job=None, return_view=None, master=None):
        Frame.__init__(self, master)
        self.job = job
        self.parent = master
        self.get_options = []
        self.old_content = return_view # view to restore when THIS frame is hidden
        self.options = []
        self.content = None # view to show when THIS frame is visible
        self.listbox = None # list box to show selections
        self.entry = None # entry field to filter selections
        self.option_paths = None
        self.display_keys = {}
        self.background_color = {}

    def rebuild(self):
        if self.content:
            self.content.destroy()
        if self.entry:
            self.entry.destroy()
        self.content = Frame(self.master) 
        self.content.pack(fill=BOTH, expand=1)

    def set_color(self):
        try:
            for i, listbox_entry in enumerate(self.listbox.get(0, END)):
                self.listbox.itemconfig(i, bg='white')

            print self.background_color
            for k, v in self.background_color.items():
                for value in v:
                    try:
                        print v, k
                        self.listbox.itemconfig(value, bg=k)
                    except:
                        pass
        except Exception as e:
            print e

    def set_options(self):
        add_col = self.job.get_value('add_col')

        if add_col == Util.DEFAULT_PROMPT:
            add_col = []
        
        self.background_color = {}
        if add_col and len(add_col):
            opt = []
            for index, i in enumerate(add_col):
                opt.append(i)

            self.options = opt
        else:
            self.options = []

    def show(self):
        self.old_content.pack_forget()
        self.set_options()
        self.__list_options()

    def hide(self):
        self.parent.showing = None
        self.content.pack_forget()
        self.old_content.pack(fill=X)

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
                    key = None
                    if ':' in i:
                        key, value = i.split(':')
                    else:
                        value = i
                    
                    root = os.path.dirname(value)
                    fl, ext = os.path.splitext(os.path.basename(value))
                    if not self.option_paths: 
                        self.option_paths = {'root':root, 'ext':ext}
                    display_name = "%s:%s" % (key, fl) if key else fl
                    self.display_keys[display_name] = i
                    write_options.append(display_name)
            else:
                write_options = options

            self.listbox.delete(0, END)
            for i in write_options:
                self.listbox.insert(END, i)
            self.set_color()

    def remove(self):
        try:
            val = self.listbox.get(self.listbox.curselection()[0])
            add_col = self.job.get_value('add_col')

            for index, i in enumerate(add_col):
                if val in self.display_keys:
                    val = self.display_keys[val]
  
                if val == i:
                    del add_col[index]
                    break

            self.job.set_value("add_col", add_col)
            self.set_options()
            self.__list_options()
        except Exception as e:
            print('ERROR', e)
            pass
        
    def add(self):
        key = 'add_col'
        print 'showing split'
        Split(key, get_options=lambda: Util.get_column_names(self.job, key), return_callback=self.__add, return_view=self.content, master=self.parent).show()


    def __add(self, key, values):
        if self.job:
            old = self.job.get_value('add_col')
            old += values
            options = list(set(old))
            options.sort()
            
            self.job.set_value('add_col', options)
            self.job.validate()
            self.show()

    def __list_options(self):
        self.rebuild()
        scrollbar = Scrollbar(self.content)
        scrollbar.pack(side=RIGHT, fill=Y)

        prompt = "List of columns to add to output file."
        Label(self.content, text=prompt).pack(fill=X, padx=10, pady=10)
        
        self.listbox = Listbox(self.content)
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
        back = Button(buttons, text='Done', command=self.hide)
        back.pack(fill=X, side=LEFT, padx=10, pady=10)
        clear = Button(buttons, text='Clear', command=self.clear_entry)
        clear.pack(fill=X, side=LEFT, padx=10, pady=10)
        delete = Button(buttons, text='Remove', command=self.remove)
        delete.pack(fill=X, side=LEFT, padx=10, pady=10)
        prompt = 'Choose columns to include in the output file.\nDouble Click a column and then click submit to complete the selection.'
        add = Button(buttons, text='Add', command=self.add)
        add.pack(fill=X, side=LEFT, padx=10, pady=10)

        
