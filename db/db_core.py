# # db/db_core.py
# import sqlite3
# import traceback
# from datetime import datetime, timezone, timedelta


# def _debug_trace(sql):
#     if "processed" in sql.lower():
#         print("\n=== SQL ===", sql)
#         traceback.print_stack()


# def normalize_author(author):
#     """Normalize all apostrophe variations to standard ASCII apostrophe."""
#     if not author:
#         return author
#     return (
#         author.replace("’", "'").replace("ʼ", "'").replace("‘", "'").replace("‛", "'")
#     )


# class Core:
#     """Owns the sqlite connection, schema, and migrations. Nothing else."""

#     def __init__(self, db_path: str | None = None, cleanup_days: int = 45):
#         if db_path is None:
#             db_path = "posts.db"
#         self.conn = sqlite3.connect(db_path)
#         # self.conn.set_trace_callback(_debug_trace)
#         self.conn.row_factory = sqlite3.Row
#         self.cur = self.conn.cursor()
#         self._setup_schema()
#         self._ensure_columns()
#         self.cleanup_old_posts(days=cleanup_days)

#     def _setup_schema(self):
#         self.cur.execute("""
#             CREATE TABLE IF NOT EXISTS posts (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 post_id TEXT UNIQUE,
#                 author TEXT,
#                 timestamp TEXT,
#                 text TEXT,
#                 post_url TEXT,
#                 scraped_at TEXT,
#                 group_name TEXT,
#                 selected INTEGER DEFAULT 0
#             )
#         """)
#         self.cur.execute("""
#             CREATE TABLE IF NOT EXISTS blacklist (
#                 author TEXT PRIMARY KEY,
#                 count INTEGER DEFAULT 0
#             )
#         """)
#         self.cur.execute("""
#             CREATE TABLE IF NOT EXISTS filter_phrases (
#                 phrase TEXT PRIMARY KEY,
#                 added_at TEXT
#             )
#         """)
#         self.cur.execute("CREATE INDEX IF NOT EXISTS idx_dedup ON posts(author, text)")
#         self.cur.execute(
#             "CREATE INDEX IF NOT EXISTS idx_blacklist ON blacklist(author)"
#         )
#         self.conn.commit()

#         self.cur.execute("""
#             CREATE TABLE IF NOT EXISTS entry_review_queue (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 post_id INTEGER NOT NULL UNIQUE,
#                 candidate_property_id INTEGER,
#                 reviewed INTEGER NOT NULL DEFAULT 0,
#                 created_at TEXT NOT NULL
#             )
#         """)
#         self.cur.execute("""
#             CREATE INDEX IF NOT EXISTS idx_entry_review_pending
#             ON entry_review_queue(reviewed)
#         """)

#     def _ensure_columns(self):
#         cols = [r[1] for r in self.cur.execute("PRAGMA table_info(posts)").fetchall()]
#         if "scraped_at" not in cols:
#             self.conn.execute("ALTER TABLE posts ADD COLUMN scraped_at TEXT")
#         if "group_name" not in cols:
#             self.conn.execute("ALTER TABLE posts ADD COLUMN group_name TEXT")
#         if "selected" not in cols:
#             self.conn.execute("ALTER TABLE posts ADD COLUMN selected INTEGER DEFAULT 0")
#         if "processed" not in cols:
#             self.conn.execute(
#                 "ALTER TABLE posts ADD COLUMN processed INTEGER DEFAULT 0"
#             )
#         if "ai_processed" not in cols:
#             self.conn.execute(
#                 "ALTER TABLE posts ADD COLUMN ai_processed INTEGER DEFAULT 0"
#             )
#         if "review_building" not in cols:
#             self.conn.execute(
#                 "ALTER TABLE posts ADD COLUMN review_building INTEGER DEFAULT 0"
#             )
#         if "result_json_v1" not in cols:
#             self.conn.execute("ALTER TABLE posts ADD COLUMN result_json_v1 TEXT")
#         if "gate1_reasoning" not in cols:
#             self.conn.execute("ALTER TABLE posts ADD COLUMN gate1_reasoning TEXT")
#         if "gate1_prompt_version" not in cols:
#             self.conn.execute("ALTER TABLE posts ADD COLUMN gate1_prompt_version TEXT")
#         if "extraction_result_json" not in cols:
#             self.conn.execute(
#                 "ALTER TABLE posts ADD COLUMN extraction_result_json TEXT"
#             )
#         if "extraction_reasoning" not in cols:
#             self.conn.execute("ALTER TABLE posts ADD COLUMN extraction_reasoning TEXT")
#         if "extraction_prompt_version" not in cols:
#             self.conn.execute(
#                 "ALTER TABLE posts ADD COLUMN extraction_prompt_version TEXT"
#             )
#         self.cur.execute("CREATE INDEX IF NOT EXISTS idx_group ON posts(group_name)")
#         self.conn.commit()

#     def cleanup_old_posts(self, days: int = 45) -> int:
#         cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
#         self.cur.execute(
#             "DELETE FROM posts WHERE scraped_at IS NOT NULL AND scraped_at < ?",
#             (cutoff,),
#         )
#         deleted = self.cur.rowcount
#         self.conn.commit()
#         return deleted

#     def get_next_unprocessed_ai(self):
#         row = self.cur.execute("""
#             SELECT id, author, group_name, timestamp, post_url, text
#             FROM posts
#             WHERE ai_processed = 0 OR ai_processed IS NULL
#             ORDER BY id LIMIT 1
#         """).fetchone()
#         return dict(row) if row else None

#     def mark_ai_processed(self, row_id: int):
#         self.cur.execute("UPDATE posts SET ai_processed = 1 WHERE id = ?", (row_id,))
#         self.conn.commit()

#     def mark_processed(self, row_id: int):
#         self.cur.execute("UPDATE posts SET processed = 1 WHERE id = ?", (row_id,))
#         self.conn.commit()

#     # CLAUDE: SHAKY ADD
#     def mark_review_building(self, row_id: int):
#         self.cur.execute(
#             "UPDATE posts SET review_building = 1, processed = 1 WHERE id = ?",
#             (row_id,),
#         )
#         self.conn.commit()

#     def save_gate1_result(
#         self, row_id: int, result_json: str, reasoning: str, prompt_version: str
#     ):
#         self.cur.execute(
#             """
#             UPDATE posts
#             SET result_json_v1 = ?, gate1_reasoning = ?, gate1_prompt_version = ?
#             WHERE id = ?
#         """,
#             (result_json, reasoning, prompt_version, row_id),
#         )
#         self.conn.commit()

#     def get_next_unprocessed_for_extraction(self):
#         row = self.cur.execute("""
#             SELECT id, author, group_name, timestamp, post_url, text
#             FROM posts
#             WHERE (ai_processed = 1 OR ai_processed IS NOT NULL)
#             AND (extraction_result_json IS NULL OR extraction_result_json = '')
#             AND processed = 0
#             ORDER BY id LIMIT 1
#         """).fetchone()
#         return dict(row) if row else None

#     def save_extraction_result(
#         self, row_id: int, result_json: str, reasoning: str, prompt_version: str
#     ):
#         self.cur.execute(
#             """
#             UPDATE posts
#             SET extraction_result_json = ?, extraction_reasoning = ?, extraction_prompt_version = ?
#             WHERE id = ?
#         """,
#             (result_json, reasoning, prompt_version, row_id),
#         )
#         self.conn.commit()

#     def close(self):
#         self.conn.close()


# # Single shared connection for the whole app.
# core = Core()
