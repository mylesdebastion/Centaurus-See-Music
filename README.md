# Centaurus See Music

A distributed music visualization system that enables real-time collaboration between musicians by synchronizing LED visualizations across different instruments using MQTT.

## Overview

This project allows multiple musicians to see each other's playing in real-time through LED visualizations. Each musician can have their own visualization setup (e.g., LED strips on a piano, fretboard lights on a guitar) while also seeing what other musicians are playing through their local LED setup.

### Features

- Real-time MIDI note visualization
- MQTT-based synchronization between instruments
- Support for multiple WLED devices
- Configurable color mappings
- Auto-discovery of MIDI devices
- Per-host configuration management
- Support for different instruments (piano, guitar, etc.)
- Visual feedback of remote players' notes

## Prerequisites

### Required Hardware
- WLED-compatible LED strip (WS2812B recommended)
- ESP8266 or ESP32 controller (for WLED)
- MIDI device/instrument (keyboard, guitar interface, etc.)
- Computer with USB ports
- Stable network connection

### Software Requirements
1. Python Environment
   ```powershell
   # Check Python version (needs 3.8+)
   python --version
   ```

2. WLED Installation
   - Download WLED from: https://github.com/Aircoookie/WLED/releases
   - Flash WLED to your ESP8266/ESP32
   - Configure WLED with your network settings
   - Note down the IP address of your WLED device

3. Python Packages
   ```powershell
   # Core dependencies
   pip install pygame==2.6.1
   pip install mido==1.3.0
   pip install python-rtmidi==1.5.8
   pip install wled==0.16.0
   pip install numpy==1.24.3
   ```

4. MIDI Drivers
   - Windows: Download and install [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)
   - macOS: Built-in, no action needed
   - Linux: Install ALSA utilities
     ```bash
     sudo apt-get install libasound2-dev
     sudo apt-get install libjack-dev
     ```

5. Development Tools
   - VS Code or Cursor IDE
   - Git (for version control)
   ```powershell
   # Check Git installation
   git --version
   ```

### Network Configuration
1. WLED Setup
   - Connect to WLED AP (appears as "WLED-AP")
   - Configure WiFi settings
   - Note the assigned IP address
   - Update `WLED_IP` in your configuration

2. Firewall Settings
   - Allow UDP port 21324 (WLED)
   - Allow TCP port 1883 (MQTT)

### Optional Tools
- [Wireshark](https://www.wireshark.org/) for network debugging
- [MQTT Explorer](http://mqtt-explorer.com/) for MQTT testing
- [MIDI Monitor](https://www.midimonitor.com/) for MIDI debugging

### System Requirements
- Operating System:
  - Windows 10/11
  - macOS 10.15+
  - Linux (Ubuntu 20.04+ recommended)
- RAM: 4GB minimum
- Storage: 1GB free space
- Network: Stable WiFi or Ethernet connection

### Troubleshooting Common Issues

1. MIDI Device Not Detected
   ```powershell
   # Windows: Check MIDI devices
   midiInGetNumDevs
   
   # Linux: List MIDI devices
   aconnect -l
   ```

2. WLED Connection Issues
   ```powershell
   # Test WLED connection
   ping your-wled-ip-address
   ```

3. Python Environment Problems
   ```powershell
   # Verify virtual environment
   pip list
   python -c "import pygame; print(pygame.version.ver)"
   ```

### Development Environment Setup

1. Clone Repository
   ```powershell
   git clone https://github.com/your-username/Centaurus-See-Music.git
   cd Centaurus-See-Music
   ```

2. Create Virtual Environment
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install Dependencies
   ```powershell
   pip install -r requirements.txt
   ```

4. Configure Settings
   - Copy `config.example.py` to `config.py`
   - Update WLED IP address and other settings
   ```powershell
   cp config.example.py config.py
   ```

5. Verify Installation
   ```powershell
   python tests/test_environment.py
   ```

### Next Steps
- Continue to [Development Setup](#development-setup)
- Read the [MQTT Setup](#mqtt-setup-and-usage) guide
- Check [Troubleshooting](#troubleshooting-common-issues) if needed

## Development Setup

### Setting up Virtual Environment

1. Open PowerShell and navigate to your project directory:
```powershell
cd path/to/Centaurus-See-Music
```

2. Create a new virtual environment:
```powershell
python -m venv venv
```

3. Activate the virtual environment:
```powershell
.\venv\Scripts\Activate.ps1
```

If you get a security error, you may need to run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

4. Install dependencies:
```powershell
pip install -r requirements.txt
```

### VS Code / Cursor Setup

1. Open VS Code/Cursor in your project directory:
```powershell
code .  # for VS Code
cursor .  # for Cursor
```

2. Select Python Interpreter:
   - Press `Ctrl + Shift + P`
   - Type "Python: Select Interpreter"
   - Choose the interpreter from your virtual environment (`./venv/Scripts/python.exe`)

3. Configure Terminal:
   - Open a new terminal in VS Code/Cursor
   - It should automatically activate the virtual environment
   - If not, run the activation command from step 3 above

4. Verify Setup:
```powershell
python --version
pip list
```

## Installation

### Prerequisites

- Python 3.8+
- WLED-compatible LED strips
- MQTT broker (e.g., Mosquitto)
- MIDI devices (optional)

### Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- pygame
- paho-mqtt
- mido
- python-rtm

## MQTT Setup and Usage

### MQTT Broker Setup
1. Install Mosquitto MQTT broker:
   ```bash
   # Windows (using Chocolatey)
   choco install mosquitto

   # Linux
   sudo apt install mosquitto mosquitto-clients

   # macOS
   brew install mosquitto
   ```

2. Start the MQTT broker:
   ```bash
   # Windows
   net start mosquitto

   # Linux/macOS
   mosquitto -v
   ```

The broker runs on localhost:1883 by default.

### Local vs Remote Mode
Each visualizer instance can operate in one of two modes (toggle with 't' key):

- **LOCAL Mode**: 
  - Processes MIDI input from connected devices
  - Publishes notes to MQTT broker
  - Shows local notes with "(L)" indicator
  - Default mode on startup

- **REMOTE Mode**:
  - Ignores local MIDI input
  - Only displays notes received via MQTT
  - Shows remote notes with "(R)" indicator
  - Useful for monitoring other musicians

### Testing MQTT Setup
1. Run two instances of the visualizer:
   ```bash
   python -m src.visualizers.test_visualizer
   ```

2. In one instance, press 't' to switch to REMOTE mode
3. Play notes on the LOCAL instance
4. Both visualizers should show the notes:
   - LOCAL instance: Shows notes with "(L)"
   - REMOTE instance: Shows same notes with "(R)"

### MQTT Topics
The system uses the following MQTT topic structure:
- Notes: `centaurus/music/notes/<instrument>`
- Status: `centaurus/music/status/<instrument>/<client_id>`

Each client automatically subscribes to all instrument channels for cross-instrument visualization.
