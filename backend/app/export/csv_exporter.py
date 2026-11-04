"""CSV export engine with formula injection defense and Excel UTF-8 BOM."""

import csv
import io
from typing import List
from app.schemas.transaction import NormalizedTransaction

UNSAFE_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def sanitize_formula_injection(value: str) -> str:
    """Prepend single quote to neutralize formula injection in spreadsheet software."""
    if not value:
        return ""
    val_str = str(value)
    if val_str.startswith(UNSAFE_PREFIXES):
        return f"'{val_str}"
    return val_str


def export_transactions_to_csv(
    transactions: List[NormalizedTransaction],
    date_format: str = "ISO",  # "ISO" (YYYY-MM-DD) or "DAY_FIRST" (DD/MM/YYYY)
    include_bom: bool = True,
) -> bytes:
    """Generate RFC 4180 compliant CSV bytes with formula injection defense."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")

    # Header row
    headers = [
        "Date",
        "Description",
        "Reference",
        "Debit",
        "Credit",
        "Balance",
        "Currency",
        "Category",
        "Subcategory",
        "Category Source",
        "Confidence",
        "Flags",
        "Page",
    ]
    writer.writerow(headers)

    for txn in transactions:
        date_display = txn.date or txn.date_raw
        if date_format == "DAY_FIRST" and txn.date:
            try:
                parts = txn.date.split("-")
                date_display = f"{parts[2]}/{parts[1]}/{parts[0]}"
            except Exception:
                pass

        source_val = (
            txn.category_source.value
            if hasattr(txn.category_source, "value")
            else str(txn.category_source)
        )

        row = [
            sanitize_formula_injection(date_display),
            sanitize_formula_injection(txn.description),
            sanitize_formula_injection(txn.ref_no or ""),
            f"{txn.debit:.2f}" if txn.debit is not None else "",
            f"{txn.credit:.2f}" if txn.credit is not None else "",
            f"{txn.balance:.2f}" if txn.balance is not None else "",
            sanitize_formula_injection(txn.currency or "AUD"),
            sanitize_formula_injection(txn.category),
            sanitize_formula_injection(txn.subcategory or ""),
            source_val,
            f"{txn.category_confidence:.2f}",
            sanitize_formula_injection("; ".join(txn.flags)),
            str(txn.page_number),
        ]
        writer.writerow(row)

    csv_text = buffer.getvalue()
    if include_bom:
        return b"\xef\xbb\xbf" + csv_text.encode("utf-8")
    return csv_text.encode("utf-8")
