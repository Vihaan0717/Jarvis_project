from tools.automation_tools import AutomationTools
from tools.toolbox import Toolbox
from core.logger import get_logger
from agents.messaging_agent import MessagingAgent

logger = get_logger("ActionEngine")

class ActionEngine:
    """
    JARVIS 2.0 Action Engine (Backward Compatibility Bridge).
    Wraps the new Toolbox and AutomationTools to support legacy calls.
    """
    def __init__(self):
        self.toolbox = Toolbox()
        self.automation = AutomationTools()
        self.messaging = MessagingAgent()
        logger.info("Action Engine Bridge initialized.")

    def get_time(self) -> str:
        """ Legacy support for get_time """
        from datetime import datetime
        now = datetime.now()
        return f"Sir, the current time is {now.strftime('%I:%M %p')}."

    def play_youtube(self, query: str) -> str:
        """ Legacy support for play_youtube """
        from tools.web_tools import WebTools
        return WebTools.play_youtube(query)

    def search_google(self, query: str) -> str:
        """ Legacy support for search_google """
        from tools.web_tools import WebTools
        return WebTools.search_google(query)

    def open_application(self, command: str) -> str:
        """ Legacy support for open_application """
        return self.automation.open_application(command)

    def open_website(self, site: str, url: str) -> str:
        """ Legacy support for open_website """
        from tools.web_tools import WebTools
        return WebTools.open_website(url)

    def control_media(self, command: str) -> str:
        """ Legacy support for control_media """
        return self.automation.control_media(command)

    def check_unread_whatsapp(self) -> str:
        """Fetch real unread messages from the persistent browser context."""
        import asyncio
        try:
            # Try to get the running loop (works if called from an async context)
            loop = asyncio.get_running_loop()
            return asyncio.run_coroutine_threadsafe(self.messaging.check_whatsapp_messages(), loop).result()
        except RuntimeError:
            # No running loop (typical in background threads/executors)
            return asyncio.run(self.messaging.check_whatsapp_messages())

    def send_whatsapp_message(self, contact: str, message: str) -> str:
        """ Use Playwright Messaging Agent for WhatsApp """
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            asyncio.run_coroutine_threadsafe(self.messaging.send_message(contact, message), loop)
        except RuntimeError:
            asyncio.run(self.messaging.send_message(contact, message))
        return f"Sir, I am transmitting your message to {contact} via the CDP bridge."

    def execute_command(self, command: str) -> str:
        """ Legacy support for execute_command """
        logger.info(f"Legacy ActionEngine: Processing '{command}'")
        # Direct common commands to automation tools
        command_lower = command.lower()
        if "open" in command_lower or "launch" in command_lower:
            return self.automation.open_application(command)
        elif any(key in command_lower for key in ["pause", "play", "next"]):
            return self.automation.control_media(command)
        
        return f"Legacy command '{command}' received. Routing to new architecture."

# Singleton instance for legacy imports if needed
action_engine_instance = ActionEngine()
