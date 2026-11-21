"""
Lecteur de télémétrie mémoire partagée Automobilista 2 ($pcars2$) sous Windows.
Alignement bit-à-bit 100% conforme à l'en-tête officiel Reiza Studios SharedMemory.h.
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
SHARED_MEMORY_VERSION = 14
STRING_LENGTH_MAX = 64
STORED_PARTICIPANTS_MAX = 64
TYRE_COMPOUND_NAME_LENGTH_MAX = 40
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
if sys.platform == "win32":
    from ctypes import wintypes
    _kernel32 = ctypes.windll.kernel32
    _kernel32.OpenFileMappingW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    _kernel32.OpenFileMappingW.restype = wintypes.HANDLE
    _kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    _kernel32.CloseHandle.restype = wintypes.BOOL


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
    Alignement standard MSVC 4 octets conforme à SharedMemory.h (20700 octets).
    """
    _pack_ = 4
    _fields_ = [
        ("mVersion", c_uint),  # [ RANGE = 0->... ]
        ("mBuildVersionNumber", c_uint),  # [ RANGE = 0->... ]   [ UNSET = 0 ]
        ("mGameState", c_uint),  # [ enum (Type#1) Game state ]
        ("mSessionState", c_uint),  # [ enum (Type#2) Session state ]
        ("mRaceState", c_uint),  # [ enum (Type#3) Race State ]
        ("mViewedParticipantIndex", c_int),  # [ RANGE = 0->STORED_PARTICIPANTS_MAX ]   [ UNSET = -1 ]
        ("mNumParticipants", c_int),  # [ RANGE = 0->STORED_PARTICIPANTS_MAX ]   [ UNSET = -1 ]
        ("mParticipantInfo", ParticipantInfo * STORED_PARTICIPANTS_MAX),  # [ struct (Type#13) ParticipantInfo struct ]
        ("mUnfilteredThrottle", c_float),  # [ RANGE = 0.0f->1.0f ]
        ("mUnfilteredBrake", c_float),  # [ RANGE = 0.0f->1.0f ]
        ("mUnfilteredSteering", c_float),  # [ RANGE = -1.0f->1.0f ]
        ("mUnfilteredClutch", c_float),  # [ RANGE = 0.0f->1.0f ]
        ("mCarName", c_char * STRING_LENGTH_MAX),  # [ string ]
        ("mCarClassName", c_char * STRING_LENGTH_MAX),  # [ string ]
        ("mLapsInEvent", c_uint),  # [ RANGE = 0->... ]   [ UNSET = 0 ]
        ("mTrackLocation", c_char * STRING_LENGTH_MAX),  # [ string ] - untranslated shortened English name
        ("mTrackVariation", c_char * STRING_LENGTH_MAX),  # [ string ]- untranslated shortened English variation description
        ("mTrackLength", c_float),  # [ UNITS = Metres ]   [ RANGE = 0.0f->... ]    [ UNSET = 0.0f ]
        ("mNumSectors", c_int),  # [ RANGE = 0->... ]   [ UNSET = -1 ]
        ("mLapInvalidated", c_bool),  # [ UNITS = boolean ]   [ RANGE = false->true ]   [ UNSET = false ]
        ("mBestLapTime", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mLastLapTime", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = 0.0f ]
        ("mCurrentTime", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = 0.0f ]
        ("mSplitTimeAhead", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mSplitTimeBehind", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mSplitTime", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = 0.0f ]
        ("mEventTimeRemaining", c_float),  # [ UNITS = milli-seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mPersonalFastestLapTime", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mWorldFastestLapTime", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mCurrentSector1Time", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mCurrentSector2Time", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mCurrentSector3Time", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mFastestSector1Time", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mFastestSector2Time", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mFastestSector3Time", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mPersonalFastestSector1Time", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mPersonalFastestSector2Time", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mPersonalFastestSector3Time", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mWorldFastestSector1Time", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mWorldFastestSector2Time", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mWorldFastestSector3Time", c_float),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mHighestFlagColour", c_uint),  # [ enum (Type#5) Flag Colour ]
        ("mHighestFlagReason", c_uint),  # [ enum (Type#6) Flag Reason ]
        ("mPitMode", c_uint),  # [ enum (Type#7) Pit Mode ]
        ("mPitSchedule", c_uint),  # [ enum (Type#8) Pit Stop Schedule ]
        ("mCarFlags", c_uint),  # [ enum (Type#9) Car Flags ]
        ("mOilTempCelsius", c_float),  # [ UNITS = Celsius ]   [ UNSET = 0.0f ]
        ("mOilPressureKPa", c_float),  # [ UNITS = Kilopascal ]   [ RANGE = 0.0f->... ]   [ UNSET = 0.0f ]
        ("mWaterTempCelsius", c_float),  # [ UNITS = Celsius ]   [ UNSET = 0.0f ]
        ("mWaterPressureKPa", c_float),  # [ UNITS = Kilopascal ]   [ RANGE = 0.0f->... ]   [ UNSET = 0.0f ]
        ("mFuelPressureKPa", c_float),  # [ UNITS = Kilopascal ]   [ RANGE = 0.0f->... ]   [ UNSET = 0.0f ]
        ("mFuelLevel", c_float),  # [ RANGE = 0.0f->1.0f ]
        ("mFuelCapacity", c_float),  # [ UNITS = Liters ]   [ RANGE = 0.0f->1.0f ]   [ UNSET = 0.0f ]
        ("mSpeed", c_float),  # [ UNITS = Metres per-second ]   [ RANGE = 0.0f->... ]
        ("mRpm", c_float),  # [ UNITS = Revolutions per minute ]   [ RANGE = 0.0f->... ]   [ UNSET = 0.0f ]
        ("mMaxRPM", c_float),  # [ UNITS = Revolutions per minute ]   [ RANGE = 0.0f->... ]   [ UNSET = 0.0f ]
        ("mBrake", c_float),  # [ RANGE = 0.0f->1.0f ]
        ("mThrottle", c_float),  # [ RANGE = 0.0f->1.0f ]
        ("mClutch", c_float),  # [ RANGE = 0.0f->1.0f ]
        ("mSteering", c_float),  # [ RANGE = -1.0f->1.0f ]
        ("mGear", c_int),  # [ RANGE = -1 (Reverse)  0 (Neutral)  1 (Gear 1)  2 (Gear 2)  etc... ]   [ UNSET = 0 (Neutral) ]
        ("mNumGears", c_int),  # [ RANGE = 0->... ]   [ UNSET = -1 ]
        ("mOdometerKM", c_float),  # [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mAntiLockActive", c_bool),  # [ UNITS = boolean ]   [ RANGE = false->true ]   [ UNSET = false ]
        ("mLastOpponentCollisionIndex", c_int),  # [ RANGE = 0->STORED_PARTICIPANTS_MAX ]   [ UNSET = -1 ]
        ("mLastOpponentCollisionMagnitude", c_float),  # [ RANGE = 0.0f->... ]
        ("mBoostActive", c_bool),  # [ UNITS = boolean ]   [ RANGE = false->true ]   [ UNSET = false ]
        ("mBoostAmount", c_float),  # [ RANGE = 0.0f->100.0f ]
        ("mOrientation", c_float * VEC_MAX),  # [ UNITS = Euler Angles ]
        ("mLocalVelocity", c_float * VEC_MAX),  # [ UNITS = Metres per-second ]
        ("mWorldVelocity", c_float * VEC_MAX),  # [ UNITS = Metres per-second ]
        ("mAngularVelocity", c_float * VEC_MAX),  # [ UNITS = Radians per-second ]
        ("mLocalAcceleration", c_float * VEC_MAX),  # [ UNITS = Metres per-second ]
        ("mWorldAcceleration", c_float * VEC_MAX),  # [ UNITS = Metres per-second ]
        ("mExtentsCentre", c_float * VEC_MAX),  # [ UNITS = Local Space  X  Y  Z ]
        ("mTyreFlags", c_uint * TYRE_MAX),  # [ enum (Type#10) Tyre Flags ]
        ("mTerrain", c_uint * TYRE_MAX),  # [ enum (Type#11) Terrain Materials ]
        ("mTyreY", c_float * TYRE_MAX),  # [ UNITS = Local Space  Y ]
        ("mTyreRPS", c_float * TYRE_MAX),  # [ UNITS = Revolutions per second ]
        ("mTyreSlipSpeed", c_float * TYRE_MAX),  # OBSOLETE, kept for backward compatibility only
        ("mTyreTemp", c_float * TYRE_MAX),  # [ UNITS = Celsius ]   [ UNSET = 0.0f ]
        ("mTyreGrip", c_float * TYRE_MAX),  # OBSOLETE, kept for backward compatibility only
        ("mTyreHeightAboveGround", c_float * TYRE_MAX),  # [ UNITS = Local Space  Y ]
        ("mTyreLateralStiffness", c_float * TYRE_MAX),  # OBSOLETE, kept for backward compatibility only
        ("mTyreWear", c_float * TYRE_MAX),  # [ RANGE = 0.0f->1.0f ]
        ("mBrakeDamage", c_float * TYRE_MAX),  # [ RANGE = 0.0f->1.0f ]
        ("mSuspensionDamage", c_float * TYRE_MAX),  # [ RANGE = 0.0f->1.0f ]
        ("mBrakeTempCelsius", c_float * TYRE_MAX),  # [ UNITS = Celsius ]
        ("mTyreTreadTemp", c_float * TYRE_MAX),  # [ UNITS = Kelvin ]
        ("mTyreLayerTemp", c_float * TYRE_MAX),  # [ UNITS = Kelvin ]
        ("mTyreCarcassTemp", c_float * TYRE_MAX),  # [ UNITS = Kelvin ]
        ("mTyreRimTemp", c_float * TYRE_MAX),  # [ UNITS = Kelvin ]
        ("mTyreInternalAirTemp", c_float * TYRE_MAX),  # [ UNITS = Kelvin ]
        ("mCrashState", c_uint),  # [ enum (Type#12) Crash Damage State ]
        ("mAeroDamage", c_float),  # [ RANGE = 0.0f->1.0f ]
        ("mEngineDamage", c_float),  # [ RANGE = 0.0f->1.0f ]
        ("mAmbientTemperature", c_float),  # [ UNITS = Celsius ]   [ UNSET = 25.0f ]
        ("mTrackTemperature", c_float),  # [ UNITS = Celsius ]   [ UNSET = 30.0f ]
        ("mRainDensity", c_float),  # [ UNITS = How much rain will fall ]   [ RANGE = 0.0f->1.0f ]
        ("mWindSpeed", c_float),  # [ RANGE = 0.0f->100.0f ]   [ UNSET = 2.0f ]
        ("mWindDirectionX", c_float),  # [ UNITS = Normalised Vector X ]
        ("mWindDirectionY", c_float),  # [ UNITS = Normalised Vector Y ]
        ("mCloudBrightness", c_float),  # [ RANGE = 0.0f->... ]
        ("mSequenceNumber", c_uint),  # 0 at the start, incremented at start and end of writing, so odd when Shared Memory is being filled, even when the memory is not being touched
        ("mWheelLocalPositionY", c_float * TYRE_MAX),  # [ UNITS = Local Space  Y ]
        ("mSuspensionTravel", c_float * TYRE_MAX),  # [ UNITS = meters ] [ RANGE 0.f =>... ]  [ UNSET =  0.0f ]
        ("mSuspensionVelocity", c_float * TYRE_MAX),  # [ UNITS = Rate of change of pushrod deflection ] [ RANGE 0.f =>... ]  [ UNSET =  0.0f ]
        ("mAirPressure", c_float * TYRE_MAX),  # [ UNITS = PSI ]  [ RANGE 0.f =>... ]  [ UNSET =  0.0f ]
        ("mEngineSpeed", c_float),  # [ UNITS = Rad/s ] [UNSET = 0.f ]
        ("mEngineTorque", c_float),  # [ UNITS = Newton Meters] [UNSET = 0.f ] [ RANGE = 0.0f->... ]
        ("mWings", c_float * 2),  # [ RANGE = 0.0f->1.0f ] [UNSET = 0.f ]
        ("mHandBrake", c_float),  # [ RANGE = 0.0f->1.0f ] [UNSET = 0.f ]
        ("mCurrentSector1Times", c_float * STORED_PARTICIPANTS_MAX),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mCurrentSector2Times", c_float * STORED_PARTICIPANTS_MAX),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mCurrentSector3Times", c_float * STORED_PARTICIPANTS_MAX),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mFastestSector1Times", c_float * STORED_PARTICIPANTS_MAX),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mFastestSector2Times", c_float * STORED_PARTICIPANTS_MAX),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mFastestSector3Times", c_float * STORED_PARTICIPANTS_MAX),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mFastestLapTimes", c_float * STORED_PARTICIPANTS_MAX),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mLastLapTimes", c_float * STORED_PARTICIPANTS_MAX),  # [ UNITS = seconds ]   [ RANGE = 0.0f->... ]   [ UNSET = -1.0f ]
        ("mLapsInvalidated", c_bool * STORED_PARTICIPANTS_MAX),  # [ UNITS = boolean for all participants ]   [ RANGE = false->true ]   [ UNSET = false ]
        ("mRaceStates", c_uint * STORED_PARTICIPANTS_MAX),  # [ enum (Type#3) Race State ]
        ("mPitModes", c_uint * STORED_PARTICIPANTS_MAX),  # [ enum (Type#7)  Pit Mode ]
        ("mOrientations", (c_float * VEC_MAX) * STORED_PARTICIPANTS_MAX),  # [ UNITS = Euler Angles ]
        ("mSpeeds", c_float * STORED_PARTICIPANTS_MAX),  # [ UNITS = Metres per-second ]   [ RANGE = 0.0f->... ]
        ("mCarNames", (c_char * STRING_LENGTH_MAX) * STORED_PARTICIPANTS_MAX),  # [ string ]
        ("mCarClassNames", (c_char * STRING_LENGTH_MAX) * STORED_PARTICIPANTS_MAX),  # [ string ]
        ("mEnforcedPitStopLap", c_int),  # [ UNITS = in which lap there will be a mandatory pitstop] [ RANGE = 0.0f->... ] [ UNSET = -1 ]
        ("mTranslatedTrackLocation", c_char * STRING_LENGTH_MAX),  # [ string ]
        ("mTranslatedTrackVariation", c_char * STRING_LENGTH_MAX),  # [ string ]
        ("mBrakeBias", c_float),  # [ RANGE = 0.0f->1.0f... ]   [ UNSET = -1.0f ]
        ("mTurboBoostPressure", c_float),  # RANGE = 0.0f->1.0f... ]   [ UNSET = -1.0f ]
        ("mTyreCompound", (c_char * TYRE_COMPOUND_NAME_LENGTH_MAX) * TYRE_MAX),  # [ strings  ]
        ("mPitSchedules", c_uint * STORED_PARTICIPANTS_MAX),  # [ enum (Type#7)  Pit Mode ]
        ("mHighestFlagColours", c_uint * STORED_PARTICIPANTS_MAX),  # [ enum (Type#5) Flag Colour ]
        ("mHighestFlagReasons", c_uint * STORED_PARTICIPANTS_MAX),  # [ enum (Type#6) Flag Reason ]
        ("mNationalities", c_uint * STORED_PARTICIPANTS_MAX),  # [ nationality table , SP AND UNSET = 0 ]
        ("mSnowDensity", c_float),  # [ UNITS = How much snow will fall ]   [ RANGE = 0.0f->1.0f ], this is non zero only in Winter and Snow seasons
        ("mSessionDuration", c_float),  # [ UNITS = minutes ]   [ UNSET = 0.0f ]  The scheduled session Length (unset means laps race. See mLapsInEvent)
        ("mSessionAdditionalLaps", c_int),  # The number of additional complete laps lead lap drivers must complete to finish a timed race after the session duration has elapsed.
        ("mTyreTempLeft", c_float * TYRE_MAX),  # [ UNITS = Celsius ]   [ UNSET = 0.0f ]
        ("mTyreTempCenter", c_float * TYRE_MAX),  # [ UNITS = Celsius ]   [ UNSET = 0.0f ]
        ("mTyreTempRight", c_float * TYRE_MAX),  # [ UNITS = Celsius ]   [ UNSET = 0.0f ]
        ("mDrsState", c_uint),  # [ enum (Type#14) DrsState ]
        ("mRideHeight", c_float * TYRE_MAX),  # [ UNITS = cm ]
        ("mJoyPad0", c_uint),  # button mask
        ("mDPad", c_uint),  # button mask
        ("mAntiLockSetting", c_int),  # [ UNSET = -1 ] Current ABS garage setting. Valid under player control only.
        ("mTractionControlSetting", c_int),  # [ UNSET = -1 ] Current ABS garage setting. Valid under player control only.
        ("mErsDeploymentMode", c_int),  # [ enum (Type#15)  ErsDeploymentMode ]
        ("mErsAutoModeEnabled", c_bool),  # true if the deployment mode was selected by auto system. Valid only when mErsDeploymentMode > ERS_DEPLOYMENT_MODE_NONE
        ("mClutchTemp", c_float),  # [ UNITS = Kelvin ] [ UNSET = -273.16 ]
        ("mClutchWear", c_float),  # [ RANGE = 0.0f->1.0f... ]
        ("mClutchOverheated", c_bool),  # true if clutch performance is degraded due to overheating
        ("mClutchSlipping", c_bool),  # true if clutch is slipping (can be induced by overheating or wear)
        ("mYellowFlagState", c_int),  # [ enum (Type#16) YellowFlagState ]
        ("mSessionIsPrivate", c_bool),  # true if this is a private session where users cannot see or interact with other drivers (and so would not need positional awareness of them etc)
        ("mLaunchStage", c_int),  # [ enum (Type#17) LaunchStage
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
        self._last_signature: Optional[tuple] = None
        self._last_change_ts: float = time.time()

    def _shared_memory_exists(self) -> bool:
        """Vérifie si le bloc de mémoire partagée a réellement été alloué par le jeu."""
        if sys.platform != "win32":
            return False
        try:
            h = _kernel32.OpenFileMappingW(FILE_MAP_READ, False, self.SHM_NAME)
            if h:
                _kernel32.CloseHandle(h)
                return True
        except Exception:
            pass
        return False

    def _open(self) -> bool:
        if sys.platform != "win32":
            return False

        if self.mmap_shm is not None:
            return True

        if not self._shared_memory_exists():
            self.close()
            return False

        for fileno in (-1, 0):
            try:
                self.mmap_shm = mmap.mmap(
                    fileno,
                    self.struct_size,
                    tagname=self.SHM_NAME,
                    access=mmap.ACCESS_READ
                )
                self._last_signature = None
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
            seq_offset = AMS2SharedMemory.mSequenceNumber.offset
            shm = None
            for attempt in range(5):
                seq_before = c_uint.from_buffer_copy(self.mmap_shm, seq_offset).value
                if seq_before & 1:
                    if attempt < 4:
                        time.sleep(0.0002)
                    continue
                candidate = AMS2SharedMemory.from_buffer_copy(self.mmap_shm)
                seq_after = c_uint.from_buffer_copy(self.mmap_shm, seq_offset).value
                if seq_before == seq_after and (seq_before & 1) == 0 and candidate.mSequenceNumber == seq_before:
                    shm = candidate
                    break
                if attempt < 4:
                    time.sleep(0.0002)

            if shm is None:
                return {"connected": False, "sim": "AMS2", "in_game": False}

            # mGameState : 0=EXITED, 1=FRONT_END, 2=INGAME_PLAYING, 3=PAUSED, 4=INMENU, 5=RESTARTING, 6=REPLAY
            in_game = (shm.mGameState in (2, 3, 4, 5, 6))
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

            # Détection de heartbeat basée sur mSequenceNumber + variables physiques
            # (évite toute coupure lors des tours de sortie des stands où mCurrentTime reste à -1.0)
            now = time.time()
            sig = (
                int(shm.mSequenceNumber),
                int(shm.mGameState),
                round(float(shm.mCurrentTime), 3),
                round(float(shm.mRpm), 1),
                round(float(shm.mSpeed), 2),
                round(float(shm.mUnfilteredSteering), 3),
            )
            if sig != self._last_signature:
                self._last_signature = sig
                self._last_change_ts = now
            elif shm.mGameState == 2 and (now - self._last_change_ts) > 10.0:
                # Si plus aucune trame ni micro-variation pendant 10s en plein roulage (crash du jeu)
                self.close()
                return {"connected": False, "sim": "AMS2", "in_game": False}

            # Conversion de la vitesse m/s -> km/h
            speed_kmh = round(float(shm.mSpeed) * 3.6, 1) if shm.mSpeed > 0 else 0.0

            # Rapport engagé sécurisé (-1=R, 0=N, 1..10)
            raw_gear = int(shm.mGear)
            if -1 <= raw_gear <= 10:
                gear = raw_gear
                gear_str = GEAR_NAMES.get(gear, str(gear))
            else:
                gear = 0
                gear_str = "N"

            # Régimes moteurs (RPM & MaxRPM avec fallback mEngineSpeed rad/s)
            rpms = int(round(float(shm.mRpm))) if shm.mRpm > 0 else 0
            if rpms == 0 and shm.mEngineSpeed > 0:
                rpms = int(round(float(shm.mEngineSpeed) * 9.5492966))
            max_rpm = int(round(float(shm.mMaxRPM))) if shm.mMaxRPM > 1000 else 8500
            if rpms > max_rpm:
                max_rpm = rpms

            # Carburant (mFuelCapacity en litres, mFuelLevel en ratio 0.0->1.0)
            max_fuel = round(float(shm.mFuelCapacity), 1) if shm.mFuelCapacity > 0 else 100.0
            fuel_level = round(float(shm.mFuelLevel) * max_fuel, 1) if shm.mFuelLevel > 0 else 0.0

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

            # Usure résiduelle des pneus (mTyreWear: 0.0=neuf -> 1.0=usé, converti en % de vie restante)
            tyre_wear = [
                round(max(0.0, min(1.0, 1.0 - float(w))) * 100.0, 1)
                for w in shm.mTyreWear
            ]

            # Chronométrage
            current_time_sec = float(shm.mCurrentTime)
            best_lap_sec = float(shm.mBestLapTime)
            last_lap_sec = float(shm.mLastLapTime)

            split_ahead = round(float(shm.mSplitTimeAhead), 3) if shm.mSplitTimeAhead != -1.0 else 0.0
            split_behind = round(float(shm.mSplitTimeBehind), 3) if shm.mSplitTimeBehind != -1.0 else 0.0
            split_delta = round(float(shm.mSplitTime), 2) if shm.mSplitTime != 0.0 else 0.0

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

            # DRS : 2 = actif, 1 = disponible, 0 = inactif
            drs_state = int(shm.mDrsState)
            if drs_state & (1 << 4):
                drs_val = 2
            elif drs_state & ((1 << 2) | (1 << 3)):
                drs_val = 1
            else:
                drs_val = 0

            # Répartition de freinage (Brake Bias %)
            raw_bias = float(shm.mBrakeBias)
            if raw_bias > 0:
                brake_bias = round(raw_bias * 100.0 if raw_bias <= 1.0 else raw_bias, 1)
            else:
                brake_bias = 0.0

            # Réglages d'aides ABS & TC
            if shm.mAntiLockSetting >= 0:
                abs_val = int(shm.mAntiLockSetting)
            elif shm.mAntiLockActive or (shm.mCarFlags & 0x10):
                abs_val = 1
            else:
                abs_val = 0

            if shm.mTractionControlSetting >= 0:
                tc_val = int(shm.mTractionControlSetting)
            elif shm.mCarFlags & 0x40:
                tc_val = 1
            else:
                tc_val = 0

            # ERS / Boost (mBoostAmount: 0.0->100.0)
            ers_level = round(max(0.0, min(100.0, float(shm.mBoostAmount))), 1)
            boost_active = bool(shm.mBoostActive)
            ers_deployment_mode = int(shm.mErsDeploymentMode)

            # Durée de session (minutes) et temps restant (secondes) pour les courses chronométrées
            raw_time_remaining = float(shm.mEventTimeRemaining)
            event_time_remaining = round(raw_time_remaining / 1000.0, 1) if raw_time_remaining >= 0.0 else -1.0
            raw_session_duration = float(shm.mSessionDuration)
            session_duration = round(raw_session_duration, 1) if raw_session_duration > 0.0 else 0.0

            # Pédales et direction (filtrées avec fallback non-filtrées)
            throttle = round(float(shm.mThrottle), 3) if shm.mThrottle > 0 else round(float(shm.mUnfilteredThrottle), 3)
            brake = round(float(shm.mBrake), 3) if shm.mBrake > 0 else round(float(shm.mUnfilteredBrake), 3)
            clutch = round(float(shm.mClutch), 3) if shm.mClutch > 0 else round(float(shm.mUnfilteredClutch), 3)
            steering = round(float(shm.mSteering), 3) if abs(shm.mSteering) > 0.001 else round(float(shm.mUnfilteredSteering), 3)

            return {
                "connected": True,
                "sim": "AMS2",
                "in_game": in_game,
                "is_paused": is_paused,
                "gameState": int(shm.mGameState),
                "speedKmh": speed_kmh,
                "gear": gear,
                "gearStr": gear_str,
                "rpms": rpms,
                "maxRpm": max_rpm,
                "fuel": fuel_level,
                "maxFuel": max_fuel,
                "ers_level": ers_level,
                "boostActive": boost_active,
                "ersDeploymentMode": ers_deployment_mode,
                "wheelsPressure": pressures,
                "tyreCoreTemperature": temps,
                "tyreThermal3Zones": tyre_thermal_3zones,
                "tyreWear": tyre_wear,
                "brakeTemp": brakes,
                "brakeBias": brake_bias,
                "airTemp": round(float(shm.mAmbientTemperature), 1),
                "roadTemp": round(float(shm.mTrackTemperature), 1),
                "currentTime": format_lap_time(current_time_sec),
                "bestLapTime": format_lap_time(best_lap_sec),
                "lastLapTime": format_lap_time(last_lap_sec),
                "splitTimeAhead": split_ahead,
                "splitTimeBehind": split_behind,
                "delta": split_delta,
                "completedLaps": completed_laps,
                "numberOfLaps": int(shm.mLapsInEvent),
                "eventTimeRemaining": event_time_remaining,
                "sessionDuration": session_duration,
                "position": position,
                "abs": abs_val,
                "tc": tc_val,
                "drs": drs_val,
                "throttle": max(0.0, throttle),
                "brake": max(0.0, brake),
                "clutch": max(0.0, clutch),
                "steering": steering,
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
        self._last_signature = None


_ams2_reader_instance: Optional[Automobilista2Reader] = None


def get_ams2_reader() -> Automobilista2Reader:
    global _ams2_reader_instance
    if _ams2_reader_instance is None:
        _ams2_reader_instance = Automobilista2Reader()
    return _ams2_reader_instance
