from Tkinter import *
import data.packages.frames.display as display
import data.packages.frames.ribbon as ribbon
import data.packages.frames.summary as summary
import data.packages.frames.helper as helper
from data.packages.frames.util import Util as Util
import os, json, time
import tkMessageBox
import data.packages.modules.compare as compare
import data.packages.modules.union as union
import data.packages.modules.fill as fill
import data.packages.modules.report as report

class Gui(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master, bg='grey')
        self.parent = master
        self.display = None
        self.summary = None
        self.config = None
        self.helper = None
        self.parent.protocol("WM_DELETE_WINDOW", self.exit)
        self.menu_bar()
        self.home()

    def home(self):
        self.pack_forget()
        self.pack(expand=1, fill=BOTH)
        self.ribbon = ribbon.Ribbon(master=self)
        self.ribbon.grid(row=0, columnspan=2, sticky="nsew")
        self.summary = summary.Summary(master=self)
        self.summary.grid(row=1, column=0, sticky="nsew")
        self.display = display.Display(master=self)
        self.display.grid(row=1, column=1, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def run(self, open_file=True):
        path = self.config['path']
        output_file = os.path.basename(path)
        out_file_time = time.strftime("%Y%m%d-%H%M%S")
        output_folder = 'output'
        f_name, f_ext = os.path.splitext(output_file)
        stamped_file = "%s-%s%s" % (f_name[:30 - (len(out_file_time) + 5)], out_file_time, '.xlsx')
        out_path = os.path.join(output_folder, stamped_file)

        try:
            os.mkdir(output_folder)
        except:
            pass
   
        report.do_work(path, out_path)
        compare.do_work(path, out_path)
        union.do_work(path, out_path)
        fill.do_work(path, out_path)

        if open_file:
            try:
                os.startfile(out_path, 'open')
            except Exception as e:
                print(e)
                pass

        return out_path

    def action_in_progress(self):
        if self.display:
            return self.display.job
        else:
            return true

    def add(self, action):
        if self.config and self.summary:
            self.display.new_job(action)
        else:
            print('no config loaded')

    def remove(self):
        if self.action_in_progress():
            tkMessageBox.showinfo("Help", "Action in progress. Please complete that action first.")
            return
        
        if self.config and self.summary:
            if self.summary.remove():
                self.save_config()
            else:
                tkMessageBox.showinfo("Help", "Please select an action to remove.")
        else:
            tkMessageBox.showinfo("Help", "Please load a file to edit.")

    def edit(self):
        if self.action_in_progress():
            tkMessageBox.showinfo("Help", "Action in progress. Please complete that action first.")
            return
        
        if self.config and self.summary and self.display:
            try:
                action, index = self.summary.edit()
            except TypeError:
                tkMessageBox.showinfo("Help", "Please select an action to edit.")
                return
            self.display.edit_job(action, index)
        else:
            tkMessageBox.showinfo("Help", "Please load a file to edit.")

    def save_config(self):
        if self.config:
            full_path = self.config['path']
            with open(full_path, 'w') as f:
                f.write(json.dumps(self.config))
            self.summary.show_actions()

    def load_config(self, config=None):
        Util.check_masters()
        if self.display and self.display.job:
            tkMessageBox.showinfo("Warning", "Please submit or cancel the current task before changing files.")
            return
        if config and len(config) == 2:
            index, options = config
            name = options[index]
            full_path = options[index]
            try:
                with open(full_path, 'r') as f:
                    self.config = json.loads(f.read())
                    self.config['path'] = full_path
                self.ribbon.update_file_label(name)
                self.summary.show_actions()
            except Exception as e:
                print(e)
        else:
            if self.display:
                self.display.get_file(Util.CONFIG_ROOT, Util.CONFIG_EXT, self.load_config)

    def menu_bar(self):
        menubar = Menu(self.parent)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label='Open', command=self.load_config)
        filemenu.add_command(label='Exit', command=self.exit)
        menubar.add_cascade(label='File', menu=filemenu)

        helpmenu = Menu(menubar, tearoff=0)

        self.helper = helper.Helper(master=self)
        
        helpmenu.add_command(label='with Reduce', command=lambda:self.helper.show('reduce'))
        helpmenu.add_command(label='with Union', command=lambda:self.helper.show('union'))
        helpmenu.add_command(label='with Fill', command=lambda:self.helper.show('fill'))
        menubar.add_cascade(label='Help', menu=helpmenu)

        self.parent.config(menu=menubar)

    def exit(self):
        self.parent.destroy()
