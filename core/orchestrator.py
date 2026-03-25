import re
from typing import TypedDict, Literal
import asyncio
from langgraph.graph import StateGraph, START, END

# Import the Brains, Hands, and the new Vault!
from agents.executive_agent import ExecutiveMind
from agents.research_agent import AnalyticalMind
from tools.action_engine import ActionEngine
from agents.memory_agent import MemoryVault
from agents.planning_agent import TemporalMind
from agents.translation_agent import MultilingualTranslator
from core.logger import get_logger
from config.system_config import JarvisConfig
from core.avatar_server import avatar_server_instance
from core.intent_engine import intent_engine
from core.command_router import command_router

logger = get_logger("Orchestrator")

# Global reference for Telegram notification hook (set by main.py)
telegram_service_instance = None
class AgentState(TypedDict):
    messages: list[str]
    complexity: str
    final_response: str
    emotion: str
    pose: str

logger.info("Booting up the Trinity Mind architecture with Actions & Memory...")
local_brain = ExecutiveMind()
cloud_brain = AnalyticalMind()
hands = ActionEngine()
vault = MemoryVault() # The memory vault is now online!
temporal_mind = TemporalMind()
translator = MultilingualTranslator()

# --- 1. The Traffic Cop ---
def router_node(state: AgentState):
    user_input = state["messages"][-1].lower()
    
    # We added the new media keywords so the router knows to send them to the Action Engine
    # Action triggers include the new physical commands
    action_triggers = ["time", "youtube", "search", "google", "open", "launch", "turn on", "remember", "recall", "pause", "play", "skip", "next", "mute", "volume", "remind", "whatsapp", "message", "telugu", "hindi", "translate", "check", "unread", "sit", "walk", "follow", "stand", "come closer", "step back", "full view", "zoom in", "zoom out", "closer", "back up", "create project", "delete project", "open ide"]
    cloud_triggers = ["research", "explain", "summarize", "code", "analyze"]
    
    if any(keyword in user_input for keyword in action_triggers):
        complexity = "action"
        logger.info("Router: Action/Memory command detected.")
    elif any(keyword in user_input for keyword in cloud_triggers):
        complexity = "cloud"
        logger.info("Router: Complex task detected. Preparing Cloud transfer.")
    else:
        complexity = "local"
        logger.info("Router: Simple task detected. Keeping it Local.")
        
    return {"complexity": complexity}

# --- 2. The Nodes (Workers) ---
def local_node(state: AgentState):
    user_input = state["messages"][-1].lower()
    response = local_brain.think(user_input)
    
    emotion = "neutral"
    pose = None
    
    # GREETING / PRAISE → Joy + open arms
    if any(word in user_input for word in ["how are you", "how are u", "doing", "feeling"]):
        emotion = "Joy"
        pose = "open_hands"
    elif any(word in response.lower() for word in ["happy", "glad", "welcome", "nice", "brilliant"]):
        emotion = "Joy"
        pose = "open_hands"

    # SORROW / REJECTION → crossed arms  
    if any(word in response.lower() for word in ["sorry", "sad", "unfortunately", "can't", "cannot"]):
        emotion = "Sorrow"
        pose = "crossed_arms"
    
    # EXPLANATION → pointing
    if any(word in response.lower() for word in ["because", "since", "therefore", "note that"]):
        pose = "pointing"

    # QUESTION → thinking pose
    if user_input.endswith("?") or any(user_input.startswith(w) for w in ["how", "what", "why", "can you", "could you", "tell me", "explain"]):
        pose = "thinking"
        
    return {"final_response": response, "emotion": emotion, "pose": pose}

def cloud_node(state: AgentState):
    user_input = state["messages"][-1].lower()
    response = cloud_brain.think(user_input)
    
    emotion = "neutral"
    pose = "thinking"  # Default for cloud = deep thought
    
    if "!" in response or any(word in response.lower() for word in ["happy", "glad", "wonderful", "excellent"]):
        emotion = "Joy"
        pose = "open_hands"
    if any(word in response.lower() for word in ["sorry", "regret", "failed", "unsuccessful", "unfortunately"]):
        emotion = "Sorrow"
        pose = "crossed_arms"
    if "error" in response.lower() or "danger" in response.lower():
        emotion = "Angry"
        pose = "crossed_arms"
    # Explaining something → point
    if any(word in response.lower() for word in ["because", "therefore", "note that", "here's", "here is"]):
        pose = "pointing"
        
    return {"final_response": response, "emotion": emotion, "pose": pose}

# Failure tracker to keep JARVIS's state between turns
system_state = {"failure_counter": 0}

def action_node(state: AgentState):
    user_input = state["messages"][-1].lower()
    response = ""
    emotion = "neutral"
    pose = None
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 1: Avatar-specific commands (need special state / pose)
    # These CANNOT be in the registry because they set emotion/pose.
    # ═══════════════════════════════════════════════════════════════

    # --- CAMERA COMMANDS ---
    if any(word in user_input for word in ["come closer", "closer", "zoom in", "get closer"]):
        avatar_server_instance.set_camera_state("talk")
        response = "Moving in closer, Sir."
        pose = "open_hands"
        emotion = "Joy"
    elif any(word in user_input for word in ["step back", "back up", "zoom out", "move back"]):
        avatar_server_instance.set_camera_state("full")
        response = "Stepping back, Sir. Full view active."
    elif any(word in user_input for word in ["full view", "full body", "show full"]):
        avatar_server_instance.set_camera_state("full")
        response = "Full body view, Sir."

    # --- PHYSICAL COMMANDS ---
    elif "sit" in user_input:
        response = "Of course, Boss. I'll take a seat."
        pose = "sitting"
    elif "walk" in user_input:
        response = "Understood. I'll stretch my digital legs."
        pose = "walk"
    elif "stand" in user_input:
        response = "Standing by and ready, Sir."
        pose = "idle"
    elif "follow" in user_input:
        response = "I'm following the screen now, Sir."
        pose = "walk" 

    # --- AVATAR ANIMATIONS ---
    elif "secret" in user_input or "whisper" in user_input:
        avatar_server_instance.trigger_animation("WHISPER")
        response = "I have a secret for you, Boss... The servers are running perfectly."
        
    elif "wave" in user_input or "hello" in user_input.split() or "hi" in user_input.split():
        avatar_server_instance.trigger_animation("WAVE")
        response = "Hello there, Sir! Great to see you."
        emotion = "Joy"
        pose = "open_hands"

    else:
        # ═══════════════════════════════════════════════════════════
        # PHASE 2: Tool Registry Pipeline (dynamic dispatch)
        # ═══════════════════════════════════════════════════════════
        resolved = intent_engine.resolve(user_input)
        if resolved:
            tool = resolved["tool"]
            params = resolved["params"]
            response = command_router.execute(tool, params)
        else:
            response = "I couldn't figure out exactly what action you wanted me to take, Boss."
            system_state["failure_counter"] += 1
            if system_state["failure_counter"] >= 3:
                emotion = "Sorrow"
                pose = "head_down"
                system_state["failure_counter"] = 0
        
    return {"final_response": response, "emotion": emotion, "pose": pose}

# --- 3. The Switch Track ---
def route_task(state: AgentState) -> Literal["local_node", "cloud_node", "action_node"]:
    if state["complexity"] == "action":
        return "action_node"
    elif state["complexity"] == "cloud":
        return "cloud_node"
    return "local_node"

# --- 4. Compile the Graph ---
builder = StateGraph(AgentState)
builder.add_node("router", router_node)
builder.add_node("local_node", local_node)
builder.add_node("cloud_node", cloud_node)
builder.add_node("action_node", action_node)
builder.add_edge(START, "router")
builder.add_conditional_edges("router", route_task)
builder.add_edge("local_node", END)
builder.add_edge("cloud_node", END)
builder.add_edge("action_node", END)
jarvis_mind = builder.compile()

async def process_telegram_command(user_input: str):
    """Entry point for Telegram messages into the jarvis_mind graph."""
    try:
        logger.info(f"Routing Telegram command to the Orchestrator: {user_input}")
        # Run the sync graph in a separate thread to avoid blocking the async bot loop
        loop = asyncio.get_running_loop()
        state = await loop.run_in_executor(None, lambda: jarvis_mind.invoke({"messages": [user_input]}))
        return state.get('final_response', "Command processed, but no response generated.")
    except Exception as e:
        logger.error(f"Brain connection error (Telegram): {e}")
        return "I'm sorry, I encountered a cognitive routing error while processing your remote request."

def broadcast_alert(message: str):
    """Sends a message to the user via Telegram if the service is online.
    Can be called from anywhere in the synchronous core.
    """
    if telegram_service_instance and hasattr(telegram_service_instance, 'loop'):
        # Use the service's internal loop to send the message
        asyncio.run_coroutine_threadsafe(
            telegram_service_instance.send_alert(message), 
            telegram_service_instance.loop
        )
    else:
        logger.warning(f"Alert ignored (Telegram offline or not initialized): {message}")
