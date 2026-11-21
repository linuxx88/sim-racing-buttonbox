# État du Projet & Transition Machine (AG_STATE)

## 1. Objectif Global du Sprint / Module
- Finalisation d'une Button Box tactile Android ultra-faible latence et d'un Dashboard télémétrique multi-catégorie temps réel (30 Hz SSE) pour simulateurs de course PC (priorité **Automobilista 2 (AMS2)** via `$pcars2$`, support secondaire **Assetto Corsa** via `acpmf`), pilotés par un pont Windows autonome (`SimBoxBridge.exe`).

## 2. Complété et Validé Aujourd'hui
- **Correction des 3 Bugs En Jeu (Diodes RPM Inversées, Rapport Bloqué sur N, et Rafraîchissement Écran Rapide)** :
  1. **Élimination des instances fantômes (`SimBoxBridge.running.exe` / `SimBoxBridge.old.exe`)** :
     - Lors de la recompilation précédente, l'ancien exécutable (`SimBoxBridge.running.exe`, compilé avant l'alignement de `SharedMemory.h`) avait été renommé à chaud sans être arrêté. Sous Windows, ce processus fantôme conservait le port `5000` ouvert avec l'ancienne structure décalée de 24/40 octets (où `mRpm`/`mMaxRPM` lisaient la température/pression d'eau et `mGear` restait forcé à `N`).
     - Suppression des binaires résiduels `.running.exe` et `.old.exe`, ajout d'un nettoyage automatique (`kill_stale_instances()`) au démarrage de [`main.py`](file:///k:/simbox/sim-box/sim_box_bridge/main.py) et dans [`SimBoxBridge.bat`](file:///k:/simbox/sim-box/release/SimBoxBridge.bat), et ajout des en-têtes `Cache-Control: no-store` dans [`bridge.py`](file:///k:/simbox/sim-box/sim_box_bridge/bridge.py).
  2. **Suppression du Rafraîchissement / Clignotement de l'Écran en Roulage** :
     - **Cause A (Heartbeat `mCurrentTime` sur tour de sortie / tour invalidé)** : Dans AMS2, `mCurrentTime` vaut `-1.0` pendant tout le tour de sortie des stands (*Outlap*) ou lorsqu'un tour est invalidé. L'ancien heartbeat fermait la mémoire partagée toutes les 2,5 s en croyant le jeu figé, faisant basculer le dashboard sur `0 / STANDBY` pendant une trame avant de se reconnecter. Remplacé dans [`telemetry_ams2.py`](file:///k:/simbox/sim-box/sim_box_bridge/telemetry_ams2.py) par une signature basée sur `mSequenceNumber` + variables physiques (`mRpm`, `mSpeed`, `mUnfilteredSteering`) et typage 64-bit `wintypes.HANDLE`.
     - **Cause B (Relances intempestives `adb shell am start` par le Watcher)** : En roulage, [`watcher.py`](file:///k:/simbox/sim-box/sim_box_bridge/watcher.py) / [`main.py`](file:///k:/simbox/sim-box/sim_box_bridge/main.py) relançait parfois l'intent Android `VIEW http://localhost:5000` après un micro-délai ADB, forçant Chrome Android à recharger la page. Désormais, tant qu'un client WebSocket ou SSE est connecté (`bridge.has_active_clients()`), le watcher ne lance plus `tasklist` ni `am start`.
     - **Cause C (Reflows DOM & Transitions CSS à 30 Hz dans `index.html`)** : Synchronisation via `requestAnimationFrame`, mise en cache des nœuds DOM, mise à jour différentielle stricte (`setText`, paliers de freins, classes LEDs), police `tabular-nums` à largeur fixe sur le rapport/vitesse, et persistance de l'onglet actif dans `sessionStorage`.

## 3. Tâches en Cours & Blocages Actifs
- **Tâches en cours** : Finalisation de la recompilation propre de `release/SimBoxBridge.exe`.
- **Blocages actifs** : Aucun.

## 4. Prochaine Étape Atomique Exacte
- Tester en piste sous Automobilista 2 avec le nouveau `release/SimBoxBridge.exe`.
