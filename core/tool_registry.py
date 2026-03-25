"""
JARVIS 2.0 — Centralized Tool Registry
Stores all system capabilities as ToolSpec entries.
Supports dynamic registration, lookup, and keyword-based discovery.
"""
from dataclasses import dataclass, field
from typing import Optional
from core.logger import get_logger

logger = get_logger("ToolRegistry")


@dataclass
class ToolSpec:
    """Specification for a single JARVIS tool / capability."""
    name: str                            # Unique ID:       "check_whatsapp"
    description: str                     # Human-readable:  "Check unread WhatsApp messages"
    module_path: str                     # Import target:   "tools.action_engine"
    function_name: str                   # Callable:        "check_unread_whatsapp"
    keywords: list[str] = field(default_factory=list)   # Trigger words for intent matching
    parameters: dict = field(default_factory=dict)      # Expected params: {"contact": "str"}
    is_async: bool = False               # Whether execution needs await
    category: str = "general"            # Grouping: "media", "communication", "system"


class ToolRegistry:
    """
    Central registry of all JARVIS tools.
    New tools are added via register() — no code changes elsewhere needed.
    """

    def __init__(self):
        self._tools: dict[str, ToolSpec] = {}
        logger.info("Tool Registry initialized.")

    # ── Registration ──────────────────────────────────────────────
    def register(self, spec: ToolSpec):
        """Register a tool. Overwrites if name already exists."""
        self._tools[spec.name] = spec
        logger.info(f"Registered tool: {spec.name}")

    def unregister(self, name: str):
        """Remove a tool by name."""
        if name in self._tools:
            del self._tools[name]
            logger.info(f"Unregistered tool: {name}")

    # ── Lookup ────────────────────────────────────────────────────
    def get(self, name: str) -> Optional[ToolSpec]:
        """Get a tool spec by exact name."""
        return self._tools.get(name)

    def list_all(self) -> list[ToolSpec]:
        """Return all registered tools."""
        return list(self._tools.values())

    def list_by_category(self, category: str) -> list[ToolSpec]:
        """Return tools filtered by category."""
        return [t for t in self._tools.values() if t.category == category]

    def search(self, query: str) -> list[ToolSpec]:
        """Search tools by keyword overlap with the query string."""
        query_lower = query.lower()
        scored = []
        for tool in self._tools.values():
            score = sum(1 for kw in tool.keywords if kw in query_lower)
            if score > 0:
                scored.append((score, tool))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored]

    def __len__(self):
        return len(self._tools)

    def __repr__(self):
        return f"ToolRegistry({len(self._tools)} tools)"


# ══════════════════════════════════════════════════════════════════
# Default registry instance + built-in tool registration
# ══════════════════════════════════════════════════════════════════
registry = ToolRegistry()


def _register_builtin_tools():
    """Pre-register all existing JARVIS capabilities."""

    # ── Time ──────────────────────────────────────────────────────
    registry.register(ToolSpec(
        name="get_time",
        description="Tell the user the current time",
        module_path="tools.action_engine",
        function_name="get_time",
        keywords=["time", "clock", "hour", "what time"],
        category="system",
    ))

    # ── YouTube ───────────────────────────────────────────────────
    registry.register(ToolSpec(
        name="play_youtube",
        description="Search and play a video on YouTube",
        module_path="tools.action_engine",
        function_name="play_youtube",
        keywords=["youtube", "play", "video", "watch"],
        parameters={"query": "str"},
        category="media",
    ))

    # ── Google Search ─────────────────────────────────────────────
    registry.register(ToolSpec(
        name="search_google",
        description="Search Google for a query",
        module_path="tools.action_engine",
        function_name="search_google",
        keywords=["google", "search", "look up", "find"],
        parameters={"query": "str"},
        category="web",
    ))

    # ── Open Application ──────────────────────────────────────────
    registry.register(ToolSpec(
        name="open_application",
        description="Launch a desktop application",
        module_path="tools.action_engine",
        function_name="open_application",
        keywords=["open", "launch", "start", "run"],
        parameters={"command": "str"},
        category="system",
    ))

    # ── Open Website ──────────────────────────────────────────────
    registry.register(ToolSpec(
        name="open_website",
        description="Open a website in the browser",
        module_path="tools.action_engine",
        function_name="open_website",
        keywords=["open", "website", "browse", "go to"],
        parameters={"site": "str", "url": "str"},
        category="web",
    ))

    # ── Media Control ─────────────────────────────────────────────
    registry.register(ToolSpec(
        name="control_media",
        description="Control media playback (pause, play, skip, volume)",
        module_path="tools.action_engine",
        function_name="control_media",
        keywords=["pause", "play", "stop", "skip", "next", "previous", "mute", "volume", "louder", "quieter"],
        parameters={"command": "str"},
        category="media",
    ))

    # ── WhatsApp Check ────────────────────────────────────────────
    registry.register(ToolSpec(
        name="check_whatsapp",
        description="Check unread WhatsApp messages",
        module_path="tools.action_engine",
        function_name="check_unread_whatsapp",
        keywords=["check", "unread", "whatsapp", "messages", "notifications", "inbox"],
        category="communication",
    ))

    # ── WhatsApp Send ─────────────────────────────────────────────
    registry.register(ToolSpec(
        name="send_whatsapp",
        description="Send a WhatsApp message to a contact",
        module_path="tools.action_engine",
        function_name="send_whatsapp_message",
        keywords=["send", "whatsapp", "message", "text"],
        parameters={"contact": "str", "message": "str"},
        category="communication",
    ))

    # ── Translation ───────────────────────────────────────────────
    registry.register(ToolSpec(
        name="translate_speech",
        description="Translate and speak a phrase in another language",
        module_path="agents.translation_agent",
        function_name="translate_and_speak",
        keywords=["translate", "say", "telugu", "hindi", "in telugu", "in hindi"],
        parameters={"phrase": "str", "target_lang": "str"},
        category="language",
    ))

    # ── Memory: Remember ──────────────────────────────────────────
    registry.register(ToolSpec(
        name="remember_fact",
        description="Store a fact in long-term memory",
        module_path="agents.memory_agent",
        function_name="remember_fact",
        keywords=["remember", "store", "save", "note"],
        parameters={"fact": "str"},
        category="memory",
    ))

    # ── Memory: Recall ────────────────────────────────────────────
    registry.register(ToolSpec(
        name="recall_facts",
        description="Recall stored facts from memory",
        module_path="agents.memory_agent",
        function_name="recall_facts",
        keywords=["recall", "what do you remember", "memory", "what do you know"],
        category="memory",
    ))

    # ── Reminders ─────────────────────────────────────────────────
    registry.register(ToolSpec(
        name="set_reminder",
        description="Set a timed reminder",
        module_path="agents.planning_agent",
        function_name="set_reminder",
        keywords=["remind", "reminder", "alert", "schedule"],
        parameters={"user_input": "str"},
        category="planning",
    ))


    logger.info(f"Built-in tools registered: {len(registry)} tools ready.")


# Auto-register on import
_register_builtin_tools()
