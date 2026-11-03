from pathlib import Path

APP_NAME = "Campus Lost & Found"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = DATA_DIR / "campus_lost_found.sqlite3"
MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".webp"}
PBKDF2_ITERATIONS = 310_000
CATEGORIES = ("Electronics", "ID / Cards", "Books", "Bags", "Clothing", "Keys", "Accessories", "Other")
TEAM = (
    ("Priyanshu Mishra", "TEAM LEADER"),
    ("Argha Atta", "TEAM MEMBER"),
    ("Kumar Harshvardhan Jaytri", "TEAM MEMBER"),
)
