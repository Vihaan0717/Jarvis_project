import win32com.client
import re
from core.logger import get_logger

logger = get_logger("VoiceSpeaker")

class VoiceSpeaker:
    """JARVIS's ultra-stable direct Windows vocal cords."""
    
    def __init__(self):
        self.engine = win32com.client.Dispatch("SAPI.SpVoice")
        self.engine.Rate = -2 
        self.engine.Volume = 100
        logger.info("Voice Speaker initialized. Direct SAPI5 vocal cords are online.")

    def speak(self, text: str):
        """Converts text into offline audible speech."""
        
        # 1. Strip out Markdown formatting (*, _, #, `, ~) so he doesn't say "asterisk"
        clean_text = re.sub(r'[*_#`~]', '', text)
        
        # 2. Strip out emojis and special characters that crash the speech engine
        clean_text = clean_text.encode('ascii', 'ignore').decode('ascii')
        
        logger.info(f"JARVIS Speaking: '{clean_text.strip()}'")
        self.engine.Speak(clean_text)

# Test the vocal cords directly!
if __name__ == "__main__":
    mouth = VoiceSpeaker()
    print("\n🗣️ Testing Audio Output...\n")
    mouth.speak("Hello Boss. My direct Windows vocal systems are fully operational.")
