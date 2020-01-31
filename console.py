import pandas as pd
from openpyxl import load_workbook
from shutil import copyfile
import glob, os, xlrd, json, time, re, logging
import data.packages.modules.compare as compare
import data.packages.modules.union as union
import data.packages.modules.fill as fill
import data.packages.modules.report as report
from data.packages.frames.util import Util as Util

class CancelRequest(Exception):
    pass

def clear():
    if True:
        try:
            if os.name == 'nt':
                os.system('cls')
            else:
                os.system('clear')
        except:
            log('clear', str(e))
            pass

def get_file(prompt, root, extension):
    files = sorted([i for i in glob.glob(os.path.join(root,"*.%s" % extension)) if '$' not in i])
    if len(files) == 0:
        raise OSError
    try:
        return pick_index(prompt, files)
    except CancelRequest as e: raise e
    except Exception as e:
        log('get_file', str(e))
        raise e

def get_sheet_name(prompt, sheets):
    try:
        return pick_index(prompt, sheets)
    except Exception as e:
        log('get_sheet_name', str(e))
        raise e

def get_column_name(prompt, source_file, source_tab, df=None, zero_name=None):
    if not df:
        df = pd.read_excel(source_file, source_tab)
    try:
        return pick_index(prompt, sorted([str(i) for i in df.keys()]), zero_name=zero_name)
    except Exception as e:
        log('get_column_name', str(get_column_name))
        raise e

def get_filter(source_file, source_tab):
    filter_setup = {}
    df = pd.read_excel(source_file, source_tab)
        
    options = ['Single Filter', 'Filter File']
    choice = pick_index('What type of filter? ', options)
    col = get_column_name("What column in the master file has the field to filter with? ", source_file, source_tab)
    filter_setup['filter_col'] = col
    
    if choice == options[0]:
        all_filters = sorted(set([str(i) for i in df[filter_setup['filter_col']] if i]))
        try:
            filter_setup['filter_value'] = pick_index('Choose a field to filter %s by: ' % col, all_filters)
        except Exception as e:
            log('get_filter', str(e))
    else:
        try:
            filter_setup['filter_file'] = get_file('Please choose a filter file to use: ', 'filters', 'filter')
        except OSError as e:
            log('get_filter, os error', str(e))
    return filter_setup

def pick_index(prompt, options, top=None, can_cancel=True, do_clear=True, zero_name=None): 
    if not top:
        top = options
    page_size = 20
    
    while True:
        # clear the screen to only view page_size options and prompt
        if do_clear:
            clear()
        # Inform the user how to cancel the selection
        if can_cancel:
            if not zero_name:
                print('0.  Cancel Selection')
            else:
                print(zero_name)
        # look at the next 20 entries with number
        for index, option in enumerate(options[:page_size]):
            if '/' or '\\' in option:
                option, _ = os.path.splitext(os.path.basename(option))
            # print the option with number to choose. offset row to account for choice length
            print("%s. %s" % (index + 1, option[:75] if index + 1 > 9 else ' ' + str(option[:75])))
        try:
            # get the input, and cast seperately, that way the choice is still recorded if an exception is thrown
            choice = raw_input(prompt)
            choice = int(choice)
            # Cancel this selection and notify the caller
            if choice == 0:
                if can_cancel:
                    raise CancelRequest
            # Prevent out of range integer entries
            elif choice < 0 or choice > len(top):
                continue
            # We have a valid index to get from the array
            break
        # Cancel out of selection
        except CancelRequest as e: raise e
        # cast to int will raise exception, treat entry as a filter instead
        except ValueError:
            # Empty input will page ahead by page_size
            if top and len(choice) == 0:
                # Get the last index displayed to the user
                next_start = top.index(options[-1]) + 1
                # Prevent index out of bounds from paginating ahead
                if next_start + page_size > len(top):
                    start = len(top) - page_size
                    # save last_start so we know if we are at the end
                    last_start = next_start
                    next_start = start if start >= 0 else 0
                    # if we already showed the end, wrap to top
                    if next_start + page_size == last_start:
                        next_start = 0
                choice = top[ next_start ]

            # Recursively show filtered list to user
            for x, i in enumerate(top if top else options):
                file_i = None
                if '/' or '\\' in i:
                    file_i, _ = os.path.splitext(os.path.basename(i))
                if (choice and re.match(choice, i, re.IGNORECASE)) or (file_i and choice and re.match(choice, file_i, re.IGNORECASE)) or choice == i:
                    return pick_index(prompt, top[x:x+page_size] if top and len(top) else options[x:x+page_size], top=top if top else options)
            else:
                # no match for filter found
                return pick_index(prompt, top[:page_size] if top else options[:page_size], top=top if top else options)
        except Exception as e:
            log("pick index", e)
            raise CancelRequest
    return options[choice - 1]
    
def configure_master(config):
    try:
        source_file = get_file('What is the master record: ', 'input', 'xlsx')
        config['source_file'] = source_file
    except CancelRequest as e: raise e
    except Exception as e:
        log('configure_master', str(e))

def add_filters(source_file, source_tab):
    filters = []
    try:
        filter_choice = get_filter(source_file, source_tab)
        filters.append(filter_choice)
    except CancelRequest:
        pass

    return filters

def summary(config):
    clear()
    center = '-' * 35
    print('%sSummary%s\nOn file: %s'  % (center, center, os.path.splitext(os.path.basename(config['source_file']))[0][:60]))
    print('\nReduce Actions\n%s' % ('-' * 75))
    list_compares(config, '', 'display')
    print('\nUnion Actions\n%s' % ('-' * 75))
    list_unions(config, '', 'display')
    print('\nFill Actions\n%s' % ('-' * 75))
    list_fills(config, '', 'display')
    raw_input('\n\nPress enter to continue...')

def get_output_name(action, count, source_base, compare_base):
    default_item_length = 8
    default_a = os.path.splitext(source_base)[0][:default_item_length].replace('-', '_').replace(' ', '_')
    default_b = os.path.splitext(compare_base)[0][:default_item_length].replace('-', '_').replace(' ', '_')

    default = "%s%s_%s-%s" % (action, count, default_a.strip('-').strip('_'), default_b.strip('-').strip('_'))
    name = raw_input("\nEnter a name for output file sheet:\n Press enter for default of: (%s): " % default)
    if not name:
        name = default
    return name[:30]

def add_compare(config):
    try:
        ##
        source_temp = xlrd.open_workbook(config['source_file'], on_demand=True)
        source_base = os.path.basename(config['source_file'])
        source_tab = get_sheet_name("\nPlease choose a sheet from,\n(source: %s): " % source_base, source_temp.sheet_names())
        source_col = get_column_name("\nPlease choose a column from,\n(source: %s): " % source_base, config['source_file'], source_tab)
        source_temp.release_resources()
        ##
        compare_name = get_file('\nWhat is the compare file? ', 'input', 'xlsx')
        compare_base = os.path.basename(compare_name)
        compare_temp = xlrd.open_workbook(compare_name, on_demand=True)
        compare_tab = get_sheet_name("\nPlease choose a sheet from,\n(compare: %s): " % compare_base, compare_temp.sheet_names())
        compare_col = get_column_name('\nPlease choose a column from,\n(compare: %s): ' % compare_base, compare_name, compare_tab)
        compare_temp.release_resources()
        ##
        clear()

        if 'work' not in config:
            config['work'] = {}
        if 'reduce' not in config['work']:
            config['work']['reduce'] = []

        next_of_type = str(len(config['work']['reduce']) + 1)
        name = get_output_name('R', next_of_type, source_base, compare_base)

        filters = add_filters(config['source_file'], source_tab)

        try:
            d = {'filters': filters, 'source_tab': source_tab, 'source_col': source_col, 'compare_tab': compare_tab, 'compare_col': compare_col, 'compare_name': compare_name, 'name': name}
            config['work']['reduce'].append(d)
        except Exception as e:
            log('add_compare dictionary', str(e))
        save(config)
    except CancelRequest as e: raise e
    except Exception as e:
        log('add_compare', str(e))

def remove_compare(config, index):
    del config['work']['reduce'][index]
    save(config)
    raw_input("\nComparison Removed. Press enter to continue.")

def load_config(path = None):
    try:
        Util.check_masters()
    except Exception as e:
        log('check_masters', str(e))
        pass

    if not path:
        path = get_file("Select a master file: ", Util.CONFIG_ROOT, Util.CONFIG_EXT)

    config = None
    with open(path, 'r') as f:
        config = json.loads(f.read())
    config['path'] = path
    return config

def work_reduce(config):
    options = ['Add Compare', 'List/Edit', 'Reverse', 'Remove Compare']
    choice = pick_index('Please choose an option: ', options)
    try:
        if choice == options[0]:
            add_compare(config)
        elif choice == options[1]:
            list_compares(config, "\nEdit Compare? ", 'edit')
        elif choice == options[2]:
            list_compares(config, "\nExisting Compare to switch from? ", "switch")
        elif choice == options[3]:
            list_compares(config, "\nRemove Compare? ", 'remove')
    except Exception as e:
        print(e)

def work_union(config):
    options = ['Add Union', 'List/Edit', 'Reverse', 'Remove Union']
    choice = pick_index('Please choose an option: ', options)
    try:
        if choice == options[0]:
            add_union(config)
        elif choice == options[1]:
            list_unions(config, "\nEdit Union? ", 'edit')
        elif choice == options[2]:
            list_unions(config, "\nExisting Union to switch from? ", "switch")
        elif choice == options[3]:
            list_unions(config, "\nRemove Union? ", 'remove')
    except Exception as e:
        print(e)

def add_union(config):
    try:
        source_temp = xlrd.open_workbook(config['source_file'], on_demand=True)
        source_base = os.path.basename(config['source_file'])
        source_tab = get_sheet_name("\nPlease choose a sheet from,\n(source: %s): " % source_base, source_temp.sheet_names())
        source_col = get_column_name("\nPlease choose a column from,\n(source: %s): " % source_base, config['source_file'], source_tab)
        source_temp.release_resources()
        ##
        compare_name = get_file('\nWhat is the compare file? ', 'input', 'xlsx')
        compare_base = os.path.basename(compare_name)
        compare_temp = xlrd.open_workbook(compare_name, on_demand=True)
        compare_tab = get_sheet_name("\nPlease choose a sheet from,\n(compare: %s): " % compare_base, compare_temp.sheet_names())
        compare_col = get_column_name('\nPlease choose a column from,\n(compare: %s): ' % compare_base, compare_name, compare_tab)
        compare_temp.release_resources()
        ##


        if 'work' not in config:
            config['work'] = {}
        if 'union' not in config['work']:
            config['work']['union'] = []

        next_of_type = str(len(config['work']['union']) + 1)
        name = get_output_name('U', next_of_type, source_base, compare_base)

        try:
            d = {'source_tab': source_tab, 'source_col': source_col, 'compare_tab': compare_tab, 'compare_col': compare_col, 'compare_name': compare_name, 'name': name}
            config['work']['union'].append(d)
        except Exception as e:
            log('add_union dictionary', str(e))
        save(config)
    except CancelRequest as e: raise e
    except Exception as e:
        log('add_union', str(e))

def list_unions(config, prompt, action='list'):
    if 'work' not in config or 'union' not in config['work']:
        return
    
    try:
        format_str = "Name: %s Source: (%s, %s) Compare: (%s, %s)\n\tCompare File: (%s)"
        compares = [format_str % (i['name'], i['source_col'], i['source_tab'], i['compare_col'], i['compare_tab'], os.path.splitext(os.path.basename(i['compare_name']))[0][:60]) for i in config['work']['union']]
    except Exception as e:
        log('format_str list compares', str(e))

    if action == 'display':
        for i in compares:
            print(i)
        return
     
    index = compares.index(pick_index(prompt, compares))

    if action == 'remove':
        remove_union(config, index)
    elif action == 'switch':
        switch(config, index, 'union')

def reverse_name(name):
    if '-' in name and name.count('-') == 1:
        start, end = tokens = name.split('-')
        name = end + '-' + start
    else:
        name = 'reverse_' + name

    return name

def switch(config, index, action):
    try:
        old_action = config['work'][action][index]
        compare_file, ext = os.path.splitext(os.path.basename(old_action['compare_name']))

        compare_path = os.path.join('config', compare_file + '.json')
        with open(compare_path, 'r') as f:
            compare_json = json.loads(f.read())

        if 'work' not in compare_json:
                compare_json['work'] = {}
        if action not in compare_json['work']:
                compare_json['work'][action] = []

        name = reverse_name(old_action['name'])
            
        compare_name = config['source_file']
        d = {'source_tab': old_action['compare_tab'], 'source_col': old_action['compare_col'], 'compare_tab': old_action['source_tab'],
             'compare_col': old_action['source_col'], 'compare_name': compare_name, 'name': name}

        if action == 'reduce':
            raw_input('Press enter to configure filters, no filters can be copied over.')
            d['filters'] = add_filters(compare_json['source_file'], d['source_tab'])
            
        compare_json['work'][action].append(d)

        with open(compare_path, 'w') as f:
            f.write(json.dumps(compare_json))
            
        clear()
        raw_input('Added a %s, you should load and run file:\n(%s)\noutput tab will be: (%s)\n\nPress enter to continue...\n' % (action, compare_file, name))
    except Exception as e:
        log('switch_action', str(e))

def remove_union(config, index):
    del config['work']['union'][index]
    save(config)
    raw_input("\nUnion Removed. Press enter to continue.")

def list_compares(config, prompt, action='list'):
    if 'work' not in config or 'reduce' not in config['work']:
        return
    
    try:
        format_str = "Name: %s Source: (%s, %s) Compare: (%s, %s) Filters: (%s)\n\tCompare File: (%s)"
        compares = [format_str % (i['name'], i['source_col'], i['source_tab'], i['compare_col'], i['compare_tab'], len(i['filters']), os.path.splitext(os.path.basename(i['compare_name']))[0][:60]) for i in config['work']['reduce']]
    except Exception as e:
        log('format_str list compares', str(e))

    if action == 'display':
        for i in compares:
            print(i)
        return
    
    index = compares.index(pick_index(prompt, compares))

    if action == 'remove':
        remove_compare(config, index)
    elif action == 'switch':
        switch(config, index, 'reduce')
        

def add_fill(config):
    try:
        source_temp = xlrd.open_workbook(config['source_file'], on_demand=True)
        source_base = os.path.basename(config['source_file'])
        source_tab = get_sheet_name("\nPlease choose a sheet from,\n(source: %s): " % source_base, source_temp.sheet_names())
        source_col = get_column_name("\nPlease choose a lookup column from,\n(source: %s): " % source_base, config['source_file'], source_tab)

        add_columns = []

        while True:
            try:
                current_cols = ', '.join(add_columns)
                add_columns.append(get_column_name("Adding Columns:%s \nPlease choose a column to add to output from,\n(source: %s): " % (current_cols, source_base), config['source_file'], source_tab, zero_name="0.  Done"))
            except CancelRequest:
                break
            
        source_temp.release_resources()
        ##
        compare_name = get_file('\nWhat is the compare file? ', 'input', 'xlsx')
        compare_base = os.path.basename(compare_name)
        compare_temp = xlrd.open_workbook(compare_name, on_demand=True)
        compare_tab = get_sheet_name("\nPlease choose a sheet from,\n(compare: %s): " % compare_base, compare_temp.sheet_names())
        compare_col = get_column_name('\nPlease choose a lookup column from,\n(compare: %s): ' % compare_base, compare_name, compare_tab)
        compare_temp.release_resources()
        ##

        if 'work' not in config:
            config['work'] = {}
        if 'fill' not in config['work']:
            config['work']['fill'] = []

        next_of_type = str(len(config['work']['fill']) + 1)
        name = get_output_name('F', next_of_type, source_base, compare_base)

        try:
            d = {'add_col':add_columns, 'source_tab': source_tab, 'source_col': source_col, 'compare_tab': compare_tab, 'compare_col': compare_col, 'compare_name': compare_name, 'name': name}
            config['work']['fill'].append(d)
        except Exception as e:
            log('add_fill dictionary', str(e))
        save(config)
    except CancelRequest as e: raise e
    except Exception as e:
        log('add_fill', str(e))
        
def list_fills(config, prompt, action='list'):
    if 'work' not in config or 'fill' not in config['work']:
        return
    
    try:
        format_str = "Name: %s Source: (%s, %s) Compare: (%s, %s)\n\tCompare File: (%s)\n\tFill Columns: (%s)"
        compares = [format_str % (i['name'], i['source_col'], i['source_tab'], i['compare_col'], i['compare_tab'], os.path.splitext(os.path.basename(i['compare_name']))[0][:60],
                                  (", ".join(i['add_col']))[:60] if type(i['add_col']) == list else i['add_col']
                                  ) for i in config['work']['fill']]
    except Exception as e:
        log('format_str list compares', str(e))

    if action == 'display':
        for i in compares:
            print(i)
        return
    
    index = compares.index(pick_index(prompt, compares))

    if action == 'remove':
        remove_fill(config, index)

def remove_fill(config, index):
    del config['work']['fill'][index]
    save(config)
    raw_input("\nFill Removed. Press enter to continue.")


def work_fill(config):
    options = ['Add Fill', 'List/Edit', 'Remove Fill']
    choice = pick_index('Please choose an option: ', options)
    try:
        if choice == options[0]:
            add_fill(config)
        elif choice == options[1]:
            list_fills(config, "\nEdit Fill? ", 'edit')
        elif choice == options[2]:
            list_fills(config, "\nRemove Fill? ", 'remove')
    except Exception as e:
        print(e)

def work(config):
    options = ['Reduce', 'Union', 'Fill']

    try:
        choice = pick_index('Please choose an action to perform on the file: ', options)
    except CancelRequest:
        return

    try:
        if choice == options[0]:
            work_reduce(config)
        elif choice == options[1]:
            work_union(config)
        elif choice == options[2]:
            work_fill(config)
    except Exception as e:
        print(e)

def save(config):
    clear()
    
    backup = 'backup'
    config_folder = 'config'
    timestr = time.strftime("%Y%m%d-%H%M%S")
    
    loaded_path = config['path'] if 'path' in config else None
  
    fn, ext = os.path.splitext(os.path.basename(loaded_path))

    f_name, f_ext = os.path.splitext(os.path.basename(loaded_path))
    stamped_file = "%s-%s%s" % (f_name, timestr, f_ext)

    try:
        os.mkdir(backup)
    except:
        pass

    try:
        os.mkdir(config_folder)
    except:
        pass

    if os.path.exists(loaded_path):    
        try:
            copyfile(loaded_path, os.path.join(backup, stamped_file))
        except:
            print("Backup of config failed, config not saved.")
            return None

    with open(loaded_path, 'w') as f:
        config['path'] = loaded_path
        f.write(json.dumps(config))
    
    return config

def log(location, message):
    logger.warning(location + ': %s', message)

def main_loop(config):
    main = ['Run Work', 'Load File', 'Setup Actions', 'Summary', 'Exit']
    
    while True:
        clear()
        c_name, _ = os.path.splitext(os.path.basename(config['path']))
        padding = '-'* 75
        config_details = "%s\nLoaded File: (%s)\n%s" % (padding, c_name[:60], padding)
        print(config_details)
        
        choice = pick_index('\nPlease enter a number: ', main, can_cancel=False, do_clear=False)
        if choice == main[0]:
            try:
                pick_index('Confirm Run: ', ['Run'])

                path = config['path']
                output_file = os.path.basename(path)
                out_file_time = time.strftime("%Y%m%d-%H%M%S")
                output_folder = 'output'
                f_name, f_ext = os.path.splitext(output_file)
                stamped_file = "%s-%s%s" % (f_name[:30 - (len(out_file_time) + 5)], out_file_time, '.xlsx')
                out_path = os.path.join(output_folder, stamped_file)

                if 'work' not in config:
                    config['work'] = {}
                    save(config)
                    summary(config)
                else:
                    util.do_work(path, out_path)
                    compare.do_work(path, out_path)
                    union.do_work(path, out_path)
                    fill.do_work(path, out_path)

                    try:
                        open_file = pick_index("Open file (%s)? " % out_path, ['Open File'])
                        os.startfile(out_path, 'open')
                    except Exception as e:
                        print(e)
                        pass
            except Exception as e:
                print(e)
                log('main_loop', str(e))
            except CancelRequest:
                pass
        elif choice == main[1]:
            try:
                config = load_config()
            except CancelRequest:
                pass
            except Exception as e:
                log('load_config selected', str(e))
                pass
        elif choice == main[2]:
            work(config)
        elif choice == main[3]:
            summary(config)
        elif choice == main[4]:
            break

def log(*args):
    print('called log')
    print(args)
    
def run():
    try:
        config = load_config()
        main_loop(config)
    except CancelRequest:
        clear()
        raw_input('\n\nExiting... \n\n\tPress enter to close.')
        pass
    except Exception as e:
        log('main',e)
        pass

logger = None
            
if __name__ == "__main__":
    run()
