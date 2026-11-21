@echo off
setlocal
cd /d "%~dp0"
title Sim Racing Button Box Bridge
echo ========================================================
echo    Sim Racing Button Box Bridge - Standalone Package
echo ========================================================
echo [CLEAN] Fermeture des anciennes instances eventuelles...
taskkill /F /IM SimBoxBridge.running.exe >nul 2>&1
taskkill /F /IM SimBoxBridge.old.exe >nul 2>&1
taskkill /F /IM SimBoxBridge.exe >nul 2>&1
if exist "SimBoxBridge.running.exe" del /F /Q "SimBoxBridge.running.exe" >nul 2>&1
if exist "SimBoxBridge.old.exe" del /F /Q "SimBoxBridge.old.exe" >nul 2>&1
echo [START] Lancement du pont autonome (bridge + watcher + ADB)...
SimBoxBridge.exe main.py
if errorlevel 1 (
    echo [ERREUR] Le pont s'est arrete avec une erreur.
    pause
)
