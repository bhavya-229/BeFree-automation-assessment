# Architectural Decision Records (ADRs)

- **ADR-001: Geographic Priority Alignment (Australia & UK)**
  - *Context*: The original assessment specification leaned on Indian banking defaults (INR, IFSC, paise).
  - *Decision*: Shift primary focus to Australia (AUD, BSB, PayID/Osko) and the United Kingdom (GBP, Sort Code, BACS/Faster Payments), treating India as secondary and country-aware.
  - *Consequence*: Decoupled core numeric and schema models from hardcoded Indian conventions; all identifiers are polymorphic.

- **ADR-002: Zero-LLM Deterministic & Classical ML Pipeline**
  - *Context*: Privacy, reproducibility, processing speed, and zero cloud API expenses are non-negotiable requirements for banking data pipelines.
  - *Decision*: Strictly prohibit generative AI / LLM APIs in the extraction and classification pipelines. Use an explainable deterministic rule engine + calibrated scikit-learn TF-IDF Logistic Regression.
  - *Consequence*: Zero data leakage, instant throughput, full explainability.

- **ADR-003: Page-Level PDF Type Detection**
  - *Context*: Bank statements frequently combine digital text pages with scanned attachments or image pages.
  - *Decision*: Inspect and classify every page independently (`DIGITAL`, `SCANNED`, `HYBRID`) based on font integrity, text density, and raster image area.
  - *Consequence*: OCR runs only on scanned or broken-font pages, eliminating redundant OCR slowdowns on native digital pages.

- **ADR-004: Raw Financial Value Preservation and Bounded Auto-Repair**
  - *Context*: OCR misreads and tabular continuation lines can create reconciliation errors.
  - *Decision*: Never silently fabricate or alter transaction amounts to force reconciliation. Preserve `raw_debit`, `raw_credit`, `raw_balance`, and record all repairs (`REPAIRED_DIRECTION`, `BALANCE_MISMATCH`).
  - *Consequence*: 100% auditability for accountants and credit analysts.

- **ADR-005: Formula Injection Defense in CSV and XLSX Exports**
  - *Context*: Malicious or corrupted narrations starting with `=`, `+`, `-`, or `@` can execute macros when opened in Microsoft Excel.
  - *Decision*: Prepend a single quote `'` to neutralize formula injection in both CSV and XLSX outputs.
