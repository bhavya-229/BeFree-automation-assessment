"""Hybrid classification engine coordinating rules, ML model, and confidence thresholds."""

import re
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
        ml_min_prob: float = settings.ML_MIN_PROB_THRESHOLD,
        ml_min_margin: float = settings.ML_MIN_MARGIN_RATIO,
    ):
        self.rule_engine = rule_engine or default_rule_engine
        self.ml_classifier = ml_classifier or default_ml_classifier
        self.rule_threshold = rule_threshold
        self.ml_threshold = ml_threshold
        self.ml_min_prob = ml_min_prob
        self.ml_min_margin = ml_min_margin

    def classify_transaction(
        self,
        txn: NormalizedTransaction,
        user_rules: Optional[Dict[str, Tuple[str, Optional[str]]]] = None,
    ) -> NormalizedTransaction:
        """Classify a single transaction obeying the hierarchy: MANUAL -> ACTIVE LEARNING -> RULE -> ML -> UNCLASSIFIED."""
        # 1. Manual user edits on this specific transaction are authoritative and permanent
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

        # 1.5 Active Learning: Layer 0 User Correction Memory
        if user_rules is None:
            try:
                from app.core.storage import statement_store
                user_rules = statement_store.get_user_rules()
            except Exception:
                user_rules = {}

        clean_upper = clean_desc.upper()
        raw_upper = raw_desc.upper()
        matched_user_cat = user_rules.get(clean_upper) or user_rules.get(raw_upper)
        if not matched_user_cat and user_rules:
            for pat, (u_cat, u_subcat) in user_rules.items():
                if pat in clean_upper or pat in raw_upper:
                    matched_user_cat = (u_cat, u_subcat)
                    break

        if matched_user_cat:
            txn.category = matched_user_cat[0]
            txn.subcategory = matched_user_cat[1]
            txn.category_source = ClassificationSource.MANUAL
            txn.category_confidence = 1.0
            txn.rule_id = "USER_LEARNED_RULE"
            return txn

        # 2. Rule Engine check (Layer 1)
        rule_match = self.rule_engine.classify(clean_desc, direction=direction)

        # If a Tier 1 or Tier 2 rule matches with confidence >= 0.85: accept directly
        if rule_match and rule_match[2] >= 0.85:
            cat, subcat, conf, rule_id, tokens = rule_match
            txn.category = cat
            txn.subcategory = subcat
            txn.category_source = ClassificationSource.RULE
            txn.category_confidence = conf
            txn.rule_id = rule_id
            return txn

        # 3. Traditional ML Model check (Layer 2)
        ml_cat, ml_prob, top3 = self.ml_classifier.predict(clean_desc)
        txn.ml_top3 = top3

        # If a Tier 3 generic rule matched (conf < 0.85), corroborate with ML
        if rule_match:
            cat, subcat, conf, rule_id, tokens = rule_match
            # If ML has strong disagreement and much higher confidence, accept ML
            if ml_prob >= 0.85 and ml_cat != cat:
                txn.category = ml_cat
                txn.subcategory = None
                txn.category_source = ClassificationSource.ML
                txn.category_confidence = ml_prob
                return txn
            else:
                # Corroborate rule match
                txn.category = cat
                txn.subcategory = subcat
                txn.category_source = ClassificationSource.RULE
                txn.category_confidence = conf
                txn.rule_id = rule_id
                return txn

        # 4. Corporate Payroll Heuristic for Unlabeled Credits (Evaluated before generic ML)
        if direction == "credit" and txn.credit is not None and txn.credit >= 400.00:
            is_payroll_rail = bool(re.search(r"\b(BACS CR|DIRECT CREDIT|DIR CR|SALARY|PAYROLL|WAGES|REMPAY)\b", clean_desc, re.IGNORECASE))
            is_corporate_entity = bool(re.search(r"\b(PTY LTD|LTD|PLC|LLC|LIMITED|CORP|CORPORATION|INC)\b", clean_desc, re.IGNORECASE))
            is_excluded = any(t in clean_desc for t in ["REFUND", "REBATE", "DIVIDEND", "INTEREST", "TRANSFER FROM SAVINGS", "CASH DEPOSIT"])
            if (is_payroll_rail or is_corporate_entity) and not is_excluded:
                txn.category = "Salary & Wages"
                txn.subcategory = "Regular Pay"
                txn.category_source = ClassificationSource.RULE
                txn.category_confidence = 0.88
                txn.rule_id = "HEURISTIC_PAYROLL"
                return txn

        # 5. Standard ML Model prediction with relative margin arbitration
        margin_ratio = (
            round(top3[0]["probability"] / (top3[1]["probability"] + 1e-5), 2)
            if len(top3) > 1 and top3[1]["probability"] > 0
            else 10.0
        )
        is_confident = (
            ml_prob >= self.ml_threshold
            or (ml_prob >= self.ml_min_prob and margin_ratio >= self.ml_min_margin)
        )
        if is_confident and ml_cat != "Other / Unclassified":
            txn.category = ml_cat
            txn.subcategory = None
            txn.category_source = ClassificationSource.ML
            txn.category_confidence = ml_prob
            return txn

        # 6. Low confidence fallback -> Mark for human review
        txn.category = "Other / Unclassified"
        txn.subcategory = None
        txn.category_source = ClassificationSource.UNCLASSIFIED
        txn.category_confidence = ml_prob
        txn.flags.append("LOW_CONFIDENCE")
        return txn

    def classify_all(
        self, transactions: List[NormalizedTransaction]
    ) -> List[NormalizedTransaction]:
        """Classify a batch of normalized transactions with batch-cached user rules."""
        try:
            from app.core.storage import statement_store
            cached_user_rules = statement_store.get_user_rules()
        except Exception:
            cached_user_rules = {}
        return [self.classify_transaction(t, user_rules=cached_user_rules) for t in transactions]

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
            ml_cat, ml_prob, ml_top3 = self.ml_classifier.predict(clean)
            y_ml_pred.append(ml_cat)

            # 3. Hybrid with relative margin arbitration
            ml_margin = (
                round(ml_top3[0]["probability"] / (ml_top3[1]["probability"] + 1e-5), 2)
                if len(ml_top3) > 1 and ml_top3[1]["probability"] > 0
                else 10.0
            )
            is_ml_confident = (
                ml_prob >= self.ml_threshold
                or (ml_prob >= self.ml_min_prob and ml_margin >= self.ml_min_margin)
            )

            if r_match and r_match[2] >= self.rule_threshold:
                hybrid_cat = r_match[0]
                accepted_without_review += 1
            elif is_ml_confident and ml_cat != "Other / Unclassified":
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
