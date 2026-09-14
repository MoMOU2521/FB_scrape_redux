# web.queries.posts.py
from db.database import db


def is_duplicate(author: str, text_preview: str) -> bool:
    row = db.cur.execute(
        "SELECT 1 FROM posts WHERE author = ? AND SUBSTR(text, 1, 1000) = ? LIMIT 1",
        (author, text_preview[:1000]),
    ).fetchone()
    return row is not None


def insert_post(post_id, author, timestamp, text, post_url, group_name, scraped_at):
    import sqlite3

    try:
        db.cur.execute(
            """INSERT INTO posts (post_id, author, timestamp, text, post_url, scraped_at, group_name, selected)
               VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
            (post_id, author, timestamp, text, post_url, scraped_at, group_name),
        )
        db.conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def toggle_selected(post_id: int, value: int):
    db.cur.execute("UPDATE posts SET selected = ? WHERE id = ?", (value, post_id))
    db.conn.commit()
    return db.cur.rowcount


def get_post_by_id(row_id: int):
    row = db.cur.execute(
        """
        SELECT id, post_id, author, text, post_url, processed, group_name, scraped_at, selected,
               result_json_v1, gate1_reasoning, gate1_prompt_version,
               extraction_result_json, extraction_reasoning, extraction_prompt_version
        FROM posts
        WHERE id = ?
        AND (processed = 0 OR processed IS NULL)
        """,
        (row_id,),
    ).fetchone()
    return dict(row) if row else None


def get_post_for_lookup(row_id: int):
    """
    Retrieve a post directly by its SQLite auto-increment row ID.

    Unlike get_post_by_id(), this lookup intentionally has no processed
    status restriction. It returns the exact posts row regardless of
    whether the post is processed, unprocessed, selected, or in review.
    """
    row = db.cur.execute(
        """
        SELECT
            id,
            post_id,
            author,
            text,
            post_url,
            processed,
            group_name,
            scraped_at,
            selected,
            ai_processed,
            review_building,
            result_json_v1,
            gate1_reasoning,
            gate1_prompt_version,
            extraction_result_json,
            extraction_reasoning,
            extraction_prompt_version
        FROM posts
        WHERE id = ?
        """,
        (row_id,),
    ).fetchone()

    return dict(row) if row else None


def count_unprocessed_by_author(author: str) -> int:
    row = db.cur.execute(
        "SELECT COUNT(*) FROM posts WHERE author = ? AND (processed = 0 OR processed IS NULL)",
        (author,),
    ).fetchone()
    return row[0]


def get_unprocessed_ids():
    rows = db.cur.execute("""
        SELECT id, processed
        FROM posts
        WHERE processed = 0 OR processed IS NULL
        ORDER BY id ASC
    """).fetchall()
    return [(row["id"], row["processed"]) for row in rows]


def get_first_unprocessed_id():
    row = db.cur.execute("""
        SELECT id
        FROM posts
        WHERE processed = 0 OR processed IS NULL
        ORDER BY id ASC 
        LIMIT 1
    """).fetchone()
    return row[0] if row else None


def get_author_of_post(row_id: int):
    row = db.cur.execute("SELECT author FROM posts WHERE id = ?", (row_id,)).fetchone()
    return row["author"] if row else None


def get_posts_by_author_unprocessed(author: str):
    rows = db.cur.execute(
        """
        SELECT id, post_id, author, text, post_url, processed, group_name, selected,
               result_json_v1, gate1_reasoning, gate1_prompt_version,
               extraction_result_json, extraction_reasoning, extraction_prompt_version
        FROM posts
        WHERE author = ?
        AND (processed = 0 OR processed IS NULL)
        ORDER BY id
        """,
        (author,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_first_unprocessed_id_for_author(author: str):
    row = db.cur.execute(
        "SELECT id FROM posts WHERE author = ? AND (processed = 0 OR processed IS NULL) ORDER BY id LIMIT 1",
        (author,),
    ).fetchone()
    return row[0] if row else None


def update_processed(row_id: int, processed: int):
    db.cur.execute("UPDATE posts SET processed = ? WHERE id = ?", (processed, row_id))
    db.conn.commit()
    return db.cur.rowcount
