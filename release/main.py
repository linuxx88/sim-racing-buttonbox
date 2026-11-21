import asyncio
import os
import subprocess
import sys
import threading
import time

if getattr(sys, "frozen", False):
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Assure la présence des dossiers critiques dans sys.path (pour exécution standalone et source)
for p in (
    BASE_DIR,
    os.path.join(BASE_DIR, "sim_box_bridge"),
    os.path.dirname(BASE_DIR),
    os.path.join(os.path.dirname(BASE_DIR), "sim_box_bridge"),
):
    if p and os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

try:
    import bridge
    import watcher
except ImportError:
    from sim_box_bridge import bridge
    from sim_box_bridge import watcher


def kill_stale_instances():
    """Arrête toute ancienne instance fantôme de SimBoxBridge avant d'ouvrir le port 5000."""
    if sys.platform != "win32":
        return
    my_pid = os.getpid()
    for exe_name in ("SimBoxBridge.running.exe", "SimBoxBridge.old.exe", "SimBoxBridge.exe"):
        try:
            subprocess.run(
                ["taskkill", "/F", "/FI", f"PID ne {my_pid}", "/IM", exe_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                timeout=2,
            )
        except Exception:
            pass


def run_watcher():
    time.sleep(1.0)
    print("[MAIN] Demarrage de la surveillance arriere-plan...", flush=True)
    target_games = watcher.DEFAULT_TARGET_GAMES
    engaged = False
    reverse_ready = False
    fail_count = 0

    while True:
        try:
            # Si le téléphone est déjà connecté au serveur (WebSocket ou SSE actif),
            # on ne relance jamais 'adb shell am start' ni 'tasklist' pour éviter tout refresh d'écran.
            if bridge.has_active_clients():
                engaged = True
                fail_count = 0
                time.sleep(3.0)
                continue

            adb_state = watcher.get_adb_state()
            if adb_state == "device" and not reverse_ready:
                reverse_ready = watcher.ensure_adb_reverse()

            proc_found = watcher.is_process_running(target_games)

            if proc_found and adb_state == "device":
                fail_count = 0
                if not engaged:
                    print(f"[WATCHER] Processus detecte : {proc_found}", flush=True)
                    print(f"[WATCHER] Peripherique USB ADB detecte : {adb_state}", flush=True)
                    watcher.trigger_bridge(dry_run=False, launch_browser=not bridge.has_active_clients())
                    engaged = True
                    reverse_ready = True
            else:
                if adb_state != "device":
                    reverse_ready = False
                if engaged:
                    fail_count += 1
                    if fail_count >= 3:
                        print("[WATCHER] Deconnexion detectee. Reinitialisation.", flush=True)
                        engaged = False
                        fail_count = 0
            time.sleep(2.5)
        except Exception:
            time.sleep(2.5)


def main():
    print("=======================================================", flush=True)
    print("      Sim Racing Button Box Bridge - Standalone        ", flush=True)
    print("=======================================================", flush=True)

    kill_stale_instances()

    watcher_thread = threading.Thread(target=run_watcher, daemon=True)
    watcher_thread.start()

    try:
        asyncio.run(bridge.main())
    except KeyboardInterrupt:
        print("[MAIN] Fermeture propre.", flush=True)


if __name__ == "__main__":
    main()
