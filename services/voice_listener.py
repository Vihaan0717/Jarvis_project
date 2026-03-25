import speech_recognition as sr
import time
from core.logger import get_logger

logger = get_logger("VoiceListener")


class VoiceListener:
    """JARVIS audio intake system."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.5
        self._mic_ready = True
        self._mic_error_logged = False
        self._mic_checked = False
        logger.info("Voice Listener initialized. Ears are open.")

    def is_available(self) -> bool:
        if self._mic_checked:
            return self._mic_ready
        try:
            # Deep diagnostic check
            import pyaudio
            p = pyaudio.PyAudio()
            count = p.get_device_count()
            p.terminate()
            
            if count == 0:
                logger.error("No audio input devices found.")
                self._mic_ready = False
            else:
                _ = sr.Microphone()
                self._mic_ready = True
                logger.info(f"Microphone system active. {count} devices detected.")
        except ImportError:
            self._mic_ready = False
            if not self._mic_error_logged:
                logger.error("CRITICAL: PyAudio library not found in the current Python environment.")
                self._mic_error_logged = True
        except Exception as e:
            self._mic_ready = False
            if not self._mic_error_logged:
                logger.error(f"Microphone unavailable (Hardware/Driver issue): {e}")
                self._mic_error_logged = True
        self._mic_checked = True
        return self._mic_ready

    def listen(self, language_code: str = "en-IN", speaker=None) -> str:
        """Listen from microphone and return recognized text."""
        # --- ANTI-SELF-TALKING GUARD ---
        if speaker and speaker.active_speaking:
            logger.info("JARVIS is speaking. Pausing listener...")
            while speaker.active_speaking:
                time.sleep(0.1)
            time.sleep(0.5) # Silence buffer after speaking
            return ""

        if not self.is_available():
            if not self._mic_error_logged:
                print("\n⚠️  MICROPHONE ERROR: Hardware not detected or PyAudio missing.")
                self._mic_error_logged = True
            time.sleep(2)
            return ""

        try:
            mic = sr.Microphone()
        except Exception as e:
            if not self._mic_error_logged:
                logger.error(f"Microphone unavailable (PyAudio/device issue): {e}")
                self._mic_error_logged = True
            self._mic_ready = False
            return ""

        with mic as source:
            if speaker and speaker.active_speaking: return ""
            print(f"\nJARVIS is listening ({language_code})... Speak now!")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("Processing audio...")
                text = self.recognizer.recognize_google(audio, language=language_code)
                return text
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                return ""
            except Exception as e:
                logger.error(f"Microphone error: {e}")
                return ""


if __name__ == "__main__":
    ears = VoiceListener()
    print("\nInitializing audio hardware...\n")
    spoken_text = ears.listen()
    if spoken_text:
        print(f"\nSUCCESS! You said: {spoken_text}")
    else:
        print("\nJARVIS: I did not catch that.")
