"""
Model Training Script
=====================
Train a KNN classifier on the Kaggle Resume Dataset.

Usage:
    python -m backend.train_model

Prerequisites:
    - Download the dataset from Kaggle:
      https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset
    - Place 'UpdatedResumeDataSet.csv' in backend/data/
"""
import os
import sys
import io
import warnings
warnings.filterwarnings('ignore')

# Fix Windows console encoding for Unicode
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ml.preprocessor import preprocess, clean_text, get_custom_stopwords
from backend.config import (
    DATASET_PATH, MODEL_DIR,
    TFIDF_MODEL_PATH, CLASSIFIER_MODEL_PATH, LABEL_ENCODER_PATH
)
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from imblearn.over_sampling import RandomOverSampler
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB


def load_dataset():
    """Load and validate the resume dataset."""
    if not os.path.exists(DATASET_PATH):
        print(f"[ERROR] Dataset not found at: {DATASET_PATH}")
        print("   Please download from: https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset")
        print(f"   Place 'UpdatedResumeDataSet.csv' in: {os.path.dirname(DATASET_PATH)}")
        sys.exit(1)

    df = pd.read_csv(DATASET_PATH)
    print(f"[OK] Dataset loaded: {len(df)} resumes")

    # Check required columns
    if 'Category' not in df.columns:
        print("[ERROR] Dataset must have a 'Category' column")
        sys.exit(1)

    # Identify the text column
    text_col = None
    for col in ['Resume_str', 'Resume', 'resume', 'Text', 'text']:
        if col in df.columns:
            text_col = col
            break

    if text_col is None:
        print(f"[ERROR] Cannot find text column. Available: {list(df.columns)}")
        sys.exit(1)

    print(f"   Text column: '{text_col}'")
    print(f"   Categories: {df['Category'].nunique()}")
    print(f"\n--- Category Distribution ---")
    print(df['Category'].value_counts().to_string())
    print()

    return df, text_col


def train():
    """Main training pipeline."""
    print("=" * 60)
    print("  Resume Classifier - Model Training")
    print("=" * 60)
    print()

    # 1. Load data
    df, text_col = load_dataset()

    # 2. Preprocess text
    print("[STEP] Preprocessing resume text...")
    df['cleaned'] = df[text_col].apply(lambda x: clean_text(str(x)))
    # Remove empty rows
    df = df[df['cleaned'].str.len() > 10].reset_index(drop=True)
    print(f"   {len(df)} resumes after cleaning")

    # 3. Encode labels
    print("[STEP] Encoding labels...")
    le = LabelEncoder()
    df['label'] = le.fit_transform(df['Category'])
    print(f"   {len(le.classes_)} classes: {list(le.classes_)[:10]}...")

    # 4. TF-IDF Vectorization
    print("[STEP] TF-IDF Vectorization (Noise-Filtered Signal Space)...")
    # min_df=5 is crucial to stop memorizing unique resume words
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3), 
        stop_words='english', 
        sublinear_tf=True,
        max_df=0.6,
        min_df=5,
        max_features=8000
    )
    
    X = vectorizer.fit_transform(df['cleaned'])
    y = df['label']
    print(f"   Feature matrix shape: {X.shape}")

    # 5. Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")

    # 5.5 Oversampling
    print("\n[STEP] Oversampling Minority Classes...")
    ros = RandomOverSampler(random_state=42)
    X_train_res, y_train_res = ros.fit_resample(X_train, y_train)
    print(f"   Train (resampled): {X_train_res.shape[0]}")

    # 6. Train Stability Ensemble 4.0 (XGB + SVC)
    from xgboost import XGBClassifier
    from sklearn.svm import LinearSVC
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.ensemble import VotingClassifier
    
    print("\n[STEP] Training Stability Ensemble 4.0 (Regularized XGB + SVC)...")
    
    # max_depth=3 prevents overfitting by forcing simple decision rules
    xgb = XGBClassifier(
        n_estimators=500,
        max_depth=3, 
        gamma=2.0, # Minimum loss reduction to split
        learning_rate=0.1,
        random_state=42,
        eval_metric='mlogloss',
        n_jobs=-1
    )
    
    # C=0.1 is the middle ground between signal and stability
    svc_base = LinearSVC(C=0.1, random_state=42, class_weight='balanced')
    svc = CalibratedClassifierCV(svc_base, cv=5)
    
    model = VotingClassifier(
        estimators=[
            ('xgb', xgb),
            ('svc', svc)
        ],
        voting='soft',
        n_jobs=-1
    )
    
    model.fit(X_train_res, y_train_res)
    
    train_pred = model.predict(X_train)
    train_acc = accuracy_score(y_train, train_pred)
    print(f"   Training Accuracy: {train_acc:.4f} ({train_acc*100:.1f}%)")

    # 7. Evaluate
    print("\n--- Evaluation Results ---")
    print("-" * 60)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n   Testing Accuracy: {accuracy:.4f} ({accuracy*100:.1f}%)\n")

    # Classification report
    target_names = le.inverse_transform(sorted(y_test.unique()))
    report = classification_report(y_test, y_pred, target_names=target_names, zero_division=0)
    print(report)

    # 8. Save models
    print("[STEP] Saving model artifacts...")
    os.makedirs(MODEL_DIR, exist_ok=True)

    joblib.dump(vectorizer, TFIDF_MODEL_PATH)
    print(f"   [OK] TF-IDF Pipeline -> {TFIDF_MODEL_PATH}")

    joblib.dump(model, CLASSIFIER_MODEL_PATH)
    print(f"   [OK] Classifier Model  -> {CLASSIFIER_MODEL_PATH}")

    joblib.dump(le, LABEL_ENCODER_PATH)
    print(f"   [OK] Label Encoder     -> {LABEL_ENCODER_PATH}")

    print(f"\n{'=' * 60}")
    print(f"  Training complete! Accuracy: {accuracy*100:.1f}%")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    train()
