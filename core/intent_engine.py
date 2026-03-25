"""
JARVIS 2.0 — Intent Engine
Maps natural-language user input to the best-matching tool in the registry.
"""
import re
from typing import Optional
from core.tool_registry import registry, ToolSpec
from core.logger import get_logger

logger = get_logger("IntentEngine")


class IntentEngine:
    """
    Resolves user input to a registered tool name + extracted parameters.
    Uses keyword scoring with priority rules.
    Future: swap internals for vector-search or LLM-based classification.
    """

    # Minimum keyword hits required to consider a match
    MIN_SCORE = 1

    def resolve(self, user_input: str) -> Optional[dict]:
        """
        Returns {"tool": ToolSpec, "params": {}} or None if no match.
        """
        user_lower = user_input.lower()
        best_tool: Optional[ToolSpec] = None
        best_score = 0

        for tool in registry.list_all():
            score = 0
            for kw in tool.keywords:
                if kw in user_lower:
                    # Longer keywords get bonus weight (e.g. "what time" > "time")
                    score += len(kw.split())
            if score > best_score:
                best_score = score
                best_tool = tool

        if best_score < self.MIN_SCORE or best_tool is None:
            logger.info(f"IntentEngine: No tool matched for '{user_input}'")
            return None

        # Extract parameters from the user input based on tool spec
        params = self._extract_params(user_lower, best_tool)

        logger.info(f"IntentEngine: Resolved '{user_input}' -> {best_tool.name} (score={best_score})")
        return {"tool": best_tool, "params": params}

    def _extract_params(self, user_input: str, tool: ToolSpec) -> dict:
        """
        Best-effort parameter extraction from natural language.
        Each tool may need custom extraction logic for its params.
        """
        params = {}

        if tool.name == "play_youtube":
            query = user_input
            for word in ["jarvis", "play", "youtube", "search", "on", "for", "is"]:
                query = re.sub(rf'\b{word}\b', '', query)
            params["query"] = query.strip() or "trending"

        elif tool.name == "search_google":
            query = user_input
            for word in ["jarvis", "search", "google", "for", "look up", "find"]:
                query = re.sub(rf'\b{word}\b', '', query)
            params["query"] = query.strip() or "technology news"

        elif tool.name == "open_application":
            params["command"] = user_input

        elif tool.name == "open_website":
            site = user_input
            for word in ["jarvis", "open", "go to", "browse"]:
                site = site.replace(word, "")
            site = site.strip()
            params["site"] = site
            params["url"] = f"https://www.{site.replace(' ', '')}.com"

        elif tool.name == "control_media":
            params["command"] = user_input

        elif tool.name == "translate_speech":
            target_lang = "telugu" if "telugu" in user_input else "hindi"
            phrase = user_input
            for word in ["jarvis", "say", "translate", f"in {target_lang}"]:
                phrase = phrase.replace(word, "")
            params["phrase"] = phrase.strip()
            params["target_lang"] = target_lang

        elif tool.name == "remember_fact":
            fact = user_input
            for word in ["jarvis", "remember that", "remember"]:
                fact = fact.replace(word, "")
            params["fact"] = fact.strip().capitalize()

        elif tool.name == "set_reminder":
            params["user_input"] = user_input

        elif tool.name == "send_whatsapp":
            # Basic contact and message extraction
            valid_contacts = ["kanna", "mom", "friend", "nikhil", "budda bava", "amma"]
            target_contact = next((c for c in valid_contacts if c in user_input), None)
            params["contact"] = target_contact or "Unknown"
            message_text = ""
            if "saying" in user_input:
                message_text = user_input.split("saying", 1)[1]
            elif "that" in user_input:
                message_text = user_input.split("that", 1)[1]
            else:
                message_text = user_input
            message_text = message_text.replace(f"to {target_contact}", "").replace("on whatsapp", "").strip()
            params["message"] = message_text or "Hello"

        return params


# Singleton
intent_engine = IntentEngine()
