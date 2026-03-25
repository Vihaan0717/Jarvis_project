import time
import json
import os
from context.context_monitor import ContextMonitor

def get_presence_status():
    """
    JARVIS 2.0 Presence Monitor.
    Simple wrapper to check current state from the ContextMonitor.
    """
    state_file = "context/current_state.json"
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
                return state.get("presence_status", "Away")
        except:
            pass
    return "Away"

if __name__ == "__main__":
    # If run as standalone, acts as a logger
    print(f"Current User Presence: {get_presence_status()}")
