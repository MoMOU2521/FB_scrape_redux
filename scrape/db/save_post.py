# # db.services.scraper.save_post.py
# from db.database import db


# def is_duplicate(author: str, text_preview: str) -> bool:
#     row = db.cur.execute(
#         "SELECT 1 FROM posts WHERE author = ? AND SUBSTR(text, 1, 1000) = ? LIMIT 1",
#         (author, text_preview[:1000]),
#     ).fetchone()
#     return row is not None


# def insert_post(post_id, author, timestamp, text, post_url, group_name, scraped_at):
#     import sqlite3

#     try:
#         db.cur.execute(
#             """INSERT INTO posts (post_id, author, timestamp, text, post_url, scraped_at, group_name, selected)
#                VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
#             (post_id, author, timestamp, text, post_url, scraped_at, group_name),
#         )
#         db.conn.commit()
#         return True
#     except sqlite3.IntegrityError:
#         return False


# def save_post(
#     post_id: str,
#     author: str,
#     timestamp: str,
#     text: str,
#     url: str,
#     group_name: str,
#     scraped_at: str,
# ) -> bool:
#     if is_duplicate(author, text):
#         return False
#     return insert_post(post_id, author, timestamp, text, url, group_name, scraped_at)
