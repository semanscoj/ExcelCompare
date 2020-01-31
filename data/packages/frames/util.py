from glob import glob
import os, json
import pandas as pd
from zipfile import ZipFile
from bs4 import BeautifulSoup
from Tkinter import *
from shutil import move

class Util:
    __timer_id = None
    ROOT = None
    
    CACHED_DATAFRAMES = {}
    
    CONFIG_ROOT = 'data\\config'
    OUTPUT_ROOT = 'output'
    INPUT_ROOT = 'input'
    CACHE_ROOT = 'data\\cache'
    FILTER_ROOT = 'data\\filters'

    RESOURCE_ROOT = 'data\\resources'

    CONFIG_EXT = 'json'
    OUTPUT_EXT = 'xlsx'
    INPUT_EXT = 'xlsx'
    FILTER_EXT = 'filter'

    DEFAULT_PROMPT = 'Click Here'

    REQUIRED_COLOR = 'yellow'
    OPTIONAL_COLOR = 'green'
    COMPLETED_COLOR = 'green'

    ACTIONS = ['reduce', 'union', 'fill']

    ACTION_FORMAT = {
        'reduce':'NAME: (%s) FILE: (%s)',
        'union':'NAME: (%s) FILE: (%s)',
        'fill':'NAME: (%s) FILE: (%s)'
    }

    JOBS = {
        'reduce':{'order': ['source_tab', 'source_col', 'compare_file', 'compare_tab', 'compare_col', 'name', 'filters'],
                  'optional':['filters'], 'partial':[]},
        'union':{'order': ['source_tab', 'source_col', 'compare_file', 'compare_tab', 'compare_col', 'name'],
                 'optional':[], 'partial':[]},
        'fill':{'order': ['source_tab', 'source_col', 'compare_file', 'compare_tab', 'compare_col', 'name', 'add_col'],
                'optional':['add_col'], 'partial':[]}
    }

    ONE_TO_MANY = ['filters', 'add_col']

    @staticmethod
    def get_help_text(command):
        help_text = {
            'reduce':'''
            The Reduce Action:

            The output will be the result of subtracting file A from file B.
            The results will show every row that exists in A but does not exist in B.
            You can filter the file A, to reduce the noise shown in the output file.
            All columns from A will be shown in the output file.''',
            'union':'''
            The Union Action:

            The output will have all rows that exist in File A but are missing in File B highlighted in red.''',
            'fill':'''
            The Fill Action:

            The output will Fill file B using looked up values in file A.
            You will be required to choose a column from File A and File B to direct the look up operation.
            Extra Columns from File A will NOT be included.
            All columns from File B WILL be included.
            '''
        }

        if command not in help_text:
            return 'Not implemented'

        return help_text[command]

    @staticmethod
    def get_resource(resource):
        path = os.path.join(Util.RESOURCE_ROOT, resource)
        print(path)
        return path

    @staticmethod
    def get_values(job, path, sheet, column):
        df = Util.cache_dataframe(job, 'source_file', 'source_tab')
        return sorted(set(df[column]))

    @staticmethod
    def cache_dataframe(job, path, sheet):
        mtime = os.path.getmtime(job.get_value(path))
        path = job.get_value(path)
        sheet = job.get_value(sheet)

        base_name = os.path.splitext(os.path.basename(path))[0]

        key = "%s-%s-%s" % (base_name, sheet, str(mtime))

        try:
            os.mkdir(Util.CACHE_ROOT)
        except:
            pass

        cache_path = os.path.join(Util.CACHE_ROOT, key)
        
        if key in Util.CACHED_DATAFRAMES:
             df = Util.CACHED_DATAFRAMES[key]
        elif os.path.exists(cache_path):
            df = pd.read_csv(cache_path)
            Util.CACHED_DATAFRAMES[key] = df
        else:
            df = pd.read_excel(path, sheet)
            Util.CACHED_DATAFRAMES[key] = df
            df.to_csv(cache_path, encoding = 'utf-8')
        return df

    @staticmethod
    def get_file_list(path, ext):
        return [i for i in glob(os.path.join(path, '*.%s' % ext))]

    @staticmethod
    def check_masters(source_root = None, source_extension = None, config_root = None, config_extension = None):
        source_root =  source_root or Util.INPUT_ROOT
        source_extension = source_extension or Util.INPUT_EXT
        config_root =  config_root or Util.CONFIG_ROOT
        config_extension = config_extension or Util.CONFIG_EXT
    
        default = {"work":{"reduce":[],"union":[],"fill":[]}}
        
        masters = set([os.path.splitext(os.path.basename(i))[0] for i in glob(os.path.join(source_root,"*.%s" % source_extension)) if '$' not in i])
        configs = set([os.path.splitext(os.path.basename(i))[0] for i in glob(os.path.join(config_root,"*.%s" % config_extension)) if '$' not in i])

        try:
            for i in (masters - configs):
                default['path'] = os.path.join(config_root, "%s.%s" % (i, config_extension))
                default['source_file'] = os.path.join(source_root, "%s.%s" % (i, source_extension))
                with open(os.path.join(config_root, '%s.%s' % (i, config_extension)), 'w') as f:
                    f.write(json.dumps(default))
        except Exception as e:
            print(e)
            pass
        
        full_configs = set([os.path.splitext(os.path.basename(i))[0] for i in glob(os.path.join(config_root,"*.%s" % config_extension)) if '$' not in i])

        missing = os.path.join(config_root, 'missing')
        try:
            os.mkdir(missing)
        except:
            pass

        for c in full_configs:
            if c not in masters:
                m = c + ".%s" % config_extension
                try:
                    move(os.path.join(config_root, m), os.path.join(missing, m))
                except:
                    pass
                
    @staticmethod
    def get_sheet_name(job, level):
        if level == 0:
            key = 'source_file'
        else:
            key = 'compare_file'

        try:    
            with ZipFile(job.get_value(key)) as zippedFile:
                summary = zippedFile.open(r'xl/workbook.xml').read()
                soup = BeautifulSoup(summary, "xml")
                sheets = [sheet.get("name") for sheet in soup.find_all('sheet')]

            return sheets
        except:
            return []

    @staticmethod
    def get_filters(job, key):
        df = Util.cache_dataframe(job, 'source_file', 'source_tab')
        return sorted(set([str(i) for i in df[job.get_value('filter_col')] if i]))
    
    @staticmethod
    def get_column_names(job, level):
        if level == 0:
            f = 'source_file'
            tab = 'source_tab'
        else:
            f = 'compare_file'
            tab = 'compare_tab'
        df = Util.cache_dataframe(job, f, tab) 
        try:
            return sorted([str(i) for i in df.keys()])
        except Exception as e:
            print(e)
            return []
        
    @staticmethod
    def get_output_name(job, count):
        try:
            source_base = os.path.basename(job.get_value('source_file'))
            compare_base = os.path.basename(job.get_value('compare_file'))
            
            default_item_length = 8
            default_a = os.path.splitext(source_base)[0][:default_item_length].replace('-', '_').replace(' ', '_')
            default_b = os.path.splitext(compare_base)[0][:default_item_length].replace('-', '_').replace(' ', '_')

            default = "%s%s_%s-%s" % (job.action[0].upper(), count, default_a.strip('-').strip('_'), default_b.strip('-').strip('_'))
            return default[:30]
        except Exception as e:
            print(e)
            return ''
