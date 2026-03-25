from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from core.logger import get_logger
from agents.memory_agent import MemoryVault

logger = get_logger("ExecutiveAgent")

class ExecutiveAgent:
    """JARVIS's fast, local, conversational brain with injected memory."""
    
    def __init__(self):
        self.llm = ChatOllama(model="gemma3:1b", temperature=0.3)
        self.vault = MemoryVault() 
        
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
        logger.info("Executive Agent initialized.")

    def think(self, prompt: str) -> str:
        logger.info(f"Thinking about: '{prompt}'...")
        try:
            current_memory = self.vault.recall_facts()
            response = self.chain.invoke({
                "memory": current_memory,
                "input": prompt
            })
            return response.content
        except Exception as e:
            logger.error(f"Local brain freeze: {e}")
            return "Sir, I am having trouble connecting to my local logic core."

# Alias for backward compatibility if needed
ExecutiveMind = ExecutiveAgent
