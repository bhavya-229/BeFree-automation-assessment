"""Tests for page-level and document-level PDF type detection (Digital vs Scanned vs Hybrid)."""

from pathlib import Path
import pytest

from app.pipeline.pdf_type import (
    PageType,
    DocType,
    detect_document_type,
)


def test_detect_digital_pdf(sample_digital_pdf: Path):
    """Verify that a clean digital statement is identified as DIGITAL at page and doc level."""
    report = detect_document_type(sample_digital_pdf)

    assert report.doc_type == DocType.DIGITAL
    assert report.total_pages == 1
    assert report.digital_page_count == 1
    assert report.scanned_page_count == 0
    assert report.pages[0].page_type == PageType.DIGITAL
    assert report.pages[0].meaningful_text_count >= 40
    assert report.pages[0].garbage_char_ratio < 0.05


def test_detect_scanned_pdf(sample_scanned_pdf: Path):
    """Verify that an image-only PDF is identified as SCANNED at page and doc level."""
    report = detect_document_type(sample_scanned_pdf)

    assert report.doc_type == DocType.SCANNED
    assert report.total_pages == 1
    assert report.scanned_page_count == 1
    assert report.digital_page_count == 0
    assert report.pages[0].page_type == PageType.SCANNED
    assert report.pages[0].image_count >= 1
    assert report.pages[0].meaningful_text_count < 40


def test_detect_mixed_pdf(sample_mixed_pdf: Path):
    """Verify that a multi-page PDF with digital and scanned pages is identified as MIXED."""
    report = detect_document_type(sample_mixed_pdf)

    assert report.doc_type == DocType.MIXED
    assert report.total_pages == 2
    assert report.digital_page_count == 1
    assert report.scanned_page_count == 1
    # Page 1 is digital text
    assert report.pages[0].page_number == 1
    assert report.pages[0].page_type == PageType.DIGITAL
    # Page 2 is scanned image
    assert report.pages[1].page_number == 2
    assert report.pages[1].page_type == PageType.SCANNED


def test_detect_cid_corrupted_pdf_routes_to_ocr(sample_cid_corrupted_pdf: Path):
    """Verify that a PDF with corrupted (cid:N) fonts routes to SCANNED/OCR."""
    report = detect_document_type(sample_cid_corrupted_pdf)

    assert report.total_pages == 1
    assert report.pages[0].page_type == PageType.SCANNED
    assert report.pages[0].garbage_char_ratio >= 0.05
