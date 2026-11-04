"""Standardized error codes and exception classes."""

from enum import Enum
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class ErrorCode(str, Enum):
    """Stable error codes mapped to specific error conditions."""

    NOT_A_PDF = "NOT_A_PDF"
    PDF_CORRUPT = "PDF_CORRUPT"
    PDF_ENCRYPTED = "PDF_ENCRYPTED"
    WRONG_PASSWORD = "WRONG_PASSWORD"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    FILE_EMPTY = "FILE_EMPTY"
    TOO_MANY_PAGES = "TOO_MANY_PAGES"
    DUPLICATE_FILE = "DUPLICATE_FILE"
    UNSUPPORTED_DOCUMENT = "UNSUPPORTED_DOCUMENT"
    NO_TRANSACTIONS_FOUND = "NO_TRANSACTIONS_FOUND"
    OCR_UNAVAILABLE = "OCR_UNAVAILABLE"
    OCR_TIMEOUT = "OCR_TIMEOUT"
    PARSE_FAILED = "PARSE_FAILED"
    RATE_LIMITED = "RATE_LIMITED"


class ProcessingError(Exception):
    """Domain exception raised within the processing pipeline."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code

    def to_problem_dict(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Convert into RFC 7807 application/problem+json format."""
        return {
            "type": f"https://api.befree.io/errors/{self.code.value.lower()}",
            "title": self.code.value.replace("_", " ").title(),
            "status": self.status_code,
            "detail": self.message,
            "code": self.code.value,
            "request_id": request_id,
            "details": self.details,
        }
