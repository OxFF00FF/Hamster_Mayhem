@echo off


echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate
echo.

echo Installing dependencies...
pip install -r requirements.txt
echo.


if not exist ".env" (
    echo Copying .env.example to .env...
    copy .env.example .env
    echo.
)

echo Required dependencies installed
echo.
echo Please edit the .env file to add your HAMSTER_TOKEN
echo.
pause

start .env