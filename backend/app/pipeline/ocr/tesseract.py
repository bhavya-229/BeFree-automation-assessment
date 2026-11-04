"""Tesseract OCR engine wrapper emitting normalized Word streams."""

import os
from pathlib import Path
from typing import List, Optional
import shutil
from fastapi import status
from PIL import Image
import pytesseract
from pytesseract import Output

from app.pipeline.layout.words import Word
from app.pipeline.ocr.preprocess import render_page_to_image, preprocess_image_for_ocr
from app.config import settings
from app.errors import ErrorCode, ProcessingError


def find_tesseract_cmd() -> Optional[str]:
    """Dynamically locate Tesseract executable across system PATH and well-known Windows locations."""
    cmd = shutil.which("tesseract")
    if cmd:
        return cmd

    if os.name == "nt":
        candidates = [
            Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
            Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
            Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe")),
            Path(r"C:\Tesseract-OCR\tesseract.exe"),
        ]
        for p in candidates:
            if p.exists():
                return str(p)

    return None


class TesseractOcrEngine:
    """Wrapper around local Tesseract binary with automatic dynamic fallback."""

    def __init__(self, tesseract_cmd: Optional[str] = None):
        self.tesseract_cmd = tesseract_cmd or find_tesseract_cmd()
        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    @property
    def is_available(self) -> bool:
        """Check if local Tesseract executable is installed and runnable."""
        if not self.tesseract_cmd:
            self.tesseract_cmd = find_tesseract_cmd()
            if self.tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

        if not self.tesseract_cmd:
            return False
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def ocr_page_image(self, image: Image.Image, page_number: int) -> List[Word]:
        """Perform word-level OCR on an image and normalize coordinates to [0, 1]."""
        width, height = image.size
        if width <= 0 or height <= 0:
            return []

        if not self.is_available:
            raise ProcessingError(
                code=ErrorCode.OCR_UNAVAILABLE,
                message=(
                    f"Page {page_number} is a scanned raster image requiring OCR, but Tesseract 5 was not found on your system. "
                    "To process scanned/image-based PDFs, run using Docker ('docker compose up') where Tesseract is pre-configured, "
                    "or install Tesseract OCR on Windows."
                ),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        try:
            # PSM 4: Assume a single column of text of variable sizes (ideal for tables and bank statements)
            config = f"--psm 4 -l {settings.OCR_LANGS}"
            data = pytesseract.image_to_data(image, config=config, output_type=Output.DICT)
        except Exception as e:
            raise ProcessingError(
                code=ErrorCode.OCR_TIMEOUT,
                message=f"OCR execution failed on page {page_number}: {str(e)}",
            )

        words: List[Word] = []
        n_boxes = len(data["text"])
        for i in range(n_boxes):
            text = str(data["text"][i]).strip()
            conf = float(data["conf"][i])

            # Filter out empty strings or low confidence non-text
            if not text or conf < 0:
                continue

            x = float(data["left"][i])
            y = float(data["top"][i])
            w = float(data["width"][i])
            h = float(data["height"][i])

            x0 = max(0.0, min(1.0, x / width))
            y0 = max(0.0, min(1.0, y / height))
            x1 = max(0.0, min(1.0, (x + w) / width))
            y1 = max(0.0, min(1.0, (y + h) / height))

            words.append(
                Word(
                    page_number=page_number,
                    text=text,
                    x0=round(x0, 5),
                    y0=round(y0, 5),
                    x1=round(x1, 5),
                    y1=round(y1, 5),
                    confidence=round(conf, 2),
                    source="ocr",
                )
            )

        return words

    def ocr_page(self, file_path: Path, page_number: int, dpi: int = 300) -> List[Word]:
        """Full pipeline: render PDF page -> OpenCV preprocess -> Tesseract OCR."""
        raw_image = render_page_to_image(file_path, page_number, dpi=dpi)
        processed_image = preprocess_image_for_ocr(raw_image)
        return self.ocr_page_image(processed_image, page_number)


default_ocr_engine = TesseractOcrEngine()
