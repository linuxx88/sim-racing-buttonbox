# AMS2 Sim Dashboard & Button Box

[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)](#)
[![Client: Android / Web](https://img.shields.io/badge/Client-Android%20%2F%20Web-3DDC84?logo=android&logoColor=white)](#)
[![Sim: Automobilista 2](https://img.shields.io/badge/Primary%20Sim-Automobilista%202-FF4500)](#)
[![Sim: Assetto Corsa](https://img.shields.io/badge/Supported-Assetto%20Corsa-darkred)](#)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](#)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Boîte à boutons tactile (Button Box) ultra-faible latence pour smartphone/tablette Android, propulsée par un pont Windows autonome.

Conçu en priorité pour **Automobilista 2 (AMS2)**, avec support d'**Assetto Corsa**.

---

## 🚀 Fonctionnalités Opérationnelles

### 1. Boîte à Boutons Tactile (Course & Cockpit)
- **Onglet Course** : DRS, Répartition de freinage (Bias +/-), Antipatinage (TC +/-), Frein moteur (+/-), ABS (+/-), Pleins phares / Appel de phares, Essuie-glaces, Limiteur de stands (Pit Limiter).
- **Onglet Cockpit** : Réglages direct en course de la position du siège (Hauteur, Avance/Recul), inclinaison (Pitch) et Champ de vision (FOV).
- **Drawer de correspondance** : Volet latéral rétractable (`☰`) listant l'ensemble des raccourcis clavier associés.
- **Retour haptique & visuel** : Confirmation instantanée à l'appui tactile, gestion des appuis répétés ou maintenus.
- **Mode Plein Écran PWA** : Raccourci natif pour masquer les barres de navigation du navigateur mobile.

---

## 🚧 En Cours de Développement (WIP)

Le **Dashboard Télémétrique GT3** (compteur, rapport de vitesse, rampe de LED et monitoring des pneus en temps réel) est en cours de développement et de calibration.

👉 Consultez [TODO.md](TODO.md) pour la feuille de route détaillée et l'avancement du moteur de télémétrie (AMS2 & Assetto Corsa).

---

## 🏗️ Architecture Technique

```
┌───────────────────────────────┐
│       Android Device          │
│ (Chrome PWA / Fullscreen Web) │
└──────────────┬────────────────┘
               │ HTTP (SSE) & WebSocket :5000
               │ (USB via ADB Tunnel ou WiFi LAN)
┌──────────────▼────────────────────────────────────────┐
│               SimBoxBridge (PC Windows)               │
│  - server.py       : Serveur HTTP statique & SSE      │
│  - bridge.py       : Hub WebSocket & routage          │
│  - injector.py     : Injection clavier DirectInput    │
│  - telemetry_ac.py : Lecteur Shared Memory (mmap)     │
└──────────────┬────────────────────────────────────────┘
               │ DirectInput / Win32 API / Shared Memory
┌──────────────▼────────────────────────────────────────┐
│     Automobilista 2 (AMS2)  /  Assetto Corsa (AC)     │
└───────────────────────────────────────────────────────┘
```

---

## 📦 Installation & Démarrage Rapide

### Méthode 1 : Binaire Autonome (Recommandé)
Aucune installation de Python requise sur la machine de jeu.

1. Téléchargez ou récupérez l'exécutable [release/SimBoxBridge.exe](file:///home/ssr/Desktop/ANDROID%20PROJECT/SIMDASHBOARD/release/SimBoxBridge.exe).
2. Lancez **`SimBoxBridge.exe`** (clic droit > *Exécuter en tant qu'administrateur* pour garantir l'accès à la mémoire partagée et l'injection d'inputs).

### Méthode 2 : Depuis les Sources (Python)
```bash
git clone https://github.com/linuxx88/sim-racing-buttonbox.git
cd sim-racing-buttonbox/sim_box_bridge

python -m venv .venv
# Windows :
.venv\Scripts\activate
pip install -r requirements-win.txt
python bridge.py
```

---

## 📱 Connexion de l'Appareil Android

### Option A : Câble USB via ADB Reverse (Zéro Latence - Recommandé)
1. Activez le **Débogage USB** sur votre smartphone ou tablette Android.
2. Reliez l'appareil au PC par câble USB.
3. Exécutez sur votre PC :
   ```bash
   adb reverse tcp:5000 tcp:5000
   ```
4. Ouvrez **Google Chrome** sur Android à l'adresse :
   ```
   http://localhost:5000
   ```

#### ⚠️ Première connexion & Autorisation ADB (si l'appareil n'est pas détecté)
Si la commande échoue ou si le mobile n'est pas reconnu :
1. **Ouvrir un terminal** : Dans le dossier du projet, ouvrez une invite de commandes (`cmd` ou PowerShell).
2. **Détecter le mobile** : Tapez la commande suivante :
   ```bash
   adb devices
   ```
3. **Valider l'invite sur Android** : Un pop-up *"Autoriser le débogage USB ?"* apparaît sur le téléphone. Cochez *"Toujours autoriser sur cet ordinateur"* et appuyez sur **OK**.
4. **Confirmer l'accès** : Si le terminal indiquait `unauthorized`, réexécutez `adb devices` jusqu'à voir votre appareil avec le statut `device` (autorisé).
5. **Démarrer le pont** : Lancez ensuite `run.bat` ou `SimBoxBridge.exe`.

### Option B : Connexion Réseau Local (WiFi)
1. Vérifiez que votre smartphone et votre PC sont sur le même réseau WiFi.
2. Trouvez l'adresse IP locale de votre PC (`ipconfig` sous Windows, ex: `192.168.1.50`).
3. Ouvrez le navigateur mobile à l'adresse :
   ```
   http://192.168.1.50:5000
   ```

---

## ⚙️ Configuration dans les Simulateurs

### 1. Automobilista 2 (AMS2)
Dans les options de commandes d'AMS2, associez les touches suivantes (ou adaptez le dictionnaire dans `sim_box_bridge/injector.py`) :

| Fonction | Touche Clavier Injectée |
| :--- | :--- |
| **DRS** | `D` |
| **Brake Bias + / -** | `Ctrl + Up` / `Ctrl + Down` |
| **Traction Control (TC) + / -** | `T` / `Shift + T` |
| **Engine Brake + / -** | `E` / `Shift + E` |
| **ABS + / -** | `A` / `Shift + A` |
| **Phares / Appel de phares** | `L` / `F` |
| **Essuie-glaces** | `W` |
| **Limiteur Stands (Pit Limiter)** | `P` |
| **Réglages Siège (Haut / Bas / Av / Ar)** | `Home` / `End` / `PageUp` / `PageDown` |
| **Pitch & FOV** | `Insert` / `Delete` |

### 2. Assetto Corsa (AC)
- Activez la mémoire partagée dans **Content Manager** : *Settings > Custom Shaders Patch > General Patch Settings*.
- La télémétrie démarre automatiquement dès que vous cliquez sur le volant ("Drive") et que la session passe en piste (`LIVE`).

---

## 🛠️ Structure du Projet

```
├── release/
│   └── SimBoxBridge.exe       # Binaire Windows portable autonome
├── sim_box_bridge/
│   ├── bridge.py              # Serveur principal WebSocket & orchestration
│   ├── server.py              # Serveur HTTP et flux SSE télémétrie (/telemetry)
│   ├── index.html             # Interface web tactile (Course, Cockpit, Dashboard)
│   ├── injector.py            # Moteur d'injection de touches DirectInput Windows
│   ├── telemetry_ac.py        # Connecteur Shared Memory Kunos (ctypes / mmap)
│   ├── requirements.txt       # Dépendances multiplateforme
│   └── requirements-win.txt   # Dépendances spécifiques Windows
└── README.md
```

---

## 📄 Licence
Projet distribué sous licence Apache 2.0. Voir [LICENSE](file:///home/ssr/Desktop/ANDROID%20PROJECT/SIMDASHBOARD/LICENSE) pour les termes complets.
