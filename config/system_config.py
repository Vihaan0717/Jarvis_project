import os
from dotenv import load_dotenv

# This tells Python to go find the .env file and load the secrets into memory
load_dotenv()

class JarvisConfig:
    """Central configuration hub for Project JARVIS."""
    
    # 1. API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    AUTHORIZED_CHAT_ID = os.getenv("AUTHORIZED_CHAT_ID")
    
    # 2. News & Info
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
    RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "gowatch.p.rapidapi.com")
    
    # 3. System Settings
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOCAL_MODEL_NAME = "llama3.2"
    
    @classmethod
    def validate_keys(cls):
        """Checks if JARVIS has what he needs to boot up."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("🚨 CRITICAL: Gemini API Key is missing from the .env file!")
        print("✅ All system configuration keys loaded successfully.")

# Test it out if this file is run directly
if __name__ == "__main__":
    JarvisConfig.validate_keys()