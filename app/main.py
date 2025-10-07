import threading
import psutil
import time
import json
import webview
import os, sys
import shutil
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bridge.antivirus_bridge import stream_scan

class API:
    def __init__(self):
        self.window = None

    def start_scan(self):
        try:
            if self.window:
                self.window.evaluate_js("startScanUI()")
        except Exception as e:
            print("[WARN] evaluate_js(startScanUI) failed:", e)

        threading.Thread(target=self._run_scan, daemon=True).start()

    def _run_scan(self):
        def handle_progress(line):
            try:
                if line.startswith("#TOTAL"):
                    total = line.split()[1]
                    if self.window:
                        self.window.evaluate_js(f"updateTotal({total})")
                elif line.startswith("#PROGRESS"):
                    parts = line.split(" ", 2)
                    count = parts[1]
                    file_path = parts[2] if len(parts) > 2 else ""
                    if self.window:
                        # escape single quotes in file_path to avoid JS syntax error
                        safe_path = file_path.replace("'", "\\'")
                        self.window.evaluate_js(f"updateProgress({count}, '{safe_path}')")
                elif line.startswith("#DONE"):
                    if self.window:
                        self.window.evaluate_js("finishScanUI()")
            except Exception as e:
                print("[Monitor handler] exception:", e)

        stream_scan(os.path.expanduser("~"), handle_progress)

    def clearPath(self, text: str):
        home = os.path.expanduser("~")
        paths = {
            "logs": [
                f"{home}/Library/Logs",
                "/Library/Logs",
                "/private/var/log"
            ],
            "cache": [
                f"{home}/Library/Caches",
                "/Library/Caches",
                "/private/tmp",
                "/private/var/tmp"
            ],
            "downloads": [
                f"{home}/Downloads"
            ],
            "trash": [
                f"{home}/.Trash",
                "/Volumes"
            ],
            "leftovers": [
                f"{home}/Library/Application Support/",
                f"{home}/Library/Preferences/",
                f"{home}/Library/Containers/"
            ]
        }

        text = text.strip().lower()
        if text == "all":
            target_dirs = [p for v in paths.values() for p in v]
        elif text in paths:
            target_dirs = paths[text]
        else:
            print(f"[ERRORE] Argomento non valido: {text}")
            return

        removed_count = 0
        for base_dir in target_dirs:
            if not os.path.exists(base_dir):
                print(f"(MANCANTE) {base_dir}")
                continue

            print(f"Pulizia in corso: {base_dir}")
            if base_dir == "/Volumes":
                for vol in os.listdir("/Volumes"):
                    trash_path = os.path.join("/Volumes", vol, ".Trashes")
                    if os.path.exists(trash_path):
                        try:
                            shutil.rmtree(trash_path, ignore_errors=True)
                            print(f"(RMTREE) {trash_path}")
                            removed_count += 1
                        except Exception as e:
                            print(f"(SKIP) {trash_path} -> {e}")
                continue

            for entry in os.scandir(base_dir):
                try:
                    if entry.is_file():
                        os.remove(entry.path)
                        print(f"(REMOVE) {entry.path}")
                    elif entry.is_dir():
                        shutil.rmtree(entry.path, ignore_errors=True)
                        print(f"(RMTREE) {entry.path}")
                    removed_count += 1
                except Exception as e:
                    print(f"(SKIP) {entry.path} -> {e}")

        if text in ["all", "cache"]:
            try:
                subprocess.run(["purge"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("(CMD) purge eseguito (senza sudo)")
            except Exception as e:
                print(f"[INFO] purge non eseguito: {e}")
        msg = f"{text.capitalize()} cleared: {removed_count} items removed"
        print(msg)
        try:
            if self.window:
                execfu = f"notification('{msg}', 'bg-teal-600')"
                self.window.evaluate_js(execfu)
        except Exception as e:
            print(f"[INFO] Notification skipped: {e}")

    def get_cpu_temp(self):
        try:
            temp_output = subprocess.check_output(["osx-cpu-temp"]).decode().strip()
            temp = temp_output.replace("°C", "").strip()
            return float(temp)
        except Exception:
            return None

    def monitor_system(self, window):
        while True:
            try:
                cpu = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory().percent
                disk = psutil.disk_usage("/").percent
                temp = self.get_cpu_temp()
                data = {
                    "cpu": cpu,
                    "memory": memory,
                    "disk": disk,
                    "temperature": temp if temp is not None else "N/A"
                }
                js = f"updateVitals({json.dumps(data)})"
                try:
                    window.evaluate_js(js)
                except Exception as e:
                    pass
            except Exception as e:
                print(f"[Monitor] {e}")
            time.sleep(2)  # update every 2 seconds


if __name__ == "__main__":
    api = API()
    html_path = os.path.join(os.path.dirname(__file__), "index.html")

    window = webview.create_window(
        "Cleaner",
        f"file://{html_path}",
        js_api=api,
        width=960,
        height=720,
        resizable=False
    )

    api.window = window
    threading.Thread(target=api.monitor_system, args=(window,), daemon=True).start()
    webview.start(debug=False)