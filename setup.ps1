# Setup script for Centaurus-See-Music
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

# Check if pip is installed
try {
    $pipVersion = pip --version
    Write-Host "Found pip: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "pip not found! Please install pip" -ForegroundColor Red
    exit 1
}

# Create and activate virtual environment
Write-Host "`nSetting up virtual environment..." -ForegroundColor Cyan
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Cyan
try {
    .\venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "Failed to activate virtual environment. You may need to run:" -ForegroundColor Red
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    exit 1
}

# Install requirements
Write-Host "`nInstalling dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

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
Write-Host "1. Update config.py with your WLED device IP address" -ForegroundColor White
Write-Host "2. Install loopMIDI if not already installed" -ForegroundColor White
Write-Host "3. Connect your MIDI device" -ForegroundColor White
Write-Host "4. Run the visualizer:" -ForegroundColor White
Write-Host "   python sketches/wled-guitar-fretboard-pygame.py" -ForegroundColor Yellow

# Keep the window open
Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")