# server/admin.py
import asyncio
import server.building_alias as building_alias
from flask import Blueprint, jsonify, request

import server.queries.blacklist as blacklist_queries
import server.queries.filters as filters_queries
import server.services.stats as stats_services

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/buildings")
def buildings():
    rows = asyncio.run(building_alias.get_building_names())
    return jsonify({"buildings": [{"id": r[0], "name": r[1]} for r in rows]})


@admin_bp.post("/add-alias")
def add_alias():
    building_id = request.json.get("building_id")
    alias = (request.json.get("alias") or "").strip()
    if building_id is None or not alias:
        return jsonify({"error": "Missing building_id or alias"}), 400
    ok = asyncio.run(building_alias.add_building_alias(int(building_id), alias))
    return jsonify({"ok": ok}), (200 if ok else 500)


@admin_bp.get("/blacklist")
def list_blacklist():
    sort = request.args.get("sort", "count")
    rows = blacklist_queries.get_blacklist_rows(sort)
    return jsonify({"rows": [{"author": a, "count": c} for a, c in rows]})


@admin_bp.post("/blacklist")
def add_blacklist():
    author = (request.json.get("author") or "").strip()
    if not author:
        return jsonify({"error": "Missing author"}), 400
    inserted, updated = blacklist_queries.add_blacklist(author)
    return jsonify({"ok": True, "inserted": inserted, "skipped": updated})


@admin_bp.delete("/blacklist")
def remove_blacklist():
    author = (request.json.get("author") or "").strip()
    if not author:
        return jsonify({"error": "Missing author"}), 400
    blacklist_queries.delete_blacklist(author)
    return jsonify({"ok": True})


@admin_bp.get("/filters")
def list_filters():
    rows = filters_queries.get_filter_rows()
    return jsonify({"rows": [{"phrase": p, "added_at": a} for p, a in rows]})


@admin_bp.post("/filters")
def add_filter():
    phrase = (request.json.get("phrase") or "").strip()
    if not phrase:
        return jsonify({"error": "Missing phrase"}), 400
    if filters_queries.filter_phrase_exists(phrase):
        return jsonify({"ok": True, "already_exists": True})
    filters_queries.add_filter_phrase(phrase)
    return jsonify({"ok": True, "already_exists": False})


@admin_bp.delete("/filters")
def remove_filter():
    phrase = (request.json.get("phrase") or "").strip()
    if not phrase:
        return jsonify({"error": "Missing phrase"}), 400
    filters_queries.delete_filter_phrase(phrase)
    return jsonify({"ok": True})


@admin_bp.get("/stats")
def stats():
    return jsonify(stats_services.get_group_stats())


@admin_bp.get("/authors")
def authors():
    min_count = int(request.args.get("min_count", 2))
    rows = stats_services.get_authors_by_unprocessed_count(min_count)
    return jsonify({"rows": rows})
