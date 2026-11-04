"""Country-aware date normalization (Australia/UK day-first priority)."""

import re
from datetime import datetime
from typing import List, Optional, Tuple
from dateutil import parser as dateutil_parser


# Common OCR character substitutions in purely numeric date tokens
OCR_NUMERIC_SUBS = {
    "O": "0",
    "o": "0",
    "l": "1",
    "I": "1",
    "i": "1",
    "S": "5",
    "s": "5",
}

# Day-first date formats prominent in Australia and the UK
DAY_FIRST_FORMATS = [
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d.%m.%Y",
    "%d/%m/%y",
    "%d-%m-%y",
    "%d %b %Y",
    "%d %B %Y",
    "%d-%b-%Y",
    "%d-%b-%y",
    "%d %b %y",
    "%d-%B-%Y",
    "%Y-%m-%d",
]

MONTH_NAMES_PATTERN = re.compile(
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", re.IGNORECASE
)


def clean_date_token(token: str) -> Tuple[str, bool]:
    """Clean date string and repair common OCR character confusions in numeric date parts."""
    cleaned = token.strip()
    repaired = False

    # Do not substitute letters inside words if token already contains a standard month name
    has_month_word = bool(MONTH_NAMES_PATTERN.search(cleaned))

    if not has_month_word and ("/" in cleaned or "-" in cleaned or "." in cleaned):
        repaired_chars: List[str] = []
        for char in cleaned:
            if char in OCR_NUMERIC_SUBS:
                repaired_chars.append(OCR_NUMERIC_SUBS[char])
                repaired = True
            else:
                repaired_chars.append(char)
        cleaned = "".join(repaired_chars)

    return cleaned, repaired


def parse_date(
    raw_date: str, reference_year: Optional[int] = None
) -> Tuple[Optional[str], List[str]]:
    """Parse date string into ISO-8601 (YYYY-MM-DD) format using day-first precedence."""
    flags: List[str] = []
    if not raw_date or not raw_date.strip():
        return None, ["MISSING_DATE"]

    cleaned, was_repaired = clean_date_token(raw_date)
    if was_repaired:
        flags.append("REPAIRED_DATE_OCR")

    # 1. Try explicit day-first standard formats
    for fmt in DAY_FIRST_FORMATS:
        try:
            dt = datetime.strptime(cleaned, fmt)
            # Two-digit year cutoff handling
            if dt.year < 100:
                dt = dt.replace(year=2000 + dt.year)
            return dt.strftime("%Y-%m-%d"), flags
        except ValueError:
            continue

    # 2. Try dateutil parser with dayfirst=True
    try:
        dt = dateutil_parser.parse(cleaned, dayfirst=True)
        return dt.strftime("%Y-%m-%d"), flags
    except Exception:
        pass

    # 3. Handle dates without years (e.g. "12 Oct" or "03/10")
    month_name_match = re.match(
        r"^(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*$",
        cleaned,
        re.IGNORECASE,
    )
    if month_name_match:
        day_str, mon_str = month_name_match.groups()
        year = reference_year or datetime.now().year
        try:
            dt = datetime.strptime(f"{day_str} {mon_str} {year}", "%d %b %Y")
            flags.append("INFERRED_DATE_YEAR")
            return dt.strftime("%Y-%m-%d"), flags
        except ValueError:
            pass

    flags.append("INVALID_DATE")
    return None, flags
