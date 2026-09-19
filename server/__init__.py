# server.__init__.py
from flask import Flask, app, jsonify
from flask_cors import CORS

from db.exceptions import (
    OwnerConflictError,
    BuildingConflictError,
    NoIdentifiableOwnerError,
    BuildingNotFoundError,
)
from server.posts import posts_bp
from server.processed import processed_bp
from server.admin import admin_bp
from server.entry import entry_bp
from server.review import review_bp
from server.review_building import review_building_bp


def create_app():
    app = Flask(__name__)
    CORS(app)  # dev only — tighten origins before anything public-facing

    app.register_blueprint(posts_bp)
    app.register_blueprint(processed_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(entry_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(review_building_bp)

    @app.errorhandler(OwnerConflictError)
    @app.errorhandler(BuildingConflictError)
    @app.errorhandler(NoIdentifiableOwnerError)
    @app.errorhandler(BuildingNotFoundError)
    def _handle_domain_conflict(e):
        return jsonify({"error": str(e)}), 409

    return app
