from core.logger import get_logger

logger = get_logger("ResponseEngine")

class ResponseEngine:
    """
    JARVIS 2.0 Response Engine.
    Safe automated replies for trusted contacts.
    """
    def __init__(self):
        self.trusted_contacts = ["kanna", "mom", "boss", "nikhil"]
        logger.info("Response Engine initialized.")

    def generate_reply(self, contact, message_text):
        contact = contact.lower()
        if contact not in self.trusted_contacts:
            return "Hello! I am JARVIS, an AI assistant. I'll notify my Boss about your message."
        
        # Simple rule-based logic for demo (Feature 7)
        if "hello" in message_text.lower() or "hi" in message_text.lower():
            return f"Hello! My Boss is currently away, but I've notified them."
        
        return None # No auto-reply generated
