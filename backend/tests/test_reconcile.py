"""Tests for running balance reconciliation, auto-repair, and discrepancy explanation."""

from decimal import Decimal
import uuid
import pytest

from app.schemas.transaction import NormalizedTransaction
from app.pipeline.validate.reconcile import validate_and_reconcile_transactions


def test_reconcile_clean_transaction_chain():
    """Verify that a mathematically consistent transaction chain achieves 100% reconciliation."""
    txns = [
        NormalizedTransaction(
            id=str(uuid.uuid4()),
            line_number=1,
            page_number=1,
            date="2023-10-03",
            date_raw="03/10/2023",
            description="WOOLWORTHS SYDNEY",
            description_raw="WOOLWORTHS SYDNEY",
            debit=Decimal("85.50"),
            credit=None,
            balance=Decimal("1414.50"),
        ),
        NormalizedTransaction(
            id=str(uuid.uuid4()),
            line_number=2,
            page_number=1,
            date="2023-10-05",
            date_raw="05/10/2023",
            description="SALARY DIRECT CREDIT",
            description_raw="SALARY DIRECT CREDIT",
            debit=None,
            credit=Decimal("3200.00"),
            balance=Decimal("4614.50"),
        ),
        NormalizedTransaction(
            id=str(uuid.uuid4()),
            line_number=3,
            page_number=1,
            date="2023-10-08",
            date_raw="08/10/2023",
            description="TELSTRA BILL PAYMENT",
            description_raw="TELSTRA BILL PAYMENT",
            debit=Decimal("120.00"),
            credit=None,
            balance=Decimal("4494.50"),
        ),
    ]

    opening = Decimal("1500.00")
    closing = Decimal("4494.50")

    reconciled_txns, summary = validate_and_reconcile_transactions(
        txns, opening_balance=opening, closing_balance=closing
    )

    assert summary.total_transactions == 3
    assert summary.reconciled_count == 3
    assert summary.mismatch_count == 0
    assert summary.quality_score == 100.0
    assert summary.statement_reconciled is True
    assert summary.net_movement == Decimal("2994.50")


def test_reconcile_detects_balance_mismatch_without_fabricating():
    """Verify that an intentional balance discrepancy is flagged and never silently altered."""
    txns = [
        NormalizedTransaction(
            id=str(uuid.uuid4()),
            line_number=1,
            page_number=1,
            date="2023-10-03",
            date_raw="03/10/2023",
            description="WOOLWORTHS SYDNEY",
            description_raw="WOOLWORTHS SYDNEY",
            debit=Decimal("85.50"),
            credit=None,
            balance=Decimal("1414.50"),
        ),
        # Corrupted balance on row 2 (e.g. 4000.00 instead of 4614.50)
        NormalizedTransaction(
            id=str(uuid.uuid4()),
            line_number=2,
            page_number=1,
            date="2023-10-05",
            date_raw="05/10/2023",
            description="SALARY DIRECT CREDIT",
            description_raw="SALARY DIRECT CREDIT",
            debit=None,
            credit=Decimal("3200.00"),
            balance=Decimal("4000.00"),
        ),
    ]

    opening = Decimal("1500.00")
    reconciled_txns, summary = validate_and_reconcile_transactions(txns, opening_balance=opening)

    assert summary.mismatch_count == 1
    assert "BALANCE_MISMATCH" in reconciled_txns[1].flags
    assert "POSSIBLE_MISSING_ROW" in reconciled_txns[1].flags
    # Crucial rule: Balance value must NOT be fabricated or changed
    assert reconciled_txns[1].balance == Decimal("4000.00")


def test_reconcile_auto_repairs_swapped_direction():
    """Verify that inverted debit and credit columns are auto-repaired and flagged."""
    # Transaction printed as debit=50.00 but balance went UP by 50.00
    txns = [
        NormalizedTransaction(
            id=str(uuid.uuid4()),
            line_number=1,
            page_number=1,
            date="2023-10-01",
            date_raw="01/10/2023",
            description="REFUND FROM MERCHANT",
            description_raw="REFUND FROM MERCHANT",
            debit=Decimal("50.00"),  # Mistakenly placed in debit
            credit=None,
            balance=Decimal("1050.00"),  # Increased from 1000.00
        )
    ]

    opening = Decimal("1000.00")
    reconciled_txns, summary = validate_and_reconcile_transactions(txns, opening_balance=opening)

    # Direction should be repaired: debit -> credit
    assert reconciled_txns[0].credit == Decimal("50.00")
    assert reconciled_txns[0].debit is None
    assert "REPAIRED_DIRECTION" in reconciled_txns[0].flags
    assert summary.reconciled_count == 1
