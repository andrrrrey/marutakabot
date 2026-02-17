from __future__ import annotations
import aiosqlite
from typing import Any

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY,
  first_name TEXT,
  username TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS user_threads (
  user_id INTEGER PRIMARY KEY,
  thread_id TEXT NOT NULL,
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS settings (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  openai_api_key TEXT,
  openai_assistant_id TEXT,
  openai_vector_store_id TEXT,
  updated_at TEXT DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO settings (id) VALUES (1);
"""

class DB:
    def __init__(self, path: str):
        self.path = path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(SCHEMA)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if not self._conn:
            raise RuntimeError("DB not connected")
        return self._conn

    async def upsert_user(self, user_id: int, first_name: str | None, username: str | None) -> None:
        await self.conn.execute(
            """INSERT INTO users(user_id, first_name, username)
                 VALUES(?, ?, ?)
                 ON CONFLICT(user_id) DO UPDATE SET
                   first_name=excluded.first_name,
                   username=excluded.username
            """,
            (user_id, first_name, username),
        )
        await self.conn.commit()

    async def get_user_thread(self, user_id: int) -> str | None:
        cur = await self.conn.execute("SELECT thread_id FROM user_threads WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return row["thread_id"] if row else None

    async def set_user_thread(self, user_id: int, thread_id: str) -> None:
        await self.conn.execute(
            """INSERT INTO user_threads(user_id, thread_id)
                 VALUES(?, ?)
                 ON CONFLICT(user_id) DO UPDATE SET
                   thread_id=excluded.thread_id,
                   updated_at=datetime('now')
            """,
            (user_id, thread_id),
        )
        await self.conn.commit()

    async def get_settings(self) -> dict[str, Any]:
        cur = await self.conn.execute(
            "SELECT openai_api_key, openai_assistant_id, openai_vector_store_id FROM settings WHERE id=1"
        )
        row = await cur.fetchone()
        return dict(row) if row else {"openai_api_key": None, "openai_assistant_id": None, "openai_vector_store_id": None}

    async def update_settings(
        self,
        *,
        openai_api_key: str | None = None,
        openai_assistant_id: str | None = None,
        openai_vector_store_id: str | None = None
    ) -> None:
        current = await self.get_settings()
        new_key = openai_api_key if openai_api_key is not None else current.get("openai_api_key")
        new_asst = openai_assistant_id if openai_assistant_id is not None else current.get("openai_assistant_id")
        new_vs = openai_vector_store_id if openai_vector_store_id is not None else current.get("openai_vector_store_id")

        await self.conn.execute(
            """UPDATE settings
                 SET openai_api_key=?,
                     openai_assistant_id=?,
                     openai_vector_store_id=?,
                     updated_at=datetime('now')
                 WHERE id=1
            """,
            (new_key, new_asst, new_vs),
        )
        await self.conn.commit()
