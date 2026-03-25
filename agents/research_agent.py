from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from core.logger import get_logger
from agents.memory_agent import MemoryVault

logger = get_logger("ResearchAgent")

class ResearchAgent:
    """JARVIS's heavy-lifting cloud brain for complex coding and research."""
    
    def __init__(self):
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
        logger.info("Research Agent initialized.")

    def think(self, prompt: str) -> str:
        logger.info(f"Analyzing complex query: '{prompt}'...")
        try:
            current_memory = self.vault.recall_facts()
            response = self.chain.invoke({
                "memory": current_memory,
                "input": prompt
            })
            return response.content
        except Exception as e:
            logger.error(f"Cloud connection failed: {e}")
            return "Sir, I am having trouble connecting to my main cloud servers."

# Alias for backward compatibility if needed
AnalyticalMind = ResearchAgent
