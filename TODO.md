# 📋 Feuille de Route & Tâches à Traiter (TODO)

Ce fichier regroupe les fonctionnalités en cours de développement, avec une priorité accordée à la finalisation du **Dashboard Télémétrique GT3**.

---

## 🏎️ Dashboard Télémétrique GT3 (En Cours / Non Finalisé)

Le rendu visuel (rampe LED, affichage rapport/vitesse, tracé châssis SVG, cartouches pneus) est intégré dans l'interface, mais le moteur de données en temps réel requiert encore les étapes suivantes pour être 100 % opérationnel :

### 1. Télémétrie Automobilista 2 (AMS2) - Priorité Haute
- [ ] **Connecteur Shared Memory AMS2** : Implémenter la structure de lecture ctypes/mmap du bloc `$pcars2$` (spécification Project CARS 2 / AMS2).
- [ ] **Synchronisation des variables moteur** :
  - `mRpm` et `mMaxRPM` pour animer dynamiquement les 16 LED de la rampe de régime.
  - `mGear` pour le rapport engagé (R, N, 1-8).
  - `mSpeed` (m/s converti en km/h).
- [ ] **Télémétrie Châssis & Pneus AMS2** :
  - `mTyrePressure` (conversion KPa vers bar).
  - `mTyreTemp` (température de la bande de roulement en °C).
  - `mFuelLevel` et capacité maximale du réservoir.
- [ ] **Chronos & Delta de course** :
  - `mCurrentTime`, `mBestLapTime`, `mSplitTimeAhead` pour le calcul du delta dynamique (-0.14 vert/rouge).
  - Compteur de tours complétés et position dans la session.

### 2. Télémétrie Assetto Corsa (AC) - Priorité Secondaire
- [ ] **Élévation de privilèges & Processus** : Automatiser la détection si Content Manager ou `acs.exe` tourne en mode administrateur.
- [ ] **Validation de la session en direct** : Renforcer la transition entre les menus (statut inactif) et la session sur piste (`AC_LIVE`).
- [ ] **Calibration de la rampe de régime** : Ajuster les seuils d'activation des LED rouge/bleu selon les fichiers de configuration de chaque voiture.

### 3. Pipeline de Diffusion Réseau (SSE / WebSocket)
- [ ] **Format de payload unifié** : Standardiser le JSON émis sur `/telemetry` pour qu'il soit identique quel que soit le simulateur détecté (AMS2 ou Assetto Corsa).
- [ ] **Tolérance aux pannes** : Gestion de la reconnexion automatique du flux SSE sans rechargement de page en cas de redémarrage de session.

### 4. Graphisme Châssis, Rendu Visuel des Pneus & Freins
- [ ] **Silhouette Châssis SVG détaillée** : Remplacer le tracé minimaliste par une vue de dessus plus fine (profilage aérodynamique, aileron arrière, splitter avant et passages de roues).
- [ ] **Coloration thermique dynamique des pneus** :
  - Dégradé de couleur en temps réel sur les 4 roues selon la température (Bleu = froid `< 75°C`, Vert = optimal `80-95°C`, Orange = chaud `> 95°C`, Rouge = surchauffe `> 105°C`).
  - Découpage en 3 zones thermiques par pneu (Intérieur / Milieu / Extérieur) pour visualiser le carrossage.
- [ ] **Indicateurs d'usure & état des gommes** : Jauge visuelle d'usure résiduelle (0-100%) et détection des plats de freinage (flat spots).
- [ ] **Monitoring visuel des disques de frein** : Disques de frein SVG aux 4 coins avec incandescence dynamique selon la température des plaquettes/disques.

---

## 🏎️ Profils & Tableaux de Bord par Catégorie de Véhicule

Les besoins d'instrumentation diffèrent radicalement entre les catégories (régimes moteurs, aides électroniques, systèmes hybrides) :

### 1. Profil Formule 1 & Monoplaces (Open-Wheel)
- [ ] **Disposition typée volant F1** : Écran compact avec LED latérales, régime moteur étalonné jusqu'à 15 000 RPM.
- [ ] **Gestion de l'hybride (ERS / MGU-K)** : Jauge de charge de batterie (%), mode de déploiement (Hotlap, Overtake, Balanced) et jauge d'énergie par tour.
- [ ] **Indicateur DRS dynamique** : État DRS (Zone détectée, disponible < 1s, ouvert / actif).
- [ ] **Paramètres avancés** : Brake Migration, réglages de différentiel (Entrée / Milieu / Sortie).

### 2. Profil GT3 / GTE / GT4 (Actuel)
- [ ] **Disposition DDU de course (type Bosch / MoTeC)** : Étalonnage 6 000 - 8 500 RPM.
- [ ] **Aides électroniques** : Niveaux d'ABS (1-12), Traction Control (TC1 / TC2) et cartographie moteur (Engine Map).
- [ ] **Gestion des pneus & endurance** : Fenêtre thermique optimale (core/surface) et calcul de consommation d'essence au tour.

### 3. Profil Prototypes & Hypercars (LMDh / LMh)
- [ ] **Réservoir d'énergie virtuelle (Virtual Energy Tank)** : Suivi des allocations mégajoules (MJ) par relais (règlement WEC/IMSA).
- [ ] **Surveillance thermique des freins carbone** et équilibre aéro actif.

### 4. Architecture IHM Multi-Dash
- [ ] **Sélecteur manuel / détection automatique** : Commutation instantanée du thème et des jauges selon la voiture détectée en piste.

---

## 🕹️ Boîte à Boutons (Améliorations Futures)
- [ ] Support de profils de touches configurables directement depuis un fichier JSON sans modifier le code Python.
- [ ] Possibilité de mapper des axes virtuels (ex: mollettes rotatives pour l'ABS / TC).
