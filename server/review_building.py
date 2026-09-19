# server/review_building.py
from flask import Blueprint, jsonify, request

import server.queries.review_building as queries
import server.services.review_building as services

review_building_bp = Blueprint(
    "review_building", __name__, url_prefix="/api/review-building"
)


@review_building_bp.get("/next")
def next_building():
    return jsonify({"row_id": queries.get_first_pending_building_id()})


@review_building_bp.get("/<int:post_id>")
def get_building(post_id):
    result = services.get_review_building_with_nav(post_id)
    if result is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(result)


@review_building_bp.post("/<int:post_id>/enter")
def enter(post_id):
    try:
        result = services.enter(post_id)
        return jsonify({"ok": True, **result})
    except LookupError as e:
        return jsonify({"error": str(e)}), 404


@review_building_bp.post("/<int:post_id>/assign")
def assign(post_id):
    building_id = request.json.get("building_id")
    if building_id is None:
        return jsonify({"error": "Missing building_id"}), 400
    try:
        result = services.assign(post_id, int(building_id))
        return jsonify({"ok": True, **result})
    except LookupError as e:
        return jsonify({"error": str(e)}), 404


@review_building_bp.post("/<int:post_id>/dismiss")
def dismiss(post_id):
    try:
        services.dismiss(post_id)
        return jsonify({"ok": True})
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
