import win32com.client
from core.logger import get_logger

logger = get_logger("VoiceSpeaker")

class VoiceSpeaker:
    """JARVIS's ultra-stable direct Windows vocal cords."""
    
    def __init__(self):
        # Connect DIRECTLY to the Windows Core Audio (Bypassing pyttsx3 entirely)
        self.engine = win32com.client.Dispatch("SAPI.SpVoice")
        
        # 1. Drop the speed (-10 to 10 scale). -2 makes him sound heavy and authoritative.
        self.engine.Rate = -2
        
        # 2. Max out the volume (0 to 100 scale)
        self.engine.Volume = 100
        
        logger.info("Voice Speaker initialized. Direct SAPI5 vocal cords are online.")

    def speak(self, text: str):
        """Converts text into offline audible speech."""
        
        # Strip out emojis and special characters that crash the speech engine
        clean_text = text.encode('ascii', 'ignore').decode('ascii')
        
        logger.info(f"JARVIS Speaking: '{clean_text}'")
        
        # Speak the text synchronously (TensorFlow cannot interrupt this)
        self.engine.Speak(clean_text)

# Test the vocal cords directly!
if __name__ == "__main__":
    mouth = VoiceSpeaker()
    print("\n🗣️ Testing Audio Output...\n")
    mouth.speak("Hello Boss. My direct Windows vocal systems are fully operational.")