from Tkinter import *
from gui import Gui
from console import run as console
from data.packages.frames.util import Util as Util
import os, argparse
from os import path

parser = argparse.ArgumentParser()
parser.add_argument('-config_file', dest='config_file', action="store", default=None, type=str, help='File to run, no configuration prompts.')
parser.add_argument('-console', dest='console', action="store_true", help='Use commandline only for task setup. If omitted, GUI is presented')
parser.add_argument('-open_file', dest='open_file', action="store_false", help='Open document after tasks complete, defaults to NOT opening the file.')

args = parser.parse_args()
config_file = args.config_file
no_interface = args.console
open_file = args.open_file

root = Tk()
Util.ROOT = root

root.minsize(800, 600)
root.title("Excel File Compare")

if not config_file:
    if no_interface:
        console()
    else:
        interface = Gui(master=root)
        try:
            interface.mainloop()
        except:
            interface.destroy()
else:
    interface = Gui(master=root)
    print "Loading config %s"% config_file
    if config_file:
        path = os.path.join(Util.CONFIG_ROOT, config_file)
        if os.path.exists(path):
            print "Running config %s"% config_file
            interface.load_config((0, [path]))
            a = interface.run(open_file=open_file)
            print a
    else:
        print "File %s not found" % file_path        
