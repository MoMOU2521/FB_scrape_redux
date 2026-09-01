# ai.schema.py
def ensure_schema(conn):
    """Idempotent guard: adds any columns the 'posts' table is missing."""
    cols = [r[1] for r in conn.execute("PRAGMA table_info(posts)").fetchall()]

    if "gate1_reasoning" not in cols:
        conn.execute("ALTER TABLE posts ADD COLUMN gate1_reasoning TEXT")
    if "gate1_prompt_version" not in cols:
        conn.execute("ALTER TABLE posts ADD COLUMN gate1_prompt_version TEXT")
    if "extraction_result_json" not in cols:
        conn.execute("ALTER TABLE posts ADD COLUMN extraction_result_json TEXT")
    if "extraction_reasoning" not in cols:
        conn.execute("ALTER TABLE posts ADD COLUMN extraction_reasoning TEXT")
    if "extraction_prompt_version" not in cols:
        conn.execute("ALTER TABLE posts ADD COLUMN extraction_prompt_version TEXT")

    conn.commit()
