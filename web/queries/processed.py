# web.queries.processed.py
from db.database import db


def get_processed_ids():
    """Get all processed post IDs ordered oldest to newest."""
    rows = db.cur.execute("""
        SELECT id, processed
        FROM posts
        WHERE processed = 1
        ORDER BY id DESC
    """).fetchall()
    return [(row["id"], row["processed"]) for row in rows]


def get_first_processed_id():
    """Get the oldest processed post ID."""
    row = db.cur.execute("""
        SELECT id
        FROM posts
        WHERE processed = 1
        ORDER BY id DESC
        LIMIT 1 
    """).fetchone()
    return row[0] if row else None


def get_post_by_id(row_id: int):
    row = db.cur.execute(
        """
        SELECT id, post_id, author, text, post_url, processed, group_name, scraped_at, selected,
               result_json_v1, gate1_reasoning, gate1_prompt_version,
               extraction_result_json, extraction_reasoning, extraction_prompt_version
        FROM posts
        WHERE id = ?
        AND processed = 1
        """,
        (row_id,),
    ).fetchone()
    return dict(row) if row else None


def get_author_of_post(row_id: int):
    """Get author name for a given post ID (processed or not)."""
    row = db.cur.execute("SELECT author FROM posts WHERE id = ?", (row_id,)).fetchone()
    return row["author"] if row else None


def get_posts_by_author_processed(author: str):
    rows = db.cur.execute(
        """
        SELECT id, post_id, author, text, post_url, processed, group_name, selected,
               result_json_v1, gate1_reasoning, gate1_prompt_version,
               extraction_result_json, extraction_reasoning, extraction_prompt_version
        FROM posts
        WHERE author = ?
        AND processed = 1
        ORDER BY id
        """,
        (author,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_first_processed_id_for_author(author: str):
    """Get the oldest processed post ID for a specific author."""
    row = db.cur.execute(
        """
        SELECT id
        FROM posts
        WHERE author = ?
        AND processed = 1
        ORDER BY id
        LIMIT 1
        """,
        (author,),
    ).fetchone()
    return row[0] if row else None


def count_processed_by_author(author: str) -> int:
    """Count processed posts for a specific author."""
    row = db.cur.execute(
        "SELECT COUNT(*) FROM posts WHERE author = ? AND processed = 1",
        (author,),
    ).fetchone()
    return row[0]
