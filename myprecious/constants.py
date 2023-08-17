from dotenv import load_dotenv
import os, uuid
load_dotenv()

def env_bool(env_var: str):
    return os.getenv(env_var, 'False') == 'True'

# user-provided config
DEBUG_SWITCH = env_bool("DEBUG_SWITCH")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

SECRET_KEY = os.getenv("SECRET_KEY", str(uuid.uuid4()))
DEFAULT_ADMIN_USER = os.getenv("DEFAULT_ADMIN_USER", "admin")
DEFAULT_ADMIN_PW = os.getenv("DEFAULT_ADMIN_PW", "admin")
DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "")
PEPPER = os.getenv("PEPPER", "")

# other constants
MIN_PW_LENGTH = 5
MIN_USERNAME_LENGTH = 3
MAX_LENGTH = 20
MISSING_COVER_URL = "https://placehold.co/100?text=no%20cover"
BASE_DIRECTORY = "data"
CONTENT_DIRECTORY = "content"
MIGRATIONS_DIRECTORY = "migrations"
MIGRATIONS_INIT_FILE = "init.sql"
MIGRATIONS_INIT_PATH = os.path.join(MIGRATIONS_DIRECTORY, MIGRATIONS_INIT_FILE)
DB_FILE = "myprecious.db"

DB_PATH = os.path.join(BASE_DIRECTORY, DB_FILE)
NO_GAME = {
    "game_id": -1,
    "platform_id": -1,
    "title": " Click here to select a game.",
    "cover": MISSING_COVER_URL
}
TOKEN_FILENAME = "igdb.txt"
TOKEN_PATH = os.path.join(BASE_DIRECTORY, TOKEN_FILENAME)
AUTH_URL = "https://id.twitch.tv/oauth2/token"
AUTH_URL_PARAMS = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "client_credentials"
}
