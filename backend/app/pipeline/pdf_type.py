"""Page-level and document-level PDF type detection (Digital vs Scanned vs Hybrid)."""

import re
from enum import Enum
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

import pdfplumber
import pypdfium2 as pdfium
from app.errors import ErrorCode, ProcessingError


class PageType(str, Enum):
    """Classification of an individual PDF page."""

    DIGITAL = "DIGITAL"
    SCANNED = "SCANNED"
    HYBRID = "HYBRID"


class DocType(str, Enum):
    """Aggregate classification of an entire PDF document."""

    DIGITAL = "DIGITAL"
    SCANNED = "SCANNED"
    MIXED = "MIXED"


class PageTypeMetrics(BaseModel):
    """Diagnostic metrics used to classify a page."""

    page_number: int
    page_type: PageType
    meaningful_text_count: int
    total_char_count: int
    garbage_char_ratio: float
    image_count: int
    image_area_ratio: float
    width: float
    height: float
    reason: str


class DocumentTypeReport(BaseModel):
    """Comprehensive page-level and document-level type analysis."""

    doc_type: DocType
    total_pages: int
    digital_page_count: int
    scanned_page_count: int
    hybrid_page_count: int
    pages: List[PageTypeMetrics]
    reason: str


# Regex for detecting (cid:N) font mapping failures
CID_PATTERN = re.compile(r"\(cid:\d+\)")


def analyze_page_type(page: pdfplumber.page.Page, page_num: int) -> PageTypeMetrics:
    """Analyze a single pdfplumber page to determine whether it is digital, scanned, or hybrid."""
    width = float(page.width)
    height = float(page.height)
    page_area = width * height if width > 0 and height > 0 else 1.0

    raw_text = page.extract_text() or ""
    total_chars = len(raw_text)

    # 1. Calculate garbage characters: replacement character, private use area, or (cid:N)
    replacement_chars = raw_text.count("\ufffd")
    pua_chars = sum(1 for c in raw_text if "\ue000" <= c <= "\uf8ff")
    cid_matches = len(CID_PATTERN.findall(raw_text))
    garbage_chars = replacement_chars + pua_chars + (cid_matches * 5)

    garbage_ratio = (garbage_chars / total_chars) if total_chars > 0 else 0.0

    # 2. Meaningful characters: alphanumeric and standard punctuation excluding whitespace
    meaningful_chars = sum(1 for c in raw_text if not c.isspace() and c.isprintable())
    meaningful_chars = max(0, meaningful_chars - garbage_chars)

    # 3. Image analysis
    images = page.images
    image_count = len(images)
    total_image_area = 0.0

    for img in images:
        w = float(img.get("width", 0))
        h = float(img.get("height", 0))
        total_image_area += w * h

    image_area_ratio = min(1.0, total_image_area / page_area) if page_area > 0 else 0.0

    # 4. Classification logic
    # Rule 1: Font failure / high garbage -> must be routed to OCR (SCANNED)
    if garbage_ratio >= 0.05 and total_chars > 10:
        return PageTypeMetrics(
            page_number=page_num,
            page_type=PageType.SCANNED,
            meaningful_text_count=meaningful_chars,
            total_char_count=total_chars,
            garbage_char_ratio=round(garbage_ratio, 4),
            image_count=image_count,
            image_area_ratio=round(image_area_ratio, 4),
            width=width,
            height=height,
            reason=f"High font encoding corruption (garbage ratio: {garbage_ratio:.1%}, cids: {cid_matches}). Routes to OCR.",
        )

    # Rule 2: Substantial digital text and low image dominance -> DIGITAL
    if meaningful_chars >= 40 and image_area_ratio < 0.70:
        return PageTypeMetrics(
            page_number=page_num,
            page_type=PageType.DIGITAL,
            meaningful_text_count=meaningful_chars,
            total_char_count=total_chars,
            garbage_char_ratio=round(garbage_ratio, 4),
            image_count=image_count,
            image_area_ratio=round(image_area_ratio, 4),
            width=width,
            height=height,
            reason=f"Sufficient extractable text ({meaningful_chars} chars) with valid fonts and low image coverage.",
        )

    # Rule 3: Negligible text and substantial image coverage -> SCANNED
    if meaningful_chars < 40 and (image_area_ratio >= 0.30 or image_count > 0):
        return PageTypeMetrics(
            page_number=page_num,
            page_type=PageType.SCANNED,
            meaningful_text_count=meaningful_chars,
            total_char_count=total_chars,
            garbage_char_ratio=round(garbage_ratio, 4),
            image_count=image_count,
            image_area_ratio=round(image_area_ratio, 4),
            width=width,
            height=height,
            reason=f"Sparse native text ({meaningful_chars} chars) and raster image presence ({image_area_ratio:.1%} area). Routes to OCR.",
        )

    # Rule 4: Moderate text with high image area coverage (e.g. background scan with low-quality OCR text layer) -> HYBRID
    if meaningful_chars >= 40 and image_area_ratio >= 0.70:
        return PageTypeMetrics(
            page_number=page_num,
            page_type=PageType.HYBRID,
            meaningful_text_count=meaningful_chars,
            total_char_count=total_chars,
            garbage_char_ratio=round(garbage_ratio, 4),
            image_count=image_count,
            image_area_ratio=round(image_area_ratio, 4),
            width=width,
            height=height,
            reason=f"Both text layer ({meaningful_chars} chars) and dominant background scan ({image_area_ratio:.1%} area) detected.",
        )

    # Fallback: if very little text and no images (e.g. blank page or sparse text)
    if meaningful_chars >= 15:
        p_type = PageType.DIGITAL
        reason = f"Low text volume ({meaningful_chars} chars) but clean digital structure."
    else:
        p_type = PageType.SCANNED
        reason = f"Negligible text ({meaningful_chars} chars). Fallback to image processing."

    return PageTypeMetrics(
        page_number=page_num,
        page_type=p_type,
        meaningful_text_count=meaningful_chars,
        total_char_count=total_chars,
        garbage_char_ratio=round(garbage_ratio, 4),
        image_count=image_count,
        image_area_ratio=round(image_area_ratio, 4),
        width=width,
        height=height,
        reason=reason,
    )


def detect_document_type(file_path: Path) -> DocumentTypeReport:
    """Inspect every page of a PDF file and produce an aggregate document type report."""
    if not file_path.exists():
        raise ProcessingError(
            code=ErrorCode.PDF_CORRUPT,
            message=f"File not found: {file_path}",
        )

    page_metrics_list: List[PageTypeMetrics] = []

    try:
        with pdfplumber.open(file_path) as pdf:
            if len(pdf.pages) == 0:
                raise ProcessingError(
                    code=ErrorCode.PDF_CORRUPT,
                    message="PDF has 0 pages.",
                )

            for idx, page in enumerate(pdf.pages, start=1):
                metrics = analyze_page_type(page, idx)
                page_metrics_list.append(metrics)
    except ProcessingError:
        raise
    except Exception as e:
        raise ProcessingError(
            code=ErrorCode.PDF_CORRUPT,
            message=f"Failed to read PDF for type detection: {str(e)}",
        )

    digital_count = sum(1 for p in page_metrics_list if p.page_type == PageType.DIGITAL)
    scanned_count = sum(1 for p in page_metrics_list if p.page_type == PageType.SCANNED)
    hybrid_count = sum(1 for p in page_metrics_list if p.page_type == PageType.HYBRID)
    total_pages = len(page_metrics_list)

    if digital_count == total_pages:
        doc_type = DocType.DIGITAL
        doc_reason = "All pages contain direct extractable digital text."
    elif scanned_count == total_pages:
        doc_type = DocType.SCANNED
        doc_reason = "All pages contain scanned raster images or corrupted font layers requiring OCR."
    else:
        doc_type = DocType.MIXED
        doc_reason = (
            f"Document contains a mixture of pages ({digital_count} digital, "
            f"{scanned_count} scanned, {hybrid_count} hybrid)."
        )

    return DocumentTypeReport(
        doc_type=doc_type,
        total_pages=total_pages,
        digital_page_count=digital_count,
        scanned_page_count=scanned_count,
        hybrid_page_count=hybrid_count,
        pages=page_metrics_list,
        reason=doc_reason,
    )
