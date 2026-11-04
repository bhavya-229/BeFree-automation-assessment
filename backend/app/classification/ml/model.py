"""Scikit-learn TF-IDF Logistic Regression text classifier."""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.classification.ml.seed import TRAINING_SAMPLES


class MLClassifier:
    """Explainable TF-IDF + Logistic Regression baseline text classifier."""

    def __init__(self):
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)),
            ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, C=10.0)),
        ])
        self.is_fitted = False
        self._fit_initial_model()

    def _fit_initial_model(self) -> None:
        """Fit baseline model using synthetic seed dataset."""
        texts = [sample[0] for sample in TRAINING_SAMPLES]
        labels = [sample[1] for sample in TRAINING_SAMPLES]
        self.pipeline.fit(texts, labels)
        self.is_fitted = True

    def predict(
        self, description: str
    ) -> Tuple[str, float, List[Dict[str, Any]]]:
        """Predict category, probability confidence, and top-3 ranked candidate categories."""
        if not self.is_fitted or not description.strip():
            return "Other / Unclassified", 0.0, []

        clf: LogisticRegression = self.pipeline.named_steps["clf"]
        classes = clf.classes_

        # Get probability vector
        probs = self.pipeline.predict_proba([description])[0]
        top_indices = np.argsort(probs)[::-1][:3]

        best_idx = top_indices[0]
        best_category = str(classes[best_idx])
        best_prob = round(float(probs[best_idx]), 4)

        top3 = [
            {"category": str(classes[idx]), "probability": round(float(probs[idx]), 4)}
            for idx in top_indices
        ]

        return best_category, best_prob, top3


default_ml_classifier = MLClassifier()
