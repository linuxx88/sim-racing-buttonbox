import argparse
import atexit
import os
import signal
import subprocess
import sys
import time

TARGET_PROCESSES = ["AMS2AVX.exe", "acs.exe"]
DEFAULT_TARGET_GAMES = TARGET_PROCESSES

def get_adb_binary() -> str:
    candidates = [
        os.path.join(os.path.abspath("."), "adb.exe"),
        os.path.join(os.path.dirname(sys.executable), "adb.exe"),
        os.path.join(getattr(sys, "_MEIPASS", ""), "adb.exe"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "adb.exe"),
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return "adb"

def get_env():
    env = os.environ.copy()
    if not os.access(os.path.expanduser("~"), os.W_OK):
        env["HOME"] = "/tmp"
    return env

_cleaned_up = False

def cleanup_adb():
    global _cleaned_up
    if _cleaned_up:
        return
    _cleaned_up = True
    try:
        adb_bin = get_adb_binary()
        print(f"[WATCHER_CLEANUP] Arret du daemon ADB via {adb_bin} kill-server...", flush=True)
        subprocess.run(
            [adb_bin, "kill-server"],
            env=get_env(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3,
        )
    except Exception:
        pass

atexit.register(cleanup_adb)

def _signal_handler(sig, frame):
    cleanup_adb()
    sys.exit(0)

for _sig_name in ("SIGINT", "SIGTERM", "SIGBREAK"):
    if hasattr(signal, _sig_name):
        try:
            signal.signal(getattr(signal, _sig_name), _signal_handler)
        except (ValueError, OSError):
            pass

def is_process_running(targets: list[str]) -> str | None:
    if sys.platform == "win32":
        try:
            out = subprocess.check_output(
                ["tasklist"],
                text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            for target in targets:
                if target.lower() in out.lower():
                    return target
        except Exception:
            pass
    else:
        for target in targets:
            try:
                res = subprocess.run(
                    ["pgrep", "-f", target],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if res.returncode == 0:
                    return target
            except Exception:
                pass
    return None

def get_adb_state() -> str | None:
    try:
        res = subprocess.run(
            [get_adb_binary(), "get-state"],
            capture_output=True,
            text=True,
            env=get_env(),
            timeout=2,
        )
        if res.returncode == 0:
            return res.stdout.strip()
        else:
            if res.stderr:
                print(f"[WATCHER_DEBUG] adb get-state error: {res.stderr.strip()}", flush=True)
    except Exception as e:
        print(f"[WATCHER_DEBUG] adb get-state exception: {e}", flush=True)
    return None

def trigger_bridge(dry_run: bool = False):
    env = get_env()
    adb_bin = get_adb_binary()
    if dry_run:
        print(f"[DRY_RUN] {adb_bin} reverse tcp:5000 tcp:5000", flush=True)
        print(f"[DRY_RUN] {adb_bin} shell am start -a android.intent.action.VIEW -d http://localhost:5000", flush=True)
    else:
        res_rev = subprocess.run(
            [adb_bin, "reverse", "tcp:5000", "tcp:5000"],
            env=env,
            capture_output=True,
            text=True,
        )
        if res_rev.returncode != 0:
            print(f"[WATCHER_ERROR] adb reverse failed: {res_rev.stderr.strip()}", flush=True)
        
        res_act = subprocess.run(
            [adb_bin, "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "http://localhost:5000"],
            env=env,
            capture_output=True,
            text=True,
        )
        if res_act.returncode != 0:
            print(f"[WATCHER_ERROR] adb shell am start failed: {res_act.stderr.strip()}", flush=True)

    print("BRIDGE_AUTO_TRIGGERED", flush=True)

def main():
    parser = argparse.ArgumentParser(description="Sim Racing Bridge Watcher")
    parser.add_argument("--mock-process", type=str, help="Surcharge du processus pour tests")
    parser.add_argument("--dry-run", action="store_true", help="Exécuter une seule détection sans appliquer les commandes ADB")
    parser.add_argument("--once", action="store_true", help="Déclencher une seule fois et quitter")
    parser.add_argument("--interval", type=float, default=2.0, help="Intervalle de vérification en secondes")
    args = parser.parse_args()

    target_games = [args.mock_process] if args.mock_process else DEFAULT_TARGET_GAMES
    print(f"[WATCHER] Surveillance active. Processus cibles : {target_games}", flush=True)

    engaged = False
    try:
        while True:
            proc_found = is_process_running(target_games)
            adb_state = get_adb_state()

            if proc_found and adb_state == "device":
                if not engaged:
                    print(f"[WATCHER] Processus détecté : {proc_found}", flush=True)
                    print(f"[WATCHER] Périphérique USB ADB détecté : {adb_state}", flush=True)
                    trigger_bridge(dry_run=args.dry_run)
                    engaged = True
                    if args.dry_run or args.once:
                        break
            else:
                if engaged:
                    print("[WATCHER] Déconnexion détectée. Réinitialisation de l'état du pont.", flush=True)
                    engaged = False

            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
