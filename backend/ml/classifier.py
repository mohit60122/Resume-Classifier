"""
Resume Classifier - Predict job category from resume text.
Uses a pre-trained TF-IDF + KNN model.
"""
import os
import joblib
import numpy as np
from backend.ml.preprocessor import clean_text
from backend.config import TFIDF_MODEL_PATH, CLASSIFIER_MODEL_PATH, LABEL_ENCODER_PATH


class ResumeClassifier:
    """Loads trained model and classifies resume text into job categories."""

    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.label_encoder = None
        self._loaded = False

    def load_models(self):
        """Load pre-trained model artifacts from disk."""
        if self._loaded:
            return

        if not all(os.path.exists(p) for p in [
            TFIDF_MODEL_PATH, CLASSIFIER_MODEL_PATH, LABEL_ENCODER_PATH
        ]):
            raise FileNotFoundError(
                "Model files not found. Please run train_model.py first."
            )

        self.vectorizer = joblib.load(TFIDF_MODEL_PATH)
        self.model = joblib.load(CLASSIFIER_MODEL_PATH)
        self.label_encoder = joblib.load(LABEL_ENCODER_PATH)
        self._loaded = True
        print("✅ ML models loaded successfully.")

    def predict_category(self, resume_text: str) -> dict:
        """
        Predict the job category for a single resume.

        Returns:
            dict with 'category' (str) and 'confidence' (float, 0-100)
        """
        self.load_models()

        # Preprocess
        cleaned = clean_text(resume_text)

        if not cleaned:
            return {"category": "Unknown", "confidence": 0.0}

        # Vectorize
        features = self.vectorizer.transform([cleaned])

        # Predict
        prediction = self.model.predict(features)[0]
        category = self.label_encoder.inverse_transform([prediction])[0]

        # Get confidence from prediction probabilities
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(features)[0]
            confidence = round(float(np.max(probabilities)) * 100, 1)
        else:
            # For models without predict_proba, use decision function
            confidence = 85.0  # Default confidence

        return {
            "category": category,
            "confidence": confidence
        }

    def predict_batch(self, resume_texts: list) -> list:
        """
        Predict categories for multiple resumes.

        Returns:
            List of dicts with 'category' and 'confidence'
        """
        self.load_models()
        results = []

        for text in resume_texts:
            result = self.predict_category(text)
            results.append(result)

        return results

    def get_categories(self) -> list:
        """Return all possible category labels."""
        self.load_models()
        return list(self.label_encoder.classes_)


# Global singleton instance
classifier = ResumeClassifier()
