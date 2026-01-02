import logging
from dotenv import load_dotenv
from os import environ, path, makedirs, access, W_OK

load_dotenv()

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
# Configure logging for console output (serverless platforms expect logs on stdout)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

basePath = path.dirname(path.abspath(__file__))
logFolder = path.join(basePath, 'logs')

# Ensure logs directory exists (safe no-op on read-only filesystems)
try:
    makedirs(logFolder, exist_ok=True)
except Exception:
    # If directory creation fails (read-only FS), skip file logging
    pass

# Add FileHandler only when not running on Vercel (serverless) and folder is writable
if environ.get('VERCEL') != '1' and path.exists(logFolder) and access(logFolder, W_OK):
    logging.getLogger().addHandler(logging.FileHandler(path.join(logFolder, 'app.log')))

logger = logging.getLogger(__name__)


class Config:
    basePath = path.dirname(path.abspath(__file__))
    print(f"Config basePath: {basePath}")

    # Flask Application Settings
    FLASK_ENV = 'development'
    FLASK_HOST = '127.0.0.1'
    FLASK_PORT = 5055

    SECRET_KEY = environ.get('SECRET_KEY') or 'dev-secret-key-change-me'
    DEBUG = environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    DATABASE_JSON_FOLDER = environ.get('DATABASE_JSON_PATH') or path.join(basePath, 'static', 'data', 'events')
    JSON_FILE_EVENTS = 'internationalDays.json'
    DATABASE_JSON_EVENTS = path.join(DATABASE_JSON_FOLDER, JSON_FILE_EVENTS)

    JSON_FILE_DAYOFF = 'daysOff.json'
    DATABASE_JSON_DAYOFF = path.join(DATABASE_JSON_FOLDER, JSON_FILE_DAYOFF)

    # Flask-Mail, etc.
    MAIL_SERVER = environ.get('MAIL_SERVER')