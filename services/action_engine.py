import webbrowser
import datetime
import urllib.parse
import urllib.request
import re
import os  # New: Allows JARVIS to interact directly with Windows
from core.logger import get_logger

logger = get_logger("ActionEngine")

class ActionEngine:
    """JARVIS's digital hands for interacting with the PC and the web."""
    
    def __init__(self):
        logger.info("Action Engine initialized. Digital hands are online.")

    def get_time(self) -> str:
        now = datetime.datetime.now()
        current_time = now.strftime("%I:%M %p") 
        logger.info(f"Checked time: {current_time}")
        return f"Sir, the current time is {current_time}."

    def open_website(self, site_name: str, url: str) -> str:
        logger.info(f"Opening browser to: {site_name}")
        webbrowser.open(url)
        return f"Opening {site_name} for you now, Boss."

    def play_youtube(self, query: str) -> str:
        logger.info(f"Finding the first video for: '{query}'")
        try:
            safe_query = urllib.parse.quote(query)
            html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={safe_query}")
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            
            if video_ids:
                url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                webbrowser.open(url)
                return f"Playing {query} on YouTube."
            else:
                return "I couldn't find any videos for that search, Boss."
        except Exception as e:
            logger.error(f"YouTube playback error: {e}")
            return "Sir, I encountered an error trying to play that video."

    def search_google(self, query: str) -> str:
        logger.info(f"Googling: '{query}'")
        safe_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={safe_query}"
        webbrowser.open(url)
        return f"Pulling up Google search results for {query}."

    def open_application(self, command: str) -> str:
        """Opens a local application using keyword scanning."""
        # Make the whole sentence lowercase so it's easy to read
        command = command.lower()
        logger.info(f"Scanning command for application targets: '{command}'")
        
        try:
            # Instead of deleting words, we just check if the app name is IN the sentence
            if "spotify" in command:
                # The colon ':' tells Windows to use the native URI protocol for Store Apps!
                os.system("start spotify:") 
                return "Launching Spotify for you, Sir."
            elif "code" in command or "vs code" in command:
                os.system("start code")
                return "Launching Visual Studio Code."
            elif "notepad" in command:
                os.system("start notepad")
                return "Launching Notepad."
            elif "calculator" in command or "calc" in command:
                os.system("start calc")
                return "Launching the Calculator."
            elif "chrome" in command:
                os.system("start chrome")
                return "Launching Google Chrome."
            else:
                return "I don't have a registered path for that application, Boss."
        except Exception as e:
            logger.error(f"App launch error: {e}")
            return "I encountered an error trying to launch that application."