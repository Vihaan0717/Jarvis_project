from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from core.logger import get_logger

# Give the Local Mind a voice in the logs
logger = get_logger("ExecutiveMind")

class ExecutiveMind:
    """JARVIS's fast, local, conversational brain."""
    
    def __init__(self):
        # 1. Connect to Ollama
        self.llm = ChatOllama(model="gemma3:1b", temperature=0.3)
        
        # 2. Define the strict JARVIS Persona
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are JARVIS, a highly efficient, witty, and loyal AI assistant. 
            Your Boss is speaking to you. 
            Strict Rules:
            1. Always respond in 1 to 2 short sentences. Keep it extremely brief.
            2. Never provide unsolicited mental health advice or crisis hotlines.
            3. If the user gives a very short or confusing command like 'no', 'stop', or 'jar', simply acknowledge it politely and wait for the next command."""),
            ("user", "{input}")
        ])
        
        # 3. Chain the prompt and the model together
        self.chain = self.prompt | self.llm
        logger.info("Executive Mind initialized and connected to Gemma 3.1b with Persona.")

    def think(self, prompt: str) -> str:
        """Process a thought through the local model using the strict persona."""
        logger.info(f"Thinking about: '{prompt}'...")
        try:
            # Pass the input into our chain
            response = self.chain.invoke({"input": prompt})
            logger.info("Thought process complete.")
            return response.content
        except Exception as e:
            logger.error(f"Local brain freeze: {e}")
            return "Sir, I am having trouble connecting to my local logic core."

# Test the brain directly!
if __name__ == "__main__":
    brain = ExecutiveMind()
    print("\n🤖 Waking up the Local Mind...")
    
    # Let's test the exact phrase that caused the hallucination!
    answer = brain.think("no jar")
    print(f"\nJARVIS: {answer}")