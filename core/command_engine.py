
import webbrowser
import urllib.parse
from typing import Optional
import logging
import re

logger = logging.getLogger(__name__)

class CommandEngine:
    """
    Handles system & browser level commands. Returns user-friendly messages on actions.
    """

    def __init__(self):
        self._open_map = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
        }

    def execute(self, command: str) -> str:
        if not command or not command.strip():
            return "No command provided."

        cmd = command.lower().strip()


        open_match = re.search(r"\b(open|go to|visit)\b\s+(\w+)", cmd)
        if open_match:
            site = open_match.group(2)
            url = self._open_map.get(site)
            if url:
                try:
                    webbrowser.open(url)
                    return f"Opening {site.capitalize()}."
                except Exception as e:
                    logger.exception("Failed to open browser URL: %s", e)
                    return f"Failed to open {site}: {e}"
            return f"I don't know how to open '{site}'. Try 'open google' or 'open youtube'."

        if "search google" in cmd or cmd.startswith("google "):
            q = re.sub(r"(search google|google)\s*", "", cmd).strip()
            if not q:
                return "What do you want to search for on Google?"
            url = f"https://www.google.com/search?q={urllib.parse.quote(q)}"
            try:
                webbrowser.open(url)
                return f"Searching Google for '{q}'."
            except Exception as e:
                logger.exception("Failed to open search URL: %s", e)
                return f"Failed to perform search: {e}"
            
        if "search youtube" in cmd or cmd.startswith("youtube "):
            q = re.sub(r"(search youtube|youtube)\s*", "", cmd).strip()
            if not q:
                return "What do you want to search for on YouTube?"
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}"
            try:
                webbrowser.open(url)
                return f"Searching YouTube for '{q}'."
            except Exception as e:
                logger.exception("Failed to open search URL: %s", e)
                return f"Failed to perform search: {e}"

        return "Unknown command. Try 'open google', 'search google cats', or 'search youtube cats'."
