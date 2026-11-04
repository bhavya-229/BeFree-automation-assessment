"""Mathematical balance validation, auto-repair, and discrepancy explanation."""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.schemas.transaction import NormalizedTransaction


class ReconciliationSummary(BaseModel):
    """Aggregate statement reconciliation metrics."""

    total_transactions: int
    reconciled_count: int
    mismatch_count: int
    quality_score: float = Field(..., description="Reconciliation quality score [0, 100]")
    total_debits: Decimal
    total_credits: Decimal
    net_movement: Decimal
    opening_balance: Optional[Decimal] = None
    closing_balance: Optional[Decimal] = None
    statement_reconciled: bool = False
    discrepancy_explanation: str


def validate_and_reconcile_transactions(
    transactions: List[NormalizedTransaction],
    opening_balance: Optional[Decimal] = None,
    closing_balance: Optional[Decimal] = None,
) -> Tuple[List[NormalizedTransaction], ReconciliationSummary]:
    """Validate running balances, attempt bounded auto-repairs, and calculate reconciliation quality."""
    if not transactions:
        return transactions, ReconciliationSummary(
            total_transactions=0,
            reconciled_count=0,
            mismatch_count=0,
            quality_score=100.0,
            total_debits=Decimal("0.00"),
            total_credits=Decimal("0.00"),
            net_movement=Decimal("0.00"),
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            statement_reconciled=True,
            discrepancy_explanation="No transactions to reconcile.",
        )

    reconciled_count = 0
    mismatch_count = 0
    total_debits = Decimal("0.00")
    total_credits = Decimal("0.00")

    # Track running balance through the ledger chain
    prev_balance: Optional[Decimal] = opening_balance

    for idx, txn in enumerate(transactions):
        # Accumulate totals
        deb = txn.debit or Decimal("0.00")
        cred = txn.credit or Decimal("0.00")
        total_debits += deb
        total_credits += cred

        actual_bal = txn.balance

        if prev_balance is not None and actual_bal is not None:
            expected_bal = prev_balance - deb + cred
            diff = abs(actual_bal - expected_bal)

            if diff <= Decimal("0.01"):
                # Clean mathematical match
                reconciled_count += 1
            else:
                # Discrepancy detected -> Attempt bounded auto-repair hypotheses
                # Hypothesis 1: Debit and Credit columns were inverted
                inverted_bal = prev_balance + deb - cred
                if abs(actual_bal - inverted_bal) <= Decimal("0.01"):
                    # Swapping debit and credit reconciles!
                    txn.debit, txn.credit = txn.credit, txn.debit
                    txn.flags.append("REPAIRED_DIRECTION")
                    reconciled_count += 1
                elif deb == Decimal("0.00") and cred == Decimal("0.00"):
                    # Hypothesis 2: Amount was missing or merged with description
                    delta = prev_balance - actual_bal
                    if delta > Decimal("0.00"):
                        # Inferred Debit
                        txn.debit = delta
                        txn.raw_debit = f"{delta:.2f}"
                        delta_str = f"{delta:.2f}"
                        if txn.description and txn.description.rstrip().endswith(delta_str):
                            txn.description = txn.description.rstrip()[:-len(delta_str)].rstrip()
                        txn.flags.append("INFERRED_AMOUNT")
                        reconciled_count += 1
                    elif delta < Decimal("0.00"):
                        # Inferred Credit
                        cred_delta = abs(delta)
                        txn.credit = cred_delta
                        txn.raw_credit = f"{cred_delta:.2f}"
                        delta_str = f"{cred_delta:.2f}"
                        if txn.description and txn.description.rstrip().endswith(delta_str):
                            txn.description = txn.description.rstrip()[:-len(delta_str)].rstrip()
                        txn.flags.append("INFERRED_AMOUNT")
                        reconciled_count += 1
                    else:
                        mismatch_count += 1
                        txn.flags.append("BALANCE_MISMATCH")
                else:
                    # Hypothesis 3: Balance mismatch remains
                    mismatch_count += 1
                    txn.flags.append("BALANCE_MISMATCH")
                    # If delta is significant, flag possible missing transaction
                    if diff > Decimal("1.00"):
                        txn.flags.append("POSSIBLE_MISSING_ROW")

            # Update running balance to trusted actual balance for next iteration
            prev_balance = actual_bal
        elif actual_bal is not None:
            # First transaction with printed balance establishes chain
            prev_balance = actual_bal
            reconciled_count += 1
        else:
            # Balance column is missing on this row
            if prev_balance is not None:
                # Infer balance from previous balance
                prev_balance = prev_balance - deb + cred

    # Statement-level opening + credits - debits = closing check
    net_movement = total_credits - total_debits
    statement_reconciled = False
    discrepancy_reasons: List[str] = []

    if opening_balance is not None and closing_balance is not None:
        expected_closing = opening_balance + net_movement
        if abs(closing_balance - expected_closing) <= Decimal("0.01"):
            statement_reconciled = True
            discrepancy_reasons.append("Statement opening and closing balances match total net movement.")
        else:
            statement_reconciled = False
            delta = closing_balance - expected_closing
            discrepancy_reasons.append(
                f"Statement closing balance differs from calculated closing by {delta:+.2f}."
            )
    else:
        discrepancy_reasons.append("Opening or closing balance was not provided.")

    # Quality score calculation: 0 - 100
    if len(transactions) > 0:
        base_rate = (reconciled_count / len(transactions)) * 100.0
        quality_score = round(max(0.0, min(100.0, base_rate)), 2)
    else:
        quality_score = 100.0

    summary = ReconciliationSummary(
        total_transactions=len(transactions),
        reconciled_count=reconciled_count,
        mismatch_count=mismatch_count,
        quality_score=quality_score,
        total_debits=total_debits,
        total_credits=total_credits,
        net_movement=net_movement,
        opening_balance=opening_balance,
        closing_balance=closing_balance,
        statement_reconciled=statement_reconciled,
        discrepancy_explanation=" ".join(discrepancy_reasons),
    )

    return transactions, summary
