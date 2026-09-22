# db.services.scraper.save_post.py
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


def save_post(
    post_id: str,
    author: str,
    timestamp: str,
    text: str,
    url: str,
    group_name: str,
    scraped_at: str,
) -> bool:
    if is_duplicate(author, text):
        return False
    return insert_post(post_id, author, timestamp, text, url, group_name, scraped_at)


def save_stub_post(post_id: str, group_name: str, scraped_at: str) -> bool:
    """Records post_id + scraped_at only, for posts that failed a check.
    Marked processed/ai_processed so it never enters the AI pipeline or UI queues."""
    import sqlite3

    try:
        db.cur.execute(
            """INSERT INTO posts (post_id, group_name, scraped_at, selected, processed, ai_processed)
               VALUES (?, ?, ?, 0, 1, 1)""",
            (post_id, group_name, scraped_at),
        )
        db.conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
