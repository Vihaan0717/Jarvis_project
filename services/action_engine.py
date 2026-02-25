import webbrowser
import datetime
import urllib.parse
import urllib.request
import re
import os
import time
import pyautogui
import pytesseract
from PIL import Image
from PIL import ImageEnhance
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
                pyautogui.press('win')
                time.sleep(0.5) # Wait half a second for the menu to pop up
                pyautogui.write('spotify')
                time.sleep(0.5)
                pyautogui.press('enter')
                return "Launching Spotify."
            elif "whatsapp" in command: 
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
        """Automates WhatsApp using Computer Vision to verify UI state before typing."""
        import pyautogui
        import time
        import os
        
        logger.info(f"Initiating Vision-Based Comms Relay to {contact_name}...")
        
        valid_contacts = ["kanna", "mom", "friend", "nikhil"]
        target_contact = None
        for contact in valid_contacts:
            if contact in contact_name.lower() or "karn" in contact_name.lower() and contact == "kanna":
                target_contact = contact
                break
                
        if not target_contact:
            return f"I do not have a registered contact for {contact_name}, Sir."
            
        try:
            # 1. Launch WhatsApp
            logger.info("Launching WhatsApp via URI...")
            os.system("start whatsapp:") 
            
            # 2. Wait for the Search Bar to visually appear (Max 10 seconds)
            logger.info("Visually scanning for the Search Bar...")
            search_bar_location = None
            for _ in range(10):
                try:
                    # Looking for the magnifying glass icon or the search box itself
                    search_bar_location = pyautogui.locateCenterOnScreen('whatsapp_search.png', confidence=0.8)
                    if search_bar_location:
                        break
                except pyautogui.ImageNotFoundException:
                    pass
                time.sleep(1)
                
            if not search_bar_location:
                return "I could not visually confirm WhatsApp loaded, Boss. Aborting to prevent misfires."

            # 3. Click the Search Bar and Type the Contact
            logger.info("Search bar confirmed. Entering target contact...")
            pyautogui.click(search_bar_location)
            time.sleep(0.5)
            
            # Clear any old searches just in case
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            
            pyautogui.write(target_contact)
            time.sleep(1.5) # Give WhatsApp a moment to filter the contact list
            pyautogui.press('enter') # Open the chat
            
            # 4. Verify the Chat Opened by looking for the Text Input area
            # We look for the little microphone or paperclip icon next to the text box
            logger.info("Verifying chat window is active...")
            chat_active = False
            for _ in range(5):
                try:
                    # We need a small picture of the paperclip/plus icon or mic icon next to the chat bar
                    chat_box = pyautogui.locateCenterOnScreen('whatsapp_input_anchor.png', confidence=0.8)
                    if chat_box:
                        chat_active = True
                        break
                except pyautogui.ImageNotFoundException:
                    pass
                time.sleep(1)
                
            if not chat_active:
                return "I selected the contact, but the chat window failed to open properly."
                
            # 5. Type and Send!
            logger.info("Chat window verified. Transmitting payload...")
            pyautogui.write(message)
            time.sleep(0.5)
            pyautogui.press('enter')
            
            return f"Message successfully transmitted to {target_contact}."
            
        except Exception as e:
            logger.error(f"Comms automation failed: {e}")
            return "I encountered a critical error while operating the desktop interface."

    def check_unread_whatsapp(self) -> str:
        """Uses Computer Vision to find unread badges and pytesseract to read the text and time."""
        logger.info("Initiating Incoming Comms Poller...")
        try:
            # 1. Pull up WhatsApp using the URI shortcut
            logger.info("Opening WhatsApp...")
            os.system("start whatsapp:")
            time.sleep(2) # Give it a moment to render

            # 2. Scan the screen for the green badge
            logger.info("Visually scanning for unread_badge.png...")
            try:
                badge_location = pyautogui.locateCenterOnScreen('unread_badge.png', confidence=0.7, grayscale=True)
                
                if badge_location:
                    logger.info("Unread badge detected! Engaging...")
                    
                    # --- NEW: STEP 2.5 - EXTRACT THE EXACT TIME BEFORE CLICKING ---
                    # The time is located exactly above and slightly left of the green badge!
                    t_x = int(badge_location.x - 50)
                    t_y = int(badge_location.y - 35)
                    t_w = 75
                    t_h = 25
                    
                    time_image = pyautogui.screenshot(region=(t_x, t_y, t_w, t_h))
                    
                    # AI TRICK: Upscale the tiny image by 300% so Tesseract can easily read the small font
                    time_image = time_image.resize((t_w * 3, t_h * 3))
                    time_image = time_image.convert('L')
                    
                    # Save it so YOU can see his "Time Eyes"
                    time_image.save("debug_time_eyes.png")
                    
                    # Extract the time, using --psm 7 to tell Tesseract it's a single line of text
                    raw_time = pytesseract.image_to_string(time_image, config='--psm 7').strip()
                    
                    # Clean it up: find the actual numbers and am/pm
                    time_match = re.search(r'\d{1,2}[:.]\d{2}\s*[aApP][mM]', raw_time)
                    exact_time = time_match.group(0).replace('.', ':') if time_match else "an unknown time"
                    
                    # --------------------------------------------------------------

                    # 3. Focus and Auto-Scroll to the bottom
                    time.sleep(0.5)
                    screen_width, screen_height = pyautogui.size()
                    
                    pyautogui.click(badge_location.x + 400, screen_height - 60)
                    time.sleep(1.0) 
                    
                    # The Mouse Flick to hide emojis
                    pyautogui.moveTo(10, 10)
                    time.sleep(0.5)

                    # 4. Take the MASSIVE screenshot of the chat text
                    crop_x = int(badge_location.x + 50) 
                    crop_y = 100 
                    crop_w = int(screen_width - crop_x - 50)  
                    crop_h = int(screen_height - 150) 
                    
                    logger.info("Taking screenshot of message payload...")
                    chat_image = pyautogui.screenshot(region=(crop_x, crop_y, crop_w, crop_h))
                    
                    # Convert to grayscale and boost contrast by 300%
                    gray_image = chat_image.convert('L')
                    enhancer = ImageEnhance.Contrast(gray_image)
                    clean_image = enhancer.enhance(3.0)
                    clean_image.save("debug_jarvis_eyes.png")

                    # 5. Extract text from the cleaned screenshot
                    extracted_text = pytesseract.image_to_string(clean_image)
                    
                    if extracted_text and extracted_text.strip():
                        lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
                        garbage_words = ["type a message", "unread message", "search", "today", "yesterday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                        
                        valid_lines = [
                            line for line in lines 
                            if not re.match(r'^\d{1,2}:\d{2}\s*[aApP][mM]$', line) 
                            and not any(garbage in line.lower() for garbage in garbage_words)
                        ]
                        
                        if valid_lines:
                            raw_msg = valid_lines[-1] 
                            
                            # Scrub off any leftover hallucinated time/emojis from the end of the text
                            clean_msg = re.sub(r'\s+[\d:oO.]+\s*[aApP]?\w*[@]?$', '', raw_msg).strip()
                            
                            # Combine the cleanly scrubbed message with the exact time we read earlier!
                            return f"You have a new message. It says: {clean_msg}. It was received at {exact_time}."
                
                return "I took a picture of the chat, but I couldn't find any readable text in the image."

            except pyautogui.ImageNotFoundException:
                return "I scanned the interface, Boss, but you have no new messages."

        except Exception as e:
            logger.error(f"Failed to execute incoming comms macro: {e}")
            return "I encountered a critical error while trying to check your messages."