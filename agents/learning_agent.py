import sqlite3
import os
from datetime import datetime
from core.logger import get_logger

logger = get_logger("LearningAgent")

class LearningAgent:
    """
    JARVIS 2.0 Learning Engine.
    Tracks user interactions to learn response patterns.
    """
    def __init__(self, db_path="memory/learning.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS interactions
                     (id INTEGER PRIMARY KEY, contact TEXT, intent TEXT, 
                      user_response TEXT, response_time_ms INTEGER, timestamp DATETIME)''')
        conn.commit()
        conn.close()

    def record_interaction(self, contact, intent, response, response_time_ms):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO interactions (contact, intent, user_response, response_time_ms, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (contact, intent, response, response_time_ms, datetime.now()))
        conn.commit()
        conn.close()
        logger.info(f"LearningAgent: Recorded interaction for {contact}.")

    def get_common_patterns(self, contact):
        # Placeholder for pattern detection logic
        return []
