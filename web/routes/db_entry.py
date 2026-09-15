# web/routes/db_entry.py
import json
import asyncio
from datetime import datetime, timezone

from web.http_helpers import run_route
import web.queries.posts as posts_queries
import web.review_building as review_building
from db.database import db
import db.db_entry as db_entry


def _queue_review(row_id, candidate_property_id):
    db.conn.execute(
        """
        INSERT INTO entry_review_queue (post_id, candidate_property_id, reviewed, created_at)
        VALUES (?, ?, 0, ?)
        """,
        (row_id, candidate_property_id, datetime.now(timezone.utc).isoformat()),
    )
    db.conn.commit()


def _load_post_json(post_row):
    result_json = post_row.get("extraction_result_json")
    if not result_json:
        raise ValueError("no extraction result (extraction_result_json) for this post")
    parsed = json.loads(result_json)
    if not parsed.get("relevant"):
        raise ValueError("extraction marked this post as not relevant")
    return parsed


def enter(request):
    def _do(data):
        row_id = int(data["id"])

        p = posts_queries.get_post_by_id(row_id)
        if not p:
            p = review_building.get_building_review_post(row_id)
        if not p:
            raise ValueError(f"post {row_id} not found or already processed")

        post_json = _load_post_json(p)
        decision, candidate_property_id = asyncio.run(
            db_entry.enter_post(
                post_json, p["author"], p["post_url"], p["text"], p["scraped_at"]
            )
        )

        if decision == "discard":
            posts_queries.update_processed(row_id, 1)
            return 200, {"ok": True, "discarded": True}

        if decision == "review":
            _queue_review(row_id, candidate_property_id)
            posts_queries.update_processed(row_id, 1)
            return 200, {
                "ok": True,
                "sent_to_review": True,
                "candidate_property_id": candidate_property_id,
            }

        posts_queries.update_processed(row_id, 1)
        posts_queries.toggle_selected(row_id, 1)
        return 200, {"ok": True, "property_id": candidate_property_id}

    return run_route(_do, request)


def enter_building(request):
    def _do(data):
        row_id = int(data["id"])

        p = review_building.get_building_review_post(row_id)
        if not p:
            raise ValueError(f"post {row_id} not in building review queue")

        post_json = _load_post_json(p)
        decision, candidate_property_id = asyncio.run(
            db_entry.enter_post(
                post_json, p["author"], p["post_url"], p["text"], p["scraped_at"]
            )
        )

        db.conn.execute(
            "UPDATE posts SET processed = 1, review_building = 0 WHERE id = ?",
            (row_id,),
        )
        db.conn.commit()

        if decision == "discard":
            return 200, {"ok": True, "discarded": True}

        if decision == "review":
            _queue_review(row_id, candidate_property_id)
            return 200, {
                "ok": True,
                "sent_to_review": True,
                "candidate_property_id": candidate_property_id,
            }

        posts_queries.toggle_selected(row_id, 1)
        return 200, {"ok": True, "property_id": candidate_property_id}

    return run_route(_do, request)
