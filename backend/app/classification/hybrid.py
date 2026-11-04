"""Hybrid classification engine coordinating rules, ML model, and confidence thresholds."""

from typing import Any, Dict, List, Optional, Tuple
from sklearn.metrics import accuracy_score, f1_score

from app.schemas.transaction import NormalizedTransaction, ClassificationSource
from app.classification.normalize import clean_description
from app.classification.rules_engine import default_rule_engine, RuleEngine
from app.classification.ml.model import default_ml_classifier, MLClassifier
from app.config import settings


class HybridClassifier:
    """Hybrid transaction classifier orchestrating deterministic rules and ML model."""

    def __init__(
        self,
        rule_engine: Optional[RuleEngine] = None,
        ml_classifier: Optional[MLClassifier] = None,
        rule_threshold: float = settings.RULE_CONF_THRESHOLD,
        ml_threshold: float = settings.ML_CONF_THRESHOLD,
    ):
        self.rule_engine = rule_engine or default_rule_engine
        self.ml_classifier = ml_classifier or default_ml_classifier
        self.rule_threshold = rule_threshold
        self.ml_threshold = ml_threshold

    def classify_transaction(self, txn: NormalizedTransaction) -> NormalizedTransaction:
        """Classify a single transaction obeying the hierarchy: MANUAL -> RULE -> ML -> UNCLASSIFIED."""
        # 1. Manual user edits are authoritative and permanent
        if txn.user_edited and txn.category_source == ClassificationSource.MANUAL:
            return txn

        raw_desc = txn.description_raw or txn.description
        clean_desc, channel, ref = clean_description(raw_desc)
        txn.description = clean_desc
        if channel and not txn.channel:
            txn.channel = channel
        if ref and not txn.ref_no:
            txn.ref_no = ref

        # Determine transaction direction
        direction = "debit" if txn.debit is not None and txn.debit > 0 else (
            "credit" if txn.credit is not None and txn.credit > 0 else "both"
        )

        # 2. Rule Engine check (Layer 1)
        rule_match = self.rule_engine.classify(clean_desc, direction=direction)
        if rule_match:
            cat, subcat, conf, rule_id, tokens = rule_match
            if conf >= self.rule_threshold:
                txn.category = cat
                txn.subcategory = subcat
                txn.category_source = ClassificationSource.RULE
                txn.category_confidence = conf
                txn.rule_id = rule_id
                return txn

        # 3. Traditional ML Model check (Layer 2)
        ml_cat, ml_prob, top3 = self.ml_classifier.predict(clean_desc)
        txn.ml_top3 = top3

        if ml_prob >= self.ml_threshold:
            txn.category = ml_cat
            txn.subcategory = None
            txn.category_source = ClassificationSource.ML
            txn.category_confidence = ml_prob
            return txn

        # 4. Low confidence fallback -> Mark for human review
        txn.category = "Other / Unclassified"
        txn.subcategory = None
        txn.category_source = ClassificationSource.UNCLASSIFIED
        txn.category_confidence = ml_prob
        txn.flags.append("LOW_CONFIDENCE")
        return txn

    def classify_all(
        self, transactions: List[NormalizedTransaction]
    ) -> List[NormalizedTransaction]:
        """Classify a batch of normalized transactions."""
        return [self.classify_transaction(t) for t in transactions]

    def evaluate_on_benchmark(
        self, benchmark_samples: List[Tuple[str, str, str]]
    ) -> Dict[str, Any]:
        """Compare Rule-only, ML-only, and Hybrid approaches on a test dataset."""
        y_true = [s[1] for s in benchmark_samples]
        y_rule_pred: List[str] = []
        y_ml_pred: List[str] = []
        y_hybrid_pred: List[str] = []

        accepted_without_review = 0

        for text, true_cat, direction in benchmark_samples:
            clean, _, _ = clean_description(text)

            # 1. Rule-only
            r_match = self.rule_engine.classify(clean, direction=direction)
            rule_cat = r_match[0] if r_match else "Other / Unclassified"
            y_rule_pred.append(rule_cat)

            # 2. ML-only
            ml_cat, ml_prob, _ = self.ml_classifier.predict(clean)
            y_ml_pred.append(ml_cat)

            # 3. Hybrid
            if r_match and r_match[2] >= self.rule_threshold:
                hybrid_cat = r_match[0]
                accepted_without_review += 1
            elif ml_prob >= self.ml_threshold:
                hybrid_cat = ml_cat
                accepted_without_review += 1
            else:
                hybrid_cat = "Other / Unclassified"

            y_hybrid_pred.append(hybrid_cat)

        total = len(benchmark_samples)
        return {
            "total_samples": total,
            "coverage_at_threshold": round(accepted_without_review / total, 4) if total > 0 else 0.0,
            "rule_only": {
                "accuracy": round(accuracy_score(y_true, y_rule_pred), 4),
                "macro_f1": round(f1_score(y_true, y_rule_pred, average="macro", zero_division=0), 4),
            },
            "ml_only": {
                "accuracy": round(accuracy_score(y_true, y_ml_pred), 4),
                "macro_f1": round(f1_score(y_true, y_ml_pred, average="macro", zero_division=0), 4),
            },
            "hybrid": {
                "accuracy": round(accuracy_score(y_true, y_hybrid_pred), 4),
                "macro_f1": round(f1_score(y_true, y_hybrid_pred, average="macro", zero_division=0), 4),
                "weighted_f1": round(f1_score(y_true, y_hybrid_pred, average="weighted", zero_division=0), 4),
            },
        }


default_hybrid_classifier = HybridClassifier()
