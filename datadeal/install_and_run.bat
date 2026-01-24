@echo off
echo Installing required packages...
pip install pandas openpyxl xlrd
echo.
echo Running simple_datadeal.py...
python simple_datadeal.py
pause