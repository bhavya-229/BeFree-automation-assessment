"""Tesseract OCR engine wrapper emitting normalized Word streams."""

from pathlib import Path
from typing import List, Optional
import shutil
from PIL import Image
import pytesseract
from pytesseract import Output

from app.pipeline.layout.words import Word
from app.pipeline.ocr.preprocess import render_page_to_image, preprocess_image_for_ocr
from app.config import settings
from app.errors import ErrorCode, ProcessingError


class TesseractOcrEngine:
    """Wrapper around local Tesseract binary with automatic fallback."""

    def __init__(self, tesseract_cmd: Optional[str] = None):
        self.tesseract_cmd = tesseract_cmd or shutil.which("tesseract")
        if self.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    @property
    def is_available(self) -> bool:
        """Check if local Tesseract executable is installed and runnable."""
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

        # If Tesseract is not installed on the host runner, return empty or raise structured error
        if not self.is_available:
            return []

        try:
            # PSM 6: Assume a single uniform block of text
            config = f"--psm 6 -l {settings.OCR_LANGS}"
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
