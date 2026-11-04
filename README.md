# AMS2 Sim Dashboard & Button Box

[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)](#)
[![Client: Android / Web](https://img.shields.io/badge/Client-Android%20%2F%20Web-3DDC84?logo=android&logoColor=white)](#)
[![Sim: Automobilista 2](https://img.shields.io/badge/Primary%20Sim-Automobilista%202-FF4500)](#)
[![Sim: Assetto Corsa](https://img.shields.io/badge/Supported-Assetto%20Corsa-darkred)](#)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](#)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Ultra-low latency touch Button Box and real-time Telemetry Dashboard for Android smartphones and tablets, powered by a lightweight standalone Windows bridge.

Designed primarily for **Automobilista 2 (AMS2)** via `$pcars2$` Windows Shared Memory, with secondary support for **Assetto Corsa** (`acpmf_physics`).

---

## 🚀 Key Features

### 1. Touch Button Box (Race & Cockpit)
- **Race Tab**: DRS, Brake Bias (+/-), Traction Control (TC +/-), Engine Brake (+/-), ABS (+/-), Headlights / Flash, Wipers, Pit Limiter.
- **Cockpit Tab**: On-the-fly in-race seat adjustments (Height, Forward/Backward), Pitch angle, and Field of View (FOV).
- **Mapping Drawer**: Retractable slide-out drawer (`☰`) displaying all assigned keyboard shortcut mappings.
- **Ultra-Low Latency**: DirectInput key injection with tactile visual feedback and support for repeated and held taps.
- **PWA Fullscreen Mode**: Native fullscreen toggle (`⛶`) to maximize screen real estate on mobile devices.

### 2. Multi-Class Telemetry Dashboard (30 Hz SSE Stream)
- **Active Simulator Detection Badge**: Real-time indication of connected game (`AMS2`, `Assetto Corsa`, or `EN ATTENTE`).
- **Multi-Class Profile Selector**: Switch layouts on the fly between **GT3 / GTE**, **Formula 1**, and **Prototypes / Hypercars**.
- **16-LED Progressive Rev Bar**: Dynamic shift lights with configurable RPM limits (GT3: ~8,500 RPM, F1: ~15,000 RPM).
- **Digital Speedometer & Huge Gear Readout**: Instant speed (km/h) and gear indicator (`R`, `N`, `1..8`).
- **3-Zone Thermal Tire Heatmap**: Dynamic Inside / Middle / Outside thermal monitoring for all 4 tires (Cold < 75°C, Optimal 80-95°C, Hot > 95°C, Overheating > 105°C).
- **Glowing Brake Incandescence**: SVG disc rotors that dynamically heat up and glow bright orange/red under heavy braking.
- **Live Timing & Delta**: Live lap timer, best lap, last lap, sector delta (+/-), and completed lap counters.
- **Hybrid & Aero Systems**: ERS State of Charge battery bar and dynamic DRS status badge.

---

## 🏗️ Technical Architecture

```
┌─────────────────────────────────┐
│         Android Device          │
│  (Chrome PWA / Fullscreen Web)  │
└────────────────┬────────────────┘
                 │ HTTP (SSE /telemetry) & WebSocket :5000
                 │ (Zero-latency USB via ADB Tunnel or WiFi LAN)
┌────────────────▼────────────────────────────────────────┐
│               SimBoxBridge (Windows PC)                 │
│  - server.py            : SSE telemetry stream (30 Hz)  │
│  - bridge.py            : WebSocket hub & command router│
│  - injector.py          : DirectInput key injection     │
│  - telemetry_manager.py : Multi-sim orchestrator        │
│  - telemetry_ams2.py    : $pcars2$ Shared Memory reader │
│  - telemetry_ac.py      : acpmf Shared Memory reader    │
│  - watcher.py           : Process & ADB auto-engagement │
└────────────────┬────────────────────────────────────────┘
                 │ Windows Shared Memory & DirectInput
┌────────────────▼────────────────────────────────────────┐
│      Automobilista 2 (AMS2)  /  Assetto Corsa (AC)      │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Installation & Quick Start

### Method 1: Standalone Binary (Recommended)
No Python installation or dependencies required on your gaming PC.

1. Locate or run the executable at [`release/SimBoxBridge.exe`](release/SimBoxBridge.exe).
2. Run **`SimBoxBridge.exe`** (run as Administrator if your simulator runs with elevated privileges).

### Method 2: From Source (Python 3.10+)
```bash
git clone https://github.com/linuxx88/sim-racing-buttonbox.git
cd sim-racing-buttonbox/sim_box_bridge

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-win.txt
python bridge.py
```

---

## 📱 Connecting Your Android Device

### Option A: USB Cable via ADB Reverse (Zero Latency - Recommended)
1. Enable **USB Debugging** in Android Developer Options.
2. Connect your device to your PC with a USB cable.
3. In a terminal on your PC, run:
   ```bash
   adb reverse tcp:5000 tcp:5000
   ```
4. Open **Google Chrome** on your Android device and go to:
   ```
   http://localhost:5000
   ```

#### ⚠️ First Connection & ADB Pairing (If Device Is Not Detected)
1. Open a Command Prompt (`cmd`) or PowerShell in the project directory.
2. Run:
   ```bash
   adb devices
   ```
3. A prompt *"Allow USB debugging?"* will appear on your phone screen. Check *"Always allow from this computer"* and tap **OK**.
4. Confirm authorization: `adb devices` should show `device` (authorized).
5. Launch `SimBoxBridge.exe`.

### Option B: Local Network (WiFi)
1. Connect your smartphone and PC to the same WiFi network.
2. Find your PC's local IP address (`ipconfig`, e.g. `192.168.1.50`).
3. Open your mobile browser and navigate to:
   ```
   http://192.168.1.50:5000
   ```

---

## ⚙️ Simulator Configuration

### 1. Automobilista 2 (AMS2)
> [!IMPORTANT]
> To enable telemetry streaming in Automobilista 2:
> 1. Launch **Automobilista 2**.
> 2. Go to **Options > System**.
> 3. Set **Shared Memory** to **`Project CARS 2`**.

In the AMS2 control settings, assign the following keys (or adjust mappings in `sim_box_bridge/injector.py`):

| Action | Injected Keystroke |
| :--- | :--- |
| **DRS** | `D` |
| **Brake Bias + / -** | `Ctrl + Up` / `Ctrl + Down` |
| **Traction Control (TC) + / -** | `T` / `Shift + T` |
| **Engine Brake + / -** | `E` / `Shift + E` |
| **ABS + / -** | `A` / `Shift + A` |
| **Headlights / High Beam Flash** | `L` / `F` |
| **Wipers** | `W` |
| **Pit Limiter** | `P` |
| **Seat Adjustments (Up / Down / Fwd / Back)** | `Home` / `End` / `PageUp` / `PageDown` |
| **Pitch & FOV** | `Insert` / `Delete` |

### 2. Assetto Corsa (AC)
- Enable Shared Memory in **Content Manager**: *Settings > Custom Shaders Patch > General Patch Settings*.
- Telemetry streaming goes live once you hit "Drive" on the track (`LIVE` session).

---

## 🛠️ Project Structure

```
├── release/
│   └── SimBoxBridge.exe          # Standalone portable Windows binary (~9.5 MB)
├── sim_box_bridge/
│   ├── bridge.py                 # Main WebSocket server & input routing
│   ├── server.py                 # Static HTTP server & SSE stream (/telemetry)
│   ├── index.html                # Responsive Web UI (Race, Cockpit, Dashboard)
│   ├── injector.py               # Windows DirectInput keyboard injection engine
│   ├── telemetry_manager.py      # Multi-sim orchestrator (AMS2 & AC)
│   ├── telemetry_ams2.py         # AMS2 ($pcars2$) Shared Memory reader
│   ├── telemetry_ac.py           # Assetto Corsa Shared Memory reader
│   ├── mock_ams2_producer.py     # Standalone synthetic telemetry generator
│   ├── test_ams2_integration.py  # Unit test suite for AMS2 telemetry
│   ├── test_e2e_sse.py           # E2E integration test for telemetry manager
│   ├── watcher.py                # Process monitor and ADB reverse trigger
│   ├── requirements.txt          # Cross-platform dependencies
│   └── requirements-win.txt      # Windows-specific dependencies
├── TODO.md                       # Roadmap & completed tasks
└── README.md
```

---

## 📄 License
Distributed under the Apache License 2.0. See [LICENSE](LICENSE) for full details.
