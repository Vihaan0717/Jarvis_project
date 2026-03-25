import psutil
import pygetwindow as gw
import json
import time
import threading
import os
from datetime import datetime
from pynput import mouse, keyboard

class ContextMonitor:
    """
    JARVIS 2.0 Context Awareness Engine.
    Monitors active windows, system load, and user idle time.
    """
    def __init__(self, output_path="context/current_state.json", interval=5):
        self.output_path = output_path
        self.interval = interval
        self.running = False
        self.thread = None
        self.last_input_time = time.time()
        self.idle_threshold = 120 # 2 minutes
        
        # Initialize the file if it doesn't exist
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # Start input listeners
        self.mouse_listener = mouse.Listener(on_move=self._on_activity, on_click=self._on_activity, on_scroll=self._on_activity)
        self.key_listener = keyboard.Listener(on_press=self._on_activity)
        self.mouse_listener.start()
        self.key_listener.start()

    def _on_activity(self, *args):
        self.last_input_time = time.time()

    def get_active_window(self):
        try:
            window = gw.getActiveWindow()
            if window:
                return window.title
        except Exception:
            pass
        return "Unknown"

    def get_user_idle_time(self):
        """Returns seconds since last keyboard/mouse activity."""
        return time.time() - self.last_input_time

    def update_state(self):
        while self.running:
            idle_seconds = int(self.get_user_idle_time())
            presence = "Home" if idle_seconds < self.idle_threshold else "Away"
            
            state = {
                "active_app": self.get_active_window(),
                "cpu_usage": psutil.cpu_percent(),
                "user_idle_seconds": idle_seconds,
                "presence_status": presence,
                "battery_level": psutil.sensors_battery().percent if psutil.sensors_battery() else 100,
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                with open(self.output_path, "w") as f:
                    json.dump(state, f, indent=4)
            except Exception as e:
                pass # Avoid crashing context engine on file lock
            
            time.sleep(self.interval)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.update_state, daemon=True)
            self.thread.start()
            print("Context Monitor started with Presence Tracking.")

    def stop(self):
        self.running = False
        self.mouse_listener.stop()
        self.key_listener.stop()
        if self.thread:
            self.thread.join()

if __name__ == "__main__":
    monitor = ContextMonitor()
    monitor.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
