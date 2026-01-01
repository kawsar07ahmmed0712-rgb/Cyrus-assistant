import re
from typing import Iterable

DEFAULT_COMMAND_PHRASES = [
    "open google",
    "open youtube",
    "search google",
    "search youtube",
    "google ",
    "youtube ",
    "search ",
]

def is_command(text: str, extra_phrases: Iterable[str] = ()) -> bool:
    """
    Return True if text likely contains a simple command we can handle.
    This is intentionally permissive (contains / startswith) to handle varied user phrasing.
    """
    if not text:
        return False
    txt = text.lower().strip()
    for p in list(DEFAULT_COMMAND_PHRASES) + list(extra_phrases):
        if p and p in txt:
            return True
    if re.search(r"\b(open|visit|search|find|google|youtube)\b", txt):
        return True
    return False
