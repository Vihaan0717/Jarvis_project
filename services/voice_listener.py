import speech_recognition as sr
from core.logger import get_logger

# Give the ears a voice in the logs
logger = get_logger("VoiceListener")

class VoiceListener:
    """JARVIS's audio intake system."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        logger.info("Voice Listener initialized. Ears are open.")

    def listen(self) -> str:
        """Turns on the mic, listens for a command, and translates it to text."""
        # Use the default laptop microphone
        with sr.Microphone() as source:
            logger.info("Calibrating to background noise... please wait 1 second.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("\n🎙️ JARVIS is listening... Speak now!")
            
            try:
                # Listen to the audio (stops listening if you pause for 5 seconds)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("Processing audio...")
                
                # We use Google's free, built-in speech engine for quick testing
                text = self.recognizer.recognize_google(audio)
                logger.info(f"JARVIS Heard: '{text}'")
                return text
                
            except sr.WaitTimeoutError:
                logger.warning("No speech detected.")
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