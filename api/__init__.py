from flask import Flask, jsonify

from .libs.src.utils import Print
from .config import Config
from .routes.home import home
from .routes.events_v100 import events as events_V100


# ============================================================================
# Create  APPLICATION
# ============================================================================
# Configure logging for better debugging and production monitoring

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # === ERRORS MANAGEMENT ===
    @app.errorhandler(404)
    def not_found(e):
        return jsonify( {"status":"error", "event":"unknown", "data":[], "errors": ["Unknown page"],"message": "#404 Unknown page.", "meta":{} } ), 404

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal Error: {e}")
        return jsonify( {"status":"error","event":"unknown", "data":[], "errors": ["Internal error"],"message": "#500 Internal error.", "meta":{} } ), 500


    # Enregistrer les blueprints PAGES and SERVICES API
    app.register_blueprint(home)
    app.register_blueprint(events_V100, url_prefix='/v100')


    return app

