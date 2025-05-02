@echo off
:: Check if the script is running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Change directory to the script's location
cd /d "%~dp0"

:: Run the Python script
python main.py
pause