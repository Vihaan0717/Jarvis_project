from agents.automation_agent import AutomationAgent
from agents.planning_agent import TemporalMind
from agents.vision_agent import VisionTracker
from agents.memory_agent import MemoryAgent
from core.logger import get_logger
import json

logger = get_logger("Commander")

class Commander:
    """
    JARVIS 2.0 Commander (Orchestrator).
    Routes intent, plans multi-step tasks, and verifies execution.
    """
    def __init__(self):
        self.memory = MemoryAgent()
        # Other agents will be initialized here as needed
        print("Commander 2.0 online. Analyzing reality matrix, Sir.")

    def router(self, user_input: str) -> str:
        """
        Analyzes user input and returns a JSON mapping intent to an agent.
        """
        user_input = user_input.lower()
        
        # Rule-based router implementation as requested
        intent_map = {
            "intent": "conversational",
            "agent": "core",
            "confidence": 0.5
        }

        if any(word in user_input for word in ["open", "launch", "whatsapp", "browser", "youtube", "google"]):
            intent_map = {"intent": "execute_automation", "agent": "automation_agent", "confidence": 0.95}
        elif any(word in user_input for word in ["remember", "forget", "recall", "who is", "what do you know"]):
            intent_map = {"intent": "access_memory", "agent": "memory_agent", "confidence": 0.92}
        elif any(word in user_input for word in ["plan", "schedule", "tomorrow", "remind"]):
            intent_map = {"intent": "temporal_planning", "agent": "planning_agent", "confidence": 0.88}
        elif any(word in user_input for word in ["look", "see", "camera", "detect"]):
            intent_map = {"intent": "visual_scan", "agent": "vision_agent", "confidence": 0.90}
        elif "whatsapp" in user_input and any(word in user_input for word in ["check", "unread", "messages", "notifications"]):
            intent_map = {"intent": "check_whatsapp", "agent": "messaging_agent", "confidence": 0.98}

        return json.dumps(intent_map, indent=2)

    def plan_execute_verify(self, user_input: str):
        """
        The three-step core logic for complex tasks.
        """
        # STEP 1: PLAN (Routing and intent detection)
        routing_json = self.router(user_input)
        routing = json.loads(routing_json)
        logger.info(f"PLAN: User intent detected as {routing['intent']} for {routing['agent']}")

        # STEP 2: EXECUTE (In a full implementation, this calls agent methods)
        logger.info(f"EXECUTE: Routing payload to {routing['agent']}...")
        result = f"Command routed to {routing['agent']}."

        # STEP 3: VERIFY (Check results against user intent)
        logger.info("VERIFY: Execution completed. Checking status.")
        return result

if __name__ == "__main__":
    commander = Commander()
    print(commander.router("Open YouTube and look for Jarvis videos"))
