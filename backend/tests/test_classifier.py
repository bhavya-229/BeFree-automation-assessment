"""Tests for deterministic rules, baseline ML model, and hybrid classification."""

from decimal import Decimal
import uuid
import pytest

from app.schemas.transaction import NormalizedTransaction, ClassificationSource
from app.classification.rules_engine import default_rule_engine
from app.classification.ml.model import default_ml_classifier
from app.classification.hybrid import default_hybrid_classifier
from app.classification.ml.seed import HELD_OUT_TEST_SAMPLES


def test_rule_engine_australian_merchants():
    """Verify deterministic rule matching on Australian merchants."""
    # Groceries
    res1 = default_rule_engine.classify("WOOLWORTHS METRO SYDNEY", direction="debit")
    assert res1 is not None
    assert res1[0] == "Groceries"
    assert "WOOLWORTHS" in res1[4]

    # Utilities
    res2 = default_rule_engine.classify("TELSTRA MOBILE BILL DIRECT DEBIT", direction="debit")
    assert res2 is not None
    assert res2[0] == "Utilities & Bills"

    # Hardware
    res3 = default_rule_engine.classify("BUNNINGS WAREHOUSE ALEXANDRIA", direction="debit")
    assert res3 is not None
    assert res3[0] == "Shopping & Retail"


def test_rule_engine_uk_merchants():
    """Verify deterministic rule matching on United Kingdom merchants."""
    # Groceries
    res1 = default_rule_engine.classify("TESCO STORES LONDON", direction="debit")
    assert res1 is not None
    assert res1[0] == "Groceries"

    # Transport
    res2 = default_rule_engine.classify("TRANSPORT FOR LONDON CONTACTLESS", direction="debit")
    assert res2 is not None
    assert res2[0] == "Transport & Travel"

    # Coffee
    res3 = default_rule_engine.classify("PRET A MANGER VICTORIA", direction="debit")
    assert res3 is not None
    assert res3[0] == "Dining & Restaurants"


def test_ml_classifier_predict_proba():
    """Verify that ML model predicts category with confidence and top 3 candidates."""
    cat, prob, top3 = default_ml_classifier.predict("NETFLIX STREAMING SUBSCRIPTION")
    assert cat == "Entertainment & Subscriptions"
    assert prob > 0.50
    assert len(top3) == 3
    assert top3[0]["category"] == "Entertainment & Subscriptions"


def test_hybrid_classification_hierarchy():
    """Verify the hybrid routing hierarchy: Manual > Rule > ML > Review Fallback."""
    # 1. Rule match
    t1 = NormalizedTransaction(
        id=str(uuid.uuid4()),
        line_number=1,
        page_number=1,
        date="2023-10-01",
        date_raw="01/10/2023",
        description_raw="WOOLWORTHS SUPERMARKET",
        description="WOOLWORTHS SUPERMARKET",
        debit=Decimal("85.50"),
    )
    c1 = default_hybrid_classifier.classify_transaction(t1)
    assert c1.category == "Groceries"
    assert c1.category_source == ClassificationSource.RULE
    assert c1.category_confidence >= 0.90

    # 2. Unknown gibberish falls back to unclassified and flags for review
    t2 = NormalizedTransaction(
        id=str(uuid.uuid4()),
        line_number=2,
        page_number=1,
        date="2023-10-02",
        date_raw="02/10/2023",
        description_raw="XYZQWERT98765 MISC UNKNOWN",
        description="XYZQWERT98765 MISC UNKNOWN",
        debit=Decimal("15.00"),
    )
    c2 = default_hybrid_classifier.classify_transaction(t2)
    assert c2.category == "Other / Unclassified"
    assert c2.category_source == ClassificationSource.UNCLASSIFIED
    assert "LOW_CONFIDENCE" in c2.flags

    # 3. Manual user correction is protected from being overwritten
    t3 = NormalizedTransaction(
        id=str(uuid.uuid4()),
        line_number=3,
        page_number=1,
        date="2023-10-03",
        date_raw="03/10/2023",
        description_raw="WOOLWORTHS SUPERMARKET",
        description="WOOLWORTHS SUPERMARKET",
        category="Dining & Restaurants",
        category_source=ClassificationSource.MANUAL,
        category_confidence=1.0,
        user_edited=True,
    )
    c3 = default_hybrid_classifier.classify_transaction(t3)
    # Remains the user's manual correction despite matching the Woolworths rule!
    assert c3.category == "Dining & Restaurants"
    assert c3.category_source == ClassificationSource.MANUAL


def test_classification_benchmark_evaluation():
    """Verify comparative evaluation reporting on the held-out test dataset."""
    metrics = default_hybrid_classifier.evaluate_on_benchmark(HELD_OUT_TEST_SAMPLES)

    assert "total_samples" in metrics
    assert metrics["total_samples"] == len(HELD_OUT_TEST_SAMPLES)
    assert "rule_only" in metrics
    assert "ml_only" in metrics
    assert "hybrid" in metrics
    assert "accuracy" in metrics["hybrid"]
    assert "macro_f1" in metrics["hybrid"]
    assert "coverage_at_threshold" in metrics
