# # web.pages.processed.py
# from web.templates import PAGE_TEMPLATE


# def build_page(post, all_rows, mode="processed", author_name=None):
#     """
#     Build the HTML page for a processed post with navigation.

#     Args:
#         post: The current post dict
#         all_rows: List of (id, processed) tuples for navigation
#         mode: "processed" (global processed FIFO) or "author" (author-filtered)
#         author_name: Name of author when mode="author"
#     """
#     if not post or not all_rows:
#         return None

#     current_idx = next(
#         (i for i, (rid, _) in enumerate(all_rows) if rid == post["id"]), None
#     )
#     if current_idx is None:
#         return None

#     total = len(all_rows)
#     prev_id = all_rows[current_idx - 1][0] if current_idx > 0 else None
#     next_id = all_rows[current_idx + 1][0] if current_idx < total - 1 else None

#     if mode == "author":
#         prev_url = f"/processed/author/{prev_id}" if prev_id else None
#         next_url = f"/processed/author/{next_id}" if next_id else None
#         back_button = (
#             '<a href="/processed" class="back-link">← Back to processed posts</a>'
#         )
#         author_button = ""
#     else:
#         prev_url = f"/processed/{prev_id}" if prev_id else None
#         next_url = f"/processed/{next_id}" if next_id else None
#         back_button = ""
#         if post.get("processed_count", 0) > 1:
#             author_button = f'<div class="author-action-row"><a href="/processed/author/{post["id"]}">▶ View all processed posts by this author</a></div>'
#         else:
#             author_button = ""

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

#     page_title = (
#         "Processed Posts"
#         if mode == "processed"
#         else f"Processed Posts by {author_name}"
#     )

#     return PAGE_TEMPLATE % {
#         "page_title": page_title,
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
#         "row_id": post.get("id", 0),
#         "checked": "checked",
#         "selected_checked": "checked" if post.get("selected", 0) else "",
#         "prev_button": prev_button,
#         "next_button": next_button,
#         "unprocessed_count": 0,
#         "back_button": back_button,
#         "author_button": author_button,
#         "building_options": "",
#         "building_name": "",
#         "dismiss_button": "",
#     }
