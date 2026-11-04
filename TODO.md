# 📋 Project Roadmap & Backlog (TODO)

This document tracks upcoming features and pending development tasks, with priority given to completing the **GT3 Telemetry Dashboard**.

---

## 🏎️ GT3 Telemetry Dashboard (Work In Progress)

The visual interface (16-LED shift light bar, gear/speed readout, GT3 chassis SVG wireframe, tire telemetry cards) is implemented in the web UI. The live data engine requires the following tasks to become 100% operational:

### 1. Automobilista 2 (AMS2) Telemetry - High Priority
- [ ] **AMS2 Shared Memory Connector**: Implement the `ctypes`/`mmap` memory mapping structure for the `$pcars2$` block (Project CARS 2 / AMS2 memory specification).
- [ ] **Engine Variables Synchronization**:
  - `mRpm` and `mMaxRPM` for dynamic animation of the 16-LED shift light bar.
  - `mGear` for the current gear (R, N, 1-8).
  - `mSpeed` (converted from m/s to km/h).
- [ ] **Chassis & Tire Telemetry**:
  - `mTyrePressure` (converted from KPa to bar).
  - `mTyreTemp` (tire tread surface/core temperature in °C).
  - `mFuelLevel` and maximum tank capacity.
- [ ] **Lap Timing & Live Delta**:
  - `mCurrentTime`, `mBestLapTime`, and `mSplitTimeAhead` for dynamic delta calculations (-0.14 green/red).
  - Completed lap counter and current track position.

### 2. Assetto Corsa (AC) Telemetry - Secondary Priority
- [ ] **Privilege Elevation & Process Check**: Automate detection of whether Content Manager or `acs.exe` is running with administrator privileges.
- [ ] **Live Session State Verification**: Harden state transitions between menus (inactive state) and on-track gameplay (`AC_LIVE`).
- [ ] **Shift Light RPM Calibration**: Adjust red/blue shift light trigger thresholds based on per-car configuration files.

### 3. Network Streaming Pipeline (SSE / WebSocket)
- [ ] **Unified Payload Format**: Standardize the JSON structure broadcast on `/telemetry` so it remains identical regardless of the detected simulator (AMS2 or Assetto Corsa).
- [ ] **Fault Tolerance**: Automatically reconnect the SSE stream without needing a full page reload if a race session restarts.

### 4. Chassis Graphics, Tire & Brake Visualization
- [ ] **Detailed SVG Chassis Silhouette**: Enhance the current wireframe with a detailed top-down view (aerodynamic profiling, rear wing, front splitter, and wheel arches).
- [ ] **Dynamic Tire Thermal Heatmap**:
  - Real-time gradient coloration across all 4 tires according to temperature (Blue = cold `< 75°C`, Green = optimal `80-95°C`, Orange = hot `> 95°C`, Red = overheating `> 105°C`).
  - 3-zone thermal breakdown per tire (Inside / Middle / Outside) to monitor camber alignment.
- [ ] **Tire Wear & Surface Condition**: Visual residual tread wear gauge (0-100%) and flat-spot detection.
- [ ] **Brake Disc Temperature Monitoring**: SVG brake discs on all 4 corners with dynamic incandescence glow matching pad and rotor temperatures.

---

## 🏎️ Vehicle Class Profiles & Dedicated Dashboards

Telemetry requirements differ fundamentally across racing classes (rev limits, electronic assists, hybrid systems):

### 1. Formula 1 & Open-Wheel Profile
- [ ] **Modern F1 Steering Wheel Layout**: Ultra-compact central display with lateral rev LEDs and RPM range calibrated up to 15,000 RPM.
- [ ] **Hybrid Management (ERS / MGU-K)**: State of Charge (SOC %) battery gauge, deployment mode (Hotlap, Overtake, Balanced), and per-lap energy quota bar.
- [ ] **Dynamic DRS Indicator**: DRS status (detection zone, available within 1s window, open/active).
- [ ] **Advanced Driver Controls**: Brake Migration, Differential settings (Entry / Mid / Exit).

### 2. GT3 / GTE / GT4 Profile (Current)
- [ ] **Race DDU Display (Bosch / MoTeC Style)**: RPM range calibrated for 6,000 - 8,500 RPM.
- [ ] **Driver Assists**: Real-time ABS levels (1-12), Traction Control (TC1 / TC2), and Engine Mapping.
- [ ] **Endurance & Tire Management**: Core/surface operating windows and per-lap fuel consumption metrics.

### 3. Prototypes & Hypercars Profile (LMDh / LMh)
- [ ] **Virtual Energy Tank (VET)**: Tracking megajoule (MJ) energy allocations per stint per WEC/IMSA regulations.
- [ ] **Carbon Brake Monitoring**: Thermal status and active aerodynamic balance.

### 4. Multi-Dashboard UI Architecture
- [ ] **Auto-Detection / Manual Class Selector**: Instant theme and layout switching based on the car detected on track.

---

## 🕹️ Button Box (Future Enhancements)
- [ ] Configurable keybind profiles loaded from external JSON files without touching Python code.
- [ ] Virtual rotary encoder dials with haptic feedback (e.g. for multi-position Brake Bias / TC switches).
