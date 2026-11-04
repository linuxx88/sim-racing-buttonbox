# AMS2 Sim Dashboard & Button Box

[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)](#)
[![Client: Android / Web](https://img.shields.io/badge/Client-Android%20%2F%20Web-3DDC84?logo=android&logoColor=white)](#)
[![Sim: Automobilista 2](https://img.shields.io/badge/Primary%20Sim-Automobilista%202-FF4500)](#)
[![Sim: Assetto Corsa](https://img.shields.io/badge/Supported-Assetto%20Corsa-darkred)](#)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](#)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Ultra-low latency touch Button Box and telemetry dashboard for Android smartphones and tablets, powered by a lightweight standalone Windows bridge.

Designed primarily for **Automobilista 2 (AMS2)**, with full **Assetto Corsa** support.

---

## 🚀 Operational Features

### 1. Touch Button Box (Race & Cockpit)
- **Race Tab**: DRS, Brake Bias (+/-), Traction Control (TC +/-), Engine Brake (+/-), ABS (+/-), Headlights / Flash, Wipers, Pit Limiter.
- **Cockpit Tab**: On-the-fly in-race seat adjustments (Height, Forward/Backward), Pitch angle, and Field of View (FOV).
- **Mapping Drawer**: Retractable slide-out drawer (`☰`) listing all assigned keyboard shortcut mappings.
- **Haptic & Visual Feedback**: Instant touch visual feedback with support for repeated and held taps.
- **PWA Fullscreen Mode**: Native fullscreen toggle to hide mobile browser URL bars and system navigation.

---

## 🚧 Work In Progress (WIP)

The **GT3 Telemetry Dashboard** (digital speedometer, large gear indicator, 16-LED shift light bar, and live tire telemetry) is currently under active development and calibration.

👉 Check [TODO.md](TODO.md) for the detailed roadmap and telemetry engine progress (AMS2 & Assetto Corsa).

---

## 🏗️ Technical Architecture

```
┌───────────────────────────────┐
│       Android Device          │
│ (Chrome PWA / Fullscreen Web) │
└──────────────┬────────────────┘
               │ HTTP (SSE) & WebSocket :5000
               │ (USB via ADB Tunnel or WiFi LAN)
┌──────────────▼────────────────────────────────────────┐
│               SimBoxBridge (Windows PC)               │
│  - server.py       : Static HTTP server & SSE stream  │
│  - bridge.py       : WebSocket hub & message router   │
│  - injector.py     : DirectInput keystroke injection  │
│  - telemetry_ac.py : Shared Memory reader (mmap)      │
└──────────────┬────────────────────────────────────────┘
               │ DirectInput / Win32 API / Shared Memory
┌──────────────▼────────────────────────────────────────┐
│     Automobilista 2 (AMS2)  /  Assetto Corsa (AC)     │
└───────────────────────────────────────────────────────┘
```

---

## 📦 Installation & Quick Start

### Method 1: Standalone Binary (Recommended)
No Python installation required on your gaming PC.

1. Download or locate the executable at [release/SimBoxBridge.exe](file:///home/ssr/Desktop/ANDROID%20PROJECT/SIMDASHBOARD/release/SimBoxBridge.exe).
2. Run **`SimBoxBridge.exe`** (right-click > *Run as Administrator* to ensure DirectInput injection and shared memory access).

### Method 2: From Source (Python)
```bash
git clone https://github.com/linuxx88/sim-racing-buttonbox.git
cd sim-racing-buttonbox/sim_box_bridge

python -m venv .venv
# Windows :
.venv\Scripts\activate
pip install -r requirements-win.txt
python bridge.py
```

---

## 📱 Connecting Your Android Device

### Option A: USB Cable via ADB Reverse (Zero Latency - Recommended)
1. Enable **USB Debugging** in Android Developer Options.
2. Connect your device to the PC using a USB cable.
3. Run on your PC:
   ```bash
   adb reverse tcp:5000 tcp:5000
   ```
4. Open **Google Chrome** on Android and navigate to:
   ```
   http://localhost:5000
   ```

#### ⚠️ First Connection & ADB Pairing (If Device Is Not Detected)
If the reverse command fails or your phone is not recognized:
1. **Open a terminal**: In the project folder, open a Command Prompt (`cmd`) or PowerShell.
2. **Scan for devices**: Run:
   ```bash
   adb devices
   ```
3. **Allow USB Debugging on Android**: A prompt *"Allow USB debugging?"* will appear on your phone screen. Check *"Always allow from this computer"* and tap **OK**.
4. **Confirm Authorization**: If the terminal showed `unauthorized`, run `adb devices` again until the device status displays `device` (authorized).
5. **Start Bridge**: Run `run.bat` or `SimBoxBridge.exe`.

### Option B: Local Network (WiFi)
1. Ensure your smartphone and PC are connected to the same local WiFi network.
2. Find your PC's local IP address (`ipconfig` on Windows, e.g., `192.168.1.50`).
3. Open your mobile browser and go to:
   ```
   http://192.168.1.50:5000
   ```

---

## ⚙️ Simulator Configuration

### 1. Automobilista 2 (AMS2)
In the AMS2 control settings, assign the following keys (or customize the mapping dictionary in `sim_box_bridge/injector.py`):

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
- Telemetry streaming automatically goes live once you click "Drive" and enter the track (`LIVE` session).

---

## 🛠️ Project Structure

```
├── release/
│   └── SimBoxBridge.exe       # Standalone portable Windows binary
├── sim_box_bridge/
│   ├── bridge.py              # Main WebSocket server & input routing
│   ├── server.py              # Static HTTP server & SSE stream (/telemetry)
│   ├── index.html             # Touch web UI (Race, Cockpit, Dashboard tabs)
│   ├── injector.py            # Windows DirectInput keyboard injection engine
│   ├── telemetry_ac.py        # Kunos Shared Memory reader (ctypes / mmap)
│   ├── requirements.txt       # Cross-platform dependencies
│   └── requirements-win.txt   # Windows-specific dependencies
├── TODO.md                    # Roadmap & pending tasks
└── README.md
```

---

## 📄 License
Distributed under the Apache License 2.0. See [LICENSE](LICENSE) for full details.
