import threading
import queue
import time
from core.logger import get_logger
from services.temporal_mind import TemporalMind

logger = get_logger("BackgroundBrain")

class BackgroundBrain:
    """JARVIS's background daemon that monitors time, apps, and health."""
    
    def __init__(self, alert_queue: queue.Queue):
        self.alert_queue = alert_queue
        self.running = False
        self.thread = None
        self.temporal_mind = TemporalMind() # The internal clock is online!
        
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._background_loop, daemon=True)
            self.thread.start()
            logger.info("Background Brain activated. Daemon thread is listening.")
            
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Background Brain powered down.")
        
    def _background_loop(self):
        while self.running:
            try:
                current_time = time.strftime("%H:%M")
                
                # 1. Ask Temporal Mind to check the JSON for active reminders
                due_reminders = self.temporal_mind.check_reminders(current_time)
                
                for reminder in due_reminders:
                    self.alert_queue.put({
                        "type": "reminder",
                        "message": f"Excuse me Boss, but it is time to {reminder['task']}.",
                        "timestamp": time.time()
                    })
                    logger.info(f"Triggered reminder: {reminder['task']}")
                    
                # 2. Check WhatsApp (Module 3 placeholder)
                
                # Sleep for 10 seconds (Checking HH:MM every single second wastes CPU)
                time.sleep(10) 
                
            except Exception as e:
                logger.error(f"Background Brain error: {e}")
                time.sleep(10)