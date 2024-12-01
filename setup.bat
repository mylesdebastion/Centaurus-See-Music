@echo off
echo Starting Centaurus-See-Music setup...
color 0B

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo Python not found! Please install Python 3.8 or higher from python.org
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Found Python: 
python --version

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo pip not found! Please install pip
    pause
    exit /b 1
)
echo Found pip:
pip --version

REM Create and activate virtual environment
echo.
echo Setting up virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    color 0C
    echo Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated

REM Install requirements
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Check for MIDI drivers
echo.
echo Checking MIDI drivers...
if exist "C:\Program Files (x86)\Tobias Erichsen\loopMIDI" (
    echo loopMIDI found
) else (
    echo loopMIDI not found! Please install from:
    echo https://www.tobias-erichsen.de/software/loopmidi.html
)

REM Create example config if it doesn't exist
echo.
echo Checking configuration...
if not exist config.py (
    if exist config.example.py (
        copy config.example.py config.py
        echo Created config.py from example
        echo Please update config.py with your WLED IP address and other settings
    ) else (
        echo Warning: config.example.py not found
    )
)

REM Test the installation
echo.
echo Testing installation...
python -c "import pygame; import mido; import numpy; print('All core modules imported successfully!')"
if %errorlevel% neq 0 (
    color 0C
    echo Failed to import some dependencies
) else (
    echo Core dependencies test passed
)

REM Print success message and next steps
echo.
color 0A
echo Setup completed!
echo.
color 0B
echo Next steps:
echo 1. Update config.py with your WLED device IP address
echo 2. Install loopMIDI if not already installed
echo 3. Connect your MIDI device
echo 4. Run the visualizer:
echo    python sketches/wled-guitar-fretboard-pygame.py

REM Keep the window open
echo.
color 07
pause 