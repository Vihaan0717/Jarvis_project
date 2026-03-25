import psutil
import pygetwindow as gw
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.logger import get_logger
from core.health_monitor import HealthMonitor

logger = get_logger("SystemWatcher")

class ProjectFileHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory:
            self.callback(event.src_path)

class SystemWatcher:
    """
    Monitors OS activity (active window) and project file changes to provide context to JARVIS.
    """
    def __init__(self, project_path, on_context_change):
        self.project_path = project_path
        self.on_context_change = on_context_change
        self.running = False
        self.last_active_window = ""
        
        # File observer
        self.observer = Observer()
        self.handler = ProjectFileHandler(self._handle_file_change)

    def _handle_file_change(self, file_path):
        logger.info(f"File modified: {file_path}")
        context = {
            "type": "FILE_CHANGE",
            "file": file_path,
            "timestamp": time.time()
        }
        self.on_context_change(context)

    def _monitor_windows(self):
        while self.running:
            try:
                # 1. Active Window
                active_window = gw.getActiveWindow()
                title = active_window.title if active_window else "Idle"
                
                # 2. Vitals from HealthMonitor
                vitals = HealthMonitor.check_vitals()
                
                if title != self.last_active_window:
                    logger.info(f"Active window changed: {title}")
                    self.last_active_window = title
                
                context = {
                    "type": "OS_CONTEXT",
                    "context": {
                        "active_window": title,
                        "cpu_percent": vitals["cpu_percent"],
                        "memory_percent": vitals["ram_percent"],
                        "battery_percent": vitals["battery_percent"],
                        "is_plugged_in": vitals["plugged_in"],
                        "biological_state": vitals["biological_state"]
                    },
                    "timestamp": time.time()
                }
                self.on_context_change(context)
            except Exception as e:
                logger.error(f"Error monitoring system: {e}")
            
            time.sleep(2) # Check every 2 seconds

    def start(self):
        self.running = True
        
        # Start file observer
        self.observer.schedule(self.handler, self.project_path, recursive=True)
        self.observer.start()
        
        # Start window monitor thread
        self.window_thread = threading.Thread(target=self._monitor_windows, daemon=True)
        self.window_thread.start()
        logger.info("System Watcher started.")

    def stop(self):
        self.running = False
        self.observer.stop()
        self.observer.join()
        logger.info("System Watcher stopped.")

if __name__ == "__main__":
    # Test
    def test_callback(data):
        print(f"DEBUG: Context Update -> {data}")
    
    watcher = SystemWatcher(".", test_callback)
    watcher.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
