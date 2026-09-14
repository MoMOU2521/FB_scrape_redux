# web/review.py
import asyncio

from db.database import db
from web.templates import REVIEW_TEMPLATE
import db.db_entry as db_entry

# ============================================================================
# QUERIES
# ============================================================================


def get_pending_review_ids():
    rows = db.cur.execute("""
        SELECT id
        FROM entry_review_queue
        WHERE reviewed = 0
        ORDER BY id ASC
    """).fetchall()
    return [row["id"] for row in rows]


def get_first_pending_id():
    row = db.cur.execute("""
        SELECT id
        FROM entry_review_queue
        WHERE reviewed = 0
        ORDER BY id ASC
        LIMIT 1
    """).fetchone()
    return row["id"] if row else None


def get_review_row(review_id: int):
    row = db.cur.execute(
        """
        SELECT rq.id AS review_id,
               rq.post_id,
               rq.candidate_property_id,
               rq.reviewed,
               rq.created_at,
               p.author,
               p.post_id AS fb_post_id,
               p.post_url,
               p.text,
               p.scraped_at,
               p.extraction_result_json
        FROM entry_review_queue rq
        JOIN posts p ON p.id = rq.post_id
        WHERE rq.id = ?
        """,
        (review_id,),
    ).fetchone()
    return dict(row) if row else None


def mark_reviewed(review_id: int):
    db.cur.execute(
        "UPDATE entry_review_queue SET reviewed = 1 WHERE id = ?", (review_id,)
    )
    db.conn.commit()
    return db.cur.rowcount


# ============================================================================
# ACTIONS
# ============================================================================


def approve(review_id: int):
    """Force-insert the post's extraction result, bypassing duplicate check."""
    import json

    row = get_review_row(review_id)
    if not row:
        raise ValueError(f"review row {review_id} not found")

    post_json = json.loads(row["extraction_result_json"])

    async def _do():
        async with db_entry.get_session() as db:
            owner_id = await db_entry.resolve_or_create_owner(
                db, post_json, row["author"]
            )
            building_id = await db_entry.resolve_building_id(db, post_json)

            property_id = await db_entry.create_property_registry(
                db, owner_id, post_json
            )
            await db_entry.create_unit_detail(db, property_id, building_id, post_json)
            await db_entry.create_features(db, property_id, post_json)
            await db_entry.create_rent_term(
                db, property_id, post_json, row["scraped_at"]
            )
            await db_entry.create_sale_term(db, property_id, post_json)
            await db_entry.create_property_note(
                db, property_id, row["post_url"], row["text"]
            )

            await db.commit()
            return property_id

    property_id = asyncio.run(_do())
    mark_reviewed(review_id)
    return property_id


def reject(review_id: int):
    """Discard — do not insert, just mark reviewed."""
    row = get_review_row(review_id)
    if not row:
        raise ValueError(f"review row {review_id} not found")
    mark_reviewed(review_id)
    return True


def dismiss(review_id: int):
    """Leave post as-is, just clear from the queue."""
    row = get_review_row(review_id)
    if not row:
        raise ValueError(f"review row {review_id} not found")
    mark_reviewed(review_id)
    return True


# ============================================================================
# PAGE ASSEMBLY
# ============================================================================


def build_page(review_id: int, all_ids: list):
    row = get_review_row(review_id)
    if not row:
        return None

    current_idx = next((i for i, rid in enumerate(all_ids) if rid == review_id), None)
    if current_idx is None:
        return None

    total = len(all_ids)
    prev_id = all_ids[current_idx - 1] if current_idx > 0 else None
    next_id = all_ids[current_idx + 1] if current_idx < total - 1 else None

    prev_button = (
        f'<a href="/review/{prev_id}"><button>← Previous</button></a>'
        if prev_id
        else "<button disabled>← Previous</button>"
    )
    next_button = (
        f'<a href="/review/{next_id}"><button>Next →</button></a>'
        if next_id
        else "<button disabled>Next →</button>"
    )

    candidate_html = (
        f'Candidate duplicate property ID: <strong>{row["candidate_property_id"]}</strong>'
        if row["candidate_property_id"] is not None
        else "No candidate property recorded."
    )

    return REVIEW_TEMPLATE % {
        "current": current_idx + 1,
        "total": total,
        "prev_button": prev_button,
        "next_button": next_button,
        "author": row["author"] or "",
        "post_url": row["post_url"] or "",
        "scraped_at": row["scraped_at"] or "",
        "candidate_html": candidate_html,
        "text": row["text"] or "",
        "extraction_result_json": row["extraction_result_json"] or "",
        "review_id": row["review_id"],
    }
