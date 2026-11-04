"""Country-aware currency and decimal amount normalization."""

import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import List, Optional, Tuple


# Currency symbol mappings
CURRENCY_SYMBOLS = {
    "A$": "AUD",
    "AU$": "AUD",
    "$": "AUD",   # Default dollar in AU context
    "£": "GBP",
    "GBP": "GBP",
    "₹": "INR",
    "RS.": "INR",
    "RS": "INR",
    "INR": "INR",
    "€": "EUR",
}


def detect_currency(raw_text: str, default_currency: str = "AUD") -> str:
    """Identify currency code from string tokens."""
    upper = raw_text.upper()
    for sym, code in CURRENCY_SYMBOLS.items():
        if sym in upper:
            return code
    return default_currency


def parse_amount(
    raw_amount: Optional[str], default_currency: str = "AUD"
) -> Tuple[Optional[Decimal], str, List[str]]:
    """Parse raw financial string into an exact Decimal quantized to 2 decimal places."""
    flags: List[str] = []
    if not raw_amount or not raw_amount.strip():
        return None, default_currency, []

    token = raw_amount.strip()

    # Detect currency
    currency = detect_currency(token, default_currency=default_currency)

    # Check for empty placeholders (- or -- or NIL)
    if token in ("-", "--", "NIL", "nil", "0.00", "0"):
        if token in ("-", "--", "NIL", "nil"):
            return None, currency, []
        return Decimal("0.00"), currency, []

    # Detect Dr / Cr suffixes
    upper = token.upper()
    is_dr = "DR" in upper
    is_cr = "CR" in upper

    # Detect parentheses for negative amount (e.g. "(85.50)")
    is_negative = False
    if token.startswith("(") and token.endswith(")"):
        is_negative = True
        token = token[1:-1]
        flags.append("NEGATIVE_BRACKET_AMOUNT")
    elif token.startswith("-"):
        is_negative = True
        token = token[1:]
    elif token.endswith("-"):
        is_negative = True
        token = token[:-1]

    # Clean characters: remove currency symbols, spaces, and Dr/Cr markers
    clean = re.sub(r"[A-Za-z$£€₹,\s]", "", token)

    try:
        dec = Decimal(clean)
        # Quantize to 2 decimals
        dec = dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if is_negative:
            dec = -dec
        return dec, currency, flags
    except (InvalidOperation, ValueError):
        flags.append("INVALID_AMOUNT")
        return None, currency, flags
