import os
from deep_translator import GoogleTranslator
from gtts import gTTS
import pygame
from core.logger import get_logger

logger = get_logger("MultilingualTranslator")

class MultilingualTranslator:
    """Handles translation and foreign-language audio synthesis."""
    
    def __init__(self):
        # Initialize the invisible audio mixer
        pygame.mixer.init()
        self.audio_file = "temp_foreign_speech.mp3"
        logger.info("Multilingual Engine initialized.")

    def translate_and_speak(self, english_text: str, target_language: str) -> str:
        """Translates English text and speaks it using Google's Neural Voice."""
        try:
            # 1. Map the language to the correct Google code
            lang_code = 'te' if 'telugu' in target_language.lower() else 'hi' if 'hindi' in target_language.lower() else 'en'
            
            if lang_code == 'en':
                return english_text # Let the normal Windows voice handle English
                
            logger.info(f"Translating to {lang_code}: '{english_text}'")
            
            # 2. Translate the text
            translated_text = GoogleTranslator(source='en', target=lang_code).translate(english_text)
            # logger.info(f"Translation complete: {translated_text}") # Fixed: Commented out to prevent Windows encoding errors
            
            # 3. Generate the foreign audio file
            tts = gTTS(text=translated_text, lang=lang_code, slow=False)
            tts.save(self.audio_file)
            
            # 4. Play the audio file silently in the background
            pygame.mixer.music.load(self.audio_file)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing before moving on
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            # Unload the file so we can overwrite it next time
            pygame.mixer.music.unload() 
            
            # Delete the temp file to keep the folder clean
            if os.path.exists(self.audio_file):
                os.remove(self.audio_file)
                
            return translated_text
            
        except Exception as e:
            logger.error(f"Multilingual error: {e}")
            return "I encountered an error trying to translate that."

    def translate_to_english(self, foreign_text: str, source_lang_code: str) -> str:
        """Translates recognized foreign speech back to English for JARVIS's brain to process."""
        try:
            logger.info(f"Translating input to English...")
            translated_text = GoogleTranslator(source=source_lang_code, target='en').translate(foreign_text)
            logger.info(f"English translation: {translated_text}")
            return translated_text
        except Exception as e:
            logger.error(f"Input translation error: {e}")
            return ""

# Direct Module Test
if __name__ == "__main__":
    translator = MultilingualTranslator()
    print("\n🌍 Testing Multilingual Mimicry...\n")
    
    print("Testing Telugu...")
    translator.translate_and_speak("Hello Boss, my systems are fully operational and I am ready to assist you.", "telugu")
    
    print("Testing Hindi...")
    translator.translate_and_speak("I am an advanced artificial intelligence.", "hindi")