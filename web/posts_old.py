# # web.posts.py
# import os
# import asyncio

# from db.db_core import core
# from web.templates import PAGE_TEMPLATE, POST_LOOKUP_TEMPLATE
# from web.building_alias import get_building_names

# # ============================================================================
# # QUERIES
# # ============================================================================


# def is_duplicate(author: str, text_preview: str) -> bool:
#     row = core.cur.execute(
#         "SELECT 1 FROM posts WHERE author = ? AND SUBSTR(text, 1, 1000) = ? LIMIT 1",
#         (author, text_preview[:1000]),
#     ).fetchone()
#     return row is not None


# def insert_post(post_id, author, timestamp, text, post_url, group_name, scraped_at):
#     import sqlite3

#     try:
#         core.cur.execute(
#             """INSERT INTO posts (post_id, author, timestamp, text, post_url, scraped_at, group_name, selected)
#                VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
#             (post_id, author, timestamp, text, post_url, scraped_at, group_name),
#         )
#         core.conn.commit()
#         return True
#     except sqlite3.IntegrityError:
#         return False


# def toggle_selected(post_id: int, value: int):
#     core.cur.execute("UPDATE posts SET selected = ? WHERE id = ?", (value, post_id))
#     core.conn.commit()
#     return core.cur.rowcount


# def get_post_by_id(row_id: int):
#     row = core.cur.execute(
#         """
#         SELECT id, post_id, author, text, post_url, processed, group_name, scraped_at, selected,
#                result_json_v1, gate1_reasoning, gate1_prompt_version,
#                extraction_result_json, extraction_reasoning, extraction_prompt_version
#         FROM posts
#         WHERE id = ?
#         AND (processed = 0 OR processed IS NULL)
#         """,
#         (row_id,),
#     ).fetchone()
#     return dict(row) if row else None


# def get_post_for_lookup(row_id: int):
#     """
#     Retrieve a post directly by its SQLite auto-increment row ID.

#     Unlike get_post_by_id(), this lookup intentionally has no processed
#     status restriction. It returns the exact posts row regardless of
#     whether the post is processed, unprocessed, selected, or in review.
#     """
#     row = core.cur.execute(
#         """
#         SELECT
#             id,
#             post_id,
#             author,
#             text,
#             post_url,
#             processed,
#             group_name,
#             scraped_at,
#             selected,
#             ai_processed,
#             review_building,
#             result_json_v1,
#             gate1_reasoning,
#             gate1_prompt_version,
#             extraction_result_json,
#             extraction_reasoning,
#             extraction_prompt_version
#         FROM posts
#         WHERE id = ?
#         """,
#         (row_id,),
#     ).fetchone()

#     return dict(row) if row else None


# def count_unprocessed_by_author(author: str) -> int:
#     row = core.cur.execute(
#         "SELECT COUNT(*) FROM posts WHERE author = ? AND (processed = 0 OR processed IS NULL)",
#         (author,),
#     ).fetchone()
#     return row[0]


# def get_unprocessed_ids():
#     rows = core.cur.execute("""
#         SELECT id, processed
#         FROM posts
#         WHERE processed = 0 OR processed IS NULL
#         ORDER BY id ASC
#     """).fetchall()
#     return [(row["id"], row["processed"]) for row in rows]


# def get_first_unprocessed_id():
#     row = core.cur.execute("""
#         SELECT id
#         FROM posts
#         WHERE processed = 0 OR processed IS NULL
#         ORDER BY id ASC
#         LIMIT 1
#     """).fetchone()
#     return row[0] if row else None


# def get_author_of_post(row_id: int):
#     row = core.cur.execute(
#         "SELECT author FROM posts WHERE id = ?", (row_id,)
#     ).fetchone()
#     return row["author"] if row else None


# def get_posts_by_author_unprocessed(author: str):
#     rows = core.cur.execute(
#         """
#         SELECT id, post_id, author, text, post_url, processed, group_name, selected,
#                result_json_v1, gate1_reasoning, gate1_prompt_version,
#                extraction_result_json, extraction_reasoning, extraction_prompt_version
#         FROM posts
#         WHERE author = ?
#         AND (processed = 0 OR processed IS NULL)
#         ORDER BY id
#         """,
#         (author,),
#     ).fetchall()
#     return [dict(r) for r in rows]


# def get_first_unprocessed_id_for_author(author: str):
#     row = core.cur.execute(
#         "SELECT id FROM posts WHERE author = ? AND (processed = 0 OR processed IS NULL) ORDER BY id LIMIT 1",
#         (author,),
#     ).fetchone()
#     return row[0] if row else None


# def update_processed(row_id: int, processed: int):
#     core.cur.execute("UPDATE posts SET processed = ? WHERE id = ?", (processed, row_id))
#     core.conn.commit()
#     return core.cur.rowcount


# # ============================================================================
# # SERVICE FUNCTIONS (used by server.py routes)
# # ============================================================================


# def _attach_images(post):
#     post_dir = f"images/{post['post_id']}"
#     if os.path.isdir(post_dir):
#         post["images"] = sorted(
#             [
#                 os.path.join(post_dir, f)
#                 for f in os.listdir(post_dir)
#                 if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))
#             ]
#         )
#     else:
#         post["images"] = []


# def get_post(row_id):
#     post = get_post_by_id(row_id)

#     if post:
#         _attach_images(post)
#         post["unprocessed_count"] = count_unprocessed_by_author(post["author"])
#     else:
#         post = {}

#     all_rows = get_unprocessed_ids()
#     return post, all_rows


# def get_author_posts_by_row_id(row_id):
#     """
#     Given a row id, resolve the author and fetch all unprocessed posts by
#     that author.
#     """
#     author = get_author_of_post(row_id)
#     if author is None:
#         return None, None, []

#     all_posts = get_posts_by_author_unprocessed(author)

#     if not all_posts:
#         return author, None, []

#     author_name = all_posts[0]["author"]

#     target_post = None
#     for p in all_posts:
#         if p["id"] == row_id:
#             target_post = p
#             break
#     if target_post is None:
#         target_post = all_posts[0]

#     _attach_images(target_post)
#     target_post["unprocessed_count"] = len(all_posts)

#     all_rows = [(p["id"], p["processed"]) for p in all_posts]

#     return author_name, target_post, all_rows


# def mark_processed(row_id, processed):
#     changes = update_processed(row_id, processed)
#     print(f"[UPDATED] row={row_id} processed={processed} changes={changes}")


# def delete_post(row_id: int) -> bool:
#     """Delete a post by ID. Returns True if deleted, False if not found."""
#     # First check if post exists
#     row = core.cur.execute("SELECT id FROM posts WHERE id = ?", (row_id,)).fetchone()
#     if not row:
#         return False

#     core.cur.execute("DELETE FROM posts WHERE id = ?", (row_id,))
#     core.conn.commit()
#     return core.cur.rowcount > 0


# # ============================================================================
# # LOOKUP PAGE
# # ============================================================================


# def build_lookup_page(post=None, searched_id=None, error=None):
#     images_html = ""

#     if post:
#         for img_path in post.get("images", []):
#             images_html += f'<img src="/{img_path}" alt="">\n'

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
#         "images": images_html,
#     }


# # ============================================================================
# # PAGE ASSEMBLY
# # ============================================================================


# def build_page(post, all_rows, mode="fifo", author_name=None):
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
#     _, processed = all_rows[current_idx]

#     images_html = ""
#     for img_path in post.get("images", []):
#         images_html += f'<img src="/{img_path}" alt="">\n'

#     if mode == "author":
#         prev_url = f"/author/{prev_id}" if prev_id else None
#         next_url = f"/author/{next_id}" if next_id else None
#         back_button = '<a href="/" class="back-link">← Back to all posts</a>'
#         author_button = ""
#     else:
#         prev_url = f"/post/{prev_id}" if prev_id else None
#         next_url = f"/post/{next_id}" if next_id else None
#         back_button = ""
#         author_button = f'<div class="author-action-row"><a href="/author/{post["id"]}">▶ Process all unprocessed posts by this author</a></div>'

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
#     building_rows = asyncio.run(get_building_names())
#     building_options = "\n".join(
#         f'<option value="{bid}">{name}</option>' for bid, name in building_rows
#     )

#     return PAGE_TEMPLATE % {
#         "page_title": (
#             "Unprocessed Posts"
#             if mode == "fifo"
#             else f"Unprocessed Posts by {author_name}"
#         ),
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
#         "images": images_html,
#         "row_id": post.get("id", 0),
#         "checked": "checked" if processed else "",
#         "selected_checked": "checked" if post.get("selected", 0) else "",
#         "prev_button": prev_button,
#         "next_button": next_button,
#         "unprocessed_count": post.get("unprocessed_count", 0),
#         "back_button": back_button,
#         "author_button": author_button,
#         "building_options": building_options,
#         "building_name": "",
#         "dismiss_button": "",
#         "db_entry_endpoint": "/db-entry",
#     }
