"""Tests for digital text extraction, table header detection, and transaction row reconstruction."""

from pathlib import Path
import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image

from app.pipeline.native_extract import extract_native_words_from_document
from app.pipeline.layout.words import cluster_words_into_lines
from app.pipeline.layout.table_detector import detect_table_header, ColumnType
from app.pipeline.layout.row_builder import reconstruct_transaction_rows
from app.pipeline.ocr.preprocess import preprocess_image_for_ocr


def test_native_word_extraction(sample_digital_pdf: Path):
    """Verify that extract_native_words_from_document extracts words with normalized coordinates."""
    words = extract_native_words_from_document(sample_digital_pdf)

    assert len(words) > 0
    for w in words:
        assert 0.0 <= w.x0 <= 1.0
        assert 0.0 <= w.y0 <= 1.0
        assert 0.0 <= w.x1 <= 1.0
        assert 0.0 <= w.y1 <= 1.0
        assert w.source == "native"
        assert w.confidence == 100.0


def test_table_header_detection(sample_digital_pdf: Path):
    """Verify that the header detector finds Date, Description, Debit, Credit, Balance columns."""
    words = extract_native_words_from_document(sample_digital_pdf)
    lines = cluster_words_into_lines(words)
    header = detect_table_header(lines)

    assert header is not None
    col_types = [c.col_type for c in header.columns]
    assert ColumnType.DATE in col_types
    assert ColumnType.DESCRIPTION in col_types
    assert ColumnType.DEBIT in col_types
    assert ColumnType.CREDIT in col_types
    assert ColumnType.BALANCE in col_types


def test_transaction_row_reconstruction(sample_digital_pdf: Path):
    """Verify full extraction of transaction rows from a digital bank statement."""
    words = extract_native_words_from_document(sample_digital_pdf)
    lines = cluster_words_into_lines(words)
    header = detect_table_header(lines)
    assert header is not None

    rows = reconstruct_transaction_rows(lines, header)

    # 3 transactions: Woolworths, Salary, Telstra (Opening balance excluded as metadata)
    assert len(rows) == 3

    # Row 1: Woolworths debit
    assert rows[0].date_raw == "03/10/2023"
    assert "WOOLWORTHS" in rows[0].description_raw
    assert rows[0].debit_raw == "85.50"
    assert rows[0].balance_raw == "1,414.50"

    # Row 2: Salary credit
    assert rows[1].date_raw == "05/10/2023"
    assert "SALARY" in rows[1].description_raw
    assert rows[1].credit_raw == "3,200.00"
    assert rows[1].balance_raw == "4,614.50"

    # Row 3: Telstra debit
    assert rows[2].date_raw == "08/10/2023"
    assert "TELSTRA" in rows[2].description_raw
    assert rows[2].debit_raw == "120.00"
    assert rows[2].balance_raw == "4,494.50"


def test_multiline_narration_continuation(tmp_path: Path):
    """Verify that lines without dates are correctly merged into the active transaction's description."""
    multiline_pdf = tmp_path / "multiline_statement.pdf"
    c = canvas.Canvas(str(multiline_pdf), pagesize=letter)

    # Aligned header
    c.drawString(50, 750, "Date")
    c.drawString(130, 750, "Description")
    c.drawString(330, 750, "Debit")
    c.drawString(490, 750, "Balance")

    # Transaction 1 line
    c.drawString(50, 720, "15/10/2023")
    c.drawString(130, 720, "TRANSFER TO JOHN SMITH")
    c.drawString(330, 720, "250.00")
    c.drawString(490, 720, "1,250.00")

    # Continuation line with no date or amounts in narration column:
    c.drawString(130, 705, "REFERENCE: RENT PAYMENT OCT")
    c.drawString(130, 690, "OSKO PAYMENT ACC 987654")

    # Next transaction:
    c.drawString(50, 660, "18/10/2023")
    c.drawString(130, 660, "COLES SUPERMARKET")
    c.drawString(330, 660, "45.20")
    c.drawString(490, 660, "1,204.80")
    c.save()

    words = extract_native_words_from_document(multiline_pdf)
    lines = cluster_words_into_lines(words)
    header = detect_table_header(lines)
    assert header is not None

    rows = reconstruct_transaction_rows(lines, header)
    assert len(rows) == 2

    # First transaction should contain the continuation line text
    assert rows[0].date_raw == "15/10/2023"
    assert "TRANSFER TO JOHN SMITH" in rows[0].description_raw
    assert "REFERENCE: RENT PAYMENT OCT" in rows[0].description_raw
    assert "OSKO PAYMENT ACC 987654" in rows[0].description_raw
    assert rows[0].debit_raw == "250.00"
    assert rows[0].balance_raw == "1,250.00"

    # Second transaction remains isolated
    assert rows[1].date_raw == "18/10/2023"
    assert "COLES SUPERMARKET" in rows[1].description_raw
    assert rows[1].debit_raw == "45.20"
    assert rows[1].balance_raw == "1,204.80"


def test_ocr_image_preprocessing():
    """Verify that OpenCV image preprocessing pipeline produces valid enhanced image."""
    raw_img = Image.new("RGB", (400, 300), color=(240, 240, 240))
    processed = preprocess_image_for_ocr(raw_img)
    assert processed is not None
    assert processed.size == (400, 300)
