from Tkinter import *
from util import Util
import os

class Job:
    def __init__(self, master, action):
        self.parent = master
        self.action = action
        self.operation = Util.JOBS[action]
        self.instruction = -1
        self.done = None
        self.edit_index = None
        self.caller = None
        self.DEFAULT = 'Click Here'
        self.workers = {
            'source_tab':{'cmd':lambda e: self.parent.get_sheet(e, 0)}, 
            'source_col':{'cmd':lambda e: self.parent.get_column(e, 0)}, 
            'compare_file':{'cmd':lambda e: self.get_file(e, Util.INPUT_ROOT, Util.INPUT_EXT, self.validate)},
            'compare_tab':{'cmd':lambda e: self.parent.get_sheet(e, 1)},
            'compare_col':{'cmd':lambda e: self.parent.get_column(e, 1)},
            'name':{'cmd':lambda e: self.parent.get_name(e)},
            'filters':{'cmd':lambda e: self.parent.get_filter(e, 'filters')},
            'add_col':{'cmd':lambda e: self.parent.fill_cols(e, 'add_col')}
        }

        self.key_button = {}
        self.display_names = {}

    def get_value(self, key):
        if key in self.display_names:
            return self.display_names[key]
        
        if key == 'source_file':
            return self.parent.parent.config['source_file']
        else:
            b = self.key_button[key]
            if b['text'] in self.display_names:
                return self.display_names[b['text']]
            else:
                return b['text']

    def set_value(self, key, value):
        if type(value) != list and '//' or '\\' in value:
            fl, __ = os.path.splitext(os.path.basename(value))
            self.display_names[fl] = value
            self.key_button[key]['text'] = fl
        elif type(value) == list:
            self.display_names[key] = value
            self.key_button[key]['text'] = str(len(value))
        else:
            self.key_button[key]['text'] = value
    
    def validate(self, *values):
        if values:
            for k, v in self.key_button.items():
                if v == self.caller:
                    order = k
                    break
            else:
                return
            working_index = self.get_instruction_index(order)
            self.clear_future(working_index)

            try:
                if len(values[0]) == 2:
                    index, options = values[0]
                    selected = options[index]
                else:
                    selected = values[0]

                self.set_value(order, selected)
                current_order = self.get_current_instruction() 
                if order == current_order:
                    self.next()
            except Exception as e:
                print('no next step', e)

    def check(self):
        pass

    def clear_future(self, index):
        orders = Util.JOBS[self.action]['order']
        if len(orders) > index+1:
            remove = orders[index+1:]
            for key in remove:
                button = self.key_button[key] if key in self.key_button else None
                if button:
                    button.master.destroy()
                    del self.key_button[key]
            self.instruction = index

    def disable_submit(self):
        if self.done:
            self.done['state'] = 'disabled'

    def enable_submit(self):
        if self.done:
            self.done['state'] = 'normal'

    def edit(self, index, config):
        self.edit_index = index
        orders = Util.JOBS[self.action]['order']
        for i in orders:
            self.next()
        work = config['work'][self.action][index]
        for k, v in self.key_button.items():
            self.set_value(k, work[k])
        self.next()

    def complete_job(self):
        item = {}
        for key, button in self.key_button.items():
            val = self.get_value(key)
            if val == self.DEFAULT:
                item[key] = ''
            else:
                item[key] = val
                
        if self.edit_index is not None:
            self.parent.parent.config['work'][self.action][self.edit_index] = item
        else:
            self.parent.parent.config['work'][self.action].append(item)

    def get_current_instruction(self):
        orders = Util.JOBS[self.action]['order']
        return orders[self.instruction]

    def get_instruction_index(self, key):
        orders = Util.JOBS[self.action]['order']
        return orders.index(key)

    def get_file(self, caller, path, ext, callback):
        self.caller = caller
        self.parent.get_file(path, ext, callback)

    def get_completed_count(self):
        count = 0
        for k, v in self.key_button.items():
            if v['text'] and v['text'].strip() and v['text'] != self.DEFAULT:
                count += 1
                v.master['bg'] = Util.COMPLETED_COLOR
            else:
                if k not in Util.JOBS[self.action]['optional']:
                    v.master['bg'] = Util.REQUIRED_COLOR
                
        count += len(Util.JOBS[self.action]['optional'])
        return count

    def check_done(self):
        order_count = len(Util.JOBS[self.action]['order'])

        count = self.get_completed_count()
        if order_count <= count:
            self.enable_submit()
            return True
        else:
            self.disable_submit()
            return False

    def next(self):
        orders = self.operation['order']
        self.instruction += 1
        try:
            current_order = orders[self.instruction]
        except:
            current_order = None

        if current_order:
            color = Util.OPTIONAL_COLOR if current_order and current_order in Util.JOBS[self.action]['optional'] else Util.REQUIRED_COLOR
            f = Frame(self.parent.wizard, bg=color)
            f.pack(fill=X)
            label_text = ' '.join([i.title() for i in current_order.split('_')])
            Label(f, text=label_text).pack(side=LEFT, pady=10, padx=5)
            button = Button(f, justify=LEFT, text=self.DEFAULT)
            button.configure(command=lambda: self.workers[current_order]['cmd'](button))
            button.pack(fill=X, side=LEFT, expand=1, pady=10)
            self.key_button[current_order] = button

        next_order = orders[self.instruction + 1] if self.instruction + 1 < len(orders) else None
        if next_order:
            if next_order in Util.JOBS[self.action]['optional']:
                self.next()
        self.check_done()



