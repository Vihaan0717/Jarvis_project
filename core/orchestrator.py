import re
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

# Import the Brains, Hands, and the new Vault!
from services.executive_mind import ExecutiveMind
from services.analytical_mind import AnalyticalMind
from services.action_engine import ActionEngine
from services.memory_vault import MemoryVault
from services.temporal_mind import TemporalMind
from services.multilingual_translator import MultilingualTranslator
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
temporal_mind = TemporalMind()
translator = MultilingualTranslator()

# --- 1. The Traffic Cop ---
def router_node(state: AgentState):
    user_input = state["messages"][-1].lower()
    
    # We added the new media keywords so the router knows to send them to the Action Engine
    action_triggers = ["time", "youtube", "search", "google", "open", "launch", "turn on", "remember", "recall", "pause", "play", "skip", "next", "mute", "volume", "remind", "whatsapp", "message", "telugu", "hindi", "translate", "check", "unread"]
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
        # 1. Remove obvious trigger words
        query = user_input.replace("jarvis", "").replace("play", "").replace("youtube", "").replace("search", "").strip()
        
        # 2. Use Regex to cleanly strip standalone words like "on", "for", or "is"
        query = re.sub(r'\b(on|for|is)\b', '', query).strip()
        
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
        
    elif "in telugu" in user_input or "in hindi" in user_input:
        target_lang = "telugu" if "in telugu" in user_input else "hindi"
        
        # Strip out the command words to isolate the exact phrase you want translated
        phrase = user_input.replace("jarvis", "").replace("say", "").replace("translate", "").replace(f"in {target_lang}", "").strip()
        
        if phrase:
            logger.info(f"Routing translation task to Multilingual Engine: {phrase}")
            # This triggers the Google Neural Voice and plays the audio in the background!
            translator.translate_and_speak(phrase, target_lang)
            # This is the English confirmation his default voice will speak afterward
            response = f"I have spoken the phrase in {target_lang.capitalize()}, Sir."
        else:
            response = "What would you like me to say in that language, Boss?"

    elif "check" in user_input and ("message" in user_input or "unread" in user_input):
        response = hands.check_unread_whatsapp()

    elif "whatsapp" in user_input or "message" in user_input:
        # 1. Identify the contact dynamically using a known list
        valid_contacts = ["kanna", "mom", "friend", "nikhil"]
        
        # This scans the sentence and finds the first valid contact, regardless of grammar!
        target_contact = next((c for c in valid_contacts if c in user_input.lower()), None)
        
        if not target_contact:
            response = "I couldn't identify who you want to send the message to, Sir."
        else:
            # 2. Extract the message payload dynamically
            message_text = ""
            if "saying" in user_input:
                message_text = user_input.split("saying", 1)[1]
            elif "that" in user_input:
                message_text = user_input.split("that", 1)[1]
            else:
                message_text = user_input # Fallback
            
            # 3. Clean up the messy translation grammar Google adds to the end
            message_text = message_text.lower().replace(f"to {target_contact}", "").replace("on whatsapp", "").strip()
            
            if not message_text: message_text = "Hello" # Failsafe
            
            response = hands.send_whatsapp_message(target_contact, message_text)

    elif any(word in user_input for word in ["pause", "play", "stop", "skip", "next", "previous", "back", "mute", "volume", "louder", "quieter"]):
        # This will now perfectly catch "play music on Spotify" and trigger the Ghost Keyboard!
        response = hands.control_media(user_input)
            
    elif "remind" in user_input and "at" in user_input:
        response = temporal_mind.set_reminder(user_input)
            
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