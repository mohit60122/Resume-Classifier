# CV/Resume Screener with Machine Learning

An AI-powered resume screening application built with **Flask** (frontend dashboard) and **FastAPI** (backend API), using NLP and Machine Learning to classify resumes, match them against job descriptions, and extract skills.

## Features

- 🤖 **Resume Classification** — Classifies resumes into 24 job categories using a professional-grade **Stability Ensemble** (XGBoost + Calibrated SVC) achieving **82.9% accuracy**.
- 📊 **JD Matching** — Ranks resumes against a job description using TF-IDF + Cosine Similarity
- 🔍 **Skill Extraction** — Identifies 150+ technical skills, soft skills, and certifications
- 📄 **Resume Parsing** — Extracts text from PDF and DOCX files
- 🎨 **Premium Dashboard** — Dark glassmorphism UI with animations

## Performance Metrics (Professional Grade)

Our model has been optimized for real-world generalization, achieving a "Final Exam Victory" certification level:

- **Testing Accuracy**: 82.9%
- **Generalization Gap**: 8.6% (Training 91.5% vs Testing 83%)
- **Noise Filtering**: Implemented `min_df=5` filtering to prevent memorization of unique resume words.
- **Robustness**: 5-fold cross-validated probability calibration.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Flask + Jinja2 + HTML/CSS/JS |
| Backend API | FastAPI + Uvicorn |
| ML/NLP | scikit-learn, XGBoost, NLTK, TF-IDF |
| Parsing | PyPDF2, python-docx |
| Data | pandas, numpy, imbalanced-learn |

## Setup Instructions

### 1. Install Dependencies

```bash
# Install backend dependencies
pip install -r backend/requirements.txt xgboost imbalanced-learn

# Install frontend dependencies
pip install -r frontend/requirements.txt
```

### 2. Download Dataset

Download the Resume Dataset from Kaggle:
- https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset

Place `UpdatedResumeDataSet.csv` in `backend/data/`

### 3. Train the Model

```bash
python -m backend.train_model
```

This will:
- Load and preprocess the dataset
- Train a **Stability Ensemble 4.0** (Tuned XGBoost + Calibrated LinearSVC)
- Implement noise pruning to ensure high generalization
- Save model artifacts to `backend/models/`
- Print accuracy and detailed classification report

### 4. Start the Backend (FastAPI)

```bash
uvicorn backend.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 5. Start the Frontend (Flask)

```bash
python -m frontend.app
```

Dashboard available at: http://localhost:5000

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/classify` | POST | Upload resumes → get predicted categories |
| `/api/match` | POST | Upload JD + resumes → get ranked match scores |
| `/api/extract-skills` | POST | Upload resume → get extracted skills |

## Project Structure

```
├── backend/                 # FastAPI Backend
│   ├── main.py              # FastAPI app entry point
│   ├── train_model.py       # Model training script
│   ├── config.py            # Configuration
│   ├── api/routes.py        # API route handlers
│   ├── ml/
│   │   ├── preprocessor.py  # Text preprocessing
│   │   ├── classifier.py    # Resume classifier
│   │   ├── matcher.py       # JD matching
│   │   └── skill_extractor.py
│   ├── utils/parser.py      # PDF/DOCX parsing
│   ├── models/              # Saved ML models
│   └── data/                # Dataset
│
├── frontend/                # Flask Frontend
│   ├── app.py               # Flask app
│   ├── config.py            # Configuration
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # CSS, JS, images
│
└── uploads/                 # Uploaded files (runtime)
```
