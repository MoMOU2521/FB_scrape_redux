# server/admin.py
from flask import Blueprint, jsonify, request

import server.queries.blacklist as blacklist_queries
import server.queries.filters as filters_queries

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.post("/blacklist")
def add_blacklist():
    author = (request.json.get("author") or "").strip()
    if not author:
        return jsonify({"error": "Missing author"}), 400
    inserted, updated = blacklist_queries.add_blacklist(author)
    return jsonify({"ok": True, "inserted": inserted, "skipped": updated})


@admin_bp.post("/filters")
def add_filter():
    phrase = (request.json.get("phrase") or "").strip()
    if not phrase:
        return jsonify({"error": "Missing phrase"}), 400
    if filters_queries.filter_phrase_exists(phrase):
        return jsonify({"ok": True, "already_exists": True})
    filters_queries.add_filter_phrase(phrase)
    return jsonify({"ok": True, "already_exists": False})
