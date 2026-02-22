from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

# Import the Brains, Hands, and the new Vault!
from services.executive_mind import ExecutiveMind
from services.analytical_mind import AnalyticalMind
from services.action_engine import ActionEngine
from services.memory_vault import MemoryVault
from core.logger import get_logger
from config.system_config import JarvisConfig

logger = get_logger("Orchestrator")

class AgentState(TypedDict):
    messages: list[str]
    complexity: str
    final_response: str

logger.info("Booting up the Trinity Mind architecture with Actions & Memory...")
local_brain = ExecutiveMind()
cloud_brain = AnalyticalMind()
hands = ActionEngine()
vault = MemoryVault() # The memory vault is now online!

# --- 1. The Traffic Cop ---
def router_node(state: AgentState):
    user_input = state["messages"][-1].lower()
    
    # We added the new media keywords so the router knows to send them to the Action Engine
    action_triggers = ["time", "youtube", "search", "google", "open", "launch", "turn on", "remember", "recall", "pause", "play", "skip", "next", "mute", "volume"]
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
    response = local_brain.think(state["messages"][-1])
    return {"final_response": response}

def cloud_node(state: AgentState):
    response = cloud_brain.think(state["messages"][-1])
    return {"final_response": response}

def action_node(state: AgentState):
    user_input = state["messages"][-1].lower()
    response = ""
    
    # --- MEMORY COMMANDS ---
    if "what do you remember" in user_input or "recall" in user_input:
        response = vault.recall_facts()
        
    elif "remember" in user_input:
        # Strip out the command words to isolate the actual fact
        fact = user_input.replace("jarvis", "").replace("remember that", "").replace("remember", "").strip()
        if fact:
            # Capitalize the first letter so it looks nice in the JSON file
            fact = fact.capitalize()
            response = vault.remember_fact(fact)
        else:
            response = "What would you like me to remember, Sir?"

    # --- ACTION COMMANDS ---
    elif "time" in user_input:
        response = hands.get_time()
        
    elif "youtube" in user_input:
        query = user_input.replace("jarvis", "").replace("play", "").replace("youtube", "").replace("search", "").strip()
        if query.endswith(" on"): query = query[:-3].strip()
        if query.startswith("is "): query = query[3:].strip()
        if not query: query = "trending" 
        response = hands.play_youtube(query)
        
    elif "google" in user_input or "search" in user_input:
        query = user_input.replace("jarvis", "").replace("search", "").replace("google", "").replace("for", "").strip()
        if not query: query = "technology news"
        response = hands.search_google(query)
        
    elif "launch" in user_input:
        response = hands.open_application(user_input)
        
    elif "open" in user_input:
        site = user_input.replace("jarvis", "").replace("open", "").strip()
        url = f"https://www.{site.replace(' ', '')}.com"
        response = hands.open_website(site, url)
        
    elif any(word in user_input for word in ["pause", "play", "stop", "skip", "next", "previous", "back", "mute", "volume", "louder", "quieter"]):
        # This will now perfectly catch "play music on Spotify" and trigger the Ghost Keyboard!
        response = hands.control_media(user_input)
            
    else:
        response = "I couldn't figure out exactly what action you wanted me to take, Boss."
        
    return {"final_response": response}

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