import os
import sqlite3
import time
from dataclasses import dataclass

from dict_tiny.config import MAX_ENTRIES
from dict_tiny.util import get_data_dir


@dataclass
class WordBookEntry:
    """A single wordbook entry record.

    Attributes:
        id: Unique identifier (primary key).
        text: The queried word or phrase.
        source_language: Language of the source text.
        target_language: Language to translate into.
        translator: Translator backend used (e.g. "youdaodict").
        timestamp: Creation time as Unix timestamp.
        last_access: Most recent access time as Unix timestamp.
        access_count: Number of times this entry has been accessed.
    """

    id: int
    text: str
    source_language: str | None
    target_language: str | None
    translator: str | None
    timestamp: float
    last_access: float
    access_count: int


class WordBook:
    """Persistent word book backed by a SQLite database.

    Stores translation query records with access tracking, configurable
    maximum capacity, and automatic eviction of least-recently-used entries.
    """

    def __init__(self, path=None):
        """Initialize the wordbook database connection.

        Args:
            path: Database file path. Defaults to ``<data_dir>/wordbook.db``.
                  The parent directory is created if it does not exist.
        """
        if path is None:
            path = str(get_data_dir() / "wordbook.db")
        self._path = path
        self._conn = None
        try:
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            self._conn = sqlite3.connect(self._path, check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA busy_timeout=3000")
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
        """Check whether the wordbook database file exists on disk.

        Args:
            path: Database file path. Defaults to ``<data_dir>/wordbook.db``.

        Returns:
            True if the file exists, False otherwise.
        """
        if path is None:
            path = str(get_data_dir() / "wordbook.db")
        return os.path.isfile(path)

    def _init_db(self):
        """Create tables and indexes if they do not already exist."""
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
        """Record or update a translation query.

        If the entry limit (``MAX_ENTRIES``) is reached, the least-recently-
        accessed entry is evicted before inserting the new one.  If the text
        already exists its timestamp and access count are updated in place.

        Args:
            text: The queried word or phrase.
            source_language: Language of the source text.
            target_language: Language to translate into.
            translator: Translator backend identifier.

        Returns:
            True on success, False if the database is unavailable or an error
            occurs.
        """
        if not self._conn:
            return False
        try:
            now = time.time()
            existing = self._conn.execute(
                "SELECT id FROM entries WHERE text = ?", (text,)
            ).fetchone()
            if existing is None:
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
                " VALUES (?, ?, ?, ?, ?, ?, 1)"
                " ON CONFLICT(text) DO UPDATE SET"
                " last_access=excluded.last_access, access_count=access_count+1,"
                " source_language=excluded.source_language,"
                " target_language=excluded.target_language,"
                " translator=excluded.translator",
                (text, source_language, target_language, translator, now, now),
            )
            self._conn.commit()
            return True
        except Exception:
            return False

    def get_entry(self, entry_id):
        """Retrieve a single entry by its ID.

        Args:
            entry_id: The entry's primary key.

        Returns:
            A :class:`WordBookEntry` if found, or None if the entry does not
            exist, the ID is invalid, or the database is unavailable.
        """
        if not self._conn or entry_id < 1:
            return None
        try:
            row = self._conn.execute(
                "SELECT id, text, source_language, target_language, translator,"
                " timestamp, last_access, access_count"
                " FROM entries WHERE id = ?",
                (entry_id,),
            ).fetchone()
            if row is None:
                return None
            return WordBookEntry(*row)
        except Exception:
            return None

    def delete(self, entry_id):
        """Delete an entry by its ID.

        Args:
            entry_id: The entry's primary key.

        Returns:
            True if a row was deleted, False otherwise (including when the
            entry does not exist or the database is unavailable).
        """
        if not self._conn:
            return False
        try:
            cur = self._conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            self._conn.commit()
            return cur.rowcount > 0
        except Exception:
            return False

    # ── list / query ───────────────────────────────────────────

    def list_entries(
        self,
        page=1,
        page_size=20,
        sort_by="created",
        since=None,
        search=None,
        exact=False,
    ):
        """List entries with pagination, sorting, and filtering.

        Args:
            page: Page number (1-based).
            page_size: Number of entries per page.
            sort_by: Sort order. One of ``"created"``, ``"freq"``, or
                     ``"recent"``. Falls back to ``"created"`` for unknown
                     values.
            since: Optional Unix timestamp; only entries created at or after
                   this time are included.
            search: Optional search string. Performs a fuzzy ``LIKE`` match
                    unless ``exact`` is True.
            exact: When True, ``search`` performs an exact match instead of
                   fuzzy.

        Returns:
            A tuple ``(entries, total)`` where ``entries`` is a list of
            :class:`WordBookEntry` objects for the requested page, and
            ``total`` is the total number of matching entries across all pages.
            Returns ``([], 0)`` on error or when the database is unavailable.
        """
        if not self._conn or page < 1:
            return [], 0
        sort_map = {
            "created": "timestamp DESC",
            "freq": "access_count DESC",
            "recent": "last_access DESC",
        }
        order = sort_map.get(sort_by, "timestamp DESC")
        clauses = []
        params = ()
        if search is not None:
            if exact:
                clauses.append("text = ?")
            else:
                clauses.append("text LIKE ?")
                search = f"%{search}%"
            params += (search,)
        if since is not None:
            clauses.append("timestamp >= ?")
            params += (since,)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        try:
            total = self._conn.execute(
                f"SELECT COUNT(*) FROM entries{where}", params
            ).fetchone()[0]
            offset = (page - 1) * page_size
            rows = self._conn.execute(
                "SELECT id, text, source_language, target_language, translator,"
                " timestamp, last_access, access_count"
                f" FROM entries{where} ORDER BY {order} LIMIT ? OFFSET ?",
                params + (page_size, offset),
            ).fetchall()
            return [WordBookEntry(*r) for r in rows], total
        except Exception:
            return [], 0

    def count(self):
        """Return the total number of entries in the wordbook.

        Returns:
            Entry count, or 0 if the database is unavailable.
        """
        if not self._conn:
            return 0
        try:
            return self._conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        except Exception:
            return 0

    # ── config ─────────────────────────────────────────────────

    def get_config(self):
        """Return a summary dict with the current entry count and default
        recording preference.

        Returns:
            A dict with keys ``"count"`` and ``"default_record"``.
        """
        count = self.count()
        return {"count": count, "default_record": self.get_default_record()}

    def get_default_record(self):
        """Return whether the ``--record`` flag is enabled by default.

        Returns:
            True if default recording is on, False otherwise (also returned
            when the database is unavailable or the config row is missing).
        """
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
        """Persist the default recording preference.

        Args:
            on: True to enable default recording, False to disable.
        """
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
        """Close the connection and remove the database file from disk."""
        self.close()
        try:
            os.remove(self._path)
        except OSError:
            pass

    def close(self):
        """Close the database connection if it is open."""
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None
