"""Normalized transaction schema and classification metadata."""

from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class ClassificationSource(str, Enum):
    """Source that assigned the transaction category."""

    RULE = "RULE"
    ML = "ML"
    MANUAL = "MANUAL"
    UNCLASSIFIED = "UNCLASSIFIED"


class NormalizedTransaction(BaseModel):
    """Canonical transaction model across all countries and banks."""

    id: str = Field(..., description="Unique transaction UUID")
    statement_id: Optional[str] = None
    line_number: int
    page_number: int

    # Dates
    date: Optional[str] = Field(None, description="ISO-8601 formatted date (YYYY-MM-DD)")
    date_raw: str
    value_date: Optional[str] = None
    value_date_raw: Optional[str] = None

    # Descriptions
    description: str = Field(..., description="Cleaned, canonicalized description")
    description_raw: str = Field(..., description="Verbatim raw description from statement")
    ref_no: Optional[str] = None
    channel: Optional[str] = None
    counterparty: Optional[str] = None

    # Financial Amounts (Decimals in Python, rendered as decimal strings in API)
    debit: Optional[Decimal] = None
    credit: Optional[Decimal] = None
    amount: Optional[Decimal] = None
    balance: Optional[Decimal] = None
    currency: str = "AUD"

    # Raw Financial Strings (verbatim preservation)
    raw_debit: Optional[str] = None
    raw_credit: Optional[str] = None
    raw_balance: Optional[str] = None

    # Classification
    category: str = "Other / Unclassified"
    subcategory: Optional[str] = None
    category_source: ClassificationSource = ClassificationSource.UNCLASSIFIED
    category_confidence: float = 0.0
    rule_id: Optional[str] = None
    ml_top3: List[Dict[str, Any]] = Field(default_factory=list)
    user_edited: bool = False

    # Validation & Provenance Flags
    flags: List[str] = Field(default_factory=list)
    row_confidence: float = 100.0
    bounding_box: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("debit", "credit", "amount", "balance", when_used="json")
    def serialize_decimal(self, v: Optional[Decimal]) -> Optional[str]:
        return f"{v:.2f}" if v is not None else None
