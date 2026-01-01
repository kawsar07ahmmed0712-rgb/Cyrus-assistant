# core/memory.py
import json
import os
import tempfile
from datetime import datetime
from typing import List, Dict, Any
import threading
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Thread-safe file-backed session memory manager.
    Stores messages per session as a list of dicts.
    """

    def __init__(self, file_path: str = "History.json", max_messages: int = 200):
        self.file_path = file_path
        self.max_messages = max_messages
        self._lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self):
        dirpath = os.path.dirname(self.file_path)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({"sessions": {}}, f, indent=2)

    def _load(self) -> Dict[str, Any]:
        with self._lock:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.exception("JSON decode error when loading memory file; returning empty structure.")
                return {"sessions": {}}
            except FileNotFoundError:
                return {"sessions": {}}

    def _save(self, data: Dict[str, Any]):
        with self._lock:
            dirpath = os.path.dirname(self.file_path) or "."
            fd, tmp = tempfile.mkstemp(dir=dirpath, prefix=".tmp_history_", text=True)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                os.replace(tmp, self.file_path)
            except Exception:
                logger.exception("Failed to write memory file atomically.")
                if os.path.exists(tmp):
                    os.remove(tmp)
                raise

    def add_message(self, session_id: str, role: str, content: str, model: str = "gemini"):
        data = self._load()
        sessions = data.setdefault("sessions", {})
        msgs = sessions.setdefault(session_id, [])
        msgs.append({
            "role": role,
            "content": content,
            "model": model,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        sessions[session_id] = msgs[-self.max_messages:]
        data["sessions"] = sessions
        self._save(data)

    def get_context(self, session_id: str) -> List[Dict[str, Any]]:
        data = self._load()
        return data.get("sessions", {}).get(session_id, [])

    def clear_session(self, session_id: str):
        data = self._load()
        if session_id in data.get("sessions", {}):
            del data["sessions"][session_id]
            self._save(data)

    def clear_all(self):
        self._save({"sessions": {}})

