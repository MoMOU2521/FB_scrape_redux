# web/routes/review_building.py
import json
import asyncio

from web.http_helpers import html_response, redirect, run_route
import web.queries.review_building as queries
import web.pages.review_building as pages
from web.building_alias import get_building_names
from db.database import db
from db.db_supabase import get_session
from db.services.db_entry.resolve_or_create_owner import resolve_or_create_owner
from db.services.db_entry.enter_post_with_known_building import (
    enter_post_with_known_building,
)


def index(request):
    first_id = queries.get_first_pending_building_id()
    if first_id:
        return redirect(f"/review-building/{first_id}")
    return html_response("<h2>No pending building reviews.</h2>")


def post(request):
    review_id = int(request["path"].split("/review-building/")[1])
    all_ids = queries.get_pending_building_ids()
    if review_id not in all_ids:
        return redirect("/review-building")

    p = queries.get_building_review_post(review_id)
    if not p:
        return redirect("/review-building")

    building_options = asyncio.run(get_building_names())
    html = pages.build_page(p, all_ids, building_options=building_options)
    if html is None:
        return redirect("/review-building")
    return html_response(html)


def assign(request):
    def _do(data):
        post_id = int(data["post_id"])
        building_id = int(data["building_id"])

        p = queries.get_building_review_post(post_id)
        if not p:
            raise ValueError(f"Post {post_id} not in building review queue")

        post_json = json.loads(p["extraction_result_json"])

        async def _do_assign():
            async with get_session() as session:
                owner_id = await resolve_or_create_owner(
                    session, post_json, p["author"]
                )
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

        return 200, {"ok": True, "property_id": property_id}

    return run_route(_do, request)


def dismiss(request):
    def _do(data):
        post_id = int(data["post_id"])
        db.conn.execute("UPDATE posts SET review_building = 0 WHERE id = ?", (post_id,))
        db.conn.commit()
        return 200, {"ok": True}

    return run_route(_do, request)
