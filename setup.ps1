# setup.ps1

Write-Host "Starting Centaurus-See-Music setup..." -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found! Please install Python 3.8 or higher from python.org" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "`nCreating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate virtual environment
try {
    Write-Host "`nActivating virtual environment..." -ForegroundColor Cyan
    .\venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "Failed to activate virtual environment. You may need to run:" -ForegroundColor Red
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    exit 1
}

# Install dependencies with binary preference
Write-Host "`nInstalling dependencies..." -ForegroundColor Cyan
python -m pip install --upgrade pip
pip install --only-binary :all: pygame==2.5.2
pip install mido python-rtmidi wled paho-mqtt
pip install --only-binary :all: numpy

# Check for MIDI drivers
Write-Host "`nChecking MIDI drivers..." -ForegroundColor Cyan
$loopMidiPath = "C:\Program Files (x86)\Tobias Erichsen\loopMIDI"
if (Test-Path $loopMidiPath) {
    Write-Host "loopMIDI found" -ForegroundColor Green
} else {
    Write-Host "loopMIDI not found! Please install from:" -ForegroundColor Yellow
    Write-Host "https://www.tobias-erichsen.de/software/loopmidi.html" -ForegroundColor Yellow
}

# Create example config if it doesn't exist
Write-Host "`nChecking configuration..." -ForegroundColor Cyan
if (-not (Test-Path "config.py")) {
    if (Test-Path "config.example.py") {
        Copy-Item "config.example.py" "config.py"
        Write-Host "Created config.py from example" -ForegroundColor Green
        Write-Host "Please update config.py with your WLED IP address and other settings" -ForegroundColor Yellow
    } else {
        Write-Host "Warning: config.example.py not found" -ForegroundColor Red
    }
}

# Test the installation
Write-Host "`nTesting installation..." -ForegroundColor Cyan
try {
    python -c "import pygame; import mido; import numpy; print('All core modules imported successfully!')"
    Write-Host "Core dependencies test passed" -ForegroundColor Green
} catch {
    Write-Host "Failed to import some dependencies" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

# Print success message and next steps
Write-Host "`nSetup completed!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Update config.py with your settings" -ForegroundColor Yellow
Write-Host "2. Run 'start.ps1' to launch the visualizer" -ForegroundColor Yellow
Write-Host "3. Press 't' to toggle between LOCAL and REMOTE modes" -ForegroundColor Yellow