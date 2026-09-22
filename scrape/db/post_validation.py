# # db.services.scraper.post_validation.py
# from db.database import db


# def increment_blacklist_count(author: str) -> None:
#     db.cur.execute("UPDATE blacklist SET count = count + 1 WHERE author = ?", (author,))
#     db.conn.commit()


# def is_author_blacklisted(author: str) -> bool:
#     return (
#         db.cur.execute("SELECT 1 FROM blacklist WHERE author = ?", (author,)).fetchone()
#         is not None
#     )


# def matches_filter_phrase(text: str):
#     return db.cur.execute(
#         "SELECT phrase FROM filter_phrases WHERE ? LIKE '%' || phrase || '%'", (text,)
#     ).fetchone()
