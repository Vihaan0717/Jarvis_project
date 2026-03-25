import psutil
import json
import time
import os
from core.logger import get_logger

logger = get_logger("SystemMonitor")

class SystemMonitor:
    """
    JARVIS 2.0 Autonomous Brain Monitor.
    Runs as a persistent background process to monitor system context and trigger alerts.
    """
    def __init__(self, context_path="context/current_state.json"):
        self.context_path = context_path
        self.running = True

    def check_rules(self, state: dict):
        """
        Executes proactive rules based on system state.
        """
        # Rule: Low Power Warning
        if state.get("battery_level", 100) < 20 and "vscode" in state.get("active_app", "").lower():
            msg = "Low Power Warning: Your battery is below 20% and you are coding. Please connect a charger, Sir."
            logger.warning(msg)
            print(f"ALERT: {msg}")

        # Rule: High CPU Usage
        if state.get("cpu_usage", 0) > 90:
            logger.warning("High CPU load detected. Monitor system thermal stability.")

    def run(self):
        print("Autonomous System Monitor online. Watching the vitals, Sir.")
        while self.running:
            if os.path.exists(self.context_path):
                try:
                    with open(self.context_path, "r") as f:
                        state = json.load(f)
                    self.check_rules(state)
                except Exception as e:
                    logger.error(f"Monitor error reading context: {e}")
            
            time.sleep(10) # Run check every 10 seconds

    def stop(self):
        self.running = False

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.run()
