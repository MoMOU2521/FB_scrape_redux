# web.processed.py
import os
import asyncio

from db.db_core import core
from web.templates import PAGE_TEMPLATE
from web.building_alias import get_building_names

# ============================================================================
# QUERIES
# ============================================================================


def get_processed_ids():
    """Get all processed post IDs ordered oldest to newest."""
    rows = core.cur.execute("""
        SELECT id, processed
        FROM posts
        WHERE processed = 1
        ORDER BY id DESC
    """).fetchall()
    return [(row["id"], row["processed"]) for row in rows]


def get_first_processed_id():
    """Get the oldest processed post ID."""
    row = core.cur.execute("""
        SELECT id
        FROM posts
        WHERE processed = 1
        ORDER BY id DESC
        LIMIT 1 
    """).fetchone()
    return row[0] if row else None


# def get_post_by_id(row_id: int):
#     """Fetch a specific processed post by ID."""
#     row = core.cur.execute(
#         """
#         SELECT id, post_id, author, text, post_url, processed, group_name, scraped_at, selected,
#                result_json_v1, gate1_reasoning, gate1_prompt_version
#         FROM posts
#         WHERE id = ?
#         AND processed = 1
#         """,
#         (row_id,),
#     ).fetchone()
#     return dict(row) if row else None
def get_post_by_id(row_id: int):
    row = core.cur.execute(
        """
        SELECT id, post_id, author, text, post_url, processed, group_name, scraped_at, selected,
               result_json_v1, gate1_reasoning, gate1_prompt_version,
               extraction_result_json, extraction_reasoning, extraction_prompt_version
        FROM posts
        WHERE id = ?
        AND processed = 1
        """,
        (row_id,),
    ).fetchone()
    return dict(row) if row else None


def get_author_of_post(row_id: int):
    """Get author name for a given post ID (processed or not)."""
    row = core.cur.execute(
        "SELECT author FROM posts WHERE id = ?", (row_id,)
    ).fetchone()
    return row["author"] if row else None


# def get_posts_by_author_processed(author: str):
#     """Get all processed posts for a specific author, ordered oldest to newest."""
#     rows = core.cur.execute(
#         """
#         SELECT id, post_id, author, text, post_url, processed, group_name, selected,
#                result_json_v1, gate1_reasoning, gate1_prompt_version
#         FROM posts
#         WHERE author = ?
#         AND processed = 1
#         ORDER BY id
#         """,
#         (author,),
#     ).fetchall()
#     return [dict(r) for r in rows]
def get_posts_by_author_processed(author: str):
    rows = core.cur.execute(
        """
        SELECT id, post_id, author, text, post_url, processed, group_name, selected,
               result_json_v1, gate1_reasoning, gate1_prompt_version,
               extraction_result_json, extraction_reasoning, extraction_prompt_version
        FROM posts
        WHERE author = ?
        AND processed = 1
        ORDER BY id
        """,
        (author,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_first_processed_id_for_author(author: str):
    """Get the oldest processed post ID for a specific author."""
    row = core.cur.execute(
        """
        SELECT id
        FROM posts
        WHERE author = ?
        AND processed = 1
        ORDER BY id
        LIMIT 1
        """,
        (author,),
    ).fetchone()
    return row[0] if row else None


def count_processed_by_author(author: str) -> int:
    """Count processed posts for a specific author."""
    row = core.cur.execute(
        "SELECT COUNT(*) FROM posts WHERE author = ? AND processed = 1",
        (author,),
    ).fetchone()
    return row[0]


# ============================================================================
# HELPERS
# ============================================================================


def _attach_images(post):
    """Attach image list to a post dict."""
    post_dir = f"images/{post['post_id']}"
    if os.path.isdir(post_dir):
        post["images"] = sorted(
            [
                os.path.join(post_dir, f)
                for f in os.listdir(post_dir)
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))
            ]
        )
    else:
        post["images"] = []


# ============================================================================
# SERVICE FUNCTIONS (called by server.py routes)
# ============================================================================


def get_post(row_id):
    """Fetch a processed post and the full processed list for navigation."""
    post = get_post_by_id(row_id)

    if post:
        _attach_images(post)
        post["processed_count"] = count_processed_by_author(post["author"])
    else:
        post = {}

    all_rows = get_processed_ids()
    return post, all_rows


def get_author_posts_by_row_id(row_id):
    """
    Given a row id, resolve the author and fetch all processed posts by that author.
    Used for author-mode navigation within processed view.
    """
    author = get_author_of_post(row_id)
    if author is None:
        return None, None, []

    all_posts = get_posts_by_author_processed(author)

    if not all_posts:
        return author, None, []

    author_name = all_posts[0]["author"]

    target_post = None
    for p in all_posts:
        if p["id"] == row_id:
            target_post = p
            break
    if target_post is None:
        target_post = all_posts[0]

    _attach_images(target_post)
    target_post["processed_count"] = len(all_posts)

    all_rows = [(p["id"], p["processed"]) for p in all_posts]

    return author_name, target_post, all_rows


# ============================================================================
# PAGE ASSEMBLY
# ============================================================================


def build_page(post, all_rows, mode="processed", author_name=None):
    """
    Build the HTML page for a processed post with navigation.

    Args:
        post: The current post dict
        all_rows: List of (id, processed) tuples for navigation
        mode: "processed" (global processed FIFO) or "author" (author-filtered)
        author_name: Name of author when mode="author"
    """
    if not post or not all_rows:
        return None

    # Find current position in the list
    current_idx = next(
        (i for i, (rid, _) in enumerate(all_rows) if rid == post["id"]), None
    )
    if current_idx is None:
        return None

    total = len(all_rows)
    prev_id = all_rows[current_idx - 1][0] if current_idx > 0 else None
    next_id = all_rows[current_idx + 1][0] if current_idx < total - 1 else None

    # Build image HTML
    images_html = ""
    for img_path in post.get("images", []):
        images_html += f'<img src="/{img_path}" alt="">\n'

    # Determine navigation URLs based on mode
    if mode == "author":
        prev_url = f"/processed/author/{prev_id}" if prev_id else None
        next_url = f"/processed/author/{next_id}" if next_id else None
        back_button = (
            '<a href="/processed" class="back-link">← Back to processed posts</a>'
        )
        author_button = ""
    else:
        prev_url = f"/processed/{prev_id}" if prev_id else None
        next_url = f"/processed/{next_id}" if next_id else None
        back_button = ""
        # If there are multiple processed posts by this author, offer to filter by author
        if post.get("processed_count", 0) > 1:
            author_button = f'<div class="author-action-row"><a href="/processed/author/{post["id"]}">▶ View all processed posts by this author</a></div>'
        else:
            author_button = ""

    # Build navigation buttons
    prev_button = (
        f'<a href="{prev_url}"><button>← Previous</button></a>'
        if prev_url
        else "<button disabled>← Previous</button>"
    )
    next_button = (
        f'<a href="{next_url}"><button>Next →</button></a>'
        if next_url
        else "<button disabled>Next →</button>"
    )

    # Building options for alias dropdown
    building_rows = asyncio.run(get_building_names())
    building_options = "\n".join(
        f'<option value="{bid}">{name}</option>' for bid, name in building_rows
    )

    # Determine page title
    page_title = (
        "Processed Posts"
        if mode == "processed"
        else f"Processed Posts by {author_name}"
    )

    return PAGE_TEMPLATE % {
        "page_title": page_title,
        "current": current_idx + 1,
        "total": total,
        "author": post.get("author", "UNKNOWN"),
        "post_id": post.get("post_id", ""),
        "group_name": post.get("group_name", "Unknown"),
        "url": post.get("post_url", "") or "",
        "text": post.get("text", ""),
        "ai_result": post.get("result_json_v1") or "Not yet AI-processed",
        "gate1_reasoning": post.get("gate1_reasoning") or "No reasoning recorded.",
        "gate1_prompt_version": post.get("gate1_prompt_version") or "unknown",
        "extraction_result": post.get("extraction_result_json") or "Not yet extracted",
        "extraction_reasoning": post.get("extraction_reasoning")
        or "No reasoning recorded.",
        "extraction_prompt_version": post.get("extraction_prompt_version") or "unknown",
        "images": images_html,
        "row_id": post.get("id", 0),
        "checked": "checked",
        "selected_checked": "checked" if post.get("selected", 0) else "",
        "prev_button": prev_button,
        "next_button": next_button,
        "unprocessed_count": 0,  # Not applicable, but template expects it
        "back_button": back_button,
        "author_button": author_button,
        "building_options": building_options,
        "building_name": "",
        "dismiss_button": "",
    }
