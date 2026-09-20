# # web.actions.review.py
# import asyncio
# import json

# import web.queries.review as queries
# import db.db_entry as db_entry


# def approve(review_id: int):
#     """Force-insert the post's extraction result, bypassing duplicate check."""
#     row = queries.get_review_row(review_id)
#     if not row:
#         raise ValueError(f"review row {review_id} not found")

#     post_json = json.loads(row["extraction_result_json"])

#     async def _do():
#         async with db_entry.get_session() as db:
#             owner_id = await db_entry.resolve_or_create_owner(
#                 db, post_json, row["author"]
#             )
#             building_id = await db_entry.resolve_building_id(db, post_json)

#             property_id = await db_entry.create_property_registry(
#                 db, owner_id, post_json
#             )
#             await db_entry.create_unit_detail(db, property_id, building_id, post_json)
#             await db_entry.create_features(db, property_id, post_json)
#             await db_entry.create_rent_term(
#                 db, property_id, post_json, row["scraped_at"]
#             )
#             await db_entry.create_sale_term(db, property_id, post_json)
#             await db_entry.create_property_note(
#                 db, property_id, row["post_url"], row["text"]
#             )

#             await db.commit()
#             return property_id

#     property_id = asyncio.run(_do())
#     queries.mark_reviewed(review_id)
#     return property_id


# def reject(review_id: int):
#     """Discard — do not insert, just mark reviewed."""
#     row = queries.get_review_row(review_id)
#     if not row:
#         raise ValueError(f"review row {review_id} not found")
#     queries.mark_reviewed(review_id)
#     return True


# def dismiss(review_id: int):
#     """Leave post as-is, just clear from the queue."""
#     row = queries.get_review_row(review_id)
#     if not row:
#         raise ValueError(f"review row {review_id} not found")
#     queries.mark_reviewed(review_id)
#     return True
