# SeeMusic MVP & Revenue Strategy (Software-Only Phase 1)

## ✅ Mission

**SeeMusic** empowers Deaf, hard-of-hearing, and neurodivergent musicians with **real-time visual cues** to interpret and play music with others—no sound required.

Our Phase 1 MVP delivers **on-screen, software-only visualization** tools that require no hardware setup, making the system accessible from day one.

As interest grows, **Pro and Educator users will gain access to premium hardware add-ons** such as LED strips for keyboards and Fret Zealot-compatible LED grids for guitars, **with 1:1 support and tailored onboarding** as we co-design around their needs.

---

## 💡 Phase 1 MVP Summary

A **software-only, cross-platform app** that:
- Converts **MIDI or audio input** into real-time visual feedback.
- Shows **on-screen visualizations** of instruments with chromatic color mapping.
- Enables **networked jam rooms** for visual ensemble sync.
- Provides a clean, **accessible GUI** for selecting scales, color palettes, and layouts.
- Supports **tiered subscriptions** with feature unlocks for educators and power users.

> 🎯 **Hardware kits** are a feature-rich add-on for *later*, not required to benefit from the MVP.

---

## 🧩 MVP Features – Must Haves

| Feature                   | Description                                                                 | Priority   |
|--------------------------|-----------------------------------------------------------------------------|------------|
| 🎵 Input Capture         | MIDI input (existing), optional audio-to-MIDI detection                     | Essential  |
| 🖥️ On-Screen Visualizer | Fullscreen grid visualizer for guitar, piano, drum pad, or abstract modes   | Essential  |
| 🌐 Cloud Jam Rooms       | WebSocket-based room sync for remote ensemble play                          | High       |
| 🎛️ GUI Control Panel    | React-based UI for visual layout, scale/key, palette, device settings       | Essential  |
| 💡 Color Mapping Presets | Chromatic color map (C=Red, G=Orange, etc.) with future custom themes       | Essential  |
| 🧾 Tiered Account Access | Stripe billing integration with Free, Pro, and Educator feature gating      | Essential  |

---

## 🛠️ Tech Stack (Software-Only Phase 1)

| Layer        | Tools / Notes                                                                 |
|--------------|--------------------------------------------------------------------------------|
| Input        | MIDI (mido), audio-to-MIDI (Essentia or WebAudio)                             |
| Core Engine  | Python (FastAPI) or JS (NestJS), modular `seemusic_core` backend               |
| GUI          | React + Tailwind via Electron, or browser-based front-end                     |
| Visualization| Canvas/WebGL rendering for simulated LED display                              |
| Sync         | WebSockets for room sync, FastAPI or NestJS server                            |
| Billing      | Stripe Checkout, webhook-based feature gating                                 |

---

## 📦 Revenue Model (Draft)

| Tier          | Price     | Features                                                                 |
|---------------|-----------|--------------------------------------------------------------------------|
| **Free**      | $0        | Local visualizer, 1 device, limited layouts                              |
| **Pro**       | $9/mo     | Multiple layouts, 3 devices, join/host cloud jam rooms, priority support |
| **Educator**  | $29/mo    | Up to 10 devices, classroom presets, save/share layouts, 1:1 onboarding  |
| *(Future)* **Hardware Add-on** | TBD | Preconfigured LED kits (keyboard/guitar), device auto-calibration, extended support |

---

## 🚧 Deferred (Future Hardware Phase)

| Deferred Item                     | Reason for Deferral                                                  |
|----------------------------------|-----------------------------------------------------------------------|
| ESP32 Hardware Kits              | Tariff risks and manufacturing complexity                            |
| Firmware Auto-flash / OTA        | Only needed when hardware kits are shipped                           |
| Sensor-based Interactivity       | (e.g., foot pads, percussion triggers) - Phase 3 exploration         |
| Custom 3D Mounting Solutions     | Co-design with early Pro/Educator adopters only                      |

---

## 🧪 Immediate Next Steps

1. ✅ Refactor `Centaurus-See-Music` repo into modular `seemusic_core` Python package.
2. 🟡 Prototype cross-platform GUI with React in Electron.
3. 🟡 Set up FastAPI WebSocket server with room code and device auth.
4. 🟡 Integrate Stripe Checkout for basic Free/Pro billing tiers.
5. 🔲 Design onboarding UX (palette/scale wizard, preset preview).
6. 🔲 Launch landing page to capture beta signups + use case surveys.

---

## 📅 Projected Timeline (Software-Only)

| Phase                  | Weeks | Deliverables                                                           |
|------------------------|-------|------------------------------------------------------------------------|
| Repo Cleanup & Modularization | 1     | `seemusic_core` pip package, CLI examples                            |
| GUI Alpha (Electron + React)  | 3     | Local visualizer, scale/palette controls                             |
| WebSocket Jam Rooms            | 3     | Internet-enabled sync w/ latency handling                            |
| Stripe Integration             | 2     | Checkout, webhook, tier-gated feature flags                          |
| Polishing, Onboarding & Docs  | 2     | Sentry, tooltips, videos, Docker image for headless users            |

**→ Total: ~11 weeks part-time (7–8 weeks full-time)**