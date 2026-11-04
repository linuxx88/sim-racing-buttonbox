"""
Module de télémétrie mémoire partagée Assetto Corsa (Kunos Simulazioni).
Lit les structures partagées Windows 'acpmf_physics', 'acpmf_graphics' et 'acpmf_static'.
"""

import ctypes
from ctypes import Structure, c_int, c_float, c_wchar
import mmap
import sys

# Mapping rapports de vitesse Assetto Corsa : 0=R, 1=N, 2=1ere, 3=2eme, etc.
GEAR_MAPPING = ["R", "N", "1", "2", "3", "4", "5", "6", "7", "8"]
PSI_TO_BAR = 14.5038


class SPageFilePhysics(Structure):
    _pack_ = 4
    _fields_ = [
        ("packetId", c_int),
        ("gas", c_float),
        ("brake", c_float),
        ("fuel", c_float),
        ("gear", c_int),
        ("rpms", c_int),
        ("steerAngle", c_float),
        ("speedKmh", c_float),
        ("velocity", c_float * 3),
        ("accG", c_float * 3),
        ("wheelSlip", c_float * 4),
        ("wheelLoad", c_float * 4),
        ("wheelsPressure", c_float * 4),
        ("wheelAngularSpeed", c_float * 4),
        ("tyreWear", c_float * 4),
        ("tyreDirtyLevel", c_float * 4),
        ("tyreCoreTemperature", c_float * 4),
        ("camberRAD", c_float * 4),
        ("suspensionTravel", c_float * 4),
        ("drs", c_float),
        ("tc", c_float),
        ("heading", c_float),
        ("pitch", c_float),
        ("roll", c_float),
        ("cgHeight", c_float),
        ("carDamage", c_float * 5),
        ("numberOfTyresOut", c_int),
        ("pitLimiterOn", c_int),
        ("abs", c_float),
        ("kersCharge", c_float),
        ("kersInput", c_float),
        ("autoShifterOn", c_int),
        ("rideHeight", c_float * 2),
        ("turboBoost", c_float),
        ("ballast", c_float),
        ("airDensity", c_float),
        ("airTemp", c_float),
        ("roadTemp", c_float),
        ("localAngularVel", c_float * 3),
        ("finalFF", c_float),
        ("performanceMeter", c_float),
        ("engineBrake", c_int),
        ("ersRecoveryLevel", c_int),
        ("ersPowerLevel", c_int),
        ("ersHeatCharging", c_int),
        ("ersIsCharging", c_int),
        ("kersCurrentKJ", c_float),
        ("drsAvailable", c_int),
        ("drsEnabled", c_int),
        ("brakeTemp", c_float * 4),
        ("clutch", c_float),
        ("tyreTempI", c_float * 4),
        ("tyreTempM", c_float * 4),
        ("tyreTempO", c_float * 4),
        ("isAIControlled", c_int),
        ("tyreContactPoint", (c_float * 3) * 4),
        ("tyreContactNormal", (c_float * 3) * 4),
        ("tyreContactHeading", (c_float * 3) * 4),
        ("brakeBias", c_float),
        ("localVelocity", c_float * 3),
    ]


class SPageFileGraphic(Structure):
    _pack_ = 4
    _fields_ = [
        ("packetId", c_int),
        ("status", c_int),
        ("session", c_int),
        ("currentTime", c_wchar * 15),
        ("lastTime", c_wchar * 15),
        ("bestTime", c_wchar * 15),
        ("split", c_wchar * 15),
        ("completedLaps", c_int),
        ("position", c_int),
        ("iCurrentTime", c_int),
        ("iLastTime", c_int),
        ("iBestTime", c_int),
        ("sessionTimeLeft", c_float),
        ("distanceTraveled", c_float),
        ("isInPit", c_int),
        ("currentSectorIndex", c_int),
        ("lastSectorTime", c_int),
        ("numberOfLaps", c_int),
        ("tyreCompound", c_wchar * 33),
        ("replayTimeMultiplier", c_float),
        ("normalizedCarPosition", c_float),
        ("carCoordinates", c_float * 3),
        ("penaltyTime", c_float),
        ("flag", c_int),
        ("idealLineOn", c_int),
        ("isInPitLane", c_int),
        ("surfaceGrip", c_float),
        ("mandatoryPitDone", c_int),
        ("windSpeed", c_float),
        ("windDirection", c_float),
        ("isSetupMenuVisible", c_int),
        ("mainDisplayIndex", c_int),
        ("secondaryDisplayIndex", c_int),
        ("tc", c_int),
        ("tcCut", c_int),
        ("engineMap", c_int),
        ("abs", c_int),
        ("fuelXLap", c_float),
        ("rainLights", c_int),
        ("flashingLights", c_int),
        ("lightsStage", c_int),
        ("exhaustFlames", c_int),
        ("wiperLV", c_int),
        ("driverStintTotalTimeLeft", c_int),
        ("driverStintTimeLeft", c_int),
        ("rainTyres", c_int),
    ]


class SPageFileStatic(Structure):
    _pack_ = 4
    _fields_ = [
        ("smVersion", c_wchar * 15),
        ("acVersion", c_wchar * 15),
        ("numberOfSessions", c_int),
        ("numCars", c_int),
        ("carModel", c_wchar * 33),
        ("track", c_wchar * 33),
        ("playerName", c_wchar * 33),
        ("playerSurname", c_wchar * 33),
        ("playerNick", c_wchar * 33),
        ("sectorCount", c_int),
        ("maxTorque", c_float),
        ("maxPower", c_float),
        ("maxRpm", c_int),
        ("maxFuel", c_float),
        ("suspensionMaxTravel", c_float * 4),
        ("tyreRadius", c_float * 4),
        ("maxTurboBoost", c_float),
        ("airTemp", c_float),
        ("roadTemp", c_float),
        ("penaltiesEnabled", c_int),
        ("aidFuelRate", c_float),
        ("aidTireRate", c_float),
        ("aidMechanicalDamage", c_float),
        ("aidAllowTyreBlankets", c_int),
        ("aidStability", c_float),
        ("aidAutoClutch", c_int),
        ("aidAutoBlip", c_int),
        ("hasDRS", c_int),
        ("hasERS", c_int),
        ("hasKERS", c_int),
        ("kersMaxJ", c_float),
        ("engineBrakeSettingsCount", c_int),
        ("ersPowerControllerCount", c_int),
        ("trackSPlineLength", c_float),
        ("trackConfiguration", c_wchar * 33),
        ("ersMaxJ", c_float),
        ("isTimedRace", c_int),
        ("hasExtraLap", c_int),
        ("carSkin", c_wchar * 33),
        ("reversedGridPositions", c_int),
        ("pitWindowStart", c_int),
        ("pitWindowEnd", c_int),
        ("isOnline", c_int),
    ]


class AssettoCorsaReader:
    """
    Lecteur de mémoire partagée pour Assetto Corsa.
    Utilise mmap sous Windows avec tagname ('Local\\acpmf_physics' ou 'acpmf_physics').
    """

    def __init__(self):
        self.mmap_physics = None
        self.mmap_graphics = None
        self.mmap_static = None

    @staticmethod
    def _open_single_mmap(tag_base: str, struct_cls):
        size = ctypes.sizeof(struct_cls)
        # Tente l'espace de nommage Windows 'Local\\' puis le nom direct avec accès lecture seule
        for tag in (f"Local\\{tag_base}", tag_base):
            for fileno in (-1, 0):
                try:
                    return mmap.mmap(fileno, size, tagname=tag, access=mmap.ACCESS_READ)
                except Exception:
                    pass
        return None

    def _open(self) -> bool:
        if sys.platform != "win32":
            return False

        try:
            if self.mmap_physics is None:
                self.mmap_physics = self._open_single_mmap("acpmf_physics", SPageFilePhysics)
            if self.mmap_graphics is None:
                self.mmap_graphics = self._open_single_mmap("acpmf_graphics", SPageFileGraphic)
            if self.mmap_static is None:
                self.mmap_static = self._open_single_mmap("acpmf_static", SPageFileStatic)

            return (self.mmap_physics is not None and self.mmap_graphics is not None)
        except Exception:
            self.close()
            return False

    def read(self) -> dict:
        """
        Lit les structures partagées d'Assetto Corsa.
        Retourne un dictionnaire avec 'connected': True et les valeurs, ou {'connected': False} si absent/fermé.
        """
        if not self._open():
            return {"connected": False}

        try:
            physics = SPageFilePhysics.from_buffer(self.mmap_physics)
            graphics = SPageFileGraphic.from_buffer(self.mmap_graphics)

            # status: 0=OFF, 1=REPLAY, 2=LIVE, 3=PAUSE
            if graphics.status not in (2, 3) or physics.packetId == 0:
                return {
                    "connected": False,
                    "status": int(graphics.status)
                }

            gear = int(physics.gear)
            gear_str = GEAR_MAPPING[gear] if 0 <= gear < len(GEAR_MAPPING) else str(gear)

            pressures = [round(float(p) / PSI_TO_BAR, 2) for p in physics.wheelsPressure]
            temps = [round(float(t), 1) for t in physics.tyreCoreTemperature]

            max_rpm = 8000
            max_fuel = 100.0
            if self.mmap_static is not None:
                try:
                    static = SPageFileStatic.from_buffer(self.mmap_static)
                    if static.maxRpm > 0:
                        max_rpm = int(static.maxRpm)
                    if static.maxFuel > 0:
                        max_fuel = round(float(static.maxFuel), 1)
                except Exception:
                    pass

            return {
                "connected": True,
                "speedKmh": round(float(physics.speedKmh), 1),
                "gear": gear,
                "gearStr": gear_str,
                "rpms": int(physics.rpms),
                "fuel": round(float(physics.fuel), 1),
                "wheelsPressure": pressures,
                "tyreCoreTemperature": temps,
                "brakeBias": round(float(physics.brakeBias) * 100.0, 1) if physics.brakeBias > 0 else 0.0,
                "status": int(graphics.status),
                "currentTime": str(graphics.currentTime).strip(),
                "completedLaps": int(graphics.completedLaps),
                "numberOfLaps": int(graphics.numberOfLaps),
                "position": int(graphics.position),
                "tc": int(graphics.tc),
                "abs": int(graphics.abs),
                "engineMap": int(graphics.engineMap),
                "maxRpm": max_rpm,
                "maxFuel": max_fuel,
                "airTemp": round(float(physics.airTemp), 1),
                "roadTemp": round(float(physics.roadTemp), 1),
            }
        except Exception:
            self.close()
            return {"connected": False}

    def close(self):
        for attr in ("mmap_physics", "mmap_graphics", "mmap_static"):
            m = getattr(self, attr, None)
            if m is not None:
                try:
                    m.close()
                except Exception:
                    pass
                setattr(self, attr, None)


_reader_instance = None


def get_ac_reader() -> AssettoCorsaReader:
    global _reader_instance
    if _reader_instance is None:
        _reader_instance = AssettoCorsaReader()
    return _reader_instance
