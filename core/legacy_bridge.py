from core.commander import Commander
from agents.automation_agent import AutomationAgent
from core.logger import get_logger

logger = get_logger("LegacyBridge")

class LegacyBridge:
    """
    JARVIS 2.0 Legacy Bridge.
    Routes legacy entry points through the new modular Commander.
    """
    def __init__(self):
        self.commander = Commander()
        self.automation = AutomationAgent()
        logger.info("Legacy Bridge status: Operational.")

    def handle_voice_input(self, raw_text: str):
        """
        Entry point for existing voice recognition modules.
        """
        logger.info(f"LegacyBridge: Intercepted voice input: {raw_text}")
        return self.commander.plan_execute_verify(raw_text)

    def handle_ui_command(self, command: str, params: dict = None):
        """
        Entry point for existing GUI calls.
        """
        logger.info(f"LegacyBridge: Intercepted UI command: {command}")
        # Map legacy UI calls to the new execution agent
        return self.automation.execute_tool(command, params or {})

# Singleton instance for legacy imports
legacy_bridge = LegacyBridge()
