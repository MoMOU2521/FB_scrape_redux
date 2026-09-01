# scrape.db_ops.py
from db.db_core import Core
import web.posts as posts

core = Core()


def is_author_blacklisted(author: str) -> bool:
    return (
        core.cur.execute(
            "SELECT 1 FROM blacklist WHERE author = ?", (author,)
        ).fetchone()
        is not None
    )


def increment_blacklist_count(author: str) -> None:
    core.cur.execute(
        "UPDATE blacklist SET count = count + 1 WHERE author = ?", (author,)
    )
    core.conn.commit()


def matches_filter_phrase(text: str):
    return core.cur.execute(
        "SELECT phrase FROM filter_phrases WHERE ? LIKE '%' || phrase || '%'", (text,)
    ).fetchone()


def save_post(
    post_id: str,
    author: str,
    timestamp: str,
    text: str,
    url: str,
    group_name: str,
    scraped_at: str,
) -> bool:
    if posts.is_duplicate(author, text):
        return False
    return posts.insert_post(
        post_id, author, timestamp, text, url, group_name, scraped_at
    )


def get_last_scraped_post(group_name: str):
    row = core.cur.execute(
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
