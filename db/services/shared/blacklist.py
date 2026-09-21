# db.services.shared.blacklist.py
from db.database import db
from db.helpers import normalize_author


def get_blacklist_counts(authors):
    authors = [normalize_author(a) for a in authors]
    placeholders = ",".join("?" * len(authors))
    rows = db.cur.execute(
        f"SELECT author, count FROM blacklist WHERE author IN ({placeholders})",
        tuple(authors),
    ).fetchall()
    return {author: count for author, count in rows}
