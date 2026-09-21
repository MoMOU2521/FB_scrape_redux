# server.queries.blacklist.py
from db.database import db
from db.helpers import normalize_author


def is_blacklisted(author: str) -> bool:
    author = normalize_author(author)
    row = db.cur.execute(
        "SELECT count FROM blacklist WHERE author = ?", (author,)
    ).fetchone()
    return row is not None


def increment_blacklist(author: str):
    author = normalize_author(author)
    db.cur.execute(
        "INSERT INTO blacklist (author, count) VALUES (?, 1) "
        "ON CONFLICT(author) DO UPDATE SET count = count + 1",
        (author,),
    )
    db.conn.commit()


def add_blacklist(author: str):
    author = normalize_author(author)

    cur = db.cur
    cur.execute(
        "INSERT OR IGNORE INTO blacklist (author, count) VALUES (?, 0)",
        (author,),
    )
    inserted = cur.rowcount > 0

    cur2 = db.cur
    cur2.execute(
        "UPDATE posts SET processed = 1 WHERE author = ? AND (processed = 0 OR processed IS NULL)",
        (author,),
    )
    updated = cur2.rowcount

    db.conn.commit()
    return inserted, updated


# def get_blacklist_counts(authors):
#     authors = [normalize_author(a) for a in authors]
#     placeholders = ",".join("?" * len(authors))
#     rows = db.cur.execute(
#         f"SELECT author, count FROM blacklist WHERE author IN ({placeholders})",
#         tuple(authors),
#     ).fetchall()
#     return {author: count for author, count in rows}


def get_blacklist_rows(sort="count"):
    if sort == "alpha":
        query = "SELECT author, count FROM blacklist ORDER BY author"
    else:
        query = "SELECT author, count FROM blacklist ORDER BY count DESC, author"
    return db.cur.execute(query).fetchall()


def delete_blacklist(author: str):
    db.cur.execute("DELETE FROM blacklist WHERE author = ?", (author,))
    db.conn.commit()
