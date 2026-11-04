"""
Lecteur de télémétrie mémoire partagée Automobilista 2 ($pcars2$) sous Windows.
Dédié au Dashboard GT3/Multi-Class et à la Sim Box Bridge.
"""

import ctypes
from ctypes import (
    Structure,
    c_bool,
    c_char,
    c_float,
    c_int,
    c_uint,
)
import mmap
import sys
import time
from typing import Dict, Any, Optional

# Constantes de dimensionnement de la mémoire partagée AMS2 / PCars2
STRING_LENGTH_MAX = 64
STORED_PARTICIPANTS_MAX = 64
TYRE_MAX = 4
VEC_MAX = 3

# Index des 4 roues
TYRE_FRONT_LEFT = 0
TYRE_FRONT_RIGHT = 1
TYRE_REAR_LEFT = 2
TYRE_REAR_RIGHT = 3

# Constantes de conversion
PSI_TO_BAR = 14.503773773

# Correspondance des rapports de vitesse
GEAR_NAMES = {
    -1: "R",
    0: "N",
}

# Windows API pour vérification de l'existence du mapping mémoire
FILE_MAP_READ = 0x0004


class ParticipantInfo(Structure):
    _pack_ = 4
    _fields_ = [
        ("mIsActive", c_bool),
        ("mName", c_char * STRING_LENGTH_MAX),
        ("mWorldPosition", c_float * VEC_MAX),
        ("mCurrentLapDistance", c_float),
        ("mRacePosition", c_uint),
        ("mLapsCompleted", c_uint),
        ("mCurrentLap", c_uint),
        ("mCurrentSector", c_int),
    ]


class AMS2SharedMemory(Structure):
    """
    Cartographie complète de la mémoire partagée '$pcars2$' (AMS2 / PCars2).
    Alignement standard MSVC 4 octets.
    """
    _pack_ = 4
    _fields_ = [
        # Version & Construction
        ("mVersion", c_uint),
        ("mBuildVersionNumber", c_uint),

        # États du Jeu & Session
        ("mGameState", c_uint),      # 0=EXITED, 1=FRONT_END, 2=INGAME_PLAYING, 3=PAUSED, etc.
        ("mSessionState", c_uint),  # 0=INVALID, 1=PRACTICE, 2=TEST, 3=QUALIFY, 4=FORMATION, 5=RACE, etc.
        ("mRaceState", c_uint),     # 0=INVALID, 1=NOT_STARTED, 2=RACING, 3=FINISHED, etc.

        # Participants
        ("mViewedParticipantIndex", c_int),
        ("mNumParticipants", c_int),
        ("mParticipantInfo", ParticipantInfo * STORED_PARTICIPANTS_MAX),

        # Entrées Pilote Brutes (Unfiltered)
        ("mUnfilteredThrottle", c_float),
        ("mUnfilteredBrake", c_float),
        ("mUnfilteredSteering", c_float),
        ("mUnfilteredClutch", c_float),

        # Informations Véhicule & Circuit
        ("mCarName", c_char * STRING_LENGTH_MAX),
        ("mCarClassName", c_char * STRING_LENGTH_MAX),
        ("mLapsInEvent", c_uint),
        ("mTrackLocation", c_char * STRING_LENGTH_MAX),
        ("mTrackVariation", c_char * STRING_LENGTH_MAX),
        ("mTrackLength", c_float),

        # Chronométrage & Secteurs
        ("mNumSectors", c_int),
        ("mLapInvalidated", c_bool),
        ("mBestLapTime", c_float),
        ("mLastLapTime", c_float),
        ("mCurrentTime", c_float),
        ("mSplitTimeAhead", c_float),
        ("mSplitTimeBehind", c_float),
        ("mSplitTime", c_float),
        ("mEventTimeRemaining", c_float),
        ("mPersonalFastestLapTime", c_float),
        ("mWorldFastestLapTime", c_float),
        ("mPersonalFastestSector1Time", c_float),
        ("mPersonalFastestSector2Time", c_float),
        ("mPersonalFastestSector3Time", c_float),
        ("mWorldFastestSector1Time", c_float),
        ("mWorldFastestSector2Time", c_float),
        ("mWorldFastestSector3Time", c_float),

        # Drapeaux & Arrêts aux stands
        ("mHighestFlagColour", c_uint),
        ("mHighestFlagReason", c_uint),
        ("mPitMode", c_uint),
        ("mPitSchedule", c_uint),

        # État Moteur & Fluides
        ("mCarFlags", c_uint),
        ("mOilTempCelsius", c_float),
        ("mOilPressureKPa", c_float),
        ("mWaterTempCelsius", c_float),
        ("mWaterPressureKPa", c_float),
        ("mFuelPressureKPa", c_float),
        ("mFuelLevel", c_float),       # Ratio 0.0 -> 1.0
        ("mFuelCapacity", c_float),    # Litres
        ("mSpeed", c_float),           # m/s
        ("mRpm", c_float),
        ("mMaxRPM", c_float),
        ("mBrake", c_float),
        ("mThrottle", c_float),
        ("mClutch", c_float),
        ("mSteering", c_float),
        ("mGear", c_int),              # -1=R, 0=N, 1..n
        ("mNumGears", c_int),
        ("mOdometerKM", c_float),
        ("mAntiLockActive", c_bool),
        ("mLastOpponentCollisionIndex", c_int),
        ("mLastOpponentCollisionMagnitude", c_float),
        ("mBoostActive", c_bool),
        ("mBoostAmount", c_float),

        # Vecteurs Mouvement & Dynamique
        ("mOrientation", c_float * VEC_MAX),
        ("mLocalVelocity", c_float * VEC_MAX),
        ("mWorldVelocity", c_float * VEC_MAX),
        ("mAngularVelocity", c_float * VEC_MAX),
        ("mLocalAcceleration", c_float * VEC_MAX),
        ("mWorldAcceleration", c_float * VEC_MAX),
        ("mExtentsCentre", c_float * VEC_MAX),

        # Roues & Pneus (Physique de base)
        ("mTyreFlags", c_uint * TYRE_MAX),
        ("mTerrain", c_uint * TYRE_MAX),
        ("mTyreY", c_float * TYRE_MAX),
        ("mTyreRPS", c_float * TYRE_MAX),
        ("mTyreSlipSpeed", c_float * TYRE_MAX),
        ("mTyreGrip", c_float * TYRE_MAX),
        ("mTyreHeightAboveGround", c_float * TYRE_MAX),
        ("mTyreLateralStiffness", c_float * TYRE_MAX),
        ("mTyreWear", c_float * TYRE_MAX),                 # Ratio 0.0 -> 1.0
        ("mBrakeDamage", c_float * TYRE_MAX),
        ("mSuspensionDamage", c_float * TYRE_MAX),
        ("mBrakeTempCelsius", c_float * TYRE_MAX),         # °C
        ("mTyreTemp", c_float * TYRE_MAX),                 # °C
        ("mTyreLayer", c_float * TYRE_MAX),
        ("mTyreCarcassTemp", c_float * TYRE_MAX),
        ("mTyreRimTemp", c_float * TYRE_MAX),
        ("mTyreInternalAirTemp", c_float * TYRE_MAX),
        ("mWheelLocalPositionY", c_float * TYRE_MAX),
        ("mSuspensionTravel", c_float * TYRE_MAX),
        ("mSuspensionVelocity", c_float * TYRE_MAX),
        ("mAirPressure", c_float * TYRE_MAX),              # PSI

        # Aérodynamique & Entrées Pilote Étendues
        ("mEngineSpeed", c_float),
        ("mEngineTorque", c_float),
        ("mWings", c_float * 2),
        ("mHandBrake", c_float),

        # Météo & Environnement
        ("mAmbientTemperature", c_float),
        ("mTrackTemperature", c_float),
        ("mRainDensity", c_float),
        ("mWindSpeed", c_float),
        ("mWindDirectionX", c_float),
        ("mWindDirectionY", c_float),
        ("mCloudBrightness", c_float),

        # Extensions AMS2 v10+ (Session & Températures 3 zones bande de roulement)
        ("mSessionDuration", c_float),
        ("mSessionAdditionalLaps", c_int),
        ("mTyreTempLeft", c_float * TYRE_MAX),             # °C
        ("mTyreTempCenter", c_float * TYRE_MAX),           # °C
        ("mTyreTempRight", c_float * TYRE_MAX),            # °C
        ("mDrsState", c_uint),
    ]


def format_lap_time(seconds: float) -> str:
    """Formate un temps en secondes sous forme 'M:SS.mmm'."""
    if seconds <= 0.0:
        return "--:--.---"
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins}:{secs:06.3f}"


class Automobilista2Reader:
    """
    Lecteur résilient de télémétrie Windows Shared Memory pour Automobilista 2.
    """
    SHM_NAME = "$pcars2$"

    def __init__(self):
        self.mmap_shm: Optional[mmap.mmap] = None
        self.struct_size = ctypes.sizeof(AMS2SharedMemory)
        self._last_time: float = -1.0
        self._last_change_ts: float = time.time()

    def _shared_memory_exists(self) -> bool:
        """Vérifie si le bloc de mémoire partagée a réellement été alloué par le jeu."""
        if sys.platform != "win32":
            return False
        try:
            h = ctypes.windll.kernel32.OpenFileMappingW(FILE_MAP_READ, False, self.SHM_NAME)
            if h:
                ctypes.windll.kernel32.CloseHandle(h)
                return True
        except Exception:
            pass
        return False

    def _open(self) -> bool:
        if sys.platform != "win32":
            return False

        if not self._shared_memory_exists():
            self.close()
            return False

        if self.mmap_shm is not None:
            return True

        for fileno in (-1, 0):
            try:
                self.mmap_shm = mmap.mmap(
                    fileno,
                    self.struct_size,
                    tagname=self.SHM_NAME,
                    access=mmap.ACCESS_READ
                )
                self._last_time = -1.0
                self._last_change_ts = time.time()
                return True
            except Exception:
                pass
        return False

    def read(self) -> Dict[str, Any]:
        """
        Lit et extrait les données de télémétrie normalisées.
        Retourne un dictionnaire avec 'connected': True et les valeurs, ou {'connected': False, 'in_game': False}.
        """
        if not self._open():
            return {"connected": False, "sim": "AMS2", "in_game": False}

        try:
            shm = AMS2SharedMemory.from_buffer_copy(self.mmap_shm)

            # mGameState : 0=EXITED, 1=FRONT_END (menus), 2=INGAME_PLAYING, 3=PAUSED, 6=REPLAY
            in_game = (shm.mGameState == 2)
            is_paused = (shm.mGameState == 3)

            # Si le jeu vient d'être quitté ou réinitialisé
            if shm.mGameState == 0 or shm.mVersion == 0:
                self.close()
                return {
                    "connected": False,
                    "sim": "AMS2",
                    "in_game": False,
                    "status": int(shm.mGameState)
                }

            # Détection de heartbeat (si le jeu est mort ou figé en mode course)
            current_time_val = float(shm.mCurrentTime)
            now = time.time()
            if in_game:
                if abs(current_time_val - self._last_time) > 0.0001:
                    self._last_time = current_time_val
                    self._last_change_ts = now
                elif (now - self._last_change_ts) > 2.5:
                    # Plus de mise à jour depuis plus de 2.5s : simulation interrompue
                    self.close()
                    return {"connected": False, "sim": "AMS2", "in_game": False}

            # Conversion de la vitesse m/s -> km/h
            speed_kmh = round(float(shm.mSpeed) * 3.6, 1) if shm.mSpeed > 0 else 0.0

            # Rapport engagé
            gear = int(shm.mGear)
            gear_str = GEAR_NAMES.get(gear, str(gear) if gear > 0 else "N")

            # Pressions pneus (PSI -> bar)
            pressures = [
                round(float(p) / PSI_TO_BAR, 2) if p > 0 else 0.0
                for p in shm.mAirPressure
            ]

            # Températures pneus moyennes / centrales (°C)
            temps = [
                round(float(t), 1) if t > 0 else 0.0
                for t in shm.mTyreTemp
            ]

            # Températures 3 zones par pneu (Intérieur, Centre, Extérieur)
            tyre_thermal_3zones = []
            for i in range(TYRE_MAX):
                t_l = round(float(shm.mTyreTempLeft[i]), 1)
                t_c = round(float(shm.mTyreTempCenter[i]), 1)
                t_r = round(float(shm.mTyreTempRight[i]), 1)

                if t_c <= 0.0 and temps[i] > 0.0:
                    t_l = t_c = t_r = temps[i]

                if i in (TYRE_FRONT_LEFT, TYRE_REAR_LEFT):
                    inside, middle, outside = t_r, t_c, t_l
                else:
                    inside, middle, outside = t_l, t_c, t_r

                tyre_thermal_3zones.append({
                    "inside": inside,
                    "middle": middle,
                    "outside": outside
                })

            # Températures disques de freins (°C)
            brakes = [
                round(float(b), 1) if b > 0 else 0.0
                for b in shm.mBrakeTempCelsius
            ]

            # Usure résiduelle des pneus (% restante)
            tyre_wear = [
                round(float(w) * 100.0, 1) if w > 0 else 100.0
                for w in shm.mTyreWear
            ]

            # Carburant
            max_fuel = round(float(shm.mFuelCapacity), 1) if shm.mFuelCapacity > 0 else 100.0
            fuel_level = round(float(shm.mFuelLevel) * max_fuel, 1)

            # Chronométrage
            current_time_sec = float(shm.mCurrentTime)
            best_lap_sec = float(shm.mBestLapTime)
            last_lap_sec = float(shm.mLastLapTime)

            split_ahead = round(float(shm.mSplitTimeAhead), 3) if shm.mSplitTimeAhead != -1.0 else 0.0
            split_behind = round(float(shm.mSplitTimeBehind), 3) if shm.mSplitTimeBehind != -1.0 else 0.0

            car_name = shm.mCarName.decode("utf-8", errors="ignore").strip("\x00").strip()
            track_location = shm.mTrackLocation.decode("utf-8", errors="ignore").strip("\x00").strip()

            completed_laps = 0
            position = 1
            idx = int(shm.mViewedParticipantIndex)
            if 0 <= idx < STORED_PARTICIPANTS_MAX:
                p_info = shm.mParticipantInfo[idx]
                if p_info.mIsActive:
                    completed_laps = int(p_info.mLapsCompleted)
                    position = int(p_info.mRacePosition)

            max_rpm = int(shm.mMaxRPM) if shm.mMaxRPM > 0 else 8500

            return {
                "connected": True,
                "sim": "AMS2",
                "in_game": in_game,
                "is_paused": is_paused,
                "gameState": int(shm.mGameState),
                "speedKmh": speed_kmh,
                "gear": gear,
                "gearStr": gear_str,
                "rpms": int(shm.mRpm) if shm.mRpm > 0 else 0,
                "maxRpm": max_rpm,
                "fuel": fuel_level,
                "maxFuel": max_fuel,
                "wheelsPressure": pressures,
                "tyreCoreTemperature": temps,
                "tyreThermal3Zones": tyre_thermal_3zones,
                "tyreWear": tyre_wear,
                "brakeTemp": brakes,
                "airTemp": round(float(shm.mAmbientTemperature), 1),
                "roadTemp": round(float(shm.mTrackTemperature), 1),
                "currentTime": format_lap_time(current_time_sec),
                "bestLapTime": format_lap_time(best_lap_sec),
                "lastLapTime": format_lap_time(last_lap_sec),
                "splitTimeAhead": split_ahead,
                "splitTimeBehind": split_behind,
                "completedLaps": completed_laps,
                "numberOfLaps": int(shm.mLapsInEvent),
                "position": position,
                "abs": 1 if shm.mAntiLockActive else 0,
                "tc": 0,
                "drs": int(shm.mDrsState),
                "carName": car_name,
                "trackName": track_location,
            }
        except Exception:
            self.close()
            return {"connected": False, "sim": "AMS2", "in_game": False}

    def close(self):
        if self.mmap_shm is not None:
            try:
                self.mmap_shm.close()
            except Exception:
                pass
            self.mmap_shm = None
        self._last_time = -1.0


_ams2_reader_instance: Optional[Automobilista2Reader] = None


def get_ams2_reader() -> Automobilista2Reader:
    global _ams2_reader_instance
    if _ams2_reader_instance is None:
        _ams2_reader_instance = Automobilista2Reader()
    return _ams2_reader_instance
