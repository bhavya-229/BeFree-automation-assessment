"""Text cleaning, payment channel extraction, and merchant canonicalization."""

import re
from typing import Optional, Tuple


# Payment channel prefixes and keywords
CHANNEL_PATTERNS = {
    # Australia
    "PAYID": re.compile(r"\bPAYID\b", re.IGNORECASE),
    "OSKO": re.compile(r"\bOSKO\b", re.IGNORECASE),
    "BPAY": re.compile(r"\bBPAY\b", re.IGNORECASE),
    "EFTPOS": re.compile(r"\bEFTPOS\b", re.IGNORECASE),
    "DIRECT_DEBIT": re.compile(r"\b(DIRECT DEBIT|DIR DEB|D/D)\b", re.IGNORECASE),
    # UK
    "FPS": re.compile(r"\b(FASTER PAYMENT|FPS|F/P)\b", re.IGNORECASE),
    "BACS": re.compile(r"\b(BACS|DIRECT CREDIT)\b", re.IGNORECASE),
    "CHAPS": re.compile(r"\bCHAPS\b", re.IGNORECASE),
    "STANDING_ORDER": re.compile(r"\b(STANDING ORDER|S/O)\b", re.IGNORECASE),
    "CONTACTLESS": re.compile(r"\b(CONTACTLESS|CPT)\b", re.IGNORECASE),
    # Universal / ATM / POS
    "ATM": re.compile(r"\b(ATM|CASH WDL|ATM WDL)\b", re.IGNORECASE),
    "POS": re.compile(r"\b(POS|PURCHASE|CARD PURCHASE)\b", re.IGNORECASE),
    "INTEREST": re.compile(r"\b(INTEREST PAID|INT PD|CREDIT INTEREST)\b", re.IGNORECASE),
    # Secondary / India
    "UPI": re.compile(r"\bUPI\b", re.IGNORECASE),
    "NEFT": re.compile(r"\bNEFT\b", re.IGNORECASE),
    "IMPS": re.compile(r"\bIMPS\b", re.IGNORECASE),
}

# Common merchant aliases mapping to clean canonical names
MERCHANT_ALIASES = {
    "WOOLIES": "WOOLWORTHS",
    "WOOLWORTHS METRO": "WOOLWORTHS",
    "AMZN": "AMAZON",
    "AMZN MKTP": "AMAZON MARKETPLACE",
    "AMAZON PRIME": "AMAZON PRIME SUBSCRIPTION",
    "AMZN PRIME": "AMAZON PRIME SUBSCRIPTION",
    "APPLE.COM/BILL": "APPLE DIGITAL SUBSCRIPTION",
    "ITUNES.COM": "APPLE DIGITAL SUBSCRIPTION",
    "TFL": "TRANSPORT FOR LONDON",
    "TFL.GOV.UK": "TRANSPORT FOR LONDON",
    "TFL TRAVEL": "TRANSPORT FOR LONDON",
    "MCD": "MCDONALDS",
    "MCDONALD'S": "MCDONALDS",
    "JBHIFI": "JB HI-FI",
    "JB HI FI": "JB HI-FI",
    "MARKS & SPENCER": "MARKS AND SPENCER",
    "M&S": "MARKS AND SPENCER",
    "SAINSBURY": "SAINSBURYS",
    "SAINSBURY'S": "SAINSBURYS",
}

# Payment intermediary / gateway prefixes that wrap the real downstream merchant
PROCESSOR_PATTERNS = [
    (re.compile(r"^\s*PAYPAL\s*[*_\-]\s*", re.IGNORECASE), "PAYPAL"),
    (re.compile(r"^\s*SQ\s*[*_\-]\s*", re.IGNORECASE), "SQUARE"),
    (re.compile(r"^\s*SQUARE\s*[*_\-]\s*", re.IGNORECASE), "SQUARE"),
    (re.compile(r"^\s*SP\s*[*_\-]\s*", re.IGNORECASE), "STRIPE"),
    (re.compile(r"^\s*STRIPE\s*[*_\-]\s*", re.IGNORECASE), "STRIPE"),
    (re.compile(r"^\s*KLARNA\s*[*_\-]\s*", re.IGNORECASE), "BNPL"),
    (re.compile(r"^\s*AFTERPAY\s*[*_\-]\s*", re.IGNORECASE), "BNPL"),
]


def clean_description(raw_description: str) -> Tuple[str, Optional[str], Optional[str]]:
    """Clean transaction description, strip payment processors, and extract payment rail channel and ref number."""
    if not raw_description:
        return "", None, None

    text = raw_description.strip()

    # 1. Strip and detect payment processors / gateways (e.g. "PAYPAL * STEAM" -> "STEAM")
    detected_channel: Optional[str] = None
    for proc_pat, ch_name in PROCESSOR_PATTERNS:
        if proc_pat.match(text):
            detected_channel = ch_name
            text = proc_pat.sub("", text).strip()
            break

    # 2. Detect channel rail if not already set by gateway
    if not detected_channel:
        for ch_name, pattern in CHANNEL_PATTERNS.items():
            if pattern.search(text):
                detected_channel = ch_name
                break

    # 3. Extract reference numbers if present (e.g. "REF 123456", "AUTH 7890", "OSKO 998877")
    detected_ref: Optional[str] = None
    ref_match = re.search(r"\b(?:REF|REFERENCE|AUTH|RRN|NO|TXN)\s*[:#]?\s*([A-Za-z0-9_-]{4,20})\b", text, re.IGNORECASE)
    if ref_match:
        detected_ref = ref_match.group(1)
        # Remove the reference token from narrative text so it doesn't pollute classification
        text = text[:ref_match.start()] + " " + text[ref_match.end():]

    # 4. Strip synthetic test artifacts, headers and watermarks
    text = re.sub(r"SYNTHETIC (?:SAMPLE|TEST).*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"FOR SOFTWARE TESTING.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"TRANSACTION DESCRIPTION.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"PAGE \d+.*", "", text, flags=re.IGNORECASE)

    # 5. Strip OCR noise characters and trailing artifacts
    text = re.sub(r"[=_—–|~]+", " ", text)

    # 6. Strip card masks (e.g. "CARD ... 1234", "XXXX-XXXX-1234", "XXXXXXXXXXXX1234")
    text = re.sub(r"\b(?:CARD\s+)?(?:\d{4}|\*{4}|X{4})[- ]?(?:\d{4}|\*{4}|X{4})[- ]?(?:\d{4}|\*{4}|X{4})[- ]?(\d{4})\b", r"CARD \1", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(?:\*{4,}|X{4,})\d{4}\b", "", text, flags=re.IGNORECASE)

    # 7. Strip long timestamps / transaction IDs (sequences of 8+ digits)
    text = re.sub(r"\b\d{8,}\b", "", text)

    # 8. Normalize whitespace, trim leading/trailing dashes and uppercase
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^[-–—\s]+|[-–—\s]+$", "", text).strip().upper()

    # 9. Apply merchant aliases
    for alias, canonical in MERCHANT_ALIASES.items():
        if alias in text:
            text = text.replace(alias, canonical)

    return text, detected_channel, detected_ref
