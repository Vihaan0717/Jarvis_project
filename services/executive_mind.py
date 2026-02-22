from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from core.logger import get_logger
from services.memory_vault import MemoryVault

logger = get_logger("ExecutiveMind")

class ExecutiveMind:
    """JARVIS's fast, local, conversational brain with injected memory."""
    
    def __init__(self):
        self.llm = ChatOllama(model="gemma3:1b", temperature=0.3)
        self.vault = MemoryVault() # Connect the brain to the storage drive
        
        # We added a {memory} placeholder to his absolute reality
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are JARVIS, a highly efficient, witty, and loyal AI assistant. 
            Your Boss is speaking to you. 
            
            Here is what you currently know about your Boss:
            {memory}
            
            Strict Rules:
            1. Always respond in 1 to 2 short sentences. Keep it extremely brief.
            2. Never provide unsolicited mental health advice.
            3. Use the memories provided to personalize your answers naturally, but don't force them if they aren't relevant."""),
            ("user", "{input}")
        ])
        
        self.chain = self.prompt | self.llm
        logger.info("Executive Mind initialized with dynamic Memory Injection.")

    def think(self, prompt: str) -> str:
        """Process a thought through the local model with fresh memory context."""
        logger.info(f"Thinking about: '{prompt}'...")
        try:
            # 1. Fetch the freshest memories right before he thinks!
            current_memory = self.vault.recall_facts()
            
            # 2. Pass BOTH your voice command and the memory into the prompt chain
            response = self.chain.invoke({
                "memory": current_memory,
                "input": prompt
            })
            
            logger.info("Thought process complete.")
            return response.content
        except Exception as e:
            logger.error(f"Local brain freeze: {e}")
            return "Sir, I am having trouble connecting to my local logic core."

# Test the brain directly!
if __name__ == "__main__":
    brain = ExecutiveMind()
    print("\n🤖 Waking up the Local Mind...")
    
    # Let's seed the vault with some core facts for testing
    brain.vault.remember_fact("My name is Kanna.")
    brain.vault.remember_fact("I am a B.Tech CSE student.")
    brain.vault.remember_fact("I want to become a data analyst.")
    
    # Test if he naturally uses the injected memory without us explicitly asking him to recall it!
    answer = brain.think("Who am I and what kind of projects should I be working on today?")
    print(f"\nJARVIS: {answer}")