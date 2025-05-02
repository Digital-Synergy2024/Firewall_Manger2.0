@echo off
:: Check if pyinstaller is installed
where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller is not installed or not added to PATH. Please install PyInstaller and try again.
    pause
    exit /b
)

:: Run PyInstaller to create a standalone executable with an icon
pyinstaller --onefile --icon="icon.ico" --name="N3xG3n_FireWall_Manager" main.py

:: Check if the build was successful
if exist "dist\N3xG3n_FireWall_Manager.exe" (
    echo Build successful! The executable is located in the "dist" folder.
) else (
    echo Build failed. Please check for errors in the output above.
)

pause
