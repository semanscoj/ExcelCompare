import pandas as pd
from openpyxl import load_workbook
from shutil import copyfile
import glob, os, xlrd, json, time, re, logging

def do_work(config, full_path):
    with open(config, 'r') as f:
        config = json.loads(f.read())

    name = 'Summary'
    source_file = config['source_file']
    path = config['path']

    cols = ['type', 'name','source_file', 'source_tab', 'source_col', 'compare_file', 'compare_tab', 'compare_col', 'add_col', 'filters']

    data = []

    for work_type, work in config['work'].items():
        for task in work:
            task['type'] = work_type
            task['source_file'] = source_file
            task['path'] = path
            data.append(task)

    
    df = pd.DataFrame(data)
    
    # Load existing workbook to update
    book = None
    try:
        book = load_workbook(full_path) 
    except:
        pass

    try:
        with pd.ExcelWriter(full_path) as writer:
            if book:
                writer.book = book
                writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
            df.to_excel(writer, sheet_name=name, index=False, columns=cols)
            print("Processed %s: %s" % (name, full_path))
    except Exception as e:
        print(e)
        print("Please close the file %s before running." % full_path)

if __name__ == "__main__":
    #do_work('config\\test.json', 'output\\test.xlsx')
    raw_input('\n\nPress enter to exit')
