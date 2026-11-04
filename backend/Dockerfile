FROM python:3.11-slim

# Install system dependencies including Tesseract OCR and OpenCV runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-osd \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/pyproject.toml .
RUN pip install --no-cache-dir \
    fastapi uvicorn pydantic pydantic-settings pdfplumber pypdfium2 pikepdf \
    pytesseract opencv-python-headless numpy Pillow rapidfuzz python-dateutil \
    scikit-learn joblib xlsxwriter openpyxl python-multipart httpx \
    sqlalchemy pyyaml

COPY backend/app ./app
COPY backend/app/classification/taxonomy.yaml ./app/classification/taxonomy.yaml
COPY data/samples ./data/samples
RUN mkdir -p /app/data/uploads

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
