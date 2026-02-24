import webbrowser
import datetime
import urllib.parse
import urllib.request
import re
import os
import pyautogui # New: The Ghost Keyboard!
import pytesseract
from PIL import Image
from core.logger import get_logger

# Point Python to the Tesseract engine you just installed!
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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

    def check_unread_whatsapp(self) -> str:
        """Uses Computer Vision to find unread badges and pyperclip to read the text."""
        import pyautogui
        import time
        import os
        import pyperclip

        logger.info("Initiating Incoming Comms Poller...")
        try:
            # 1. Pull up WhatsApp using the URI shortcut
            logger.info("Opening WhatsApp...")
            os.system("start whatsapp:")
            time.sleep(2) # Give it a moment to render

            # 2. Scan the screen for the green badge
            logger.info("Visually scanning for unread_badge.png...")
            try:
                # We use locateCenterOnScreen so JARVIS knows exactly where to click
                badge_location = pyautogui.locateCenterOnScreen('unread_badge.png', confidence=0.8)
                
                if badge_location:
                    logger.info("Unread badge detected! Engaging...")
                    pyautogui.click(badge_location)
                    time.sleep(1) # Wait for the specific chat to load on the right side
# 3. Focus and Auto-Scroll to the bottom
                    time.sleep(1.5)
                    screen_width, screen_height = pyautogui.size()
                    
                    # Click lower to hit the "Type a message" box (changed from -100 to -60)
                    pyautogui.click(badge_location.x + 400, screen_height - 60)
                    time.sleep(1.0) 

                    # --- THE MOUSE FLICK ---
                    # Move the mouse to the top-left corner of the screen!
                    # This guarantees we aren't hovering over any messages, hiding the emoji popups!
                    pyautogui.moveTo(10, 10)
                    time.sleep(0.5) # Give WhatsApp half a second to hide the hover menu

                    # 4. Take the MASSIVE screenshot with a wider lens
                    # Move only 50px right of the badge to capture the extreme left edge of the chat!
                    crop_x = int(badge_location.x + 50) 
                    crop_y = 100 
                    crop_w = int(screen_width - crop_x - 50)  
                    crop_h = int(screen_height - 150) 
                    
                    logger.info("Taking screenshot...")
                    chat_image = pyautogui.screenshot(region=(crop_x, crop_y, crop_w, crop_h))
                    
                    # --- THE AI VISION FILTER ---
                    # Convert to grayscale and boost contrast by 300%
                    from PIL import ImageEnhance
                    gray_image = chat_image.convert('L')
                    enhancer = ImageEnhance.Contrast(gray_image)
                    clean_image = enhancer.enhance(3.0)
                    
                    # Save the cleaned image to verify the view!
                    clean_image.save("debug_jarvis_eyes.png")
                    
                    # 5. Extract text from the screenshot using Tesseract OCR!
                    logger.info("Extracting text via Optical Character Recognition...")
                    extracted_text = pytesseract.image_to_string(chat_image)
                    
                    if extracted_text and extracted_text.strip():
                        # Split into lines and remove empty spaces
                        lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
                        
                        # Filter out garbage: timestamps (e.g., "4:32 pm"), UI buttons, and Date dividers
                        garbage_words = ["type a message", "unread message", "search", "today", "yesterday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                        
                        valid_lines = [
                            line for line in lines 
                            if not re.match(r'^\d{1,2}:\d{2}\s*[aApP][mM]$', line) 
                            and not any(garbage in line.lower() for garbage in garbage_words)
                        ]
                        
                        if valid_lines:
                            raw_msg = valid_lines[-1] 
                            
                            # --- OCR TIME EXTRACTOR & SCRUBBER ---
                            # Search for anything that looks like a time at the end of the string
                            # This catches "9:53 am", "11:03 pm", but also botches like "o.534m"
                            time_match = re.search(r'([0-9oO]{1,2}[:.][0-9oO]{2}\s*[aApP4]?[mM]?)[\s@a-zA-Z]*$', raw_msg)
                            
                            if time_match:
                                # 1. Extract the messy time string
                                messy_time = time_match.group(1)
                                
                                # 2. Clean up the actual text message by slicing off the time and trailing emojis/@ symbols
                                clean_msg = raw_msg[:time_match.start()].strip()
                                
                                # 3. Auto-correct the OCR hallucinations in the timestamp!
                                # Convert 'o' to '0', '.' to ':', and fix '4m' back to 'am'
                                clean_time = messy_time.replace('o', '0').replace('O', '0').replace('.', ':').replace('4m', 'am')
                                
                                # Ensure there is a space before am/pm so JARVIS reads it naturally
                                clean_time = re.sub(r'([aApP][mM])', r' \1', clean_time).strip()
                                
                                return f"You have a new message. It says: {clean_msg}. It was received at {clean_time}."
                            else:
                                # Fallback: If no time was found, just read the message normally
                                return f"You have a new message. It says: {raw_msg.strip()}"
                    
                    return "I took a picture of the chat, but I couldn't find any readable text in the image."

            except pyautogui.ImageNotFoundException:
                return "I scanned the interface, Boss, but you have no new messages."

        except Exception as e:
            logger.error(f"Failed to execute incoming comms macro: {e}")
            return "I encountered a critical error while trying to check your messages."