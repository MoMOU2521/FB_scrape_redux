# web.queries.filters.py
from datetime import datetime, timezone

from db.database import db


def is_phrase_filtered(text: str):
    cur = db.cur
    cur.execute("SELECT phrase FROM filter_phrases")
    for (phrase,) in cur.fetchall():
        if phrase in text:
            return phrase
    return None


def add_filter_phrase(phrase: str):
    db.cur.execute(
        "INSERT OR IGNORE INTO filter_phrases (phrase, added_at) VALUES (?, ?)",
        (phrase, datetime.now(timezone.utc).isoformat()),
    )
    db.conn.commit()


def filter_phrase_exists(phrase: str) -> bool:
    row = db.cur.execute(
        "SELECT 1 FROM filter_phrases WHERE phrase = ?", (phrase,)
    ).fetchone()
    return row is not None


def delete_filter_phrase(phrase: str):
    db.cur.execute("DELETE FROM filter_phrases WHERE phrase = ?", (phrase,))
    db.conn.commit()


def get_filter_rows():
    return db.cur.execute(
        "SELECT phrase, added_at FROM filter_phrases ORDER BY added_at DESC"
    ).fetchall()
