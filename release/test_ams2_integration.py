"""
Test unitaire et d'intégration pour le connecteur Automobilista 2 ($pcars2$).
"""

import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from telemetry_ams2 import get_ams2_reader
import mock_ams2_producer


def test_ams2_telemetry():
    print("=== Test Unitaire & Integration Télémétrie AMS2 ===", flush=True)

    # 1. Test quand AMS2 n'est pas lancé
    reader = get_ams2_reader()
    reader.close()
    data_off = reader.read()
    assert data_off["connected"] is False, f"Attendu connected=False, obtenu {data_off}"
    print("[PASS] Validation hors-jeu : détection 'connected=False' OK")

    # 2. Démarrage du mock producer en arrière-plan pendant 4 secondes
    producer_thread = threading.Thread(
        target=mock_ams2_producer.run_mock,
        args=(4.0, 30),
        daemon=True
    )
    producer_thread.start()
    time.sleep(0.5)  # Attente de création de la mémoire partagée

    # 3. Lecture via get_ams2_reader()
    data_live = reader.read()
    assert data_live["connected"] is True, f"Attendu connected=True, obtenu {data_live}"
    assert data_live["sim"] == "AMS2", f"Attendu sim='AMS2', obtenu {data_live.get('sim')}"
    assert data_live["in_game"] is True, f"Attendu in_game=True"
    assert data_live["speedKmh"] > 50.0, f"Vitesse invalide: {data_live.get('speedKmh')}"
    assert data_live["rpms"] > 1000, f"Régime invalide: {data_live.get('rpms')}"
    assert data_live["maxRpm"] == 8800, f"Max RPM invalide: {data_live.get('maxRpm')}"
    assert data_live["carName"] == "Porsche 911 GT3 R", f"Voiture invalide: {data_live.get('carName')}"
    assert data_live["trackName"] == "Spa-Francorchamps", f"Circuit invalide: {data_live.get('trackName')}"

    # Validation conversion pressions (27.5 PSI -> ~1.90 bar)
    pressures = data_live["wheelsPressure"]
    assert len(pressures) == 4, f"Nombre de pressions roues invalide: {len(pressures)}"
    assert 1.85 <= pressures[0] <= 1.95, f"Pression attendue ~1.90 bar, obtenu {pressures[0]}"

    # Validation thermique 3 zones
    thermals = data_live["tyreThermal3Zones"]
    assert len(thermals) == 4, f"Nombre de zones thermiques invalide: {len(thermals)}"
    for z in thermals:
        assert "inside" in z and "middle" in z and "outside" in z
        assert z["inside"] > 70.0 and z["outside"] > 70.0

    # Validation freins
    brakes = data_live["brakeTemp"]
    assert len(brakes) == 4
    assert brakes[0] > 300.0

    print("[PASS] Données en direct extraites et validées avec succès !")
    print(f"       -> Vitesse : {data_live['speedKmh']} km/h")
    print(f"       -> Régime  : {data_live['rpms']} / {data_live['maxRpm']} RPM (Rapport {data_live['gearStr']})")
    print(f"       -> Carburant : {data_live['fuel']} L / {data_live['maxFuel']} L")
    print(f"       -> Pression pneus : {pressures} bar")
    print(f"       -> Température freins : {brakes} °C")
    print(f"       -> Temps au tour : {data_live['currentTime']} (Meilleur : {data_live['bestLapTime']})")

    producer_thread.join()
    reader.close()
    print("=== TOUS LES TESTS AMS2 SONT VALIDÉS AVEC SUCCÈS ===", flush=True)


if __name__ == "__main__":
    test_ams2_telemetry()
