# # web.pages.review_building.py
# from web.templates import PAGE_TEMPLATE


# def build_page(post, all_ids: list, building_options: str = ""):
#     if not post:
#         return None

#     post_id = post["id"]

#     current_idx = next((i for i, rid in enumerate(all_ids) if rid == post_id), None)
#     if current_idx is None:
#         return None

#     total = len(all_ids)
#     prev_id = all_ids[current_idx - 1] if current_idx > 0 else None
#     next_id = all_ids[current_idx + 1] if current_idx < total - 1 else None

#     prev_url = f"/review-building/{prev_id}" if prev_id else None
#     next_url = f"/review-building/{next_id}" if next_id else None

#     prev_button = (
#         f'<a href="{prev_url}"><button>← Previous</button></a>'
#         if prev_url
#         else "<button disabled>← Previous</button>"
#     )
#     next_button = (
#         f'<a href="{next_url}"><button>Next →</button></a>'
#         if next_url
#         else "<button disabled>Next →</button>"
#     )

#     dismiss_button = f"""
#     <div class="action-row">
#         <button class="btn-dismiss" onclick="dismissBuilding({post_id})" style="background: #f44336; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
#             🗑️ Dismiss from Building Review
#         </button>
#         <span id="dismiss-feedback" class="feedback"></span>
#     </div>
#     """

#     return PAGE_TEMPLATE % {
#         "page_title": "Building Review Queue",
#         "current": current_idx + 1,
#         "total": total,
#         "author": post.get("author", "UNKNOWN"),
#         "post_id": post.get("post_id", ""),
#         "group_name": post.get("group_name", "Unknown"),
#         "url": post.get("post_url", "") or "",
#         "text": post.get("text", ""),
#         "ai_result": post.get("result_json_v1") or "Not yet AI-processed",
#         "gate1_reasoning": post.get("gate1_reasoning") or "No reasoning recorded.",
#         "gate1_prompt_version": post.get("gate1_prompt_version") or "unknown",
#         "extraction_result": post.get("extraction_result_json") or "Not yet extracted",
#         "extraction_reasoning": post.get("extraction_reasoning")
#         or "No reasoning recorded.",
#         "extraction_prompt_version": post.get("extraction_prompt_version") or "unknown",
#         "images": "",
#         "row_id": post_id,
#         "checked": "checked",
#         "selected_checked": "checked" if post.get("selected", 0) else "",
#         "prev_button": prev_button,
#         "next_button": next_button,
#         "unprocessed_count": 0,
#         "back_button": '<a href="/" class="back-link">← Back to main queue</a>',
#         "author_button": "",
#         "building_options": building_options,
#         "building_name": "",
#         "dismiss_button": dismiss_button,
#         "db_entry_endpoint": "/db-entry-building",
#     }
