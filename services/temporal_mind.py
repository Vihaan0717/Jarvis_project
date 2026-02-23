import json
import os
import re
from datetime import datetime
from core.logger import get_logger

logger = get_logger("TemporalMind")

class TemporalMind:
    """JARVIS's time-awareness system for reminders and schedules."""
    
    def __init__(self):
        self.filepath = "reminders.json"
        if not os.path.exists(self.filepath):
            self._save_reminders({})
        logger.info("Temporal Mind initialized.")
        
    def _load_reminders(self):
        with open(self.filepath, 'r') as f:
            try: return json.load(f)
            except: return {}
        
    def _save_reminders(self, data):
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=4)
            
    def set_reminder(self, user_input: str) -> str:
        """Parses the voice command and saves the reminder."""
        try:
            # 1. Clean the messy voice input
            clean_input = user_input.lower().replace("jarvis", "").replace("remind me to ", "").replace("remind me ", "").strip()
            
            if " at " not in clean_input:
                return "Sir, please specify a time using the word 'at', for example: 'Remind me to study at 7 pm'."
            
            # 2. Split into Task and Time
            task, time_str = clean_input.split(" at ", 1)
            time_str = time_str.strip()
            
            # 3. Convert "5 pm" to "17:00"
            parsed_time = self._convert_to_24h(time_str)
            if not parsed_time:
                return f"I couldn't understand the time format for '{time_str}'. Please use a standard format like '5 PM'."
            
            # 4. Save to JSON database
            reminders = self._load_reminders()
            reminder_id = str(datetime.now().timestamp())
            reminders[reminder_id] = {"task": task.strip(), "time": parsed_time}
            self._save_reminders(reminders)
            
            logger.info(f"Reminder created: '{task}' at {parsed_time}")
            return f"I have set a reminder to {task} at {time_str}, Boss."
            
        except Exception as e:
            logger.error(f"Failed to parse reminder: {e}")
            return "I had trouble processing that reminder, Sir."
            
    def _convert_to_24h(self, time_str: str) -> str:
        """Regex helper to convert messy voice times to strict 24-hour HH:MM format."""
        match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_str.lower())
        if not match: return None
        
        hours = int(match.group(1))
        mins = int(match.group(2)) if match.group(2) else 0
        meridian = match.group(3)
        
        if meridian == 'pm' and hours != 12: hours += 12
        elif meridian == 'am' and hours == 12: hours = 0
            
        return f"{hours:02d}:{mins:02d}"
        
    def check_reminders(self, current_time_24h: str) -> list:
        """Reads the JSON and returns tasks that match the current system time."""
        reminders = self._load_reminders()
        alerts = []
        keys_to_delete = []
        
        for r_id, data in reminders.items():
            if data["time"] == current_time_24h:
                alerts.append(data)
                keys_to_delete.append(r_id)
                
        # Auto-delete reminders that have already triggered
        if keys_to_delete:
            for key in keys_to_delete: del reminders[key]
            self._save_reminders(reminders)
            
        return alerts