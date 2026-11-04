"""Reconstruction of transaction rows and multiline narrations from text lines."""

import re
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.pipeline.layout.words import TextLine, Word
from app.pipeline.layout.table_detector import ColumnBoundary, ColumnType, DetectedHeader


class RawTransactionRow(BaseModel):
    """Extracted raw transaction row with provenance."""

    line_number: int
    page_number: int
    date_raw: str
    value_date_raw: Optional[str] = None
    description_raw: str
    ref_raw: Optional[str] = None
    debit_raw: Optional[str] = None
    credit_raw: Optional[str] = None
    amount_raw: Optional[str] = None
    balance_raw: Optional[str] = None
    confidence: float = 100.0
    bounding_box: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)


# Regular expressions for common bank date tokens
DATE_PATTERNS = [
    re.compile(r"^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$"),  # 01/10/2023, 01-10-23
    re.compile(r"^\d{4}[/-]\d{2}[/-]\d{2}$"),        # 2023-10-01
    re.compile(
        r"^\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*(\s+\d{2,4})?$",
        re.IGNORECASE,
    ),  # 12 Oct 2023 or 12 Oct
]

# Patterns for line terminators and summary rows
TERMINATOR_PATTERNS = [
    re.compile(r"^closing balance", re.IGNORECASE),
    re.compile(r"^statement summary", re.IGNORECASE),
    re.compile(r"^page \d+ of \d+", re.IGNORECASE),
    re.compile(r"^totals?", re.IGNORECASE),
]

# Opening balance patterns that represent starting balance rather than a transaction
OPENING_BALANCE_PATTERNS = [
    re.compile(r"opening balance", re.IGNORECASE),
    re.compile(r"brought forward", re.IGNORECASE),
    re.compile(r"balance brought forward", re.IGNORECASE),
    re.compile(r"^b/fwd?", re.IGNORECASE),
]


def looks_like_date(text: str) -> bool:
    """Check if token string looks like a transaction date."""
    clean = text.strip()
    return any(p.match(clean) for p in DATE_PATTERNS)


def looks_like_amount(text: str) -> bool:
    """Check if token looks like a currency amount (must contain digits and decimal/currency marker)."""
    clean = re.sub(r"[£$€,]", "", text.strip()).rstrip("drDRcrCR+-()")
    if not clean:
        return False
    # Must contain at least one digit and a decimal point or currency indicator
    if not any(c.isdigit() for c in clean):
        return False
    if "." not in clean and "," not in text:
        return False
    try:
        float(clean)
        return True
    except ValueError:
        return False


def is_opening_balance_row(desc: str) -> bool:
    """Check if row description signifies an opening balance rather than a transaction."""
    return any(p.search(desc) for p in OPENING_BALANCE_PATTERNS)


def assign_words_to_columns(
    words: List[Word], columns: List[ColumnBoundary]
) -> Dict[ColumnType, List[Word]]:
    """Assign words in a line to their closest column boundary based on horizontal position."""
    assigned: Dict[ColumnType, List[Word]] = {col.col_type: [] for col in columns}
    if not columns or not words:
        return assigned

    sorted_cols = sorted(columns, key=lambda c: c.x_center)
    split_points: List[float] = []
    for i in range(len(sorted_cols) - 1):
        mid = (sorted_cols[i].x_center + sorted_cols[i + 1].x_center) / 2.0
        split_points.append(mid)

    # Disentangle tokens where narration and amount were merged due to zero gap (e.g. PICCADILLY18.30)
    expanded_words: List[Word] = []
    for word in words:
        m = re.match(r"^([A-Za-z]+)(\d+\.\d{2})$", word.text)
        if m:
            text_part, num_part = m.group(1), m.group(2)
            total_len = len(word.text)
            split_ratio = len(text_part) / total_len
            split_x = word.x0 + (word.x1 - word.x0) * split_ratio
            w1 = Word(
                page_number=word.page_number,
                text=text_part,
                x0=word.x0,
                y0=word.y0,
                x1=split_x,
                y1=word.y1,
                confidence=word.confidence,
                source=word.source,
            )
            w2 = Word(
                page_number=word.page_number,
                text=num_part,
                x0=split_x,
                y0=word.y0,
                x1=word.x1,
                y1=word.y1,
                confidence=word.confidence,
                source=word.source,
            )
            expanded_words.extend([w1, w2])
        else:
            expanded_words.append(word)

    for word in expanded_words:
        wx = word.x_center
        col_idx = 0
        while col_idx < len(split_points) and wx > split_points[col_idx]:
            col_idx += 1
        target_col = sorted_cols[col_idx]
        assigned[target_col.col_type].append(word)

    return assigned


def reconstruct_transaction_rows(
    lines: List[TextLine], header: DetectedHeader
) -> List[RawTransactionRow]:
    """Reconstruct transaction rows and multiline continuations using header boundary intervals."""
    rows: List[RawTransactionRow] = []
    current_row: Optional[RawTransactionRow] = None

    # Determine left edge of amount columns
    amount_col_types = {ColumnType.DEBIT, ColumnType.CREDIT, ColumnType.AMOUNT, ColumnType.BALANCE}
    amount_cols = [c for c in header.columns if c.col_type in amount_col_types]
    min_amount_x = min((c.x0 for c in amount_cols), default=0.5)

    # Lines starting after the header line
    body_lines = [l for l in lines if l.page_number > header.page_number or l.y0 > header.header_y1]

    for line_idx, line in enumerate(body_lines, start=1):
        line_text = line.text.strip()
        if any(term.match(line_text) for term in TERMINATOR_PATTERNS):
            continue

        assigned = assign_words_to_columns(line.words, header.columns)
        date_words = assigned.get(ColumnType.DATE, [])
        date_str = " ".join(w.text for w in date_words).strip()

        first_word_text = line.words[0].text if line.words else ""
        first_two_words = f"{line.words[0].text} {line.words[1].text}" if len(line.words) > 1 else ""
        starts_with_date = (
            looks_like_date(date_str)
            or looks_like_date(first_word_text)
            or looks_like_date(first_two_words)
        )

        if starts_with_date:
            # Commit previously active row if it was not an opening balance metadata row
            if current_row:
                if not is_opening_balance_row(current_row.description_raw):
                    rows.append(current_row)

            matched_date = (
                date_str
                if looks_like_date(date_str)
                else (first_word_text if looks_like_date(first_word_text) else first_two_words)
            )

            # Separate words into amounts vs narrative text
            desc_tokens: List[str] = []
            ref_tokens: List[str] = []
            debit_tokens: List[str] = []
            credit_tokens: List[str] = []
            amount_tokens: List[str] = []
            balance_tokens: List[str] = []

            for col_type, col_words in assigned.items():
                for w in col_words:
                    if w.text == matched_date or (matched_date.startswith(w.text) and w in date_words):
                        continue

                    if col_type == ColumnType.DESCRIPTION:
                        desc_tokens.append(w.text)
                    elif col_type == ColumnType.REFERENCE:
                        ref_tokens.append(w.text)
                    elif col_type == ColumnType.DEBIT:
                        if looks_like_amount(w.text):
                            debit_tokens.append(w.text)
                        else:
                            desc_tokens.append(w.text)
                    elif col_type == ColumnType.CREDIT:
                        if looks_like_amount(w.text):
                            credit_tokens.append(w.text)
                        else:
                            desc_tokens.append(w.text)
                    elif col_type == ColumnType.AMOUNT:
                        if looks_like_amount(w.text):
                            amount_tokens.append(w.text)
                        else:
                            desc_tokens.append(w.text)
                    elif col_type == ColumnType.BALANCE:
                        if looks_like_amount(w.text):
                            balance_tokens.append(w.text)
                        else:
                            desc_tokens.append(w.text)
                    elif col_type == ColumnType.DATE:
                        desc_tokens.append(w.text)

            desc_str = " ".join(desc_tokens).strip()
            bbox = (line.x0, line.y0, line.x1, line.y1)

            current_row = RawTransactionRow(
                line_number=line_idx,
                page_number=line.page_number,
                date_raw=matched_date,
                description_raw=desc_str,
                ref_raw=" ".join(ref_tokens).strip() or None,
                debit_raw=" ".join(debit_tokens).strip() or None,
                credit_raw=" ".join(credit_tokens).strip() or None,
                amount_raw=" ".join(amount_tokens).strip() or None,
                balance_raw=" ".join(balance_tokens).strip() or None,
                confidence=min(w.confidence for w in line.words) if line.words else 100.0,
                bounding_box=bbox,
            )
        else:
            # Continuation line
            if current_row:
                desc_line_tokens: List[str] = []
                for w in line.words:
                    if w.x0 < min_amount_x:
                        # Left side of table -> unconditionally description
                        desc_line_tokens.append(w.text)
                    elif looks_like_amount(w.text):
                        # Right side of table with decimal amount -> orphan amount
                        if not current_row.debit_raw and not current_row.credit_raw:
                            current_row.amount_raw = w.text
                        elif not current_row.balance_raw:
                            current_row.balance_raw = w.text
                    else:
                        desc_line_tokens.append(w.text)

                continuation_text = " ".join(desc_line_tokens).strip()
                if continuation_text:
                    current_row.description_raw += f" {continuation_text}"

                current_row.bounding_box = (
                    min(current_row.bounding_box[0], line.x0),
                    current_row.bounding_box[1],
                    max(current_row.bounding_box[2], line.x1),
                    max(current_row.bounding_box[3], line.y1),
                )

    if current_row:
        if not is_opening_balance_row(current_row.description_raw):
            rows.append(current_row)

    return rows
