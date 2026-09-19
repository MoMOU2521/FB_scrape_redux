# db.services.scraper.get_last_scraped_post.py
from db.database import db


def get_last_scraped_post(group_name: str):
    row = db.cur.execute(
        """
        SELECT group_name, post_id
        FROM posts
        WHERE group_name = ?
        ORDER BY scraped_at DESC
        LIMIT 1
        """,
        (group_name,),
    ).fetchone()

    return dict(row) if row else None
