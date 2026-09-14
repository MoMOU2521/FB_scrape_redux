# web/review_building.py
import os
import asyncio
from db.database import db
from web.templates import PAGE_TEMPLATE
from web.building_alias import get_building_names

# ============================================================================
# QUERIES
# ============================================================================


def get_pending_building_ids():
    rows = db.cur.execute("""
        SELECT id FROM posts
        WHERE review_building = 1 AND processed = 1
        ORDER BY id ASC
    """).fetchall()
    return [row["id"] for row in rows]


def get_first_pending_building_id():
    row = db.cur.execute("""
        SELECT id FROM posts
        WHERE review_building = 1 AND processed = 1
        ORDER BY id ASC LIMIT 1
    """).fetchone()
    return row["id"] if row else None


def get_building_review_post(post_id: int):
    row = db.cur.execute(
        """
        SELECT id, post_id, author, text, post_url, processed, group_name, scraped_at, selected,
               result_json_v1, gate1_reasoning, gate1_prompt_version,
               extraction_result_json, extraction_reasoning, extraction_prompt_version,
               review_building
        FROM posts
        WHERE id = ? AND review_building = 1 AND processed = 1
    """,
        (post_id,),
    ).fetchone()
    return dict(row) if row else None


def _attach_images(post):
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
# PAGE ASSEMBLY
# ============================================================================


def build_page(post_id: int, all_ids: list):
    post = get_building_review_post(post_id)
    if not post:
        return None

    _attach_images(post)

    current_idx = next((i for i, rid in enumerate(all_ids) if rid == post_id), None)
    if current_idx is None:
        return None

    total = len(all_ids)
    prev_id = all_ids[current_idx - 1] if current_idx > 0 else None
    next_id = all_ids[current_idx + 1] if current_idx < total - 1 else None

    prev_url = f"/review-building/{prev_id}" if prev_id else None
    next_url = f"/review-building/{next_id}" if next_id else None

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

    building_rows = asyncio.run(get_building_names())
    building_options = "\n".join(
        f'<option value="{bid}">{name}</option>' for bid, name in building_rows
    )

    dismiss_button = f"""
    <div class="action-row">
        <button class="btn-dismiss" onclick="dismissBuilding({post_id})" style="background: #f44336; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
            🗑️ Dismiss from Building Review
        </button>
        <span id="dismiss-feedback" class="feedback"></span>
    </div>
    """

    images_html = ""
    for img_path in post.get("images", []):
        images_html += f'<img src="/{img_path}" alt="">\n'

    return PAGE_TEMPLATE % {
        "page_title": "Building Review Queue",
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
        "row_id": post_id,
        "checked": "checked",
        "selected_checked": "checked" if post.get("selected", 0) else "",
        "prev_button": prev_button,
        "next_button": next_button,
        "unprocessed_count": 0,
        "back_button": '<a href="/" class="back-link">← Back to main queue</a>',
        "author_button": "",
        "building_options": building_options,
        "building_name": "",
        "dismiss_button": dismiss_button,
        "db_entry_endpoint": "/db-entry-building",
    }
