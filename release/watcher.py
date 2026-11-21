import argparse
import atexit
import ctypes
import os
import signal
import subprocess
import sys
import time

TARGET_PROCESSES = ["AMS2AVX.exe", "AMS2.exe", "acs.exe"]
DEFAULT_TARGET_GAMES = TARGET_PROCESSES
FILE_MAP_READ = 0x0004


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


def _is_sim_shm_active() -> str | None:
    if sys.platform != "win32":
        return None
    try:
        from ctypes import wintypes
        k32 = ctypes.windll.kernel32
        k32.OpenFileMappingW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
        k32.OpenFileMappingW.restype = wintypes.HANDLE
        k32.CloseHandle.argtypes = [wintypes.HANDLE]
        k32.CloseHandle.restype = wintypes.BOOL

        for shm_name, proc_name in (("$pcars2$", "AMS2AVX.exe"), ("Local\\acpmf_physics", "acs.exe"), ("acpmf_physics", "acs.exe")):
            h = k32.OpenFileMappingW(FILE_MAP_READ, False, shm_name)
            if h:
                k32.CloseHandle(h)
                return proc_name
    except Exception:
        pass
    return None


def is_process_running(targets: list[str]) -> str | None:
    if sys.platform == "win32":
        if targets == DEFAULT_TARGET_GAMES:
            shm_proc = _is_sim_shm_active()
            if shm_proc:
                return shm_proc
        try:
            out = subprocess.check_output(
                ["tasklist", "/NH"],
                text=True,
                errors="ignore",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                timeout=3,
            )
            out_lower = out.lower()
            for target in targets:
                if target.lower() in out_lower:
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
            errors="ignore",
            env=get_env(),
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            timeout=3,
        )
        if res.returncode == 0:
            return res.stdout.strip()
        else:
            if res.stderr:
                print(f"[WATCHER_DEBUG] adb get-state error: {res.stderr.strip()}", flush=True)
    except Exception as e:
        print(f"[WATCHER_DEBUG] adb get-state exception: {e}", flush=True)
    return None


def ensure_adb_reverse() -> bool:
    env = get_env()
    adb_bin = get_adb_binary()
    try:
        res_rev = subprocess.run(
            [adb_bin, "reverse", "tcp:5000", "tcp:5000"],
            env=env,
            capture_output=True,
            text=True,
            errors="ignore",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            timeout=3,
        )
        return res_rev.returncode == 0
    except Exception:
        return False


def trigger_bridge(dry_run: bool = False, launch_browser: bool = True):
    env = get_env()
    adb_bin = get_adb_binary()
    if dry_run:
        print(f"[DRY_RUN] {adb_bin} reverse tcp:5000 tcp:5000", flush=True)
        if launch_browser:
            print(f"[DRY_RUN] {adb_bin} shell am start -a android.intent.action.VIEW -d http://localhost:5000", flush=True)
    else:
        res_rev = subprocess.run(
            [adb_bin, "reverse", "tcp:5000", "tcp:5000"],
            env=env,
            capture_output=True,
            text=True,
            errors="ignore",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if res_rev.returncode != 0:
            print(f"[WATCHER_ERROR] adb reverse failed: {res_rev.stderr.strip()}", flush=True)

        if launch_browser:
            res_act = subprocess.run(
                [adb_bin, "shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", "http://localhost:5000"],
                env=env,
                capture_output=True,
                text=True,
                errors="ignore",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
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
    fail_count = 0
    try:
        while True:
            proc_found = is_process_running(target_games)
            adb_state = get_adb_state()

            if proc_found and adb_state == "device":
                fail_count = 0
                if not engaged:
                    print(f"[WATCHER] Processus détecté : {proc_found}", flush=True)
                    print(f"[WATCHER] Périphérique USB ADB détecté : {adb_state}", flush=True)
                    trigger_bridge(dry_run=args.dry_run)
                    engaged = True
                    if args.dry_run or args.once:
                        break
            else:
                if engaged:
                    fail_count += 1
                    if fail_count >= 3:
                        print("[WATCHER] Déconnexion détectée. Réinitialisation de l'état du pont.", flush=True)
                        engaged = False
                        fail_count = 0

            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
