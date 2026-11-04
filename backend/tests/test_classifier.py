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


def test_adversarial_precision_and_negative_matching():
    """Verify substring collisions, negative keyword exclusions, processor routing, and specificity arbitration."""
    # 1. Substring Collision Defense
    # CURRENT ACCOUNT must not trigger RENT
    t_rent_neg = NormalizedTransaction(
        id="t1", line_number=1, page_number=1, date="2026-08-01", date_raw="01/08/2026",
        description="CURRENT ACCOUNT MONTHLY FEE", description_raw="CURRENT ACCOUNT MONTHLY FEE", debit=Decimal("10.00")
    )
    c_rent_neg = default_hybrid_classifier.classify_transaction(t_rent_neg)
    assert c_rent_neg.category != "Rent & Housing"
    assert c_rent_neg.category == "Fees & Charges"

    # OPTUS MOBILE must not trigger MOBIL fuel rule
    t_fuel_neg = NormalizedTransaction(
        id="t2", line_number=2, page_number=1, date="2026-08-01", date_raw="01/08/2026",
        description="OPTUS MOBILE BROADBAND DIRECT DEBIT", description_raw="OPTUS MOBILE BROADBAND DIRECT DEBIT", debit=Decimal("79.00")
    )
    c_fuel_neg = default_hybrid_classifier.classify_transaction(t_fuel_neg)
    assert c_fuel_neg.category == "Utilities & Bills"

    # COLA must not trigger OLA rideshare
    t_ola_neg = NormalizedTransaction(
        id="t3", line_number=3, page_number=1, date="2026-08-01", date_raw="01/08/2026",
        description="COLA BEVERAGE PURCHASE", description_raw="COLA BEVERAGE PURCHASE", debit=Decimal("4.50")
    )
    c_ola_neg = default_hybrid_classifier.classify_transaction(t_ola_neg)
    assert c_ola_neg.category != "Transport & Travel"

    # 2. Specificity and Processor Gateway Routing
    # PAYPAL * STEAM GAMES should strip PAYPAL and route to Entertainment via STEAM
    t_paypal = NormalizedTransaction(
        id="t4", line_number=4, page_number=1, date="2026-08-01", date_raw="01/08/2026",
        description="PAYPAL * STEAM GAMES ONLINE", description_raw="PAYPAL * STEAM GAMES ONLINE", debit=Decimal("29.99")
    )
    c_paypal = default_hybrid_classifier.classify_transaction(t_paypal)
    assert c_paypal.channel == "PAYPAL"
    assert c_paypal.category == "Entertainment & Subscriptions"

    # TRANSFER TO LANDLORD should match LANDLORD (Rent) over TRANSFER TO (Transfers Out)
    t_landlord = NormalizedTransaction(
        id="t5", line_number=5, page_number=1, date="2026-08-01", date_raw="01/08/2026",
        description="TRANSFER TO LANDLORD RENT AUGUST", description_raw="TRANSFER TO LANDLORD RENT AUGUST", debit=Decimal("650.00")
    )
    c_landlord = default_hybrid_classifier.classify_transaction(t_landlord)
    assert c_landlord.category == "Rent & Housing"

    # ANZ MORTGAGE PAYMENT should route to Loan & Credit Payments, not Rent
    t_mortgage = NormalizedTransaction(
        id="t6", line_number=6, page_number=1, date="2026-08-01", date_raw="01/08/2026",
        description="ANZ MORTGAGE REPAYMENT HOME LOAN", description_raw="ANZ MORTGAGE REPAYMENT HOME LOAN", debit=Decimal("1850.00")
    )
    c_mortgage = default_hybrid_classifier.classify_transaction(t_mortgage)
    assert c_mortgage.category == "Loan & Credit Payments"

    # APPLE.COM/BILL should route to Entertainment & Subscriptions
    t_apple = NormalizedTransaction(
        id="t7", line_number=7, page_number=1, date="2026-08-01", date_raw="01/08/2026",
        description="APPLE.COM/BILL DIGITAL MEDIA", description_raw="APPLE.COM/BILL DIGITAL MEDIA", debit=Decimal("14.99")
    )
    c_apple = default_hybrid_classifier.classify_transaction(t_apple)
    assert c_apple.category == "Entertainment & Subscriptions"

    # AMAZON PRIME should route to Entertainment & Subscriptions
    t_prime = NormalizedTransaction(
        id="t8", line_number=8, page_number=1, date="2026-08-01", date_raw="01/08/2026",
        description="AMAZON PRIME SUBSCRIPTION", description_raw="AMAZON PRIME SUBSCRIPTION", debit=Decimal("9.99")
    )
    c_prime = default_hybrid_classifier.classify_transaction(t_prime)
    assert c_prime.category == "Entertainment & Subscriptions"

    # 3. New Taxonomy Categories
    # Taxes
    t_tax = NormalizedTransaction(
        id="t9", line_number=9, page_number=1, date="2026-08-01", date_raw="01/08/2026",
        description="ATO TAX PAYMENT 2026", description_raw="ATO TAX PAYMENT 2026", debit=Decimal("450.00")
    )
    c_tax = default_hybrid_classifier.classify_transaction(t_tax)
    assert c_tax.category == "Taxes & Government"

    # Education
    t_edu = NormalizedTransaction(
        id="t10", line_number=10, page_number=1, date="2026-08-01", date_raw="01/08/2026",
        description="SYDNEY UNIVERSITY TUITION FEES", description_raw="SYDNEY UNIVERSITY TUITION FEES", debit=Decimal("1200.00")
    )
    c_edu = default_hybrid_classifier.classify_transaction(t_edu)
    assert c_edu.category == "Education & Childcare"

    # Donations
    t_don = NormalizedTransaction(
        id="t11", line_number=11, page_number=1, date="2026-08-01", date_raw="01/08/2026",
        description="RED CROSS AUSTRALIA DONATION", description_raw="RED CROSS AUSTRALIA DONATION", debit=Decimal("50.00")
    )
    c_don = default_hybrid_classifier.classify_transaction(t_don)
    assert c_don.category == "Donations & Charity"

    # Investments
    t_inv = NormalizedTransaction(
        id="t12", line_number=12, page_number=1, date="2026-08-01", date_raw="01/08/2026",
        description="VANGUARD DIVERSIFIED ETF", description_raw="VANGUARD DIVERSIFIED ETF", debit=Decimal("500.00")
    )
    c_inv = default_hybrid_classifier.classify_transaction(t_inv)
    assert c_inv.category == "Investments & Wealth"

    # 4. Corporate Payroll Heuristic (no literal word 'salary' in narrative)
    t_corp = NormalizedTransaction(
        id="t13", line_number=13, page_number=1, date="2026-08-01", date_raw="01/08/2026",
        description="CANVA PTY LTD DIRECT CREDIT", description_raw="CANVA PTY LTD DIRECT CREDIT", credit=Decimal("3450.00")
    )
    c_corp = default_hybrid_classifier.classify_transaction(t_corp)
    assert c_corp.category == "Salary & Wages"
    assert c_corp.rule_id == "HEURISTIC_PAYROLL"


def test_active_learning_user_rule_memory():
    """Verify that user-learned rules are persisted and take top priority (Layer 0)."""
    from app.core.storage import statement_store

    # 1. Register a custom vendor in user rules
    pattern = "XYZ TECH ADVISORY"
    expected_category = "Professional & Legal Services"
    statement_store.learn_user_rule(pattern=pattern, category=expected_category)

    # 2. Classify a new transaction matching this pattern
    t = NormalizedTransaction(
        id="t_user_learned",
        line_number=1,
        page_number=1,
        date="2026-08-06",
        date_raw="06-08-2026",
        description="UPI/999999999999/DR/XYZ TECH ADVISORY/MUMBAI/NO REM",
        description_raw="UPI/999999999999/DR/XYZ TECH ADVISORY/MUMBAI/NO REM",
        debit=Decimal("1500.00"),
    )
    classified = default_hybrid_classifier.classify_transaction(t)

    assert classified.category == expected_category
    assert classified.category_source == ClassificationSource.MANUAL
    assert classified.category_confidence == 1.0
    assert classified.rule_id == "USER_LEARNED_RULE"


def test_lru_and_deterministic_rule_caching():
    """Verify that description normalization and rule classification are cached for high throughput."""
    from app.classification.normalize import clean_description

    clean_description.cache_clear()
    raw = "UPI/621848103425/DR/Amazon/RATN/amazonpay/Reques"
    res1, ch1, ref1 = clean_description(raw)
    res2, ch2, ref2 = clean_description(raw)

    assert res1 == res2
    assert clean_description.cache_info().hits >= 1

    # Verify RuleEngine cache
    cache_key = ("AMAZON", "debit")
    rule_res1 = default_rule_engine.classify("AMAZON", direction="debit")
    assert cache_key in default_rule_engine._classification_cache
    rule_res2 = default_rule_engine.classify("AMAZON", direction="debit")
    assert rule_res1 == rule_res2


def test_real_world_upi_bank_statement_records():
    """Verify classification of real-world Indian bank statement records."""
    records = [
        ("UPI/621848103425/DR/Amazon/RATN/amazonpay/Reques", Decimal("1000.00"), None, "Shopping & Retail"),
        ("UPI/621859612800/DR/Flipka/YESB/flipkart./OD3382", Decimal("426.00"), None, "Shopping & Retail"),
        ("UPI/622163379669/DR/Meesho/YESB/paytm-177/UPI In", Decimal("188.00"), None, "Shopping & Retail"),
        ("UPI/622100783538/CR/Meesho/YESB/paytm-177/expres", None, Decimal("188.00"), "Refunds & Cashbacks"),
        ("NACH DR INW - TP ACH NIPPON IND MF 3170507420 RA", Decimal("2000.00"), None, "Investments & Wealth"),
        ("UPI/622330342177/CR/Flipka/YESB/flipkart./Refund", None, Decimal("426.00"), "Refunds & Cashbacks"),
        ("UPI/623736640172/DR/PHARME/HDFC/pharmeasy/Sent u", Decimal("480.37"), None, "Healthcare & Pharmacy"),
        ("UPI/192425475385/DR/BHIM/ICIC/bhimrecha/NO REM", Decimal("2249.00"), None, "Utilities & Bills"),
        ("UPI/103809560173/CR/NPCIB/HDFC/bhimcashb/BHIMCA", None, Decimal("3.00"), "Refunds & Cashbacks"),
        ("UPI/164947239493/DR/Smart /JIOP/241514726/NO REM", Decimal("1440.44"), None, "Utilities & Bills"),
    ]

    for desc, debit, credit, expected_category in records:
        t = NormalizedTransaction(
            id=f"t_upi_{uuid.uuid4().hex[:6]}",
            line_number=1,
            page_number=1,
            date="2026-08-06",
            date_raw="06-08-2026",
            description=desc,
            description_raw=desc,
            debit=debit,
            credit=credit,
        )
        res = default_hybrid_classifier.classify_transaction(t)
        assert res.category == expected_category, f"Failed for '{desc}': got '{res.category}', expected '{expected_category}'"
        assert res.category_confidence >= 0.85


