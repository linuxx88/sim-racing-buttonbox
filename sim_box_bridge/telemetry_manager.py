"""
Gestionnaire et Orchestrateur de télémétrie multi-simulateurs (AMS2, Assetto Corsa).
Aiguille automatiquement le flux vers le lecteur adéquat et normalise le payload JSON.
"""

from typing import Dict, Any, Optional

try:
    from telemetry_ams2 import get_ams2_reader, Automobilista2Reader
    from telemetry_ac import get_ac_reader, AssettoCorsaReader
except ImportError:
    from sim_box_bridge.telemetry_ams2 import get_ams2_reader, Automobilista2Reader
    from sim_box_bridge.telemetry_ac import get_ac_reader, AssettoCorsaReader


class TelemetryManager:
    """
    Orchestrateur multi-simulateurs.
    Scrute en continu Automobilista 2 et Assetto Corsa avec priorité AMS2.
    """

    def __init__(self):
        self.ams2_reader: Automobilista2Reader = get_ams2_reader()
        self.ac_reader: AssettoCorsaReader = get_ac_reader()
        self.active_sim: Optional[str] = None

    def read(self) -> Dict[str, Any]:
        """
        Lit la télémétrie du simulateur actif.
        Si aucun simulateur n'est en ligne, retourne {'connected': False, 'in_game': False}.
        """
        # 1. Vérification prioritaire : Automobilista 2 ($pcars2$)
        data_ams2 = self.ams2_reader.read()
        if data_ams2.get("connected"):
            self.active_sim = "AMS2"
            return self._normalize_payload(data_ams2, "AMS2")

        # 2. Vérification secondaire : Assetto Corsa (acpmf_physics)
        data_ac = self.ac_reader.read()
        if data_ac.get("connected"):
            self.active_sim = "Assetto Corsa"
            return self._normalize_payload(data_ac, "Assetto Corsa")

        # 3. Aucun simulateur actif
        self.active_sim = None
        return {
            "connected": False,
            "sim": None,
            "in_game": False,
        }

    def _normalize_payload(self, raw: Dict[str, Any], sim_name: str) -> Dict[str, Any]:
        """
        Garantit que toutes les clés attendues par l'interface web sont présentes et typées,
        avec rétro-compatibilité sur les noms de clés courts/longs.
        """
        speed = float(raw.get("speedKmh", 0.0))
        rpms = int(raw.get("rpms", 0))
        max_rpm = int(raw.get("maxRpm", 8000))
        gear = int(raw.get("gear", 0))
        gear_str = str(raw.get("gearStr", "N"))
        drs = int(raw.get("drs", 0))
        split_ahead = float(raw.get("splitTimeAhead", 0.0))

        # Organisation dictionnaire 3 zones par pneu (FL, FR, RL, RR)
        zones_raw = raw.get("tyreThermal3Zones")
        if isinstance(zones_raw, list) and len(zones_raw) >= 4:
            tyre_thermal_dict = {
                "FL": zones_raw[0],
                "FR": zones_raw[1],
                "RL": zones_raw[2],
                "RR": zones_raw[3],
            }
            tyre_thermal_list = zones_raw
        elif isinstance(zones_raw, dict):
            tyre_thermal_dict = zones_raw
            tyre_thermal_list = [
                zones_raw.get("FL", {"inside": 0.0, "middle": 0.0, "outside": 0.0}),
                zones_raw.get("FR", {"inside": 0.0, "middle": 0.0, "outside": 0.0}),
                zones_raw.get("RL", {"inside": 0.0, "middle": 0.0, "outside": 0.0}),
                zones_raw.get("RR", {"inside": 0.0, "middle": 0.0, "outside": 0.0}),
            ]
        else:
            default_zone = {"inside": 0.0, "middle": 0.0, "outside": 0.0}
            tyre_thermal_dict = {"FL": default_zone, "FR": default_zone, "RL": default_zone, "RR": default_zone}
            tyre_thermal_list = [default_zone, default_zone, default_zone, default_zone]

        return {
            "connected": True,
            "sim": sim_name,
            "in_game": bool(raw.get("in_game", False)),
            "is_paused": bool(raw.get("is_paused", False)),
            # Champs vitesse & régime (formes longue et courte)
            "speedKmh": speed,
            "speed": speed,
            "gear": gear,
            "gearStr": gear_str,
            "gear_str": gear_str,
            "rpms": rpms,
            "rpm": rpms,
            "maxRpm": max_rpm,
            "max_rpm": max_rpm,
            # Fluides & aides
            "fuel": float(raw.get("fuel", 0.0)),
            "maxFuel": float(raw.get("maxFuel", 100.0)),
            "ers_level": float(raw.get("fuel", 0.0)),  # Fallback ERS pour prototypes/F1
            "wheelsPressure": list(raw.get("wheelsPressure", [0.0, 0.0, 0.0, 0.0])),
            "tyreCoreTemperature": list(raw.get("tyreCoreTemperature", [0.0, 0.0, 0.0, 0.0])),
            "tyreThermal3Zones": tyre_thermal_dict,
            "tyreThermal3ZonesList": tyre_thermal_list,
            "tyreWear": list(raw.get("tyreWear", [100.0, 100.0, 100.0, 100.0])),
            "brakeTemp": list(raw.get("brakeTemp", [0.0, 0.0, 0.0, 0.0])),
            "brakeBias": float(raw.get("brakeBias", 0.0)),
            "brake_bias": float(raw.get("brakeBias", 0.0)),
            "airTemp": float(raw.get("airTemp", 20.0)),
            "roadTemp": float(raw.get("roadTemp", 25.0)),
            # Chronométrage
            "currentTime": str(raw.get("currentTime", "--:--.---")),
            "bestLapTime": str(raw.get("bestLapTime", "--:--.---")),
            "lastLapTime": str(raw.get("lastLapTime", "--:--.---")),
            "splitTimeAhead": split_ahead,
            "splitTimeBehind": float(raw.get("splitTimeBehind", 0.0)),
            "delta": float(raw.get("delta", 0.0)),
            "delta_lap": split_ahead,
            "completedLaps": int(raw.get("completedLaps", 0)),
            "numberOfLaps": int(raw.get("numberOfLaps", 0)),
            "position": int(raw.get("position", 1)),
            "abs": int(raw.get("abs", 0)),
            "tc": int(raw.get("tc", 0)),
            "drs": drs,
            "drs_status": drs,
            "throttle": float(raw.get("throttle", 0.0)),
            "brake": float(raw.get("brake", 0.0)),
            "clutch": float(raw.get("clutch", 0.0)),
            "steering": float(raw.get("steering", 0.0)),
            "carName": str(raw.get("carName", "")),
            "trackName": str(raw.get("trackName", "")),
        }

    def close(self):
        self.ams2_reader.close()
        self.ac_reader.close()
        self.active_sim = None


_telemetry_manager: Optional[TelemetryManager] = None


def get_telemetry_manager() -> TelemetryManager:
    global _telemetry_manager
    if _telemetry_manager is None:
        _telemetry_manager = TelemetryManager()
    return _telemetry_manager
