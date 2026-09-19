# server/services/entry.py
import asyncio
import json

import db.db_entry as db_entry
import server.queries.posts as posts_queries
import server.queries.review as review_queries


def _load_extraction(post: dict) -> dict:
    raw = post.get("extraction_result_json")
    if not raw:
        raise ValueError("no extraction result for this post")
    parsed = json.loads(raw)
    if not parsed.get("relevant"):
        raise ValueError("extraction marked this post as not relevant")
    return parsed


def enter_post(row_id: int) -> dict:
    post = posts_queries.get_post_by_id(row_id)
    if not post:
        raise LookupError(f"post {row_id} not found or already processed")

    post_json = _load_extraction(post)
    decision, property_id = asyncio.run(
        db_entry.enter_post(
            post_json,
            post["author"],
            post["post_url"],
            post["text"],
            post["scraped_at"],
        )
    )

    if decision == "discard":
        posts_queries.update_processed(row_id, 1)
        return {"decision": "discard"}

    if decision == "review":
        review_queries.queue_review(row_id, property_id)
        posts_queries.update_processed(row_id, 1)
        return {"decision": "review", "candidate_property_id": property_id}

    posts_queries.update_processed(row_id, 1)
    posts_queries.toggle_selected(row_id, 1)
    return {"decision": "insert", "property_id": property_id}
