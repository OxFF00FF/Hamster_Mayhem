@echo off

wt.exe -d . cmd.exe /c "venv\Scripts\activate && python main.py"

taskkill /IM cmd.exe /F

pause