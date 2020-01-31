import pandas as pd
import os, json
from openpyxl import load_workbook

def do_work(config, full_path):
    with open(config, 'r') as f:
        config = json.loads(f.read())

    if 'work' in config and 'fill' in config['work']: 
        for row in config['work']['fill']:
            try:
                name = row['name']
                source_file = config['source_file']
                source_tab = row['source_tab']
                source_col = row['source_col']
                        
                compare_file = row['compare_file']
                compare_tab = row['compare_tab']
                compare_col =  row['compare_col']
                add_col = row['add_col']
            except Exception as e:
                print('error pulling config')
                raise e
            
            to_fill = pd.read_excel(compare_file, sheet_name=compare_tab)
            reference = pd.read_excel(source_file, sheet_name=source_tab)

            results = pd.merge(to_fill, reference, left_on=compare_col, right_on=source_col, how='left')

            results[add_col[0] + '_x'] = results[add_col[0] + '_x'].fillna(results[add_col[0] + '_y'])
            results.rename(columns = {add_col[0] + '_x':add_col[0]}, inplace = True)
            
            # Load existing workbook to update
            book = None
            try:
                book = load_workbook(full_path) 
            except Exception as e:
                print(e)

            out_cols = list(to_fill.keys())

            if type(add_col) == list:
                for a in add_col:
                    if a not in out_cols:
                        out_cols.append(a)
            else:
                out_cols.append(add_col)

            try:
                with pd.ExcelWriter(full_path) as writer:
                    if book:
                        writer.book = book
                        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
                    results.to_excel(writer, sheet_name=name, index=False, columns=out_cols)
                print("Processed %s: %s" % (name, full_path))
            except Exception as e:
                print(e)
                print("Please close the file %s before running." % full_path)

if __name__ == "__main__":
    do_work('../config\\a.json', 'output\\test.xlsx')
    raw_input('\n\nPress enter to exit')
