"""Excel (.xlsx) export engine with styled tables and formula defense."""

import io
from decimal import Decimal
from typing import List, Optional
import xlsxwriter

from app.schemas.transaction import NormalizedTransaction
from app.export.csv_exporter import sanitize_formula_injection


def export_transactions_to_xlsx(
    transactions: List[NormalizedTransaction],
    bank_name: str = "Bank Statement",
    account_number: Optional[str] = None,
    quality_score: float = 100.0,
) -> bytes:
    """Generate multi-sheet Excel file containing reviewed transactions and statement summary."""
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})

    # Formats
    header_fmt = workbook.add_format({
        "bold": True,
        "bg_color": "#2E2C8F",
        "font_color": "#FFFFFF",
        "border": 1,
        "valign": "vcenter",
    })
    cell_fmt = workbook.add_format({"border": 1, "valign": "vcenter"})
    date_fmt = workbook.add_format({"border": 1, "num_format": "yyyy-mm-dd", "align": "center"})
    amount_fmt = workbook.add_format({"border": 1, "num_format": "#,##0.00", "align": "right"})
    warning_fmt = workbook.add_format({
        "border": 1,
        "bg_color": "#FEF3F2",
        "font_color": "#B42318",
        "valign": "vcenter",
    })

    # --- Sheet 1: Transactions ---
    ws = workbook.add_worksheet("Transactions")
    ws.freeze_panes(1, 0)

    headers = [
        ("Date", 12),
        ("Description", 35),
        ("Reference", 15),
        ("Debit", 14),
        ("Credit", 14),
        ("Balance", 14),
        ("Category", 22),
        ("Subcategory", 18),
        ("Source", 12),
        ("Confidence", 12),
        ("Flags", 20),
    ]

    for col_idx, (h_title, col_width) in enumerate(headers):
        ws.write(0, col_idx, h_title, header_fmt)
        ws.set_column(col_idx, col_idx, col_width)

    for row_idx, txn in enumerate(transactions, start=1):
        has_warning = bool(txn.flags)
        base_style = warning_fmt if has_warning else cell_fmt

        source_val = (
            txn.category_source.value
            if hasattr(txn.category_source, "value")
            else str(txn.category_source)
        )

        ws.write(row_idx, 0, sanitize_formula_injection(txn.date or txn.date_raw), date_fmt)
        ws.write(row_idx, 1, sanitize_formula_injection(txn.description), base_style)
        ws.write(row_idx, 2, sanitize_formula_injection(txn.ref_no or ""), base_style)
        if txn.debit is not None:
            ws.write_number(row_idx, 3, float(txn.debit), amount_fmt)
        else:
            ws.write_blank(row_idx, 3, None, cell_fmt)
        if txn.credit is not None:
            ws.write_number(row_idx, 4, float(txn.credit), amount_fmt)
        else:
            ws.write_blank(row_idx, 4, None, cell_fmt)
        if txn.balance is not None:
            ws.write_number(row_idx, 5, float(txn.balance), amount_fmt)
        else:
            ws.write_blank(row_idx, 5, None, cell_fmt)

        ws.write(row_idx, 6, sanitize_formula_injection(txn.category), base_style)
        ws.write(row_idx, 7, sanitize_formula_injection(txn.subcategory or ""), base_style)
        ws.write(row_idx, 8, source_val, base_style)
        ws.write(row_idx, 9, round(txn.category_confidence, 2), base_style)
        ws.write(row_idx, 10, sanitize_formula_injection("; ".join(txn.flags)), base_style)

    # --- Sheet 2: Statement Summary ---
    ws_summary = workbook.add_worksheet("Summary")
    ws_summary.set_column(0, 0, 25)
    ws_summary.set_column(1, 1, 20)

    summary_headers = [("Statement Metric", 25), ("Value", 20)]
    for c_idx, (st, sw) in enumerate(summary_headers):
        ws_summary.write(0, c_idx, st, header_fmt)

    tot_deb = sum((t.debit for t in transactions if t.debit is not None), Decimal("0.00"))
    tot_cred = sum((t.credit for t in transactions if t.credit is not None), Decimal("0.00"))

    summary_rows = [
        ("Bank Name", sanitize_formula_injection(bank_name)),
        ("Account Number", sanitize_formula_injection(account_number or "N/A")),
        ("Total Transactions", len(transactions)),
        ("Quality Score", f"{quality_score:.1f}%"),
        ("Total Debits", float(tot_deb)),
        ("Total Credits", float(tot_cred)),
        ("Net Movement", float(tot_cred - tot_deb)),
    ]

    for s_idx, (label, val) in enumerate(summary_rows, start=1):
        ws_summary.write(s_idx, 0, label, cell_fmt)
        if isinstance(val, float):
            ws_summary.write_number(s_idx, 1, val, amount_fmt)
        else:
            ws_summary.write(s_idx, 1, val, cell_fmt)

    workbook.close()
    return output.getvalue()
