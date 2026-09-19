# server/services/review.py
import asyncio
import json

import server.queries.review as queries
import db.db_entry as db_entry


def _nav_context(review_id, all_ids):
    idx = next((i for i, rid in enumerate(all_ids) if rid == review_id), None)
    if idx is None:
        return None
    total = len(all_ids)
    return {
        "current": idx + 1,
        "total": total,
        "prev_id": all_ids[idx - 1] if idx > 0 else None,
        "next_id": all_ids[idx + 1] if idx < total - 1 else None,
    }


def get_review_with_nav(review_id):
    row = queries.get_review_row(review_id)
    if not row:
        return None
    all_ids = queries.get_pending_review_ids()
    return {"row": row, "nav": _nav_context(review_id, all_ids)}


def approve(review_id: int):
    row = queries.get_review_row(review_id)
    if not row:
        raise LookupError(f"review row {review_id} not found")

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
    queries.mark_reviewed(review_id)
    return property_id


def reject(review_id: int):
    if not queries.get_review_row(review_id):
        raise LookupError(f"review row {review_id} not found")
    queries.mark_reviewed(review_id)
    return True


def dismiss(review_id: int):
    if not queries.get_review_row(review_id):
        raise LookupError(f"review row {review_id} not found")
    queries.mark_reviewed(review_id)
    return True
