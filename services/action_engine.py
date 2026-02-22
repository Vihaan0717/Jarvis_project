import webbrowser
import datetime
import urllib.parse
import urllib.request
import re
import os
import pyautogui # New: The Ghost Keyboard!
from core.logger import get_logger

logger = get_logger("ActionEngine")

class ActionEngine:
    """JARVIS's digital hands for interacting with the PC and the web."""
    
    def __init__(self):
        logger.info("Action Engine initialized. Digital hands and Ghost Keyboard are online.")

    def get_time(self) -> str:
        now = datetime.datetime.now()
        current_time = now.strftime("%I:%M %p") 
        return f"Sir, the current time is {current_time}."

    def open_website(self, site_name: str, url: str) -> str:
        webbrowser.open(url)
        return f"Opening {site_name} for you now, Boss."

    def play_youtube(self, query: str) -> str:
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
            return "Sir, I encountered an error trying to play that video."

    def search_google(self, query: str) -> str:
        safe_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={safe_query}"
        webbrowser.open(url)
        return f"Pulling up Google search results for {query}."

    def open_application(self, command: str) -> str:
        command = command.lower()
        try:
            if "spotify" in command:
                os.system("start spotify:") 
                return "Launching Spotify."
            elif "code" in command:
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
            return "I encountered an error trying to launch that application."

    def control_media(self, command: str) -> str:
        """Uses the Ghost Keyboard to press physical media keys."""
        command = command.lower()
        logger.info(f"Triggering Ghost Keyboard for: {command}")
        
        if "pause" in command or "play" in command or "stop" in command:
            pyautogui.press("playpause")
            return "Executing playback control."
            
        elif "next" in command or "skip" in command or "forward" in command:
            pyautogui.press("nexttrack")
            return "Skipping to the next track."
            
        elif "previous" in command or "back" in command:
            pyautogui.press("prevtrack")
            return "Playing the previous track."
            
        elif "mute" in command or "silence" in command:
            pyautogui.press("volumemute")
            return "Muting system audio."
            
        elif "volume up" in command or "louder" in command:
            # Press it 5 times to make a noticeable difference
            for _ in range(5): pyautogui.press("volumeup")
            return "Increasing volume."
            
        elif "volume down" in command or "quieter" in command:
            for _ in range(5): pyautogui.press("volumedown")
            return "Decreasing volume."
            
        return "I am not sure which media control you wanted to trigger, Sir."