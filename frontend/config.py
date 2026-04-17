import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# FastAPI backend URL
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# Flask settings
SECRET_KEY = os.environ.get("SECRET_KEY", "cv-screener-secret-key-2024")
DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() == "true"

# Upload settings
UPLOAD_DIR = os.path.join(os.path.dirname(BASE_DIR), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

os.makedirs(UPLOAD_DIR, exist_ok=True)
