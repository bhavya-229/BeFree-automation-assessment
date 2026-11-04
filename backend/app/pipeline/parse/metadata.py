"""Extract account-holder, bank name, identifiers, and statement metadata."""

import re
from typing import Optional, Dict, Any
from pydantic import BaseModel
from decimal import Decimal


class StatementMetadata(BaseModel):
    """Account and statement metadata extracted from header/footer blocks."""

    bank_name: Optional[str] = "Unknown Bank"
    account_name: Optional[str] = None
    account_number: Optional[str] = None
    account_identifier_type: Optional[str] = None  # BSB, Sort Code, IFSC, Account Number
    sort_code_or_bsb: Optional[str] = None
    statement_period_start: Optional[str] = None
    statement_period_end: Optional[str] = None
    currency: str = "AUD"
    opening_balance: Optional[str] = None
    closing_balance: Optional[str] = None


def extract_metadata_from_text(raw_text: str) -> StatementMetadata:
    """Parse common bank header/footer patterns to extract statement metadata."""
    meta = StatementMetadata()

    text_upper = raw_text.upper()

    # 1. Bank Identification
    if "COMMONWEALTH BANK" in text_upper or "COMMBANK" in text_upper or "CBA" in text_upper:
        meta.bank_name = "Commonwealth Bank of Australia"
        meta.currency = "AUD"
    elif "BARCLAYS" in text_upper:
        meta.bank_name = "Barclays Bank UK PLC"
        meta.currency = "GBP"
    elif "WESTPAC" in text_upper:
        meta.bank_name = "Westpac Banking Corporation"
        meta.currency = "AUD"
    elif "ANZ" in text_upper:
        meta.bank_name = "ANZ Bank"
        meta.currency = "AUD"
    elif "HSBC" in text_upper:
        meta.bank_name = "HSBC Bank"
        meta.currency = "GBP"
    elif "NATWEST" in text_upper:
        meta.bank_name = "NatWest"
        meta.currency = "GBP"
    elif "STATE BANK OF INDIA" in text_upper or "SBI" in text_upper:
        meta.bank_name = "State Bank of India"
        meta.currency = "INR"
    else:
        # Generic institution detection (e.g. "Southern Cross Test Bank", "St. George Bank")
        bank_title_match = re.search(r'([A-Za-z\s]+(?:Bank|Building Society|Credit Union))', raw_text, re.IGNORECASE)
        if bank_title_match:
            meta.bank_name = bank_title_match.group(1).strip()

    # Explicit Currency overrides
    if "CURRENCY: AUD" in text_upper or " AUD " in text_upper or "A$" in raw_text:
        meta.currency = "AUD"
    elif "CURRENCY: GBP" in text_upper or "£" in raw_text or " POUND" in text_upper:
        meta.currency = "GBP"
    elif "CURRENCY: INR" in text_upper or "₹" in raw_text or " RS." in text_upper:
        meta.currency = "INR"

    # 2. Account identifiers
    # Australian BSB + Account (e.g. 062-000 12345678 or BSB: 062-984)
    bsb_match = re.search(r'(?:BSB|ACCOUNT|A/C)[:\s]*([0-9]{3}[-\s][0-9]{3})\s*([0-9]{5,10})?', raw_text, re.IGNORECASE)
    if bsb_match:
        meta.sort_code_or_bsb = bsb_match.group(1).replace(" ", "-")
        meta.account_identifier_type = "BSB & Account"
        if bsb_match.group(2):
            meta.account_number = bsb_match.group(2)

    # UK Sort Code + Account Number (e.g. Sort Code: 20-00-00   Account Number: 87654321)
    sort_match = re.search(r'Sort\s*Code[:\s]*([0-9]{2}[-\s][0-9]{2}[-\s][0-9]{2})', raw_text, re.IGNORECASE)
    if sort_match:
        meta.sort_code_or_bsb = sort_match.group(1).replace(" ", "-")
        meta.account_identifier_type = "Sort Code & Account"

    acc_num_match = re.search(r'Account\s*(?:Number|No|#)?[:\s]*((?:[*X\d]{2,6}\s*)?[0-9]{4,12})', raw_text, re.IGNORECASE)
    if acc_num_match:
        meta.account_number = acc_num_match.group(1).strip()

    # 3. Period extraction
    period_slash_match = re.search(r'(?:period|statement period)[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})\s*[^0-9]+\s*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})', raw_text, re.IGNORECASE)
    if period_slash_match:
        meta.statement_period_start = period_slash_match.group(1)
        meta.statement_period_end = period_slash_match.group(2)
    else:
        period_match = re.search(r'Period[:\s]*([0-9]{1,2}\s+[A-Za-z]{3,9}\s+[0-9]{4})\s+to\s+([0-9]{1,2}\s+[A-Za-z]{3,9}\s+[0-9]{4})', raw_text, re.IGNORECASE)
        if period_match:
            meta.statement_period_start = period_match.group(1)
            meta.statement_period_end = period_match.group(2)
        else:
            stmt_date_match = re.search(r'(?:Statement Date|As at|Date)[:\s]*([0-9]{1,2}\s+[A-Za-z]{3,9}\s+[0-9]{4})', raw_text, re.IGNORECASE)
            if stmt_date_match:
                meta.statement_period_end = stmt_date_match.group(1)

    # 4. Opening & Closing Balances with international currency prefixes
    open_bal_match = re.search(r'Opening\s*Balance[:\s]*(?:[A-Za-z]{3}|\$|£|€|₹)?\s*([0-9,]+\.[0-9]{2})', raw_text, re.IGNORECASE)
    if open_bal_match:
        meta.opening_balance = open_bal_match.group(1).replace(",", "")

    close_bal_match = re.search(r'Closing\s*Balance[^:]*[:\s]*(?:[A-Za-z]{3}|\$|£|€|₹)?\s*([0-9,]+\.[0-9]{2})', raw_text, re.IGNORECASE)
    if close_bal_match:
        meta.closing_balance = close_bal_match.group(1).replace(",", "")

    return meta
