# server.__init__.py
from flask import Flask, jsonify
from flask_cors import CORS

from db.exceptions import (
    OwnerConflictError,
    BuildingConflictError,
    NoIdentifiableOwnerError,
    BuildingNotFoundError,
)


def create_app():
    app = Flask(__name__)
    CORS(app)  # dev only — tighten origins before anything public-facing

    from server.posts import posts_bp

    app.register_blueprint(posts_bp)

    @app.errorhandler(OwnerConflictError)
    @app.errorhandler(BuildingConflictError)
    @app.errorhandler(NoIdentifiableOwnerError)
    @app.errorhandler(BuildingNotFoundError)
    def _handle_domain_conflict(e):
        return jsonify({"error": str(e)}), 409

    return app
