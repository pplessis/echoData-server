from app import create_app

# Expose the Flask WSGI application as `app` for Vercel/Python runtime
app = create_app()
