# server/services/review_building.py
import asyncio
import json

import server.queries.review_building as queries
import server.building_alias as building_alias
import server.queries.review as review_queries
from db.database import db
from db.db_supabase import get_session
import db.db_entry as db_entry
from db.services.posts.actions import toggle_selected
from db.services.db_entry.resolve_or_create_owner import resolve_or_create_owner
from db.services.db_entry.enter_post_with_known_building import (
    enter_post_with_known_building,
)


def _nav_context(post_id, all_ids):
    idx = next((i for i, rid in enumerate(all_ids) if rid == post_id), None)
    if idx is None:
        return None
    total = len(all_ids)
    return {
        "current": idx + 1,
        "total": total,
        "prev_id": all_ids[idx - 1] if idx > 0 else None,
        "next_id": all_ids[idx + 1] if idx < total - 1 else None,
    }


def get_review_building_with_nav(post_id):
    post = queries.get_building_review_post(post_id)
    if not post:
        return None
    all_ids = queries.get_pending_building_ids()
    return {"post": post, "nav": _nav_context(post_id, all_ids)}


async def _enter(row_id):
    p = queries.get_building_review_post(row_id)
    if not p:
        raise LookupError(f"post {row_id} not in building review queue")

    post_json = json.loads(p["extraction_result_json"])
    decision, candidate_property_id = await db_entry.enter_post(
        post_json, p["author"], p["post_url"], p["text"], p["scraped_at"]
    )

    db.conn.execute(
        "UPDATE posts SET processed = 1, review_building = 0 WHERE id = ?",
        (row_id,),
    )
    db.conn.commit()

    if decision == "discard":
        return {"discarded": True}

    if decision == "review":
        review_queries.queue_review(row_id, candidate_property_id)
        return {
            "sent_to_review": True,
            "candidate_property_id": candidate_property_id,
        }

    toggle_selected(row_id, 1)
    return {"property_id": candidate_property_id}


def enter(row_id: int):
    return asyncio.run(_enter(row_id))


def dismiss(post_id: int):
    if not queries.get_building_review_post(post_id):
        raise LookupError(f"post {post_id} not in building review queue")
    db.conn.execute("UPDATE posts SET review_building = 0 WHERE id = ?", (post_id,))
    db.conn.commit()
    return True


def _nav_context(post_id, all_ids):
    idx = next((i for i, rid in enumerate(all_ids) if rid == post_id), None)
    if idx is None:
        return None
    total = len(all_ids)
    return {
        "current": idx + 1,
        "total": total,
        "prev_id": all_ids[idx - 1] if idx > 0 else None,
        "next_id": all_ids[idx + 1] if idx < total - 1 else None,
    }


def get_review_building_with_nav(post_id):
    post = queries.get_building_review_post(post_id)
    if not post:
        return None
    all_ids = queries.get_pending_building_ids()
    nav = _nav_context(post_id, all_ids)
    rows = asyncio.run(building_alias.get_building_names())
    buildings = [{"id": r[0], "name": r[1]} for r in rows]
    return {"post": post, "nav": nav, "buildings": buildings}


def assign(post_id: int, building_id: int):
    p = queries.get_building_review_post(post_id)
    if not p:
        raise LookupError(f"post {post_id} not in building review queue")

    post_json = json.loads(p["extraction_result_json"])

    async def _do_assign():
        async with get_session() as session:
            owner_id = await resolve_or_create_owner(session, post_json, p["author"])
            decision, candidate_id = await enter_post_with_known_building(
                session,
                post_json,
                owner_id,
                building_id,
                p["post_url"],
                p["text"],
                p["scraped_at"],
            )
            if decision == "insert":
                await session.commit()
                return candidate_id
            return None

    property_id = asyncio.run(_do_assign())

    db.conn.execute("UPDATE posts SET review_building = 0 WHERE id = ?", (post_id,))
    db.conn.commit()

    return {"property_id": property_id}


def dismiss(post_id: int):
    if not queries.get_building_review_post(post_id):
        raise LookupError(f"post {post_id} not in building review queue")
    db.conn.execute("UPDATE posts SET review_building = 0 WHERE id = ?", (post_id,))
    db.conn.commit()
    return True
