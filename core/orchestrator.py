from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

# Import JARVIS's two brains and his voice
from services.executive_mind import ExecutiveMind
from services.analytical_mind import AnalyticalMind
from core.logger import get_logger
from config.system_config import JarvisConfig

logger = get_logger("Orchestrator")

# 1. Define the Memory State
# This is the shared data payload passed between the nodes
class AgentState(TypedDict):
    messages: list[str]
    complexity: str
    final_response: str

# 2. Wake up the Brains
logger.info("Booting up the Trinity Mind architecture...")
local_brain = ExecutiveMind()
cloud_brain = AnalyticalMind()

# 3. Define the Nodes (The Agents)
def router_node(state: AgentState):
    """The Traffic Cop: Decides if the task stays local or goes to the cloud."""
    user_input = state["messages"][-1].lower()
    
    # Simple keyword routing (We will upgrade this to AI-driven routing later)
    cloud_triggers = ["research", "explain", "summarize", "code", "analyze"]
    
    if any(keyword in user_input for keyword in cloud_triggers):
        complexity = "cloud"
        logger.info("Router: Complex task detected. Preparing Cloud transfer.")
    else:
        complexity = "local"
        logger.info("Router: Simple task detected. Keeping it Local.")
        
    return {"complexity": complexity}

def local_node(state: AgentState):
    """Hands the task to Gemma 3."""
    response = local_brain.think(state["messages"][-1])
    return {"final_response": response}

def cloud_node(state: AgentState):
    """Hands the task to Gemini 2.5."""
    response = cloud_brain.think(state["messages"][-1])
    return {"final_response": response}

# 4. Define the Conditional Edge Logic
def route_task(state: AgentState) -> Literal["local_node", "cloud_node"]:
    """The actual switch track that diverts the flow."""
    if state["complexity"] == "cloud":
        return "cloud_node"
    return "local_node"

# 5. Build and Compile the Master Graph
builder = StateGraph(AgentState)

# Add our three functional nodes
builder.add_node("router", router_node)
builder.add_node("local_node", local_node)
builder.add_node("cloud_node", cloud_node)

# Map the workflow
builder.add_edge(START, "router")
builder.add_conditional_edges("router", route_task)
builder.add_edge("local_node", END)
builder.add_edge("cloud_node", END)

# Compile the final JARVIS entity
jarvis_mind = builder.compile()

# --- Test the Unified System ---
if __name__ == "__main__":
    JarvisConfig.validate_keys()
    print("\n🧠 Testing the Master Orchestrator...\n")
    
    # Test 1: A simple greeting (Should stay local)
    print("--- Test 1: Local Reflex ---")
    state1 = jarvis_mind.invoke({"messages": ["Hello! Acknowledge systems are online."]})
    print(f"\nJARVIS: {state1['final_response']}\n")
    print("-" * 40)
    
    # Test 2: A complex request (Should route to cloud)
    print("\n--- Test 2: Cloud Intellect ---")
    state2 = jarvis_mind.invoke({"messages": ["Summarize the concept of quantum computing in exactly one sentence."]})
    print(f"\nJARVIS: {state2['final_response']}\n")