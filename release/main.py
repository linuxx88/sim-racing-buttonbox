import asyncio
import os
import sys
import threading
import time

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
sim_box_dir = os.path.join(BASE_DIR, "sim_box_bridge")
if os.path.exists(sim_box_dir) and sim_box_dir not in sys.path:
    sys.path.insert(0, sim_box_dir)

import bridge
import watcher

def run_watcher():
    time.sleep(1.0)
    print("[MAIN] Demarrage de la surveillance arriere-plan...", flush=True)
    target_games = watcher.DEFAULT_TARGET_GAMES
    engaged = False
    while True:
        try:
            proc_found = watcher.is_process_running(target_games)
            adb_state = watcher.get_adb_state()

            if proc_found and adb_state == "device":
                if not engaged:
                    print(f"[WATCHER] Processus detecte : {proc_found}", flush=True)
                    print(f"[WATCHER] Peripherique USB ADB detecte : {adb_state}", flush=True)
                    watcher.trigger_bridge(dry_run=False)
                    engaged = True
            else:
                if engaged:
                    print("[WATCHER] Deconnexion detectee. Reinitialisation.", flush=True)
                    engaged = False
            time.sleep(2.0)
        except Exception:
            time.sleep(2.0)

def main():
    print("=======================================================", flush=True)
    print("      Sim Racing Button Box Bridge - Standalone        ", flush=True)
    print("=======================================================", flush=True)

    watcher_thread = threading.Thread(target=run_watcher, daemon=True)
    watcher_thread.start()

    try:
        asyncio.run(bridge.main())
    except KeyboardInterrupt:
        print("[MAIN] Fermeture propre.", flush=True)

if __name__ == "__main__":
    main()
