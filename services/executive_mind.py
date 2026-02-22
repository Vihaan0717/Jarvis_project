from langchain_ollama import ChatOllama
from core.logger import get_logger

# Give the Executive Mind a voice in the logs
logger = get_logger("ExecutiveMind")

class ExecutiveMind:
    """JARVIS's fast, private, offline brain."""
    
    def __init__(self):
        # Connect to the Llama 3.2 model running locally
        # Temperature is set to 0.3 so he gives precise, logical answers
        self.llm = ChatOllama(model="gemma3:1b", temperature=0.3)
        logger.info("Executive Mind initialized and connected to Gemma 3.1b.")

    def think(self, prompt: str) -> str:
        """Send a prompt to the local model and get a response."""
        logger.info(f"Thinking about: '{prompt}'...")
        try:
            # Send the prompt to Ollama
            response = self.llm.invoke(prompt)
            logger.info("Thought process complete.")
            return response.content
        except Exception as e:
            logger.error(f"Brain freeze! Error: {e}")
            return "Sir, my local cognitive systems are currently offline. Please check Ollama."

# Test the brain directly!
if __name__ == "__main__":
    brain = ExecutiveMind()
    print("\n🤖 Waking up the Local Mind...")
    print("Asking JARVIS a question...\n")
    
    answer = brain.think("In one short sentence, what is your primary directive?")
    print(f"\nJARVIS: {answer}")