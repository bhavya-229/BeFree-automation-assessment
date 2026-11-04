# Bank Statement Processing & Classification System
### Befree AI & Automation Internship Assessment — Australia & UK Focused MVP

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.0-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-grade, privacy-centric Document-AI web application engineered to ingest, extract, reconcile, and classify bank statements across diverse layouts without external cloud dependencies or LLMs.

Prioritized for **Australia (CommBank, Westpac, ANZ)** and the **United Kingdom (Barclays, HSBC, NatWest)** with country-aware support for **India (SBI, HDFC)**, this system is designed for high-throughput, deterministic financial document intake.

---

## Architecture Overview

```mermaid
flowchart TD
    subgraph Intake ["1. Intake & Security"]
        A["PDF Upload / Stream"] --> B["Header & Magic Byte Verification (%PDF-)"]
        B --> C{"Encrypted / Locked?"}
        C -->|Yes, No Key| D["RFC 7807 401 PDF_ENCRYPTED"]
        D --> E["UI Password Prompt (In-Memory Decryption)"]
        E --> C
        C -->|Unlocked / Clean| F["Security Scan (Malicious JS / Launch Actions)"]
    end

    subgraph Inspection ["2. Page-Level Inspection"]
        F --> G["Per-Page Analyzer"]
        G -->|Extractable Fonts| H["Native Text Engine (pdfplumber)"]
        G -->|Raster Scan / Corrupted CIDs| I["Computer Vision OCR (CLAHE + Tesseract 5)"]
        H --> J["Normalized Spatial Geometry Stream [0, 1]"]
        I --> J
    end

    subgraph Layout ["3. Layout & Reconstruction"]
        J --> K["Fuzzy Header Discovery & Column Bounds"]
        K --> L["Spatial Token De-Concatenation (Regex + Coordinate Split)"]
        L --> M["Multiline Narration Continuation Stitching"]
    end

    subgraph Validation ["4. Mathematical Reconciliation"]
        M --> N["Running Balance Verification: B(t-1) - Debit + Credit = B(t)"]
        N --> O{"Discrepancy Detected?"}
        O -->|Inverted Columns| P["Bounded Auto-Repair: Swapped Dr/Cr"]
        O -->|Merged / Missing Amount| Q["Hypothesis 2: Delta Deduction from Narration"]
        O -->|Unresolved| R["Flag: BALANCE_MISMATCH / MISSING_ROW"]
        P --> S["Audit Quality Scoring [0 - 100%]"]
        Q --> S
        R --> S
    end

    subgraph Intelligence ["5. Non-LLM Hybrid Classification"]
        S --> T0["Active Learning Memory (user_rules SQLite WAL)"]
        T0 -->|Cache Miss| T["Deterministic Heuristic Rules Engine (>= 0.80)"]
        T -->|No Rule Match| U["Sub-word Char + Word n-gram FeatureUnion (>= 1.80x margin)"]
        U -->|Ambiguous / Low Margin| V["Human-in-the-Loop Review Queue"]
        V -->|User Reclassifies| T0
    end

    subgraph Presentation ["6. Presentation & Delivery"]
        T --> W["Interactive Review Workspace (React 18)"]
        U --> W
        V --> W
        W --> X["Formula-Sanitized CSV (UTF-8 BOM)"]
        W --> Y["Multi-Tab Styled Excel (.xlsx)"]
    end
```

---

## Core Engineering Principles

### 1. Zero-LLM & Fully Local Processing
- **Predictable & Reproducible**: Transaction classification runs deterministically using a prioritized rule engine (regex merchant normalization) combined with a calibrated `scikit-learn` Logistic Regression classifier powered by `FeatureUnion` (word n-grams `(1, 2)` + sub-word character n-grams `(3, 5)`).
- **Active Learning Feedback Loop**: User manual corrections in the UI persist directly to SQLite WAL (`user_rules`) and immediately apply to all future statements with `1.0` confidence and `MANUAL` provenance.
- **Privacy & Cost**: Zero external cloud APIs, zero third-party data leaks, zero tokens billed per page. Financial data never leaves the runtime environment.
- **Strict Guardrail**: Automated linting and tests fail if any LLM SDK (`openai`, `anthropic`, `langchain`, `transformers`) appears in dependencies.

### 2. Strict Monetary Arithmetic
- Floating-point representations (`0.1 + 0.2 != 0.3`) are banned from financial logic.
- Python `Decimal` is used across all extraction, reconciliation, and export calculations.
- Decimal strings are used in JSON transport and frontend display, preventing IEEE 754 precision errors.

### 3. Truth-Preserving Auditability
- The system **never fabricates data**. If an amount or date cannot be extracted with high confidence, it is marked as `null` and assigned an audit flag rather than guessed.
- Repaired values retain their raw, untouched representations alongside repair audit logs (`raw_debit`, `raw_credit`, `raw_balance`, `flags`).

---

## Key Capabilities & Edge-Case Catalog

| Challenge / Edge Case | Engineering Solution | Traceability |
| :--- | :--- | :--- |
| **Password-Protected PDFs** | In-memory `pikepdf` decryption. Returns RFC 7807 `401 PDF_ENCRYPTED` or `WRONG_PASSWORD`. UI renders a dedicated `PasswordDialog` with show/hide toggle. Zero storage of credentials. | [`app/api/v1/statements.py`](backend/app/api/v1/statements.py) |
| **Glued Columns & Agglutination** | When merchant narrations collide with money columns (e.g. `BOOTS PICCADILLY18.30`), the coordinate tokenizer performs regex token splitting (`r"^([A-Za-z]+)(\d+\.\d{2})$"`) with proportional bounding box subdivision. | [`app/pipeline/layout/row_builder.py`](backend/app/pipeline/layout/row_builder.py) |
| **Swallowed Amounts in Narrations** | If an amount is missing, the reconciliation engine calculates $\Delta = B_{prev} - B_{curr}$. If $\Delta$ matches the description suffix, it extracts the debit, trims the narration, and flags `INFERRED_AMOUNT`. | [`app/pipeline/validate/reconcile.py`](backend/app/pipeline/validate/reconcile.py) |
| **Scanned & Degraded Pages** | Page-level inspector calculates text density, non-printing garbage characters (`(cid:N)`, `\ufffd`), and image area ratios. Automatically triggers OpenCV CLAHE thresholding and multi-threaded Tesseract 5 OCR (`ThreadPoolExecutor`) across CPU cores. | [`app/pipeline/pdf_type.py`](backend/app/pipeline/pdf_type.py), [`app/api/v1/statements.py`](backend/app/api/v1/statements.py) |
| **Inverted Debit/Credit Columns** | Validates $B_{prev} - D + C = B_{curr}$. If invalid, tests whether swapping Debit and Credit reconciles the equation ($B_{prev} + D - C = B_{curr}$). If so, repairs columns with flag `REPAIRED_DIRECTION`. | [`app/pipeline/validate/reconcile.py`](backend/app/pipeline/validate/reconcile.py) |
| **Multi-Line Narrations** | Continuation lines lacking dates or amounts are re-assembled into the parent transaction's narration block, preserving spatial order and line breaks. | [`app/pipeline/layout/row_builder.py`](backend/app/pipeline/layout/row_builder.py) |
| **Active Learning Memory** | Manual category edits in the UI persist to `user_rules` table in SQLite, automatically learning payee patterns across statements and skipping ML/rules for familiar merchants. | [`app/core/database.py`](backend/app/core/database.py), [`app/core/storage.py`](backend/app/core/storage.py) |
| **Concatenated Bank Rails & OCR Noise** | Uses `char_wb (3, 5)` sub-word character n-grams to extract embedded merchant tokens within noisy payment strings (`UPI/.../DR/Amazon/...` or `POS2193WOOLWORTHS`). | [`app/classification/ml/model.py`](backend/app/classification/ml/model.py) |
| **Spreadsheet Formula Injection** | Prevents CSV/Excel formula execution by sanitizing all cells starting with `=`, `+`, `-`, or `@` with a leading apostrophe (`'`). | [`app/export/csv_exporter.py`](backend/app/export/csv_exporter.py), [`xlsx_exporter.py`](backend/app/export/xlsx_exporter.py) |

---

## Geographic & Banking Support

The pipeline dynamically adapts to locale-specific bank statement schemas:

```
├── Australia (Primary)
│   ├── Currency: AUD ($)
│   ├── Date Formats: DD/MM/YYYY, DD-MMM-YYYY
│   ├── Identifiers: BSB (XXX-XXX) & Account Number
│   ├── Payment Rails: PayID, Osko, EFTPOS, Direct Debit
│   └── Supported Profiles: Commonwealth Bank of Australia (CBA), Westpac, ANZ
│
├── United Kingdom (Primary)
│   ├── Currency: GBP (£)
│   ├── Date Formats: DD/MM/YYYY, DD MMM YYYY
│   ├── Identifiers: Sort Code (XX-XX-XX) & Account Number (8 digits)
│   ├── Payment Rails: BACS, Faster Payments, Direct Debit, CHAPS
│   └── Supported Profiles: Barclays, HSBC, NatWest
│
└── India (Secondary / Country-Aware)
    ├── Currency: INR (₹)
    ├── Date Formats: DD/MM/YYYY
    ├── Identifiers: IFSC Code & Account Number
    ├── Payment Rails: UPI, NEFT, RTGS, IMPS
    └── Supported Profiles: State Bank of India (SBI), HDFC Bank
```

---

## Technology Stack

### Backend
- **Framework**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2
- **PDF & Document AI**: `pdfplumber`, `pdfminer.six`, `pypdfium2`, `pikepdf`, `pytesseract` (Tesseract 5), `opencv-python-headless`, `NumPy`, `Pillow`
- **NLP & Classification**: `RapidFuzz` (token ratio string alignment), `scikit-learn` (TF-IDF + Calibrated Logistic Regression), `joblib`
- **Data & Export**: `python-dateutil`, `XlsxWriter` (formula defense)
- **Testing**: `pytest`, `httpx`, `ReportLab` (synthetic fixture generation)

### Frontend
- **Framework**: React 18, TypeScript, Vite
- **Styling & UI**: Tailwind CSS v4, Lucide React
- **State & Networking**: Native Async/Await, RFC 7807 Error Interceptor

---

## Quick Evaluation Walkthrough (30 Seconds)

If you are reviewing this assessment, here is the fastest way to test all core capabilities:

1. **Start the application** using Docker (`docker compose up --build`) or local setup.
2. Open **[http://localhost:5173](http://localhost:5173)** in your browser.
3. **1-Click Statement Demo**: In the *"Try Demo Statements"* panel on the homepage, click **"Run in App"** on **CommBank (AU)** or **Barclays (UK)**. The statement processes instantly, showing the interactive table, audit score, and ledger reconciliation proof.
4. **Test Encrypted PDF**: Click **"Run in App"** on **Encrypted CommBank**. A secure decryption modal appears. Enter password: `befree2026`. The PDF unlocks in-memory without saving the password to disk.
5. **Test Active Learning**:
   - In the transaction table, change any transaction's category (e.g., set an e-commerce or utility transaction to *Consulting & Services*).
   - The change is saved and immediately learned into the persistent `user_rules` table.
   - Any matching transaction across future statement uploads will now automatically classify as *Consulting & Services* with confidence `1.0` and source `MANUAL`.
6. **Test Formula-Safe Export**: Click **"Export CSV"** or **"Export Excel"**. Open the downloaded file to verify that all financial amounts use decimal formatting and dangerous formula characters (`=`, `+`, `-`, `@`) are safely escaped with a leading apostrophe (`'`).

---

## Getting Started & Execution Instructions

### Prerequisites
- **Docker & Docker Compose** (Recommended for 1-command startup with pre-configured Tesseract 5 & OpenCV)  
  *— OR —*
- **Python 3.11+** and **Node.js 18+ (with npm)** for running locally.

---

### Option A: Running with Docker Compose (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/bhavya-229/BeFree-automation-assessment.git
cd BeFree-automation-assessment

# 2. Build and launch all services
docker compose up --build
```

- **Frontend App**: [http://localhost:5173](http://localhost:5173)
- **FastAPI OpenAPI Swagger**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **Backend Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

*To stop the containers:*
```bash
docker compose down
```

---

### Option B: Running Locally

#### 1. Backend Setup

**On Windows (PowerShell):**
```powershell
# In repository root:
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install backend dependencies:
pip install -e "backend[dev]"

# Launch FastAPI development server:
python backend/run_dev.py
```

**On Linux / macOS (Bash):**
```bash
# In repository root:
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies:
pip install -e "./backend[dev]"

# Launch FastAPI development server:
python backend/run_dev.py
```
*Backend runs on `http://127.0.0.1:8000` (auto-reloading on changes).*

#### 2. Frontend Setup

In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:5173` and automatically proxies `/api` requests to `http://127.0.0.1:8000`.*

---

## Testing with Pre-Bundled Statement Fixtures

The repository includes synthetic, realistic bank statement PDFs in `data/samples/`. You can either:
1. Click **"Run in App"** directly on any sample card in the web UI.
2. Click **"PDF"** to download the fixture and test drag-and-drop file upload.

| Fixture Name | Bank & Region | Characteristics Tested |
| :--- | :--- | :--- |
| **`cba_australian_statement.pdf`** | CommBank (AU) | Native digital text, AUD currency, BSB formatting, Woolworths / Telstra merchant rules. |
| **`barclays_uk_statement.pdf`** | Barclays (UK) | Native digital text, GBP currency, Sort Code, Boots tight narration-amount boundary. |
| **`westpac_australian_statement.pdf`**| Westpac (AU) | Multiline payment references, BPAY & direct debit narrations. |
| **`sbi_india_statement.pdf`** | SBI (IN) | Day-first date parsing, INR currency, IFSC metadata extraction. |
| **`encrypted_cba_statement.pdf`** | CommBank (AU) | 128-bit PDF encryption. Triggers `PasswordDialog` in UI. **Password: `befree2026`**. |

To regenerate or customize fixtures:
```bash
python backend/scripts/make_fixtures.py
```

---

## Automated Test Suite

The test suite validates the complete ingestion pipeline, spatial layout reconstruction, password security, mathematical ledger checks, active learning feedback loops, and non-LLM classifiers:

```bash
# Run pytest across the entire test suite (38 tests, 100% passing)
pytest backend/tests -v

# Or run inside Docker:
docker compose exec api pytest tests -v
```

### Test Coverage Highlights (38 Tests):
- `test_intake.py` (6 tests): Magic byte validation, file size limits, corrupt stream rejection, 128-bit encryption detection.
- `test_pdf_type.py` (4 tests): Page-level digital vs. scanned vs. hybrid classification, CID font corruption routing.
- `test_extraction.py` (5 tests): Spatial word extraction, table header discovery, multiline continuation, CLAHE preprocessing.
- `test_parsing.py` (4 tests): Country-aware date formats (`DD/MM/YYYY`, `DD-MMM-YYYY`), amount normalizers, OCR repair.
- `test_reconcile.py` (3 tests): Running balance ledger checks, inverted column repairs, delta amount recovery.
- `test_classifier.py` (9 tests): Deterministic rules, sub-word char_wb FeatureUnion ML, active learning user rules memory, LRU cache hit checks, and real-world Indian UPI statements.
- `test_export.py` (3 tests): Formula injection neutralization (`'` prefix), CSV BOM encoding, XLSX workbook structures.
- `test_api.py` (4 tests): End-to-end API lifecycle: upload, encrypted 401 handling, patch category, export CSV/XLSX.

---

## REST API Specification

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health status. |
| `POST` | `/api/v1/statements` | Upload and process statement PDF. Accepts multipart `file` and optional `password`. |
| `GET` | `/api/v1/statements/{id}` | Retrieve parsed statement record, provenance metadata, and transactions. |
| `PATCH`| `/api/v1/statements/{id}/transactions/{tx_id}` | Human-in-the-loop review: update transaction category with audit record. |
| `GET` | `/api/v1/statements/{id}/export/csv` | Download formula-safe CSV file (UTF-8 BOM). |
| `GET` | `/api/v1/statements/{id}/export/xlsx` | Download formatted Excel workbook. |
| `POST` | `/api/v1/statements/samples/{key}` | Process pre-bundled demo fixture (`cba`, `barclays`, `westpac`, `sbi`, `encrypted`). |
| `GET` | `/api/v1/statements/samples/{key}/download` | Download raw synthetic sample PDF. |

---

## Project Structure

```
beFree/
├── backend/
│   ├── app/
│   │   ├── api/v1/                 # REST endpoints (statements, export, review)
│   │   ├── classification/         # Non-LLM classifier (rules engine, TF-IDF + Logistic Regression)
│   │   ├── core/                   # SQLite WAL repository with active learning user_rules persistence
│   │   ├── export/                 # Formula-safe CSV & XLSX export engines
│   │   ├── pipeline/
│   │   │   ├── bank_profiles/      # Bank layout profiles (AU CBA, UK Barclays, Generic)
│   │   │   ├── layout/             # Spatial table detector & multiline row builder
│   │   │   ├── ocr/                # OpenCV CLAHE preprocessing & Tesseract engine
│   │   │   ├── parse/              # Dates, amounts, and account metadata parsers
│   │   │   └── validate/           # Running balance reconciler & auto-repair logic
│   │   ├── schemas/                # Pydantic data schemas & transaction contracts
│   │   ├── errors.py               # RFC 7807 problem+json error handlers
│   │   └── main.py                 # FastAPI application factory
│   ├── scripts/
│   │   └── make_fixtures.py        # ReportLab synthetic statement generator
│   └── tests/                      # 38 unit and end-to-end pytest tests
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AccountDetailsCard.tsx  # Bank metadata with Mask/Reveal toggle
│   │   │   ├── FileUpload.tsx          # Drag-and-drop dropzone & demo fixture bar
│   │   │   ├── Header.tsx              # Fintech gradient header & taxonomy modal
│   │   │   ├── PasswordDialog.tsx      # Modal for encrypted statement decryption
│   │   │   ├── StatementInsights.tsx   # Spend distribution & category breakdown
│   │   │   ├── StatementOverview.tsx   # Workspace coordinator (4 tab navigation)
│   │   │   ├── StatementValidation.tsx # Mathematical balance proof ledger
│   │   │   └── TransactionTable.tsx    # Live grid with drawer audit & in-place edit
│   │   ├── lib/api.ts                  # Typed API client with 401 error interceptor
│   │   └── types/index.ts              # TypeScript domain types
│   ├── Dockerfile
│   └── vite.config.ts
│
├── data/
│   ├── samples/                    # Pre-generated synthetic PDF statements
│   └── uploads/                    # Local temporary processing storage (.gitkeep)
├── docs/                           # Architectural Decision Records & Deep-Dive Specs
├── docker-compose.yml
└── README.md
```

---

## Author & Contact

**Bhavya Dubal**  
- **Email**: [bhavyadubal@gmail.com](mailto:bhavyadubal@gmail.com)  
- **GitHub**: [@bhavya-229](https://github.com/bhavya-229)  
- **Repository**: [https://github.com/bhavya-229/BeFree-automation-assessment](https://github.com/bhavya-229/BeFree-automation-assessment)
