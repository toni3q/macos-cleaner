import os
import sys
import time
import threading

def stream_scan(path, handle_progress):
    """
    Simulates an antivirus directory scan and streams progress lines to the callback.
    Replace the fake scanning part later with real Rust bridge logic.
    """

    # Collect all files first
    all_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            all_files.append(os.path.join(root, file))

    total = len(all_files)
    handle_progress(f"#TOTAL {total}")

    count = 0
    for file_path in all_files:
        count += 1
        handle_progress(f"#PROGRESS {count} {file_path}")
        time.sleep(0.01)  # simulate scan delay

    handle_progress("#DONE")