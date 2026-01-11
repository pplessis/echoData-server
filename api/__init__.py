from flask import Flask, jsonify, redirect, url_for

from .libs.src.utils import Print
from .config import Config
from .routes.home import home
from .routes.events_v100 import events as events_V100
from .routes.oracle_v100 import oracle as oracle_v100


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

    # === REDIRECTIONS ===
    @app.route('/favicon.ico')
    def redirect_favicon():
        return redirect( url_for ('/static/medias/favIcon.svg') )

    @app.route('/apple-touch-icon.png')
    def redirect_appleTouchIcon():
        return redirect( url_for ('/static/medias/favIcon.svg') )

    @app.route('/apple-touch-icon-precomposed.png')
    def redirect_appleTouchIconPrecomposed():
        return redirect( url_for ('/static/medias/favIcon.svg') )

    # === BLUEPRINTS PAGES and SERVICES API
    app.register_blueprint(home)
    app.register_blueprint(events_V100, url_prefix='/v100')
    app.register_blueprint(oracle_v100, url_prefix='/v100')


    return app

