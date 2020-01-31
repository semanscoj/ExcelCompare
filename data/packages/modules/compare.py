import pandas as pd
from openpyxl import load_workbook
import glob, os, json, xlrd, time

def upcase(cell):
    try:
        return cell.upper().lstrip().strip()
    except:
        return str(cell).lstrip().strip()

def filter_dataframe(filters, filtered):
    print(filters, filtered)
    try:
        for f in filters:
            print(f)
            filter_file = f['filter_file'] if 'filter_file' in f else None
            filter_value = f['filter_value'] if 'filter_value' in f else None
            filter_col = f['filter_col']
            
            if filter_file:
                try:
                    with open(lookup_file, 'r') as f:
                        all_filters = [i.strip() for i in f.readlines()]
                    filterred = filtered[filtered[filter_col].isin(all_filters)]
                except:
                    pass
            elif filter_value:
                filtered = filtered[filtered[filter_col] == filter_value]
    except Exception as e:
        print('error filtering dataframe', str(e))
             
    return filtered

def update(config, row, output_path):
    try:
        name = row['name']
        source_file = config['source_file']
        source_tab = row['source_tab']
        source_col = row['source_col']
                
        compare_file = row['compare_file']
        compare_tab = row['compare_tab']
        compare_col =  row['compare_col']
    except Exception as e:
        print('error pulling config')
        raise e

    # Record to compare
    try:
        adf = pd.read_excel(source_file, source_tab, converters={source_col:upcase})
        bdf = pd.read_excel(compare_file, compare_tab, converters={compare_col:upcase})
        print('adf', adf)
        print('bdf', bdf)
    except Exception as e:
        print('adf?', e)

    if 'filters' in row:
        filtered = filter_dataframe(row['filters'], adf)
    else:
        filtered = adf

    if source_file == compare_file:
        missing = filtered
    else:
        # Get the compare values as a set for a set subraction
        should_have = set(filtered[source_col])
        # Get a set of values that already exist

        if compare_file == source_file:
            missing = filtered
        else:
            has = set(bdf[compare_col])
            # Do a set subtraction and then get the missing rows from the master record
            missing = filtered[filtered[source_col].isin(should_have - has)]
        
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
            missing.to_excel(writer, sheet_name=name, index=False)
            print("Processed %s: %s" % (name, output_path))
    except Exception as e:
        print(e)
        print("Please close the file %s before running." % output_path)

def do_work(path, full_path):
    with open(path, 'r') as f:
        config = json.loads(f.read())

    print(config)

    if 'work' in config and 'reduce' in config['work']: 
        for row in config['work']['reduce']:
            try:
                update(config, row, full_path)
            except Exception as e:
                print('error', str(e))

if __name__ == "__main__":
    do_work('a.json', 'output\\test.xlsx')
    raw_input('\n\nPress enter to exit')
