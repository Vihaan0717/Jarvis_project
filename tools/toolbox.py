from tools.automation_tools import AutomationTools
from tools.web_tools import WebTools
from tools.file_tools import FileTools
from tools.project_tools import ProjectTools
from core.logger import get_logger

logger = get_logger("Toolbox")

class Toolbox:
    """
    JARVIS 2.0 Unified Toolbox.
    Standardized interface for all tool executions.
    """
    def __init__(self):
        self.automation = AutomationTools()
        self.web = WebTools()
        self.file = FileTools()
        self.project = ProjectTools()

    def execute_tool(self, tool_name: str, parameters: dict):
        """
        Safe tool execution entry point.
        """
        logger.info(f"Toolbox: Executing {tool_name} with {parameters}")
        
        try:
            if tool_name == "open_application":
                return self.automation.open_application(parameters.get("app_name"))
            elif tool_name == "control_media":
                return self.automation.control_media(parameters.get("command"))
            elif tool_name == "open_website":
                return self.web.open_website(parameters.get("url"))
            elif tool_name == "search_google":
                return self.web.search_google(parameters.get("query"))
            elif tool_name == "play_youtube":
                return self.web.play_youtube(parameters.get("query"))
            elif tool_name == "list_files":
                return self.file.list_files(parameters.get("directory"))
            elif tool_name == "create_project":
                return self.project.create_project(parameters.get("name"))
            elif tool_name == "delete_project":
                return self.project.delete_project(parameters.get("name"))
            elif tool_name == "open_ide":
                return self.project.open_ide(parameters.get("path"))
            else:
                return f"Error: Tool {tool_name} not found."
        except Exception as e:
            logger.error(f"Toolbox execution error: {e}")
            return "Tool execution failed."

