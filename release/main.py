import asyncio
import os
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
