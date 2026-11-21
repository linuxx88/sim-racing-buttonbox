"""
Générateur / Mock de télémétrie mémoire partagée Automobilista 2 ($pcars2$).
Permet de tester et valider le lecteur AMS2 et le dashboard sans lancer le jeu.
"""

import ctypes
import math
import mmap
import threading
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from telemetry_ams2 import AMS2SharedMemory, TYRE_MAX, STORED_PARTICIPANTS_MAX


class MockAMS2Producer:
    """Producteur contrôlable par thread de la mémoire partagée AMS2 ($pcars2$)."""

    def __init__(self, fps: int = 30):
        self.fps = fps
        self._running = False
        self._thread = None
        self._mm = None
        self._shm = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _worker(self):
        size = ctypes.sizeof(AMS2SharedMemory)
        self._mm = mmap.mmap(-1, size, tagname="$pcars2$", access=mmap.ACCESS_WRITE)
        self._shm = AMS2SharedMemory.from_buffer(self._mm)

        shm = self._shm
        shm.mVersion = 10
        shm.mBuildVersionNumber = 1520
        shm.mGameState = 2  # INGAME_PLAYING
        shm.mSessionState = 5  # RACE
        shm.mRaceState = 2  # RACING
        shm.mNumParticipants = 20
        shm.mViewedParticipantIndex = 0

        p0 = shm.mParticipantInfo[0]
        p0.mIsActive = True
        p0.mName = b"Sim Driver"
        p0.mRacePosition = 3
        p0.mLapsCompleted = 5

        shm.mCarName = b"Porsche 911 GT3 R"
        shm.mCarClassName = b"GT3"
        shm.mTrackLocation = b"Spa-Francorchamps"
        shm.mTrackVariation = b"GP"
        shm.mTrackLength = 7004.0
        shm.mLapsInEvent = 15

        shm.mMaxRPM = 8800.0
        shm.mFuelCapacity = 110.0
        shm.mFuelLevel = 0.55
        shm.mBrakeBias = 0.54
        shm.mAntiLockSetting = 2
        shm.mTractionControlSetting = 3

        shm.mBestLapTime = 138.450
        shm.mLastLapTime = 139.120
        shm.mSplitTimeAhead = 0.425
        shm.mSplitTimeBehind = 1.150

        shm.mAmbientTemperature = 22.5
        shm.mTrackTemperature = 34.0

        for i in range(TYRE_MAX):
            shm.mAirPressure[i] = 27.5
            shm.mTyreWear[i] = 0.94
            shm.mBrakeTempCelsius[i] = 420.0
            shm.mTyreTemp[i] = 85.0
            shm.mTyreTempLeft[i] = 84.0
            shm.mTyreTempCenter[i] = 86.5
            shm.mTyreTempRight[i] = 88.0

        t = 0.0
        dt = 1.0 / float(self.fps)

        try:
            while self._running:
                t += dt
                cycle = t % 12.0
                if cycle < 7.0:
                    ratio = cycle / 7.0
                    speed_kmh = 80.0 + ratio * 160.0
                    rpm = 4500.0 + (ratio * 4000.0) % 3800.0
                    gear = int(2 + ratio * 4)
                    brake_temp = 350.0 + ratio * 80.0
                    brake_input = 0.0
                    throttle_input = 0.95
                else:
                    ratio = (cycle - 7.0) / 5.0
                    speed_kmh = 240.0 - ratio * 160.0
                    rpm = 8000.0 - ratio * 3500.0
                    gear = int(6 - ratio * 4)
                    brake_temp = 430.0 + math.sin(ratio * math.pi) * 220.0
                    brake_input = 0.85
                    throttle_input = 0.0

                shm.mSpeed = speed_kmh / 3.6
                shm.mRpm = rpm
                shm.mGear = gear
                shm.mCurrentTime = 45.0 + t
                shm.mThrottle = throttle_input
                shm.mBrake = brake_input
                shm.mSequenceNumber += 2

                for i in range(TYRE_MAX):
                    shm.mBrakeTempCelsius[i] = brake_temp
                    shm.mTyreTemp[i] = 85.0 + (speed_kmh / 240.0) * 8.0

                time.sleep(dt)
        finally:
            try:
                shm.mGameState = 0
                shm.mVersion = 0
            except Exception:
                pass
            del self._shm
            self._shm = None
            if self._mm:
                try:
                    self._mm.close()
                except Exception:
                    pass
                self._mm = None


def run_mock(duration_sec: float = 30.0, fps: int = 30):
    print(f"[MOCK_AMS2] Lancement mock pendant {duration_sec}s à {fps} FPS...", flush=True)
    producer = MockAMS2Producer(fps=fps)
    producer.start()
    try:
        time.sleep(duration_sec)
    except KeyboardInterrupt:
        pass
    finally:
        producer.stop()
        print("[MOCK_AMS2] Fin de simulation et libération mémoire.", flush=True)


if __name__ == "__main__":
    dur = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
    run_mock(duration_sec=dur)
