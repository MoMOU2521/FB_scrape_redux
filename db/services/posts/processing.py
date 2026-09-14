# db.services.posts.processing.py
from __future__ import annotations

from datetime import datetime, timezone, timedelta

from db.database import db


def cleanup_old_posts(days: int = 45) -> int:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    cursor = db.conn.execute(
        """
        DELETE FROM posts
        WHERE scraped_at IS NOT NULL
          AND scraped_at < ?
        """,
        (cutoff,),
    )

    db.conn.commit()
    return cursor.rowcount


def get_next_unprocessed_ai():
    row = db.conn.execute("""
        SELECT id, author, group_name, timestamp, post_url, text
        FROM posts
        WHERE ai_processed = 0 OR ai_processed IS NULL
        ORDER BY id
        LIMIT 1
        """).fetchone()

    return dict(row) if row else None


def mark_ai_processed(row_id: int) -> None:
    db.conn.execute(
        "UPDATE posts SET ai_processed = 1 WHERE id = ?",
        (row_id,),
    )
    db.conn.commit()


def mark_processed(row_id: int) -> None:
    db.conn.execute(
        "UPDATE posts SET processed = 1 WHERE id = ?",
        (row_id,),
    )
    db.conn.commit()


def mark_review_building(row_id: int) -> None:
    db.conn.execute(
        """
        UPDATE posts
        SET review_building = 1,
            processed = 1
        WHERE id = ?
        """,
        (row_id,),
    )
    db.conn.commit()


def get_next_unprocessed_for_extraction():
    row = db.conn.execute("""
        SELECT id, author, group_name, timestamp, post_url, text
        FROM posts
        WHERE (ai_processed IS NOT NULL)
          AND (extraction_result_json IS NULL OR extraction_result_json = '')
          AND processed = 0
        ORDER BY id
        LIMIT 1
        """).fetchone()

    return dict(row) if row else None
