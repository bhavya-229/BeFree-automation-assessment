"""Scikit-learn FeatureUnion (Word + Sub-word Char) Logistic Regression text classifier."""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

from app.classification.ml.seed import TRAINING_SAMPLES


class MLClassifier:
    """Explainable Word + Sub-word Character N-Gram FeatureUnion + Logistic Regression classifier."""

    def __init__(self):
        features = FeatureUnion([
            ("word", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1, token_pattern=r"(?u)\b\w+\b")),
            ("char_wb", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=1)),
        ])
        self.pipeline = Pipeline([
            ("features", features),
            ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, C=10.0, solver="lbfgs")),
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

        # Calculate relative margin ratio over runner-up
        runner_up_prob = float(probs[top_indices[1]]) if len(top_indices) > 1 else 0.0
        margin_ratio = round(float(probs[best_idx] / (runner_up_prob + 1e-5)), 2)

        top3 = [
            {
                "category": str(classes[idx]),
                "probability": round(float(probs[idx]), 4),
                "margin_ratio": margin_ratio if i == 0 else None,
            }
            for i, idx in enumerate(top_indices)
        ]

        return best_category, best_prob, top3


default_ml_classifier = MLClassifier()
