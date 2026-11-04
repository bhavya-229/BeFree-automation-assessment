"""Direct layout text extraction for digital PDF pages."""

from pathlib import Path
from typing import List, Optional
import pdfplumber

from app.pipeline.layout.words import Word
from app.errors import ErrorCode, ProcessingError


def extract_native_words_from_page(page: pdfplumber.page.Page, page_number: int) -> List[Word]:
    """Extract individual words with normalized [0, 1] coordinates from a single page."""
    width = float(page.width)
    height = float(page.height)

    if width <= 0 or height <= 0:
        return []

    words_raw = page.extract_words(
        x_tolerance=3,
        y_tolerance=3,
        keep_blank_chars=False,
        use_text_flow=True,
    )

    extracted_words: List[Word] = []
    for w in words_raw:
        text = w.get("text", "").strip()
        if not text:
            continue

        x0 = max(0.0, min(1.0, float(w.get("x0", 0.0)) / width))
        y0 = max(0.0, min(1.0, float(w.get("top", 0.0)) / height))
        x1 = max(0.0, min(1.0, float(w.get("x1", 0.0)) / width))
        y1 = max(0.0, min(1.0, float(w.get("bottom", 0.0)) / height))

        extracted_words.append(
            Word(
                page_number=page_number,
                text=text,
                x0=round(x0, 5),
                y0=round(y0, 5),
                x1=round(x1, 5),
                y1=round(y1, 5),
                confidence=100.0,
                source="native",
            )
        )

    return extracted_words


def extract_native_words_from_document(
    file_path: Path, pages_to_extract: Optional[List[int]] = None
) -> List[Word]:
    """Extract native words from specified pages or all pages of a digital PDF."""
    if not file_path.exists():
        raise ProcessingError(
            code=ErrorCode.PDF_CORRUPT,
            message=f"File not found: {file_path}",
        )

    all_words: List[Word] = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for idx, page in enumerate(pdf.pages, start=1):
                if pages_to_extract is not None and idx not in pages_to_extract:
                    continue
                page_words = extract_native_words_from_page(page, idx)
                all_words.extend(page_words)
    except Exception as e:
        raise ProcessingError(
            code=ErrorCode.PARSE_FAILED,
            message=f"Native extraction failed: {str(e)}",
        )

    return all_words
