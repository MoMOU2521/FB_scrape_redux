# server/entry.py
from flask import Blueprint, jsonify

import server.services.entry as services

entry_bp = Blueprint("entry", __name__, url_prefix="/api/entry")


@entry_bp.post("/<int:row_id>")
def enter(row_id):
    try:
        return jsonify(services.enter_post(row_id))
    except LookupError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
