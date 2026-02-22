from langchain_google_genai import ChatGoogleGenerativeAI
from core.logger import get_logger
from config.system_config import JarvisConfig

# Give the Cloud Mind a voice in the logs
logger = get_logger("AnalyticalMind")

class AnalyticalMind:
    """JARVIS's deep-reasoning, cloud-connected brain."""
    
    def __init__(self):
        # We use gemini-2.5-flash because it is incredibly fast and free-tier friendly
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            api_key=JarvisConfig.GEMINI_API_KEY,
            temperature=0.7 # A bit more creative for writing and research
        )
        logger.info("Analytical Mind initialized and connected to Gemini 2.5 Flash.")

    def think(self, prompt: str) -> str:
        """Send a complex prompt to the cloud model."""
        logger.info(f"Uploading thought to Cloud: '{prompt}'...")
        try:
            # Send the prompt to Google's servers
            response = self.llm.invoke(prompt)
            logger.info("Cloud processing complete.")
            return response.content
        except Exception as e:
            logger.error(f"Cloud connection failed! Error: {e}")
            return "Sir, I am unable to reach the cloud servers. Please check our internet connection or API key."

# Test the cloud brain directly!
if __name__ == "__main__":
    # Make sure keys are loaded before testing
    JarvisConfig.validate_keys()
    
    brain = AnalyticalMind()
    print("\n☁️ Waking up the Cloud Mind...")
    print("Asking JARVIS a complex question...\n")
    
    # We ask a question that the tiny local brain wouldn't know
    answer = brain.think("In two sentences, explain the concept of a LangGraph multi-agent orchestrator.")
    print(f"\nJARVIS (Cloud): {answer}")