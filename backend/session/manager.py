import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

SESSIONS_DIR = Path.home() / ".meeting-translator" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, dict] = {}

    def create_session(self, session_id: str, target_lang: str, profile_id: Optional[str] = None) -> dict:
        session = {
            "session_id": session_id,
            "target_lang": target_lang,
            "profile_id": profile_id,
            "start_time": datetime.now().isoformat(),
            "phrases": [],
            "active": True,
        }
        self._sessions[session_id] = session
        self._save(session_id)
        return session

    def get_session(self, session_id: str) -> Optional[dict]:
        return self._sessions.get(session_id)

    def add_phrase(self, session_id: str, original: str, translated: str):
        session = self._sessions.get(session_id)
        if session:
            session["phrases"].append({
                "original":   original,
                "translated": translated,
                "timestamp":  datetime.now().isoformat(),
            })
            self._save(session_id)

    def end_session(self, session_id: str):
        session = self._sessions.get(session_id)
        if session:
            start = datetime.fromisoformat(session["start_time"])
            session["duration_minutes"] = round((datetime.now() - start).total_seconds() / 60, 1)
            session["active"] = False
            self._save(session_id)

    def list_active(self) -> List[str]:
        return [sid for sid, s in self._sessions.items() if s.get("active")]

    # ── persistence ──────────────────────────────────────────────────────────

    def _save(self, session_id: str):
        session = self._sessions.get(session_id)
        if not session:
            return
        path = SESSIONS_DIR / f"{session_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2, ensure_ascii=False)

    def load_all(self):
        """Re-hydrate sessions from disk on startup (optional warm-start)."""
        for path in SESSIONS_DIR.glob("*.json"):
            try:
                with open(path, encoding="utf-8") as f:
                    session = json.load(f)
                # Only restore finished sessions — active ones from a previous run are stale
                if not session.get("active", True):
                    self._sessions[session["session_id"]] = session
            except Exception:
                pass
