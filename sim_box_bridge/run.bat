@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo    Sim Racing Button Box Bridge - Demarrage Windows
echo ========================================================

if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] Initialisation du virtualenv...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements-win.txt
) else (
    call .venv\Scripts\activate.bat
)

echo [START] Lancement du serveur bridge.py en arriere-plan...
start "" /B python bridge.py

echo [START] Lancement du watcher (detection AMS2 / Assetto Corsa et USB)...
python watcher.py

echo [CLEANUP] Arret des processus...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Sim Racing*" >nul 2>&1
