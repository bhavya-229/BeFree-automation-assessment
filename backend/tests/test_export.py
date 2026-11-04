"""Tests for CSV and Excel (.xlsx) export engines and formula injection defense."""

import csv
import io
from decimal import Decimal
import uuid
import pytest
import openpyxl

from app.schemas.transaction import NormalizedTransaction, ClassificationSource
from app.export.csv_exporter import export_transactions_to_csv, sanitize_formula_injection
from app.export.xlsx_exporter import export_transactions_to_xlsx


@pytest.fixture
def sample_transactions_for_export() -> list[NormalizedTransaction]:
    """Sample transactions including a formula-injection attack vector."""
    return [
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
            category="Groceries",
            category_source=ClassificationSource.RULE,
            category_confidence=0.98,
        ),
        # Malicious narration testing formula injection defense
        NormalizedTransaction(
            id=str(uuid.uuid4()),
            line_number=2,
            page_number=1,
            date="2023-10-05",
            date_raw="05/10/2023",
            description="=cmd|'/C calc'!A0",
            description_raw="=cmd|'/C calc'!A0",
            debit=None,
            credit=Decimal("500.00"),
            balance=Decimal("1914.50"),
            category="Other / Unclassified",
            category_source=ClassificationSource.UNCLASSIFIED,
            category_confidence=0.10,
            flags=["LOW_CONFIDENCE"],
        ),
    ]


def test_sanitize_formula_injection():
    """Verify that dangerous spreadsheet formula prefixes are neutralized with leading single quote."""
    assert sanitize_formula_injection("=1+1") == "'=1+1"
    assert sanitize_formula_injection("+SUM(A1:A5)") == "'+SUM(A1:A5)"
    assert sanitize_formula_injection("-50.00") == "'-50.00"
    assert sanitize_formula_injection("@IMPORT") == "'@IMPORT"
    assert sanitize_formula_injection("SAFE_TEXT") == "SAFE_TEXT"


def test_export_transactions_to_csv(sample_transactions_for_export):
    """Verify CSV export contains BOM, correct headers, values, and sanitized formulas."""
    csv_bytes = export_transactions_to_csv(sample_transactions_for_export)

    # Check UTF-8 BOM
    assert csv_bytes.startswith(b"\xef\xbb\xbf")

    # Read CSV contents
    content = csv_bytes.decode("utf-8-sig")
    reader = list(csv.reader(io.StringIO(content)))

    assert len(reader) == 3  # Header + 2 rows
    assert reader[0][0] == "Date"
    assert reader[0][1] == "Description"
    assert reader[0][3] == "Debit"
    assert reader[0][4] == "Credit"
    assert reader[0][6] == "Category"

    # Row 1 check
    assert reader[1][0] == "2023-10-03"
    assert reader[1][1] == "WOOLWORTHS SYDNEY"
    assert reader[1][3] == "85.50"
    assert reader[1][6] == "Groceries"

    # Row 2 check (Formula injection neutralized)
    assert reader[2][1] == "'=cmd|'/C calc'!A0"
    assert reader[2][4] == "500.00"


def test_export_transactions_to_xlsx(sample_transactions_for_export):
    """Verify Excel export produces valid workbook with Transactions and Summary sheets."""
    xlsx_bytes = export_transactions_to_xlsx(
        sample_transactions_for_export,
        bank_name="Commonwealth Bank",
        account_number="12345678",
        quality_score=100.0,
    )

    wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))
    sheet_names = wb.sheetnames
    assert "Transactions" in sheet_names
    assert "Summary" in sheet_names

    ws_txns = wb["Transactions"]
    assert ws_txns.cell(row=1, column=1).value == "Date"
    assert ws_txns.cell(row=1, column=2).value == "Description"
    assert ws_txns.cell(row=2, column=2).value == "WOOLWORTHS SYDNEY"

    # Verify numeric debit cell
    debit_val = ws_txns.cell(row=2, column=4).value
    assert float(debit_val) == 85.50

    # Verify formula-neutralized text cell on row 3
    malicious_val = ws_txns.cell(row=3, column=2).value
    assert malicious_val == "'=cmd|'/C calc'!A0"

    # Check Summary sheet
    ws_summary = wb["Summary"]
    assert ws_summary.cell(row=2, column=1).value == "Bank Name"
    assert ws_summary.cell(row=2, column=2).value == "Commonwealth Bank"
