import webview
import os, shutil

# Our API it's a bridge between our Front-end and Back-end.
class API:
    def terminal(self, text):
        print("@Developer: " + text)


    def clearPath(self, text: str):
        paths = {
            "logs": [
                os.path.expanduser("~/Library/Logs"),
                "/Library/Logs",
                "/private/var/log"
            ],
            "cache": [
                os.path.expanduser("~/Library/Caches")
            ],
            "downloads": [
                os.path.expanduser("~/Downloads")
            ]
        }

        text = text.strip().lower()
        if text not in paths:
            print(f"[ERRORE] Argomento non valido: {text}")
            return

        target_dirs = paths[text]
        removed_count = 0

        for base_dir in target_dirs:
            if not os.path.exists(base_dir):
                print(f"(MANCANTE) {base_dir}")
                continue

            print(f"Pulizia in corso: {base_dir}")

            for entry in os.scandir(base_dir):
                try:
                    if entry.is_file():
                        os.remove(entry.path)
                        print(f"(REMOVE) {entry.path}")
                    elif entry.is_dir():
                        shutil.rmtree(entry.path)
                        print(f"(RMTREE) {entry.path}")
                    removed_count += 1
                except Exception as e:
                    print(f"(SKIP) {entry.path} -> {e}")

        msg = f"{text.capitalize()} cleared: {removed_count} items removed"
        print(msg)

        try:
            execfu = f"notification('{msg}', 'bg-teal-600')"
            window.evaluate_js(execfu)
        except Exception as e:
            print(f"[INFO] Notification skipped: {e}")



# Webview
if __name__ == "__main__":
    api = API()
    html_path = os.path.abspath("index.html")

    window = webview.create_window(
        "Cleaner",
        f"file://{html_path}",
        js_api=api,
        width=800,
        height=600
    )

    webview.start(debug=False)