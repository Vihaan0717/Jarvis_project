from tools.toolbox import Toolbox
from core.logger import get_logger

logger = get_logger("AutomationAgent")

class AutomationAgent:
    """
    JARVIS 2.0 Automation Agent.
    Executes tasks safely through the standardized Toolbox.
    """
    def __init__(self):
        self.toolbox = Toolbox()
        logger.info("Automation Agent initialized.")

    def execute_tool(self, tool_name: str, parameters: dict):
        """
        The only way for JARVIS to interact with the system.
        """
        logger.info(f"AutomationAgent: Executing {tool_name}")
        return self.toolbox.execute_tool(tool_name, parameters)
