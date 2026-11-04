import os
import select
import subprocess
import sys
import time

PYTHON_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "bin", "python3")
if not os.path.exists(PYTHON_BIN):
    PYTHON_BIN = sys.executable

BRIDGE_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bridge.py")
WATCHER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "watcher.py")

def main():
    env = os.environ.copy()
    if not os.access(os.path.expanduser("~"), os.W_OK):
        env["HOME"] = "/tmp"

    # 1. Démarrer bridge.py
    bridge_proc = subprocess.Popen(
        [PYTHON_BIN, BRIDGE_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
    )

    try:
        time.sleep(1)

        # 2. Déclencher watcher.py (mode mock avec --once)
        subprocess.run(
            [PYTHON_BIN, WATCHER_SCRIPT, "--mock-process", "python3", "--once"],
            timeout=5,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )

        # 3. Message d'invite utilisateur
        print("[USER_PROMPT] PRET: Appuyez sur le bouton DRS sur votre telephone maintenant (fenetre de 15s)...", flush=True)

        # 4. Surveillance non bloquante des logs avec timeout strict de 15s
        start_time = time.time()
        timeout = 15.0
        success = False

        while True:
            remaining = timeout - (time.time() - start_time)
            if remaining <= 0:
                break

            rlist, _, _ = select.select([bridge_proc.stdout], [], [], min(remaining, 0.5))
            if rlist:
                line = bridge_proc.stdout.readline()
                if not line:
                    break
                line_str = line.strip()
                if line_str:
                    print(line_str, flush=True)
                if "[MOCK_INJECTOR] Action: drs | Type: tap" in line_str:
                    success = True
                    print("[TEST_RESULT] SUCCESS: Evenement tactile DRS recu avec succes!", flush=True)
                    break

        if not success:
            print("[TEST_RESULT] TIMEOUT_EXPIRED", flush=True)
            sys.exit(1)

    finally:
        bridge_proc.terminate()
        try:
            bridge_proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            bridge_proc.kill()

if __name__ == "__main__":
    main()
