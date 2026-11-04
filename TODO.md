# 📋 Project Roadmap & Backlog (TODO)

This document tracks upcoming features, completed capabilities, and pending backlog tasks.

---

## ✅ Completed in this Sprint (AMS2 & GT3 Dashboard Integration)

### 1. Automobilista 2 (AMS2) Telemetry - High Priority (DONE)
- [x] **AMS2 Shared Memory Connector (`telemetry_ams2.py`)**:
  - Full `ctypes.Structure` mapping of `$pcars2$` Windows named memory mapping (MSVC 4-byte packed).
  - Validation of active shared memory via `OpenFileMappingW(FILE_MAP_READ, False, "$pcars2$")`.
  - Snapshot deserialization via `from_buffer_copy` with automatic heartbeat and pause detection.
- [x] **Engine Variables Synchronization**:
  - `mRpm` and `mMaxRPM` powering dynamic 16-LED shift light bar with progressive thresholds.
  - `mGear` with alphanumeric mapping (`-1` -> `R`, `0` -> `N`, `1..8` -> gears).
  - `mSpeed` conversion from m/s to km/h (`* 3.6`).
- [x] **Chassis & Tire Telemetry**:
  - `mAirPressure` converted from PSI to bar (`/ 14.5038`).
  - 3-Zone Thermal Breakdown (`Inside`, `Middle`, `Outside`) per tire from `mTyreTempLeft`, `mTyreTempCenter`, `mTyreTempRight` with geometric left/right wheel orientation.
  - Dynamic incandescence brake rotor temperatures from `mBrakeTempCelsius` (ambient to 650°C+ glow).
  - Residual tire wear percentages (`mTyreWear`).
  - Fuel level in liters and tank capacity.
- [x] **Lap Timing & Live Delta**:
  - `mCurrentTime`, `mBestLapTime`, `mLastLapTime` formatted in `M:SS.mmm`.
  - `mSplitTimeAhead` and `mSplitTimeBehind` live delta displays.
  - Lap count (`completedLaps / numberOfLaps`) and race track position.

### 2. Multi-Simulator Orchestration (`telemetry_manager.py`) (DONE)
- [x] Automatic simulator prioritization (AMS2 `$pcars2$` primary, Assetto Corsa `acpmf_physics` secondary).
- [x] Unified JSON payload normalization broadcast on `/telemetry` at 30 Hz SSE (Server-Sent Events).
- [x] Resilient recovery when simulator is started, restarted, or paused.

### 3. Multi-Class Vehicle Profiles (Frontend & Dashboard) (DONE)
- [x] **Multi-Class Quick-Switcher**: Instant profile selector buttons (`GT3`, `F1`, `HYPERCAR`) on top of the dashboard.
- [x] **GT3 / GTE Profile**: 6,000 - 8,500 RPM calibration, Bosch/MoTeC style DDU layout, ABS/TC status, 3-zone thermal heatmap.
- [x] **Formula 1 Profile**: 15,000 RPM range, Dynamic DRS indicator badge, ERS State of Charge (SOC %) battery gauge.
- [x] **Hypercar Profile**: Hybrid virtual energy tank, active aerodynamic indicators, carbon brake thermal monitoring.

### 4. Standalone Windows Executable & Verification (DONE)
- [x] Standalone binary compilation with PyInstaller 6.14.1 (`release/SimBoxBridge.exe`).
- [x] Automated integration testing suites (`test_ams2_integration.py` & `test_e2e_sse.py`).
- [x] Standalone synthetic mock producer for offline testing (`mock_ams2_producer.py`).

---

## 🔮 Future Enhancements & Backlog

### 1. Extended Driver Controls & Telemetry
- [ ] Real-time Engine Mapping selector readouts from AMS2 vehicle telemetry.
- [ ] Differential configuration (Entry, Mid, Exit) and Brake Migration displays for open-wheelers.
- [ ] Virtual fuel strategy calculator (estimated laps remaining based on rolling fuel consumption).

### 2. Button Box Hardware & Input
- [ ] External JSON configuration profiles for custom user keybindings without modifying source code.
- [ ] Rotary encoder support with haptic feedback simulation on Android touchscreen.
- [ ] Secondary companion layouts (Pit Strategy page, Flag and Spotter warnings overlay).
