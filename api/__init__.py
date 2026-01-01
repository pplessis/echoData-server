from flask import Flask

from .libs.src.utils import Print
from .config import Config
from .routes.home import home
from .routes.international_day_v100 import international_day_v100


# ============================================================================
# Create  APPLICATION
# ============================================================================
# Configure logging for better debugging and production monitoring

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enregistrer les blueprints PAGES and SERVICES API
    app.register_blueprint(home)
    app.register_blueprint(international_day_v100)

    return app
