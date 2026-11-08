"""SQLite-backed conversation history and checkpoints."""
from __future__ import annotations
import json, sqlite3, os
from pathlib import Path
from typing import Any
from uuid import uuid4

class SessionStore:
    def __init__(self, path: Path | None = None):
        self.path = path or (Path.home() / ".claude" / "sessions.sqlite3")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _init(self):
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
              id TEXT PRIMARY KEY, workspace TEXT NOT NULL, title TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS messages (
              id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
              role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS messages_session_idx ON messages(session_id,id);
            CREATE TABLE IF NOT EXISTS checkpoints (
              id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
              label TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """)

    def create(self, workspace: str, title: str = "New session") -> str:
        sid = str(uuid4())
        with self._connect() as db:
            db.execute("INSERT INTO sessions(id,workspace,title) VALUES(?,?,?)", (sid,workspace,title[:160]))
        return sid

    def ensure(self, sid: str | None, workspace: str) -> str:
        if sid:
            with self._connect() as db:
                row = db.execute("SELECT id,workspace FROM sessions WHERE id=?", (sid,)).fetchone()
                if row and row["workspace"] == workspace:
                    return sid
            raise KeyError("Session not found for this workspace")
        return self.create(workspace)

    def append(self, sid: str, role: str, content: str):
        if role not in {"user","assistant","tool"}:
            raise ValueError("Invalid message role")
        with self._connect() as db:
            db.execute("INSERT INTO messages(session_id,role,content) VALUES(?,?,?)",(sid,role,content[:200000]))
            db.execute("UPDATE sessions SET updated_at=CURRENT_TIMESTAMP WHERE id=?",(sid,))

    def history(self, sid: str, limit: int = 40) -> list[dict[str,str]]:
        with self._connect() as db:
            rows=db.execute("SELECT role,content FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?",(sid,max(1,min(limit,100)))).fetchall()
        return [{"role":r["role"],"content":r["content"]} for r in reversed(rows)]

    def list(self, workspace: str) -> list[dict[str,Any]]:
        with self._connect() as db:
            rows=db.execute("SELECT s.id,s.title,s.created_at,s.updated_at,(SELECT COUNT(*) FROM messages m WHERE m.session_id=s.id) AS messages FROM sessions s WHERE workspace=? ORDER BY updated_at DESC LIMIT 100",(workspace,)).fetchall()
        return [dict(r) for r in rows]

    def delete(self, sid: str, workspace: str):
        with self._connect() as db:
            db.execute("DELETE FROM sessions WHERE id=? AND workspace=?",(sid,workspace))

    def checkpoint(self, sid: str, label: str, payload: dict[str,Any]):
        with self._connect() as db:
            db.execute("INSERT INTO checkpoints(session_id,label,payload) VALUES(?,?,?)",(sid,label[:160],json.dumps(payload)[:500000]))

    def checkpoints(self, sid: str, workspace: str) -> list[dict[str,Any]]:
        with self._connect() as db:
            owner=db.execute("SELECT 1 FROM sessions WHERE id=? AND workspace=?",(sid,workspace)).fetchone()
            if not owner:
                raise KeyError("Session not found for this workspace")
            rows=db.execute("SELECT id,label,payload,created_at FROM checkpoints WHERE session_id=? ORDER BY id DESC LIMIT 50",(sid,)).fetchall()
        return [{"id":r["id"],"label":r["label"],"payload":json.loads(r["payload"]),"created_at":r["created_at"]} for r in rows]
