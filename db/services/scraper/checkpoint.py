# db.services.scraper.checkpoint.py
from db.database import db


def save_checkpoint(group_name: str, post_id: str, scraped_at: str) -> None:
    db.cur.execute(
        """INSERT INTO scrape_checkpoint (group_name, top_post_id, updated_at)
           VALUES (?, ?, ?)
           ON CONFLICT(group_name) DO UPDATE SET
               top_post_id = excluded.top_post_id,
               updated_at = excluded.updated_at""",
        (group_name, post_id, scraped_at),
    )
    db.conn.commit()


def get_checkpoint(group_name: str):
    row = db.cur.execute(
        "SELECT group_name, top_post_id FROM scrape_checkpoint WHERE group_name = ?",
        (group_name,),
    ).fetchone()
    return dict(row) if row else None
