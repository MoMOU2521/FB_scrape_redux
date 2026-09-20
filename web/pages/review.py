# # web.pages.review.py
# from web.templates import REVIEW_TEMPLATE


# def build_page(row, all_ids: list):
#     if not row:
#         return None

#     review_id = row["review_id"]
#     current_idx = next((i for i, rid in enumerate(all_ids) if rid == review_id), None)
#     if current_idx is None:
#         return None

#     total = len(all_ids)
#     prev_id = all_ids[current_idx - 1] if current_idx > 0 else None
#     next_id = all_ids[current_idx + 1] if current_idx < total - 1 else None

#     prev_button = (
#         f'<a href="/review/{prev_id}"><button>← Previous</button></a>'
#         if prev_id
#         else "<button disabled>← Previous</button>"
#     )
#     next_button = (
#         f'<a href="/review/{next_id}"><button>Next →</button></a>'
#         if next_id
#         else "<button disabled>Next →</button>"
#     )

#     candidate_html = (
#         f'Candidate duplicate property ID: <strong>{row["candidate_property_id"]}</strong>'
#         if row["candidate_property_id"] is not None
#         else "No candidate property recorded."
#     )

#     return REVIEW_TEMPLATE % {
#         "current": current_idx + 1,
#         "total": total,
#         "prev_button": prev_button,
#         "next_button": next_button,
#         "author": row["author"] or "",
#         "post_url": row["post_url"] or "",
#         "scraped_at": row["scraped_at"] or "",
#         "candidate_html": candidate_html,
#         "text": row["text"] or "",
#         "extraction_result_json": row["extraction_result_json"] or "",
#         "review_id": row["review_id"],
#     }
