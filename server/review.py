# server/review.py
from flask import Blueprint, jsonify

import server.queries.review as queries
import server.services.review as services

review_bp = Blueprint("review", __name__, url_prefix="/api/review")


@review_bp.get("/next")
def next_review():
    return jsonify({"row_id": queries.get_first_pending_id()})


@review_bp.get("/<int:review_id>")
def get_review(review_id):
    result = services.get_review_with_nav(review_id)
    if result is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(result)


@review_bp.post("/<int:review_id>/approve")
def approve(review_id):
    try:
        property_id = services.approve(review_id)
        return jsonify({"ok": True, "property_id": property_id})
    except LookupError as e:
        return jsonify({"error": str(e)}), 404


@review_bp.post("/<int:review_id>/reject")
def reject(review_id):
    try:
        services.reject(review_id)
        return jsonify({"ok": True, "rejected": True})
    except LookupError as e:
        return jsonify({"error": str(e)}), 404


@review_bp.post("/<int:review_id>/dismiss")
def dismiss(review_id):
    try:
        services.dismiss(review_id)
        return jsonify({"ok": True, "dismissed": True})
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
