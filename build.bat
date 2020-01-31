call clean.bat

pyinstaller --windowed --onefile main.py -n ExcelCompare

MKDIR dist\input
MKDIR dist\output
MKDIR dist\data
MKDIR dist\data\config
MKDIR dist\data\logs
MKDIR dist\data\cache

XCOPY input dist\input\
XCOPY data\docs dist\docs\
XCOPY data\filters dist\data\filters\
XCOPY data\resources dist\data\resources\

timeout /t 5 /nobreak

RENAME dist ExcelCompare

echo waiting for folder name change
timeout /t 5 /nobreak

"C:\Program Files\7-Zip\7z.exe" a -sfx ExcelCompareCompressed.exe ExcelCompare