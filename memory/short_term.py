"""
memory/short_term.py
Conversation ring buffer — persists across restarts via JSON.
"""
import json
import threading
from pathlib import Path
from typing import Optional


class ShortTermMemory:
    def __init__(self, filepath: str = "data/short_term.json", buffer_size: int = 20):
        self.filepath = Path(filepath)
        self.buffer_size = buffer_size
        self._lock = threading.Lock()
        self.buffer: list[dict] = self._load()

    def _load(self) -> list[dict]:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.buffer, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def add(self, user_msg: str, assistant_msg: str):
        with self._lock:
            self.buffer.append({"user": user_msg, "assistant": assistant_msg})
            if len(self.buffer) > self.buffer_size:
                self.buffer.pop(0)
            self._save()

    def get_last(self, n: int = 10) -> list[dict]:
        with self._lock:
            return self.buffer[-n:] if len(self.buffer) >= n else self.buffer[:]

    def format_for_prompt(self, n: int = 10) -> str:
        """Return recent exchanges formatted as a string for prompt injection."""
        exchanges = self.get_last(n)
        if not exchanges:
            return ""
        lines = []
        for ex in exchanges:
            lines.append(f"User: {ex['user']}")
            lines.append(f"Jane: {ex['assistant']}")
        return "\n".join(lines)

    def clear(self):
        with self._lock:
            self.buffer = []
            self._save()

    def __len__(self) -> int:
        return len(self.buffer)
