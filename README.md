# Centaurus SeeMusic

**Centaurus SeeMusic** is an accessible, real-time music visualization system that translates musical input into colorful, intuitive visual feedback. Designed with Deaf, hard-of-hearing, and neurodivergent musicians in mind, it enhances individual practice and group collaboration through vibrant on-screen displays.

While the full system supports synchronized LED instruments using ESP32 hardware, this repo is currently focused on delivering a **software-only MVP**—providing powerful on-screen visuals with no hardware setup required.

👉 Read the [SeeMusic MVP & Revenue Strategy](docs/SeeMusic_MVP.md) for the roadmap, use cases, and phased rollout plan.

---

## 🚀 Quick Start (Software-Only MVP)

This mode runs on any desktop system and provides visual feedback for piano or guitar—no soldering or hardware required.

```bash
# Clone the repo
git clone https://github.com/mylesdebastion/Centaurus-See-Music.git
cd Centaurus-See-Music

# Set up a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch software visualizer (piano-style)
python -m src.visualizers.test_visualizer
```

| Visualizer Module           | Description                        |
|-----------------------------|------------------------------------|
| `test_visualizer.py`        | Piano roll-style on-screen visual  |
| `guitar_visualizer.py`      | Fretboard grid-style preview       |
| `6x25_matrix_visualizer.py` | Simulates LED grid for guitar neck |

---

## 🧩 Key Features

- Real-time MIDI note capture and visualization
- Fullscreen visual feedback for different instruments
- Configurable color palettes (chromatic scale default)
- Room-based network sync (coming soon)
- Cross-platform (Windows, macOS, Linux)

---

## 🔧 Development Setup

```bash
# Activate virtual environment
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install/update dependencies
pip install -r requirements.txt
```

To run and test different visualizers, launch one of the scripts in `src/visualizers/`.

---

## 📡 [Phase 2] Optional Hardware Setup (ESP32 + WLED)

> These instructions are for the **future hardware add-on kits**, intended for Pro/Educator users who want to control real LED strips attached to instruments.

### Hardware Requirements
- WLED-compatible LED strip (WS2812B recommended)
- ESP8266 or ESP32 controller
- Local MQTT broker (e.g., Mosquitto)

### Example Setup
1. Flash [WLED firmware](https://github.com/Aircoookie/WLED) to your ESP32.
2. Connect the strip and configure WLED via browser.
3. Update `config.py` with your WLED IP.
4. Start the visualizer script with LED output enabled.

---

## 🧪 Troubleshooting

| Problem | Fix |
|--------|-----|
| MIDI input not detected | Run `python -c "import mido; print(mido.get_input_names())"` |
| WLED not responding | Ensure correct IP address and check network settings |
| MQTT errors | Confirm broker is running and firewall allows port 1883 |

---

## 🤝 Contributing

We welcome collaborators, testers, and feedback—especially from Deaf musicians and inclusive educators.

Start with the [SeeMusic MVP doc](docs/SeeMusic_MVP.md) and check issues labeled `good first issue`.

---

## 📄 License

MIT License (add LICENSE file if not already present)

---

## 👀 Coming Soon

- Web-based jam rooms for remote collaboration
- User-defined visual themes
- Stripe billing integration
- Hardware kits with 1:1 setup support for Pro/Educator users