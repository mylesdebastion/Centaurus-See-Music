# SeeMusic – Prompt Design Doc (v0.3 – Mobile-Aware, Software-Only MVP)

---

## 1. Use-Case Stories  (who / why)

### 1.1 Deaf Solo Performer – "Myles"

- **Goal:** Practices guitar riffs and sees pitch & velocity as color flashes on a virtual fretboard directly on their phone.
- **Scenario:** Opens the app on mobile ➜ MIDI guitar is detected ➜ notes light up on a simulated fretboard and keyboard grid ➜ can swap between views instantly.

### 1.2 Inclusive Music Teacher – "Ms. Rivers"

- **Goal:** Runs ensemble with Deaf & hearing students; wants synchronized visuals across mobile devices.
- **Scenario:** Logs into web app ➜ creates a Jam Room ➜ students join via mobile devices using a code ➜ each student selects their instrument view (e.g., piano, guitar) ➜ notes sync across devices.

### 1.3 Remote Band Session – "Looper Trio"

- **Goal:** Three musicians in different cities jam in real-time; need shared visuals.
- **Scenario:** Bassist starts cloud room ➜ other members join via mobile ➜ play notes ➜ each sees the others’ notes lit on their device’s chosen instrument grid.

### 1.4 Immediate Feedback Experience – Non-logged-in user

- Opens the app ➜ no login required ➜ app detects any connected MIDI instrument ➜ default piano grid view lights up with notes.
- Can switch to guitar grid or drum pads ➜ mobile-responsive layout.
- AI suggestions appear as soft pulses across views.

### 1.5 Educator Demonstration in Classroom

- Projects app from desktop while students join via phones or tablets.
- Teacher’s instrument drives synced lighting on each student’s screen in their chosen view.

### 1.6 Onboarding for New User

- New users tap "Start" ➜ app loads piano grid ➜ notes light up on press.
- User can toggle instrument views (keyboard, guitar, etc.) with 1 tap.
- Tooltip appears: "Jam with others? Join a room."

---

## 2. MVP Scope Summary

| Step | Component              | Details                                                                                                 |
| ---- | ---------------------- | ------------------------------------------------------------------------------------------------------- |
| 1    | **Input**              | MIDI (USB / Bluetooth / virtual). Option to toggle to monophonic pitch-to-MIDI via microphone.          |
| 2    | **Color Engine**       | HSV-based chromatic map. All users share one universal color scale.                                     |
| 3    | **Live Visualization** | Mobile-first grid visualization (keyboard, guitar, drum views).                                         |
| 4    | **Cloud Jam Rooms**    | FastAPI WebSocket server ➜ multi-user sync ➜ each device displays active notes based on joined session. |
| 5    | **AI Conductor**       | Suggests next note/chord ➜ shown in user’s current view.                                                |
| 6    | **Payment Processing** | Stripe Checkout integration for subscriptions; webhook to validate Pro/Educator access.                 |
| 7    | **Distribution**       | Electron app for desktop ➜ responsive web app for mobile (PWA capable).                                 |

---

## 3. Color Logic – The "Secret Sauce"

### 🔁 Shared Color Language (Cross-Instrument)

- Universal HSV-based chromatic color map:
  - C = Red, C#/Db = Red-Orange, ..., B = Purple.
  - Consistent across views and users.
- Note played ➜ lights up in same color on all devices, all views.
- Grid view updates live (keyboard, guitar, etc.) on every device in the room.

### 💡 Lighting Priority

- **Active notes**: bright, fully saturated.
- **AI-suggested**: pulsing, desaturated.
- **Faded history**: dimmed hue version.

### 🎯 Intuitive Instrument Feedback

- On-screen instruments light up in real time.
- No physical hardware needed for MVP.
- Mobile screen becomes the instrument’s mirror — notes appear where they'd be played.

### 🧠 AI Conductor

- Suggests next notes based on real-time play.
- Guides solos, fills, harmonies.
- Works across mobile + desktop ➜ visible on every user’s active view.

---

## 4. High-Level Architecture (Updated for Mobile Support)

```text
+--------------+        WebSocket        +--------------+
| Mobile/WebUI |  <--------------------> | FastAPI Hub  |
| (React/PWA)  |                        |  (Supabase)   |
+--------------+                        +--------------+
       | local MIDI via WebMIDI/WebUSB or mic-to-MIDI  |
       |                                        |
+--------------+                        +--------------+
| Visualization |                    | AI Conductor  |
|   Engine      |                    |   Engine      |
+--------------+                    +--------------+
       |
       v
+-------------------+
| Stripe Webhooks   |
| (Pro/Edu Tiers)   |
+-------------------+
```

---

## 5. Distribution Phases

### Phase 1 – Software-Only MVP (Web + Mobile)

- PWA-style mobile and desktop app
- Instrument views: keyboard, guitar, drums
- Cross-user lighting via WebSocket
- No external hardware required
- Toggle between MIDI input and monophonic pitch-to-MIDI (mic input)
- Payment processing via Stripe Checkout (monthly Pro, Educator plans)

### Phase 2 – AI & Playback Layer

- Add Conductor suggestions as predictive overlays
- Optional: MIDI playback for testing

### Phase 3 – Hardware Expansion

- LED kits (keyboard overlays, fretboards)
- AR overlay for phone camera (experimental)

---

## 6. Business Logic

| Tier                     | Free | Pro ($9/mo) | Educator ($29/mo) |
| ------------------------ | ---- | ------------ | ------------------ |
| Instrument View Switcher | ✅    | ✅            | ✅                  |
| Create/Join Room         | ✅    | ✅            | ✅                  |
| Max Connected Devices    | 1    | 3            | 10                 |
| AI Conductor             | ❌    | ✅            | ✅                  |
| Preset Save Slots        | 1    | 10           | ∞                  |
| Hardware Support         | ❌    | ❌            | ✅ (when launched)  |
| 1:1 Onboarding           | ❌    | ❌            | ✅                  |

Stripe billing env: `STRIPE_SECRET`