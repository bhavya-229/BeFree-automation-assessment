"""Tests for file intake validation, security inspection, and temporary persistence."""

import io
from pathlib import Path
import pytest

from app.errors import ErrorCode, ProcessingError
from app.pipeline.intake import (
    compute_sha256_and_validate_magic,
    inspect_pdf_structure,
    process_intake,
    cleanup_intake_file,
)


def test_intake_non_pdf_fails():
    """Verify that non-PDF content (e.g. text/html) is rejected by magic byte check."""
    fake_data = io.BytesIO(b"Hello world, this is a plain text file renamed to .pdf")
    with pytest.raises(ProcessingError) as exc_info:
        compute_sha256_and_validate_magic(fake_data)
    assert exc_info.value.code == ErrorCode.NOT_A_PDF


def test_intake_empty_file_fails():
    """Verify that 0-byte uploads are rejected."""
    empty_stream = io.BytesIO(b"")
    with pytest.raises(ProcessingError) as exc_info:
        compute_sha256_and_validate_magic(empty_stream)
    assert exc_info.value.code == ErrorCode.FILE_EMPTY


def test_intake_file_too_large_fails():
    """Verify that uploads exceeding max_mb are rejected."""
    # Create 2 KB mock stream with magic bytes and test with max_mb=0 (simulate limit)
    oversized = io.BytesIO(b"%PDF-1.4\n" + b"X" * 2048)
    with pytest.raises(ProcessingError) as exc_info:
        compute_sha256_and_validate_magic(oversized, max_mb=0)
    assert exc_info.value.code == ErrorCode.FILE_TOO_LARGE


def test_intake_corrupted_pdf_structure(tmp_path: Path):
    """Verify that a damaged PDF with valid magic bytes but corrupted xref fails gracefully."""
    corrupt_pdf = tmp_path / "corrupt.pdf"
    corrupt_pdf.write_bytes(b"%PDF-1.4\nSome random garbage that is not valid xref\n%%EOF")

    with pytest.raises(ProcessingError) as exc_info:
        inspect_pdf_structure(corrupt_pdf)
    assert exc_info.value.code == ErrorCode.PDF_CORRUPT


def test_intake_valid_digital_pdf(sample_digital_pdf: Path, tmp_path: Path):
    """Verify that a valid digital PDF passes intake inspection and computes SHA-256."""
    with open(sample_digital_pdf, "rb") as f:
        result = process_intake(f, "cba_statement.pdf", target_dir=tmp_path)

    assert result.original_filename == "cba_statement.pdf"
    assert result.page_count == 1
    assert result.is_encrypted is False
    assert result.needs_password is False
    assert len(result.sha256) == 64
    assert result.file_path.exists()

    # Cleanup verification
    cleanup_intake_file(result.file_path)
    assert not result.file_path.exists()


def test_intake_encrypted_pdf_detects_password_requirement(sample_encrypted_pdf: Path, tmp_path: Path):
    """Verify that a password-protected PDF is detected and marked as needs_password."""
    with open(sample_encrypted_pdf, "rb") as f:
        result = process_intake(f, "encrypted.pdf", target_dir=tmp_path)

    assert result.is_encrypted is True
    assert result.needs_password is True
    assert result.file_path.exists()

    cleanup_intake_file(result.file_path)
