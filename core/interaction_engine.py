from core.logger import get_logger
import random

logger = get_logger("InteractionEngine")

class InteractionEngine:
    """
    JARVIS 2.0 Interaction Engine.
    Manages user feedback loops and natural interaction cues.
    """
    def __init__(self):
        self.greetings = ["At your service, Sir.", "What can I do for you, Boss?", "Systems online. Ready for input."]
        self.witty_remarks = ["Well, that was unexpected.", "I've seen slower processors, but not many.", "Efficiency is up by 0.05%. You're welcome."]

    def get_greeting(self):
        return random.choice(self.greetings)

    def acknowledge(self):
        return "Understood, Sir."

    def finalize(self, success=True):
        if success:
            return "Task completed as requested."
        return "I'm afraid I encountered an obstacle, Sir."
