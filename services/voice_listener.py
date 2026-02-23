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

    def listen(self, language_code: str = "en-IN") -> str:
        """Turns on the mic, listens, and translates audio to text."""
        with sr.Microphone() as source:
            print(f"\n🎙️ JARVIS is listening ({language_code})... Speak now!")
            try:
                # We added a 5-second timeout so it doesn't hang if you are quiet
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("Processing audio...")
                
                # We pass the specific language code to Google's Speech-to-Text engine
                text = self.recognizer.recognize_google(audio, language=language_code)
                # logger.info(f"JARVIS Heard ({language_code}): '{text}'")
                return text
                
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                pass # Silently ignore background static
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
