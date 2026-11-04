# Edge-Case Catalog & Implementation Status

| Edge Case Scenario | Expected Behavior | Implementation Status | Verified Test Name |
| :--- | :--- | :--- | :--- |
| **Non-PDF file uploaded** | Reject with `NOT_A_PDF` error code | Implemented | `test_intake_non_pdf_fails` |
| **Empty 0-byte file** | Reject with `FILE_EMPTY` error code | Implemented | `test_intake_empty_file_fails` |
| **Oversized file (>25 MB)** | Reject with `FILE_TOO_LARGE` | Implemented | `test_intake_file_too_large_fails` |
| **Password-protected PDF** | Detect encryption; prompt with `needs_password=True` | Implemented | `test_intake_encrypted_pdf_detects_password_requirement` |
| **Corrupted PDF structure** | Reject with `PDF_CORRUPT` error code | Implemented | `test_intake_corrupted_pdf_structure` |
| **Mixed digital and scanned pages** | Detect page 1 as DIGITAL, page 2 as SCANNED, document as MIXED | Implemented | `test_detect_mixed_pdf` |
| **Corrupted font encoding / (cid:N)** | Detect garbage ratio $\ge 5\%$; route page to OCR | Implemented | `test_detect_cid_corrupted_pdf_routes_to_ocr` |
| **Multiline narration continuation** | Merge continuation lines without dates into preceding transaction description | Implemented | `test_multiline_narration_continuation` |
| **Opening balance line in table** | Identify starting balance metadata; exclude from transaction rows | Implemented | `test_transaction_row_reconstruction` |
| **Inverted Debit/Credit direction** | Verify running balance delta; auto-repair swap and flag `REPAIRED_DIRECTION` | Implemented | `test_reconcile_auto_repairs_swapped_direction` |
| **Balance ledger discrepancy** | Flag row with `BALANCE_MISMATCH` and `POSSIBLE_MISSING_ROW`; never fabricate fake numbers | Implemented | `test_reconcile_detects_balance_mismatch_without_fabricating` |
| **OCR date digit confusions** | Bounded repair of OCR letters (`O` $\to$ `0`, `l` $\to$ `1`) on date tokens; flag `REPAIRED_DATE_OCR` | Implemented | `test_parse_date_ocr_character_repair` |
| **Negative amounts in parentheses** | Parse `(85.50)` to `Decimal("-85.50")`; flag `NEGATIVE_BRACKET_AMOUNT` | Implemented | `test_parse_amounts_and_currencies` |
| **Formula injection in descriptions** | Prepend `'` to strings starting with `=`, `+`, `-`, `@` in CSV and XLSX | Implemented | `test_sanitize_formula_injection`, `test_export_transactions_to_csv` |
| **Manual user category override** | Preserve user-edited category permanently; protect from reclassification | Implemented | `test_hybrid_classification_hierarchy` |
| **Unrecognized transaction narration** | Fall back to `Other / Unclassified`; flag `LOW_CONFIDENCE` for human review | Implemented | `test_hybrid_classification_hierarchy` |
