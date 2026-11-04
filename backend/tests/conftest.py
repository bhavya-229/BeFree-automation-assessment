"""Pytest fixtures for generating synthetic test PDFs."""

import os
import sys

# Prevent OpenBLAS memory allocation error on Windows Python 3.13
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
from pathlib import Path
import pytest
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pikepdf

# Add app to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


@pytest.fixture
def sample_digital_pdf(tmp_path: Path) -> Path:
    """Generate a clean digital PDF with formatted aligned table columns."""
    pdf_path = tmp_path / "digital_sample.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawString(50, 750, "Commonwealth Bank of Australia - Statement of Account")
    c.drawString(50, 730, "Account Number: 1234 5678 9012  BSB: 062-000")

    # Table Header at aligned X coordinates
    c.drawString(50, 700, "Date")
    c.drawString(130, 700, "Description")
    c.drawString(330, 700, "Debit")
    c.drawString(410, 700, "Credit")
    c.drawString(490, 700, "Balance")

    # Opening balance metadata
    c.drawString(50, 675, "01/10/2023")
    c.drawString(130, 675, "Opening Balance")
    c.drawString(490, 675, "1,500.00")

    # Row 1: Woolworths debit
    c.drawString(50, 650, "03/10/2023")
    c.drawString(130, 650, "WOOLWORTHS SYDNEY")
    c.drawString(330, 650, "85.50")
    c.drawString(490, 650, "1,414.50")

    # Row 2: Salary credit
    c.drawString(50, 625, "05/10/2023")
    c.drawString(130, 625, "SALARY DIRECT CREDIT")
    c.drawString(410, 625, "3,200.00")
    c.drawString(490, 625, "4,614.50")

    # Row 3: Telstra debit
    c.drawString(50, 600, "08/10/2023")
    c.drawString(130, 600, "TELSTRA BILL PAYMENT")
    c.drawString(330, 600, "120.00")
    c.drawString(490, 600, "4,494.50")

    c.save()
    return pdf_path


@pytest.fixture
def sample_scanned_pdf(tmp_path: Path) -> Path:
    """Generate a scanned PDF with an embedded raster image and no text."""
    img_path = tmp_path / "scan_page.png"
    img = Image.new("RGB", (600, 800), color=(245, 245, 245))
    img.save(img_path, format="PNG")

    pdf_path = tmp_path / "scanned_sample.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawImage(str(img_path), 0, 0, width=612, height=792)
    c.save()
    return pdf_path


@pytest.fixture
def sample_mixed_pdf(tmp_path: Path) -> Path:
    """Generate a multi-page PDF with Page 1 digital text and Page 2 scanned image."""
    img_path = tmp_path / "scan_page2.png"
    img = Image.new("RGB", (600, 800), color=(245, 245, 245))
    img.save(img_path, format="PNG")

    pdf_path = tmp_path / "mixed_sample.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    # Page 1: Digital text
    c.drawString(50, 750, "Barclays Bank UK PLC - Account Statement Page 1")
    c.drawString(50, 730, "Sort Code: 20-00-00  Account: 12345678")
    c.drawString(50, 700, "Date")
    c.drawString(130, 700, "Description")
    c.drawString(330, 700, "Paid Out")
    c.drawString(410, 700, "Paid In")
    c.drawString(490, 700, "Balance")

    c.drawString(50, 675, "12 Oct 2023")
    c.drawString(130, 675, "TESCO STORES LONDON")
    c.drawString(330, 675, "25.40")
    c.drawString(490, 675, "850.00")

    c.drawString(50, 650, "14 Oct 2023")
    c.drawString(130, 650, "SAINSBURYS SUPERMARKET")
    c.drawString(330, 650, "42.10")
    c.drawString(490, 650, "807.90")
    c.showPage()

    # Page 2: Scanned receipt image
    c.drawImage(str(img_path), 0, 0, width=612, height=792)
    c.save()
    return pdf_path


@pytest.fixture
def sample_encrypted_pdf(tmp_path: Path, sample_digital_pdf: Path) -> Path:
    """Generate a password-protected PDF."""
    encrypted_path = tmp_path / "encrypted_sample.pdf"
    with pikepdf.Pdf.open(sample_digital_pdf) as pdf:
        encryption = pikepdf.Encryption(owner="secret123", user="userpass")
        pdf.save(encrypted_path, encryption=encryption)
    return encrypted_path


@pytest.fixture
def sample_cid_corrupted_pdf(tmp_path: Path) -> Path:
    """Generate a PDF containing (cid:N) font encoding failures."""
    pdf_path = tmp_path / "cid_corrupted.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    c.drawString(50, 750, "(cid:12)(cid:14)(cid:18)(cid:20)(cid:22) (cid:33)(cid:45)(cid:67)")
    c.drawString(50, 730, "(cid:100)(cid:101)(cid:102) \ufffd\ufffd\ufffd \ufffd\ufffd\ufffd")
    c.save()
    return pdf_path
