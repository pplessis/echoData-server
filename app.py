import os
from flask          import Flask, render_template, request, jsonify, url_for, redirect
from urllib.parse   import urlencode
from .api            import create_app
from .api.config     import logger, Config

# Initialize Flask app with correct template folder path
app = create_app()



# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    """
    Application entry point.

    Before running:
    1. Copy .env.example to .env
    2. Fill in your Adyen credentials in .env
    3. Run: pip install -r requirements.txt
    4. Run: python app.py

    The application will start on http://localhost:5001
    """

    try:
        # Get Flask settings
        debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

        host = os.getenv('FLASK_HOST', app.config['FLASK_HOST'])
        port = int(os.getenv('FLASK_PORT', app.config['FLASK_PORT']))

        logger.info(f"Debug Mode: {debug_mode}")
        logger.info(f"Server: {host}:{port}")

        # Run Flask development server
        # NOTE: For production, use a WSGI server like Gunicorn:
        #   gunicorn -w 4 -b 0.0.0.0:5001 app:app
        app.run(host=host, port=port, debug=debug_mode)

    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        exit(1)

