# server.queries.stats.py
from db.database import db


def get_group_stats():
    rows = db.cur.execute("""
        SELECT
            group_name,
            COUNT(*) as total,
            SUM(selected) as selected
        FROM posts
        WHERE group_name IS NOT NULL
        GROUP BY group_name
        ORDER BY group_name
    """).fetchall()
    return rows


def get_authors_by_unprocessed_count(min_count=2):
    return db.cur.execute(
        """
        SELECT
            author,
            COUNT(*) as unprocessed_count,
            MIN(id) as first_unprocessed_id
        FROM posts
        WHERE (processed = 0 OR processed IS NULL)
        GROUP BY author
        HAVING COUNT(*) > ?
        ORDER BY unprocessed_count DESC
        """,
        (min_count,),
    ).fetchall()


def get_next_unprocessed_ai():
    row = db.cur.execute("""
        SELECT id, author, group_name, timestamp, post_url, text
        FROM posts
        WHERE ai_processed = 0 OR ai_processed IS NULL
        ORDER BY id LIMIT 1
        """).fetchone()
    return dict(row) if row else None


def mark_ai_processed(row_id: int):
    db.cur.execute("UPDATE posts SET ai_processed = 1 WHERE id = ?", (row_id,))
    db.conn.commit()
