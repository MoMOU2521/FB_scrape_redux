# # web.pages.look_up.py
# from web.templates import POST_LOOKUP_TEMPLATE


# def build_lookup_page(post=None, searched_id=None, error=None):
#     return POST_LOOKUP_TEMPLATE % {
#         "searched_id": "" if searched_id is None else str(searched_id),
#         "error": error or "",
#         "has_post": bool(post),
#         "author": post.get("author", "") if post else "",
#         "group_name": post.get("group_name", "") if post else "",
#         "post_id": post.get("post_id", "") if post else "",
#         "row_id": post.get("id", 0) if post else 0,
#         "processed": ("Yes" if post and post.get("processed") else "No"),
#         "selected": ("Yes" if post and post.get("selected") else "No"),
#         "ai_processed": ("Yes" if post and post.get("ai_processed") else "No"),
#         "review_building": ("Yes" if post and post.get("review_building") else "No"),
#         "scraped_at": post.get("scraped_at", "") if post else "",
#         "url": post.get("post_url", "") if post else "",
#         "text": post.get("text", "") if post else "",
#         "ai_result": (
#             post.get("result_json_v1") or "Not yet AI-processed" if post else ""
#         ),
#         "gate1_reasoning": (
#             post.get("gate1_reasoning") or "No reasoning recorded." if post else ""
#         ),
#         "gate1_prompt_version": (
#             post.get("gate1_prompt_version") or "unknown" if post else ""
#         ),
#         "extraction_result": (
#             post.get("extraction_result_json") or "Not yet extracted" if post else ""
#         ),
#         "extraction_reasoning": (
#             post.get("extraction_reasoning") or "No reasoning recorded." if post else ""
#         ),
#         "extraction_prompt_version": (
#             post.get("extraction_prompt_version") or "unknown" if post else ""
#         ),
#         "images": "",
#     }
