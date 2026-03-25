import pyautogui
import os
import time
from core.logger import get_logger

logger = get_logger("AutomationTools")

class AutomationTools:
    """
    Tools for OS and Application control.
    """
    @staticmethod
    def open_application(command: str) -> str:
        try:
            if "spotify" in command.lower():
                pyautogui.press('win')
                time.sleep(0.5)
                pyautogui.write('spotify')
                pyautogui.press('enter')
                return "Launching Spotify."
            elif "whatsapp" in command.lower():
                os.system("start whatsapp:")
                return "Opening WhatsApp."
            elif "notepad" in command.lower():
                os.system("start notepad")
                return "Launching Notepad."
            return f"No path registered for {command}."
        except Exception as e:
            logger.error(f"Automation failed: {e}")
            return "Application launch failed."

    @staticmethod
    def control_media(command: str) -> str:
        command = command.lower()
        if "pause" in command or "play" in command:
            pyautogui.press("playpause")
            return "Media toggled."
        elif "next" in command:
            pyautogui.press("nexttrack")
            return "Next track."
        return "Unknown media command."
