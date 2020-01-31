from Tkinter import *
from collections import OrderedDict
from util import Util as Util
import os

class Summary(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.parent = master
        self.content = None
        self.actions = {}
        self.__show_actions()
        self.selected_listbox = None

    def rebuild(self):
        if self.content:
            self.content.destroy()
        self.content = Frame(self) 
        self.content.pack(fill=BOTH, expand=1)

    def show_actions(self):
        if self.parent.config and 'work' in self.parent.config:
            work = self.parent.config['work']
            for k, v in work.items():
                lb = self.actions[k]['list']
                lb.delete(0, END)
                for i in v:
                    s = Util.ACTION_FORMAT[k] % (i['name'], os.path.splitext(os.path.basename(i['compare_file']))[0])
                    lb.insert(END, s)

    def single_selection(self, event):
        for k, v in self.actions.items():
            lb = v['list']
            if lb != event.widget:
                lb.selection_clear(0, END)
            else:
                self.selected_listbox = lb

    def get_selected_lb(self):
        for k, v in self.actions.items():
            lb = v['list']
            if self.selected_listbox and lb == self.selected_listbox:
                return (k, lb)

    def edit(self):
        if self.selected_listbox:
           action, lb = self.get_selected_lb() 
           try:
                return (action, lb.curselection()[0])
           except IndexError:
               return None
           except TypeError:
               return None

    def remove(self):
        if self.selected_listbox:
           try:
               action, lb = self.get_selected_lb()
               index = lb.curselection()[0]
               del  self.parent.config['work'][action][index]
               return True
           except:
                return False
        else:
            return False

    def add(self, event):
        for k, v in self.actions.items():
            button = v['button']
            if button == event:
                self.parent.add(k)
                break

    def __show_actions(self):

        self.rebuild()
        for action in Util.ACTIONS:
            button = Button(self.content, text='Add %s' % action.title())
            button.configure(command=lambda button=button: self.add(button))
            button.pack(fill=X, expand=1, padx=10)

            f = Frame(self.content)
            scrollbar = Scrollbar(f)
            scrollbar.pack(side=RIGHT, fill=Y)

            lb = Listbox(f)
            lb.bind('<<ListboxSelect>>', lambda e: self.single_selection(e))
            lb.bind('<Double-Button-1>', lambda e: self.parent.edit())
            lb.pack(fill=X, expand=1)

            f.pack(fill=X)
            lb.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=lb.yview)

            self.actions[action] = {}
            self.actions[action]['button'] = button
            self.actions[action]['list'] = lb
