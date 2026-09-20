# # web.queries.review.py
# from db.database import db


# def get_pending_review_ids():
#     rows = db.cur.execute("""
#         SELECT id
#         FROM entry_review_queue
#         WHERE reviewed = 0
#         ORDER BY id ASC
#     """).fetchall()
#     return [row["id"] for row in rows]


# def get_first_pending_id():
#     row = db.cur.execute("""
#         SELECT id
#         FROM entry_review_queue
#         WHERE reviewed = 0
#         ORDER BY id ASC
#         LIMIT 1
#     """).fetchone()
#     return row["id"] if row else None


# def get_review_row(review_id: int):
#     row = db.cur.execute(
#         """
#         SELECT rq.id AS review_id,
#                rq.post_id,
#                rq.candidate_property_id,
#                rq.reviewed,
#                rq.created_at,
#                p.author,
#                p.post_id AS fb_post_id,
#                p.post_url,
#                p.text,
#                p.scraped_at,
#                p.extraction_result_json
#         FROM entry_review_queue rq
#         JOIN posts p ON p.id = rq.post_id
#         WHERE rq.id = ?
#         """,
#         (review_id,),
#     ).fetchone()
#     return dict(row) if row else None


# def mark_reviewed(review_id: int):
#     db.cur.execute(
#         "UPDATE entry_review_queue SET reviewed = 1 WHERE id = ?", (review_id,)
#     )
#     db.conn.commit()
#     return db.cur.rowcount
