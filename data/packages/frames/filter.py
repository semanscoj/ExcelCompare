from Tkinter import *
from collections import OrderedDict
from glob import glob
import os
from data.packages.frames.picker import Picker
from data.packages.frames.util import Util as Util
from data.packages.frames.button_options import Button_options
from data.packages.frames.split import Split
from itertools import groupby

class Filter(Frame):
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
        filters = self.job.get_value('filters')

        if filters == Util.DEFAULT_PROMPT:
            filters = []
        
        self.background_color = {}
        print 'set_options', filters
        if filters and len(filters):
            opt = []
            for index, i in enumerate(filters):
                col = i["filter_col"] if 'filter_col' in i else None
                val = i["filter_value"] if 'filter_value' in i else None
                fn = i['filter_file'] if 'filter_file' in i else None

                if fn:
                    if 'grey' in self.background_color:
                        self.background_color['grey'].append(index)
                    else:
                        self.background_color['grey'] = [index]
                
                ln = "%s:%s" % (col, val if val else fn)
                opt.append(ln)

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

    def __unique_filters(self, old, new):
        old = old if old and old != Util.DEFAULT_PROMPT else []
        new = new if new and new != Util.DEFAULT_PROMPT else []
 
        old += new
        old.sort(key=lambda x:x['filter_col'])

        return_filters = []

        for k, v in groupby(old, key=lambda x:x['filter_col']):
            content = list(v)
            values = sorted(set([str(i['filter_value']) for i in content]))
            files = sorted(set([str(i['filter_file']) for i in content]))

            for val in values:
                if val:
                    return_filters.append({"filter_col":k,"filter_value":val,"filter_file":""})

            for fn in files:
                if fn:
                    return_filters.append({"filter_col":k,"filter_value":"","filter_file":fn})
                    
        return return_filters

    def add_file_callback(self, col, values):
        old_filters = self.job.get_value('filters')
        new_filters = [{"filter_col":str(col), "filter_value":"", "filter_file":str(i)} for i in values]

        added = self.__unique_filters(old_filters, new_filters)        
        
        self.job.set_value("filters", added)
        self.set_options()
        self.__list_options()

    def add_callback(self, col, values):
        old_filters = self.job.get_value('filters')
        new_filters = [{"filter_col":str(col), "filter_value":str(i), "filter_file":""} for i in values]

        added = self.__unique_filters(old_filters, new_filters)        
        
        self.job.set_value("filters", added)
        self.set_options()
        self.__list_options()
            
    def select_file(self, col):
        self.show()
        key = 'filters'
        prompt = 'Please select a that contains the desired filters.'
        Split(key, column=col, get_options=lambda: Util.get_file_list(Util.FILTER_ROOT, Util.FILTER_EXT), return_callback=self.add_file_callback, return_view=self.content, master=self.parent, prompt=prompt).show()

    def select_values(self, col):
        self.show()
        key = 'filters'
        path = 'source_file'
        sheet = 'source_tab'
        prompt = 'Please double click values to move them. \nThe values in the right column are selected and will be used in filtering.'
        Split(key, column=col, get_options=lambda: Util.get_values(self.job, path, sheet, col), return_callback=self.add_callback, return_view=self.content, master=self.parent, prompt=prompt).show()

    def remove(self):
        try:
            val = self.listbox.get(self.listbox.curselection()[0])
            filters = self.job.get_value('filters')

            for index, i in enumerate(filters):
                if val in self.display_keys:
                    val = self.display_keys[val]
   
                test = "%s:%s" % (i['filter_col'], i['filter_value'])
                test2 = "%s:%s" % (i['filter_col'], i['filter_file'])

                if val == test or val == test2:
                    del filters[index]
                    break

            self.job.set_value("filters", filters)
            self.set_options()
            self.__list_options()
        except Exception as e:
            print('ERROR', e)
            pass
        
    def add(self, tup):
        index, options = tup
        col = options[index]
        options = {"prompt":"Add a filter from column %s" % col, "buttons":
           [
               {"text":"Select Filters", "command":lambda col=col: self.select_values(col)},
               {"text":"Select File", "command":lambda col=col: self.select_file(col)},
               {"text":"Back", "command":lambda col=col: self.show()}
            ]
        }
        self.rebuild()
        b = Button_options(setup=options, return_view=self.content, master=self.parent)
        b.show()

    def __list_options(self):
        self.rebuild()
        scrollbar = Scrollbar(self.content)
        scrollbar.pack(side=RIGHT, fill=Y)

        prompt = "List of filters to be applied.\nFORMAT (Column Name:Column Value).\nFilter files have a grey background."
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
        prompt = 'Choose a column to filter on.\nClick a column and then click submit to make a selection. \nYou can double click a row to submit.'
        p = Picker(get_options=lambda: Util.get_column_names(self.job, 0), return_callback=self.add, return_view=self.content, master=self.parent, prompt=prompt)
        add = Button(buttons, text='Add', command=p.show)
        add.pack(fill=X, side=LEFT, padx=10, pady=10)

        
