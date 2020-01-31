import pandas as pd
from openpyxl import load_workbook
from shutil import copyfile
import glob, os, xlrd, json, time, re, logging, traceback

def upcase(cell):
    try:
        return cell.upper().lstrip().strip()
    except:
        return str(cell).lstrip().strip()

def highlight_diff(x, list_file, list_col, ref_file, ref_col, highlight_matching=True):
    if not highlight_matching:
        c1 = 'background-color: red'
        c2 = ''
    else:
        c1 = ''
        c2 = 'background-color: red'

    m = list_file[list_col].isin(ref_file[ref_col])

    df1 = pd.DataFrame(c2, index=x.index, columns=x.columns)
    df1.loc[m, :] = c1
    return df1

def write_style(output_path, list_file, list_col, ref_file, ref_col, name):
        # Load existing workbook to update
        book = None
        try:
            book = load_workbook(output_path) 
        except:
            pass
        try:
            with pd.ExcelWriter(output_path) as writer:
                if book:
                    writer.book = book
                    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
                (list_file.style.apply(highlight_diff, list_file=list_file, list_col=list_col, ref_file=ref_file, ref_col=ref_col, axis=None).to_excel(writer, sheet_name=name, engine='openpyxl', index=False))
            print("Processed %s: %s" % (name, output_path))
        except Exception as e:
            tb = traceback.format_exc()
            with open('error.txt', 'w') as f:
                f.write(str(e))
                f.write(tb)
            print(e)
            print(tb)

def do_work(config, full_path):
    with open(config, 'r') as f:
        config = json.loads(f.read())
    
    if 'work' in config and 'union' in config['work']:    
        for row in config['work']['union']:
            try:
                name = row['name']
                source_file = config['source_file']
                source_tab = row['source_tab']
                source_col = row['source_col']
                
                compare_file = row['compare_file']
                compare_tab = row['compare_tab']
                compare_col =  row['compare_col']
            except Exception as e:
                print('error', str(e))            

            df1 = pd.read_excel(source_file, source_tab, converters={source_col:upcase})
            df2 = pd.read_excel(compare_file, compare_tab, converters={compare_col:upcase})


            write_style(full_path, df1, source_col, df2, compare_col, name)


if __name__ == "__main__":
    do_work('a.json', 'test.xlsx')
    raw_input('\n\nPress enter to exit')
