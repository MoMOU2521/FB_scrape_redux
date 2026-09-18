from flask import Blueprint, jsonify, request, send_file
import os

import web.queries.posts as queries
from db.services.posts.actions import (
    toggle_selected as _toggle_selected,
    delete_post as _delete_post,
)

posts_bp = Blueprint("posts", __name__, url_prefix="/api/posts")


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


@posts_bp.get("/next")
def next_unprocessed():
    row_id = queries.get_first_unprocessed_id()
    if row_id is None:
        return jsonify({"row_id": None})
    return jsonify({"row_id": row_id})


@posts_bp.get("/<int:row_id>")
def get_post(row_id):
    post = queries.get_post_by_id(row_id)
    if not post:
        return jsonify({"error": "not found or already processed"}), 404

    post = dict(post)
    post["unprocessed_count"] = queries.count_unprocessed_by_author(post["author"])

    all_rows = queries.get_unprocessed_ids()
    nav = _nav_context(row_id, all_rows)

    return jsonify({"post": post, "nav": nav})


@posts_bp.get("/author/<int:row_id>")
def get_author_posts(row_id):
    author = queries.get_author_of_post(row_id)
    if author is None:
        return jsonify({"error": "not found"}), 404

    all_posts = queries.get_posts_by_author_unprocessed(author)
    if not all_posts:
        return jsonify({"author": author, "post": None, "nav": None})

    target = dict(next((p for p in all_posts if p["id"] == row_id), all_posts[0]))
    target["unprocessed_count"] = len(all_posts)

    all_rows = [(p["id"], p["processed"]) for p in all_posts]
    nav = _nav_context(target["id"], all_rows)

    return jsonify({"author": author, "post": target, "nav": nav})


@posts_bp.post("/<int:row_id>/mark")
def mark(row_id):
    processed = int(request.json["processed"])
    queries.update_processed(row_id, processed)
    return jsonify({"ok": True})


@posts_bp.post("/<int:row_id>/selected")
def selected(row_id):
    value = int(request.json["selected"])
    _toggle_selected(row_id, value)
    return jsonify({"ok": True})


@posts_bp.delete("/<int:row_id>")
def delete(row_id):
    return jsonify({"ok": _delete_post(row_id)})
