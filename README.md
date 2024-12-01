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
