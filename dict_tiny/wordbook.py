import os
import sqlite3
import time
from dataclasses import dataclass

from dict_tiny.config import MAX_ENTRIES
from dict_tiny.util import get_data_dir


@dataclass
class WordBookEntry:
    id: int
    text: str
    source_language: str | None
    target_language: str | None
    translator: str | None
    timestamp: float
    last_access: float
    access_count: int


class WordBook:
    def __init__(self, path=None):
        if path is None:
            path = str(get_data_dir() / "wordbook.db")
        self._path = path
        self._conn = None
        try:
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            self._conn = sqlite3.connect(self._path, check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._init_db()
        except Exception:
            if self._conn:
                self._conn.close()
                self._conn = None

    @classmethod
    def open(cls, path=None):
        """Create WordBook instance. Returns None if database is unavailable."""
        instance = cls(path)
        if instance._conn is None:
            print("Word book database is not available.")
            return None
        return instance

    @classmethod
    def db_exists(cls, path=None):
        if path is None:
            path = str(get_data_dir() / "wordbook.db")
        return os.path.isfile(path)

    def _init_db(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS entries (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                text            TEXT NOT NULL UNIQUE,
                source_language TEXT,
                target_language TEXT,
                translator      TEXT,
                timestamp       REAL NOT NULL,
                last_access     REAL NOT NULL,
                access_count    INTEGER NOT NULL DEFAULT 1
            );
            CREATE INDEX IF NOT EXISTS idx_entries_timestamp
                ON entries(timestamp);
            CREATE INDEX IF NOT EXISTS idx_entries_last_access
                ON entries(last_access);
            CREATE INDEX IF NOT EXISTS idx_entries_access_count
                ON entries(access_count);
            CREATE TABLE IF NOT EXISTS config (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)

    # ── core CRUD ──────────────────────────────────────────────

    def record(self, text, source_language, target_language, translator):
        if not self._conn:
            return False
        try:
            now = time.time()
            cur = self._conn.execute(
                "SELECT id, access_count FROM entries WHERE text = ?", (text,)
            )
            row = cur.fetchone()
            if row:
                self._conn.execute(
                    "UPDATE entries SET last_access = ?, access_count = access_count + 1,"
                    " source_language = ?, target_language = ?, translator = ?"
                    " WHERE id = ?",
                    (now, source_language, target_language, translator, row[0]),
                )
            else:
                count = self._conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
                if count >= MAX_ENTRIES:
                    self._conn.execute(
                        "DELETE FROM entries WHERE id = ("
                        "SELECT id FROM entries ORDER BY last_access ASC LIMIT 1"
                        ")"
                    )
                self._conn.execute(
                    "INSERT INTO entries (text, source_language, target_language,"
                    " translator, timestamp, last_access, access_count)"
                    " VALUES (?, ?, ?, ?, ?, ?, 1)",
                    (text, source_language, target_language, translator, now, now),
                )
            self._conn.commit()
            return True
        except Exception:
            return False

    def get_entry(self, index):
        if not self._conn or index < 1:
            return None
        try:
            row = self._conn.execute(
                "SELECT id, text, source_language, target_language, translator,"
                " timestamp, last_access, access_count"
                " FROM entries ORDER BY timestamp DESC LIMIT 1 OFFSET ?",
                (index - 1,),
            ).fetchone()
            if row is None:
                return None
            return WordBookEntry(*row)
        except Exception:
            return None

    def delete(self, index):
        if not self._conn:
            return False
        try:
            row = self._conn.execute(
                "SELECT id FROM entries ORDER BY timestamp DESC LIMIT 1 OFFSET ?",
                (index - 1,),
            ).fetchone()
            if row is None:
                return False
            self._conn.execute("DELETE FROM entries WHERE id = ?", (row[0],))
            self._conn.commit()
            return True
        except Exception:
            return False

    # ── list / query ───────────────────────────────────────────

    def list_entries(self, page=1, page_size=20, sort_by="time"):
        if not self._conn or page < 1:
            return [], 0
        sort_map = {
            "time": "timestamp DESC",
            "freq": "access_count DESC",
            "recent": "last_access DESC",
        }
        order = sort_map.get(sort_by, "timestamp DESC")
        try:
            total = self._conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
            offset = (page - 1) * page_size
            rows = self._conn.execute(
                f"SELECT id, text, source_language, target_language, translator,"
                f" timestamp, last_access, access_count"
                f" FROM entries ORDER BY {order} LIMIT ? OFFSET ?",
                (page_size, offset),
            ).fetchall()
            return [WordBookEntry(*r) for r in rows], total
        except Exception:
            return [], 0

    def list_entries_since(self, timestamp, page=1, page_size=20):
        if not self._conn or page < 1:
            return [], 0
        try:
            total = self._conn.execute(
                "SELECT COUNT(*) FROM entries WHERE timestamp >= ?", (timestamp,)
            ).fetchone()[0]
            offset = (page - 1) * page_size
            rows = self._conn.execute(
                "SELECT id, text, source_language, target_language, translator,"
                " timestamp, last_access, access_count"
                " FROM entries WHERE timestamp >= ?"
                " ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                (timestamp, page_size, offset),
            ).fetchall()
            return [WordBookEntry(*r) for r in rows], total
        except Exception:
            return [], 0

    def count(self):
        if not self._conn:
            return 0
        try:
            return self._conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        except Exception:
            return 0

    # ── config ─────────────────────────────────────────────────

    def get_config(self):
        count = self.count()
        return {"count": count, "default_record": self.get_default_record()}

    def get_default_record(self):
        if not self._conn:
            return False
        try:
            row = self._conn.execute(
                "SELECT value FROM config WHERE key = 'default_record'"
            ).fetchone()
            return row is not None and row[0] == "1"
        except Exception:
            return False

    def set_default_record(self, on):
        if not self._conn:
            return
        try:
            self._conn.execute(
                "INSERT OR REPLACE INTO config (key, value) VALUES ('default_record', ?)",
                ("1" if on else "0",),
            )
            self._conn.commit()
        except Exception:
            pass

    # ── lifecycle ──────────────────────────────────────────────

    def delete_db(self):
        self.close()
        try:
            os.remove(self._path)
        except OSError:
            pass

    def close(self):
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None
