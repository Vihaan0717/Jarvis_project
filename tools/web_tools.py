import webbrowser
import urllib.parse
from core.logger import get_logger

logger = get_logger("WebTools")

class WebTools:
    """
    Tools for web interaction and search.
    """
    @staticmethod
    def open_website(url: str) -> str:
        webbrowser.open(url)
        return f"Opening {url}."

    @staticmethod
    def search_google(query: str) -> str:
        safe_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={safe_query}"
        webbrowser.open(url)
        return f"Searching Google for: {query}"

    @staticmethod
    def play_youtube(query: str) -> str:
        safe_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={safe_query}"
        webbrowser.open(url)
        return f"Opening YouTube results for: {query}"
