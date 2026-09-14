# db/database.py

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_FILE = "/media/aasava/07A42CF9224B4FB1/FB_scrape/posts.db"


class LocalDatabase:
    """
    Local SQLite database used by the scraping / processing pipeline.

    This module is responsible only for:
    - database connection
    - local database configuration
    - schema initialization

    Processing operations belong elsewhere.
    """

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        self._setup_schema()

    @property
    def cur(self) -> sqlite3.Cursor:
        """Compatibility/convenience access to the current connection cursor."""
        return self.conn.cursor()

    def _setup_schema(self) -> None:
        """
        Create the complete current local database schema.

        There is intentionally no migration / ensure-columns logic here.
        This database is established and its current schema is authoritative.
        """

        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT UNIQUE,
                author TEXT,
                timestamp TEXT,
                text TEXT,
                post_url TEXT,
                scraped_at TEXT,
                group_name TEXT,
                selected INTEGER DEFAULT 0,

                processed INTEGER DEFAULT 0,
                ai_processed INTEGER DEFAULT 0,
                review_building INTEGER DEFAULT 0,

                result_json_v1 TEXT,
                gate1_reasoning TEXT,
                gate1_prompt_version TEXT,

                extraction_result_json TEXT,
                extraction_reasoning TEXT,
                extraction_prompt_version TEXT
            );

            CREATE TABLE IF NOT EXISTS blacklist (
                author TEXT PRIMARY KEY,
                count INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS filter_phrases (
                phrase TEXT PRIMARY KEY,
                added_at TEXT
            );

            CREATE TABLE IF NOT EXISTS entry_review_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL UNIQUE,
                candidate_property_id INTEGER,
                reviewed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_dedup
                ON posts(author, text);

            CREATE INDEX IF NOT EXISTS idx_blacklist
                ON blacklist(author);

            CREATE INDEX IF NOT EXISTS idx_group
                ON posts(group_name);

            CREATE INDEX IF NOT EXISTS idx_entry_review_pending
                ON entry_review_queue(reviewed);
            """)

        self.conn.commit()

    def close(self) -> None:
        """Close the local database connection."""
        self.conn.close()


db = LocalDatabase(DB_FILE)
print("Opening:", db.db_path.absolute())
