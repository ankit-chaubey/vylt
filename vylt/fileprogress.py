import os
import time

def track_progress(path, bar, stop, interval=0.05):
    last = 0
    while not stop.is_set():
        try:
            if os.path.exists(path):
                size = os.path.getsize(path)
                delta = size - last
                if delta > 0:
                    bar.update(delta)
                    last = size
        except Exception:
            pass
        time.sleep(interval)
