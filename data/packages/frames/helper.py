from Tkinter import *
from data.packages.frames.util import Util as Util

class Helper(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.parent = master
        self.image = None
        self.showing = {}
 
    def show(self, command):
        if command in self.showing:
            return

        win = Toplevel()
        win.wm_title("%s Help" % command.title())
        self.showing[command] = win

        self.image = PhotoImage(file = Util.get_resource('%s.gif' % command))

        image = Label(win, image = self.image)
        image.pack()

        text = Util.get_help_text(command)

        label = Label(win, text=text)
        label.pack(fill=X) 
    
        b = Button(win, text="Close", command=lambda :self.close(win))
        b.pack()

    def close(self, win):

        for k, i in self.showing.items():
            if i == win:
                del self.showing[k]
        
        win.destroy()
