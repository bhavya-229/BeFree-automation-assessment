"""Table header detection and column boundary discovery using fuzzy matching."""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel
from rapidfuzz import fuzz

from app.pipeline.layout.words import TextLine, Word


class ColumnType(str, Enum):
    """Standardized transaction table column types."""

    DATE = "date"
    VALUE_DATE = "value_date"
    DESCRIPTION = "description"
    REFERENCE = "reference"
    DEBIT = "debit"
    CREDIT = "credit"
    AMOUNT = "amount"
    BALANCE = "balance"


# Comprehensive synonym dictionary covering AU, UK, and generic banks
COLUMN_SYNONYMS: Dict[ColumnType, List[str]] = {
    ColumnType.DATE: [
        "date", "txn date", "transaction date", "trans date", "booking date",
        "value date", "post date", "processed date"
    ],
    ColumnType.VALUE_DATE: [
        "value date", "eff date", "effective date"
    ],
    ColumnType.DESCRIPTION: [
        "description", "narration", "particulars", "details", "transaction details",
        "transaction remarks", "payment details", "remarks", "narrative"
    ],
    ColumnType.REFERENCE: [
        "ref", "reference", "ref no", "reference no", "chq / ref no", "chq no",
        "cheque no", "cheque / ref", "instrument no", "cheque number"
    ],
    ColumnType.DEBIT: [
        "debit", "dr", "withdrawal", "withdrawals", "payments", "paid out",
        "money out", "debit amount", "debit ($)", "debit (£)"
    ],
    ColumnType.CREDIT: [
        "credit", "cr", "deposit", "deposits", "receipts", "paid in",
        "money in", "credit amount", "credit ($)", "credit (£)"
    ],
    ColumnType.AMOUNT: [
        "amount", "transaction amount", "amount ($)", "amount (£)", "net amount"
    ],
    ColumnType.BALANCE: [
        "balance", "running balance", "closing balance", "total balance",
        "account balance", "balance ($)", "balance (£)"
    ],
}


class ColumnBoundary(BaseModel):
    """Horizontal boundary interval [x0, x1] for a detected table column."""

    col_type: ColumnType
    header_text: str
    x0: float
    x1: float

    @property
    def x_center(self) -> float:
        return (self.x0 + self.x1) / 2.0


class DetectedHeader(BaseModel):
    """Result of header detection on a page."""

    line_index: int
    page_number: int
    columns: List[ColumnBoundary]
    header_y1: float
    confidence: float


def match_column_type(text: str, score_cutoff: float = 85.0) -> Optional[Tuple[ColumnType, float]]:
    """Match a word or phrase against column synonym dictionaries using RapidFuzz."""
    clean_text = text.lower().strip()
    best_match: Optional[ColumnType] = None
    best_score = 0.0

    for col_type, synonyms in COLUMN_SYNONYMS.items():
        for syn in synonyms:
            # Check exact match or token ratio
            if clean_text == syn:
                return col_type, 100.0
            score = fuzz.token_sort_ratio(clean_text, syn)
            if score > best_score and score >= score_cutoff:
                best_score = score
                best_match = col_type

    if best_match:
        return best_match, best_score
    return None


def detect_table_header(lines: List[TextLine], min_columns: int = 3) -> Optional[DetectedHeader]:
    """Scan lines to find a table header matching at least min_columns synonyms."""
    for idx, line in enumerate(lines):
        matched_columns: List[ColumnBoundary] = []
        words = line.words

        # Check individual words or adjacent 2-word pairs
        i = 0
        while i < len(words):
            w = words[i]
            pair_text = f"{w.text} {words[i+1].text}" if i + 1 < len(words) else ""

            # Check pair first
            pair_match = match_column_type(pair_text) if pair_text else None
            if pair_match:
                col_type, _ = pair_match
                # Avoid duplicate column types
                if not any(c.col_type == col_type for c in matched_columns):
                    w2 = words[i+1]
                    matched_columns.append(
                        ColumnBoundary(
                            col_type=col_type,
                            header_text=pair_text,
                            x0=w.x0,
                            x1=w2.x1,
                        )
                    )
                i += 2
                continue

            single_match = match_column_type(w.text)
            if single_match:
                col_type, _ = single_match
                if not any(c.col_type == col_type for c in matched_columns):
                    matched_columns.append(
                        ColumnBoundary(
                            col_type=col_type,
                            header_text=w.text,
                            x0=w.x0,
                            x1=w.x1,
                        )
                    )
            i += 1

        # Must have at least min_columns (including a Date or Description column)
        has_date_or_desc = any(
            c.col_type in (ColumnType.DATE, ColumnType.DESCRIPTION) for c in matched_columns
        )
        if len(matched_columns) >= min_columns and has_date_or_desc:
            # Sort columns left to right
            matched_columns = sorted(matched_columns, key=lambda c: c.x0)
            return DetectedHeader(
                line_index=idx,
                page_number=line.page_number,
                columns=matched_columns,
                header_y1=line.y1,
                confidence=len(matched_columns) / 5.0,
            )

    return None
