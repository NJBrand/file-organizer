@echo off
echo Starting File Organizer...

rem Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.6 or higher.
    pause
    exit /b 1
)

rem Check if required packages are installed
echo Checking required packages...
python -c "import send2trash" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required package: send2trash
    pip install send2trash
)

rem Start the GUI version
echo Starting File Organizer GUI...
python gui_organizer.py

if %errorlevel% neq 0 (
    echo An error occurred while running the application.
    pause
)

exit /b
