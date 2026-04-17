import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Upload settings
UPLOAD_DIR = os.path.join(os.path.dirname(BASE_DIR), "uploads")
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE_MB = 10

# Model paths
MODEL_DIR = os.path.join(BASE_DIR, "models")
TFIDF_MODEL_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
CLASSIFIER_MODEL_PATH = os.path.join(MODEL_DIR, "classifier_model.pkl")
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")

# Dataset
DATA_DIR = os.path.join(BASE_DIR, "data")
DATASET_PATH = os.path.join(DATA_DIR, "UpdatedResumeDataSet.csv")

# CORS
FRONTEND_ORIGIN = "http://localhost:5000"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
