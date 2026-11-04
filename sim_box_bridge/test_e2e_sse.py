"""
Test d'intégration End-to-End pour Sim Box Bridge :
1. Démarre le producteur synthétique AMS2 ($pcars2$).
2. Initialise TelemetryManager.
3. Vérifie que la télémétrie reçue est bien routée sur AMS2 avec les données cohérentes.
4. Vérifie la présence de tous les champs unifiés requis par le Dashboard GT3/F1/Hypercar.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_ams2_producer import MockAMS2Producer
from telemetry_manager import get_telemetry_manager

def run_test():
    print("=== TEST E2E TELEMETRY MANAGER & AMS2 SHARED MEMORY ===")
    
    # 1. Avant lancement du mock : doit être fallback
    manager = get_telemetry_manager()
    initial_data = manager.read()
    print(f"État initial (hors-jeu) : sim='{initial_data.get('sim')}', in_game={initial_data.get('in_game')}")
    assert initial_data.get("in_game") is False, "Le statut initial devrait être hors-jeu (False)"
    
    # 2. Démarrage du producteur mock AMS2
    producer = MockAMS2Producer()
    producer.start()
    time.sleep(0.3)
    
    try:
        # Lecture pendant 1 seconde
        for i in range(5):
            time.sleep(0.1)
            frame = manager.read()
            print(f"[Frame {i+1}] sim={frame.get('sim')} | speed={frame.get('speed')} km/h | rpm={frame.get('rpm')}/{frame.get('max_rpm')} | gear={frame.get('gear')} | in_game={frame.get('in_game')}")
            
            # Validations clés
            assert frame.get("sim") == "AMS2", f"Attendu sim='AMS2', reçu: {frame.get('sim')}"
            assert frame.get("in_game") is True, f"Attendu in_game=True"
            assert frame.get("rpm", 0) > 0, f"RPM attendu > 0, reçu: {frame.get('rpm')}"
            assert frame.get("max_rpm", 0) > 0, f"Max RPM attendu > 0, reçu: {frame.get('max_rpm')}"
            assert "tyreThermal3Zones" in frame, "tyreThermal3Zones manquant"
            assert "FL" in frame["tyreThermal3Zones"], "Roue FL manquante"
            assert "tyreWear" in frame, "tyreWear manquant"
            assert "brakeTemp" in frame, "brakeTemp manquant"
            assert "ers_level" in frame, "ers_level manquant"
            assert "drs_status" in frame, "drs_status manquant"
            assert "delta_lap" in frame, "delta_lap manquant"
        
        print("\n=== TOUTES LES VÉRIFICATIONS E2E TÉLÉMÉTRIE ONT RÉUSSI ===")
    finally:
        producer.stop()
        time.sleep(0.2)
        final_data = manager.read()
        print(f"État après arrêt mock : sim='{final_data.get('sim')}', in_game={final_data.get('in_game')}")
        assert final_data.get("in_game") is False, "Après arrêt du mock, le manager doit revenir hors-jeu"
        print("=== REPRISE HORS-JEU VALIDÉE ===")

if __name__ == "__main__":
    run_test()
