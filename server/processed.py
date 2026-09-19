# server/processed.py
from flask import Blueprint, jsonify

import server.queries.processed as queries
import server.services.processed as services

processed_bp = Blueprint("processed", __name__, url_prefix="/api/processed")


@processed_bp.get("/next")
def next_processed():
    return jsonify({"row_id": queries.get_first_processed_id()})


@processed_bp.get("/<int:row_id>")
def get_post(row_id):
    result = services.get_post_with_nav(row_id)
    if result is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(result)


@processed_bp.get("/author/<int:row_id>")
def get_author_posts(row_id):
    result = services.get_author_posts_with_nav(row_id)
    if result is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(result)
