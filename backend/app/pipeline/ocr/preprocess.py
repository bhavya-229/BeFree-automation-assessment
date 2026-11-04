"""Page rendering and OpenCV image preprocessing for scanned statements."""

from pathlib import Path
from typing import Optional, Tuple
import cv2
import numpy as np
from PIL import Image
import pypdfium2 as pdfium

from app.config import settings
from app.errors import ErrorCode, ProcessingError


def render_page_to_image(file_path: Path, page_number: int, dpi: int = 300) -> Image.Image:
    """Render a specific PDF page to a PIL Image at specified DPI."""
    try:
        pdf = pdfium.PdfDocument(file_path)
        page_idx = page_number - 1
        if page_idx < 0 or page_idx >= len(pdf):
            raise IndexError(f"Page {page_number} out of range (total {len(pdf)} pages).")

        page = pdf[page_idx]
        scale = dpi / 72.0
        bitmap = page.render(scale=scale)
        pil_image = bitmap.to_pil()
        pdf.close()
        return pil_image
    except Exception as e:
        raise ProcessingError(
            code=ErrorCode.OCR_UNAVAILABLE,
            message=f"Failed to render PDF page {page_number}: {str(e)}",
        )


def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    """Apply grayscale, contrast enhancement (CLAHE), deskew, and thresholding using OpenCV."""
    # Convert PIL Image to OpenCV BGR numpy array
    np_img = np.array(image.convert("RGB"))
    bgr = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

    # 1. Grayscale
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # 2. Contrast Enhancement via CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 3. Deskew detection (detect text angle using minAreaRect on contours)
    thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))

    if len(coords) > 100:
        angle = cv2.minAreaRect(coords)[-1]
        # Normalize angle
        if angle < -45:
            angle = -(90 + angle)
        elif angle > 45:
            angle = 90 - angle
        else:
            angle = -angle

        # Only deskew if tilt is between 0.5 and 15 degrees
        if 0.5 < abs(angle) < 15.0:
            (h, w) = enhanced.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            enhanced = cv2.warpAffine(
                enhanced, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
            )

    # Convert back to PIL Image
    return Image.fromarray(enhanced)
