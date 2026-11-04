@echo off
setlocal
cd /d "%~dp0"
title Sim Racing Button Box Bridge
echo ========================================================
echo    Sim Racing Button Box Bridge - Standalone Package
echo ========================================================
echo [START] Lancement du pont autonome (bridge + watcher + ADB)...
SimBoxBridge.exe main.py
if errorlevel 1 (
    echo [ERREUR] Le pont s'est arrete avec une erreur.
    pause
)
