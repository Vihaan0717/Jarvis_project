import os
from deep_translator import GoogleTranslator
from gtts import gTTS
import pygame
from core.logger import get_logger

logger = get_logger("TranslationAgent")

class TranslationAgent:
    """Handles translation and foreign-language audio synthesis."""
    
    def __init__(self):
        pygame.mixer.init()
        self.audio_file = "temp_foreign_speech.mp3"
        logger.info("Translation Agent initialized.")

    def translate_and_speak(self, english_text: str, target_language: str) -> str:
        try:
            lang_code = 'te' if 'telugu' in target_language.lower() else 'hi' if 'hindi' in target_language.lower() else 'en'
            if lang_code == 'en': return english_text
            
            logger.info(f"Translating to {lang_code}: '{english_text}'")
            translated_text = GoogleTranslator(source='en', target=lang_code).translate(english_text)
            
            tts = gTTS(text=translated_text, lang=lang_code, slow=False)
            tts.save(self.audio_file)
            
            pygame.mixer.music.load(self.audio_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload() 
            
            if os.path.exists(self.audio_file):
                os.remove(self.audio_file)
            return translated_text
        except Exception as e:
            logger.error(f"Multilingual error: {e}")
            return "I encountered an error trying to translate that."

# Alias for backward compatibility if needed
MultilingualTranslator = TranslationAgent
