# server/services/processed.py

import server.queries.processed as queries


def _nav_context(row_id, all_rows):
    idx = next((i for i, (rid, _) in enumerate(all_rows) if rid == row_id), None)
    if idx is None:
        return None
    total = len(all_rows)
    return {
        "current": idx + 1,
        "total": total,
        "prev_id": all_rows[idx - 1][0] if idx > 0 else None,
        "next_id": all_rows[idx + 1][0] if idx < total - 1 else None,
    }


def get_post_with_nav(row_id):
    post, all_rows = queries.get_post_with_context(row_id)
    if not post:
        return None
    return {"post": post, "nav": _nav_context(row_id, all_rows)}


def get_author_posts_with_nav(row_id):
    author, post, all_rows = queries.get_author_context(row_id)
    if author is None:
        return None
    nav = _nav_context(post["id"], all_rows) if post else None
    return {"author": author, "post": post, "nav": nav}
