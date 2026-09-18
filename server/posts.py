# server/posts.py
from flask import Blueprint, jsonify, request

import web.queries.posts as queries
import server.services.posts as services
from db.services.posts.actions import (
    toggle_selected as _toggle_selected,
    delete_post as _delete_post,
)

posts_bp = Blueprint("posts", __name__, url_prefix="/api/posts")


@posts_bp.get("/next")
def next_unprocessed():
    row_id = queries.get_first_unprocessed_id()
    return jsonify({"row_id": row_id})


@posts_bp.get("/<int:row_id>")
def get_post(row_id):
    result = services.get_post_with_nav(row_id)
    if result is None:
        return jsonify({"error": "not found or already processed"}), 404
    return jsonify(result)


@posts_bp.get("/author/<int:row_id>")
def get_author_posts(row_id):
    result = services.get_author_posts_with_nav(row_id)
    if result is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(result)


@posts_bp.post("/<int:row_id>/mark")
def mark(row_id):
    queries.update_processed(row_id, int(request.json["processed"]))
    return jsonify({"ok": True})


@posts_bp.post("/<int:row_id>/selected")
def selected(row_id):
    _toggle_selected(row_id, int(request.json["selected"]))
    return jsonify({"ok": True})


@posts_bp.delete("/<int:row_id>")
def delete(row_id):
    return jsonify({"ok": _delete_post(row_id)})
