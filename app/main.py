import threading
import psutil
import time
import json
import webview
import os, sys
import shutil
import subprocess

#python -m app.main => top level folder as package root automatically
#python sets the working path including the file directory and the standard library locations
#so we need a line of code that tells python to get out of this folder and search in the others
#so this line adds the bridge folder to my python path and i can import stuff from it:
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bridge.antivirus_bridge import stream_scan

#this works as a bridge between python and javascript
#when we run await window.pywebview.api.clearPath("x") pywebview looks for a python method in the API class 
class API:
    def __init__(self):
        self.window = None #just a variable named window set to None (for this moment)
        self._scan_thread = None
        self._scan_stop_event = None

    def start_scan(self):
        try:
            if self.window:
                self.window.evaluate_js("startScanUI()")
        except Exception as e:
            print("[WARN] evaluate_js(startScanUI) failed:", e)

        # if a scan is already running, ignore
        if self._scan_thread and self._scan_thread.is_alive():
            print("[INFO] scan already running")
            return

        # create a stop event the thread will watch
        self._scan_stop_event = threading.Event()
        self._scan_thread = threading.Thread(target=self._run_scan, daemon=True)
        self._scan_thread.start()

    def stop_scan(self):
        """Signal a running scan to stop. The scanning thread should check the stop event."""
        try:
            if self._scan_stop_event:
                self._scan_stop_event.set()
                # wait a short time for thread to acknowledge
                if self._scan_thread:
                    self._scan_thread.join(timeout=2)
            else:
                print("[INFO] no active scan to stop")
        except Exception as e:
            print("[WARN] stop_scan failed:", e)

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
                elif line.startswith("#INTERRUPTED"):
                    if self.window:
                        self.window.evaluate_js("finishScanUI()")
                        self.window.evaluate_js("(function(){ const s = document.getElementById('status'); if(s) s.textContent='Scan interrupted.'; })()")
            except Exception as e:
                print("[Monitor handler] exception:", e)

        stream_scan(os.path.expanduser("~"), handle_progress, stop_event=self._scan_stop_event)

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



#__name__ is like a built in variable in python, so its value is automatically set to "__main__"
#but if you import that file into another file, not running it directly, python sets it to "app.main"
#we are protecting our app from auto-starting itself every time it’s imported somewhere
#because otherwise it would immediately start our GUI.
if __name__ == "__main__":
    #self.window = None (no link to UI)
    api = API()
    html_path = os.path.join(os.path.dirname(__file__), "index.html")

    #we are just creating our pywebview window
    window = webview.create_window(
        "Cleaner",
        f"file://{html_path}",
        js_api=api,
        width=960,
        height=720,
        resizable=False
    )

    #now the API can access and control our front-end
    #so from now we could run self.window.evaluate_js("something()")
    #and it would automatically run that function in the window we created before
    api.window = window
    threading.Thread(target=api.monitor_system, args=(window,), daemon=True).start()
    webview.start(debug=False)



    # IGNORE
    # python3 -m venv .venv
    # source .venv/bin/activate
    # pip install psutil pywebview