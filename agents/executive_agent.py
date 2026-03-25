from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from core.logger import get_logger
from agents.memory_agent import MemoryVault
from config.system_config import JarvisConfig

logger = get_logger("ExecutiveAgent")

class ExecutiveAgent:
    """JARVIS's fast, local, conversational brain with injected memory."""
    
    def __init__(self):
        # Use centralized OLLAMA_BASE_URL for technical robustness
        self.llm = ChatOllama(
            model="gemma3:1b", 
            temperature=0.3,
            base_url=JarvisConfig.OLLAMA_BASE_URL
        )
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
        logger.info(f"Executive Agent initialized at {JarvisConfig.OLLAMA_BASE_URL}")

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
            # Catch specific getaddrinfo / connection errors
            err_str = str(e)
            if "getaddrinfo failed" in err_str or "11001" in err_str:
                logger.error(f"DNS Resolution Failure: Check OLLAMA_BASE_URL ({JarvisConfig.OLLAMA_BASE_URL})")
                return "Sir, I cannot resolve the connection to my local logic core. Please check if the API URL is correct."
            elif "ConnectionRefusedError" in err_str or "target machine actively refused it" in err_str:
                logger.error("Ollama connection refused. Is Ollama running?")
                return "Sir, my local logic core is offline. Please ensure Ollama is running."
            
            logger.error(f"Local brain freeze: {e}")
            return "Sir, I am having trouble connecting to my local logic core."

# Alias for backward compatibility if needed
ExecutiveMind = ExecutiveAgent
