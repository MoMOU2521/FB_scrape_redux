# server/services/posts.py
import server.queries.posts as queries


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
    post = queries.get_post_by_id(row_id)
    if not post:
        return None

    post = dict(post)
    post["unprocessed_count"] = queries.count_unprocessed_by_author(post["author"])

    all_rows = queries.get_unprocessed_ids()
    nav = _nav_context(row_id, all_rows)

    return {"post": post, "nav": nav}


def get_author_posts_with_nav(row_id):
    author = queries.get_author_of_post(row_id)
    if author is None:
        return None

    all_posts = queries.get_posts_by_author_unprocessed(author)
    if not all_posts:
        return {"author": author, "post": None, "nav": None}

    target = dict(next((p for p in all_posts if p["id"] == row_id), all_posts[0]))
    target["unprocessed_count"] = len(all_posts)

    all_rows = [(p["id"], p["processed"]) for p in all_posts]
    nav = _nav_context(target["id"], all_rows)

    return {"author": author, "post": target, "nav": nav}


def get_post_for_lookup(row_id):
    return queries.get_post_for_lookup(row_id)
