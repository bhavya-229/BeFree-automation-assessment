"""Tests for country-aware date and currency amount parsing."""

from decimal import Decimal
import pytest

from app.pipeline.parse.dates import parse_date
from app.pipeline.parse.amounts import parse_amount, detect_currency


def test_parse_australian_uk_dates():
    """Verify parsing of standard AU and UK day-first date formats into ISO YYYY-MM-DD."""
    # Standard slash day-first
    d1, f1 = parse_date("03/10/2023")
    assert d1 == "2023-10-03"

    # Dash day-first
    d2, f2 = parse_date("15-11-2023")
    assert d2 == "2023-11-15"

    # UK standard month name format
    d3, f3 = parse_date("12 Oct 2023")
    assert d3 == "2023-10-12"

    # Short year
    d4, f4 = parse_date("14-Oct-23")
    assert d4 == "2023-10-14"

    # ISO format
    d5, f5 = parse_date("2023-12-25")
    assert d5 == "2023-12-25"


def test_parse_date_ocr_character_repair():
    """Verify that OCR letter confusions (O for 0, l for 1) are repaired in date strings."""
    repaired_date, flags = parse_date("O3/1O/2O23")
    assert repaired_date == "2023-10-03"
    assert "REPAIRED_DATE_OCR" in flags


def test_parse_amounts_and_currencies():
    """Verify parsing of amounts in AUD, GBP, and negative bracket notations."""
    # Australian Dollars
    amt1, curr1, f1 = parse_amount("$85.50", default_currency="AUD")
    assert amt1 == Decimal("85.50")
    assert curr1 == "AUD"

    # British Pounds with thousands separator
    amt2, curr2, f2 = parse_amount("£1,250.00", default_currency="GBP")
    assert amt2 == Decimal("1250.00")
    assert curr2 == "GBP"

    # Parentheses negative notation (85.50)
    amt3, curr3, f3 = parse_amount("(85.50)")
    assert amt3 == Decimal("-85.50")
    assert "NEGATIVE_BRACKET_AMOUNT" in f3

    # Trailing minus notation
    amt4, curr4, f4 = parse_amount("120.00-")
    assert amt4 == Decimal("-120.00")

    # Indian Rupees
    amt5, curr5, f5 = parse_amount("₹5,000.00")
    assert amt5 == Decimal("5000.00")
    assert curr5 == "INR"


def test_parse_invalid_amount_preserves_error():
    """Verify that unparseable text does not crash and sets INVALID_AMOUNT flag."""
    amt, curr, flags = parse_amount("N/A_NOT_AN_AMOUNT")
    assert amt is None
    assert "INVALID_AMOUNT" in flags
