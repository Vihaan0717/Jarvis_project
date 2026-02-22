import pyttsx3
from core.logger import get_logger

# Give the mouth a voice in the logs
logger = get_logger("VoiceSpeaker")

class VoiceSpeaker:
    """JARVIS's offline vocal cords."""
    
    def __init__(self):
        # Initialize the native Windows speech engine
        self.engine = pyttsx3.init()
        
        # 1. Drop the speed to make him sound deliberate and heavy
        self.engine.setProperty('rate', 145) 
        
        # 2. Max out the volume
        self.engine.setProperty('volume', 1.0)
        
        # 3. Switch back to David (Index 0)
        voices = self.engine.getProperty('voices')
        if len(voices) > 0:
            self.engine.setProperty('voice', voices[0].id) 
            
        logger.info("Voice Speaker initialized. Authoritative vocal cords are online.")

    def speak(self, text: str):
        """Converts text into offline audible speech."""
        
        # 1. Strip out emojis and special characters that crash Windows
        # This forces the text into basic characters only
        clean_text = text.encode('ascii', 'ignore').decode('ascii')
        
        logger.info(f"JARVIS Speaking: '{clean_text}'")
        self.engine.say(clean_text)
        
        # This tells the script to wait until he is completely finished talking
        self.engine.runAndWait()

# Test the vocal cords directly!
if __name__ == "__main__":
    mouth = VoiceSpeaker()
    print("\n🗣️ Testing Audio Output...\n")
    mouth.speak("Hello Boss. My vocal systems are fully operational.")