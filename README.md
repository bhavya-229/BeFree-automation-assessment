# Bank Statement Processing & Classification System (Australia & UK MVP)

A production-grade, privacy-centric web application that processes bank statement PDFs (digital, scanned, and mixed) from major Australian and UK banks. The system extracts transaction tables, mathematically validates running balances, categorizes transactions strictly without LLMs, allows human-in-the-loop review, and exports clean CSV and Excel files.

---

## 1. Key Features

- **Australia & UK Geographic Priority**: Built-in support for Australian (AUD, BSB, PayID, Osko, EFTPOS) and UK (GBP, Sort Code, BACS, Faster Payments) banking conventions, alongside secondary country-aware support for India (INR, IFSC).
- **Page-Level PDF Type Detection**: Inspects every page individually to distinguish extractable digital text from scanned raster images or broken font layers (`(cid:N)` sequences).
- **Coordinate-Preserving Extraction**: Extracts words into a unified spatial geometry stream with normalized $[0, 1]$ coordinates across native text and local Tesseract OCR.
- **Robust Table & Multiline Reconstruction**: Reassembles complex transaction tables, automatically stitching multi-line payment narrations across continuation rows.
- **Mathematical Balance Reconciliation**: Reconciles running balances (`prev_balance - debit + credit == balance`) and opening/closing totals. Detects and flags anomalies (`BALANCE_MISMATCH`, `POSSIBLE_MISSING_ROW`) without ever fabricating data.
- **Strictly Non-LLM Hybrid Classification**: Combines a fast deterministic rule engine with a calibrated scikit-learn TF-IDF Logistic Regression model. Transactions with low confidence are flagged for manual review rather than forcing guesses.
- **Formula-Injection Defense**: Sanitizes all export fields prepending `'` to unsafe prefixes (`=`, `+`, `-`, `@`) in CSV and Excel (`.xlsx`) downloads.

---

## 2. Quick Start

### Option A: Running with Docker Compose (Recommended)
Ensure Docker is running, then run:

```bash
docker compose up --build
```

- **Web Application**: Visit [http://localhost:5173](http://localhost:5173)
- **API Documentation (Swagger UI)**: Visit [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

---

### Option B: Running Locally

#### 1. Backend (FastAPI)
```bash
# In project root
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

pip install -e backend/.[dev]
# Or install dependencies from pyproject.toml
uvicorn backend.app.main:app --reload --port 8000
```

#### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 3. Generating Sample Statements for Testing

To generate synthetic Australian (Commonwealth Bank) and UK (Barclays) sample statement PDFs:

```bash
python backend/scripts/make_fixtures.py
```

Generated files will be saved in `data/samples/`:
- `data/samples/cba_australian_statement.pdf`
- `data/samples/barclays_uk_statement.pdf`

Upload either file directly in the web UI to test extraction, reconciliation, and classification immediately.

---

## 4. Running Automated Tests

The test suite covers intake validation, page-level detection, word extraction, multiline reconstruction, country-aware date/amount parsing, balance reconciliation, rules engine, ML classifier, exports, and end-to-end API workflows.

```bash
pytest backend/tests -v
```

All 32 tests pass out of the box with zero warnings.

---

## 5. Architecture & Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): Full pipeline architecture and component breakdown.
- [docs/CLASSIFICATION.md](docs/CLASSIFICATION.md): Non-LLM hybrid classification engine and held-out benchmark evaluation.
- [docs/EDGE_CASES.md](docs/EDGE_CASES.md): Real-world edge-case catalog and test verification traceability.
- [docs/DECISIONS.md](docs/DECISIONS.md): Architectural Decision Records (ADRs).
