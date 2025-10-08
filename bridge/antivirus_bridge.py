import os
import sys
import time
import threading

def stream_scan(path, handle_progress, stop_event=None):
    # Collect all files first
    all_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            all_files.append(os.path.join(root, file))

    total = len(all_files)
    handle_progress(f"#TOTAL {total}")

    count = 0
    for file_path in all_files:
        # check for cancellation
        if stop_event is not None and stop_event.is_set():
            handle_progress("#INTERRUPTED")
            return

        count += 1
        handle_progress(f"#PROGRESS {count} {file_path}")
        time.sleep(0.01)  # simulate scan delay

    handle_progress("#DONE")