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
                # The ultimate fallback: Use the Ghost Keyboard to search Windows!
                import pyautogui
                import time
                pyautogui.press('win')
                time.sleep(0.5) # Wait half a second for the menu to pop up
                pyautogui.write('spotify')
                time.sleep(0.5)
                pyautogui.press('enter')
                return "Launching Spotify."
            elif "whatsapp" in command: # NEW BLOCK
                import pyautogui
                import time
                pyautogui.press('win')
                time.sleep(0.5)
                pyautogui.write('whatsapp')
                time.sleep(0.5)
                pyautogui.press('enter')
                return "Opening WhatsApp."
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

    def send_whatsapp_message(self, contact_name: str, message: str) -> str:
        """Automates WhatsApp using Multi-Modal Launching and Computer Vision."""
        import pyautogui
        import time
        import os
        
        logger.info(f"Initiating robust Comms Relay to {contact_name}...")
        
        valid_contacts = ["kanna", "mom", "friend", "nikhil"]
        target_contact = None
        for contact in valid_contacts:
            if contact in contact_name.lower() or "karn" in contact_name.lower() and contact == "kanna":
                target_contact = contact
                break
                
        if not target_contact:
            return f"I do not have a registered contact for {contact_name}, Sir."
            
        try:
            # --- METHOD 1: Multi-Modal Launch Chain ---
            logger.info("Attempting primary launch via URI protocol...")
            # Try launching instantly via Windows URI
            os.system("start whatsapp:") 
            time.sleep(1) # Brief pause to let Windows react
            
            # --- METHOD 2: Visual Screen Monitoring ---
            logger.info("Visually scanning monitor for WhatsApp interface...")
            app_loaded = False
            
            # Instead of a blind sleep, JARVIS actively watches the screen for up to 15 seconds
            for attempt in range(15): 
                try:
                    # He looks for the exact pixels of the screenshot you saved
                    target = pyautogui.locateOnScreen('whatsapp_search.png', confidence=0.8)
                    if target:
                        logger.info("Visual confirmation: WhatsApp interface detected.")
                        app_loaded = True
                        break
                except pyautogui.ImageNotFoundException:
                    pass # Ignore if he doesn't see it yet
                    
                time.sleep(1) # Check the screen once per second
                
            if not app_loaded:
                # Fallback to Taskbar Search if the URI failed and the screen is empty
                logger.warning("Primary launch failed. Initiating Taskbar override...")
                pyautogui.press('win')
                time.sleep(0.5)
                pyautogui.write('whatsapp')
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(5) # Blind wait as an absolute last resort
            
            # --- METHOD 3: Execution ---
            # Now that he *knows* the app is open, he executes the keystrokes
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(1)
            pyautogui.write(target_contact)
            time.sleep(2) 
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.write(message)
            time.sleep(0.5)
            pyautogui.press('enter')
            
            return f"Message successfully transmitted to {target_contact}."
            
        except Exception as e:
            logger.error(f"Comms automation failed: {e}")
            return "I encountered a critical error while operating the desktop interface."