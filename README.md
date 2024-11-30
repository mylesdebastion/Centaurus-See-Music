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

