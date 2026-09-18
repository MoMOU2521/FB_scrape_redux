# server.queries.review_building.py
from db.database import db


def get_pending_building_ids():
    rows = db.cur.execute("""
        SELECT id FROM posts
        WHERE review_building = 1 AND processed = 1
        ORDER BY id ASC
    """).fetchall()
    return [row["id"] for row in rows]


def get_first_pending_building_id():
    row = db.cur.execute("""
        SELECT id FROM posts
        WHERE review_building = 1 AND processed = 1
        ORDER BY id ASC LIMIT 1
    """).fetchone()
    return row["id"] if row else None


def get_building_review_post(post_id: int):
    row = db.cur.execute(
        """
        SELECT id, post_id, author, text, post_url, processed, group_name, scraped_at, selected,
               result_json_v1, gate1_reasoning, gate1_prompt_version,
               extraction_result_json, extraction_reasoning, extraction_prompt_version,
               review_building
        FROM posts
        WHERE id = ? AND review_building = 1 AND processed = 1
    """,
        (post_id,),
    ).fetchone()
    return dict(row) if row else None
