import speech_recognition as sr
from core.logger import get_logger

logger = get_logger("VoiceListener")

class VoiceListener:
    """JARVIS's audio intake system."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Give you a slightly longer pause (1.5 seconds) before he thinks you are done talking
        self.recognizer.pause_threshold = 1.5 
        
        logger.info("Voice Listener initialized. Ears are open.")

    def listen(self) -> str:
        """Turns on the mic, listens for a command, and translates it to text."""
        with sr.Microphone() as source:
            # We removed the 1-second delay from here so he listens INSTANTLY!
            print("\n🎙️ JARVIS is listening... Speak now!")
            
            try:
                # We removed the phrase_time_limit so you can speak as long as you want
                audio = self.recognizer.listen(source, timeout=8)
                print("Processing audio...")
                
                text = self.recognizer.recognize_google(audio)
                logger.info(f"JARVIS Heard: '{text}'")
                return text
                
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                logger.warning("Could not understand the audio. Please speak clearly.")
                return ""
            except Exception as e:
                logger.error(f"Microphone error: {e}")
                return ""

# Test the microphone directly!
if __name__ == "__main__":
    ears = VoiceListener()
    print("\n🎧 Initializing Audio Hardware...\n")
    
    # Try to listen and capture a sentence
    spoken_text = ears.listen()
    
    if spoken_text:
        print(f"\nSUCCESS! You said: {spoken_text}")
    else:
        print("\nJARVIS: I didn't catch that, Boss.")
