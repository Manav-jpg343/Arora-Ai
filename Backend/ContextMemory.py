"""
ContextMemory.py - Contextual Memory Module for Aura OS

Tracks recent OS events, user actions, conversation history, and system state
so the assistant can understand context like "the file I just downloaded" or
"go back to the app I was using".
"""

import os
import json
import time
import datetime
from collections import deque
from threading import Lock

MEMORY_FILE = os.path.join(os.getcwd(), "Data", "Memory.json")

class ContextMemory:
    """
    Persistent + in-memory contextual memory that tracks:
    - Recent user queries and assistant responses
    - Recent file operations (downloads, opens, creates)
    - Recent app interactions (opened, closed, focused)
    - System events (volume changes, screenshots, etc.)
    - Current session state
    """

    def __init__(self, max_events: int = 100, max_conversation: int = 30):
        self._lock = Lock()
        self.max_events = max_events
        self.max_conversation = max_conversation

        # In-memory stores
        self.conversation: list[dict] = []         # {role, content, timestamp}
        self.recent_events: deque = deque(maxlen=max_events)  # {type, detail, timestamp}
        self.session_state: dict = {
            "current_app": None,
            "last_app": None,
            "last_query": None,
            "last_file": None,
            "last_url": None,
            "last_folder": None,
            "tasks_executed": 0,
            "errors_encountered": 0,
            "session_start": datetime.datetime.now().isoformat(),
        }

        self._load()

    # ──────────── Conversation ────────────

    def add_user_message(self, content: str):
        """Record a user message."""
        with self._lock:
            entry = {
                "role": "user",
                "content": content,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.conversation.append(entry)
            self.session_state["last_query"] = content
            self._trim_conversation()
            self._save()

    def add_assistant_message(self, content: str):
        """Record an assistant response."""
        with self._lock:
            entry = {
                "role": "assistant",
                "content": content,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.conversation.append(entry)
            self._trim_conversation()
            self._save()

    def get_conversation_context(self, last_n: int = 10) -> list[dict]:
        """Get last N conversation messages for LLM context."""
        with self._lock:
            return list(self.conversation[-last_n:])

    # ──────────── Events ────────────

    def log_event(self, event_type: str, detail: str, metadata: dict = None):
        """
        Log an OS/system event.
        event_type: "app_opened", "app_closed", "file_created", "file_opened",
                    "url_opened", "command_run", "screenshot", "error", etc.
        """
        with self._lock:
            event = {
                "type": event_type,
                "detail": detail,
                "metadata": metadata or {},
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.recent_events.append(event)

            # Update session state based on event type
            if event_type == "app_opened":
                self.session_state["last_app"] = self.session_state.get("current_app")
                self.session_state["current_app"] = detail
            elif event_type == "app_closed":
                if self.session_state.get("current_app") == detail:
                    self.session_state["current_app"] = self.session_state.get("last_app")
            elif event_type in ("file_created", "file_opened"):
                self.session_state["last_file"] = detail
            elif event_type == "url_opened":
                self.session_state["last_url"] = detail
            elif event_type == "folder_opened":
                self.session_state["last_folder"] = detail
            elif event_type == "task_executed":
                self.session_state["tasks_executed"] = self.session_state.get("tasks_executed", 0) + 1
            elif event_type == "error":
                self.session_state["errors_encountered"] = self.session_state.get("errors_encountered", 0) + 1

            self._save()

    def get_recent_events(self, event_type: str = None, last_n: int = 10) -> list[dict]:
        """Get recent events, optionally filtered by type."""
        with self._lock:
            events = list(self.recent_events)
            if event_type:
                events = [e for e in events if e["type"] == event_type]
            return events[-last_n:]

    # ──────────── Session State ────────────

    def get_state(self, key: str = None):
        """Get session state or specific key."""
        with self._lock:
            if key:
                return self.session_state.get(key)
            return dict(self.session_state)

    def set_state(self, key: str, value):
        """Update a session state value."""
        with self._lock:
            self.session_state[key] = value
            self._save()

    # ──────────── Context Summary (for LLM) ────────────

    def get_context_summary(self) -> str:
        """
        Build a concise context string for the Strategist LLM,
        including recent events and session state.
        """
        with self._lock:
            lines = []
            lines.append("=== Current Context ===")

            # Time
            now = datetime.datetime.now()
            lines.append(f"Date/Time: {now.strftime('%A, %B %d, %Y %I:%M %p')}")

            # Session state
            if self.session_state.get("current_app"):
                lines.append(f"Currently active app: {self.session_state['current_app']}")
            if self.session_state.get("last_file"):
                lines.append(f"Last file accessed: {self.session_state['last_file']}")
            if self.session_state.get("last_url"):
                lines.append(f"Last URL visited: {self.session_state['last_url']}")
            if self.session_state.get("last_folder"):
                lines.append(f"Last folder opened: {self.session_state['last_folder']}")

            # Recent events (last 5)
            recent = list(self.recent_events)[-5:]
            if recent:
                lines.append("\nRecent actions:")
                for e in recent:
                    lines.append(f"  - [{e['type']}] {e['detail']}")

            lines.append("=== End Context ===")
            return "\n".join(lines)

    # ──────────── Persistence ────────────

    def _trim_conversation(self):
        """Keep conversation within limits."""
        if len(self.conversation) > self.max_conversation:
            self.conversation = self.conversation[-self.max_conversation:]

    def _save(self):
        """Save conversation and state to disk."""
        try:
            data = {
                "conversation": self.conversation[-self.max_conversation:],
                "session_state": self.session_state,
                "recent_events": list(self.recent_events)[-50:]  # Save last 50 events
            }
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception:
            pass

    def _load(self):
        """Load conversation and state from disk."""
        try:
            if os.path.exists(MEMORY_FILE):
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.conversation = data.get("conversation", [])
                self.session_state.update(data.get("session_state", {}))
                for event in data.get("recent_events", []):
                    self.recent_events.append(event)
                # Reset session start for new session
                self.session_state["session_start"] = datetime.datetime.now().isoformat()
        except Exception:
            pass

    def clear(self):
        """Clear all memory."""
        with self._lock:
            self.conversation.clear()
            self.recent_events.clear()
            self.session_state = {
                "current_app": None,
                "last_app": None,
                "last_query": None,
                "last_file": None,
                "last_url": None,
                "last_folder": None,
                "tasks_executed": 0,
                "errors_encountered": 0,
                "session_start": datetime.datetime.now().isoformat(),
            }
            self._save()


# Singleton instance
memory = ContextMemory()
