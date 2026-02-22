import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from core.logger import get_logger
from services.memory_vault import MemoryVault

logger = get_logger("AnalyticalMind")

class AnalyticalMind:
    """JARVIS's heavy-lifting cloud brain for complex coding and research."""
    
    def __init__(self):
        # Connects to Google's servers using the API key in your .env file
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0.4
        )
        self.vault = MemoryVault() 
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are JARVIS, a highly advanced AI assistant. 
            Your Boss is speaking to you. 
            
            Here is what you currently know about your Boss:
            {memory}
            
            Strict Rules:
            1. You handle complex analytical tasks, deep research, and heavy coding.
            2. Provide structured, clear, and comprehensive answers. 
            3. Maintain the professional, witty JARVIS persona.
            4. Use the provided memories to personalize your response if relevant, but do not force them."""),
            ("user", "{input}")
        ])
        
        self.chain = self.prompt | self.llm
        logger.info("Analytical Mind initialized and connected to Gemini Cloud.")

    def think(self, prompt: str) -> str:
        """Process a thought through the cloud model."""
        logger.info(f"Analyzing complex query: '{prompt}'...")
        try:
            current_memory = self.vault.recall_facts()
            
            response = self.chain.invoke({
                "memory": current_memory,
                "input": prompt
            })
            
            logger.info("Cloud analysis complete.")
            return response.content
        except Exception as e:
            logger.error(f"Cloud connection failed: {e}")
            return "Sir, I am having trouble connecting to my main cloud servers."

# Test the cloud brain directly!
if __name__ == "__main__":
    from config.system_config import JarvisConfig
    JarvisConfig.validate_keys() # Make sure the API key is loaded
    
    brain = AnalyticalMind()
    print("\n🌩️ Waking up the Cloud Mind...\n")
    
    # Let's give it a heavy coding task to see how it handles it
    answer = brain.think("Can you write a complete Python function that uses regular expressions to extract all email addresses from a large block of text?")
    print(f"\nJARVIS: {answer}")