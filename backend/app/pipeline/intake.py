"""File intake, validation, security checks, and temporary persistence."""

import hashlib
import os
import shutil
import uuid
from pathlib import Path
from typing import BinaryIO, List, Optional, Tuple
from pydantic import BaseModel, Field

import pikepdf
from app.config import settings
from app.errors import ErrorCode, ProcessingError


class IntakeResult(BaseModel):
    """Result of intake validation."""

    file_id: str
    original_filename: str
    file_path: Path
    file_size_bytes: int
    sha256: str
    page_count: int
    is_encrypted: bool = False
    needs_password: bool = False
    security_warnings: List[str] = Field(default_factory=list)


def compute_sha256_and_validate_magic(
    file_stream: BinaryIO, max_mb: int = settings.MAX_UPLOAD_MB
) -> Tuple[str, int]:
    """Validate %PDF- magic bytes, check file size limits, and compute SHA-256."""
    file_stream.seek(0, os.SEEK_END)
    size_bytes = file_stream.tell()
    file_stream.seek(0)

    if size_bytes == 0:
        raise ProcessingError(
            code=ErrorCode.FILE_EMPTY,
            message="Uploaded file is empty (0 bytes).",
        )

    max_bytes = max_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise ProcessingError(
            code=ErrorCode.FILE_TOO_LARGE,
            message=f"File size ({size_bytes / (1024 * 1024):.2f} MB) exceeds maximum allowed limit ({max_mb} MB).",
            details={"size_bytes": size_bytes, "max_bytes": max_bytes},
        )

    # Check magic bytes in the first 1 KB
    header_sample = file_stream.read(1024)
    file_stream.seek(0)

    if b"%PDF-" not in header_sample:
        raise ProcessingError(
            code=ErrorCode.NOT_A_PDF,
            message="File does not have valid PDF magic bytes (%PDF-).",
        )

    # Compute SHA-256
    hasher = hashlib.sha256()
    while chunk := file_stream.read(65536):
        hasher.update(chunk)
    file_stream.seek(0)

    return hasher.hexdigest(), size_bytes


def inspect_pdf_structure(
    file_path: Path, max_pages: int = settings.MAX_PAGES
) -> Tuple[int, bool, bool, List[str]]:
    """Inspect PDF with pikepdf for page count, encryption, and embedded executable constructs."""
    security_warnings: List[str] = []
    is_encrypted = False
    needs_password = False
    page_count = 0

    # 1. Quick low-level byte scan for suspicious actions
    try:
        with open(file_path, "rb") as f:
            raw_content = f.read()
            if b"/JavaScript" in raw_content or b"/JS" in raw_content:
                security_warnings.append("SUSPICIOUS_JAVASCRIPT_DETECTED")
            if b"/Launch" in raw_content:
                security_warnings.append("SUSPICIOUS_LAUNCH_ACTION_DETECTED")
            if b"/EmbeddedFiles" in raw_content:
                security_warnings.append("EMBEDDED_FILES_DETECTED")
    except Exception as e:
        raise ProcessingError(
            code=ErrorCode.PDF_CORRUPT,
            message=f"Could not read PDF bytes: {str(e)}",
        )

    # 2. Structural parsing with pikepdf
    try:
        # First try opening without password (or empty password)
        try:
            pdf = pikepdf.Pdf.open(file_path)
            is_encrypted = False
            page_count = len(pdf.pages)
            pdf.close()
        except pikepdf.PasswordError:
            # File is password-protected
            is_encrypted = True
            needs_password = True
            # Attempt to verify if empty password works
            try:
                pdf = pikepdf.Pdf.open(file_path, password="")
                needs_password = False
                page_count = len(pdf.pages)
                pdf.close()
            except pikepdf.PasswordError:
                needs_password = True
                return 0, is_encrypted, needs_password, security_warnings

    except pikepdf.PdfError as e:
        raise ProcessingError(
            code=ErrorCode.PDF_CORRUPT,
            message=f"Corrupted or invalid PDF structure: {str(e)}",
        )
    except Exception as e:
        raise ProcessingError(
            code=ErrorCode.PDF_CORRUPT,
            message=f"Failed to inspect PDF: {str(e)}",
        )

    if page_count > max_pages:
        raise ProcessingError(
            code=ErrorCode.TOO_MANY_PAGES,
            message=f"PDF page count ({page_count}) exceeds limit of {max_pages} pages.",
            details={"page_count": page_count, "max_pages": max_pages},
        )

    return page_count, is_encrypted, needs_password, security_warnings


def process_intake(
    file_stream: BinaryIO,
    filename: str,
    target_dir: Optional[Path] = None,
    max_mb: int = settings.MAX_UPLOAD_MB,
    max_pages: int = settings.MAX_PAGES,
) -> IntakeResult:
    """Execute complete intake validation and persist file securely to disk."""
    dest_dir = target_dir or settings.UPLOAD_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)

    # 1. Validate magic bytes, size, and hash
    sha256, size_bytes = compute_sha256_and_validate_magic(file_stream, max_mb=max_mb)

    # 2. Persist to randomized temporary file
    file_id = str(uuid.uuid4())
    stored_path = dest_dir / f"{file_id}.pdf"

    try:
        with open(stored_path, "wb") as f_out:
            file_stream.seek(0)
            shutil.copyfileobj(file_stream, f_out)
    except Exception as e:
        if stored_path.exists():
            stored_path.unlink()
        raise ProcessingError(
            code=ErrorCode.PDF_CORRUPT,
            message=f"Failed to persist file: {str(e)}",
        )

    # 3. Structural inspection
    try:
        page_count, is_encrypted, needs_password, warnings = inspect_pdf_structure(
            stored_path, max_pages=max_pages
        )
    except Exception:
        if stored_path.exists():
            stored_path.unlink()
        raise

    return IntakeResult(
        file_id=file_id,
        original_filename=filename,
        file_path=stored_path,
        file_size_bytes=size_bytes,
        sha256=sha256,
        page_count=page_count,
        is_encrypted=is_encrypted,
        needs_password=needs_password,
        security_warnings=warnings,
    )


def cleanup_intake_file(file_path: Path) -> None:
    """Safely delete uploaded file from temporary storage."""
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass
