import threading
import queue
import time
from core.logger import get_logger
from agents.planning_agent import TemporalMind

logger = get_logger("BackgroundBrain")

class BackgroundBrain:
    """JARVIS's background daemon that monitors time, apps, and health."""
    
    def __init__(self, alert_queue: queue.Queue):
        self.alert_queue = alert_queue
        self.running = False
        self.thread = None
        self.temporal_mind = TemporalMind()
        
        # News tracking state
        from services.api_hub import APIHub
        self.api_hub = APIHub()
        self.notified_news = set()
        self.last_news_check = 0
        
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
                    
                # 2. Priority News Monitoring (Every 1 hour)
                now = time.time()
                if now - self.last_news_check > 3600:
                    logger.info("Background check: Fetching high-priority news...")
                    urgent_news = self.api_hub.get_filtered_news(keywords=["IT", "war", "tech", "politics", "India", "conflict"])
                    
                    for article in urgent_news:
                        if article["title"] not in self.notified_news:
                            self.alert_queue.put({
                                "type": "news_alert",
                                "message": f"Urgent Update: {article['title']}",
                                "timestamp": now
                            })
                            self.notified_news.add(article["title"])
                            # Limit to 1 alert at a time to avoid spamming
                            break 
                    
                    self.last_news_check = now
                
                # 3. Check WhatsApp (Module 3 placeholder)
                
                # Sleep for 10 seconds
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Background Brain error: {e}")
                time.sleep(10)