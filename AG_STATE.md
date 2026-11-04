# État du Projet & Transition Machine (AG_STATE)

## 1. Objectif Global du Sprint / Module
- Finalisation d'une Button Box tactile Android ultra-faible latence et d'un Dashboard télémétrique multi-catégorie temps réel (30 Hz SSE) pour simulateurs de course PC (priorité **Automobilista 2 (AMS2)** via `$pcars2$`, support secondaire **Assetto Corsa** via `acpmf`), pilotés par un pont Windows autonome (`SimBoxBridge.exe`).

## 2. Complété et Validé Aujourd'hui
- **Lecteur Mémoire Partagée Automobilista 2 (`telemetry_ams2.py`)** :
  - Implémentation complète `ctypes.Structure` de la spécification `$pcars2$` (pack MSVC 4 octets).
  - Validation préalable de l'existence du bloc via `OpenFileMappingW(FILE_MAP_READ, False, "$pcars2$")`.
  - Désérialisation instantanée via `from_buffer_copy` avec sécurité anti-corruption et détection de heartbeat (temps au tour figé / sortie de jeu).
  - Normalisation des unités : vitesse en km/h, pressions en bar (`PSI / 14.5038`), rapports (`-1=R, 0=N, 1..n`), températures disques en °C, et usure résiduelle en %.
- **Décomposition Thermique Pneus 3 Zones (`Inside`, `Middle`, `Outside`)** :
  - Extraction de `mTyreTempLeft`, `mTyreTempCenter`, `mTyreTempRight` avec inversion géométrique appropriée selon le côté (roues gauches vs droites).
- **Orchestrateur Multi-Simulateurs (`telemetry_manager.py`)** :
  - Priorisation automatique d'AMS2 avec bascule transparente vers Assetto Corsa.
  - Normalisation unifiée du payload JSON pour le flux `/telemetry` à 30 Hz.
- **Frontend & Dashboard Multi-Catégories (`index.html`)** :
  - Badge dynamique du simulateur actif (`AMS2`, `Assetto Corsa`, ou `EN ATTENTE`).
  - Sélecteur de profil instantané en en-tête (`GT3`, `F1`, `HYPERCAR`).
  - Rampe 16 LED animée et étalonnée selon la classe (8 500 RPM pour GT3, 15 000 RPM pour F1).
  - Barres thermiques 3 zones pour les 4 pneus (bleu < 75°C, vert 80-95°C, orange > 95°C, rouge > 105°C).
  - Disques de frein SVG avec effet d'incandescence dynamique (glow orangé/rougeoyant en cas de gros freinage).
  - Delta au tour dynamique (-0.14 vert / +0.32 rouge), affichage DRS et jauge de batterie ERS / Hybride.
- **Outils de Test & Simulation** :
  - `mock_ams2_producer.py` : Générateur autonome et multithread de télémétrie `$pcars2$` (cycles réalistes de pleine accélération et freinages violents).
  - `test_ams2_integration.py` : Suite de tests unitaires validant la connexion, l'extraction et le fallback hors-jeu.
  - `test_e2e_sse.py` : Test d'intégration de bout en bout validant le pipeline complet `Mock -> TelemetryManager -> Payload unifié`.
- **Binaire Autonome Windows (`SimBoxBridge.exe`)** :
  - Compilation réussie avec PyInstaller 6.14.1 sous Python 3.12 (taille : ~9.5 Mo dans `release/SimBoxBridge.exe`).
  - Inclusion autonome de `index.html` et de tous les modules de télémétrie et d'injection.
- **Documentation & Spécifications** :
  - `README.md` mis à jour avec le guide d'activation de la mémoire partagée dans AMS2 (*Options > System > Shared Memory = Project CARS 2*), l'architecture complète et les instructions ADB.
  - `TODO.md` mis à jour avec toutes les tâches validées et le backlog des futures extensions.

## 3. Tâches en Cours & Blocages Actifs
- **Tâches en cours** : Toutes les phases du plan de travail sont achevées, testées et validées.
- **Blocages actifs** : Aucun blocage technique ou système.

## 4. Prochaine Étape Atomique Exacte
- Mettre en scène une session live en jeu sous Automobilista 2 avec `SimBoxBridge.exe` lancé et le téléphone connecté en USB via ADB pour valider le comportement in situ en course.
