import webview
import os, shutil

# Our API it's a bridge between our Front-end and Back-end.
class API:
    def terminal(self, text):
        print("@Developer: " + text)

    def cache(self):
        print("CLEARING CACHE")
        count = 0
        # cache_dir diventa il nostro percorso grazie a os.path.expander che aggiunge la home directory.
        cache_dir = os.path.expanduser("~/Library/Caches")
        # Leggiamo i file dentro la cartella tramite os.listdir 
        for item in os.listdir(cache_dir):
            # Cambio il nome della cartella con il percorso completo
            path = os.path.join(cache_dir, item)
            try:
                # Verifichiamo se si tratta di un file regolare
                # Se restituisce false si tratta di una directory o di un'altro non-file.
                if os.path.isfile(path):
                    # Andiamo a rimuovere il file, ma solo se non si trova in esecuzione o se abbiamo i permessi.
                    os.remove(path)
                    print("(OS.REMOVE) " + path)
                else:
                    # Andiamo a rimuovere forzatamente qualsiasi cartella o file target.
                    shutil.rmtree(path)
                    print("(SHUTIL.RMTREE) " + path)
            except Exception as e:
                # Se saltiamo un file o una directory per qualsiasi motivo, stampiamo quale.
                count += 1
                print("(SKIP) ", path, e)
                execfu = "notification('Cache directory cleared with success (" + str(count) + " skipped)', 'bg-teal-600')"
                window.evaluate_js(execfu)

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