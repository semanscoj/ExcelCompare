@ECHO OFF

python -m pip install pandas xlrd openpyxl Jinja2 beautifulsoup4 pywin32 pyinstaller lxml

MKDIR input
MKDIR data\filters

echo.
echo MANUAL ACTION REQUIRED! In order to compile this application to an executable you will need to modify a file in: "C:\Python27\Lib\site-packages\pandas\io\formats" change the line within the style object from: template = env.get_template("html.tpl") to: template = env.from_string("html.tpl")
echo.

explorer C:\Python27\Lib\site-packages\pandas\io\formats

PAUSE